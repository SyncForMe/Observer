#!/usr/bin/env python3
"""
Test script for scenario clearing functionality in the reset endpoint.

This test specifically verifies that the POST /api/simulation/reset endpoint
properly clears the scenario and scenario_name fields, ensuring they are
empty strings after reset (not "The Research Station" default).
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

def get_auth_token():
    """Get authentication token using test login endpoint"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Failed to get auth token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def test_scenario_clearing():
    """Test the specific scenario clearing functionality"""
    print("="*80)
    print("TESTING SCENARIO CLEARING FUNCTIONALITY")
    print("="*80)
    
    # Get authentication token
    auth_token = get_auth_token()
    if not auth_token:
        print("❌ Failed to get authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 1: Set a scenario first
    print("\nStep 1: Setting a test scenario")
    scenario_data = {
        "scenario": "Test Scenario",
        "scenario_name": "Test Name"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/simulation/set-scenario",
            json=scenario_data,
            headers=headers
        )
        print(f"Set scenario response: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ Failed to set scenario")
            return False
        
        print("✅ Successfully set test scenario")
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False
    
    # Step 2: Verify scenario is set
    print("\nStep 2: Verifying scenario is set")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        print(f"Get state response: {response.status_code}")
        
        if response.status_code == 200:
            state_data = response.json()
            print(f"State before reset: {json.dumps(state_data, indent=2)}")
            
            scenario = state_data.get("scenario", "")
            scenario_name = state_data.get("scenario_name", "")
            
            if scenario == "Test Scenario" and scenario_name == "Test Name":
                print("✅ Scenario is correctly set")
            else:
                print(f"❌ Scenario not set correctly. Got scenario='{scenario}', scenario_name='{scenario_name}'")
                return False
        else:
            print(f"❌ Failed to get simulation state: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
        return False
    
    # Step 3: Reset the simulation
    print("\nStep 3: Resetting the simulation")
    try:
        response = requests.post(f"{API_URL}/simulation/reset", headers=headers)
        print(f"Reset response: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
            print("❌ Failed to reset simulation")
            return False
        
        print("✅ Successfully reset simulation")
    except Exception as e:
        print(f"❌ Error resetting simulation: {e}")
        return False
    
    # Step 4: Verify scenario is completely cleared
    print("\nStep 4: Verifying scenario is completely cleared")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        print(f"Get state after reset response: {response.status_code}")
        
        if response.status_code == 200:
            state_data = response.json()
            print(f"State after reset: {json.dumps(state_data, indent=2)}")
            
            scenario = state_data.get("scenario", "")
            scenario_name = state_data.get("scenario_name", "")
            
            print(f"After reset - scenario: '{scenario}', scenario_name: '{scenario_name}'")
            
            # Critical test: Both should be empty strings, NOT "The Research Station"
            if scenario == "" and scenario_name == "":
                print("✅ CRITICAL TEST PASSED: Scenario and scenario_name are empty strings")
                return True
            elif scenario == "The Research Station":
                print("❌ CRITICAL TEST FAILED: scenario shows 'The Research Station' (default value)")
                print("This indicates the reset is not properly clearing the scenario field")
                return False
            else:
                print(f"❌ CRITICAL TEST FAILED: scenario='{scenario}', scenario_name='{scenario_name}' (should both be empty)")
                return False
        else:
            print(f"❌ Failed to get simulation state after reset: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting simulation state after reset: {e}")
        return False

def test_multiple_scenario_reset_cycles():
    """Test multiple cycles of setting and resetting scenarios"""
    print("\n" + "="*80)
    print("TESTING MULTIPLE SCENARIO RESET CYCLES")
    print("="*80)
    
    # Get authentication token
    auth_token = get_auth_token()
    if not auth_token:
        print("❌ Failed to get authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    test_scenarios = [
        {"scenario": "Business Meeting", "scenario_name": "Q4 Planning"},
        {"scenario": "Research Discussion", "scenario_name": "AI Ethics"},
        {"scenario": "Creative Brainstorm", "scenario_name": "Product Ideas"}
    ]
    
    for i, scenario_data in enumerate(test_scenarios, 1):
        print(f"\nCycle {i}: Testing with scenario '{scenario_data['scenario_name']}'")
        
        # Set scenario
        try:
            response = requests.post(
                f"{API_URL}/simulation/set-scenario",
                json=scenario_data,
                headers=headers
            )
            if response.status_code != 200:
                print(f"❌ Failed to set scenario in cycle {i}")
                return False
        except Exception as e:
            print(f"❌ Error setting scenario in cycle {i}: {e}")
            return False
        
        # Verify scenario is set
        try:
            response = requests.get(f"{API_URL}/simulation/state", headers=headers)
            if response.status_code == 200:
                state_data = response.json()
                if (state_data.get("scenario") != scenario_data["scenario"] or 
                    state_data.get("scenario_name") != scenario_data["scenario_name"]):
                    print(f"❌ Scenario not set correctly in cycle {i}")
                    return False
            else:
                print(f"❌ Failed to get state in cycle {i}")
                return False
        except Exception as e:
            print(f"❌ Error getting state in cycle {i}: {e}")
            return False
        
        # Reset simulation
        try:
            response = requests.post(f"{API_URL}/simulation/reset", headers=headers)
            if response.status_code != 200:
                print(f"❌ Failed to reset in cycle {i}")
                return False
        except Exception as e:
            print(f"❌ Error resetting in cycle {i}: {e}")
            return False
        
        # Verify scenario is cleared
        try:
            response = requests.get(f"{API_URL}/simulation/state", headers=headers)
            if response.status_code == 200:
                state_data = response.json()
                scenario = state_data.get("scenario", "")
                scenario_name = state_data.get("scenario_name", "")
                
                if scenario != "" or scenario_name != "":
                    print(f"❌ Scenario not cleared in cycle {i}: scenario='{scenario}', scenario_name='{scenario_name}'")
                    return False
                else:
                    print(f"✅ Cycle {i}: Scenario properly cleared")
            else:
                print(f"❌ Failed to get state after reset in cycle {i}")
                return False
        except Exception as e:
            print(f"❌ Error getting state after reset in cycle {i}: {e}")
            return False
    
    print("✅ All scenario reset cycles completed successfully")
    return True

def main():
    """Main test function"""
    print("SCENARIO RESET ENDPOINT TESTING")
    print("Testing that POST /api/simulation/reset properly clears scenario fields")
    
    # Test 1: Basic scenario clearing functionality
    test1_result = test_scenario_clearing()
    
    # Test 2: Multiple cycles
    test2_result = test_multiple_scenario_reset_cycles()
    
    # Summary
    print("\n" + "="*80)
    print("SCENARIO RESET TEST SUMMARY")
    print("="*80)
    
    if test1_result and test2_result:
        print("✅ ALL TESTS PASSED")
        print("✅ The reset endpoint properly clears scenario and scenario_name fields")
        print("✅ No 'Research Station' default appears after reset")
        print("✅ Multiple reset cycles work correctly")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        if not test1_result:
            print("❌ Basic scenario clearing test failed")
        if not test2_result:
            print("❌ Multiple cycles test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)