#!/usr/bin/env python3
"""
DETAILED PROFILE DATA INVESTIGATION FOR dino@cytonic.com
Investigating the specific issue where:
- Admin endpoint shows: name="Dino Observer", email="dino@cytonic.com"
- Login/auth/me shows: name="Dino", email=""

This suggests there's a profile merging issue between users and user_profiles collections.
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

# Global variables for auth testing
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, auth=False, headers=None):
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
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Determine test result
        test_passed = response.status_code == expected_status
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

def main():
    """Main investigation function"""
    global auth_token, test_user_id
    
    print("DETAILED PROFILE DATA INVESTIGATION FOR dino@cytonic.com")
    print("Investigating profile merging issue between users and user_profiles collections")
    print("="*80)
    
    # Step 1: Login as dino@cytonic.com
    print("\n" + "="*80)
    print("STEP 1: LOGIN AS dino@cytonic.com")
    print("="*80)
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Dino Login",
        "/auth/login",
        method="POST",
        data=login_data
    )
    
    if not login_test or not login_response:
        print("❌ Cannot login as dino@cytonic.com")
        return False
    
    auth_token = login_response.get("access_token")
    user_data = login_response.get("user", {})
    test_user_id = user_data.get("id")
    
    print(f"\n--- LOGIN RESPONSE ANALYSIS ---")
    print(f"User ID: {test_user_id}")
    print(f"Name from login: '{user_data.get('name', 'NOT_FOUND')}'")
    print(f"Email from login: '{user_data.get('email', 'NOT_FOUND')}'")
    print(f"Picture from login: '{user_data.get('picture', 'NOT_FOUND')}'")
    
    # Step 2: Get profile from /auth/me
    print("\n" + "="*80)
    print("STEP 2: GET PROFILE FROM /auth/me")
    print("="*80)
    
    me_test, me_response = run_test(
        "Get Profile from /auth/me",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if me_test and me_response:
        print(f"\n--- /auth/me RESPONSE ANALYSIS ---")
        print(f"Name from /auth/me: '{me_response.get('name', 'NOT_FOUND')}'")
        print(f"Email from /auth/me: '{me_response.get('email', 'NOT_FOUND')}'")
        print(f"Picture from /auth/me: '{me_response.get('picture', 'NOT_FOUND')}'")
    
    # Step 3: Get user data from admin endpoint
    print("\n" + "="*80)
    print("STEP 3: GET USER DATA FROM ADMIN ENDPOINT")
    print("="*80)
    
    admin_test, admin_response = run_test(
        "Get Admin Users Data",
        "/admin/users",
        method="GET",
        auth=True
    )
    
    dino_user_from_admin = None
    if admin_test and admin_response:
        users = admin_response.get("users", [])
        for user in users:
            if user.get("id") == test_user_id:
                dino_user_from_admin = user
                break
        
        if dino_user_from_admin:
            print(f"\n--- ADMIN ENDPOINT USER DATA ---")
            print(f"Name from admin: '{dino_user_from_admin.get('name', 'NOT_FOUND')}'")
            print(f"Email from admin: '{dino_user_from_admin.get('email', 'NOT_FOUND')}'")
            print(f"Auth Type: '{dino_user_from_admin.get('auth_type', 'NOT_FOUND')}'")
            print(f"Created At: '{dino_user_from_admin.get('created_at', 'NOT_FOUND')}'")
        else:
            print("❌ Could not find dino user in admin response")
    
    # Step 4: Test profile update to see what happens
    print("\n" + "="*80)
    print("STEP 4: TEST PROFILE UPDATE TO INVESTIGATE user_profiles COLLECTION")
    print("="*80)
    
    # First, let's try to update the profile with the correct email
    update_data = {
        "name": "Dino",
        "email": "dino@cytonic.com",
        "picture": "https://example.com/dino-avatar.jpg"
    }
    
    update_test, update_response = run_test(
        "Update Profile with Correct Email",
        "/auth/profile",
        method="PUT",
        data=update_data,
        auth=True
    )
    
    if update_test:
        print("✅ Profile update successful")
        
        # Now check /auth/me again to see if the email appears
        me_after_test, me_after_response = run_test(
            "Get Profile After Update",
            "/auth/me",
            method="GET",
            auth=True
        )
        
        if me_after_test and me_after_response:
            print(f"\n--- /auth/me AFTER UPDATE ---")
            print(f"Name after update: '{me_after_response.get('name', 'NOT_FOUND')}'")
            print(f"Email after update: '{me_after_response.get('email', 'NOT_FOUND')}'")
            print(f"Picture after update: '{me_after_response.get('picture', 'NOT_FOUND')}'")
    else:
        print("❌ Profile update failed")
    
    # Step 5: Analysis and Summary
    print("\n" + "="*80)
    print("STEP 5: ANALYSIS AND SUMMARY")
    print("="*80)
    
    print("\n--- DATA COMPARISON ---")
    
    # Compare all the data sources
    login_name = user_data.get('name', '')
    login_email = user_data.get('email', '')
    
    me_name = me_response.get('name', '') if me_response else ''
    me_email = me_response.get('email', '') if me_response else ''
    
    admin_name = dino_user_from_admin.get('name', '') if dino_user_from_admin else ''
    admin_email = dino_user_from_admin.get('email', '') if dino_user_from_admin else ''
    
    after_update_name = me_after_response.get('name', '') if me_after_response else ''
    after_update_email = me_after_response.get('email', '') if me_after_response else ''
    
    print(f"LOGIN RESPONSE    - Name: '{login_name}', Email: '{login_email}'")
    print(f"/auth/me RESPONSE - Name: '{me_name}', Email: '{me_email}'")
    print(f"ADMIN RESPONSE    - Name: '{admin_name}', Email: '{admin_email}'")
    print(f"AFTER UPDATE      - Name: '{after_update_name}', Email: '{after_update_email}'")
    
    print("\n--- ROOT CAUSE ANALYSIS ---")
    
    # Identify the issue
    if admin_email == "dino@cytonic.com" and (login_email == "" or me_email == ""):
        print("🔍 ISSUE IDENTIFIED: Email field is being lost during profile merging")
        print("   - Base user record (users collection) has correct email")
        print("   - Profile merging logic is overriding email with empty value")
        print("   - This suggests user_profiles collection has empty email field")
        
        if after_update_email == "dino@cytonic.com":
            print("✅ SOLUTION CONFIRMED: Updating user_profiles collection fixes the issue")
        else:
            print("❌ SOLUTION FAILED: Profile update didn't fix the email issue")
    
    if admin_name == "Dino Observer" and (login_name == "Dino" or me_name == "Dino"):
        print("🔍 ISSUE IDENTIFIED: Name field is being overridden during profile merging")
        print("   - Base user record (users collection) has 'Dino Observer'")
        print("   - Profile merging logic is overriding with 'Dino' from user_profiles")
        print("   - This suggests user_profiles collection has 'Dino' as name")
    
    print("\n--- RECOMMENDATIONS ---")
    print("1. Check user_profiles collection for user_id:", test_user_id)
    print("2. Verify profile merging logic in /auth/me endpoint")
    print("3. Ensure email field is properly preserved during profile updates")
    print("4. Consider which data source should be authoritative (users vs user_profiles)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)