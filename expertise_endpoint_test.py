#!/usr/bin/env python3
import requests
import json
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

def test_login():
    """Login with test endpoint to get auth token"""
    print("\n=== Testing Login ===")
    
    # Try the test login endpoint
    test_login_url = f"{API_URL}/auth/test-login"
    print(f"POST {test_login_url}")
    
    try:
        response = requests.post(test_login_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_data = data.get("user", {})
            user_id = user_data.get("id")
            print(f"Login successful. Token: {token[:10]}...")
            print(f"User ID: {user_id}")
            return token
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def create_test_agent(auth_token):
    """Create a test agent for update testing"""
    print("\n=== Creating Test Agent ===")
    
    # Create agent data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 8
        },
        "goal": "Test the expertise field update",
        "expertise": "Initial Expertise Value",
        "background": "Created for testing expertise update",
        "memory_summary": "",
        "avatar_prompt": "A robot testing software"
    }
    
    url = f"{API_URL}/agents"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"POST {url}")
    print(f"Headers: {headers}")
    print(f"Request data: {json.dumps(agent_data, indent=2)}")
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Store the created agent ID for later tests
            agent_id = response_data.get("id")
            
            if agent_id:
                print(f"✅ Successfully created agent with ID: {agent_id}")
                return agent_id, response_data
            else:
                print("❌ No agent ID in response")
                return None, None
        else:
            print(f"❌ Request failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return None, None

def test_update_expertise(auth_token, agent_id):
    """Test updating the expertise field using the new endpoint"""
    print("\n=== Testing Expertise Field Update with New Endpoint ===")
    
    # Prepare update data with only expertise field
    update_data = {
        "expertise": f"Updated Expertise {uuid.uuid4().hex[:8]}"
    }
    
    url = f"{API_URL}/agents/{agent_id}/expertise"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"PUT {url}")
    print(f"Headers: {headers}")
    print(f"Request data: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Verify the expertise field was updated correctly
            if response_data.get("expertise") == update_data.get("expertise"):
                print(f"✅ Expertise field updated successfully")
                print(f"Expected: {update_data.get('expertise')}")
                print(f"Actual: {response_data.get('expertise')}")
                return True, response_data
            else:
                print(f"❌ Expertise field not updated correctly")
                print(f"Expected: {update_data.get('expertise')}")
                print(f"Actual: {response_data.get('expertise')}")
                return False, response_data
        else:
            print(f"❌ Request failed: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_invalid_agent_id(auth_token):
    """Test PUT with invalid agent ID"""
    print("\n=== Testing Invalid Agent ID Handling ===")
    
    # Generate a random invalid ID
    invalid_id = str(uuid.uuid4())
    
    # Test PUT with invalid ID
    print("\n--- Testing PUT /agents/{agent_id}/expertise with Invalid ID ---")
    update_data = {
        "expertise": "This update should fail"
    }
    
    url = f"{API_URL}/agents/{invalid_id}/expertise"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"PUT {url}")
    print(f"Headers: {headers}")
    print(f"Request data: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 404:
            print(f"✅ Correctly returned 404 for invalid agent ID")
            return True
        else:
            print(f"❌ Expected 404, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def cleanup(auth_token, agent_id):
    """Delete the test agent"""
    print("\n=== Cleaning Up ===")
    
    url = f"{API_URL}/agents/{agent_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"DELETE {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.delete(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Successfully deleted test agent")
            return True
        else:
            print(f"❌ Failed to delete test agent: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def main():
    """Run the expertise update test"""
    print("=== TESTING AGENT EXPERTISE UPDATE WITH NEW ENDPOINT ===")
    
    # Login to get auth token
    auth_token = test_login()
    if not auth_token:
        print("❌ Login failed. Cannot proceed with tests.")
        return
    
    # Create a test agent
    agent_id, agent_data = create_test_agent(auth_token)
    if not agent_id:
        print("❌ Failed to create test agent. Cannot proceed with tests.")
        return
    
    # Test updating the expertise field
    expertise_update_success, _ = test_update_expertise(auth_token, agent_id)
    
    # Test invalid agent ID handling
    invalid_id_success = test_invalid_agent_id(auth_token)
    
    # Clean up
    cleanup(auth_token, agent_id)
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    print(f"Expertise Field Update: {'✅ PASSED' if expertise_update_success else '❌ FAILED'}")
    print(f"Invalid Agent ID Handling: {'✅ PASSED' if invalid_id_success else '❌ FAILED'}")
    
    if expertise_update_success and invalid_id_success:
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")

if __name__ == "__main__":
    main()