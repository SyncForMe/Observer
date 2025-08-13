#!/usr/bin/env python3
"""
PROFILE AUTHENTICATION SYSTEM TESTING FOR DINO@CYTONIC.COM
Testing the fixed profile authentication system to verify the improvements:

1. Test Updated Authentication - Login with dino@cytonic.com / Observerinho8
2. Test the updated /auth/me endpoint to see if email now appears correctly
3. Verify that profile merging now preserves email from users collection
4. Test Profile Avatar Generation - Test the `/auth/generate-profile-avatar` endpoint
5. Test Profile Update - Update the user profile with the generated avatar URL
6. Verify Complete Profile Data - Confirm user sees proper email and avatar

Focus: Verify that the user sees their proper email address in profile settings 
and a real generated avatar instead of placeholder images.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

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

# Test credentials for dino@cytonic.com
TEST_EMAIL = "dino@cytonic.com"
TEST_PASSWORD = "Observerinho8"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
user_data = None
generated_avatar_url = None

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

def test_dino_authentication():
    """Test authentication with dino@cytonic.com credentials"""
    global auth_token, user_data
    
    print("\n" + "="*80)
    print("1. DINO@CYTONIC.COM AUTHENTICATION TESTING")
    print("="*80)
    
    print(f"Testing login with credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
    
    # Test email/password login
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_test, login_response = run_test(
        "Login with dino@cytonic.com",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"],
        measure_time=True
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        
        print(f"✅ Login successful!")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Name: {user_data.get('name')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Picture: {user_data.get('picture')}")
        
        # Verify email is correct
        if user_data.get('email') == TEST_EMAIL:
            print(f"✅ Email correctly preserved: {TEST_EMAIL}")
        else:
            print(f"❌ Email mismatch: expected {TEST_EMAIL}, got {user_data.get('email')}")
            return False
            
        # Verify name is not empty
        if user_data.get('name'):
            print(f"✅ Name is present: {user_data.get('name')}")
        else:
            print(f"❌ Name is missing or empty")
            return False
            
    else:
        print("❌ Login failed")
        return False
    
    return True

def test_auth_me_endpoint():
    """Test the /auth/me endpoint to verify profile data merging"""
    global user_data
    
    print("\n" + "="*80)
    print("2. /AUTH/ME ENDPOINT TESTING")
    print("="*80)
    
    print("Testing the updated /auth/me endpoint to verify email appears correctly")
    
    # Test /auth/me endpoint
    me_test, me_response = run_test(
        "Get Profile via /auth/me",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"],
        measure_time=True
    )
    
    if me_test and me_response:
        print(f"✅ /auth/me endpoint working!")
        print(f"   User ID: {me_response.get('id')}")
        print(f"   Name: {me_response.get('name')}")
        print(f"   Email: {me_response.get('email')}")
        print(f"   Picture: {me_response.get('picture')}")
        
        # Verify email consistency between login and /auth/me
        login_email = user_data.get('email')
        me_email = me_response.get('email')
        
        if login_email == me_email == TEST_EMAIL:
            print(f"✅ Email consistency verified: {TEST_EMAIL}")
        else:
            print(f"❌ Email inconsistency:")
            print(f"   Login response: {login_email}")
            print(f"   /auth/me response: {me_email}")
            print(f"   Expected: {TEST_EMAIL}")
            return False
            
        # Verify name consistency
        login_name = user_data.get('name')
        me_name = me_response.get('name')
        
        if login_name == me_name:
            print(f"✅ Name consistency verified: {me_name}")
        else:
            print(f"❌ Name inconsistency:")
            print(f"   Login response: {login_name}")
            print(f"   /auth/me response: {me_name}")
            return False
            
        # Update user_data with /auth/me response for further tests
        user_data = me_response
        
    else:
        print("❌ /auth/me endpoint failed")
        return False
    
    return True

def test_profile_avatar_generation():
    """Test the /auth/generate-profile-avatar endpoint"""
    global generated_avatar_url
    
    print("\n" + "="*80)
    print("3. PROFILE AVATAR GENERATION TESTING")
    print("="*80)
    
    print("Testing the /auth/generate-profile-avatar endpoint with professional prompt")
    
    # Test avatar generation with professional prompt
    avatar_data = {
        "prompt": "professional business portrait, confident expression",
        "name": user_data.get('name', 'Dino')
    }
    
    avatar_test, avatar_response = run_test(
        "Generate Profile Avatar",
        "/auth/generate-profile-avatar",
        method="POST",
        data=avatar_data,
        auth=True,
        expected_keys=["success", "avatar_url"],
        measure_time=True
    )
    
    if avatar_test and avatar_response:
        success = avatar_response.get("success")
        generated_avatar_url = avatar_response.get("avatar_url")
        
        if success and generated_avatar_url:
            print(f"✅ Avatar generation successful!")
            print(f"   Avatar URL: {generated_avatar_url}")
            
            # Verify URL is valid (starts with http)
            if generated_avatar_url.startswith('http'):
                print(f"✅ Avatar URL is valid")
            else:
                print(f"❌ Avatar URL appears invalid: {generated_avatar_url}")
                return False
                
        else:
            print(f"❌ Avatar generation failed:")
            print(f"   Success: {success}")
            print(f"   Avatar URL: {generated_avatar_url}")
            return False
            
    else:
        print("❌ Avatar generation endpoint failed")
        return False
    
    return True

def test_profile_update():
    """Test profile update with generated avatar URL"""
    print("\n" + "="*80)
    print("4. PROFILE UPDATE TESTING")
    print("="*80)
    
    print("Testing profile update with generated avatar URL")
    
    # Test profile update with avatar
    profile_update_data = {
        "name": user_data.get('name'),
        "email": user_data.get('email'),
        "bio": "Updated profile with generated avatar",
        "picture": generated_avatar_url
    }
    
    update_test, update_response = run_test(
        "Update Profile with Avatar",
        "/auth/profile",
        method="PUT",
        data=profile_update_data,
        auth=True,
        expected_keys=["success", "message"],
        measure_time=True
    )
    
    if update_test and update_response:
        success = update_response.get("success")
        message = update_response.get("message")
        
        if success:
            print(f"✅ Profile update successful: {message}")
        else:
            print(f"❌ Profile update failed: {message}")
            return False
            
    else:
        print("❌ Profile update endpoint failed")
        return False
    
    return True

def test_complete_profile_verification():
    """Verify complete profile data after updates"""
    print("\n" + "="*80)
    print("5. COMPLETE PROFILE DATA VERIFICATION")
    print("="*80)
    
    print("Verifying complete profile data shows proper email and avatar")
    
    # Test /auth/me again to verify updates persisted
    final_test, final_response = run_test(
        "Final Profile Verification",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name", "picture"],
        measure_time=True
    )
    
    if final_test and final_response:
        print(f"✅ Final profile verification successful!")
        print(f"   User ID: {final_response.get('id')}")
        print(f"   Name: {final_response.get('name')}")
        print(f"   Email: {final_response.get('email')}")
        print(f"   Picture: {final_response.get('picture')}")
        
        # Verify email is still correct
        if final_response.get('email') == TEST_EMAIL:
            print(f"✅ Email maintained during profile updates: {TEST_EMAIL}")
        else:
            print(f"❌ Email lost during profile updates: expected {TEST_EMAIL}, got {final_response.get('email')}")
            return False
            
        # Verify avatar URL is present and correct
        final_picture = final_response.get('picture')
        if final_picture and final_picture == generated_avatar_url:
            print(f"✅ Avatar URL properly persisted and displays correctly")
        elif final_picture:
            print(f"⚠️ Avatar URL present but different from generated:")
            print(f"   Generated: {generated_avatar_url}")
            print(f"   Final: {final_picture}")
        else:
            print(f"❌ Avatar URL missing from final profile")
            return False
            
        # Verify name is still present
        if final_response.get('name'):
            print(f"✅ Name maintained: {final_response.get('name')}")
        else:
            print(f"❌ Name lost during profile updates")
            return False
            
        # Summary of complete profile
        print(f"\n🎯 COMPLETE PROFILE SUMMARY:")
        print(f"   ✅ Name: {final_response.get('name')}")
        print(f"   ✅ Email: {final_response.get('email')}")
        print(f"   ✅ Avatar: {'Present' if final_picture else 'Missing'}")
        print(f"   ✅ Profile Complete: All required data present")
        
    else:
        print("❌ Final profile verification failed")
        return False
    
    return True

def test_authentication_flow_consistency():
    """Test the complete authentication flow to ensure consistency"""
    print("\n" + "="*80)
    print("6. AUTHENTICATION FLOW CONSISTENCY TESTING")
    print("="*80)
    
    print("Testing complete authentication flow for consistency")
    
    # Test multiple /auth/me calls to ensure consistency
    consistency_tests = []
    
    for i in range(3):
        test_name = f"Consistency Check #{i+1}"
        consistency_test, consistency_response = run_test(
            test_name,
            "/auth/me",
            method="GET",
            auth=True,
            expected_keys=["id", "email", "name"]
        )
        
        if consistency_test and consistency_response:
            consistency_tests.append({
                "test": test_name,
                "email": consistency_response.get('email'),
                "name": consistency_response.get('name'),
                "picture": consistency_response.get('picture')
            })
        else:
            print(f"❌ {test_name} failed")
            return False
    
    # Verify all responses are identical
    if len(consistency_tests) == 3:
        first_test = consistency_tests[0]
        all_consistent = True
        
        for test in consistency_tests[1:]:
            if (test['email'] != first_test['email'] or 
                test['name'] != first_test['name'] or 
                test['picture'] != first_test['picture']):
                all_consistent = False
                break
        
        if all_consistent:
            print(f"✅ Authentication flow is consistent across multiple calls")
            print(f"   Email: {first_test['email']}")
            print(f"   Name: {first_test['name']}")
            print(f"   Picture: {'Present' if first_test['picture'] else 'Missing'}")
        else:
            print(f"❌ Authentication flow inconsistency detected:")
            for i, test in enumerate(consistency_tests):
                print(f"   Test {i+1}: email={test['email']}, name={test['name']}")
            return False
    else:
        print(f"❌ Could not complete consistency tests")
        return False
    
    return True

def main():
    """Main test execution function"""
    print("PROFILE AUTHENTICATION SYSTEM TESTING FOR DINO@CYTONIC.COM")
    print("Testing the fixed profile authentication system to verify improvements")
    print("="*80)
    
    # Run all test suites in order
    test_suites = [
        ("Dino Authentication", test_dino_authentication),
        ("Auth Me Endpoint", test_auth_me_endpoint),
        ("Profile Avatar Generation", test_profile_avatar_generation),
        ("Profile Update", test_profile_update),
        ("Complete Profile Verification", test_complete_profile_verification),
        ("Authentication Flow Consistency", test_authentication_flow_consistency)
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
                # Continue with other tests even if one fails
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
        print(f"\n🎯 VERIFICATION COMPLETE:")
        print(f"   ✅ User can login with dino@cytonic.com / Observerinho8")
        print(f"   ✅ Email appears correctly in profile settings")
        print(f"   ✅ Profile merging preserves email from users collection")
        print(f"   ✅ Avatar generation works with professional prompts")
        print(f"   ✅ Profile updates persist correctly")
        print(f"   ✅ Complete profile data is consistent")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_suites) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)