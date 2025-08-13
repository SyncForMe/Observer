#!/usr/bin/env python3
"""
Detailed Time Progression Debug Test

This test will examine the exact issue with time progression logic.
Based on the investigation, we found:
- 19 conversations exist
- Simulation state shows Day 2, afternoon
- Expected state should be Day 3, morning (19 conversations / 3 = 6 advancements)
- last_time_advance_round is 18, but we have 19 conversations

The issue appears to be that the logic only advances when conversation_count % 3 == 0,
but we have 19 conversations (19 % 3 = 1), so it won't advance until we reach 21 conversations.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def debug_time_progression():
    print("🔍 DETAILED TIME PROGRESSION DEBUG")
    print("=" * 80)
    
    # Login as guest
    response = requests.post(f"{API_URL}/auth/test-login")
    auth_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get simulation state
    sim_state = requests.get(f"{API_URL}/simulation/state", headers=headers).json()
    
    # Get conversations
    conversations = requests.get(f"{API_URL}/conversations", headers=headers).json()
    
    print(f"CURRENT STATE:")
    print(f"  Conversations: {len(conversations)}")
    print(f"  Simulation Day: {sim_state['current_day']}")
    print(f"  Simulation Time: {sim_state['current_time_period']}")
    print(f"  Last Time Advance Round: {sim_state.get('last_time_advance_round', 'Not set')}")
    
    print(f"\nTIME ADVANCEMENT LOGIC ANALYSIS:")
    conversation_count = len(conversations)
    print(f"  Current conversation count: {conversation_count}")
    print(f"  conversation_count % 3 = {conversation_count % 3}")
    print(f"  Should advance? {conversation_count % 3 == 0}")
    
    last_advance = sim_state.get('last_time_advance_round', 0)
    print(f"  Last advance at round: {last_advance}")
    print(f"  conversation_count > last_advance? {conversation_count > last_advance}")
    
    # Calculate expected state
    total_advances = conversation_count // 3
    print(f"\nEXPECTED STATE CALCULATION:")
    print(f"  Total advances should be: {conversation_count} // 3 = {total_advances}")
    
    # Time progression: morning -> afternoon -> evening -> next day morning
    time_periods = ["morning", "afternoon", "evening"]
    expected_day = 1 + (total_advances // 3)
    expected_period = time_periods[total_advances % 3]
    
    print(f"  Expected day: {expected_day}")
    print(f"  Expected period: {expected_period}")
    
    print(f"\nPROBLEM IDENTIFIED:")
    print(f"  The logic only advances when conversation_count % 3 == 0")
    print(f"  With {conversation_count} conversations, {conversation_count} % 3 = {conversation_count % 3}")
    print(f"  So time won't advance until we reach {conversation_count + (3 - conversation_count % 3)} conversations")
    
    print(f"\nCONVERSATION TIME PERIODS:")
    for i, conv in enumerate(conversations):
        round_num = conv.get('round_number', i+1)
        time_period = conv.get('time_period', 'Unknown')
        print(f"  Round {round_num}: {time_period}")
    
    # The issue is that individual conversations have correct time_period metadata
    # but the simulation state is not being updated correctly
    
    print(f"\nROOT CAUSE:")
    print(f"  1. Individual conversations have correct time_period metadata")
    print(f"  2. But simulation state is lagging behind")
    print(f"  3. The time advancement logic waits for multiples of 3")
    print(f"  4. With 19 conversations, it won't advance until 21 conversations")
    print(f"  5. However, conversation metadata shows Day 3 Morning for round 19")
    print(f"  6. This suggests the conversation creation logic is working")
    print(f"  7. But the simulation state update is not keeping up")

if __name__ == "__main__":
    debug_time_progression()