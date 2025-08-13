#!/usr/bin/env python3
"""
AUTHENTICATION SYSTEM TESTING AFTER TEST LOGIN REMOVAL
Testing authentication system to ensure it works properly after removing test login functionality.

Focus Areas:
1. Test Login Removal Verification (test-login endpoint should return 404)
2. Google OAuth Endpoints (google and callback endpoints should work)
3. JWT Token Validation (me endpoint should work correctly)
4. Protected Endpoints (should require proper authentication)
5. Core Functionality (agent creation, conversation generation, reports)
6. Unauthenticated Request Handling (graceful error handling)
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

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []
created_document_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def test_authentication_system():
    """Test authentication system after test login removal"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION SYSTEM TESTING AFTER TEST LOGIN REMOVAL")
    print("="*80)
    
    # Test 1: Verify test-login endpoint has been removed (should return 404)
    print("\n--- Test 1: Test Login Endpoint Removal ---")
    test_login_removed, test_login_response = run_test(
        "Test Login Endpoint Removal",
        "/auth/test-login",
        method="POST",
        expected_status=404,  # Should return 404 Not Found
        data={}
    )
    
    if test_login_removed:
        print("✅ Test login endpoint successfully removed (returns 404)")
    else:
        print("❌ Test login endpoint still exists - this is a problem!")
        return False
    
    # Test 2: Verify Google OAuth endpoints exist and are accessible
    print("\n--- Test 2: Google OAuth Endpoints ---")
    
    # Test Google OAuth initiation endpoint
    google_oauth_test, google_oauth_response = run_test(
        "Google OAuth Initiation",
        "/auth/google",
        method="POST",
        expected_status=422,  # Should return 422 for missing credential
        data={}
    )
    
    if google_oauth_test:
        print("✅ Google OAuth endpoint exists and is accessible")
    else:
        print("❌ Google OAuth endpoint not working properly")
        return False
    
    # Test Google OAuth callback endpoint
    callback_test, callback_response = run_test(
        "Google OAuth Callback",
        "/auth/google/callback",
        method="POST",
        expected_status=422,  # Should return 422 for missing credential
        data={}
    )
    
    if callback_test:
        print("✅ Google OAuth callback endpoint exists and is accessible")
    else:
        print("❌ Google OAuth callback endpoint not working properly")
        return False
    
    # Test 3: Create a test JWT token for further testing (simulating successful Google OAuth)
    print("\n--- Test 3: JWT Token Creation for Testing ---")
    
    # Create a test JWT token manually (simulating what Google OAuth would do)
    import jwt
    from datetime import datetime, timedelta
    
    test_payload = {
        "user_id": "test-user-123",
        "sub": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    try:
        auth_token = jwt.encode(test_payload, JWT_SECRET, algorithm="HS256")
        test_user_id = "test-user-123"
        print("✅ Test JWT token created successfully for testing")
    except Exception as e:
        print(f"❌ Failed to create test JWT token: {e}")
        return False
    
    # Test 4: Verify JWT token validation with /auth/me endpoint
    print("\n--- Test 4: JWT Token Validation ---")
    
    me_test, me_response = run_test(
        "JWT Token Validation (/auth/me)",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if me_test and me_response:
        print("✅ JWT token validation successful")
        if me_response.get("id") == test_user_id:
            print("✅ User ID matches between token and profile")
        else:
            print("❌ User ID mismatch")
            return False
    else:
        print("❌ JWT token validation failed")
        return False
    
    # Test 5: Test unauthenticated request handling
    print("\n--- Test 5: Unauthenticated Request Handling ---")
    
    unauth_test, unauth_response = run_test(
        "Unauthenticated Request",
        "/auth/me",
        method="GET",
        auth=False,
        expected_status=403  # Should return 403 Forbidden
    )
    
    if unauth_test:
        print("✅ Unauthenticated requests properly rejected")
    else:
        print("❌ Unauthenticated request handling not working properly")
        return False
    
    print("✅ Authentication system working correctly after test login removal")
    return True

def test_protected_endpoints():
    """Test that protected endpoints require proper authentication"""
    print("\n" + "="*80)
    print("2. PROTECTED ENDPOINTS TESTING")
    print("="*80)
    
    # Test protected endpoints that should require authentication
    protected_endpoints = [
        ("/simulation/state", "GET"),
        ("/agents", "GET"),
        ("/conversations", "GET"),
        ("/observer/messages", "GET"),
        ("/documents", "GET"),
        ("/usage", "GET")
    ]
    
    all_protected = True
    
    for endpoint, method in protected_endpoints:
        print(f"\n--- Testing Protected Endpoint: {endpoint} ---")
        
        # Test without authentication (should fail)
        unauth_test, unauth_response = run_test(
            f"Unauthenticated {endpoint}",
            endpoint,
            method=method,
            auth=False,
            expected_status=403  # Should return 403 Forbidden
        )
        
        if unauth_test:
            print(f"✅ {endpoint} properly requires authentication")
        else:
            print(f"❌ {endpoint} does not require authentication - security issue!")
            all_protected = False
        
        # Test with authentication (should work)
        auth_test, auth_response = run_test(
            f"Authenticated {endpoint}",
            endpoint,
            method=method,
            auth=True,
            expected_status=200  # Should return 200 OK
        )
        
        if auth_test:
            print(f"✅ {endpoint} works with proper authentication")
        else:
            print(f"❌ {endpoint} fails even with authentication")
            all_protected = False
    
    if all_protected:
        print("✅ All protected endpoints properly require authentication")
        return True
    else:
        print("❌ Some protected endpoints have authentication issues")
        return False

def test_core_functionality():
    """Test core functionality still works with authentication"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("3. CORE FUNCTIONALITY TESTING")
    print("="*80)
    
    # Test 1: Agent Creation
    print("\n--- Test 1: Agent Creation ---")
    agent_data = {
        "name": "Dr. Sarah Quantum",
        "archetype": "scientist",
        "goal": "Advance quantum computing research",
        "expertise": "Quantum physics and cryptography",
        "background": "PhD in Quantum Physics from MIT",
        "personality": {
            "extroversion": 6,
            "optimism": 8,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 7
        }
    }
    
    create_agent_test, create_agent_response = run_test(
        "Create Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True,
        expected_keys=["message", "agent_id"]
    )
    
    if create_agent_test and create_agent_response:
        agent_id = create_agent_response.get("agent_id")
        if agent_id:
            created_agent_ids.append(agent_id)
            print(f"✅ Created agent with ID: {agent_id}")
        else:
            print("❌ No agent ID returned")
            return False
    else:
        print("❌ Agent creation failed")
        return False
    
    # Test 2: Simulation State
    print("\n--- Test 2: Simulation State ---")
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period", "is_active"]
    )
    
    if not state_test:
        print("❌ Simulation state retrieval failed")
        return False
    
    # Test 3: Conversation Generation (if we have agents)
    print("\n--- Test 3: Conversation Generation ---")
    if len(created_agent_ids) > 0:
        conversation_test, conversation_response = run_test(
            "Generate Conversation",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True
        )
        
        if conversation_test:
            print("✅ Conversation generation working")
        else:
            print("❌ Conversation generation failed")
            return False
    else:
        print("⚠️ Skipping conversation generation - no agents created")
    
    print("✅ Core functionality working with authentication")
    return True

def test_reports_functionality():
    """Test reports functionality with authentication"""
    print("\n" + "="*80)
    print("4. REPORTS FUNCTIONALITY TESTING")
    print("="*80)
    
    # Test 1: Daily Report Generation
    print("\n--- Test 1: Daily Report Generation ---")
    daily_report_test, daily_report_response = run_test(
        "Generate Daily Report",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True
    )
    
    if daily_report_test and daily_report_response:
        print("✅ Daily report generation working")
        
        # Test 2: Reports Retrieval
        print("\n--- Test 2: Reports Retrieval ---")
        reports_test, reports_response = run_test(
            "Get Reports",
            "/reports",
            method="GET",
            auth=True,
            expected_keys=["success", "reports", "count"]
        )
        
        if reports_test:
            print("✅ Reports retrieval working")
        else:
            print("❌ Reports retrieval failed")
            return False
    else:
        print("❌ Daily report generation failed")
        return False
    
    print("✅ Reports functionality working with authentication")
    return True

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution function"""
    print("AUTHENTICATION SYSTEM TESTING AFTER TEST LOGIN REMOVAL")
    print("Testing authentication system to ensure it works properly after removing test login functionality")
    print("="*80)
    
    # Run all test suites
    test_suites = [
        ("Authentication System", test_authentication_system),
        ("Protected Endpoints", test_protected_endpoints),
        ("Core Functionality", test_core_functionality),
        ("Reports Functionality", test_reports_functionality)
    ]
    
    failed_suites = []
    
    for suite_name, test_function in test_suites:
        try:
            print(f"\n{'='*80}")
            print(f"RUNNING TEST SUITE: {suite_name}")
            print(f"{'='*80}")
            
            success = test_function()
            if success:
                print(f"✅ {suite_name} test suite PASSED")
            else:
                print(f"❌ {suite_name} test suite FAILED")
                failed_suites.append(suite_name)
        except Exception as e:
            print(f"❌ {suite_name} test suite ERROR: {e}")
            failed_suites.append(suite_name)
    
    # Cleanup test data
    cleanup_test_data()
    
    # Print final summary
    print_summary()
    
    # Print test suite summary
    print(f"\n{'='*80}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*80}")
    
    total_suites = len(test_suites)
    passed_suites = total_suites - len(failed_suites)
    
    print(f"Total Test Suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {len(failed_suites)}")
    
    if failed_suites:
        print(f"\nFailed Test Suites:")
        for suite in failed_suites:
            print(f"  ❌ {suite}")
    else:
        print(f"\n✅ ALL TEST SUITES PASSED!")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_suites) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)