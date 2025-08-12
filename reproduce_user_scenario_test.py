#!/usr/bin/env python3
"""
REPRODUCE EXACT USER SCENARIO TEST
Create exactly 3 agents and 28 messages to reproduce the reported bug:
- User has exactly 3 agents and 28 messages
- System shows "Day 1, Morning" instead of "Day 1, Afternoon"
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

print(f"🧪 REPRODUCE EXACT USER SCENARIO TEST")
print(f"Creating 3 agents and 28 messages to test time progression")
print("="*80)

def login_as_guest():
    """Login as guest user to get auth token"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Guest login successful - User ID: {user_id}")
            return token, user_id
        else:
            print(f"❌ Guest login failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Guest login error: {e}")
        return None, None

def clear_user_data(token):
    """Clear all existing agents and conversations for clean test"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get and delete all agents
    try:
        agents_response = requests.get(f"{API_URL}/agents", headers=headers)
        if agents_response.status_code == 200:
            agents = agents_response.json()
            for agent in agents:
                agent_id = agent.get("id")
                if agent_id:
                    delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted agent: {agent.get('name', 'Unknown')}")
    except Exception as e:
        print(f"⚠️ Error clearing agents: {e}")
    
    # Reset simulation state
    try:
        reset_response = requests.post(f"{API_URL}/simulation/reset", headers=headers)
        if reset_response.status_code == 200:
            print(f"✅ Reset simulation state")
    except Exception as e:
        print(f"⚠️ Error resetting simulation: {e}")

def create_test_agent(token, name, archetype, expertise):
    """Create a test agent"""
    headers = {"Authorization": f"Bearer {token}"}
    agent_data = {
        "name": name,
        "archetype": archetype,
        "personality": {
            "extroversion": 7,
            "optimism": 6,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": f"Contribute expertise in {expertise}",
        "expertise": expertise,
        "background": f"Expert in {expertise} with years of experience",
        "memory_summary": "",
        "avatar_prompt": "",
        "avatar_url": ""
    }
    
    try:
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        if response.status_code == 200:
            agent = response.json()
            print(f"✅ Created agent: {name}")
            return agent.get("id")
        else:
            print(f"❌ Failed to create agent {name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating agent {name}: {e}")
        return None

def start_simulation(token):
    """Start the simulation"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if response.status_code == 200:
            print(f"✅ Started simulation")
            return True
        else:
            print(f"❌ Failed to start simulation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False

def generate_conversation(token):
    """Generate a single conversation"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return None

def get_simulation_state(token):
    """Get current simulation state"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
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
    """Get all conversations"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return None

def count_total_messages(conversations):
    """Count total messages across all conversations"""
    total_messages = 0
    agent_names = set()
    
    for conv in conversations:
        messages = conv.get("messages", [])
        total_messages += len(messages)
        
        for msg in messages:
            agent_name = msg.get("agent_name")
            if agent_name and agent_name != "Observer (You)":
                agent_names.add(agent_name)
    
    return total_messages, len(agent_names), list(agent_names)

def main():
    print("\n🔍 STEP 1: Login and clear existing data")
    token, user_id = login_as_guest()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Clear existing data for clean test
    clear_user_data(token)
    
    print("\n🔍 STEP 2: Create exactly 3 agents")
    agent_ids = []
    
    # Create 3 specific agents
    agents_to_create = [
        ("Dr. Alice Quantum", "scientist", "Quantum Physics"),
        ("Prof. Bob Neural", "researcher", "Neural Networks"), 
        ("Dr. Carol Crypto", "scientist", "Cryptography")
    ]
    
    for name, archetype, expertise in agents_to_create:
        agent_id = create_test_agent(token, name, archetype, expertise)
        if agent_id:
            agent_ids.append(agent_id)
    
    if len(agent_ids) != 3:
        print(f"❌ Failed to create exactly 3 agents. Created: {len(agent_ids)}")
        return
    
    print(f"✅ Successfully created 3 agents")
    
    print("\n🔍 STEP 3: Start simulation")
    if not start_simulation(token):
        print("❌ Cannot proceed without starting simulation")
        return
    
    print("\n🔍 STEP 4: Generate conversations to reach exactly 28 messages")
    
    target_messages = 28
    current_messages = 0
    conversation_count = 0
    
    while current_messages < target_messages:
        print(f"\n📝 Generating conversation {conversation_count + 1}...")
        
        # Generate a conversation
        conversation = generate_conversation(token)
        if not conversation:
            print("❌ Failed to generate conversation")
            break
        
        conversation_count += 1
        
        # Check current message count
        conversations = get_all_conversations(token)
        if conversations:
            current_messages, agent_count, agent_names = count_total_messages(conversations)
            print(f"   - Total messages now: {current_messages}")
            print(f"   - Agent count: {agent_count}")
            
            # Stop if we've reached or exceeded target
            if current_messages >= target_messages:
                break
        
        # Safety limit
        if conversation_count > 20:
            print("⚠️ Safety limit reached - stopping conversation generation")
            break
        
        # Small delay between conversations
        time.sleep(1)
    
    print(f"\n📊 Final conversation generation results:")
    print(f"   - Conversations generated: {conversation_count}")
    print(f"   - Total messages: {current_messages}")
    
    print("\n🔍 STEP 5: Analyze final state")
    
    # Get final simulation state
    sim_state = get_simulation_state(token)
    if sim_state:
        current_day = sim_state.get("current_day", 1)
        current_time_period = sim_state.get("current_time_period", "morning")
        
        print(f"📊 Final Simulation State:")
        print(f"   - Day: {current_day}")
        print(f"   - Time Period: {current_time_period}")
        print(f"   - Total messages: {current_messages}")
        print(f"   - Agent count: {agent_count}")
    
    print("\n🔍 STEP 6: Verify if bug is reproduced")
    
    # Check if we have the exact user scenario
    if agent_count == 3 and current_messages == 28:
        print(f"\n🎯 EXACT USER SCENARIO ACHIEVED!")
        print(f"   - 3 agents ✓")
        print(f"   - 28 messages ✓")
        
        # Calculate expected time period
        messages_per_time_period = 3 * 9  # 3 agents × 9 messages per time period = 27
        
        print(f"\n📊 Time Progression Analysis:")
        print(f"   - Messages per time period: {messages_per_time_period}")
        print(f"   - Messages 1-27 should be: Day 1, Morning")
        print(f"   - Messages 28+ should be: Day 1, Afternoon")
        print(f"   - Current state: Day {current_day}, {current_time_period}")
        
        if current_messages >= 28 and current_time_period == "morning":
            print(f"\n🚨 BUG CONFIRMED!")
            print(f"   - With 28 messages, should be 'Day 1, Afternoon'")
            print(f"   - But system shows 'Day {current_day}, {current_time_period}'")
            print(f"   - This matches the exact user report!")
        elif current_messages >= 28 and current_time_period == "afternoon":
            print(f"\n✅ Time progression working correctly")
            print(f"   - With 28 messages, correctly shows 'Day 1, Afternoon'")
        else:
            print(f"\n⚠️ Unexpected state")
    else:
        print(f"\n⚠️ Did not achieve exact user scenario")
        print(f"   - Target: 3 agents, 28 messages")
        print(f"   - Actual: {agent_count} agents, {current_messages} messages")
    
    print("\n📋 FINAL SUMMARY:")
    print(f"   - Agents created: {len(agent_ids)}")
    print(f"   - Conversations generated: {conversation_count}")
    print(f"   - Total messages: {current_messages}")
    print(f"   - Current time: Day {current_day}, {current_time_period}")
    
    if agent_count == 3 and current_messages >= 28 and current_time_period == "morning":
        print(f"   - 🚨 USER BUG SUCCESSFULLY REPRODUCED")
        print(f"   - Issue: Time progression not advancing from Morning to Afternoon")
    else:
        print(f"   - ℹ️ Bug not reproduced or already fixed")

if __name__ == "__main__":
    main()