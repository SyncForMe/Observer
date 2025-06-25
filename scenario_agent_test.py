#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import base64
import re
import uuid
import jwt
from datetime import datetime, timedelta
import statistics
from collections import Counter, defaultdict

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

def create_test_agents(num_agents=3):
    """Create test agents for the current user"""
    print("\n" + "="*80)
    print(f"CREATING {num_agents} TEST AGENTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot create test agents without authentication")
            return False, "Authentication failed"
    
    # Define archetypes to create agents for
    archetypes = ["scientist", "leader", "skeptic", "optimist", "artist", "introvert"]
    
    # Create agents
    for i in range(num_agents):
        archetype = archetypes[i % len(archetypes)]
        agent_data = {
            "name": f"Test {archetype.capitalize()} {uuid.uuid4().hex[:8]}",
            "archetype": archetype,
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 5,
                "cooperativeness": 5,
                "energy": 5
            },
            "goal": f"Test the {archetype} agent functionality",
            "expertise": f"Expert in {archetype} testing",
            "background": f"Extensive background in {archetype} testing",
            "memory_summary": f"Remembers all {archetype} tests",
            "avatar_prompt": f"A professional {archetype}",
            "avatar_url": ""
        }
        
        create_agent_test, create_agent_response = run_test(
            f"Create Agent {i+1}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_agent_test and create_agent_response:
            agent_id = create_agent_response.get("id")
            if agent_id:
                print(f"✅ Created {archetype} agent with ID: {agent_id}")
                created_agent_ids.append(agent_id)
            else:
                print(f"❌ Failed to get agent ID for {archetype} agent")
        else:
            print(f"❌ Failed to create {archetype} agent")
    
    # Print summary
    print("\nAGENT CREATION SUMMARY:")
    if len(created_agent_ids) > 0:
        print(f"✅ Successfully created {len(created_agent_ids)} agents")
        return True, created_agent_ids
    else:
        print(f"❌ Failed to create any agents")
        return False, created_agent_ids

def test_clear_all_agents():
    """Test the Clear All agents functionality"""
    print("\n" + "="*80)
    print("TESTING CLEAR ALL AGENTS FUNCTIONALITY")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test Clear All agents without authentication")
            return False, "Authentication failed"
    
    # Create test agents if needed
    if not created_agent_ids:
        create_success, agent_ids = create_test_agents(5)
        if not create_success:
            print("❌ Failed to create test agents for Clear All testing")
            return False, "Failed to create test agents"
    
    # Test 1: Verify agents exist before clearing
    print("\nTest 1: Verifying agents exist before clearing")
    
    get_agents_test, get_agents_response = run_test(
        "Get User Agents Before Clear",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_test:
        print("❌ Failed to get user agents")
        return False, "Failed to get user agents"
    
    agent_count = len(get_agents_response) if get_agents_response else 0
    print(f"Agent count before clearing: {agent_count}")
    
    if agent_count == 0:
        print("❌ No agents found to clear")
        return False, "No agents found to clear"
    else:
        print(f"✅ Found {agent_count} agents to clear")
    
    # Test 2: Test Clear All agents endpoint
    print("\nTest 2: Testing Clear All agents endpoint")
    
    clear_all_test, clear_all_response = run_test(
        "Clear All Agents",
        "/agents/bulk-delete",
        method="POST",
        data={"agent_ids": [agent.get("id") for agent in get_agents_response]},
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if not clear_all_test:
        print("❌ Failed to clear all agents")
        return False, "Failed to clear all agents"
    
    deleted_count = clear_all_response.get("deleted_count", 0)
    print(f"Deleted {deleted_count} agents")
    
    if deleted_count != agent_count:
        print(f"❌ Only deleted {deleted_count} out of {agent_count} agents")
    else:
        print(f"✅ Successfully deleted all {agent_count} agents")
    
    # Test 3: Verify agents are cleared
    print("\nTest 3: Verifying agents are cleared")
    
    get_agents_after_test, get_agents_after_response = run_test(
        "Get User Agents After Clear",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_after_test:
        print("❌ Failed to get user agents after clearing")
        return False, "Failed to get user agents after clearing"
    
    agent_count_after = len(get_agents_after_response) if get_agents_after_response else 0
    print(f"Agent count after clearing: {agent_count_after}")
    
    if agent_count_after > 0:
        print(f"❌ {agent_count_after} agents still exist after clearing")
        return False, f"{agent_count_after} agents still exist after clearing"
    else:
        print("✅ All agents were successfully cleared")
    
    # Test 4: Test authentication requirements
    print("\nTest 4: Testing authentication requirements")
    
    # Create a few more test agents
    create_success, new_agent_ids = create_test_agents(2)
    
    # Test without authentication
    no_auth_data = {
        "agent_ids": new_agent_ids
    }
    
    no_auth_test, no_auth_response = run_test(
        "Clear All Agents Without Authentication",
        "/agents/bulk-delete",
        method="POST",
        data=no_auth_data,
        auth=False,
        expected_status=403
    )
    
    if no_auth_test:
        print("✅ Clear All agents correctly requires authentication")
    else:
        print("❌ Clear All agents does not properly enforce authentication")
    
    # Test 5: Test with empty array
    print("\nTest 5: Testing with empty array")
    
    empty_data = {
        "agent_ids": []
    }
    
    empty_test, empty_response = run_test(
        "Clear All Agents With Empty Array",
        "/agents/bulk-delete",
        method="POST",
        data=empty_data,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if empty_test:
        print("✅ Clear All agents correctly handles empty arrays")
        
        # Check deleted count is 0
        if empty_response.get("deleted_count") == 0:
            print("✅ Deleted count is correctly 0 for empty array")
        else:
            print(f"❌ Deleted count is {empty_response.get('deleted_count')} instead of 0 for empty array")
    else:
        print("❌ Clear All agents does not properly handle empty arrays")
    
    # Test 6: Test with invalid agent IDs
    print("\nTest 6: Testing with invalid agent IDs")
    
    invalid_data = {
        "agent_ids": [str(uuid.uuid4()) for _ in range(3)]
    }
    
    invalid_test, invalid_response = run_test(
        "Clear All Agents With Invalid IDs",
        "/agents/bulk-delete",
        method="POST",
        data=invalid_data,
        auth=True,
        expected_status=404
    )
    
    if invalid_test:
        print("✅ Clear All agents correctly handles invalid agent IDs")
    else:
        print("❌ Clear All agents does not properly handle invalid agent IDs")
    
    # Test 7: Test user data isolation
    print("\nTest 7: Testing user data isolation")
    
    # Create a new test user
    new_user_email = f"another.user.{uuid.uuid4()}@example.com"
    new_user_password = "securePassword123"
    new_user_name = "Another Test User"
    
    register_data = {
        "email": new_user_email,
        "password": new_user_password,
        "name": new_user_name
    }
    
    register_test, register_response = run_test(
        "Register New Test User",
        "/auth/register",
        method="POST",
        data=register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not register_test or not register_response:
        print("❌ Failed to create new test user for isolation testing")
        return False, "Failed to create new test user"
    
    new_user_token = register_response.get("access_token")
    new_user_id = register_response.get("user", {}).get("id")
    
    # Create agents for original user
    original_token = auth_token
    auth_token = original_token
    create_success, original_agent_ids = create_test_agents(2)
    
    # Create agents for new user
    auth_token = new_user_token
    create_success, new_user_agent_ids = create_test_agents(2)
    
    # Try to delete original user's agents with new user's token
    auth_token = new_user_token
    cross_user_data = {
        "agent_ids": original_agent_ids
    }
    
    cross_user_test, cross_user_response = run_test(
        "Delete Other User's Agents",
        "/agents/bulk-delete",
        method="POST",
        data=cross_user_data,
        auth=True,
        expected_status=404
    )
    
    if cross_user_test:
        print("✅ User cannot delete other users' agents")
    else:
        print("❌ User can delete other users' agents")
    
    # Verify original user's agents still exist
    auth_token = original_token
    verify_original_test, verify_original_response = run_test(
        "Verify Original User's Agents Still Exist",
        "/agents",
        method="GET",
        auth=True
    )
    
    if verify_original_test:
        original_agents_count = len(verify_original_response) if verify_original_response else 0
        if original_agents_count >= len(original_agent_ids):
            print(f"✅ Original user's agents still exist ({original_agents_count} agents)")
        else:
            print(f"❌ Some original user's agents were deleted ({original_agents_count} remaining)")
    else:
        print("❌ Failed to verify original user's agents")
    
    # Print summary
    print("\nCLEAR ALL AGENTS FUNCTIONALITY SUMMARY:")
    
    if clear_all_test and agent_count_after == 0 and no_auth_test and empty_test and invalid_test and cross_user_test:
        print("✅ Clear All agents functionality is working correctly!")
        print("✅ Successfully clears all user agents")
        print("✅ Authentication is properly enforced")
        print("✅ Empty arrays are handled correctly")
        print("✅ Invalid agent IDs are handled correctly")
        print("✅ User data isolation is properly implemented")
        return True, "Clear All agents functionality is working correctly"
    else:
        issues = []
        if not clear_all_test:
            issues.append("Failed to clear all agents")
        if agent_count_after > 0:
            issues.append(f"{agent_count_after} agents still exist after clearing")
        if not no_auth_test:
            issues.append("Authentication is not properly enforced")
        if not empty_test:
            issues.append("Empty arrays are not handled correctly")
        if not invalid_test:
            issues.append("Invalid agent IDs are not handled correctly")
        if not cross_user_test:
            issues.append("User data isolation is not properly implemented")
        
        print("❌ Clear All agents functionality has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def test_random_scenario():
    """Test the random scenario generation endpoint"""
    print("\n" + "="*80)
    print("TESTING RANDOM SCENARIO GENERATION")
    print("="*80)
    
    # Test 1: Get random scenario
    print("\nTest 1: Getting random scenario")
    
    random_scenario_test, random_scenario_response = run_test(
        "Get Random Scenario",
        "/simulation/random-scenario",
        method="GET",
        expected_keys=["scenario", "scenario_name"]
    )
    
    if not random_scenario_test:
        print("❌ Failed to get random scenario")
        return False, "Failed to get random scenario"
    
    scenario = random_scenario_response.get("scenario", "")
    scenario_name = random_scenario_response.get("scenario_name", "")
    
    print(f"Scenario Name: {scenario_name}")
    print(f"Scenario Length: {len(scenario)} characters")
    
    if len(scenario) > 100 and len(scenario_name) > 0:
        print("✅ Random scenario has appropriate content length and name")
    else:
        print("❌ Random scenario has insufficient content or missing name")
    
    # Test 2: Get multiple random scenarios to verify randomness
    print("\nTest 2: Verifying scenario randomness")
    
    scenarios = []
    for i in range(3):
        random_test, random_response = run_test(
            f"Get Random Scenario {i+1}",
            "/simulation/random-scenario",
            method="GET",
            expected_keys=["scenario", "scenario_name"]
        )
        
        if random_test and random_response:
            scenarios.append(random_response)
    
    # Check if scenarios are different
    scenario_names = [s.get("scenario_name", "") for s in scenarios]
    unique_names = set(scenario_names)
    
    print(f"Retrieved {len(scenarios)} scenarios with {len(unique_names)} unique names")
    
    if len(unique_names) > 1:
        print("✅ Random scenario generation provides different scenarios")
    else:
        print("❌ Random scenario generation returns the same scenario repeatedly")
    
    # Test 3: Login and set random scenario
    print("\nTest 3: Setting random scenario after login")
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test setting random scenario without authentication")
            return False, "Authentication failed"
    
    # Get a random scenario
    random_test, random_response = run_test(
        "Get Random Scenario For Setting",
        "/simulation/random-scenario",
        method="GET",
        expected_keys=["scenario", "scenario_name"]
    )
    
    if not random_test or not random_response:
        print("❌ Failed to get random scenario for setting")
        return False, "Failed to get random scenario for setting"
    
    # Set the random scenario
    set_data = {
        "scenario": random_response.get("scenario", ""),
        "scenario_name": random_response.get("scenario_name", "")
    }
    
    set_test, set_response = run_test(
        "Set Random Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=set_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_test:
        print("❌ Failed to set random scenario")
        return False, "Failed to set random scenario"
    
    print("✅ Successfully set random scenario")
    
    # Print summary
    print("\nRANDOM SCENARIO GENERATION SUMMARY:")
    
    if random_scenario_test and len(unique_names) > 1 and set_test:
        print("✅ Random scenario generation is working correctly!")
        print("✅ Endpoint returns detailed scenarios with names")
        print("✅ Different scenarios are provided on multiple calls")
        print("✅ Random scenarios can be set for the simulation")
        return True, "Random scenario generation is working correctly"
    else:
        issues = []
        if not random_scenario_test:
            issues.append("Failed to get random scenario")
        if len(unique_names) <= 1:
            issues.append("Random scenario generation returns the same scenario repeatedly")
        if not set_test:
            issues.append("Failed to set random scenario")
        
        print("❌ Random scenario generation has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def test_set_scenario():
    """Test the set scenario endpoint"""
    print("\n" + "="*80)
    print("TESTING SET SCENARIO FUNCTIONALITY")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test set scenario without authentication")
            return False, "Authentication failed"
    
    # Test 1: Set custom scenario
    print("\nTest 1: Setting custom scenario")
    
    custom_scenario = "This is a custom test scenario for the AI agent simulation platform."
    custom_scenario_name = "Custom Test Scenario"
    
    set_data = {
        "scenario": custom_scenario,
        "scenario_name": custom_scenario_name
    }
    
    set_test, set_response = run_test(
        "Set Custom Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=set_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_test:
        print("❌ Failed to set custom scenario")
        return False, "Failed to set custom scenario"
    
    print("✅ Successfully set custom scenario")
    
    # Test 2: Set scenario with empty text
    print("\nTest 2: Setting scenario with empty text")
    
    empty_data = {
        "scenario": "",
        "scenario_name": "Empty Scenario"
    }
    
    empty_test, empty_response = run_test(
        "Set Empty Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=empty_data,
        auth=True,
        expected_status=400
    )
    
    if empty_test:
        print("✅ Correctly rejects empty scenario text")
    else:
        print("❌ Does not properly validate empty scenario text")
    
    # Test 3: Set scenario with empty name
    print("\nTest 3: Setting scenario with empty name")
    
    no_name_data = {
        "scenario": "This is a scenario without a name",
        "scenario_name": ""
    }
    
    no_name_test, no_name_response = run_test(
        "Set Scenario Without Name",
        "/simulation/set-scenario",
        method="POST",
        data=no_name_data,
        auth=True,
        expected_status=400
    )
    
    if no_name_test:
        print("✅ Correctly rejects scenario without a name")
    else:
        print("❌ Does not properly validate empty scenario name")
    
    # Test 4: Verify scenario was set
    print("\nTest 4: Verifying scenario was set")
    
    # Get simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if not state_test:
        print("❌ Failed to get simulation state")
        return False, "Failed to get simulation state"
    
    scenario = state_response.get("scenario", "")
    scenario_name = state_response.get("scenario_name", "")
    
    print(f"Current Scenario: {scenario_name}")
    print(f"Scenario Text: {scenario}")
    
    if scenario == custom_scenario and scenario_name == custom_scenario_name:
        print("✅ Custom scenario was correctly set in simulation state")
    else:
        print("❌ Custom scenario was not correctly set in simulation state")
    
    # Print summary
    print("\nSET SCENARIO FUNCTIONALITY SUMMARY:")
    
    if set_test and empty_test and no_name_test and scenario == custom_scenario:
        print("✅ Set scenario functionality is working correctly!")
        print("✅ Custom scenarios can be set")
        print("✅ Input validation is properly implemented")
        print("✅ Scenario is correctly stored in simulation state")
        return True, "Set scenario functionality is working correctly"
    else:
        issues = []
        if not set_test:
            issues.append("Failed to set custom scenario")
        if not empty_test:
            issues.append("Does not properly validate empty scenario text")
        if not no_name_test:
            issues.append("Does not properly validate empty scenario name")
        if scenario != custom_scenario:
            issues.append("Custom scenario was not correctly set in simulation state")
        
        print("❌ Set scenario functionality has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def test_transcribe_scenario():
    """Test the transcribe scenario endpoint"""
    print("\n" + "="*80)
    print("TESTING TRANSCRIBE SCENARIO FUNCTIONALITY")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test transcribe scenario without authentication")
            return False, "Authentication failed"
    
    # Test 1: Check endpoint existence and authentication
    print("\nTest 1: Checking endpoint existence and authentication")
    
    # Test without authentication
    no_auth_test, no_auth_response = run_test(
        "Transcribe Scenario Without Authentication",
        "/speech/transcribe-scenario",
        method="POST",
        data={},
        auth=False,
        expected_status=403
    )
    
    if no_auth_test:
        print("✅ Transcribe scenario endpoint exists and requires authentication")
    else:
        print("❌ Transcribe scenario endpoint does not properly enforce authentication")
    
    # Test 2: Test with invalid file type
    print("\nTest 2: Testing with invalid file type")
    
    # Since we can't easily test file uploads with this test framework,
    # we'll just check that the endpoint exists and requires authentication
    
    print("ℹ️ Skipping file upload test - would require multipart/form-data support")
    print("ℹ️ Endpoint exists at POST /api/speech/transcribe-scenario")
    
    # Print summary
    print("\nTRANSCRIBE SCENARIO FUNCTIONALITY SUMMARY:")
    
    if no_auth_test:
        print("✅ Transcribe scenario endpoint exists and requires authentication")
        print("ℹ️ Full functionality testing would require multipart/form-data support")
        print("ℹ️ Based on code review, the endpoint should transcribe audio to text for scenario creation")
        return True, "Transcribe scenario endpoint exists and requires authentication"
    else:
        print("❌ Transcribe scenario endpoint has issues with authentication")
        return False, "Transcribe scenario endpoint has issues with authentication"

def test_scenario_integration():
    """Test the integration of scenarios with agents"""
    print("\n" + "="*80)
    print("TESTING SCENARIO INTEGRATION WITH AGENTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test scenario integration without authentication")
            return False, "Authentication failed"
    
    # Test 1: Create multiple agents
    print("\nTest 1: Creating multiple agents")
    
    create_success, agent_ids = create_test_agents(3)
    if not create_success:
        print("❌ Failed to create test agents for scenario integration")
        return False, "Failed to create test agents"
    
    print(f"✅ Created {len(agent_ids)} test agents")
    
    # Test 2: Set custom scenario
    print("\nTest 2: Setting custom scenario")
    
    custom_scenario = "This is a custom test scenario for the AI agent simulation platform."
    custom_scenario_name = "Custom Test Scenario"
    
    set_data = {
        "scenario": custom_scenario,
        "scenario_name": custom_scenario_name
    }
    
    set_test, set_response = run_test(
        "Set Custom Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=set_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_test:
        print("❌ Failed to set custom scenario")
        return False, "Failed to set custom scenario"
    
    print("✅ Successfully set custom scenario")
    
    # Test 3: Verify scenario was set
    print("\nTest 3: Verifying scenario was set")
    
    # Get simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if not state_test:
        print("❌ Failed to get simulation state")
        return False, "Failed to get simulation state"
    
    scenario = state_response.get("scenario", "")
    scenario_name = state_response.get("scenario_name", "")
    
    print(f"Current Scenario: {scenario_name}")
    print(f"Scenario Text: {scenario}")
    
    if scenario == custom_scenario and scenario_name == custom_scenario_name:
        print("✅ Custom scenario was correctly set in simulation state")
    else:
        print("❌ Custom scenario was not correctly set in simulation state")
    
    # Test 4: Set random scenario
    print("\nTest 4: Setting random scenario")
    
    # Get a random scenario
    random_test, random_response = run_test(
        "Get Random Scenario",
        "/simulation/random-scenario",
        method="GET",
        expected_keys=["scenario", "scenario_name"]
    )
    
    if not random_test or not random_response:
        print("❌ Failed to get random scenario")
        return False, "Failed to get random scenario"
    
    # Set the random scenario
    random_set_data = {
        "scenario": random_response.get("scenario", ""),
        "scenario_name": random_response.get("scenario_name", "")
    }
    
    random_set_test, random_set_response = run_test(
        "Set Random Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=random_set_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not random_set_test:
        print("❌ Failed to set random scenario")
        return False, "Failed to set random scenario"
    
    print("✅ Successfully set random scenario")
    
    # Test 5: Verify random scenario was set
    print("\nTest 5: Verifying random scenario was set")
    
    # Get simulation state
    random_state_test, random_state_response = run_test(
        "Get Simulation State After Random Scenario",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if not random_state_test:
        print("❌ Failed to get simulation state after random scenario")
        return False, "Failed to get simulation state after random scenario"
    
    random_scenario = random_state_response.get("scenario", "")
    random_scenario_name = random_state_response.get("scenario_name", "")
    
    print(f"Current Scenario: {random_scenario_name}")
    print(f"Scenario Text Length: {len(random_scenario)} characters")
    
    if random_scenario == random_set_data["scenario"] and random_scenario_name == random_set_data["scenario_name"]:
        print("✅ Random scenario was correctly set in simulation state")
    else:
        print("❌ Random scenario was not correctly set in simulation state")
    
    # Test 6: Start simulation with scenario
    print("\nTest 6: Starting simulation with scenario")
    
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print("✅ Successfully started simulation")
    
    # Test 7: Verify simulation state after starting
    print("\nTest 7: Verifying simulation state after starting")
    
    # Get simulation state
    final_state_test, final_state_response = run_test(
        "Get Simulation State After Starting",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if not final_state_test:
        print("❌ Failed to get simulation state after starting")
        return False, "Failed to get simulation state after starting"
    
    is_active = final_state_response.get("is_active", False)
    final_scenario = final_state_response.get("scenario", "")
    final_scenario_name = final_state_response.get("scenario_name", "")
    
    print(f"Simulation Active: {is_active}")
    print(f"Current Scenario: {final_scenario_name}")
    
    if is_active and final_scenario == random_scenario and final_scenario_name == random_scenario_name:
        print("✅ Simulation is active with the correct scenario")
    else:
        print("❌ Simulation state is incorrect after starting")
    
    # Test 8: Clear all agents
    print("\nTest 8: Clearing all agents")
    
    clear_all_test, clear_all_response = run_test(
        "Clear All Agents",
        "/agents/bulk-delete",
        method="POST",
        data={"agent_ids": agent_ids},
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if not clear_all_test:
        print("❌ Failed to clear all agents")
        return False, "Failed to clear all agents"
    
    deleted_count = clear_all_response.get("deleted_count", 0)
    print(f"Deleted {deleted_count} agents")
    
    if deleted_count != len(agent_ids):
        print(f"❌ Only deleted {deleted_count} out of {len(agent_ids)} agents")
    else:
        print(f"✅ Successfully deleted all {len(agent_ids)} agents")
    
    # Test 9: Verify agents are cleared
    print("\nTest 9: Verifying agents are cleared")
    
    get_agents_after_test, get_agents_after_response = run_test(
        "Get User Agents After Clear",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_after_test:
        print("❌ Failed to get user agents after clearing")
        return False, "Failed to get user agents after clearing"
    
    agent_count_after = len(get_agents_after_response) if get_agents_after_response else 0
    print(f"Agent count after clearing: {agent_count_after}")
    
    if agent_count_after > 0:
        print(f"❌ {agent_count_after} agents still exist after clearing")
    else:
        print("✅ All agents were successfully cleared")
    
    # Print summary
    print("\nSCENARIO INTEGRATION SUMMARY:")
    
    if (create_success and set_test and state_test and random_set_test and 
        random_state_test and start_test and final_state_test and 
        clear_all_test and agent_count_after == 0):
        print("✅ Scenario integration is working correctly!")
        print("✅ Agents can be created and managed")
        print("✅ Custom scenarios can be set")
        print("✅ Random scenarios can be set")
        print("✅ Scenarios are correctly stored in simulation state")
        print("✅ Simulation can be started with scenarios")
        print("✅ Agents can be cleared after simulation")
        return True, "Scenario integration is working correctly"
    else:
        issues = []
        if not create_success:
            issues.append("Failed to create test agents")
        if not set_test:
            issues.append("Failed to set custom scenario")
        if not state_test or scenario != custom_scenario:
            issues.append("Custom scenario was not correctly set in simulation state")
        if not random_set_test:
            issues.append("Failed to set random scenario")
        if not random_state_test or random_scenario != random_set_data["scenario"]:
            issues.append("Random scenario was not correctly set in simulation state")
        if not start_test:
            issues.append("Failed to start simulation")
        if not final_state_test or not is_active:
            issues.append("Simulation state is incorrect after starting")
        if not clear_all_test:
            issues.append("Failed to clear all agents")
        if agent_count_after > 0:
            issues.append(f"{agent_count_after} agents still exist after clearing")
        
        print("❌ Scenario integration has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def main():
    """Main function to run all tests"""
    print("\n" + "="*80)
    print("RUNNING SCENARIO AND AGENT MANAGEMENT TESTS")
    print("="*80)
    
    # Login first
    test_login()
    
    # Run tests
    test_clear_all_agents()
    test_random_scenario()
    test_set_scenario()
    test_transcribe_scenario()
    test_scenario_integration()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()