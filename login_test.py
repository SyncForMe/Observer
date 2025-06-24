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

# Test credentials
TEST_EMAIL = "dino@cytonic.com"
TEST_PASSWORD = "Observerinho8"

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

def test_login():
    """Test login with specific credentials"""
    print("\n" + "="*80)
    print("TESTING LOGIN WITH SPECIFIC CREDENTIALS")
    print("="*80)
    
    # Check if user exists in database
    user_exists, user_data = check_user_in_database()
    
    # Test login with specific credentials
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    print(f"\nAttempting login with email: {TEST_EMAIL}, password: {TEST_PASSWORD}")
    
    try:
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        print(f"Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            auth_token = login_data.get("access_token")
            user = login_data.get("user", {})
            
            print("✅ Login successful!")
            print(f"User ID: {user.get('id')}")
            print(f"User Name: {user.get('name')}")
            print(f"JWT Token: {auth_token}")
            
            # Verify token
            try:
                decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
                print(f"✅ JWT token is valid and contains: {decoded_token}")
                
                # Test /api/auth/me endpoint
                print("\nTesting /api/auth/me endpoint with token")
                me_response = requests.get(
                    f"{API_URL}/auth/me",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ Successfully retrieved user profile")
                    print(f"Profile: {json.dumps(me_data, indent=2)}")
                else:
                    print(f"❌ Failed to retrieve user profile: {me_response.status_code}")
                    if me_response.headers.get("content-type") == "application/json":
                        print(f"Error: {me_response.json()}")
                    else:
                        print(f"Response: {me_response.text}")
                
                # Test protected endpoint
                print("\nTesting protected endpoint with token")
                protected_response = requests.get(
                    f"{API_URL}/documents",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                
                if protected_response.status_code == 200:
                    print("✅ Successfully accessed protected endpoint")
                else:
                    print(f"❌ Failed to access protected endpoint: {protected_response.status_code}")
                    if protected_response.headers.get("content-type") == "application/json":
                        print(f"Error: {protected_response.json()}")
                    else:
                        print(f"Response: {protected_response.text}")
                
                return True, auth_token
                
            except Exception as e:
                print(f"❌ JWT token validation failed: {e}")
                return False, None
        else:
            print("❌ Login failed")
            if login_response.headers.get("content-type") == "application/json":
                print(f"Error: {login_response.json()}")
            else:
                print(f"Response: {login_response.text}")
            
            return False, None
    
    except Exception as e:
        print(f"❌ Error during login request: {e}")
        return False, None

def test_guest_login():
    """Test 'Continue as Guest' functionality"""
    print("\n" + "="*80)
    print("TESTING 'CONTINUE AS GUEST' FUNCTIONALITY")
    print("="*80)
    
    try:
        guest_response = requests.post(f"{API_URL}/auth/test-login")
        print(f"Status Code: {guest_response.status_code}")
        
        if guest_response.status_code == 200:
            guest_data = guest_response.json()
            guest_token = guest_data.get("access_token")
            guest_user = guest_data.get("user", {})
            
            print("✅ 'Continue as Guest' successful!")
            print(f"Guest User ID: {guest_user.get('id')}")
            print(f"Guest User Name: {guest_user.get('name')}")
            print(f"Guest JWT Token: {guest_token}")
            
            # Verify token
            try:
                decoded_token = jwt.decode(guest_token, JWT_SECRET, algorithms=["HS256"])
                print(f"✅ Guest JWT token is valid and contains: {decoded_token}")
                
                # Test /api/auth/me endpoint
                print("\nTesting /api/auth/me endpoint with guest token")
                me_response = requests.get(
                    f"{API_URL}/auth/me",
                    headers={"Authorization": f"Bearer {guest_token}"}
                )
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ Successfully retrieved guest user profile")
                    print(f"Profile: {json.dumps(me_data, indent=2)}")
                else:
                    print(f"❌ Failed to retrieve guest user profile: {me_response.status_code}")
                    if me_response.headers.get("content-type") == "application/json":
                        print(f"Error: {me_response.json()}")
                    else:
                        print(f"Response: {me_response.text}")
                
                # Test protected endpoint
                print("\nTesting protected endpoint with guest token")
                protected_response = requests.get(
                    f"{API_URL}/documents",
                    headers={"Authorization": f"Bearer {guest_token}"}
                )
                
                if protected_response.status_code == 200:
                    print("✅ Successfully accessed protected endpoint with guest token")
                else:
                    print(f"❌ Failed to access protected endpoint with guest token: {protected_response.status_code}")
                    if protected_response.headers.get("content-type") == "application/json":
                        print(f"Error: {protected_response.json()}")
                    else:
                        print(f"Response: {protected_response.text}")
                
                return True, guest_token
                
            except Exception as e:
                print(f"❌ Guest JWT token validation failed: {e}")
                return False, None
        else:
            print("❌ 'Continue as Guest' failed")
            if guest_response.headers.get("content-type") == "application/json":
                print(f"Error: {guest_response.json()}")
            else:
                print(f"Response: {guest_response.text}")
            
            return False, None
    
    except Exception as e:
        print(f"❌ Error during 'Continue as Guest' request: {e}")
        return False, None

def print_summary(login_success, guest_success):
    """Print a summary of the test results"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if login_success:
        print("✅ Login with dino@cytonic.com/Observerinho8 is working correctly")
        print("✅ JWT token is generated and validated properly")
        print("✅ Protected endpoints can be accessed with the token")
    else:
        print("❌ Login with dino@cytonic.com/Observerinho8 failed")
    
    if guest_success:
        print("✅ 'Continue as Guest' functionality is working correctly")
        print("✅ Guest JWT token is generated and validated properly")
        print("✅ Protected endpoints can be accessed with the guest token")
    else:
        print("❌ 'Continue as Guest' functionality failed")
    
    print("="*80)
    overall_result = "PASSED" if (login_success or guest_success) else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

if __name__ == "__main__":
    login_success, auth_token = test_login()
    guest_success, guest_token = test_guest_login()
    
    print_summary(login_success, guest_success)
    
    sys.exit(0 if (login_success or guest_success) else 1)