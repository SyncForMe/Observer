#!/usr/bin/env python3
"""
Detailed Conversation Generation Analysis
"""

import requests
import json
import time

API_URL = "http://localhost:8001/api"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def analyze_conversations():
    """Analyze existing conversations"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 ANALYZING EXISTING CONVERSATIONS")
    print("="*50)
    
    # Get conversations
    response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
    if response.status_code != 200:
        print("❌ Failed to get conversations")
        return
    
    conversations = response.json()
    print(f"📊 Total conversations: {len(conversations)}")
    
    if conversations:
        # Analyze first conversation
        conv = conversations[0]
        print(f"\n📋 Sample Conversation Analysis:")
        print(f"   ID: {conv.get('id')}")
        print(f"   Scenario: {conv.get('scenario_name', 'Unknown')}")
        print(f"   Messages: {len(conv.get('messages', []))}")
        print(f"   User ID: {conv.get('user_id')}")
        print(f"   Created: {conv.get('created_at')}")
        
        # Analyze messages
        messages = conv.get('messages', [])
        if messages:
            print(f"\n💬 Message Analysis:")
            for i, msg in enumerate(messages[:3]):  # First 3 messages
                agent_name = msg.get('agent_name', 'Unknown')
                message_text = msg.get('message', '')[:100] + "..."
                print(f"   Msg {i+1}: {agent_name}")
                print(f"           {message_text}")
    
    # Get agents
    print(f"\n🤖 AGENT ANALYSIS")
    print("="*30)
    
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code == 200:
        agents = response.json()
        print(f"📊 Total agents: {len(agents)}")
        
        for i, agent in enumerate(agents):
            name = agent.get('name', 'Unknown')
            archetype = agent.get('archetype', 'Unknown')
            user_id = agent.get('user_id', 'Unknown')
            print(f"   Agent {i+1}: {name} ({archetype}) - User: {user_id}")
    
    # Get simulation state
    print(f"\n🎮 SIMULATION STATE ANALYSIS")
    print("="*35)
    
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    if response.status_code == 200:
        state = response.json()
        print(f"   Active: {state.get('is_active', False)}")
        print(f"   Scenario: {state.get('scenario', 'Unknown')}")
        print(f"   Scenario Name: {state.get('scenario_name', 'Unknown')}")
        print(f"   User ID: {state.get('user_id', 'Unknown')}")
        print(f"   Current Day: {state.get('current_day', 'Unknown')}")
        print(f"   Time Period: {state.get('current_time_period', 'Unknown')}")
    
    # Test conversation generation with longer timeout
    print(f"\n⚡ CONVERSATION GENERATION TEST")
    print("="*40)
    
    print("🔄 Attempting conversation generation (60s timeout)...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/conversation/generate", 
            headers=headers, 
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Generation took {duration:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conv_id = data.get('id')
            messages = data.get('messages', [])
            print(f"✅ SUCCESS!")
            print(f"   Generated ID: {conv_id}")
            print(f"   Generated Messages: {len(messages)}")
            
            if messages:
                print(f"\n💬 Generated Messages:")
                for i, msg in enumerate(messages[:2]):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_text = msg.get('message', '')[:150] + "..."
                    print(f"   Msg {i+1}: {agent_name}")
                    print(f"           {message_text}")
        else:
            print(f"❌ FAILED!")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
    
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT after 60 seconds")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    analyze_conversations()