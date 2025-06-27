#!/usr/bin/env python3
"""
Fix for the conversation retrieval user data isolation issue
"""

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

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

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
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
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
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

# Global variables for auth testing
auth_token = None
test_user_id = None

def test_login():
    """Login with test endpoint to get auth token"""
    global auth_token, test_user_id
    
    # Try using the email/password login first with admin credentials
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    # If email/password login fails, try the test login endpoint
    if not login_test or not login_response:
        test_login_test, test_login_response = run_test(
            "Test Login Endpoint",
            "/auth/test-login",
            method="POST",
            expected_keys=["access_token", "token_type", "user"]
        )
        
        # Store the token for further testing if successful
        if test_login_test and test_login_response:
            auth_token = test_login_response.get("access_token")
            user_data = test_login_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"Test login successful. User ID: {test_user_id}")
            print(f"JWT Token: {auth_token}")
            return True
        else:
            print("Test login failed. Some tests may not work correctly.")
            return False
    else:
        # Store the token from email/password login
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True

def test_conversation_retrieval_fix():
    """Test the fix for conversation retrieval user data isolation"""
    print("\n" + "="*80)
    print("TESTING FIX FOR CONVERSATION RETRIEVAL USER DATA ISOLATION")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not test_login():
        print("❌ Cannot test conversation retrieval fix without authentication")
        return False, "Authentication failed"
    
    print("✅ Authentication successful")
    
    # Step 2: Create a second user for testing isolation
    print("\nStep 2: Creating a second user for testing isolation")
    
    second_user_email = f"second.user.{uuid.uuid4()}@example.com"
    second_user_password = "securePassword123"
    second_user_name = "Second Test User"
    
    register_data = {
        "email": second_user_email,
        "password": second_user_password,
        "name": second_user_name
    }
    
    register_test, register_response = run_test(
        "Register Second User",
        "/auth/register",
        method="POST",
        data=register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not register_test:
        print("❌ Failed to register second user")
        return False, "Failed to register second user"
    
    print("✅ Successfully registered second user")
    
    # Store the second user's token and ID
    second_user_token = register_response.get("access_token")
    second_user_data = register_response.get("user", {})
    second_user_id = second_user_data.get("id")
    
    # Step 3: Create a conversation for the first user
    print("\nStep 3: Creating a conversation for the first user")
    
    # Create agents for the first user
    agent_data = [
        {
            "name": "Dr. James Wilson",
            "archetype": "scientist",
            "personality": {
                "extroversion": 4,
                "optimism": 6,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 6
            },
            "goal": "Advance scientific understanding of the project",
            "expertise": "Quantum Physics",
            "background": "Former lead researcher at CERN",
            "memory_summary": "",
            "avatar_prompt": "",
            "avatar_url": ""
        },
        {
            "name": "Sarah Johnson",
            "archetype": "leader",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            },
            "goal": "Ensure project success and team coordination",
            "expertise": "Project Management",
            "background": "20 years experience in tech leadership",
            "memory_summary": "",
            "avatar_prompt": "",
            "avatar_url": ""
        }
    ]
    
    created_agents = []
    
    for agent in agent_data:
        create_agent_test, create_agent_response = run_test(
            f"Create Agent: {agent['name']}",
            "/agents",
            method="POST",
            data=agent,
            auth=True,
            headers={"Authorization": f"Bearer {auth_token}"},
            expected_keys=["id", "name"]
        )
        
        if create_agent_test and create_agent_response:
            print(f"✅ Created agent: {create_agent_response.get('name')} with ID: {create_agent_response.get('id')}")
            created_agents.append(create_agent_response)
        else:
            print(f"❌ Failed to create agent: {agent['name']}")
    
    if len(created_agents) < 2:
        print(f"❌ Failed to create at least 2 agents. Only created {len(created_agents)} out of 2.")
        return False, "Failed to create at least 2 agents"
    
    print(f"✅ Successfully created {len(created_agents)} agents")
    
    # Set a scenario for the first user
    scenario_data = {
        "scenario": "The team is discussing the implementation of a new quantum computing project with potential applications in cryptography.",
        "scenario_name": "Quantum Computing Project"
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        headers={"Authorization": f"Bearer {auth_token}"},
        expected_keys=["message", "scenario"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario")
        return False, "Failed to set scenario"
    
    print("✅ Successfully set scenario")
    
    # Start simulation for the first user
    simulation_start_test, simulation_start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        headers={"Authorization": f"Bearer {auth_token}"},
        expected_keys=["message", "state"]
    )
    
    if not simulation_start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print("✅ Successfully started simulation")
    
    # Generate conversation for the first user
    generate_data = {
        "round_number": 1,
        "time_period": "Day 1 Morning",
        "scenario": scenario_data["scenario"],
        "scenario_name": scenario_data["scenario_name"]
    }
    
    generate_test, generate_response = run_test(
        "Generate Conversation",
        "/conversation/generate",
        method="POST",
        data=generate_data,
        auth=True,
        headers={"Authorization": f"Bearer {auth_token}"},
        expected_keys=["id", "round_number", "messages"]
    )
    
    if not generate_test:
        print("❌ Failed to generate conversation")
        return False, "Failed to generate conversation"
    
    print("✅ Successfully generated conversation")
    
    # Step 4: Get conversations for the first user
    print("\nStep 4: Getting conversations for the first user")
    
    get_conversations_test, get_conversations_response = run_test(
        "Get First User Conversations",
        "/conversations",
        method="GET",
        auth=True,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    if not get_conversations_test:
        print("❌ Failed to get first user conversations")
        return False, "Failed to get first user conversations"
    
    print("✅ Successfully retrieved first user conversations")
    
    # Check if the first user can see their conversations
    first_user_conversations = get_conversations_response
    
    if len(first_user_conversations) > 0:
        print(f"✅ First user can see their conversations ({len(first_user_conversations)} conversations)")
    else:
        print("❌ First user cannot see their conversations")
        return False, "First user cannot see their conversations"
    
    # Step 5: Get conversations for the second user
    print("\nStep 5: Getting conversations for the second user")
    
    get_second_user_conversations_test, get_second_user_conversations_response = run_test(
        "Get Second User Conversations",
        "/conversations",
        method="GET",
        auth=True,
        headers={"Authorization": f"Bearer {second_user_token}"}
    )
    
    if not get_second_user_conversations_test:
        print("❌ Failed to get second user conversations")
        return False, "Failed to get second user conversations"
    
    print("✅ Successfully retrieved second user conversations")
    
    # Check if the second user can see the first user's conversations
    second_user_conversations = get_second_user_conversations_response
    
    if len(second_user_conversations) == 0:
        print("✅ Second user cannot see first user's conversations")
    else:
        print(f"❌ Second user can see first user's conversations ({len(second_user_conversations)} conversations)")
        
        # Check if any of the conversations belong to the first user
        first_user_conversations_seen_by_second = [conv for conv in second_user_conversations if conv.get("user_id") == test_user_id]
        
        if len(first_user_conversations_seen_by_second) > 0:
            print(f"❌ Second user can see {len(first_user_conversations_seen_by_second)} conversations belonging to the first user")
            return False, "Second user can see conversations belonging to the first user"
        else:
            print("✅ None of the conversations seen by the second user belong to the first user")
    
    return True, "Conversation retrieval user data isolation is working correctly"

if __name__ == "__main__":
    # Run the test
    test_conversation_retrieval_fix()