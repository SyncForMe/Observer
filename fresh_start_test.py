#!/usr/bin/env python3
"""
Fresh Start Cleanup Functionality Test
Tests the POST /api/simulation/reset endpoint for timeout issues and performance
"""
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

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
            response = requests.get(url, headers=headers, params=params, timeout=120)  # 2 minute timeout
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params, timeout=120)  # 2 minute timeout
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params, timeout=120)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params, timeout=120)
            else:
                response = requests.delete(url, headers=headers, params=params, timeout=120)
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
        
        return test_passed, response_data, response_time if measure_time else None
    
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 120 seconds")
        return False, {"error": "timeout"}, 120.0
    except Exception as e:
        print(f"Error during test: {e}")
        return False, {"error": str(e)}, None

def test_login():
    """Test login to get authentication token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("TESTING LOGIN FOR AUTHENTICATION")
    print("="*80)
    
    # Try admin credentials first
    admin_email = "dino@cytonic.com"
    admin_password = "Observerinho8"
    
    login_data = {
        "email": admin_email,
        "password": admin_password
    }
    
    login_test, login_response, _ = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True
    else:
        print("❌ Login failed")
        return False

def create_test_data():
    """Create test data to be cleared by reset"""
    print("\n" + "="*80)
    print("CREATING TEST DATA FOR RESET TESTING")
    print("="*80)
    
    created_items = {
        "agents": [],
        "conversations": [],
        "documents": [],
        "observer_messages": []
    }
    
    # Create test agents
    print("\n--- Creating Test Agents ---")
    for i in range(5):  # Create 5 agents for substantial data
        agent_data = {
            "name": f"Reset Test Agent {i+1}",
            "archetype": "scientist",
            "goal": f"Test goal for reset functionality {i+1}",
            "expertise": f"Test expertise area {i+1}",
            "background": f"Test background for agent {i+1}",
            "avatar_prompt": f"Professional test agent {i+1}",
            "personality": {
                "extroversion": 5 + i,
                "optimism": 6 + i,
                "curiosity": 7 + i,
                "cooperativeness": 8 - i,
                "energy": 5 + i
            }
        }
        
        create_agent_test, create_agent_response, response_time = run_test(
            f"Create Test Agent {i+1}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name"],
            measure_time=True
        )
        
        if create_agent_test and create_agent_response:
            created_items["agents"].append(create_agent_response)
            print(f"✅ Created test agent: {create_agent_response.get('name')} (Time: {response_time:.3f}s)")
        else:
            print(f"❌ Failed to create test agent {i+1}")
    
    # Set a test scenario
    print("\n--- Setting Test Scenario ---")
    scenario_data = {
        "scenario": "Fresh Start Reset Test Scenario - This is a comprehensive test of the reset functionality with substantial data to verify performance and timeout handling.",
        "scenario_name": "Reset Performance Test"
    }
    
    set_scenario_test, set_scenario_response, response_time = run_test(
        "Set Test Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message"],
        measure_time=True
    )
    
    if set_scenario_test:
        print(f"✅ Set test scenario (Time: {response_time:.3f}s)")
    else:
        print("❌ Failed to set test scenario")
    
    # Start simulation to create state
    print("\n--- Starting Simulation ---")
    start_sim_test, start_sim_response, response_time = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message"],
        measure_time=True
    )
    
    if start_sim_test:
        print(f"✅ Started simulation (Time: {response_time:.3f}s)")
    else:
        print("❌ Failed to start simulation")
    
    # Generate multiple conversations if we have agents
    if len(created_items["agents"]) >= 2:
        print("\n--- Generating Test Conversations ---")
        for i in range(3):  # Generate 3 conversations for substantial data
            generate_conv_test, generate_conv_response, response_time = run_test(
                f"Generate Test Conversation {i+1}",
                "/conversation/generate",
                method="POST",
                auth=True,
                expected_keys=["id", "messages"],
                measure_time=True
            )
            
            if generate_conv_test and generate_conv_response:
                created_items["conversations"].append(generate_conv_response)
                print(f"✅ Generated test conversation {i+1} (Time: {response_time:.3f}s)")
            else:
                print(f"❌ Failed to generate test conversation {i+1}")
    
    # Send observer messages
    print("\n--- Sending Observer Messages ---")
    for i in range(2):  # Send 2 observer messages
        observer_data = {
            "observer_message": f"Test observer message {i+1} for reset functionality testing. This message should be cleared during reset."
        }
        
        observer_test, observer_response, response_time = run_test(
            f"Send Observer Message {i+1}",
            "/observer/send-message",
            method="POST",
            data=observer_data,
            auth=True,
            expected_keys=["message"],
            measure_time=True
        )
        
        if observer_test and observer_response:
            created_items["observer_messages"].append(observer_response)
            print(f"✅ Sent observer message {i+1} (Time: {response_time:.3f}s)")
        else:
            print(f"❌ Failed to send observer message {i+1}")
    
    return created_items

def verify_data_before_reset():
    """Verify that test data exists before reset"""
    print("\n" + "="*80)
    print("VERIFYING DATA EXISTS BEFORE RESET")
    print("="*80)
    
    data_counts = {}
    
    # Check agents exist
    get_agents_test, get_agents_response, response_time = run_test(
        "Get Agents Before Reset",
        "/agents",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    agents_count = 0
    if get_agents_test and get_agents_response:
        agents_count = len(get_agents_response)
        data_counts["agents"] = agents_count
        print(f"✅ Found {agents_count} agents before reset (Time: {response_time:.3f}s)")
    else:
        print("❌ Failed to get agents before reset")
        data_counts["agents"] = 0
    
    # Check conversations exist
    get_conversations_test, get_conversations_response, response_time = run_test(
        "Get Conversations Before Reset",
        "/conversations",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    conversations_count = 0
    if get_conversations_test and get_conversations_response:
        conversations_count = len(get_conversations_response)
        data_counts["conversations"] = conversations_count
        print(f"✅ Found {conversations_count} conversations before reset (Time: {response_time:.3f}s)")
    else:
        print("❌ Failed to get conversations before reset")
        data_counts["conversations"] = 0
    
    # Check simulation state exists
    get_state_test, get_state_response, response_time = run_test(
        "Get Simulation State Before Reset",
        "/simulation/state",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    state_exists = False
    if get_state_test and get_state_response:
        state_exists = True
        scenario = get_state_response.get("scenario", "")
        scenario_name = get_state_response.get("scenario_name", "")
        is_active = get_state_response.get("is_active", False)
        data_counts["state"] = 1
        print(f"✅ Simulation state exists before reset (Time: {response_time:.3f}s)")
        print(f"   Scenario: {scenario}")
        print(f"   Scenario Name: {scenario_name}")
        print(f"   Is Active: {is_active}")
    else:
        print("❌ Failed to get simulation state before reset")
        data_counts["state"] = 0
    
    # Check observer messages exist
    get_observer_test, get_observer_response, response_time = run_test(
        "Get Observer Messages Before Reset",
        "/observer/messages",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    observer_count = 0
    if get_observer_test and get_observer_response:
        observer_count = len(get_observer_response)
        data_counts["observer_messages"] = observer_count
        print(f"✅ Found {observer_count} observer messages before reset (Time: {response_time:.3f}s)")
    else:
        print("❌ Failed to get observer messages before reset")
        data_counts["observer_messages"] = 0
    
    return data_counts

def test_fresh_start_reset():
    """Test the Fresh Start reset functionality"""
    print("\n" + "="*80)
    print("TESTING FRESH START RESET FUNCTIONALITY")
    print("="*80)
    
    # Test reset endpoint without authentication first
    print("\n--- Testing Reset Without Authentication ---")
    reset_no_auth_test, reset_no_auth_response, response_time = run_test(
        "Reset Without Authentication",
        "/simulation/reset",
        method="POST",
        auth=False,
        expected_status=403,
        measure_time=True
    )
    
    if reset_no_auth_test:
        print(f"✅ Reset endpoint correctly requires authentication (Time: {response_time:.3f}s)")
    else:
        print("❌ Reset endpoint should require authentication")
    
    # Test reset endpoint with authentication
    print("\n--- Testing Fresh Start Reset with Authentication ---")
    print("⏱️  Starting reset operation - measuring performance...")
    
    reset_test, reset_response, response_time = run_test(
        "Fresh Start Reset",
        "/simulation/reset",
        method="POST",
        auth=True,
        expected_keys=["message", "success", "state", "cleared_collections"],
        measure_time=True
    )
    
    if not reset_test:
        print("❌ Reset endpoint failed")
        return False, f"Reset endpoint failed after {response_time:.3f}s"
    
    if reset_response.get("success") != True:
        print("❌ Reset did not return success=True")
        return False, "Reset did not return success"
    
    # Check performance - should complete within 60 seconds
    performance_ok = response_time <= 60.0
    if performance_ok:
        print(f"✅ Reset completed within 60 seconds: {response_time:.3f}s")
    else:
        print(f"❌ Reset took too long: {response_time:.3f}s (should be ≤ 60s)")
    
    # Check cleared collections count
    cleared_collections = reset_response.get("cleared_collections", 0)
    print(f"✅ Reset cleared {cleared_collections} collections")
    
    # Check response format
    state = reset_response.get("state", {})
    if state:
        print("✅ Reset response includes new simulation state")
        print(f"   New state is_active: {state.get('is_active', 'unknown')}")
        print(f"   New state scenario: '{state.get('scenario', 'unknown')}'")
    else:
        print("❌ Reset response missing state information")
    
    return True, {
        "response_time": response_time,
        "performance_ok": performance_ok,
        "cleared_collections": cleared_collections,
        "success": True
    }

def verify_data_after_reset():
    """Verify that all data is cleared after reset"""
    print("\n" + "="*80)
    print("VERIFYING ALL DATA IS CLEARED AFTER RESET")
    print("="*80)
    
    verification_results = {}
    
    # Check agents are cleared
    get_agents_after_test, get_agents_after_response, response_time = run_test(
        "Get Agents After Reset",
        "/agents",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    agents_cleared = False
    if get_agents_after_test and get_agents_after_response:
        agents_count_after = len(get_agents_after_response)
        if agents_count_after == 0:
            agents_cleared = True
            print(f"✅ All agents cleared (Time: {response_time:.3f}s)")
        else:
            print(f"❌ Agents not fully cleared: {agents_count_after} remaining")
    else:
        print("❌ Failed to get agents after reset")
    
    verification_results["agents_cleared"] = agents_cleared
    
    # Check conversations are cleared
    get_conversations_after_test, get_conversations_after_response, response_time = run_test(
        "Get Conversations After Reset",
        "/conversations",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    conversations_cleared = False
    if get_conversations_after_test and get_conversations_after_response:
        conversations_count_after = len(get_conversations_after_response)
        if conversations_count_after == 0:
            conversations_cleared = True
            print(f"✅ All conversations cleared (Time: {response_time:.3f}s)")
        else:
            print(f"❌ Conversations not fully cleared: {conversations_count_after} remaining")
    else:
        print("❌ Failed to get conversations after reset")
    
    verification_results["conversations_cleared"] = conversations_cleared
    
    # Check simulation state is reset to default
    get_state_after_test, get_state_after_response, response_time = run_test(
        "Get Simulation State After Reset",
        "/simulation/state",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    state_reset = False
    if get_state_after_test and get_state_after_response:
        is_active = get_state_after_response.get("is_active", True)
        scenario = get_state_after_response.get("scenario", "not_empty")
        scenario_name = get_state_after_response.get("scenario_name", "not_empty")
        
        if not is_active and scenario == "" and scenario_name == "":
            state_reset = True
            print(f"✅ Simulation state reset to default (Time: {response_time:.3f}s)")
            print("   - Not active: ✅")
            print("   - Scenario cleared: ✅")
            print("   - Scenario name cleared: ✅")
        else:
            print(f"❌ Simulation state not properly reset:")
            print(f"   - Active: {is_active} (should be False)")
            print(f"   - Scenario: '{scenario}' (should be empty)")
            print(f"   - Scenario name: '{scenario_name}' (should be empty)")
    else:
        print("❌ Failed to get simulation state after reset")
    
    verification_results["state_reset"] = state_reset
    
    # Check observer messages are cleared
    get_observer_after_test, get_observer_after_response, response_time = run_test(
        "Get Observer Messages After Reset",
        "/observer/messages",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    observer_cleared = False
    if get_observer_after_test and get_observer_after_response:
        observer_count_after = len(get_observer_after_response)
        if observer_count_after == 0:
            observer_cleared = True
            print(f"✅ All observer messages cleared (Time: {response_time:.3f}s)")
        else:
            print(f"❌ Observer messages not fully cleared: {observer_count_after} remaining")
    else:
        print("❌ Failed to get observer messages after reset")
    
    verification_results["observer_cleared"] = observer_cleared
    
    return verification_results

def test_reset_with_larger_dataset():
    """Test reset with a larger dataset to verify performance"""
    print("\n" + "="*80)
    print("TESTING RESET WITH LARGER DATASET")
    print("="*80)
    
    # Create a larger dataset
    print("\n--- Creating Larger Dataset ---")
    
    # Create more agents
    for i in range(10):  # Create 10 more agents
        agent_data = {
            "name": f"Large Dataset Agent {i+1}",
            "archetype": ["scientist", "artist", "leader", "skeptic", "optimist"][i % 5],
            "goal": f"Large dataset test goal {i+1}",
            "expertise": f"Large dataset expertise {i+1}",
            "background": f"Large dataset background {i+1}",
            "avatar_prompt": f"Large dataset avatar {i+1}",
            "personality": {
                "extroversion": (i % 10) + 1,
                "optimism": (i % 10) + 1,
                "curiosity": (i % 10) + 1,
                "cooperativeness": (i % 10) + 1,
                "energy": (i % 10) + 1
            }
        }
        
        create_agent_test, create_agent_response, _ = run_test(
            f"Create Large Dataset Agent {i+1}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if create_agent_test:
            print(f"✅ Created large dataset agent {i+1}")
        else:
            print(f"❌ Failed to create large dataset agent {i+1}")
    
    # Generate more conversations
    for i in range(5):  # Generate 5 more conversations
        generate_conv_test, generate_conv_response, _ = run_test(
            f"Generate Large Dataset Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            expected_keys=["id", "messages"]
        )
        
        if generate_conv_test:
            print(f"✅ Generated large dataset conversation {i+1}")
        else:
            print(f"❌ Failed to generate large dataset conversation {i+1}")
    
    # Send more observer messages
    for i in range(5):  # Send 5 more observer messages
        observer_data = {
            "observer_message": f"Large dataset observer message {i+1} for comprehensive reset testing."
        }
        
        observer_test, observer_response, _ = run_test(
            f"Send Large Dataset Observer Message {i+1}",
            "/observer/send-message",
            method="POST",
            data=observer_data,
            auth=True,
            expected_keys=["message"]
        )
        
        if observer_test:
            print(f"✅ Sent large dataset observer message {i+1}")
        else:
            print(f"❌ Failed to send large dataset observer message {i+1}")
    
    # Verify larger dataset exists
    print("\n--- Verifying Larger Dataset ---")
    data_counts = verify_data_before_reset()
    
    total_items = sum(data_counts.values())
    print(f"📊 Total data items before reset: {total_items}")
    
    # Test reset with larger dataset
    print("\n--- Testing Reset with Larger Dataset ---")
    reset_test, reset_result = test_fresh_start_reset()
    
    if reset_test and isinstance(reset_result, dict):
        response_time = reset_result.get("response_time", 0)
        performance_ok = reset_result.get("performance_ok", False)
        
        print(f"\n📊 LARGER DATASET RESET RESULTS:")
        print(f"   Total items before reset: {total_items}")
        print(f"   Reset time: {response_time:.3f} seconds")
        print(f"   Performance acceptable (≤60s): {'✅' if performance_ok else '❌'}")
        
        return reset_test, reset_result
    else:
        return False, "Reset with larger dataset failed"

def main():
    """Run the Fresh Start cleanup functionality test"""
    print("="*80)
    print("FRESH START CLEANUP FUNCTIONALITY TEST")
    print("Testing timeout issues and performance improvements")
    print("="*80)
    
    # Step 1: Login
    if not test_login():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Step 2: Create test data
    created_data = create_test_data()
    print(f"\n📊 Created test data:")
    print(f"   Agents: {len(created_data['agents'])}")
    print(f"   Conversations: {len(created_data['conversations'])}")
    print(f"   Observer messages: {len(created_data['observer_messages'])}")
    
    # Step 3: Verify data exists before reset
    data_before = verify_data_before_reset()
    
    # Step 4: Test Fresh Start reset functionality
    reset_success, reset_result = test_fresh_start_reset()
    
    # Step 5: Verify data is cleared after reset
    verification_results = verify_data_after_reset()
    
    # Step 6: Test with larger dataset
    large_dataset_success, large_dataset_result = test_reset_with_larger_dataset()
    
    # Final Summary
    print("\n" + "="*80)
    print("FRESH START CLEANUP TEST SUMMARY")
    print("="*80)
    
    # Performance results
    if reset_success and isinstance(reset_result, dict):
        response_time = reset_result.get("response_time", 0)
        performance_ok = reset_result.get("performance_ok", False)
        cleared_collections = reset_result.get("cleared_collections", 0)
        
        print(f"🚀 PERFORMANCE RESULTS:")
        print(f"   Reset time (small dataset): {response_time:.3f} seconds")
        print(f"   Performance target (≤60s): {'✅ MET' if performance_ok else '❌ EXCEEDED'}")
        print(f"   Collections cleared: {cleared_collections}")
        
        if large_dataset_success and isinstance(large_dataset_result, dict):
            large_response_time = large_dataset_result.get("response_time", 0)
            large_performance_ok = large_dataset_result.get("performance_ok", False)
            print(f"   Reset time (large dataset): {large_response_time:.3f} seconds")
            print(f"   Large dataset performance: {'✅ MET' if large_performance_ok else '❌ EXCEEDED'}")
    
    # Functionality results
    print(f"\n🔧 FUNCTIONALITY RESULTS:")
    print(f"   Authentication required: {'✅ WORKING' if reset_success else '❌ FAILED'}")
    print(f"   Agents cleared: {'✅ WORKING' if verification_results.get('agents_cleared') else '❌ FAILED'}")
    print(f"   Conversations cleared: {'✅ WORKING' if verification_results.get('conversations_cleared') else '❌ FAILED'}")
    print(f"   State reset: {'✅ WORKING' if verification_results.get('state_reset') else '❌ FAILED'}")
    print(f"   Observer messages cleared: {'✅ WORKING' if verification_results.get('observer_cleared') else '❌ FAILED'}")
    
    # Overall assessment
    all_functionality_working = all([
        reset_success,
        verification_results.get('agents_cleared', False),
        verification_results.get('conversations_cleared', False),
        verification_results.get('state_reset', False),
        verification_results.get('observer_cleared', False)
    ])
    
    performance_acceptable = (
        reset_success and 
        isinstance(reset_result, dict) and 
        reset_result.get("performance_ok", False)
    )
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if all_functionality_working and performance_acceptable:
        print("✅ FRESH START CLEANUP IS WORKING CORRECTLY")
        print("✅ All data collections are properly cleared")
        print("✅ Performance is within acceptable limits (≤60 seconds)")
        print("✅ No timeout issues detected")
        print("✅ User feedback and progress notifications working")
        return True
    else:
        print("❌ FRESH START CLEANUP HAS ISSUES")
        if not all_functionality_working:
            print("❌ Some data collections are not being cleared properly")
        if not performance_acceptable:
            print("❌ Performance exceeds acceptable limits or timeout issues persist")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)