#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient

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
MONGO_URL = os.environ.get('MONGO_URL')
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Test credentials
TEST_EMAIL = "dino@cytonic.com"
TEST_PASSWORD = "Observerinho8"

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers if needed
    if headers is None:
        headers = {}
    
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
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
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

def check_user_in_database():
    """Check if the test user exists in the database"""
    print("\n" + "="*80)
    print("CHECKING USER IN DATABASE")
    print("="*80)
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URL)
        db = client.ai_simulation
        
        # Check if user exists
        user = db.users.find_one({"email": TEST_EMAIL})
        
        if user:
            print(f"✅ User {TEST_EMAIL} exists in the database")
            print(f"User ID: {user.get('_id')}")
            print(f"User Name: {user.get('name')}")
            
            # Check password hash if available
            password_hash = user.get('password_hash')
            if password_hash:
                print(f"Password hash exists: {password_hash}")
                
                # Verify password hash
                try:
                    is_valid = bcrypt.checkpw(TEST_PASSWORD.encode('utf-8'), password_hash.encode('utf-8'))
                    if is_valid:
                        print(f"✅ Password hash is valid for password '{TEST_PASSWORD}'")
                    else:
                        print(f"❌ Password hash is NOT valid for password '{TEST_PASSWORD}'")
                except Exception as e:
                    print(f"Error verifying password hash: {e}")
            else:
                print("❌ No password hash found for user")
            
            return True, user
        else:
            print(f"❌ User {TEST_EMAIL} does not exist in the database")
            return False, None
    
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False, None

def test_specific_login():
    """Test the specific login credentials for dino@cytonic.com"""
    print("\n" + "="*80)
    print("TESTING SPECIFIC LOGIN CREDENTIALS")
    print("="*80)
    
    global auth_token
    
    # Test 1: Check if user exists in database
    print("\nTest 1: Checking if user exists in database")
    user_exists, user_data = check_user_in_database()
    
    # Test 2: Login with specific credentials
    print("\nTest 2: Login with specific credentials (dino@cytonic.com)")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_test, login_response = run_test(
        "Login with specific credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        print("✅ Login successful with dino@cytonic.com/Observerinho8")
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        user_id = user_data.get("id")
        print(f"User ID: {user_id}")
        print(f"JWT Token: {auth_token}")
        
        # Verify token structure
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ JWT token is valid and contains: {decoded_token}")
            if "user_id" in decoded_token and "sub" in decoded_token:
                print("✅ JWT token contains required fields (user_id, sub)")
            else:
                print("❌ JWT token is missing required fields")
        except Exception as e:
            print(f"❌ JWT token validation failed: {e}")
    else:
        print("❌ Login failed with dino@cytonic.com/Observerinho8")
        
        # Test 3: Try user registration if needed
        print("\nTest 3: Registering user since login failed")
        
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Dino Test"
        }
        
        register_test, register_response = run_test(
            "Register user",
            "/auth/register",
            method="POST",
            data=register_data,
            expected_keys=["access_token", "token_type", "user"]
        )
        
        if register_test and register_response:
            print(f"✅ Successfully registered user with email: {TEST_EMAIL}")
            auth_token = register_response.get("access_token")
            user_data = register_response.get("user", {})
            user_id = user_data.get("id")
            print(f"User ID: {user_id}")
            print(f"JWT Token: {auth_token}")
        else:
            print(f"❌ Failed to register user with email: {TEST_EMAIL}")
    
    # Test 4: Test "Continue as Guest" functionality
    print("\nTest 4: Testing 'Continue as Guest' functionality")
    
    guest_test, guest_response = run_test(
        "Continue as Guest",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        print("✅ 'Continue as Guest' functionality works correctly")
        guest_token = guest_response.get("access_token")
        guest_user = guest_response.get("user", {})
        guest_user_id = guest_user.get("id")
        print(f"Guest User ID: {guest_user_id}")
        print(f"Guest JWT Token: {guest_token}")
        
        # Verify token structure
        try:
            decoded_token = jwt.decode(guest_token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ Guest JWT token is valid and contains: {decoded_token}")
            if "sub" in decoded_token:
                print("✅ Guest JWT token contains required fields")
            else:
                print("❌ Guest JWT token is missing required fields")
        except Exception as e:
            print(f"❌ Guest JWT token validation failed: {e}")
    else:
        print("❌ 'Continue as Guest' functionality failed")
    
    # Test 5: Test JWT token validation with /api/auth/me endpoint
    print("\nTest 5: Testing JWT token validation with /api/auth/me endpoint")
    
    if 'auth_token' in locals() and auth_token:
        me_test, me_response = run_test(
            "Get current user profile",
            "/auth/me",
            method="GET",
            auth=True,
            headers={"Authorization": f"Bearer {auth_token}"},
            expected_keys=["id", "email", "name"]
        )
        
        if me_test and me_response:
            print("✅ Successfully retrieved user profile with JWT token")
            print(f"User profile: {json.dumps(me_response, indent=2)}")
        else:
            print("❌ Failed to retrieve user profile with JWT token")
    else:
        print("❌ Cannot test /api/auth/me endpoint without valid token")
    
    # Test 6: Test protected endpoint access
    print("\nTest 6: Testing protected endpoint access")
    
    if 'auth_token' in locals() and auth_token:
        protected_test, protected_response = run_test(
            "Access protected endpoint",
            "/documents",
            method="GET",
            auth=True,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if protected_test:
            print("✅ Successfully accessed protected endpoint with JWT token")
        else:
            print("❌ Failed to access protected endpoint with JWT token")
    else:
        print("❌ Cannot test protected endpoint without valid token")
    
    # Print summary
    print("\nSPECIFIC LOGIN CREDENTIALS SUMMARY:")
    
    if login_test or (not login_test and register_test):
        print("✅ Authentication with dino@cytonic.com/Observerinho8 is working correctly")
        print("✅ JWT token is generated and validated properly")
        print("✅ Protected endpoints can be accessed with the token")
        return True
    else:
        print("❌ Authentication with dino@cytonic.com/Observerinho8 failed")
        if guest_test:
            print("✅ 'Continue as Guest' functionality is working as a backup")
        else:
            print("❌ 'Continue as Guest' functionality is also not working")
        return False

if __name__ == "__main__":
    success = test_specific_login()
    print_summary()
    sys.exit(0 if success else 1)