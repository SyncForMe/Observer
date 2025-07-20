#!/usr/bin/env python3
"""
Comprehensive Conversation Generation System Test
Tests the specific issues reported in the review request:
1. GET /api/conversations endpoint
2. Simulation state verification
3. Conversation generation trigger
4. Data persistence verification
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables
auth_token = None
test_user_id = None
test_agents = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
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
            response = requests.delete(url, json=data, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
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
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result,
            "response_time": response_time
        })
        
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

def authenticate():
    """Authenticate using guest login"""
    global auth_token, test_user_id
    
    print("\n" + "="*60)
    print("AUTHENTICATING WITH GUEST LOGIN")
    print("="*60)
    
    # Try guest authentication first
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest authentication successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest authentication failed")
        return False

def setup_test_agents():
    """Create test agents for conversation generation"""
    global test_agents
    
    print("\n" + "="*60)
    print("SETTING UP TEST AGENTS")
    print("="*60)
    
    # Define test agents
    agent_configs = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics, 10 years research experience"
        },
        {
            "name": "Marcus Rodriguez",
            "archetype": "leader",
            "goal": "Lead the research team effectively",
            "expertise": "Project Management and Leadership",
            "background": "MBA, 15 years in tech leadership roles"
        },
        {
            "name": "Dr. Emily Watson",
            "archetype": "researcher",
            "goal": "Conduct thorough analysis and documentation",
            "expertise": "Data Analysis and Research Methods",
            "background": "PhD in Computer Science, specializing in AI research"
        }
    ]
    
    created_agents = []
    
    for i, agent_config in enumerate(agent_configs):
        agent_data = {
            "name": agent_config["name"],
            "archetype": agent_config["archetype"],
            "goal": agent_config["goal"],
            "expertise": agent_config["expertise"],
            "background": agent_config["background"],
            "personality": {
                "extroversion": 7,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            }
        }
        
        create_test, create_response = run_test(
            f"Create Test Agent {i+1}: {agent_config['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            created_agents.append({
                "id": agent_id,
                "name": agent_config["name"],
                "archetype": agent_config["archetype"]
            })
            print(f"✅ Created agent: {agent_config['name']} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent: {agent_config['name']}")
    
    test_agents = created_agents
    print(f"\n✅ Successfully created {len(test_agents)} test agents")
    return len(test_agents) >= 2  # Need at least 2 agents for conversation

def test_simulation_state():
    """Test GET /api/simulation/state endpoint"""
    print("\n" + "="*60)
    print("TESTING SIMULATION STATE")
    print("="*60)
    
    # Test 1: Get initial simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if not state_test or not state_response:
        print("❌ Failed to get simulation state")
        return False
    
    print(f"✅ Retrieved simulation state successfully")
    
    # Test 2: Start simulation
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_test or not start_response:
        print("❌ Failed to start simulation")
        return False
    
    print(f"✅ Started simulation successfully")
    
    # Test 3: Verify simulation is active
    active_state_test, active_state_response = run_test(
        "Get Active Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if active_state_test and active_state_response:
        is_active = active_state_response.get("is_active", False)
        if is_active:
            print("✅ Simulation is marked as active")
            return True
        else:
            print("❌ Simulation is not marked as active")
            return False
    else:
        print("❌ Failed to verify simulation state")
        return False

def test_conversations_endpoint():
    """Test GET /api/conversations endpoint"""
    print("\n" + "="*60)
    print("TESTING CONVERSATIONS ENDPOINT")
    print("="*60)
    
    # Test 1: Get conversations (should be empty initially)
    conversations_test, conversations_response = run_test(
        "Get Conversations (Initial)",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test:
        print("❌ Failed to get conversations")
        return False
    
    initial_count = len(conversations_response) if conversations_response else 0
    print(f"✅ Retrieved conversations successfully. Initial count: {initial_count}")
    
    # Test 2: Verify conversation data structure if any exist
    if initial_count > 0:
        sample_conversation = conversations_response[0]
        print(f"Sample conversation structure: {list(sample_conversation.keys())}")
        
        # Check for required fields
        required_fields = ["id", "messages", "user_id"]
        missing_fields = [field for field in required_fields if field not in sample_conversation]
        
        if missing_fields:
            print(f"❌ Missing required fields in conversation: {missing_fields}")
            return False
        else:
            print("✅ Conversation structure contains required fields")
    
    return True

def test_conversation_generation():
    """Test POST /api/conversation/generate endpoint"""
    print("\n" + "="*60)
    print("TESTING CONVERSATION GENERATION")
    print("="*60)
    
    # Test 1: Generate conversation with valid setup
    generate_test, generate_response = run_test(
        "Generate Conversation",
        "/conversation/generate",
        method="POST",
        auth=True,
        expected_keys=["id", "messages"]
    )
    
    if not generate_test or not generate_response:
        print("❌ Failed to generate conversation")
        return False
    
    conversation_id = generate_response.get("id")
    messages = generate_response.get("messages", [])
    
    print(f"✅ Generated conversation successfully")
    print(f"Conversation ID: {conversation_id}")
    print(f"Message count: {len(messages)}")
    
    # Test 2: Verify message structure
    if messages:
        sample_message = messages[0]
        print(f"Sample message structure: {list(sample_message.keys())}")
        
        required_message_fields = ["agent_name", "message"]
        missing_message_fields = [field for field in required_message_fields if field not in sample_message]
        
        if missing_message_fields:
            print(f"❌ Missing required fields in message: {missing_message_fields}")
            return False
        else:
            print("✅ Message structure contains required fields")
    
    # Test 3: Verify conversation was saved
    saved_conversations_test, saved_conversations_response = run_test(
        "Get Conversations After Generation",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if saved_conversations_test and saved_conversations_response:
        new_count = len(saved_conversations_response)
        print(f"✅ Conversations count after generation: {new_count}")
        
        # Find the generated conversation
        generated_conversation = None
        for conv in saved_conversations_response:
            if conv.get("id") == conversation_id:
                generated_conversation = conv
                break
        
        if generated_conversation:
            print("✅ Generated conversation found in saved conversations")
            
            # Verify user_id association
            conv_user_id = generated_conversation.get("user_id")
            if conv_user_id == test_user_id:
                print("✅ Conversation is properly associated with user")
            else:
                print(f"❌ Conversation user_id mismatch: {conv_user_id} vs {test_user_id}")
                return False
        else:
            print("❌ Generated conversation not found in saved conversations")
            return False
    else:
        print("❌ Failed to retrieve conversations after generation")
        return False
    
    return True

def test_data_persistence():
    """Test data persistence across multiple operations"""
    print("\n" + "="*60)
    print("TESTING DATA PERSISTENCE")
    print("="*60)
    
    # Test 1: Generate multiple conversations
    conversation_ids = []
    
    for i in range(3):
        generate_test, generate_response = run_test(
            f"Generate Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            expected_keys=["id", "messages"]
        )
        
        if generate_test and generate_response:
            conversation_id = generate_response.get("id")
            conversation_ids.append(conversation_id)
            print(f"✅ Generated conversation {i+1}: {conversation_id}")
        else:
            print(f"❌ Failed to generate conversation {i+1}")
    
    # Test 2: Verify all conversations are persisted
    all_conversations_test, all_conversations_response = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if all_conversations_test and all_conversations_response:
        total_count = len(all_conversations_response)
        print(f"✅ Total conversations in database: {total_count}")
        
        # Verify all generated conversations exist
        found_conversations = []
        for conv in all_conversations_response:
            if conv.get("id") in conversation_ids:
                found_conversations.append(conv.get("id"))
        
        if len(found_conversations) == len(conversation_ids):
            print("✅ All generated conversations are persisted")
        else:
            print(f"❌ Only {len(found_conversations)}/{len(conversation_ids)} conversations persisted")
            return False
    else:
        print("❌ Failed to retrieve all conversations")
        return False
    
    # Test 3: Verify conversation content integrity
    for conv_id in conversation_ids:
        conversation = next((c for c in all_conversations_response if c.get("id") == conv_id), None)
        if conversation:
            messages = conversation.get("messages", [])
            if len(messages) > 0:
                print(f"✅ Conversation {conv_id} has {len(messages)} messages")
            else:
                print(f"❌ Conversation {conv_id} has no messages")
                return False
        else:
            print(f"❌ Conversation {conv_id} not found")
            return False
    
    return True

def test_error_conditions():
    """Test error conditions and edge cases"""
    print("\n" + "="*60)
    print("TESTING ERROR CONDITIONS")
    print("="*60)
    
    # Test 1: Generate conversation without agents
    # First, clear all agents
    if test_agents:
        for agent in test_agents:
            delete_test, delete_response = run_test(
                f"Delete Agent {agent['name']}",
                f"/agents/{agent['id']}",
                method="DELETE",
                auth=True
            )
    
    # Try to generate conversation with no agents
    no_agents_test, no_agents_response = run_test(
        "Generate Conversation Without Agents",
        "/conversation/generate",
        method="POST",
        auth=True,
        expected_status=400
    )
    
    if no_agents_test:
        print("✅ Correctly rejected conversation generation without agents")
    else:
        print("❌ Failed to reject conversation generation without agents")
    
    # Test 2: Generate conversation without authentication
    no_auth_test, no_auth_response = run_test(
        "Generate Conversation Without Auth",
        "/conversation/generate",
        method="POST",
        auth=False,
        expected_status=403
    )
    
    if no_auth_test:
        print("✅ Correctly rejected conversation generation without authentication")
    else:
        print("❌ Failed to reject conversation generation without authentication")
    
    # Test 3: Get conversations without authentication
    no_auth_conversations_test, no_auth_conversations_response = run_test(
        "Get Conversations Without Auth",
        "/conversations",
        method="GET",
        auth=False,
        expected_status=403
    )
    
    if no_auth_conversations_test:
        print("✅ Correctly rejected conversations access without authentication")
        return True
    else:
        print("❌ Failed to reject conversations access without authentication")
        return False

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"CONVERSATION GENERATION SYSTEM TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The conversation generation system is working correctly.")
    else:
        print(f"\n⚠️  {test_results['failed']} TESTS FAILED")
        print("Issues found in the conversation generation system:")
        
        for test in test_results["tests"]:
            if test["result"] == "FAILED":
                print(f"  ❌ {test['name']} - Expected {test['expected_status']}, got {test['status_code']}")
            elif test["result"] == "ERROR":
                print(f"  ❌ {test['name']} - Error: {test.get('error', 'Unknown error')}")
    
    print("="*80)

def main():
    """Main test execution"""
    print("🚀 STARTING CONVERSATION GENERATION SYSTEM TESTS")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Setup test agents
    if not setup_test_agents():
        print("❌ Failed to setup test agents. Cannot proceed with conversation tests.")
        return
    
    # Step 3: Test simulation state
    if not test_simulation_state():
        print("❌ Simulation state tests failed.")
    
    # Step 4: Test conversations endpoint
    if not test_conversations_endpoint():
        print("❌ Conversations endpoint tests failed.")
    
    # Step 5: Test conversation generation
    if not test_conversation_generation():
        print("❌ Conversation generation tests failed.")
    
    # Step 6: Test data persistence
    if not test_data_persistence():
        print("❌ Data persistence tests failed.")
    
    # Step 7: Test error conditions
    if not test_error_conditions():
        print("❌ Error conditions tests failed.")
    
    # Print final summary
    print_summary()

if __name__ == "__main__":
    main()