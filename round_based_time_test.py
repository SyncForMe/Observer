#!/usr/bin/env python3
"""
Round-Based Time Progression System Test
Testing the new round-based time progression system where:
- Each round = each agent sends 3 messages
- With 3 agents: 1 round = 9 messages total
- Time advances after each completed round
- Each time period (Morning/Afternoon/Evening) = 3 rounds
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime

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

def test_guest_login():
    """Login as guest user to get auth token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("STEP 1: LOGIN AS GUEST USER")
    print("="*80)
    
    guest_test, guest_response = run_test(
        "Guest Login",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token[:50]}...")
        return True
    else:
        print("❌ Guest login failed. Cannot proceed with testing.")
        return False

def get_simulation_state():
    """Get current simulation state"""
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_test and state_response:
        return state_response
    return None

def get_agent_count():
    """Get current agent count"""
    agents_test, agents_response = run_test(
        "Get Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if agents_test and agents_response:
        return len(agents_response)
    return 0

def create_test_agents():
    """Create 3 test agents for round-based testing"""
    print("\n" + "="*80)
    print("STEP 2: CREATE 3 TEST AGENTS FOR ROUND-BASED TESTING")
    print("="*80)
    
    agents_data = [
        {
            "name": "Dr. Quantum Researcher",
            "archetype": "scientist",
            "goal": "Research quantum computing applications",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics with 10 years research experience"
        },
        {
            "name": "Prof. AI Specialist", 
            "archetype": "researcher",
            "goal": "Develop advanced AI algorithms",
            "expertise": "Artificial Intelligence and Machine Learning",
            "background": "Professor of Computer Science specializing in AI"
        },
        {
            "name": "Tech Innovation Leader",
            "archetype": "leader", 
            "goal": "Lead technology innovation projects",
            "expertise": "Technology Leadership and Innovation",
            "background": "CTO with 15 years experience in tech innovation"
        }
    ]
    
    created_agents = []
    
    for i, agent_data in enumerate(agents_data, 1):
        create_test, create_response = run_test(
            f"Create Agent {i}: {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            if agent_id:
                created_agents.append(agent_id)
                print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
            else:
                print(f"❌ Failed to get agent ID for {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    if len(created_agents) == 3:
        print(f"✅ Successfully created all 3 agents for round-based testing")
        return True, created_agents
    else:
        print(f"❌ Only created {len(created_agents)} out of 3 agents")
        return False, created_agents

def test_round_based_time_progression():
    """Test the new round-based time progression system"""
    print("\n" + "="*80)
    print("STEP 3: TEST ROUND-BASED TIME PROGRESSION SYSTEM")
    print("="*80)
    
    # Get initial simulation state
    initial_state = get_simulation_state()
    if not initial_state:
        print("❌ Failed to get initial simulation state")
        return False
    
    print(f"Initial Time: Day {initial_state.get('current_day', 1)}, {initial_state.get('current_time_period', 'morning').title()}")
    
    # Verify we have 3 agents
    agent_count = get_agent_count()
    if agent_count != 3:
        print(f"❌ Expected 3 agents, found {agent_count}")
        return False
    
    print(f"✅ Confirmed 3 agents available for round-based testing")
    
    # Test Round 1: Generate first conversation
    print("\n" + "-"*60)
    print("ROUND 1: GENERATE FIRST CONVERSATION")
    print("-"*60)
    
    round1_test, round1_response = run_test(
        "Generate Round 1 Conversation",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True
    )
    
    if not round1_test or not round1_response:
        print("❌ Failed to generate Round 1 conversation")
        return False
    
    # Verify Round 1 creates 9 messages (3 agents × 3 messages each)
    round1_messages = round1_response.get("messages", [])
    round1_message_count = len(round1_messages)
    
    print(f"Round 1 Message Count: {round1_message_count}")
    
    if round1_message_count == 9:
        print("✅ Round 1 correctly created 9 messages (3 agents × 3 messages each)")
    else:
        print(f"❌ Round 1 created {round1_message_count} messages instead of 9")
        return False
    
    # Verify message distribution among agents
    agent_message_counts = {}
    for msg in round1_messages:
        agent_name = msg.get("agent_name", "Unknown")
        agent_message_counts[agent_name] = agent_message_counts.get(agent_name, 0) + 1
    
    print("Round 1 Message Distribution:")
    for agent, count in agent_message_counts.items():
        print(f"  - {agent}: {count} messages")
    
    # Check if each agent sent exactly 3 messages
    expected_messages_per_agent = 3
    all_agents_correct = True
    for agent, count in agent_message_counts.items():
        if count != expected_messages_per_agent:
            print(f"❌ {agent} sent {count} messages instead of {expected_messages_per_agent}")
            all_agents_correct = False
    
    if all_agents_correct:
        print("✅ All agents sent exactly 3 messages each in Round 1")
    else:
        print("❌ Message distribution is incorrect in Round 1")
        return False
    
    # Check time progression after Round 1
    time.sleep(2)  # Wait for time progression to process
    
    after_round1_state = get_simulation_state()
    if not after_round1_state:
        print("❌ Failed to get simulation state after Round 1")
        return False
    
    expected_time_after_round1 = "afternoon"
    actual_time_after_round1 = after_round1_state.get('current_time_period', 'morning')
    
    print(f"Time after Round 1: Day {after_round1_state.get('current_day', 1)}, {actual_time_after_round1.title()}")
    
    if actual_time_after_round1 == expected_time_after_round1:
        print("✅ Time correctly advanced to 'Day 1, Afternoon' after Round 1")
    else:
        print(f"❌ Time should be '{expected_time_after_round1}' but is '{actual_time_after_round1}'")
        return False
    
    # Test Round 2: Generate second conversation
    print("\n" + "-"*60)
    print("ROUND 2: GENERATE SECOND CONVERSATION")
    print("-"*60)
    
    round2_test, round2_response = run_test(
        "Generate Round 2 Conversation",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True
    )
    
    if not round2_test or not round2_response:
        print("❌ Failed to generate Round 2 conversation")
        return False
    
    # Verify Round 2 creates 9 messages
    round2_messages = round2_response.get("messages", [])
    round2_message_count = len(round2_messages)
    
    print(f"Round 2 Message Count: {round2_message_count}")
    
    if round2_message_count == 9:
        print("✅ Round 2 correctly created 9 messages (3 agents × 3 messages each)")
    else:
        print(f"❌ Round 2 created {round2_message_count} messages instead of 9")
        return False
    
    # Check time progression after Round 2
    time.sleep(2)  # Wait for time progression to process
    
    after_round2_state = get_simulation_state()
    if not after_round2_state:
        print("❌ Failed to get simulation state after Round 2")
        return False
    
    expected_time_after_round2 = "evening"
    actual_time_after_round2 = after_round2_state.get('current_time_period', 'afternoon')
    
    print(f"Time after Round 2: Day {after_round2_state.get('current_day', 1)}, {actual_time_after_round2.title()}")
    
    if actual_time_after_round2 == expected_time_after_round2:
        print("✅ Time correctly advanced to 'Day 1, Evening' after Round 2")
    else:
        print(f"❌ Time should be '{expected_time_after_round2}' but is '{actual_time_after_round2}'")
        return False
    
    # Test Round 3: Generate third conversation
    print("\n" + "-"*60)
    print("ROUND 3: GENERATE THIRD CONVERSATION")
    print("-"*60)
    
    round3_test, round3_response = run_test(
        "Generate Round 3 Conversation",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True
    )
    
    if not round3_test or not round3_response:
        print("❌ Failed to generate Round 3 conversation")
        return False
    
    # Verify Round 3 creates 9 messages
    round3_messages = round3_response.get("messages", [])
    round3_message_count = len(round3_messages)
    
    print(f"Round 3 Message Count: {round3_message_count}")
    
    if round3_message_count == 9:
        print("✅ Round 3 correctly created 9 messages (3 agents × 3 messages each)")
    else:
        print(f"❌ Round 3 created {round3_message_count} messages instead of 9")
        return False
    
    # Check time progression after Round 3 (should advance to Day 2, Morning)
    time.sleep(2)  # Wait for time progression to process
    
    after_round3_state = get_simulation_state()
    if not after_round3_state:
        print("❌ Failed to get simulation state after Round 3")
        return False
    
    expected_day_after_round3 = 2
    expected_time_after_round3 = "morning"
    actual_day_after_round3 = after_round3_state.get('current_day', 1)
    actual_time_after_round3 = after_round3_state.get('current_time_period', 'evening')
    
    print(f"Time after Round 3: Day {actual_day_after_round3}, {actual_time_after_round3.title()}")
    
    if actual_day_after_round3 == expected_day_after_round3 and actual_time_after_round3 == expected_time_after_round3:
        print("✅ Time correctly advanced to 'Day 2, Morning' after Round 3")
    else:
        print(f"❌ Time should be 'Day {expected_day_after_round3}, {expected_time_after_round3.title()}' but is 'Day {actual_day_after_round3}, {actual_time_after_round3.title()}'")
        return False
    
    return True

def verify_simulation_state_updates():
    """Verify that simulation state updates properly"""
    print("\n" + "="*80)
    print("STEP 4: VERIFY SIMULATION STATE UPDATES")
    print("="*80)
    
    # Get all conversations to verify total message count
    conversations_test, conversations_response = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to get conversations")
        return False
    
    total_conversations = len(conversations_response)
    total_messages = sum(len(conv.get("messages", [])) for conv in conversations_response)
    
    print(f"Total Conversations: {total_conversations}")
    print(f"Total Messages: {total_messages}")
    
    # With 3 rounds, we should have 3 conversations and 27 messages total
    expected_conversations = 3
    expected_messages = 27  # 3 rounds × 9 messages per round
    
    if total_conversations == expected_conversations:
        print(f"✅ Correct number of conversations: {total_conversations}")
    else:
        print(f"❌ Expected {expected_conversations} conversations, found {total_conversations}")
        return False
    
    if total_messages == expected_messages:
        print(f"✅ Correct total message count: {total_messages}")
    else:
        print(f"❌ Expected {expected_messages} messages, found {total_messages}")
        return False
    
    # Verify final simulation state
    final_state = get_simulation_state()
    if not final_state:
        print("❌ Failed to get final simulation state")
        return False
    
    print(f"Final Simulation State:")
    print(f"  - Day: {final_state.get('current_day', 1)}")
    print(f"  - Time Period: {final_state.get('current_time_period', 'unknown').title()}")
    print(f"  - Is Active: {final_state.get('is_active', False)}")
    
    return True

def main():
    """Main test execution"""
    print("="*80)
    print("ROUND-BASED TIME PROGRESSION SYSTEM TEST")
    print("="*80)
    print("Testing the new system where:")
    print("- Each round = each agent sends 3 messages")
    print("- With 3 agents: 1 round = 9 messages total")
    print("- Time advances after each completed round")
    print("- Each time period (Morning/Afternoon/Evening) = 3 rounds")
    print("="*80)
    
    # Step 1: Login as guest user
    if not test_guest_login():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Step 2: Create 3 test agents
    agents_created, agent_ids = create_test_agents()
    if not agents_created:
        print("❌ Cannot proceed without 3 agents")
        return False
    
    # Step 3: Test round-based time progression
    if not test_round_based_time_progression():
        print("❌ Round-based time progression test failed")
        return False
    
    # Step 4: Verify simulation state updates
    if not verify_simulation_state_updates():
        print("❌ Simulation state verification failed")
        return False
    
    # Print final summary
    print_summary()
    
    # Final assessment
    if test_results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Round-based time progression system is working correctly")
        print("✅ Each conversation generates 9 messages (3 agents × 3 messages)")
        print("✅ Time advances after each completed round")
        print("✅ Time periods progress: Morning → Afternoon → Evening → Next Day Morning")
        print("✅ Simulation state updates properly")
        return True
    else:
        print(f"\n❌ {test_results['failed']} TESTS FAILED")
        print("❌ Round-based time progression system has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)