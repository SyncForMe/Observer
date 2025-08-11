#!/usr/bin/env python3
"""
Round-Based System Investigation Test
Investigating critical issues with the round-based system:
1. Round 2 appearing after only 4 messages (should be 9 with 3 agents)
2. Round 2 disappearing/reappearing when pause clicked
3. No progression to Round 3 after 15+ messages (19+ total)
4. Wrong time period showing "Day 1, Afternoon" but should need 3 complete rounds
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
from collections import defaultdict

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load JWT secret for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

# Global variables
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
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
            print(f"Unsupported method: {method}")
            return False, None
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        test_passed = response.status_code == expected_status
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

def login_as_guest():
    """Login as guest user"""
    global auth_token, test_user_id
    
    test_login_test, test_login_response = run_test(
        "Guest Login",
        "/auth/test-login",
        method="POST",
        expected_status=200
    )
    
    if test_login_test and test_login_response:
        auth_token = test_login_response.get("access_token")
        user_data = test_login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest login successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest login failed")
        return False

def analyze_conversations_and_rounds():
    """Get all conversations and analyze round numbers, message counts, and time periods"""
    print("\n" + "="*80)
    print("ANALYZING CONVERSATIONS AND ROUND SYSTEM")
    print("="*80)
    
    # Get all conversations
    conversations_test, conversations_response = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to get conversations")
        return False, {}
    
    print(f"\n📊 FOUND {len(conversations_response)} CONVERSATIONS")
    
    # Analyze each conversation
    conversation_analysis = []
    total_messages = 0
    round_message_counts = defaultdict(int)
    time_period_progression = []
    
    for i, conv in enumerate(conversations_response):
        conv_id = conv.get('id', f'conv_{i}')
        messages = conv.get('messages', [])
        message_count = len(messages)
        total_messages += message_count
        
        # Get conversation metadata
        round_number = conv.get('round_number', 'Unknown')
        time_period = conv.get('time_period', 'Unknown')
        created_at = conv.get('created_at', 'Unknown')
        scenario = conv.get('scenario', 'Unknown')
        
        # Count messages per round
        if round_number != 'Unknown':
            round_message_counts[round_number] += message_count
        
        # Track time period progression
        time_period_progression.append({
            'round': round_number,
            'time_period': time_period,
            'messages': message_count,
            'created_at': created_at
        })
        
        conversation_analysis.append({
            'index': i + 1,
            'id': conv_id,
            'round_number': round_number,
            'time_period': time_period,
            'message_count': message_count,
            'created_at': created_at,
            'scenario': scenario
        })
        
        print(f"Conversation {i+1}:")
        print(f"  - Round: {round_number}")
        print(f"  - Time Period: {time_period}")
        print(f"  - Messages: {message_count}")
        print(f"  - Created: {created_at}")
        print(f"  - Scenario: {scenario[:50]}..." if len(str(scenario)) > 50 else f"  - Scenario: {scenario}")
    
    print(f"\n📈 TOTAL MESSAGES ACROSS ALL CONVERSATIONS: {total_messages}")
    
    # Analyze round distribution
    print(f"\n🔄 MESSAGES PER ROUND:")
    for round_num in sorted(round_message_counts.keys()):
        print(f"  - Round {round_num}: {round_message_counts[round_num]} messages")
    
    # Analyze time period progression
    print(f"\n⏰ TIME PERIOD PROGRESSION:")
    for entry in time_period_progression:
        print(f"  - Round {entry['round']}: {entry['time_period']} ({entry['messages']} messages)")
    
    return True, {
        'conversations': conversation_analysis,
        'total_messages': total_messages,
        'round_message_counts': dict(round_message_counts),
        'time_progression': time_period_progression
    }

def get_simulation_state():
    """Get current simulation state"""
    print("\n" + "="*60)
    print("GETTING SIMULATION STATE")
    print("="*60)
    
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_test and state_response:
        print(f"✅ Simulation State Retrieved:")
        print(f"  - Current Day: {state_response.get('current_day', 'Unknown')}")
        print(f"  - Current Time Period: {state_response.get('current_time_period', 'Unknown')}")
        print(f"  - Scenario: {state_response.get('scenario', 'Unknown')}")
        print(f"  - Is Active: {state_response.get('is_active', 'Unknown')}")
        
        return True, state_response
    else:
        print("❌ Failed to get simulation state")
        return False, {}

def get_agents():
    """Get all agents to understand the team size"""
    print("\n" + "="*60)
    print("GETTING AGENTS")
    print("="*60)
    
    agents_test, agents_response = run_test(
        "Get All Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if agents_test and agents_response:
        print(f"✅ Found {len(agents_response)} agents:")
        for i, agent in enumerate(agents_response):
            print(f"  {i+1}. {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
        
        return True, agents_response
    else:
        print("❌ Failed to get agents")
        return False, []

def analyze_round_logic(agents_count, conversations_data):
    """Analyze the round logic based on agent count and conversation data"""
    print("\n" + "="*80)
    print("ANALYZING ROUND LOGIC")
    print("="*80)
    
    print(f"📊 ROUND SYSTEM ANALYSIS:")
    print(f"  - Number of agents: {agents_count}")
    print(f"  - Expected messages per round: {agents_count * 3} (3 messages per agent)")
    
    # Analyze the issues
    issues_found = []
    
    # Issue 1: Check if Round 2 appears too early
    round_2_conversations = [conv for conv in conversations_data['conversations'] if conv['round_number'] == 2]
    if round_2_conversations:
        # Find the first Round 2 conversation
        first_round_2 = min(round_2_conversations, key=lambda x: x['index'])
        messages_before_round_2 = sum(conv['message_count'] for conv in conversations_data['conversations'] if conv['index'] < first_round_2['index'])
        
        expected_messages_for_round_2 = agents_count * 3  # Should be 9 with 3 agents
        
        print(f"\n🚨 ISSUE 1 ANALYSIS - Round 2 Timing:")
        print(f"  - First Round 2 conversation appears at index: {first_round_2['index']}")
        print(f"  - Messages before Round 2: {messages_before_round_2}")
        print(f"  - Expected messages before Round 2: {expected_messages_for_round_2}")
        
        if messages_before_round_2 < expected_messages_for_round_2:
            issues_found.append(f"Round 2 appears after only {messages_before_round_2} messages (should be {expected_messages_for_round_2})")
            print(f"  ❌ CONFIRMED: Round 2 appears too early!")
        else:
            print(f"  ✅ Round 2 timing is correct")
    
    # Issue 2: Check for Round 3 progression
    round_3_conversations = [conv for conv in conversations_data['conversations'] if conv['round_number'] == 3]
    total_messages = conversations_data['total_messages']
    expected_messages_for_round_3 = agents_count * 3 * 2  # Should be 18 with 3 agents (2 complete rounds)
    
    print(f"\n🚨 ISSUE 2 ANALYSIS - Round 3 Progression:")
    print(f"  - Total messages: {total_messages}")
    print(f"  - Expected messages for Round 3: {expected_messages_for_round_3}")
    print(f"  - Round 3 conversations found: {len(round_3_conversations)}")
    
    if total_messages >= expected_messages_for_round_3 and len(round_3_conversations) == 0:
        issues_found.append(f"No Round 3 after {total_messages} messages (should appear after {expected_messages_for_round_3})")
        print(f"  ❌ CONFIRMED: Round 3 missing despite sufficient messages!")
    elif len(round_3_conversations) > 0:
        print(f"  ✅ Round 3 found")
    else:
        print(f"  ⚠️ Not enough messages yet for Round 3")
    
    # Issue 3: Check time period progression
    time_periods = [entry['time_period'] for entry in conversations_data['time_progression']]
    unique_time_periods = list(dict.fromkeys(time_periods))  # Preserve order, remove duplicates
    
    print(f"\n🚨 ISSUE 3 ANALYSIS - Time Period Progression:")
    print(f"  - Time periods seen: {unique_time_periods}")
    print(f"  - Total conversations: {len(conversations_data['conversations'])}")
    
    # Expected progression: 3 rounds per time period
    expected_rounds_per_time_period = 3
    max_round = max([conv['round_number'] for conv in conversations_data['conversations'] if conv['round_number'] != 'Unknown'], default=0)
    expected_time_periods = max_round // expected_rounds_per_time_period
    
    print(f"  - Max round number: {max_round}")
    print(f"  - Expected time periods based on rounds: {expected_time_periods}")
    
    if len(unique_time_periods) == 1 and max_round >= expected_rounds_per_time_period:
        issues_found.append(f"Time stuck on '{unique_time_periods[0]}' despite {max_round} rounds (should advance every {expected_rounds_per_time_period} rounds)")
        print(f"  ❌ CONFIRMED: Time period not advancing!")
    else:
        print(f"  ✅ Time period progression appears normal")
    
    return issues_found

def investigate_round_calculation_logic():
    """Try to understand how rounds are calculated by creating new conversations"""
    print("\n" + "="*80)
    print("INVESTIGATING ROUND CALCULATION LOGIC")
    print("="*80)
    
    # Get current state before generating
    print("\n📊 BEFORE GENERATING NEW CONVERSATIONS:")
    before_conversations_test, before_conversations = run_test(
        "Get Conversations Before",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if before_conversations_test:
        print(f"  - Conversations before: {len(before_conversations)}")
        if before_conversations:
            last_conv = before_conversations[0]  # Most recent first
            print(f"  - Last round: {last_conv.get('round_number', 'Unknown')}")
            print(f"  - Last time period: {last_conv.get('time_period', 'Unknown')}")
    
    # Generate a new conversation
    print("\n🔄 GENERATING NEW CONVERSATION:")
    generate_test, generate_response = run_test(
        "Generate New Conversation",
        "/conversation/generate",
        method="POST",
        auth=True
    )
    
    if generate_test and generate_response:
        print(f"✅ Generated new conversation")
        print(f"  - Response: {json.dumps(generate_response, indent=2)}")
    else:
        print("❌ Failed to generate new conversation")
        return False
    
    # Get state after generating
    print("\n📊 AFTER GENERATING NEW CONVERSATION:")
    after_conversations_test, after_conversations = run_test(
        "Get Conversations After",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if after_conversations_test:
        print(f"  - Conversations after: {len(after_conversations)}")
        if after_conversations:
            new_conv = after_conversations[0]  # Most recent first
            print(f"  - New round: {new_conv.get('round_number', 'Unknown')}")
            print(f"  - New time period: {new_conv.get('time_period', 'Unknown')}")
            print(f"  - New messages: {len(new_conv.get('messages', []))}")
    
    # Check simulation state
    state_test, state_response = run_test(
        "Get Simulation State After",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_test and state_response:
        print(f"  - Simulation day: {state_response.get('current_day', 'Unknown')}")
        print(f"  - Simulation time: {state_response.get('current_time_period', 'Unknown')}")
    
    return True

def main():
    """Main investigation function"""
    print("🔍 ROUND-BASED SYSTEM INVESTIGATION")
    print("="*80)
    print("Investigating critical issues reported by user:")
    print("1. Round 2 appearing after only 4 messages (should be 9 with 3 agents)")
    print("2. Round 2 disappearing/reappearing when pause clicked")
    print("3. No progression to Round 3 after 15+ messages (19+ total)")
    print("4. Wrong time period showing 'Day 1, Afternoon' but should need 3 complete rounds")
    print("="*80)
    
    # Step 1: Login as guest
    if not login_as_guest():
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Get agents to understand team size
    agents_success, agents_data = get_agents()
    if not agents_success:
        print("❌ Cannot proceed without agent data")
        return
    
    agents_count = len(agents_data)
    
    # Step 3: Get simulation state
    state_success, state_data = get_simulation_state()
    
    # Step 4: Analyze all conversations and rounds
    conv_success, conv_data = analyze_conversations_and_rounds()
    if not conv_success:
        print("❌ Cannot proceed without conversation data")
        return
    
    # Step 5: Analyze round logic and identify issues
    issues = analyze_round_logic(agents_count, conv_data)
    
    # Step 6: Investigate round calculation by generating new conversation
    investigate_round_calculation_logic()
    
    # Step 7: Final summary
    print("\n" + "="*80)
    print("🎯 INVESTIGATION SUMMARY")
    print("="*80)
    
    print(f"📊 SYSTEM STATE:")
    print(f"  - Agents: {agents_count}")
    print(f"  - Total Conversations: {len(conv_data['conversations'])}")
    print(f"  - Total Messages: {conv_data['total_messages']}")
    print(f"  - Current Simulation Day: {state_data.get('current_day', 'Unknown')}")
    print(f"  - Current Time Period: {state_data.get('current_time_period', 'Unknown')}")
    
    print(f"\n🚨 ISSUES IDENTIFIED:")
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("  ✅ No issues found with current data")
    
    print(f"\n🔄 ROUND DISTRIBUTION:")
    for round_num, message_count in conv_data['round_message_counts'].items():
        print(f"  - Round {round_num}: {message_count} messages")
    
    print(f"\n⏰ TIME PROGRESSION:")
    time_periods = [entry['time_period'] for entry in conv_data['time_progression']]
    unique_periods = list(dict.fromkeys(time_periods))
    for period in unique_periods:
        count = time_periods.count(period)
        print(f"  - {period}: {count} conversations")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if issues:
        print("  1. Check round calculation logic in backend")
        print("  2. Verify time advancement triggers")
        print("  3. Investigate conversation-to-round mapping")
        print("  4. Check for race conditions in round updates")
    else:
        print("  ✅ System appears to be working correctly with current data")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Investigation completed successfully")
    else:
        print("\n❌ Investigation found critical issues")