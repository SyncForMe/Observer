#!/usr/bin/env python3
"""
JWT Token Debug Test - Check token generation and validation
"""

import requests
import json
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"
JWT_SECRET = os.environ.get('JWT_SECRET')

print(f"🔧 API URL: {API_URL}")
print(f"🔑 JWT Secret: {JWT_SECRET[:10]}..." if JWT_SECRET else "❌ No JWT Secret found")

def test_token_generation_and_validation():
    """Test JWT token generation and validation"""
    
    # Step 1: Get token from test-login endpoint
    print("\n1. Getting token from /auth/test-login...")
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code} - {auth_response.text}")
        return
    
    auth_data = auth_response.json()
    token = auth_data["access_token"]
    print(f"✅ Token received: {token[:50]}...")
    
    # Step 2: Decode the token to see its contents
    print("\n2. Decoding token...")
    try:
        # Decode without verification first to see contents
        decoded_unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"Token payload: {json.dumps(decoded_unverified, indent=2, default=str)}")
        
        # Now decode with verification using the JWT secret
        if JWT_SECRET:
            decoded_verified = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ Token verification successful")
        else:
            print("❌ Cannot verify token - no JWT secret")
            
    except Exception as e:
        print(f"❌ Token decode error: {e}")
        return
    
    # Step 3: Test the token with a protected endpoint
    print("\n3. Testing token with protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with /auth/me endpoint
    me_response = requests.get(f"{API_URL}/auth/me", headers=headers)
    print(f"/auth/me status: {me_response.status_code}")
    if me_response.status_code == 200:
        print(f"✅ /auth/me successful")
    else:
        print(f"❌ /auth/me failed: {me_response.text}")
    
    # Test with /simulation/state endpoint
    state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    print(f"/simulation/state status: {state_response.status_code}")
    if state_response.status_code == 200:
        print(f"✅ /simulation/state successful")
    else:
        print(f"❌ /simulation/state failed: {state_response.text}")
    
    # Step 4: Test observer endpoint specifically
    print("\n4. Testing observer endpoint...")
    
    # First create an agent
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist", 
        "goal": "Test goal",
        "expertise": "Testing"
    }
    agent_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    print(f"Agent creation status: {agent_response.status_code}")
    
    if agent_response.status_code == 200:
        # Start simulation
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        print(f"Simulation start status: {start_response.status_code}")
        
        if start_response.status_code == 200:
            # Test observer message
            observer_data = {"observer_message": "Hello test"}
            observer_response = requests.post(f"{API_URL}/observer/send-message", json=observer_data, headers=headers)
            print(f"Observer message status: {observer_response.status_code}")
            
            if observer_response.status_code == 200:
                print(f"✅ Observer message successful!")
            else:
                print(f"❌ Observer message failed: {observer_response.text}")
        else:
            print(f"❌ Cannot test observer - simulation start failed")
    else:
        print(f"❌ Cannot test observer - agent creation failed")

if __name__ == "__main__":
    test_token_generation_and_validation()