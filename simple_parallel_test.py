#!/usr/bin/env python3
"""
SIMPLIFIED PARALLEL MESSAGE GENERATION TESTING
Testing the key aspects of parallel processing implementation.
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

print(f"🚀 PARALLEL MESSAGE GENERATION TESTING")
print(f"Using API URL: {API_URL}")
print("="*80)

# Test authentication
print("\n🔐 Testing Authentication...")
login_data = {
    "email": "dino@cytonic.com",
    "password": "Observerinho8"
}

try:
    response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
    if response.status_code == 200:
        auth_data = response.json()
        auth_token = auth_data.get("access_token")
        print("✅ Authentication successful")
        
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Test 1: Check agents
        print("\n🤖 Testing Agent Availability...")
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=30)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            for agent in agents[:3]:
                print(f"   - {agent.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
        
        # Test 2: Set scenario
        print("\n📋 Testing Scenario Setup...")
        scenario_data = {
            "scenario": "A team of quantum physicists needs to develop a breakthrough quantum communication device.",
            "scenario_name": "Quantum Communication Device Development"
        }
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=30)
        if response.status_code == 200:
            print("✅ Scenario set successfully")
        else:
            print(f"❌ Failed to set scenario: {response.status_code}")
        
        # Test 3: Test parallel conversation generation (CRITICAL TEST)
        print("\n⚡ Testing PARALLEL Conversation Generation...")
        print("   This is the key test for parallel processing performance!")
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            generation_time = end_time - start_time
            response_data = response.json()
            
            print(f"✅ Conversation generated in {generation_time:.2f} seconds")
            print(f"   Conversation ID: {response_data.get('id', 'Unknown')}")
            
            # Check if it's within parallel processing target (~27s vs ~81s sequential)
            if generation_time <= 45:
                improvement = 81 / generation_time  # Assuming 3 agents * 27s = 81s sequential
                print(f"🎉 PARALLEL PROCESSING SUCCESS: {improvement:.1f}x faster than sequential!")
                print(f"   Target: ~27s, Actual: {generation_time:.2f}s")
            else:
                print(f"⚠️ Performance below target: {generation_time:.2f}s (target: ~27s)")
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}")
        
        # Test 4: Test message streaming
        print("\n📤 Testing Message Streaming...")
        response = requests.get(f"{API_URL}/messages/stream", headers=headers, timeout=30)
        if response.status_code == 200:
            stream_data = response.json()
            message_count = stream_data.get('count', 0)
            print(f"✅ Streaming endpoint working - {message_count} messages available")
            
            # Check required fields
            required_fields = ['messages', 'count', 'since', 'timestamp']
            has_all_fields = all(field in stream_data for field in required_fields)
            if has_all_fields:
                print("✅ Streaming response has all required fields")
            else:
                print("❌ Missing required fields in streaming response")
        else:
            print(f"❌ Failed to access streaming endpoint: {response.status_code}")
        
        # Test 5: Verify conversation was created
        print("\n📋 Testing Conversation Retrieval...")
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=30)
        if response.status_code == 200:
            conversations = response.json()
            if conversations:
                latest_conv = conversations[-1]
                messages = latest_conv.get('messages', [])
                print(f"✅ Latest conversation has {len(messages)} messages")
                
                # Check agent participation
                unique_agents = set(msg.get('agent_name', '') for msg in messages)
                print(f"✅ {len(unique_agents)} different agents participated")
                
                # Check message quality
                avg_length = sum(len(msg.get('message', '')) for msg in messages) / len(messages) if messages else 0
                print(f"✅ Average message length: {avg_length:.0f} characters")
            else:
                print("❌ No conversations found")
        else:
            print(f"❌ Failed to retrieve conversations: {response.status_code}")
            
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Test failed with error: {e}")

print("\n" + "="*80)
print("🏁 PARALLEL MESSAGE GENERATION TEST COMPLETE")
print("="*80)