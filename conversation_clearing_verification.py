#!/usr/bin/env python3
import requests
import json
import time

# Use the external URL from the environment
BACKEND_URL = "https://ceb1040f-47be-4ea5-aa05-81bfb7cce94d.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def run_test(name, endpoint, method="GET", data=None, headers=None):
    """Run a test and print the results"""
    url = f"{API_URL}{endpoint}"
    print(f"\n=== Testing: {name} ({method} {url}) ===")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            return response_data
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None

# 1. Login to get auth token
print("\n=== Step 1: Login ===")
login_data = {
    "email": "dino@cytonic.com",
    "password": "Observerinho8"
}

login_response = run_test("Login", "/auth/login", method="POST", data=login_data)
if not login_response or "access_token" not in login_response:
    print("Login failed, trying test login...")
    login_response = run_test("Test Login", "/auth/test-login", method="POST")

if not login_response or "access_token" not in login_response:
    print("All login attempts failed. Cannot proceed with tests.")
    exit(1)

auth_token = login_response["access_token"]
auth_headers = {"Authorization": f"Bearer {auth_token}"}
print(f"Successfully logged in. Token: {auth_token[:20]}...")

# 2. Start simulation
print("\n=== Step 2: Start Simulation ===")
start_response = run_test("Start Simulation", "/simulation/start", method="POST", headers=auth_headers)
if not start_response:
    print("Failed to start simulation. Cannot proceed with tests.")
    exit(1)

print("Simulation started successfully.")

# 3. Create agents for conversation generation
print("\n=== Step 3: Create Agents ===")
agent1_data = {
    "name": "Test Agent 1",
    "archetype": "scientist",
    "personality": {
        "extroversion": 5,
        "optimism": 5,
        "curiosity": 5,
        "cooperativeness": 5,
        "energy": 5
    },
    "goal": "Test goal 1",
    "expertise": "Test expertise 1",
    "background": "Test background 1"
}

agent1_response = run_test("Create Agent 1", "/agents", method="POST", data=agent1_data, headers=auth_headers)
if not agent1_response:
    print("Failed to create agent 1.")
    exit(1)

agent1_id = agent1_response.get("id")
print(f"Created agent 1 with ID: {agent1_id}")

agent2_data = {
    "name": "Test Agent 2",
    "archetype": "leader",
    "personality": {
        "extroversion": 7,
        "optimism": 7,
        "curiosity": 7,
        "cooperativeness": 7,
        "energy": 7
    },
    "goal": "Test goal 2",
    "expertise": "Test expertise 2",
    "background": "Test background 2"
}

agent2_response = run_test("Create Agent 2", "/agents", method="POST", data=agent2_data, headers=auth_headers)
if not agent2_response:
    print("Failed to create agent 2.")
    exit(1)

agent2_id = agent2_response.get("id")
print(f"Created agent 2 with ID: {agent2_id}")

# 4. Set a scenario
print("\n=== Step 4: Set Scenario ===")
scenario_data = {
    "scenario": "Test scenario for conversation clearing",
    "scenario_name": "Test Scenario"
}

scenario_response = run_test("Set Scenario", "/simulation/set-scenario", method="POST", data=scenario_data, headers=auth_headers)
if not scenario_response:
    print("Failed to set scenario.")
    exit(1)

print("Scenario set successfully.")

# 5. Generate a conversation
print("\n=== Step 5: Generate Conversation ===")
conversation_data = {
    "message": "Test conversation message"
}

conversation_response = run_test("Generate Conversation", "/conversation/generate", method="POST", data=conversation_data, headers=auth_headers)
if not conversation_response:
    print("Failed to generate conversation.")
    exit(1)

print("Conversation generated successfully.")

# 6. Check conversations
print("\n=== Step 6: Check Conversations ===")
conversations_response = run_test("Get Conversations", "/conversations", method="GET", headers=auth_headers)
if conversations_response is None:
    print("Failed to get conversations.")
    exit(1)

conversation_count = len(conversations_response) if isinstance(conversations_response, list) else 0
print(f"Found {conversation_count} conversations.")

if conversation_count == 0:
    print("No conversations found. This is unexpected after generating a conversation.")
    exit(1)

# 7. Restart simulation
print("\n=== Step 7: Restart Simulation ===")
restart_response = run_test("Restart Simulation", "/simulation/start", method="POST", headers=auth_headers)
if not restart_response:
    print("Failed to restart simulation.")
    exit(1)

print("Simulation restarted successfully.")

# 8. Check conversations after restart
print("\n=== Step 8: Check Conversations After Restart ===")
conversations_after_response = run_test("Get Conversations After Restart", "/conversations", method="GET", headers=auth_headers)
if conversations_after_response is None:
    print("Failed to get conversations after restart.")
    exit(1)

conversation_count_after = len(conversations_after_response) if isinstance(conversations_after_response, list) else 0
print(f"Found {conversation_count_after} conversations after restart.")

# Print summary
print("\n=== SUMMARY ===")
print(f"1. Start Simulation: {'✅ Success' if start_response else '❌ Failed'}")
print(f"2. Create Agents: {'✅ Success' if agent1_response and agent2_response else '❌ Failed'}")
print(f"3. Set Scenario: {'✅ Success' if scenario_response else '❌ Failed'}")
print(f"4. Generate Conversation: {'✅ Success' if conversation_response else '❌ Failed'}")
print(f"5. Conversations Before Restart: {conversation_count}")
print(f"6. Restart Simulation: {'✅ Success' if restart_response else '❌ Failed'}")
print(f"7. Conversations After Restart: {conversation_count_after}")
print(f"8. Conversations Cleared: {'✅ Yes' if conversation_count_after == 0 else '❌ No'}")

overall_success = (
    start_response and 
    agent1_response and 
    agent2_response and 
    scenario_response and 
    conversation_response and 
    conversation_count > 0 and 
    restart_response and 
    conversation_count_after == 0
)

print(f"\nOVERALL RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")
print(f"\nConclusion: {'The simulation/start endpoint properly clears conversations.' if conversation_count_after == 0 else 'The simulation/start endpoint does NOT properly clear conversations.'}")