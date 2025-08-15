#!/usr/bin/env python3
"""
CRITICAL SIMULATION START ENDPOINT TESTING
Investigating why /api/simulation/start endpoint is hanging/getting stuck.

Focus Areas:
1. Test /api/simulation/start endpoint directly with proper authentication
2. Monitor how long it takes to respond and check for timeouts
3. Check conversation generation within start endpoint
4. Look for hanging LLM API calls or parallel processing issues
5. Test with timeout scenarios and error handling
6. Check database operations for deadlocks
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import threading
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

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

def make_authenticated_request(method, endpoint, data=None, timeout=120):
    """Make an authenticated request to the API with extended timeout"""
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

def setup_test_environment():
    """Set up the test environment with agents and scenario"""
    print("\n" + "="*80)
    print("🔧 SETTING UP TEST ENVIRONMENT")
    print("="*80)
    
    # Step 1: Check current agents
    print("\n🤖 Step 1: Checking existing agents...")
    response = make_authenticated_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        print(f"   Found {len(agents)} existing agents")
        
        if len(agents) >= 3:
            print("   ✅ Sufficient agents for testing")
            agent_names = [agent.get('name', 'Unknown') for agent in agents[:5]]
            print(f"   Agents: {agent_names}")
        else:
            print("   ⚠️ Need more agents, creating test agents...")
            success = create_test_agents()
            if not success:
                print("   ❌ Failed to create test agents")
                return False
    else:
        print("   ❌ Failed to get agents")
        return False
    
    # Step 2: Set up scenario
    print("\n📋 Step 2: Setting up scenario...")
    scenario_data = {
        "scenario": "Swarm Robotics Military Coup - A team of military robotics experts must develop countermeasures against an AI-controlled swarm of autonomous military robots that have gone rogue and are threatening civilian populations.",
        "scenario_name": "Swarm Robotics Military Coup"
    }
    
    response = make_authenticated_request('POST', '/simulation/set-scenario', scenario_data)
    if response and response.status_code == 200:
        print("   ✅ Scenario set successfully")
        print(f"   Scenario: {scenario_data['scenario_name']}")
    else:
        print(f"   ❌ Failed to set scenario: {response.status_code if response else 'No response'}")
        return False
    
    print("\n✅ Test environment setup complete")
    return True

def create_test_agents():
    """Create test agents for simulation"""
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Develop technical countermeasures against rogue AI swarms",
            "expertise": "AI Systems and Robotics Security",
            "background": "Leading expert in AI safety and autonomous systems security with 15 years experience",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            }
        },
        {
            "name": "Dr. James Park",
            "archetype": "leader",
            "goal": "Coordinate military response and strategic planning",
            "expertise": "Military Strategy and Crisis Management",
            "background": "Former military commander with expertise in coordinating complex defense operations",
            "personality": {
                "extroversion": 8,
                "optimism": 6,
                "curiosity": 6,
                "cooperativeness": 9,
                "energy": 8
            }
        },
        {
            "name": "Dr. Marcus Rodriguez",
            "archetype": "skeptic",
            "goal": "Identify vulnerabilities and potential failure points",
            "expertise": "Cybersecurity and Risk Analysis",
            "background": "Expert in identifying security vulnerabilities and analyzing potential attack vectors",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 8,
                "cooperativeness": 6,
                "energy": 5
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
    
    return created_count >= 3

def test_simulation_start_endpoint():
    """Test the /api/simulation/start endpoint for hanging issues"""
    print("\n" + "="*80)
    print("🚀 TESTING SIMULATION START ENDPOINT")
    print("="*80)
    
    # Test with different timeout scenarios
    timeout_tests = [
        {"timeout": 30, "description": "30-second timeout (expected completion time)"},
        {"timeout": 60, "description": "60-second timeout (maximum expected time)"},
        {"timeout": 120, "description": "120-second timeout (extended for debugging)"}
    ]
    
    for test_config in timeout_tests:
        timeout = test_config["timeout"]
        description = test_config["description"]
        
        print(f"\n🧪 Testing with {description}")
        print(f"   Expected behavior: Complete in 15-35 seconds")
        
        # Record start time
        start_time = time.time()
        print(f"   Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Make the request
        response = make_authenticated_request('POST', '/simulation/start', None, timeout)
        
        # Record end time
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   End time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Duration: {duration:.2f} seconds")
        
        if response is None:
            print(f"   ❌ TIMEOUT: Request timed out after {timeout} seconds")
            print(f"   🚨 CRITICAL: Endpoint is hanging - this confirms the user's issue")
            
            # If we timeout, try to get more info
            print(f"   🔍 Checking simulation state after timeout...")
            state_response = make_authenticated_request('GET', '/simulation/state', None, 10)
            if state_response and state_response.status_code == 200:
                state_data = state_response.json()
                is_active = state_data.get('is_active', False)
                print(f"   Simulation active: {is_active}")
                if is_active:
                    print(f"   ⚠️ Simulation marked as active despite timeout - partial completion")
                else:
                    print(f"   ❌ Simulation not active - complete failure")
            
            return False
            
        elif response.status_code == 200:
            print(f"   ✅ SUCCESS: Completed in {duration:.2f} seconds")
            
            # Check response content
            try:
                response_data = response.json()
                success = response_data.get('success', False)
                message = response_data.get('message', '')
                
                print(f"   Response success: {success}")
                print(f"   Response message: {message}")
                
                # Check if conversation was generated
                if 'Initial conversation generated successfully' in str(response_data):
                    print(f"   ✅ Automatic conversation generation worked")
                else:
                    print(f"   ⚠️ No indication of conversation generation")
                
                # Verify simulation state
                state_response = make_authenticated_request('GET', '/simulation/state', None, 10)
                if state_response and state_response.status_code == 200:
                    state_data = state_response.json()
                    is_active = state_data.get('is_active', False)
                    print(f"   Simulation active: {is_active}")
                
                # Check if conversations were created
                conv_response = make_authenticated_request('GET', '/conversations', None, 10)
                if conv_response and conv_response.status_code == 200:
                    conversations = conv_response.json()
                    print(f"   Conversations created: {len(conversations)}")
                    if conversations:
                        latest_conv = conversations[-1]
                        messages = latest_conv.get('messages', [])
                        print(f"   Messages in latest conversation: {len(messages)}")
                
                if duration <= 35:
                    print(f"   ✅ PERFORMANCE: Within expected time range (15-35s)")
                    return True
                else:
                    print(f"   ⚠️ SLOW: Took longer than expected (>35s) but completed")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Error parsing response: {e}")
                return False
                
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
    
    return False

def test_conversation_generation_directly():
    """Test conversation generation endpoint directly to isolate issues"""
    print("\n" + "="*80)
    print("💬 TESTING CONVERSATION GENERATION DIRECTLY")
    print("="*80)
    
    print("\n🧪 Testing /api/conversation/generate endpoint...")
    
    start_time = time.time()
    response = make_authenticated_request('POST', '/conversation/generate', None, 60)
    end_time = time.time()
    duration = end_time - start_time
    
    if response is None:
        print(f"   ❌ TIMEOUT: Conversation generation timed out after 60 seconds")
        print(f"   🚨 This indicates the parallel processing is hanging")
        return False
    elif response.status_code == 200:
        print(f"   ✅ SUCCESS: Conversation generated in {duration:.2f} seconds")
        
        try:
            response_data = response.json()
            conv_id = response_data.get('id')
            print(f"   Conversation ID: {conv_id}")
            
            # Check conversation content
            conv_response = make_authenticated_request('GET', '/conversations', None, 10)
            if conv_response and conv_response.status_code == 200:
                conversations = conv_response.json()
                if conversations:
                    latest_conv = conversations[-1]
                    messages = latest_conv.get('messages', [])
                    print(f"   Messages generated: {len(messages)}")
                    
                    # Check message quality
                    for i, msg in enumerate(messages[:3]):
                        agent_name = msg.get('agent_name', 'Unknown')
                        message_text = msg.get('message', '')
                        print(f"   Message {i+1} ({agent_name}): {len(message_text)} chars")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error parsing response: {e}")
            return False
    else:
        print(f"   ❌ FAILED: HTTP {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Error: {response.text}")
        return False

def monitor_backend_during_test():
    """Monitor backend behavior during simulation start"""
    print("\n" + "="*80)
    print("📊 MONITORING BACKEND DURING SIMULATION START")
    print("="*80)
    
    print("\n🔍 Expected backend logs to look for:")
    print("   - '🚀 Starting automatic conversation generation...'")
    print("   - '🤖 Found X agents, generating initial conversation...'")
    print("   - '🚀 Starting parallel message generation...'")
    print("   - '⚡ Parallel generation completed in X.XX seconds'")
    print("   - '✅ Initial conversation generated successfully'")
    
    print("\n⚠️ Warning signs to watch for:")
    print("   - Long delays without log output")
    print("   - Repeated timeout errors from LLM APIs")
    print("   - Database connection errors")
    print("   - Asyncio task hanging messages")
    
    print("\n🧪 Starting monitored simulation start test...")
    
    # Start the simulation start request
    start_time = time.time()
    print(f"   Sending POST /api/simulation/start at {datetime.now().strftime('%H:%M:%S')}")
    
    response = make_authenticated_request('POST', '/simulation/start', None, 90)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   Request completed at {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Total duration: {duration:.2f} seconds")
    
    if response is None:
        print(f"   ❌ CONFIRMED HANG: Request timed out after 90 seconds")
        print(f"   🚨 ROOT CAUSE: The endpoint is definitely hanging")
        print(f"   📋 LIKELY CAUSES:")
        print(f"      - LLM API calls hanging in parallel processing")
        print(f"      - Database operations deadlocking")
        print(f"      - Asyncio tasks not completing properly")
        print(f"      - Infinite loops in conversation generation")
        return False
    else:
        print(f"   ✅ Request completed successfully")
        return True

def run_comprehensive_test():
    """Run comprehensive test suite for simulation start hanging issue"""
    print("🚨 CRITICAL SIMULATION START ENDPOINT INVESTIGATION")
    print("=" * 80)
    print("Investigating why /api/simulation/start endpoint is hanging/getting stuck")
    print("User report: Play button stuck in loading state with proper setup")
    print("=" * 80)
    
    # Test results tracking
    results = {
        "setup": False,
        "simulation_start": False,
        "conversation_generation": False,
        "monitoring": False
    }
    
    # Step 1: Setup test environment
    results["setup"] = setup_test_environment()
    if not results["setup"]:
        print("\n❌ CRITICAL: Test environment setup failed")
        return False
    
    # Step 2: Test simulation start endpoint
    results["simulation_start"] = test_simulation_start_endpoint()
    
    # Step 3: Test conversation generation directly
    results["conversation_generation"] = test_conversation_generation_directly()
    
    # Step 4: Monitor backend during test
    results["monitoring"] = monitor_backend_during_test()
    
    # Summary
    print("\n" + "="*80)
    print("📊 INVESTIGATION SUMMARY")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name.replace('_', ' ').title()}")
    
    # Root cause analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    
    if not results["simulation_start"]:
        print(f"   🚨 CONFIRMED: /api/simulation/start endpoint is hanging")
        print(f"   📋 EVIDENCE: Request times out consistently")
        print(f"   🎯 LOCATION: Issue is in the automatic conversation generation")
        print(f"   💡 LIKELY CAUSE: Parallel LLM API calls hanging or deadlocking")
        
        if not results["conversation_generation"]:
            print(f"   🔍 DEEPER ISSUE: /api/conversation/generate also hangs")
            print(f"   📍 SPECIFIC LOCATION: Parallel message generation in asyncio.gather()")
            print(f"   🛠️ RECOMMENDED FIX: Add timeout to individual LLM API calls")
        else:
            print(f"   🔍 ISOLATED ISSUE: Only simulation start hangs, not conversation generation")
            print(f"   📍 SPECIFIC LOCATION: Integration between start endpoint and conversation generation")
    else:
        print(f"   ✅ UNEXPECTED: Simulation start is working in this test")
        print(f"   🤔 POSSIBLE CAUSES: Intermittent issue, load-dependent, or environment-specific")
    
    print(f"\n🎯 RECOMMENDATIONS FOR MAIN AGENT:")
    if not results["simulation_start"]:
        print(f"   1. Add timeout to asyncio.gather() in parallel message generation")
        print(f"   2. Add individual timeouts to LLM API calls (6-10 seconds max)")
        print(f"   3. Implement circuit breaker pattern for LLM failures")
        print(f"   4. Add more detailed logging in conversation generation")
        print(f"   5. Consider reducing parallel processing to sequential for reliability")
    else:
        print(f"   1. Monitor for intermittent issues")
        print(f"   2. Add more robust error handling")
        print(f"   3. Implement health checks for LLM APIs")
    
    return results["simulation_start"]

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)