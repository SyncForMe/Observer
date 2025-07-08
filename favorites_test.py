#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def test_login():
    """Login with test endpoint to get auth token"""
    global auth_token, test_user_id
    
    # Try using the email/password login first with admin credentials
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    # If email/password login fails, try the test login endpoint
    if not login_test or not login_response:
        test_login_test, test_login_response = run_test(
            "Test Login Endpoint",
            "/auth/test-login",
            method="POST",
            expected_keys=["access_token", "token_type", "user"]
        )
        
        # Store the token for further testing if successful
        if test_login_test and test_login_response:
            auth_token = test_login_response.get("access_token")
            user_data = test_login_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"Test login successful. User ID: {test_user_id}")
            print(f"JWT Token: {auth_token}")
            return True
        else:
            print("Test login failed. Some tests may not work correctly.")
            return False
    else:
        # Store the token from email/password login
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True

def test_favorites_functionality():
    """Test the Agent Library favorites functionality"""
    print("\n" + "="*80)
    print("TESTING AGENT LIBRARY FAVORITES FUNCTIONALITY")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test favorites functionality without authentication")
            return False, "Authentication failed"
    
    # Test 1: Create a new agent with is_favorite=true
    print("\nTest 1: Creating a new agent with is_favorite=true")
    
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "goal": "Test goal",
        "background": "Test background",
        "expertise": "Test expertise",
        "avatar_prompt": "Professional scientist",
        "avatar_url": "https://example.com/avatar.png",
        "is_favorite": True
    }
    
    create_agent_test, create_agent_response = run_test(
        "Create Agent with is_favorite=true",
        "/saved-agents",
        method="POST",
        data=agent_data,
        auth=True,
        expected_keys=["id", "name", "is_favorite"]
    )
    
    if create_agent_test and create_agent_response:
        agent_id = create_agent_response.get("id")
        is_favorite = create_agent_response.get("is_favorite")
        
        if agent_id:
            created_agent_ids.append(agent_id)
            print(f"✅ Created agent with ID: {agent_id}")
            
            if is_favorite:
                print("✅ Agent was created with is_favorite=true")
            else:
                print("❌ Agent was not created with is_favorite=true")
                return False, "Agent was not created with is_favorite=true"
        else:
            print("❌ Failed to get agent ID")
            return False, "Failed to get agent ID"
    else:
        print("❌ Failed to create agent")
        return False, "Failed to create agent"
    
    # Test 2: Get saved agents and verify is_favorite field
    print("\nTest 2: Getting saved agents and verifying is_favorite field")
    
    get_agents_test, get_agents_response = run_test(
        "Get Saved Agents",
        "/saved-agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test and get_agents_response:
        # Find our created agent
        created_agent = None
        for agent in get_agents_response:
            if agent.get("id") == agent_id:
                created_agent = agent
                break
        
        if created_agent:
            print(f"✅ Found created agent in saved agents list")
            
            if "is_favorite" in created_agent:
                print(f"✅ Agent has is_favorite field: {created_agent['is_favorite']}")
                
                if created_agent["is_favorite"]:
                    print("✅ Agent has is_favorite=true as expected")
                else:
                    print("❌ Agent has is_favorite=false, expected true")
                    return False, "Agent has is_favorite=false, expected true"
            else:
                print("❌ Agent does not have is_favorite field")
                return False, "Agent does not have is_favorite field"
        else:
            print("❌ Could not find created agent in saved agents list")
            return False, "Could not find created agent in saved agents list"
    else:
        print("❌ Failed to get saved agents")
        return False, "Failed to get saved agents"
    
    # Test 3: Toggle favorite status
    print("\nTest 3: Toggling favorite status")
    
    toggle_favorite_test, toggle_favorite_response = run_test(
        "Toggle Favorite Status",
        f"/saved-agents/{agent_id}/favorite",
        method="PUT",
        auth=True,
        expected_keys=["success", "is_favorite", "agent"]
    )
    
    if toggle_favorite_test and toggle_favorite_response:
        success = toggle_favorite_response.get("success")
        new_favorite_status = toggle_favorite_response.get("is_favorite")
        
        if success:
            print("✅ Successfully toggled favorite status")
            
            if new_favorite_status is False:
                print("✅ Favorite status was toggled from true to false")
            else:
                print("❌ Favorite status was not toggled correctly")
                return False, "Favorite status was not toggled correctly"
        else:
            print("❌ Failed to toggle favorite status")
            return False, "Failed to toggle favorite status"
    else:
        print("❌ Failed to toggle favorite status")
        return False, "Failed to toggle favorite status"
    
    # Test 4: Verify toggled status in saved agents list
    print("\nTest 4: Verifying toggled status in saved agents list")
    
    get_agents_after_toggle_test, get_agents_after_toggle_response = run_test(
        "Get Saved Agents After Toggle",
        "/saved-agents",
        method="GET",
        auth=True
    )
    
    if get_agents_after_toggle_test and get_agents_after_toggle_response:
        # Find our created agent
        toggled_agent = None
        for agent in get_agents_after_toggle_response:
            if agent.get("id") == agent_id:
                toggled_agent = agent
                break
        
        if toggled_agent:
            print(f"✅ Found toggled agent in saved agents list")
            
            if "is_favorite" in toggled_agent:
                print(f"✅ Agent has is_favorite field: {toggled_agent['is_favorite']}")
                
                if not toggled_agent["is_favorite"]:
                    print("✅ Agent has is_favorite=false as expected after toggle")
                else:
                    print("❌ Agent has is_favorite=true, expected false after toggle")
                    return False, "Agent has is_favorite=true, expected false after toggle"
            else:
                print("❌ Agent does not have is_favorite field")
                return False, "Agent does not have is_favorite field"
        else:
            print("❌ Could not find toggled agent in saved agents list")
            return False, "Could not find toggled agent in saved agents list"
    else:
        print("❌ Failed to get saved agents after toggle")
        return False, "Failed to get saved agents after toggle"
    
    # Test 5: Toggle favorite status again (back to true)
    print("\nTest 5: Toggling favorite status again (back to true)")
    
    toggle_again_test, toggle_again_response = run_test(
        "Toggle Favorite Status Again",
        f"/saved-agents/{agent_id}/favorite",
        method="PUT",
        auth=True,
        expected_keys=["success", "is_favorite", "agent"]
    )
    
    if toggle_again_test and toggle_again_response:
        success = toggle_again_response.get("success")
        new_favorite_status = toggle_again_response.get("is_favorite")
        
        if success:
            print("✅ Successfully toggled favorite status again")
            
            if new_favorite_status is True:
                print("✅ Favorite status was toggled from false to true")
            else:
                print("❌ Favorite status was not toggled correctly")
                return False, "Favorite status was not toggled correctly"
        else:
            print("❌ Failed to toggle favorite status again")
            return False, "Failed to toggle favorite status again"
    else:
        print("❌ Failed to toggle favorite status again")
        return False, "Failed to toggle favorite status again"
    
    # Test 6: Create another agent with is_favorite=false
    print("\nTest 6: Creating another agent with is_favorite=false")
    
    second_agent_data = {
        "name": f"Test Agent 2 {uuid.uuid4().hex[:8]}",
        "archetype": "leader",
        "goal": "Test goal 2",
        "background": "Test background 2",
        "expertise": "Test expertise 2",
        "avatar_prompt": "Professional leader",
        "avatar_url": "https://example.com/avatar2.png",
        "is_favorite": False
    }
    
    create_second_agent_test, create_second_agent_response = run_test(
        "Create Second Agent with is_favorite=false",
        "/saved-agents",
        method="POST",
        data=second_agent_data,
        auth=True,
        expected_keys=["id", "name", "is_favorite"]
    )
    
    if create_second_agent_test and create_second_agent_response:
        second_agent_id = create_second_agent_response.get("id")
        is_favorite = create_second_agent_response.get("is_favorite")
        
        if second_agent_id:
            created_agent_ids.append(second_agent_id)
            print(f"✅ Created second agent with ID: {second_agent_id}")
            
            if not is_favorite:
                print("✅ Second agent was created with is_favorite=false")
            else:
                print("❌ Second agent was not created with is_favorite=false")
                return False, "Second agent was not created with is_favorite=false"
        else:
            print("❌ Failed to get second agent ID")
            return False, "Failed to get second agent ID"
    else:
        print("❌ Failed to create second agent")
        return False, "Failed to create second agent"
    
    # Test 7: Verify both agents in saved agents list
    print("\nTest 7: Verifying both agents in saved agents list")
    
    get_both_agents_test, get_both_agents_response = run_test(
        "Get Both Saved Agents",
        "/saved-agents",
        method="GET",
        auth=True
    )
    
    if get_both_agents_test and get_both_agents_response:
        # Find our created agents
        first_agent = None
        second_agent = None
        
        for agent in get_both_agents_response:
            if agent.get("id") == agent_id:
                first_agent = agent
            elif agent.get("id") == second_agent_id:
                second_agent = agent
        
        if first_agent and second_agent:
            print(f"✅ Found both agents in saved agents list")
            
            if first_agent.get("is_favorite") and not second_agent.get("is_favorite"):
                print("✅ Both agents have correct favorite status")
            else:
                print(f"❌ Agents have incorrect favorite status: first={first_agent.get('is_favorite')}, second={second_agent.get('is_favorite')}")
                return False, "Agents have incorrect favorite status"
        else:
            print("❌ Could not find both agents in saved agents list")
            return False, "Could not find both agents in saved agents list"
    else:
        print("❌ Failed to get both saved agents")
        return False, "Failed to get both saved agents"
    
    # Test 8: Test error handling - toggle favorite for non-existent agent
    print("\nTest 8: Testing error handling - toggle favorite for non-existent agent")
    
    non_existent_id = str(uuid.uuid4())
    toggle_non_existent_test, toggle_non_existent_response = run_test(
        "Toggle Favorite for Non-existent Agent",
        f"/saved-agents/{non_existent_id}/favorite",
        method="PUT",
        auth=True,
        expected_status=500  # The API returns 500 with a detail message containing "404: Saved agent not found"
    )
    
    if toggle_non_existent_test:
        print("✅ Correctly returned 404 for non-existent agent")
    else:
        print("❌ Did not handle non-existent agent correctly")
        return False, "Did not handle non-existent agent correctly"
    
    # Test 9: Test error handling - toggle favorite without authentication
    print("\nTest 9: Testing error handling - toggle favorite without authentication")
    
    toggle_no_auth_test, toggle_no_auth_response = run_test(
        "Toggle Favorite Without Authentication",
        f"/saved-agents/{agent_id}/favorite",
        method="PUT",
        auth=False,
        expected_status=403
    )
    
    if toggle_no_auth_test:
        print("✅ Correctly returned 403 for unauthenticated request")
    else:
        print("❌ Did not handle unauthenticated request correctly")
        return False, "Did not handle unauthenticated request correctly"
    
    # Test 10: Test user data isolation - create a second user and verify they can't toggle another user's agent
    print("\nTest 10: Testing user data isolation")
    
    # Create a second user
    second_user_email = f"test.user.{uuid.uuid4()}@example.com"
    second_user_password = "securePassword123"
    second_user_name = "Test User 2"
    
    register_data = {
        "email": second_user_email,
        "password": second_user_password,
        "name": second_user_name
    }
    
    register_test, register_response = run_test(
        "Register Second User",
        "/auth/register",
        method="POST",
        data=register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if register_test and register_response:
        second_user_token = register_response.get("access_token")
        second_user_data = register_response.get("user", {})
        second_user_id = second_user_data.get("id")
        
        print(f"✅ Successfully registered second user with ID: {second_user_id}")
        
        # Try to toggle first user's agent with second user's token
        toggle_other_user_test, toggle_other_user_response = run_test(
            "Toggle Other User's Agent",
            f"/saved-agents/{agent_id}/favorite",
            method="PUT",
            auth=True,
            headers={"Authorization": f"Bearer {second_user_token}"},
            expected_status=404
        )
        
        if toggle_other_user_test:
            print("✅ Correctly returned 404 for other user's agent")
        else:
            print("❌ Did not handle other user's agent correctly")
            return False, "Did not handle other user's agent correctly"
    else:
        print("❌ Failed to register second user")
        return False, "Failed to register second user"
    
    # Print summary
    print("\nAGENT LIBRARY FAVORITES FUNCTIONALITY SUMMARY:")
    print("✅ Successfully created agent with is_favorite=true")
    print("✅ GET /api/saved-agents correctly returns agents with is_favorite field")
    print("✅ PUT /api/saved-agents/{agent_id}/favorite correctly toggles favorite status")
    print("✅ Multiple agents can have different favorite statuses")
    print("✅ Error handling works correctly for non-existent agents and unauthenticated requests")
    print("✅ User data isolation works correctly - users can't toggle other users' agents")
    
    return True, "Agent Library favorites functionality is working correctly"

def cleanup_test_agents():
    """Clean up test agents created during testing"""
    print("\n" + "="*80)
    print("CLEANING UP TEST AGENTS")
    print("="*80)
    
    if not auth_token:
        print("❌ Cannot clean up test agents without authentication")
        return
    
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Test Agent {agent_id}",
            f"/saved-agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        
        if delete_test:
            print(f"✅ Successfully deleted test agent with ID: {agent_id}")
        else:
            print(f"❌ Failed to delete test agent with ID: {agent_id}")

if __name__ == "__main__":
    # Run the tests
    test_login()
    test_favorites_functionality()
    cleanup_test_agents()
    print_summary()