#!/usr/bin/env python3
"""
Debug script to check the simulation state after reset
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def main():
    # Authenticate
    response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create some test data
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist",
        "goal": "Test goal",
        "expertise": "Testing",
        "background": "Test background"
    }
    requests.post(f"{API_URL}/agents", json=agent_data, headers=headers, timeout=10)
    requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
    
    # Check state before reset
    print("=== STATE BEFORE RESET ===")
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    state_before = response.json()
    print(json.dumps(state_before, indent=2))
    
    # Reset
    print("\n=== PERFORMING RESET ===")
    response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
    reset_result = response.json()
    print(json.dumps(reset_result, indent=2))
    
    # Check state after reset
    print("\n=== STATE AFTER RESET ===")
    response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
    state_after = response.json()
    print(json.dumps(state_after, indent=2))
    
    # Check if scenario field exists and has content
    scenario = state_after.get('scenario', '')
    print(f"\nScenario field: '{scenario}'")
    print(f"Scenario length: {len(scenario)}")
    print(f"Has scenario content: {len(scenario) > 0}")

if __name__ == "__main__":
    main()