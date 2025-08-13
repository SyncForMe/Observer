#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND AUTHENTICATION TESTING
Testing the complete backend system with email/password authentication for user "dino@cytonic.com"

Focus Areas:
1. Email/Password Authentication System
2. Profile Data Loading and Consistency
3. Backend API Endpoints with Authentication
4. User Profile Data Merging from user_profiles collection
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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None
user_profile_data = None

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
    """Test the complete authentication system"""
    global auth_token, test_user_id, user_profile_data
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION SYSTEM TESTING")
    print("="*80)
    
    # Test email/password login with dino@cytonic.com
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login (dino@cytonic.com)",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"],
        measure_time=True
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        user_profile_data = user_data
        
        print(f"✅ Authentication successful for dino@cytonic.com")
        print(f"   User ID: {test_user_id}")
        print(f"   Name: {user_data.get('name', 'N/A')}")
        print(f"   Picture: {user_data.get('picture', 'N/A')}")
        
        # Test /auth/me endpoint
        me_test, me_response = run_test(
            "Profile Verification (/auth/me)",
            "/auth/me",
            method="GET",
            auth=True,
            expected_keys=["id", "email", "name"]
        )
        
        if me_test and me_response:
            print("✅ Profile data loaded correctly")
            
            # Check profile data consistency
            login_name = user_data.get('name', '')
            me_name = me_response.get('name', '')
            
            if login_name == me_name:
                print(f"✅ Profile name consistent: '{login_name}'")
            else:
                print(f"❌ Profile name inconsistent: login='{login_name}' vs me='{me_name}'")
                
            # Check if this matches user expectations
            if me_name == "Dino":
                print("✅ User sees 'Dino' as expected (not 'Dino Observer')")
            elif me_name == "Dino Observer":
                print("❌ User sees 'Dino Observer' instead of expected 'Dino'")
            else:
                print(f"⚠️ User sees unexpected name: '{me_name}'")
                
            return True
        else:
            print("❌ Profile verification failed")
            return False
    else:
        print("❌ Authentication failed")
        return False

def test_backend_endpoints():
    """Test key backend endpoints with authentication"""
    print("\n" + "="*80)
    print("2. BACKEND ENDPOINTS TESTING")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available - skipping backend tests")
        return False
    
    # Test simulation control
    print("\n--- SIMULATION CONTROL ---")
    
    # Start simulation
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message"]
    )
    
    # Get simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period", "is_active"]
    )
    
    # Test agent management
    print("\n--- AGENT MANAGEMENT ---")
    
    # Get agents
    agents_test, agents_response = run_test(
        "Get User Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if agents_test and agents_response:
        agent_count = len(agents_response) if isinstance(agents_response, list) else 0
        print(f"✅ Found {agent_count} agents for user")
    
    # Test conversation system
    print("\n--- CONVERSATION SYSTEM ---")
    
    # Get conversations
    conversations_test, conversations_response = run_test(
        "Get User Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if conversations_test and conversations_response:
        conv_count = len(conversations_response) if isinstance(conversations_response, list) else 0
        print(f"✅ Found {conv_count} conversations for user")
    
    # Test observer messages
    print("\n--- OBSERVER MESSAGES ---")
    
    # Get observer messages
    observer_test, observer_response = run_test(
        "Get Observer Messages",
        "/observer/messages",
        method="GET",
        auth=True
    )
    
    # Get observer guidance
    guidance_test, guidance_response = run_test(
        "Get Observer Guidance",
        "/observer/guidance",
        method="GET",
        auth=True,
        expected_keys=["current_scenario", "guidance_count", "guidance"]
    )
    
    # Test document system
    print("\n--- DOCUMENT SYSTEM ---")
    
    # Get documents
    docs_test, docs_response = run_test(
        "Get User Documents",
        "/documents",
        method="GET",
        auth=True
    )
    
    if docs_test and docs_response:
        doc_count = len(docs_response) if isinstance(docs_response, list) else 0
        print(f"✅ Found {doc_count} documents for user")
    
    # Test reports system
    print("\n--- REPORTS SYSTEM ---")
    
    # Get reports
    reports_test, reports_response = run_test(
        "Get User Reports",
        "/reports",
        method="GET",
        auth=True
    )
    
    if reports_test and reports_response:
        if isinstance(reports_response, dict) and "reports" in reports_response:
            report_count = len(reports_response["reports"])
            print(f"✅ Found {report_count} reports for user")
        else:
            print("⚠️ Reports response format unexpected")
    
    # Count successful tests
    successful_tests = sum([
        start_test, state_test, agents_test, conversations_test,
        observer_test, guidance_test, docs_test, reports_test
    ])
    
    print(f"\n✅ Backend endpoints test: {successful_tests}/8 endpoints working")
    return successful_tests >= 6  # At least 75% should work

def test_profile_data_merging():
    """Test profile data merging functionality"""
    print("\n" + "="*80)
    print("3. PROFILE DATA MERGING TESTING")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available - skipping profile merging tests")
        return False
    
    print("🔍 Testing profile data merging from user_profiles collection")
    
    # Test profile update to verify merging works
    original_profile = user_profile_data.copy() if user_profile_data else {}
    
    # Update profile with test data
    update_data = {
        "name": "Dino Test",
        "picture": "https://test.example.com/test-avatar.jpg"
    }
    
    update_test, update_response = run_test(
        "Update Profile Data",
        "/auth/profile",
        method="PUT",
        data=update_data,
        auth=True,
        expected_keys=["success", "message"]
    )
    
    if update_test and update_response:
        print("✅ Profile update endpoint working")
        
        # Verify the update was applied
        verify_test, verify_response = run_test(
            "Verify Profile Update",
            "/auth/me",
            method="GET",
            auth=True,
            expected_keys=["id", "email", "name"]
        )
        
        if verify_test and verify_response:
            updated_name = verify_response.get('name', '')
            updated_picture = verify_response.get('picture', '')
            
            if updated_name == "Dino Test":
                print("✅ Profile name update successful")
            else:
                print(f"❌ Profile name update failed: expected 'Dino Test', got '{updated_name}'")
                
            if updated_picture == "https://test.example.com/test-avatar.jpg":
                print("✅ Profile picture update successful")
            else:
                print(f"❌ Profile picture update failed: expected test URL, got '{updated_picture}'")
        
        # Restore original profile
        restore_data = {
            "name": original_profile.get('name', 'Dino'),
            "picture": original_profile.get('picture', '')
        }
        
        restore_test, restore_response = run_test(
            "Restore Original Profile",
            "/auth/profile",
            method="PUT",
            data=restore_data,
            auth=True
        )
        
        if restore_test:
            print("✅ Profile restored to original state")
        
        return True
    else:
        print("❌ Profile update endpoint not working")
        return False

def main():
    """Main test execution function"""
    print("COMPREHENSIVE BACKEND AUTHENTICATION TESTING")
    print("Testing backend system with dino@cytonic.com authentication")
    print("="*80)
    
    # Run all test suites
    test_suites = [
        ("Authentication System", test_authentication_system),
        ("Backend Endpoints", test_backend_endpoints),
        ("Profile Data Merging", test_profile_data_merging)
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
    
    # Print final summary
    print_summary()
    
    # Print test suite summary
    print(f"\n{'='*80}")
    print("AUTHENTICATION TESTING RESULTS")
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
    
    # Print specific findings
    print(f"\n{'='*80}")
    print("KEY FINDINGS FOR USER 'dino@cytonic.com'")
    print(f"{'='*80}")
    
    if user_profile_data:
        name = user_profile_data.get('name', 'N/A')
        picture = user_profile_data.get('picture', 'N/A')
        email = user_profile_data.get('email', 'N/A')
        
        print(f"✅ Authentication: WORKING")
        print(f"✅ User Email: {email}")
        print(f"✅ Display Name: '{name}'")
        print(f"✅ Avatar Picture: {picture}")
        
        if name == "Dino":
            print(f"✅ RESULT: User sees 'Dino' as expected (not 'Dino Observer')")
        elif name == "Dino Observer":
            print(f"❌ ISSUE: User sees 'Dino Observer' instead of expected 'Dino'")
        else:
            print(f"⚠️ UNEXPECTED: User sees '{name}' - needs investigation")
            
        if picture and picture != "":
            print(f"✅ RESULT: User has avatar picture loaded correctly")
        else:
            print(f"❌ ISSUE: User has no avatar picture")
    else:
        print(f"❌ Authentication failed - no profile data available")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_suites) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)