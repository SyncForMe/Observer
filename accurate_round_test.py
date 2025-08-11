#!/usr/bin/env python3
"""
Accurate Round-Based Time Progression Test
Testing the new round-based system correctly
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
    print("NEW SYSTEM UNDERSTANDING:")
    print("- Each round = each agent sends 3 messages")
    print("- With N agents: 1 round = N × 3 messages total")
    print("- Time advances after each completed round")
    print("- Each time period (Morning/Afternoon/Evening) = 3 rounds")
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
    
    # Calculate expected messages per round
    expected_messages_per_agent = 3
    expected_total_messages = agent_count * expected_messages_per_agent
    
    print(f"Expected messages per round: {agent_count} agents × 3 messages = {expected_total_messages}")
    
    # Step 4: Generate first conversation (Round 1)
    print(f"\n4. Generating Round 1 conversation...")
    conv1_response = requests.post(f'{API_URL}/conversation/generate', headers=headers)
    if conv1_response.status_code != 200:
        print("❌ Failed to generate Round 1 conversation")
        return False
    
    conv1_data = conv1_response.json()
    conv1_messages = conv1_data.get('messages', [])
    conv1_message_count = len(conv1_messages)
    
    print(f"✅ Round 1 generated with {conv1_message_count} messages")
    
    if conv1_message_count == expected_total_messages:
        print(f"✅ Round 1 message count is correct ({conv1_message_count} messages)")
    else:
        print(f"❌ Round 1 message count is incorrect ({conv1_message_count} vs {expected_total_messages})")
        return False
    
    # Verify each agent sent exactly 3 messages
    agent_message_counts = {}
    for msg in conv1_messages:
        agent_name = msg.get('agent_name', 'Unknown')
        agent_message_counts[agent_name] = agent_message_counts.get(agent_name, 0) + 1
    
    print("\nRound 1 Message Distribution:")
    all_agents_correct = True
    for agent_name, count in agent_message_counts.items():
        print(f"  - {agent_name}: {count} messages")
        if count != expected_messages_per_agent:
            print(f"    ❌ Expected {expected_messages_per_agent} messages")
            all_agents_correct = False
        else:
            print(f"    ✅ Correct message count")
    
    if not all_agents_correct:
        print("❌ Round 1 message distribution is incorrect")
        return False
    
    print("✅ Round 1 message distribution is correct - each agent sent exactly 3 messages")
    
    # Step 5: Check time progression after Round 1
    print(f"\n5. Checking time progression after Round 1...")
    time.sleep(3)  # Wait for time progression to process
    
    after_round1_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    if after_round1_response.status_code != 200:
        print("❌ Failed to get simulation state after Round 1")
        return False
    
    after_round1_state = after_round1_response.json()
    after_round1_day = after_round1_state.get('current_day', 1)
    after_round1_period = after_round1_state.get('current_time_period', 'morning')
    
    print(f"Time after Round 1: Day {after_round1_day}, {after_round1_period.title()}")
    
    # Check if time advanced
    time_advanced = False
    if after_round1_day > initial_day:
        time_advanced = True
        print("✅ Time advanced to next day")
    elif after_round1_day == initial_day and after_round1_period != initial_period:
        time_advanced = True
        print("✅ Time advanced to next period")
    
    if time_advanced:
        print("✅ Round-based time progression is working")
    else:
        print("❌ Time did not advance after completing Round 1")
        return False
    
    # Step 6: Generate Round 2 conversation
    print(f"\n6. Generating Round 2 conversation...")
    conv2_response = requests.post(f'{API_URL}/conversation/generate', headers=headers)
    if conv2_response.status_code != 200:
        print("❌ Failed to generate Round 2 conversation")
        return False
    
    conv2_data = conv2_response.json()
    conv2_messages = conv2_data.get('messages', [])
    conv2_message_count = len(conv2_messages)
    
    print(f"✅ Round 2 generated with {conv2_message_count} messages")
    
    if conv2_message_count == expected_total_messages:
        print(f"✅ Round 2 message count is correct ({conv2_message_count} messages)")
    else:
        print(f"❌ Round 2 message count is incorrect ({conv2_message_count} vs {expected_total_messages})")
        return False
    
    # Step 7: Check time progression after Round 2
    print(f"\n7. Checking time progression after Round 2...")
    time.sleep(3)  # Wait for time progression to process
    
    after_round2_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    if after_round2_response.status_code != 200:
        print("❌ Failed to get simulation state after Round 2")
        return False
    
    after_round2_state = after_round2_response.json()
    after_round2_day = after_round2_state.get('current_day', 1)
    after_round2_period = after_round2_state.get('current_time_period', 'morning')
    
    print(f"Time after Round 2: Day {after_round2_day}, {after_round2_period.title()}")
    
    # Check if time advanced again
    second_time_advanced = False
    if after_round2_day > after_round1_day:
        second_time_advanced = True
        print("✅ Time advanced to next day after Round 2")
    elif after_round2_day == after_round1_day and after_round2_period != after_round1_period:
        second_time_advanced = True
        print("✅ Time advanced to next period after Round 2")
    
    if second_time_advanced:
        print("✅ Continued round-based time progression is working")
    else:
        print("❌ Time did not advance after Round 2")
        return False
    
    # Step 8: Generate Round 3 conversation
    print(f"\n8. Generating Round 3 conversation...")
    conv3_response = requests.post(f'{API_URL}/conversation/generate', headers=headers)
    if conv3_response.status_code != 200:
        print("❌ Failed to generate Round 3 conversation")
        return False
    
    conv3_data = conv3_response.json()
    conv3_messages = conv3_data.get('messages', [])
    conv3_message_count = len(conv3_messages)
    
    print(f"✅ Round 3 generated with {conv3_message_count} messages")
    
    if conv3_message_count == expected_total_messages:
        print(f"✅ Round 3 message count is correct ({conv3_message_count} messages)")
    else:
        print(f"❌ Round 3 message count is incorrect ({conv3_message_count} vs {expected_total_messages})")
        return False
    
    # Step 9: Check time progression after Round 3
    print(f"\n9. Checking time progression after Round 3...")
    time.sleep(3)  # Wait for time progression to process
    
    after_round3_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    if after_round3_response.status_code != 200:
        print("❌ Failed to get simulation state after Round 3")
        return False
    
    after_round3_state = after_round3_response.json()
    after_round3_day = after_round3_state.get('current_day', 1)
    after_round3_period = after_round3_state.get('current_time_period', 'morning')
    
    print(f"Time after Round 3: Day {after_round3_day}, {after_round3_period.title()}")
    
    # Check if time advanced again
    third_time_advanced = False
    if after_round3_day > after_round2_day:
        third_time_advanced = True
        print("✅ Time advanced to next day after Round 3")
    elif after_round3_day == after_round2_day and after_round3_period != after_round2_period:
        third_time_advanced = True
        print("✅ Time advanced to next period after Round 3")
    
    if third_time_advanced:
        print("✅ Continued round-based time progression is working")
    else:
        print("❌ Time did not advance after Round 3")
        return False
    
    # Step 10: Verify total conversation and message counts
    print(f"\n10. Verifying total conversation and message counts...")
    conversations_response = requests.get(f'{API_URL}/conversations', headers=headers)
    if conversations_response.status_code != 200:
        print("❌ Failed to get conversations")
        return False
    
    conversations = conversations_response.json()
    total_conversations = len(conversations)
    total_messages = sum(len(conv.get("messages", [])) for conv in conversations)
    
    print(f"Total Conversations: {total_conversations}")
    print(f"Total Messages: {total_messages}")
    
    # With 3 rounds, we should have 3 conversations and (agent_count × 3 × 3) messages total
    expected_conversations = 3
    expected_total_messages = agent_count * 3 * 3  # 3 rounds × agent_count × 3 messages per agent
    
    if total_conversations >= expected_conversations:
        print(f"✅ Correct number of conversations: {total_conversations} (expected at least {expected_conversations})")
    else:
        print(f"❌ Expected at least {expected_conversations} conversations, found {total_conversations}")
        return False
    
    if total_messages >= expected_total_messages:
        print(f"✅ Correct total message count: {total_messages} (expected at least {expected_total_messages})")
    else:
        print(f"❌ Expected at least {expected_total_messages} messages, found {total_messages}")
        return False
    
    # Final summary
    print("\n" + "="*80)
    print("ROUND-BASED TIME PROGRESSION TEST RESULTS")
    print("="*80)
    print("✅ Guest login successful")
    print(f"✅ Found {agent_count} agents for testing")
    print(f"✅ Each conversation generates {expected_total_messages//3} messages ({agent_count} agents × 3 messages)")
    print("✅ Each agent sends exactly 3 messages per round")
    print("✅ Time advances after each completed round")
    print("✅ Generated 3 rounds successfully")
    print("✅ Time progression working correctly across multiple rounds")
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