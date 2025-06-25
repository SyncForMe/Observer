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

# Global variables
auth_token = None
test_user_id = None
created_agent_ids = []

def login():
    """Login to get auth token"""
    global auth_token, test_user_id
    
    # Try using the email/password login with admin credentials
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    url = f"{API_URL}/auth/login"
    print(f"Logging in with admin credentials: {url}")
    
    try:
        response = requests.post(url, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            auth_token = response_data.get("access_token")
            user_data = response_data.get("user", {})
            test_user_id = user_data.get("id")
            print(f"Login successful. User ID: {test_user_id}")
            print(f"JWT Token: {auth_token}")
            return True
        else:
            print(f"Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def create_agent_with_user_id():
    """Create a test agent with user_id explicitly set"""
    global auth_token, test_user_id, created_agent_ids
    
    if not auth_token or not test_user_id:
        print("Cannot create agent without authentication")
        return False
    
    agent_data = {
        "name": f"Test Agent with User ID {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 5,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": "Test goal for agent with user ID",
        "expertise": "Test expertise with user ID",
        "background": "Test background with user ID",
        "user_id": test_user_id  # Explicitly set user_id
    }
    
    url = f"{API_URL}/agents"
    print(f"Creating agent with user_id: {url}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            agent_id = response_data.get("id")
            print(f"Created agent with ID: {agent_id}")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            created_agent_ids.append(agent_id)
            return agent_id
        else:
            print(f"Failed to create agent: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None

def get_agents():
    """Get all agents"""
    global auth_token
    
    if not auth_token:
        print("Cannot get agents without authentication")
        return None
    
    url = f"{API_URL}/agents"
    print(f"Getting agents: {url}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data)} agents")
            return response_data
        else:
            print(f"Failed to get agents: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting agents: {e}")
        return None

def test_bulk_delete_with_user_id():
    """Test bulk delete with agents that have user_id set"""
    global auth_token, created_agent_ids
    
    if not auth_token:
        print("Cannot test bulk delete without authentication")
        return False
    
    # Create multiple agents with user_id
    print("\nCreating multiple agents with user_id for bulk delete testing...")
    agent_ids = []
    for i in range(3):
        agent_id = create_agent_with_user_id()
        if agent_id:
            agent_ids.append(agent_id)
    
    if not agent_ids:
        print("Failed to create any agents with user_id")
        return False
    
    print(f"Created {len(agent_ids)} agents with user_id: {agent_ids}")
    
    # Test DELETE /api/agents/bulk endpoint
    url = f"{API_URL}/agents/bulk"
    print(f"\nTesting DELETE /api/agents/bulk with user_id: {url}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.delete(url, json=agent_ids, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            deleted_count = response_data.get("deleted_count", 0)
            print(f"Successfully deleted {deleted_count} agents")
            return True
        else:
            print(f"Failed to delete agents: {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting agents: {e}")
        return False

def test_bulk_delete_post_with_user_id():
    """Test POST /api/agents/bulk-delete with agents that have user_id set"""
    global auth_token, created_agent_ids
    
    if not auth_token:
        print("Cannot test bulk delete without authentication")
        return False
    
    # Create multiple agents with user_id
    print("\nCreating multiple agents with user_id for bulk delete testing...")
    agent_ids = []
    for i in range(3):
        agent_id = create_agent_with_user_id()
        if agent_id:
            agent_ids.append(agent_id)
    
    if not agent_ids:
        print("Failed to create any agents with user_id")
        return False
    
    print(f"Created {len(agent_ids)} agents with user_id: {agent_ids}")
    
    # Test POST /api/agents/bulk-delete endpoint
    url = f"{API_URL}/agents/bulk-delete"
    print(f"\nTesting POST /api/agents/bulk-delete with user_id: {url}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    data = {"agent_ids": agent_ids}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            deleted_count = response_data.get("deleted_count", 0)
            print(f"Successfully deleted {deleted_count} agents")
            return True
        else:
            print(f"Failed to delete agents: {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting agents: {e}")
        return False

def test_direct_array_format():
    """Test POST /api/agents/bulk-delete with direct array format"""
    global auth_token, created_agent_ids
    
    if not auth_token:
        print("Cannot test bulk delete without authentication")
        return False
    
    # Create multiple agents with user_id
    print("\nCreating multiple agents with user_id for direct array format testing...")
    agent_ids = []
    for i in range(3):
        agent_id = create_agent_with_user_id()
        if agent_id:
            agent_ids.append(agent_id)
    
    if not agent_ids:
        print("Failed to create any agents with user_id")
        return False
    
    print(f"Created {len(agent_ids)} agents with user_id: {agent_ids}")
    
    # Test POST /api/agents/bulk-delete endpoint with direct array format
    url = f"{API_URL}/agents/bulk-delete"
    print(f"\nTesting POST /api/agents/bulk-delete with direct array format: {url}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(url, json=agent_ids, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            deleted_count = response_data.get("deleted_count", 0)
            print(f"Successfully deleted {deleted_count} agents")
            return True
        else:
            print(f"Failed to delete agents: {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting agents: {e}")
        return False

def test_clear_all():
    """Test clear all functionality"""
    global auth_token, test_user_id
    
    if not auth_token or not test_user_id:
        print("Cannot test clear all without authentication")
        return False
    
    # Create multiple agents with user_id
    print("\nCreating multiple agents with user_id for clear all testing...")
    for i in range(5):
        create_agent_with_user_id()
    
    # Get all agents
    agents = get_agents()
    if not agents:
        print("Failed to get agents")
        return False
    
    # Filter agents that belong to the current user
    user_agents = [agent for agent in agents if agent.get("user_id") == test_user_id]
    print(f"Found {len(user_agents)} agents belonging to the current user")
    
    if not user_agents:
        print("No agents found belonging to the current user")
        return False
    
    # Get agent IDs
    agent_ids = [agent.get("id") for agent in user_agents]
    
    # Test DELETE /api/agents/bulk endpoint
    url = f"{API_URL}/agents/bulk"
    print(f"\nTesting clear all with DELETE /api/agents/bulk: {url}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.delete(url, json=agent_ids, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            deleted_count = response_data.get("deleted_count", 0)
            print(f"Successfully deleted {deleted_count} agents")
            
            # Verify all agents are deleted
            agents_after = get_agents()
            if agents_after:
                user_agents_after = [agent for agent in agents_after if agent.get("user_id") == test_user_id]
                if not user_agents_after:
                    print("All user agents were successfully deleted")
                    return True
                else:
                    print(f"{len(user_agents_after)} user agents still exist after clear all")
                    return False
            else:
                print("Failed to get agents after clear all")
                return False
        else:
            print(f"Failed to delete agents: {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting agents: {e}")
        return False

if __name__ == "__main__":
    print("Starting agent bulk delete with user_id tests...")
    
    # Login first to get auth token
    if login():
        # Test bulk delete with user_id
        test_bulk_delete_with_user_id()
        
        # Test bulk delete post with user_id
        test_bulk_delete_post_with_user_id()
        
        # Test direct array format
        test_direct_array_format()
        
        # Test clear all
        test_clear_all()
    else:
        print("Login failed. Cannot proceed with tests.")