#!/usr/bin/env python3
"""
Comprehensive Observer Message Functionality Test Script
Tests the observer message functionality in the AI Agent Simulation Platform
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
    """Test 1: Verify guest authentication works with POST /auth/test-login"""
    print("\n🔐 Testing Guest Authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test("Guest Authentication - Response Structure", False, 
                        f"Missing fields: {missing_fields}")
                return None
            
            # Validate JWT token structure
            token = data['access_token']
            try:
                # Decode without verification to check structure
                import jwt
                decoded = jwt.decode(token, options={"verify_signature": False})
                
                if 'sub' not in decoded or 'user_id' not in decoded:
                    log_test("Guest Authentication - JWT Structure", False, 
                            "JWT missing required fields 'sub' or 'user_id'")
                    return None
                
                log_test("Guest Authentication - JWT Structure", True, 
                        f"JWT contains required fields: sub={decoded.get('sub')}")
                
            except Exception as e:
                log_test("Guest Authentication - JWT Validation", False, f"JWT decode error: {e}")
                return None
            
            log_test("Guest Authentication - Endpoint", True, 
                    f"Token type: {data['token_type']}, User: {data['user']['email']}")
            
            return {
                'token': token,
                'user_id': data['user']['id'],
                'user_email': data['user']['email']
            }
        else:
            log_test("Guest Authentication - Endpoint", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Guest Authentication - Endpoint", False, f"Exception: {e}")
        return None

def test_observer_endpoint_authentication(auth_info):
    """Test 2: Verify observer endpoint requires authentication"""
    print("\n🔒 Testing Observer Endpoint Authentication...")
    
    # Test without authentication
    try:
        response = requests.post(f"{API_URL}/observer/send-message", 
                               json={"observer_message": "Test message"}, 
                               timeout=10)
        
        if response.status_code == 403:
            log_test("Observer Endpoint - No Auth Rejection", True, 
                    "Correctly rejects unauthenticated requests")
        else:
            log_test("Observer Endpoint - No Auth Rejection", False, 
                    f"Expected 403, got {response.status_code}")
    except Exception as e:
        log_test("Observer Endpoint - No Auth Rejection", False, f"Exception: {e}")
    
    # Test with authentication
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    try:
        response = requests.post(f"{API_URL}/observer/send-message", 
                               json={"observer_message": "Test authenticated message"}, 
                               headers=headers, 
                               timeout=10)
        
        if response.status_code in [200, 400]:  # 400 might be expected if no agents
            log_test("Observer Endpoint - Auth Acceptance", True, 
                    f"Accepts authenticated requests (status: {response.status_code})")
            return True
        else:
            log_test("Observer Endpoint - Auth Acceptance", False, 
                    f"Unexpected status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        log_test("Observer Endpoint - Auth Acceptance", False, f"Exception: {e}")
        return False

def create_test_agents(auth_info):
    """Create test agents for observer message testing"""
    print("\n🤖 Creating Test Agents...")
    
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    created_agents = []
    
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics",
            "background": "PhD in Quantum Physics from MIT"
        },
        {
            "name": "Marcus Johnson",
            "archetype": "leader",
            "goal": "Lead successful project outcomes",
            "expertise": "Project Management",
            "background": "15 years of project management experience"
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "optimist",
            "goal": "Foster positive team dynamics",
            "expertise": "Team Psychology",
            "background": "Expert in organizational psychology"
        }
    ]
    
    for agent_data in test_agents:
        try:
            response = requests.post(f"{API_URL}/agents", 
                                   json=agent_data, 
                                   headers=headers, 
                                   timeout=10)
            
            if response.status_code == 200:
                agent = response.json()
                created_agents.append(agent)
                log_test(f"Agent Creation - {agent_data['name']}", True, 
                        f"Agent ID: {agent.get('id', 'Unknown')}")
            else:
                log_test(f"Agent Creation - {agent_data['name']}", False, 
                        f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            log_test(f"Agent Creation - {agent_data['name']}", False, f"Exception: {e}")
    
    return created_agents

def test_observer_message_processing(auth_info, agents):
    """Test 3: Test observer message processing and agent responses"""
    print("\n💬 Testing Observer Message Processing...")
    
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    
    # Start simulation first
    try:
        start_response = requests.post(f"{API_URL}/simulation/start", 
                                     headers=headers, 
                                     timeout=10)
        if start_response.status_code != 200:
            log_test("Observer Message - Simulation Start", False, 
                    f"Failed to start simulation: {start_response.status_code}")
            return None
    except Exception as e:
        log_test("Observer Message - Simulation Start", False, f"Exception: {e}")
        return None
    
    # Test empty message rejection
    try:
        response = requests.post(f"{API_URL}/observer/send-message", 
                               json={"observer_message": ""}, 
                               headers=headers, 
                               timeout=10)
        
        if response.status_code == 400:
            log_test("Observer Message - Empty Message Rejection", True, 
                    "Correctly rejects empty messages")
        else:
            log_test("Observer Message - Empty Message Rejection", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Observer Message - Empty Message Rejection", False, f"Exception: {e}")
    
    # Test valid observer message
    test_message = "Hello team! Let's focus on developing a quantum encryption protocol. I want to see innovative solutions and collaborative problem-solving."
    
    try:
        response = requests.post(f"{API_URL}/observer/send-message", 
                               json={"observer_message": test_message}, 
                               headers=headers, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            required_fields = ['message', 'observer_message', 'agent_responses']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test("Observer Message - Response Structure", False, 
                        f"Missing fields: {missing_fields}")
                return None
            
            # Verify observer message is preserved
            if data['observer_message'] == test_message:
                log_test("Observer Message - Message Preservation", True, 
                        "Observer message correctly preserved in response")
            else:
                log_test("Observer Message - Message Preservation", False, 
                        "Observer message not preserved correctly")
            
            # Check agent responses
            agent_responses = data['agent_responses']
            if 'messages' in agent_responses and len(agent_responses['messages']) > 0:
                messages = agent_responses['messages']
                
                # First message should be from observer
                if messages[0]['agent_name'] == "Observer (You)":
                    log_test("Observer Message - Observer Display", True, 
                            "Observer message appears first with correct label")
                else:
                    log_test("Observer Message - Observer Display", False, 
                            f"First message from: {messages[0]['agent_name']}")
                
                # Check agent responses
                agent_response_count = len([msg for msg in messages if msg['agent_name'] != "Observer (You)"])
                expected_responses = len(agents)
                
                if agent_response_count == expected_responses:
                    log_test("Observer Message - Agent Response Count", True, 
                            f"All {expected_responses} agents responded")
                else:
                    log_test("Observer Message - Agent Response Count", False, 
                            f"Expected {expected_responses} responses, got {agent_response_count}")
                
                # Check response quality
                agent_messages = [msg for msg in messages if msg['agent_name'] != "Observer (You)"]
                if agent_messages:
                    avg_length = sum(len(msg['message']) for msg in agent_messages) / len(agent_messages)
                    if avg_length > 20:  # Reasonable response length
                        log_test("Observer Message - Response Quality", True, 
                                f"Average response length: {avg_length:.1f} characters")
                    else:
                        log_test("Observer Message - Response Quality", False, 
                                f"Responses too short (avg: {avg_length:.1f} chars)")
                
                return agent_responses
            else:
                log_test("Observer Message - Agent Responses", False, 
                        "No agent responses found in response")
                return None
        else:
            log_test("Observer Message - Processing", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Observer Message - Processing", False, f"Exception: {e}")
        return None

def test_database_integration(auth_info):
    """Test 4: Verify observer messages are saved to database"""
    print("\n💾 Testing Database Integration...")
    
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    
    # Test observer messages endpoint
    try:
        response = requests.get(f"{API_URL}/observer/messages", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code == 200:
            messages = response.json()
            
            if isinstance(messages, list):
                if len(messages) > 0:
                    log_test("Observer Messages - Database Retrieval", True, 
                            f"Retrieved {len(messages)} observer messages")
                    
                    # Check message structure
                    latest_message = messages[0]
                    required_fields = ['message', 'user_id', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in latest_message]
                    
                    if not missing_fields:
                        log_test("Observer Messages - Message Structure", True, 
                                "Messages have required fields")
                        
                        # Verify user association
                        if latest_message['user_id'] == auth_info['user_id']:
                            log_test("Observer Messages - User Association", True, 
                                    "Messages correctly associated with user")
                        else:
                            log_test("Observer Messages - User Association", False, 
                                    f"Expected user_id {auth_info['user_id']}, got {latest_message['user_id']}")
                    else:
                        log_test("Observer Messages - Message Structure", False, 
                                f"Missing fields: {missing_fields}")
                else:
                    log_test("Observer Messages - Database Retrieval", True, 
                            "No messages found (empty state)")
            else:
                log_test("Observer Messages - Database Retrieval", False, 
                        f"Expected list, got {type(messages)}")
        else:
            log_test("Observer Messages - Database Retrieval", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("Observer Messages - Database Retrieval", False, f"Exception: {e}")

def test_conversation_integration(auth_info):
    """Test 5: Verify observer messages appear in conversation flow"""
    print("\n🗣️ Testing Conversation Integration...")
    
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    
    # Get conversations to see if observer messages appear
    try:
        response = requests.get(f"{API_URL}/conversations", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code == 200:
            conversations = response.json()
            
            if isinstance(conversations, list) and len(conversations) > 0:
                # Look for observer-related conversations
                observer_conversations = [
                    conv for conv in conversations 
                    if conv.get('scenario_name') == 'Observer Guidance'
                ]
                
                if observer_conversations:
                    log_test("Conversation Integration - Observer Conversations", True, 
                            f"Found {len(observer_conversations)} observer conversations")
                    
                    # Check latest observer conversation
                    latest_conv = observer_conversations[0]
                    if 'messages' in latest_conv and len(latest_conv['messages']) > 0:
                        messages = latest_conv['messages']
                        
                        # Check for observer message
                        observer_msg = next((msg for msg in messages if msg['agent_name'] == "Observer (You)"), None)
                        if observer_msg:
                            log_test("Conversation Integration - Observer Message Display", True, 
                                    "Observer message appears in conversation")
                        else:
                            log_test("Conversation Integration - Observer Message Display", False, 
                                    "Observer message not found in conversation")
                        
                        # Check for agent responses
                        agent_responses = [msg for msg in messages if msg['agent_name'] != "Observer (You)"]
                        if agent_responses:
                            log_test("Conversation Integration - Agent Responses", True, 
                                    f"Found {len(agent_responses)} agent responses in conversation")
                        else:
                            log_test("Conversation Integration - Agent Responses", False, 
                                    "No agent responses found in conversation")
                    else:
                        log_test("Conversation Integration - Message Content", False, 
                                "Observer conversation has no messages")
                else:
                    log_test("Conversation Integration - Observer Conversations", False, 
                            "No observer conversations found")
            else:
                log_test("Conversation Integration - Conversations Retrieval", True, 
                        "No conversations found (empty state)")
        else:
            log_test("Conversation Integration - Conversations Retrieval", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("Conversation Integration - Conversations Retrieval", False, f"Exception: {e}")

def test_multiple_observer_messages(auth_info):
    """Test 6: Test sending multiple observer messages in sequence"""
    print("\n🔄 Testing Multiple Observer Messages...")
    
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    
    test_messages = [
        "Great work so far! Now let's focus on the technical implementation details.",
        "I want to see more collaboration between the quantum physics and project management perspectives.",
        "Let's wrap up with concrete next steps and timeline commitments."
    ]
    
    successful_messages = 0
    
    for i, message in enumerate(test_messages, 1):
        try:
            response = requests.post(f"{API_URL}/observer/send-message", 
                                   json={"observer_message": message}, 
                                   headers=headers, 
                                   timeout=15)
            
            if response.status_code == 200:
                successful_messages += 1
                log_test(f"Multiple Messages - Message {i}", True, 
                        f"Successfully sent message {i}")
            else:
                log_test(f"Multiple Messages - Message {i}", False, 
                        f"Status: {response.status_code}")
            
            # Small delay between messages
            time.sleep(1)
            
        except Exception as e:
            log_test(f"Multiple Messages - Message {i}", False, f"Exception: {e}")
    
    if successful_messages == len(test_messages):
        log_test("Multiple Messages - Sequence", True, 
                f"Successfully sent all {len(test_messages)} messages")
    else:
        log_test("Multiple Messages - Sequence", False, 
                f"Only {successful_messages}/{len(test_messages)} messages succeeded")

def cleanup_test_data(auth_info, agents):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    headers = {"Authorization": f"Bearer {auth_info['token']}"}
    
    # Delete test agents
    for agent in agents:
        try:
            response = requests.delete(f"{API_URL}/agents/{agent['id']}", 
                                     headers=headers, 
                                     timeout=10)
            if response.status_code == 200:
                print(f"   Deleted agent: {agent['name']}")
        except Exception as e:
            print(f"   Failed to delete agent {agent['name']}: {e}")

def print_test_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("🧪 OBSERVER MESSAGE FUNCTIONALITY TEST SUMMARY")
    print("="*60)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"   • {test['name']}: {test['details']}")
    
    print("\n" + "="*60)
    
    # Overall assessment
    if pass_rate >= 90:
        print("🎉 EXCELLENT: Observer message functionality is working very well!")
    elif pass_rate >= 75:
        print("✅ GOOD: Observer message functionality is working with minor issues.")
    elif pass_rate >= 50:
        print("⚠️ MODERATE: Observer message functionality has some significant issues.")
    else:
        print("❌ POOR: Observer message functionality has major problems.")

def main():
    """Main test execution"""
    print("🚀 Starting Observer Message Functionality Tests")
    print("="*60)
    
    # Test 1: Guest Authentication
    auth_info = test_guest_authentication()
    if not auth_info:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test 2: Observer Endpoint Authentication
    auth_works = test_observer_endpoint_authentication(auth_info)
    if not auth_works:
        print("⚠️ Authentication issues detected, but continuing...")
    
    # Create test agents
    agents = create_test_agents(auth_info)
    if not agents:
        print("❌ Cannot proceed without test agents")
        return
    
    # Test 3: Observer Message Processing
    observer_response = test_observer_message_processing(auth_info, agents)
    
    # Test 4: Database Integration
    test_database_integration(auth_info)
    
    # Test 5: Conversation Integration
    test_conversation_integration(auth_info)
    
    # Test 6: Multiple Observer Messages
    test_multiple_observer_messages(auth_info)
    
    # Cleanup
    cleanup_test_data(auth_info, agents)
    
    # Print summary
    print_test_summary()

if __name__ == "__main__":
    main()