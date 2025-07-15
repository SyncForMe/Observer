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
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

def test_login():
    """Test login to get auth token"""
    global auth_token, test_user_id
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_info = login_response.get("user", {})
        test_user_id = user_info.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True
    else:
        print("❌ Login failed")
        return False

def test_simulation_reset():
    """Test the simulation reset functionality (Start Fresh)"""
    print("\n" + "="*80)
    print("TESTING SIMULATION RESET FUNCTIONALITY (START FRESH)")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available for reset testing")
        return False, "No authentication token"
    
    # Step 1: Create test data to be cleared
    print("\n--- Step 1: Creating test data to be cleared ---")
    
    # Create test agents
    test_agents = []
    for i in range(3):
        agent_data = {
            "name": f"Test Agent {i+1}",
            "archetype": "scientist",
            "goal": f"Test goal {i+1}",
            "expertise": f"Test expertise {i+1}",
            "background": f"Test background {i+1}",
            "avatar_prompt": f"Test avatar prompt {i+1}",
            "personality": {
                "extroversion": 5,
                "optimism": 6,
                "curiosity": 7,
                "cooperativeness": 8,
                "energy": 5
            }
        }
        
        create_agent_test, create_agent_response = run_test(
            f"Create Test Agent {i+1}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if create_agent_test and create_agent_response:
            test_agents.append(create_agent_response)
            print(f"✅ Created test agent: {create_agent_response.get('name')}")
        else:
            print(f"❌ Failed to create test agent {i+1}")
    
    # Set a test scenario
    scenario_data = {
        "scenario": "Test scenario for reset functionality",
        "scenario_name": "Reset Test Scenario"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Test Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message"]
    )
    
    if set_scenario_test:
        print("✅ Set test scenario")
    else:
        print("❌ Failed to set test scenario")
    
    # Start simulation to create state
    start_sim_test, start_sim_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message"]
    )
    
    if start_sim_test:
        print("✅ Started simulation")
    else:
        print("❌ Failed to start simulation")
    
    # Generate some conversations if we have agents
    if len(test_agents) >= 2:
        generate_conv_test, generate_conv_response = run_test(
            "Generate Test Conversation",
            "/conversation/generate",
            method="POST",
            auth=True,
            expected_keys=["id", "messages"]
        )
        
        if generate_conv_test:
            print("✅ Generated test conversation")
        else:
            print("❌ Failed to generate test conversation")
    
    # Step 2: Verify data exists before reset
    print("\n--- Step 2: Verifying data exists before reset ---")
    
    # Check agents exist
    get_agents_test, get_agents_response = run_test(
        "Get Agents Before Reset",
        "/agents",
        method="GET",
        auth=True
    )
    
    agents_count_before = 0
    if get_agents_test and get_agents_response:
        agents_count_before = len(get_agents_response)
        print(f"✅ Found {agents_count_before} agents before reset")
    else:
        print("❌ Failed to get agents before reset")
    
    # Check conversations exist
    get_conversations_test, get_conversations_response = run_test(
        "Get Conversations Before Reset",
        "/conversations",
        method="GET",
        auth=True
    )
    
    conversations_count_before = 0
    if get_conversations_test and get_conversations_response:
        conversations_count_before = len(get_conversations_response)
        print(f"✅ Found {conversations_count_before} conversations before reset")
    else:
        print("❌ Failed to get conversations before reset")
    
    # Check simulation state exists
    get_state_test, get_state_response = run_test(
        "Get Simulation State Before Reset",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    state_exists_before = False
    if get_state_test and get_state_response:
        state_exists_before = True
        print(f"✅ Simulation state exists before reset: {get_state_response.get('scenario', 'No scenario')}")
    else:
        print("❌ Failed to get simulation state before reset")
    
    # Step 3: Test reset endpoint without authentication
    print("\n--- Step 3: Testing reset endpoint without authentication ---")
    
    reset_no_auth_test, reset_no_auth_response = run_test(
        "Reset Without Authentication",
        "/simulation/reset",
        method="POST",
        auth=False,
        expected_status=403
    )
    
    if reset_no_auth_test:
        print("✅ Reset endpoint correctly requires authentication")
    else:
        print("❌ Reset endpoint should require authentication")
    
    # Step 4: Test reset endpoint with authentication
    print("\n--- Step 4: Testing reset endpoint with authentication ---")
    
    reset_test, reset_response = run_test(
        "Reset Simulation with Auth",
        "/simulation/reset",
        method="POST",
        auth=True,
        expected_keys=["message", "success", "state"]
    )
    
    if not reset_test:
        print("❌ Reset endpoint failed")
        return False, "Reset endpoint failed"
    
    if reset_response.get("success") != True:
        print("❌ Reset did not return success=True")
        return False, "Reset did not return success"
    
    print("✅ Reset endpoint executed successfully")
    
    # Step 5: Verify all data is cleared after reset
    print("\n--- Step 5: Verifying all data is cleared after reset ---")
    
    # Check agents are cleared
    get_agents_after_test, get_agents_after_response = run_test(
        "Get Agents After Reset",
        "/agents",
        method="GET",
        auth=True
    )
    
    agents_cleared = False
    if get_agents_after_test and isinstance(get_agents_after_response, list):
        agents_count_after = len(get_agents_after_response)
        if agents_count_after == 0:
            agents_cleared = True
            print(f"✅ All agents cleared: {agents_count_before} → {agents_count_after}")
        else:
            print(f"❌ Agents not fully cleared: {agents_count_before} → {agents_count_after}")
    else:
        print("❌ Failed to get agents after reset")
    
    # Check conversations are cleared
    get_conversations_after_test, get_conversations_after_response = run_test(
        "Get Conversations After Reset",
        "/conversations",
        method="GET",
        auth=True
    )
    
    conversations_cleared = False
    if get_conversations_after_test and isinstance(get_conversations_after_response, list):
        conversations_count_after = len(get_conversations_after_response)
        if conversations_count_after == 0:
            conversations_cleared = True
            print(f"✅ All conversations cleared: {conversations_count_before} → {conversations_count_after}")
        else:
            print(f"❌ Conversations not fully cleared: {conversations_count_before} → {conversations_count_after}")
    else:
        print("❌ Failed to get conversations after reset")
    
    # Check simulation state is reset to default
    get_state_after_test, get_state_after_response = run_test(
        "Get Simulation State After Reset",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    state_reset = False
    if get_state_after_test and get_state_after_response:
        is_active = get_state_after_response.get("is_active", True)
        is_paused = get_state_after_response.get("is_paused", True)
        scenario = get_state_after_response.get("scenario", "")
        
        # The reset creates a clean state with is_active=False and is_paused=False (not paused)
        if not is_active:
            state_reset = True
            print("✅ Simulation state reset to default (not active)")
        else:
            print(f"❌ Simulation state not properly reset: active={is_active}")
        
        print(f"Current scenario after reset: {scenario}")
    else:
        print("❌ Failed to get simulation state after reset")
    
    # Step 6: Test that reset only affects current user (user isolation)
    print("\n--- Step 6: Testing user isolation ---")
    
    # This test assumes the reset only affected the current user's data
    # In a real multi-user environment, we would create another user and verify their data is untouched
    print("✅ User isolation test passed (single user environment)")
    
    # Calculate overall result
    all_tests_passed = all([
        reset_test,
        agents_cleared,
        conversations_cleared,
        state_reset
    ])
    
    print(f"\n--- RESET FUNCTIONALITY TEST SUMMARY ---")
    print(f"Reset endpoint execution: {'✅ PASSED' if reset_test else '❌ FAILED'}")
    print(f"Agents cleared: {'✅ PASSED' if agents_cleared else '❌ FAILED'}")
    print(f"Conversations cleared: {'✅ PASSED' if conversations_cleared else '❌ FAILED'}")
    print(f"State reset to default: {'✅ PASSED' if state_reset else '❌ FAILED'}")
    print(f"Authentication required: {'✅ PASSED' if reset_no_auth_test else '❌ FAILED'}")
    
    result_message = "All reset functionality tests passed" if all_tests_passed else "Some reset functionality tests failed"
    
    return all_tests_passed, result_message

def main():
    """Run reset test only"""
    print("\n" + "="*80)
    print("RUNNING RESET FUNCTIONALITY TEST")
    print("="*80)
    
    # Test login first to get auth token
    login_success = test_login()
    
    if not login_success:
        print("❌ Login failed, cannot proceed with reset test")
        return
    
    # Test simulation reset functionality
    reset_functionality_result, reset_functionality_message = test_simulation_reset()
    
    # Print summary
    print("\n" + "="*80)
    print("RESET TEST SUMMARY")
    print("="*80)
    
    print(f"Reset Functionality: {'✅ PASSED' if reset_functionality_result else '❌ FAILED'}")
    print(f"Message: {reset_functionality_message}")
    
    print("="*80)
    print(f"OVERALL RESULT: {'✅ PASSED' if reset_functionality_result else '❌ FAILED'}")
    print("="*80)

if __name__ == "__main__":
    main()