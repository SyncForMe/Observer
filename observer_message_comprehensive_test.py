#!/usr/bin/env python3
"""
Comprehensive Observer Message Functionality Test Script
Tests the observer message workflow that's getting stuck at "sending"
Focus on response time, response structure, and error handling as requested in review
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
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
    "tests": [],
    "response_times": []
}

def log_test(test_name, passed, details="", response_time=None):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    if response_time:
        print(f"   Response time: {response_time:.2f}s")
        test_results["response_times"].append(response_time)
    
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

def test_guest_authentication():
    """Test guest authentication for observer message workflow"""
    print("\n🔐 Testing Guest Authentication...")
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/auth/test-login", timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                log_test("Guest Authentication", True, 
                        f"Token received, user_id: {data['user']['id']}", response_time)
                return data["access_token"], data["user"]["id"]
            else:
                log_test("Guest Authentication", False, 
                        f"Missing required fields in response: {data}", response_time)
                return None, None
        else:
            log_test("Guest Authentication", False, 
                    f"Status: {response.status_code}, Response: {response.text}", response_time)
            return None, None
            
    except requests.exceptions.Timeout:
        log_test("Guest Authentication", False, "Request timed out after 30 seconds")
        return None, None
    except Exception as e:
        log_test("Guest Authentication", False, f"Exception: {str(e)}")
        return None, None

def test_simulation_reset(token):
    """Test simulation reset endpoint"""
    print("\n🔄 Testing Simulation Reset...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            log_test("Simulation Reset", True, "Reset successful", response_time)
            return True
        else:
            log_test("Simulation Reset", False, 
                    f"Status: {response.status_code}, Response: {response.text}", response_time)
            return False
            
    except requests.exceptions.Timeout:
        log_test("Simulation Reset", False, "Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Simulation Reset", False, f"Exception: {str(e)}")
        return False

def create_test_agents(token, count=3):
    """Create test agents for observer message testing"""
    print(f"\n🤖 Creating {count} Test Agents...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    agent_ids = []
    
    test_agents = [
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
    
    for i, agent_data in enumerate(test_agents[:count]):
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/agents", 
                                   headers=headers, 
                                   json=agent_data,
                                   timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                agent_ids.append(data["id"])
                log_test(f"Create Agent {i+1} ({agent_data['name']})", True, 
                        f"Agent ID: {data['id']}", response_time)
            else:
                log_test(f"Create Agent {i+1} ({agent_data['name']})", False, 
                        f"Status: {response.status_code}, Response: {response.text}", response_time)
                
        except requests.exceptions.Timeout:
            log_test(f"Create Agent {i+1} ({agent_data['name']})", False, 
                    "Request timed out after 30 seconds")
        except Exception as e:
            log_test(f"Create Agent {i+1} ({agent_data['name']})", False, f"Exception: {str(e)}")
    
    return agent_ids

def test_observer_message_sending(token):
    """Test the core observer message sending functionality"""
    print("\n💬 Testing Observer Message Sending...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test message that should generate good responses
    observer_message = "Hello team, let's discuss the deep space signal discovery."
    
    payload = {
        "observer_message": observer_message
    }
    
    try:
        print(f"   Sending observer message: '{observer_message}'")
        start_time = time.time()
        
        response = requests.post(f"{API_URL}/observer/send-message", 
                               headers=headers, 
                               json=payload,
                               timeout=60)  # Longer timeout for agent processing
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            required_fields = ["message", "observer_message", "agent_responses"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test("Observer Message Sending", False, 
                        f"Missing required fields: {missing_fields}", response_time)
                return None
            
            # Check agent_responses structure
            agent_responses = data["agent_responses"]
            if not isinstance(agent_responses, dict) or "messages" not in agent_responses:
                log_test("Observer Message Sending", False, 
                        f"Invalid agent_responses structure: {type(agent_responses)}", response_time)
                return None
            
            messages = agent_responses["messages"]
            if not isinstance(messages, list) or len(messages) == 0:
                log_test("Observer Message Sending", False, 
                        f"No messages in agent_responses: {len(messages) if isinstance(messages, list) else 'not a list'}", 
                        response_time)
                return None
            
            # Check if observer message is first
            first_message = messages[0]
            if first_message.get("agent_name") != "Observer (You)":
                log_test("Observer Message Sending", False, 
                        f"First message not from Observer: {first_message.get('agent_name')}", response_time)
                return None
            
            # Count agent responses (excluding observer message)
            agent_message_count = len([msg for msg in messages if msg.get("agent_name") != "Observer (You)"])
            
            # Check response time - should complete within 30 seconds as per review requirements
            if response_time > 30:
                log_test("Observer Message Sending", False, 
                        f"Response too slow: {response_time:.2f}s (should be ≤30s)", response_time)
                return None
            
            log_test("Observer Message Sending", True, 
                    f"Response received with {agent_message_count} agent responses, "
                    f"total messages: {len(messages)}", response_time)
            
            return data
            
        else:
            log_test("Observer Message Sending", False, 
                    f"Status: {response.status_code}, Response: {response.text}", response_time)
            return None
            
    except requests.exceptions.Timeout:
        log_test("Observer Message Sending", False, 
                f"Request timed out after 60 seconds - this indicates the 'sending' stuck issue")
        return None
    except Exception as e:
        log_test("Observer Message Sending", False, f"Exception: {str(e)}")
        return None

def test_observer_message_error_handling(token):
    """Test error handling for observer messages"""
    print("\n🚫 Testing Observer Message Error Handling...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Empty observer message
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/observer/send-message", 
                               headers=headers, 
                               json={"observer_message": ""},
                               timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 400:
            log_test("Empty Observer Message Error", True, 
                    "Correctly rejected empty message", response_time)
        else:
            log_test("Empty Observer Message Error", False, 
                    f"Expected 400, got {response.status_code}: {response.text}", response_time)
            
    except Exception as e:
        log_test("Empty Observer Message Error", False, f"Exception: {str(e)}")
    
    # Test 2: No authentication
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/observer/send-message", 
                               json={"observer_message": "Test message"},
                               timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 403:
            log_test("Unauthenticated Observer Message Error", True, 
                    "Correctly rejected unauthenticated request", response_time)
        else:
            log_test("Unauthenticated Observer Message Error", False, 
                    f"Expected 403, got {response.status_code}: {response.text}", response_time)
            
    except Exception as e:
        log_test("Unauthenticated Observer Message Error", False, f"Exception: {str(e)}")

def test_observer_messages_retrieval(token):
    """Test observer messages retrieval endpoint"""
    print("\n📋 Testing Observer Messages Retrieval...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_URL}/observer/messages", 
                              headers=headers,
                              timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("Observer Messages Retrieval", True, 
                        f"Retrieved {len(data)} observer messages", response_time)
                return data
            else:
                log_test("Observer Messages Retrieval", False, 
                        f"Expected list, got {type(data)}: {data}", response_time)
                return None
        else:
            log_test("Observer Messages Retrieval", False, 
                    f"Status: {response.status_code}, Response: {response.text}", response_time)
            return None
            
    except requests.exceptions.Timeout:
        log_test("Observer Messages Retrieval", False, "Request timed out after 30 seconds")
        return None
    except Exception as e:
        log_test("Observer Messages Retrieval", False, f"Exception: {str(e)}")
        return None

def test_response_structure_validation(observer_response):
    """Validate the response structure matches frontend expectations"""
    print("\n🔍 Testing Response Structure Validation...")
    
    if not observer_response:
        log_test("Response Structure Validation", False, "No observer response to validate")
        return False
    
    try:
        # Check top-level structure
        required_top_level = ["message", "observer_message", "agent_responses"]
        missing_top_level = [field for field in required_top_level if field not in observer_response]
        
        if missing_top_level:
            log_test("Response Structure Validation", False, 
                    f"Missing top-level fields: {missing_top_level}")
            return False
        
        # Check agent_responses structure
        agent_responses = observer_response["agent_responses"]
        required_agent_fields = ["messages", "round_number", "scenario_name"]
        missing_agent_fields = [field for field in required_agent_fields if field not in agent_responses]
        
        if missing_agent_fields:
            log_test("Response Structure Validation", False, 
                    f"Missing agent_responses fields: {missing_agent_fields}")
            return False
        
        # Check messages structure
        messages = agent_responses["messages"]
        if not isinstance(messages, list) or len(messages) == 0:
            log_test("Response Structure Validation", False, 
                    f"Invalid messages structure: {type(messages)}, length: {len(messages) if isinstance(messages, list) else 'N/A'}")
            return False
        
        # Check individual message structure
        for i, message in enumerate(messages):
            required_msg_fields = ["agent_id", "agent_name", "message"]
            missing_msg_fields = [field for field in required_msg_fields if field not in message]
            
            if missing_msg_fields:
                log_test("Response Structure Validation", False, 
                        f"Message {i} missing fields: {missing_msg_fields}")
                return False
        
        log_test("Response Structure Validation", True, 
                f"All required fields present, {len(messages)} messages validated")
        return True
        
    except Exception as e:
        log_test("Response Structure Validation", False, f"Exception during validation: {str(e)}")
        return False

def print_test_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("🧪 OBSERVER MESSAGE FUNCTIONALITY TEST SUMMARY")
    print("="*60)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {test_results['passed']}")
    print(f"   ❌ Failed: {test_results['failed']}")
    print(f"   📈 Pass Rate: {pass_rate:.1f}%")
    
    if test_results["response_times"]:
        avg_time = sum(test_results["response_times"]) / len(test_results["response_times"])
        max_time = max(test_results["response_times"])
        min_time = min(test_results["response_times"])
        
        print(f"\n⏱️  Response Time Analysis:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Maximum: {max_time:.2f}s")
        print(f"   Minimum: {min_time:.2f}s")
        
        # Check for performance issues as per review requirements
        slow_responses = [t for t in test_results["response_times"] if t > 30]
        if slow_responses:
            print(f"   ⚠️  Slow responses (>30s): {len(slow_responses)}")
        
        timeout_issues = [t for t in test_results["tests"] if "timed out" in t.get("details", "")]
        if timeout_issues:
            print(f"   🚨 Timeout issues: {len(timeout_issues)}")
    
    print(f"\n🔍 Key Findings (Review Requirements):")
    
    # Check for specific issues mentioned in review
    hanging_issues = [t for t in test_results["tests"] if "timed out" in t.get("details", "")]
    if hanging_issues:
        print(f"   🚨 HANGING ISSUE DETECTED: {len(hanging_issues)} requests timed out")
        print(f"      This confirms the 'sending' stuck issue mentioned in the review")
    else:
        print(f"   ✅ No hanging/timeout issues detected")
    
    # Check response structure
    structure_issues = [t for t in test_results["tests"] 
                       if "Missing required fields" in t.get("details", "") or 
                          "Invalid" in t.get("details", "")]
    if structure_issues:
        print(f"   🚨 RESPONSE STRUCTURE ISSUES: {len(structure_issues)} problems detected")
    else:
        print(f"   ✅ Response structure appears correct")
    
    # Check authentication
    auth_issues = [t for t in test_results["tests"] if "auth" in t["name"].lower() and not t["passed"]]
    if auth_issues:
        print(f"   🚨 AUTHENTICATION ISSUES: {len(auth_issues)} problems detected")
    else:
        print(f"   ✅ Authentication working properly")
    
    # Check response time requirement (≤30 seconds)
    performance_issues = [t for t in test_results["tests"] if t.get("response_time", 0) > 30]
    if performance_issues:
        print(f"   🚨 PERFORMANCE ISSUES: {len(performance_issues)} responses >30s")
    else:
        print(f"   ✅ All responses completed within 30 seconds")
    
    print(f"\n📋 Detailed Test Results:")
    for test in test_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        time_info = f" ({test['response_time']:.2f}s)" if test["response_time"] else ""
        print(f"   {status} {test['name']}{time_info}")
        if test["details"] and not test["passed"]:
            print(f"      └─ {test['details']}")

def main():
    """Main test execution"""
    print("🚀 OBSERVER MESSAGE FUNCTIONALITY TEST")
    print("Testing the observer message workflow that's getting stuck at 'sending'")
    print("Focus: Response time, response structure, authentication, error handling")
    print("-" * 60)
    
    # Step 1: Authenticate as guest user
    token, user_id = test_guest_authentication()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return False
    
    # Step 2: Reset simulation state
    if not test_simulation_reset(token):
        print("⚠️  Simulation reset failed, continuing anyway...")
    
    # Step 3: Create test agents
    agent_ids = create_test_agents(token, 3)
    if len(agent_ids) < 2:
        print("⚠️  Need at least 2 agents for observer messages, continuing with available agents...")
    
    # Step 4: Test core observer message functionality
    observer_response = test_observer_message_sending(token)
    
    # Step 5: Test response structure validation
    test_response_structure_validation(observer_response)
    
    # Step 6: Test error handling
    test_observer_message_error_handling(token)
    
    # Step 7: Test observer messages retrieval
    test_observer_messages_retrieval(token)
    
    # Print comprehensive summary
    print_test_summary()
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT:")
    if test_results["failed"] == 0:
        print("   ✅ All tests passed - Observer message functionality is working correctly")
        print("   ✅ No 'sending' stuck issues detected")
        print("   ✅ Response structure matches frontend expectations")
        print("   ✅ Authentication and error handling working properly")
    elif test_results["failed"] <= 2:
        print("   ⚠️  Minor issues detected - Observer message functionality mostly working")
    else:
        print("   🚨 Significant issues detected - Observer message functionality needs attention")
        hanging_issues = [t for t in test_results["tests"] if "timed out" in t.get("details", "")]
        if hanging_issues:
            print("   🚨 CRITICAL: 'Sending' stuck issue confirmed - requests are timing out")
    
    return test_results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)