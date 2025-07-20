#!/usr/bin/env python3
"""
Debug script to test the exact user issues:
1. Authentication failed when setting scenario
2. Agents not showing in agent list after adding from library
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_user_workflow():
    """Test the exact workflow the user is experiencing"""
    print("🧪 TESTING USER WORKFLOW - EXACT REPRODUCTION")
    print("="*60)
    
    # Step 1: Login as guest
    print("\n1. 🔐 Testing Guest Login")
    login_response = requests.post(f"{API_URL}/auth/test-login")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    auth_data = login_response.json()
    token = auth_data.get("access_token")
    user_id = auth_data.get("user", {}).get("id")
    
    print(f"✅ Login successful - User: {user_id}")
    print(f"🔑 Token: {token[:20]}...")
    
    # Step 2: Test scenario setting (user's exact issue)
    print("\n2. 📝 Testing Scenario Setting")
    scenario_data = {
        "scenario": "User reported test scenario",
        "scenario_name": "Debug Test Scenario"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    scenario_response = requests.post(
        f"{API_URL}/simulation/set-scenario", 
        json=scenario_data, 
        headers=headers
    )
    
    print(f"Status: {scenario_response.status_code}")
    print(f"Response: {scenario_response.text}")
    
    if scenario_response.status_code == 401:
        print("❌ CONFIRMED: User's authentication issue reproduced!")
        print("Token might be invalid or backend auth is broken")
    elif scenario_response.status_code == 200:
        print("✅ Scenario setting works - might be frontend issue")
    else:
        print(f"⚠️ Unexpected status: {scenario_response.status_code}")
    
    # Step 3: Test agent creation and listing
    print("\n3. 🤖 Testing Agent Adding Workflow")
    
    # First, check current agent count
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    print(f"Current agents status: {agents_response.status_code}")
    
    if agents_response.status_code == 200:
        current_agents = agents_response.json()
        print(f"Current agent count: {len(current_agents)}")
        for agent in current_agents:
            print(f"  - {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'None')})")
    else:
        print(f"❌ Cannot get agents list: {agents_response.status_code}")
        if agents_response.status_code == 401:
            print("❌ CONFIRMED: Agent listing has auth issues too!")
    
    # Try to add a new agent
    print("\n4. ➕ Testing Agent Creation")
    new_agent = {
        "name": "Debug Test Agent",
        "archetype": "scientist",
        "personality": {"extroversion": 5, "optimism": 7, "curiosity": 9, "cooperativeness": 6, "energy": 5},
        "goal": "Debug the user's agent adding issue",
        "background": "Created specifically to debug user reported issues",
        "expertise": "Testing and debugging"
    }
    
    create_response = requests.post(f"{API_URL}/agents", json=new_agent, headers=headers)
    print(f"Agent creation status: {create_response.status_code}")
    
    if create_response.status_code == 401:
        print("❌ CONFIRMED: Agent creation has auth issues!")
    elif create_response.status_code == 200:
        created_agent = create_response.json()
        print(f"✅ Agent created: {created_agent.get('name')} (ID: {created_agent.get('id')})")
        
        # Check if agent appears in list
        time.sleep(1)  # Give it a moment
        agents_check = requests.get(f"{API_URL}/agents", headers=headers)
        if agents_check.status_code == 200:
            updated_agents = agents_check.json()
            print(f"Updated agent count: {len(updated_agents)}")
            
            found_new_agent = any(agent.get('id') == created_agent.get('id') for agent in updated_agents)
            if found_new_agent:
                print("✅ New agent appears in list correctly")
            else:
                print("❌ CONFIRMED: New agent NOT in list - backend issue!")
        else:
            print("❌ Cannot re-check agents list")
    else:
        print(f"⚠️ Unexpected agent creation status: {create_response.status_code}")
    
    # Step 5: Test simulation state 
    print("\n5. 🎮 Testing Simulation State")
    sim_state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    print(f"Simulation state status: {sim_state_response.status_code}")
    
    if sim_state_response.status_code == 401:
        print("❌ CONFIRMED: Simulation state has auth issues!")
    elif sim_state_response.status_code == 200:
        state_data = sim_state_response.json()
        print(f"✅ Simulation state accessible")
        print(f"Scenario: {state_data.get('scenario', 'None')}")
        print(f"Scenario Name: {state_data.get('scenario_name', 'None')}")
    
    print("\n" + "="*60)
    print("🔍 DEBUGGING SUMMARY:")
    print("If you see 401 errors above, the issue is backend authentication")
    print("If you see 200s but frontend doesn't work, the issue is frontend state management")
    print("="*60)

if __name__ == "__main__":
    test_user_workflow()