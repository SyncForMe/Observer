#!/usr/bin/env python3
"""
Debug script for observer message issues
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def debug_observer_issues():
    print("🔍 Debugging Observer Message Issues")
    print("="*50)
    
    # Get authentication
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    if auth_response.status_code != 200:
        print("❌ Failed to authenticate")
        return
    
    auth_data = auth_response.json()
    token = auth_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authenticated as: {auth_data['user']['email']}")
    
    # Create a test agent
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist",
        "goal": "Test observer messages",
        "expertise": "Testing",
        "background": "Test background"
    }
    
    agent_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    if agent_response.status_code != 200:
        print("❌ Failed to create test agent")
        return
    
    agent = agent_response.json()
    print(f"✅ Created test agent: {agent['name']} (ID: {agent['id']})")
    
    # Start simulation
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code != 200:
        print("❌ Failed to start simulation")
        return
    
    print("✅ Started simulation")
    
    # Send observer message
    observer_message = "Hello! This is a test observer message."
    observer_response = requests.post(f"{API_URL}/observer/send-message", 
                                    json={"observer_message": observer_message}, 
                                    headers=headers)
    
    if observer_response.status_code == 200:
        data = observer_response.json()
        print("✅ Observer message sent successfully")
        
        # Debug agent response count issue
        if 'agent_responses' in data and 'messages' in data['agent_responses']:
            messages = data['agent_responses']['messages']
            print(f"\n🔍 Message Analysis:")
            print(f"Total messages: {len(messages)}")
            
            for i, msg in enumerate(messages):
                print(f"  {i+1}. {msg['agent_name']}: {msg['message'][:50]}...")
            
            observer_messages = [msg for msg in messages if msg['agent_name'] == "Observer (You)"]
            agent_messages = [msg for msg in messages if msg['agent_name'] != "Observer (You)"]
            
            print(f"\nObserver messages: {len(observer_messages)}")
            print(f"Agent messages: {len(agent_messages)}")
            
            # Check if there are duplicate agents or unexpected agents
            agent_names = [msg['agent_name'] for msg in agent_messages]
            print(f"Agent names responding: {agent_names}")
    else:
        print(f"❌ Failed to send observer message: {observer_response.status_code}")
        print(f"Response: {observer_response.text}")
    
    # Debug database retrieval issue
    print(f"\n🔍 Testing Observer Messages Database Retrieval:")
    messages_response = requests.get(f"{API_URL}/observer/messages", headers=headers)
    
    print(f"Status Code: {messages_response.status_code}")
    if messages_response.status_code == 200:
        messages = messages_response.json()
        print(f"✅ Retrieved {len(messages)} observer messages")
        if messages:
            print(f"Latest message: {messages[0]}")
    else:
        print(f"❌ Error retrieving observer messages")
        print(f"Response: {messages_response.text}")
        
        # Check if the endpoint exists
        print("\n🔍 Checking if endpoint exists...")
        try:
            # Try with different methods to see what's available
            options_response = requests.options(f"{API_URL}/observer/messages", headers=headers)
            print(f"OPTIONS response: {options_response.status_code}")
        except Exception as e:
            print(f"OPTIONS error: {e}")
    
    # Cleanup
    delete_response = requests.delete(f"{API_URL}/agents/{agent['id']}", headers=headers)
    if delete_response.status_code == 200:
        print(f"\n✅ Cleaned up test agent")
    else:
        print(f"\n⚠️ Failed to cleanup test agent")

if __name__ == "__main__":
    debug_observer_issues()