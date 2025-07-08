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

def run_request(method, endpoint, data=None, headers=None, params=None):
    """Run a request against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nRequest: {method} {url}")
    
    if headers:
        print(f"Headers: {headers}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
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
            return None
        
        print(f"Status Code: {response.status_code}")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            response_data = {"text": response.text}
            print(f"Response: {response.text}")
        
        return {
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers)
        }
    
    except Exception as e:
        print(f"Error during request: {e}")
        return None

def create_user():
    """Create a new user account"""
    email = f"test.user.{uuid.uuid4()}@example.com"
    password = "securePassword123"
    name = f"Test User {uuid.uuid4().hex[:8]}"
    
    register_data = {
        "email": email,
        "password": password,
        "name": name
    }
    
    response = run_request("POST", "/auth/register", data=register_data)
    
    if response and response["status_code"] == 200:
        user_data = response["data"].get("user", {})
        token = response["data"].get("access_token")
        user_id = user_data.get("id")
        
        print(f"Created user: {name} ({user_id})")
        
        return {
            "id": user_id,
            "email": email,
            "name": name,
            "token": token
        }
    else:
        print("Failed to create user")
        return None

def create_agent(user_token, is_favorite=False):
    """Create a new agent for the user"""
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "goal": "Test goal",
        "background": "Test background",
        "expertise": "Test expertise",
        "avatar_prompt": "Professional scientist",
        "avatar_url": "https://example.com/avatar.png",
        "is_favorite": is_favorite
    }
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    response = run_request("POST", "/saved-agents", data=agent_data, headers=headers)
    
    if response and response["status_code"] == 200:
        agent_id = response["data"].get("id")
        print(f"Created agent: {agent_data['name']} ({agent_id})")
        
        return {
            "id": agent_id,
            "name": agent_data["name"],
            "is_favorite": response["data"].get("is_favorite", False)
        }
    else:
        print("Failed to create agent")
        return None

def get_user_agents(user_token):
    """Get all agents for the user"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    response = run_request("GET", "/saved-agents", headers=headers)
    
    if response and response["status_code"] == 200:
        agents = response["data"]
        print(f"Found {len(agents)} agents")
        return agents
    else:
        print("Failed to get agents")
        return []

def toggle_agent_favorite(user_token, agent_id):
    """Toggle favorite status of an agent"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    response = run_request("PUT", f"/saved-agents/{agent_id}/favorite", headers=headers)
    
    if response:
        return response
    else:
        print("Failed to toggle favorite")
        return None

def test_favorites_isolation():
    """Test user data isolation for agent favorites"""
    print("\n=== TESTING USER DATA ISOLATION FOR AGENT FAVORITES ===\n")
    
    # Create two users
    print("Creating two users...")
    user1 = create_user()
    user2 = create_user()
    
    if not user1 or not user2:
        print("Failed to create users")
        return
    
    print(f"\nUser 1: {user1['name']} ({user1['id']})")
    print(f"User 2: {user2['name']} ({user2['id']})")
    
    # Create an agent for user 1
    print("\nCreating agent for User 1...")
    agent1 = create_agent(user1["token"], is_favorite=True)
    
    if not agent1:
        print("Failed to create agent for User 1")
        return
    
    # Create an agent for user 2
    print("\nCreating agent for User 2...")
    agent2 = create_agent(user2["token"], is_favorite=False)
    
    if not agent2:
        print("Failed to create agent for User 2")
        return
    
    # Verify each user can see only their own agents
    print("\nVerifying User 1 can see only their own agents...")
    user1_agents = get_user_agents(user1["token"])
    
    user1_can_see_own_agent = any(a.get("id") == agent1["id"] for a in user1_agents)
    user1_can_see_other_agent = any(a.get("id") == agent2["id"] for a in user1_agents)
    
    print(f"User 1 can see own agent: {user1_can_see_own_agent}")
    print(f"User 1 can see User 2's agent: {user1_can_see_other_agent}")
    
    print("\nVerifying User 2 can see only their own agents...")
    user2_agents = get_user_agents(user2["token"])
    
    user2_can_see_own_agent = any(a.get("id") == agent2["id"] for a in user2_agents)
    user2_can_see_other_agent = any(a.get("id") == agent1["id"] for a in user2_agents)
    
    print(f"User 2 can see own agent: {user2_can_see_own_agent}")
    print(f"User 2 can see User 1's agent: {user2_can_see_other_agent}")
    
    # Test if User 2 can toggle User 1's agent favorite status
    print("\nTesting if User 2 can toggle User 1's agent favorite status...")
    toggle_response = toggle_agent_favorite(user2["token"], agent1["id"])
    
    if toggle_response:
        status_code = toggle_response["status_code"]
        
        if status_code == 200:
            print("❌ SECURITY ISSUE: User 2 was able to toggle User 1's agent favorite status!")
            
            # Check if the agent was actually modified
            user1_agents_after = get_user_agents(user1["token"])
            agent1_after = next((a for a in user1_agents_after if a.get("id") == agent1["id"]), None)
            
            if agent1_after:
                is_favorite_changed = agent1_after.get("is_favorite") != agent1["is_favorite"]
                print(f"Agent favorite status was actually changed: {is_favorite_changed}")
                print(f"Original is_favorite: {agent1['is_favorite']}")
                print(f"New is_favorite: {agent1_after.get('is_favorite')}")
            else:
                print("Could not find agent after toggle")
        elif status_code == 404:
            print("✅ User 2 correctly received 404 when trying to toggle User 1's agent")
        elif status_code == 403:
            print("✅ User 2 correctly received 403 when trying to toggle User 1's agent")
        elif status_code == 500:
            error_message = toggle_response["data"].get("detail", "")
            if "404: Saved agent not found" in error_message:
                print("✅ User 2 correctly received 500 with '404: Saved agent not found' when trying to toggle User 1's agent")
            else:
                print(f"❌ User 2 received 500 with unexpected error: {error_message}")
        else:
            print(f"❌ User 2 received unexpected status code: {status_code}")
    else:
        print("Failed to test toggle")
    
    # Test if User 1 can toggle User 2's agent favorite status
    print("\nTesting if User 1 can toggle User 2's agent favorite status...")
    toggle_response = toggle_agent_favorite(user1["token"], agent2["id"])
    
    if toggle_response:
        status_code = toggle_response["status_code"]
        
        if status_code == 200:
            print("❌ SECURITY ISSUE: User 1 was able to toggle User 2's agent favorite status!")
            
            # Check if the agent was actually modified
            user2_agents_after = get_user_agents(user2["token"])
            agent2_after = next((a for a in user2_agents_after if a.get("id") == agent2["id"]), None)
            
            if agent2_after:
                is_favorite_changed = agent2_after.get("is_favorite") != agent2["is_favorite"]
                print(f"Agent favorite status was actually changed: {is_favorite_changed}")
                print(f"Original is_favorite: {agent2['is_favorite']}")
                print(f"New is_favorite: {agent2_after.get('is_favorite')}")
            else:
                print("Could not find agent after toggle")
        elif status_code == 404:
            print("✅ User 1 correctly received 404 when trying to toggle User 2's agent")
        elif status_code == 403:
            print("✅ User 1 correctly received 403 when trying to toggle User 2's agent")
        elif status_code == 500:
            error_message = toggle_response["data"].get("detail", "")
            if "404: Saved agent not found" in error_message:
                print("✅ User 1 correctly received 500 with '404: Saved agent not found' when trying to toggle User 2's agent")
            else:
                print(f"❌ User 1 received 500 with unexpected error: {error_message}")
        else:
            print(f"❌ User 1 received unexpected status code: {status_code}")
    else:
        print("Failed to test toggle")
    
    print("\n=== USER DATA ISOLATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_favorites_isolation()