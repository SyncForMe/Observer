#!/usr/bin/env python3
"""
Focused Authentication System Test Script
Focus: Test guest authentication flow and main application endpoints
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import jwt
from datetime import datetime
import uuid

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
print(f"Using API URL: {API_URL}")

# JWT secret for token validation
JWT_SECRET = os.environ.get('JWT_SECRET', 'test_secret')

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
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
            "result": result,
            "response_time": response_time
        }
        
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

def test_guest_authentication():
    """Test the guest authentication flow (POST /auth/test-login)"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("TESTING GUEST AUTHENTICATION FLOW")
    print("="*80)
    
    # Test 1: Guest login endpoint
    print("\nTest 1: Testing guest login endpoint (POST /auth/test-login)")
    
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        print("✅ Guest authentication successful")
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        
        print(f"User ID: {test_user_id}")
        print(f"User Email: {user_data.get('email', 'N/A')}")
        print(f"User Name: {user_data.get('name', 'N/A')}")
        print(f"JWT Token: {auth_token[:50]}..." if auth_token else "No token")
        
        # Verify token structure
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ JWT token is valid")
            print(f"Token payload: {json.dumps(decoded_token, indent=2)}")
            
            # Check for required fields
            if "sub" in decoded_token and "user_id" in decoded_token:
                print("✅ JWT token contains required fields (sub, user_id)")
            else:
                print("❌ JWT token is missing required fields")
                print(f"Available fields: {list(decoded_token.keys())}")
        except Exception as e:
            print(f"❌ JWT token validation failed: {e}")
        
        return True
    else:
        print("❌ Guest authentication failed")
        return False

def test_main_application_endpoints():
    """Test access to main application endpoints after authentication"""
    print("\n" + "="*80)
    print("TESTING MAIN APPLICATION ENDPOINTS")
    print("="*80)
    
    if not auth_token:
        print("❌ Cannot test endpoints without authentication token")
        return False
    
    # Test 2: Simulation state endpoint
    print("\nTest 2: Testing simulation state endpoint")
    
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_test:
        print("✅ Successfully accessed simulation state endpoint")
    else:
        print("❌ Failed to access simulation state endpoint")
    
    # Test 3: Agents endpoint
    print("\nTest 3: Testing agents endpoint")
    
    agents_test, agents_response = run_test(
        "Get User Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if agents_test:
        print("✅ Successfully accessed agents endpoint")
        agent_count = len(agents_response) if agents_response else 0
        print(f"Agent count: {agent_count}")
    else:
        print("❌ Failed to access agents endpoint")
    
    # Test 4: Conversations endpoint
    print("\nTest 4: Testing conversations endpoint")
    
    conversations_test, conversations_response = run_test(
        "Get User Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if conversations_test:
        print("✅ Successfully accessed conversations endpoint")
        conversation_count = len(conversations_response) if conversations_response else 0
        print(f"Conversation count: {conversation_count}")
    else:
        print("❌ Failed to access conversations endpoint")
    
    # Test 5: Documents endpoint
    print("\nTest 5: Testing documents endpoint")
    
    documents_test, documents_response = run_test(
        "Get User Documents",
        "/documents",
        method="GET",
        auth=True
    )
    
    if documents_test:
        print("✅ Successfully accessed documents endpoint")
        document_count = len(documents_response) if documents_response else 0
        print(f"Document count: {document_count}")
    else:
        print("❌ Failed to access documents endpoint")
    
    # Test 6: User profile endpoint
    print("\nTest 6: Testing user profile endpoint")
    
    profile_test, profile_response = run_test(
        "Get User Profile",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if profile_test:
        print("✅ Successfully accessed user profile endpoint")
        if profile_response.get("id") == test_user_id:
            print("✅ User ID matches authentication token")
        else:
            print("❌ User ID mismatch")
    else:
        print("❌ Failed to access user profile endpoint")
    
    # Test 7: Archetypes endpoint
    print("\nTest 7: Testing archetypes endpoint")
    
    archetypes_test, archetypes_response = run_test(
        "Get Agent Archetypes",
        "/archetypes",
        method="GET",
        auth=True
    )
    
    if archetypes_test:
        print("✅ Successfully accessed archetypes endpoint")
        if archetypes_response:
            archetype_count = len(archetypes_response)
            print(f"Available archetypes: {archetype_count}")
    else:
        print("❌ Failed to access archetypes endpoint")
    
    # Test 8: API usage endpoint
    print("\nTest 8: Testing API usage endpoint")
    
    usage_test, usage_response = run_test(
        "Get API Usage",
        "/usage",
        method="GET",
        auth=True
    )
    
    if usage_test:
        print("✅ Successfully accessed API usage endpoint")
    else:
        print("❌ Failed to access API usage endpoint")
    
    # Count successful endpoint tests
    endpoint_tests = [state_test, agents_test, conversations_test, documents_test, profile_test, archetypes_test, usage_test]
    successful_endpoints = sum(1 for test in endpoint_tests if test)
    
    print(f"\nEndpoint Access Summary: {successful_endpoints}/7 endpoints accessible")
    
    return successful_endpoints >= 6  # At least 6 out of 7 should work

def test_admin_credentials():
    """Test login with admin credentials as fallback"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("TESTING ADMIN CREDENTIALS LOGIN")
    print("="*80)
    
    # Test admin login
    admin_login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    admin_test, admin_response = run_test(
        "Admin Login",
        "/auth/login",
        method="POST",
        data=admin_login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if admin_test and admin_response:
        print("✅ Admin login successful")
        auth_token = admin_response.get("access_token")  # Update global token
        admin_user = admin_response.get("user", {})
        test_user_id = admin_user.get("id")  # Update global user ID
        
        print(f"Admin User ID: {admin_user.get('id')}")
        print(f"Admin Email: {admin_user.get('email')}")
        
        # Test admin token with protected endpoint
        admin_protected_test, admin_protected_response = run_test(
            "Admin Protected Access",
            "/agents",
            method="GET",
            auth=True  # Use global token now
        )
        
        if admin_protected_test:
            print("✅ Admin token works with protected endpoints")
            return True
        else:
            print("❌ Admin token failed with protected endpoints")
            return False
    else:
        print("❌ Admin login failed")
        return False

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"AUTHENTICATION TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(test_results['tests'])}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print("="*80)
    
    # Group tests by category
    categories = {
        "Authentication": [],
        "Endpoints": [],
        "Security": [],
        "Workflow": []
    }
    
    for test in test_results["tests"]:
        name = test["name"]
        if "Auth" in name or "Login" in name:
            categories["Authentication"].append(test)
        elif "No Auth" in name or "Authentication Requirements" in name:
            categories["Security"].append(test)
        elif "Agent" in name or "Workflow" in name:
            categories["Workflow"].append(test)
        else:
            categories["Endpoints"].append(test)
    
    for category, tests in categories.items():
        if tests:
            print(f"\n{category}:")
            for test in tests:
                result_symbol = "✅" if test["result"] == "PASSED" else "❌"
                print(f"  {result_symbol} {test['name']}")
    
    print("\n" + "="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    
    # Specific findings for the review request
    print("\n" + "="*80)
    print("SPECIFIC FINDINGS FOR REVIEW REQUEST:")
    print("="*80)
    
    guest_auth_working = any(test["name"] == "Guest Authentication" and test["result"] == "PASSED" for test in test_results["tests"])
    admin_auth_working = any(test["name"] == "Admin Login" and test["result"] == "PASSED" for test in test_results["tests"])
    endpoints_accessible = sum(1 for test in test_results["tests"] if "Get" in test["name"] and test["result"] == "PASSED")
    
    if guest_auth_working:
        print("✅ Guest authentication flow (POST /auth/test-login) is working correctly")
    elif admin_auth_working:
        print("✅ Admin authentication flow (POST /auth/login) is working correctly")
        print("⚠️ Guest authentication flow (POST /auth/test-login) is NOT working")
    else:
        print("❌ Both guest and admin authentication flows are NOT working")
    
    if endpoints_accessible >= 5:
        print(f"✅ Main application endpoints are accessible ({endpoints_accessible} endpoints tested successfully)")
    else:
        print(f"❌ Main application endpoints have issues ({endpoints_accessible} endpoints accessible)")
    
    if (guest_auth_working or admin_auth_working) and endpoints_accessible >= 5:
        print("✅ No authentication issues preventing main app from loading")
    else:
        print("❌ Authentication issues may be preventing main app from loading")
    
    print("="*80)

def main():
    """Main test execution"""
    print("Starting Authentication System Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API URL: {API_URL}")
    
    # Run tests in sequence
    guest_auth_success = test_guest_authentication()
    
    if guest_auth_success:
        endpoints_success = test_main_application_endpoints()
    else:
        print("\n⚠️ Guest authentication failed, trying admin credentials...")
        admin_success = test_admin_credentials()
        
        endpoints_success = test_main_application_endpoints() if auth_token else False
    
    # Print final summary
    print_summary()
    
    # Return overall success
    return test_results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)