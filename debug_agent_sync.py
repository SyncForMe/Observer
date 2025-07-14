#!/usr/bin/env python3
"""
Debug Agent Synchronization Issue
Investigates why conversation generation is not using newly created agents.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "dino@cytonic.com"
TEST_PASSWORD = "Observerinho8"

def authenticate():
    """Authenticate and return token"""
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def debug_conversation_generation():
    """Debug conversation generation to see which agents are being used"""
    print("🔍 Debugging Conversation Generation Agent Selection...")
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 1: Get current agents
    print("\n📋 Step 1: Getting current agents...")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        current_agents = agents_response.json()
        print(f"Current agents ({len(current_agents)}):")
        for agent in current_agents:
            print(f"  - {agent['name']} (ID: {agent['id']}, Archetype: {agent['archetype']})")
    else:
        print(f"❌ Failed to get agents: {agents_response.status_code}")
        return
    
    # Step 2: Create a new agent with a unique name
    print("\n🤖 Step 2: Creating a new agent with unique name...")
    unique_name = f"Debug Agent {int(time.time())}"
    agent_data = {
        "name": unique_name,
        "archetype": "scientist",
        "goal": "Debug conversation generation",
        "expertise": "Debugging and Testing",
        "background": "Created specifically to debug conversation generation",
        "personality": {
            "extroversion": 8, "optimism": 9, "curiosity": 10,
            "cooperativeness": 9, "energy": 8
        }
    }
    
    create_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    if create_response.status_code == 200:
        new_agent_id = create_response.json()["id"]
        print(f"✅ Created debug agent: {unique_name} (ID: {new_agent_id})")
    else:
        print(f"❌ Failed to create debug agent: {create_response.status_code}")
        return
    
    # Step 3: Verify the new agent appears in GET /api/agents
    print("\n📋 Step 3: Verifying new agent appears in agent list...")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        updated_agents = agents_response.json()
        agent_names = [agent['name'] for agent in updated_agents]
        
        if unique_name in agent_names:
            print(f"✅ New agent found in agent list")
            print(f"Updated agents ({len(updated_agents)}):")
            for agent in updated_agents:
                marker = " 🆕" if agent['name'] == unique_name else ""
                print(f"  - {agent['name']} (ID: {agent['id']}, Archetype: {agent['archetype']}){marker}")
        else:
            print(f"❌ New agent NOT found in agent list")
            return
    else:
        print(f"❌ Failed to get updated agents: {agents_response.status_code}")
        return
    
    # Step 4: Clear all conversations to start fresh
    print("\n🧹 Step 4: Clearing conversations...")
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code == 200:
        print("✅ Conversations cleared")
    else:
        print(f"⚠️ Failed to clear conversations: {start_response.status_code}")
    
    # Step 5: Set scenario
    print("\n🎬 Step 5: Setting scenario...")
    scenario_data = {
        "scenario": f"Debug meeting to test if {unique_name} participates in conversations",
        "scenario_name": "Debug Conversation Test"
    }
    
    scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
    if scenario_response.status_code == 200:
        print("✅ Scenario set")
    else:
        print(f"❌ Failed to set scenario: {scenario_response.status_code}")
        return
    
    # Step 6: Generate conversation
    print("\n💬 Step 6: Generating conversation...")
    conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    
    if conversation_response.status_code == 200:
        conversation_data = conversation_response.json()
        
        if "messages" in conversation_data:
            messages = conversation_data["messages"]
            participating_agents = []
            
            print(f"Generated conversation with {len(messages)} messages:")
            for i, message in enumerate(messages, 1):
                agent_name = message.get("agent_name", "Unknown")
                participating_agents.append(agent_name)
                marker = " 🆕" if agent_name == unique_name else ""
                print(f"  {i}. {agent_name}{marker}: {message.get('message', '')[:100]}...")
            
            # Check if our new agent participated
            if unique_name in participating_agents:
                print(f"\n✅ SUCCESS: New agent '{unique_name}' participated in conversation!")
            else:
                print(f"\n❌ ISSUE: New agent '{unique_name}' did NOT participate in conversation")
                print(f"Participating agents: {set(participating_agents)}")
                
                # Let's check what the conversation generation endpoint is actually using
                print("\n🔍 Investigating conversation generation logic...")
                
                # Check simulation state
                state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
                if state_response.status_code == 200:
                    state_data = state_response.json()
                    print(f"Simulation state: {json.dumps(state_data, indent=2)}")
                else:
                    print(f"Failed to get simulation state: {state_response.status_code}")
        else:
            print("❌ Conversation response missing messages")
    else:
        print(f"❌ Conversation generation failed: {conversation_response.status_code}")
        print(f"Response: {conversation_response.text}")
    
    # Step 7: Clean up
    print(f"\n🧹 Step 7: Cleaning up debug agent...")
    delete_response = requests.delete(f"{API_URL}/agents/{new_agent_id}", headers=headers)
    if delete_response.status_code == 200:
        print(f"✅ Cleaned up debug agent")
    else:
        print(f"⚠️ Failed to clean up debug agent: {delete_response.status_code}")

def test_conversation_endpoint_directly():
    """Test the conversation generation endpoint directly to see what it's doing"""
    print("\n🔬 Testing Conversation Endpoint Directly...")
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get agents first
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"Available agents for conversation: {len(agents)}")
        for agent in agents:
            print(f"  - {agent['name']} (User ID: {agent.get('user_id', 'MISSING')})")
    
    # Check if there are enough agents
    if len(agents) < 2:
        print("❌ Need at least 2 agents for conversation generation")
        return
    
    # Try to generate conversation
    print("\nGenerating conversation...")
    conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    
    if conversation_response.status_code == 200:
        conversation_data = conversation_response.json()
        print("✅ Conversation generated successfully")
        
        if "messages" in conversation_data:
            messages = conversation_data["messages"]
            agent_names = [msg.get("agent_name") for msg in messages]
            print(f"Agents that participated: {set(agent_names)}")
        
        # Check if conversation was saved with correct user_id
        if "user_id" in conversation_data:
            print(f"Conversation saved with user_id: {conversation_data['user_id']}")
        else:
            print("⚠️ Conversation missing user_id")
    else:
        print(f"❌ Conversation generation failed: {conversation_response.status_code}")
        print(f"Error: {conversation_response.text}")

def main():
    """Main debug function"""
    print("🚀 Starting Agent Synchronization Debug...")
    print(f"API URL: {API_URL}")
    
    debug_conversation_generation()
    test_conversation_endpoint_directly()

if __name__ == "__main__":
    main()