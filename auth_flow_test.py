#!/usr/bin/env python3
"""
Authentication Flow Test Script
Tests the complete authentication flow including localStorage caching:
1. Test the test-login endpoint to ensure it returns proper user data
2. Test the /auth/me endpoint to ensure it returns updated profile data after profile updates
3. Test the profile update endpoint to ensure it properly saves name and picture changes
4. Verify that the /auth/me endpoint returns the merged data from both users and user_profiles collections
"""

import requests
import json
import time
import os
import sys
import uuid
from dotenv import load_dotenv
import jwt
from datetime import datetime

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
test_user_email = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
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
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
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

def test_login_endpoint():
    """Test the test-login endpoint to ensure it returns proper user data"""
    global auth_token, test_user_id, test_user_email
    
    print("\n" + "="*80)
    print("TESTING TEST-LOGIN ENDPOINT")
    print("="*80)
    
    # Test 1: Call the test-login endpoint
    print("\nTest 1: Testing POST /auth/test-login endpoint")
    
    test_login_test, test_login_response = run_test(
        "Test Login Endpoint",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not test_login_test or not test_login_response:
        print("❌ Test login endpoint failed")
        return False
    
    # Extract token and user data
    auth_token = test_login_response.get("access_token")
    user_data = test_login_response.get("user", {})
    test_user_id = user_data.get("id")
    test_user_email = user_data.get("email")
    
    print(f"✅ Test login successful")
    print(f"User ID: {test_user_id}")
    print(f"User Email: {test_user_email}")
    print(f"JWT Token: {auth_token}")
    
    # Test 2: Verify JWT token structure
    print("\nTest 2: Verifying JWT token structure")
    
    try:
        decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
        print(f"✅ JWT token is valid and contains: {decoded_token}")
        
        # Check for required fields
        required_fields = ["sub", "user_id"]
        missing_fields = [field for field in required_fields if field not in decoded_token]
        
        if not missing_fields:
            print("✅ JWT token contains all required fields (sub, user_id)")
        else:
            print(f"❌ JWT token is missing required fields: {missing_fields}")
            return False
            
        # Verify user_id matches
        if decoded_token.get("user_id") == test_user_id:
            print("✅ JWT token user_id matches response user_id")
        else:
            print("❌ JWT token user_id does not match response user_id")
            return False
            
    except Exception as e:
        print(f"❌ JWT token validation failed: {e}")
        return False
    
    # Test 3: Verify user data structure
    print("\nTest 3: Verifying user data structure")
    
    required_user_fields = ["id", "email", "name"]
    missing_user_fields = [field for field in required_user_fields if field not in user_data]
    
    if not missing_user_fields:
        print("✅ User data contains all required fields (id, email, name)")
    else:
        print(f"❌ User data is missing required fields: {missing_user_fields}")
        return False
    
    # Test 4: Verify token can be used for authentication
    print("\nTest 4: Verifying token can be used for authentication")
    
    auth_test, auth_response = run_test(
        "Test token authentication",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if auth_test and auth_response:
        print("✅ Token successfully used for authentication")
        
        # Verify user data consistency
        if auth_response.get("id") == test_user_id:
            print("✅ User ID consistent between login and /auth/me")
        else:
            print("❌ User ID inconsistent between login and /auth/me")
            return False
    else:
        print("❌ Token authentication failed")
        return False
    
    print("\n✅ TEST-LOGIN ENDPOINT: All tests passed")
    return True

def test_auth_me_endpoint():
    """Test the /auth/me endpoint to ensure it returns proper user data"""
    print("\n" + "="*80)
    print("TESTING /AUTH/ME ENDPOINT")
    print("="*80)
    
    if not auth_token:
        print("❌ Cannot test /auth/me endpoint without authentication token")
        return False
    
    # Test 1: Basic /auth/me endpoint functionality
    print("\nTest 1: Testing GET /auth/me endpoint")
    
    me_test, me_response = run_test(
        "Get current user profile",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if not me_test or not me_response:
        print("❌ /auth/me endpoint failed")
        return False
    
    print("✅ /auth/me endpoint working correctly")
    
    # Test 2: Verify data structure and completeness
    print("\nTest 2: Verifying user profile data structure")
    
    # Check for basic required fields
    required_fields = ["id", "email", "name"]
    missing_fields = [field for field in required_fields if field not in me_response]
    
    if not missing_fields:
        print("✅ User profile contains all required fields")
    else:
        print(f"❌ User profile missing required fields: {missing_fields}")
        return False
    
    # Check for optional profile fields
    optional_fields = ["picture", "created_at", "last_login"]
    present_optional = [field for field in optional_fields if field in me_response]
    
    if present_optional:
        print(f"✅ User profile contains optional fields: {present_optional}")
    else:
        print("⚠️ User profile contains no optional fields")
    
    # Test 3: Verify user ID consistency
    print("\nTest 3: Verifying user ID consistency")
    
    if me_response.get("id") == test_user_id:
        print("✅ User ID consistent with login response")
    else:
        print("❌ User ID inconsistent with login response")
        return False
    
    # Test 4: Test without authentication
    print("\nTest 4: Testing /auth/me without authentication")
    
    no_auth_test, no_auth_response = run_test(
        "Get user profile without auth",
        "/auth/me",
        method="GET",
        auth=False,
        expected_status=403
    )
    
    if no_auth_test:
        print("✅ /auth/me correctly requires authentication")
    else:
        print("❌ /auth/me does not properly enforce authentication")
        return False
    
    print("\n✅ /AUTH/ME ENDPOINT: All tests passed")
    return True

def test_profile_update_endpoint():
    """Test the profile update endpoint to ensure it properly saves name and picture changes"""
    print("\n" + "="*80)
    print("TESTING PROFILE UPDATE ENDPOINT")
    print("="*80)
    
    if not auth_token:
        print("❌ Cannot test profile update endpoint without authentication token")
        return False
    
    # Get current profile data first
    print("\nGetting current profile data...")
    current_profile_test, current_profile = run_test(
        "Get current profile before update",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not current_profile_test or not current_profile:
        print("❌ Cannot get current profile data")
        return False
    
    original_name = current_profile.get("name", "")
    original_picture = current_profile.get("picture", "")
    
    print(f"Original name: {original_name}")
    print(f"Original picture: {original_picture}")
    
    # Test 1: Update user name
    print("\nTest 1: Testing name update")
    
    new_name = f"Updated Test User {uuid.uuid4().hex[:8]}"
    name_update_data = {
        "name": new_name
    }
    
    name_update_test, name_update_response = run_test(
        "Update user name",
        "/auth/profile",
        method="PUT",
        data=name_update_data,
        auth=True,
        expected_keys=["success", "user"]
    )
    
    if not name_update_test or not name_update_response:
        print("❌ Name update failed")
        return False
    
    print("✅ Name update request successful")
    
    # Verify the name was updated
    updated_user = name_update_response.get("user", {})
    if updated_user.get("name") == new_name:
        print("✅ Name successfully updated in response")
    else:
        print("❌ Name not updated in response")
        return False
    
    # Test 2: Verify name update persists via /auth/me
    print("\nTest 2: Verifying name update persists via /auth/me")
    
    me_after_name_test, me_after_name = run_test(
        "Get profile after name update",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not me_after_name_test or not me_after_name:
        print("❌ Cannot get profile after name update")
        return False
    
    if me_after_name.get("name") == new_name:
        print("✅ Name update persists in /auth/me endpoint")
    else:
        print(f"❌ Name update does not persist. Expected: {new_name}, Got: {me_after_name.get('name')}")
        return False
    
    # Test 3: Update user picture
    print("\nTest 3: Testing picture update")
    
    new_picture = f"https://example.com/avatar/{uuid.uuid4().hex[:8]}.jpg"
    picture_update_data = {
        "picture": new_picture
    }
    
    picture_update_test, picture_update_response = run_test(
        "Update user picture",
        "/auth/profile",
        method="PUT",
        data=picture_update_data,
        auth=True,
        expected_keys=["success", "user"]
    )
    
    if not picture_update_test or not picture_update_response:
        print("❌ Picture update failed")
        return False
    
    print("✅ Picture update request successful")
    
    # Verify the picture was updated
    updated_user = picture_update_response.get("user", {})
    if updated_user.get("picture") == new_picture:
        print("✅ Picture successfully updated in response")
    else:
        print("❌ Picture not updated in response")
        return False
    
    # Test 4: Verify picture update persists via /auth/me
    print("\nTest 4: Verifying picture update persists via /auth/me")
    
    me_after_picture_test, me_after_picture = run_test(
        "Get profile after picture update",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not me_after_picture_test or not me_after_picture:
        print("❌ Cannot get profile after picture update")
        return False
    
    if me_after_picture.get("picture") == new_picture:
        print("✅ Picture update persists in /auth/me endpoint")
    else:
        print(f"❌ Picture update does not persist. Expected: {new_picture}, Got: {me_after_picture.get('picture')}")
        return False
    
    # Test 5: Update both name and picture simultaneously
    print("\nTest 5: Testing simultaneous name and picture update")
    
    final_name = f"Final Test User {uuid.uuid4().hex[:8]}"
    final_picture = f"https://example.com/final-avatar/{uuid.uuid4().hex[:8]}.jpg"
    
    both_update_data = {
        "name": final_name,
        "picture": final_picture
    }
    
    both_update_test, both_update_response = run_test(
        "Update both name and picture",
        "/auth/profile",
        method="PUT",
        data=both_update_data,
        auth=True,
        expected_keys=["success", "user"]
    )
    
    if not both_update_test or not both_update_response:
        print("❌ Simultaneous update failed")
        return False
    
    print("✅ Simultaneous update request successful")
    
    # Verify both fields were updated
    updated_user = both_update_response.get("user", {})
    name_ok = updated_user.get("name") == final_name
    picture_ok = updated_user.get("picture") == final_picture
    
    if name_ok and picture_ok:
        print("✅ Both name and picture successfully updated in response")
    else:
        print(f"❌ Simultaneous update failed. Name OK: {name_ok}, Picture OK: {picture_ok}")
        return False
    
    # Test 6: Verify simultaneous update persists via /auth/me
    print("\nTest 6: Verifying simultaneous update persists via /auth/me")
    
    me_final_test, me_final = run_test(
        "Get profile after simultaneous update",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not me_final_test or not me_final:
        print("❌ Cannot get profile after simultaneous update")
        return False
    
    final_name_ok = me_final.get("name") == final_name
    final_picture_ok = me_final.get("picture") == final_picture
    
    if final_name_ok and final_picture_ok:
        print("✅ Simultaneous update persists in /auth/me endpoint")
    else:
        print(f"❌ Simultaneous update does not persist. Name OK: {final_name_ok}, Picture OK: {final_picture_ok}")
        return False
    
    # Test 7: Test profile update without authentication
    print("\nTest 7: Testing profile update without authentication")
    
    no_auth_update_test, no_auth_update_response = run_test(
        "Update profile without auth",
        "/auth/profile",
        method="PUT",
        data={"name": "Unauthorized User"},
        auth=False,
        expected_status=403
    )
    
    if no_auth_update_test:
        print("✅ Profile update correctly requires authentication")
    else:
        print("❌ Profile update does not properly enforce authentication")
        return False
    
    print("\n✅ PROFILE UPDATE ENDPOINT: All tests passed")
    return True

def test_merged_data_collections():
    """Verify that the /auth/me endpoint returns the merged data from both users and user_profiles collections"""
    print("\n" + "="*80)
    print("TESTING MERGED DATA FROM USERS AND USER_PROFILES COLLECTIONS")
    print("="*80)
    
    if not auth_token:
        print("❌ Cannot test merged data without authentication token")
        return False
    
    # Test 1: Get current profile data and analyze structure
    print("\nTest 1: Analyzing current profile data structure")
    
    profile_test, profile_data = run_test(
        "Get current profile for analysis",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not profile_test or not profile_data:
        print("❌ Cannot get profile data for analysis")
        return False
    
    print("✅ Profile data retrieved successfully")
    
    # Analyze the data structure
    print("\nProfile data structure analysis:")
    for key, value in profile_data.items():
        print(f"  - {key}: {type(value).__name__} = {value}")
    
    # Test 2: Check for fields that would come from users collection
    print("\nTest 2: Checking for users collection fields")
    
    users_fields = ["id", "email", "created_at", "last_login", "is_active"]
    found_users_fields = []
    missing_users_fields = []
    
    for field in users_fields:
        if field in profile_data:
            found_users_fields.append(field)
        else:
            missing_users_fields.append(field)
    
    if found_users_fields:
        print(f"✅ Found users collection fields: {found_users_fields}")
    else:
        print("❌ No users collection fields found")
    
    if missing_users_fields:
        print(f"⚠️ Missing users collection fields: {missing_users_fields}")
    
    # Test 3: Check for fields that would come from user_profiles collection
    print("\nTest 3: Checking for user_profiles collection fields")
    
    profiles_fields = ["name", "picture", "bio", "preferences", "settings"]
    found_profiles_fields = []
    missing_profiles_fields = []
    
    for field in profiles_fields:
        if field in profile_data:
            found_profiles_fields.append(field)
        else:
            missing_profiles_fields.append(field)
    
    if found_profiles_fields:
        print(f"✅ Found user_profiles collection fields: {found_profiles_fields}")
    else:
        print("❌ No user_profiles collection fields found")
    
    if missing_profiles_fields:
        print(f"⚠️ Missing user_profiles collection fields: {missing_profiles_fields}")
    
    # Test 4: Update profile and verify merge behavior
    print("\nTest 4: Testing merge behavior after profile update")
    
    # Update profile with new data
    update_data = {
        "name": f"Merge Test User {uuid.uuid4().hex[:8]}",
        "picture": f"https://example.com/merge-test/{uuid.uuid4().hex[:8]}.jpg"
    }
    
    update_test, update_response = run_test(
        "Update profile for merge test",
        "/auth/profile",
        method="PUT",
        data=update_data,
        auth=True
    )
    
    if not update_test or not update_response:
        print("❌ Profile update for merge test failed")
        return False
    
    # Get updated profile
    updated_profile_test, updated_profile = run_test(
        "Get updated profile for merge analysis",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not updated_profile_test or not updated_profile:
        print("❌ Cannot get updated profile for merge analysis")
        return False
    
    # Verify the merge worked correctly
    name_updated = updated_profile.get("name") == update_data["name"]
    picture_updated = updated_profile.get("picture") == update_data["picture"]
    id_preserved = updated_profile.get("id") == test_user_id
    email_preserved = updated_profile.get("email") == test_user_email
    
    if name_updated and picture_updated:
        print("✅ Profile fields successfully updated and merged")
    else:
        print(f"❌ Profile merge failed. Name updated: {name_updated}, Picture updated: {picture_updated}")
        return False
    
    if id_preserved and email_preserved:
        print("✅ User identity fields preserved during merge")
    else:
        print(f"❌ User identity not preserved. ID preserved: {id_preserved}, Email preserved: {email_preserved}")
        return False
    
    # Test 5: Verify data consistency across multiple requests
    print("\nTest 5: Testing data consistency across multiple requests")
    
    consistency_results = []
    
    for i in range(3):
        consistency_test, consistency_data = run_test(
            f"Consistency check {i+1}",
            "/auth/me",
            method="GET",
            auth=True
        )
        
        if consistency_test and consistency_data:
            consistency_results.append(consistency_data)
        else:
            print(f"❌ Consistency check {i+1} failed")
            return False
    
    # Compare all results
    first_result = consistency_results[0]
    all_consistent = True
    
    for i, result in enumerate(consistency_results[1:], 2):
        for key in first_result:
            if first_result[key] != result.get(key):
                print(f"❌ Inconsistency found in request {i} for field '{key}': {first_result[key]} != {result.get(key)}")
                all_consistent = False
    
    if all_consistent:
        print("✅ Data is consistent across multiple requests")
    else:
        print("❌ Data inconsistency detected across requests")
        return False
    
    print("\n✅ MERGED DATA COLLECTIONS: All tests passed")
    return True

def test_localstorage_caching_behavior():
    """Test localStorage caching behavior by simulating page refreshes"""
    print("\n" + "="*80)
    print("TESTING LOCALSTORAGE CACHING BEHAVIOR")
    print("="*80)
    
    if not auth_token:
        print("❌ Cannot test localStorage caching without authentication token")
        return False
    
    # Test 1: Verify profile data is accessible after "page refresh" (new request)
    print("\nTest 1: Testing profile accessibility after simulated page refresh")
    
    # Simulate a fresh request (as if page was refreshed and token retrieved from localStorage)
    fresh_request_test, fresh_request_data = run_test(
        "Fresh profile request (simulated page refresh)",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not fresh_request_test or not fresh_request_data:
        print("❌ Profile not accessible after simulated page refresh")
        return False
    
    print("✅ Profile accessible after simulated page refresh")
    
    # Test 2: Update profile and verify changes persist across "page refreshes"
    print("\nTest 2: Testing profile update persistence across page refreshes")
    
    # Update profile
    cache_test_name = f"Cache Test User {uuid.uuid4().hex[:8]}"
    cache_test_picture = f"https://example.com/cache-test/{uuid.uuid4().hex[:8]}.jpg"
    
    cache_update_data = {
        "name": cache_test_name,
        "picture": cache_test_picture
    }
    
    cache_update_test, cache_update_response = run_test(
        "Update profile for cache test",
        "/auth/profile",
        method="PUT",
        data=cache_update_data,
        auth=True
    )
    
    if not cache_update_test or not cache_update_response:
        print("❌ Profile update for cache test failed")
        return False
    
    # Simulate multiple page refreshes and verify data persists
    print("\nSimulating multiple page refreshes...")
    
    for i in range(3):
        print(f"\nSimulated page refresh {i+1}:")
        
        refresh_test, refresh_data = run_test(
            f"Profile after refresh {i+1}",
            "/auth/me",
            method="GET",
            auth=True
        )
        
        if not refresh_test or not refresh_data:
            print(f"❌ Profile not accessible after refresh {i+1}")
            return False
        
        # Verify updated data persists
        name_persists = refresh_data.get("name") == cache_test_name
        picture_persists = refresh_data.get("picture") == cache_test_picture
        
        if name_persists and picture_persists:
            print(f"✅ Profile updates persist after refresh {i+1}")
        else:
            print(f"❌ Profile updates do not persist after refresh {i+1}")
            print(f"   Name persists: {name_persists}, Picture persists: {picture_persists}")
            return False
    
    # Test 3: Test token expiration handling
    print("\nTest 3: Testing token validation consistency")
    
    # Verify token is still valid
    token_validation_test, token_validation_data = run_test(
        "Token validation check",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if token_validation_test and token_validation_data:
        print("✅ Token remains valid for profile access")
        
        # Verify token structure hasn't changed
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            if decoded_token.get("user_id") == test_user_id:
                print("✅ Token user_id remains consistent")
            else:
                print("❌ Token user_id inconsistency detected")
                return False
        except Exception as e:
            print(f"❌ Token validation failed: {e}")
            return False
    else:
        print("❌ Token validation failed")
        return False
    
    # Test 4: Test data integrity after multiple operations
    print("\nTest 4: Testing data integrity after multiple operations")
    
    # Perform multiple profile updates
    operations = [
        {"name": f"Operation 1 User {uuid.uuid4().hex[:4]}"},
        {"picture": f"https://example.com/op2/{uuid.uuid4().hex[:4]}.jpg"},
        {"name": f"Operation 3 User {uuid.uuid4().hex[:4]}", "picture": f"https://example.com/op3/{uuid.uuid4().hex[:4]}.jpg"}
    ]
    
    final_expected_name = None
    final_expected_picture = None
    
    for i, operation in enumerate(operations, 1):
        print(f"\nPerforming operation {i}: {operation}")
        
        op_test, op_response = run_test(
            f"Profile operation {i}",
            "/auth/profile",
            method="PUT",
            data=operation,
            auth=True
        )
        
        if not op_test or not op_response:
            print(f"❌ Operation {i} failed")
            return False
        
        # Track final expected values
        if "name" in operation:
            final_expected_name = operation["name"]
        if "picture" in operation:
            final_expected_picture = operation["picture"]
        
        # Verify operation result
        updated_user = op_response.get("user", {})
        for key, value in operation.items():
            if updated_user.get(key) == value:
                print(f"✅ Operation {i}: {key} updated correctly")
            else:
                print(f"❌ Operation {i}: {key} update failed")
                return False
    
    # Final verification
    print("\nFinal data integrity check...")
    
    final_check_test, final_check_data = run_test(
        "Final data integrity check",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not final_check_test or not final_check_data:
        print("❌ Final data integrity check failed")
        return False
    
    final_name_ok = final_check_data.get("name") == final_expected_name
    final_picture_ok = final_check_data.get("picture") == final_expected_picture
    
    if final_name_ok and final_picture_ok:
        print("✅ Final data integrity check passed")
    else:
        print(f"❌ Final data integrity check failed. Name OK: {final_name_ok}, Picture OK: {final_picture_ok}")
        return False
    
    print("\n✅ LOCALSTORAGE CACHING BEHAVIOR: All tests passed")
    return True

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"AUTHENTICATION FLOW TEST SUMMARY")
    print(f"PASSED: {test_results['passed']} | FAILED: {test_results['failed']}")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution function"""
    print("AUTHENTICATION FLOW COMPREHENSIVE TEST")
    print("="*80)
    print("Testing complete authentication flow including localStorage caching")
    print("="*80)
    
    # Run all test suites
    test_suites = [
        ("Test Login Endpoint", test_login_endpoint),
        ("Test /auth/me Endpoint", test_auth_me_endpoint),
        ("Test Profile Update Endpoint", test_profile_update_endpoint),
        ("Test Merged Data Collections", test_merged_data_collections),
        ("Test localStorage Caching Behavior", test_localstorage_caching_behavior)
    ]
    
    suite_results = []
    
    for suite_name, suite_function in test_suites:
        print(f"\n{'='*80}")
        print(f"RUNNING TEST SUITE: {suite_name}")
        print(f"{'='*80}")
        
        try:
            result = suite_function()
            suite_results.append((suite_name, result))
            
            if result:
                print(f"\n✅ {suite_name}: PASSED")
            else:
                print(f"\n❌ {suite_name}: FAILED")
                
        except Exception as e:
            print(f"\n❌ {suite_name}: ERROR - {e}")
            suite_results.append((suite_name, False))
    
    # Print final summary
    print("\n" + "="*80)
    print("FINAL TEST SUITE RESULTS")
    print("="*80)
    
    passed_suites = 0
    failed_suites = 0
    
    for suite_name, result in suite_results:
        if result:
            print(f"✅ {suite_name}")
            passed_suites += 1
        else:
            print(f"❌ {suite_name}")
            failed_suites += 1
    
    print("="*80)
    print(f"SUITE SUMMARY: {passed_suites} passed, {failed_suites} failed")
    
    # Print detailed test summary
    print_summary()
    
    # Return overall success
    return failed_suites == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)