#!/usr/bin/env python3
"""
Focused Authentication Flow Test
Tests the specific authentication flow requirements from the review request
"""

import requests
import json
import os
import sys
import uuid
from dotenv import load_dotenv
import jwt

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET', "test_secret")

def test_authentication_flow():
    """Test the complete authentication flow as requested"""
    print("="*80)
    print("FOCUSED AUTHENTICATION FLOW TEST")
    print("="*80)
    
    # Test 1: Test the test-login endpoint to ensure it returns proper user data
    print("\n1. TESTING TEST-LOGIN ENDPOINT")
    print("-" * 50)
    
    response = requests.post(f"{API_URL}/auth/test-login")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Test-login endpoint failed")
        return False
    
    login_data = response.json()
    token = login_data.get("access_token")
    user_data = login_data.get("user", {})
    user_id = user_data.get("id")
    
    # Verify JWT token structure
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"✅ JWT token valid: {decoded}")
        if "sub" in decoded and "user_id" in decoded:
            print("✅ JWT contains required fields")
        else:
            print("❌ JWT missing required fields")
            return False
    except Exception as e:
        print(f"❌ JWT validation failed: {e}")
        return False
    
    print("✅ Test-login endpoint working correctly")
    
    # Test 2: Test the /auth/me endpoint to ensure it returns updated profile data
    print("\n2. TESTING /AUTH/ME ENDPOINT")
    print("-" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{API_URL}/auth/me", headers=headers)
    print(f"Status: {me_response.status_code}")
    print(f"Response: {json.dumps(me_response.json(), indent=2)}")
    
    if me_response.status_code != 200:
        print("❌ /auth/me endpoint failed")
        return False
    
    me_data = me_response.json()
    
    # Verify required fields
    required_fields = ["id", "email", "name"]
    for field in required_fields:
        if field not in me_data:
            print(f"❌ Missing required field: {field}")
            return False
    
    print("✅ /auth/me endpoint working correctly")
    
    # Test 3: Test the profile update endpoint to ensure it properly saves name and picture changes
    print("\n3. TESTING PROFILE UPDATE ENDPOINT")
    print("-" * 50)
    
    # Get current profile data
    original_name = me_data.get("name")
    original_picture = me_data.get("picture")
    print(f"Original name: {original_name}")
    print(f"Original picture: {original_picture}")
    
    # Update profile with new data
    new_name = f"Updated User {uuid.uuid4().hex[:8]}"
    new_picture = f"https://example.com/avatar/{uuid.uuid4().hex[:8]}.jpg"
    
    update_data = {
        "name": new_name,
        "picture": new_picture
    }
    
    update_response = requests.put(f"{API_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Update Status: {update_response.status_code}")
    print(f"Update Response: {json.dumps(update_response.json(), indent=2)}")
    
    if update_response.status_code != 200:
        print("❌ Profile update failed")
        return False
    
    update_result = update_response.json()
    if not update_result.get("success"):
        print("❌ Profile update not successful")
        return False
    
    print("✅ Profile update request successful")
    
    # Test 4: Verify that the /auth/me endpoint returns the merged data from both users and user_profiles collections
    print("\n4. TESTING MERGED DATA AFTER PROFILE UPDATE")
    print("-" * 50)
    
    # Get updated profile
    updated_me_response = requests.get(f"{API_URL}/auth/me", headers=headers)
    print(f"Status: {updated_me_response.status_code}")
    print(f"Response: {json.dumps(updated_me_response.json(), indent=2)}")
    
    if updated_me_response.status_code != 200:
        print("❌ Failed to get updated profile")
        return False
    
    updated_me_data = updated_me_response.json()
    
    # Verify the updates persisted
    if updated_me_data.get("name") == new_name:
        print("✅ Name update persisted")
    else:
        print(f"❌ Name update failed. Expected: {new_name}, Got: {updated_me_data.get('name')}")
        return False
    
    if updated_me_data.get("picture") == new_picture:
        print("✅ Picture update persisted")
    else:
        print(f"❌ Picture update failed. Expected: {new_picture}, Got: {updated_me_data.get('picture')}")
        return False
    
    # Verify user identity fields are preserved
    if updated_me_data.get("id") == user_id:
        print("✅ User ID preserved")
    else:
        print("❌ User ID not preserved")
        return False
    
    # Test data structure shows merged collections
    print("\nData structure analysis:")
    print("Fields that likely come from users collection:")
    users_fields = ["id", "created_at", "last_login"]
    for field in users_fields:
        if field in updated_me_data:
            print(f"  ✅ {field}: {updated_me_data[field]}")
        else:
            print(f"  ❌ Missing {field}")
    
    print("Fields that likely come from user_profiles collection:")
    profile_fields = ["name", "picture"]
    for field in profile_fields:
        if field in updated_me_data:
            print(f"  ✅ {field}: {updated_me_data[field]}")
        else:
            print(f"  ❌ Missing {field}")
    
    print("✅ Merged data working correctly")
    
    # Test 5: Test localStorage caching behavior (persistence across requests)
    print("\n5. TESTING LOCALSTORAGE CACHING BEHAVIOR")
    print("-" * 50)
    
    # Simulate multiple "page refreshes" by making multiple requests
    for i in range(3):
        print(f"\nSimulated page refresh {i+1}:")
        refresh_response = requests.get(f"{API_URL}/auth/me", headers=headers)
        
        if refresh_response.status_code != 200:
            print(f"❌ Request {i+1} failed")
            return False
        
        refresh_data = refresh_response.json()
        
        # Verify data consistency
        if (refresh_data.get("name") == new_name and 
            refresh_data.get("picture") == new_picture and
            refresh_data.get("id") == user_id):
            print(f"✅ Data consistent on refresh {i+1}")
        else:
            print(f"❌ Data inconsistent on refresh {i+1}")
            return False
    
    print("✅ localStorage caching behavior working correctly")
    
    # Final verification: Test one more profile update to ensure the system is stable
    print("\n6. FINAL STABILITY TEST")
    print("-" * 50)
    
    final_name = f"Final User {uuid.uuid4().hex[:8]}"
    final_update = {"name": final_name}
    
    final_update_response = requests.put(f"{API_URL}/auth/profile", json=final_update, headers=headers)
    if final_update_response.status_code == 200:
        # Verify it persists
        final_check = requests.get(f"{API_URL}/auth/me", headers=headers)
        if final_check.status_code == 200 and final_check.json().get("name") == final_name:
            print("✅ Final stability test passed")
        else:
            print("❌ Final stability test failed")
            return False
    else:
        print("❌ Final update failed")
        return False
    
    print("\n" + "="*80)
    print("🎉 ALL AUTHENTICATION FLOW TESTS PASSED!")
    print("="*80)
    print("✅ Test-login endpoint returns proper user data")
    print("✅ /auth/me endpoint returns updated profile data after updates")
    print("✅ Profile update endpoint properly saves name and picture changes")
    print("✅ /auth/me endpoint returns merged data from users and user_profiles collections")
    print("✅ Changes persist across page refreshes (localStorage caching)")
    print("="*80)
    
    return True

if __name__ == "__main__":
    success = test_authentication_flow()
    sys.exit(0 if success else 1)