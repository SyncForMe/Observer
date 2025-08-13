#!/usr/bin/env python3
"""
QUICK TIME PROGRESSION TEST
Generate conversations to reach 28 messages and test time progression
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def login_and_get_token():
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def get_conversations(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_simulation_state(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    if response.status_code == 200:
        return response.json()
    return {}

def generate_conversation(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    return response.status_code == 200

def count_messages(conversations):
    total = 0
    for conv in conversations:
        total += len(conv.get("messages", []))
    return total

def main():
    print("🧪 QUICK TIME PROGRESSION TEST")
    
    token = login_and_get_token()
    if not token:
        print("❌ Login failed")
        return
    
    # Check current state
    conversations = get_conversations(token)
    current_messages = count_messages(conversations)
    sim_state = get_simulation_state(token)
    
    print(f"📊 Current state:")
    print(f"   - Messages: {current_messages}")
    print(f"   - Time: Day {sim_state.get('current_day', 1)}, {sim_state.get('current_time_period', 'morning')}")
    
    # Generate conversations to reach 28+ messages
    target = 28
    attempts = 0
    max_attempts = 10
    
    while current_messages < target and attempts < max_attempts:
        print(f"\n📝 Generating conversation {attempts + 1}...")
        
        if generate_conversation(token):
            conversations = get_conversations(token)
            current_messages = count_messages(conversations)
            sim_state = get_simulation_state(token)
            
            print(f"   - Messages now: {current_messages}")
            print(f"   - Time now: Day {sim_state.get('current_day', 1)}, {sim_state.get('current_time_period', 'morning')}")
            
            if current_messages >= target:
                break
        else:
            print("   - Failed to generate conversation")
        
        attempts += 1
        time.sleep(2)  # Brief delay
    
    # Final check
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   - Total messages: {current_messages}")
    print(f"   - Current time: Day {sim_state.get('current_day', 1)}, {sim_state.get('current_time_period', 'morning')}")
    
    # Check if bug is present
    if current_messages >= 28:
        expected_period = "afternoon"  # Messages 28+ should be afternoon
        actual_period = sim_state.get('current_time_period', 'morning')
        
        if actual_period == "morning":
            print(f"   - 🚨 BUG CONFIRMED: With {current_messages} messages, should be '{expected_period}' but showing '{actual_period}'")
        else:
            print(f"   - ✅ Time progression working: With {current_messages} messages, correctly showing '{actual_period}'")
    else:
        print(f"   - ⚠️ Did not reach 28 messages to test the bug")

if __name__ == "__main__":
    main()