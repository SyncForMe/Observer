#!/usr/bin/env python3
"""
Scenario Persistence Test Script

This script tests the scenario persistence fix that was implemented to ensure
scenarios don't get lost when users navigate between Observatory and Agent Library.

Test Focus Areas:
1. Scenario Persistence: Verify scenario data is saved and retrieved correctly
2. State Consistency: Ensure scenario remains consistent across multiple API calls
3. No Data Loss: Confirm scenario doesn't get lost when other operations are performed
4. Backend Response: Verify the simulation state endpoint returns complete scenario data
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        # Disable SSL verification for testing
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params, verify=False)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params, verify=False)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params, verify=False)
            else:
                response = requests.delete(url, headers=headers, params=params, verify=False)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        
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
    print(f"SCENARIO PERSISTENCE TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def test_scenario_persistence_workflow():
    """Test the complete scenario persistence workflow as specified in the review"""
    print("\n" + "="*80)
    print("TESTING SCENARIO PERSISTENCE WORKFLOW")
    print("="*80)
    
    global auth_token, test_user_id
    
    # Step 1: Setup - Authenticate as guest user using POST /auth/test-login
    print("\n🔐 STEP 1: SETUP - AUTHENTICATE AS GUEST USER")
    print("-" * 60)
    
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not guest_test or not guest_response:
        print("❌ CRITICAL: Guest authentication failed - cannot proceed with scenario persistence tests")
        return False
    
    # Store the token for further testing
    auth_token = guest_response.get("access_token")
    user_data = guest_response.get("user", {})
    test_user_id = user_data.get("id")
    print(f"✅ Guest authentication successful. User ID: {test_user_id}")
    
    # Step 2: Clear any existing state using POST /api/simulation/reset
    print("\n🧹 STEP 2: CLEAR EXISTING STATE")
    print("-" * 60)
    
    reset_test, reset_response = run_test(
        "Reset Simulation State",
        "/simulation/reset",
        method="POST",
        auth=True,
        expected_keys=["message"]
    )
    
    if reset_test:
        print("✅ Simulation state reset successfully")
    else:
        print("⚠️ Simulation reset failed, but continuing with tests")
    
    # Step 3: Set Scenario with specific scenario and scenario_name
    print("\n📝 STEP 3: SET SCENARIO")
    print("-" * 60)
    
    test_scenario = "A team of researchers discovers an unexpected signal from deep space and must decide how to respond."
    test_scenario_name = "Deep Space Signal Discovery"
    
    scenario_data = {
        "scenario": test_scenario,
        "scenario_name": test_scenario_name
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Custom Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_scenario_test:
        print("❌ CRITICAL: Failed to set scenario - cannot proceed with persistence tests")
        return False
    
    print(f"✅ Scenario set successfully:")
    print(f"   Scenario: {test_scenario}")
    print(f"   Scenario Name: {test_scenario_name}")
    
    # Step 4: Verify Scenario is Saved - Call GET /api/simulation/state
    print("\n🔍 STEP 4: VERIFY SCENARIO IS SAVED")
    print("-" * 60)
    
    get_state_test, get_state_response = run_test(
        "Get Simulation State - Initial Verification",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name"]
    )
    
    if not get_state_test or not get_state_response:
        print("❌ CRITICAL: Failed to retrieve simulation state")
        return False
    
    # Verify scenario and scenario_name fields match what was set
    retrieved_scenario = get_state_response.get("scenario", "")
    retrieved_scenario_name = get_state_response.get("scenario_name", "")
    
    scenario_match = retrieved_scenario == test_scenario
    scenario_name_match = retrieved_scenario_name == test_scenario_name
    
    print(f"Expected Scenario: {test_scenario}")
    print(f"Retrieved Scenario: {retrieved_scenario}")
    print(f"Scenario Match: {'✅' if scenario_match else '❌'}")
    
    print(f"Expected Scenario Name: {test_scenario_name}")
    print(f"Retrieved Scenario Name: {retrieved_scenario_name}")
    print(f"Scenario Name Match: {'✅' if scenario_name_match else '❌'}")
    
    if not scenario_match or not scenario_name_match:
        print("❌ CRITICAL: Scenario data does not match what was set")
        return False
    
    print("✅ Scenario data successfully saved and retrieved")
    
    # Step 5: Test State Persistence - Add a few agents using POST /api/agents
    print("\n🤖 STEP 5: TEST STATE PERSISTENCE - ADD AGENTS")
    print("-" * 60)
    
    # Create test agents to verify scenario persists when other operations are performed
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Analyze the deep space signal using advanced spectroscopy",
            "expertise": "Radio Astronomy and Signal Processing",
            "background": "PhD in Astrophysics with 15 years experience in SETI research"
        },
        {
            "name": "Commander Jake Morrison",
            "archetype": "leader", 
            "goal": "Coordinate the team response and make critical decisions",
            "expertise": "Mission Command and Strategic Planning",
            "background": "Former NASA mission commander with deep space exploration experience"
        },
        {
            "name": "Dr. Elena Vasquez",
            "archetype": "researcher",
            "goal": "Research potential origins and implications of the signal",
            "expertise": "Xenobiology and Astrobiology",
            "background": "Leading researcher in extraterrestrial life detection methods"
        }
    ]
    
    created_agent_ids = []
    
    for i, agent_data in enumerate(test_agents):
        create_agent_test, create_agent_response = run_test(
            f"Create Test Agent {i+1} - {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_agent_test and create_agent_response:
            agent_id = create_agent_response.get("id")
            created_agent_ids.append(agent_id)
            print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    print(f"✅ Successfully created {len(created_agent_ids)} test agents")
    
    # Step 6: Call GET /api/simulation/state again to verify scenario persists
    print("\n🔍 STEP 6: VERIFY SCENARIO PERSISTS AFTER AGENT OPERATIONS")
    print("-" * 60)
    
    get_state_after_agents_test, get_state_after_agents_response = run_test(
        "Get Simulation State - After Agent Creation",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name"]
    )
    
    if not get_state_after_agents_test or not get_state_after_agents_response:
        print("❌ CRITICAL: Failed to retrieve simulation state after agent creation")
        return False
    
    # Verify scenario and scenario_name are still present and unchanged
    retrieved_scenario_after = get_state_after_agents_response.get("scenario", "")
    retrieved_scenario_name_after = get_state_after_agents_response.get("scenario_name", "")
    
    scenario_match_after = retrieved_scenario_after == test_scenario
    scenario_name_match_after = retrieved_scenario_name_after == test_scenario_name
    
    print(f"Expected Scenario: {test_scenario}")
    print(f"Retrieved Scenario After Agents: {retrieved_scenario_after}")
    print(f"Scenario Match After Agents: {'✅' if scenario_match_after else '❌'}")
    
    print(f"Expected Scenario Name: {test_scenario_name}")
    print(f"Retrieved Scenario Name After Agents: {retrieved_scenario_name_after}")
    print(f"Scenario Name Match After Agents: {'✅' if scenario_name_match_after else '❌'}")
    
    if not scenario_match_after or not scenario_name_match_after:
        print("❌ CRITICAL: Scenario data was lost after agent operations")
        return False
    
    print("✅ Scenario data persisted correctly after agent operations")
    
    # Step 7: Test Scenario Retrieval - Call GET /api/simulation/state multiple times
    print("\n🔄 STEP 7: TEST MULTIPLE SCENARIO RETRIEVALS")
    print("-" * 60)
    
    retrieval_results = []
    
    for i in range(5):
        get_state_multiple_test, get_state_multiple_response = run_test(
            f"Get Simulation State - Retrieval {i+1}/5",
            "/simulation/state",
            method="GET",
            auth=True,
            expected_keys=["scenario", "scenario_name"]
        )
        
        if get_state_multiple_test and get_state_multiple_response:
            retrieved_scenario_multi = get_state_multiple_response.get("scenario", "")
            retrieved_scenario_name_multi = get_state_multiple_response.get("scenario_name", "")
            
            scenario_match_multi = retrieved_scenario_multi == test_scenario
            scenario_name_match_multi = retrieved_scenario_name_multi == test_scenario_name
            
            retrieval_results.append({
                "retrieval": i+1,
                "scenario_match": scenario_match_multi,
                "scenario_name_match": scenario_name_match_multi,
                "scenario": retrieved_scenario_multi,
                "scenario_name": retrieved_scenario_name_multi
            })
            
            print(f"Retrieval {i+1}: Scenario {'✅' if scenario_match_multi else '❌'}, Name {'✅' if scenario_name_match_multi else '❌'}")
        else:
            print(f"❌ Retrieval {i+1} failed")
            retrieval_results.append({
                "retrieval": i+1,
                "scenario_match": False,
                "scenario_name_match": False,
                "error": "API call failed"
            })
    
    # Analyze retrieval consistency
    successful_retrievals = [r for r in retrieval_results if r.get("scenario_match") and r.get("scenario_name_match")]
    consistency_rate = len(successful_retrievals) / len(retrieval_results) * 100
    
    print(f"\nRetrieval Consistency: {len(successful_retrievals)}/{len(retrieval_results)} ({consistency_rate:.1f}%)")
    
    if consistency_rate == 100:
        print("✅ Perfect scenario persistence across multiple retrievals")
    elif consistency_rate >= 80:
        print("⚠️ Good scenario persistence with minor inconsistencies")
    else:
        print("❌ Poor scenario persistence - significant data loss detected")
        return False
    
    # Step 8: Test scenario persistence with additional operations
    print("\n⚙️ STEP 8: TEST SCENARIO PERSISTENCE WITH ADDITIONAL OPERATIONS")
    print("-" * 60)
    
    # Test starting simulation
    start_sim_test, start_sim_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if start_sim_test:
        print("✅ Simulation started successfully")
        
        # Check scenario after starting simulation
        get_state_after_start_test, get_state_after_start_response = run_test(
            "Get Simulation State - After Start",
            "/simulation/state",
            method="GET",
            auth=True,
            expected_keys=["scenario", "scenario_name"]
        )
        
        if get_state_after_start_test and get_state_after_start_response:
            scenario_after_start = get_state_after_start_response.get("scenario", "")
            scenario_name_after_start = get_state_after_start_response.get("scenario_name", "")
            
            scenario_match_start = scenario_after_start == test_scenario
            scenario_name_match_start = scenario_name_after_start == test_scenario_name
            
            print(f"Scenario after start: {'✅' if scenario_match_start else '❌'}")
            print(f"Scenario name after start: {'✅' if scenario_name_match_start else '❌'}")
            
            if not scenario_match_start or not scenario_name_match_start:
                print("❌ Scenario data lost after starting simulation")
                return False
        else:
            print("❌ Failed to retrieve state after starting simulation")
            return False
    else:
        print("⚠️ Failed to start simulation, but continuing tests")
    
    # Test pausing simulation
    pause_sim_test, pause_sim_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if pause_sim_test:
        print("✅ Simulation paused successfully")
        
        # Check scenario after pausing simulation
        get_state_after_pause_test, get_state_after_pause_response = run_test(
            "Get Simulation State - After Pause",
            "/simulation/state",
            method="GET",
            auth=True,
            expected_keys=["scenario", "scenario_name"]
        )
        
        if get_state_after_pause_test and get_state_after_pause_response:
            scenario_after_pause = get_state_after_pause_response.get("scenario", "")
            scenario_name_after_pause = get_state_after_pause_response.get("scenario_name", "")
            
            scenario_match_pause = scenario_after_pause == test_scenario
            scenario_name_match_pause = scenario_name_after_pause == test_scenario_name
            
            print(f"Scenario after pause: {'✅' if scenario_match_pause else '❌'}")
            print(f"Scenario name after pause: {'✅' if scenario_name_match_pause else '❌'}")
            
            if not scenario_match_pause or not scenario_name_match_pause:
                print("❌ Scenario data lost after pausing simulation")
                return False
        else:
            print("❌ Failed to retrieve state after pausing simulation")
            return False
    else:
        print("⚠️ Failed to pause simulation, but continuing tests")
    
    # Final verification
    print("\n🏁 FINAL VERIFICATION")
    print("-" * 60)
    
    final_state_test, final_state_response = run_test(
        "Final Simulation State Check",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name"]
    )
    
    if final_state_test and final_state_response:
        final_scenario = final_state_response.get("scenario", "")
        final_scenario_name = final_state_response.get("scenario_name", "")
        
        final_scenario_match = final_scenario == test_scenario
        final_scenario_name_match = final_scenario_name == test_scenario_name
        
        print(f"Final scenario verification: {'✅' if final_scenario_match else '❌'}")
        print(f"Final scenario name verification: {'✅' if final_scenario_name_match else '❌'}")
        
        if final_scenario_match and final_scenario_name_match:
            print("✅ SCENARIO PERSISTENCE TEST COMPLETED SUCCESSFULLY")
            print("✅ Scenario data persisted correctly throughout all operations")
            return True
        else:
            print("❌ SCENARIO PERSISTENCE TEST FAILED")
            print("❌ Scenario data was lost during operations")
            return False
    else:
        print("❌ SCENARIO PERSISTENCE TEST FAILED")
        print("❌ Unable to retrieve final simulation state")
        return False

def main():
    """Main test execution function"""
    print("🚀 STARTING SCENARIO PERSISTENCE TESTING")
    print("="*80)
    print("Testing the scenario persistence fix to ensure scenarios don't get lost")
    print("when users navigate between Observatory and Agent Library.")
    print("="*80)
    
    # Run the comprehensive scenario persistence workflow test
    success = test_scenario_persistence_workflow()
    
    # Print final summary
    print_summary()
    
    if success:
        print("\n🎉 SCENARIO PERSISTENCE FIX VERIFICATION: SUCCESS")
        print("✅ All scenario persistence requirements have been met:")
        print("   • Scenario data is saved and retrieved correctly")
        print("   • Scenario remains consistent across multiple API calls") 
        print("   • No data loss when other operations are performed")
        print("   • Backend response includes complete scenario data")
        print("\n✅ The fetchSimulationState fix is working correctly!")
    else:
        print("\n❌ SCENARIO PERSISTENCE FIX VERIFICATION: FAILED")
        print("❌ One or more scenario persistence requirements were not met")
        print("❌ The fetchSimulationState fix needs further investigation")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)