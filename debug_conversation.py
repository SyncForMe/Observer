#!/usr/bin/env python3
"""
Debug script to investigate the conversation generation issue
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def debug_conversation_generation():
    print("🔍 DEBUGGING CONVERSATION GENERATION")
    print("=" * 50)
    
    # Step 1: Get auth token
    print("1. Getting auth token...")
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    auth_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code} - {auth_response.text}")
        return
    
    token = auth_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Auth token obtained")
    
    # Step 2: Check simulation state
    print("\n2. Checking simulation state...")
    state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    if state_response.status_code == 200:
        state = state_response.json()
        print(f"✅ Simulation state: {json.dumps(state, indent=2)}")
    else:
        print(f"❌ Failed to get simulation state: {state_response.status_code} - {state_response.text}")
    
    # Step 3: Check agents
    print("\n3. Checking agents...")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"✅ Found {len(agents)} agents")
        for agent in agents:
            print(f"   - {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
    else:
        print(f"❌ Failed to get agents: {agents_response.status_code} - {agents_response.text}")
        return
    
    # Step 4: Start simulation
    print("\n4. Starting simulation...")
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code == 200:
        start_data = start_response.json()
        print(f"✅ Simulation started: {json.dumps(start_data, indent=2)}")
    else:
        print(f"❌ Failed to start simulation: {start_response.status_code} - {start_response.text}")
        return
    
    # Step 5: Try conversation generation with detailed response
    print("\n5. Attempting conversation generation...")
    conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    print(f"Status Code: {conv_response.status_code}")
    print(f"Response Headers: {dict(conv_response.headers)}")
    print(f"Response Text: {conv_response.text}")
    
    if conv_response.status_code == 200:
        try:
            conv_data = conv_response.json()
            print(f"✅ Conversation response: {json.dumps(conv_data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
    else:
        print(f"❌ Conversation generation failed: {conv_response.status_code}")
    
    # Step 6: Check conversations
    print("\n6. Checking existing conversations...")
    convs_response = requests.get(f"{API_URL}/conversations", headers=headers)
    if convs_response.status_code == 200:
        conversations = convs_response.json()
        print(f"✅ Found {len(conversations)} conversations")
        for i, conv in enumerate(conversations):
            print(f"   Conversation {i+1}: {len(conv.get('messages', []))} messages")
    else:
        print(f"❌ Failed to get conversations: {convs_response.status_code} - {convs_response.text}")

if __name__ == "__main__":
    debug_conversation_generation()