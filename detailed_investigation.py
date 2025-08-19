#!/usr/bin/env python3
"""
DETAILED INVESTIGATION OF STREAMING AND DATABASE ISSUES

Investigating why:
1. Streaming endpoint returns dict instead of list
2. No conversations in database despite generation
3. Message timing and alternation issues
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def authenticate():
    """Authenticate and return session"""
    session = requests.Session()
    
    try:
        login_data = {
            "email": "dino@cytonic.com", 
            "password": "Observerinho8"
        }
        
        response = session.post(f"{API_BASE}/auth/login", 
                               json=login_data, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            user_data = data.get('user', {})
            
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
            print(f"✅ Authenticated as {user_data.get('name', 'Unknown')}")
            return session, user_data.get('id')
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return None, None

def investigate_streaming_endpoint():
    """Investigate what the streaming endpoint actually returns"""
    print("🔍 INVESTIGATING STREAMING ENDPOINT")
    print("=" * 50)
    
    session, user_id = authenticate()
    if not session:
        return
    
    try:
        print("Testing /api/messages/stream endpoint...")
        response = session.get(f"{API_BASE}/messages/stream", timeout=20)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                print(f"Response Content (first 500 chars):")
                print(json.dumps(data, indent=2)[:500] + "...")
                
                # Check if it has a messages field
                if isinstance(data, dict) and 'messages' in data:
                    messages = data['messages']
                    print(f"\nFound 'messages' field with {len(messages)} items")
                    
                    if messages:
                        print("First message sample:")
                        print(json.dumps(messages[0], indent=2))
                        
                elif isinstance(data, dict) and 'conversations' in data:
                    conversations = data['conversations']
                    print(f"\nFound 'conversations' field with {len(conversations)} items")
                    
            except json.JSONDecodeError:
                print("Response is not valid JSON")
                print(f"Raw response: {response.text[:500]}...")
                
        else:
            print(f"❌ Endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Investigation error: {str(e)}")

def investigate_conversation_endpoints():
    """Investigate all conversation-related endpoints"""
    print("\n🔍 INVESTIGATING CONVERSATION ENDPOINTS")
    print("=" * 50)
    
    session, user_id = authenticate()
    if not session:
        return
    
    endpoints_to_test = [
        "/conversations",
        "/conversation/history", 
        "/simulation/state",
        "/agents"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\nTesting {endpoint}...")
            response = session.get(f"{API_BASE}{endpoint}", timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Type: List with {len(data)} items")
                        if data:
                            print(f"   First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                    elif isinstance(data, dict):
                        print(f"   Type: Dict with keys: {list(data.keys())}")
                        
                        # Special handling for simulation state
                        if endpoint == "/simulation/state":
                            is_active = data.get('is_active', False)
                            scenario = data.get('scenario', '')
                            print(f"   Simulation Active: {is_active}")
                            print(f"   Scenario: {scenario[:50]}...")
                            
                        # Special handling for agents
                        elif endpoint == "/agents":
                            if isinstance(data, list):
                                print(f"   Agent count: {len(data)}")
                            elif 'agents' in data:
                                print(f"   Agent count: {len(data['agents'])}")
                    else:
                        print(f"   Type: {type(data)}")
                        
                except json.JSONDecodeError:
                    print(f"   Response not JSON: {response.text[:100]}...")
                    
            elif response.status_code == 404:
                print(f"   ⚠️ Endpoint not found")
            elif response.status_code == 401:
                print(f"   ⚠️ Authentication required")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error testing {endpoint}: {str(e)}")

def test_conversation_generation_and_storage():
    """Test conversation generation and check if it's stored"""
    print("\n🔍 TESTING CONVERSATION GENERATION & STORAGE")
    print("=" * 50)
    
    session, user_id = authenticate()
    if not session:
        return
    
    # Check baseline
    try:
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        baseline_count = len(response.json()) if response.status_code == 200 and isinstance(response.json(), list) else 0
        print(f"Baseline conversations: {baseline_count}")
    except:
        baseline_count = 0
        print("Could not get baseline conversation count")
    
    # Generate a conversation
    print("\nGenerating conversation...")
    try:
        start_time = time.time()
        response = session.post(f"{API_BASE}/conversation/generate", 
                               json={}, 
                               timeout=90)
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Generation successful in {generation_time:.2f}s")
            
            try:
                data = response.json()
                print(f"Response type: {type(data)}")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                
                # Check if response contains conversation data
                if isinstance(data, dict):
                    if 'conversation' in data:
                        conv = data['conversation']
                        print(f"Conversation ID: {conv.get('id', 'unknown')}")
                        print(f"Messages in response: {len(conv.get('messages', []))}")
                    elif 'messages' in data:
                        print(f"Messages in response: {len(data['messages'])}")
                    elif 'id' in data:
                        print(f"Conversation ID: {data['id']}")
                        
            except json.JSONDecodeError:
                print("Response not JSON")
                
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print(f"⏰ Generation timed out after 90s")
    except Exception as e:
        print(f"❌ Generation error: {str(e)}")
    
    # Check if conversation was stored
    print("\nChecking if conversation was stored...")
    time.sleep(2)  # Wait for database consistency
    
    try:
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                new_count = len(data)
                print(f"New conversation count: {new_count}")
                
                if new_count > baseline_count:
                    print(f"✅ Conversation stored! Increase: {baseline_count} → {new_count}")
                    
                    # Analyze the latest conversation
                    if data:
                        latest = data[-1]  # Assuming sorted by creation time
                        print(f"\nLatest conversation analysis:")
                        print(f"   ID: {latest.get('id', 'unknown')}")
                        print(f"   Round: {latest.get('round_number', 'unknown')}")
                        print(f"   Messages: {len(latest.get('messages', []))}")
                        
                        if 'messages' in latest:
                            agents = [msg.get('agent_name', 'Unknown') for msg in latest['messages']]
                            print(f"   Agent sequence: {' → '.join(agents)}")
                            
                            # Check for alternation issue
                            consecutive = 0
                            for i in range(1, len(agents)):
                                if agents[i] == agents[i-1]:
                                    consecutive += 1
                            
                            if consecutive > 0:
                                print(f"   🚨 Alternation issue: {consecutive} consecutive same-agent messages")
                            else:
                                print(f"   ✅ Good alternation: No consecutive same-agent messages")
                else:
                    print(f"⚠️ No new conversations stored: {baseline_count} → {new_count}")
            else:
                print(f"⚠️ Conversations endpoint returned {type(data)}, not list")
        else:
            print(f"❌ Cannot check conversations: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Storage check error: {str(e)}")

def main():
    """Run detailed investigation"""
    print("🔍 DETAILED INVESTIGATION OF STREAMING AND DATABASE ISSUES")
    print("=" * 70)
    print("Investigating:")
    print("- What streaming endpoint actually returns")
    print("- All conversation-related endpoints")
    print("- Conversation generation and storage process")
    print("=" * 70)
    
    investigate_streaming_endpoint()
    investigate_conversation_endpoints()
    test_conversation_generation_and_storage()
    
    print("\n" + "=" * 70)
    print("🔍 DETAILED INVESTIGATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()