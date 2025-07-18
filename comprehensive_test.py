#!/usr/bin/env python3
"""
Comprehensive test script following the exact workflow specified in the review request
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

def test_exact_workflow():
    """Test the exact workflow specified in the review request"""
    print("🧪 TESTING EXACT WORKFLOW FROM REVIEW REQUEST")
    print("=" * 60)
    
    # Test 1: Set Scenario Functionality
    print("\n🎯 TEST 1: SET SCENARIO FUNCTIONALITY")
    print("-" * 40)
    
    # 1. Authenticate as guest user using POST /auth/test-login
    print("1. Authenticating as guest user...")
    response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return False
    
    auth_data = response.json()
    token = auth_data['access_token']
    user_id = auth_data['user']['id']
    print(f"✅ Authentication successful - User ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 2. Clear any existing state using POST /api/simulation/reset
    print("2. Clearing existing state...")
    response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Reset failed: {response.status_code} - {response.text}")
        return False
    print("✅ State reset successful")
    
    # 3. Set a scenario using POST /api/simulation/set-scenario
    print("3. Setting scenario...")
    scenario_data = {
        "scenario": "A team of scientists discovers a mysterious quantum signal",
        "scenario_name": "Quantum Signal Discovery"
    }
    response = requests.post(f"{API_URL}/simulation/set-scenario", 
                           headers=headers, json=scenario_data, timeout=10)
    if response.status_code != 200:
        print(f"❌ Set scenario failed: {response.status_code} - {response.text}")
        return False
    
    set_response = response.json()
    print(f"✅ Scenario set successfully: {set_response}")
    
    # 4. Verify the scenario is saved by calling GET /api/simulation/state
    print("4. Verifying scenario is saved...")
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get state failed: {response.status_code} - {response.text}")
        return False
    
    state_data = response.json()
    scenario = state_data.get('scenario', '')
    scenario_name = state_data.get('scenario_name', '')
    
    print(f"📋 Retrieved Scenario: {scenario}")
    print(f"🏷️  Retrieved Scenario Name: {scenario_name}")
    
    # 5. Check if the response includes the scenario and scenario_name fields
    if scenario == scenario_data['scenario'] and scenario_name == scenario_data['scenario_name']:
        print("✅ Scenario persistence verified - both scenario and scenario_name fields present and correct")
    else:
        print("❌ Scenario persistence failed - fields missing or incorrect")
        return False
    
    # Test 2: Agent Creation Functionality
    print("\n🎯 TEST 2: AGENT CREATION FUNCTIONALITY")
    print("-" * 40)
    
    # 1. Create an agent using POST /api/agents
    print("1. Creating first agent...")
    agent1_data = {
        "name": "Dr. Test Agent",
        "archetype": "scientist",
        "goal": "Test goal",
        "expertise": "Testing",
        "background": "Test background",
        "personality": {
            "extroversion": 5,
            "optimism": 6,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        }
    }
    
    response = requests.post(f"{API_URL}/agents", headers=headers, json=agent1_data, timeout=10)
    if response.status_code != 200:
        print(f"❌ Create agent 1 failed: {response.status_code} - {response.text}")
        return False
    
    agent1_response = response.json()
    agent1_id = agent1_response.get('id')
    print(f"✅ Agent 1 created successfully - ID: {agent1_id}")
    
    # 2. Verify the agent is created by calling GET /api/agents
    print("2. Verifying first agent appears in list...")
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get agents failed: {response.status_code} - {response.text}")
        return False
    
    agents_data = response.json()
    print(f"📊 Found {len(agents_data)} agents after creating first agent")
    
    # 3. Check if the agent appears in the response
    agent1_found = any(agent.get('id') == agent1_id for agent in agents_data)
    if agent1_found:
        print("✅ First agent appears in agent list")
    else:
        print("❌ First agent does NOT appear in agent list")
        return False
    
    # 4. Create another agent with different data
    print("3. Creating second agent...")
    agent2_data = {
        "name": "Prof. Research Agent",
        "archetype": "researcher",
        "goal": "Research quantum phenomena",
        "expertise": "Quantum Physics",
        "background": "PhD in Quantum Mechanics",
        "personality": {
            "extroversion": 4,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 8,
            "energy": 5
        }
    }
    
    response = requests.post(f"{API_URL}/agents", headers=headers, json=agent2_data, timeout=10)
    if response.status_code != 200:
        print(f"❌ Create agent 2 failed: {response.status_code} - {response.text}")
        return False
    
    agent2_response = response.json()
    agent2_id = agent2_response.get('id')
    print(f"✅ Agent 2 created successfully - ID: {agent2_id}")
    
    # 5. Verify both agents are returned
    print("4. Verifying both agents appear in list...")
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get agents failed: {response.status_code} - {response.text}")
        return False
    
    agents_data = response.json()
    print(f"📊 Found {len(agents_data)} agents after creating second agent")
    
    agent1_found = any(agent.get('id') == agent1_id for agent in agents_data)
    agent2_found = any(agent.get('id') == agent2_id for agent in agents_data)
    
    if agent1_found and agent2_found and len(agents_data) == 2:
        print("✅ Both agents appear in agent list")
        for i, agent in enumerate(agents_data, 1):
            print(f"   {i}. {agent.get('name')} ({agent.get('archetype')})")
    else:
        print(f"❌ Agent verification failed - Agent1 found: {agent1_found}, Agent2 found: {agent2_found}, Total count: {len(agents_data)}")
        return False
    
    # Test 3: Combined Functionality
    print("\n🎯 TEST 3: COMBINED FUNCTIONALITY")
    print("-" * 40)
    
    # 1. Set a scenario (from Test 1) - already done, verify it's still there
    print("1. Verifying scenario persists after agent creation...")
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get state failed: {response.status_code} - {response.text}")
        return False
    
    state_data = response.json()
    scenario = state_data.get('scenario', '')
    scenario_name = state_data.get('scenario_name', '')
    
    if scenario == scenario_data['scenario'] and scenario_name == scenario_data['scenario_name']:
        print("✅ Scenario still persists after agent creation")
    else:
        print("❌ Scenario lost after agent creation")
        return False
    
    # 2. Create 2 agents (from Test 2) - already done, verify they're still there
    print("2. Verifying agents persist...")
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get agents failed: {response.status_code} - {response.text}")
        return False
    
    agents_data = response.json()
    if len(agents_data) == 2:
        print("✅ Both agents still persist")
    else:
        print(f"❌ Agent persistence failed - Expected 2, found {len(agents_data)}")
        return False
    
    # 3. Call GET /api/simulation/state to verify scenario persists
    print("3. Final scenario persistence check...")
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get state failed: {response.status_code} - {response.text}")
        return False
    
    state_data = response.json()
    if state_data.get('scenario') and state_data.get('scenario_name'):
        print("✅ Scenario data persists in simulation state")
    else:
        print("❌ Scenario data missing from simulation state")
        return False
    
    # 4. Call GET /api/agents to verify agents persist
    print("4. Final agent persistence check...")
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get agents failed: {response.status_code} - {response.text}")
        return False
    
    agents_data = response.json()
    if len(agents_data) == 2:
        print("✅ Agent data persists")
    else:
        print(f"❌ Agent data persistence failed - Expected 2, found {len(agents_data)}")
        return False
    
    # 5. Start simulation using POST /api/simulation/start
    print("5. Starting simulation...")
    response = requests.post(f"{API_URL}/simulation/start", headers=headers, json={}, timeout=10)
    if response.status_code != 200:
        print(f"❌ Start simulation failed: {response.status_code} - {response.text}")
        return False
    
    start_response = response.json()
    print(f"✅ Simulation started successfully")
    
    # 6. Verify the state includes both scenario and agents
    print("6. Final verification - state includes both scenario and agents...")
    
    # Check simulation state
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get state failed: {response.status_code} - {response.text}")
        return False
    
    final_state = response.json()
    is_active = final_state.get('is_active', False)
    has_scenario = bool(final_state.get('scenario'))
    has_scenario_name = bool(final_state.get('scenario_name'))
    
    # Check agents still exist
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Get agents failed: {response.status_code} - {response.text}")
        return False
    
    final_agents = response.json()
    has_agents = len(final_agents) == 2
    
    print(f"   🎮 Simulation Active: {is_active}")
    print(f"   📋 Has Scenario: {has_scenario}")
    print(f"   🏷️  Has Scenario Name: {has_scenario_name}")
    print(f"   🤖 Has Agents: {has_agents} ({len(final_agents)} agents)")
    
    if is_active and has_scenario and has_scenario_name and has_agents:
        print("✅ Final verification successful - simulation includes both scenario and agents")
        return True
    else:
        print("❌ Final verification failed - missing scenario or agents in active simulation")
        return False

def main():
    """Main test execution"""
    print("🔬 COMPREHENSIVE BACKEND TESTING")
    print("Testing the exact workflow specified in the review request")
    print("=" * 60)
    
    success = test_exact_workflow()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ ALL TESTS PASSED")
        print("✅ Set Scenario Functionality: WORKING")
        print("✅ Agent Creation Functionality: WORKING") 
        print("✅ Combined Functionality: WORKING")
        print("✅ Data Persistence: WORKING")
        print("✅ Response Format: CORRECT")
        print("✅ State Consistency: MAINTAINED")
        print("✅ Authentication: WORKING")
        print("\n🎉 CONCLUSION: Both reported issues are NOT present in the backend!")
        print("🔍 The backend APIs are working correctly for both scenario setting and agent creation.")
        print("📝 If users are experiencing issues, they are likely in the frontend integration.")
    else:
        print("❌ SOME TESTS FAILED")
        print("🚨 Issues found in backend functionality")
    
    return success

if __name__ == "__main__":
    main()