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

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth_token=None, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
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
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        
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

def test_agent_library_enhanced_button():
    """Test the enhanced button functionality for agent management"""
    print("\n" + "="*80)
    print("TESTING AGENT LIBRARY ENHANCED BUTTON FUNCTIONALITY")
    print("="*80)
    
    # Step 1: Test user authentication (email/password)
    print("\nStep 1: Test user authentication (email/password)")
    
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
    
    if not login_test or not login_response:
        print("❌ Login failed, trying test login")
        test_login_test, test_login_response = run_test(
            "Test Login Endpoint",
            "/auth/test-login",
            method="POST",
            expected_keys=["access_token", "token_type", "user"]
        )
        
        if not test_login_test or not test_login_response:
            print("❌ Both login methods failed, cannot continue testing")
            return False
        
        auth_token = test_login_response.get("access_token")
        user_id = test_login_response.get("user", {}).get("id")
    else:
        auth_token = login_response.get("access_token")
        user_id = login_response.get("user", {}).get("id")
    
    print(f"✅ Authentication successful. User ID: {user_id}")
    
    # Step 2: Test GET /api/agents endpoint with authentication
    print("\nStep 2: Test GET /api/agents endpoint with authentication")
    
    get_agents_test, get_agents_response = run_test(
        "Get Agents With Authentication",
        "/agents",
        method="GET",
        auth_token=auth_token
    )
    
    if not get_agents_test:
        print("❌ Failed to get agents with authentication")
        return False
    
    initial_agent_count = len(get_agents_response) if get_agents_response else 0
    print(f"✅ Successfully retrieved agents. Initial count: {initial_agent_count}")
    
    # Step 3: Test POST /api/agents endpoint to add an agent
    print("\nStep 3: Test POST /api/agents endpoint to add an agent")
    
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
        "goal": "Test the agent management functionality",
        "expertise": "Software testing and quality assurance",
        "background": "Experienced in automated testing and API validation",
        "avatar_prompt": "professional software tester, glasses, lab coat"
    }
    
    create_agent_test, create_agent_response = run_test(
        "Create New Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth_token=auth_token,
        expected_keys=["id", "name", "archetype"]
    )
    
    if not create_agent_test or not create_agent_response:
        print("❌ Failed to create new agent")
        return False
    
    agent_id = create_agent_response.get("id")
    print(f"✅ Successfully created new agent with ID: {agent_id}")
    
    # Step 4: Verify agent was added to the list
    print("\nStep 4: Verify agent was added to the list")
    
    get_updated_agents_test, get_updated_agents_response = run_test(
        "Get Updated Agents List",
        "/agents",
        method="GET",
        auth_token=auth_token
    )
    
    if not get_updated_agents_test or not get_updated_agents_response:
        print("❌ Failed to get updated agents list")
        return False
    
    updated_agent_count = len(get_updated_agents_response)
    agent_found = any(a.get("id") == agent_id for a in get_updated_agents_response)
    
    if updated_agent_count > initial_agent_count and agent_found:
        print(f"✅ Agent count increased from {initial_agent_count} to {updated_agent_count}")
        print(f"✅ Newly created agent found in the list")
    else:
        print(f"❌ Agent count did not increase or agent not found")
        return False
    
    # Step 5: Test adding the same agent again (Add Again functionality)
    print("\nStep 5: Test adding the same agent again (Add Again functionality)")
    
    create_again_test, create_again_response = run_test(
        "Create Same Agent Again",
        "/agents",
        method="POST",
        data=agent_data,
        auth_token=auth_token,
        expected_keys=["id", "name", "archetype"]
    )
    
    if not create_again_test or not create_again_response:
        print("❌ Failed to create agent again")
        return False
    
    second_agent_id = create_again_response.get("id")
    
    if second_agent_id != agent_id:
        print(f"✅ Successfully created agent again with different ID: {second_agent_id}")
    else:
        print(f"❌ Created agent has the same ID as the original")
        return False
    
    # Step 6: Verify both instances exist
    print("\nStep 6: Verify both instances exist")
    
    get_both_agents_test, get_both_agents_response = run_test(
        "Get Agents After Second Creation",
        "/agents",
        method="GET",
        auth_token=auth_token
    )
    
    if not get_both_agents_test or not get_both_agents_response:
        print("❌ Failed to get agents after second creation")
        return False
    
    both_agent_count = len(get_both_agents_response)
    first_agent_found = any(a.get("id") == agent_id for a in get_both_agents_response)
    second_agent_found = any(a.get("id") == second_agent_id for a in get_both_agents_response)
    
    if both_agent_count > updated_agent_count and first_agent_found and second_agent_found:
        print(f"✅ Agent count increased to {both_agent_count}")
        print(f"✅ Both agent instances found in the list")
    else:
        print(f"❌ Agent count did not increase or both agents not found")
        return False
    
    # Step 7: Test removing an agent
    print("\nStep 7: Test removing an agent")
    
    delete_agent_test, delete_agent_response = run_test(
        "Delete Agent",
        f"/agents/{agent_id}",
        method="DELETE",
        auth_token=auth_token,
        expected_keys=["message"]
    )
    
    if not delete_agent_test or not delete_agent_response:
        print("❌ Failed to delete agent")
        return False
    
    print(f"✅ Successfully deleted agent: {agent_id}")
    
    # Step 8: Verify agent was removed
    print("\nStep 8: Verify agent was removed")
    
    get_after_delete_test, get_after_delete_response = run_test(
        "Get Agents After Delete",
        "/agents",
        method="GET",
        auth_token=auth_token
    )
    
    if not get_after_delete_test or not get_after_delete_response:
        print("❌ Failed to get agents after deletion")
        return False
    
    after_delete_count = len(get_after_delete_response)
    deleted_agent_found = any(a.get("id") == agent_id for a in get_after_delete_response)
    
    if after_delete_count < both_agent_count and not deleted_agent_found:
        print(f"✅ Agent count decreased to {after_delete_count}")
        print(f"✅ Deleted agent not found in the list")
    else:
        print(f"❌ Agent count did not decrease or deleted agent still found")
        return False
    
    # Step 9: Test authentication requirement
    print("\nStep 9: Test authentication requirement")
    
    no_auth_test, _ = run_test(
        "Get Agents Without Authentication",
        "/agents",
        method="GET",
        expected_status=403  # Should fail with 403 Forbidden
    )
    
    if no_auth_test:
        print("✅ Authentication is properly enforced for GET /agents endpoint")
    else:
        print("❌ GET /agents endpoint does not properly enforce authentication")
        return False
    
    # Print summary
    print("\nAGENT LIBRARY ENHANCED BUTTON FUNCTIONALITY SUMMARY:")
    
    print("✅ Authentication is working correctly")
    print("✅ GET /agents endpoint returns the expected data")
    print("✅ POST /agents endpoint creates agents successfully")
    print("✅ Add Again functionality works correctly")
    print("✅ DELETE /agents/{agent_id} endpoint deletes agents successfully")
    print("✅ Authentication is properly enforced")
    
    return True

if __name__ == "__main__":
    print("Starting agent library enhanced button functionality tests...")
    
    # Run the tests
    test_agent_library_enhanced_button()
    
    # Print overall summary
    print_summary()