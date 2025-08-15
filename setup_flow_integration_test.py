#!/usr/bin/env python3
"""
SETUP FLOW INTEGRATION TESTING
Testing agent creation and scenario saving functionality for setup flow integration.

SPECIFIC TESTING OBJECTIVES:
1. Verify the agent creation endpoint `/api/agents` is working properly
2. Test the simulation state endpoint `/api/simulation/state` for scenario saving
3. Check if agents are being created and stored correctly in the database
4. Verify that the scenario is being saved properly

TESTING APPROACH:
1. Test POST /api/agents to create a test agent
2. Test GET /api/agents to retrieve agents
3. Test the simulation state endpoints for scenario management
4. Check the database to see if agents are being stored correctly

EXPECTED RESULTS:
- Agents should be created successfully via POST /api/agents
- Agents should be retrievable via GET /api/agents  
- Simulation state should accept and store scenario data
- The setup flow integration should work when these endpoints function properly
"""

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

def test_authentication_setup():
    """Set up authentication for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION SETUP")
    print("="*80)
    
    # Test email/password login with known test user
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Authentication failed")
        return False

def test_agent_creation_endpoint():
    """Test POST /api/agents endpoint for agent creation"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("2. AGENT CREATION ENDPOINT TESTING")
    print("="*80)
    
    print("🔍 Testing POST /api/agents endpoint for setup flow integration")
    
    # Test 1: Create a realistic agent for setup flow
    print("\n--- Test 1: Create Setup Flow Agent ---")
    
    agent_data = {
        "name": "Dr. Sarah Chen",
        "archetype": "scientist",
        "goal": "Lead quantum computing research and development",
        "expertise": "Quantum Physics and Computing",
        "background": "PhD in Quantum Physics from MIT, 10 years experience in quantum computing research",
        "personality": {
            "extroversion": 7,
            "optimism": 8,
            "curiosity": 9,
            "cooperativeness": 8,
            "energy": 7
        }
    }
    
    create_agent_test, create_agent_response = run_test(
        "Create Setup Flow Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True,
        measure_time=True,
        expected_keys=["id", "name", "archetype"]
    )
    
    if create_agent_test and create_agent_response:
        agent_id = create_agent_response.get("id")
        if agent_id:
            created_agent_ids.append(agent_id)
            print(f"✅ Created agent with ID: {agent_id}")
            print(f"✅ Agent creation successful for setup flow")
        else:
            print("❌ No agent ID returned")
            return False
    else:
        print("❌ Agent creation failed")
        return False
    
    # Test 2: Create multiple agents to test batch creation
    print("\n--- Test 2: Create Multiple Agents for Setup Flow ---")
    
    additional_agents = [
        {
            "name": "Marcus Rodriguez",
            "archetype": "leader",
            "goal": "Manage project timelines and team coordination",
            "expertise": "Project Management and Leadership",
            "background": "Senior Project Manager with 8 years experience in tech projects",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 9,
                "energy": 8
            }
        },
        {
            "name": "Dr. Emily Watson",
            "archetype": "researcher",
            "goal": "Conduct detailed analysis and research",
            "expertise": "Data Analysis and Research Methodology",
            "background": "Research Scientist with expertise in data analysis and statistical modeling",
            "personality": {
                "extroversion": 4,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 6
            }
        }
    ]
    
    for i, agent_data in enumerate(additional_agents, 2):
        create_test, create_response = run_test(
            f"Create Additional Agent {i} ({agent_data['name']})",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            measure_time=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            if agent_id:
                created_agent_ids.append(agent_id)
                print(f"✅ Created agent {agent_data['name']} with ID: {agent_id}")
            else:
                print(f"❌ No agent ID returned for {agent_data['name']}")
                return False
        else:
            print(f"❌ Failed to create agent {agent_data['name']}")
            return False
    
    print(f"✅ Successfully created {len(created_agent_ids)} agents for setup flow")
    return True

def test_agent_retrieval_endpoint():
    """Test GET /api/agents endpoint for agent retrieval"""
    print("\n" + "="*80)
    print("3. AGENT RETRIEVAL ENDPOINT TESTING")
    print("="*80)
    
    print("🔍 Testing GET /api/agents endpoint for setup flow integration")
    
    # Test 1: Get all agents
    print("\n--- Test 1: Retrieve All Agents ---")
    
    get_agents_test, get_agents_response = run_test(
        "Get All Agents",
        "/agents",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    if get_agents_test and get_agents_response:
        agent_count = len(get_agents_response)
        print(f"✅ Retrieved {agent_count} agents")
        
        # Verify we can see our created agents
        created_agent_names = []
        for agent in get_agents_response:
            if agent.get("id") in created_agent_ids:
                created_agent_names.append(agent.get("name"))
        
        print(f"✅ Found {len(created_agent_names)} of our created agents: {', '.join(created_agent_names)}")
        
        # Verify agent structure
        if get_agents_response:
            sample_agent = get_agents_response[0]
            required_fields = ["id", "name", "archetype", "goal", "expertise", "personality"]
            missing_fields = [field for field in required_fields if field not in sample_agent]
            if missing_fields:
                print(f"❌ Missing fields in agent: {missing_fields}")
                return False
            else:
                print("✅ Agent structure is correct")
        
        # Verify personality structure
        if get_agents_response and "personality" in get_agents_response[0]:
            personality = get_agents_response[0]["personality"]
            personality_fields = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
            missing_personality_fields = [field for field in personality_fields if field not in personality]
            if missing_personality_fields:
                print(f"❌ Missing personality fields: {missing_personality_fields}")
                return False
            else:
                print("✅ Personality structure is correct")
    else:
        print("❌ Failed to retrieve agents")
        return False
    
    # Test 2: Get specific agent by ID
    print("\n--- Test 2: Retrieve Specific Agent ---")
    
    if created_agent_ids:
        test_agent_id = created_agent_ids[0]
        get_agent_test, get_agent_response = run_test(
            f"Get Specific Agent {test_agent_id}",
            f"/agents/{test_agent_id}",
            method="GET",
            auth=True,
            measure_time=True,
            expected_keys=["id", "name", "archetype", "goal", "expertise", "personality"]
        )
        
        if get_agent_test and get_agent_response:
            retrieved_id = get_agent_response.get("id")
            if retrieved_id == test_agent_id:
                print(f"✅ Successfully retrieved specific agent: {get_agent_response.get('name')}")
            else:
                print(f"❌ Agent ID mismatch: expected {test_agent_id}, got {retrieved_id}")
                return False
        else:
            print("❌ Failed to retrieve specific agent")
            return False
    
    print("✅ Agent retrieval endpoints working correctly")
    return True

def test_simulation_state_scenario_management():
    """Test simulation state endpoints for scenario management"""
    print("\n" + "="*80)
    print("4. SIMULATION STATE SCENARIO MANAGEMENT TESTING")
    print("="*80)
    
    print("🔍 Testing simulation state endpoints for scenario saving and management")
    
    # Test 1: Get initial simulation state
    print("\n--- Test 1: Get Initial Simulation State ---")
    
    initial_state_test, initial_state_response = run_test(
        "Get Initial Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        measure_time=True,
        expected_keys=["current_day", "current_time_period", "scenario", "is_active"]
    )
    
    if initial_state_test and initial_state_response:
        print("✅ Simulation state endpoint accessible")
        initial_scenario = initial_state_response.get("scenario", "")
        initial_scenario_name = initial_state_response.get("scenario_name", "")
        print(f"Initial scenario: '{initial_scenario}'")
        print(f"Initial scenario name: '{initial_scenario_name}'")
    else:
        print("❌ Failed to get initial simulation state")
        return False
    
    # Test 2: Set a scenario for setup flow
    print("\n--- Test 2: Set Scenario for Setup Flow ---")
    
    scenario_data = {
        "scenario": "Advanced Quantum Computing Research Laboratory",
        "scenario_name": "Quantum Computing Research Project"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario for Setup Flow",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        measure_time=True,
        expected_keys=["message", "scenario"]
    )
    
    if set_scenario_test and set_scenario_response:
        returned_scenario = set_scenario_response.get("scenario")
        if returned_scenario == scenario_data["scenario"]:
            print("✅ Scenario set successfully")
        else:
            print(f"❌ Scenario mismatch: expected '{scenario_data['scenario']}', got '{returned_scenario}'")
            return False
    else:
        print("❌ Failed to set scenario")
        return False
    
    # Test 3: Verify scenario persistence in simulation state
    print("\n--- Test 3: Verify Scenario Persistence ---")
    
    verify_state_test, verify_state_response = run_test(
        "Verify Scenario in Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    if verify_state_test and verify_state_response:
        persisted_scenario = verify_state_response.get("scenario")
        persisted_scenario_name = verify_state_response.get("scenario_name")
        
        if persisted_scenario == scenario_data["scenario"]:
            print("✅ Scenario correctly persisted in simulation state")
        else:
            print(f"❌ Scenario not persisted: expected '{scenario_data['scenario']}', got '{persisted_scenario}'")
            return False
        
        if persisted_scenario_name == scenario_data["scenario_name"]:
            print("✅ Scenario name correctly persisted in simulation state")
        else:
            print(f"❌ Scenario name not persisted: expected '{scenario_data['scenario_name']}', got '{persisted_scenario_name}'")
            return False
    else:
        print("❌ Failed to verify scenario persistence")
        return False
    
    # Test 4: Test scenario switching
    print("\n--- Test 4: Test Scenario Switching ---")
    
    new_scenario_data = {
        "scenario": "AI Ethics and Safety Research Center",
        "scenario_name": "AI Safety Research Initiative"
    }
    
    switch_scenario_test, switch_scenario_response = run_test(
        "Switch to New Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=new_scenario_data,
        auth=True,
        measure_time=True,
        expected_keys=["message", "scenario"]
    )
    
    if switch_scenario_test and switch_scenario_response:
        print("✅ Scenario switching successful")
        
        # Verify the switch took effect
        verify_switch_test, verify_switch_response = run_test(
            "Verify Scenario Switch",
            "/simulation/state",
            method="GET",
            auth=True
        )
        
        if verify_switch_test and verify_switch_response:
            switched_scenario = verify_switch_response.get("scenario")
            if switched_scenario == new_scenario_data["scenario"]:
                print("✅ Scenario switch verified")
            else:
                print(f"❌ Scenario switch failed: expected '{new_scenario_data['scenario']}', got '{switched_scenario}'")
                return False
        else:
            print("❌ Failed to verify scenario switch")
            return False
    else:
        print("❌ Failed to switch scenario")
        return False
    
    print("✅ Simulation state scenario management working correctly")
    return True

def test_database_storage_verification():
    """Verify that agents and scenarios are being stored correctly in the database"""
    print("\n" + "="*80)
    print("5. DATABASE STORAGE VERIFICATION")
    print("="*80)
    
    print("🔍 Verifying database storage through API responses")
    
    # Test 1: Verify agent persistence across sessions
    print("\n--- Test 1: Verify Agent Persistence ---")
    
    # Get agents again to verify they persist
    persistence_test, persistence_response = run_test(
        "Verify Agent Persistence",
        "/agents",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    if persistence_test and persistence_response:
        persistent_agent_ids = [agent.get("id") for agent in persistence_response]
        
        # Check if our created agents are still there
        persistent_created_agents = [aid for aid in created_agent_ids if aid in persistent_agent_ids]
        
        if len(persistent_created_agents) == len(created_agent_ids):
            print(f"✅ All {len(created_agent_ids)} created agents persist in database")
        else:
            print(f"❌ Only {len(persistent_created_agents)} of {len(created_agent_ids)} agents persist")
            return False
        
        # Verify agent data integrity
        for agent in persistence_response:
            if agent.get("id") in created_agent_ids:
                required_fields = ["name", "archetype", "goal", "expertise", "personality", "user_id"]
                missing_fields = [field for field in required_fields if not agent.get(field)]
                if missing_fields:
                    print(f"❌ Agent {agent.get('name')} missing fields: {missing_fields}")
                    return False
        
        print("✅ Agent data integrity verified")
    else:
        print("❌ Failed to verify agent persistence")
        return False
    
    # Test 2: Verify scenario persistence
    print("\n--- Test 2: Verify Scenario Persistence ---")
    
    scenario_persistence_test, scenario_persistence_response = run_test(
        "Verify Scenario Persistence",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if scenario_persistence_test and scenario_persistence_response:
        current_scenario = scenario_persistence_response.get("scenario")
        current_scenario_name = scenario_persistence_response.get("scenario_name")
        
        if current_scenario and current_scenario_name:
            print(f"✅ Scenario persists: '{current_scenario}' - '{current_scenario_name}'")
        else:
            print("❌ Scenario not persisting properly")
            return False
        
        # Verify simulation state structure
        required_state_fields = ["current_day", "current_time_period", "is_active", "user_id"]
        missing_state_fields = [field for field in required_state_fields if field not in scenario_persistence_response]
        if missing_state_fields:
            print(f"❌ Simulation state missing fields: {missing_state_fields}")
            return False
        
        print("✅ Simulation state structure verified")
    else:
        print("❌ Failed to verify scenario persistence")
        return False
    
    # Test 3: Verify user isolation
    print("\n--- Test 3: Verify User Isolation ---")
    
    # Check that agents belong to the correct user
    user_isolation_test, user_isolation_response = run_test(
        "Verify User Isolation",
        "/agents",
        method="GET",
        auth=True
    )
    
    if user_isolation_test and user_isolation_response:
        for agent in user_isolation_response:
            agent_user_id = agent.get("user_id")
            if agent_user_id != test_user_id:
                print(f"❌ Agent {agent.get('name')} has wrong user_id: {agent_user_id} (expected {test_user_id})")
                return False
        
        print(f"✅ All agents correctly associated with user {test_user_id}")
    else:
        print("❌ Failed to verify user isolation")
        return False
    
    print("✅ Database storage verification successful")
    return True

def test_setup_flow_integration_readiness():
    """Test overall readiness for setup flow integration"""
    print("\n" + "="*80)
    print("6. SETUP FLOW INTEGRATION READINESS")
    print("="*80)
    
    print("🔍 Testing complete setup flow integration readiness")
    
    # Test 1: Simulate complete setup flow
    print("\n--- Test 1: Simulate Complete Setup Flow ---")
    
    # Step 1: Create agents (already done)
    print(f"✅ Step 1: Created {len(created_agent_ids)} agents")
    
    # Step 2: Set scenario (already done)
    print("✅ Step 2: Set scenario successfully")
    
    # Step 3: Start simulation
    start_simulation_test, start_simulation_response = run_test(
        "Start Simulation for Setup Flow",
        "/simulation/start",
        method="POST",
        auth=True,
        measure_time=True,
        expected_keys=["message", "state"]
    )
    
    if start_simulation_test and start_simulation_response:
        print("✅ Step 3: Simulation started successfully")
        
        # Verify simulation is active
        state = start_simulation_response.get("state", {})
        if state.get("is_active"):
            print("✅ Simulation is active")
        else:
            print("❌ Simulation not active after start")
            return False
    else:
        print("❌ Failed to start simulation")
        return False
    
    # Test 2: Verify complete system state
    print("\n--- Test 2: Verify Complete System State ---")
    
    final_state_test, final_state_response = run_test(
        "Get Final System State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if final_state_test and final_state_response:
        print("✅ System state accessible")
        
        # Check all required components
        has_scenario = bool(final_state_response.get("scenario"))
        has_scenario_name = bool(final_state_response.get("scenario_name"))
        is_active = final_state_response.get("is_active", False)
        
        if has_scenario and has_scenario_name and is_active:
            print("✅ All setup flow components ready:")
            print(f"   - Scenario: {final_state_response.get('scenario')}")
            print(f"   - Scenario Name: {final_state_response.get('scenario_name')}")
            print(f"   - Active: {is_active}")
            print(f"   - Agents: {len(created_agent_ids)} created")
        else:
            print("❌ Setup flow components not ready:")
            print(f"   - Has Scenario: {has_scenario}")
            print(f"   - Has Scenario Name: {has_scenario_name}")
            print(f"   - Is Active: {is_active}")
            return False
    else:
        print("❌ Failed to get final system state")
        return False
    
    # Test 3: Test conversation generation with setup
    print("\n--- Test 3: Test Conversation Generation with Setup ---")
    
    conversation_test, conversation_response = run_test(
        "Generate Conversation with Setup",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True,
        expected_keys=["message", "conversation"]
    )
    
    if conversation_test and conversation_response:
        conversation = conversation_response.get("conversation", {})
        messages = conversation.get("messages", [])
        
        if messages:
            print(f"✅ Generated conversation with {len(messages)} messages")
            
            # Verify messages are from our created agents
            message_agents = [msg.get("agent_name") for msg in messages]
            print(f"✅ Messages from agents: {', '.join(message_agents)}")
        else:
            print("❌ No messages generated")
            return False
    else:
        print("❌ Failed to generate conversation")
        return False
    
    print("✅ Setup flow integration is ready")
    return True

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    # Reset simulation
    reset_test, reset_response = run_test(
        "Reset Simulation",
        "/simulation/reset",
        method="POST",
        auth=True
    )
    if reset_test:
        print("✅ Reset simulation")
    else:
        print("❌ Failed to reset simulation")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution function"""
    print("SETUP FLOW INTEGRATION TESTING")
    print("Testing agent creation and scenario saving functionality")
    print("="*80)
    
    # Run all test suites
    test_suites = [
        ("Authentication Setup", test_authentication_setup),
        ("Agent Creation Endpoint", test_agent_creation_endpoint),
        ("Agent Retrieval Endpoint", test_agent_retrieval_endpoint),
        ("Simulation State Scenario Management", test_simulation_state_scenario_management),
        ("Database Storage Verification", test_database_storage_verification),
        ("Setup Flow Integration Readiness", test_setup_flow_integration_readiness),
    ]
    
    all_passed = True
    
    for suite_name, test_function in test_suites:
        print(f"\n{'='*80}")
        print(f"RUNNING TEST SUITE: {suite_name}")
        print(f"{'='*80}")
        
        try:
            result = test_function()
            if not result:
                all_passed = False
                print(f"❌ Test suite '{suite_name}' FAILED")
            else:
                print(f"✅ Test suite '{suite_name}' PASSED")
        except Exception as e:
            print(f"❌ Test suite '{suite_name}' ERROR: {e}")
            all_passed = False
    
    # Cleanup
    try:
        cleanup_test_data()
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    
    # Print final summary
    print_summary()
    
    # Final assessment
    print("\n" + "="*80)
    print("SETUP FLOW INTEGRATION TEST RESULTS")
    print("="*80)
    
    if all_passed:
        print("✅ ALL TESTS PASSED - Setup flow integration is ready")
        print("✅ Agent creation endpoint working properly")
        print("✅ Agent retrieval endpoint working properly")
        print("✅ Scenario saving and persistence working properly")
        print("✅ Database storage working correctly")
        print("✅ Complete setup flow integration functional")
    else:
        print("❌ SOME TESTS FAILED - Setup flow integration needs attention")
        print("❌ Check failed tests above for specific issues")
    
    print("="*80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)