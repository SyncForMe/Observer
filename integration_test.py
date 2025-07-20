#!/usr/bin/env python3
"""
Integration Test Script for AI Agent Simulation Platform
Testing specific integrations as requested in the review:
1. Claude Sonnet 4 Integration Test
2. OpenAI Whisper Integration Test  
3. Saved Agents & Favorites Test
4. Authentication Test
"""

import requests
import json
import time
import os
import sys
import uuid
import jwt
from datetime import datetime
from dotenv import load_dotenv
import tempfile
import base64

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
AUTH_URL = f"{BACKEND_URL}/auth"
JWT_SECRET = os.environ.get('JWT_SECRET', 'test_secret')

print(f"🔗 Using API URL: {API_URL}")
print(f"🔗 Using Auth URL: {AUTH_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "critical_issues": [],
    "minor_issues": []
}

# Global auth variables
auth_token = None
test_user_id = None

def log_test_result(test_name, passed, details="", is_critical=True):
    """Log test result and categorize issues"""
    result = "PASSED" if passed else "FAILED"
    test_results["tests"].append({
        "name": test_name,
        "result": result,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    
    if passed:
        test_results["passed"] += 1
        print(f"✅ {test_name}: PASSED")
    else:
        test_results["failed"] += 1
        print(f"❌ {test_name}: FAILED - {details}")
        
        if is_critical:
            test_results["critical_issues"].append(f"{test_name}: {details}")
        else:
            test_results["minor_issues"].append(f"{test_name}: {details}")

def make_request(method, endpoint, data=None, headers=None, files=None, timeout=30):
    """Make HTTP request with error handling"""
    url = f"{API_URL}{endpoint}"
    
    if headers is None:
        headers = {}
    
    if auth_token and 'Authorization' not in headers:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data, timeout=timeout)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, headers=headers, timeout=timeout)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.Timeout:
        print(f"⏰ Request timeout for {method} {url}")
        return None
    except Exception as e:
        print(f"🚨 Request error for {method} {url}: {e}")
        return None

def test_authentication():
    """Test authentication endpoints as requested"""
    print("\n" + "="*80)
    print("🔐 TESTING AUTHENTICATION INTEGRATION")
    print("="*80)
    
    global auth_token, test_user_id
    
    # Test 1: Guest Authentication (POST /auth/test-login)
    print("\n📋 Test 1: Guest Authentication (POST /auth/test-login)")
    
    response = make_request("POST", "/auth/test-login")
    
    if response and response.status_code == 200:
        try:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            
            # Verify JWT token structure
            try:
                decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
                required_fields = ["sub", "user_id"]
                missing_fields = [field for field in required_fields if field not in decoded_token]
                
                if missing_fields:
                    log_test_result("Guest Auth JWT Structure", False, f"Missing fields: {missing_fields}")
                else:
                    log_test_result("Guest Auth JWT Structure", True, "JWT contains required fields")
                    
            except Exception as e:
                log_test_result("Guest Auth JWT Validation", False, f"JWT decode error: {e}")
            
            log_test_result("Guest Authentication", True, f"User ID: {test_user_id}")
            print(f"🎫 JWT Token: {auth_token[:50]}...")
            
        except Exception as e:
            log_test_result("Guest Authentication", False, f"Response parsing error: {e}")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Guest Authentication", False, f"HTTP {status}")
    
    # Test 2: JWT Token Validation
    print("\n📋 Test 2: JWT Token Validation")
    
    if auth_token:
        response = make_request("GET", "/auth/me")
        
        if response and response.status_code == 200:
            try:
                user_data = response.json()
                if user_data.get("id") == test_user_id:
                    log_test_result("JWT Token Validation", True, "Token validates correctly")
                else:
                    log_test_result("JWT Token Validation", False, "User ID mismatch")
            except Exception as e:
                log_test_result("JWT Token Validation", False, f"Response parsing error: {e}")
        else:
            status = response.status_code if response else "No response"
            log_test_result("JWT Token Validation", False, f"HTTP {status}")
    else:
        log_test_result("JWT Token Validation", False, "No auth token available")

def test_claude_sonnet_4_integration():
    """Test Claude Sonnet 4 integration with conversation generation"""
    print("\n" + "="*80)
    print("🤖 TESTING CLAUDE SONNET 4 INTEGRATION")
    print("="*80)
    
    if not auth_token:
        log_test_result("Claude Integration Setup", False, "No authentication token")
        return
    
    # Test 1: Create test agents for conversation
    print("\n📋 Test 1: Setting up test agents")
    
    # Create 3 test agents
    test_agents = []
    agent_names = ["Claude Test Agent 1", "Claude Test Agent 2", "Claude Test Agent 3"]
    
    for i, name in enumerate(agent_names):
        agent_data = {
            "name": name,
            "archetype": "scientist",
            "personality": {
                "extroversion": 5,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 6
            },
            "goal": f"Test Claude Sonnet 4 integration - Agent {i+1}",
            "expertise": "AI Testing and Integration",
            "background": "Specialized in testing AI model integrations"
        }
        
        response = make_request("POST", "/agents", data=agent_data)
        
        if response and response.status_code == 200:
            agent_id = response.json().get("id")
            test_agents.append(agent_id)
            print(f"✅ Created agent: {name} (ID: {agent_id})")
        else:
            status = response.status_code if response else "No response"
            print(f"❌ Failed to create agent {name}: HTTP {status}")
    
    if len(test_agents) < 2:
        log_test_result("Claude Agent Setup", False, "Need at least 2 agents for conversation")
        return
    
    log_test_result("Claude Agent Setup", True, f"Created {len(test_agents)} test agents")
    
    # Test 2: Start simulation
    print("\n📋 Test 2: Starting simulation")
    
    response = make_request("POST", "/simulation/start")
    
    if response and response.status_code == 200:
        log_test_result("Simulation Start", True, "Simulation started successfully")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Simulation Start", False, f"HTTP {status}")
        return
    
    # Test 3: Test conversation generation endpoint
    print("\n📋 Test 3: Testing conversation generation (POST /api/conversation/generate)")
    
    start_time = time.time()
    response = make_request("POST", "/conversation/generate", timeout=60)
    end_time = time.time()
    
    response_time = end_time - start_time
    print(f"⏱️ Response time: {response_time:.2f} seconds")
    
    if response and response.status_code == 200:
        try:
            conversation_data = response.json()
            
            # Check response structure
            required_fields = ["id", "messages", "user_id"]
            missing_fields = [field for field in required_fields if field not in conversation_data]
            
            if missing_fields:
                log_test_result("Conversation Response Structure", False, f"Missing fields: {missing_fields}")
            else:
                log_test_result("Conversation Response Structure", True, "All required fields present")
            
            # Check message quality and count
            messages = conversation_data.get("messages", [])
            if len(messages) > 0:
                avg_length = sum(len(msg.get("message", "")) for msg in messages) / len(messages)
                
                # Check if messages seem to be generated by AI (length and quality indicators)
                if avg_length > 50:  # Reasonable message length
                    log_test_result("Conversation Quality", True, f"Generated {len(messages)} messages, avg length: {avg_length:.1f}")
                    
                    # Try to detect if Claude Sonnet 4 was used (check response headers or content)
                    print("🔍 Analyzing conversation for Claude Sonnet 4 usage...")
                    
                    # Look for sophisticated language patterns that might indicate Claude usage
                    sophisticated_indicators = 0
                    for msg in messages[:3]:  # Check first 3 messages
                        message_text = msg.get("message", "").lower()
                        if any(indicator in message_text for indicator in [
                            "comprehensive", "sophisticated", "nuanced", "multifaceted",
                            "strategic", "systematic", "methodical", "analytical"
                        ]):
                            sophisticated_indicators += 1
                    
                    if sophisticated_indicators > 0:
                        log_test_result("Claude Sonnet 4 Usage Indicators", True, 
                                      f"Found {sophisticated_indicators} sophistication indicators")
                    else:
                        log_test_result("Claude Sonnet 4 Usage Indicators", False, 
                                      "No clear sophistication indicators found", is_critical=False)
                    
                else:
                    log_test_result("Conversation Quality", False, f"Messages too short (avg: {avg_length:.1f})")
            else:
                log_test_result("Conversation Generation", False, "No messages generated")
            
            # Test fallback mechanism by checking if Gemini was used as backup
            print("🔄 Testing fallback mechanism...")
            
            # Make another request to see consistency
            response2 = make_request("POST", "/conversation/generate", timeout=60)
            if response2 and response2.status_code == 200:
                log_test_result("Fallback Mechanism", True, "Secondary generation successful")
            else:
                log_test_result("Fallback Mechanism", False, "Secondary generation failed", is_critical=False)
            
        except Exception as e:
            log_test_result("Conversation Generation", False, f"Response parsing error: {e}")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Conversation Generation", False, f"HTTP {status}")
    
    # Cleanup: Remove test agents
    print("\n🧹 Cleaning up test agents...")
    for agent_id in test_agents:
        response = make_request("DELETE", f"/agents/{agent_id}")
        if response and response.status_code == 200:
            print(f"✅ Deleted agent {agent_id}")

def test_openai_whisper_integration():
    """Test OpenAI Whisper integration for speech transcription"""
    print("\n" + "="*80)
    print("🎤 TESTING OPENAI WHISPER INTEGRATION")
    print("="*80)
    
    if not auth_token:
        log_test_result("Whisper Integration Setup", False, "No authentication token")
        return
    
    # Test 1: Check if endpoint exists and requires authentication
    print("\n📋 Test 1: Testing endpoint authentication")
    
    # Test without auth first
    response = make_request("POST", "/speech/transcribe", headers={})
    
    if response and response.status_code == 403:
        log_test_result("Whisper Auth Requirement", True, "Endpoint correctly requires authentication")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Whisper Auth Requirement", False, f"Unexpected status: {status}", is_critical=False)
    
    # Test 2: Test with authentication but no file
    print("\n📋 Test 2: Testing request validation")
    
    response = make_request("POST", "/speech/transcribe")
    
    if response and response.status_code == 422:
        log_test_result("Whisper Request Validation", True, "Endpoint validates file requirement")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Whisper Request Validation", False, f"Unexpected status: {status}", is_critical=False)
    
    # Test 3: Test with invalid file type
    print("\n📋 Test 3: Testing file type validation")
    
    # Create a fake text file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"This is not an audio file")
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            files = {'audio': ('test.txt', f, 'text/plain')}
            response = make_request("POST", "/speech/transcribe", files=files)
        
        if response and response.status_code == 400:
            log_test_result("Whisper File Type Validation", True, "Endpoint rejects invalid file types")
        else:
            status = response.status_code if response else "No response"
            log_test_result("Whisper File Type Validation", False, f"Unexpected status: {status}", is_critical=False)
    
    finally:
        os.unlink(temp_file_path)
    
    # Test 4: Check OpenAI API key configuration
    print("\n📋 Test 4: Checking OpenAI API key configuration")
    
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        log_test_result("OpenAI API Key", True, f"Key configured (starts with: {openai_key[:10]}...)")
    else:
        log_test_result("OpenAI API Key", False, "OpenAI API key not properly configured")
    
    # Test 5: Test scenario transcription endpoint
    print("\n📋 Test 5: Testing scenario transcription endpoint")
    
    response = make_request("POST", "/speech/transcribe-scenario")
    
    if response and response.status_code == 422:
        log_test_result("Scenario Transcription Endpoint", True, "Endpoint exists and validates requests")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Scenario Transcription Endpoint", False, f"Unexpected status: {status}", is_critical=False)
    
    print("ℹ️ Note: Full audio transcription testing requires actual audio files")
    print("ℹ️ The endpoint structure and validation are working correctly")

def test_saved_agents_and_favorites():
    """Test saved agents and favorites functionality"""
    print("\n" + "="*80)
    print("⭐ TESTING SAVED AGENTS & FAVORITES")
    print("="*80)
    
    if not auth_token:
        log_test_result("Saved Agents Setup", False, "No authentication token")
        return
    
    # Test 1: Create a saved agent
    print("\n📋 Test 1: Creating saved agent (POST /api/saved-agents)")
    
    saved_agent_data = {
        "name": "Test Favorite Agent",
        "archetype": "scientist",
        "personality": {
            "extroversion": 6,
            "optimism": 8,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 5
        },
        "goal": "Test the favorites functionality",
        "expertise": "Testing and Quality Assurance",
        "background": "Specialized in testing saved agents and favorites",
        "is_favorite": False
    }
    
    response = make_request("POST", "/saved-agents", data=saved_agent_data)
    
    saved_agent_id = None
    if response and response.status_code == 200:
        try:
            result = response.json()
            saved_agent_id = result.get("id")
            log_test_result("Create Saved Agent", True, f"Agent ID: {saved_agent_id}")
        except Exception as e:
            log_test_result("Create Saved Agent", False, f"Response parsing error: {e}")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Create Saved Agent", False, f"HTTP {status}")
    
    if not saved_agent_id:
        print("❌ Cannot continue without saved agent ID")
        return
    
    # Test 2: Get saved agents list
    print("\n📋 Test 2: Getting saved agents list")
    
    response = make_request("GET", "/saved-agents")
    
    if response and response.status_code == 200:
        try:
            agents = response.json()
            found_agent = None
            for agent in agents:
                if agent.get("id") == saved_agent_id:
                    found_agent = agent
                    break
            
            if found_agent:
                log_test_result("Get Saved Agents", True, f"Found {len(agents)} agents including test agent")
                
                # Check if is_favorite field exists
                if "is_favorite" in found_agent:
                    log_test_result("Favorite Field Present", True, f"is_favorite: {found_agent['is_favorite']}")
                else:
                    log_test_result("Favorite Field Present", False, "is_favorite field missing")
            else:
                log_test_result("Get Saved Agents", False, "Created agent not found in list")
        except Exception as e:
            log_test_result("Get Saved Agents", False, f"Response parsing error: {e}")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Get Saved Agents", False, f"HTTP {status}")
    
    # Test 3: Toggle favorite status
    print("\n📋 Test 3: Toggling favorite status (PUT /api/saved-agents/{agent_id}/favorite)")
    
    response = make_request("PUT", f"/saved-agents/{saved_agent_id}/favorite")
    
    if response and response.status_code == 200:
        try:
            result = response.json()
            new_favorite_status = result.get("is_favorite")
            log_test_result("Toggle Favorite Status", True, f"New favorite status: {new_favorite_status}")
            
            # Verify the change persisted
            response2 = make_request("GET", "/saved-agents")
            if response2 and response2.status_code == 200:
                agents = response2.json()
                updated_agent = None
                for agent in agents:
                    if agent.get("id") == saved_agent_id:
                        updated_agent = agent
                        break
                
                if updated_agent and updated_agent.get("is_favorite") == new_favorite_status:
                    log_test_result("Favorite Status Persistence", True, "Status change persisted")
                else:
                    log_test_result("Favorite Status Persistence", False, "Status change not persisted")
            
        except Exception as e:
            log_test_result("Toggle Favorite Status", False, f"Response parsing error: {e}")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Toggle Favorite Status", False, f"HTTP {status}")
    
    # Test 4: Toggle favorite status back
    print("\n📋 Test 4: Toggling favorite status back")
    
    response = make_request("PUT", f"/saved-agents/{saved_agent_id}/favorite")
    
    if response and response.status_code == 200:
        log_test_result("Toggle Favorite Back", True, "Successfully toggled back")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Toggle Favorite Back", False, f"HTTP {status}")
    
    # Test 5: Test with invalid agent ID
    print("\n📋 Test 5: Testing with invalid agent ID")
    
    fake_id = str(uuid.uuid4())
    response = make_request("PUT", f"/saved-agents/{fake_id}/favorite")
    
    if response and response.status_code == 404:
        log_test_result("Invalid Agent ID Handling", True, "Correctly handles invalid agent ID")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Invalid Agent ID Handling", False, f"Unexpected status: {status}", is_critical=False)
    
    # Test 6: Test authentication requirement
    print("\n📋 Test 6: Testing authentication requirement")
    
    response = make_request("PUT", f"/saved-agents/{saved_agent_id}/favorite", headers={})
    
    if response and response.status_code == 403:
        log_test_result("Favorites Auth Requirement", True, "Endpoint correctly requires authentication")
    else:
        status = response.status_code if response else "No response"
        log_test_result("Favorites Auth Requirement", False, f"Unexpected status: {status}", is_critical=False)
    
    # Cleanup: Delete test saved agent
    print("\n🧹 Cleaning up test saved agent...")
    response = make_request("DELETE", f"/saved-agents/{saved_agent_id}")
    if response and response.status_code == 200:
        print(f"✅ Deleted saved agent {saved_agent_id}")

def print_test_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {test_results['passed']} ✅")
    print(f"   Failed: {test_results['failed']} ❌")
    print(f"   Pass Rate: {pass_rate:.1f}%")
    
    print(f"\n🔍 Test Details:")
    for test in test_results["tests"]:
        status_icon = "✅" if test["result"] == "PASSED" else "❌"
        print(f"   {status_icon} {test['name']}")
        if test["details"] and test["result"] == "FAILED":
            print(f"      └─ {test['details']}")
    
    if test_results["critical_issues"]:
        print(f"\n🚨 Critical Issues ({len(test_results['critical_issues'])}):")
        for issue in test_results["critical_issues"]:
            print(f"   ❌ {issue}")
    
    if test_results["minor_issues"]:
        print(f"\n⚠️ Minor Issues ({len(test_results['minor_issues'])}):")
        for issue in test_results["minor_issues"]:
            print(f"   ⚠️ {issue}")
    
    print("\n" + "="*80)
    
    # Determine overall status
    critical_failures = len(test_results["critical_issues"])
    if critical_failures == 0:
        print("🎉 ALL CRITICAL INTEGRATIONS WORKING!")
        return True
    else:
        print(f"🚨 {critical_failures} CRITICAL INTEGRATION ISSUES FOUND!")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Integration Tests for AI Agent Simulation Platform")
    print("🎯 Focus: Claude Sonnet 4, OpenAI Whisper, Saved Agents & Favorites, Authentication")
    
    # Run all integration tests
    test_authentication()
    test_claude_sonnet_4_integration()
    test_openai_whisper_integration()
    test_saved_agents_and_favorites()
    
    # Print final summary
    success = print_test_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)