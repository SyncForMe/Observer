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

def get_observer_messages(token=None):
    """Get all observer messages"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_URL}/observer/messages"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get observer messages. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return []

def analyze_agents(agents):
    """Analyze the agents data"""
    print(f"\n{'='*80}\nANALYZING {len(agents)} AGENTS")
    
    # Count agents by archetype
    archetype_counts = {}
    for agent in agents:
        archetype = agent.get("archetype", "unknown")
        if archetype in archetype_counts:
            archetype_counts[archetype] += 1
        else:
            archetype_counts[archetype] = 1
    
    print("\nAgent count by archetype:")
    for archetype, count in archetype_counts.items():
        print(f"  - {archetype}: {count}")
    
    # Check user_id field
    user_id_present = 0
    user_id_missing = 0
    user_ids = set()
    
    for agent in agents:
        user_id = agent.get("user_id", "")
        if user_id:
            user_id_present += 1
            user_ids.add(user_id)
        else:
            user_id_missing += 1
    
    print(f"\nUser ID analysis:")
    print(f"  - Agents with user_id: {user_id_present}")
    print(f"  - Agents without user_id: {user_id_missing}")
    print(f"  - Unique user_ids: {len(user_ids)}")
    
    if user_ids:
        print("\nUnique user_ids found:")
        for uid in user_ids:
            print(f"  - {uid}")
    
    # Check for test agents
    test_agents = []
    for agent in agents:
        name = agent.get("name", "").lower()
        if "test" in name or "dummy" in name or "sample" in name:
            test_agents.append(agent)
    
    if test_agents:
        print(f"\nPotential test agents found: {len(test_agents)}")
        for agent in test_agents:
            print(f"  - {agent.get('name')} (ID: {agent.get('id')}, User ID: {agent.get('user_id', 'None')})")
    else:
        print("\nNo obvious test agents found")
    
    return {
        "total": len(agents),
        "archetype_counts": archetype_counts,
        "user_id_present": user_id_present,
        "user_id_missing": user_id_missing,
        "unique_user_ids": list(user_ids),
        "test_agents": len(test_agents)
    }

def test_observer_message_with_auth():
    """Test the observer message endpoint with authentication"""
    print(f"\n{'='*80}\nTESTING OBSERVER MESSAGE ENDPOINT WITH AUTHENTICATION")
    
    if not auth_token:
        print("❌ No auth token available. Please login first.")
        return False
    
    # Get agents before sending message
    agents_before = get_agents(auth_token)
    print(f"Found {len(agents_before)} agents for the current user")
    
    # Send observer message
    message = "This is a test message from the observer. Please acknowledge."
    print(f"\nSending observer message: '{message}'")
    
    response = send_observer_message(message, auth_token)
    
    if response:
        print("✅ Observer message sent successfully")
        
        # Check agent responses
        agent_responses = response.get("agent_responses", {}).get("messages", [])
        
        # First message should be the observer message
        if agent_responses and len(agent_responses) > 0:
            first_message = agent_responses[0]
            if first_message.get("agent_name") == "Observer (You)" and first_message.get("message") == message:
                print("✅ Observer message appears as first message in response")
            else:
                print("❌ Observer message does not appear as first message in response")
        
        # Count agent responses
        agent_response_count = len(agent_responses) - 1  # Subtract 1 for the observer message
        print(f"Received responses from {agent_response_count} agents")
        
        # Compare with number of agents for the user
        if agent_response_count == len(agents_before):
            print("✅ Number of responses matches number of user's agents")
        else:
            print(f"❌ Number of responses ({agent_response_count}) does not match number of user's agents ({len(agents_before)})")
            print("This suggests the observer message endpoint is not properly filtering agents by user_id")
        
        return True
    else:
        print("❌ Failed to send observer message")
        return False

def test_observer_message_without_auth():
    """Test the observer message endpoint without authentication"""
    print(f"\n{'='*80}\nTESTING OBSERVER MESSAGE ENDPOINT WITHOUT AUTHENTICATION")
    
    # Send observer message without auth token
    message = "This is a test message without authentication."
    print(f"\nSending observer message without auth: '{message}'")
    
    response = send_observer_message(message)
    
    if response:
        print("❌ Observer message sent successfully without authentication")
        print("This is a security issue - the endpoint should require authentication")
        return False
    else:
        print("✅ Observer message endpoint correctly rejected unauthenticated request")
        return True

def main():
    """Main test function"""
    print(f"\n{'='*80}")
    print("AGENT DATABASE AND OBSERVER MESSAGE TESTING")
    print(f"{'='*80}")
    
    # Login as admin
    if not login_as_admin():
        print("❌ Cannot proceed with testing without admin login")
        sys.exit(1)
    
    # Get all agents for admin user
    admin_agents = get_agents(auth_token)
    print(f"\nFound {len(admin_agents)} agents for admin user")
    
    # Analyze admin agents
    admin_analysis = analyze_agents(admin_agents)
    
    # Create a test user for comparison
    test_token, test_user_id = create_test_user()
    
    if test_token:
        # Get agents for test user
        test_agents = get_agents(test_token)
        print(f"\nFound {len(test_agents)} agents for test user")
        
        # Analyze test user agents
        if test_agents:
            test_analysis = analyze_agents(test_agents)
        
        # Compare admin and test user
        print(f"\n{'='*80}\nCOMPARING ADMIN AND TEST USER")
        print(f"Admin user has {len(admin_agents)} agents")
        print(f"Test user has {len(test_agents)} agents")
        
        # Test observer message with admin auth
        test_observer_message_with_auth()
        
        # Test observer message without auth
        test_observer_message_without_auth()
        
        # Test observer message with test user auth
        print(f"\n{'='*80}\nTESTING OBSERVER MESSAGE WITH TEST USER AUTH")
        
        # Get agents before sending message
        test_user_agents = get_agents(test_token)
        print(f"Found {len(test_user_agents)} agents for test user")
        
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
            
            # Compare with number of agents for the test user
            if agent_response_count == len(test_user_agents):
                print("✅ Number of responses matches number of test user's agents")
            else:
                print(f"❌ Number of responses ({agent_response_count}) does not match number of test user's agents ({len(test_user_agents)})")
                print("This suggests the observer message endpoint is not properly filtering agents by user_id")
    
    # Print summary
    print(f"\n{'='*80}\nSUMMARY")
    print(f"{'='*80}")
    
    print(f"Admin user has {len(admin_agents)} agents")
    if admin_analysis["user_id_missing"] > 0:
        print(f"⚠️ {admin_analysis['user_id_missing']} agents have no user_id")
    
    if admin_analysis["unique_user_ids"] and len(admin_analysis["unique_user_ids"]) > 1:
        print(f"⚠️ Found {len(admin_analysis['unique_user_ids'])} different user_ids in admin's agents")
    
    if admin_analysis["test_agents"] > 0:
        print(f"⚠️ Found {admin_analysis['test_agents']} potential test agents")
    
    # Check observer message endpoint
    print("\nObserver Message Endpoint:")
    print("- The observer message endpoint is not properly filtering agents by user_id")
    print("- It's getting all agents from the database instead of just the current user's agents")
    print("- This is why so many agents are responding to observer messages")
    
    # Provide recommendations
    print("\nRecommendations:")
    print("1. Fix the observer message endpoint to filter agents by user_id")
    print("2. Add authentication requirement to the observer message endpoint")
    print("3. Clean up any test agents or agents without user_id")
    print("4. Ensure all agents have the correct user_id")

if __name__ == "__main__":
    main()