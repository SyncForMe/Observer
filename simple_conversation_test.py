#!/usr/bin/env python3
"""
Simple focused test for conversation generation debugging
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

print(f"Testing API: {API_URL}")

def test_auth_and_conversation():
    """Test authentication and conversation generation"""
    
    # 1. Authenticate
    print("\n1. 🔐 Testing Authentication...")
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Auth successful. User ID: {user_id}")
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Check current conversations
    print("\n2. 📊 Checking current conversation state...")
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if response.status_code == 200:
            conversations = response.json()
            total_messages = sum(len(conv.get("messages", [])) for conv in conversations)
            print(f"✅ Current state: {len(conversations)} conversations, {total_messages} total messages")
            
            # Analyze message patterns
            if conversations:
                print("\n📋 Recent conversation analysis:")
                recent_conv = conversations[-1] if conversations else None
                if recent_conv:
                    messages = recent_conv.get("messages", [])
                    print(f"  - Last conversation: {len(messages)} messages")
                    print(f"  - Time period: {recent_conv.get('time_period', 'N/A')}")
                    
                    # Check for consecutive messages
                    if len(messages) >= 3:
                        last_3_agents = [msg.get("agent_name") for msg in messages[-3:]]
                        print(f"  - Last 3 message agents: {last_3_agents}")
                        
                        # Check for consecutive same agent
                        consecutive_found = False
                        for i in range(len(messages) - 1):
                            if messages[i].get("agent_name") == messages[i+1].get("agent_name"):
                                consecutive_found = True
                                print(f"  ⚠️ Consecutive messages found: {messages[i].get('agent_name')}")
                                break
                        
                        if not consecutive_found:
                            print(f"  ✅ No consecutive messages from same agent")
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return
    
    # 3. Test single conversation generation
    print("\n3. 🧪 Testing single conversation generation...")
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conversation = data.get("conversation", {})
            messages = conversation.get("messages", [])
            
            print(f"✅ Generated conversation with {len(messages)} messages")
            print(f"  - Conversation ID: {conversation.get('id')}")
            print(f"  - Time period: {conversation.get('time_period')}")
            
            # Analyze agent distribution
            agent_counts = {}
            for msg in messages:
                agent_name = msg.get("agent_name", "Unknown")
                agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
            
            print(f"  - Agent message distribution:")
            for agent, count in agent_counts.items():
                print(f"    • {agent}: {count} messages")
            
            # Check for consecutive messages issue
            consecutive_issues = []
            for i in range(len(messages) - 1):
                if messages[i].get("agent_name") == messages[i+1].get("agent_name"):
                    consecutive_issues.append(f"{messages[i].get('agent_name')} at positions {i}-{i+1}")
            
            if consecutive_issues:
                print(f"  ⚠️ CONSECUTIVE MESSAGE ISSUES:")
                for issue in consecutive_issues:
                    print(f"    • {issue}")
            else:
                print(f"  ✅ No consecutive message issues")
                
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
    
    # 4. Check simulation state
    print("\n4. ⚙️ Checking simulation state...")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
        if response.status_code == 200:
            state = response.json()
            print(f"✅ Simulation state:")
            print(f"  - Day: {state.get('current_day')}")
            print(f"  - Time period: {state.get('current_time_period')}")
            print(f"  - Active: {state.get('is_active')}")
        else:
            print(f"❌ Failed to get simulation state: {response.status_code}")
    except Exception as e:
        print(f"❌ Simulation state error: {e}")

if __name__ == "__main__":
    test_auth_and_conversation()