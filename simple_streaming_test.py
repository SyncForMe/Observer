#!/usr/bin/env python3
"""
SIMPLE PROGRESSIVE STREAMING TEST
Quick test of the progressive streaming endpoints
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

print(f"Testing API URL: {API_URL}")

# Test authentication first
def test_auth():
    login_data = {
        "email": "dino@cytonic.com", 
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=15)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

# Test streaming endpoint
def test_streaming_endpoint(token):
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{API_URL}/messages/stream", headers=headers, timeout=15)
        print(f"📤 Streaming endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Messages: {len(data.get('messages', []))}")
            print(f"   Structure: {list(data.keys())}")
            return True
        else:
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Streaming test error: {e}")
        return False

# Test conversation generation (quick)
def test_conversation_generation(token):
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        print("🎬 Testing conversation generation...")
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"   Response: {response.status_code} in {end_time - start_time:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"   Type: {data.get('type')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Message count: {data.get('message_count')}")
            return data.get('id')
        else:
            print(f"   Error: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Conversation generation error: {e}")
        return None

# Main test
def main():
    print("🚀 SIMPLE PROGRESSIVE STREAMING TEST")
    print("="*50)
    
    # Test 1: Authentication
    token = test_auth()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test 2: Streaming endpoint
    streaming_works = test_streaming_endpoint(token)
    
    # Test 3: Conversation generation
    conv_id = test_conversation_generation(token)
    
    # Test 4: Stream completion (if we have a conversation)
    if conv_id:
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(f"{API_URL}/messages/stream/complete?conversation_id={conv_id}", 
                                   headers=headers, timeout=15)
            print(f"🏁 Stream completion: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Message count: {data.get('message_count')}")
        except Exception as e:
            print(f"❌ Stream completion error: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY:")
    print(f"✅ Authentication: {'✅' if token else '❌'}")
    print(f"✅ Streaming endpoint: {'✅' if streaming_works else '❌'}")
    print(f"✅ Conversation generation: {'✅' if conv_id else '❌'}")
    
    if token and streaming_works:
        print("\n🎉 Progressive streaming system appears to be working!")
    else:
        print("\n❌ Progressive streaming system has issues")

if __name__ == "__main__":
    main()