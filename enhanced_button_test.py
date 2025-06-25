#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

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

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

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
test_user_email = f"test.user.{uuid.uuid4()}@example.com"
test_user_password = "securePassword123"
test_user_name = "Test User"

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

def test_enhanced_button_functionality():
    """Test the enhanced button functionality for agent management"""
    print("\n" + "="*80)
    print("TESTING ENHANCED BUTTON FUNCTIONALITY FOR AGENT MANAGEMENT")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test enhanced button functionality without authentication")
            return False, "Authentication failed"
    
    # Test 1: Get agents without authentication
    print("\nTest 1: Get agents without authentication")
    
    no_auth_test, no_auth_response = run_test(
        "Get Agents Without Authentication",
        "/agents",
        method="GET",
        auth=False,
        expected_status=403  # Should fail with 403 Forbidden
    )
    
    if no_auth_test:
        print("✅ Authentication is properly enforced for GET /agents endpoint")
    else:
        print("❌ GET /agents endpoint does not properly enforce authentication")
    
    # Test 2: Get agents with authentication
    print("\nTest 2: Get agents with authentication")
    
    get_agents_test, get_agents_response = run_test(
        "Get Agents With Authentication",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test:
        print(f"✅ Successfully retrieved agents with authentication")
        initial_agent_count = len(get_agents_response) if get_agents_response else 0
        print(f"Initial agent count: {initial_agent_count}")
    else:
        print("❌ Failed to retrieve agents with authentication")
        initial_agent_count = 0
    
    # Test 3: Create a new agent
    print("\nTest 3: Create a new agent")
    
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 8
        },
        "goal": "Test the enhanced button functionality",
        "expertise": "Software testing and quality assurance",
        "background": "Experienced in automated testing and API validation",
        "avatar_prompt": "professional software tester, glasses, lab coat"
    }
    
    create_agent_test, create_agent_response = run_test(
        "Create New Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True,
        expected_keys=["id", "name", "archetype"]
    )
    
    if create_agent_test and create_agent_response:
        print(f"✅ Successfully created new agent: {create_agent_response.get('name')}")
        agent_id = create_agent_response.get("id")
        if agent_id:
            created_agent_ids.append(agent_id)
            print(f"Agent ID: {agent_id}")
        else:
            print("❌ Failed to get agent ID from response")
    else:
        print("❌ Failed to create new agent")
    
    # Test 4: Verify agent was added to the list
    print("\nTest 4: Verify agent was added to the list")
    
    get_updated_agents_test, get_updated_agents_response = run_test(
        "Get Updated Agents List",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_updated_agents_test and get_updated_agents_response:
        updated_agent_count = len(get_updated_agents_response)
        print(f"Updated agent count: {updated_agent_count}")
        
        if updated_agent_count > initial_agent_count:
            print(f"✅ Agent count increased from {initial_agent_count} to {updated_agent_count}")
            
            # Find the newly created agent in the list
            new_agent = next((a for a in get_updated_agents_response if a.get("id") in created_agent_ids), None)
            if new_agent:
                print(f"✅ Found newly created agent in the list: {new_agent.get('name')}")
            else:
                print("❌ Could not find newly created agent in the list")
        else:
            print(f"❌ Agent count did not increase after creation")
    else:
        print("❌ Failed to retrieve updated agents list")
    
    # Test 5: Test adding the same agent multiple times (Add Again functionality)
    print("\nTest 5: Test adding the same agent multiple times (Add Again functionality)")
    
    # Create a new agent with a distinctive name
    duplicate_agent_name = f"Duplicate Test Agent {uuid.uuid4().hex[:8]}"
    duplicate_agent_data = {
        "name": duplicate_agent_name,
        "archetype": "researcher",
        "personality": {
            "extroversion": 3,
            "optimism": 6,
            "curiosity": 10,
            "cooperativeness": 5,
            "energy": 7
        },
        "goal": "Test the Add Again functionality",
        "expertise": "Duplicate detection and management",
        "background": "Specialized in identifying and handling duplicate entries",
        "avatar_prompt": "focused researcher, analytical expression"
    }
    
    # Add the agent first time
    create_dup_agent_test, create_dup_agent_response = run_test(
        "Create Duplicate Agent (First Time)",
        "/agents",
        method="POST",
        data=duplicate_agent_data,
        auth=True,
        expected_keys=["id", "name", "archetype"]
    )
    
    if create_dup_agent_test and create_dup_agent_response:
        print(f"✅ Successfully created duplicate agent (first time): {create_dup_agent_response.get('name')}")
        dup_agent_id = create_dup_agent_response.get("id")
        if dup_agent_id:
            created_agent_ids.append(dup_agent_id)
            print(f"Duplicate Agent ID (first): {dup_agent_id}")
            
            # Add the same agent again (second time)
            create_dup_agent2_test, create_dup_agent2_response = run_test(
                "Create Duplicate Agent (Second Time)",
                "/agents",
                method="POST",
                data=duplicate_agent_data,
                auth=True,
                expected_keys=["id", "name", "archetype"]
            )
            
            if create_dup_agent2_test and create_dup_agent2_response:
                print(f"✅ Successfully created duplicate agent (second time): {create_dup_agent2_response.get('name')}")
                dup_agent2_id = create_dup_agent2_response.get("id")
                if dup_agent2_id:
                    created_agent_ids.append(dup_agent2_id)
                    print(f"Duplicate Agent ID (second): {dup_agent2_id}")
                    
                    # Verify both instances exist with the same name
                    get_dups_test, get_dups_response = run_test(
                        "Get Agents After Duplicate Creation",
                        "/agents",
                        method="GET",
                        auth=True
                    )
                    
                    if get_dups_test and get_dups_response:
                        dup_agents = [a for a in get_dups_response if a.get("name") == duplicate_agent_name]
                        if len(dup_agents) >= 2:
                            print(f"✅ Found {len(dup_agents)} instances of the duplicate agent")
                            
                            # Verify they have different IDs
                            dup_ids = [a.get("id") for a in dup_agents]
                            if len(set(dup_ids)) == len(dup_ids):
                                print(f"✅ All duplicate agents have unique IDs")
                            else:
                                print(f"❌ Some duplicate agents have the same ID")
                        else:
                            print(f"❌ Found only {len(dup_agents)} instances of the duplicate agent")
                else:
                    print("❌ Failed to get duplicate agent ID (second) from response")
            else:
                print("❌ Failed to create duplicate agent (second time)")
        else:
            print("❌ Failed to get duplicate agent ID (first) from response")
    else:
        print("❌ Failed to create duplicate agent (first time)")
    
    # Test 6: Delete an agent
    print("\nTest 6: Delete an agent")
    
    if created_agent_ids:
        agent_to_delete = created_agent_ids[0]
        
        delete_agent_test, delete_agent_response = run_test(
            "Delete Agent",
            f"/agents/{agent_to_delete}",
            method="DELETE",
            auth=True,
            expected_keys=["message"]
        )
        
        if delete_agent_test:
            print(f"✅ Successfully deleted agent: {agent_to_delete}")
            created_agent_ids.remove(agent_to_delete)
        else:
            print(f"❌ Failed to delete agent: {agent_to_delete}")
        
        # Verify the agent was deleted
        get_after_delete_test, get_after_delete_response = run_test(
            "Get Agents After Delete",
            "/agents",
            method="GET",
            auth=True
        )
        
        if get_after_delete_test and get_after_delete_response:
            deleted_agent = next((a for a in get_after_delete_response if a.get("id") == agent_to_delete), None)
            if deleted_agent:
                print(f"❌ Agent was not actually deleted from the database")
            else:
                print(f"✅ Agent was successfully deleted from the database")
    else:
        print("❌ No agents available to test deletion")
    
    # Test 7: Try to delete a non-existent agent
    print("\nTest 7: Try to delete a non-existent agent")
    
    non_existent_id = str(uuid.uuid4())
    
    delete_nonexistent_test, delete_nonexistent_response = run_test(
        "Delete Non-existent Agent",
        f"/agents/{non_existent_id}",
        method="DELETE",
        auth=True,
        expected_status=404  # Should return 404 Not Found
    )
    
    if delete_nonexistent_test:
        print(f"✅ Correctly returned 404 for non-existent agent")
    else:
        print(f"❌ Did not handle non-existent agent correctly")
    
    # Test 8: Test user data isolation
    print("\nTest 8: Test user data isolation")
    
    # Create a new test user
    test_user_email_2 = f"test.user.2.{uuid.uuid4()}@example.com"
    test_user_password_2 = "securePassword456"
    test_user_name_2 = "Test User 2"
    
    register_data_2 = {
        "email": test_user_email_2,
        "password": test_user_password_2,
        "name": test_user_name_2
    }
    
    register_test_2, register_response_2 = run_test(
        "Register second test user",
        "/auth/register",
        method="POST",
        data=register_data_2,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if register_test_2 and register_response_2:
        # Store the token for the second user
        auth_token_2 = register_response_2.get("access_token")
        user_data_2 = register_response_2.get("user", {})
        test_user_id_2 = user_data_2.get("id")
        
        print(f"✅ Successfully created second test user with ID: {test_user_id_2}")
        
        # Save original auth token
        original_auth_token = auth_token
        
        # Switch to the second user
        auth_token = auth_token_2
        
        # Try to access the first user's agent
        if len(created_agent_ids) > 0:
            first_user_agent_id = created_agent_ids[0]
            
            get_first_user_agent_test, get_first_user_agent_response = run_test(
                "Get First User's Agent With Second User's Credentials",
                f"/agents/{first_user_agent_id}",
                method="GET",
                auth=True,
                expected_status=404  # Should return 404 Not Found
            )
            
            if get_first_user_agent_test:
                print("✅ Second user cannot access first user's agent")
            else:
                print("❌ Second user can access first user's agent")
            
            # Restore original auth token
            auth_token = original_auth_token
        else:
            print("❌ No agents available to test user data isolation")
            
            # Restore original auth token
            auth_token = original_auth_token
    else:
        print("❌ Failed to create second test user for data isolation testing")
    
    # Print summary
    print("\nENHANCED BUTTON FUNCTIONALITY SUMMARY:")
    
    # Check if all critical tests passed
    auth_enforced = no_auth_test
    get_agents_works = get_agents_test
    create_agent_works = create_agent_test
    add_again_works = create_dup_agent2_test if 'create_dup_agent2_test' in locals() else False
    delete_agent_works = delete_agent_test if 'delete_agent_test' in locals() else False
    data_isolation_works = get_first_user_agent_test if 'get_first_user_agent_test' in locals() else False
    
    if auth_enforced and get_agents_works and create_agent_works and add_again_works and delete_agent_works:
        print("✅ Enhanced button functionality is working correctly!")
        print("✅ Authentication is properly enforced")
        print("✅ GET /agents endpoint returns the expected data")
        print("✅ POST /agents endpoint creates agents successfully")
        print("✅ Add Again functionality works correctly")
        print("✅ DELETE /agents/{agent_id} endpoint deletes agents successfully")
        if data_isolation_works:
            print("✅ User data isolation is working correctly")
        return True, "Enhanced button functionality is working correctly"
    else:
        issues = []
        if not auth_enforced:
            issues.append("Authentication is not properly enforced")
        if not get_agents_works:
            issues.append("GET /agents endpoint is not working correctly")
        if not create_agent_works:
            issues.append("POST /agents endpoint is not working correctly")
        if not add_again_works:
            issues.append("Add Again functionality is not working correctly")
        if not delete_agent_works:
            issues.append("DELETE /agents/{agent_id} endpoint is not working correctly")
        if not data_isolation_works and 'get_first_user_agent_test' in locals():
            issues.append("User data isolation is not working correctly")
        
        print("❌ Enhanced button functionality has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

if __name__ == "__main__":
    print("Starting enhanced button functionality tests...")
    
    # Test login first to get authentication token
    test_login()
    
    # Run the enhanced button functionality tests
    test_enhanced_button_functionality()
    
    # Print overall summary
    print_summary()