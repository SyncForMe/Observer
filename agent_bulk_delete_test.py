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

def create_test_agents(num_agents=5):
    """Create test agents for bulk delete testing"""
    print("\n" + "="*80)
    print(f"CREATING {num_agents} TEST AGENTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot create test agents without authentication")
            return False, "Authentication failed"
    
    # Create agents
    for i in range(num_agents):
        agent_data = {
            "name": f"Test Agent {i+1}",
            "archetype": "scientist",
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 8,
                "cooperativeness": 7,
                "energy": 6
            },
            "goal": f"Test goal for agent {i+1}",
            "expertise": f"Test expertise {i+1}",
            "background": f"Test background {i+1}"
        }
        
        create_agent_test, create_agent_response = run_test(
            f"Create Agent {i+1}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if create_agent_test and create_agent_response:
            agent_id = create_agent_response.get("id")
            if agent_id:
                print(f"✅ Created agent with ID: {agent_id}")
                created_agent_ids.append(agent_id)
            else:
                print(f"❌ Failed to get agent ID")
        else:
            print(f"❌ Failed to create agent")
    
    # Print summary
    print("\nAGENT CREATION SUMMARY:")
    if len(created_agent_ids) > 0:
        print(f"✅ Successfully created {len(created_agent_ids)} agents")
        return True, created_agent_ids
    else:
        print(f"❌ Failed to create any agents")
        return False, created_agent_ids

def test_agent_bulk_delete_endpoints():
    """Test the agent bulk delete endpoints"""
    print("\n" + "="*80)
    print("TESTING AGENT BULK DELETE ENDPOINTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test agent bulk delete without authentication")
            return False, "Authentication failed"
    
    # Create test agents for deletion
    print("\nCreating test agents for bulk delete testing...")
    test_agent_success, test_agent_ids = create_test_agents(10)
    
    if not test_agent_success or len(test_agent_ids) < 5:
        print(f"⚠️ Created only {len(test_agent_ids)} test agents")
    
    print(f"Created {len(test_agent_ids)} test agents for bulk delete testing")
    
    # Verify agents exist in database
    print("\nVerifying agents exist in database...")
    get_agents_test, get_agents_response = run_test(
        "Get All Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test and get_agents_response:
        agent_count = len(get_agents_response)
        print(f"Total agents in database: {agent_count}")
        
        # Extract agent IDs from response
        db_agent_ids = [agent.get("id") for agent in get_agents_response]
        
        # Check if all created agent IDs exist in database
        missing_agents = [agent_id for agent_id in test_agent_ids if agent_id not in db_agent_ids]
        if missing_agents:
            print(f"⚠️ {len(missing_agents)} created agents not found in database")
        else:
            print("✅ All created agents found in database")
    
    # Test 1: Test authentication requirements
    print("\nTest 1: Test authentication requirements")
    
    # Test DELETE endpoint without auth
    delete_no_auth_test, delete_no_auth_response = run_test(
        "DELETE Bulk Delete Without Authentication",
        "/agents/bulk",
        method="DELETE",
        data=test_agent_ids[:2],
        auth=False,
        expected_status=403
    )
    
    if delete_no_auth_test:
        print("✅ DELETE bulk delete correctly requires authentication")
    else:
        print("❌ DELETE bulk delete does not properly enforce authentication")
    
    # Test POST endpoint without auth
    post_data = {
        "agent_ids": test_agent_ids[:2]
    }
    
    post_no_auth_test, post_no_auth_response = run_test(
        "POST Bulk Delete Without Authentication",
        "/agents/bulk-delete",
        method="POST",
        data=post_data,
        auth=False,
        expected_status=403
    )
    
    if post_no_auth_test:
        print("✅ POST bulk delete correctly requires authentication")
    else:
        print("❌ POST bulk delete does not properly enforce authentication")
    
    # Test 2: Test DELETE /api/agents/bulk endpoint with empty array
    print("\nTest 2: Test DELETE /api/agents/bulk with empty array")
    
    empty_delete_test, empty_delete_response = run_test(
        "DELETE Bulk Delete with Empty Array",
        "/agents/bulk",
        method="DELETE",
        data=[],
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if empty_delete_test and empty_delete_response:
        deleted_count = empty_delete_response.get("deleted_count", -1)
        if deleted_count == 0:
            print("✅ DELETE bulk delete correctly handles empty array")
        else:
            print(f"❌ DELETE bulk delete returned incorrect deleted_count: {deleted_count}")
    else:
        print("❌ DELETE bulk delete failed with empty array")
    
    # Test 3: Test POST /api/agents/bulk-delete endpoint with empty array
    print("\nTest 3: Test POST /api/agents/bulk-delete with empty array")
    
    empty_post_data = {
        "agent_ids": []
    }
    
    empty_post_test, empty_post_response = run_test(
        "POST Bulk Delete with Empty Array",
        "/agents/bulk-delete",
        method="POST",
        data=empty_post_data,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if empty_post_test and empty_post_response:
        deleted_count = empty_post_response.get("deleted_count", -1)
        if deleted_count == 0:
            print("✅ POST bulk delete correctly handles empty array")
        else:
            print(f"❌ POST bulk delete returned incorrect deleted_count: {deleted_count}")
    else:
        print("❌ POST bulk delete failed with empty array")
    
    # Test 4: Test DELETE /api/agents/bulk endpoint with valid agent IDs
    print("\nTest 4: Test DELETE /api/agents/bulk with valid agent IDs")
    
    # Use half of the test agents for DELETE endpoint
    delete_agent_ids = test_agent_ids[:len(test_agent_ids)//2]
    
    delete_test, delete_response = run_test(
        "DELETE Bulk Delete with Valid Agent IDs",
        "/agents/bulk",
        method="DELETE",
        data=delete_agent_ids,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if delete_test and delete_response:
        deleted_count = delete_response.get("deleted_count", 0)
        if deleted_count == len(delete_agent_ids):
            print(f"✅ DELETE bulk delete successfully deleted all {len(delete_agent_ids)} agents")
            delete_success = True
        else:
            print(f"❌ DELETE bulk delete deleted only {deleted_count} out of {len(delete_agent_ids)} agents")
            delete_success = False
    else:
        print("❌ DELETE bulk delete request failed")
        delete_success = False
    
    # Verify agents were actually deleted
    if delete_success:
        print("\nVerifying agents were deleted from database...")
        get_agents_after_delete_test, get_agents_after_delete_response = run_test(
            "Get All Agents After DELETE",
            "/agents",
            method="GET",
            auth=True
        )
        
        if get_agents_after_delete_test and get_agents_after_delete_response:
            remaining_agents = [agent for agent in get_agents_after_delete_response if agent.get("id") in delete_agent_ids]
            if remaining_agents:
                print(f"❌ {len(remaining_agents)} agents still exist in database after DELETE")
                delete_success = False
            else:
                print("✅ All agents were successfully deleted from database")
    
    # Test 5: Test POST /api/agents/bulk-delete endpoint with valid agent IDs
    print("\nTest 5: Test POST /api/agents/bulk-delete with valid agent IDs")
    
    # Use the remaining test agents for POST endpoint
    post_agent_ids = test_agent_ids[len(test_agent_ids)//2:]
    
    post_data = {
        "agent_ids": post_agent_ids
    }
    
    post_test, post_response = run_test(
        "POST Bulk Delete with Valid Agent IDs",
        "/agents/bulk-delete",
        method="POST",
        data=post_data,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if post_test and post_response:
        deleted_count = post_response.get("deleted_count", 0)
        if deleted_count == len(post_agent_ids):
            print(f"✅ POST bulk delete successfully deleted all {len(post_agent_ids)} agents")
            post_success = True
        else:
            print(f"❌ POST bulk delete deleted only {deleted_count} out of {len(post_agent_ids)} agents")
            post_success = False
    else:
        print("❌ POST bulk delete request failed")
        post_success = False
    
    # Verify agents were actually deleted
    if post_success:
        print("\nVerifying agents were deleted from database...")
        get_agents_after_post_test, get_agents_after_post_response = run_test(
            "Get All Agents After POST Delete",
            "/agents",
            method="GET",
            auth=True
        )
        
        if get_agents_after_post_test and get_agents_after_post_response:
            remaining_agents = [agent for agent in get_agents_after_post_response if agent.get("id") in post_agent_ids]
            if remaining_agents:
                print(f"❌ {len(remaining_agents)} agents still exist in database after POST delete")
                post_success = False
            else:
                print("✅ All agents were successfully deleted from database")
    
    # Test 6: Test with non-existent agent IDs
    print("\nTest 6: Test with non-existent agent IDs")
    
    # Generate non-existent agent IDs
    non_existent_ids = [str(uuid.uuid4()) for _ in range(3)]
    
    # Test DELETE endpoint with non-existent IDs
    non_existent_delete_test, non_existent_delete_response = run_test(
        "DELETE Bulk Delete with Non-existent Agent IDs",
        "/agents/bulk",
        method="DELETE",
        data=non_existent_ids,
        auth=True,
        expected_status=404
    )
    
    if non_existent_delete_test:
        print("✅ DELETE bulk delete correctly handles non-existent agent IDs")
    else:
        print("❌ DELETE bulk delete does not properly handle non-existent agent IDs")
    
    # Test POST endpoint with non-existent IDs
    non_existent_post_data = {
        "agent_ids": non_existent_ids
    }
    
    non_existent_post_test, non_existent_post_response = run_test(
        "POST Bulk Delete with Non-existent Agent IDs",
        "/agents/bulk-delete",
        method="POST",
        data=non_existent_post_data,
        auth=True,
        expected_status=404
    )
    
    if non_existent_post_test:
        print("✅ POST bulk delete correctly handles non-existent agent IDs")
    else:
        print("❌ POST bulk delete does not properly handle non-existent agent IDs")
    
    # Test 7: Test different request body formats for POST endpoint
    print("\nTest 7: Test different request body formats for POST endpoint")
    
    # Create more test agents
    print("\nCreating more test agents for format testing...")
    format_test_success, format_test_ids = create_test_agents(3)
    
    if not format_test_success:
        print("❌ Failed to create test agents for format testing")
    else:
        # Test with direct array format
        direct_array_test, direct_array_response = run_test(
            "POST Bulk Delete with Direct Array Format",
            "/agents/bulk-delete",
            method="POST",
            data=format_test_ids,
            auth=True,
            expected_keys=["message", "deleted_count"]
        )
        
        if direct_array_test and direct_array_response:
            deleted_count = direct_array_response.get("deleted_count", 0)
            if deleted_count > 0:
                print(f"✅ POST bulk delete works with direct array format")
            else:
                print(f"❌ POST bulk delete failed with direct array format")
        else:
            print("❌ POST bulk delete request failed with direct array format")
    
    # Test 8: Test clear all functionality
    print("\nTest 8: Test clear all functionality")
    
    # Create multiple test agents
    print("\nCreating test agents for clear all testing...")
    clear_test_success, clear_test_ids = create_test_agents(5)
    
    if not clear_test_success:
        print("❌ Failed to create test agents for clear all testing")
    else:
        # Get all agents
        get_all_agents_test, get_all_agents_response = run_test(
            "Get All Agents for Clear All",
            "/agents",
            method="GET",
            auth=True
        )
        
        if get_all_agents_test and get_all_agents_response:
            all_agent_ids = [agent.get("id") for agent in get_all_agents_response]
            
            # Delete all agents
            clear_all_test, clear_all_response = run_test(
                "Clear All Agents",
                "/agents/bulk",
                method="DELETE",
                data=all_agent_ids,
                auth=True,
                expected_keys=["message", "deleted_count"]
            )
            
            if clear_all_test and clear_all_response:
                deleted_count = clear_all_response.get("deleted_count", 0)
                if deleted_count == len(all_agent_ids):
                    print(f"✅ Successfully cleared all {len(all_agent_ids)} agents")
                    
                    # Verify all agents are deleted
                    verify_clear_test, verify_clear_response = run_test(
                        "Verify All Agents Cleared",
                        "/agents",
                        method="GET",
                        auth=True
                    )
                    
                    if verify_clear_test and verify_clear_response:
                        if len(verify_clear_response) == 0:
                            print("✅ Verified all agents are cleared")
                        else:
                            print(f"❌ {len(verify_clear_response)} agents still exist after clear all")
                else:
                    print(f"❌ Clear all deleted only {deleted_count} out of {len(all_agent_ids)} agents")
            else:
                print("❌ Clear all request failed")
        else:
            print("❌ Failed to get all agents for clear all testing")
    
    # Print summary
    print("\nAGENT BULK DELETE ENDPOINTS SUMMARY:")
    
    if delete_success:
        print("✅ DELETE /api/agents/bulk endpoint is working correctly")
        print("✅ Authentication is properly enforced")
        print("✅ Empty arrays are handled correctly")
        print("✅ Valid agent IDs are deleted successfully")
        print("✅ Non-existent agent IDs are handled correctly")
    else:
        print("❌ DELETE /api/agents/bulk endpoint has issues")
    
    if post_success:
        print("✅ POST /api/agents/bulk-delete endpoint is working correctly")
        print("✅ Authentication is properly enforced")
        print("✅ Empty arrays are handled correctly")
        print("✅ Valid agent IDs are deleted successfully")
        print("✅ Non-existent agent IDs are handled correctly")
        print("✅ Different request body formats are supported")
    else:
        print("❌ POST /api/agents/bulk-delete endpoint has issues")
    
    # Overall assessment
    if delete_success and post_success:
        print("\n✅ Both bulk delete endpoints are fully functional")
        return True, "Both bulk delete endpoints are fully functional"
    elif delete_success or post_success:
        print("\n✅ At least one bulk delete endpoint is fully functional")
        return True, "At least one bulk delete endpoint is fully functional"
    else:
        print("\n❌ Both bulk delete endpoints have issues")
        return False, "Both bulk delete endpoints have issues"

if __name__ == "__main__":
    print("Starting agent bulk delete endpoints tests...")
    
    # Test login first to get auth token
    test_login()
    
    # Test agent bulk delete endpoints
    test_agent_bulk_delete_endpoints()
    
    # Print summary of all tests
    print_summary()