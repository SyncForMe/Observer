#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv
import uuid
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

# Global variables for auth testing
auth_token = None
test_user_id = None

def login_as_admin():
    """Login with admin credentials"""
    global auth_token, test_user_id
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    print(f"\n{'='*80}\nLogging in as admin user (dino@cytonic.com)")
    
    url = f"{API_URL}/auth/login"
    response = requests.post(url, json=login_data)
    
    if response.status_code == 200:
        response_data = response.json()
        auth_token = response_data.get("access_token")
        user_data = response_data.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Login successful. User ID: {test_user_id}")
        return True
    else:
        print(f"❌ Login failed. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
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

def main():
    """Main test function"""
    print(f"\n{'='*80}")
    print("OBSERVER MESSAGE ENDPOINT TESTING")
    print(f"{'='*80}")
    
    # Login as admin
    if not login_as_admin():
        print("❌ Cannot proceed with testing without admin login")
        sys.exit(1)
    
    # Get agents for admin user
    admin_agents = get_agents(auth_token)
    print(f"\nFound {len(admin_agents)} agents for admin user")
    
    # Create a test user for comparison
    test_token, test_user_id = create_test_user()
    
    if test_token:
        # Get agents for test user
        test_agents = get_agents(test_token)
        print(f"\nFound {len(test_agents)} agents for test user")
        
        # Test observer message with admin auth
        print(f"\n{'='*80}\nTESTING OBSERVER MESSAGE WITH ADMIN AUTH")
        
        # Send observer message
        message = "This is a test message from the admin observer. Please acknowledge."
        print(f"\nSending observer message as admin: '{message}'")
        
        response = send_observer_message(message, auth_token)
        
        if response:
            print("✅ Observer message sent successfully as admin")
            
            # Check agent responses
            agent_responses = response.get("agent_responses", {}).get("messages", [])
            
            # Count agent responses
            agent_response_count = len(agent_responses) - 1  # Subtract 1 for the observer message
            print(f"Received responses from {agent_response_count} agents")
            
            # Print agent names
            print("\nResponding agents:")
            for i, msg in enumerate(agent_responses):
                if i == 0:  # Skip observer message
                    continue
                print(f"  - {msg.get('agent_name')}")
            
            # Compare with number of agents for the admin user
            if agent_response_count == len(admin_agents):
                print("✅ Number of responses matches number of admin user's agents")
            else:
                print(f"❌ Number of responses ({agent_response_count}) does not match number of admin user's agents ({len(admin_agents)})")
                print("This suggests the observer message endpoint is not properly filtering agents by user_id")
        
        # Test observer message with test user auth
        print(f"\n{'='*80}\nTESTING OBSERVER MESSAGE WITH TEST USER AUTH")
        
        # Send observer message
        message = "This is a test message from the test user observer. Please acknowledge."
        print(f"\nSending observer message as test user: '{message}'")
        
        response = send_observer_message(message, test_token)
        
        if response:
            print("✅ Observer message sent successfully as test user")
            
            # Check agent responses
            agent_responses = response.get("agent_responses", {}).get("messages", [])
            
            # Count agent responses
            agent_response_count = len(agent_responses) - 1  # Subtract 1 for the observer message
            print(f"Received responses from {agent_response_count} agents")
            
            # Print agent names
            print("\nResponding agents:")
            for i, msg in enumerate(agent_responses):
                if i == 0:  # Skip observer message
                    continue
                print(f"  - {msg.get('agent_name')}")
            
            # Compare with number of agents for the test user
            if agent_response_count == len(test_agents):
                print("✅ Number of responses matches number of test user's agents")
            else:
                print(f"❌ Number of responses ({agent_response_count}) does not match number of test user's agents ({len(test_agents)})")
                print("This suggests the observer message endpoint is not properly filtering agents by user_id")
    
    # Print summary
    print(f"\n{'='*80}\nSUMMARY")
    print(f"{'='*80}")
    
    print("\nIssues Found:")
    print("1. The observer message endpoint is not properly filtering agents by user_id")
    print("   - It's getting all agents from the database instead of just the current user's agents")
    print("   - This is why so many agents are responding to observer messages")
    print("2. The observer message endpoint does not require authentication")
    print("   - This is a security issue that allows anyone to send observer messages")
    
    print("\nRecommendations:")
    print("1. Fix the observer message endpoint to filter agents by user_id:")
    print("   - Change line 298 from:")
    print("     agents = await db.agents.find().to_list(100)")
    print("   - To:")
    print("     agents = await db.agents.find({\"user_id\": current_user.id}).to_list(100)")
    print("2. Add authentication requirement to the observer message endpoint:")
    print("   - Change line 289 from:")
    print("     @api_router.post(\"/observer/send-message\")")
    print("     async def send_observer_message(input_data: ObserverInput):")
    print("   - To:")
    print("     @api_router.post(\"/observer/send-message\")")
    print("     async def send_observer_message(input_data: ObserverInput, current_user: User = Depends(get_current_user)):")
    print("3. Fix the get_observer_messages endpoint to filter by user_id")
    print("4. Add user_id to the ConversationRound when creating observer conversations")

if __name__ == "__main__":
    main()