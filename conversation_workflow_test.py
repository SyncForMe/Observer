#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import base64
import re
import uuid
import jwt
from datetime import datetime, timedelta
import statistics
from collections import Counter, defaultdict

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
created_document_ids = []
test_user_email = f"test.user.{uuid.uuid4()}@example.com"
test_user_password = "securePassword123"
test_user_name = "Test User"

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

def test_complete_conversation_workflow():
    """Test the complete conversation generation workflow"""
    print("\n" + "="*80)
    print("TESTING COMPLETE CONVERSATION GENERATION WORKFLOW")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not auth_token:
        if not test_login():
            print("❌ Cannot test conversation workflow without authentication")
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
    
    # Print the generated conversation
    print("\nGenerated Conversation:")
    for message in generate_response.get("messages", []):
        agent_name = message.get("agent_name", "Unknown")
        message_text = message.get("message", "")
        print(f"{agent_name}: {message_text[:100]}..." if len(message_text) > 100 else f"{agent_name}: {message_text}")
    
    # Step 6: Verify conversation is saved with proper user_id
    print("\nStep 6: Verifying conversation is saved with proper user_id")
    
    # Get all conversations for the user
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
            
            # Check if the user_id is correct
            if conversation.get("user_id") == test_user_id:
                print("✅ Conversation is saved with correct user_id")
            else:
                print(f"❌ Conversation has incorrect user_id: {conversation.get('user_id')} (expected: {test_user_id})")
                return False, "Conversation has incorrect user_id"
            
            break
    
    if not conversation_found:
        print("❌ Generated conversation not found in user conversations")
        return False, "Generated conversation not found in user conversations"
    
    print("✅ Generated conversation found in user conversations")
    
    # Print summary
    print("\nCOMPLETE CONVERSATION GENERATION WORKFLOW SUMMARY:")
    print("✅ Successfully authenticated user")
    print(f"✅ Successfully created {len(created_agents)} agents")
    print("✅ Successfully set scenario")
    print("✅ Successfully started simulation")
    print("✅ Successfully generated conversation")
    print("✅ Conversation is saved with proper user_id")
    
    return True, "Complete conversation generation workflow is working correctly"

def test_fixed_conversation_generation():
    """Test the fixed conversation generation endpoint"""
    print("\n" + "="*80)
    print("TESTING FIXED CONVERSATION GENERATION")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not auth_token:
        if not test_login():
            print("❌ Cannot test fixed conversation generation without authentication")
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
        print(f"❌ Failed to create at least 2 agents. Only created {len(created_agents)} out of 2.")
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
    
    # Step 5: Generate conversation with POST /api/conversation/generate
    print("\nStep 5: Generating conversation with POST /api/conversation/generate")
    
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
    
    # Check if the user_id is correct
    if generate_response.get("user_id") == test_user_id:
        print("✅ Conversation is generated with correct user_id")
    else:
        print(f"❌ Conversation has incorrect user_id: {generate_response.get('user_id')} (expected: {test_user_id})")
        return False, "Conversation has incorrect user_id"
    
    # Check if the conversation includes messages from the user's agents
    agent_names = [agent.get("name") for agent in created_agents]
    conversation_agent_names = [message.get("agent_name") for message in generate_response.get("messages", [])]
    
    all_agents_included = all(name in conversation_agent_names for name in agent_names)
    if all_agents_included:
        print("✅ Conversation includes messages from all user's agents")
    else:
        print(f"❌ Conversation does not include messages from all user's agents")
        print(f"Expected agents: {agent_names}")
        print(f"Agents in conversation: {conversation_agent_names}")
        return False, "Conversation does not include messages from all user's agents"
    
    # Step 6: Verify conversation content is generated using Gemini
    print("\nStep 6: Verifying conversation content is generated using Gemini")
    
    # Check if the conversation messages have substantial content
    has_substantial_content = all(len(message.get("message", "")) > 50 for message in generate_response.get("messages", []))
    if has_substantial_content:
        print("✅ Conversation messages have substantial content")
    else:
        print("❌ Some conversation messages have insufficient content")
        return False, "Some conversation messages have insufficient content"
    
    # Print the generated conversation
    print("\nGenerated Conversation:")
    for message in generate_response.get("messages", []):
        agent_name = message.get("agent_name", "Unknown")
        message_text = message.get("message", "")
        print(f"{agent_name}: {message_text[:100]}..." if len(message_text) > 100 else f"{agent_name}: {message_text}")
    
    # Print summary
    print("\nFIXED CONVERSATION GENERATION SUMMARY:")
    print("✅ Successfully authenticated user")
    print(f"✅ Successfully created {len(created_agents)} agents")
    print("✅ Successfully set scenario")
    print("✅ Successfully started simulation")
    print("✅ Successfully generated conversation with POST /api/conversation/generate")
    print("✅ Conversation includes messages from all user's agents")
    print("✅ Conversation messages have substantial content")
    
    return True, "Fixed conversation generation is working correctly"

def test_conversation_retrieval():
    """Test the conversation retrieval endpoints"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION RETRIEVAL")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not auth_token:
        if not test_login():
            print("❌ Cannot test conversation retrieval without authentication")
            return False, "Authentication failed"
    
    print("✅ Authentication successful")
    
    # Step 2: Get all conversations for the user
    print("\nStep 2: Getting all conversations for the user")
    
    get_conversations_test, get_conversations_response = run_test(
        "Get User Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not get_conversations_test:
        print("❌ Failed to get user conversations")
        return False, "Failed to get user conversations"
    
    print("✅ Successfully retrieved user conversations")
    
    # Check if the conversations have the correct user_id
    user_conversations = [conv for conv in get_conversations_response if conv.get("user_id") == test_user_id]
    other_user_conversations = [conv for conv in get_conversations_response if conv.get("user_id") != test_user_id and conv.get("user_id")]
    
    print(f"User conversations: {len(user_conversations)}")
    print(f"Other user conversations: {len(other_user_conversations)}")
    
    if len(user_conversations) > 0:
        print("✅ Retrieved conversations include user's conversations")
    else:
        print("⚠️ No conversations found for the user")
    
    # Step 3: Verify user data isolation in conversation viewing
    print("\nStep 3: Verifying user data isolation in conversation viewing")
    
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
    
    print("✅ Successfully retrieved second user conversations")
    
    # Check if the second user can see the first user's conversations
    second_user_conversations = [conv for conv in get_second_user_conversations_response if conv.get("user_id") == second_user_id]
    first_user_conversations_seen_by_second = [conv for conv in get_second_user_conversations_response if conv.get("user_id") == test_user_id]
    
    print(f"Second user conversations: {len(second_user_conversations)}")
    print(f"First user conversations seen by second user: {len(first_user_conversations_seen_by_second)}")
    
    if len(first_user_conversations_seen_by_second) == 0:
        print("✅ Second user cannot see first user's conversations")
    else:
        print("❌ Second user can see first user's conversations")
        return False, "Second user can see first user's conversations"
    
    # Print summary
    print("\nCONVERSATION RETRIEVAL SUMMARY:")
    print("✅ Successfully authenticated user")
    print("✅ Successfully retrieved user conversations")
    print("✅ User data isolation is properly implemented")
    
    return True, "Conversation retrieval is working correctly"

def test_error_handling():
    """Test error handling in conversation generation"""
    print("\n" + "="*80)
    print("TESTING ERROR HANDLING IN CONVERSATION GENERATION")
    print("="*80)
    
    # Step 1: Authenticate a user
    print("\nStep 1: Authenticating a user")
    if not auth_token:
        if not test_login():
            print("❌ Cannot test error handling without authentication")
            return False, "Authentication failed"
    
    print("✅ Authentication successful")
    
    # Step 2: Test conversation generation with < 2 agents
    print("\nStep 2: Testing conversation generation with < 2 agents")
    
    # Delete all existing agents
    get_agents_test, get_agents_response = run_test(
        "Get User Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test and get_agents_response:
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
    
    # Create a single agent
    agent_data = {
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
    }
    
    create_agent_test, create_agent_response = run_test(
        f"Create Single Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True,
        expected_keys=["id", "name"]
    )
    
    if create_agent_test:
        print("✅ Created single agent")
    else:
        print("❌ Failed to create single agent")
        return False, "Failed to create single agent"
    
    # Set a scenario
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
    
    if set_scenario_test:
        print("✅ Successfully set scenario")
    else:
        print("❌ Failed to set scenario")
        return False, "Failed to set scenario"
    
    # Start simulation
    simulation_start_test, simulation_start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if simulation_start_test:
        print("✅ Successfully started simulation")
    else:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    # Try to generate conversation with only one agent
    generate_data = {
        "round_number": 1,
        "time_period": "Day 1 Morning",
        "scenario": scenario_data["scenario"],
        "scenario_name": scenario_data["scenario_name"]
    }
    
    generate_test, generate_response = run_test(
        "Generate Conversation with < 2 Agents",
        "/conversation/generate",
        method="POST",
        data=generate_data,
        auth=True,
        expected_status=400
    )
    
    if generate_test:
        print("✅ Correctly rejected conversation generation with < 2 agents")
    else:
        print("❌ Failed to reject conversation generation with < 2 agents")
        return False, "Failed to reject conversation generation with < 2 agents"
    
    # Step 3: Test conversation generation without active simulation
    print("\nStep 3: Testing conversation generation without active simulation")
    
    # Create a second agent
    agent_data = {
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
    
    create_agent_test, create_agent_response = run_test(
        f"Create Second Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True,
        expected_keys=["id", "name"]
    )
    
    if create_agent_test:
        print("✅ Created second agent")
    else:
        print("❌ Failed to create second agent")
        return False, "Failed to create second agent"
    
    # Pause simulation
    pause_simulation_test, pause_simulation_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if pause_simulation_test:
        print("✅ Successfully paused simulation")
    else:
        print("❌ Failed to pause simulation")
        return False, "Failed to pause simulation"
    
    # Try to generate conversation without active simulation
    generate_test, generate_response = run_test(
        "Generate Conversation without Active Simulation",
        "/conversation/generate",
        method="POST",
        data=generate_data,
        auth=True,
        expected_status=400
    )
    
    if generate_test:
        print("✅ Correctly rejected conversation generation without active simulation")
    else:
        print("❌ Failed to reject conversation generation without active simulation")
        return False, "Failed to reject conversation generation without active simulation"
    
    # Step 4: Test authentication failures
    print("\nStep 4: Testing authentication failures")
    
    # Resume simulation
    resume_simulation_test, resume_simulation_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if resume_simulation_test:
        print("✅ Successfully resumed simulation")
    else:
        print("❌ Failed to resume simulation")
        return False, "Failed to resume simulation"
    
    # Try to generate conversation without authentication
    generate_test, generate_response = run_test(
        "Generate Conversation without Authentication",
        "/conversation/generate",
        method="POST",
        data=generate_data,
        auth=False,
        expected_status=403
    )
    
    if generate_test:
        print("✅ Correctly rejected conversation generation without authentication")
    else:
        print("❌ Failed to reject conversation generation without authentication")
        return False, "Failed to reject conversation generation without authentication"
    
    # Print summary
    print("\nERROR HANDLING SUMMARY:")
    print("✅ Correctly rejected conversation generation with < 2 agents")
    print("✅ Correctly rejected conversation generation without active simulation")
    print("✅ Correctly rejected conversation generation without authentication")
    
    return True, "Error handling in conversation generation is working correctly"

if __name__ == "__main__":
    # First, login to get authentication token
    test_login()
    
    # Run the tests
    test_complete_conversation_workflow()
    test_fixed_conversation_generation()
    test_conversation_retrieval()
    test_error_handling()
    
    # Print summary of all tests
    print_summary()