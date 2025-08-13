#!/usr/bin/env python3
"""
EMAIL/PASSWORD AUTHENTICATION SYSTEM TESTING
Testing the email/password authentication system for user "dino@cytonic" to verify profile data loading.

Focus Areas:
1. Email/Password Login with credentials: email="dino@cytonic.com", password="Observerinho8"
2. Profile Data Verification from user_profiles collection
3. /auth/me Endpoint Testing for consistency
4. Profile Data Debugging (name and picture data)
5. User Profile Data Merging Verification
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

def test_email_password_login():
    """Test email/password login with specific credentials"""
    global auth_token, test_user_id, user_profile_data
    
    print("\n" + "="*80)
    print("1. EMAIL/PASSWORD LOGIN TESTING")
    print("="*80)
    
    print("🔍 Testing login with credentials:")
    print("   Email: dino@cytonic.com")
    print("   Password: Observerinho8")
    
    # Test email/password login
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login",
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
        
        print(f"✅ Email/password login successful")
        print(f"   User ID: {test_user_id}")
        print(f"   User Name: {user_data.get('name', 'N/A')}")
        print(f"   User Email: {user_data.get('email', 'N/A')}")
        print(f"   User Picture: {user_data.get('picture', 'N/A')}")
        
        # Verify JWT token structure
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ JWT token is valid and contains: {list(decoded_token.keys())}")
            if "user_id" in decoded_token and "sub" in decoded_token:
                print("✅ JWT token contains required fields (user_id, sub)")
            else:
                print("❌ JWT token is missing required fields")
        except Exception as e:
            print(f"❌ JWT token validation failed: {e}")
            
        # Analyze profile data from login response
        print("\n--- LOGIN RESPONSE PROFILE DATA ANALYSIS ---")
        print(f"Name from login: '{user_data.get('name', 'N/A')}'")
        print(f"Picture from login: '{user_data.get('picture', 'N/A')}'")
        print(f"Email from login: '{user_data.get('email', 'N/A')}'")
        print(f"Auth type: '{user_data.get('auth_type', 'N/A')}'")
        
        return True
    else:
        print("❌ Email/password login failed")
        print("🔍 This could indicate:")
        print("   1. User 'dino@cytonic.com' doesn't exist in the database")
        print("   2. Password 'Observerinho8' is incorrect")
        print("   3. Email/password authentication endpoint is not working")
        print("   4. Database connection issues")
        return False

def test_auth_me_endpoint():
    """Test /auth/me endpoint for profile consistency"""
    print("\n" + "="*80)
    print("2. /AUTH/ME ENDPOINT TESTING")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available - skipping /auth/me test")
        return False
    
    # Test JWT token validation with protected endpoint
    me_test, me_response = run_test(
        "JWT Token Validation (/auth/me)",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"],
        measure_time=True
    )
    
    if me_test and me_response:
        print("✅ /auth/me endpoint working correctly")
        
        # Compare login response vs /auth/me response
        print("\n--- PROFILE DATA CONSISTENCY CHECK ---")
        
        login_name = user_profile_data.get('name', 'N/A') if user_profile_data else 'N/A'
        login_picture = user_profile_data.get('picture', 'N/A') if user_profile_data else 'N/A'
        login_email = user_profile_data.get('email', 'N/A') if user_profile_data else 'N/A'
        
        me_name = me_response.get('name', 'N/A')
        me_picture = me_response.get('picture', 'N/A')
        me_email = me_response.get('email', 'N/A')
        
        print(f"Login Response - Name: '{login_name}', Picture: '{login_picture}', Email: '{login_email}'")
        print(f"/auth/me Response - Name: '{me_name}', Picture: '{me_picture}', Email: '{me_email}'")
        
        # Check for consistency
        consistency_issues = []
        
        if login_name != me_name:
            consistency_issues.append(f"Name mismatch: login='{login_name}' vs me='{me_name}'")
        
        if login_picture != me_picture:
            consistency_issues.append(f"Picture mismatch: login='{login_picture}' vs me='{me_picture}'")
            
        if login_email != me_email:
            consistency_issues.append(f"Email mismatch: login='{login_email}' vs me='{me_email}'")
        
        if consistency_issues:
            print("❌ CONSISTENCY ISSUES FOUND:")
            for issue in consistency_issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Profile data is consistent between login and /auth/me")
            
        # Check if user ID matches
        if me_response.get("id") == test_user_id:
            print("✅ User ID matches between login and /auth/me")
        else:
            print("❌ User ID mismatch between login and /auth/me")
            return False
            
        return True
    else:
        print("❌ /auth/me endpoint failed")
        return False

def test_profile_data_investigation():
    """Investigate profile data sources and merging"""
    print("\n" + "="*80)
    print("3. PROFILE DATA INVESTIGATION")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available - skipping profile investigation")
        return False
    
    print("🔍 Investigating profile data sources for user 'dino@cytonic.com'")
    
    # Check if there are any profile-related endpoints
    profile_endpoints_to_test = [
        "/user/profile",
        "/profile",
        "/users/profile", 
        "/auth/profile",
        "/user/me",
        "/users/me"
    ]
    
    print("\n--- TESTING POTENTIAL PROFILE ENDPOINTS ---")
    for endpoint in profile_endpoints_to_test:
        test_name = f"Profile Endpoint Test ({endpoint})"
        profile_test, profile_response = run_test(
            test_name,
            endpoint,
            method="GET",
            auth=True,
            expected_status=200  # We'll accept any status for investigation
        )
        
        if profile_test and profile_response:
            print(f"✅ Found working profile endpoint: {endpoint}")
            print(f"   Response keys: {list(profile_response.keys())}")
            
            # Check for profile-specific data
            if 'name' in profile_response or 'picture' in profile_response:
                print(f"   Profile data found:")
                print(f"     Name: '{profile_response.get('name', 'N/A')}'")
                print(f"     Picture: '{profile_response.get('picture', 'N/A')}'")
        else:
            print(f"❌ Endpoint {endpoint} not available or failed")
    
    # Test user registration endpoint to understand user structure
    print("\n--- TESTING USER REGISTRATION ENDPOINT (for structure understanding) ---")
    
    # Try to understand the user registration structure
    register_test_data = {
        "email": "test_structure@example.com",
        "password": "testpassword123",
        "name": "Test Structure User"
    }
    
    register_test, register_response = run_test(
        "User Registration Structure Test",
        "/auth/register",
        method="POST",
        data=register_test_data,
        expected_status=200  # We'll accept any status for investigation
    )
    
    if register_test and register_response:
        print("✅ Registration endpoint available - understanding user structure")
        print(f"   Registration response keys: {list(register_response.keys())}")
    else:
        print("❌ Registration endpoint not available or failed")
    
    return True

def test_profile_data_debugging():
    """Debug profile data to understand name/picture inconsistencies"""
    print("\n" + "="*80)
    print("4. PROFILE DATA DEBUGGING")
    print("="*80)
    
    if not user_profile_data:
        print("❌ No user profile data available - skipping debugging")
        return False
    
    print("🔍 Debugging profile data for inconsistencies")
    print("🎯 Expected: User should see 'Dino' with avatar instead of 'Dino Observer'")
    
    # Analyze current profile data
    current_name = user_profile_data.get('name', '')
    current_picture = user_profile_data.get('picture', '')
    current_email = user_profile_data.get('email', '')
    
    print(f"\n--- CURRENT PROFILE DATA ANALYSIS ---")
    print(f"Current Name: '{current_name}'")
    print(f"Current Picture: '{current_picture}'")
    print(f"Current Email: '{current_email}'")
    
    # Check for issues
    issues_found = []
    
    if current_name == "Dino Observer":
        issues_found.append("Name shows 'Dino Observer' instead of expected 'Dino'")
    elif current_name != "Dino" and "Dino" not in current_name:
        issues_found.append(f"Name '{current_name}' doesn't contain expected 'Dino'")
    
    if not current_picture or current_picture in ['', 'N/A', None]:
        issues_found.append("No avatar picture URL found")
    elif 'default' in current_picture.lower() or 'placeholder' in current_picture.lower():
        issues_found.append("Picture appears to be a default/placeholder image")
    
    print(f"\n--- ISSUE ANALYSIS ---")
    if issues_found:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n--- POTENTIAL ROOT CAUSES ---")
        print("1. Profile data not properly merged from user_profiles collection")
        print("2. User profile record missing or incomplete in database")
        print("3. Authentication system not loading profile data correctly")
        print("4. Profile update mechanism not working properly")
        
        return False
    else:
        print("✅ No obvious issues found with current profile data")
        if current_name == "Dino" and current_picture:
            print("✅ Profile data appears to match user expectations")
        return True

def test_user_profile_endpoints():
    """Test user profile management endpoints"""
    print("\n" + "="*80)
    print("5. USER PROFILE MANAGEMENT TESTING")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available - skipping profile management tests")
        return False
    
    # Test profile update endpoint
    print("\n--- TESTING PROFILE UPDATE FUNCTIONALITY ---")
    
    profile_update_data = {
        "name": "Dino",
        "picture": "https://example.com/dino-avatar.jpg"
    }
    
    # Try different potential profile update endpoints
    update_endpoints = [
        "/auth/profile",
        "/user/profile", 
        "/profile",
        "/auth/update-profile",
        "/user/update"
    ]
    
    profile_updated = False
    for endpoint in update_endpoints:
        update_test, update_response = run_test(
            f"Profile Update Test ({endpoint})",
            endpoint,
            method="PUT",
            data=profile_update_data,
            auth=True,
            expected_status=200
        )
        
        if update_test and update_response:
            print(f"✅ Profile update successful via {endpoint}")
            profile_updated = True
            break
        else:
            print(f"❌ Profile update failed via {endpoint}")
    
    if not profile_updated:
        print("❌ No working profile update endpoint found")
        print("🔍 This could explain why user profile data isn't being updated properly")
    
    # Test profile retrieval after update
    if profile_updated:
        print("\n--- VERIFYING PROFILE UPDATE ---")
        
        # Re-test /auth/me to see if changes were applied
        verify_test, verify_response = run_test(
            "Verify Profile Update (/auth/me)",
            "/auth/me",
            method="GET",
            auth=True,
            expected_keys=["id", "email", "name"]
        )
        
        if verify_test and verify_response:
            updated_name = verify_response.get('name', '')
            updated_picture = verify_response.get('picture', '')
            
            print(f"Updated Name: '{updated_name}'")
            print(f"Updated Picture: '{updated_picture}'")
            
            if updated_name == "Dino":
                print("✅ Name successfully updated to 'Dino'")
            else:
                print(f"❌ Name update failed - still shows '{updated_name}'")
                
            if updated_picture == "https://example.com/dino-avatar.jpg":
                print("✅ Picture successfully updated")
            else:
                print(f"❌ Picture update failed - shows '{updated_picture}'")
        else:
            print("❌ Failed to verify profile update")
    
    return profile_updated

def main():
    """Main test execution function"""
    print("EMAIL/PASSWORD AUTHENTICATION SYSTEM TESTING")
    print("Testing authentication for user 'dino@cytonic.com' and profile data loading")
    print("="*80)
    
    # Run all test suites
    test_suites = [
        ("Email/Password Login", test_email_password_login),
        ("/auth/me Endpoint", test_auth_me_endpoint),
        ("Profile Data Investigation", test_profile_data_investigation),
        ("Profile Data Debugging", test_profile_data_debugging),
        ("User Profile Management", test_user_profile_endpoints)
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
    
    # Print specific findings and recommendations
    print(f"\n{'='*80}")
    print("SPECIFIC FINDINGS & RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if failed_suites:
        print("🔍 INVESTIGATION RESULTS:")
        
        if "Email/Password Login" in failed_suites:
            print("❌ Email/password login failed for 'dino@cytonic.com'")
            print("   Recommendations:")
            print("   1. Check if user exists in database")
            print("   2. Verify password hash is correct")
            print("   3. Ensure email/password auth endpoint is implemented")
        
        if "Profile Data Debugging" in failed_suites:
            print("❌ Profile data issues detected")
            print("   Recommendations:")
            print("   1. Check user_profiles collection for 'dino@cytonic.com'")
            print("   2. Verify profile data merging logic in authentication")
            print("   3. Ensure profile updates are properly saved")
        
        if "User Profile Management" in failed_suites:
            print("❌ Profile management endpoints not working")
            print("   Recommendations:")
            print("   1. Implement profile update endpoints")
            print("   2. Add profile data merging from user_profiles collection")
            print("   3. Ensure profile changes persist correctly")
    else:
        print("✅ All authentication and profile tests passed!")
        print("✅ User 'dino@cytonic.com' authentication system is working correctly")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_suites) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)