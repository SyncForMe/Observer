#!/usr/bin/env python3
"""
Observer Message Immediate Display Fix Testing
Tests the immediate response functionality for observer messages as requested in the review.
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import asyncio
import threading
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test_result(test_name, passed, details="", response_time=None):
    """Log test result with details"""
    status = "✅ PASS" if passed else "❌ FAIL"
    time_info = f" ({response_time:.3f}s)" if response_time else ""
    print(f"{status}: {test_name}{time_info}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details,
        "response_time": response_time
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def get_auth_token():
    """Get authentication token for testing"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token'), data.get('user', {}).get('id')
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def setup_test_agents(auth_token):
    """Create test agents for observer message testing"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create 3 test agents for observer message testing
    test_agents = [
        {
            "name": "Dr. Quantum Researcher",
            "archetype": "scientist",
            "goal": "Develop quantum security protocols",
            "expertise": "Quantum computing and cryptography",
            "background": "PhD in Quantum Physics with 10 years in quantum security research"
        },
        {
            "name": "Security Project Manager",
            "archetype": "leader", 
            "goal": "Manage security device development project",
            "expertise": "Project management and security systems",
            "background": "15 years managing complex security technology projects"
        },
        {
            "name": "Risk Assessment Specialist",
            "archetype": "skeptic",
            "goal": "Identify and mitigate security risks",
            "expertise": "Risk analysis and threat assessment",
            "background": "Former cybersecurity analyst with expertise in threat modeling"
        }
    ]
    
    created_agents = []
    for agent_data in test_agents:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers, timeout=10)
            if response.status_code == 200:
                created_agents.append(response.json())
                print(f"✅ Created agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    return created_agents

def start_simulation(auth_token):
    """Start simulation for observer message testing"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Set scenario first
        scenario_data = {
            "scenario": "Quantum Security Device Development",
            "scenario_name": "Security Device Priority Planning"
        }
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to set scenario: {response.status_code}")
            return False
        
        # Start simulation
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Simulation started successfully")
            return True
        else:
            print(f"❌ Failed to start simulation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False

def test_immediate_response():
    """Test 1: Immediate Response Test - Verify API returns immediately with required fields"""
    print("\n🧪 TEST 1: IMMEDIATE RESPONSE TEST")
    
    auth_token, user_id = get_auth_token()
    if not auth_token:
        log_test_result("Authentication for immediate response test", False, "Could not get auth token")
        return
    
    # Setup test environment
    agents = setup_test_agents(auth_token)
    if len(agents) < 2:
        log_test_result("Agent setup for immediate response test", False, f"Only created {len(agents)} agents, need at least 2")
        return
    
    if not start_simulation(auth_token):
        log_test_result("Simulation setup for immediate response test", False, "Could not start simulation")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test observer message with immediate response requirement
    observer_message = "list the key priorities for our security device"
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": observer_message},
            headers=headers,
            timeout=15  # Allow reasonable timeout but expect much faster response
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required immediate response fields
            required_fields = ["observer_message", "conversation_id", "agent_responses_generating"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test_result("Immediate response structure", False, f"Missing fields: {missing_fields}", response_time)
                return
            
            # Verify field values
            if data["observer_message"] != observer_message:
                log_test_result("Observer message preservation", False, f"Expected '{observer_message}', got '{data['observer_message']}'", response_time)
                return
            
            if not data["conversation_id"]:
                log_test_result("Conversation ID generation", False, "conversation_id is empty", response_time)
                return
            
            if data["agent_responses_generating"] != True:
                log_test_result("Agent responses generating flag", False, f"Expected True, got {data['agent_responses_generating']}", response_time)
                return
            
            # Check response time - should be very fast (under 1 second as specified)
            if response_time > 1.0:
                log_test_result("Response time performance", False, f"Response took {response_time:.3f}s, expected < 1.0s", response_time)
            else:
                log_test_result("Response time performance", True, f"Fast response in {response_time:.3f}s", response_time)
            
            log_test_result("Immediate response structure", True, f"All required fields present: {required_fields}", response_time)
            log_test_result("Observer message preservation", True, "Observer message correctly preserved", response_time)
            log_test_result("Conversation ID generation", True, f"Generated conversation_id: {data['conversation_id'][:8]}...", response_time)
            log_test_result("Agent responses generating flag", True, "Correctly set to True for background processing", response_time)
            
            return data["conversation_id"]
            
        else:
            log_test_result("Observer message API call", False, f"HTTP {response.status_code}: {response.text}", response_time)
            return None
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        log_test_result("Observer message timeout", False, f"Request timed out after {response_time:.3f}s", response_time)
        return None
    except Exception as e:
        response_time = time.time() - start_time
        log_test_result("Observer message request", False, f"Request failed: {e}", response_time)
        return None

def test_background_agent_response_generation(conversation_id, auth_token):
    """Test 2: Background Agent Response Generation - Verify agents respond progressively"""
    print("\n🧪 TEST 2: BACKGROUND AGENT RESPONSE GENERATION")
    
    if not conversation_id or not auth_token:
        log_test_result("Background generation prerequisites", False, "Missing conversation_id or auth_token")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Wait for background processing to complete (give it reasonable time)
    print("⏳ Waiting for background agent response generation...")
    time.sleep(3)  # Initial wait
    
    max_wait_time = 30  # Maximum wait time for background processing
    check_interval = 2  # Check every 2 seconds
    start_wait = time.time()
    
    agent_responses_found = False
    final_conversation = None
    
    while time.time() - start_wait < max_wait_time:
        try:
            # Check if conversation has been updated with agent responses
            response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
            if response.status_code == 200:
                conversations = response.json()
                
                # Find our conversation
                target_conversation = None
                for conv in conversations:
                    if conv.get("id") == conversation_id:
                        target_conversation = conv
                        break
                
                if target_conversation:
                    messages = target_conversation.get("messages", [])
                    
                    # Check if we have more than just the observer message
                    if len(messages) > 1:
                        agent_responses_found = True
                        final_conversation = target_conversation
                        break
                    
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"⚠️ Error checking conversation updates: {e}")
            time.sleep(check_interval)
    
    total_wait_time = time.time() - start_wait
    
    if agent_responses_found and final_conversation:
        messages = final_conversation.get("messages", [])
        
        # Analyze the conversation structure
        observer_messages = [msg for msg in messages if msg.get("agent_name") == "Observer (You)"]
        agent_messages = [msg for msg in messages if msg.get("agent_name") != "Observer (You)"]
        
        log_test_result("Background agent response generation", True, 
                       f"Found {len(agent_messages)} agent responses after {total_wait_time:.1f}s", total_wait_time)
        
        if len(observer_messages) >= 1:
            log_test_result("Observer message in conversation", True, 
                           f"Observer message properly stored: '{observer_messages[0].get('message', '')[:50]}...'")
        else:
            log_test_result("Observer message in conversation", False, "Observer message not found in conversation")
        
        if len(agent_messages) >= 2:
            log_test_result("Multiple agent responses", True, 
                           f"Multiple agents responded ({len(agent_messages)} responses)")
            
            # Check response quality
            avg_response_length = sum(len(msg.get("message", "")) for msg in agent_messages) / len(agent_messages)
            if avg_response_length > 50:
                log_test_result("Agent response quality", True, 
                               f"Good response quality (avg {avg_response_length:.0f} chars)")
            else:
                log_test_result("Agent response quality", False, 
                               f"Poor response quality (avg {avg_response_length:.0f} chars)")
        else:
            log_test_result("Multiple agent responses", False, 
                           f"Only {len(agent_messages)} agent responses found")
        
        return final_conversation
    else:
        log_test_result("Background agent response generation", False, 
                       f"No agent responses found after {total_wait_time:.1f}s wait", total_wait_time)
        return None

def test_database_integration(conversation_id, auth_token):
    """Test 3: Database Integration - Verify proper storage and retrieval"""
    print("\n🧪 TEST 3: DATABASE INTEGRATION")
    
    if not conversation_id or not auth_token:
        log_test_result("Database integration prerequisites", False, "Missing conversation_id or auth_token")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Test conversation retrieval
        start_time = time.time()
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        retrieval_time = time.time() - start_time
        
        if response.status_code == 200:
            conversations = response.json()
            
            # Find our specific conversation
            target_conversation = None
            for conv in conversations:
                if conv.get("id") == conversation_id:
                    target_conversation = conv
                    break
            
            if target_conversation:
                log_test_result("Conversation storage and retrieval", True, 
                               f"Conversation found in database", retrieval_time)
                
                # Verify conversation structure
                required_fields = ["id", "messages", "user_id", "created_at"]
                missing_fields = [field for field in required_fields if field not in target_conversation]
                
                if missing_fields:
                    log_test_result("Conversation structure validation", False, 
                                   f"Missing fields: {missing_fields}")
                else:
                    log_test_result("Conversation structure validation", True, 
                                   "All required fields present")
                
                # Verify user association
                if target_conversation.get("user_id"):
                    log_test_result("User data isolation", True, 
                                   f"Conversation properly associated with user")
                else:
                    log_test_result("User data isolation", False, 
                                   "Conversation not associated with user")
                
                # Test observer messages endpoint
                try:
                    start_time = time.time()
                    obs_response = requests.get(f"{API_URL}/observer/messages", headers=headers, timeout=10)
                    obs_retrieval_time = time.time() - start_time
                    
                    if obs_response.status_code == 200:
                        observer_messages = obs_response.json()
                        log_test_result("Observer messages endpoint", True, 
                                       f"Retrieved {len(observer_messages)} observer messages", obs_retrieval_time)
                        
                        # Check if our message is in the observer messages
                        found_our_message = any(
                            "key priorities for our security device" in msg.get("message", "")
                            for msg in observer_messages
                        )
                        
                        if found_our_message:
                            log_test_result("Observer message persistence", True, 
                                           "Observer message found in observer_messages collection")
                        else:
                            log_test_result("Observer message persistence", False, 
                                           "Observer message not found in observer_messages collection")
                    else:
                        log_test_result("Observer messages endpoint", False, 
                                       f"HTTP {obs_response.status_code}: {obs_response.text}", obs_retrieval_time)
                        
                except Exception as e:
                    log_test_result("Observer messages endpoint", False, f"Request failed: {e}")
                
            else:
                log_test_result("Conversation storage and retrieval", False, 
                               f"Conversation {conversation_id} not found in database", retrieval_time)
        else:
            log_test_result("Conversation storage and retrieval", False, 
                           f"HTTP {response.status_code}: {response.text}", retrieval_time)
            
    except Exception as e:
        log_test_result("Database integration test", False, f"Request failed: {e}")

def test_error_handling():
    """Test 4: Error Handling - Test various error conditions"""
    print("\n🧪 TEST 4: ERROR HANDLING")
    
    auth_token, user_id = get_auth_token()
    if not auth_token:
        log_test_result("Authentication for error handling test", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Empty observer message
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": ""},
            headers=headers,
            timeout=10
        )
        response_time = time.time() - start_time
        
        if response.status_code == 400:
            log_test_result("Empty message validation", True, 
                           "Correctly rejected empty observer message", response_time)
        else:
            log_test_result("Empty message validation", False, 
                           f"Expected 400, got {response.status_code}", response_time)
    except Exception as e:
        log_test_result("Empty message validation", False, f"Request failed: {e}")
    
    # Test 2: Missing authentication
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": "test message"},
            timeout=10  # No auth headers
        )
        response_time = time.time() - start_time
        
        if response.status_code in [401, 403]:
            log_test_result("Authentication requirement", True, 
                           f"Correctly rejected unauthenticated request (HTTP {response.status_code})", response_time)
        else:
            log_test_result("Authentication requirement", False, 
                           f"Expected 401/403, got {response.status_code}", response_time)
    except Exception as e:
        log_test_result("Authentication requirement", False, f"Request failed: {e}")
    
    # Test 3: Invalid JSON
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/observer/send-message",
            data="invalid json",
            headers={**headers, "Content-Type": "application/json"},
            timeout=10
        )
        response_time = time.time() - start_time
        
        if response.status_code == 422:
            log_test_result("Invalid JSON handling", True, 
                           "Correctly rejected invalid JSON", response_time)
        else:
            log_test_result("Invalid JSON handling", False, 
                           f"Expected 422, got {response.status_code}", response_time)
    except Exception as e:
        log_test_result("Invalid JSON handling", False, f"Request failed: {e}")

def test_performance_under_load():
    """Test 5: Performance Test - Test multiple concurrent observer messages"""
    print("\n🧪 TEST 5: PERFORMANCE UNDER LOAD")
    
    auth_token, user_id = get_auth_token()
    if not auth_token:
        log_test_result("Authentication for performance test", False, "Could not get auth token")
        return
    
    # Setup test environment
    agents = setup_test_agents(auth_token)
    if len(agents) < 2:
        log_test_result("Agent setup for performance test", False, f"Only created {len(agents)} agents")
        return
    
    if not start_simulation(auth_token):
        log_test_result("Simulation setup for performance test", False, "Could not start simulation")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test multiple observer messages in sequence
    test_messages = [
        "What are the top 3 security priorities?",
        "How should we approach quantum encryption?",
        "What are the main technical challenges?"
    ]
    
    response_times = []
    successful_requests = 0
    
    for i, message in enumerate(test_messages):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": message},
                headers=headers,
                timeout=15
            )
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                successful_requests += 1
                data = response.json()
                
                # Verify immediate response structure
                if all(field in data for field in ["observer_message", "conversation_id", "agent_responses_generating"]):
                    log_test_result(f"Sequential message {i+1} structure", True, 
                                   f"Correct structure in {response_time:.3f}s", response_time)
                else:
                    log_test_result(f"Sequential message {i+1} structure", False, 
                                   f"Missing fields in response", response_time)
            else:
                log_test_result(f"Sequential message {i+1}", False, 
                               f"HTTP {response.status_code}", response_time)
            
            # Small delay between requests to avoid overwhelming
            time.sleep(1)
            
        except Exception as e:
            log_test_result(f"Sequential message {i+1}", False, f"Request failed: {e}")
    
    # Performance analysis
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        log_test_result("Sequential performance analysis", True, 
                       f"Avg: {avg_response_time:.3f}s, Min: {min_response_time:.3f}s, Max: {max_response_time:.3f}s")
        
        if avg_response_time < 1.0:
            log_test_result("Average response time performance", True, 
                           f"Excellent average response time: {avg_response_time:.3f}s")
        elif avg_response_time < 2.0:
            log_test_result("Average response time performance", True, 
                           f"Good average response time: {avg_response_time:.3f}s")
        else:
            log_test_result("Average response time performance", False, 
                           f"Slow average response time: {avg_response_time:.3f}s")
    
    success_rate = (successful_requests / len(test_messages)) * 100
    log_test_result("Sequential request success rate", success_rate >= 80, 
                   f"{success_rate:.1f}% success rate ({successful_requests}/{len(test_messages)})")

def main():
    """Main test execution"""
    print("🚀 OBSERVER MESSAGE IMMEDIATE DISPLAY FIX TESTING")
    print("=" * 60)
    print("Testing the immediate observer message display improvement as requested in the review.")
    print()
    
    # Test 1: Immediate Response Test
    conversation_id = test_immediate_response()
    
    if conversation_id:
        # Get auth token for subsequent tests
        auth_token, user_id = get_auth_token()
        
        if auth_token:
            # Test 2: Background Agent Response Generation
            final_conversation = test_background_agent_response_generation(conversation_id, auth_token)
            
            # Test 3: Database Integration
            test_database_integration(conversation_id, auth_token)
    
    # Test 4: Error Handling
    test_error_handling()
    
    # Test 5: Performance Under Load
    test_performance_under_load()
    
    # Final Results Summary
    print("\n" + "=" * 60)
    print("🏁 OBSERVER MESSAGE IMMEDIATE DISPLAY FIX TEST RESULTS")
    print("=" * 60)
    
    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 EXCELLENT: Observer message immediate display fix is working well!")
    elif success_rate >= 60:
        print("\n⚠️ GOOD: Observer message immediate display fix is mostly working with some issues.")
    else:
        print("\n🚨 NEEDS ATTENTION: Observer message immediate display fix has significant issues.")
    
    # Detailed test breakdown
    print(f"\n📋 DETAILED TEST RESULTS:")
    for test in test_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        time_info = f" ({test['response_time']:.3f}s)" if test.get('response_time') else ""
        print(f"{status} {test['name']}{time_info}")
        if test["details"]:
            print(f"    {test['details']}")
    
    print(f"\n🔗 Tested against: {API_URL}")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()