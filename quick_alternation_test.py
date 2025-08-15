#!/usr/bin/env python3
"""
QUICK AGENT ALTERNATION FIX VERIFICATION TEST
Testing the conversation generation endpoint to verify agent alternation fix.
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

def test_agent_alternation():
    """Test the agent alternation fix"""
    print("🔍 AGENT ALTERNATION FIX VERIFICATION TEST")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get existing agents
    print("\n1. GETTING EXISTING AGENTS...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} existing agents")
            
            if len(agents) == 0:
                print("❌ No agents found - cannot test conversation generation")
                return False
                
            # Show agent names
            for i, agent in enumerate(agents[:5], 1):  # Show first 5
                print(f"  [{i}] {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
                
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return False
    
    # Generate conversation to test alternation
    print(f"\n2. GENERATING CONVERSATION WITH {len(agents)} AGENTS...")
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            conversation_data = response.json()
            conversation = conversation_data.get("conversation", {})
            messages = conversation.get("messages", [])
            
            print(f"✅ Conversation generated in {end_time - start_time:.2f} seconds")
            print(f"📊 Generated {len(messages)} messages")
            print(f"📊 Expected {len(agents)} messages (1 per agent)")
            
            # Analyze agent alternation
            print(f"\n3. ANALYZING AGENT ALTERNATION...")
            
            # Count messages per agent
            agent_message_count = {}
            message_sequence = []
            
            for i, message in enumerate(messages):
                agent_name = message.get("agent_name", "Unknown")
                agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
                message_sequence.append(agent_name)
                print(f"  Message {i+1}: {agent_name} - {message.get('message', '')[:60]}...")
            
            print(f"\n📊 MESSAGE COUNT PER AGENT:")
            all_agents_have_one_message = True
            for agent_name, count in agent_message_count.items():
                status = "✅" if count == 1 else "❌"
                print(f"  {status} {agent_name}: {count} message(s)")
                if count != 1:
                    all_agents_have_one_message = False
            
            # Check for consecutive messages from same agent
            print(f"\n📊 CHECKING FOR CONSECUTIVE MESSAGES:")
            consecutive_found = False
            for i in range(1, len(message_sequence)):
                if message_sequence[i] == message_sequence[i-1]:
                    print(f"  ❌ Consecutive messages from {message_sequence[i]} at positions {i} and {i+1}")
                    consecutive_found = True
            
            if not consecutive_found:
                print("  ✅ No consecutive messages from the same agent")
            
            # Check total message count
            print(f"\n📊 TOTAL MESSAGE COUNT:")
            expected_total = len(agents)
            actual_total = len(messages)
            
            if actual_total == expected_total:
                print(f"  ✅ Total messages ({actual_total}) equals agent count ({expected_total})")
            else:
                print(f"  ❌ Expected {expected_total} messages, got {actual_total}")
            
            # Final assessment
            print(f"\n🎯 AGENT ALTERNATION FIX ASSESSMENT:")
            
            if all_agents_have_one_message and not consecutive_found and actual_total == expected_total:
                print("✅ AGENT ALTERNATION FIX SUCCESSFUL!")
                print("✅ Each agent sends exactly 1 message per conversation round")
                print("✅ No consecutive messages from the same agent")
                print("✅ Total message count equals agent count")
                print("✅ The agent alternation issue has been RESOLVED")
                return True
            else:
                print("❌ AGENT ALTERNATION FIX FAILED!")
                if not all_agents_have_one_message:
                    print("❌ Some agents sent multiple messages or no messages")
                if consecutive_found:
                    print("❌ Found consecutive messages from the same agent")
                if actual_total != expected_total:
                    print("❌ Total message count doesn't match agent count")
                print("❌ The agent alternation issue is NOT resolved")
                return False
                
        else:
            print(f"❌ Conversation generation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Conversation generation timed out (30 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return False

def main():
    """Main test execution"""
    success = test_agent_alternation()
    
    print("\n" + "="*80)
    if success:
        print("🎉 AGENT ALTERNATION FIX VERIFICATION: PASSED")
        print("The conversation generation endpoint is working correctly!")
    else:
        print("💥 AGENT ALTERNATION FIX VERIFICATION: FAILED")
        print("The conversation generation endpoint needs further investigation!")
    print("="*80)
    
    return success

if __name__ == "__main__":
    main()