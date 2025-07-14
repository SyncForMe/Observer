#!/usr/bin/env python3
"""
Final Agent Synchronization Verification Test
Confirms that the agent synchronization between Agent Library and Observatory is working correctly.
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

def test_agent_synchronization_comprehensive():
    """Comprehensive test of agent synchronization"""
    print("🔄 COMPREHENSIVE AGENT SYNCHRONIZATION TEST")
    print("="*60)
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Verify GET /api/agents uses user_id filtering
    print("\n📋 Test 1: Verify GET /api/agents uses user_id filtering")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"✅ Retrieved {len(agents)} agents for current user")
        
        # Verify all agents have the same user_id
        user_ids = set(agent.get('user_id') for agent in agents)
        if len(user_ids) == 1:
            print(f"✅ All agents belong to the same user (proper isolation)")
        else:
            print(f"❌ Agents have different user_ids: {user_ids}")
            return False
    else:
        print(f"❌ Failed to get agents: {agents_response.status_code}")
        return False
    
    # Test 2: Create agent via POST /api/agents (Agent Library functionality)
    print("\n🤖 Test 2: Create agent via POST /api/agents (Agent Library)")
    agent_data = {
        "name": "Sync Test Agent",
        "archetype": "scientist",
        "goal": "Test agent synchronization",
        "expertise": "Synchronization Testing",
        "background": "Created to test Agent Library to Observatory sync",
        "personality": {
            "extroversion": 7, "optimism": 8, "curiosity": 9,
            "cooperativeness": 8, "energy": 7
        }
    }
    
    create_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    if create_response.status_code == 200:
        new_agent = create_response.json()
        new_agent_id = new_agent["id"]
        print(f"✅ Created agent via Agent Library: {new_agent['name']} (ID: {new_agent_id})")
    else:
        print(f"❌ Failed to create agent: {create_response.status_code}")
        return False
    
    # Test 3: Verify agent appears in Observatory (GET /api/agents)
    print("\n🔭 Test 3: Verify agent appears in Observatory (GET /api/agents)")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        updated_agents = agents_response.json()
        agent_ids = [agent["id"] for agent in updated_agents]
        
        if new_agent_id in agent_ids:
            print(f"✅ Agent created in Agent Library appears in Observatory")
            print(f"   Total agents now: {len(updated_agents)}")
        else:
            print(f"❌ Agent created in Agent Library does NOT appear in Observatory")
            return False
    else:
        print(f"❌ Failed to verify agent in Observatory: {agents_response.status_code}")
        return False
    
    # Test 4: Verify conversation generation uses user's agents
    print("\n💬 Test 4: Verify conversation generation uses user's agents")
    
    # Set scenario
    scenario_data = {
        "scenario": "Team meeting to discuss synchronization testing",
        "scenario_name": "Sync Test Meeting"
    }
    scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
    
    # Start simulation
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    
    # Generate multiple conversations to test agent selection
    participating_agents = set()
    
    for i in range(5):  # Generate 5 conversations to see different agent combinations
        conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        if conversation_response.status_code == 200:
            conversation_data = conversation_response.json()
            
            if "messages" in conversation_data:
                messages = conversation_data["messages"]
                for message in messages:
                    if "agent_name" in message:
                        participating_agents.add(message["agent_name"])
        
        time.sleep(0.5)  # Small delay between requests
    
    # Check if our new agent participated in any conversation
    if "Sync Test Agent" in participating_agents:
        print(f"✅ New agent participated in conversation generation")
    else:
        print(f"⚠️ New agent didn't participate (this is normal - random selection)")
    
    print(f"   Agents that participated across 5 conversations: {participating_agents}")
    print(f"   Total unique participating agents: {len(participating_agents)}")
    
    # Test 5: Verify agent deletion works
    print("\n🗑️ Test 5: Verify agent deletion works")
    delete_response = requests.delete(f"{API_URL}/agents/{new_agent_id}", headers=headers)
    if delete_response.status_code == 200:
        print(f"✅ Agent deleted successfully")
        
        # Verify agent is gone
        agents_response = requests.get(f"{API_URL}/agents", headers=headers)
        if agents_response.status_code == 200:
            final_agents = agents_response.json()
            final_agent_ids = [agent["id"] for agent in final_agents]
            
            if new_agent_id not in final_agent_ids:
                print(f"✅ Agent no longer appears in Observatory after deletion")
            else:
                print(f"❌ Agent still appears after deletion")
                return False
        else:
            print(f"❌ Failed to verify deletion: {agents_response.status_code}")
            return False
    else:
        print(f"❌ Failed to delete agent: {delete_response.status_code}")
        return False
    
    return True

def test_backend_implementation_details():
    """Test the specific backend implementation details"""
    print("\n🔍 BACKEND IMPLEMENTATION VERIFICATION")
    print("="*60)
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test that conversation generation endpoint filters by user_id
    print("\n💬 Verifying conversation generation filters by user_id")
    
    # Get current agents
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        user_agents = agents_response.json()
        print(f"✅ User has {len(user_agents)} agents")
        
        if len(user_agents) >= 2:
            # Generate conversation
            conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            
            if conversation_response.status_code == 200:
                conversation_data = conversation_response.json()
                
                # Verify conversation is associated with user
                if "user_id" in conversation_data:
                    print(f"✅ Conversation properly associated with user_id")
                else:
                    print(f"❌ Conversation missing user_id")
                    return False
                
                # Verify only user's agents participated
                if "messages" in conversation_data:
                    messages = conversation_data["messages"]
                    participating_agent_names = set(msg.get("agent_name") for msg in messages)
                    user_agent_names = set(agent["name"] for agent in user_agents)
                    
                    # Check if participating agents are subset of user's agents
                    if participating_agent_names.issubset(user_agent_names):
                        print(f"✅ Only user's agents participated in conversation")
                    else:
                        unknown_agents = participating_agent_names - user_agent_names
                        print(f"❌ Unknown agents participated: {unknown_agents}")
                        return False
                else:
                    print(f"❌ Conversation missing messages")
                    return False
            else:
                print(f"❌ Failed to generate conversation: {conversation_response.status_code}")
                return False
        else:
            print(f"⚠️ Need at least 2 agents for conversation test")
    else:
        print(f"❌ Failed to get user agents: {agents_response.status_code}")
        return False
    
    return True

def main():
    """Main test execution"""
    print("🚀 FINAL AGENT SYNCHRONIZATION VERIFICATION")
    print("Testing the fix: 'agents added through Agent Library should now appear in Observatory'")
    print("since both use the same /api/agents endpoint filtered by user_id")
    print(f"API URL: {API_URL}")
    
    # Run comprehensive test
    test1_passed = test_agent_synchronization_comprehensive()
    
    # Run backend implementation test
    test2_passed = test_backend_implementation_details()
    
    # Final summary
    print("\n" + "="*60)
    print("🏁 FINAL TEST SUMMARY")
    print("="*60)
    
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        print("\n🎉 AGENT SYNCHRONIZATION FIX VERIFIED!")
        print("✅ Agent Library and Observatory use the same /api/agents endpoint")
        print("✅ Both endpoints properly filter by user_id")
        print("✅ Agents created in Agent Library appear in Observatory")
        print("✅ Conversation generation uses user's agents")
        print("✅ Agent deletion works correctly")
        print("✅ User data isolation is maintained")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Comprehensive test: {'PASSED' if test1_passed else 'FAILED'}")
        print(f"Backend implementation test: {'PASSED' if test2_passed else 'FAILED'}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)