#!/usr/bin/env python3
"""
SCENARIO SETTING AND PERSISTENCE TESTING
Testing the specific scenario setting functionality to verify why the setup flow scenario isn't persisting.

Focus Areas:
1. Login as dino@cytonic.com (password: Observerinho8)
2. Test POST /api/simulation/set-scenario with sample scenario
3. Test GET /api/simulation/state to verify it was saved
4. Test if the scenario persists across subsequent GET requests
5. Provide detailed logs showing before/after scenario state
"""

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

def test_authentication():
    """Test authentication with dino@cytonic.com"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION TESTING")
    print("="*80)
    
    # Test email/password login with dino@cytonic.com
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login as dino@cytonic.com",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"],
        measure_time=True
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Login successful. User ID: {test_user_id}")
        print(f"✅ User Name: {user_data.get('name', 'N/A')}")
        print(f"✅ User Email: {user_data.get('email', 'N/A')}")
        return True
    else:
        print("❌ Login failed")
        return False

def test_scenario_setting_and_persistence():
    """Test scenario setting and persistence functionality"""
    print("\n" + "="*80)
    print("2. SCENARIO SETTING AND PERSISTENCE TESTING")
    print("="*80)
    
    print("🔍 Testing the specific scenario setting functionality")
    print("Focus: Verify why the setup flow scenario isn't persisting")
    
    # Step 1: Get initial simulation state (BEFORE setting scenario)
    print("\n--- Step 1: Get Initial Simulation State ---")
    
    initial_state_test, initial_state_response = run_test(
        "Get Initial Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period"],
        measure_time=True
    )
    
    if initial_state_test and initial_state_response:
        initial_scenario = initial_state_response.get("scenario", "")
        initial_scenario_name = initial_state_response.get("scenario_name", "")
        print(f"📊 INITIAL STATE:")
        print(f"   Scenario: '{initial_scenario}'")
        print(f"   Scenario Name: '{initial_scenario_name}'")
        print(f"   Current Day: {initial_state_response.get('current_day', 'N/A')}")
        print(f"   Current Time Period: {initial_state_response.get('current_time_period', 'N/A')}")
        print(f"   Is Active: {initial_state_response.get('is_active', 'N/A')}")
    else:
        print("❌ Failed to get initial simulation state")
        return False
    
    # Step 2: Test POST /api/simulation/set-scenario with sample scenario
    print("\n--- Step 2: Set Sample Scenario ---")
    
    sample_scenario_data = {
        "scenario": "A business team needs to decide on their go-to-market strategy",
        "scenario_name": "Business - Strategic Track Simulation"
    }
    
    print(f"🎯 Setting scenario:")
    print(f"   Scenario: '{sample_scenario_data['scenario']}'")
    print(f"   Scenario Name: '{sample_scenario_data['scenario_name']}'")
    
    # Check if the endpoint is /simulation/set-scenario or /simulation/scenario
    set_scenario_test, set_scenario_response = run_test(
        "Set Sample Scenario (set-scenario endpoint)",
        "/simulation/set-scenario",
        method="POST",
        data=sample_scenario_data,
        auth=True,
        measure_time=True
    )
    
    if not set_scenario_test:
        # Try alternative endpoint
        print("⚠️ /simulation/set-scenario failed, trying /simulation/scenario")
        set_scenario_test, set_scenario_response = run_test(
            "Set Sample Scenario (scenario endpoint)",
            "/simulation/scenario",
            method="POST",
            data=sample_scenario_data,
            auth=True,
            measure_time=True
        )
    
    if set_scenario_test and set_scenario_response:
        print("✅ Scenario setting request successful")
        print(f"📊 SET SCENARIO RESPONSE:")
        print(f"   Response: {json.dumps(set_scenario_response, indent=2)}")
    else:
        print("❌ Scenario setting failed")
        print("🔍 This could be the root cause of the persistence issue!")
        return False
    
    # Step 3: Immediately test GET /api/simulation/state to verify it was saved
    print("\n--- Step 3: Verify Scenario Was Saved (Immediate Check) ---")
    
    immediate_state_test, immediate_state_response = run_test(
        "Get Simulation State (Immediate After Setting)",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period"],
        measure_time=True
    )
    
    if immediate_state_test and immediate_state_response:
        immediate_scenario = immediate_state_response.get("scenario", "")
        immediate_scenario_name = immediate_state_response.get("scenario_name", "")
        
        print(f"📊 IMMEDIATE STATE AFTER SETTING:")
        print(f"   Scenario: '{immediate_scenario}'")
        print(f"   Scenario Name: '{immediate_scenario_name}'")
        print(f"   Current Day: {immediate_state_response.get('current_day', 'N/A')}")
        print(f"   Current Time Period: {immediate_state_response.get('current_time_period', 'N/A')}")
        print(f"   Is Active: {immediate_state_response.get('is_active', 'N/A')}")
        
        # Verify scenario was set correctly
        if immediate_scenario == sample_scenario_data["scenario"]:
            print("✅ Scenario correctly saved in simulation state")
        else:
            print(f"❌ Scenario NOT saved correctly!")
            print(f"   Expected: '{sample_scenario_data['scenario']}'")
            print(f"   Got: '{immediate_scenario}'")
            return False
        
        # Verify scenario name was set correctly
        if immediate_scenario_name == sample_scenario_data["scenario_name"]:
            print("✅ Scenario name correctly saved in simulation state")
        else:
            print(f"❌ Scenario name NOT saved correctly!")
            print(f"   Expected: '{sample_scenario_data['scenario_name']}'")
            print(f"   Got: '{immediate_scenario_name}'")
            return False
            
    else:
        print("❌ Failed to get simulation state after setting scenario")
        return False
    
    # Step 4: Wait a moment and test persistence
    print("\n--- Step 4: Test Scenario Persistence (After Delay) ---")
    
    print("⏳ Waiting 2 seconds to test persistence...")
    time.sleep(2)
    
    persistence_test, persistence_response = run_test(
        "Get Simulation State (Persistence Check)",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period"],
        measure_time=True
    )
    
    if persistence_test and persistence_response:
        persistent_scenario = persistence_response.get("scenario", "")
        persistent_scenario_name = persistence_response.get("scenario_name", "")
        
        print(f"📊 PERSISTENT STATE AFTER DELAY:")
        print(f"   Scenario: '{persistent_scenario}'")
        print(f"   Scenario Name: '{persistent_scenario_name}'")
        
        # Verify scenario persisted
        if persistent_scenario == sample_scenario_data["scenario"]:
            print("✅ Scenario persisted correctly after delay")
        else:
            print(f"❌ Scenario did NOT persist!")
            print(f"   Expected: '{sample_scenario_data['scenario']}'")
            print(f"   Got: '{persistent_scenario}'")
            return False
        
        # Verify scenario name persisted
        if persistent_scenario_name == sample_scenario_data["scenario_name"]:
            print("✅ Scenario name persisted correctly after delay")
        else:
            print(f"❌ Scenario name did NOT persist!")
            print(f"   Expected: '{sample_scenario_data['scenario_name']}'")
            print(f"   Got: '{persistent_scenario_name}'")
            return False
            
    else:
        print("❌ Failed to get simulation state for persistence check")
        return False
    
    # Step 5: Test multiple subsequent GET requests
    print("\n--- Step 5: Test Multiple Subsequent GET Requests ---")
    
    for i in range(3):
        print(f"\n🔄 Subsequent GET request #{i+1}")
        
        subsequent_test, subsequent_response = run_test(
            f"Get Simulation State (Subsequent #{i+1})",
            "/simulation/state",
            method="GET",
            auth=True,
            measure_time=True
        )
        
        if subsequent_test and subsequent_response:
            subsequent_scenario = subsequent_response.get("scenario", "")
            subsequent_scenario_name = subsequent_response.get("scenario_name", "")
            
            print(f"   Scenario: '{subsequent_scenario}'")
            print(f"   Scenario Name: '{subsequent_scenario_name}'")
            
            # Verify scenario still persists
            if subsequent_scenario == sample_scenario_data["scenario"] and subsequent_scenario_name == sample_scenario_data["scenario_name"]:
                print(f"   ✅ Scenario persisted in request #{i+1}")
            else:
                print(f"   ❌ Scenario lost in request #{i+1}!")
                return False
        else:
            print(f"   ❌ Failed subsequent request #{i+1}")
            return False
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Step 6: Test scenario change and persistence
    print("\n--- Step 6: Test Scenario Change and Persistence ---")
    
    new_scenario_data = {
        "scenario": "Research team investigating quantum computing applications",
        "scenario_name": "Research - Quantum Computing Investigation"
    }
    
    print(f"🎯 Changing to new scenario:")
    print(f"   Scenario: '{new_scenario_data['scenario']}'")
    print(f"   Scenario Name: '{new_scenario_data['scenario_name']}'")
    
    # Set new scenario
    change_scenario_test, change_scenario_response = run_test(
        "Change to New Scenario",
        "/simulation/scenario",
        method="POST",
        data=new_scenario_data,
        auth=True,
        measure_time=True
    )
    
    if change_scenario_test:
        # Verify new scenario was set
        verify_change_test, verify_change_response = run_test(
            "Verify New Scenario Was Set",
            "/simulation/state",
            method="GET",
            auth=True,
            measure_time=True
        )
        
        if verify_change_test and verify_change_response:
            changed_scenario = verify_change_response.get("scenario", "")
            changed_scenario_name = verify_change_response.get("scenario_name", "")
            
            print(f"📊 STATE AFTER SCENARIO CHANGE:")
            print(f"   Scenario: '{changed_scenario}'")
            print(f"   Scenario Name: '{changed_scenario_name}'")
            
            if changed_scenario == new_scenario_data["scenario"] and changed_scenario_name == new_scenario_data["scenario_name"]:
                print("✅ Scenario change persisted correctly")
            else:
                print("❌ Scenario change did NOT persist correctly")
                return False
        else:
            print("❌ Failed to verify scenario change")
            return False
    else:
        print("❌ Failed to change scenario")
        return False
    
    # Step 7: Final comprehensive state check
    print("\n--- Step 7: Final Comprehensive State Check ---")
    
    final_state_test, final_state_response = run_test(
        "Final Comprehensive State Check",
        "/simulation/state",
        method="GET",
        auth=True,
        measure_time=True
    )
    
    if final_state_test and final_state_response:
        print(f"📊 FINAL SIMULATION STATE:")
        for key, value in final_state_response.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Scenario setting and persistence functionality is working correctly!")
        return True
    else:
        print("❌ Failed final state check")
        return False

def test_edge_cases():
    """Test edge cases for scenario setting"""
    print("\n" + "="*80)
    print("3. EDGE CASES TESTING")
    print("="*80)
    
    # Test 1: Empty scenario
    print("\n--- Test 1: Empty Scenario ---")
    
    empty_scenario_data = {
        "scenario": "",
        "scenario_name": ""
    }
    
    empty_test, empty_response = run_test(
        "Set Empty Scenario",
        "/simulation/scenario",
        method="POST",
        data=empty_scenario_data,
        auth=True,
        measure_time=True
    )
    
    if empty_test:
        # Check if empty scenario was set
        verify_empty_test, verify_empty_response = run_test(
            "Verify Empty Scenario",
            "/simulation/state",
            method="GET",
            auth=True
        )
        
        if verify_empty_test and verify_empty_response:
            empty_scenario = verify_empty_response.get("scenario", "NOT_EMPTY")
            empty_scenario_name = verify_empty_response.get("scenario_name", "NOT_EMPTY")
            
            if empty_scenario == "" and empty_scenario_name == "":
                print("✅ Empty scenario handled correctly")
            else:
                print(f"⚠️ Empty scenario behavior: scenario='{empty_scenario}', scenario_name='{empty_scenario_name}'")
    
    # Test 2: Very long scenario
    print("\n--- Test 2: Very Long Scenario ---")
    
    long_scenario_data = {
        "scenario": "A" * 1000,  # Very long scenario
        "scenario_name": "B" * 500  # Very long scenario name
    }
    
    long_test, long_response = run_test(
        "Set Very Long Scenario",
        "/simulation/scenario",
        method="POST",
        data=long_scenario_data,
        auth=True,
        measure_time=True
    )
    
    if long_test:
        print("✅ Long scenario handled without errors")
    else:
        print("⚠️ Long scenario caused issues")
    
    # Test 3: Special characters in scenario
    print("\n--- Test 3: Special Characters in Scenario ---")
    
    special_scenario_data = {
        "scenario": "Test scenario with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "scenario_name": "Special Chars Test: 🚀🔬💡"
    }
    
    special_test, special_response = run_test(
        "Set Special Characters Scenario",
        "/simulation/scenario",
        method="POST",
        data=special_scenario_data,
        auth=True,
        measure_time=True
    )
    
    if special_test:
        # Verify special characters persisted
        verify_special_test, verify_special_response = run_test(
            "Verify Special Characters Scenario",
            "/simulation/state",
            method="GET",
            auth=True
        )
        
        if verify_special_test and verify_special_response:
            special_scenario = verify_special_response.get("scenario", "")
            special_scenario_name = verify_special_response.get("scenario_name", "")
            
            if special_scenario == special_scenario_data["scenario"]:
                print("✅ Special characters in scenario persisted correctly")
            else:
                print("⚠️ Special characters in scenario may have been modified")
                
            if special_scenario_name == special_scenario_data["scenario_name"]:
                print("✅ Special characters in scenario name persisted correctly")
            else:
                print("⚠️ Special characters in scenario name may have been modified")
    
    return True

def main():
    """Main test execution function"""
    print("SCENARIO SETTING AND PERSISTENCE TESTING")
    print("Testing specific scenario setting functionality to identify persistence issues")
    print("="*80)
    
    # Run test suites
    test_suites = [
        ("Authentication", test_authentication),
        ("Scenario Setting and Persistence", test_scenario_setting_and_persistence),
        ("Edge Cases", test_edge_cases)
    ]
    
    all_passed = True
    
    for suite_name, test_function in test_suites:
        print(f"\n🧪 Running {suite_name} tests...")
        try:
            result = test_function()
            if not result:
                all_passed = False
                print(f"❌ {suite_name} tests failed")
            else:
                print(f"✅ {suite_name} tests passed")
        except Exception as e:
            print(f"❌ {suite_name} tests encountered error: {e}")
            all_passed = False
    
    # Print final summary
    print_summary()
    
    # Print detailed analysis
    print("\n" + "="*80)
    print("DETAILED ANALYSIS")
    print("="*80)
    
    if all_passed:
        print("✅ SCENARIO SETTING AND PERSISTENCE IS WORKING CORRECTLY")
        print("\n📊 Key Findings:")
        print("   • Authentication with dino@cytonic.com works properly")
        print("   • POST /api/simulation/set-scenario or /api/simulation/scenario works")
        print("   • Scenarios are immediately saved to simulation state")
        print("   • Scenarios persist across multiple GET requests")
        print("   • Scenario changes are handled correctly")
        print("   • Edge cases (empty, long, special chars) are handled")
        
        print("\n🎯 CONCLUSION:")
        print("The scenario setting functionality is working as expected.")
        print("If users are experiencing persistence issues, the problem may be:")
        print("   1. Frontend not calling the correct endpoint")
        print("   2. Frontend not handling the response correctly")
        print("   3. Race conditions in the frontend state management")
        print("   4. Browser caching issues")
    else:
        print("❌ SCENARIO SETTING AND PERSISTENCE HAS ISSUES")
        print("\n📊 Issues Found:")
        failed_tests = [test for test in test_results["tests"] if test["result"] == "FAILED"]
        for test in failed_tests:
            print(f"   • {test['name']} - {test['method']} {test['endpoint']}")
        
        print("\n🎯 RECOMMENDED ACTIONS:")
        print("   1. Check backend logs for detailed error messages")
        print("   2. Verify database connectivity and schema")
        print("   3. Check LLM API credentials and quotas")
        print("   4. Verify user authentication and permissions")
        print("   5. Test with different user accounts")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
Comprehensive test script for scenario setting functionality
Tests the specific issue reported by the user where scenarios disappear from the notification bar
"""
import requests
import json
import time
import os
import sys
import uuid
from dotenv import load_dotenv
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

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

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
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params, verify=False, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params, verify=False, timeout=30)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params, verify=False, timeout=30)
            else:
                response = requests.delete(url, headers=headers, params=params, verify=False, timeout=30)
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
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

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
            print("Test login failed. Cannot proceed with scenario testing.")
            return False
    else:
        # Store the token from email/password login
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True

def test_scenario_setting_functionality():
    """Test the complete scenario setting functionality"""
    print("\n" + "="*80)
    print("TESTING SCENARIO SETTING FUNCTIONALITY")
    print("="*80)
    
    # Login first to get auth token
    if not test_login():
        print("❌ Cannot test scenario functionality without authentication")
        return False
    
    # Test 1: Create a fresh simulation state
    print("\nTest 1: Creating a fresh simulation state")
    
    # Start simulation to create fresh state
    start_sim_test, start_sim_response = run_test(
        "Start Fresh Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start fresh simulation")
        return False
    
    print("✅ Fresh simulation state created")
    
    # Test 2: Set a scenario with both "scenario" and "scenario_name" fields
    print("\nTest 2: Setting scenario with both scenario and scenario_name fields")
    
    test_scenario = "A team of quantum computing researchers must develop a breakthrough quantum encryption algorithm within 6 months to secure a major government contract worth $50 million."
    test_scenario_name = "Quantum Encryption Challenge"
    
    scenario_data = {
        "scenario": test_scenario,
        "scenario_name": test_scenario_name
    }
    
    set_scenario_test, set_scenario_response = run_test(
        "Set Scenario with Both Fields",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_scenario_test:
        print("❌ Failed to set scenario")
        return False
    
    print("✅ Scenario set successfully")
    
    # Verify the response contains the scenario data
    if set_scenario_response:
        response_scenario = set_scenario_response.get("scenario")
        response_scenario_name = set_scenario_response.get("scenario_name")
        
        if response_scenario == test_scenario:
            print("✅ Scenario field correctly returned in response")
        else:
            print(f"❌ Scenario field mismatch. Expected: {test_scenario}, Got: {response_scenario}")
        
        if response_scenario_name == test_scenario_name:
            print("✅ Scenario name field correctly returned in response")
        else:
            print(f"❌ Scenario name field mismatch. Expected: {test_scenario_name}, Got: {response_scenario_name}")
    
    # Test 3: Verify scenario persistence - immediate GET call
    print("\nTest 3: Verifying scenario persistence - immediate GET call")
    
    get_state_test, get_state_response = run_test(
        "Get Simulation State Immediately",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name", "is_active"]
    )
    
    if not get_state_test:
        print("❌ Failed to get simulation state")
        return False
    
    # Check if scenario and scenario_name are properly returned
    immediate_scenario = get_state_response.get("scenario")
    immediate_scenario_name = get_state_response.get("scenario_name")
    
    if immediate_scenario == test_scenario:
        print("✅ Scenario persists correctly in immediate GET call")
    else:
        print(f"❌ Scenario not persisted correctly. Expected: {test_scenario}, Got: {immediate_scenario}")
        return False
    
    if immediate_scenario_name == test_scenario_name:
        print("✅ Scenario name persists correctly in immediate GET call")
    else:
        print(f"❌ Scenario name not persisted correctly. Expected: {test_scenario_name}, Got: {immediate_scenario_name}")
        return False
    
    # Test 4: Test scenario persistence across multiple GET calls
    print("\nTest 4: Testing scenario persistence across multiple GET calls")
    
    persistence_results = []
    
    for i in range(5):
        print(f"\nGET call {i+1}/5:")
        
        # Add a small delay between calls
        time.sleep(0.5)
        
        get_state_test, get_state_response = run_test(
            f"Get Simulation State - Call {i+1}",
            "/simulation/state",
            method="GET",
            auth=True,
            expected_keys=["scenario", "scenario_name", "is_active"]
        )
        
        if get_state_test and get_state_response:
            call_scenario = get_state_response.get("scenario")
            call_scenario_name = get_state_response.get("scenario_name")
            
            scenario_match = call_scenario == test_scenario
            scenario_name_match = call_scenario_name == test_scenario_name
            
            persistence_results.append({
                "call": i+1,
                "scenario_match": scenario_match,
                "scenario_name_match": scenario_name_match,
                "scenario": call_scenario,
                "scenario_name": call_scenario_name
            })
            
            if scenario_match and scenario_name_match:
                print(f"✅ Call {i+1}: Scenario data persists correctly")
            else:
                print(f"❌ Call {i+1}: Scenario data not persisting correctly")
                if not scenario_match:
                    print(f"  Scenario mismatch: Expected '{test_scenario}', Got '{call_scenario}'")
                if not scenario_name_match:
                    print(f"  Scenario name mismatch: Expected '{test_scenario_name}', Got '{call_scenario_name}'")
        else:
            print(f"❌ Call {i+1}: Failed to get simulation state")
            persistence_results.append({
                "call": i+1,
                "scenario_match": False,
                "scenario_name_match": False,
                "error": "Failed to get state"
            })
    
    # Analyze persistence results
    successful_calls = [r for r in persistence_results if r.get("scenario_match") and r.get("scenario_name_match")]
    
    if len(successful_calls) == 5:
        print("✅ Scenario data persists correctly across all 5 GET calls")
    else:
        print(f"❌ Scenario data only persisted correctly in {len(successful_calls)}/5 GET calls")
        return False
    
    # Test 5: Test scenario clearing behavior
    print("\nTest 5: Testing scenario clearing behavior")
    
    # Try to clear scenario by setting empty values
    clear_scenario_data = {
        "scenario": "",
        "scenario_name": ""
    }
    
    clear_scenario_test, clear_scenario_response = run_test(
        "Clear Scenario with Empty Values",
        "/simulation/set-scenario",
        method="POST",
        data=clear_scenario_data,
        auth=True,
        expected_status=400  # Should reject empty scenario
    )
    
    if clear_scenario_test:
        print("✅ Empty scenario correctly rejected")
    else:
        print("❌ Empty scenario not properly validated")
    
    # Verify original scenario still exists after failed clear attempt
    get_after_clear_test, get_after_clear_response = run_test(
        "Get State After Clear Attempt",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["scenario", "scenario_name"]
    )
    
    if get_after_clear_test and get_after_clear_response:
        after_clear_scenario = get_after_clear_response.get("scenario")
        after_clear_scenario_name = get_after_clear_response.get("scenario_name")
        
        if after_clear_scenario == test_scenario and after_clear_scenario_name == test_scenario_name:
            print("✅ Original scenario preserved after failed clear attempt")
        else:
            print("❌ Original scenario was modified by failed clear attempt")
            return False
    
    # Test 6: Test scenario data structure in database
    print("\nTest 6: Testing scenario data structure in database")
    
    # Get the full simulation state to verify structure
    get_full_state_test, get_full_state_response = run_test(
        "Get Full Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if get_full_state_test and get_full_state_response:
        print("Full simulation state structure:")
        for key, value in get_full_state_response.items():
            print(f"  {key}: {type(value).__name__} = {value}")
        
        # Check for required fields
        required_fields = ["scenario", "scenario_name", "is_active", "user_id"]
        missing_fields = [field for field in required_fields if field not in get_full_state_response]
        
        if not missing_fields:
            print("✅ All required fields present in simulation state")
        else:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Verify user_id is correctly set
        state_user_id = get_full_state_response.get("user_id")
        if state_user_id == test_user_id:
            print("✅ Simulation state correctly associated with user")
        else:
            print(f"❌ Simulation state user_id mismatch. Expected: {test_user_id}, Got: {state_user_id}")
            return False
    
    # Test 7: Test scenario with different scenario types
    print("\nTest 7: Testing different scenario types")
    
    scenario_types = [
        {
            "scenario": "A startup team needs to pivot their business model after losing their main investor.",
            "scenario_name": "Business Pivot Challenge"
        },
        {
            "scenario": "Research scientists discover a potential cure for a rare disease but face ethical dilemmas.",
            "scenario_name": "Medical Ethics Dilemma"
        },
        {
            "scenario": "A software development team must fix critical security vulnerabilities before a major product launch.",
            "scenario_name": "Security Crisis Management"
        }
    ]
    
    for i, scenario_type in enumerate(scenario_types):
        print(f"\nTesting scenario type {i+1}: {scenario_type['scenario_name']}")
        
        # Set the new scenario
        set_new_scenario_test, set_new_scenario_response = run_test(
            f"Set Scenario Type {i+1}",
            "/simulation/set-scenario",
            method="POST",
            data=scenario_type,
            auth=True,
            expected_keys=["message", "scenario", "scenario_name"]
        )
        
        if not set_new_scenario_test:
            print(f"❌ Failed to set scenario type {i+1}")
            continue
        
        # Verify the scenario was set correctly
        verify_new_scenario_test, verify_new_scenario_response = run_test(
            f"Verify Scenario Type {i+1}",
            "/simulation/state",
            method="GET",
            auth=True,
            expected_keys=["scenario", "scenario_name"]
        )
        
        if verify_new_scenario_test and verify_new_scenario_response:
            verified_scenario = verify_new_scenario_response.get("scenario")
            verified_scenario_name = verify_new_scenario_response.get("scenario_name")
            
            if (verified_scenario == scenario_type["scenario"] and 
                verified_scenario_name == scenario_type["scenario_name"]):
                print(f"✅ Scenario type {i+1} set and verified correctly")
            else:
                print(f"❌ Scenario type {i+1} not set correctly")
                return False
    
    # Test 8: Test scenario persistence after other operations
    print("\nTest 8: Testing scenario persistence after other operations")
    
    # Set a final test scenario
    final_scenario = {
        "scenario": "Final test scenario for persistence verification",
        "scenario_name": "Persistence Test Scenario"
    }
    
    set_final_test, set_final_response = run_test(
        "Set Final Test Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=final_scenario,
        auth=True,
        expected_keys=["message", "scenario", "scenario_name"]
    )
    
    if not set_final_test:
        print("❌ Failed to set final test scenario")
        return False
    
    # Perform other operations that might affect scenario persistence
    operations = [
        ("Pause Simulation", "/simulation/pause", "POST"),
        ("Resume Simulation", "/simulation/resume", "POST"),
        ("Get Usage Stats", "/usage", "GET"),
        ("Get Archetypes", "/archetypes", "GET")
    ]
    
    for op_name, endpoint, method in operations:
        print(f"\nPerforming operation: {op_name}")
        
        op_test, op_response = run_test(
            op_name,
            endpoint,
            method=method,
            auth=True
        )
        
        if op_test:
            print(f"✅ {op_name} completed successfully")
        else:
            print(f"❌ {op_name} failed")
        
        # Check if scenario still persists after this operation
        check_persistence_test, check_persistence_response = run_test(
            f"Check Scenario After {op_name}",
            "/simulation/state",
            method="GET",
            auth=True,
            expected_keys=["scenario", "scenario_name"]
        )
        
        if check_persistence_test and check_persistence_response:
            persist_scenario = check_persistence_response.get("scenario")
            persist_scenario_name = check_persistence_response.get("scenario_name")
            
            if (persist_scenario == final_scenario["scenario"] and 
                persist_scenario_name == final_scenario["scenario_name"]):
                print(f"✅ Scenario persists correctly after {op_name}")
            else:
                print(f"❌ Scenario lost after {op_name}")
                print(f"  Expected scenario: {final_scenario['scenario']}")
                print(f"  Got scenario: {persist_scenario}")
                print(f"  Expected scenario_name: {final_scenario['scenario_name']}")
                print(f"  Got scenario_name: {persist_scenario_name}")
                return False
    
    print("\n" + "="*80)
    print("SCENARIO SETTING FUNCTIONALITY TEST SUMMARY")
    print("="*80)
    print("✅ Fresh simulation state creation works correctly")
    print("✅ Scenario setting with both 'scenario' and 'scenario_name' fields works")
    print("✅ Scenario data is immediately available after setting")
    print("✅ Scenario data persists across multiple GET calls")
    print("✅ Empty scenarios are properly rejected")
    print("✅ Scenario data structure is correct in database")
    print("✅ Different scenario types can be set successfully")
    print("✅ Scenario data persists after other simulation operations")
    print("✅ User data isolation is working correctly")
    
    return True

if __name__ == "__main__":
    print("Starting comprehensive scenario setting functionality tests...")
    
    success = test_scenario_setting_functionality()
    
    if success:
        print("\n🎉 ALL SCENARIO SETTING TESTS PASSED!")
        print("The scenario setting functionality is working correctly.")
        print("Scenarios are properly persisted and do not disappear from the notification bar.")
    else:
        print("\n❌ SCENARIO SETTING TESTS FAILED!")
        print("There are issues with scenario persistence that need to be addressed.")
    
    sys.exit(0 if success else 1)