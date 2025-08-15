#!/usr/bin/env python3
"""
Minimal conversation test with fresh agents to verify alternation fix
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

def create_minimal_agents(token):
    """Create 3 simple agents for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    
    agents_data = [
        {
            "name": "Agent Alpha",
            "archetype": "scientist",
            "goal": "Test conversation",
            "expertise": "Testing",
            "background": "Test agent",
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 5,
                "cooperativeness": 5,
                "energy": 5
            }
        },
        {
            "name": "Agent Beta",
            "archetype": "leader",
            "goal": "Test conversation",
            "expertise": "Testing",
            "background": "Test agent",
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 5,
                "cooperativeness": 5,
                "energy": 5
            }
        },
        {
            "name": "Agent Gamma",
            "archetype": "researcher",
            "goal": "Test conversation",
            "expertise": "Testing",
            "background": "Test agent",
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 5,
                "cooperativeness": 5,
                "energy": 5
            }
        }
    ]
    
    created_agents = []
    
    print("Creating minimal test agents...")
    for i, agent_data in enumerate(agents_data):
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                agent_response = response.json()
                agent_id = agent_response.get("agent_id")
                created_agents.append(agent_id)
                print(f"✅ Created {agent_data['name']} (ID: {agent_id})")
            else:
                print(f"❌ Failed to create {agent_data['name']}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error creating {agent_data['name']}: {e}")
            return None
    
    return created_agents

def cleanup_agents(token, agent_ids):
    """Clean up created agents"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\nCleaning up test agents...")
    for agent_id in agent_ids:
        try:
            response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
            if response.status_code == 200:
                print(f"✅ Deleted agent {agent_id}")
            else:
                print(f"❌ Failed to delete agent {agent_id}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error deleting agent {agent_id}: {e}")

def test_minimal_conversation():
    """Test conversation generation with minimal setup"""
    print("🔍 MINIMAL CONVERSATION ALTERNATION TEST")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Clear existing agents first
    print("\n1. CLEARING EXISTING AGENTS...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            existing_agents = response.json()
            print(f"Found {len(existing_agents)} existing agents")
            
            # Delete all existing agents
            for agent in existing_agents:
                agent_id = agent.get("id")
                if agent_id:
                    delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted existing agent: {agent.get('name', 'Unknown')}")
                    else:
                        print(f"❌ Failed to delete agent: {agent.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to get existing agents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error clearing agents: {e}")
    
    # Create minimal test agents
    print("\n2. CREATING MINIMAL TEST AGENTS...")
    created_agent_ids = create_minimal_agents(token)
    if not created_agent_ids:
        print("❌ Failed to create test agents")
        return False
    
    try:
        # Test conversation generation
        print(f"\n3. TESTING CONVERSATION GENERATION...")
        print(f"   Expected: 3 messages (1 per agent)")
        
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/conversation/generate", 
            headers=headers, 
            timeout=45  # 45 second timeout
        )
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   Duration: {duration:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ Conversation generation successful!")
            
            conversation_data = response.json()
            conversation = conversation_data.get("conversation", {})
            messages = conversation.get("messages", [])
            
            print(f"\n4. ANALYZING RESULTS...")
            print(f"   Total messages: {len(messages)}")
            print(f"   Expected messages: 3")
            
            # Show all messages
            agent_message_count = {}
            message_sequence = []
            
            print(f"\n   MESSAGES:")
            for i, message in enumerate(messages):
                agent_name = message.get("agent_name", "Unknown")
                agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
                message_sequence.append(agent_name)
                
                msg_preview = message.get('message', '')[:60] + "..." if len(message.get('message', '')) > 60 else message.get('message', '')
                print(f"   [{i+1}] {agent_name}: {msg_preview}")
            
            # Check alternation
            print(f"\n   ALTERNATION ANALYSIS:")
            
            # 1. Check message count per agent
            all_agents_one_message = True
            print(f"   Agent message counts:")
            for agent_name, count in agent_message_count.items():
                status = "✅" if count == 1 else "❌"
                print(f"     {status} {agent_name}: {count} message(s)")
                if count != 1:
                    all_agents_one_message = False
            
            # 2. Check for consecutive messages
            consecutive_found = False
            for i in range(1, len(message_sequence)):
                if message_sequence[i] == message_sequence[i-1]:
                    print(f"   ❌ Consecutive messages from {message_sequence[i]} at positions {i} and {i+1}")
                    consecutive_found = True
            
            if not consecutive_found:
                print("   ✅ No consecutive messages from the same agent")
            
            # 3. Check total count
            total_correct = len(messages) == 3
            if total_correct:
                print("   ✅ Total message count is correct (3)")
            else:
                print(f"   ❌ Total message count incorrect: got {len(messages)}, expected 3")
            
            # Final assessment
            print(f"\n5. FINAL ASSESSMENT:")
            
            if all_agents_one_message and not consecutive_found and total_correct:
                print("   🎉 AGENT ALTERNATION FIX: WORKING PERFECTLY!")
                print("   ✅ Each agent sends exactly 1 message")
                print("   ✅ No consecutive messages from same agent")
                print("   ✅ Total message count is correct")
                print("   ✅ Agent alternation issue has been RESOLVED!")
                return True
            else:
                print("   ❌ AGENT ALTERNATION FIX: ISSUES DETECTED!")
                if not all_agents_one_message:
                    print("   ❌ Some agents sent multiple/no messages")
                if consecutive_found:
                    print("   ❌ Found consecutive messages from same agent")
                if not total_correct:
                    print("   ❌ Total message count is incorrect")
                print("   ❌ Agent alternation issue is NOT fully resolved")
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
        print("❌ Conversation generation timed out (45 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error during conversation generation: {e}")
        return False
    finally:
        # Always cleanup
        if created_agent_ids:
            cleanup_agents(token, created_agent_ids)

def main():
    """Main test execution"""
    success = test_minimal_conversation()
    
    print("\n" + "="*80)
    if success:
        print("🎉 AGENT ALTERNATION FIX VERIFICATION: PASSED")
        print("✅ The agent alternation issue has been RESOLVED!")
        print("✅ Each agent sends exactly 1 message per conversation round")
        print("✅ Agents alternate properly without consecutive messages")
        print("✅ Total messages equal the number of agents")
    else:
        print("💥 AGENT ALTERNATION FIX VERIFICATION: FAILED")
        print("❌ The agent alternation issue may NOT be fully resolved")
        print("❌ Further investigation is needed")
    print("="*80)
    
    return success

if __name__ == "__main__":
    main()