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

# Admin credentials
ADMIN_EMAIL = "dino@cytonic.com"
ADMIN_PASSWORD = "Observerinho8"

def login():
    """Login with admin credentials"""
    print("Logging in with admin credentials...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    user_id = data.get("user", {}).get("id")
    
    print(f"✅ Login successful. User ID: {user_id}")
    return token

def get_agents(token):
    """Get all agents"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/agents", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get agents. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    
    agents = response.json()
    print(f"Found {len(agents)} agents")
    return agents

def create_agent(token, name="Test Agent"):
    """Create a test agent"""
    headers = {"Authorization": f"Bearer {token}"}
    agent_data = {
        "name": name,
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 5,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": "Test goal",
        "expertise": "Test expertise",
        "background": "Test background"
    }
    
    response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to create agent. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    agent_id = data.get("id")
    print(f"✅ Created agent with ID: {agent_id}")
    return agent_id

def get_conversations(token):
    """Get all conversations"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get conversations. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    
    conversations = response.json()
    print(f"Found {len(conversations)} conversations")
    return conversations

def generate_conversation(token):
    """Generate a conversation"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to generate conversation. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    print(f"✅ Generated conversation: {data.get('message', '')}")
    return True

def get_simulation_state(token):
    """Get the current simulation state"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get simulation state. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    state = response.json()
    print(f"Simulation state: is_active={state.get('is_active', False)}")
    return state

def start_simulation(token):
    """Start the simulation"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to start simulation. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    print(f"✅ Simulation started: {data.get('message', '')}")
    return True

def pause_simulation(token):
    """Pause the simulation"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/simulation/pause", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to pause simulation. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    print(f"✅ Simulation paused: {data.get('message', '')}")
    return True

def test_start_fresh_with_conversations():
    """Test the Start Fresh functionality with existing conversations"""
    print("\n" + "="*80)
    print("TESTING START FRESH FUNCTIONALITY WITH EXISTING CONVERSATIONS")
    print("="*80)
    
    # Step 1: Login
    token = login()
    if not token:
        print("❌ Test failed: Could not login")
        return False
    
    # Step 2: Check if we have enough agents for conversation generation
    agents = get_agents(token)
    if len(agents) < 2:
        print(f"Creating agents since we need at least 2 for conversation generation...")
        create_agent(token, "Test Agent 1")
        create_agent(token, "Test Agent 2")
        agents = get_agents(token)
        if len(agents) < 2:
            print("❌ Test failed: Could not create enough agents")
            return False
    
    # Step 3: Start simulation and generate conversations
    if not start_simulation(token):
        print("❌ Test failed: Could not start simulation")
        return False
    
    # Generate a conversation
    if not generate_conversation(token):
        print("❌ Test failed: Could not generate conversation")
        return False
    
    # Check if conversation was created
    initial_conversations = get_conversations(token)
    if len(initial_conversations) == 0:
        print("❌ Test failed: No conversations were generated")
        return False
    
    print(f"✅ Successfully generated {len(initial_conversations)} conversations")
    
    # Step 4: Execute Start Fresh sequence
    print("\n" + "="*80)
    print("EXECUTING START FRESH SEQUENCE")
    print("1. Call POST /api/simulation/start (clears conversations and starts simulation)")
    print("2. Immediately call POST /api/simulation/pause (stops the simulation)")
    print("="*80)
    
    # Step 4.1: Call POST /api/simulation/start
    if not start_simulation(token):
        print("❌ Test failed: Could not start simulation in Start Fresh sequence")
        return False
    
    # Step 4.2: Call POST /api/simulation/pause
    if not pause_simulation(token):
        print("❌ Test failed: Could not pause simulation in Start Fresh sequence")
        return False
    
    # Step 5: Verify conversations are cleared
    after_conversations = get_conversations(token)
    
    if len(after_conversations) > 0:
        print(f"❌ Test failed: Found {len(after_conversations)} conversations after Start Fresh, expected 0")
        return False
    
    print("✅ Conversations are cleared after Start Fresh")
    
    # Step 6: Verify simulation state is properly stopped
    final_state = get_simulation_state(token)
    
    if final_state is None:
        print("❌ Test failed: Could not get final simulation state")
        return False
    
    if final_state.get('is_active', True):
        print("❌ Test failed: Simulation is still active after Start Fresh, expected stopped")
        return False
    
    print("✅ Simulation is properly stopped (is_active=False) after Start Fresh")
    
    # Test passed
    print("\n" + "="*80)
    print("✅ START FRESH FUNCTIONALITY TEST PASSED")
    print("✅ 1. Started with conversations in the system")
    print("✅ 2. POST /api/simulation/start cleared conversations and started simulation")
    print("✅ 3. POST /api/simulation/pause stopped the simulation")
    print("✅ 4. Conversations were cleared")
    print("✅ 5. Simulation ended up in stopped state (is_active=False)")
    print("="*80)
    
    return True

if __name__ == "__main__":
    test_start_fresh_with_conversations()