#!/usr/bin/env python3
"""
Diagnostic test to check the current state and identify issues
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print("🔍 DIAGNOSTIC TEST")
print(f"API URL: {API_URL}")
print("="*60)

# Step 1: Guest login
print("\n1. Testing guest login...")
response = requests.post(f"{API_URL}/auth/test-login")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    auth_token = data.get("access_token")
    user_id = data.get("user", {}).get("id")
    print(f"   ✅ Login successful, User ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 2: Check simulation state
    print("\n2. Checking simulation state...")
    response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        state = response.json()
        print(f"   ✅ Day {state.get('current_day', 1)}, {state.get('current_time_period', 'unknown')}")
        print(f"   Active: {state.get('is_active', False)}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Step 3: Check agents
    print("\n3. Checking available agents...")
    response = requests.get(f"{API_URL}/agents", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        agents = response.json()
        print(f"   ✅ Found {len(agents)} agents")
        for agent in agents[:3]:  # Show first 3
            print(f"      - {agent.get('name', 'Unknown')}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Step 4: Check conversations
    print("\n4. Checking existing conversations...")
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        conversations = response.json()
        print(f"   ✅ Found {len(conversations)} conversations")
        for i, conv in enumerate(conversations[-3:], 1):  # Show last 3
            time_period = conv.get('time_period', 'Not set')
            msg_count = len(conv.get('messages', []))
            print(f"      {i}. {time_period} ({msg_count} messages)")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Step 5: Try a simple conversation generation (with timeout)
    print("\n5. Testing conversation generation...")
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Conversation generated successfully")
        else:
            print(f"   ❌ Failed: {response.text}")
    except requests.exceptions.Timeout:
        print(f"   ⏰ Request timed out after 30 seconds")
    except Exception as e:
        print(f"   ❌ Error: {e}")

else:
    print(f"   ❌ Login failed: {response.text}")

print("\n" + "="*60)
print("Diagnostic complete")