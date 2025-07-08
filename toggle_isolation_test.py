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

def test_toggle_favorite_isolation():
    """Test user data isolation for agent favorites toggle"""
    print("\n=== TESTING USER DATA ISOLATION FOR AGENT FAVORITES TOGGLE ===\n")
    
    # Step 1: Create two users
    print("Step 1: Creating two users")
    
    # Create User 1
    user1_email = f"user1.{uuid.uuid4()}@example.com"
    user1_password = "securePassword123"
    user1_name = "Test User 1"
    
    user1_register_data = {
        "email": user1_email,
        "password": user1_password,
        "name": user1_name
    }
    
    user1_response = run_request("POST", "/auth/register", data=user1_register_data)
    
    if not user1_response or user1_response["status_code"] != 200:
        print("Failed to create User 1")
        return
    
    user1_token = user1_response["data"].get("access_token")
    user1_id = user1_response["data"].get("user", {}).get("id")
    
    print(f"Created User 1: {user1_name} ({user1_id})")
    
    # Create User 2
    user2_email = f"user2.{uuid.uuid4()}@example.com"
    user2_password = "securePassword456"
    user2_name = "Test User 2"
    
    user2_register_data = {
        "email": user2_email,
        "password": user2_password,
        "name": user2_name
    }
    
    user2_response = run_request("POST", "/auth/register", data=user2_register_data)
    
    if not user2_response or user2_response["status_code"] != 200:
        print("Failed to create User 2")
        return
    
    user2_token = user2_response["data"].get("access_token")
    user2_id = user2_response["data"].get("user", {}).get("id")
    
    print(f"Created User 2: {user2_name} ({user2_id})")
    
    # Step 2: Create an agent for User 1
    print("\nStep 2: Creating an agent for User 1")
    
    user1_agent_data = {
        "name": f"User1 Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "goal": "Test goal",
        "background": "Test background",
        "expertise": "Test expertise",
        "avatar_prompt": "Professional scientist",
        "avatar_url": "https://example.com/avatar.png",
        "is_favorite": True
    }
    
    user1_agent_response = run_request(
        "POST", 
        "/saved-agents", 
        data=user1_agent_data, 
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    if not user1_agent_response or user1_agent_response["status_code"] != 200:
        print("Failed to create agent for User 1")
        return
    
    user1_agent_id = user1_agent_response["data"].get("id")
    user1_agent_name = user1_agent_response["data"].get("name")
    
    print(f"Created agent for User 1: {user1_agent_name} ({user1_agent_id})")
    
    # Step 3: Create an agent for User 2
    print("\nStep 3: Creating an agent for User 2")
    
    user2_agent_data = {
        "name": f"User2 Agent {uuid.uuid4().hex[:8]}",
        "archetype": "leader",
        "goal": "Test goal 2",
        "background": "Test background 2",
        "expertise": "Test expertise 2",
        "avatar_prompt": "Professional leader",
        "avatar_url": "https://example.com/avatar2.png",
        "is_favorite": False
    }
    
    user2_agent_response = run_request(
        "POST", 
        "/saved-agents", 
        data=user2_agent_data, 
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    if not user2_agent_response or user2_agent_response["status_code"] != 200:
        print("Failed to create agent for User 2")
        return
    
    user2_agent_id = user2_agent_response["data"].get("id")
    user2_agent_name = user2_agent_response["data"].get("name")
    
    print(f"Created agent for User 2: {user2_agent_name} ({user2_agent_id})")
    
    # Step 4: Verify each user can see only their own agents
    print("\nStep 4: Verifying each user can see only their own agents")
    
    # Get User 1's agents
    user1_agents_response = run_request(
        "GET", 
        "/saved-agents", 
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    if not user1_agents_response or user1_agents_response["status_code"] != 200:
        print("Failed to get agents for User 1")
        return
    
    user1_agents = user1_agents_response["data"]
    user1_agent_ids = [agent.get("id") for agent in user1_agents]
    
    print(f"User 1 has {len(user1_agents)} agents")
    print(f"User 1 agent IDs: {user1_agent_ids}")
    
    # Get User 2's agents
    user2_agents_response = run_request(
        "GET", 
        "/saved-agents", 
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    if not user2_agents_response or user2_agents_response["status_code"] != 200:
        print("Failed to get agents for User 2")
        return
    
    user2_agents = user2_agents_response["data"]
    user2_agent_ids = [agent.get("id") for agent in user2_agents]
    
    print(f"User 2 has {len(user2_agents)} agents")
    print(f"User 2 agent IDs: {user2_agent_ids}")
    
    # Check if User 1 can see User 2's agents
    user1_sees_user2_agent = user2_agent_id in user1_agent_ids
    print(f"User 1 can see User 2's agent: {user1_sees_user2_agent}")
    
    # Check if User 2 can see User 1's agents
    user2_sees_user1_agent = user1_agent_id in user2_agent_ids
    print(f"User 2 can see User 1's agent: {user2_sees_user1_agent}")
    
    # Step 5: Test if User 2 can toggle User 1's agent favorite status
    print("\nStep 5: Testing if User 2 can toggle User 1's agent favorite status")
    
    user2_toggle_user1_response = run_request(
        "PUT", 
        f"/saved-agents/{user1_agent_id}/favorite", 
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    
    if not user2_toggle_user1_response:
        print("Failed to make toggle request")
        return
    
    user2_toggle_status_code = user2_toggle_user1_response["status_code"]
    
    if user2_toggle_status_code == 200:
        print("❌ SECURITY ISSUE: User 2 was able to toggle User 1's agent favorite status!")
        
        # Check if the agent was actually modified
        user1_agents_after_response = run_request(
            "GET", 
            "/saved-agents", 
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        
        if user1_agents_after_response and user1_agents_after_response["status_code"] == 200:
            user1_agents_after = user1_agents_after_response["data"]
            user1_agent_after = next((a for a in user1_agents_after if a.get("id") == user1_agent_id), None)
            
            if user1_agent_after:
                original_is_favorite = user1_agent_response["data"].get("is_favorite", False)
                new_is_favorite = user1_agent_after.get("is_favorite", False)
                is_favorite_changed = original_is_favorite != new_is_favorite
                
                print(f"Agent favorite status was actually changed: {is_favorite_changed}")
                print(f"Original is_favorite: {original_is_favorite}")
                print(f"New is_favorite: {new_is_favorite}")
            else:
                print("Could not find agent after toggle")
    elif user2_toggle_status_code == 404:
        print("✅ User 2 correctly received 404 when trying to toggle User 1's agent")
    elif user2_toggle_status_code == 403:
        print("✅ User 2 correctly received 403 when trying to toggle User 1's agent")
    elif user2_toggle_status_code == 500:
        error_message = user2_toggle_user1_response["data"].get("detail", "")
        if "404: Saved agent not found" in error_message:
            print("✅ User 2 correctly received 500 with '404: Saved agent not found' when trying to toggle User 1's agent")
        else:
            print(f"❌ User 2 received 500 with unexpected error: {error_message}")
    else:
        print(f"❌ User 2 received unexpected status code: {user2_toggle_status_code}")
    
    # Step 6: Test if User 1 can toggle User 2's agent favorite status
    print("\nStep 6: Testing if User 1 can toggle User 2's agent favorite status")
    
    user1_toggle_user2_response = run_request(
        "PUT", 
        f"/saved-agents/{user2_agent_id}/favorite", 
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    
    if not user1_toggle_user2_response:
        print("Failed to make toggle request")
        return
    
    user1_toggle_status_code = user1_toggle_user2_response["status_code"]
    
    if user1_toggle_status_code == 200:
        print("❌ SECURITY ISSUE: User 1 was able to toggle User 2's agent favorite status!")
        
        # Check if the agent was actually modified
        user2_agents_after_response = run_request(
            "GET", 
            "/saved-agents", 
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        
        if user2_agents_after_response and user2_agents_after_response["status_code"] == 200:
            user2_agents_after = user2_agents_after_response["data"]
            user2_agent_after = next((a for a in user2_agents_after if a.get("id") == user2_agent_id), None)
            
            if user2_agent_after:
                original_is_favorite = user2_agent_response["data"].get("is_favorite", False)
                new_is_favorite = user2_agent_after.get("is_favorite", False)
                is_favorite_changed = original_is_favorite != new_is_favorite
                
                print(f"Agent favorite status was actually changed: {is_favorite_changed}")
                print(f"Original is_favorite: {original_is_favorite}")
                print(f"New is_favorite: {new_is_favorite}")
            else:
                print("Could not find agent after toggle")
    elif user1_toggle_status_code == 404:
        print("✅ User 1 correctly received 404 when trying to toggle User 2's agent")
    elif user1_toggle_status_code == 403:
        print("✅ User 1 correctly received 403 when trying to toggle User 2's agent")
    elif user1_toggle_status_code == 500:
        error_message = user1_toggle_user2_response["data"].get("detail", "")
        if "404: Saved agent not found" in error_message:
            print("✅ User 1 correctly received 500 with '404: Saved agent not found' when trying to toggle User 2's agent")
        else:
            print(f"❌ User 1 received 500 with unexpected error: {error_message}")
    else:
        print(f"❌ User 1 received unexpected status code: {user1_toggle_status_code}")
    
    print("\n=== USER DATA ISOLATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_toggle_favorite_isolation()