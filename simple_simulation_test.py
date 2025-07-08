#!/usr/bin/env python3
import requests
import json
import time

# Use the external URL from the environment
BACKEND_URL = "https://1b54c023-1ff4-4804-99a2-1b109f5253cd.preview.emergentagent.com"
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

# 3. Check simulation state
print("\n=== Step 3: Check Simulation State ===")
state_response = run_test("Get Simulation State", "/simulation/state", method="GET", headers=auth_headers)
if not state_response:
    print("Failed to get simulation state.")
    exit(1)

is_active = state_response.get("is_active", False)
print(f"Simulation is {'active' if is_active else 'inactive'}.")

# 4. Pause simulation
print("\n=== Step 4: Pause Simulation ===")
pause_response = run_test("Pause Simulation", "/simulation/pause", method="POST", headers=auth_headers)
if not pause_response:
    print("Failed to pause simulation.")
    exit(1)

print("Simulation paused successfully.")

# 5. Check simulation state after pause
print("\n=== Step 5: Check Simulation State After Pause ===")
state_after_pause = run_test("Get Simulation State After Pause", "/simulation/state", method="GET", headers=auth_headers)
if not state_after_pause:
    print("Failed to get simulation state after pause.")
    exit(1)

is_active_after_pause = state_after_pause.get("is_active", True)
print(f"Simulation is {'active' if is_active_after_pause else 'inactive'} after pause.")

# 6. Resume simulation
print("\n=== Step 6: Resume Simulation ===")
resume_response = run_test("Resume Simulation", "/simulation/resume", method="POST", headers=auth_headers)
if not resume_response:
    print("Failed to resume simulation.")
    exit(1)

print("Simulation resumed successfully.")

# 7. Check simulation state after resume
print("\n=== Step 7: Check Simulation State After Resume ===")
state_after_resume = run_test("Get Simulation State After Resume", "/simulation/state", method="GET", headers=auth_headers)
if not state_after_resume:
    print("Failed to get simulation state after resume.")
    exit(1)

is_active_after_resume = state_after_resume.get("is_active", False)
print(f"Simulation is {'active' if is_active_after_resume else 'inactive'} after resume.")

# 8. Check if conversations are cleared when starting a new simulation
print("\n=== Step 8: Check Conversations Before Restart ===")
conversations_before = run_test("Get Conversations Before Restart", "/conversations", method="GET", headers=auth_headers)
if conversations_before is None:
    print("Failed to get conversations before restart.")
    exit(1)

conversation_count_before = len(conversations_before) if isinstance(conversations_before, list) else 0
print(f"Found {conversation_count_before} conversations before restart.")

# 9. Restart simulation
print("\n=== Step 9: Restart Simulation ===")
restart_response = run_test("Restart Simulation", "/simulation/start", method="POST", headers=auth_headers)
if not restart_response:
    print("Failed to restart simulation.")
    exit(1)

print("Simulation restarted successfully.")

# 10. Check conversations after restart
print("\n=== Step 10: Check Conversations After Restart ===")
conversations_after = run_test("Get Conversations After Restart", "/conversations", method="GET", headers=auth_headers)
if conversations_after is None:
    print("Failed to get conversations after restart.")
    exit(1)

conversation_count_after = len(conversations_after) if isinstance(conversations_after, list) else 0
print(f"Found {conversation_count_after} conversations after restart.")

# Print summary
print("\n=== SUMMARY ===")
print(f"1. Start Simulation: {'✅ Success' if start_response else '❌ Failed'}")
print(f"2. Simulation State: {'✅ Active' if is_active else '❌ Inactive'}")
print(f"3. Pause Simulation: {'✅ Success' if pause_response else '❌ Failed'}")
print(f"4. State After Pause: {'✅ Inactive' if not is_active_after_pause else '❌ Still Active'}")
print(f"5. Resume Simulation: {'✅ Success' if resume_response else '❌ Failed'}")
print(f"6. State After Resume: {'✅ Active' if is_active_after_resume else '❌ Still Inactive'}")
print(f"7. Conversations Cleared: {'✅ Yes' if conversation_count_after == 0 else '❌ No'}")

overall_success = (
    start_response and 
    is_active and 
    pause_response and 
    not is_active_after_pause and 
    resume_response and 
    is_active_after_resume and 
    conversation_count_after == 0
)

print(f"\nOVERALL RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")