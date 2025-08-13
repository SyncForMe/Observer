#!/usr/bin/env python3
"""
USER PROFILE DATA PERSISTENCE TESTING
Testing user profile data persistence across login sessions as requested in the review.

SPECIFIC TESTING WORKFLOW:
1. Create a test user and save initial profile data
2. Update the user's profile (change name, bio, picture)
3. Verify the profile update was saved correctly
4. Simulate logout/login cycle by calling the authentication endpoints
5. Verify that the updated profile data persists and is returned on login
6. Test both the /auth/emergent-session and /auth/me endpoints

FOCUS AREAS:
- Profile data persistence in user_profiles collection
- Profile data merging during authentication
- Verify name changes persist across sessions
- Verify other profile data (bio, picture) persists
- Ensure login response includes saved profile data, not just fresh auth data
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

# Global variables for profile persistence testing
auth_token = None
test_user_id = None
test_user_email = None
initial_profile_data = {}
updated_profile_data = {}

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

def step_1_create_test_user_and_initial_profile():
    """Step 1: Create a test user and save initial profile data"""
    global auth_token, test_user_id, test_user_email, initial_profile_data
    
    print("\n" + "="*80)
    print("STEP 1: CREATE TEST USER AND INITIAL PROFILE DATA")
    print("="*80)
    
    # First, authenticate as a test user
    guest_test, guest_response = run_test(
        "Create Test User (Guest Login)",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"],
        measure_time=True
    )
    
    if not guest_test or not guest_response:
        print("❌ Failed to create test user")
        return False
    
    # Extract authentication details
    auth_token = guest_response.get("access_token")
    user_data = guest_response.get("user", {})
    test_user_id = user_data.get("id")
    test_user_email = user_data.get("email")
    
    print(f"✅ Test user created successfully")
    print(f"   User ID: {test_user_id}")
    print(f"   Email: {test_user_email}")
    
    # Get initial profile data
    initial_profile_test, initial_profile_response = run_test(
        "Get Initial Profile Data",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"],
        measure_time=True
    )
    
    if not initial_profile_test or not initial_profile_response:
        print("❌ Failed to get initial profile data")
        return False
    
    # Store initial profile data
    initial_profile_data = {
        "id": initial_profile_response.get("id"),
        "email": initial_profile_response.get("email"),
        "name": initial_profile_response.get("name"),
        "picture": initial_profile_response.get("picture", ""),
        "bio": initial_profile_response.get("bio", "")
    }
    
    print(f"✅ Initial profile data captured:")
    print(f"   Name: {initial_profile_data['name']}")
    print(f"   Email: {initial_profile_data['email']}")
    print(f"   Picture: {initial_profile_data['picture']}")
    print(f"   Bio: {initial_profile_data['bio']}")
    
    return True

def step_2_update_user_profile():
    """Step 2: Update the user's profile (change name, bio, picture)"""
    global updated_profile_data
    
    print("\n" + "="*80)
    print("STEP 2: UPDATE USER PROFILE DATA")
    print("="*80)
    
    # Define updated profile data with realistic values
    updated_profile_data = {
        "name": "Dr. Sarah Johnson",
        "bio": "Senior AI Researcher specializing in machine learning and neural networks. Passionate about advancing AI technology for scientific discovery.",
        "picture": "https://example.com/profiles/sarah-johnson-updated.jpg"
    }
    
    print(f"Updating profile with:")
    print(f"   Name: {initial_profile_data['name']} → {updated_profile_data['name']}")
    print(f"   Bio: '{initial_profile_data['bio']}' → '{updated_profile_data['bio']}'")
    print(f"   Picture: {initial_profile_data['picture']} → {updated_profile_data['picture']}")
    
    # Update profile via API
    update_test, update_response = run_test(
        "Update User Profile",
        "/auth/profile",
        method="PUT",
        data=updated_profile_data,
        auth=True,
        expected_keys=["success"],
        measure_time=True
    )
    
    if not update_test or not update_response:
        print("❌ Failed to update user profile")
        return False
    
    # Check if update was successful
    if update_response.get("success"):
        print("✅ Profile update API call successful")
    else:
        print("❌ Profile update API returned success=false")
        return False
    
    return True

def step_3_verify_profile_update():
    """Step 3: Verify the profile update was saved correctly"""
    print("\n" + "="*80)
    print("STEP 3: VERIFY PROFILE UPDATE WAS SAVED")
    print("="*80)
    
    # Get updated profile data
    verify_test, verify_response = run_test(
        "Verify Profile Update",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"],
        measure_time=True
    )
    
    if not verify_test or not verify_response:
        print("❌ Failed to verify profile update")
        return False
    
    # Compare updated data
    current_name = verify_response.get("name")
    current_bio = verify_response.get("bio", "")
    current_picture = verify_response.get("picture", "")
    
    print(f"Profile verification results:")
    print(f"   Name: Expected '{updated_profile_data['name']}', Got '{current_name}'")
    print(f"   Bio: Expected '{updated_profile_data['bio']}', Got '{current_bio}'")
    print(f"   Picture: Expected '{updated_profile_data['picture']}', Got '{current_picture}'")
    
    # Check if updates were saved correctly
    name_match = current_name == updated_profile_data['name']
    bio_match = current_bio == updated_profile_data['bio']
    picture_match = current_picture == updated_profile_data['picture']
    
    if name_match and bio_match and picture_match:
        print("✅ All profile updates saved correctly")
        return True
    else:
        print("❌ Profile updates not saved correctly:")
        if not name_match:
            print(f"   ❌ Name mismatch")
        if not bio_match:
            print(f"   ❌ Bio mismatch")
        if not picture_match:
            print(f"   ❌ Picture mismatch")
        return False

def step_4_simulate_logout_login_cycle():
    """Step 4: Simulate logout/login cycle by calling the authentication endpoints"""
    global auth_token
    
    print("\n" + "="*80)
    print("STEP 4: SIMULATE LOGOUT/LOGIN CYCLE")
    print("="*80)
    
    # Simulate logout by clearing the auth token
    old_auth_token = auth_token
    auth_token = None
    print("✅ Simulated logout (cleared auth token)")
    
    # Verify that protected endpoints are no longer accessible
    logout_verify_test, logout_verify_response = run_test(
        "Verify Logout (Should Fail)",
        "/auth/me",
        method="GET",
        auth=False,  # No auth token
        expected_status=401  # Should be unauthorized
    )
    
    if logout_verify_test:
        print("✅ Logout verified - protected endpoints properly inaccessible")
    else:
        print("❌ Logout verification failed")
        return False
    
    # Simulate login by getting a new auth token
    login_test, login_response = run_test(
        "Simulate Login (New Auth Token)",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"],
        measure_time=True
    )
    
    if not login_test or not login_response:
        print("❌ Failed to simulate login")
        return False
    
    # Extract new authentication details
    new_auth_token = login_response.get("access_token")
    new_user_data = login_response.get("user", {})
    new_user_id = new_user_data.get("id")
    
    # Verify we got the same user
    if new_user_id == test_user_id:
        print("✅ Login successful - same user ID returned")
        auth_token = new_auth_token
        return True
    else:
        print(f"❌ Login returned different user ID: {new_user_id} vs {test_user_id}")
        return False

def step_5_verify_profile_persistence():
    """Step 5: Verify that the updated profile data persists and is returned on login"""
    print("\n" + "="*80)
    print("STEP 5: VERIFY PROFILE DATA PERSISTENCE AFTER LOGIN")
    print("="*80)
    
    # Get profile data after login
    persistence_test, persistence_response = run_test(
        "Get Profile After Login",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"],
        measure_time=True
    )
    
    if not persistence_test or not persistence_response:
        print("❌ Failed to get profile data after login")
        return False
    
    # Compare with expected updated data
    persisted_name = persistence_response.get("name")
    persisted_bio = persistence_response.get("bio", "")
    persisted_picture = persistence_response.get("picture", "")
    persisted_email = persistence_response.get("email")
    persisted_id = persistence_response.get("id")
    
    print(f"Profile persistence verification:")
    print(f"   ID: Expected '{test_user_id}', Got '{persisted_id}'")
    print(f"   Email: Expected '{test_user_email}', Got '{persisted_email}'")
    print(f"   Name: Expected '{updated_profile_data['name']}', Got '{persisted_name}'")
    print(f"   Bio: Expected '{updated_profile_data['bio']}', Got '{persisted_bio}'")
    print(f"   Picture: Expected '{updated_profile_data['picture']}', Got '{persisted_picture}'")
    
    # Check persistence
    id_match = persisted_id == test_user_id
    email_match = persisted_email == test_user_email
    name_match = persisted_name == updated_profile_data['name']
    bio_match = persisted_bio == updated_profile_data['bio']
    picture_match = persisted_picture == updated_profile_data['picture']
    
    if id_match and email_match and name_match and bio_match and picture_match:
        print("✅ ALL PROFILE DATA PERSISTED CORRECTLY ACROSS LOGIN SESSION")
        return True
    else:
        print("❌ Profile data persistence failed:")
        if not id_match:
            print(f"   ❌ ID mismatch")
        if not email_match:
            print(f"   ❌ Email mismatch")
        if not name_match:
            print(f"   ❌ Name persistence failed")
        if not bio_match:
            print(f"   ❌ Bio persistence failed")
        if not picture_match:
            print(f"   ❌ Picture persistence failed")
        return False

def step_6_test_emergent_session_endpoint():
    """Step 6: Test both the /auth/emergent-session and /auth/me endpoints"""
    print("\n" + "="*80)
    print("STEP 6: TEST EMERGENT SESSION AND ME ENDPOINTS")
    print("="*80)
    
    # Test /auth/emergent-session endpoint with mock data
    print("--- Testing /auth/emergent-session endpoint ---")
    
    # Test with invalid session (should fail gracefully)
    emergent_test, emergent_response = run_test(
        "Test Emergent Session Endpoint",
        "/auth/emergent-session",
        method="POST",
        data={"session_id": "mock-session-for-testing"},
        auth=False,
        expected_status=401,  # Should fail with invalid session
        measure_time=True
    )
    
    if emergent_test:
        print("✅ Emergent session endpoint exists and handles invalid sessions correctly")
    else:
        print("❌ Emergent session endpoint test failed")
    
    # Test /auth/me endpoint (should work with current auth)
    print("--- Testing /auth/me endpoint with current auth ---")
    
    me_endpoint_test, me_endpoint_response = run_test(
        "Test /auth/me Endpoint",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"],
        measure_time=True
    )
    
    if me_endpoint_test and me_endpoint_response:
        print("✅ /auth/me endpoint working correctly")
        
        # Verify it returns the same persisted profile data
        me_name = me_endpoint_response.get("name")
        me_bio = me_endpoint_response.get("bio", "")
        me_picture = me_endpoint_response.get("picture", "")
        
        if (me_name == updated_profile_data['name'] and 
            me_bio == updated_profile_data['bio'] and 
            me_picture == updated_profile_data['picture']):
            print("✅ /auth/me returns correct persisted profile data")
            return True
        else:
            print("❌ /auth/me returns incorrect profile data")
            return False
    else:
        print("❌ /auth/me endpoint test failed")
        return False

def test_profile_data_merging():
    """Additional test: Verify profile data merging during authentication"""
    print("\n" + "="*80)
    print("ADDITIONAL TEST: PROFILE DATA MERGING DURING AUTHENTICATION")
    print("="*80)
    
    # Test that login response includes saved profile data, not just fresh auth data
    print("Testing that login response includes complete profile data...")
    
    # Perform another login to test data merging
    merge_test, merge_response = run_test(
        "Test Profile Data Merging on Login",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"],
        measure_time=True
    )
    
    if not merge_test or not merge_response:
        print("❌ Failed to test profile data merging")
        return False
    
    # Check if login response includes complete profile data
    login_user_data = merge_response.get("user", {})
    login_name = login_user_data.get("name")
    login_picture = login_user_data.get("picture", "")
    
    print(f"Login response profile data:")
    print(f"   Name in login response: '{login_name}'")
    print(f"   Picture in login response: '{login_picture}'")
    print(f"   Expected name: '{updated_profile_data['name']}'")
    print(f"   Expected picture: '{updated_profile_data['picture']}'")
    
    # Verify profile data is merged correctly in login response
    if (login_name == updated_profile_data['name'] and 
        login_picture == updated_profile_data['picture']):
        print("✅ Profile data correctly merged in login response")
        return True
    else:
        print("❌ Profile data not properly merged in login response")
        print("   This indicates the login response contains fresh auth data instead of saved profile data")
        return False

def main():
    """Main test execution function"""
    print("USER PROFILE DATA PERSISTENCE TESTING")
    print("Testing profile data persistence across login sessions")
    print("="*80)
    
    # Execute test steps in sequence
    test_steps = [
        ("Step 1: Create Test User and Initial Profile", step_1_create_test_user_and_initial_profile),
        ("Step 2: Update User Profile", step_2_update_user_profile),
        ("Step 3: Verify Profile Update", step_3_verify_profile_update),
        ("Step 4: Simulate Logout/Login Cycle", step_4_simulate_logout_login_cycle),
        ("Step 5: Verify Profile Persistence", step_5_verify_profile_persistence),
        ("Step 6: Test Emergent Session and Me Endpoints", step_6_test_emergent_session_endpoint),
        ("Additional: Test Profile Data Merging", test_profile_data_merging)
    ]
    
    failed_steps = []
    
    for step_name, test_function in test_steps:
        try:
            print(f"\n{'='*80}")
            print(f"EXECUTING: {step_name}")
            print(f"{'='*80}")
            
            success = test_function()
            if success:
                print(f"✅ {step_name} PASSED")
            else:
                print(f"❌ {step_name} FAILED")
                failed_steps.append(step_name)
                # Continue with remaining tests even if one fails
        except Exception as e:
            print(f"❌ {step_name} ERROR: {e}")
            failed_steps.append(step_name)
    
    # Print final summary
    print_summary()
    
    # Print step summary
    print(f"\n{'='*80}")
    print("PROFILE PERSISTENCE TEST SUMMARY")
    print(f"{'='*80}")
    
    total_steps = len(test_steps)
    passed_steps = total_steps - len(failed_steps)
    
    print(f"Total Test Steps: {total_steps}")
    print(f"Passed: {passed_steps}")
    print(f"Failed: {len(failed_steps)}")
    
    if failed_steps:
        print(f"\nFailed Test Steps:")
        for step in failed_steps:
            print(f"  ❌ {step}")
    else:
        print(f"\n✅ ALL PROFILE PERSISTENCE TESTS PASSED!")
    
    # Critical assessment
    print(f"\n{'='*80}")
    print("CRITICAL ASSESSMENT: USER PROFILE DATA PERSISTENCE")
    print(f"{'='*80}")
    
    if len(failed_steps) == 0:
        print("✅ PROFILE PERSISTENCE WORKING CORRECTLY")
        print("✅ User profile changes persist across login sessions")
        print("✅ Name changes persist correctly")
        print("✅ Bio and picture data persist correctly")
        print("✅ Login response includes saved profile data")
        print("✅ Profile data merging during authentication works")
        print("✅ Both /auth/emergent-session and /auth/me endpoints functional")
    else:
        print("❌ PROFILE PERSISTENCE HAS ISSUES")
        print("❌ User experience will be impacted")
        print("❌ Users may lose their profile changes between sessions")
        
        # Identify specific issues
        if "Step 2: Update User Profile" in failed_steps:
            print("❌ CRITICAL: Profile update API not working")
        if "Step 3: Verify Profile Update" in failed_steps:
            print("❌ CRITICAL: Profile updates not being saved to database")
        if "Step 5: Verify Profile Persistence" in failed_steps:
            print("❌ CRITICAL: Profile data not persisting across login sessions")
        if "Additional: Test Profile Data Merging" in failed_steps:
            print("❌ CRITICAL: Login response not including saved profile data")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)