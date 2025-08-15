#!/usr/bin/env python3
"""
DEBUG STREAMING MESSAGES
Debug why streaming messages aren't being returned
"""

import requests
import json
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

def debug_streaming_messages():
    print("🔍 DEBUG STREAMING MESSAGES")
    print("="*50)
    
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check streaming messages
    print("\n📤 Checking streaming messages...")
    response = requests.get(f"{API_URL}/messages/stream", headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        print(f"   Streaming messages (status='streaming'): {len(messages)}")
        
        # Check conversations to see if messages are there
        print("\n💬 Checking conversations...")
        conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        
        if conv_response.status_code == 200:
            conversations = conv_response.json()
            print(f"   Total conversations: {len(conversations)}")
            
            if conversations:
                latest_conv = conversations[-1]
                conv_messages = latest_conv.get('messages', [])
                print(f"   Latest conversation messages: {len(conv_messages)}")
                print(f"   Latest conversation ID: {latest_conv.get('id')}")
                print(f"   Latest conversation round: {latest_conv.get('round_number')}")
                
                if conv_messages:
                    print(f"   Sample message agent: {conv_messages[0].get('agent_name')}")
                    print(f"   Sample message preview: {conv_messages[0].get('message', '')[:50]}...")
        
        # The issue might be that messages are being marked as "ready_for_conversion" 
        # instead of staying as "streaming". Let's generate a new conversation and 
        # check immediately
        print("\n🎬 Generating new conversation to check streaming status...")
        gen_response = requests.post(f"{API_URL}/conversation/generate", 
                                   headers=headers, timeout=60)
        
        if gen_response.status_code == 200:
            gen_data = gen_response.json()
            print(f"   Generated conversation: {gen_data.get('id')}")
            print(f"   Message count: {gen_data.get('message_count')}")
            
            # Check streaming messages immediately
            print("\n📤 Checking streaming messages immediately after generation...")
            immediate_response = requests.get(f"{API_URL}/messages/stream", 
                                            headers=headers, timeout=10)
            
            if immediate_response.status_code == 200:
                immediate_data = immediate_response.json()
                immediate_messages = immediate_data.get('messages', [])
                print(f"   Immediate streaming messages: {len(immediate_messages)}")
                
                if immediate_messages:
                    print("✅ Found streaming messages!")
                    for i, msg in enumerate(immediate_messages[:3]):
                        print(f"   Message {i+1}:")
                        print(f"     Agent: {msg.get('agent_name')}")
                        print(f"     Status: {msg.get('status')}")
                        print(f"     Index: {msg.get('message_index')}/{msg.get('total_expected')}")
                        print(f"     Conversation ID: {msg.get('conversation_id')}")
                        print(f"     Content: {msg.get('message', '')[:50]}...")
                    
                    # Test stream completion
                    conv_id = gen_data.get('id')
                    print(f"\n🏁 Testing stream completion for: {conv_id}")
                    completion_response = requests.post(
                        f"{API_URL}/messages/stream/complete?conversation_id={conv_id}",
                        headers=headers, timeout=10
                    )
                    
                    if completion_response.status_code == 200:
                        completion_data = completion_response.json()
                        print(f"✅ Stream completion: {completion_data.get('success')}")
                        print(f"   Message count: {completion_data.get('message_count')}")
                    else:
                        print(f"❌ Stream completion failed: {completion_response.status_code}")
                        print(f"   Response: {completion_response.text[:200]}")
                else:
                    print("❌ No streaming messages found even immediately after generation")
            else:
                print(f"❌ Failed to check immediate streaming messages: {immediate_response.status_code}")
        else:
            print(f"❌ Failed to generate conversation: {gen_response.status_code}")
    else:
        print(f"❌ Failed to check streaming messages: {response.status_code}")

if __name__ == "__main__":
    debug_streaming_messages()