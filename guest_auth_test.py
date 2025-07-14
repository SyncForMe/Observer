#!/usr/bin/env python3
"""
Guest Authentication Flow Test Script

This script tests the guest authentication flow and agent endpoints to verify they work correctly:
1. Test the /auth/test-login endpoint to ensure it returns a valid token
2. Test the /api/simulation/state endpoint with the guest token
3. Test the /api/agents endpoint with the guest token (both GET and POST)
4. Verify that guest users can access agent-related endpoints

This addresses the 401 errors reported in the Agent Library functionality.
"""

import requests
import json
import time
import os
import sys
import uuid
from dotenv import load_dotenv
from datetime import datetime

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
            "result": result,
            "response_time": response_time
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

def test_guest_authentication():
    """Test the guest authentication flow"""
    print("\n" + "="*80)
    print("TESTING GUEST AUTHENTICATION FLOW")
    print("="*80)
    
    # Test 1: Test the /auth/test-login endpoint
    print("\nTest 1: Testing /auth/test-login endpoint (Continue as Guest)")
    
    guest_test, guest_response = run_test(
        "Guest Authentication - /auth/test-login",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not guest_test or not guest_response:
        print("❌ CRITICAL: Guest authentication failed - cannot proceed with other tests")
        return False, None, "Guest authentication failed"
    
    # Extract guest token and user info
    guest_token = guest_response.get("access_token")
    guest_user = guest_response.get("user", {})
    guest_user_id = guest_user.get("id")
    
    print(f"✅ Guest authentication successful")
    print(f"Guest User ID: {guest_user_id}")
    print(f"Guest Token: {guest_token[:50]}..." if guest_token else "No token")
    
    # Verify token structure
    if guest_token:
        print(f"Token Type: {guest_response.get('token_type', 'Unknown')}")
        print(f"User Name: {guest_user.get('name', 'Unknown')}")
        print(f"User Email: {guest_user.get('email', 'Unknown')}")
    
    return True, guest_token, guest_user_id

def test_simulation_state_with_guest_token(guest_token):
    """Test the /api/simulation/state endpoint with guest token"""
    print("\n" + "="*80)
    print("TESTING /api/simulation/state WITH GUEST TOKEN")
    print("="*80)
    
    # Test 2: Test /api/simulation/state endpoint with guest token
    print("\nTest 2: Testing /api/simulation/state with guest token")
    
    sim_state_test, sim_state_response = run_test(
        "Simulation State with Guest Token",
        "/simulation/state",
        method="GET",
        auth_token=guest_token,
        expected_keys=["current_day", "current_time_period", "scenario", "is_active"]
    )
    
    if sim_state_test and sim_state_response:
        print("✅ Successfully accessed /api/simulation/state with guest token")
        print(f"Simulation State: {json.dumps(sim_state_response, indent=2)}")
        
        # Verify expected fields
        expected_fields = ["current_day", "current_time_period", "scenario", "is_active", "user_id"]
        missing_fields = [field for field in expected_fields if field not in sim_state_response]
        
        if missing_fields:
            print(f"⚠️ Missing fields in simulation state: {missing_fields}")
        else:
            print("✅ All expected fields present in simulation state")
        
        return True, sim_state_response
    else:
        print("❌ CRITICAL: Failed to access /api/simulation/state with guest token")
        print("This indicates a 401 authentication error for guest users")
        return False, None

def test_agents_endpoints_with_guest_token(guest_token, guest_user_id):
    """Test the /api/agents endpoints with guest token"""
    print("\n" + "="*80)
    print("TESTING /api/agents ENDPOINTS WITH GUEST TOKEN")
    print("="*80)
    
    # Test 3: Test GET /api/agents endpoint with guest token
    print("\nTest 3: Testing GET /api/agents with guest token")
    
    get_agents_test, get_agents_response = run_test(
        "GET /api/agents with Guest Token",
        "/agents",
        method="GET",
        auth_token=guest_token
    )
    
    if get_agents_test:
        print("✅ Successfully accessed GET /api/agents with guest token")
        agent_count = len(get_agents_response) if get_agents_response else 0
        print(f"Number of agents returned: {agent_count}")
        
        if agent_count > 0:
            print("Sample agent structure:")
            sample_agent = get_agents_response[0]
            for key in sample_agent.keys():
                print(f"  - {key}: {sample_agent[key]}")
        else:
            print("No agents found (this is expected for new guest users)")
    else:
        print("❌ CRITICAL: Failed to access GET /api/agents with guest token")
        print("This indicates a 401 authentication error for guest users")
        return False
    
    # Test 4: Test POST /api/agents endpoint with guest token
    print("\nTest 4: Testing POST /api/agents with guest token")
    
    # Create a test agent
    test_agent_data = {
        "name": f"Test Agent {uuid.uuid4()}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 5
        },
        "goal": "Test the agent creation functionality for guest users",
        "expertise": "Software Testing and Quality Assurance",
        "background": "Experienced in testing authentication flows and API endpoints",
        "memory_summary": "Created for testing guest authentication flow",
        "avatar_prompt": "A professional software tester",
        "avatar_url": ""
    }
    
    post_agents_test, post_agents_response = run_test(
        "POST /api/agents with Guest Token",
        "/agents",
        method="POST",
        data=test_agent_data,
        auth_token=guest_token,
        expected_keys=["id", "name", "archetype"]
    )
    
    created_agent_id = None
    if post_agents_test and post_agents_response:
        print("✅ Successfully created agent with guest token")
        created_agent_id = post_agents_response.get("id")
        print(f"Created Agent ID: {created_agent_id}")
        print(f"Created Agent Name: {post_agents_response.get('name')}")
        
        # Verify user_id is properly set
        agent_user_id = post_agents_response.get("user_id")
        if agent_user_id == guest_user_id:
            print("✅ Agent properly associated with guest user")
        else:
            print(f"❌ Agent user_id mismatch: expected {guest_user_id}, got {agent_user_id}")
    else:
        print("❌ CRITICAL: Failed to create agent with guest token")
        print("This indicates a 401 authentication error for guest users")
        return False
    
    # Test 5: Verify the created agent appears in GET /api/agents
    print("\nTest 5: Verifying created agent appears in GET /api/agents")
    
    get_agents_after_create_test, get_agents_after_create_response = run_test(
        "GET /api/agents after creation",
        "/agents",
        method="GET",
        auth_token=guest_token
    )
    
    if get_agents_after_create_test and get_agents_after_create_response:
        agent_count_after = len(get_agents_after_create_response)
        print(f"Number of agents after creation: {agent_count_after}")
        
        # Check if our created agent is in the list
        created_agent_found = False
        for agent in get_agents_after_create_response:
            if agent.get("id") == created_agent_id:
                created_agent_found = True
                print("✅ Created agent found in agents list")
                break
        
        if not created_agent_found:
            print("❌ Created agent not found in agents list")
            return False
    else:
        print("❌ Failed to retrieve agents after creation")
        return False
    
    # Test 6: Test agent update functionality
    print("\nTest 6: Testing PUT /api/agents/{agent_id} with guest token")
    
    if created_agent_id:
        update_data = {
            "name": f"Updated Test Agent {uuid.uuid4()}",
            "goal": "Updated goal for testing purposes"
        }
        
        put_agent_test, put_agent_response = run_test(
            "PUT /api/agents/{agent_id} with Guest Token",
            f"/agents/{created_agent_id}",
            method="PUT",
            data=update_data,
            auth_token=guest_token,
            expected_keys=["id", "name"]
        )
        
        if put_agent_test and put_agent_response:
            print("✅ Successfully updated agent with guest token")
            updated_name = put_agent_response.get("name")
            print(f"Updated Agent Name: {updated_name}")
        else:
            print("❌ Failed to update agent with guest token")
    
    # Test 7: Test agent deletion functionality
    print("\nTest 7: Testing DELETE /api/agents/{agent_id} with guest token")
    
    if created_agent_id:
        delete_agent_test, delete_agent_response = run_test(
            "DELETE /api/agents/{agent_id} with Guest Token",
            f"/agents/{created_agent_id}",
            method="DELETE",
            auth_token=guest_token,
            expected_keys=["message"]
        )
        
        if delete_agent_test and delete_agent_response:
            print("✅ Successfully deleted agent with guest token")
            print(f"Delete response: {delete_agent_response.get('message')}")
        else:
            print("❌ Failed to delete agent with guest token")
    
    return True

def test_additional_agent_endpoints(guest_token):
    """Test additional agent-related endpoints"""
    print("\n" + "="*80)
    print("TESTING ADDITIONAL AGENT-RELATED ENDPOINTS")
    print("="*80)
    
    # Test 8: Test /api/archetypes endpoint
    print("\nTest 8: Testing /api/archetypes endpoint")
    
    archetypes_test, archetypes_response = run_test(
        "GET /api/archetypes",
        "/archetypes",
        method="GET",
        auth_token=guest_token
    )
    
    if archetypes_test and archetypes_response:
        print("✅ Successfully accessed /api/archetypes")
        archetype_count = len(archetypes_response)
        print(f"Number of archetypes: {archetype_count}")
        
        if archetype_count > 0:
            print("Available archetypes:")
            for archetype_key, archetype_data in archetypes_response.items():
                print(f"  - {archetype_key}: {archetype_data.get('name', 'Unknown')}")
    else:
        print("❌ Failed to access /api/archetypes")
    
    # Test 9: Test /api/saved-agents endpoint
    print("\nTest 9: Testing /api/saved-agents endpoint")
    
    saved_agents_test, saved_agents_response = run_test(
        "GET /api/saved-agents",
        "/saved-agents",
        method="GET",
        auth_token=guest_token
    )
    
    if saved_agents_test:
        print("✅ Successfully accessed /api/saved-agents")
        saved_count = len(saved_agents_response) if saved_agents_response else 0
        print(f"Number of saved agents: {saved_count}")
    else:
        print("❌ Failed to access /api/saved-agents")
    
    # Test 10: Test bulk operations
    print("\nTest 10: Testing /api/agents/bulk-delete endpoint")
    
    # Create a test agent first
    test_agent_data = {
        "name": f"Bulk Delete Test Agent {uuid.uuid4()}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 5
        },
        "goal": "Test bulk delete functionality",
        "expertise": "Testing",
        "background": "Test agent for bulk operations"
    }
    
    create_for_bulk_test, create_for_bulk_response = run_test(
        "Create agent for bulk delete test",
        "/agents",
        method="POST",
        data=test_agent_data,
        auth_token=guest_token
    )
    
    if create_for_bulk_test and create_for_bulk_response:
        bulk_agent_id = create_for_bulk_response.get("id")
        
        # Test bulk delete
        bulk_delete_data = {
            "agent_ids": [bulk_agent_id]
        }
        
        bulk_delete_test, bulk_delete_response = run_test(
            "POST /api/agents/bulk-delete",
            "/agents/bulk-delete",
            method="POST",
            data=bulk_delete_data,
            auth_token=guest_token,
            expected_keys=["message", "deleted_count"]
        )
        
        if bulk_delete_test and bulk_delete_response:
            print("✅ Successfully performed bulk delete with guest token")
            deleted_count = bulk_delete_response.get("deleted_count", 0)
            print(f"Deleted {deleted_count} agents")
        else:
            print("❌ Failed to perform bulk delete with guest token")

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"GUEST AUTHENTICATION TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        response_time = test.get("response_time", 0)
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']}) - {response_time:.3f}s")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    
    # Specific analysis for guest authentication issues
    critical_failures = []
    for test in test_results["tests"]:
        if test["result"] == "FAILED" and test["status_code"] == 401:
            critical_failures.append(test["name"])
    
    if critical_failures:
        print("\n🚨 CRITICAL AUTHENTICATION FAILURES DETECTED:")
        for failure in critical_failures:
            print(f"  - {failure}")
        print("\nThese failures indicate that guest users are getting 401 errors")
        print("when trying to access agent-related endpoints, which explains")
        print("why the Agent Library is not working for guest users.")
    else:
        print("\n✅ No critical authentication failures detected")
        print("Guest users should be able to access all agent-related endpoints")
    
    print("="*80)

def main():
    """Main test execution function"""
    print("="*80)
    print("GUEST AUTHENTICATION FLOW AND AGENT ENDPOINTS TEST")
    print("="*80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API URL: {API_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Test guest authentication
    guest_auth_success, guest_token, guest_user_id = test_guest_authentication()
    
    if not guest_auth_success:
        print("\n❌ CRITICAL: Guest authentication failed - cannot proceed with other tests")
        print_summary()
        return False
    
    # Step 2: Test simulation state endpoint
    sim_state_success, sim_state_data = test_simulation_state_with_guest_token(guest_token)
    
    # Step 3: Test agents endpoints
    agents_success = test_agents_endpoints_with_guest_token(guest_token, guest_user_id)
    
    # Step 4: Test additional agent-related endpoints
    test_additional_agent_endpoints(guest_token)
    
    # Print final summary
    print_summary()
    
    # Return overall success status
    return test_results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)