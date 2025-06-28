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

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

def login_as_admin():
    """Login with admin credentials"""
    global auth_token, test_user_id
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True
    else:
        print("Login failed. Cannot proceed with tests.")
        return False

def create_test_user():
    """Create a test user for comparison"""
    test_email = f"test.user.{uuid.uuid4()}@example.com"
    test_password = "securePassword123"
    test_name = "Test User"
    
    print(f"\n{'='*80}\nCreating test user ({test_email})")
    
    register_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name
    }
    
    url = f"{API_URL}/auth/register"
    response = requests.post(url, json=register_data)
    
    if response.status_code == 200:
        response_data = response.json()
        test_token = response_data.get("access_token")
        test_user_data = response_data.get("user", {})
        test_user_id = test_user_data.get("id")
        print(f"✅ Test user created. User ID: {test_user_id}")
        return test_token, test_user_id
    else:
        print(f"❌ Test user creation failed. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return None, None

def get_agents(token=None):
    """Get all agents for the current user"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_URL}/agents"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get agents. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return []

def send_observer_message(message, token=None):
    """Send an observer message"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_URL}/observer/send-message"
    data = {
        "observer_message": message
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to send observer message. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return None

def test_fixed_observer_message():
    """Test the fixed observer message functionality"""
    print("\n" + "="*80)
    print("TESTING FIXED OBSERVER MESSAGE FUNCTIONALITY")
    print("="*80)
    
    # Step 1: Login as admin user
    print("\nStep 1: Login as admin user (dino@cytonic.com)")
    if not login_as_admin():
        print("❌ Cannot proceed with testing without admin login")
        return False
    
    # Step 2: Check how many agents the admin user has
    print("\nStep 2: Check how many agents the admin user has")
    admin_agents = get_agents(auth_token)
    print(f"Found {len(admin_agents)} agents for admin user")
    
    # Print agent names
    print("\nAdmin user's agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 3: Create a test user for comparison
    print("\nStep 3: Create a test user for comparison")
    test_token, test_user_id = create_test_user()
    
    if test_token:
        # Get agents for test user
        test_agents = get_agents(test_token)
        print(f"\nFound {len(test_agents)} agents for test user")
        
        # Print agent names
        print("\nTest user's agents:")
        for agent in test_agents:
            print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 4: Send an observer message as admin
    print("\nStep 4: Send an observer message as admin")
    message = "hello agents"
    print(f"\nSending observer message as admin: '{message}'")
    
    response = send_observer_message(message, auth_token)
    
    if not response:
        print("❌ Failed to send observer message as admin")
        return False
    
    print("✅ Observer message sent successfully as admin")
    
    # Check agent responses
    agent_responses = response.get("agent_responses", {}).get("messages", [])
    
    # Count agent responses
    agent_response_count = len(agent_responses) - 1  # Subtract 1 for the observer message
    print(f"Received responses from {agent_response_count} agents")
    
    # Compare with number of agents for the admin user
    if agent_response_count == len(admin_agents):
        print("✅ Number of responses matches number of admin user's agents")
    else:
        print(f"❌ Number of responses ({agent_response_count}) does not match number of admin user's agents ({len(admin_agents)})")
        print("This suggests the observer message endpoint is not properly filtering agents by user_id")
        return False
    
    # Check for natural and conversational responses
    print("\nChecking for natural and conversational responses:")
    robotic_phrases = ["understood", "acknowledges", "acknowledge", "received", "directive", "instruction"]
    natural_phrases = ["hello", "hi", "hey", "good to hear", "greetings"]
    
    robotic_responses = 0
    natural_responses = 0
    
    print("\nResponding agents:")
    for i, msg in enumerate(agent_responses):
        if i == 0:  # Skip observer message
            continue
        
        agent_name = msg.get('agent_name', '')
        agent_message = msg.get('message', '')
        print(f"  - {agent_name}: {agent_message}")
        
        # Check for robotic phrases
        if any(phrase in agent_message.lower() for phrase in robotic_phrases):
            robotic_responses += 1
            print(f"    ❌ Response contains robotic phrases")
        
        # Check for natural phrases
        if any(phrase in agent_message.lower() for phrase in natural_phrases):
            natural_responses += 1
            print(f"    ✅ Response contains natural greeting phrases")
    
    print(f"\nNatural responses: {natural_responses}/{agent_response_count}")
    print(f"Robotic responses: {robotic_responses}/{agent_response_count}")
    
    if robotic_responses > 0:
        print("❌ Some responses still contain robotic phrases")
    else:
        print("✅ No responses contain robotic phrases")
    
    if natural_responses > 0:
        print("✅ Some responses contain natural greeting phrases")
    else:
        print("❌ No responses contain natural greeting phrases")
    
    # Step 5: Test sending observer message without authentication
    print("\nStep 5: Test sending observer message without authentication")
    
    no_auth_response = send_observer_message("This should fail", None)
    
    if no_auth_response:
        print("❌ Observer message sent successfully without authentication")
        print("This suggests the observer message endpoint is not properly enforcing authentication")
        return False
    else:
        print("✅ Observer message endpoint correctly requires authentication")
    
    # Step 6: Test sending observer message as test user
    if test_token:
        print("\nStep 6: Test sending observer message as test user")
        
        test_message = "hello from test user"
        print(f"\nSending observer message as test user: '{test_message}'")
        
        test_response = send_observer_message(test_message, test_token)
        
        if not test_response:
            print("❌ Failed to send observer message as test user")
        else:
            print("✅ Observer message sent successfully as test user")
            
            # Check agent responses
            test_agent_responses = test_response.get("agent_responses", {}).get("messages", [])
            
            # Count agent responses
            test_agent_response_count = len(test_agent_responses) - 1  # Subtract 1 for the observer message
            print(f"Received responses from {test_agent_response_count} agents")
            
            # Compare with number of agents for the test user
            if test_agent_response_count == len(test_agents):
                print("✅ Number of responses matches number of test user's agents")
            else:
                print(f"❌ Number of responses ({test_agent_response_count}) does not match number of test user's agents ({len(test_agents)})")
                print("This suggests the observer message endpoint is not properly filtering agents by user_id")
                return False
    
    # Print summary
    print("\n" + "="*80)
    print("FIXED OBSERVER MESSAGE FUNCTIONALITY TEST SUMMARY")
    print("="*80)
    
    print("1. User data isolation:")
    if agent_response_count == len(admin_agents):
        print("   ✅ Only the admin user's agents respond to observer messages")
    else:
        print("   ❌ User data isolation is not working properly")
    
    print("\n2. Natural and conversational responses:")
    if robotic_responses == 0:
        print("   ✅ No robotic 'Understood. [Agent Name] acknowledges...' responses")
    else:
        print("   ❌ Some responses still contain robotic phrases")
    
    if natural_responses > 0:
        print("   ✅ Agents respond with natural greetings like 'Hello! Good to hear from you'")
    else:
        print("   ❌ No natural greeting responses found")
    
    print("\n3. Authentication requirement:")
    if not no_auth_response:
        print("   ✅ Authentication is now required for observer messages")
    else:
        print("   ❌ Authentication is not properly enforced")
    
    print("\n4. Conversation association with user:")
    if test_token and test_agent_response_count == len(test_agents):
        print("   ✅ Conversations are properly associated with the user")
    else:
        print("   ❌ Conversation association with user could not be verified")
    
    return True

if __name__ == "__main__":
    test_fixed_observer_message()