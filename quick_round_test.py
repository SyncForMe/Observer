#!/usr/bin/env python3
"""
Quick Round-Based System Verification Test
Focus on core functionality verification
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
API_URL = f"{os.environ.get('REACT_APP_BACKEND_URL')}/api"

def quick_round_test():
    print("="*80)
    print("QUICK ROUND-BASED TIME PROGRESSION VERIFICATION")
    print("="*80)
    
    # Step 1: Login as guest
    print("1. Logging in as guest user...")
    login_response = requests.post(f'{API_URL}/auth/test-login')
    if login_response.status_code != 200:
        print("❌ Failed to login as guest")
        return False
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Guest login successful")
    
    # Step 2: Get initial state
    print("\n2. Getting initial simulation state...")
    state_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    initial_state = state_response.json()
    initial_day = initial_state.get('current_day', 1)
    initial_period = initial_state.get('current_time_period', 'morning')
    print(f"✅ Initial time: Day {initial_day}, {initial_period.title()}")
    
    # Step 3: Get agent count
    print("\n3. Checking available agents...")
    agents_response = requests.get(f'{API_URL}/agents', headers=headers)
    agents = agents_response.json()
    agent_count = len(agents)
    print(f"✅ Found {agent_count} agents available")
    
    # Step 4: Generate one conversation
    print(f"\n4. Generating one conversation...")
    conv_response = requests.post(f'{API_URL}/conversation/generate', headers=headers)
    if conv_response.status_code != 200:
        print("❌ Failed to generate conversation")
        return False
    
    conv_data = conv_response.json()
    messages = conv_data.get('messages', [])
    message_count = len(messages)
    
    print(f"✅ Conversation generated with {message_count} messages")
    
    # Step 5: Verify round-based structure
    expected_total = agent_count * 3
    print(f"\nExpected: {agent_count} agents × 3 messages = {expected_total} messages")
    print(f"Actual: {message_count} messages")
    
    if message_count == expected_total:
        print("✅ Message count matches round-based system expectation")
    else:
        print("❌ Message count doesn't match round-based system expectation")
        return False
    
    # Step 6: Verify each agent contributed
    agent_id_counts = {}
    for msg in messages:
        agent_id = msg.get('agent_id', 'Unknown')
        agent_id_counts[agent_id] = agent_id_counts.get(agent_id, 0) + 1
    
    print(f"\nMessage distribution by agent ID:")
    all_correct = True
    for agent_id, count in agent_id_counts.items():
        print(f"  - Agent {agent_id[:8]}...: {count} messages")
        if count != 3:
            print(f"    ❌ Expected 3 messages per agent")
            all_correct = False
        else:
            print(f"    ✅ Correct")
    
    if all_correct:
        print("✅ Each agent sent exactly 3 messages")
    else:
        print("❌ Agent message distribution is incorrect")
        return False
    
    # Step 7: Check time progression
    print(f"\n7. Checking time progression...")
    time.sleep(3)  # Wait for time progression
    
    after_state_response = requests.get(f'{API_URL}/simulation/state', headers=headers)
    after_state = after_state_response.json()
    after_day = after_state.get('current_day', 1)
    after_period = after_state.get('current_time_period', 'morning')
    
    print(f"Time after conversation: Day {after_day}, {after_period.title()}")
    
    # Check if time advanced
    time_advanced = (after_day > initial_day) or (after_day == initial_day and after_period != initial_period)
    
    if time_advanced:
        print("✅ Time advanced after completing a round")
    else:
        print("❌ Time did not advance after completing a round")
        return False
    
    print("\n" + "="*80)
    print("QUICK VERIFICATION RESULTS")
    print("="*80)
    print("✅ Guest login working")
    print(f"✅ Found {agent_count} agents")
    print(f"✅ Generated {message_count} messages ({agent_count} × 3)")
    print("✅ Each agent sent exactly 3 messages per round")
    print("✅ Time advanced after completing a round")
    print("✅ Round-based time progression system is working correctly!")
    print("="*80)
    
    return True

if __name__ == "__main__":
    success = quick_round_test()
    if success:
        print("\n🎉 VERIFICATION PASSED!")
        print("✅ Round-based time progression system is working correctly")
    else:
        print("\n❌ VERIFICATION FAILED")
        print("❌ Round-based time progression system has issues")