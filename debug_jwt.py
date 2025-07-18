#!/usr/bin/env python3
"""
Debug JWT Token Issue
"""
import requests
import json
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

print(f"JWT_SECRET from env: {JWT_SECRET}")

# Test authentication
API_URL = "http://localhost:8001/api"

print(f"\n🔐 Testing authentication...")
response = requests.post(f"{API_URL}/auth/test-login", timeout=10)

if response.status_code == 200:
    data = response.json()
    token = data["access_token"]
    print(f"✅ Token received: {token[:50]}...")
    
    # Decode token to see what's inside
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"✅ Token decoded successfully: {decoded}")
    except Exception as e:
        print(f"❌ Token decode failed: {e}")
        
        # Try with the default secret
        try:
            decoded = jwt.decode(token, "your_super_secure_jwt_secret_key_here", algorithms=["HS256"])
            print(f"✅ Token decoded with default secret: {decoded}")
            print(f"🚨 Backend is still using default JWT_SECRET!")
        except Exception as e2:
            print(f"❌ Token decode with default secret also failed: {e2}")
    
    # Test using the token
    headers = {"Authorization": f"Bearer {token}"}
    reset_response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
    print(f"\n🔄 Reset response: {reset_response.status_code}")
    if reset_response.status_code != 200:
        print(f"   Error: {reset_response.text}")
    else:
        print(f"   ✅ Reset successful")
        
else:
    print(f"❌ Auth failed: {response.status_code} - {response.text}")