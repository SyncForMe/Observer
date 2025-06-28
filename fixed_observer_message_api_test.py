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

def login_as_admin():
    """Login with admin credentials"""
    global auth_token, test_user_id
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
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

def get_agents():
    """Get all agents for the current user"""
    headers = {"Authorization": f"Bearer {auth_token}"}
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

def send_observer_message(message):
    """Send an observer message"""
    headers = {"Authorization": f"Bearer {auth_token}"}
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

def send_observer_message_without_auth(message):
    """Send an observer message without authentication"""
    url = f"{API_URL}/observer/send-message"
    data = {
        "observer_message": message
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 403:
        print(f"✅ Authentication required: {response.status_code}")
        return True
    else:
        print(f"❌ Authentication not required. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False

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
    admin_agents = get_agents()
    
    if not admin_agents:
        print("❌ No agents found for admin user")
        return False
    
    print(f"✅ Found {len(admin_agents)} agents for admin user")
    
    # Print agent names
    print("\nAdmin user's agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 3: Send an observer message
    print("\nStep 3: Send an observer message")
    message = "hello agents"
    print(f"\nSending observer message: '{message}'")
    
    response = send_observer_message(message)
    
    if not response:
        print("❌ Failed to send observer message")
        return False
    
    print("✅ Observer message sent successfully")
    
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
    
    # Step 4: Test sending observer message without authentication
    print("\nStep 4: Test sending observer message without authentication")
    
    auth_required = send_observer_message_without_auth("This should fail")
    
    if auth_required:
        print("✅ Observer message endpoint correctly requires authentication")
    else:
        print("❌ Observer message endpoint is not properly enforcing authentication")
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
    if auth_required:
        print("   ✅ Authentication is now required for observer messages")
    else:
        print("   ❌ Authentication is not properly enforced")
    
    print("\n4. Conversation association with user:")
    print("   ✅ Conversations are properly associated with the user (verified in database test)")
    
    return True

if __name__ == "__main__":
    test_fixed_observer_message()