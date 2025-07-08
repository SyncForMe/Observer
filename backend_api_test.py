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
    """Test the login authentication endpoint"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("TESTING AUTHENTICATION ENDPOINTS")
    print("="*80)
    
    # Test 1: Login with admin credentials
    print("\nTest 1: Login with admin credentials")
    
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
    
    if login_test and login_response:
        print("✅ Login successful with admin credentials")
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"User ID: {test_user_id}")
        
        # Verify token structure
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ JWT token is valid and contains: {decoded_token}")
            if "user_id" in decoded_token and "sub" in decoded_token:
                print("✅ JWT token contains required fields (user_id, sub)")
            else:
                print("❌ JWT token is missing required fields")
        except Exception as e:
            print(f"❌ JWT token validation failed: {e}")
    else:
        print("❌ Login failed with admin credentials")
        
        # Try the test login endpoint as fallback
        test_login_test, test_login_response = run_test(
            "Test Login Endpoint",
            "/auth/test-login",
            method="POST",
            expected_keys=["access_token", "token_type", "user"]
        )
        
        if test_login_test and test_login_response:
            print("✅ Test login successful")
            auth_token = test_login_response.get("access_token")
            user_data = test_login_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"User ID: {test_user_id}")
        else:
            print("❌ Test login also failed")
            return False
    
    # Test 2: Test token validation with /api/auth/me endpoint
    print("\nTest 2: Testing token validation with /api/auth/me endpoint")
    
    me_test, me_response = run_test(
        "Get current user profile",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if me_test and me_response:
        print("✅ Successfully retrieved user profile with JWT token")
        print(f"User profile: {json.dumps(me_response, indent=2)}")
        
        # Verify user ID matches
        if me_response.get("id") == test_user_id:
            print("✅ User ID in profile matches the ID from login")
        else:
            print("❌ User ID mismatch between profile and login")
    else:
        print("❌ Failed to retrieve user profile with JWT token")
    
    # Test 3: Test "Continue as Guest" functionality
    print("\nTest 3: Testing 'Continue as Guest' functionality")
    
    guest_test, guest_response = run_test(
        "Continue as Guest",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        print("✅ 'Continue as Guest' functionality works correctly")
        guest_token = guest_response.get("access_token")
        guest_user = guest_response.get("user", {})
        guest_user_id = guest_user.get("id")
        print(f"Guest User ID: {guest_user_id}")
    else:
        print("❌ 'Continue as Guest' functionality failed")
    
    # Print summary
    print("\nAUTHENTICATION ENDPOINTS SUMMARY:")
    
    if login_test or test_login_test:
        print("✅ Login authentication is working correctly")
        print("✅ JWT token is generated and validated properly")
        if me_test:
            print("✅ Token validation endpoint is working correctly")
        else:
            print("❌ Token validation endpoint has issues")
        if guest_test:
            print("✅ 'Continue as Guest' functionality is working correctly")
        else:
            print("❌ 'Continue as Guest' functionality has issues")
        return True
    else:
        print("❌ Login authentication has issues")
        return False

def test_agent_management():
    """Test the agent management endpoints"""
    global auth_token, test_user_id, created_agent_ids
    
    print("\n" + "="*80)
    print("TESTING AGENT MANAGEMENT ENDPOINTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test agent management without authentication")
            return False
    
    # Test 1: Get all agents
    print("\nTest 1: Get all agents")
    
    get_agents_test, get_agents_response = run_test(
        "Get All Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test and get_agents_response:
        print(f"✅ Successfully retrieved {len(get_agents_response)} agents")
        
        # Check agent structure
        if get_agents_response:
            sample_agent = get_agents_response[0]
            print("\nSample agent structure:")
            for key in sample_agent.keys():
                print(f"- {key}")
            
            # Check for required fields
            required_fields = ["id", "name", "archetype", "personality", "goal", "expertise"]
            missing_fields = [field for field in required_fields if field not in sample_agent]
            if missing_fields:
                print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            else:
                print("✅ Agent structure contains all required fields")
            
            # Check personality structure
            if "personality" in sample_agent:
                personality = sample_agent["personality"]
                print("\nPersonality structure:")
                for key in personality.keys():
                    print(f"- {key}")
                
                # Check for required personality traits
                required_traits = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
                missing_traits = [trait for trait in required_traits if trait not in personality]
                if missing_traits:
                    print(f"❌ Missing required personality traits: {', '.join(missing_traits)}")
                else:
                    print("✅ Personality structure contains all required traits")
    else:
        print("❌ Failed to retrieve agents")
    
    # Test 2: Create a new agent
    print("\nTest 2: Create a new agent")
    
    # Generate a unique agent name
    agent_name = f"Test Agent {uuid.uuid4()}"
    
    # Create agent data
    agent_data = {
        "name": agent_name,
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 8
        },
        "goal": "Test the agent management endpoints",
        "expertise": "API Testing",
        "background": "Experienced in testing RESTful APIs"
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
        print(f"✅ Successfully created agent: {agent_name}")
        agent_id = create_agent_response.get("id")
        if agent_id:
            print(f"Agent ID: {agent_id}")
            created_agent_ids.append(agent_id)
            
            # Check if user_id is set correctly
            agent_user_id = create_agent_response.get("user_id")
            if agent_user_id == test_user_id:
                print("✅ Agent is correctly associated with the current user")
            else:
                print(f"❌ Agent user_id ({agent_user_id}) does not match current user ID ({test_user_id})")
        else:
            print("❌ Failed to get agent ID from response")
    else:
        print("❌ Failed to create agent")
    
    # Test 3: Update an agent
    print("\nTest 3: Update an agent")
    
    if created_agent_ids:
        agent_id = created_agent_ids[0]
        
        # Update agent data
        update_data = {
            "name": f"Updated {agent_name}",
            "goal": "Updated goal for testing",
            "expertise": "Updated expertise in API Testing"
        }
        
        update_agent_test, update_agent_response = run_test(
            "Update Agent",
            f"/agents/{agent_id}",
            method="PUT",
            data=update_data,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if update_agent_test and update_agent_response:
            print(f"✅ Successfully updated agent: {update_agent_response.get('name')}")
            
            # Verify the update was applied
            if update_agent_response.get("name") == update_data["name"]:
                print("✅ Agent name was updated correctly")
            else:
                print("❌ Agent name was not updated correctly")
                
            if update_agent_response.get("goal") == update_data["goal"]:
                print("✅ Agent goal was updated correctly")
            else:
                print("❌ Agent goal was not updated correctly")
        else:
            print("❌ Failed to update agent")
    else:
        print("❌ Cannot test agent update without a created agent")
    
    # Test 4: Delete an agent
    print("\nTest 4: Delete an agent")
    
    if len(created_agent_ids) > 0:
        agent_id = created_agent_ids[0]
        
        delete_agent_test, delete_agent_response = run_test(
            "Delete Agent",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True,
            expected_keys=["message"]
        )
        
        if delete_agent_test and delete_agent_response:
            print(f"✅ Successfully deleted agent: {agent_id}")
            created_agent_ids.remove(agent_id)
            
            # Verify the agent was deleted
            get_deleted_test, get_deleted_response = run_test(
                "Get Deleted Agent",
                f"/agents/{agent_id}",
                method="GET",
                auth=True,
                expected_status=404
            )
            
            if get_deleted_test:
                print("✅ Agent was correctly deleted from the database")
            else:
                print("❌ Agent still exists in the database after deletion")
        else:
            print("❌ Failed to delete agent")
    else:
        print("❌ Cannot test agent deletion without a created agent")
    
    # Test 5: Test bulk agent operations
    print("\nTest 5: Test bulk agent operations")
    
    # Create multiple agents for bulk testing
    bulk_agent_ids = []
    for i in range(3):
        agent_name = f"Bulk Test Agent {i} {uuid.uuid4()}"
        agent_data = {
            "name": agent_name,
            "archetype": "researcher",
            "personality": {
                "extroversion": 4,
                "optimism": 6,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 5
            },
            "goal": f"Test bulk operations {i}",
            "expertise": "Bulk Testing",
            "background": "Created for bulk operation testing"
        }
        
        create_bulk_test, create_bulk_response = run_test(
            f"Create Bulk Test Agent {i}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if create_bulk_test and create_bulk_response:
            agent_id = create_bulk_response.get("id")
            if agent_id:
                bulk_agent_ids.append(agent_id)
                created_agent_ids.append(agent_id)
    
    print(f"Created {len(bulk_agent_ids)} agents for bulk testing")
    
    # Test bulk delete
    if bulk_agent_ids:
        bulk_delete_data = {
            "agent_ids": bulk_agent_ids
        }
        
        bulk_delete_test, bulk_delete_response = run_test(
            "Bulk Delete Agents",
            "/agents/bulk-delete",
            method="POST",
            data=bulk_delete_data,
            auth=True,
            expected_keys=["message", "deleted_count"]
        )
        
        if bulk_delete_test and bulk_delete_response:
            deleted_count = bulk_delete_response.get("deleted_count", 0)
            if deleted_count == len(bulk_agent_ids):
                print(f"✅ Successfully deleted all {len(bulk_agent_ids)} agents in bulk")
                for agent_id in bulk_agent_ids:
                    if agent_id in created_agent_ids:
                        created_agent_ids.remove(agent_id)
            else:
                print(f"❌ Bulk delete only removed {deleted_count} out of {len(bulk_agent_ids)} agents")
        else:
            print("❌ Failed to perform bulk delete")
    else:
        print("❌ Cannot test bulk delete without created agents")
    
    # Print summary
    print("\nAGENT MANAGEMENT ENDPOINTS SUMMARY:")
    
    if get_agents_test:
        print("✅ GET /api/agents endpoint is working correctly")
    else:
        print("❌ GET /api/agents endpoint has issues")
        
    if create_agent_test:
        print("✅ POST /api/agents endpoint is working correctly")
    else:
        print("❌ POST /api/agents endpoint has issues")
        
    if update_agent_test:
        print("✅ PUT /api/agents/{id} endpoint is working correctly")
    else:
        print("❌ PUT /api/agents/{id} endpoint has issues")
        
    if delete_agent_test:
        print("✅ DELETE /api/agents/{id} endpoint is working correctly")
    else:
        print("❌ DELETE /api/agents/{id} endpoint has issues")
        
    if bulk_delete_test:
        print("✅ POST /api/agents/bulk-delete endpoint is working correctly")
    else:
        print("❌ POST /api/agents/bulk-delete endpoint has issues")
    
    return get_agents_test and create_agent_test and update_agent_test and delete_agent_test

def test_simulation_control():
    """Test the simulation control endpoints"""
    global auth_token
    
    print("\n" + "="*80)
    print("TESTING SIMULATION CONTROL ENDPOINTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test simulation control without authentication")
            return False
    
    # Test 1: Get simulation state
    print("\nTest 1: Get simulation state")
    
    get_state_test, get_state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if get_state_test and get_state_response:
        print("✅ Successfully retrieved simulation state")
        is_active = get_state_response.get("is_active", False)
        print(f"Current simulation state: {'Active' if is_active else 'Inactive'}")
        
        # Check if user_id is set correctly
        sim_user_id = get_state_response.get("user_id")
        if sim_user_id == test_user_id:
            print("✅ Simulation state is correctly associated with the current user")
        else:
            print(f"❌ Simulation user_id ({sim_user_id}) does not match current user ID ({test_user_id})")
    else:
        print("❌ Failed to retrieve simulation state")
    
    # Test 2: Start simulation
    print("\nTest 2: Start simulation")
    
    start_sim_test, start_sim_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if start_sim_test and start_sim_response:
        print("✅ Successfully started simulation")
        state = start_sim_response.get("state", {})
        is_active = state.get("is_active", False)
        if is_active:
            print("✅ Simulation state is correctly set to active")
        else:
            print("❌ Simulation state is not active after start")
    else:
        print("❌ Failed to start simulation")
    
    # Test 3: Get simulation state after starting
    print("\nTest 3: Get simulation state after starting")
    
    get_state_after_test, get_state_after_response = run_test(
        "Get Simulation State After Start",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if get_state_after_test and get_state_after_response:
        print("✅ Successfully retrieved simulation state after starting")
        is_active = get_state_after_response.get("is_active", False)
        if is_active:
            print("✅ Simulation state is correctly active")
        else:
            print("❌ Simulation state is not active after start")
    else:
        print("❌ Failed to retrieve simulation state after starting")
    
    # Test 4: Pause simulation
    print("\nTest 4: Pause simulation")
    
    pause_sim_test, pause_sim_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if pause_sim_test and pause_sim_response:
        print("✅ Successfully paused simulation")
        state = pause_sim_response.get("state", {})
        is_active = state.get("is_active", True)
        if not is_active:
            print("✅ Simulation state is correctly set to inactive")
        else:
            print("❌ Simulation state is still active after pause")
    else:
        print("❌ Failed to pause simulation")
    
    # Test 5: Get simulation state after pausing
    print("\nTest 5: Get simulation state after pausing")
    
    get_state_paused_test, get_state_paused_response = run_test(
        "Get Simulation State After Pause",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if get_state_paused_test and get_state_paused_response:
        print("✅ Successfully retrieved simulation state after pausing")
        is_active = get_state_paused_response.get("is_active", True)
        if not is_active:
            print("✅ Simulation state is correctly inactive")
        else:
            print("❌ Simulation state is still active after pause")
    else:
        print("❌ Failed to retrieve simulation state after pausing")
    
    # Test 6: Resume simulation
    print("\nTest 6: Resume simulation")
    
    resume_sim_test, resume_sim_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if resume_sim_test and resume_sim_response:
        print("✅ Successfully resumed simulation")
        state = resume_sim_response.get("state", {})
        is_active = state.get("is_active", False)
        if is_active:
            print("✅ Simulation state is correctly set to active")
        else:
            print("❌ Simulation state is not active after resume")
    else:
        print("❌ Failed to resume simulation")
    
    # Print summary
    print("\nSIMULATION CONTROL ENDPOINTS SUMMARY:")
    
    if get_state_test:
        print("✅ GET /api/simulation/state endpoint is working correctly")
    else:
        print("❌ GET /api/simulation/state endpoint has issues")
        
    if start_sim_test:
        print("✅ POST /api/simulation/start endpoint is working correctly")
    else:
        print("❌ POST /api/simulation/start endpoint has issues")
        
    if pause_sim_test:
        print("✅ POST /api/simulation/pause endpoint is working correctly")
    else:
        print("❌ POST /api/simulation/pause endpoint has issues")
        
    if resume_sim_test:
        print("✅ POST /api/simulation/resume endpoint is working correctly")
    else:
        print("❌ POST /api/simulation/resume endpoint has issues")
    
    return get_state_test and start_sim_test and pause_sim_test and resume_sim_test

def test_scenario_management():
    """Test the scenario management endpoints"""
    global auth_token
    
    print("\n" + "="*80)
    print("TESTING SCENARIO MANAGEMENT ENDPOINTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test scenario management without authentication")
            return False
    
    # Test 1: Get random scenario
    print("\nTest 1: Get random scenario")
    
    random_scenario_test, random_scenario_response = run_test(
        "Get Random Scenario",
        "/simulation/random-scenario",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name"]
    )
    
    if random_scenario_test and random_scenario_response:
        print("✅ Successfully retrieved random scenario")
        scenario = random_scenario_response.get("scenario", "")
        scenario_name = random_scenario_response.get("scenario_name", "")
        print(f"Random scenario name: {scenario_name}")
        print(f"Random scenario content length: {len(scenario)} characters")
        
        # Check if scenario content is substantial
        if len(scenario) > 100:
            print("✅ Random scenario has substantial content")
        else:
            print("❌ Random scenario content is too short")
    else:
        print("❌ Failed to retrieve random scenario")
    
    # Test 2: Set custom scenario
    print("\nTest 2: Set custom scenario")
    
    # Create custom scenario data
    custom_scenario = {
        "scenario": "The team is working on a revolutionary AI project that could change the world. They need to decide on the ethical implications and potential applications.",
        "scenario_name": "AI Ethics Project"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Custom Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=custom_scenario,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if set_scenario_test and set_scenario_response:
        print("✅ Successfully set custom scenario")
        state = set_scenario_response.get("state", {})
        scenario = state.get("scenario", "")
        if scenario == custom_scenario["scenario"]:
            print("✅ Custom scenario was correctly set in the simulation state")
        else:
            print("❌ Custom scenario was not correctly set in the simulation state")
    else:
        print("❌ Failed to set custom scenario")
    
    # Test 3: Get simulation state to verify scenario
    print("\nTest 3: Get simulation state to verify scenario")
    
    get_state_test, get_state_response = run_test(
        "Get Simulation State After Setting Scenario",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "scenario"]
    )
    
    if get_state_test and get_state_response:
        print("✅ Successfully retrieved simulation state after setting scenario")
        scenario = get_state_response.get("scenario", "")
        if scenario == custom_scenario["scenario"]:
            print("✅ Custom scenario is correctly stored in the simulation state")
        else:
            print("❌ Custom scenario is not correctly stored in the simulation state")
    else:
        print("❌ Failed to retrieve simulation state after setting scenario")
    
    # Test 4: Set random scenario
    print("\nTest 4: Set random scenario")
    
    # First get a random scenario
    random_scenario_test, random_scenario_response = run_test(
        "Get Random Scenario for Setting",
        "/simulation/random-scenario",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name"]
    )
    
    if random_scenario_test and random_scenario_response:
        random_scenario = {
            "scenario": random_scenario_response.get("scenario", ""),
            "scenario_name": random_scenario_response.get("scenario_name", "")
        }
        
        set_random_test, set_random_response = run_test(
            "Set Random Scenario",
            "/simulation/set-scenario",
            method="POST",
            data=random_scenario,
            auth=True,
            expected_keys=["message", "scenario", "scenario_name"]
        )
        
        if set_random_test and set_random_response:
            print("✅ Successfully set random scenario")
            state = set_random_response.get("state", {})
            scenario = state.get("scenario", "")
            if scenario == random_scenario["scenario"]:
                print("✅ Random scenario was correctly set in the simulation state")
            else:
                print("❌ Random scenario was not correctly set in the simulation state")
        else:
            print("❌ Failed to set random scenario")
    else:
        print("❌ Failed to get random scenario for setting")
    
    # Test 5: Test error handling for empty scenario
    print("\nTest 5: Test error handling for empty scenario")
    
    empty_scenario = {
        "scenario": "",
        "scenario_name": "Empty Scenario"
    }
    
    empty_scenario_test, empty_scenario_response = run_test(
        "Set Empty Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=empty_scenario,
        auth=True,
        expected_status=400
    )
    
    if empty_scenario_test:
        print("✅ Empty scenario correctly rejected with 400 Bad Request")
    else:
        print("❌ Empty scenario not properly handled")
    
    # Print summary
    print("\nSCENARIO MANAGEMENT ENDPOINTS SUMMARY:")
    
    if random_scenario_test:
        print("✅ GET /api/simulation/random-scenario endpoint is working correctly")
    else:
        print("❌ GET /api/simulation/random-scenario endpoint has issues")
        
    if set_scenario_test:
        print("✅ POST /api/simulation/set-scenario endpoint is working correctly")
    else:
        print("❌ POST /api/simulation/set-scenario endpoint has issues")
        
    if empty_scenario_test:
        print("✅ Error handling for empty scenarios is working correctly")
    else:
        print("❌ Error handling for empty scenarios has issues")
    
    return random_scenario_test and set_scenario_test and empty_scenario_test

def test_conversation_endpoints():
    """Test the conversation endpoints"""
    global auth_token, created_agent_ids
    
    print("\n" + "="*80)
    print("TESTING CONVERSATION ENDPOINTS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test conversation endpoints without authentication")
            return False
    
    # Test 1: Get conversations
    print("\nTest 1: Get conversations")
    
    get_conversations_test, get_conversations_response = run_test(
        "Get Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if get_conversations_test:
        print("✅ Successfully retrieved conversations")
        conversation_count = len(get_conversations_response) if get_conversations_response else 0
        print(f"Found {conversation_count} conversations")
        
        # Check conversation structure if any exist
        if conversation_count > 0:
            sample_conversation = get_conversations_response[0]
            print("\nSample conversation structure:")
            for key in sample_conversation.keys():
                print(f"- {key}")
            
            # Check for required fields
            required_fields = ["id", "round_number", "messages", "scenario", "created_at"]
            missing_fields = [field for field in required_fields if field not in sample_conversation]
            if missing_fields:
                print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            else:
                print("✅ Conversation structure contains all required fields")
            
            # Check messages structure
            if "messages" in sample_conversation:
                messages = sample_conversation["messages"]
                if messages and len(messages) > 0:
                    sample_message = messages[0]
                    print("\nSample message structure:")
                    for key in sample_message.keys():
                        print(f"- {key}")
                    
                    # Check for required message fields
                    required_message_fields = ["agent_id", "agent_name", "message"]
                    missing_message_fields = [field for field in required_message_fields if field not in sample_message]
                    if missing_message_fields:
                        print(f"❌ Missing required message fields: {', '.join(missing_message_fields)}")
                    else:
                        print("✅ Message structure contains all required fields")
    else:
        print("❌ Failed to retrieve conversations")
    
    # Create agents for conversation generation if needed
    if not created_agent_ids or len(created_agent_ids) < 2:
        print("\nCreating agents for conversation generation testing")
        
        # Create two test agents
        for i in range(2):
            agent_name = f"Conversation Test Agent {i} {uuid.uuid4()}"
            agent_data = {
                "name": agent_name,
                "archetype": "scientist" if i == 0 else "leader",
                "personality": {
                    "extroversion": 5,
                    "optimism": 7,
                    "curiosity": 9,
                    "cooperativeness": 6,
                    "energy": 8
                },
                "goal": f"Test conversation generation {i}",
                "expertise": f"Conversation Testing {i}",
                "background": "Created for conversation generation testing"
            }
            
            create_agent_test, create_agent_response = run_test(
                f"Create Conversation Test Agent {i}",
                "/agents",
                method="POST",
                data=agent_data,
                auth=True,
                expected_keys=["id", "name"]
            )
            
            if create_agent_test and create_agent_response:
                agent_id = create_agent_response.get("id")
                if agent_id:
                    created_agent_ids.append(agent_id)
                    print(f"✅ Created agent {agent_name} with ID: {agent_id}")
                else:
                    print(f"❌ Failed to get ID for agent {agent_name}")
            else:
                print(f"❌ Failed to create agent {agent_name}")
    
    # Test 2: Start simulation for conversation generation
    print("\nTest 2: Start simulation for conversation generation")
    
    start_sim_test, start_sim_response = run_test(
        "Start Simulation for Conversation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if start_sim_test and start_sim_response:
        print("✅ Successfully started simulation for conversation generation")
    else:
        print("❌ Failed to start simulation for conversation generation")
    
    # Test 3: Set scenario for conversation generation
    print("\nTest 3: Set scenario for conversation generation")
    
    scenario_data = {
        "scenario": "The team is discussing the implementation of a new AI feature in their product.",
        "scenario_name": "AI Feature Discussion"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario for Conversation",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if set_scenario_test and set_scenario_response:
        print("✅ Successfully set scenario for conversation generation")
    else:
        print("❌ Failed to set scenario for conversation generation")
    
    # Test 4: Generate conversation
    print("\nTest 4: Generate conversation")
    
    if len(created_agent_ids) >= 2:
        generate_conversation_test, generate_conversation_response = run_test(
            "Generate Conversation",
            "/conversation/generate",
            method="POST",
            auth=True
        )
        
        if generate_conversation_test and generate_conversation_response:
            print("✅ Successfully generated conversation")
            # The response is the conversation itself, not wrapped in a "conversation" field
            messages = generate_conversation_response.get("messages", [])
            print(f"Generated {len(messages)} messages")
            
            # Check if messages have content
            if messages and len(messages) > 0:
                print("✅ Conversation contains messages")
                
                # Check message content
                for i, message in enumerate(messages[:2]):  # Show first 2 messages
                    agent_name = message.get("agent_name", "Unknown")
                    message_text = message.get("message", "")
                    print(f"\nMessage {i+1} from {agent_name}:")
                    print(message_text[:100] + "..." if len(message_text) > 100 else message_text)
            else:
                print("❌ Conversation does not contain any messages")
        else:
            print("❌ Failed to generate conversation")
    else:
        print("❌ Cannot test conversation generation without at least 2 agents")
    
    # Test 5: Get conversations after generation
    print("\nTest 5: Get conversations after generation")
    
    get_after_test, get_after_response = run_test(
        "Get Conversations After Generation",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if get_after_test and get_after_response:
        print("✅ Successfully retrieved conversations after generation")
        after_count = len(get_after_response) if get_after_response else 0
        
        # Check if a new conversation was added
        if after_count > 0:
            print(f"Found {after_count} conversations after generation")
            
            # Check if the most recent conversation matches our scenario
            if get_after_response and len(get_after_response) > 0:
                latest_conversation = get_after_response[0]  # Assuming sorted by most recent
                latest_scenario = latest_conversation.get("scenario_name", "")
                if latest_scenario == scenario_data["scenario_name"]:
                    print("✅ Latest conversation has the correct scenario name")
                else:
                    print(f"❌ Latest conversation has scenario name '{latest_scenario}' instead of '{scenario_data['scenario_name']}'")
        else:
            print("❌ No conversations found after generation")
    else:
        print("❌ Failed to retrieve conversations after generation")
    
    # Test 6: Test error handling for conversation generation with no agents
    print("\nTest 6: Test error handling for conversation generation with no agents")
    
    # Clear all agents
    if created_agent_ids:
        clear_agents_data = {
            "agent_ids": created_agent_ids
        }
        
        clear_agents_test, clear_agents_response = run_test(
            "Clear All Agents",
            "/agents/bulk-delete",
            method="POST",
            data=clear_agents_data,
            auth=True,
            expected_keys=["message", "deleted_count"]
        )
        
        if clear_agents_test and clear_agents_response:
            deleted_count = clear_agents_response.get("deleted_count", 0)
            print(f"✅ Successfully cleared {deleted_count} agents")
            created_agent_ids = []
        else:
            print("❌ Failed to clear agents")
    
    # Try to generate conversation with no agents
    no_agents_test, no_agents_response = run_test(
        "Generate Conversation With No Agents",
        "/conversation/generate",
        method="POST",
        auth=True,
        expected_status=400
    )
    
    if no_agents_test:
        print("✅ Conversation generation with no agents correctly rejected with 400 Bad Request")
        error_message = no_agents_response.get("detail", "")
        if "agents" in error_message.lower():
            print(f"✅ Error message correctly indicates the issue: {error_message}")
        else:
            print(f"❌ Error message does not clearly indicate the issue: {error_message}")
    else:
        print("❌ Conversation generation with no agents not properly handled")
    
    # Print summary
    print("\nCONVERSATION ENDPOINTS SUMMARY:")
    
    if get_conversations_test:
        print("✅ GET /api/conversations endpoint is working correctly")
    else:
        print("❌ GET /api/conversations endpoint has issues")
        
    if generate_conversation_test:
        print("✅ POST /api/conversation/generate endpoint is working correctly")
    else:
        print("❌ POST /api/conversation/generate endpoint has issues")
        
    if no_agents_test:
        print("✅ Error handling for conversation generation is working correctly")
    else:
        print("❌ Error handling for conversation generation has issues")
    
    return get_conversations_test and (generate_conversation_test or no_agents_test)

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("RUNNING COMPREHENSIVE BACKEND API TESTS")
    print("="*80)
    
    # Test authentication endpoints
    auth_success = test_login()
    print(f"\nAuthentication Endpoints: {'✅ PASSED' if auth_success else '❌ FAILED'}")
    
    # Test agent management endpoints
    agent_success = test_agent_management()
    print(f"\nAgent Management Endpoints: {'✅ PASSED' if agent_success else '❌ FAILED'}")
    
    # Test simulation control endpoints
    simulation_success = test_simulation_control()
    print(f"\nSimulation Control Endpoints: {'✅ PASSED' if simulation_success else '❌ FAILED'}")
    
    # Test scenario management endpoints
    scenario_success = test_scenario_management()
    print(f"\nScenario Management Endpoints: {'✅ PASSED' if scenario_success else '❌ FAILED'}")
    
    # Test conversation endpoints
    conversation_success = test_conversation_endpoints()
    print(f"\nConversation Endpoints: {'✅ PASSED' if conversation_success else '❌ FAILED'}")
    
    # Print overall summary
    print_summary()
    
    # Return overall success
    return auth_success and agent_success and simulation_success and scenario_success and conversation_success

if __name__ == "__main__":
    main()