#!/usr/bin/env python3
"""
Simple Round-Based Time Progression Test
Focus on testing the core round-based system functionality
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
API_URL = f"{os.environ.get('REACT_APP_BACKEND_URL')}/api"

def test_round_based_system():
    print("="*80)
    print("ROUND-BASED TIME PROGRESSION SYSTEM TEST")
    print("="*80)
    
    # Step 1: Login as guest
    print("\n1. Logging in as guest user...")
    login_response = requests.post(f'{API_URL}/auth/test-login')
    if login_response.status_code != 200:
        print("❌ Failed to login as guest")
        return False
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Guest login successful")
    
    # Step 2: Get initial simulation state
    print("\n2. Getting initial simulation state...")
    state_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    if state_response.status_code != 200:
        print("❌ Failed to get simulation state")
        return False
    
    initial_state = state_response.json()
    initial_day = initial_state.get('current_day', 1)
    initial_period = initial_state.get('current_time_period', 'morning')
    print(f"✅ Initial time: Day {initial_day}, {initial_period.title()}")
    
    # Step 3: Get agent count
    print("\n3. Checking available agents...")
    agents_response = requests.get(f'{API_URL}/agents', headers=headers)
    if agents_response.status_code != 200:
        print("❌ Failed to get agents")
        return False
    
    agents = agents_response.json()
    agent_count = len(agents)
    print(f"✅ Found {agent_count} agents available")
    
    if agent_count == 0:
        print("❌ No agents available for testing")
        return False
    
    # Step 4: Generate first conversation
    print(f"\n4. Generating first conversation...")
    conv1_response = requests.post(f'{API_URL}/conversation/generate', headers=headers)
    if conv1_response.status_code != 200:
        print("❌ Failed to generate first conversation")
        return False
    
    conv1_data = conv1_response.json()
    conv1_messages = conv1_data.get('messages', [])
    conv1_message_count = len(conv1_messages)
    
    print(f"✅ First conversation generated with {conv1_message_count} messages")
    
    # Calculate expected messages per round based on agent count
    expected_messages_per_agent = 3
    expected_total_messages = agent_count * expected_messages_per_agent
    
    print(f"Expected messages per round: {agent_count} agents × 3 messages = {expected_total_messages}")
    
    if conv1_message_count == expected_total_messages:
        print(f"✅ Message count matches expected round-based system ({conv1_message_count} messages)")
    else:
        print(f"❌ Message count doesn't match expected ({conv1_message_count} vs {expected_total_messages})")
        return False
    
    # Verify message distribution
    agent_message_counts = {}
    for msg in conv1_messages:
        agent_name = msg.get('agent_name', 'Unknown')
        agent_message_counts[agent_name] = agent_message_counts.get(agent_name, 0) + 1
    
    print("\nMessage distribution:")
    all_agents_correct = True
    for agent_name, count in agent_message_counts.items():
        print(f"  - {agent_name}: {count} messages")
        if count != expected_messages_per_agent:
            print(f"    ❌ Expected {expected_messages_per_agent} messages")
            all_agents_correct = False
        else:
            print(f"    ✅ Correct message count")
    
    if not all_agents_correct:
        print("❌ Message distribution is incorrect")
        return False
    
    # Step 5: Check time progression after first round
    print(f"\n5. Checking time progression after first round...")
    time.sleep(3)  # Wait for time progression to process
    
    after_conv1_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    if after_conv1_response.status_code != 200:
        print("❌ Failed to get simulation state after first conversation")
        return False
    
    after_conv1_state = after_conv1_response.json()
    after_conv1_day = after_conv1_state.get('current_day', 1)
    after_conv1_period = after_conv1_state.get('current_time_period', 'morning')
    
    print(f"Time after first round: Day {after_conv1_day}, {after_conv1_period.title()}")
    
    # Check if time advanced
    time_advanced = False
    if after_conv1_day > initial_day:
        time_advanced = True
        print("✅ Time advanced to next day")
    elif after_conv1_day == initial_day and after_conv1_period != initial_period:
        time_advanced = True
        print("✅ Time advanced to next period")
    
    if time_advanced:
        print("✅ Round-based time progression is working")
    else:
        print("❌ Time did not advance after completing a round")
        return False
    
    # Step 6: Generate second conversation to verify continued progression
    print(f"\n6. Generating second conversation...")
    conv2_response = requests.post(f'{API_URL}/conversation/generate', headers=headers)
    if conv2_response.status_code != 200:
        print("❌ Failed to generate second conversation")
        return False
    
    conv2_data = conv2_response.json()
    conv2_messages = conv2_data.get('messages', [])
    conv2_message_count = len(conv2_messages)
    
    print(f"✅ Second conversation generated with {conv2_message_count} messages")
    
    if conv2_message_count == expected_total_messages:
        print(f"✅ Second round also has correct message count ({conv2_message_count} messages)")
    else:
        print(f"❌ Second round has incorrect message count ({conv2_message_count} vs {expected_total_messages})")
        return False
    
    # Step 7: Check time progression after second round
    print(f"\n7. Checking time progression after second round...")
    time.sleep(3)  # Wait for time progression to process
    
    after_conv2_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    if after_conv2_response.status_code != 200:
        print("❌ Failed to get simulation state after second conversation")
        return False
    
    after_conv2_state = after_conv2_response.json()
    after_conv2_day = after_conv2_state.get('current_day', 1)
    after_conv2_period = after_conv2_state.get('current_time_period', 'morning')
    
    print(f"Time after second round: Day {after_conv2_day}, {after_conv2_period.title()}")
    
    # Check if time advanced again
    second_time_advanced = False
    if after_conv2_day > after_conv1_day:
        second_time_advanced = True
        print("✅ Time advanced to next day after second round")
    elif after_conv2_day == after_conv1_day and after_conv2_period != after_conv1_period:
        second_time_advanced = True
        print("✅ Time advanced to next period after second round")
    
    if second_time_advanced:
        print("✅ Continued round-based time progression is working")
    else:
        print("❌ Time did not advance after second round")
        return False
    
    # Final summary
    print("\n" + "="*80)
    print("ROUND-BASED TIME PROGRESSION TEST RESULTS")
    print("="*80)
    print("✅ Guest login successful")
    print(f"✅ Found {agent_count} agents for testing")
    print(f"✅ Each conversation generates {expected_total_messages} messages ({agent_count} agents × 3 messages)")
    print("✅ Each agent sends exactly 3 messages per round")
    print("✅ Time advances after each completed round")
    print("✅ Round-based time progression system is working correctly")
    print("="*80)
    
    return True

if __name__ == "__main__":
    success = test_round_based_system()
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Round-based time progression system is working correctly")
    else:
        print("\n❌ TESTS FAILED")
        print("❌ Round-based time progression system has issues")