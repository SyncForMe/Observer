#!/usr/bin/env python3
"""
CRITICAL TIME PROGRESSION DEBUG TEST
Investigating the exact issue reported by user:
- User has exactly 3 agents and 28 messages
- System shows "Day 1, Morning" instead of "Day 1, Afternoon"
- Expected: 3 agents × 9 messages per time period = 27 messages per time period
- Messages 1-27 = "Day 1, Morning", Messages 28+ = "Day 1, Afternoon"
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 CRITICAL TIME PROGRESSION DEBUG TEST")
print(f"API URL: {API_URL}")
print("="*80)

def login_as_guest():
    """Login as guest user to get auth token"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Guest login successful")
            print(f"User ID: {user_id}")
            return token, user_id
        else:
            print(f"❌ Guest login failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Guest login error: {e}")
        return None, None

def get_simulation_state(token):
    """Get current simulation state"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get simulation state: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
        return None

def get_all_conversations(token):
    """Get all conversations for the user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return None

def get_agents(token):
    """Get all agents for the user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return None

def count_messages_in_conversations(conversations):
    """Count total messages across all conversations"""
    total_messages = 0
    agent_names = set()
    
    for conv in conversations:
        messages = conv.get("messages", [])
        total_messages += len(messages)
        
        # Track unique agent names
        for msg in messages:
            agent_name = msg.get("agent_name")
            if agent_name and agent_name != "Observer (You)":
                agent_names.add(agent_name)
    
    return total_messages, len(agent_names), list(agent_names)

def manually_trigger_time_advancement(token):
    """Manually trigger time advancement function"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/simulation/advance-time", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to trigger time advancement: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error triggering time advancement: {e}")
        return None

def main():
    print("\n🔍 STEP 1: Login as guest user")
    token, user_id = login_as_guest()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print("\n🔍 STEP 2: Get simulation state and verify current_time_period")
    sim_state = get_simulation_state(token)
    if not sim_state:
        print("❌ Cannot get simulation state")
        return
    
    current_day = sim_state.get("current_day", 1)
    current_time_period = sim_state.get("current_time_period", "morning")
    is_active = sim_state.get("is_active", False)
    
    print(f"📊 Current Simulation State:")
    print(f"   - Day: {current_day}")
    print(f"   - Time Period: {current_time_period}")
    print(f"   - Active: {is_active}")
    
    print("\n🔍 STEP 3: Get all conversations and count messages exactly")
    conversations = get_all_conversations(token)
    if not conversations:
        print("❌ Cannot get conversations")
        return
    
    total_messages, agent_count_from_messages, agent_names = count_messages_in_conversations(conversations)
    
    print(f"📊 Conversation Analysis:")
    print(f"   - Total conversations: {len(conversations)}")
    print(f"   - Total messages: {total_messages}")
    print(f"   - Unique agents from messages: {agent_count_from_messages}")
    print(f"   - Agent names: {agent_names}")
    
    print("\n🔍 STEP 4: Get agents from agents endpoint")
    agents = get_agents(token)
    if agents:
        print(f"📊 Agents Endpoint:")
        print(f"   - Total agents: {len(agents)}")
        for agent in agents:
            print(f"   - {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'Unknown')})")
    
    print("\n🔍 STEP 5: Calculate expected time period")
    
    # Use the agent count from the agents endpoint if available, otherwise from messages
    agent_count = len(agents) if agents else agent_count_from_messages
    
    if agent_count == 0:
        print("❌ No agents found - cannot calculate time progression")
        return
    
    messages_per_agent_per_period = 9
    messages_per_time_period = agent_count * messages_per_agent_per_period
    
    print(f"📊 Time Calculation:")
    print(f"   - Agent count: {agent_count}")
    print(f"   - Messages per agent per time period: {messages_per_agent_per_period}")
    print(f"   - Messages per time period: {messages_per_time_period}")
    print(f"   - Total messages: {total_messages}")
    
    # Calculate expected time period
    time_period_number = total_messages // messages_per_time_period
    time_periods = ["morning", "afternoon", "evening"]
    expected_period_index = time_period_number % 3
    expected_period = time_periods[expected_period_index]
    expected_day = (time_period_number // 3) + 1
    
    print(f"📊 Expected Time:")
    print(f"   - Time period number: {time_period_number}")
    print(f"   - Expected day: {expected_day}")
    print(f"   - Expected period: {expected_period}")
    
    print(f"\n🎯 CRITICAL COMPARISON:")
    print(f"   - Current: Day {current_day}, {current_time_period}")
    print(f"   - Expected: Day {expected_day}, {expected_period}")
    
    # Check if this matches the user's reported issue
    if agent_count == 3 and total_messages == 28:
        print(f"\n🚨 EXACT USER SCENARIO DETECTED!")
        print(f"   - 3 agents ✓")
        print(f"   - 28 messages ✓")
        print(f"   - Expected: Day 1, Afternoon (messages 28+ should be afternoon)")
        print(f"   - Actual: Day {current_day}, {current_time_period}")
        
        if current_time_period == "morning":
            print(f"   - ❌ BUG CONFIRMED: Should be 'afternoon' but showing 'morning'")
        else:
            print(f"   - ✅ Time progression working correctly")
    
    print("\n🔍 STEP 6: Manually trigger time advancement function")
    time_advance_result = manually_trigger_time_advancement(token)
    if time_advance_result:
        print(f"📊 Time advancement result: {json.dumps(time_advance_result, indent=2)}")
    
    print("\n🔍 STEP 7: Check simulation state after manual trigger")
    sim_state_after = get_simulation_state(token)
    if sim_state_after:
        new_day = sim_state_after.get("current_day", 1)
        new_time_period = sim_state_after.get("current_time_period", "morning")
        
        print(f"📊 Simulation State After Manual Trigger:")
        print(f"   - Day: {new_day}")
        print(f"   - Time Period: {new_time_period}")
        
        if new_time_period != current_time_period or new_day != current_day:
            print(f"   - ✅ Time advancement occurred!")
            print(f"   - Changed from: Day {current_day}, {current_time_period}")
            print(f"   - Changed to: Day {new_day}, {new_time_period}")
        else:
            print(f"   - ❌ No time advancement occurred")
    
    print("\n🔍 STEP 8: Root cause analysis")
    
    # Check if the issue is:
    # 1. Backend calculation error
    # 2. Time advancement not being called
    # 3. Frontend not displaying updated state
    # 4. Race condition between conversation generation and time advancement
    
    print(f"\n📋 ROOT CAUSE ANALYSIS:")
    
    if agent_count == 3 and total_messages >= 28:
        expected_afternoon = total_messages >= 28
        actual_afternoon = current_time_period == "afternoon"
        
        if expected_afternoon and not actual_afternoon:
            print(f"   - ❌ BACKEND CALCULATION ERROR: Time should have advanced but didn't")
            print(f"   - Messages 1-27 should be 'morning', messages 28+ should be 'afternoon'")
            print(f"   - With {total_messages} messages, should be in 'afternoon'")
            
            # Check if manual trigger fixes it
            if sim_state_after and sim_state_after.get("current_time_period") == "afternoon":
                print(f"   - 🔧 ISSUE: Time advancement function not being called automatically")
                print(f"   - Manual trigger works, but automatic trigger during conversation generation fails")
            else:
                print(f"   - 🔧 ISSUE: Time advancement function itself has bugs")
        else:
            print(f"   - ✅ Backend calculation appears correct")
    
    print(f"\n📋 SUMMARY:")
    print(f"   - User scenario: {agent_count} agents, {total_messages} messages")
    print(f"   - Current time: Day {current_day}, {current_time_period}")
    print(f"   - Expected time: Day {expected_day}, {expected_period}")
    
    if agent_count == 3 and total_messages == 28 and current_time_period == "morning":
        print(f"   - 🚨 BUG CONFIRMED: Exact user issue reproduced")
        print(f"   - Root cause: Time advancement not working properly")
    elif agent_count == 3 and total_messages == 28 and current_time_period == "afternoon":
        print(f"   - ✅ Issue appears to be resolved")
    else:
        print(f"   - ℹ️ Different scenario than user reported")

if __name__ == "__main__":
    main()