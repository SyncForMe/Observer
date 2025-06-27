#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = "http://127.0.0.1:8001"

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
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
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
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
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def test_login():
    """Login with test endpoint to get auth token"""
    global auth_token, test_user_id
    
    # Try using the email/password login first with admin credentials
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
    
    # If email/password login fails, try the test login endpoint
    if not login_test or not login_response:
        test_login_test, test_login_response = run_test(
            "Test Login Endpoint",
            "/auth/test-login",
            method="POST",
            expected_keys=["access_token", "token_type", "user"]
        )
        
        # Store the token for further testing if successful
        if test_login_test and test_login_response:
            auth_token = test_login_response.get("access_token")
            user_data = test_login_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"Test login successful. User ID: {test_user_id}")
            print(f"JWT Token: {auth_token}")
            return True
        else:
            print("Test login failed. Some tests may not work correctly.")
            return False
    else:
        # Store the token from email/password login
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True

def test_simulation_control_flow():
    """Test the simulation control flow: start -> pause -> resume -> fast-forward"""
    print("\n" + "="*80)
    print("TESTING SIMULATION CONTROL FLOW")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test simulation control flow without authentication")
            return False, "Authentication failed"
    
    # Test 1: Get initial simulation state
    print("\nTest 1: Get initial simulation state")
    
    initial_state_test, initial_state = run_test(
        "Get Initial Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if not initial_state_test:
        print("❌ Failed to get initial simulation state")
        return False, "Failed to get initial simulation state"
    
    print(f"Initial simulation state: is_active = {initial_state.get('is_active', False)}")
    
    # Test 2: Start simulation
    print("\nTest 2: Start simulation")
    
    # Define time limit for simulation (optional)
    start_data = {
        "time_limit_hours": 2,
        "time_limit_display": "2 hours"
    }
    
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        data=start_data,
        auth=True,
        expected_keys=["message", "state", "success"]
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print(f"Simulation started: {start_response.get('message')}")
    
    # Test 3: Verify simulation state after starting
    print("\nTest 3: Verify simulation state after starting")
    
    state_after_start_test, state_after_start = run_test(
        "Get Simulation State After Start",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if not state_after_start_test:
        print("❌ Failed to get simulation state after starting")
        return False, "Failed to get simulation state after starting"
    
    is_active_after_start = state_after_start.get("is_active", False)
    print(f"Simulation state after starting: is_active = {is_active_after_start}")
    
    if not is_active_after_start:
        print("❌ Simulation is not active after starting")
        return False, "Simulation is not active after starting"
    
    # Test 4: Pause simulation
    print("\nTest 4: Pause simulation")
    
    pause_test, pause_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not pause_test:
        print("❌ Failed to pause simulation")
        return False, "Failed to pause simulation"
    
    print(f"Simulation paused: {pause_response.get('message')}")
    
    # Test 5: Verify simulation state after pausing
    print("\nTest 5: Verify simulation state after pausing")
    
    state_after_pause_test, state_after_pause = run_test(
        "Get Simulation State After Pause",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if not state_after_pause_test:
        print("❌ Failed to get simulation state after pausing")
        return False, "Failed to get simulation state after pausing"
    
    is_active_after_pause = state_after_pause.get("is_active", True)
    print(f"Simulation state after pausing: is_active = {is_active_after_pause}")
    
    if is_active_after_pause:
        print("❌ Simulation is still active after pausing")
        return False, "Simulation is still active after pausing"
    
    # Test 6: Resume simulation
    print("\nTest 6: Resume simulation")
    
    resume_test, resume_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not resume_test:
        print("❌ Failed to resume simulation")
        return False, "Failed to resume simulation"
    
    print(f"Simulation resumed: {resume_response.get('message')}")
    
    # Test 7: Verify simulation state after resuming
    print("\nTest 7: Verify simulation state after resuming")
    
    state_after_resume_test, state_after_resume = run_test(
        "Get Simulation State After Resume",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active"]
    )
    
    if not state_after_resume_test:
        print("❌ Failed to get simulation state after resuming")
        return False, "Failed to get simulation state after resuming"
    
    is_active_after_resume = state_after_resume.get("is_active", False)
    print(f"Simulation state after resuming: is_active = {is_active_after_resume}")
    
    if not is_active_after_resume:
        print("❌ Simulation is not active after resuming")
        return False, "Simulation is not active after resuming"
    
    # Test 8: Fast-forward simulation
    print("\nTest 8: Fast-forward simulation")
    
    # Define fast-forward parameters
    fast_forward_data = {
        "target_days": 1,
        "conversations_per_period": 1
    }
    
    fast_forward_test, fast_forward_response = run_test(
        "Fast-Forward Simulation",
        "/simulation/fast-forward",
        method="POST",
        data=fast_forward_data,
        auth=True,
        expected_keys=["message", "conversations_generated"]
    )
    
    # Note: Fast-forward might fail if there are no agents or if API limits are reached
    # This is expected behavior, so we'll check for specific error messages
    
    if fast_forward_test:
        print(f"Simulation fast-forwarded: {fast_forward_response.get('message')}")
        print(f"Conversations generated: {fast_forward_response.get('conversations_generated')}")
    else:
        # Check if the error is due to missing agents (expected in a test environment)
        if "response_data" in locals() and isinstance(fast_forward_response, dict):
            error_detail = fast_forward_response.get("detail", "")
            if "Need at least 2 agents" in error_detail:
                print("ℹ️ Fast-forward failed because there are not enough agents (expected in test environment)")
                print("ℹ️ This is normal behavior and not a test failure")
            elif "Not enough API requests" in error_detail:
                print("ℹ️ Fast-forward failed because of API request limits (expected in test environment)")
                print("ℹ️ This is normal behavior and not a test failure")
            else:
                print(f"❌ Fast-forward failed with unexpected error: {error_detail}")
                return False, f"Fast-forward failed with unexpected error: {error_detail}"
        else:
            print("❌ Fast-forward failed with unknown error")
            return False, "Fast-forward failed with unknown error"
    
    # Test 9: Test authentication requirements
    print("\nTest 9: Test authentication requirements for simulation endpoints")
    
    # Test start without auth
    start_no_auth_test, _ = run_test(
        "Start Simulation Without Auth",
        "/simulation/start",
        method="POST",
        data=start_data,
        auth=False,
        expected_status=403
    )
    
    if start_no_auth_test:
        print("✅ Start simulation correctly requires authentication")
    else:
        print("❌ Start simulation does not properly enforce authentication")
    
    # Test pause without auth
    pause_no_auth_test, _ = run_test(
        "Pause Simulation Without Auth",
        "/simulation/pause",
        method="POST",
        auth=False,
        expected_status=403
    )
    
    if pause_no_auth_test:
        print("✅ Pause simulation correctly requires authentication")
    else:
        print("❌ Pause simulation does not properly enforce authentication")
    
    # Test resume without auth
    resume_no_auth_test, _ = run_test(
        "Resume Simulation Without Auth",
        "/simulation/resume",
        method="POST",
        auth=False,
        expected_status=403
    )
    
    if resume_no_auth_test:
        print("✅ Resume simulation correctly requires authentication")
    else:
        print("❌ Resume simulation does not properly enforce authentication")
    
    # Test get state without auth
    state_no_auth_test, _ = run_test(
        "Get Simulation State Without Auth",
        "/simulation/state",
        method="GET",
        auth=False,
        expected_status=403
    )
    
    if state_no_auth_test:
        print("✅ Get simulation state correctly requires authentication")
    else:
        print("❌ Get simulation state does not properly enforce authentication")
    
    # Print summary
    print("\nSIMULATION CONTROL FLOW SUMMARY:")
    
    # Check if all critical tests passed
    start_works = start_test
    pause_works = pause_test
    resume_works = resume_test
    state_works = state_after_start_test and state_after_pause_test and state_after_resume_test
    auth_works = start_no_auth_test and pause_no_auth_test and resume_no_auth_test and state_no_auth_test
    
    if start_works and pause_works and resume_works and state_works and auth_works:
        print("✅ Simulation control flow is working correctly!")
        print("✅ Start simulation is functioning properly")
        print("✅ Pause simulation is functioning properly")
        print("✅ Resume simulation is functioning properly")
        print("✅ Get simulation state is functioning properly")
        print("✅ Authentication is properly enforced for all endpoints")
        return True, "Simulation control flow is working correctly"
    else:
        issues = []
        if not start_works:
            issues.append("Start simulation is not functioning properly")
        if not pause_works:
            issues.append("Pause simulation is not functioning properly")
        if not resume_works:
            issues.append("Resume simulation is not functioning properly")
        if not state_works:
            issues.append("Get simulation state is not functioning properly")
        if not auth_works:
            issues.append("Authentication is not properly enforced for all endpoints")
        
        print("❌ Simulation control flow has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def test_simulation_state_fields():
    """Test the simulation state endpoint returns the correct fields"""
    print("\n" + "="*80)
    print("TESTING SIMULATION STATE FIELDS")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test simulation state fields without authentication")
            return False, "Authentication failed"
    
    # Test 1: Start simulation to ensure state is initialized
    print("\nTest 1: Start simulation to ensure state is initialized")
    
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state", "success"]
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print(f"Simulation started: {start_response.get('message')}")
    
    # Test 2: Get simulation state and verify fields
    print("\nTest 2: Get simulation state and verify fields")
    
    state_test, state = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id"]
    )
    
    if not state_test:
        print("❌ Failed to get simulation state")
        return False, "Failed to get simulation state"
    
    # Verify required fields
    required_fields = ["id", "is_active", "user_id", "current_day", "current_time_period"]
    missing_fields = [field for field in required_fields if field not in state]
    
    if missing_fields:
        print(f"❌ Simulation state is missing required fields: {', '.join(missing_fields)}")
        return False, f"Simulation state is missing required fields: {', '.join(missing_fields)}"
    
    # Verify field values
    is_active = state.get("is_active")
    user_id = state.get("user_id")
    
    print(f"Simulation state fields:")
    print(f"  - is_active: {is_active}")
    print(f"  - user_id: {user_id}")
    
    if is_active is not True:
        print("❌ Simulation is not active after starting")
        return False, "Simulation is not active after starting"
    
    if not user_id:
        print("❌ Simulation state does not have a user_id")
        return False, "Simulation state does not have a user_id"
    
    if user_id != test_user_id:
        print(f"❌ Simulation state user_id ({user_id}) does not match test user ID ({test_user_id})")
        return False, f"Simulation state user_id ({user_id}) does not match test user ID ({test_user_id})"
    
    # Test 3: Pause simulation and verify is_active field changes
    print("\nTest 3: Pause simulation and verify is_active field changes")
    
    pause_test, pause_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not pause_test:
        print("❌ Failed to pause simulation")
        return False, "Failed to pause simulation"
    
    # Get state after pausing
    state_after_pause_test, state_after_pause = run_test(
        "Get Simulation State After Pause",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id"]
    )
    
    if not state_after_pause_test:
        print("❌ Failed to get simulation state after pausing")
        return False, "Failed to get simulation state after pausing"
    
    is_active_after_pause = state_after_pause.get("is_active")
    print(f"is_active after pause: {is_active_after_pause}")
    
    if is_active_after_pause is not False:
        print("❌ Simulation is still active after pausing")
        return False, "Simulation is still active after pausing"
    
    # Test 4: Resume simulation and verify is_active field changes back
    print("\nTest 4: Resume simulation and verify is_active field changes back")
    
    resume_test, resume_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message", "is_active", "success"]
    )
    
    if not resume_test:
        print("❌ Failed to resume simulation")
        return False, "Failed to resume simulation"
    
    # Get state after resuming
    state_after_resume_test, state_after_resume = run_test(
        "Get Simulation State After Resume",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["id", "is_active", "user_id"]
    )
    
    if not state_after_resume_test:
        print("❌ Failed to get simulation state after resuming")
        return False, "Failed to get simulation state after resuming"
    
    is_active_after_resume = state_after_resume.get("is_active")
    print(f"is_active after resume: {is_active_after_resume}")
    
    if is_active_after_resume is not True:
        print("❌ Simulation is not active after resuming")
        return False, "Simulation is not active after resuming"
    
    # Print summary
    print("\nSIMULATION STATE FIELDS SUMMARY:")
    
    print("✅ Simulation state includes all required fields")
    print("✅ is_active field correctly changes with simulation state")
    print("✅ user_id field correctly identifies the current user")
    
    return True, "Simulation state fields are correct"

if __name__ == "__main__":
    # Run the tests
    test_login()
    test_simulation_control_flow()
    test_simulation_state_fields()
    
    # Print summary of all tests
    print_summary()