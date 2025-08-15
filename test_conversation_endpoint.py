#!/usr/bin/env python3
"""
Direct test of conversation generation endpoint with detailed logging
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

def test_conversation_generation():
    """Test conversation generation with detailed analysis"""
    print("🔍 CONVERSATION GENERATION ENDPOINT TEST")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get agents first
    print("\n1. CHECKING AGENTS...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            
            # Show first few agents
            for i, agent in enumerate(agents[:3], 1):
                print(f"  [{i}] {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
            
            if len(agents) > 3:
                print(f"  ... and {len(agents) - 3} more agents")
                
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return False
    
    # Test conversation generation with extended timeout
    print(f"\n2. TESTING CONVERSATION GENERATION...")
    print(f"   Using timeout: 60 seconds")
    print(f"   Expected: {len(agents)} messages (1 per agent)")
    
    try:
        start_time = time.time()
        print(f"   Starting at: {time.strftime('%H:%M:%S')}")
        
        response = requests.post(
            f"{API_URL}/conversation/generate", 
            headers=headers, 
            timeout=60  # Extended timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   Completed at: {time.strftime('%H:%M:%S')}")
        print(f"   Duration: {duration:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ Conversation generation successful!")
            
            try:
                conversation_data = response.json()
                conversation = conversation_data.get("conversation", {})
                messages = conversation.get("messages", [])
                
                print(f"\n3. ANALYZING CONVERSATION RESULTS...")
                print(f"   Total messages: {len(messages)}")
                print(f"   Expected messages: {len(agents)}")
                
                # Analyze agent alternation
                agent_message_count = {}
                message_sequence = []
                
                print(f"\n   MESSAGE BREAKDOWN:")
                for i, message in enumerate(messages):
                    agent_name = message.get("agent_name", "Unknown")
                    agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
                    message_sequence.append(agent_name)
                    
                    # Show first few characters of message
                    msg_preview = message.get('message', '')[:50] + "..." if len(message.get('message', '')) > 50 else message.get('message', '')
                    print(f"   [{i+1}] {agent_name}: {msg_preview}")
                
                print(f"\n   AGENT MESSAGE COUNTS:")
                all_agents_one_message = True
                for agent_name, count in agent_message_count.items():
                    status = "✅" if count == 1 else "❌"
                    print(f"   {status} {agent_name}: {count} message(s)")
                    if count != 1:
                        all_agents_one_message = False
                
                # Check for consecutive messages
                print(f"\n   CONSECUTIVE MESSAGE CHECK:")
                consecutive_found = False
                for i in range(1, len(message_sequence)):
                    if message_sequence[i] == message_sequence[i-1]:
                        print(f"   ❌ Consecutive messages from {message_sequence[i]} at positions {i} and {i+1}")
                        consecutive_found = True
                
                if not consecutive_found:
                    print("   ✅ No consecutive messages from the same agent")
                
                # Final assessment
                print(f"\n4. AGENT ALTERNATION ASSESSMENT:")
                
                total_correct = len(messages) == len(agents)
                
                if all_agents_one_message and not consecutive_found and total_correct:
                    print("   ✅ AGENT ALTERNATION FIX: WORKING CORRECTLY!")
                    print("   ✅ Each agent sends exactly 1 message")
                    print("   ✅ No consecutive messages from same agent")
                    print("   ✅ Total message count matches agent count")
                    return True
                else:
                    print("   ❌ AGENT ALTERNATION FIX: ISSUES FOUND!")
                    if not all_agents_one_message:
                        print("   ❌ Some agents sent multiple/no messages")
                    if consecutive_found:
                        print("   ❌ Found consecutive messages from same agent")
                    if not total_correct:
                        print(f"   ❌ Message count mismatch: got {len(messages)}, expected {len(agents)}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"Response text: {response.text[:500]}...")
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
        print("❌ Conversation generation timed out (60 seconds)")
        print("   This suggests the endpoint is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error during conversation generation: {e}")
        return False

def main():
    """Main test execution"""
    success = test_conversation_generation()
    
    print("\n" + "="*80)
    if success:
        print("🎉 AGENT ALTERNATION FIX VERIFICATION: PASSED")
        print("✅ The conversation generation endpoint is working correctly!")
        print("✅ Agent alternation issue has been RESOLVED!")
    else:
        print("💥 AGENT ALTERNATION FIX VERIFICATION: FAILED")
        print("❌ The conversation generation endpoint has issues!")
        print("❌ Agent alternation issue may NOT be resolved!")
    print("="*80)
    
    return success

if __name__ == "__main__":
    main()