#!/usr/bin/env python3
"""
Quick Observer Message Test - Focus on the specific issue
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔗 Testing Observer Message Functionality")
print(f"API URL: {API_URL}")
print("-" * 50)

def test_with_timeout(test_name, func, timeout=30):
    """Test with timeout to detect hanging issues"""
    print(f"\n🧪 {test_name}")
    start_time = time.time()
    
    try:
        result = func()
        response_time = time.time() - start_time
        print(f"   ✅ SUCCESS ({response_time:.2f}s)")
        return result, response_time
    except Exception as e:
        response_time = time.time() - start_time
        print(f"   ❌ FAILED ({response_time:.2f}s): {str(e)}")
        return None, response_time

def authenticate():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data["access_token"], data["user"]["id"]
    else:
        raise Exception(f"Auth failed: {response.status_code}")

def reset_simulation(token):
    """Reset simulation state"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Reset failed: {response.status_code}")
    return True

def create_agents(token):
    """Create test agents"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Analyze signals",
            "expertise": "Signal Processing"
        },
        {
            "name": "Commander Alex",
            "archetype": "leader", 
            "goal": "Lead team",
            "expertise": "Command"
        }
    ]
    
    agent_ids = []
    for agent_data in agents:
        response = requests.post(f"{API_URL}/agents", headers=headers, json=agent_data, timeout=10)
        if response.status_code == 200:
            agent_ids.append(response.json()["id"])
        else:
            raise Exception(f"Agent creation failed: {response.status_code}")
    
    return agent_ids

def send_observer_message(token):
    """Send observer message - this is the critical test"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "observer_message": "Hello team, let's discuss the deep space signal discovery."
    }
    
    print(f"   Sending observer message...")
    response = requests.post(f"{API_URL}/observer/send-message", 
                           headers=headers, 
                           json=payload,
                           timeout=45)  # 45 second timeout to detect hanging
    
    if response.status_code == 200:
        data = response.json()
        
        # Validate response structure
        if "agent_responses" not in data:
            raise Exception("Missing agent_responses field")
        
        agent_responses = data["agent_responses"]
        if "messages" not in agent_responses:
            raise Exception("Missing messages in agent_responses")
        
        messages = agent_responses["messages"]
        if not isinstance(messages, list) or len(messages) == 0:
            raise Exception(f"Invalid messages: {len(messages) if isinstance(messages, list) else 'not a list'}")
        
        # Count agent responses
        agent_count = len([msg for msg in messages if msg.get("agent_name") != "Observer (You)"])
        
        print(f"   📊 Response structure: ✅")
        print(f"   📊 Total messages: {len(messages)}")
        print(f"   📊 Agent responses: {agent_count}")
        
        return data
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

def test_error_handling(token):
    """Test error handling"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test empty message
    response = requests.post(f"{API_URL}/observer/send-message", 
                           headers=headers, 
                           json={"observer_message": ""},
                           timeout=10)
    
    if response.status_code != 400:
        raise Exception(f"Expected 400 for empty message, got {response.status_code}")
    
    # Test no auth
    response = requests.post(f"{API_URL}/observer/send-message", 
                           json={"observer_message": "test"},
                           timeout=10)
    
    if response.status_code != 403:
        raise Exception(f"Expected 403 for no auth, got {response.status_code}")
    
    return True

def main():
    """Main test execution"""
    total_time = time.time()
    
    # Step 1: Authentication
    token, user_id = test_with_timeout("Guest Authentication", authenticate, 10)[0:2]
    if not token:
        print("❌ Cannot proceed without token")
        return False
    
    # Step 2: Reset simulation
    test_with_timeout("Simulation Reset", lambda: reset_simulation(token), 10)
    
    # Step 3: Create agents
    agent_ids = test_with_timeout("Create Agents", lambda: create_agents(token), 20)[0]
    if not agent_ids or len(agent_ids) < 2:
        print("❌ Need at least 2 agents")
        return False
    
    print(f"   📊 Created {len(agent_ids)} agents")
    
    # Step 4: CRITICAL TEST - Send observer message
    observer_response, response_time = test_with_timeout(
        "Send Observer Message (CRITICAL)", 
        lambda: send_observer_message(token), 
        45
    )
    
    if observer_response:
        print(f"   🎯 OBSERVER MESSAGE SUCCESS!")
        print(f"   ⏱️  Response time: {response_time:.2f}s")
        
        if response_time > 30:
            print(f"   ⚠️  WARNING: Response time >30s (review requirement)")
        else:
            print(f"   ✅ Response time within 30s requirement")
    else:
        print(f"   🚨 OBSERVER MESSAGE FAILED!")
        print(f"   🚨 This confirms the 'sending stuck' issue from the review")
    
    # Step 5: Error handling
    test_with_timeout("Error Handling", lambda: test_error_handling(token), 15)
    
    total_elapsed = time.time() - total_time
    print(f"\n" + "="*50)
    print(f"🎯 FINAL ASSESSMENT")
    print(f"="*50)
    print(f"⏱️  Total test time: {total_elapsed:.2f}s")
    
    if observer_response:
        print(f"✅ Observer message functionality is WORKING")
        print(f"✅ No 'sending stuck' issue detected")
        print(f"✅ Response structure is correct")
        print(f"✅ Authentication working properly")
        
        if response_time <= 30:
            print(f"✅ Performance meets requirements (≤30s)")
        else:
            print(f"⚠️  Performance issue: {response_time:.2f}s > 30s")
    else:
        print(f"🚨 Observer message functionality has ISSUES")
        print(f"🚨 Potential 'sending stuck' problem confirmed")
    
    return observer_response is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)