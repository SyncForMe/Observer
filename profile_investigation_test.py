#!/usr/bin/env python3
"""
PROFILE DATA LOADING INVESTIGATION FOR dino@cytonic.com
Deep investigation of the profile data loading issue as requested in the review.

Investigation Areas:
1. Check Profile Data Storage - Login as dino@cytonic.com and examine exact profile data returned
2. Check user_profiles collection data - Verify what's stored in the database
3. Test Profile Settings Endpoint - Test profile settings/update endpoints
4. Compare Base User vs Profile Data - Check users vs user_profiles collections
5. Test Profile Update Flow - Check if profile update endpoints work correctly

Expected Results:
- Name: "Dino" ✅ (working)
- Avatar: Their generated profile picture ❌ (missing)
- Email: dino@cytonic.com ❌ (not showing in profile settings)
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
    "tests": [],
    "profile_data": {},
    "issues_found": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None

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

def test_dino_email_password_login():
    """Test email/password login for dino@cytonic.com"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. DINO EMAIL/PASSWORD LOGIN TESTING")
    print("="*80)
    
    # Test email/password login for dino@cytonic.com
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"  # Known password for dino user
    }
    
    login_test, login_response = run_test(
        "Dino Email/Password Login",
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
        
        print(f"✅ Dino login successful. User ID: {test_user_id}")
        
        # Store profile data for analysis
        test_results["profile_data"]["login_response"] = user_data
        
        # Analyze profile data from login
        print("\n--- PROFILE DATA ANALYSIS FROM LOGIN ---")
        print(f"Name: {user_data.get('name', 'NOT FOUND')}")
        print(f"Email: {user_data.get('email', 'NOT FOUND')}")
        print(f"Picture: {user_data.get('picture', 'NOT FOUND')}")
        print(f"User ID: {user_data.get('id', 'NOT FOUND')}")
        print(f"Created At: {user_data.get('created_at', 'NOT FOUND')}")
        print(f"Last Login: {user_data.get('last_login', 'NOT FOUND')}")
        
        # Check for expected vs actual values
        expected_name = "Dino"
        expected_email = "dino@cytonic.com"
        
        actual_name = user_data.get('name', '')
        actual_email = user_data.get('email', '')
        actual_picture = user_data.get('picture', '')
        
        print("\n--- EXPECTATION VS REALITY CHECK ---")
        if actual_name == expected_name:
            print(f"✅ Name matches expectation: '{actual_name}'")
        else:
            print(f"❌ Name mismatch: expected '{expected_name}', got '{actual_name}'")
            test_results["issues_found"].append(f"Name mismatch: expected '{expected_name}', got '{actual_name}'")
        
        if actual_email == expected_email:
            print(f"✅ Email matches expectation: '{actual_email}'")
        else:
            print(f"❌ Email mismatch: expected '{expected_email}', got '{actual_email}'")
            test_results["issues_found"].append(f"Email mismatch: expected '{expected_email}', got '{actual_email}'")
        
        if actual_picture and actual_picture != "":
            print(f"✅ Picture URL found: '{actual_picture}'")
        else:
            print(f"❌ Picture URL missing or empty: '{actual_picture}'")
            test_results["issues_found"].append(f"Picture URL missing or empty: '{actual_picture}'")
        
        # Verify JWT token structure
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            print(f"\n✅ JWT token is valid and contains: {list(decoded_token.keys())}")
            if "user_id" in decoded_token and "sub" in decoded_token:
                print("✅ JWT token contains required fields (user_id, sub)")
            else:
                print("❌ JWT token is missing required fields")
                test_results["issues_found"].append("JWT token missing required fields")
        except Exception as e:
            print(f"❌ JWT token validation failed: {e}")
            test_results["issues_found"].append(f"JWT token validation failed: {e}")
    else:
        print("❌ Dino login failed")
        test_results["issues_found"].append("Dino email/password login failed")
        return False
    
    return True

def test_profile_me_endpoint():
    """Test the /auth/me endpoint to get current user profile"""
    print("\n" + "="*80)
    print("2. PROFILE ME ENDPOINT TESTING")
    print("="*80)
    
    # Test JWT token validation with protected endpoint
    me_test, me_response = run_test(
        "Get Current User Profile (/auth/me)",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if me_test and me_response:
        print("✅ /auth/me endpoint working")
        
        # Store profile data for analysis
        test_results["profile_data"]["me_response"] = me_response
        
        # Analyze profile data from /auth/me
        print("\n--- PROFILE DATA ANALYSIS FROM /auth/me ---")
        print(f"Name: {me_response.get('name', 'NOT FOUND')}")
        print(f"Email: {me_response.get('email', 'NOT FOUND')}")
        print(f"Picture: {me_response.get('picture', 'NOT FOUND')}")
        print(f"User ID: {me_response.get('id', 'NOT FOUND')}")
        print(f"Google ID: {me_response.get('google_id', 'NOT FOUND')}")
        print(f"Auth Type: {me_response.get('auth_type', 'NOT FOUND')}")
        
        # Compare with login response
        login_data = test_results["profile_data"].get("login_response", {})
        
        print("\n--- CONSISTENCY CHECK: LOGIN vs /auth/me ---")
        for field in ["name", "email", "picture", "id"]:
            login_value = login_data.get(field, "NOT_IN_LOGIN")
            me_value = me_response.get(field, "NOT_IN_ME")
            
            if login_value == me_value:
                print(f"✅ {field}: Consistent between login and /auth/me")
            else:
                print(f"❌ {field}: Inconsistent - Login: '{login_value}', /auth/me: '{me_value}'")
                test_results["issues_found"].append(f"{field} inconsistent between login and /auth/me")
        
        if me_response.get("id") == test_user_id:
            print("✅ User ID matches between login and profile")
        else:
            print("❌ User ID mismatch")
            test_results["issues_found"].append("User ID mismatch between login and /auth/me")
    else:
        print("❌ /auth/me endpoint failed")
        test_results["issues_found"].append("/auth/me endpoint failed")
        return False
    
    return True

def test_profile_settings_endpoints():
    """Test profile settings and update endpoints"""
    print("\n" + "="*80)
    print("3. PROFILE SETTINGS ENDPOINTS TESTING")
    print("="*80)
    
    # Check if there are profile-specific endpoints
    profile_endpoints_to_test = [
        ("/profile", "GET", "Get Profile"),
        ("/profile/settings", "GET", "Get Profile Settings"),
        ("/user/profile", "GET", "Get User Profile"),
        ("/users/profile", "GET", "Get Users Profile"),
        ("/auth/profile", "GET", "Get Auth Profile")
    ]
    
    working_endpoints = []
    
    for endpoint, method, description in profile_endpoints_to_test:
        test_passed, response_data = run_test(
            description,
            endpoint,
            method=method,
            auth=True,
            expected_status=200  # We'll accept any 2xx status
        )
        
        if test_passed and response_data:
            working_endpoints.append((endpoint, response_data))
            test_results["profile_data"][f"endpoint_{endpoint.replace('/', '_')}"] = response_data
            
            print(f"✅ Found working profile endpoint: {endpoint}")
            
            # Analyze the response for profile data
            print(f"--- PROFILE DATA FROM {endpoint} ---")
            if isinstance(response_data, dict):
                for key, value in response_data.items():
                    print(f"{key}: {value}")
            elif isinstance(response_data, list):
                print(f"Response is a list with {len(response_data)} items")
                if response_data:
                    print(f"First item: {response_data[0]}")
        else:
            print(f"❌ Profile endpoint not found or failed: {endpoint}")
    
    if not working_endpoints:
        print("⚠️ No dedicated profile endpoints found - profile data likely comes from /auth/me only")
        test_results["issues_found"].append("No dedicated profile endpoints found")
    
    return len(working_endpoints) > 0 or True  # Don't fail if no profile endpoints exist

def test_profile_update_functionality():
    """Test profile update functionality"""
    print("\n" + "="*80)
    print("4. PROFILE UPDATE FUNCTIONALITY TESTING")
    print("="*80)
    
    # Get current profile data first
    current_me_test, current_me_data = run_test(
        "Get Current Profile Before Update",
        "/auth/me",
        method="GET",
        auth=True
    )
    
    if not current_me_test:
        print("❌ Cannot get current profile data")
        return False
    
    original_name = current_me_data.get("name", "")
    original_picture = current_me_data.get("picture", "")
    
    print(f"Original Name: {original_name}")
    print(f"Original Picture: {original_picture}")
    
    # Test profile update endpoints
    update_endpoints_to_test = [
        ("/profile", "PUT", "Update Profile"),
        ("/profile", "POST", "Update Profile (POST)"),
        ("/auth/profile", "PUT", "Update Auth Profile"),
        ("/auth/profile", "POST", "Update Auth Profile (POST)"),
        ("/user/profile", "PUT", "Update User Profile"),
        ("/users/me", "PUT", "Update Users Me")
    ]
    
    # Test data for updates
    test_update_data = {
        "name": "Dino Test",
        "picture": "https://example.com/test-avatar.jpg"
    }
    
    successful_updates = []
    
    for endpoint, method, description in update_endpoints_to_test:
        print(f"\n--- Testing {description} ---")
        
        update_test, update_response = run_test(
            description,
            endpoint,
            method=method,
            data=test_update_data,
            auth=True
        )
        
        if update_test and update_response:
            print(f"✅ {description} endpoint exists and responded")
            successful_updates.append((endpoint, method, update_response))
            
            # Check if the update actually worked by getting profile again
            verify_test, verify_data = run_test(
                f"Verify Update from {endpoint}",
                "/auth/me",
                method="GET",
                auth=True
            )
            
            if verify_test and verify_data:
                updated_name = verify_data.get("name", "")
                updated_picture = verify_data.get("picture", "")
                
                print(f"After update - Name: {updated_name}, Picture: {updated_picture}")
                
                if updated_name == test_update_data["name"]:
                    print(f"✅ Name update successful via {endpoint}")
                else:
                    print(f"❌ Name update failed via {endpoint}")
                
                if updated_picture == test_update_data["picture"]:
                    print(f"✅ Picture update successful via {endpoint}")
                else:
                    print(f"❌ Picture update failed via {endpoint}")
            else:
                print(f"❌ Cannot verify update from {endpoint}")
        else:
            print(f"❌ {description} endpoint failed or doesn't exist")
    
    # Restore original profile data
    if successful_updates:
        restore_endpoint, restore_method, _ = successful_updates[0]
        restore_data = {
            "name": original_name,
            "picture": original_picture
        }
        
        print(f"\n--- Restoring Original Profile Data ---")
        restore_test, restore_response = run_test(
            "Restore Original Profile",
            restore_endpoint,
            method=restore_method,
            data=restore_data,
            auth=True
        )
        
        if restore_test:
            print("✅ Profile data restored")
        else:
            print("❌ Failed to restore profile data")
    
    if successful_updates:
        print(f"✅ Found {len(successful_updates)} working profile update endpoints")
        return True
    else:
        print("❌ No working profile update endpoints found")
        test_results["issues_found"].append("No working profile update endpoints found")
        return False

def test_database_profile_data():
    """Test if we can access database profile data through API endpoints"""
    print("\n" + "="*80)
    print("5. DATABASE PROFILE DATA INVESTIGATION")
    print("="*80)
    
    # Check if there are any endpoints that might give us database insights
    database_endpoints_to_test = [
        ("/users", "GET", "Get All Users"),
        ("/users/me", "GET", "Get Current User"),
        ("/user", "GET", "Get User"),
        ("/admin/users", "GET", "Admin Get Users"),
        ("/internal/user", "GET", "Internal User Data"),
        ("/debug/user", "GET", "Debug User Data")
    ]
    
    database_insights = []
    
    for endpoint, method, description in database_endpoints_to_test:
        test_passed, response_data = run_test(
            description,
            endpoint,
            method=method,
            auth=True
        )
        
        if test_passed and response_data:
            database_insights.append((endpoint, response_data))
            test_results["profile_data"][f"database_{endpoint.replace('/', '_')}"] = response_data
            
            print(f"✅ Found database endpoint: {endpoint}")
            
            # Analyze the response for user data structure
            print(f"--- DATABASE DATA FROM {endpoint} ---")
            if isinstance(response_data, dict):
                # Look for user-related fields
                user_fields = ["id", "email", "name", "picture", "google_id", "auth_type", "password_hash", "created_at", "last_login"]
                found_fields = []
                for field in user_fields:
                    if field in response_data:
                        found_fields.append(field)
                        print(f"{field}: {response_data[field]}")
                
                if found_fields:
                    print(f"✅ Found user fields: {found_fields}")
                else:
                    print("⚠️ No standard user fields found")
                    
            elif isinstance(response_data, list):
                print(f"Response is a list with {len(response_data)} items")
                if response_data and isinstance(response_data[0], dict):
                    print(f"First item keys: {list(response_data[0].keys())}")
        else:
            print(f"❌ Database endpoint failed or doesn't exist: {endpoint}")
    
    if database_insights:
        print(f"✅ Found {len(database_insights)} database endpoints with user data")
        return True
    else:
        print("⚠️ No database endpoints found - this is normal for security")
        return True  # Don't fail this test as it's normal not to expose database directly

def analyze_profile_data_issues():
    """Analyze all collected profile data to identify issues"""
    print("\n" + "="*80)
    print("6. PROFILE DATA ISSUE ANALYSIS")
    print("="*80)
    
    profile_data = test_results["profile_data"]
    issues = test_results["issues_found"]
    
    print("--- COLLECTED PROFILE DATA SUMMARY ---")
    for source, data in profile_data.items():
        print(f"\n{source.upper()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["name", "email", "picture", "id"]:
                    print(f"  {key}: {value}")
        else:
            print(f"  Data type: {type(data)}")
    
    print(f"\n--- ISSUES FOUND ({len(issues)} total) ---")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    # Specific analysis for the user's reported issues
    print("\n--- SPECIFIC USER ISSUE ANALYSIS ---")
    
    # Check login response for the expected data
    login_data = profile_data.get("login_response", {})
    me_data = profile_data.get("me_response", {})
    
    # Use the most recent/reliable data source
    current_data = me_data if me_data else login_data
    
    if current_data:
        current_name = current_data.get("name", "")
        current_email = current_data.get("email", "")
        current_picture = current_data.get("picture", "")
        
        print(f"Current Profile Data:")
        print(f"  Name: '{current_name}'")
        print(f"  Email: '{current_email}'")
        print(f"  Picture: '{current_picture}'")
        
        # Check against user expectations
        print(f"\nUser Expectation Analysis:")
        
        # Name check
        if current_name == "Dino":
            print(f"  ✅ Name: Expected 'Dino', Got '{current_name}' - WORKING")
        else:
            print(f"  ❌ Name: Expected 'Dino', Got '{current_name}' - ISSUE")
            
        # Email check
        if current_email == "dino@cytonic.com":
            print(f"  ✅ Email: Expected 'dino@cytonic.com', Got '{current_email}' - WORKING")
        else:
            print(f"  ❌ Email: Expected 'dino@cytonic.com', Got '{current_email}' - ISSUE")
            
        # Picture check
        if current_picture and current_picture != "" and "example.com" not in current_picture:
            print(f"  ✅ Picture: Found valid picture URL - WORKING")
        elif current_picture and "example.com" in current_picture:
            print(f"  ⚠️ Picture: Found placeholder URL '{current_picture}' - PLACEHOLDER")
        else:
            print(f"  ❌ Picture: Missing or empty '{current_picture}' - ISSUE")
    else:
        print("❌ No profile data collected - major issue")
        issues.append("No profile data could be collected")
    
    # Summary of findings
    print(f"\n--- INVESTIGATION SUMMARY ---")
    print(f"Total tests run: {len(test_results['tests'])}")
    print(f"Tests passed: {test_results['passed']}")
    print(f"Tests failed: {test_results['failed']}")
    print(f"Issues identified: {len(issues)}")
    
    return len(issues) == 0

def print_summary():
    """Print a comprehensive summary of the investigation"""
    print("\n" + "="*80)
    print("PROFILE DATA LOADING INVESTIGATION SUMMARY")
    print("="*80)
    
    print(f"User: dino@cytonic.com")
    print(f"Investigation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Tests: {len(test_results['tests'])}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    print(f"\n--- TEST RESULTS ---")
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']}")
    
    print(f"\n--- PROFILE DATA FINDINGS ---")
    profile_data = test_results["profile_data"]
    
    # Get the most reliable profile data
    current_data = profile_data.get("me_response") or profile_data.get("login_response") or {}
    
    if current_data:
        print(f"✅ Profile data successfully retrieved")
        print(f"   Name: {current_data.get('name', 'NOT FOUND')}")
        print(f"   Email: {current_data.get('email', 'NOT FOUND')}")
        print(f"   Picture: {current_data.get('picture', 'NOT FOUND')}")
        print(f"   User ID: {current_data.get('id', 'NOT FOUND')}")
    else:
        print(f"❌ No profile data could be retrieved")
    
    print(f"\n--- ISSUES IDENTIFIED ---")
    issues = test_results["issues_found"]
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("✅ No issues identified")
    
    print(f"\n--- RECOMMENDATIONS ---")
    if not issues:
        print("✅ Profile data loading appears to be working correctly")
    else:
        print("❌ Profile data loading has issues that need to be addressed:")
        
        # Specific recommendations based on issues found
        if any("Picture" in issue for issue in issues):
            print("   - Check avatar/picture generation and storage system")
            print("   - Verify profile picture upload/update endpoints")
            
        if any("Email" in issue for issue in issues):
            print("   - Check email field mapping in user profile system")
            print("   - Verify email is properly stored and retrieved")
            
        if any("Name" in issue for issue in issues):
            print("   - Check name field mapping and profile merging logic")
            
        if any("endpoint" in issue.lower() for issue in issues):
            print("   - Implement missing profile management endpoints")
            print("   - Add proper profile update functionality")
    
    print("="*80)

def main():
    """Main investigation function"""
    print("PROFILE DATA LOADING INVESTIGATION FOR dino@cytonic.com")
    print("Deep investigation of profile data storage and loading issues")
    print("="*80)
    
    # Run all investigation steps
    investigation_steps = [
        ("Dino Email/Password Login", test_dino_email_password_login),
        ("Profile Me Endpoint", test_profile_me_endpoint),
        ("Profile Settings Endpoints", test_profile_settings_endpoints),
        ("Profile Update Functionality", test_profile_update_functionality),
        ("Database Profile Data", test_database_profile_data),
        ("Profile Data Issue Analysis", analyze_profile_data_issues)
    ]
    
    failed_steps = []
    
    for step_name, test_function in investigation_steps:
        try:
            print(f"\n{'='*80}")
            print(f"INVESTIGATION STEP: {step_name}")
            print(f"{'='*80}")
            
            success = test_function()
            if success:
                print(f"✅ {step_name} completed successfully")
            else:
                print(f"❌ {step_name} found issues")
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} error: {e}")
            failed_steps.append(step_name)
            test_results["issues_found"].append(f"{step_name} error: {e}")
    
    # Print comprehensive summary
    print_summary()
    
    # Return overall success (investigation complete, regardless of issues found)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)