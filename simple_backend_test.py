#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

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

# Test results
passed = 0
failed = 0

def test_endpoint(name, url, method="GET", data=None, headers=None, expected_status=200):
    """Test an endpoint and print the result"""
    global passed, failed
    
    print(f"\n=== Testing {name} ===")
    print(f"URL: {url}")
    print(f"Method: {method}")
    
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            failed += 1
            return None
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response: {response.text}")
            response_json = None
        
        if response.status_code == expected_status:
            print("✅ Test passed")
            passed += 1
            return response_json
        else:
            print(f"❌ Test failed - Expected status {expected_status}, got {response.status_code}")
            failed += 1
            return response_json
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        failed += 1
        return None

def main():
    # Test 1: Login
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_response = test_endpoint(
        "Login",
        f"{API_URL}/auth/login",
        method="POST",
        data=login_data
    )
    
    if not login_response:
        print("❌ Login failed, cannot continue tests")
        return
    
    token = login_response.get("access_token")
    if not token:
        print("❌ No token in login response, cannot continue tests")
        return
    
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # Test 2: Get user profile
    test_endpoint(
        "Get User Profile",
        f"{API_URL}/auth/me",
        headers=auth_headers
    )
    
    # Test 3: Get agents
    agents_response = test_endpoint(
        "Get Agents",
        f"{API_URL}/agents",
        headers=auth_headers
    )
    
    # Test 4: Create agent
    agent_data = {
        "name": f"Test Agent {uuid.uuid4()}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 8
        },
        "goal": "Test the API",
        "expertise": "API Testing",
        "background": "Created for testing"
    }
    
    created_agent = test_endpoint(
        "Create Agent",
        f"{API_URL}/agents",
        method="POST",
        data=agent_data,
        headers=auth_headers
    )
    
    if created_agent and "id" in created_agent:
        agent_id = created_agent["id"]
        
        # Test 5: Update agent
        update_data = {
            "name": f"Updated {agent_data['name']}",
            "archetype": "scientist",
            "personality": {
                "extroversion": 5,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 6,
                "energy": 8
            },
            "goal": "Updated goal",
            "expertise": "Updated expertise",
            "background": "Updated background"
        }
        
        test_endpoint(
            "Update Agent",
            f"{API_URL}/agents/{agent_id}",
            method="PUT",
            data=update_data,
            headers=auth_headers
        )
        
        # Test 6: Delete agent
        test_endpoint(
            "Delete Agent",
            f"{API_URL}/agents/{agent_id}",
            method="DELETE",
            headers=auth_headers
        )
    
    # Test 7: Get simulation state
    test_endpoint(
        "Get Simulation State",
        f"{API_URL}/simulation/state",
        headers=auth_headers
    )
    
    # Test 8: Start simulation
    test_endpoint(
        "Start Simulation",
        f"{API_URL}/simulation/start",
        method="POST",
        headers=auth_headers
    )
    
    # Test 9: Pause simulation
    test_endpoint(
        "Pause Simulation",
        f"{API_URL}/simulation/pause",
        method="POST",
        headers=auth_headers
    )
    
    # Test 10: Get random scenario
    test_endpoint(
        "Get Random Scenario",
        f"{API_URL}/simulation/random-scenario",
        headers=auth_headers
    )
    
    # Test 11: Set scenario
    scenario_data = {
        "scenario": "Test scenario for API testing",
        "scenario_name": "API Test Scenario"
    }
    
    test_endpoint(
        "Set Scenario",
        f"{API_URL}/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        headers=auth_headers
    )
    
    # Test 12: Get conversations
    test_endpoint(
        "Get Conversations",
        f"{API_URL}/conversations",
        headers=auth_headers
    )
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} tests failed")

if __name__ == "__main__":
    main()