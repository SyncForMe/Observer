#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
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

def create_test_agents(num_agents=3):
    """Create test agents for simulation"""
    print("\n" + "="*80)
    print(f"CREATING {num_agents} TEST AGENTS")
    print("="*80)
    
    agent_ids = []
    
    # Define agent archetypes to use
    archetypes = ["scientist", "leader", "skeptic"]
    
    for i in range(num_agents):
        archetype = archetypes[i % len(archetypes)]
        
        # Define agent data
        agent_data = {
            "name": f"Test Agent {i+1}",
            "archetype": archetype,
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 5,
                "cooperativeness": 5,
                "energy": 5
            },
            "goal": f"Test goal for agent {i+1}",
            "expertise": f"Test expertise for agent {i+1}",
            "background": f"Test background for agent {i+1}"
        }
        
        # Create agent
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
                agent_ids.append(agent_id)
            else:
                print(f"❌ Failed to get agent ID")
        else:
            print(f"❌ Failed to create agent")
    
    return agent_ids

def test_observer_message_simulation_control():
    """Test simulation control functionality after observer messages"""
    print("\n" + "="*80)
    print("TESTING SIMULATION CONTROL AFTER OBSERVER MESSAGES")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test simulation control without authentication")
            return False
    
    # Step 1: Create test agents
    agent_ids = create_test_agents(3)
    if not agent_ids or len(agent_ids) < 2:
        print("❌ Failed to create enough test agents")
        return False
    
    # Step 2: Start a simulation
    print("\nStep 2: Starting a simulation")
    start_sim_test, start_sim_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start simulation")
        return False
    
    print("✅ Successfully started simulation")
    
    # Step 3: Verify simulation is running
    print("\nStep 3: Verifying simulation is running")
    get_state_test, get_state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["is_active"]
    )
    
    if not get_state_test or not get_state_response.get("is_active"):
        print("❌ Simulation is not running")
        return False
    
    print("✅ Simulation is running")
    
    # Step 4: Set a scenario
    print("\nStep 4: Setting a scenario")
    scenario_data = {
        "scenario": "Test scenario for simulation control testing",
        "scenario_name": "Test Scenario"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "scenario"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario")
        return False
    
    print("✅ Successfully set scenario")
    
    # Step 5: Send an observer message
    print("\nStep 5: Sending an observer message")
    observer_data = {
        "observer_message": "This is a test observer message. Please acknowledge."
    }
    
    observer_test, observer_response = run_test(
        "Send Observer Message",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=True,
        expected_keys=["message", "observer_message", "agent_responses"]
    )
    
    if not observer_test:
        print("❌ Failed to send observer message")
        return False
    
    print("✅ Successfully sent observer message")
    
    # Step 6: Verify simulation state after observer message
    print("\nStep 6: Verifying simulation state after observer message")
    get_state_after_observer_test, get_state_after_observer_response = run_test(
        "Get Simulation State After Observer Message",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["is_active"]
    )
    
    if not get_state_after_observer_test:
        print("❌ Failed to get simulation state after observer message")
        return False
    
    if not get_state_after_observer_response.get("is_active"):
        print("❌ Simulation is not running after observer message")
        return False
    
    print("✅ Simulation is still running after observer message")
    
    # Step 7: Pause the simulation
    print("\nStep 7: Pausing the simulation")
    pause_sim_test, pause_sim_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active"]
    )
    
    if not pause_sim_test:
        print("❌ Failed to pause simulation")
        return False
    
    if pause_sim_response.get("is_active"):
        print("❌ Simulation is still running after pause")
        return False
    
    print("✅ Successfully paused simulation")
    
    # Step 8: Verify simulation is paused
    print("\nStep 8: Verifying simulation is paused")
    get_state_after_pause_test, get_state_after_pause_response = run_test(
        "Get Simulation State After Pause",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["is_active"]
    )
    
    if not get_state_after_pause_test:
        print("❌ Failed to get simulation state after pause")
        return False
    
    if get_state_after_pause_response.get("is_active"):
        print("❌ Simulation is still running after pause")
        return False
    
    print("✅ Simulation is paused")
    
    # Step 9: Resume the simulation
    print("\nStep 9: Resuming the simulation")
    resume_sim_test, resume_sim_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active"]
    )
    
    if not resume_sim_test:
        print("❌ Failed to resume simulation")
        return False
    
    if not resume_sim_response.get("is_active"):
        print("❌ Simulation is not running after resume")
        return False
    
    print("✅ Successfully resumed simulation")
    
    # Step 10: Verify simulation is running again
    print("\nStep 10: Verifying simulation is running again")
    get_state_after_resume_test, get_state_after_resume_response = run_test(
        "Get Simulation State After Resume",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["is_active"]
    )
    
    if not get_state_after_resume_test:
        print("❌ Failed to get simulation state after resume")
        return False
    
    if not get_state_after_resume_response.get("is_active"):
        print("❌ Simulation is not running after resume")
        return False
    
    print("✅ Simulation is running again")
    
    # Step 11: Send another observer message
    print("\nStep 11: Sending another observer message")
    observer_data_2 = {
        "observer_message": "This is a second test observer message. Please acknowledge."
    }
    
    observer_test_2, observer_response_2 = run_test(
        "Send Second Observer Message",
        "/observer/send-message",
        method="POST",
        data=observer_data_2,
        auth=True,
        expected_keys=["message", "observer_message", "agent_responses"]
    )
    
    if not observer_test_2:
        print("❌ Failed to send second observer message")
        return False
    
    print("✅ Successfully sent second observer message")
    
    # Step 12: Verify simulation state after second observer message
    print("\nStep 12: Verifying simulation state after second observer message")
    get_state_after_observer_2_test, get_state_after_observer_2_response = run_test(
        "Get Simulation State After Second Observer Message",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["is_active"]
    )
    
    if not get_state_after_observer_2_test:
        print("❌ Failed to get simulation state after second observer message")
        return False
    
    if not get_state_after_observer_2_response.get("is_active"):
        print("❌ Simulation is not running after second observer message")
        return False
    
    print("✅ Simulation is still running after second observer message")
    
    # Step 13: Test the "start fresh" functionality
    print("\nStep 13: Testing the 'start fresh' functionality")
    start_fresh_test, start_fresh_response = run_test(
        "Start Fresh (Start Simulation)",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_fresh_test:
        print("❌ Failed to start fresh")
        return False
    
    print("✅ Successfully started fresh")
    
    # Step 14: Verify conversations were cleared
    print("\nStep 14: Verifying conversations were cleared")
    get_conversations_test, get_conversations_response = run_test(
        "Get Conversations After Start Fresh",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not get_conversations_test:
        print("❌ Failed to get conversations after start fresh")
        return False
    
    if get_conversations_response and len(get_conversations_response) > 0:
        print(f"❌ Conversations were not cleared. Found {len(get_conversations_response)} conversations.")
        return False
    
    print("✅ Conversations were cleared")
    
    # Step 15: Verify agents were preserved
    print("\nStep 15: Verifying agents were preserved")
    get_agents_test, get_agents_response = run_test(
        "Get Agents After Start Fresh",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_test:
        print("❌ Failed to get agents after start fresh")
        return False
    
    if not get_agents_response or len(get_agents_response) < len(agent_ids):
        print(f"❌ Agents were not preserved. Found {len(get_agents_response) if get_agents_response else 0} agents, expected at least {len(agent_ids)}.")
        return False
    
    print(f"✅ Agents were preserved. Found {len(get_agents_response)} agents.")
    
    # Print summary
    print("\nSIMULATION CONTROL AFTER OBSERVER MESSAGES SUMMARY:")
    
    all_tests_passed = all([
        start_sim_test, 
        get_state_test,
        set_scenario_test,
        observer_test,
        get_state_after_observer_test,
        pause_sim_test,
        get_state_after_pause_test,
        resume_sim_test,
        get_state_after_resume_test,
        observer_test_2,
        get_state_after_observer_2_test,
        start_fresh_test,
        get_conversations_test,
        get_agents_test
    ])
    
    if all_tests_passed:
        print("✅ All simulation control tests passed!")
        print("✅ Simulation can be started successfully")
        print("✅ Observer messages can be sent while simulation is running")
        print("✅ Simulation can be paused after sending observer messages")
        print("✅ Simulation can be resumed after being paused")
        print("✅ Multiple observer messages can be sent in sequence")
        print("✅ Start fresh functionality works correctly")
        print("✅ Conversations are cleared when starting fresh")
        print("✅ Agents are preserved when starting fresh")
        return True
    else:
        print("❌ Some simulation control tests failed")
        return False

if __name__ == "__main__":
    # Run the tests
    test_login()
    test_observer_message_simulation_control()
    print_summary()