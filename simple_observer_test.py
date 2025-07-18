#!/usr/bin/env python3
"""
Simple Observer Message Test - Debug timeout issue
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_observer_endpoint():
    """Test observer endpoint with minimal setup"""
    print("🔧 Testing Observer Endpoint...")
    
    # Get auth token
    print("1. Getting auth token...")
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Auth successful")
    
    # Reset simulation
    print("2. Resetting simulation...")
    reset_response = requests.post(f"{API_URL}/simulation/reset", headers=headers)
    print(f"Reset status: {reset_response.status_code}")
    
    # Create one agent
    print("3. Creating test agent...")
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist",
        "goal": "Test goal",
        "expertise": "Testing"
    }
    agent_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    if agent_response.status_code != 200:
        print(f"❌ Agent creation failed: {agent_response.status_code}")
        return
    print("✅ Agent created")
    
    # Start simulation
    print("4. Starting simulation...")
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    print(f"Start status: {start_response.status_code}")
    
    # Test observer message with short timeout
    print("5. Testing observer message (10s timeout)...")
    observer_data = {"observer_message": "Hello test"}
    
    try:
        observer_response = requests.post(
            f"{API_URL}/observer/send-message", 
            json=observer_data, 
            headers=headers,
            timeout=10
        )
        print(f"Observer response status: {observer_response.status_code}")
        if observer_response.status_code == 200:
            result = observer_response.json()
            print(f"✅ Observer message successful")
            print(f"Response keys: {list(result.keys())}")
        else:
            print(f"❌ Observer message failed: {observer_response.text}")
    except requests.exceptions.Timeout:
        print("❌ Observer message timed out after 10 seconds")
    except Exception as e:
        print(f"❌ Observer message error: {e}")

if __name__ == "__main__":
    test_observer_endpoint()