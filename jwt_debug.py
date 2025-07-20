#!/usr/bin/env python3
"""
Test JWT token generation and verification to identify the mismatch issue
"""

import os
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests

# Load environment
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"

print("🔍 JWT SECRET DEBUGGING")
print("="*50)
print(f"JWT_SECRET from env: {JWT_SECRET}")
print(f"JWT_ALGORITHM: {JWT_ALGORITHM}")

# Test 1: Create a token the same way the backend does
print("\n1. 🔧 Creating token like backend...")
user_data = {
    "sub": "test-user-123",
    "user_id": "test-user-123", 
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=24)
}

try:
    test_token = jwt.encode(user_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(f"✅ Token created: {test_token[:30]}...")
except Exception as e:
    print(f"❌ Token creation failed: {e}")
    exit(1)

# Test 2: Verify the token we just created
print("\n2. 🔍 Verifying our token...")
try:
    decoded = jwt.decode(test_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    print(f"✅ Token verified successfully")
    print(f"Decoded: {decoded}")
except Exception as e:
    print(f"❌ Token verification failed: {e}")

# Test 3: Get a token from the backend and try to verify it
print("\n3. 🌐 Testing with backend token...")
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

try:
    # Get token from backend
    login_response = requests.post(f"{API_URL}/auth/test-login")
    if login_response.status_code == 200:
        backend_token = login_response.json().get("access_token")
        print(f"✅ Got backend token: {backend_token[:30]}...")
        
        # Try to verify this token with our secret
        try:
            backend_decoded = jwt.decode(backend_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            print(f"✅ Backend token verified with env secret!")
            print(f"Backend token payload: {backend_decoded}")
        except jwt.InvalidSignatureError:
            print(f"❌ SIGNATURE MISMATCH: Backend token signed with different secret!")
            
            # Try decoding without verification to see the payload
            try:
                unverified = jwt.decode(backend_token, options={"verify_signature": False})
                print(f"Unverified backend payload: {unverified}")
            except:
                pass
                
        except Exception as verify_error:
            print(f"❌ Backend token verification error: {verify_error}")
    else:
        print(f"❌ Failed to get backend token: {login_response.status_code}")
        
except Exception as e:
    print(f"❌ Backend request failed: {e}")

print("\n" + "="*50)
print("🎯 CONCLUSION:")
print("If you see 'SIGNATURE MISMATCH' above, the backend is using")
print("a different JWT secret than what's in the .env file!")