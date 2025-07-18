#!/usr/bin/env python3
"""
Focused test script for the optimized observer message functionality with better error handling.
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

def make_request_with_retry(method, url, max_retries=3, timeout=30, **kwargs):
    """Make HTTP request with retry logic"""
    for attempt in range(max_retries):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, timeout=timeout, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, timeout=timeout, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
            
        except requests.exceptions.Timeout:
            print(f"   Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
        except Exception as e:
            print(f"   Error on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise

def test_core_observer_functionality():
    """Test the core observer message functionality"""
    print("🚀 FOCUSED OBSERVER MESSAGE TESTING")
    print("=" * 50)
    
    # Step 1: Authenticate
    print("\n🔐 Authenticating...")
    try:
        auth_response = make_request_with_retry('POST', f"{API_URL}/auth/test-login")
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        token = auth_data['access_token']
        user_id = auth_data['user']['id']
        print(f"✅ Authenticated as user: {user_id}")
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Create agents
    print("\n🤖 Creating test agents...")
    agent_data = {
        "name": "Dr. Test Agent",
        "archetype": "scientist",
        "goal": "Test observer functionality",
        "expertise": "Testing",
        "background": "Test agent for observer messages"
    }
    
    try:
        agent_response = make_request_with_retry('POST', f"{API_URL}/agents", json=agent_data, headers=headers)
        if agent_response.status_code != 200:
            print(f"❌ Agent creation failed: {agent_response.status_code}")
            return False
        
        agent = agent_response.json()
        print(f"✅ Created agent: {agent['name']} (ID: {agent['id']})")
        
    except Exception as e:
        print(f"❌ Agent creation error: {str(e)}")
        return False
    
    # Step 3: Start simulation
    print("\n▶️ Starting simulation...")
    try:
        sim_response = make_request_with_retry('POST', f"{API_URL}/simulation/start", headers=headers)
        if sim_response.status_code != 200:
            print(f"❌ Simulation start failed: {sim_response.status_code}")
            return False
        
        print("✅ Simulation started")
        
    except Exception as e:
        print(f"❌ Simulation start error: {str(e)}")
        return False
    
    # Step 4: Test observer message core functionality
    print("\n💬 Testing observer message...")
    observer_message = "Hello team, let's test the observer functionality"
    
    try:
        start_time = time.time()
        
        observer_response = make_request_with_retry(
            'POST', 
            f"{API_URL}/observer/send-message",
            json={"observer_message": observer_message},
            headers=headers,
            timeout=20
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if observer_response.status_code != 200:
            print(f"❌ Observer message failed: {observer_response.status_code}")
            print(f"   Response: {observer_response.text}")
            return False
        
        observer_data = observer_response.json()
        print(f"✅ Observer message sent successfully")
        print(f"   Response time: {response_time:.2f}s")
        
        # Check response structure
        checks = {
            "Has message field": 'message' in observer_data,
            "Has observer_message field": 'observer_message' in observer_data,
            "Has agent_responses field": 'agent_responses' in observer_data,
            "Observer message matches": observer_data.get('observer_message') == observer_message,
            "Fast response": response_time < 15.0
        }
        
        agent_responses = observer_data.get('agent_responses', {})
        checks.update({
            "Scenario name is Observer Guidance": agent_responses.get('scenario_name') == 'Observer Guidance',
            "Has messages": len(agent_responses.get('messages', [])) > 0
        })
        
        # Check observer message positioning
        messages = agent_responses.get('messages', [])
        if messages:
            first_message = messages[0]
            checks["Observer message first"] = (
                first_message.get('agent_name') == 'Observer (You)' and 
                first_message.get('message') == observer_message
            )
        else:
            checks["Observer message first"] = False
        
        print("\n📊 Response Structure Checks:")
        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All core observer message functionality checks PASSED!")
        else:
            print("\n⚠️  Some checks failed")
        
        # Step 5: Test conversation retrieval
        print("\n📚 Testing conversation retrieval...")
        try:
            conv_response = make_request_with_retry('GET', f"{API_URL}/conversations", headers=headers, timeout=15)
            
            if conv_response.status_code == 200:
                conversations = conv_response.json()
                print(f"✅ Retrieved {len(conversations)} conversations")
                
                # Find observer conversation
                observer_conv = None
                for conv in conversations:
                    if conv.get('scenario_name') == 'Observer Guidance':
                        observer_conv = conv
                        break
                
                if observer_conv:
                    print("✅ Found Observer Guidance conversation")
                    conv_messages = observer_conv.get('messages', [])
                    print(f"   Messages in conversation: {len(conv_messages)}")
                    
                    # Check for duplicates
                    observer_messages = [msg for msg in conv_messages if msg.get('agent_name') == 'Observer (You)']
                    print(f"   Observer messages found: {len(observer_messages)}")
                    
                    if len(observer_messages) == 1:
                        print("✅ No duplicate observer messages")
                    else:
                        print("⚠️  Potential duplicate observer messages")
                        
                else:
                    print("❌ Observer Guidance conversation not found")
                    
            else:
                print(f"❌ Conversation retrieval failed: {conv_response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Conversation retrieval error: {str(e)}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Observer message error: {str(e)}")
        return False

def test_multiple_observer_messages():
    """Test sending multiple observer messages"""
    print("\n🔄 Testing multiple observer messages...")
    
    # Authenticate
    try:
        auth_response = make_request_with_retry('POST', f"{API_URL}/auth/test-login")
        token = auth_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False
    
    messages = [
        "First observer message",
        "Second observer message", 
        "Third observer message"
    ]
    
    successful_sends = 0
    
    for i, message in enumerate(messages, 1):
        try:
            print(f"   Sending message {i}: {message}")
            
            response = make_request_with_retry(
                'POST',
                f"{API_URL}/observer/send-message",
                json={"observer_message": message},
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                successful_sends += 1
                print(f"   ✅ Message {i} sent successfully")
            else:
                print(f"   ❌ Message {i} failed: {response.status_code}")
                
            time.sleep(1)  # Brief pause between messages
            
        except Exception as e:
            print(f"   ❌ Message {i} error: {str(e)}")
    
    print(f"\n📊 Multiple Messages Result: {successful_sends}/{len(messages)} sent successfully")
    return successful_sends == len(messages)

def main():
    """Main test execution"""
    print("🧪 OPTIMIZED OBSERVER MESSAGE TESTING")
    print("=" * 60)
    
    # Test core functionality
    core_test_passed = test_core_observer_functionality()
    
    # Test multiple messages
    multiple_test_passed = test_multiple_observer_messages()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    print(f"✅ Core Observer Functionality: {'PASSED' if core_test_passed else 'FAILED'}")
    print(f"✅ Multiple Observer Messages: {'PASSED' if multiple_test_passed else 'FAILED'}")
    
    overall_success = core_test_passed and multiple_test_passed
    
    if overall_success:
        print("\n🎉 OBSERVER MESSAGE OPTIMIZATION TESTING: SUCCESS")
        print("   ⚡ Instant sending is working")
        print("   💬 Response structure is correct")
        print("   📝 Observer messages appear first in conversations")
        print("   🔄 Multiple messages can be sent successfully")
    else:
        print("\n⚠️  OBSERVER MESSAGE OPTIMIZATION TESTING: NEEDS ATTENTION")
        if not core_test_passed:
            print("   ❌ Core functionality issues detected")
        if not multiple_test_passed:
            print("   ❌ Multiple message handling issues detected")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)