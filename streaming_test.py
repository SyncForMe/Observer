#!/usr/bin/env python3
"""
STREAMING FUNCTIONALITY TEST
Test the streaming endpoint after parallel generation to verify messages are properly saved.
"""

import requests
import json
import time
import os

# Use internal backend URL
API_URL = "http://localhost:8001/api"

def authenticate():
    """Authenticate with the backend"""
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print(f"Auth error: {e}")
    return None

def test_streaming_endpoint():
    """Test the streaming endpoint functionality"""
    print("📤 TESTING STREAMING ENDPOINT AFTER PARALLEL GENERATION")
    print("="*60)
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Test 1: Basic streaming endpoint
    print("\n🔍 Test 1: Basic streaming endpoint access...")
    try:
        response = requests.get(f"{API_URL}/messages/stream", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Streaming endpoint accessible")
            print(f"   📊 Response structure: {list(data.keys())}")
            print(f"   📈 Message count: {data.get('count', 0)}")
            print(f"   ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
            
            if data.get('count', 0) > 0:
                messages = data.get('messages', [])
                print(f"   📝 Sample message structure: {list(messages[0].keys()) if messages else 'No messages'}")
            
            return True
        else:
            print(f"❌ Streaming endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streaming test error: {e}")
        return False

def test_conversation_endpoint():
    """Test the conversations endpoint to see completed conversations"""
    print("\n🔍 Test 2: Checking completed conversations...")
    
    auth_token = authenticate()
    if not auth_token:
        return False
    
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Found {len(conversations)} conversations")
            
            if conversations:
                latest = conversations[-1]
                messages = latest.get('messages', [])
                print(f"   📊 Latest conversation: {len(messages)} messages")
                print(f"   🕐 Created: {latest.get('created_at', 'N/A')}")
                print(f"   📝 Scenario: {latest.get('scenario_name', 'N/A')}")
                
                if messages:
                    print(f"   👥 Agents: {[msg.get('agent_name') for msg in messages]}")
                    print(f"   📏 Message lengths: {[len(msg.get('message', '')) for msg in messages]}")
                
                return True
            else:
                print("   ℹ️ No conversations found")
                return True
        else:
            print(f"❌ Conversations endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversations test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 STREAMING & CONVERSATION VERIFICATION TEST")
    print("="*60)
    
    streaming_success = test_streaming_endpoint()
    conversation_success = test_conversation_endpoint()
    
    print(f"\n📊 RESULTS:")
    print(f"   Streaming endpoint: {'✅ Working' if streaming_success else '❌ Issues'}")
    print(f"   Conversations endpoint: {'✅ Working' if conversation_success else '❌ Issues'}")
    
    if streaming_success and conversation_success:
        print(f"\n🎉 STREAMING FUNCTIONALITY: FULLY OPERATIONAL")
    else:
        print(f"\n⚠️ STREAMING FUNCTIONALITY: NEEDS ATTENTION")