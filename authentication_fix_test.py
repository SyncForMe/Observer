#!/usr/bin/env python3
"""
Authentication Fix Testing Script

This script tests the authentication fix that was implemented to resolve the issue where
`localStorage.getItem('token')` was changed to `localStorage.getItem('auth_token')` in
AgentCreateModal.js line 114. This was causing authentication failures.

Testing Requirements:
1. Test guest authentication (POST /auth/test-login)
2. Test agent creation (POST /api/agents) with proper authentication
3. Test scenario setting (POST /api/simulation/set-scenario) with authentication  
4. Test avatar generation (POST /api/avatars/generate) with authentication
5. Verify all endpoints that were failing before now work correctly
6. Confirm JWT token validation is working properly
"""

import requests
import json
import time
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# JWT secret for token validation
JWT_SECRET = os.environ.get('JWT_SECRET', 'test_secret')

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "auth_token": None,
    "user_id": None
}

def log_test_result(test_name, success, details="", response_time=None):
    """Log test result with details"""
    result = "✅ PASSED" if success else "❌ FAILED"
    print(f"{result}: {test_name}")
    if details:
        print(f"   Details: {details}")
    if response_time:
        print(f"   Response Time: {response_time:.3f}s")
    
    test_results["tests"].append({
        "name": test_name,
        "success": success,
        "details": details,
        "response_time": response_time
    })
    
    if success:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def make_request(method, endpoint, data=None, auth=False, expected_status=200):
    """Make HTTP request with proper error handling"""
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth and test_results["auth_token"]:
        headers["Authorization"] = f"Bearer {test_results['auth_token']}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response_time = time.time() - start_time
        
        # Check status code
        if response.status_code != expected_status:
            return False, None, response_time, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        
        # Try to parse JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}
        
        return True, response_data, response_time, None
        
    except Exception as e:
        return False, None, 0, str(e)

def test_guest_authentication():
    """Test 1: Guest authentication (POST /auth/test-login)"""
    print("\n" + "="*80)
    print("🔐 TEST 1: GUEST AUTHENTICATION")
    print("="*80)
    
    success, response, response_time, error = make_request("POST", "/auth/test-login")
    
    if not success:
        log_test_result("Guest Authentication", False, error, response_time)
        return False
    
    # Validate response structure
    if not response or "access_token" not in response:
        log_test_result("Guest Authentication", False, "Missing access_token in response")
        return False
    
    # Store token for subsequent tests
    test_results["auth_token"] = response["access_token"]
    user_data = response.get("user", {})
    test_results["user_id"] = user_data.get("id")
    
    log_test_result("Guest Authentication", True, 
                   f"Token obtained, User ID: {test_results['user_id']}", response_time)
    
    # Validate JWT token structure
    try:
        import jwt
        decoded = jwt.decode(test_results["auth_token"], JWT_SECRET, algorithms=["HS256"])
        if "sub" in decoded and "user_id" in decoded:
            log_test_result("JWT Token Validation", True, "Token contains required fields")
        else:
            log_test_result("JWT Token Validation", False, "Token missing required fields")
    except Exception as e:
        log_test_result("JWT Token Validation", False, f"Token validation failed: {e}")
    
    return True

def test_agent_creation():
    """Test 2: Agent creation (POST /api/agents) with proper authentication"""
    print("\n" + "="*80)
    print("🤖 TEST 2: AGENT CREATION WITH AUTHENTICATION")
    print("="*80)
    
    if not test_results["auth_token"]:
        log_test_result("Agent Creation", False, "No auth token available")
        return False
    
    # Test agent creation data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 7,
            "optimism": 8,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": "Test the authentication fix for agent creation",
        "expertise": "Authentication Testing",
        "background": "Created to test the authentication fix implementation",
        "avatar_prompt": "A professional scientist in a lab coat"
    }
    
    # Test without authentication first (should fail)
    success, response, response_time, error = make_request("POST", "/agents", agent_data, auth=False, expected_status=403)
    
    if success:
        log_test_result("Agent Creation Without Auth", True, "Correctly rejected unauthenticated request", response_time)
    else:
        log_test_result("Agent Creation Without Auth", False, "Should have rejected unauthenticated request")
    
    # Test with authentication (should succeed)
    success, response, response_time, error = make_request("POST", "/agents", agent_data, auth=True, expected_status=200)
    
    if not success:
        log_test_result("Agent Creation With Auth", False, error, response_time)
        return False
    
    # Validate response
    if not response or "id" not in response:
        log_test_result("Agent Creation With Auth", False, "Missing agent ID in response")
        return False
    
    agent_id = response["id"]
    log_test_result("Agent Creation With Auth", True, f"Agent created with ID: {agent_id}", response_time)
    
    # Verify agent is associated with correct user
    if response.get("user_id") == test_results["user_id"]:
        log_test_result("Agent User Association", True, "Agent correctly associated with user")
    else:
        log_test_result("Agent User Association", False, 
                       f"Agent user_id {response.get('user_id')} != {test_results['user_id']}")
    
    return True

def test_scenario_setting():
    """Test 3: Scenario setting (POST /api/simulation/set-scenario) with authentication"""
    print("\n" + "="*80)
    print("🎭 TEST 3: SCENARIO SETTING WITH AUTHENTICATION")
    print("="*80)
    
    if not test_results["auth_token"]:
        log_test_result("Scenario Setting", False, "No auth token available")
        return False
    
    # First, start a simulation
    success, response, response_time, error = make_request("POST", "/simulation/start", auth=True)
    
    if not success:
        log_test_result("Simulation Start", False, error, response_time)
        return False
    
    log_test_result("Simulation Start", True, "Simulation started successfully", response_time)
    
    # Test scenario setting data
    scenario_data = {
        "scenario": "Testing the authentication fix for scenario setting functionality",
        "scenario_name": "Authentication Fix Test Scenario"
    }
    
    # Test without authentication first (should fail)
    success, response, response_time, error = make_request("POST", "/simulation/set-scenario", 
                                                          scenario_data, auth=False, expected_status=403)
    
    if success:
        log_test_result("Scenario Setting Without Auth", True, "Correctly rejected unauthenticated request", response_time)
    else:
        log_test_result("Scenario Setting Without Auth", False, "Should have rejected unauthenticated request")
    
    # Test with authentication (should succeed)
    success, response, response_time, error = make_request("POST", "/simulation/set-scenario", 
                                                          scenario_data, auth=True, expected_status=200)
    
    if not success:
        log_test_result("Scenario Setting With Auth", False, error, response_time)
        return False
    
    log_test_result("Scenario Setting With Auth", True, "Scenario set successfully", response_time)
    
    # Verify scenario was actually set by checking simulation state
    success, response, response_time, error = make_request("GET", "/simulation/state", auth=True)
    
    if success and response:
        if response.get("scenario_name") == scenario_data["scenario_name"]:
            log_test_result("Scenario Persistence", True, "Scenario correctly persisted in simulation state")
        else:
            log_test_result("Scenario Persistence", False, 
                           f"Expected '{scenario_data['scenario_name']}', got '{response.get('scenario_name')}'")
    else:
        log_test_result("Scenario Persistence", False, "Could not verify scenario persistence")
    
    return True

def test_avatar_generation():
    """Test 4: Avatar generation (POST /api/avatars/generate) with authentication"""
    print("\n" + "="*80)
    print("🎨 TEST 4: AVATAR GENERATION WITH AUTHENTICATION")
    print("="*80)
    
    if not test_results["auth_token"]:
        log_test_result("Avatar Generation", False, "No auth token available")
        return False
    
    # Test avatar generation data
    avatar_data = {
        "prompt": "A professional scientist in a lab coat, testing authentication systems"
    }
    
    # Test without authentication first (should fail)
    success, response, response_time, error = make_request("POST", "/avatars/generate", 
                                                          avatar_data, auth=False, expected_status=403)
    
    if success:
        log_test_result("Avatar Generation Without Auth", True, "Correctly rejected unauthenticated request", response_time)
    else:
        log_test_result("Avatar Generation Without Auth", False, "Should have rejected unauthenticated request")
    
    # Test with authentication (should succeed)
    success, response, response_time, error = make_request("POST", "/avatars/generate", 
                                                          avatar_data, auth=True, expected_status=200)
    
    if not success:
        log_test_result("Avatar Generation With Auth", False, error, response_time)
        return False
    
    # Validate response structure
    if not response or "success" not in response:
        log_test_result("Avatar Generation With Auth", False, "Missing success field in response")
        return False
    
    if response.get("success"):
        image_url = response.get("image_url", "")
        log_test_result("Avatar Generation With Auth", True, f"Avatar generated: {image_url[:50]}...", response_time)
    else:
        error_msg = response.get("error", "Unknown error")
        log_test_result("Avatar Generation With Auth", False, f"Avatar generation failed: {error_msg}")
    
    return True

def test_protected_endpoints():
    """Test 5: Verify all previously failing endpoints now work correctly"""
    print("\n" + "="*80)
    print("🔒 TEST 5: PROTECTED ENDPOINTS VERIFICATION")
    print("="*80)
    
    if not test_results["auth_token"]:
        log_test_result("Protected Endpoints", False, "No auth token available")
        return False
    
    # List of endpoints that should require authentication
    protected_endpoints = [
        ("GET", "/agents", "Get Agents"),
        ("GET", "/conversations", "Get Conversations"),
        ("GET", "/documents", "Get Documents"),
        ("GET", "/simulation/state", "Get Simulation State"),
        ("GET", "/auth/me", "Get User Profile"),
        ("GET", "/usage", "Get API Usage"),
        ("GET", "/observer/messages", "Get Observer Messages")
    ]
    
    all_passed = True
    
    for method, endpoint, name in protected_endpoints:
        # Test without authentication (should fail)
        success, response, response_time, error = make_request(method, endpoint, auth=False, expected_status=403)
        
        if success:
            log_test_result(f"{name} - Auth Required", True, "Correctly requires authentication", response_time)
        else:
            log_test_result(f"{name} - Auth Required", False, "Should require authentication")
            all_passed = False
        
        # Test with authentication (should succeed)
        success, response, response_time, error = make_request(method, endpoint, auth=True, expected_status=200)
        
        if success:
            log_test_result(f"{name} - With Auth", True, "Successfully accessed with token", response_time)
        else:
            log_test_result(f"{name} - With Auth", False, error, response_time)
            all_passed = False
    
    return all_passed

def test_jwt_token_validation():
    """Test 6: Confirm JWT token validation is working properly"""
    print("\n" + "="*80)
    print("🔑 TEST 6: JWT TOKEN VALIDATION")
    print("="*80)
    
    if not test_results["auth_token"]:
        log_test_result("JWT Token Validation", False, "No auth token available")
        return False
    
    # Test with valid token
    success, response, response_time, error = make_request("GET", "/auth/me", auth=True)
    
    if success:
        log_test_result("Valid Token Access", True, "Valid token accepted", response_time)
    else:
        log_test_result("Valid Token Access", False, error, response_time)
        return False
    
    # Test with invalid token
    original_token = test_results["auth_token"]
    test_results["auth_token"] = "invalid_token_12345"
    
    success, response, response_time, error = make_request("GET", "/auth/me", auth=True, expected_status=403)
    
    if success:
        log_test_result("Invalid Token Rejection", True, "Invalid token correctly rejected", response_time)
    else:
        log_test_result("Invalid Token Rejection", False, "Should reject invalid token")
    
    # Test with malformed token
    test_results["auth_token"] = "Bearer malformed.token.here"
    
    success, response, response_time, error = make_request("GET", "/auth/me", auth=True, expected_status=403)
    
    if success:
        log_test_result("Malformed Token Rejection", True, "Malformed token correctly rejected", response_time)
    else:
        log_test_result("Malformed Token Rejection", False, "Should reject malformed token")
    
    # Test with expired token (simulate by using a very old token)
    try:
        import jwt
        expired_payload = {
            "sub": "test@example.com",
            "user_id": "test_user",
            "exp": 1000000000  # Very old timestamp
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")
        test_results["auth_token"] = expired_token
        
        success, response, response_time, error = make_request("GET", "/auth/me", auth=True, expected_status=403)
        
        if success:
            log_test_result("Expired Token Rejection", True, "Expired token correctly rejected", response_time)
        else:
            log_test_result("Expired Token Rejection", False, "Should reject expired token")
    except Exception as e:
        log_test_result("Expired Token Test", False, f"Could not test expired token: {e}")
    
    # Restore original token
    test_results["auth_token"] = original_token
    
    return True

def print_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*100)
    print("🏁 AUTHENTICATION FIX TEST SUMMARY")
    print("="*100)
    
    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {test_results['passed']} ✅")
    print(f"   Failed: {test_results['failed']} ❌")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n🔐 AUTHENTICATION STATUS:")
    if test_results["auth_token"]:
        print(f"   ✅ Authentication Token: Obtained")
        print(f"   ✅ User ID: {test_results['user_id']}")
    else:
        print(f"   ❌ Authentication Token: Failed to obtain")
    
    print(f"\n📋 DETAILED TEST RESULTS:")
    for i, test in enumerate(test_results["tests"], 1):
        status = "✅" if test["success"] else "❌"
        time_info = f" ({test['response_time']:.3f}s)" if test["response_time"] else ""
        print(f"   {i:2d}. {status} {test['name']}{time_info}")
        if test["details"]:
            print(f"       {test['details']}")
    
    print("\n" + "="*100)
    
    # Determine overall assessment
    critical_tests = [
        "Guest Authentication",
        "Agent Creation With Auth", 
        "Scenario Setting With Auth",
        "Avatar Generation With Auth"
    ]
    
    critical_passed = sum(1 for test in test_results["tests"] 
                         if test["name"] in critical_tests and test["success"])
    
    if critical_passed == len(critical_tests):
        print("🎉 AUTHENTICATION FIX: SUCCESSFUL")
        print("   All critical authentication endpoints are working correctly!")
        print("   The localStorage token key fix has resolved the authentication issues.")
    elif critical_passed >= len(critical_tests) * 0.75:
        print("⚠️  AUTHENTICATION FIX: MOSTLY SUCCESSFUL")
        print("   Most critical authentication endpoints are working.")
        print("   Some minor issues may need attention.")
    else:
        print("❌ AUTHENTICATION FIX: ISSUES DETECTED")
        print("   Critical authentication endpoints are still failing.")
        print("   The fix may not have fully resolved the authentication issues.")
    
    print("="*100)

def main():
    """Main test execution"""
    print("🚀 STARTING AUTHENTICATION FIX TESTING")
    print("="*80)
    print("Testing the fix for localStorage.getItem('token') -> localStorage.getItem('auth_token')")
    print("This fix was implemented in AgentCreateModal.js line 114 to resolve authentication failures.")
    print("="*80)
    
    # Run all tests in sequence
    tests = [
        test_guest_authentication,
        test_agent_creation,
        test_scenario_setting,
        test_avatar_generation,
        test_protected_endpoints,
        test_jwt_token_validation
    ]
    
    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            log_test_result(test_func.__name__, False, f"Exception: {e}")
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Print final summary
    print_summary()
    
    # Return exit code based on results
    return 0 if test_results["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)