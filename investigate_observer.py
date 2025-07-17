#!/usr/bin/env python3
"""
Investigate agent database and observer messages endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def investigate_issues():
    print("🔍 Investigating Observer Message Issues")
    print("="*50)
    
    # Get authentication
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    if auth_response.status_code != 200:
        print("❌ Failed to authenticate")
        return
    
    auth_data = auth_response.json()
    token = auth_data['access_token']
    user_id = auth_data['user']['id']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authenticated as: {auth_data['user']['email']}")
    print(f"User ID: {user_id}")
    
    # Check existing agents
    print(f"\n🤖 Checking existing agents:")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent['name']} (ID: {agent['id']}, User: {agent.get('user_id', 'Unknown')})")
    else:
        print(f"❌ Failed to get agents: {agents_response.status_code}")
    
    # Check backend logs for the 500 error
    print(f"\n🔍 Testing observer messages endpoint with detailed error info:")
    
    try:
        messages_response = requests.get(f"{API_URL}/observer/messages", headers=headers, timeout=10)
        print(f"Status Code: {messages_response.status_code}")
        print(f"Headers: {dict(messages_response.headers)}")
        
        if messages_response.status_code == 500:
            print("❌ 500 Internal Server Error - this suggests a backend code issue")
            print("This could be:")
            print("  1. Database connection issue")
            print("  2. Missing collection or field")
            print("  3. Code error in the endpoint")
            
        elif messages_response.status_code == 200:
            messages = messages_response.json()
            print(f"✅ Retrieved {len(messages)} observer messages")
            for msg in messages[:3]:  # Show first 3
                print(f"  - {msg.get('message', 'No message')[:50]}... (User: {msg.get('user_id', 'Unknown')})")
        else:
            print(f"Unexpected status: {messages_response.status_code}")
            print(f"Response: {messages_response.text}")
            
    except Exception as e:
        print(f"❌ Exception when calling observer messages: {e}")
    
    # Test if we can send an observer message and see what happens
    print(f"\n💬 Testing observer message sending:")
    
    # Start simulation first
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code == 200:
        print("✅ Simulation started")
        
        # Send observer message
        test_message = "Test message for debugging"
        observer_response = requests.post(f"{API_URL}/observer/send-message", 
                                        json={"observer_message": test_message}, 
                                        headers=headers)
        
        if observer_response.status_code == 200:
            print("✅ Observer message sent successfully")
            
            # Now try to retrieve messages again
            print("🔍 Trying to retrieve messages after sending...")
            messages_response = requests.get(f"{API_URL}/observer/messages", headers=headers)
            print(f"Status after sending: {messages_response.status_code}")
            
        else:
            print(f"❌ Failed to send observer message: {observer_response.status_code}")
    else:
        print(f"❌ Failed to start simulation: {start_response.status_code}")

if __name__ == "__main__":
    investigate_issues()