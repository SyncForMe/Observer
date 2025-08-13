#!/usr/bin/env python3
"""
FOCUSED CONVERSATION ARCHIVE SYSTEM TESTING
Testing the key features of the enhanced conversation archive system:

1. Fresh Start endpoint preservation
2. New conversation reports/documents endpoints
3. Error handling and security
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"Using API URL: {API_URL}")

# Global variables
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, auth=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\n{test_name} ({method} {endpoint})")
    
    headers = {}
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)[:500]}...")
        except:
            print(f"Response: {response.text[:200]}...")
            response_data = {}
        
        success = response.status_code == expected_status
        print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return success, response_data
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None

def setup_auth():
    """Setup authentication"""
    global auth_token, test_user_id
    
    print("\n" + "="*60)
    print("SETUP: Authentication")
    
    # Register new user
    register_data = {
        "email": f"archive_test_{int(time.time())}@test.com",
        "password": "testpass123",
        "name": "Archive Test User"
    }
    
    success, response = run_test(
        "Register Test User",
        "/auth/register",
        method="POST",
        data=register_data
    )
    
    if success and response:
        auth_token = response.get("access_token")
        user_data = response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Auth setup successful. User ID: {test_user_id}")
        return True
    
    print("❌ Auth setup failed")
    return False

def test_fresh_start_endpoint():
    """Test the Fresh Start endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Fresh Start Endpoint")
    
    # Create some test agents first
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist",
        "goal": "Test goal",
        "expertise": "Testing",
        "background": "Test background",
        "personality": {
            "extroversion": 5,
            "optimism": 5,
            "curiosity": 5,
            "cooperativeness": 5,
            "energy": 5
        }
    }
    
    # Create agent
    agent_success, agent_response = run_test(
        "Create Test Agent",
        "/agents",
        method="POST",
        data=agent_data,
        auth=True
    )
    
    if not agent_success:
        print("❌ Failed to create test agent")
        return False
    
    agent_id = agent_response.get("id")
    print(f"Created agent: {agent_id}")
    
    # Start simulation
    start_success, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True
    )
    
    if not start_success:
        print("❌ Failed to start simulation")
        return False
    
    # Get initial agent count
    agents_before_success, agents_before_response = run_test(
        "Count Agents Before Fresh Start",
        "/agents",
        method="GET",
        auth=True
    )
    
    initial_agent_count = len(agents_before_response) if agents_before_response else 0
    print(f"Agents before Fresh Start: {initial_agent_count}")
    
    # Perform Fresh Start
    fresh_start_success, fresh_start_response = run_test(
        "Fresh Start (Reset Simulation)",
        "/simulation/reset",
        method="POST",
        auth=True
    )
    
    if not fresh_start_success:
        print("❌ Fresh Start failed")
        return False
    
    # Verify response structure
    if fresh_start_response:
        success = fresh_start_response.get("success")
        cleared = fresh_start_response.get("cleared_collections", [])
        preserved = fresh_start_response.get("preserved_collections", [])
        
        print(f"Fresh Start success: {success}")
        print(f"Cleared: {cleared}")
        print(f"Preserved: {preserved}")
        
        # Check expected collections
        expected_cleared = ["simulation_state", "relationships", "summaries", "agents", "observer_messages"]
        expected_preserved = ["conversations", "documents", "reports"]
        
        if set(cleared) == set(expected_cleared) and set(preserved) == set(expected_preserved):
            print("✅ Correct collections cleared and preserved")
        else:
            print("❌ Incorrect collections in response")
            return False
    
    # Verify agents were cleared
    agents_after_success, agents_after_response = run_test(
        "Count Agents After Fresh Start",
        "/agents",
        method="GET",
        auth=True
    )
    
    final_agent_count = len(agents_after_response) if agents_after_response else 0
    print(f"Agents after Fresh Start: {final_agent_count}")
    
    if final_agent_count == 0:
        print("✅ Agents properly cleared by Fresh Start")
        return True
    else:
        print("❌ Agents not cleared by Fresh Start")
        return False

def test_conversation_endpoints():
    """Test the new conversation endpoints"""
    print("\n" + "="*60)
    print("TEST 2: Conversation Endpoints")
    
    # Test with a fake conversation ID
    fake_conversation_id = str(uuid.uuid4())
    
    # Test conversation reports endpoint
    reports_success, reports_response = run_test(
        "Get Conversation Reports (Fake ID)",
        f"/conversations/{fake_conversation_id}/reports",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if not reports_success:
        print("❌ Conversation reports endpoint failed")
        return False
    
    print("✅ Conversation reports endpoint exists and handles invalid IDs")
    
    # Test conversation documents endpoint
    docs_success, docs_response = run_test(
        "Get Conversation Documents (Fake ID)",
        f"/conversations/{fake_conversation_id}/documents",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if not docs_success:
        print("❌ Conversation documents endpoint failed")
        return False
    
    print("✅ Conversation documents endpoint exists and handles invalid IDs")
    
    return True

def test_authorization():
    """Test authorization on new endpoints"""
    print("\n" + "="*60)
    print("TEST 3: Authorization")
    
    fake_conversation_id = str(uuid.uuid4())
    
    # Test without auth token
    reports_unauth_success, reports_unauth_response = run_test(
        "Get Conversation Reports (No Auth)",
        f"/conversations/{fake_conversation_id}/reports",
        method="GET",
        auth=False,
        expected_status=403  # Updated to expect 403
    )
    
    if not reports_unauth_success:
        print("❌ Reports endpoint authorization failed")
        return False
    
    docs_unauth_success, docs_unauth_response = run_test(
        "Get Conversation Documents (No Auth)",
        f"/conversations/{fake_conversation_id}/documents",
        method="GET",
        auth=False,
        expected_status=403  # Updated to expect 403
    )
    
    if not docs_unauth_success:
        print("❌ Documents endpoint authorization failed")
        return False
    
    print("✅ Both endpoints properly require authorization")
    return True

def test_error_handling():
    """Test error handling"""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    
    # Test with malformed conversation IDs
    malformed_ids = ["invalid", "12345", "", "not-a-uuid"]
    
    for malformed_id in malformed_ids:
        print(f"\n--- Testing malformed ID: '{malformed_id}' ---")
        
        reports_success, _ = run_test(
            f"Reports with malformed ID: '{malformed_id}'",
            f"/conversations/{malformed_id}/reports",
            method="GET",
            auth=True,
            expected_status=404
        )
        
        docs_success, _ = run_test(
            f"Documents with malformed ID: '{malformed_id}'",
            f"/conversations/{malformed_id}/documents",
            method="GET",
            auth=True,
            expected_status=404
        )
        
        if not (reports_success and docs_success):
            print(f"❌ Error handling failed for ID: '{malformed_id}'")
            return False
    
    print("✅ Error handling works correctly")
    return True

def main():
    """Main test execution"""
    print("FOCUSED CONVERSATION ARCHIVE SYSTEM TESTING")
    print("="*60)
    
    # Setup
    if not setup_auth():
        return False
    
    # Run tests
    tests = [
        ("Fresh Start Endpoint", test_fresh_start_endpoint),
        ("Conversation Endpoints", test_conversation_endpoints),
        ("Authorization", test_authorization),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"RUNNING: {test_name}")
            
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)