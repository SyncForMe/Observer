#!/usr/bin/env python3
"""
Quick V2 System Test - Debug message stream issue
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_v2_system():
    session = requests.Session()
    
    # Authenticate
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    response = session.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
    if response.status_code != 200:
        print(f"❌ Auth failed: {response.status_code}")
        return
    
    data = response.json()
    session.headers.update({'Authorization': f'Bearer {data.get("access_token")}'})
    user_id = data.get('user', {}).get('id')
    print(f"✅ Authenticated as user: {user_id}")
    
    # Test V2 endpoint
    print("\n🚀 Testing V2 endpoint...")
    start_time = time.time()
    response = session.post(f"{API_BASE}/conversation/generate-v2", json={}, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        conversation_id = data.get('conversation_id')
        total_time = data.get('total_time', 0)
        messages_generated = data.get('messages_generated', 0)
        
        print(f"✅ V2 endpoint success:")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Messages generated: {messages_generated}")
        print(f"   Total time: {total_time:.2f}s")
        
        # Test message stream with different status values
        print(f"\n📤 Testing message stream access...")
        
        # Test with status: "streaming"
        response = session.get(f"{API_BASE}/messages/stream", timeout=10)
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            print(f"   Messages with status 'streaming': {len(messages)}")
        
        # Test with modified query to get "available" status messages
        # We'll need to check if there's another endpoint or modify our approach
        
        # Let's check what's actually in the database by looking at recent conversations
        print(f"\n💬 Checking recent conversations...")
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        if response.status_code == 200:
            conversations = response.json()
            print(f"   Total conversations: {len(conversations)}")
            
            # Look for our V2 conversation
            v2_conversations = [c for c in conversations if conversation_id in str(c)]
            print(f"   V2 conversations found: {len(v2_conversations)}")
            
        # Check simulation state
        print(f"\n🔍 Checking simulation state...")
        response = session.get(f"{API_BASE}/simulation/state", timeout=10)
        if response.status_code == 200:
            state = response.json()
            print(f"   Simulation active: {state.get('is_active', False)}")
            print(f"   Scenario: {state.get('scenario', 'None')[:50]}...")
            
    else:
        print(f"❌ V2 endpoint failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_v2_system()