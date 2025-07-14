#!/usr/bin/env python3
"""
Focused Conversation Generation Test
===================================

This script focuses specifically on testing the conversation generation endpoint
with existing agents to debug the issue reported by the user.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

def test_guest_auth():
    """Get guest authentication token"""
    print("🔐 Getting guest authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_info = data.get('user', {})
            print(f"✅ Authenticated as: {user_info.get('email', 'Unknown')}")
            return token, user_info.get('id')
        else:
            print(f"❌ Auth failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Auth exception: {str(e)}")
        return None, None

def check_existing_agents(token):
    """Check what agents already exist"""
    print("\n👥 Checking existing agents...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=30)
        
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} existing agents")
            
            for i, agent in enumerate(agents[:5], 1):  # Show first 5
                name = agent.get('name', 'Unknown')
                archetype = agent.get('archetype', 'Unknown')
                agent_id = agent.get('id', 'No ID')
                print(f"   {i}. {name} ({archetype}) - ID: {agent_id}")
            
            if len(agents) > 5:
                print(f"   ... and {len(agents) - 5} more agents")
            
            return agents
        else:
            print(f"❌ Failed to get agents: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception getting agents: {str(e)}")
        return []

def check_simulation_state(token):
    """Check current simulation state"""
    print("\n📊 Checking simulation state...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=30)
        
        if response.status_code == 200:
            state = response.json()
            is_active = state.get('is_active', False)
            scenario = state.get('scenario', 'No scenario')
            user_id = state.get('user_id', 'No user ID')
            
            print(f"✅ Simulation state retrieved")
            print(f"   Active: {is_active}")
            print(f"   User ID: {user_id}")
            print(f"   Scenario: {scenario[:100]}...")
            
            return state
        else:
            print(f"❌ Failed to get simulation state: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception getting simulation state: {str(e)}")
        return None

def start_simulation_if_needed(token):
    """Start simulation if it's not active"""
    print("\n▶️ Starting simulation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First set a scenario
    scenario_data = {
        "scenario": "The team is working on a breakthrough quantum computing project. They need to collaborate to solve technical challenges and make critical decisions about the implementation.",
        "scenario_name": "Quantum Computing Project"
    }
    
    try:
        print("   Setting scenario...")
        scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=30)
        
        if scenario_response.status_code == 200:
            print("   ✅ Scenario set successfully")
        else:
            print(f"   ❌ Failed to set scenario: {scenario_response.status_code} - {scenario_response.text}")
        
        # Now start the simulation
        print("   Starting simulation...")
        start_data = {"time_limit_hours": None}
        
        response = requests.post(f"{API_URL}/simulation/start", json=start_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Simulation started: {data.get('message', 'No message')}")
            return True
        else:
            print(f"   ❌ Failed to start simulation: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception starting simulation: {str(e)}")
        return False

def test_conversation_generation(token):
    """Test the conversation generation endpoint"""
    print("\n💬 Testing conversation generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("   Calling /api/conversation/generate...")
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=60)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Conversation generation successful!")
            
            conversation = data.get('conversation')
            if conversation:
                messages = conversation.get('messages', [])
                round_number = conversation.get('round_number', 'Unknown')
                scenario_name = conversation.get('scenario_name', 'Unknown')
                user_id = conversation.get('user_id', 'Unknown')
                
                print(f"   📄 Round: {round_number}")
                print(f"   📝 Scenario: {scenario_name}")
                print(f"   👤 User ID: {user_id}")
                print(f"   💬 Messages: {len(messages)}")
                
                # Show first few messages
                for i, msg in enumerate(messages[:3]):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_text = msg.get('message', '')
                    print(f"      {i+1}. {agent_name}: {message_text[:80]}...")
                
                return conversation
            else:
                print("   ❌ No conversation in response")
                return None
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def check_conversations(token):
    """Check if conversations were saved"""
    print("\n📚 Checking saved conversations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=30)
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Retrieved {len(conversations)} conversations")
            
            if len(conversations) > 0:
                # Show details of recent conversations
                for i, conv in enumerate(conversations[:3], 1):
                    round_num = conv.get('round_number', 'Unknown')
                    message_count = len(conv.get('messages', []))
                    scenario_name = conv.get('scenario_name', 'Unknown')
                    created_at = conv.get('created_at', 'Unknown')
                    user_id = conv.get('user_id', 'Unknown')
                    
                    print(f"   {i}. Round {round_num}: {message_count} messages")
                    print(f"      Scenario: {scenario_name}")
                    print(f"      User ID: {user_id}")
                    print(f"      Created: {created_at}")
            
            return conversations
        else:
            print(f"❌ Failed to get conversations: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception getting conversations: {str(e)}")
        return []

def main():
    """Main test function"""
    print("🚀 Focused Conversation Generation Test")
    print("=" * 50)
    
    # Step 1: Authenticate
    token, user_id = test_guest_auth()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Check existing agents
    agents = check_existing_agents(token)
    if len(agents) < 2:
        print(f"\n❌ Need at least 2 agents for conversation generation. Found: {len(agents)}")
        return
    
    # Step 3: Check simulation state
    sim_state = check_simulation_state(token)
    
    # Step 4: Start simulation if needed
    if not sim_state or not sim_state.get('is_active'):
        print("\n⚠️ Simulation not active, starting it...")
        if not start_simulation_if_needed(token):
            print("\n❌ Cannot proceed without active simulation")
            return
    else:
        print("\n✅ Simulation is already active")
    
    # Step 5: Test conversation generation
    conversation = test_conversation_generation(token)
    
    # Step 6: Check if conversations were saved
    conversations = check_conversations(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if conversation and len(conversations) > 0:
        print("✅ CONVERSATION GENERATION IS WORKING")
        print("   - Authentication: ✅")
        print("   - Agents available: ✅")
        print("   - Simulation active: ✅")
        print("   - Conversation generated: ✅")
        print("   - Conversations saved: ✅")
        print("\n🎯 If users report issues, check:")
        print("   - Frontend JavaScript errors")
        print("   - Network connectivity")
        print("   - Browser console for API failures")
        print("   - Auto-generation timing/intervals")
    else:
        print("❌ CONVERSATION GENERATION HAS ISSUES")
        if not conversation:
            print("   - Conversation generation failed")
        if len(conversations) == 0:
            print("   - No conversations saved")
        print("\n🔧 Issues to investigate:")
        print("   - Check backend logs for errors")
        print("   - Verify Gemini API key and quota")
        print("   - Check database connectivity")
        print("   - Review user data isolation logic")

if __name__ == "__main__":
    main()