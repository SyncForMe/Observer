#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv
import io
import tempfile
import numpy as np
import time

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
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")

if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    print("Warning: OPENAI_API_KEY not set or using default value. Transcription will likely fail.")
else:
    print(f"Using OPENAI_API_KEY: {OPENAI_API_KEY[:4]}...{OPENAI_API_KEY[-4:]}")

def test_login():
    """Login with admin credentials to get auth token"""
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    url = f"{API_URL}/auth/login"
    print(f"Logging in with admin credentials: {url}")
    
    try:
        response = requests.post(url, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            auth_token = response_data.get("access_token")
            user_data = response_data.get("user", {})
            user_id = user_data.get("id")
            print(f"Login successful. User ID: {user_id}")
            print(f"JWT Token: {auth_token}")
            return auth_token
        else:
            print(f"Login failed: {response.text}")
            
            # Try test login as fallback
            print("Trying test login endpoint...")
            test_url = f"{API_URL}/auth/test-login"
            test_response = requests.post(test_url)
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                test_token = test_data.get("access_token")
                test_user = test_data.get("user", {})
                test_id = test_user.get("id")
                print(f"Test login successful. User ID: {test_id}")
                print(f"JWT Token: {test_token}")
                return test_token
            else:
                print(f"Test login failed: {test_response.text}")
                return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_content_type_validation(auth_token):
    """Test the content-type validation in the transcribe-scenario endpoint"""
    if not auth_token:
        print("Cannot test content-type validation without authentication")
        return False
    
    # Create a simple text file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"This is a test file")
        temp_file_path = temp_file.name
    
    # Test with different content-types
    content_types = [
        ('text/plain', 'test.txt'),
        ('application/json', 'test.json'),
        ('audio/wav', 'test.txt'),  # Incorrect content-type for a text file
        ('audio/mpeg', 'test.mp3'),  # Incorrect content-type for a text file
        ('video/mp4', 'test.mp4'),   # Incorrect content-type for a text file
    ]
    
    results = {}
    
    try:
        for content_type, filename in content_types:
            print(f"\nTesting with Content-Type: {content_type}, Filename: {filename}")
            
            # Prepare the request
            url = f"{API_URL}/speech/transcribe-scenario"
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            with open(temp_file_path, 'rb') as f:
                files = {'audio': (filename, f, content_type)}
                
                # Send the request
                response = requests.post(url, headers=headers, files=files)
                
                print(f"Status Code: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Response is not JSON: {response.text}")
                    response_data = {}
                
                # Store the result
                results[content_type] = {
                    'status_code': response.status_code,
                    'response': response_data
                }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    # Analyze the results
    print("\nContent-Type Validation Results:")
    
    for content_type, result in results.items():
        status_code = result['status_code']
        response = result['response']
        
        if content_type.startswith(('audio/', 'video/')) and status_code == 400:
            print(f"✅ {content_type}: Correctly rejected with 400 status code (file content doesn't match content-type)")
        elif not content_type.startswith(('audio/', 'video/')) and status_code == 400:
            print(f"✅ {content_type}: Correctly rejected with 400 status code (not audio/video content-type)")
        else:
            print(f"❌ {content_type}: Unexpected response - Status: {status_code}")
    
    # Check if all tests passed
    all_passed = all(result['status_code'] == 400 for result in results.values())
    
    if all_passed:
        print("\n✅ Content-type validation is working correctly")
        return True
    else:
        print("\n❌ Content-type validation has issues")
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("VOICE TRANSCRIPTION CONTENT-TYPE VALIDATION TEST")
    print("="*80)
    
    # Login to get auth token
    auth_token = test_login()
    
    # Run content-type validation test
    if auth_token:
        content_type_test = test_content_type_validation(auth_token)
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Authentication: {'✅ OK' if auth_token else '❌ Failed'}")
        print(f"Content-Type Validation: {'✅ Passed' if content_type_test else '❌ Failed'}")
        
        # Overall result
        if content_type_test:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    else:
        print("\n❌ Authentication failed, cannot run tests!")

if __name__ == "__main__":
    main()