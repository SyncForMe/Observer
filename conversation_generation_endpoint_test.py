#!/usr/bin/env python3
"""
Test module for conversation generation endpoint
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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None

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
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

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

def test_conversation_generation_authentication():
    """Test authentication requirements for conversation generation endpoint"""
    print("\n" + "="*80)
    print("TESTING AUTHENTICATION REQUIREMENTS FOR CONVERSATION GENERATION")
    print("="*80)
    
    # Test 1: Try to generate conversation without authentication
    print("\nTest 1: Generating conversation without authentication")
    
    generate_data = {
        "round_number": 1,
        "time_period": "Day 1 Morning",
        "scenario": "Test scenario",
        "scenario_name": "Test Scenario"
    }
    
    no_auth_test, no_auth_response = run_test(
        "Generate Conversation Without Authentication",
        "/conversation/generate",
        method="POST",
        data=generate_data,
        expected_status=403  # Should return 403 Forbidden
    )
    
    if no_auth_test:
        print("✅ Conversation generation correctly requires authentication")
    else:
        print("❌ Conversation generation does not properly enforce authentication")
        return False, "Conversation generation does not properly enforce authentication"
    
    return True, "Authentication requirements for conversation generation are working correctly"

def test_conversation_generation_no_agents():
    """Test conversation generation with no agents"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION GENERATION WITH NO AGENTS")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not auth_token:
        if not test_login():
            print("❌ Cannot test conversation generation without authentication")
            return False, "Authentication failed"
    
    print("✅ Authentication successful")
    
    # Step 2: Delete all existing agents
    print("\nStep 2: Deleting all existing agents")
    
    get_agents_test, get_agents_response = run_test(
        "Get User Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not get_agents_test:
        print("❌ Failed to get user agents")
        return False, "Failed to get user agents"
    
    for agent in get_agents_response:
        agent_id = agent.get("id")
        if agent_id:
            delete_agent_test, delete_agent_response = run_test(
                f"Delete Agent {agent_id}",
                f"/agents/{agent_id}",
                method="DELETE",
                auth=True
            )
            if delete_agent_test:
                print(f"✅ Deleted agent {agent_id}")
            else:
                print(f"❌ Failed to delete agent {agent_id}")
    
    # Step 3: Start simulation
    print("\nStep 3: Starting simulation")
    
    simulation_start_test, simulation_start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not simulation_start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print("✅ Successfully started simulation")
    
    # Step 4: Try to generate conversation with no agents
    print("\nStep 4: Generating conversation with no agents")
    
    generate_data = {
        "round_number": 1,
        "time_period": "Day 1 Morning",
        "scenario": "Test scenario",
        "scenario_name": "Test Scenario"
    }
    
    generate_test, generate_response = run_test(
        "Generate Conversation With No Agents",
        "/conversation/generate",
        method="POST",
        data=generate_data,
        auth=True,
        expected_status=400  # Should return 400 Bad Request
    )
    
    if generate_test:
        print("✅ Conversation generation correctly requires at least 2 agents")
        
        # Check if the error message is informative
        if generate_response and "detail" in generate_response:
            error_message = generate_response.get("detail", "")
            if "Need at least 2 agents" in error_message:
                print("✅ Error message is informative: " + error_message)
            else:
                print("⚠️ Error message could be more informative: " + error_message)
    else:
        print("❌ Conversation generation does not properly handle the case with no agents")
        return False, "Conversation generation does not properly handle the case with no agents"
    
    return True, "Conversation generation correctly requires at least 2 agents"

def test_conversation_generation_with_agents():
    """Test conversation generation with agents"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION GENERATION WITH AGENTS")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not auth_token:
        if not test_login():
            print("❌ Cannot test conversation generation without authentication")
            return False, "Authentication failed"
    
    print("✅ Authentication successful")
    
    # Step 2: Create agents for the user
    print("\nStep 2: Creating agents for the user")
    
    # Create three agents with different archetypes
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
        },
        {
            "name": "Michael Chen",
            "archetype": "skeptic",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            },
            "goal": "Identify and mitigate project risks",
            "expertise": "Risk Assessment",
            "background": "Former security consultant",
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
            expected_keys=["id", "name"]
        )
        
        if create_agent_test and create_agent_response:
            print(f"✅ Created agent: {create_agent_response.get('name')} with ID: {create_agent_response.get('id')}")
            created_agents.append(create_agent_response)
        else:
            print(f"❌ Failed to create agent: {agent['name']}")
    
    if len(created_agents) < 2:
        print(f"❌ Failed to create at least 2 agents. Only created {len(created_agents)} out of 3.")
        return False, "Failed to create at least 2 agents"
    
    print(f"✅ Successfully created {len(created_agents)} agents")
    
    # Step 3: Set a scenario for the user
    print("\nStep 3: Setting a scenario for the user")
    
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
        expected_keys=["message", "scenario"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario")
        return False, "Failed to set scenario"
    
    print("✅ Successfully set scenario")
    
    # Step 4: Start simulation for the user
    print("\nStep 4: Starting simulation for the user")
    
    simulation_start_test, simulation_start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not simulation_start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print("✅ Successfully started simulation")
    
    # Step 5: Generate conversation between agents
    print("\nStep 5: Generating conversation between agents")
    
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
        expected_keys=["id", "round_number", "messages"]
    )
    
    if not generate_test:
        print("❌ Failed to generate conversation")
        return False, "Failed to generate conversation"
    
    print("✅ Successfully generated conversation")
    
    # Step 6: Verify conversation structure
    print("\nStep 6: Verifying conversation structure")
    
    # Check if the conversation has the correct structure
    if "id" in generate_response and "round_number" in generate_response and "messages" in generate_response:
        print("✅ Conversation has the correct structure")
    else:
        print("❌ Conversation does not have the correct structure")
        return False, "Conversation does not have the correct structure"
    
    # Check if the conversation has messages
    messages = generate_response.get("messages", [])
    if len(messages) > 0:
        print(f"✅ Conversation has {len(messages)} messages")
    else:
        print("❌ Conversation has no messages")
        return False, "Conversation has no messages"
    
    # Check if the messages have the correct structure
    for i, message in enumerate(messages):
        if "agent_id" in message and "agent_name" in message and "message" in message:
            print(f"✅ Message {i+1} has the correct structure")
        else:
            print(f"❌ Message {i+1} does not have the correct structure")
            return False, "Message does not have the correct structure"
    
    # Check if the conversation is associated with the user
    if "user_id" in generate_response and generate_response["user_id"] == test_user_id:
        print("✅ Conversation is associated with the user")
    else:
        print("❌ Conversation is not associated with the user")
        return False, "Conversation is not associated with the user"
    
    # Print the generated conversation
    print("\nGenerated Conversation:")
    for message in messages:
        agent_name = message.get("agent_name", "Unknown")
        message_text = message.get("message", "")
        print(f"{agent_name}: {message_text[:100]}..." if len(message_text) > 100 else f"{agent_name}: {message_text}")
    
    # Step 7: Verify conversation is saved in the database
    print("\nStep 7: Verifying conversation is saved in the database")
    
    get_conversations_test, get_conversations_response = run_test(
        "Get User Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not get_conversations_test:
        print("❌ Failed to get user conversations")
        return False, "Failed to get user conversations"
    
    # Check if the generated conversation is in the list
    conversation_found = False
    for conversation in get_conversations_response:
        if conversation.get("id") == generate_response.get("id"):
            conversation_found = True
            print("✅ Generated conversation found in the database")
            break
    
    if not conversation_found:
        print("❌ Generated conversation not found in the database")
        return False, "Generated conversation not found in the database"
    
    # Step 8: Test user data isolation
    print("\nStep 8: Testing user data isolation")
    
    # Create a second user for testing isolation
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
    
    # Get conversations for the second user
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
    
    # Check if the second user can see the first user's conversations
    first_user_conversations_seen_by_second = [conv for conv in get_second_user_conversations_response if conv.get("user_id") == test_user_id]
    
    if len(first_user_conversations_seen_by_second) == 0:
        print("✅ Second user cannot see first user's conversations")
    else:
        print("❌ Second user can see first user's conversations")
        return False, "Second user can see first user's conversations"
    
    return True, "Conversation generation with agents is working correctly"

if __name__ == "__main__":
    # First, login to get authentication token
    test_login()
    
    # Run the tests
    test_conversation_generation_authentication()
    test_conversation_generation_no_agents()
    test_conversation_generation_with_agents()
    
    # Print summary of all tests
    print_summary()