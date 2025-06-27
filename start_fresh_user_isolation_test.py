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

def login_with_test_endpoint():
    """Login with test endpoint (creates a guest user)"""
    print("Logging in with test endpoint...")
    
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code != 200:
        print(f"❌ Test login failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return None, None
    
    data = response.json()
    token = data.get("access_token")
    user_id = data.get("user", {}).get("id")
    
    print(f"✅ Test login successful. User ID: {user_id}")
    return token, user_id

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

def test_user_isolation():
    """Test that the Start Fresh functionality respects user isolation"""
    print("\n" + "="*80)
    print("TESTING USER ISOLATION WITH START FRESH")
    print("="*80)
    
    # Step 1: Login as admin user
    admin_token = login()
    if not admin_token:
        print("❌ Test failed: Could not login as admin user")
        return False
    
    # Step 2: Login as guest user using test endpoint
    guest_token, guest_user_id = login_with_test_endpoint()
    if not guest_token:
        print("❌ Test failed: Could not login as guest user")
        return False
    
    # Step 3: Create agents and conversations for admin user
    print("\n" + "="*80)
    print("SETTING UP ADMIN USER")
    print("="*80)
    
    # Check if admin has enough agents
    admin_agents = get_agents(admin_token)
    if len(admin_agents) < 2:
        print(f"Creating agents for admin user...")
        create_agent(admin_token, "Admin Agent 1")
        create_agent(admin_token, "Admin Agent 2")
        admin_agents = get_agents(admin_token)
        if len(admin_agents) < 2:
            print("❌ Test failed: Could not create enough agents for admin user")
            return False
    
    # Start simulation and generate conversation for admin
    if not start_simulation(admin_token):
        print("❌ Test failed: Could not start simulation for admin user")
        return False
    
    if not generate_conversation(admin_token):
        print("❌ Test failed: Could not generate conversation for admin user")
        return False
    
    admin_conversations = get_conversations(admin_token)
    if len(admin_conversations) == 0:
        print("❌ Test failed: No conversations were generated for admin user")
        return False
    
    print(f"✅ Admin user has {len(admin_conversations)} conversations")
    
    # Step 4: Create agents and conversations for guest user
    print("\n" + "="*80)
    print("SETTING UP GUEST USER")
    print("="*80)
    
    # Create agents for guest user
    print(f"Creating agents for guest user...")
    create_agent(guest_token, "Guest Agent 1")
    create_agent(guest_token, "Guest Agent 2")
    guest_agents = get_agents(guest_token)
    if len(guest_agents) < 2:
        print("❌ Test failed: Could not create enough agents for guest user")
        return False
    
    # Start simulation and generate conversation for guest
    if not start_simulation(guest_token):
        print("❌ Test failed: Could not start simulation for guest user")
        return False
    
    if not generate_conversation(guest_token):
        print("❌ Test failed: Could not generate conversation for guest user")
        return False
    
    guest_conversations = get_conversations(guest_token)
    if len(guest_conversations) == 0:
        print("❌ Test failed: No conversations were generated for guest user")
        return False
    
    print(f"✅ Guest user has {len(guest_conversations)} conversations")
    
    # Step 5: Execute Start Fresh for guest user only
    print("\n" + "="*80)
    print("EXECUTING START FRESH FOR GUEST USER ONLY")
    print("="*80)
    
    if not start_simulation(guest_token):
        print("❌ Test failed: Could not start simulation for guest user in Start Fresh sequence")
        return False
    
    if not pause_simulation(guest_token):
        print("❌ Test failed: Could not pause simulation for guest user in Start Fresh sequence")
        return False
    
    # Step 6: Verify guest user's conversations are cleared
    guest_after_conversations = get_conversations(guest_token)
    
    if len(guest_after_conversations) > 0:
        print(f"❌ Test failed: Found {len(guest_after_conversations)} conversations for guest user after Start Fresh, expected 0")
        return False
    
    print("✅ Guest user's conversations are cleared after Start Fresh")
    
    # Step 7: Verify admin user's conversations are still there
    admin_after_conversations = get_conversations(admin_token)
    
    if len(admin_after_conversations) == 0:
        print("❌ Test failed: Admin user's conversations were cleared when they shouldn't have been")
        return False
    
    if len(admin_after_conversations) != len(admin_conversations):
        print(f"❌ Test failed: Admin user had {len(admin_conversations)} conversations before, but has {len(admin_after_conversations)} after")
        return False
    
    print(f"✅ Admin user still has {len(admin_after_conversations)} conversations (unchanged)")
    
    # Test passed
    print("\n" + "="*80)
    print("✅ USER ISOLATION TEST PASSED")
    print("✅ Start Fresh only affects the current user's conversations")
    print("✅ Other users' conversations remain unchanged")
    print("="*80)
    
    return True

if __name__ == "__main__":
    test_user_isolation()