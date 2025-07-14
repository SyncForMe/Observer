#!/usr/bin/env python3
"""
Comprehensive test for the bulk delete functionality for the "Clear All" button.

This test script verifies:
1. Create test agents via POST /api/agents (to have agents to clear)
2. Test bulk delete endpoint POST /api/agents/bulk-delete with the agent IDs
3. Verify deletion via GET /api/agents
4. Test edge cases: empty array, non-existent agent IDs, proper error handling

This ensures the "Clear All" button functionality works correctly when users click it 
in the Observatory Agent List.
"""

import requests
import json
import time
import os
import sys
import uuid
from dotenv import load_dotenv

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

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
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

def authenticate():
    """Authenticate and get auth token"""
    global auth_token, test_user_id
    
    # Try using the admin credentials first
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
            return True
        else:
            print("Authentication failed. Cannot proceed with tests.")
            return False
    else:
        # Store the token from email/password login
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        return True

def create_test_agents(num_agents=3):
    """Create test agents for bulk delete testing"""
    print(f"\n{'='*80}\nCREATING {num_agents} TEST AGENTS FOR BULK DELETE TESTING")
    print("="*80)
    
    created_agents = []
    
    # Agent archetypes to use
    archetypes = ["scientist", "artist", "leader", "skeptic", "optimist", "introvert", "adventurer", "mediator", "researcher"]
    
    for i in range(num_agents):
        archetype = archetypes[i % len(archetypes)]
        
        # Create agent data with proper personality structure
        agent_data = {
            "name": f"Test Agent {i+1} - {archetype.title()}",
            "archetype": archetype,
            "personality": {
                "extroversion": 5 + (i % 5),
                "optimism": 5 + (i % 5),
                "curiosity": 5 + (i % 5),
                "cooperativeness": 5 + (i % 5),
                "energy": 5 + (i % 5)
            },
            "goal": f"Test goal for {archetype} agent {i+1}",
            "expertise": f"Test expertise in {archetype} domain",
            "background": f"Test background for {archetype} agent",
            "avatar_prompt": f"Professional {archetype} avatar prompt"
        }
        
        create_test, create_response = run_test(
            f"Create Test Agent {i+1}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            agent_name = create_response.get("name")
            print(f"✅ Created agent: {agent_name} (ID: {agent_id})")
            created_agents.append({
                "id": agent_id,
                "name": agent_name,
                "archetype": archetype
            })
        else:
            print(f"❌ Failed to create test agent {i+1}")
    
    print(f"\nCreated {len(created_agents)} test agents successfully")
    return created_agents

def test_bulk_delete_functionality():
    """Test the bulk delete functionality comprehensively"""
    print(f"\n{'='*80}\nTESTING BULK DELETE FUNCTIONALITY")
    print("="*80)
    
    # Step 1: Create test agents
    print("\nStep 1: Creating test agents")
    test_agents = create_test_agents(3)
    
    if len(test_agents) < 3:
        print(f"❌ Only created {len(test_agents)} agents, expected 3")
        return False
    
    agent_ids = [agent["id"] for agent in test_agents]
    print(f"Agent IDs to delete: {agent_ids}")
    
    # Step 2: Verify agents exist via GET /api/agents
    print("\nStep 2: Verifying agents exist in the system")
    get_agents_test, get_agents_response = run_test(
        "Get All Agents Before Delete",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test and get_agents_response:
        existing_agent_ids = [agent.get("id") for agent in get_agents_response]
        agents_found = [agent_id for agent_id in agent_ids if agent_id in existing_agent_ids]
        
        if len(agents_found) == len(agent_ids):
            print(f"✅ All {len(agent_ids)} test agents found in the system")
        else:
            print(f"❌ Only {len(agents_found)} out of {len(agent_ids)} test agents found")
            return False
    else:
        print("❌ Failed to retrieve agents from the system")
        return False
    
    # Step 3: Test bulk delete endpoint with all agent IDs
    print("\nStep 3: Testing bulk delete with all agent IDs")
    bulk_delete_data = {
        "agent_ids": agent_ids
    }
    
    bulk_delete_test, bulk_delete_response = run_test(
        "Bulk Delete All Test Agents",
        "/agents/bulk-delete",
        method="POST",
        data=bulk_delete_data,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if bulk_delete_test and bulk_delete_response:
        deleted_count = bulk_delete_response.get("deleted_count", 0)
        if deleted_count == len(agent_ids):
            print(f"✅ Successfully deleted all {len(agent_ids)} agents")
        else:
            print(f"❌ Expected to delete {len(agent_ids)} agents, but deleted {deleted_count}")
            return False
    else:
        print("❌ Bulk delete request failed")
        return False
    
    # Step 4: Verify agents are actually deleted
    print("\nStep 4: Verifying agents are deleted from the system")
    get_agents_after_test, get_agents_after_response = run_test(
        "Get All Agents After Delete",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_after_test and get_agents_after_response:
        remaining_agent_ids = [agent.get("id") for agent in get_agents_after_response]
        still_existing = [agent_id for agent_id in agent_ids if agent_id in remaining_agent_ids]
        
        if len(still_existing) == 0:
            print("✅ All test agents successfully deleted from the system")
        else:
            print(f"❌ {len(still_existing)} agents still exist after deletion: {still_existing}")
            return False
    else:
        print("❌ Failed to retrieve agents after deletion")
        return False
    
    return True

def test_edge_cases():
    """Test edge cases for bulk delete functionality"""
    print(f"\n{'='*80}\nTESTING EDGE CASES")
    print("="*80)
    
    # Test Case 1: Empty array
    print("\nTest Case 1: Bulk delete with empty array")
    empty_data = {
        "agent_ids": []
    }
    
    empty_test, empty_response = run_test(
        "Bulk Delete with Empty Array",
        "/agents/bulk-delete",
        method="POST",
        data=empty_data,
        auth=True,
        expected_status=200,
        expected_keys=["message", "deleted_count"]
    )
    
    if empty_test and empty_response:
        deleted_count = empty_response.get("deleted_count", -1)
        if deleted_count == 0:
            print("✅ Empty array handled correctly (deleted 0 agents)")
        else:
            print(f"❌ Empty array returned deleted_count: {deleted_count}, expected 0")
    else:
        print("❌ Empty array test failed")
    
    # Test Case 2: Non-existent agent IDs
    print("\nTest Case 2: Bulk delete with non-existent agent IDs")
    fake_ids = [str(uuid.uuid4()) for _ in range(3)]
    fake_data = {
        "agent_ids": fake_ids
    }
    
    fake_test, fake_response = run_test(
        "Bulk Delete with Non-existent IDs",
        "/agents/bulk-delete",
        method="POST",
        data=fake_data,
        auth=True,
        expected_status=404
    )
    
    if fake_test:
        print("✅ Non-existent agent IDs handled correctly (404 error)")
    else:
        print("❌ Non-existent agent IDs not handled properly")
    
    # Test Case 3: Authentication required
    print("\nTest Case 3: Bulk delete without authentication")
    unauth_data = {
        "agent_ids": fake_ids
    }
    
    unauth_test, unauth_response = run_test(
        "Bulk Delete without Authentication",
        "/agents/bulk-delete",
        method="POST",
        data=unauth_data,
        auth=False,
        expected_status=403
    )
    
    if unauth_test:
        print("✅ Authentication properly enforced (403 error)")
    else:
        print("❌ Authentication not properly enforced")
    
    # Test Case 4: Mixed valid and invalid IDs
    print("\nTest Case 4: Bulk delete with mixed valid and invalid IDs")
    
    # Create one test agent
    test_agents = create_test_agents(1)
    if len(test_agents) > 0:
        valid_id = test_agents[0]["id"]
        invalid_id = str(uuid.uuid4())
        mixed_ids = [valid_id, invalid_id]
        
        mixed_data = {
            "agent_ids": mixed_ids
        }
        
        mixed_test, mixed_response = run_test(
            "Bulk Delete with Mixed Valid/Invalid IDs",
            "/agents/bulk-delete",
            method="POST",
            data=mixed_data,
            auth=True,
            expected_status=404
        )
        
        if mixed_test:
            print("✅ Mixed valid/invalid IDs handled correctly (404 error)")
        else:
            print("❌ Mixed valid/invalid IDs not handled properly")
    else:
        print("❌ Could not create test agent for mixed ID test")

def test_clear_all_scenario():
    """Test the specific 'Clear All' button scenario"""
    print(f"\n{'='*80}\nTESTING 'CLEAR ALL' BUTTON SCENARIO")
    print("="*80)
    
    # Step 1: Create multiple agents (simulating user's agent list)
    print("\nStep 1: Creating multiple agents to simulate user's agent list")
    test_agents = create_test_agents(5)  # Create 5 agents
    
    if len(test_agents) < 5:
        print(f"❌ Only created {len(test_agents)} agents, expected 5")
        return False
    
    print(f"✅ Created {len(test_agents)} agents for Clear All test")
    
    # Step 2: Get all user's agents (what the Observatory would show)
    print("\nStep 2: Getting all user's agents (Observatory view)")
    get_all_test, get_all_response = run_test(
        "Get All User Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_all_test or not get_all_response:
        print("❌ Failed to get user's agents")
        return False
    
    all_agent_ids = [agent.get("id") for agent in get_all_response]
    print(f"Found {len(all_agent_ids)} total agents in user's list")
    
    # Step 3: Simulate "Clear All" button click
    print("\nStep 3: Simulating 'Clear All' button click")
    clear_all_data = {
        "agent_ids": all_agent_ids
    }
    
    clear_all_test, clear_all_response = run_test(
        "Clear All Agents (Simulate Button Click)",
        "/agents/bulk-delete",
        method="POST",
        data=clear_all_data,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if clear_all_test and clear_all_response:
        deleted_count = clear_all_response.get("deleted_count", 0)
        if deleted_count == len(all_agent_ids):
            print(f"✅ Clear All successfully deleted all {len(all_agent_ids)} agents")
        else:
            print(f"❌ Clear All deleted {deleted_count} agents, expected {len(all_agent_ids)}")
            return False
    else:
        print("❌ Clear All operation failed")
        return False
    
    # Step 4: Verify Observatory shows empty list
    print("\nStep 4: Verifying Observatory shows empty agent list")
    get_empty_test, get_empty_response = run_test(
        "Get Agents After Clear All",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_empty_test and get_empty_response is not None:
        remaining_count = len(get_empty_response)
        if remaining_count == 0:
            print("✅ Observatory shows empty agent list after Clear All")
        else:
            print(f"❌ Observatory still shows {remaining_count} agents after Clear All")
            return False
    else:
        print("❌ Failed to verify empty agent list")
        return False
    
    return True

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"BULK DELETE AGENTS TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution"""
    print("BULK DELETE AGENTS FUNCTIONALITY TEST")
    print("="*80)
    print("Testing the bulk delete functionality for the 'Clear All' button")
    print("This ensures the Clear All button works correctly in the Observatory Agent List")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return False
    
    # Step 2: Test basic bulk delete functionality
    print("\n" + "="*80)
    print("PHASE 1: BASIC BULK DELETE FUNCTIONALITY")
    print("="*80)
    
    basic_success = test_bulk_delete_functionality()
    
    # Step 3: Test edge cases
    print("\n" + "="*80)
    print("PHASE 2: EDGE CASES TESTING")
    print("="*80)
    
    test_edge_cases()
    
    # Step 4: Test Clear All scenario
    print("\n" + "="*80)
    print("PHASE 3: CLEAR ALL BUTTON SCENARIO")
    print("="*80)
    
    clear_all_success = test_clear_all_scenario()
    
    # Print final summary
    print_summary()
    
    # Final assessment
    if basic_success and clear_all_success:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("✅ The bulk delete functionality for the 'Clear All' button is working correctly")
        print("✅ Users can successfully clear all agents from the Observatory Agent List")
        return True
    else:
        print("\n❌ SOME CRITICAL TESTS FAILED!")
        print("❌ The bulk delete functionality needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)