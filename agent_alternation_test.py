#!/usr/bin/env python3
"""
AGENT ALTERNATION TEST
Testing the specific issue where the same agent sends multiple consecutive messages.
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

def authenticate():
    """Authenticate with the backend"""
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def test_agents_and_conversation():
    """Test agents list and conversation generation"""
    print("🔍 AGENT ALTERNATION TEST")
    print("="*60)
    
    # Authenticate
    token = authenticate()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get agents
    print("\n1. GETTING AGENTS...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents:")
            
            agent_names = []
            for i, agent in enumerate(agents, 1):
                name = agent.get('name', 'Unknown')
                agent_names.append(name)
                print(f"  [{i}] {name} (ID: {agent.get('id', 'Unknown')[:8]}...)")
            
            # Check for duplicates
            unique_names = set(agent_names)
            if len(agent_names) != len(unique_names):
                print(f"🚨 DUPLICATE AGENTS DETECTED!")
                for name in unique_names:
                    count = agent_names.count(name)
                    if count > 1:
                        print(f"  - '{name}' appears {count} times")
                return False
            else:
                print(f"✅ No duplicate agents found")
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return False
    
    # 2. Generate conversation with timeout
    print(f"\n2. GENERATING CONVERSATION...")
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=45)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conversation = data.get("conversation", {})
            messages = conversation.get("messages", [])
            
            print(f"✅ Generated {len(messages)} messages:")
            
            # Analyze message sequence
            agent_sequence = []
            agent_counts = {}
            
            for i, msg in enumerate(messages, 1):
                agent_name = msg.get("agent_name", "Unknown")
                agent_sequence.append(agent_name)
                agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
                
                print(f"  [{i}] {agent_name}: {msg.get('message', '')[:60]}...")
            
            print(f"\n📊 ANALYSIS:")
            print(f"Message sequence: {' → '.join(agent_sequence)}")
            
            print(f"\nAgent message counts:")
            issues_found = False
            for agent_name, count in agent_counts.items():
                status = "✅" if count == 1 else "🚨"
                print(f"  {status} {agent_name}: {count} message(s)")
                if count > 1:
                    issues_found = True
            
            if issues_found:
                print(f"\n🚨 ISSUE CONFIRMED: Same agent sending multiple messages!")
                
                # Check for consecutive messages
                consecutive_issues = []
                for i in range(1, len(messages)):
                    if messages[i].get("agent_name") == messages[i-1].get("agent_name"):
                        consecutive_issues.append((i+1, messages[i].get("agent_name")))
                
                if consecutive_issues:
                    print(f"\n🚨 CONSECUTIVE MESSAGE ISSUES:")
                    for pos, agent_name in consecutive_issues:
                        print(f"  - Position {pos}: {agent_name} sent consecutive messages")
                
                return False
            else:
                print(f"\n✅ PERFECT: Each agent sent exactly 1 message")
                return True
                
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Conversation generation timed out (45 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return False

if __name__ == "__main__":
    success = test_agents_and_conversation()
    if success:
        print(f"\n✅ TEST PASSED: No agent alternation issues detected")
    else:
        print(f"\n❌ TEST FAILED: Agent alternation issues found")