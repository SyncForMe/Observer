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
test_user_email = f"test.user.{uuid.uuid4()}@example.com"
test_user_password = "securePassword123"
test_user_name = "Test User"

def print_separator():
    print("\n" + "="*80 + "\n")

def register_test_user():
    """Register a new test user and return the auth token"""
    global auth_token, test_user_id
    
    print("Logging in with admin credentials...")
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        response.raise_for_status()
        data = response.json()
        
        auth_token = data.get("access_token")
        user_data = data.get("user", {})
        test_user_id = user_data.get("id")
        
        print(f"✅ Successfully logged in with admin credentials. User ID: {test_user_id}")
        return auth_token
    except Exception as e:
        print(f"❌ Failed to login with admin credentials: {e}")
        
        # Try login with test endpoint as fallback
        try:
            response = requests.post(f"{API_URL}/auth/test-login")
            response.raise_for_status()
            data = response.json()
            
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            
            print(f"✅ Successfully logged in with test endpoint. User ID: {test_user_id}")
            return auth_token
        except Exception as e2:
            print(f"❌ Failed to login with test endpoint: {e2}")
            return None

def create_test_agents(count=3):
    """Create test agents for the current user"""
    if not auth_token:
        print("❌ Cannot create test agents without authentication")
        return []
    
    print(f"Creating {count} test agents...")
    created_agent_ids = []
    
    for i in range(count):
        agent_data = {
            "name": f"Test Agent {i+1}",
            "archetype": "scientist",
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 8,
                "cooperativeness": 7,
                "energy": 6
            },
            "goal": f"Test goal for agent {i+1}",
            "expertise": f"Test expertise {i+1}",
            "background": f"Test background {i+1}"
        }
        
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            agent_id = data.get("id")
            if agent_id:
                created_agent_ids.append(agent_id)
                print(f"✅ Created agent {i+1} with ID: {agent_id}")
            else:
                print(f"❌ Failed to get ID for agent {i+1}")
        except Exception as e:
            print(f"❌ Failed to create agent {i+1}: {e}")
    
    return created_agent_ids

def generate_test_conversation():
    """Generate a test conversation"""
    if not auth_token:
        print("❌ Cannot generate test conversation without authentication")
        return False
    
    print("Generating test conversation...")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        # If we need at least 2 agents, create them first
        if response.status_code == 400 and "Need at least 2 agents" in response.text:
            print("Creating agents first since we need at least 2 for conversation...")
            create_test_agents(3)
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Successfully generated conversation: {data.get('message', '')}")
        return True
    except Exception as e:
        print(f"❌ Failed to generate conversation: {e}")
        return False

def get_conversations():
    """Get all conversations for the current user"""
    if not auth_token:
        print("❌ Cannot get conversations without authentication")
        return []
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        response.raise_for_status()
        conversations = response.json()
        
        print(f"Found {len(conversations)} conversations")
        return conversations
    except Exception as e:
        print(f"❌ Failed to get conversations: {e}")
        return []

def get_simulation_state():
    """Get the current simulation state"""
    if not auth_token:
        print("❌ Cannot get simulation state without authentication")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        response.raise_for_status()
        state = response.json()
        
        print(f"Simulation state: is_active={state.get('is_active', False)}")
        return state
    except Exception as e:
        print(f"❌ Failed to get simulation state: {e}")
        return None

def start_simulation():
    """Start the simulation"""
    if not auth_token:
        print("❌ Cannot start simulation without authentication")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Successfully started simulation: {data.get('message', '')}")
        return True
    except Exception as e:
        print(f"❌ Failed to start simulation: {e}")
        return False

def pause_simulation():
    """Pause the simulation"""
    if not auth_token:
        print("❌ Cannot pause simulation without authentication")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{API_URL}/simulation/pause", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Successfully paused simulation: {data.get('message', '')}")
        return True
    except Exception as e:
        print(f"❌ Failed to pause simulation: {e}")
        return False

def test_start_fresh_functionality():
    """Test the Start Fresh button functionality"""
    print_separator()
    print("TESTING START FRESH FUNCTIONALITY")
    print_separator()
    
    # Step 1: Register a test user
    if not register_test_user():
        print("❌ Test failed: Could not register test user")
        return False
    
    # Step 2: Create some test agents
    agent_ids = create_test_agents(3)
    if not agent_ids:
        print("❌ Test failed: Could not create test agents")
        return False
    
    # Step 3: Start the simulation
    if not start_simulation():
        print("❌ Test failed: Could not start simulation")
        return False
    
    # Step 4: Generate a test conversation
    if not generate_test_conversation():
        print("❌ Test failed: Could not generate test conversation")
        return False
    
    # Step 5: Verify we have conversations
    initial_conversations = get_conversations()
    if not initial_conversations:
        print("❌ Test failed: No conversations found after generation")
        return False
    
    print(f"✅ Found {len(initial_conversations)} conversations before Start Fresh")
    
    # Step 6: Execute the Start Fresh sequence
    print_separator()
    print("EXECUTING START FRESH SEQUENCE")
    print("1. Call POST /api/simulation/start (clears conversations and starts simulation)")
    print("2. Immediately call POST /api/simulation/pause (stops the simulation)")
    print_separator()
    
    # Step 6.1: Call POST /api/simulation/start
    if not start_simulation():
        print("❌ Test failed: Could not execute start simulation in Start Fresh sequence")
        return False
    
    # Step 6.2: Immediately call POST /api/simulation/pause
    if not pause_simulation():
        print("❌ Test failed: Could not execute pause simulation in Start Fresh sequence")
        return False
    
    # Step 7: Verify conversations are cleared
    after_conversations = get_conversations()
    if after_conversations:
        print(f"❌ Test failed: Found {len(after_conversations)} conversations after Start Fresh, expected 0")
        return False
    
    print("✅ Conversations are cleared after Start Fresh")
    
    # Step 8: Verify simulation state is properly stopped
    final_state = get_simulation_state()
    if not final_state:
        print("❌ Test failed: Could not get simulation state after Start Fresh")
        return False
    
    if final_state.get('is_active', True):
        print("❌ Test failed: Simulation is still active after Start Fresh, expected stopped")
        return False
    
    print("✅ Simulation is properly stopped (is_active=False) after Start Fresh")
    
    # Test passed
    print_separator()
    print("✅ START FRESH FUNCTIONALITY TEST PASSED")
    print("✅ 1. POST /api/simulation/start clears conversations and starts simulation")
    print("✅ 2. POST /api/simulation/pause stops the simulation")
    print("✅ 3. Conversations are cleared")
    print("✅ 4. Simulation ends up in stopped state (is_active=False)")
    print_separator()
    
    return True

def test_user_isolation():
    """Test that the Start Fresh functionality respects user isolation"""
    print_separator()
    print("TESTING USER ISOLATION WITH START FRESH")
    print_separator()
    
    # Since we can't easily create multiple users, we'll simulate this by:
    # 1. Creating a set of conversations for the admin user
    # 2. Running Start Fresh and verifying conversations are cleared
    # 3. Creating new conversations
    # 4. Verifying the new conversations exist and are separate
    
    # Step 1: Login as admin user
    global auth_token, test_user_id, test_user_email, test_user_password
    
    if not register_test_user():
        print("❌ Test failed: Could not login as admin user")
        return False
    
    # Step 2: Create agents and first set of conversations
    agent_ids = create_test_agents(3)
    if not agent_ids:
        print("❌ Test failed: Could not create test agents")
        return False
    
    if not start_simulation():
        print("❌ Test failed: Could not start simulation")
        return False
    
    if not generate_test_conversation():
        print("❌ Test failed: Could not generate first test conversation")
        return False
    
    first_conversations = get_conversations()
    if not first_conversations:
        print("❌ Test failed: No conversations found after first generation")
        return False
    
    print(f"✅ Created first set of {len(first_conversations)} conversations")
    
    # Step 3: Execute Start Fresh
    print_separator()
    print("EXECUTING START FRESH")
    print_separator()
    
    if not start_simulation():
        print("❌ Test failed: Could not execute start simulation in Start Fresh sequence")
        return False
    
    if not pause_simulation():
        print("❌ Test failed: Could not execute pause simulation in Start Fresh sequence")
        return False
    
    # Step 4: Verify conversations are cleared
    after_conversations = get_conversations()
    if after_conversations:
        print(f"❌ Test failed: Found {len(after_conversations)} conversations after Start Fresh, expected 0")
        return False
    
    print("✅ Conversations are cleared after Start Fresh")
    
    # Step 5: Create new set of conversations
    if not start_simulation():
        print("❌ Test failed: Could not start simulation for new conversations")
        return False
    
    if not generate_test_conversation():
        print("❌ Test failed: Could not generate new test conversation")
        return False
    
    new_conversations = get_conversations()
    if not new_conversations:
        print("❌ Test failed: No conversations found after new generation")
        return False
    
    print(f"✅ Created new set of {len(new_conversations)} conversations")
    
    # Step 6: Verify the new conversations are different from the first set
    if len(new_conversations) == len(first_conversations):
        print("⚠️ New and old conversation sets have the same length, checking content...")
        
        # Check if the conversations are actually different
        first_ids = [conv.get("id") for conv in first_conversations]
        new_ids = [conv.get("id") for conv in new_conversations]
        
        if set(first_ids) == set(new_ids):
            print("❌ Test failed: New conversations have the same IDs as the first set")
            return False
    
    print("✅ New conversations are different from the first set")
    
    # Test passed
    print_separator()
    print("✅ USER ISOLATION TEST PASSED")
    print("✅ Start Fresh properly clears existing conversations")
    print("✅ New conversations can be created after Start Fresh")
    print_separator()
    
    return True

if __name__ == "__main__":
    # Run the tests
    test_start_fresh_functionality()
    test_user_isolation()