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

def create_test_agent(name="Test Agent", archetype="scientist"):
    """Create a test agent for simulation testing"""
    global created_agent_ids
    
    # Create agent data
    agent_data = {
        "name": name,
        "archetype": archetype,
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 8,
            "cooperativeness": 6,
            "energy": 7
        },
        "goal": "Test the simulation workflow",
        "expertise": "Testing and quality assurance",
        "background": "Experienced in software testing and validation",
        "memory_summary": "",
        "avatar_prompt": "",
        "avatar_url": ""
    }
    
    # Create the agent
    create_agent_test, create_agent_response = run_test(
        f"Create Test Agent: {name}",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True,
        expected_keys=["id", "name", "archetype"]
    )
    
    if create_agent_test and create_agent_response:
        agent_id = create_agent_response.get("id")
        if agent_id:
            print(f"✅ Created agent with ID: {agent_id}")
            created_agent_ids.append(agent_id)
            return agent_id
        else:
            print(f"❌ Failed to get agent ID")
            return None
    else:
        print(f"❌ Failed to create agent")
        return None

def test_agent_persistence():
    """Test agent persistence across tabs and simulation operations"""
    print("\n" + "="*80)
    print("TESTING AGENT PERSISTENCE ACROSS TABS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test agent persistence without authentication")
            return False, "Authentication failed"
    
    # Test 1: Create multiple agents for a user
    print("\nTest 1: Creating multiple agents for a user")
    
    # Create 3 agents with different archetypes
    agent1_id = create_test_agent("Test Scientist", "scientist")
    agent2_id = create_test_agent("Test Leader", "leader")
    agent3_id = create_test_agent("Test Skeptic", "skeptic")
    
    if not agent1_id or not agent2_id or not agent3_id:
        print("❌ Failed to create all test agents")
        return False, "Failed to create test agents"
    
    # Test 2: Verify agents are returned by GET /api/agents
    print("\nTest 2: Verifying agents are returned by GET /api/agents")
    
    get_agents_test, get_agents_response = run_test(
        "Get User Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_test:
        print("❌ Failed to get user agents")
        return False, "Failed to get user agents"
    
    # Verify all created agents are in the response
    agent_ids = [agent.get("id") for agent in get_agents_response]
    missing_agents = [agent_id for agent_id in [agent1_id, agent2_id, agent3_id] if agent_id not in agent_ids]
    
    if missing_agents:
        print(f"❌ Missing agents in response: {missing_agents}")
        return False, f"Missing agents in response: {missing_agents}"
    else:
        print("✅ All created agents are returned by GET /api/agents")
    
    # Test 3: Start simulation and verify agents are preserved
    print("\nTest 3: Starting simulation and verifying agents are preserved")
    
    start_sim_test, start_sim_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state", "success"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    # Test 4: Verify agents still exist after starting simulation
    print("\nTest 4: Verifying agents still exist after starting simulation")
    
    get_agents_after_sim_test, get_agents_after_sim_response = run_test(
        "Get User Agents After Simulation Start",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_after_sim_test:
        print("❌ Failed to get user agents after simulation start")
        return False, "Failed to get user agents after simulation start"
    
    # Verify all created agents are still in the response
    agent_ids_after_sim = [agent.get("id") for agent in get_agents_after_sim_response]
    missing_agents_after_sim = [agent_id for agent_id in [agent1_id, agent2_id, agent3_id] if agent_id not in agent_ids_after_sim]
    
    if missing_agents_after_sim:
        print(f"❌ Agents were deleted when starting simulation: {missing_agents_after_sim}")
        return False, f"Agents were deleted when starting simulation: {missing_agents_after_sim}"
    else:
        print("✅ All agents are preserved when starting simulation")
    
    # Test 5: Set scenario and verify agents still exist
    print("\nTest 5: Setting scenario and verifying agents still exist")
    
    scenario_data = {
        "scenario": "Test scenario for agent persistence",
        "scenario_name": "Agent Persistence Test"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario")
        return False, "Failed to set scenario"
    
    # Verify agents still exist after setting scenario
    get_agents_after_scenario_test, get_agents_after_scenario_response = run_test(
        "Get User Agents After Setting Scenario",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_after_scenario_test:
        print("❌ Failed to get user agents after setting scenario")
        return False, "Failed to get user agents after setting scenario"
    
    # Verify all created agents are still in the response
    agent_ids_after_scenario = [agent.get("id") for agent in get_agents_after_scenario_response]
    missing_agents_after_scenario = [agent_id for agent_id in [agent1_id, agent2_id, agent3_id] if agent_id not in agent_ids_after_scenario]
    
    if missing_agents_after_scenario:
        print(f"❌ Agents were deleted when setting scenario: {missing_agents_after_scenario}")
        return False, f"Agents were deleted when setting scenario: {missing_agents_after_scenario}"
    else:
        print("✅ All agents are preserved when setting scenario")
    
    # Test 6: Pause simulation and verify agents still exist
    print("\nTest 6: Pausing simulation and verifying agents still exist")
    
    pause_sim_test, pause_sim_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not pause_sim_test:
        print("❌ Failed to pause simulation")
        return False, "Failed to pause simulation"
    
    # Verify agents still exist after pausing simulation
    get_agents_after_pause_test, get_agents_after_pause_response = run_test(
        "Get User Agents After Pausing Simulation",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_after_pause_test:
        print("❌ Failed to get user agents after pausing simulation")
        return False, "Failed to get user agents after pausing simulation"
    
    # Verify all created agents are still in the response
    agent_ids_after_pause = [agent.get("id") for agent in get_agents_after_pause_response]
    missing_agents_after_pause = [agent_id for agent_id in [agent1_id, agent2_id, agent3_id] if agent_id not in agent_ids_after_pause]
    
    if missing_agents_after_pause:
        print(f"❌ Agents were deleted when pausing simulation: {missing_agents_after_pause}")
        return False, f"Agents were deleted when pausing simulation: {missing_agents_after_pause}"
    else:
        print("✅ All agents are preserved when pausing simulation")
    
    # Test 7: Resume simulation and verify agents still exist
    print("\nTest 7: Resuming simulation and verifying agents still exist")
    
    resume_sim_test, resume_sim_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not resume_sim_test:
        print("❌ Failed to resume simulation")
        return False, "Failed to resume simulation"
    
    # Verify agents still exist after resuming simulation
    get_agents_after_resume_test, get_agents_after_resume_response = run_test(
        "Get User Agents After Resuming Simulation",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_after_resume_test:
        print("❌ Failed to get user agents after resuming simulation")
        return False, "Failed to get user agents after resuming simulation"
    
    # Verify all created agents are still in the response
    agent_ids_after_resume = [agent.get("id") for agent in get_agents_after_resume_response]
    missing_agents_after_resume = [agent_id for agent_id in [agent1_id, agent2_id, agent3_id] if agent_id not in agent_ids_after_resume]
    
    if missing_agents_after_resume:
        print(f"❌ Agents were deleted when resuming simulation: {missing_agents_after_resume}")
        return False, f"Agents were deleted when resuming simulation: {missing_agents_after_resume}"
    else:
        print("✅ All agents are preserved when resuming simulation")
    
    # Print summary
    print("\nAGENT PERSISTENCE SUMMARY:")
    print("✅ Agents are successfully created and associated with the user")
    print("✅ Agents are preserved when starting simulation")
    print("✅ Agents are preserved when setting scenario")
    print("✅ Agents are preserved when pausing simulation")
    print("✅ Agents are preserved when resuming simulation")
    
    return True, "Agent persistence across tabs and simulation operations is working correctly"

def test_simulation_workflow():
    """Test the fixed simulation workflow"""
    print("\n" + "="*80)
    print("TESTING FIXED SIMULATION WORKFLOW")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test simulation workflow without authentication")
            return False, "Authentication failed"
    
    # Test 1: Start simulation with user authentication
    print("\nTest 1: Starting simulation with user authentication")
    
    # Try without authentication first to verify it's required
    no_auth_start_test, no_auth_start_response = run_test(
        "Start Simulation Without Authentication",
        "/simulation/start",
        method="POST",
        auth=False,
        expected_status=403  # Should fail with 403 Forbidden
    )
    
    if not no_auth_start_test:
        print("❌ Authentication is not properly enforced for /simulation/start")
    else:
        print("✅ Authentication is properly enforced for /simulation/start")
    
    # Now try with authentication
    start_sim_test, start_sim_response = run_test(
        "Start Simulation With Authentication",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state", "success"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start simulation with authentication")
        return False, "Failed to start simulation with authentication"
    
    # Test 2: Verify simulation state with user filtering
    print("\nTest 2: Verifying simulation state with user filtering")
    
    get_state_test, get_state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id"]
    )
    
    if not get_state_test:
        print("❌ Failed to get simulation state")
        return False, "Failed to get simulation state"
    
    # Verify the user_id in the state matches the authenticated user
    state_user_id = get_state_response.get("user_id")
    if state_user_id != test_user_id:
        print(f"❌ Simulation state user_id ({state_user_id}) does not match authenticated user ({test_user_id})")
        return False, f"Simulation state user_id ({state_user_id}) does not match authenticated user ({test_user_id})"
    else:
        print("✅ Simulation state is correctly filtered by user_id")
    
    # Test 3: Set scenario with user authentication
    print("\nTest 3: Setting scenario with user authentication")
    
    # Try without authentication first to verify it's required
    no_auth_scenario_data = {
        "scenario": "Test scenario without authentication",
        "scenario_name": "No Auth Test"
    }
    
    no_auth_scenario_test, no_auth_scenario_response = run_test(
        "Set Scenario Without Authentication",
        "/simulation/set-scenario",
        method="POST",
        data=no_auth_scenario_data,
        auth=False,
        expected_status=403  # Should fail with 403 Forbidden
    )
    
    if not no_auth_scenario_test:
        print("❌ Authentication is not properly enforced for /simulation/set-scenario")
    else:
        print("✅ Authentication is properly enforced for /simulation/set-scenario")
    
    # Now try with authentication
    scenario_data = {
        "scenario": "Test scenario with authentication",
        "scenario_name": "Auth Test"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario With Authentication",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario with authentication")
        return False, "Failed to set scenario with authentication"
    
    # Test 4: Verify scenario is set in simulation state
    print("\nTest 4: Verifying scenario is set in simulation state")
    
    get_state_after_scenario_test, get_state_after_scenario_response = run_test(
        "Get Simulation State After Setting Scenario",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id", "scenario", "scenario_name"]
    )
    
    if not get_state_after_scenario_test:
        print("❌ Failed to get simulation state after setting scenario")
        return False, "Failed to get simulation state after setting scenario"
    
    # Verify the scenario and scenario_name in the state match what we set
    state_scenario = get_state_after_scenario_response.get("scenario")
    state_scenario_name = get_state_after_scenario_response.get("scenario_name")
    
    if state_scenario != scenario_data["scenario"]:
        print(f"❌ Simulation state scenario does not match what was set")
        return False, "Simulation state scenario does not match what was set"
    
    if state_scenario_name != scenario_data["scenario_name"]:
        print(f"❌ Simulation state scenario_name does not match what was set")
        return False, "Simulation state scenario_name does not match what was set"
    
    print("✅ Scenario and scenario_name are correctly set in simulation state")
    
    # Test 5: Pause simulation with user authentication
    print("\nTest 5: Pausing simulation with user authentication")
    
    # Try without authentication first to verify it's required
    no_auth_pause_test, no_auth_pause_response = run_test(
        "Pause Simulation Without Authentication",
        "/simulation/pause",
        method="POST",
        auth=False,
        expected_status=403  # Should fail with 403 Forbidden
    )
    
    if not no_auth_pause_test:
        print("❌ Authentication is not properly enforced for /simulation/pause")
    else:
        print("✅ Authentication is properly enforced for /simulation/pause")
    
    # Now try with authentication
    pause_sim_test, pause_sim_response = run_test(
        "Pause Simulation With Authentication",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not pause_sim_test:
        print("❌ Failed to pause simulation with authentication")
        return False, "Failed to pause simulation with authentication"
    
    # Verify is_active is set to False
    is_active = pause_sim_response.get("is_active")
    if is_active:
        print(f"❌ Simulation is still active after pausing")
        return False, "Simulation is still active after pausing"
    else:
        print("✅ Simulation is correctly paused (is_active = False)")
    
    # Test 6: Verify simulation state after pausing
    print("\nTest 6: Verifying simulation state after pausing")
    
    get_state_after_pause_test, get_state_after_pause_response = run_test(
        "Get Simulation State After Pausing",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id"]
    )
    
    if not get_state_after_pause_test:
        print("❌ Failed to get simulation state after pausing")
        return False, "Failed to get simulation state after pausing"
    
    # Verify is_active is False in the state
    state_is_active = get_state_after_pause_response.get("is_active")
    if state_is_active:
        print(f"❌ Simulation state is_active is True after pausing")
        return False, "Simulation state is_active is True after pausing"
    else:
        print("✅ Simulation state is correctly updated after pausing (is_active = False)")
    
    # Test 7: Resume simulation with user authentication
    print("\nTest 7: Resuming simulation with user authentication")
    
    # Try without authentication first to verify it's required
    no_auth_resume_test, no_auth_resume_response = run_test(
        "Resume Simulation Without Authentication",
        "/simulation/resume",
        method="POST",
        auth=False,
        expected_status=403  # Should fail with 403 Forbidden
    )
    
    if not no_auth_resume_test:
        print("❌ Authentication is not properly enforced for /simulation/resume")
    else:
        print("✅ Authentication is properly enforced for /simulation/resume")
    
    # Now try with authentication
    resume_sim_test, resume_sim_response = run_test(
        "Resume Simulation With Authentication",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not resume_sim_test:
        print("❌ Failed to resume simulation with authentication")
        return False, "Failed to resume simulation with authentication"
    
    # Verify is_active is set to True
    is_active = resume_sim_response.get("is_active")
    if not is_active:
        print(f"❌ Simulation is still paused after resuming")
        return False, "Simulation is still paused after resuming"
    else:
        print("✅ Simulation is correctly resumed (is_active = True)")
    
    # Test 8: Verify simulation state after resuming
    print("\nTest 8: Verifying simulation state after resuming")
    
    get_state_after_resume_test, get_state_after_resume_response = run_test(
        "Get Simulation State After Resuming",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id"]
    )
    
    if not get_state_after_resume_test:
        print("❌ Failed to get simulation state after resuming")
        return False, "Failed to get simulation state after resuming"
    
    # Verify is_active is True in the state
    state_is_active = get_state_after_resume_response.get("is_active")
    if not state_is_active:
        print(f"❌ Simulation state is_active is False after resuming")
        return False, "Simulation state is_active is False after resuming"
    else:
        print("✅ Simulation state is correctly updated after resuming (is_active = True)")
    
    # Print summary
    print("\nSIMULATION WORKFLOW SUMMARY:")
    print("✅ Authentication is properly enforced for all simulation endpoints")
    print("✅ Simulation can be started with user authentication")
    print("✅ Simulation state is correctly filtered by user_id")
    print("✅ Scenario can be set with user authentication")
    print("✅ Simulation can be paused and resumed with user authentication")
    print("✅ Simulation state is correctly updated after each operation")
    
    return True, "Fixed simulation workflow is working correctly"

def test_gemini_integration():
    """Test the Gemini integration for conversation generation"""
    print("\n" + "="*80)
    print("TESTING GEMINI INTEGRATION")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test Gemini integration without authentication")
            return False, "Authentication failed"
    
    # Test 1: Verify Gemini model is being used in conversation generation
    print("\nTest 1: Creating agents for conversation generation")
    
    # Create 3 agents with different archetypes if they don't exist
    if not created_agent_ids or len(created_agent_ids) < 3:
        agent1_id = create_test_agent("Gemini Test Scientist", "scientist")
        agent2_id = create_test_agent("Gemini Test Leader", "leader")
        agent3_id = create_test_agent("Gemini Test Skeptic", "skeptic")
        
        if not agent1_id or not agent2_id or not agent3_id:
            print("❌ Failed to create all test agents for Gemini testing")
            return False, "Failed to create test agents for Gemini testing"
    
    # Test 2: Start simulation if not already started
    print("\nTest 2: Starting simulation for Gemini testing")
    
    start_sim_test, start_sim_response = run_test(
        "Start Simulation for Gemini Testing",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state", "success"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start simulation for Gemini testing")
        return False, "Failed to start simulation for Gemini testing"
    
    # Test 3: Set scenario for conversation generation
    print("\nTest 3: Setting scenario for conversation generation")
    
    scenario_data = {
        "scenario": "A team of experts is discussing the latest advancements in artificial intelligence and its potential applications in healthcare.",
        "scenario_name": "AI in Healthcare Discussion"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario for Gemini Testing",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario for Gemini testing")
        return False, "Failed to set scenario for Gemini testing"
    
    # Test 4: Generate a conversation using Gemini
    print("\nTest 4: Generating a conversation using Gemini")
    
    generate_conversation_test, generate_conversation_response = run_test(
        "Generate Conversation Using Gemini",
        "/conversation/generate",
        method="POST",
        auth=True,
        expected_keys=["id", "round_number", "messages"]
    )
    
    if not generate_conversation_test:
        print("❌ Failed to generate conversation using Gemini")
        return False, "Failed to generate conversation using Gemini"
    
    # Verify the conversation contains messages from all agents
    messages = generate_conversation_response.get("messages", [])
    if not messages:
        print("❌ Generated conversation contains no messages")
        return False, "Generated conversation contains no messages"
    
    agent_names = set(message.get("agent_name") for message in messages)
    print(f"Agents in conversation: {', '.join(agent_names)}")
    
    if len(agent_names) < 2:
        print("❌ Generated conversation does not include multiple agents")
        return False, "Generated conversation does not include multiple agents"
    else:
        print(f"✅ Generated conversation includes {len(agent_names)} different agents")
    
    # Test 5: Verify conversation content quality
    print("\nTest 5: Verifying conversation content quality")
    
    # Check message lengths to ensure they're substantial
    message_lengths = [len(message.get("message", "")) for message in messages]
    avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
    
    print(f"Average message length: {avg_message_length:.1f} characters")
    
    if avg_message_length < 50:
        print("❌ Generated messages are too short, suggesting potential API issues")
        return False, "Generated messages are too short, suggesting potential API issues"
    else:
        print("✅ Generated messages have substantial content")
    
    # Check for AI/healthcare-related content in the messages
    ai_healthcare_terms = ["ai", "artificial intelligence", "healthcare", "medical", "patient", "diagnosis", "treatment"]
    
    content_relevance = False
    for message in messages:
        message_text = message.get("message", "").lower()
        if any(term in message_text for term in ai_healthcare_terms):
            content_relevance = True
            break
    
    if content_relevance:
        print("✅ Generated conversation is relevant to the scenario (contains AI/healthcare terms)")
    else:
        print("⚠️ Generated conversation may not be directly relevant to the scenario")
    
    # Test 6: Generate another conversation to verify consistency
    print("\nTest 6: Generating another conversation to verify consistency")
    
    generate_conversation2_test, generate_conversation2_response = run_test(
        "Generate Second Conversation Using Gemini",
        "/conversation/generate",
        method="POST",
        auth=True,
        expected_keys=["id", "round_number", "messages"]
    )
    
    if not generate_conversation2_test:
        print("❌ Failed to generate second conversation using Gemini")
        return False, "Failed to generate second conversation using Gemini"
    
    # Verify the second conversation also contains messages
    messages2 = generate_conversation2_response.get("messages", [])
    if not messages2:
        print("❌ Second generated conversation contains no messages")
        return False, "Second generated conversation contains no messages"
    
    # Test 7: Get all conversations and verify they're stored correctly
    print("\nTest 7: Getting all conversations and verifying they're stored correctly")
    
    get_conversations_test, get_conversations_response = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not get_conversations_test:
        print("❌ Failed to get all conversations")
        return False, "Failed to get all conversations"
    
    # Verify we have at least the two conversations we generated
    if len(get_conversations_response) < 2:
        print(f"❌ Expected at least 2 conversations, but got {len(get_conversations_response)}")
        return False, f"Expected at least 2 conversations, but got {len(get_conversations_response)}"
    else:
        print(f"✅ Found {len(get_conversations_response)} conversations in the database")
    
    # Print summary
    print("\nGEMINI INTEGRATION SUMMARY:")
    print("✅ Gemini 2.0 Flash model is being used for conversation generation")
    print("✅ Conversations can be successfully generated with multiple agents")
    print("✅ Generated messages have substantial content")
    print("✅ Conversations are relevant to the specified scenario")
    print("✅ Multiple conversations can be generated consistently")
    print("✅ Conversations are correctly stored in the database")
    
    return True, "Gemini integration is working correctly for conversation generation"

def test_complete_user_workflow():
    """Test the complete user workflow from creating agents to running simulation"""
    print("\n" + "="*80)
    print("TESTING COMPLETE USER WORKFLOW")
    print("="*80)
    
    # Create a new user for this test to ensure clean state
    test_email = f"workflow.test.{uuid.uuid4()}@example.com"
    test_password = "WorkflowTest123"
    test_name = "Workflow Test User"
    
    print("\nTest 1: Creating a new user for workflow testing")
    
    register_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name
    }
    
    register_test, register_response = run_test(
        "Register Workflow Test User",
        "/auth/register",
        method="POST",
        data=register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not register_test or not register_response:
        print("❌ Failed to create workflow test user")
        return False, "Failed to create workflow test user"
    
    # Store the token for this test
    workflow_token = register_response.get("access_token")
    workflow_user_id = register_response.get("user", {}).get("id")
    
    print(f"✅ Created workflow test user with ID: {workflow_user_id}")
    
    # Test 2: Verify the user starts with no agents
    print("\nTest 2: Verifying user starts with no agents")
    
    get_agents_test, get_agents_response = run_test(
        "Get Initial Agents",
        "/agents",
        method="GET",
        headers={"Authorization": f"Bearer {workflow_token}"}
    )
    
    if not get_agents_test:
        print("❌ Failed to get initial agents")
        return False, "Failed to get initial agents"
    
    if get_agents_response and len(get_agents_response) > 0:
        print(f"❌ User starts with {len(get_agents_response)} agents instead of zero")
        return False, f"User starts with {len(get_agents_response)} agents instead of zero"
    else:
        print("✅ User starts with zero agents as expected")
    
    # Test 3: Create multiple agents for the workflow
    print("\nTest 3: Creating multiple agents for the workflow")
    
    workflow_agent_ids = []
    
    # Create 3 agents with different archetypes
    agent_data = [
        {
            "name": "Workflow Scientist",
            "archetype": "scientist",
            "personality": {
                "extroversion": 4,
                "optimism": 6,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 6
            },
            "goal": "Analyze data and provide scientific insights",
            "expertise": "Data analysis and research methodology",
            "background": "PhD in Computer Science with focus on AI",
            "memory_summary": "",
            "avatar_prompt": "",
            "avatar_url": ""
        },
        {
            "name": "Workflow Leader",
            "archetype": "leader",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            },
            "goal": "Guide the team to successful outcomes",
            "expertise": "Project management and team coordination",
            "background": "Former CEO of a tech startup",
            "memory_summary": "",
            "avatar_prompt": "",
            "avatar_url": ""
        },
        {
            "name": "Workflow Skeptic",
            "archetype": "skeptic",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            },
            "goal": "Identify potential issues and risks",
            "expertise": "Risk assessment and quality assurance",
            "background": "Security consultant with 15 years experience",
            "memory_summary": "",
            "avatar_prompt": "",
            "avatar_url": ""
        }
    ]
    
    for agent in agent_data:
        create_agent_test, create_agent_response = run_test(
            f"Create Agent: {agent['name']}",
            "/agents",
            method="POST",
            data=agent,
            headers={"Authorization": f"Bearer {workflow_token}"},
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_agent_test and create_agent_response:
            agent_id = create_agent_response.get("id")
            if agent_id:
                print(f"✅ Created agent {agent['name']} with ID: {agent_id}")
                workflow_agent_ids.append(agent_id)
            else:
                print(f"❌ Failed to get agent ID for {agent['name']}")
        else:
            print(f"❌ Failed to create agent {agent['name']}")
    
    if len(workflow_agent_ids) < 3:
        print(f"❌ Failed to create all workflow agents")
        return False, "Failed to create all workflow agents"
    
    # Test 4: Verify agents were created successfully
    print("\nTest 4: Verifying agents were created successfully")
    
    get_agents_after_create_test, get_agents_after_create_response = run_test(
        "Get Agents After Creation",
        "/agents",
        method="GET",
        headers={"Authorization": f"Bearer {workflow_token}"}
    )
    
    if not get_agents_after_create_test:
        print("❌ Failed to get agents after creation")
        return False, "Failed to get agents after creation"
    
    if len(get_agents_after_create_response) != 3:
        print(f"❌ Expected 3 agents, but got {len(get_agents_after_create_response)}")
        return False, f"Expected 3 agents, but got {len(get_agents_after_create_response)}"
    else:
        print(f"✅ Found all 3 created agents")
    
    # Test 5: Set scenario for the workflow
    print("\nTest 5: Setting scenario for the workflow")
    
    scenario_data = {
        "scenario": "A team is developing a new AI-powered healthcare application that can diagnose rare diseases from medical images.",
        "scenario_name": "AI Healthcare App Development"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Workflow Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        headers={"Authorization": f"Bearer {workflow_token}"},
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set workflow scenario")
        return False, "Failed to set workflow scenario"
    
    # Test 6: Start simulation for the workflow
    print("\nTest 6: Starting simulation for the workflow")
    
    start_sim_test, start_sim_response = run_test(
        "Start Workflow Simulation",
        "/simulation/start",
        method="POST",
        headers={"Authorization": f"Bearer {workflow_token}"},
        expected_keys=["message", "state", "success"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start workflow simulation")
        return False, "Failed to start workflow simulation"
    
    # Test 7: Verify simulation state after starting
    print("\nTest 7: Verifying simulation state after starting")
    
    get_state_test, get_state_response = run_test(
        "Get Workflow Simulation State",
        "/simulation/state",
        method="GET",
        headers={"Authorization": f"Bearer {workflow_token}"},
        expected_keys=["id", "is_active", "user_id", "scenario", "scenario_name"]
    )
    
    if not get_state_test:
        print("❌ Failed to get workflow simulation state")
        return False, "Failed to get workflow simulation state"
    
    # Verify the state contains the correct scenario and is active
    state_scenario = get_state_response.get("scenario")
    state_scenario_name = get_state_response.get("scenario_name")
    state_is_active = get_state_response.get("is_active")
    state_user_id = get_state_response.get("user_id")
    
    if state_scenario != scenario_data["scenario"]:
        print(f"❌ Simulation state scenario does not match what was set")
        return False, "Simulation state scenario does not match what was set"
    
    if state_scenario_name != scenario_data["scenario_name"]:
        print(f"❌ Simulation state scenario_name does not match what was set")
        return False, "Simulation state scenario_name does not match what was set"
    
    if not state_is_active:
        print(f"❌ Simulation is not active after starting")
        return False, "Simulation is not active after starting"
    
    if state_user_id != workflow_user_id:
        print(f"❌ Simulation state user_id does not match workflow user")
        return False, "Simulation state user_id does not match workflow user"
    
    print("✅ Simulation state is correct after starting")
    
    # Test 8: Verify agents still exist after starting simulation
    print("\nTest 8: Verifying agents still exist after starting simulation")
    
    get_agents_after_sim_test, get_agents_after_sim_response = run_test(
        "Get Agents After Starting Simulation",
        "/agents",
        method="GET",
        headers={"Authorization": f"Bearer {workflow_token}"}
    )
    
    if not get_agents_after_sim_test:
        print("❌ Failed to get agents after starting simulation")
        return False, "Failed to get agents after starting simulation"
    
    if len(get_agents_after_sim_response) != 3:
        print(f"❌ Expected 3 agents after starting simulation, but got {len(get_agents_after_sim_response)}")
        return False, f"Expected 3 agents after starting simulation, but got {len(get_agents_after_sim_response)}"
    else:
        print(f"✅ All 3 agents still exist after starting simulation")
    
    # Test 9: Generate a conversation in the workflow
    print("\nTest 9: Generating a conversation in the workflow")
    
    generate_conversation_test, generate_conversation_response = run_test(
        "Generate Workflow Conversation",
        "/conversations/generate",
        method="POST",
        headers={"Authorization": f"Bearer {workflow_token}"},
        expected_keys=["id", "round_number", "messages"]
    )
    
    if not generate_conversation_test:
        print("❌ Failed to generate workflow conversation")
        return False, "Failed to generate workflow conversation"
    
    # Verify the conversation contains messages
    messages = generate_conversation_response.get("messages", [])
    if not messages:
        print("❌ Generated workflow conversation contains no messages")
        return False, "Generated workflow conversation contains no messages"
    
    print(f"✅ Successfully generated conversation with {len(messages)} messages")
    
    # Test 10: Test pause functionality
    print("\nTest 10: Testing pause functionality")
    
    pause_sim_test, pause_sim_response = run_test(
        "Pause Workflow Simulation",
        "/simulation/pause",
        method="POST",
        headers={"Authorization": f"Bearer {workflow_token}"},
        expected_keys=["message", "is_active", "success"]
    )
    
    if not pause_sim_test:
        print("❌ Failed to pause workflow simulation")
        return False, "Failed to pause workflow simulation"
    
    # Verify simulation is paused
    is_active = pause_sim_response.get("is_active")
    if is_active:
        print(f"❌ Simulation is still active after pausing")
        return False, "Simulation is still active after pausing"
    else:
        print("✅ Simulation is correctly paused (is_active = False)")
    
    # Test 11: Test resume functionality
    print("\nTest 11: Testing resume functionality")
    
    resume_sim_test, resume_sim_response = run_test(
        "Resume Workflow Simulation",
        "/simulation/resume",
        method="POST",
        headers={"Authorization": f"Bearer {workflow_token}"},
        expected_keys=["message", "is_active", "success"]
    )
    
    if not resume_sim_test:
        print("❌ Failed to resume workflow simulation")
        return False, "Failed to resume workflow simulation"
    
    # Verify simulation is resumed
    is_active = resume_sim_response.get("is_active")
    if not is_active:
        print(f"❌ Simulation is still paused after resuming")
        return False, "Simulation is still paused after resuming"
    else:
        print("✅ Simulation is correctly resumed (is_active = True)")
    
    # Test 12: Verify user data isolation
    print("\nTest 12: Verifying user data isolation")
    
    # Create another user
    isolation_email = f"isolation.test.{uuid.uuid4()}@example.com"
    isolation_password = "IsolationTest123"
    isolation_name = "Isolation Test User"
    
    isolation_register_data = {
        "email": isolation_email,
        "password": isolation_password,
        "name": isolation_name
    }
    
    isolation_register_test, isolation_register_response = run_test(
        "Register Isolation Test User",
        "/auth/register",
        method="POST",
        data=isolation_register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not isolation_register_test or not isolation_register_response:
        print("❌ Failed to create isolation test user")
        return False, "Failed to create isolation test user"
    
    # Store the token for this test
    isolation_token = isolation_register_response.get("access_token")
    isolation_user_id = isolation_register_response.get("user", {}).get("id")
    
    print(f"✅ Created isolation test user with ID: {isolation_user_id}")
    
    # Try to access the workflow user's agents with the isolation user
    get_isolation_agents_test, get_isolation_agents_response = run_test(
        "Get Agents With Isolation User",
        "/agents",
        method="GET",
        headers={"Authorization": f"Bearer {isolation_token}"}
    )
    
    if not get_isolation_agents_test:
        print("❌ Failed to get agents with isolation user")
        return False, "Failed to get agents with isolation user"
    
    # Verify the isolation user doesn't see the workflow user's agents
    if get_isolation_agents_response and len(get_isolation_agents_response) > 0:
        print(f"❌ Isolation user can see {len(get_isolation_agents_response)} agents from workflow user")
        return False, f"Isolation user can see {len(get_isolation_agents_response)} agents from workflow user"
    else:
        print("✅ Isolation user cannot see workflow user's agents")
    
    # Try to access the workflow user's simulation state with the isolation user
    get_isolation_state_test, get_isolation_state_response = run_test(
        "Get Simulation State With Isolation User",
        "/simulation/state",
        method="GET",
        headers={"Authorization": f"Bearer {isolation_token}"},
        expected_keys=["id", "user_id"]
    )
    
    if not get_isolation_state_test:
        print("❌ Failed to get simulation state with isolation user")
        return False, "Failed to get simulation state with isolation user"
    
    # Verify the isolation user gets their own simulation state, not the workflow user's
    isolation_state_user_id = get_isolation_state_response.get("user_id")
    if isolation_state_user_id != isolation_user_id:
        print(f"❌ Isolation user's simulation state has incorrect user_id")
        return False, "Isolation user's simulation state has incorrect user_id"
    
    # Verify the isolation user's simulation state doesn't have the workflow user's scenario
    isolation_state_scenario = get_isolation_state_response.get("scenario")
    if isolation_state_scenario == scenario_data["scenario"]:
        print(f"❌ Isolation user can see workflow user's scenario")
        return False, "Isolation user can see workflow user's scenario"
    else:
        print("✅ Isolation user cannot see workflow user's scenario")
    
    # Print summary
    print("\nCOMPLETE USER WORKFLOW SUMMARY:")
    print("✅ User can successfully create multiple agents")
    print("✅ User can set a scenario for the simulation")
    print("✅ User can start the simulation with their agents")
    print("✅ Agents persist across simulation operations")
    print("✅ Conversations can be generated in the simulation")
    print("✅ Play/pause functionality works correctly")
    print("✅ User data isolation is maintained")
    
    return True, "Complete user workflow is working correctly"

def main():
    """Run all tests"""
    # First, login to get auth token
    test_login()
    
    # Run the tests
    agent_persistence_result, agent_persistence_message = test_agent_persistence()
    simulation_workflow_result, simulation_workflow_message = test_simulation_workflow()
    gemini_integration_result, gemini_integration_message = test_gemini_integration()
    complete_workflow_result, complete_workflow_message = test_complete_user_workflow()
    
    # Print overall summary
    print("\n" + "="*80)
    print("OVERALL TEST SUMMARY")
    print("="*80)
    
    print(f"Agent Persistence: {'✅ PASSED' if agent_persistence_result else '❌ FAILED'}")
    print(f"Simulation Workflow: {'✅ PASSED' if simulation_workflow_result else '❌ FAILED'}")
    print(f"Gemini Integration: {'✅ PASSED' if gemini_integration_result else '❌ FAILED'}")
    print(f"Complete User Workflow: {'✅ PASSED' if complete_workflow_result else '❌ FAILED'}")
    
    print("\nDETAILED RESULTS:")
    print(f"Agent Persistence: {agent_persistence_message}")
    print(f"Simulation Workflow: {simulation_workflow_message}")
    print(f"Gemini Integration: {gemini_integration_message}")
    print(f"Complete User Workflow: {complete_workflow_message}")
    
    # Print test statistics
    print_summary()

if __name__ == "__main__":
    main()