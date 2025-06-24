#!/usr/bin/env python3
import requests
import json
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

def test_email_password_login():
    """Test email/password login functionality"""
    print("\n" + "="*80)
    print("TESTING EMAIL/PASSWORD LOGIN")
    print("="*80)
    
    # Generate unique test user credentials
    test_user_email = f"test.user.{uuid.uuid4()}@example.com"
    test_user_password = "securePassword123"
    test_user_name = "Test User"
    
    # Test 1: Register a new user
    print("\nTest 1: Register a new user")
    
    register_data = {
        "email": test_user_email,
        "password": test_user_password,
        "name": test_user_name
    }
    
    try:
        register_url = f"{API_URL}/auth/register"
        print(f"POST {register_url}")
        print(f"Request data: {json.dumps(register_data)}")
        
        register_response = requests.post(register_url, json=register_data)
        print(f"Status Code: {register_response.status_code}")
        
        if register_response.status_code == 200:
            register_data = register_response.json()
            print(f"Response: {json.dumps(register_data, indent=2)}")
            
            auth_token = register_data.get("access_token")
            user_data = register_data.get("user", {})
            user_id = user_data.get("id")
            
            print("✅ Registration successful")
            print(f"User registered with ID: {user_id}")
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
                
            # Test 2: Login with valid credentials
            print("\nTest 2: Login with valid credentials")
            
            login_data = {
                "email": test_user_email,
                "password": test_user_password
            }
            
            login_url = f"{API_URL}/auth/login"
            print(f"POST {login_url}")
            print(f"Request data: {json.dumps(login_data)}")
            
            login_response = requests.post(login_url, json=login_data)
            print(f"Status Code: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"Response: {json.dumps(login_data, indent=2)}")
                
                login_token = login_data.get("access_token")
                login_user = login_data.get("user", {})
                
                print("✅ Login successful")
                
                # Verify user data
                if login_user.get("id") == user_id:
                    print("✅ User ID matches registered user")
                else:
                    print("❌ User ID does not match registered user")
                    
                # Verify token
                try:
                    decoded_login_token = jwt.decode(login_token, JWT_SECRET, algorithms=["HS256"])
                    print(f"✅ Login JWT token is valid")
                    if decoded_login_token.get("user_id") == user_id:
                        print("✅ Login JWT token contains correct user_id")
                    else:
                        print("❌ Login JWT token has incorrect user_id")
                except Exception as e:
                    print(f"❌ Login JWT token validation failed: {e}")
                    
                # Test 3: Access protected endpoint with token
                print("\nTest 3: Access protected endpoint with token")
                
                me_url = f"{API_URL}/auth/me"
                print(f"GET {me_url}")
                print(f"Authorization: Bearer {login_token}")
                
                me_response = requests.get(me_url, headers={"Authorization": f"Bearer {login_token}"})
                print(f"Status Code: {me_response.status_code}")
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"Response: {json.dumps(me_data, indent=2)}")
                    
                    print("✅ Successfully accessed protected endpoint with token")
                    
                    # Verify user data in response
                    if me_data.get("id") == user_id:
                        print("✅ User ID in response matches registered user")
                    else:
                        print("❌ User ID in response does not match registered user")
                else:
                    print("❌ Failed to access protected endpoint with token")
                    print(f"Response: {me_response.text}")
            else:
                print("❌ Login failed")
                print(f"Response: {login_response.text}")
        else:
            print("❌ Registration failed")
            print(f"Response: {register_response.text}")
            
        # Test 4: Login with invalid credentials
        print("\nTest 4: Login with invalid credentials")
        
        invalid_login_data = {
            "email": test_user_email,
            "password": "wrongPassword123"
        }
        
        invalid_login_url = f"{API_URL}/auth/login"
        print(f"POST {invalid_login_url}")
        print(f"Request data: {json.dumps(invalid_login_data)}")
        
        invalid_login_response = requests.post(invalid_login_url, json=invalid_login_data)
        print(f"Status Code: {invalid_login_response.status_code}")
        
        if invalid_login_response.status_code == 401:
            print("✅ Invalid login correctly rejected")
        else:
            print("❌ Invalid login not properly handled")
            print(f"Response: {invalid_login_response.text}")
            
        # Print summary
        print("\nEMAIL/PASSWORD LOGIN SUMMARY:")
        
        if register_response.status_code == 200 and login_response.status_code == 200 and me_response.status_code == 200 and invalid_login_response.status_code == 401:
            print("✅ Email/password login is working correctly!")
            print("✅ Registration endpoint is functioning properly")
            print("✅ Login endpoint is functioning properly")
            print("✅ JWT tokens are generated correctly")
            print("✅ Protected endpoints can be accessed with valid token")
            print("✅ Invalid credentials are properly rejected")
            return True
        else:
            print("❌ Email/password login has issues")
            return False
            
    except Exception as e:
        print(f"❌ Error during email/password login testing: {e}")
        return False

def test_guest_login():
    """Test guest login functionality"""
    print("\n" + "="*80)
    print("TESTING GUEST LOGIN (CONTINUE AS GUEST)")
    print("="*80)
    
    try:
        # Test 1: Guest login
        print("\nTest 1: Guest login")
        
        guest_login_url = f"{API_URL}/auth/test-login"
        print(f"POST {guest_login_url}")
        
        guest_login_response = requests.post(guest_login_url)
        print(f"Status Code: {guest_login_response.status_code}")
        
        if guest_login_response.status_code == 200:
            guest_login_data = guest_login_response.json()
            print(f"Response: {json.dumps(guest_login_data, indent=2)}")
            
            guest_token = guest_login_data.get("access_token")
            guest_user = guest_login_data.get("user", {})
            guest_user_id = guest_user.get("id")
            
            print("✅ Guest login successful")
            print(f"Guest user ID: {guest_user_id}")
            print(f"JWT Token: {guest_token}")
            
            # Verify token structure
            try:
                decoded_token = jwt.decode(guest_token, JWT_SECRET, algorithms=["HS256"])
                print(f"✅ JWT token is valid and contains: {decoded_token}")
                if "sub" in decoded_token:
                    print("✅ JWT token contains required field (sub)")
                    print(f"Subject: {decoded_token['sub']}")
                else:
                    print("❌ JWT token is missing required fields")
            except Exception as e:
                print(f"❌ JWT token validation failed: {e}")
                
            # Test 2: Access protected endpoint with guest token
            print("\nTest 2: Access protected endpoint with guest token")
            
            me_url = f"{API_URL}/auth/me"
            print(f"GET {me_url}")
            print(f"Authorization: Bearer {guest_token}")
            
            me_response = requests.get(me_url, headers={"Authorization": f"Bearer {guest_token}"})
            print(f"Status Code: {me_response.status_code}")
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"Response: {json.dumps(me_data, indent=2)}")
                
                print("✅ Successfully accessed protected endpoint with guest token")
                
                # Verify user data in response
                if me_data.get("id") == guest_user_id:
                    print("✅ User ID in response matches guest user")
                else:
                    print("❌ User ID in response does not match guest user")
            else:
                print("❌ Failed to access protected endpoint with guest token")
                print(f"Response: {me_response.text}")
        else:
            print("❌ Guest login failed")
            print(f"Response: {guest_login_response.text}")
            
        # Print summary
        print("\nGUEST LOGIN SUMMARY:")
        
        if guest_login_response.status_code == 200 and me_response.status_code == 200:
            print("✅ Guest login is working correctly!")
            print("✅ Guest login endpoint is functioning properly")
            print("✅ JWT tokens are generated correctly")
            print("✅ Protected endpoints can be accessed with guest token")
            return True
        else:
            print("❌ Guest login has issues")
            return False
            
    except Exception as e:
        print(f"❌ Error during guest login testing: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("\n" + "="*80)
    print("TESTING AUTHENTICATION SYSTEM")
    print("="*80)
    
    # Test email/password login
    email_password_login_success = test_email_password_login()
    
    # Test guest login
    guest_login_success = test_guest_login()
    
    # Print final conclusion
    print("\n" + "="*80)
    print("AUTHENTICATION SYSTEM ASSESSMENT")
    print("="*80)
    
    all_tests_passed = email_password_login_success and guest_login_success
    
    if all_tests_passed:
        print("✅ Authentication system is working correctly")
        print("✅ Email/password login is functioning properly")
        print("✅ Guest login (Continue as Guest) is functioning properly")
        print("✅ JWT tokens are generated correctly with proper payload")
        print("✅ Protected endpoints can be accessed with valid tokens")
        print("✅ User profile data can be retrieved with /api/auth/me endpoint")
    else:
        print("❌ Authentication system has issues")
        
        if not email_password_login_success:
            print("❌ Email/password login has issues")
        
        if not guest_login_success:
            print("❌ Guest login has issues")
    
    print("="*80)
    
    return all_tests_passed

if __name__ == "__main__":
    main()