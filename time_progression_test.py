#!/usr/bin/env python3
"""
TIME PROGRESSION SYSTEM DEBUGGING TEST
Debug the time progression system to identify why time is stuck at "Day 1 Morning".

Investigation Steps:
1. Check current simulation state (current_day, current_time_period)
2. Count total messages in database and verify agent count
3. Test the time advancement calculation manually
4. Check if `check_and_advance_time_automatically` function is working
5. Verify the messages per agent calculation (should be 9 messages per agent per time period)
6. Test time advancement manually using the debug endpoint `/simulation/force-time-update`

Expected Logic (User's Specification):
- Each agent sends 1 message per conversation
- When ALL agents reach 9 messages total, advance to next time period
- Example: 3 agents = 27 total messages → morning to afternoon
- Pattern: morning → afternoon → evening → next day morning
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

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

# Global variables for auth testing
auth_token = None
test_user_id = None

def authenticate():
    """Authenticate as guest user"""
    global auth_token, test_user_id
    
    print("🔐 Authenticating as guest user...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            print(f"✅ Authentication successful. User ID: {test_user_id}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def make_authenticated_request(method, endpoint, data=None, params=None):
    """Make an authenticated request to the API"""
    url = f"{API_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def check_current_simulation_state():
    """Step 1: Check current simulation state (current_day, current_time_period)"""
    print("\n" + "="*80)
    print("STEP 1: CHECKING CURRENT SIMULATION STATE")
    print("="*80)
    
    response = make_authenticated_request("GET", "/simulation/state")
    if response and response.status_code == 200:
        state = response.json()
        current_day = state.get("current_day", 1)
        current_time_period = state.get("current_time_period", "morning")
        is_active = state.get("is_active", False)
        
        print(f"📊 Current Simulation State:")
        print(f"  - Current Day: {current_day}")
        print(f"  - Current Time Period: {current_time_period}")
        print(f"  - Is Active: {is_active}")
        print(f"  - Full State: {json.dumps(state, indent=2)}")
        
        return state
    else:
        print(f"❌ Failed to get simulation state: {response.status_code if response else 'No response'}")
        return None

def count_messages_and_agents():
    """Step 2: Count total messages in database and verify agent count"""
    print("\n" + "="*80)
    print("STEP 2: COUNTING MESSAGES AND AGENTS")
    print("="*80)
    
    # Get all conversations
    conversations_response = make_authenticated_request("GET", "/conversations")
    if not conversations_response or conversations_response.status_code != 200:
        print(f"❌ Failed to get conversations: {conversations_response.status_code if conversations_response else 'No response'}")
        return None, None, None
    
    conversations = conversations_response.json()
    print(f"📊 Found {len(conversations)} conversations")
    
    # Count total messages and unique agents
    total_messages = 0
    unique_agents = set()
    conversation_details = []
    
    for i, conv in enumerate(conversations, 1):
        messages = conv.get("messages", [])
        conv_message_count = len(messages)
        total_messages += conv_message_count
        
        # Track unique agents
        conv_agents = set()
        for msg in messages:
            agent_name = msg.get("agent_name")
            if agent_name and agent_name != "Observer (You)":
                unique_agents.add(agent_name)
                conv_agents.add(agent_name)
        
        conversation_details.append({
            "conversation": i,
            "messages": conv_message_count,
            "agents": list(conv_agents),
            "time_period": conv.get("time_period", "Unknown"),
            "created_at": conv.get("created_at", "Unknown")
        })
        
        print(f"  Conversation {i}: {conv_message_count} messages, agents: {list(conv_agents)}, time: {conv.get('time_period', 'Unknown')}")
    
    agent_count = len(unique_agents)
    
    print(f"\n📊 MESSAGE AND AGENT SUMMARY:")
    print(f"  - Total Messages: {total_messages}")
    print(f"  - Unique Agents: {agent_count}")
    print(f"  - Agent Names: {list(unique_agents)}")
    
    return total_messages, agent_count, conversation_details

def test_time_advancement_calculation(total_messages, agent_count):
    """Step 3: Test the time advancement calculation manually"""
    print("\n" + "="*80)
    print("STEP 3: TESTING TIME ADVANCEMENT CALCULATION")
    print("="*80)
    
    if total_messages is None or agent_count is None:
        print("❌ Cannot test calculation - missing message or agent data")
        return None
    
    # Expected Logic from User's Specification:
    # - Each agent sends 1 message per conversation
    # - When ALL agents reach 9 messages total, advance to next time period
    # - Example: 3 agents = 27 total messages → morning to afternoon
    
    messages_per_agent_per_period = 9
    messages_per_time_period = agent_count * messages_per_agent_per_period
    
    print(f"🧮 TIME ADVANCEMENT CALCULATION:")
    print(f"  - Messages per agent per time period: {messages_per_agent_per_period}")
    print(f"  - Agent count: {agent_count}")
    print(f"  - Messages per time period: {messages_per_time_period}")
    print(f"  - Total messages: {total_messages}")
    
    # Calculate which time period we should be in
    time_period_number = total_messages // messages_per_time_period
    time_periods = ["morning", "afternoon", "evening"]
    expected_period_index = time_period_number % 3
    expected_period = time_periods[expected_period_index]
    expected_day = (time_period_number // 3) + 1
    
    print(f"  - Time period calculation: {total_messages} // {messages_per_time_period} = {time_period_number}")
    print(f"  - Expected period index: {time_period_number} % 3 = {expected_period_index}")
    print(f"  - Expected period: {expected_period}")
    print(f"  - Expected day: {expected_day}")
    
    # Calculate messages until next advancement
    messages_until_next = messages_per_time_period - (total_messages % messages_per_time_period)
    print(f"  - Messages until next advancement: {messages_until_next}")
    
    return {
        "expected_day": expected_day,
        "expected_period": expected_period,
        "messages_until_next": messages_until_next,
        "time_period_number": time_period_number
    }

def test_manual_time_advancement():
    """Step 6: Test time advancement manually using the debug endpoint"""
    print("\n" + "="*80)
    print("STEP 6: TESTING MANUAL TIME ADVANCEMENT")
    print("="*80)
    
    # Test the force time update endpoint
    response = make_authenticated_request("POST", "/simulation/force-time-update")
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ Manual time advancement test successful:")
        print(f"  - Time Advanced: {result.get('time_advanced', False)}")
        print(f"  - Current State: {json.dumps(result.get('current_state', {}), indent=2)}")
        return result
    else:
        print(f"❌ Manual time advancement failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"  Error: {response.text}")
        return None

def generate_test_conversation():
    """Generate a test conversation to add messages"""
    print("\n🔄 Generating test conversation to add messages...")
    
    response = make_authenticated_request("POST", "/conversation/generate")
    if response and response.status_code == 200:
        result = response.json()
        conversation = result.get("conversation", {})
        messages = conversation.get("messages", [])
        print(f"✅ Generated conversation with {len(messages)} messages")
        return len(messages)
    else:
        print(f"❌ Failed to generate conversation: {response.status_code if response else 'No response'}")
        return 0

def check_agents():
    """Check if there are agents available for testing"""
    print("\n🤖 Checking available agents...")
    
    response = make_authenticated_request("GET", "/agents")
    if response and response.status_code == 200:
        agents = response.json()
        print(f"📊 Found {len(agents)} agents")
        for i, agent in enumerate(agents, 1):
            print(f"  Agent {i}: {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
        return len(agents)
    else:
        print(f"❌ Failed to get agents: {response.status_code if response else 'No response'}")
        return 0

def create_test_agents_if_needed():
    """Create test agents if none exist"""
    agent_count = check_agents()
    
    if agent_count < 3:
        print(f"\n🔧 Creating test agents (need at least 3, have {agent_count})...")
        
        test_agents = [
            {
                "name": "Dr. Quantum Researcher",
                "archetype": "scientist",
                "goal": "Research quantum computing applications",
                "expertise": "Quantum physics and computing",
                "background": "PhD in Quantum Physics with 10 years research experience",
                "personality": {
                    "extroversion": 7,
                    "optimism": 8,
                    "curiosity": 9,
                    "cooperativeness": 7,
                    "energy": 6
                }
            },
            {
                "name": "Prof. Engineering Lead",
                "archetype": "leader",
                "goal": "Lead engineering implementation",
                "expertise": "Systems engineering and project management",
                "background": "Senior Engineering Manager with enterprise experience",
                "personality": {
                    "extroversion": 8,
                    "optimism": 7,
                    "curiosity": 6,
                    "cooperativeness": 8,
                    "energy": 8
                }
            },
            {
                "name": "Dr. Risk Analyst",
                "archetype": "skeptic",
                "goal": "Identify and mitigate project risks",
                "expertise": "Risk assessment and quality assurance",
                "background": "Risk management specialist with technical background",
                "personality": {
                    "extroversion": 5,
                    "optimism": 4,
                    "curiosity": 8,
                    "cooperativeness": 6,
                    "energy": 5
                }
            }
        ]
        
        created_count = 0
        for agent_data in test_agents:
            response = make_authenticated_request("POST", "/agents", data=agent_data)
            if response and response.status_code == 200:
                result = response.json()
                agent_id = result.get("agent_id")
                print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
                created_count += 1
            else:
                print(f"❌ Failed to create agent: {agent_data['name']}")
        
        print(f"✅ Created {created_count} test agents")
        return agent_count + created_count
    
    return agent_count

def start_simulation_if_needed():
    """Start simulation if it's not active"""
    print("\n🚀 Checking if simulation is active...")
    
    state = check_current_simulation_state()
    if state and not state.get("is_active", False):
        print("🔧 Starting simulation...")
        response = make_authenticated_request("POST", "/simulation/start")
        if response and response.status_code == 200:
            print("✅ Simulation started")
            return True
        else:
            print(f"❌ Failed to start simulation: {response.status_code if response else 'No response'}")
            return False
    elif state and state.get("is_active", False):
        print("✅ Simulation is already active")
        return True
    else:
        print("❌ Could not determine simulation state")
        return False

def comprehensive_time_progression_test():
    """Run comprehensive time progression debugging test"""
    print("🕐 TIME PROGRESSION SYSTEM DEBUGGING TEST")
    print("="*80)
    print("Investigating why time is stuck at 'Day 1 Morning'")
    print("="*80)
    
    # Authenticate
    if not authenticate():
        print("❌ Authentication failed - cannot proceed")
        return False
    
    # Ensure we have agents and simulation is active
    agent_count = create_test_agents_if_needed()
    if agent_count < 3:
        print("❌ Need at least 3 agents for proper testing")
        return False
    
    if not start_simulation_if_needed():
        print("❌ Simulation not active - cannot proceed")
        return False
    
    # Step 1: Check current simulation state
    initial_state = check_current_simulation_state()
    if not initial_state:
        print("❌ Could not get initial simulation state")
        return False
    
    # Step 2: Count messages and agents
    total_messages, agent_count, conversation_details = count_messages_and_agents()
    if total_messages is None:
        print("❌ Could not count messages and agents")
        return False
    
    # Step 3: Test time advancement calculation
    calculation_result = test_time_advancement_calculation(total_messages, agent_count)
    if not calculation_result:
        print("❌ Could not perform time advancement calculation")
        return False
    
    # Compare expected vs actual
    print("\n" + "="*80)
    print("STEP 4: COMPARING EXPECTED VS ACTUAL STATE")
    print("="*80)
    
    current_day = initial_state.get("current_day", 1)
    current_period = initial_state.get("current_time_period", "morning")
    expected_day = calculation_result["expected_day"]
    expected_period = calculation_result["expected_period"]
    
    print(f"🔍 STATE COMPARISON:")
    print(f"  - Current State: Day {current_day}, {current_period}")
    print(f"  - Expected State: Day {expected_day}, {expected_period}")
    print(f"  - Match: {'✅ YES' if (current_day == expected_day and current_period == expected_period) else '❌ NO'}")
    
    if current_day != expected_day or current_period != expected_period:
        print(f"\n🚨 TIME PROGRESSION ISSUE DETECTED!")
        print(f"  - Time should have advanced but hasn't")
        print(f"  - Messages until next advancement: {calculation_result['messages_until_next']}")
        
        # Step 5: Test if check_and_advance_time_automatically is working
        print("\n" + "="*80)
        print("STEP 5: TESTING AUTOMATIC TIME ADVANCEMENT FUNCTION")
        print("="*80)
        
        # Generate a few more conversations to trigger advancement
        if calculation_result['messages_until_next'] > 0:
            print(f"🔄 Need {calculation_result['messages_until_next']} more messages to trigger advancement")
            print("🔄 Generating conversations to reach threshold...")
            
            conversations_needed = (calculation_result['messages_until_next'] // agent_count) + 1
            for i in range(conversations_needed):
                messages_added = generate_test_conversation()
                print(f"  Generated conversation {i+1}: +{messages_added} messages")
                time.sleep(2)  # Brief pause between generations
        
        # Check state after generating more conversations
        print("\n🔍 Checking state after generating more conversations...")
        updated_state = check_current_simulation_state()
        if updated_state:
            new_day = updated_state.get("current_day", 1)
            new_period = updated_state.get("current_time_period", "morning")
            print(f"  - Updated State: Day {new_day}, {new_period}")
            
            if new_day != current_day or new_period != current_period:
                print("✅ Time advancement is working!")
            else:
                print("❌ Time advancement is not working automatically")
    else:
        print("✅ Time progression appears to be working correctly")
    
    # Step 6: Test manual time advancement
    manual_result = test_manual_time_advancement()
    
    # Final state check
    print("\n" + "="*80)
    print("FINAL STATE CHECK")
    print("="*80)
    
    final_state = check_current_simulation_state()
    final_messages, final_agent_count, _ = count_messages_and_agents()
    
    if final_state and final_messages is not None:
        print(f"📊 FINAL SUMMARY:")
        print(f"  - Final State: Day {final_state.get('current_day', 1)}, {final_state.get('current_time_period', 'morning')}")
        print(f"  - Total Messages: {final_messages}")
        print(f"  - Agent Count: {final_agent_count}")
        
        # Recalculate expected state
        final_calculation = test_time_advancement_calculation(final_messages, final_agent_count)
        if final_calculation:
            final_expected_day = final_calculation["expected_day"]
            final_expected_period = final_calculation["expected_period"]
            
            print(f"  - Expected State: Day {final_expected_day}, {final_expected_period}")
            
            if (final_state.get('current_day', 1) == final_expected_day and 
                final_state.get('current_time_period', 'morning') == final_expected_period):
                print("✅ TIME PROGRESSION IS WORKING CORRECTLY!")
                return True
            else:
                print("❌ TIME PROGRESSION ISSUE PERSISTS")
                print(f"  - Issue: Time should be at Day {final_expected_day}, {final_expected_period}")
                print(f"  - But it's at Day {final_state.get('current_day', 1)}, {final_state.get('current_time_period', 'morning')}")
                return False
    
    return False

def main():
    """Main test execution"""
    try:
        success = comprehensive_time_progression_test()
        
        print("\n" + "="*80)
        print("TIME PROGRESSION TEST COMPLETE")
        print("="*80)
        
        if success:
            print("✅ TIME PROGRESSION SYSTEM IS WORKING CORRECTLY")
        else:
            print("❌ TIME PROGRESSION SYSTEM HAS ISSUES")
            print("\nRECOMMENDATIONS:")
            print("1. Check if check_and_advance_time_automatically() is being called after conversation generation")
            print("2. Verify database updates are persisting correctly")
            print("3. Check for race conditions in concurrent message generation")
            print("4. Ensure simulation state is being updated atomically")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)