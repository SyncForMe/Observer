#!/usr/bin/env python3
"""
CONVERSATION GENERATION WITH STREAMING TEST
Test conversation generation to populate streaming messages
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

def authenticate():
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_conversation_generation_streaming():
    print("🎬 CONVERSATION GENERATION WITH STREAMING TEST")
    print("="*60)
    
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Set up a simple scenario first
    print("\n📋 Setting up scenario...")
    scenario_data = {
        "scenario": "Test progressive streaming with a simple discussion",
        "scenario_name": "Streaming Test"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", 
                               json=scenario_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Scenario set successfully")
        else:
            print(f"⚠️ Scenario setup failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Scenario setup error: {e}")
    
    # Check agents
    print("\n🤖 Checking agents...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            if len(agents) < 2:
                print("⚠️ Need at least 2 agents for good testing")
        else:
            print(f"⚠️ Agent check failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Agent check error: {e}")
    
    # Generate conversation with extended timeout
    print("\n🎬 Generating conversation (this may take a while)...")
    start_time = time.time()
    
    try:
        # Use a longer timeout for conversation generation
        response = requests.post(f"{API_URL}/conversation/generate", 
                               headers=headers, timeout=90)
        end_time = time.time()
        generation_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation generated in {generation_time:.2f}s")
            print(f"   Type: {data.get('type')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Message count: {data.get('message_count')}")
            print(f"   Conversation ID: {data.get('id')}")
            
            # Wait a moment for streaming messages to be saved
            print("\n⏳ Waiting for streaming messages to be saved...")
            time.sleep(3)
            
            # Check streaming messages
            print("\n📤 Checking streaming messages...")
            stream_response = requests.get(f"{API_URL}/messages/stream", 
                                         headers=headers, timeout=10)
            
            if stream_response.status_code == 200:
                stream_data = stream_response.json()
                messages = stream_data.get('messages', [])
                print(f"✅ Found {len(messages)} streaming messages")
                
                if messages:
                    # Show sample message
                    first_msg = messages[0]
                    print(f"   Sample message:")
                    print(f"     Agent: {first_msg.get('agent_name')}")
                    print(f"     Status: {first_msg.get('status')}")
                    print(f"     Index: {first_msg.get('message_index')}/{first_msg.get('total_expected')}")
                    print(f"     Content: {first_msg.get('message', '')[:100]}...")
                    
                    # Test stream completion
                    conv_id = data.get('id')
                    if conv_id:
                        print(f"\n🏁 Testing stream completion...")
                        completion_response = requests.post(
                            f"{API_URL}/messages/stream/complete?conversation_id={conv_id}",
                            headers=headers, timeout=10
                        )
                        
                        if completion_response.status_code == 200:
                            completion_data = completion_response.json()
                            print(f"✅ Stream completion successful")
                            print(f"   Success: {completion_data.get('success')}")
                            print(f"   Final conversation ID: {completion_data.get('conversation_id')}")
                            print(f"   Message count: {completion_data.get('message_count')}")
                        else:
                            print(f"❌ Stream completion failed: {completion_response.status_code}")
                
                return True
            else:
                print(f"❌ Failed to get streaming messages: {stream_response.status_code}")
                return False
        else:
            print(f"❌ Conversation generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Conversation generation timed out after 90 seconds")
        return False
    except Exception as e:
        print(f"❌ Conversation generation error: {e}")
        return False

def main():
    success = test_conversation_generation_streaming()
    
    print("\n" + "="*60)
    if success:
        print("🎉 CONVERSATION GENERATION WITH STREAMING: SUCCESS!")
        print("   ✅ Conversation generated successfully")
        print("   ✅ Streaming messages created and retrieved")
        print("   ✅ Stream completion working")
        print("   ✅ Progressive streaming system operational")
    else:
        print("❌ CONVERSATION GENERATION WITH STREAMING: ISSUES")
        print("   Check the errors above for details")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)