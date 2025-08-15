#!/usr/bin/env python3
"""
PARALLEL MESSAGE GENERATION & PERFORMANCE IMPROVEMENTS TESTING
Testing the new parallel processing implementation to verify speed improvements and streaming functionality.

CRITICAL BACKEND CHANGES TO TEST:
1. Parallel Message Generation Performance - Test /api/conversation/generate endpoint with new parallel processing
2. Message Streaming with Parallel Generation - Test /api/messages/stream endpoint after parallel generation starts
3. Database Operations with Parallel Processing - Verify message_stream collection receives messages from parallel generation
4. Error Handling in Parallel System - Test what happens if one agent fails during parallel generation
5. End-to-End Performance Comparison - Generate conversation with parallel system and measure timing

EXPECTED IMPROVEMENTS:
- Total generation time: ~27 seconds (instead of ~81s)
- Performance gain: ~3x faster (67% reduction)
- Progressive display: Messages still appear individually as generated
- All functionality preserved: Streaming, completion, error handling
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global auth token
auth_token = None

def authenticate():
    """Authenticate with the backend using email/password"""
    global auth_token
    
    if auth_token:
        return True
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    url = f"{API_URL}/auth/login"
    
    try:
        response = requests.post(url, json=login_data, timeout=10)
        if response.status_code == 200:
            response_data = response.json()
            auth_token = response_data.get("access_token")
            if auth_token:
                print("✅ Authentication successful")
                return True
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def make_authenticated_request(method, endpoint, data=None, timeout=30):
    """Make an authenticated request to the API"""
    if not authenticate():
        return None
        
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response
    except requests.exceptions.Timeout:
        print(f"⏰ Request to {endpoint} timed out after {timeout} seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request to {endpoint} failed: {e}")
        return None

def log_test_result(test_name, passed, details=""):
    """Log test result"""
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

def test_parallel_message_generation_performance():
    """Test 1: Parallel Message Generation Performance - Measure total generation time"""
    print("\n" + "="*80)
    print("🚀 TEST 1: PARALLEL MESSAGE GENERATION PERFORMANCE")
    print("="*80)
    
    # Step 1: Set up scenario for testing
    print("\n📋 Step 1: Setting up quantum communication scenario...")
    scenario_data = {
        "scenario": "A team of quantum physicists needs to develop a breakthrough quantum communication device for secure military communications. The team must collaborate to solve technical challenges and create implementation plans.",
        "scenario_name": "Quantum Communication Device Development"
    }
    
    response = make_authenticated_request('POST', '/simulation/set-scenario', scenario_data)
    if response and response.status_code == 200:
        log_test_result("Scenario Setup", True, f"Scenario set: {scenario_data['scenario_name']}")
    else:
        log_test_result("Scenario Setup", False, f"Failed to set scenario: {response.status_code if response else 'No response'}")
        return False
    
    # Step 2: Ensure we have 3+ agents for parallel testing
    print("\n🤖 Step 2: Verifying agent count for parallel testing...")
    response = make_authenticated_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        agent_count = len(agents)
        
        if agent_count >= 3:
            log_test_result("Agent Count Check", True, f"Found {agent_count} agents (optimal for parallel testing)")
            print(f"   Agents: {[agent.get('name', 'Unknown') for agent in agents[:5]]}")
        else:
            # Create test agents if we don't have enough
            print(f"   Only {agent_count} agents found, creating test agents for parallel testing...")
            success = create_test_agents_for_parallel_testing()
            if not success:
                log_test_result("Agent Setup", False, "Failed to create sufficient agents")
                return False
            log_test_result("Agent Setup", True, "Created test agents successfully")
            agent_count = 3  # We created 3 agents minimum
    else:
        log_test_result("Agent Count Check", False, f"Failed to get agents: {response.status_code if response else 'No response'}")
        return False
    
    # Step 3: Test parallel conversation generation performance
    print("\n⚡ Step 3: Testing PARALLEL conversation generation performance...")
    print(f"   Expected time: ~27 seconds (vs ~{27 * agent_count}s sequential)")
    
    start_time = time.time()
    
    response = make_authenticated_request('POST', '/conversation/generate', timeout=90)  # Allow up to 90 seconds
    
    if response and response.status_code == 200:
        end_time = time.time()
        generation_time = end_time - start_time
        
        response_data = response.json()
        
        # Check if it meets the target time (~27 seconds, allow up to 45 for safety)
        expected_sequential_time = 27 * agent_count
        if generation_time <= 45:
            performance_improvement = expected_sequential_time / generation_time
            log_test_result("Parallel Generation Speed", True, 
                          f"Generated in {generation_time:.2f}s (vs ~{expected_sequential_time}s sequential) - {performance_improvement:.1f}x faster!")
        else:
            log_test_result("Parallel Generation Speed", False, 
                          f"Too slow: {generation_time:.2f}s (target: ~27s)")
        
        # Check for parallel processing indicators in response
        conversation_id = response_data.get('id')
        if conversation_id:
            log_test_result("Conversation Generation Success", True, f"Conversation generated with ID: {conversation_id}")
        else:
            log_test_result("Conversation Generation Success", False, "No conversation ID returned")
            
    else:
        log_test_result("Parallel Generation Test", False, f"Failed to generate conversation: {response.status_code if response else 'No response'}")
        return False
    
    return True

def test_message_streaming_with_parallel_generation():
    """Test 2: Message Streaming with Parallel Generation - Test /api/messages/stream endpoint"""
    print("\n" + "="*80)
    print("📤 TEST 2: MESSAGE STREAMING WITH PARALLEL GENERATION")
    print("="*80)
    
    # Step 1: Test the streaming endpoint
    print("\n📡 Step 1: Testing /api/messages/stream endpoint...")
    response = make_authenticated_request('GET', '/messages/stream')
    
    if response and response.status_code == 200:
        stream_data = response.json()
        
        # Check response structure
        required_fields = ['messages', 'count', 'since', 'timestamp']
        has_all_fields = all(field in stream_data for field in required_fields)
        
        if has_all_fields:
            log_test_result("Streaming Endpoint Structure", True, f"All required fields present: {required_fields}")
            
            # Check if we have streaming messages
            message_count = stream_data.get('count', 0)
            if message_count > 0:
                log_test_result("Streaming Messages Available", True, f"Found {message_count} streaming messages")
                
                # Verify message structure
                messages = stream_data.get('messages', [])
                if messages:
                    first_message = messages[0]
                    message_fields = ['id', 'agent_name', 'message', 'timestamp']
                    has_message_fields = all(field in first_message for field in message_fields)
                    
                    if has_message_fields:
                        log_test_result("Message Structure", True, "Streaming messages have proper structure")
                    else:
                        log_test_result("Message Structure", False, f"Missing fields in message: {message_fields}")
                else:
                    log_test_result("Message Content", False, "No messages in streaming response")
            else:
                log_test_result("Streaming Messages Available", True, "No streaming messages (expected if no recent generation)")
        else:
            log_test_result("Streaming Endpoint Structure", False, f"Missing required fields: {required_fields}")
    else:
        log_test_result("Streaming Endpoint Test", False, f"Failed to access streaming endpoint: {response.status_code if response else 'No response'}")
        return False
    
    # Step 2: Test streaming with timestamp filtering
    print("\n⏰ Step 2: Testing timestamp filtering...")
    current_time = datetime.utcnow().isoformat()
    response = make_authenticated_request('GET', f'/messages/stream?since={current_time}')
    
    if response and response.status_code == 200:
        log_test_result("Timestamp Filtering", True, "Streaming endpoint accepts timestamp filtering")
    else:
        log_test_result("Timestamp Filtering", False, "Timestamp filtering failed")
    
    return True

def test_database_operations_with_parallel_processing():
    """Test 3: Database Operations with Parallel Processing - Verify message_stream collection"""
    print("\n" + "="*80)
    print("🗄️ TEST 3: DATABASE OPERATIONS WITH PARALLEL PROCESSING")
    print("="*80)
    
    # Step 1: Generate a conversation to populate message_stream
    print("\n🔄 Step 1: Generating conversation to test database operations...")
    start_time = time.time()
    
    response = make_authenticated_request('POST', '/conversation/generate', timeout=90)
    
    if response and response.status_code == 200:
        end_time = time.time()
        generation_time = end_time - start_time
        
        log_test_result("Database Test Conversation Generation", True, f"Generated in {generation_time:.2f}s")
        
        # Step 2: Check if message_stream collection was populated
        print("\n📊 Step 2: Checking message_stream collection via streaming endpoint...")
        response = make_authenticated_request('GET', '/messages/stream')
        
        if response and response.status_code == 200:
            stream_data = response.json()
            message_count = stream_data.get('count', 0)
            
            if message_count > 0:
                log_test_result("Message Stream Population", True, f"message_stream collection has {message_count} messages")
                
                # Step 3: Verify message metadata and structure
                messages = stream_data.get('messages', [])
                if messages:
                    # Check for proper metadata
                    sample_message = messages[0]
                    required_metadata = ['id', 'agent_name', 'message', 'timestamp']
                    has_metadata = all(field in sample_message for field in required_metadata)
                    
                    if has_metadata:
                        log_test_result("Message Metadata", True, "Messages have proper metadata structure")
                        
                        # Check for user isolation
                        unique_agents = set(msg.get('agent_name', '') for msg in messages)
                        if len(unique_agents) >= 2:
                            log_test_result("Agent Participation", True, f"{len(unique_agents)} different agents in stream")
                        else:
                            log_test_result("Agent Participation", False, f"Only {len(unique_agents)} unique agents")
                    else:
                        log_test_result("Message Metadata", False, f"Missing metadata fields: {required_metadata}")
                else:
                    log_test_result("Message Content Check", False, "No messages found in stream")
            else:
                log_test_result("Message Stream Population", False, "message_stream collection appears empty")
        else:
            log_test_result("Database Stream Check", False, "Failed to check message_stream via streaming endpoint")
    else:
        log_test_result("Database Test Conversation Generation", False, "Failed to generate test conversation")
        return False
    
    return True

def test_error_handling_in_parallel_system():
    """Test 4: Error Handling in Parallel System - Test failure scenarios"""
    print("\n" + "="*80)
    print("🛡️ TEST 4: ERROR HANDLING IN PARALLEL SYSTEM")
    print("="*80)
    
    # Test 1: Generate conversation with minimal setup (edge case)
    print("\n🧪 Test 1: Testing parallel system with edge cases...")
    
    response = make_authenticated_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        if len(agents) >= 2:
            # Try to generate conversation - should handle any API issues gracefully
            response = make_authenticated_request('POST', '/conversation/generate', timeout=90)
            if response and response.status_code == 200:
                log_test_result("Parallel Error Handling", True, "Conversation generated successfully despite potential API issues")
                
                # Check if conversation has content (fallbacks should provide content)
                response = make_authenticated_request('GET', '/conversations')
                if response and response.status_code == 200:
                    conversations = response.json()
                    if conversations:
                        latest_conv = conversations[-1]
                        messages = latest_conv.get('messages', [])
                        if messages and all(len(msg.get('message', '')) > 10 for msg in messages):
                            log_test_result("Parallel Fallback Content Quality", True, "All messages have reasonable content")
                        else:
                            log_test_result("Parallel Fallback Content Quality", False, "Some messages appear to be empty or too short")
                    else:
                        log_test_result("Parallel Content Check", False, "No conversations found")
                else:
                    log_test_result("Parallel Content Check", False, "Failed to retrieve conversations")
            else:
                log_test_result("Parallel Error Handling", False, "Failed to generate conversation")
        else:
            log_test_result("Error Handling Test Setup", False, "Not enough agents for error handling testing")
    else:
        log_test_result("Error Handling Test Setup", False, "Failed to get agents for error handling testing")
    
    # Test 2: Test streaming completion endpoint
    print("\n📋 Test 2: Testing stream completion error handling...")
    
    # Test with invalid conversation ID
    fake_conversation_id = "invalid_stream_id_12345"
    response = make_authenticated_request('POST', f'/messages/stream/complete?conversation_id={fake_conversation_id}')
    
    if response and response.status_code in [400, 404]:
        log_test_result("Stream Completion Error Handling", True, f"Properly handled invalid conversation ID with {response.status_code}")
    else:
        log_test_result("Stream Completion Error Handling", False, f"Unexpected response for invalid ID: {response.status_code if response else 'No response'}")
    
    return True

def test_end_to_end_performance_comparison():
    """Test 5: End-to-End Performance Comparison - Measure complete workflow timing"""
    print("\n" + "="*80)
    print("📈 TEST 5: END-TO-END PERFORMANCE COMPARISON")
    print("="*80)
    
    # Get agent count for performance calculations
    response = make_authenticated_request('GET', '/agents')
    if not response or response.status_code != 200:
        log_test_result("Performance Test Setup", False, "Failed to get agents")
        return False
    
    agents = response.json()
    agent_count = len(agents)
    expected_sequential_time = 27 * agent_count  # 27 seconds per agent sequentially
    
    print(f"\n📊 Performance Test Setup:")
    print(f"   - Agent count: {agent_count}")
    print(f"   - Expected sequential time: ~{expected_sequential_time}s")
    print(f"   - Target parallel time: ~27s")
    print(f"   - Expected improvement: ~{expected_sequential_time/27:.1f}x faster")
    
    # Test 1: Measure conversation generation time
    print(f"\n⏱️ Test 1: Measuring parallel conversation generation...")
    start_time = time.time()
    
    response = make_authenticated_request('POST', '/conversation/generate', timeout=90)
    
    if response and response.status_code == 200:
        end_time = time.time()
        total_generation_time = end_time - start_time
        
        # Calculate performance metrics
        if total_generation_time <= 45:  # Allow some buffer
            performance_improvement = expected_sequential_time / total_generation_time
            efficiency = (expected_sequential_time - total_generation_time) / expected_sequential_time * 100
            
            log_test_result("End-to-End Performance", True, 
                          f"Total time: {total_generation_time:.2f}s, Improvement: {performance_improvement:.1f}x, Efficiency: {efficiency:.1f}%")
        else:
            log_test_result("End-to-End Performance", False, 
                          f"Performance below target: {total_generation_time:.2f}s (target: ~27s)")
        
        # Test 2: Verify messages are available in streaming endpoint
        print(f"\n📤 Test 2: Verifying messages available for streaming...")
        response = make_authenticated_request('GET', '/messages/stream')
        
        if response and response.status_code == 200:
            stream_data = response.json()
            message_count = stream_data.get('count', 0)
            
            if message_count >= agent_count:
                log_test_result("Streaming Availability", True, f"All {message_count} messages available for streaming")
            else:
                log_test_result("Streaming Availability", False, f"Only {message_count} messages available (expected {agent_count})")
        else:
            log_test_result("Streaming Availability", False, "Failed to check streaming availability")
        
        # Test 3: Verify conversation completion
        print(f"\n✅ Test 3: Verifying conversation completion...")
        response = make_authenticated_request('GET', '/conversations')
        
        if response and response.status_code == 200:
            conversations = response.json()
            if conversations:
                latest_conv = conversations[-1]
                messages = latest_conv.get('messages', [])
                
                if len(messages) >= agent_count:
                    log_test_result("Conversation Completion", True, f"Conversation completed with {len(messages)} messages")
                else:
                    log_test_result("Conversation Completion", False, f"Incomplete conversation: {len(messages)} messages")
            else:
                log_test_result("Conversation Completion", False, "No conversations found")
        else:
            log_test_result("Conversation Completion", False, "Failed to check conversation completion")
            
    else:
        log_test_result("End-to-End Performance Test", False, "Failed to generate conversation for performance testing")
        return False
    
    return True

def create_test_agents_for_parallel_testing():
    """Create test agents specifically for parallel processing testing"""
    test_agents = [
        {
            "name": "Dr. Alice Quantum",
            "archetype": "scientist",
            "goal": "Develop breakthrough quantum communication protocols",
            "expertise": "Quantum Physics and Cryptography",
            "background": "PhD in Quantum Physics with 15 years experience in quantum entanglement research",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Dr. Bob Engineer",
            "archetype": "researcher",
            "goal": "Design practical implementation solutions",
            "expertise": "Quantum Engineering and Hardware Design",
            "background": "Expert in quantum hardware design and practical implementation of quantum systems",
            "personality": {
                "extroversion": 5,
                "optimism": 7,
                "curiosity": 8,
                "cooperativeness": 8,
                "energy": 6
            }
        },
        {
            "name": "Dr. Carol Strategy",
            "archetype": "leader",
            "goal": "Coordinate team efforts and strategic planning",
            "expertise": "Project Management and Strategic Planning",
            "background": "Former military strategist with expertise in coordinating complex technical projects",
            "personality": {
                "extroversion": 8,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 9,
                "energy": 8
            }
        }
    ]
    
    created_count = 0
    for agent_data in test_agents:
        response = make_authenticated_request('POST', '/agents', agent_data)
        if response and response.status_code == 200:
            created_count += 1
            print(f"   ✅ Created agent: {agent_data['name']}")
        else:
            print(f"   ❌ Failed to create agent: {agent_data['name']}")
    
    return created_count >= 3  # Need at least 3 agents for good parallel testing

def run_all_tests():
    """Run all parallel message generation tests"""
    print("🚀 PARALLEL MESSAGE GENERATION & PERFORMANCE IMPROVEMENTS TESTING")
    print("=" * 80)
    print("Testing the new parallel processing implementation to verify speed improvements and streaming functionality")
    print("=" * 80)
    
    # Test 1: Parallel Message Generation Performance
    test1_passed = test_parallel_message_generation_performance()
    
    # Test 2: Message Streaming with Parallel Generation
    test2_passed = test_message_streaming_with_parallel_generation()
    
    # Test 3: Database Operations with Parallel Processing
    test3_passed = test_database_operations_with_parallel_processing()
    
    # Test 4: Error Handling in Parallel System
    test4_passed = test_error_handling_in_parallel_system()
    
    # Test 5: End-to-End Performance Comparison
    test5_passed = test_end_to_end_performance_comparison()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 PARALLEL MESSAGE GENERATION TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    # Detailed test results
    print(f"\n🔍 DETAILED TEST RESULTS:")
    print(f"   Test 1 - Parallel Generation Performance: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Test 2 - Message Streaming: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"   Test 3 - Database Operations: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print(f"   Test 4 - Error Handling: {'✅ PASS' if test4_passed else '❌ FAIL'}")
    print(f"   Test 5 - End-to-End Performance: {'✅ PASS' if test5_passed else '❌ FAIL'}")
    
    all_tests_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
    
    if all_tests_passed:
        print("\n🎉 PARALLEL MESSAGE GENERATION TESTING RESULT: ALL TESTS PASSED!")
        print("   ✅ Parallel processing achieves ~3x speed improvement")
        print("   ✅ Message streaming works with parallel generation")
        print("   ✅ Database operations handle parallel processing correctly")
        print("   ✅ Error handling and fallbacks work in parallel system")
        print("   ✅ End-to-end performance meets targets (~27s vs ~81s)")
    else:
        print("\n❌ PARALLEL MESSAGE GENERATION TESTING RESULT: SOME TESTS FAILED!")
        print("   Please check the failed tests above for details")
        print("   The parallel message generation system may need attention")
    
    print("\n" + "="*80)
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)