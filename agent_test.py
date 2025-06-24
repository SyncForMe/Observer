#!/usr/bin/env python3
import requests
import json
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

# Test login to get auth token
def test_login():
    """Login with test endpoint to get auth token"""
    print("\n=== Testing Login ===")
    
    # Try the test login endpoint
    test_login_url = f"{API_URL}/auth/test-login"
    print(f"POST {test_login_url}")
    
    try:
        response = requests.post(test_login_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"Login successful. Token: {token[:10]}...")
            return token
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

# Test GET /api/agents
def test_get_agents(token=None):
    """Test the GET /api/agents endpoint"""
    print("\n=== Testing GET /api/agents ===")
    
    url = f"{API_URL}/agents"
    print(f"GET {url}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} agents")
            if data:
                print("\nSample agent structure:")
                sample_agent = data[0]
                for key, value in sample_agent.items():
                    if isinstance(value, dict):
                        print(f"- {key}: {type(value)}")
                    else:
                        print(f"- {key}: {value}")
            else:
                print("No agents found")
            return data
        else:
            print(f"Request failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        return None

# Test GET /api/saved-agents
def test_get_saved_agents(token=None):
    """Test the GET /api/saved-agents endpoint"""
    print("\n=== Testing GET /api/saved-agents ===")
    
    url = f"{API_URL}/saved-agents"
    print(f"GET {url}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} saved agents")
            if data:
                print("\nSample saved agent structure:")
                sample_agent = data[0]
                for key, value in sample_agent.items():
                    if isinstance(value, dict):
                        print(f"- {key}: {type(value)}")
                    else:
                        print(f"- {key}: {value}")
            else:
                print("No saved agents found")
            return data
        else:
            print(f"Request failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        return None

# Test POST /api/agents
def test_create_agent(token=None):
    """Test the POST /api/agents endpoint"""
    print("\n=== Testing POST /api/agents ===")
    
    url = f"{API_URL}/agents"
    print(f"POST {url}")
    
    # Create test agent data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "goal": "Test the agent creation endpoint",
        "expertise": "API Testing",
        "background": "Created for testing purposes",
        "memory_summary": "This agent was created to test the API",
        "avatar_prompt": "A robot scientist in a lab coat"
    }
    
    print(f"Request data: {json.dumps(agent_data, indent=2)}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent created successfully with ID: {data.get('id')}")
            print("\nCreated agent structure:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"- {key}: {type(value)}")
                else:
                    print(f"- {key}: {value}")
            return data
        else:
            print(f"Request failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        return None

# Test GET /api/archetypes
def test_get_archetypes(token=None):
    """Test the GET /api/archetypes endpoint"""
    print("\n=== Testing GET /api/archetypes ===")
    
    url = f"{API_URL}/archetypes"
    print(f"GET {url}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} archetypes")
            print("\nAvailable archetypes:")
            for archetype, details in data.items():
                print(f"- {archetype}: {details.get('name')} - {details.get('description')}")
            return data
        else:
            print(f"Request failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        return None

# Main function
# Test POST /api/saved-agents
def test_save_agent(token=None):
    """Test the POST /api/saved-agents endpoint"""
    print("\n=== Testing POST /api/saved-agents ===")
    
    url = f"{API_URL}/saved-agents"
    print(f"POST {url}")
    
    # Create test saved agent data
    agent_data = {
        "name": f"Saved Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "researcher",
        "goal": "Test the saved agent creation endpoint",
        "expertise": "API Testing",
        "background": "Created for testing saved agents",
        "avatar_prompt": "A researcher with a clipboard"
    }
    
    print(f"Request data: {json.dumps(agent_data, indent=2)}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Saved agent created successfully with ID: {data.get('id')}")
            print("\nCreated saved agent structure:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"- {key}: {type(value)}")
                else:
                    print(f"- {key}: {value}")
            return data
        else:
            print(f"Request failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        return None

def main():
    print("=== Agent Library API Testing ===")
    
    # Login to get auth token
    token = test_login()
    
    # Test GET /api/agents
    agents = test_get_agents(token)
    
    # Test GET /api/saved-agents
    saved_agents = test_get_saved_agents(token)
    
    # Test GET /api/archetypes
    archetypes = test_get_archetypes(token)
    
    # Test POST /api/agents
    created_agent = test_create_agent(token)
    
    # Test POST /api/saved-agents
    saved_agent = test_save_agent(token)
    
    # Test GET /api/saved-agents again to see if the saved agent appears
    if saved_agent:
        print("\n=== Testing GET /api/saved-agents (After Saving) ===")
        updated_saved_agents = test_get_saved_agents(token)
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"GET /api/agents: {'Success' if agents is not None else 'Failed'}")
    print(f"GET /api/saved-agents: {'Success' if saved_agents is not None else 'Failed'}")
    print(f"GET /api/archetypes: {'Success' if archetypes is not None else 'Failed'}")
    print(f"POST /api/agents: {'Success' if created_agent is not None else 'Failed'}")
    print(f"POST /api/saved-agents: {'Success' if saved_agent is not None else 'Failed'}")

if __name__ == "__main__":
    main()