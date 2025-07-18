#!/usr/bin/env python3
"""
Observer Message Conversation Generation Debug Test

This test specifically addresses the issue reported where agents stop talking 
after observer messages are sent. The user reports that after sending 2 observer 
messages, agents stop generating conversations automatically even though the 
simulation is still running.

Test Flow:
1. Setup (authenticate, reset simulation, create 3 agents, start simulation)
2. Test normal conversation generation (2 regular conversations)
3. Test observer message impact (send observer message, check simulation state, try generating another conversation)
4. Test multiple observer messages (send another observer message, check state, try generating conversation)
5. Check simulation state throughout
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
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔧 Using API URL: {API_URL}")

# Test tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def make_request(method, endpoint, data=None, headers=None, timeout=30):
    """Make HTTP request with error handling"""
    url = f"{API_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        
        return response
    except requests.exceptions.Timeout:
        print(f"⚠️  Request timeout for {method} {endpoint}")
        return None
    except Exception as e:
        print(f"⚠️  Request error for {method} {endpoint}: {e}")
        return None

def test_guest_authentication():
    """Test guest authentication"""
    print("\n🔐 Testing Guest Authentication...")
    
    response = make_request("POST", "/auth/test-login")
    
    if not response:
        log_test("Guest Authentication", False, "Request failed")
        return None
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data and "user" in data:
            log_test("Guest Authentication", True, f"Token received, user_id: {data['user']['id']}")
            return data["access_token"], data["user"]["id"]
        else:
            log_test("Guest Authentication", False, "Missing access_token or user in response")
            return None
    else:
        log_test("Guest Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_simulation_reset(headers):
    """Test simulation reset"""
    print("\n🔄 Testing Simulation Reset...")
    
    response = make_request("POST", "/simulation/reset", headers=headers)
    
    if not response:
        log_test("Simulation Reset", False, "Request failed")
        return False
    
    if response.status_code == 200:
        log_test("Simulation Reset", True, "Simulation reset successfully")
        return True
    else:
        log_test("Simulation Reset", False, f"Status: {response.status_code}, Response: {response.text}")
        return False

def test_agent_creation(headers, count=3):
    """Create test agents"""
    print(f"\n🤖 Creating {count} Test Agents...")
    
    agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics",
            "background": "PhD in Quantum Physics, 10 years research experience"
        },
        {
            "name": "Marcus Johnson",
            "archetype": "leader", 
            "goal": "Lead successful project implementation",
            "expertise": "Project Management",
            "background": "Senior Project Manager with 15 years experience"
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "optimist",
            "goal": "Foster team collaboration and innovation",
            "expertise": "Team Dynamics",
            "background": "Organizational Psychology specialist"
        }
    ]
    
    created_agents = []
    
    for i, agent_data in enumerate(agents[:count]):
        response = make_request("POST", "/agents", data=agent_data, headers=headers)
        
        if response and response.status_code == 200:
            agent = response.json()
            created_agents.append(agent)
            log_test(f"Create Agent {i+1} ({agent_data['name']})", True, f"Agent ID: {agent['id']}")
        else:
            status = response.status_code if response else "No response"
            log_test(f"Create Agent {i+1} ({agent_data['name']})", False, f"Status: {status}")
    
    return created_agents

def test_simulation_start(headers):
    """Test simulation start"""
    print("\n▶️ Testing Simulation Start...")
    
    response = make_request("POST", "/simulation/start", headers=headers)
    
    if not response:
        log_test("Simulation Start", False, "Request failed")
        return False
    
    if response.status_code == 200:
        log_test("Simulation Start", True, "Simulation started successfully")
        return True
    else:
        log_test("Simulation Start", False, f"Status: {response.status_code}, Response: {response.text}")
        return False

def check_simulation_state(headers, expected_active=True):
    """Check simulation state"""
    print(f"\n📊 Checking Simulation State (expecting is_active={expected_active})...")
    
    response = make_request("GET", "/simulation/state", headers=headers)
    
    if not response:
        log_test("Check Simulation State", False, "Request failed")
        return None
    
    if response.status_code == 200:
        state = response.json()
        is_active = state.get("is_active", False)
        
        if is_active == expected_active:
            log_test("Check Simulation State", True, f"is_active={is_active} as expected")
        else:
            log_test("Check Simulation State", False, f"is_active={is_active}, expected {expected_active}")
        
        return state
    else:
        log_test("Check Simulation State", False, f"Status: {response.status_code}")
        return None

def test_conversation_generation(headers, test_name="Conversation Generation"):
    """Test conversation generation"""
    print(f"\n💬 Testing {test_name}...")
    
    response = make_request("POST", "/conversation/generate", headers=headers, timeout=45)
    
    if not response:
        log_test(test_name, False, "Request failed or timed out")
        return None
    
    if response.status_code == 200:
        conversation = response.json()
        message_count = len(conversation.get("messages", []))
        log_test(test_name, True, f"Generated conversation with {message_count} messages")
        return conversation
    else:
        log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_observer_message(headers, message, test_name="Observer Message"):
    """Test sending observer message"""
    print(f"\n👁️ Testing {test_name}: '{message}'...")
    
    data = {"observer_message": message}
    response = make_request("POST", "/observer/send-message", data=data, headers=headers, timeout=45)
    
    if not response:
        log_test(test_name, False, "Request failed or timed out")
        return None
    
    if response.status_code == 200:
        result = response.json()
        agent_responses = result.get("agent_responses", {})
        message_count = len(agent_responses.get("messages", []))
        log_test(test_name, True, f"Observer message sent, {message_count} agent responses received")
        return result
    else:
        log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def get_conversation_count(headers):
    """Get current conversation count"""
    response = make_request("GET", "/conversations", headers=headers)
    
    if response and response.status_code == 200:
        conversations = response.json()
        return len(conversations)
    return 0

def main():
    """Main test function"""
    print("🚀 OBSERVER MESSAGE CONVERSATION GENERATION DEBUG TEST")
    print("=" * 60)
    print("Testing the reported issue where agents stop talking after observer messages")
    
    # Step 1: Setup - Authentication
    auth_result = test_guest_authentication()
    if not auth_result:
        print("❌ Authentication failed - cannot continue")
        return
    
    token, user_id = auth_result
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Setup - Reset simulation
    if not test_simulation_reset(headers):
        print("❌ Simulation reset failed - cannot continue")
        return
    
    # Step 3: Setup - Create 3 agents
    agents = test_agent_creation(headers, 3)
    if len(agents) < 3:
        print("❌ Failed to create required agents - cannot continue")
        return
    
    # Step 4: Setup - Start simulation
    if not test_simulation_start(headers):
        print("❌ Simulation start failed - cannot continue")
        return
    
    # Step 5: Check initial simulation state
    initial_state = check_simulation_state(headers, expected_active=True)
    if not initial_state or not initial_state.get("is_active"):
        print("❌ Simulation not active after start - cannot continue")
        return
    
    print(f"\n📈 Initial conversation count: {get_conversation_count(headers)}")
    
    # Step 6: Test Normal Conversation Generation (2 conversations)
    print("\n" + "="*50)
    print("PHASE 1: NORMAL CONVERSATION GENERATION")
    print("="*50)
    
    conv1 = test_conversation_generation(headers, "Normal Conversation #1")
    time.sleep(2)  # Brief pause between requests
    
    conv2 = test_conversation_generation(headers, "Normal Conversation #2")
    time.sleep(2)
    
    if not conv1 or not conv2:
        print("❌ Normal conversation generation failed - cannot continue")
        return
    
    print(f"📈 Conversation count after normal generation: {get_conversation_count(headers)}")
    
    # Check simulation state after normal conversations
    state_after_normal = check_simulation_state(headers, expected_active=True)
    
    # Step 7: Test Observer Message Impact
    print("\n" + "="*50)
    print("PHASE 2: FIRST OBSERVER MESSAGE IMPACT")
    print("="*50)
    
    observer_msg1 = test_observer_message(headers, "Hello agents! Please focus on finding practical solutions.", "First Observer Message")
    
    if not observer_msg1:
        print("❌ First observer message failed")
        return
    
    print(f"📈 Conversation count after first observer message: {get_conversation_count(headers)}")
    
    # Check simulation state after first observer message
    state_after_observer1 = check_simulation_state(headers, expected_active=True)
    
    # Try to generate conversation after first observer message
    time.sleep(2)
    conv_after_observer1 = test_conversation_generation(headers, "Conversation After First Observer Message")
    
    print(f"📈 Conversation count after post-observer generation: {get_conversation_count(headers)}")
    
    # Step 8: Test Multiple Observer Messages
    print("\n" + "="*50)
    print("PHASE 3: SECOND OBSERVER MESSAGE IMPACT")
    print("="*50)
    
    observer_msg2 = test_observer_message(headers, "Great work! Now let's prioritize the most critical tasks.", "Second Observer Message")
    
    if not observer_msg2:
        print("❌ Second observer message failed")
        return
    
    print(f"📈 Conversation count after second observer message: {get_conversation_count(headers)}")
    
    # Check simulation state after second observer message
    state_after_observer2 = check_simulation_state(headers, expected_active=True)
    
    # Try to generate conversation after second observer message
    time.sleep(2)
    conv_after_observer2 = test_conversation_generation(headers, "Conversation After Second Observer Message")
    
    print(f"📈 Final conversation count: {get_conversation_count(headers)}")
    
    # Step 9: Test Continuous Generation
    print("\n" + "="*50)
    print("PHASE 4: CONTINUOUS GENERATION TEST")
    print("="*50)
    
    # Try generating one more conversation to test continuous capability
    time.sleep(2)
    conv_continuous = test_conversation_generation(headers, "Continuous Generation Test")
    
    # Final state check
    final_state = check_simulation_state(headers, expected_active=True)
    
    # Step 10: Analysis and Summary
    print("\n" + "="*60)
    print("ANALYSIS & SUMMARY")
    print("="*60)
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    print(f"   ✅ Passed: {test_results['passed']}")
    print(f"   ❌ Failed: {test_results['failed']}")
    print(f"   📈 Total Tests: {test_results['passed'] + test_results['failed']}")
    
    print(f"\n🔍 CONVERSATION GENERATION ANALYSIS:")
    successful_generations = [
        conv1 is not None,
        conv2 is not None, 
        conv_after_observer1 is not None,
        conv_after_observer2 is not None,
        conv_continuous is not None
    ]
    
    print(f"   Normal Conversation #1: {'✅' if conv1 else '❌'}")
    print(f"   Normal Conversation #2: {'✅' if conv2 else '❌'}")
    print(f"   After First Observer Message: {'✅' if conv_after_observer1 else '❌'}")
    print(f"   After Second Observer Message: {'✅' if conv_after_observer2 else '❌'}")
    print(f"   Continuous Generation Test: {'✅' if conv_continuous else '❌'}")
    
    print(f"\n🎯 SIMULATION STATE ANALYSIS:")
    states = [initial_state, state_after_normal, state_after_observer1, state_after_observer2, final_state]
    all_active = all(state and state.get("is_active") for state in states if state)
    print(f"   Simulation remained active throughout: {'✅' if all_active else '❌'}")
    
    print(f"\n🚨 ISSUE DIAGNOSIS:")
    if all(successful_generations):
        print("   ✅ NO ISSUE DETECTED: All conversation generations succeeded")
        print("   ✅ Observer messages do not prevent continuous conversation generation")
    else:
        print("   ❌ ISSUE CONFIRMED: Some conversation generations failed")
        failed_after_observer = not (conv_after_observer1 and conv_after_observer2)
        if failed_after_observer:
            print("   🔍 SPECIFIC ISSUE: Conversation generation fails after observer messages")
        
        if not all_active:
            print("   🔍 POTENTIAL CAUSE: Simulation state becomes inactive")
        else:
            print("   🔍 POTENTIAL CAUSE: Backend logic prevents generation despite active state")
    
    print(f"\n📋 DETAILED TEST LOG:")
    for test in test_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"   {status} {test['name']}: {test['details']}")

if __name__ == "__main__":
    main()