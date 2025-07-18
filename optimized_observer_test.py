#!/usr/bin/env python3
"""
Comprehensive test script for the optimized observer message functionality.

Tests the key optimizations:
1. Instant sending - Observer messages should send instantly without getting stuck on "sending"
2. Proper positioning - Observer messages should appear chronologically in the conversation flow
3. No duplicate messages - Fixed issue where observer messages were appearing twice
4. Proper integration - Observer messages create conversation objects instead of separate state
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
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
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

def test_guest_authentication():
    """Test guest authentication for observer message testing"""
    print("\n🔐 Testing Guest Authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data and 'user' in data:
                log_test("Guest Authentication", True, f"Token received, user_id: {data['user']['id']}")
                return data['access_token'], data['user']['id']
            else:
                log_test("Guest Authentication", False, "Missing access_token or user in response")
                return None, None
        else:
            log_test("Guest Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
            return None, None
            
    except Exception as e:
        log_test("Guest Authentication", False, f"Exception: {str(e)}")
        return None, None

def create_test_agents(token, user_id):
    """Create 2-3 test agents for observer message testing"""
    print("\n🤖 Creating Test Agents...")
    
    headers = {"Authorization": f"Bearer {token}"}
    agents = []
    
    test_agents_data = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics, 10 years research experience"
        },
        {
            "name": "Marcus Johnson",
            "archetype": "leader", 
            "goal": "Lead successful project execution",
            "expertise": "Project Management and Strategy",
            "background": "MBA, 15 years leading tech projects"
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "artist",
            "goal": "Create innovative user experiences",
            "expertise": "UX Design and Creative Strategy", 
            "background": "Design lead with focus on human-centered solutions"
        }
    ]
    
    for agent_data in test_agents_data:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                agent = response.json()
                agents.append(agent)
                log_test(f"Create Agent: {agent_data['name']}", True, f"Agent ID: {agent['id']}")
            else:
                log_test(f"Create Agent: {agent_data['name']}", False, f"Status: {response.status_code}")
                
        except Exception as e:
            log_test(f"Create Agent: {agent_data['name']}", False, f"Exception: {str(e)}")
    
    return agents

def start_simulation(token):
    """Start simulation for observer message testing"""
    print("\n▶️ Starting Simulation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Start Simulation", True, f"Simulation active: {data.get('is_active', False)}")
            return True
        else:
            log_test("Start Simulation", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Start Simulation", False, f"Exception: {str(e)}")
        return False

def test_observer_message_instant_sending(token):
    """Test that observer messages send instantly without getting stuck"""
    print("\n⚡ Testing Instant Observer Message Sending...")
    
    headers = {"Authorization": f"Bearer {token}"}
    observer_message = "Hello team, let's begin our quantum computing discussion"
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": observer_message},
            headers=headers,
            timeout=15
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            has_message = 'message' in data
            has_observer_message = 'observer_message' in data
            has_agent_responses = 'agent_responses' in data
            
            # Check response time (should be fast for instant sending)
            is_fast_response = response_time < 10.0  # Should complete within 10 seconds
            
            # Check observer message content
            observer_msg_correct = data.get('observer_message') == observer_message
            
            # Check agent responses structure
            agent_responses = data.get('agent_responses', {})
            has_scenario_name = agent_responses.get('scenario_name') == "Observer Guidance"
            has_messages = 'messages' in agent_responses and len(agent_responses['messages']) > 0
            
            # Check that observer message appears first
            messages = agent_responses.get('messages', [])
            observer_first = False
            if messages:
                first_message = messages[0]
                observer_first = (first_message.get('agent_name') == 'Observer (You)' and 
                                first_message.get('message') == observer_message)
            
            all_checks_passed = (has_message and has_observer_message and has_agent_responses and 
                               is_fast_response and observer_msg_correct and has_scenario_name and 
                               has_messages and observer_first)
            
            details = f"Response time: {response_time:.2f}s, Messages: {len(messages)}, Observer first: {observer_first}, Scenario: {agent_responses.get('scenario_name')}"
            log_test("Observer Message Instant Sending", all_checks_passed, details)
            
            return data if all_checks_passed else None
            
        else:
            log_test("Observer Message Instant Sending", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Observer Message Instant Sending", False, f"Exception: {str(e)}")
        return None

def test_conversation_integration(token):
    """Test that observer messages integrate properly with conversation flow"""
    print("\n💬 Testing Conversation Integration...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # First, generate a regular conversation
        print("   Generating regular conversation...")
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=15)
        
        if conv_response.status_code != 200:
            log_test("Regular Conversation Generation", False, f"Status: {conv_response.status_code}")
            return False
        
        # Get conversations before observer message
        conversations_before = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if conversations_before.status_code != 200:
            log_test("Get Conversations Before", False, f"Status: {conversations_before.status_code}")
            return False
        
        conv_count_before = len(conversations_before.json())
        
        # Send observer message
        print("   Sending observer message...")
        observer_response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": "Great progress, keep going with the quantum research"},
            headers=headers,
            timeout=15
        )
        
        if observer_response.status_code != 200:
            log_test("Observer Message in Integration", False, f"Status: {observer_response.status_code}")
            return False
        
        # Get conversations after observer message
        time.sleep(1)  # Brief pause to ensure data consistency
        conversations_after = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if conversations_after.status_code != 200:
            log_test("Get Conversations After", False, f"Status: {conversations_after.status_code}")
            return False
        
        conv_count_after = len(conversations_after.json())
        conversations_data = conversations_after.json()
        
        # Check that observer message created a new conversation
        new_conversation_created = conv_count_after > conv_count_before
        
        # Find the observer conversation
        observer_conversation = None
        for conv in conversations_data:
            if conv.get('scenario_name') == 'Observer Guidance':
                observer_conversation = conv
                break
        
        has_observer_conversation = observer_conversation is not None
        
        # Check chronological ordering (newer conversations should have later timestamps)
        chronological_order = True
        if len(conversations_data) > 1:
            # Sort by created_at to check order
            sorted_convs = sorted(conversations_data, key=lambda x: x.get('created_at', ''))
            chronological_order = sorted_convs == conversations_data
        
        all_checks_passed = new_conversation_created and has_observer_conversation and chronological_order
        
        details = f"Conversations before: {conv_count_before}, after: {conv_count_after}, Observer conv found: {has_observer_conversation}, Chronological: {chronological_order}"
        log_test("Conversation Integration", all_checks_passed, details)
        
        return all_checks_passed
        
    except Exception as e:
        log_test("Conversation Integration", False, f"Exception: {str(e)}")
        return False

def test_multiple_observer_messages(token):
    """Test sending multiple observer messages in sequence"""
    print("\n🔄 Testing Multiple Observer Messages...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    observer_messages = [
        "Let's focus on the technical implementation details",
        "What are the key risks we need to address?",
        "Please summarize our main conclusions so far"
    ]
    
    try:
        # Get initial conversation count
        initial_convs = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if initial_convs.status_code != 200:
            log_test("Get Initial Conversations", False, f"Status: {initial_convs.status_code}")
            return False
        
        initial_count = len(initial_convs.json())
        observer_responses = []
        
        # Send multiple observer messages
        for i, message in enumerate(observer_messages, 1):
            print(f"   Sending observer message {i}: {message[:30]}...")
            
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": message},
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                observer_responses.append(response.json())
                log_test(f"Observer Message {i}", True, f"Message sent successfully")
            else:
                log_test(f"Observer Message {i}", False, f"Status: {response.status_code}")
                return False
            
            time.sleep(0.5)  # Brief pause between messages
        
        # Get final conversation count
        time.sleep(1)  # Ensure all data is persisted
        final_convs = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if final_convs.status_code != 200:
            log_test("Get Final Conversations", False, f"Status: {final_convs.status_code}")
            return False
        
        final_count = len(final_convs.json())
        final_conversations = final_convs.json()
        
        # Check that each observer message created a separate conversation
        expected_new_conversations = len(observer_messages)
        actual_new_conversations = final_count - initial_count
        separate_conversations_created = actual_new_conversations >= expected_new_conversations
        
        # Count observer guidance conversations
        observer_guidance_count = sum(1 for conv in final_conversations if conv.get('scenario_name') == 'Observer Guidance')
        
        # Check that each response has proper structure
        all_responses_valid = True
        for i, response in enumerate(observer_responses):
            agent_responses = response.get('agent_responses', {})
            has_correct_scenario = agent_responses.get('scenario_name') == 'Observer Guidance'
            has_messages = len(agent_responses.get('messages', [])) > 0
            
            if not (has_correct_scenario and has_messages):
                all_responses_valid = False
                break
        
        # Check for no duplicate messages (each observer message should appear only once)
        no_duplicates = True
        message_counts = {}
        for conv in final_conversations:
            if conv.get('scenario_name') == 'Observer Guidance':
                messages = conv.get('messages', [])
                for msg in messages:
                    if msg.get('agent_name') == 'Observer (You)':
                        content = msg.get('message', '')
                        message_counts[content] = message_counts.get(content, 0) + 1
        
        # Check that no observer message appears more than once
        for content, count in message_counts.items():
            if count > 1:
                no_duplicates = False
                break
        
        all_checks_passed = (separate_conversations_created and all_responses_valid and 
                           observer_guidance_count >= expected_new_conversations and no_duplicates)
        
        details = f"Initial: {initial_count}, Final: {final_count}, New: {actual_new_conversations}, Observer guidance: {observer_guidance_count}, No duplicates: {no_duplicates}"
        log_test("Multiple Observer Messages", all_checks_passed, details)
        
        return all_checks_passed
        
    except Exception as e:
        log_test("Multiple Observer Messages", False, f"Exception: {str(e)}")
        return False

def test_no_duplicate_messages(token):
    """Test that observer messages don't appear twice"""
    print("\n🚫 Testing No Duplicate Messages...")
    
    headers = {"Authorization": f"Bearer {token}"}
    unique_message = f"Unique test message at {datetime.now().strftime('%H:%M:%S')}"
    
    try:
        # Send observer message
        response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": unique_message},
            headers=headers,
            timeout=15
        )
        
        if response.status_code != 200:
            log_test("Send Unique Observer Message", False, f"Status: {response.status_code}")
            return False
        
        # Get all conversations
        time.sleep(1)
        conversations = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if conversations.status_code != 200:
            log_test("Get Conversations for Duplicate Check", False, f"Status: {conversations.status_code}")
            return False
        
        conversations_data = conversations.json()
        
        # Count occurrences of the unique message
        message_occurrences = 0
        for conv in conversations_data:
            messages = conv.get('messages', [])
            for msg in messages:
                if msg.get('message') == unique_message and msg.get('agent_name') == 'Observer (You)':
                    message_occurrences += 1
        
        # Should appear exactly once
        no_duplicates = message_occurrences == 1
        
        details = f"Unique message occurrences: {message_occurrences} (expected: 1)"
        log_test("No Duplicate Messages", no_duplicates, details)
        
        return no_duplicates
        
    except Exception as e:
        log_test("No Duplicate Messages", False, f"Exception: {str(e)}")
        return False

def test_chronological_ordering(token):
    """Test that observer messages appear in chronological order"""
    print("\n📅 Testing Chronological Ordering...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get all conversations
        conversations = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if conversations.status_code != 200:
            log_test("Get Conversations for Chronological Check", False, f"Status: {conversations.status_code}")
            return False
        
        conversations_data = conversations.json()
        
        if len(conversations_data) < 2:
            log_test("Chronological Ordering", True, "Not enough conversations to test ordering (need at least 2)")
            return True
        
        # Check that conversations are ordered by creation time
        timestamps = []
        for conv in conversations_data:
            created_at = conv.get('created_at')
            if created_at:
                # Parse timestamp
                try:
                    if isinstance(created_at, str):
                        # Handle ISO format timestamp
                        timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromisoformat(str(created_at))
                    timestamps.append(timestamp)
                except:
                    # If parsing fails, use current time as fallback
                    timestamps.append(datetime.now())
        
        # Check if timestamps are in descending order (newest first)
        is_chronological = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
        
        details = f"Conversations: {len(conversations_data)}, Chronologically ordered: {is_chronological}"
        log_test("Chronological Ordering", is_chronological, details)
        
        return is_chronological
        
    except Exception as e:
        log_test("Chronological Ordering", False, f"Exception: {str(e)}")
        return False

def cleanup_test_data(token):
    """Clean up test data after testing"""
    print("\n🧹 Cleaning up test data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Reset simulation to clean up all data
        response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
        
        if response.status_code == 200:
            log_test("Cleanup Test Data", True, "All test data cleaned up successfully")
        else:
            log_test("Cleanup Test Data", False, f"Status: {response.status_code}")
            
    except Exception as e:
        log_test("Cleanup Test Data", False, f"Exception: {str(e)}")

def main():
    """Main test execution"""
    print("🚀 OPTIMIZED OBSERVER MESSAGE FUNCTIONALITY TESTING")
    print("=" * 60)
    
    # Step 1: Setup - Authenticate as guest user
    token, user_id = test_guest_authentication()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Create 2-3 agents
    agents = create_test_agents(token, user_id)
    if len(agents) < 2:
        print("❌ Need at least 2 agents for testing")
        return
    
    # Step 3: Start simulation
    if not start_simulation(token):
        print("❌ Cannot proceed without active simulation")
        return
    
    print("\n" + "=" * 60)
    print("🧪 RUNNING OPTIMIZED OBSERVER MESSAGE TESTS")
    print("=" * 60)
    
    # Test 1: Instant sending and proper response structure
    test_observer_message_instant_sending(token)
    
    # Test 2: Conversation integration
    test_conversation_integration(token)
    
    # Test 3: Multiple observer messages
    test_multiple_observer_messages(token)
    
    # Test 4: No duplicate messages
    test_no_duplicate_messages(token)
    
    # Test 5: Chronological ordering
    test_chronological_ordering(token)
    
    # Cleanup
    cleanup_test_data(token)
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"   • {test['name']}: {test['details']}")
    
    print(f"\n🎯 OPTIMIZATION STATUS:")
    
    # Check key optimizations
    instant_sending_works = any(t["name"] == "Observer Message Instant Sending" and t["passed"] for t in test_results["tests"])
    integration_works = any(t["name"] == "Conversation Integration" and t["passed"] for t in test_results["tests"])
    no_duplicates_works = any(t["name"] == "No Duplicate Messages" and t["passed"] for t in test_results["tests"])
    chronological_works = any(t["name"] == "Chronological Ordering" and t["passed"] for t in test_results["tests"])
    
    print(f"   ⚡ Instant Sending: {'✅ WORKING' if instant_sending_works else '❌ FAILED'}")
    print(f"   💬 Proper Integration: {'✅ WORKING' if integration_works else '❌ FAILED'}")
    print(f"   🚫 No Duplicates: {'✅ WORKING' if no_duplicates_works else '❌ FAILED'}")
    print(f"   📅 Chronological Order: {'✅ WORKING' if chronological_works else '❌ FAILED'}")
    
    all_optimizations_working = instant_sending_works and integration_works and no_duplicates_works and chronological_works
    
    if all_optimizations_working:
        print(f"\n🎉 ALL OPTIMIZATIONS ARE WORKING CORRECTLY!")
    else:
        print(f"\n⚠️  SOME OPTIMIZATIONS NEED ATTENTION")
    
    return pass_rate >= 80  # Consider success if 80% or more tests pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)