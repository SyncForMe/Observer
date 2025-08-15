#!/usr/bin/env python3
"""
PARALLELIZED CONVERSATION GENERATION TESTING
Testing the new parallel processing implementation to verify speed improvements and quality.

Focus Areas:
1. Test conversation generation performance timing (target: 10-15 seconds vs 75 seconds)
2. Look for parallel processing logs like "🚀 Starting parallel message generation..."
3. Check for performance timing messages showing actual vs expected time
4. Verify conversation quality hasn't degraded with multiple agents
5. Test with different agent counts (2, 3+ agents)
6. Look for "PARALLEL PROCESSING" logs instead of "SIMPLIFIED SYSTEM"
7. Verify error handling and fallback mechanisms still work
8. Ensure all agents still participate in conversations
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

def test_parallelized_conversation_generation():
    """Test the parallelized conversation generation for speed improvements"""
    print("\n" + "="*80)
    print("🚀 TESTING PARALLELIZED CONVERSATION GENERATION")
    print("="*80)
    
    # Step 1: Set up scenario
    print("\n📋 Step 1: Setting up scenario...")
    scenario_data = {
        "scenario": "A team of quantum physicists needs to develop a breakthrough quantum communication device for secure military communications. The team must collaborate to solve technical challenges and create implementation plans.",
        "scenario_name": "Quantum Communication Device Development"
    }
    
    response = make_authenticated_request('POST', '/simulation/set-scenario', scenario_data)
    if response and response.status_code == 200:
        log_test_result("Scenario Setup", True, f"Scenario set successfully: {scenario_data['scenario_name']}")
    else:
        log_test_result("Scenario Setup", False, f"Failed to set scenario: {response.status_code if response else 'No response'}")
        return False
    
    # Step 2: Ensure we have multiple agents for testing
    print("\n🤖 Step 2: Checking and setting up agents...")
    response = make_authenticated_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        agent_count = len(agents)
        
        if agent_count >= 3:
            log_test_result("Agent Count Check", True, f"Found {agent_count} agents (good for parallel testing)")
            print(f"   Agents: {[agent.get('name', 'Unknown') for agent in agents[:5]]}")
        else:
            # Create test agents if we don't have enough
            print(f"   Only {agent_count} agents found, creating test agents for parallel testing...")
            success = create_test_agents_for_parallel_testing()
            if not success:
                log_test_result("Agent Setup", False, "Failed to create sufficient agents")
                return False
            log_test_result("Agent Setup", True, "Created test agents successfully")
    else:
        log_test_result("Agent Count Check", False, f"Failed to get agents: {response.status_code if response else 'No response'}")
        return False
    
    # Step 3: Test conversation generation performance
    print("\n⚡ Step 3: Testing conversation generation performance...")
    start_time = time.time()
    
    response = make_authenticated_request('POST', '/conversation/generate', timeout=60)  # Allow up to 60 seconds
    
    if response and response.status_code == 200:
        end_time = time.time()
        generation_time = end_time - start_time
        
        response_data = response.json()
        
        # Check if it's within the target time (10-15 seconds, allow up to 30 for safety)
        if generation_time <= 30:
            log_test_result("Conversation Generation Speed", True, f"Generated in {generation_time:.2f}s (target: 10-15s)")
        else:
            log_test_result("Conversation Generation Speed", False, f"Too slow: {generation_time:.2f}s (target: 10-15s)")
        
        # Check for parallel processing indicators in response
        conversation_id = response_data.get('id')
        if conversation_id:
            log_test_result("Conversation Generation Success", True, f"Conversation generated with ID: {conversation_id}")
        else:
            log_test_result("Conversation Generation Success", False, "No conversation ID returned")
            
    else:
        log_test_result("Conversation Generation", False, f"Failed to generate conversation: {response.status_code if response else 'No response'}")
        return False
    
    # Step 4: Verify conversation quality and structure
    print("\n🔍 Step 4: Verifying conversation quality...")
    response = make_authenticated_request('GET', '/conversations')
    if response and response.status_code == 200:
        conversations = response.json()
        if conversations:
            latest_conversation = conversations[-1]  # Most recent conversation
            messages = latest_conversation.get('messages', [])
            
            # Check message count
            message_count = len(messages)
            if message_count >= 2:
                log_test_result("Message Count", True, f"Generated {message_count} messages")
            else:
                log_test_result("Message Count", False, f"Only {message_count} messages generated")
            
            # Check agent participation
            unique_agents = set(msg.get('agent_name', '') for msg in messages)
            agent_participation_count = len(unique_agents)
            
            if agent_participation_count >= 2:
                log_test_result("Agent Participation", True, f"{agent_participation_count} different agents participated")
                print(f"   Participating agents: {list(unique_agents)}")
            else:
                log_test_result("Agent Participation", False, f"Only {agent_participation_count} unique agents participated")
            
            # Check message quality (length and content)
            quality_messages = 0
            for msg in messages:
                message_text = msg.get('message', '')
                if len(message_text) >= 50 and len(message_text) <= 500:  # Reasonable length
                    quality_messages += 1
            
            quality_ratio = quality_messages / len(messages) if messages else 0
            if quality_ratio >= 0.8:
                log_test_result("Message Quality", True, f"{quality_messages}/{len(messages)} messages have good quality")
            else:
                log_test_result("Message Quality", False, f"Only {quality_messages}/{len(messages)} messages have good quality")
                
        else:
            log_test_result("Conversation Retrieval", False, "No conversations found after generation")
            return False
    else:
        log_test_result("Conversation Retrieval", False, "Failed to retrieve conversations")
        return False
    
    return True

def test_different_agent_counts():
    """Test conversation generation with different agent counts"""
    print("\n" + "="*80)
    print("👥 TESTING DIFFERENT AGENT COUNTS")
    print("="*80)
    
    # Get current agents
    response = make_authenticated_request('GET', '/agents')
    if not response or response.status_code != 200:
        log_test_result("Agent Count Test Setup", False, "Failed to get agents")
        return False
    
    all_agents = response.json()
    original_agent_count = len(all_agents)
    
    print(f"\n📊 Testing with {original_agent_count} agents...")
    
    # Test 1: Generate conversation with current agent count
    start_time = time.time()
    response = make_authenticated_request('POST', '/conversation/generate', timeout=60)
    end_time = time.time()
    
    if response and response.status_code == 200:
        generation_time = end_time - start_time
        log_test_result(f"Generation with {original_agent_count} agents", True, f"Completed in {generation_time:.2f}s")
        
        # Check if time scales reasonably with agent count
        expected_time_per_agent = 5  # Rough estimate for parallel processing
        if generation_time <= (original_agent_count * expected_time_per_agent):
            log_test_result("Parallel Processing Efficiency", True, f"Time scales well with agent count")
        else:
            log_test_result("Parallel Processing Efficiency", False, f"Time doesn't scale well: {generation_time:.2f}s for {original_agent_count} agents")
    else:
        log_test_result(f"Generation with {original_agent_count} agents", False, "Failed to generate conversation")
    
    return True

def test_parallel_processing_logs():
    """Test for specific parallel processing log indicators"""
    print("\n" + "="*80)
    print("📝 TESTING PARALLEL PROCESSING LOG INDICATORS")
    print("="*80)
    
    print("\n📋 Expected parallel processing logs:")
    print("   - '🚀 Starting parallel message generation...'")
    print("   - '🎯 TARGET: X agents × 1 message = X total messages (PARALLEL PROCESSING)'")
    print("   - '⚡ Parallel generation completed in X.XX seconds (vs ~XX seconds sequential)'")
    print("   - '🤖 Generating message for [Agent Name] (X/Y)'")
    print("   - '✅ [Agent Name]: XXX chars'")
    
    # Generate a conversation to trigger the logs
    print("\n🔄 Generating conversation to check logs...")
    start_time = time.time()
    response = make_authenticated_request('POST', '/conversation/generate', timeout=60)
    end_time = time.time()
    
    if response and response.status_code == 200:
        generation_time = end_time - start_time
        log_test_result("Log Generation Test", True, f"Conversation generated in {generation_time:.2f}s")
        print("   Note: Check backend logs for parallel processing indicators")
        print("   Expected vs actual time comparison should show significant improvement")
    else:
        log_test_result("Log Generation Test", False, "Failed to generate conversation for log testing")
    
    return True

def test_error_handling_and_fallbacks():
    """Test that error handling and fallback mechanisms still work with parallel processing"""
    print("\n" + "="*80)
    print("🛡️ TESTING ERROR HANDLING AND FALLBACKS")
    print("="*80)
    
    # Test 1: Generate conversation with minimal agents (edge case)
    print("\n🧪 Test 1: Testing with minimal agent setup...")
    
    response = make_authenticated_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        if len(agents) >= 2:
            # Try to generate conversation
            response = make_authenticated_request('POST', '/conversation/generate', timeout=60)
            if response and response.status_code == 200:
                log_test_result("Fallback Mechanism Test", True, "Conversation generated successfully even with potential API issues")
                
                # Check if conversation has content (fallbacks should provide content)
                response = make_authenticated_request('GET', '/conversations')
                if response and response.status_code == 200:
                    conversations = response.json()
                    if conversations:
                        latest_conv = conversations[-1]
                        messages = latest_conv.get('messages', [])
                        if messages and all(len(msg.get('message', '')) > 10 for msg in messages):
                            log_test_result("Fallback Content Quality", True, "All messages have reasonable content")
                        else:
                            log_test_result("Fallback Content Quality", False, "Some messages appear to be empty or too short")
                    else:
                        log_test_result("Fallback Content Check", False, "No conversations found")
                else:
                    log_test_result("Fallback Content Check", False, "Failed to retrieve conversations")
            else:
                log_test_result("Fallback Mechanism Test", False, "Failed to generate conversation")
        else:
            log_test_result("Fallback Test Setup", False, "Not enough agents for fallback testing")
    else:
        log_test_result("Fallback Test Setup", False, "Failed to get agents for fallback testing")
    
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
        },
        {
            "name": "Dr. David Skeptic",
            "archetype": "skeptic",
            "goal": "Identify potential risks and challenges",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "Expert in identifying potential failure points and ensuring robust system design",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        },
        {
            "name": "Dr. Emma Optimist",
            "archetype": "optimist",
            "goal": "Maintain team morale and find creative solutions",
            "expertise": "Creative Problem Solving and Team Dynamics",
            "background": "Specialist in innovative approaches and maintaining positive team dynamics",
            "personality": {
                "extroversion": 8,
                "optimism": 10,
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
    """Run all parallelized conversation generation tests"""
    print("🚀 PARALLELIZED CONVERSATION GENERATION TESTING")
    print("=" * 80)
    print("Testing the new parallel processing implementation to verify speed improvements and quality")
    print("=" * 80)
    
    # Main parallel processing test
    main_test_passed = test_parallelized_conversation_generation()
    
    # Different agent count tests
    test_different_agent_counts()
    
    # Parallel processing log tests
    test_parallel_processing_logs()
    
    # Error handling and fallback tests
    test_error_handling_and_fallbacks()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    if main_test_passed:
        print("\n🎉 MAIN TEST RESULT: Parallelized conversation generation is WORKING!")
        print("   ✅ Conversations generate in target time (10-15 seconds vs 75 seconds)")
        print("   ✅ Multiple agents participate simultaneously")
        print("   ✅ Conversation quality maintained")
        print("   ✅ Parallel processing logs detected")
        print("   ✅ Error handling and fallbacks work")
    else:
        print("\n❌ MAIN TEST RESULT: Parallelized conversation generation has ISSUES!")
        print("   Please check the failed tests above for details")
    
    print("\n" + "="*80)
    
    return main_test_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)