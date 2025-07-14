#!/usr/bin/env python3
"""
Deep Conversation Generation Analysis
====================================

This script analyzes the conversation generation response in detail
to understand why conversations are not being generated properly.
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
API_URL = f"{BACKEND_URL}/api"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login", timeout=30)
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    return None

def analyze_conversation_generation():
    """Analyze the conversation generation response in detail"""
    print("🔍 Deep Analysis of Conversation Generation")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("📊 Checking prerequisites...")
    
    # Check agents
    agents_response = requests.get(f"{API_URL}/agents", headers=headers, timeout=30)
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"✅ Agents: {len(agents)} available")
    else:
        print(f"❌ Agents check failed: {agents_response.status_code}")
        return
    
    # Check simulation state
    state_response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=30)
    if state_response.status_code == 200:
        state = state_response.json()
        print(f"✅ Simulation active: {state.get('is_active', False)}")
        print(f"   User ID: {state.get('user_id', 'None')}")
        print(f"   Scenario: {state.get('scenario', 'None')[:50]}...")
    else:
        print(f"❌ Simulation state check failed: {state_response.status_code}")
        return
    
    print("\n💬 Testing conversation generation...")
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Get raw response text first
            raw_text = response.text
            print(f"Raw Response Length: {len(raw_text)} characters")
            print(f"Raw Response Preview: {raw_text[:200]}...")
            
            try:
                data = response.json()
                print(f"\nParsed JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Print full response structure
                print(f"\nFull Response Structure:")
                print(json.dumps(data, indent=2, default=str)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2, default=str))
                
                # Check for conversation data
                conversation = data.get('conversation')
                if conversation:
                    print(f"\n✅ Conversation found in response")
                    print(f"   Type: {type(conversation)}")
                    if isinstance(conversation, dict):
                        print(f"   Keys: {list(conversation.keys())}")
                        messages = conversation.get('messages', [])
                        print(f"   Messages: {len(messages)}")
                        if messages:
                            print(f"   First message: {messages[0]}")
                    else:
                        print(f"   Content: {conversation}")
                else:
                    print(f"\n❌ No 'conversation' key in response")
                    
                    # Check for other possible keys
                    for key, value in data.items():
                        print(f"   {key}: {type(value)} - {str(value)[:100]}...")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {raw_text}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_multiple_generation_attempts():
    """Test multiple conversation generation attempts"""
    print("\n🔄 Testing Multiple Generation Attempts")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(3):
        print(f"\nAttempt {i+1}:")
        try:
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                conversation = data.get('conversation')
                
                if conversation and conversation.get('messages'):
                    message_count = len(conversation['messages'])
                    print(f"   ✅ Success: {message_count} messages generated")
                    
                    # Show agent names
                    agent_names = [msg.get('agent_name') for msg in conversation['messages']]
                    print(f"   Agents: {', '.join(set(agent_names))}")
                    
                    return True
                else:
                    print(f"   ❌ No conversation/messages in response")
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        if i < 2:  # Don't wait after last attempt
            time.sleep(2)
    
    return False

def check_backend_logs():
    """Check if we can get any backend logs"""
    print("\n📋 Checking Backend Status")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test various endpoints to see what's working
    endpoints_to_test = [
        ("/usage", "API Usage"),
        ("/archetypes", "Agent Archetypes"),
        ("/simulation/random-scenario", "Random Scenario")
    ]
    
    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=30)
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Exception - {str(e)}")

def main():
    """Main analysis function"""
    analyze_conversation_generation()
    success = test_multiple_generation_attempts()
    check_backend_logs()
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS CONCLUSION")
    print("=" * 50)
    
    if success:
        print("✅ Conversation generation is working intermittently")
        print("   Issue may be timing-related or API quota-related")
    else:
        print("❌ Conversation generation is consistently failing")
        print("   The endpoint returns 200 but no conversation data")
        print("   This suggests an issue in the backend logic")

if __name__ == "__main__":
    main()