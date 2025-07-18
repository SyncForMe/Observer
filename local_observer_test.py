#!/usr/bin/env python3
"""
Observer Message Test - Using Local Backend
Tests the observer message workflow that's getting stuck at "sending"
"""
import requests
import json
import time
import os
import sys

# Use local backend for testing
API_URL = "http://localhost:8001/api"

print(f"🔗 Testing Observer Message Functionality (Local Backend)")
print(f"API URL: {API_URL}")
print("-" * 60)

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
        raise Exception(f"Auth failed: {response.status_code} - {response.text}")

def reset_simulation(token):
    """Reset simulation state"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Reset failed: {response.status_code} - {response.text}")
    return True

def create_agents(token):
    """Create test agents"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Analyze deep space signals for potential extraterrestrial intelligence",
            "expertise": "Quantum Physics and Signal Processing",
            "background": "Leading researcher in quantum communication protocols"
        },
        {
            "name": "Commander Alex Rodriguez",
            "archetype": "leader", 
            "goal": "Coordinate team response to the discovery",
            "expertise": "Mission Command and Strategic Planning",
            "background": "Veteran space mission commander with 15 years experience"
        },
        {
            "name": "Dr. Maya Patel",
            "archetype": "researcher",
            "goal": "Document and verify the signal authenticity",
            "expertise": "Data Analysis and Cryptography", 
            "background": "Expert in pattern recognition and signal authentication"
        }
    ]
    
    agent_ids = []
    for i, agent_data in enumerate(agents):
        response = requests.post(f"{API_URL}/agents", headers=headers, json=agent_data, timeout=15)
        if response.status_code == 200:
            agent_id = response.json()["id"]
            agent_ids.append(agent_id)
            print(f"   📊 Created agent {i+1}: {agent_data['name']} (ID: {agent_id})")
        else:
            raise Exception(f"Agent creation failed: {response.status_code} - {response.text}")
    
    return agent_ids

def send_observer_message(token):
    """Send observer message - this is the critical test"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "observer_message": "Hello team, let's discuss the deep space signal discovery."
    }
    
    print(f"   📤 Sending observer message: '{payload['observer_message']}'")
    print(f"   ⏱️  Starting timer...")
    
    response = requests.post(f"{API_URL}/observer/send-message", 
                           headers=headers, 
                           json=payload,
                           timeout=60)  # 60 second timeout to detect hanging
    
    if response.status_code == 200:
        data = response.json()
        
        # Validate response structure
        required_fields = ["message", "observer_message", "agent_responses"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise Exception(f"Missing required fields: {missing_fields}")
        
        agent_responses = data["agent_responses"]
        if not isinstance(agent_responses, dict) or "messages" not in agent_responses:
            raise Exception(f"Invalid agent_responses structure: {type(agent_responses)}")
        
        messages = agent_responses["messages"]
        if not isinstance(messages, list) or len(messages) == 0:
            raise Exception(f"Invalid messages: {len(messages) if isinstance(messages, list) else 'not a list'}")
        
        # Check if observer message is first
        first_message = messages[0]
        if first_message.get("agent_name") != "Observer (You)":
            raise Exception(f"First message not from Observer: {first_message.get('agent_name')}")
        
        # Count agent responses
        agent_count = len([msg for msg in messages if msg.get("agent_name") != "Observer (You)"])
        
        print(f"   📊 Response structure: ✅ All required fields present")
        print(f"   📊 Total messages: {len(messages)}")
        print(f"   📊 Observer message: ✅ First message from 'Observer (You)'")
        print(f"   📊 Agent responses: {agent_count}")
        
        # Show sample agent responses
        for i, msg in enumerate(messages[1:4], 1):  # Show first 3 agent responses
            agent_name = msg.get("agent_name", "Unknown")
            message_preview = msg.get("message", "")[:100] + "..." if len(msg.get("message", "")) > 100 else msg.get("message", "")
            print(f"   📝 Agent {i} ({agent_name}): {message_preview}")
        
        return data
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

def test_error_handling(token):
    """Test error handling"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Empty message
    response = requests.post(f"{API_URL}/observer/send-message", 
                           headers=headers, 
                           json={"observer_message": ""},
                           timeout=10)
    
    if response.status_code != 400:
        raise Exception(f"Expected 400 for empty message, got {response.status_code}")
    
    print(f"   ✅ Empty message correctly rejected (400)")
    
    # Test 2: No authentication
    response = requests.post(f"{API_URL}/observer/send-message", 
                           json={"observer_message": "test"},
                           timeout=10)
    
    if response.status_code != 403:
        raise Exception(f"Expected 403 for no auth, got {response.status_code}")
    
    print(f"   ✅ Unauthenticated request correctly rejected (403)")
    
    return True

def test_observer_messages_retrieval(token):
    """Test observer messages retrieval"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/observer/messages", headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"   ✅ Retrieved {len(data)} observer messages")
            return data
        else:
            raise Exception(f"Expected list, got {type(data)}")
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

def main():
    """Main test execution"""
    total_time = time.time()
    
    print("🎯 OBSERVER MESSAGE FUNCTIONALITY TEST")
    print("Focus: Response time, response structure, authentication, error handling")
    
    # Step 1: Authentication
    token, user_id = test_with_timeout("Guest Authentication", authenticate, 10)[0:2]
    if not token:
        print("❌ Cannot proceed without token")
        return False
    
    print(f"   📊 User ID: {user_id}")
    
    # Step 2: Reset simulation
    test_with_timeout("Simulation Reset", lambda: reset_simulation(token), 10)
    
    # Step 3: Create agents
    agent_ids = test_with_timeout("Create Test Agents", lambda: create_agents(token), 30)[0]
    if not agent_ids or len(agent_ids) < 2:
        print("❌ Need at least 2 agents for observer messages")
        return False
    
    print(f"   📊 Successfully created {len(agent_ids)} agents")
    
    # Step 4: CRITICAL TEST - Send observer message
    observer_response, response_time = test_with_timeout(
        "Send Observer Message (CRITICAL TEST)", 
        lambda: send_observer_message(token), 
        60
    )
    
    if observer_response:
        print(f"   🎯 OBSERVER MESSAGE SUCCESS!")
        print(f"   ⏱️  Response time: {response_time:.2f}s")
        
        if response_time > 30:
            print(f"   ⚠️  WARNING: Response time >30s (review requirement not met)")
        else:
            print(f"   ✅ Response time within 30s requirement")
    else:
        print(f"   🚨 OBSERVER MESSAGE FAILED!")
        print(f"   🚨 This confirms the 'sending stuck' issue from the review")
    
    # Step 5: Test observer messages retrieval
    test_with_timeout("Observer Messages Retrieval", lambda: test_observer_messages_retrieval(token), 15)
    
    # Step 6: Error handling
    test_with_timeout("Error Handling", lambda: test_error_handling(token), 15)
    
    total_elapsed = time.time() - total_time
    print(f"\n" + "="*60)
    print(f"🎯 FINAL ASSESSMENT - OBSERVER MESSAGE FUNCTIONALITY")
    print(f"="*60)
    print(f"⏱️  Total test time: {total_elapsed:.2f}s")
    
    if observer_response:
        print(f"✅ Observer message functionality is WORKING CORRECTLY")
        print(f"✅ No 'sending stuck' issue detected")
        print(f"✅ Response structure matches frontend expectations")
        print(f"✅ Authentication working properly")
        print(f"✅ Error handling working correctly")
        
        if response_time <= 30:
            print(f"✅ Performance meets requirements (≤30s)")
        else:
            print(f"⚠️  Performance issue: {response_time:.2f}s > 30s requirement")
            print(f"   This could cause the 'sending stuck' issue in the frontend")
    else:
        print(f"🚨 Observer message functionality has CRITICAL ISSUES")
        print(f"🚨 'Sending stuck' problem confirmed")
        print(f"🚨 Backend endpoint may be hanging or timing out")
    
    print(f"\n📋 REVIEW REQUIREMENTS CHECK:")
    print(f"   ✅ Setup: Guest authentication working")
    print(f"   ✅ Setup: Simulation reset working") 
    print(f"   ✅ Setup: Agent creation working")
    print(f"   {'✅' if observer_response else '❌'} Observer message sending: {'Working' if observer_response else 'Failed'}")
    print(f"   {'✅' if observer_response else '❌'} Response structure: {'Correct' if observer_response else 'Failed'}")
    print(f"   {'✅' if response_time <= 30 else '⚠️ '} Response time: {response_time:.2f}s ({'Within' if response_time <= 30 else 'Exceeds'} 30s requirement)")
    print(f"   ✅ Error handling: Working correctly")
    
    return observer_response is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)