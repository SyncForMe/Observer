#!/usr/bin/env python3
"""
Quick test for Rolling Context Window functionality
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_basic_functionality():
    print("🧪 QUICK ROLLING CONTEXT WINDOW TEST")
    print("="*50)
    
    # 1. Authenticate
    print("\n1. 🔐 Authenticating...")
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    auth_data = auth_response.json()
    token = auth_data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # 2. Create test agents
    print("\n2. 🤖 Creating test agents...")
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist",
        "goal": "Test goal",
        "expertise": "Test expertise",
        "background": "Test background",
        "personality": {
            "extroversion": 5,
            "optimism": 6,
            "curiosity": 7,
            "cooperativeness": 8,
            "energy": 6
        }
    }
    
    # Create 3 agents
    for i in range(3):
        agent_data["name"] = f"Test Agent {i+1}"
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to create agent {i+1}")
            return False
    print("✅ Created 3 test agents")
    
    # 3. Start simulation
    print("\n3. 🚀 Starting simulation...")
    sim_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if sim_response.status_code != 200:
        print("❌ Failed to start simulation")
        return False
    print("✅ Simulation started")
    
    # 4. Test conversation generation
    print("\n4. 💬 Testing conversation generation...")
    conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    if conv_response.status_code != 200:
        print(f"❌ Conversation generation failed: {conv_response.status_code}")
        print(f"Response: {conv_response.text}")
        return False
    
    conv_data = conv_response.json()
    print(f"✅ Generated conversation with {len(conv_data.get('messages', []))} messages")
    
    # 5. Test conversation summaries endpoint
    print("\n5. 📋 Testing conversation summaries endpoint...")
    summaries_response = requests.get(f"{API_URL}/conversation-summaries", headers=headers)
    if summaries_response.status_code != 200:
        print(f"❌ Conversation summaries endpoint failed: {summaries_response.status_code}")
        return False
    
    summaries_data = summaries_response.json()
    print(f"✅ Conversation summaries endpoint working (found {len(summaries_data)} summaries)")
    
    # 6. Generate a few more conversations to test normal operation
    print("\n6. 🔄 Testing multiple conversation generation...")
    for i in range(3):
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if conv_response.status_code != 200:
            print(f"❌ Conversation {i+2} generation failed")
            return False
        print(f"✅ Generated conversation {i+2}")
    
    # 7. Check total conversations
    print("\n7. 📊 Checking conversation count...")
    conversations_response = requests.get(f"{API_URL}/conversations", headers=headers)
    if conversations_response.status_code != 200:
        print("❌ Failed to get conversations")
        return False
    
    conversations_data = conversations_response.json()
    print(f"✅ Total conversations: {len(conversations_data)}")
    
    print("\n🎯 BASIC FUNCTIONALITY TEST RESULTS:")
    print("✅ Authentication working")
    print("✅ Agent creation working")
    print("✅ Simulation start working")
    print("✅ Conversation generation working")
    print("✅ Conversation summaries endpoint working")
    print("✅ Multiple conversation generation working")
    
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🏆 BASIC FUNCTIONALITY: ✅ WORKING")
    else:
        print("\n🏆 BASIC FUNCTIONALITY: ❌ ISSUES DETECTED")