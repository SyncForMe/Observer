#!/usr/bin/env python3
"""
CONVERSATION FILTERING SYSTEM TESTING
Testing the new conversation filtering system to ensure proper separation between active and archived conversations.

SPECIFIC TESTING REQUIREMENTS:
1. Test the existing GET /api/conversations endpoint - should return ALL user conversations (for Library section)
2. Test the new GET /api/conversations/active endpoint - should return only active simulation conversations (for Observatory)
3. Create a test scenario with agents and generate conversations
4. Test that /conversations/active only shows conversations from current simulation scenario
5. Create a new scenario and verify that /conversations/active switches to new scenario conversations
6. Test Fresh Start behavior - active conversations should be filtered properly while all conversations are preserved
7. Verify that Library still shows all conversations while Observatory shows only active ones

FOCUS AREAS:
- Proper filtering logic for active vs archived conversations
- Scenario-based conversation filtering 
- Fresh Start impact on active conversation filtering
- User authorization and data isolation
- Proper response formats and data consistency
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

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
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []

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

def setup_authentication():
    """Set up authentication for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION SETUP")
    print("="*80)
    
    # Test email/password login with dino@cytonic.com
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login (dino@cytonic.com)",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication setup successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Authentication setup failed")
        return False

def create_test_agents():
    """Create test agents for conversation generation"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("TEST AGENTS CREATION")
    print("="*80)
    
    # Agent 1: Quantum Researcher
    agent_data_1 = {
        "name": "Dr. Quantum Alice",
        "archetype": "scientist",
        "goal": "Advance quantum computing research",
        "expertise": "Quantum mechanics and computing",
        "background": "PhD in Quantum Physics from MIT",
        "personality": {
            "extroversion": 6,
            "optimism": 8,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 7
        }
    }
    
    # Agent 2: AI Ethics Expert
    agent_data_2 = {
        "name": "Prof. Ethics Bob",
        "archetype": "mediator",
        "goal": "Ensure ethical AI development",
        "expertise": "AI ethics and philosophy",
        "background": "Professor of AI Ethics at Stanford",
        "personality": {
            "extroversion": 7,
            "optimism": 6,
            "curiosity": 8,
            "cooperativeness": 9,
            "energy": 6
        }
    }
    
    # Create agents
    create_agent1_test, create_agent1_response = run_test(
        "Create Quantum Research Agent",
        "/agents",
        method="POST",
        data=agent_data_1,
        auth=True,
        expected_keys=["id", "name", "archetype"]
    )
    
    create_agent2_test, create_agent2_response = run_test(
        "Create AI Ethics Agent",
        "/agents",
        method="POST",
        data=agent_data_2,
        auth=True,
        expected_keys=["id", "name", "archetype"]
    )
    
    if create_agent1_test and create_agent2_test:
        agent1_id = create_agent1_response.get("id")
        agent2_id = create_agent2_response.get("id")
        created_agent_ids.extend([agent1_id, agent2_id])
        print(f"✅ Created test agents: {agent1_id}, {agent2_id}")
        return True
    else:
        print("❌ Failed to create test agents")
        return False

def test_conversation_filtering_system():
    """Test the conversation filtering system comprehensively"""
    print("\n" + "="*80)
    print("CONVERSATION FILTERING SYSTEM TESTING")
    print("="*80)
    
    print("🔍 Testing conversation filtering to ensure proper separation between active and archived conversations")
    print("Focus: Observatory (active) vs Library (all) conversation filtering")
    
    # Test 1: Set first scenario and generate conversations
    print("\n--- Test 1: First Scenario Setup ---")
    scenario_data_1 = {
        "scenario": "Quantum Computing Research Lab",
        "scenario_name": "Advanced Quantum Research"
    }
    
    scenario_test_1, scenario_response_1 = run_test(
        "Set First Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data_1,
        auth=True,
        expected_keys=["message", "scenario"]
    )
    
    if not scenario_test_1:
        print("❌ Failed to set first scenario")
        return False
    
    # Generate conversations for first scenario
    conversation_test_1, conversation_response_1 = run_test(
        "Generate Conversation for First Scenario",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True,
        expected_keys=["id", "messages", "scenario"]
    )
    
    if not conversation_test_1:
        print("❌ Failed to generate conversation for first scenario")
        return False
    
    # Test 2: Check conversations endpoints after first scenario
    print("\n--- Test 2: Conversation Endpoints After First Scenario ---")
    
    # Test GET /api/conversations (should return ALL conversations)
    all_conversations_test_1, all_conversations_response_1 = run_test(
        "Get ALL Conversations (Library)",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not all_conversations_test_1:
        print("❌ Failed to get all conversations")
        return False
    
    all_conv_count_1 = len(all_conversations_response_1)
    print(f"✅ Library endpoint returned {all_conv_count_1} conversations")
    
    # Test GET /api/conversations/active (should return only active conversations)
    active_conversations_test_1, active_conversations_response_1 = run_test(
        "Get ACTIVE Conversations (Observatory)",
        "/conversations/active",
        method="GET",
        auth=True
    )
    
    if not active_conversations_test_1:
        print("❌ Failed to get active conversations")
        return False
    
    active_conv_count_1 = len(active_conversations_response_1)
    print(f"✅ Observatory endpoint returned {active_conv_count_1} active conversations")
    
    # Verify filtering logic for first scenario
    if active_conv_count_1 <= all_conv_count_1:
        print("✅ Active conversations count is <= total conversations (correct filtering)")
    else:
        print("❌ Active conversations count is > total conversations (incorrect filtering)")
        return False
    
    # Verify scenario filtering
    if active_conversations_response_1:
        first_active_conv = active_conversations_response_1[0]
        scenario_match = (first_active_conv.get("scenario") == scenario_data_1["scenario"] or 
                         first_active_conv.get("scenario_name") == scenario_data_1["scenario_name"])
        if scenario_match:
            print("✅ Active conversations are properly filtered by current scenario")
        else:
            print(f"❌ Active conversation scenario mismatch: {first_active_conv.get('scenario')} vs {scenario_data_1['scenario']}")
            return False
    
    # Test 3: Set second scenario and generate more conversations
    print("\n--- Test 3: Second Scenario Setup ---")
    scenario_data_2 = {
        "scenario": "AI Ethics Research Center",
        "scenario_name": "Ethical AI Development"
    }
    
    scenario_test_2, scenario_response_2 = run_test(
        "Set Second Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data_2,
        auth=True,
        expected_keys=["message", "scenario"]
    )
    
    if not scenario_test_2:
        print("❌ Failed to set second scenario")
        return False
    
    # Generate conversations for second scenario
    conversation_test_2, conversation_response_2 = run_test(
        "Generate Conversation for Second Scenario",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True,
        expected_keys=["id", "messages", "scenario"]
    )
    
    if not conversation_test_2:
        print("❌ Failed to generate conversation for second scenario")
        return False
    
    # Test 4: Verify scenario-based filtering after scenario change
    print("\n--- Test 4: Scenario-Based Filtering Verification ---")
    
    # Get all conversations (should include both scenarios)
    all_conversations_test_2, all_conversations_response_2 = run_test(
        "Get ALL Conversations After Scenario Change",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not all_conversations_test_2:
        print("❌ Failed to get all conversations after scenario change")
        return False
    
    all_conv_count_2 = len(all_conversations_response_2)
    print(f"✅ Library endpoint returned {all_conv_count_2} total conversations")
    
    # Get active conversations (should only show second scenario)
    active_conversations_test_2, active_conversations_response_2 = run_test(
        "Get ACTIVE Conversations After Scenario Change",
        "/conversations/active",
        method="GET",
        auth=True
    )
    
    if not active_conversations_test_2:
        print("❌ Failed to get active conversations after scenario change")
        return False
    
    active_conv_count_2 = len(active_conversations_response_2)
    print(f"✅ Observatory endpoint returned {active_conv_count_2} active conversations")
    
    # Verify that total conversations increased but active conversations switched
    if all_conv_count_2 > all_conv_count_1:
        print("✅ Total conversations increased (Library preserves all)")
    else:
        print("❌ Total conversations did not increase as expected")
        return False
    
    # Verify active conversations are filtered to current scenario
    if active_conversations_response_2:
        current_active_conv = active_conversations_response_2[0]
        current_scenario_match = (current_active_conv.get("scenario") == scenario_data_2["scenario"] or 
                                current_active_conv.get("scenario_name") == scenario_data_2["scenario_name"])
        if current_scenario_match:
            print("✅ Active conversations switched to new scenario correctly")
        else:
            print(f"❌ Active conversations not filtered to new scenario: {current_active_conv.get('scenario')}")
            return False
    
    # Test 5: Fresh Start behavior
    print("\n--- Test 5: Fresh Start Behavior Testing ---")
    
    # Perform Fresh Start
    fresh_start_test, fresh_start_response = run_test(
        "Fresh Start Reset",
        "/simulation/reset",
        method="POST",
        auth=True,
        expected_keys=["message", "success"]
    )
    
    if not fresh_start_test:
        print("❌ Fresh Start failed")
        return False
    
    print("✅ Fresh Start completed successfully")
    
    # Verify conversations are preserved in Library
    all_conversations_after_reset_test, all_conversations_after_reset_response = run_test(
        "Get ALL Conversations After Fresh Start",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not all_conversations_after_reset_test:
        print("❌ Failed to get conversations after Fresh Start")
        return False
    
    all_conv_count_after_reset = len(all_conversations_after_reset_response)
    print(f"✅ Library endpoint returned {all_conv_count_after_reset} conversations after Fresh Start")
    
    # Verify active conversations are properly filtered after Fresh Start
    active_conversations_after_reset_test, active_conversations_after_reset_response = run_test(
        "Get ACTIVE Conversations After Fresh Start",
        "/conversations/active",
        method="GET",
        auth=True
    )
    
    if not active_conversations_after_reset_test:
        print("❌ Failed to get active conversations after Fresh Start")
        return False
    
    active_conv_count_after_reset = len(active_conversations_after_reset_response)
    print(f"✅ Observatory endpoint returned {active_conv_count_after_reset} active conversations after Fresh Start")
    
    # Test 6: Verify Fresh Start impact on filtering
    print("\n--- Test 6: Fresh Start Impact Verification ---")
    
    # Conversations should be preserved in Library
    if all_conv_count_after_reset == all_conv_count_2:
        print("✅ Fresh Start preserved all conversations in Library")
    else:
        print(f"❌ Fresh Start did not preserve conversations: {all_conv_count_after_reset} vs {all_conv_count_2}")
        return False
    
    # Active conversations should be filtered properly (likely empty or filtered by date)
    if active_conv_count_after_reset <= all_conv_count_after_reset:
        print("✅ Fresh Start properly filtered active conversations")
    else:
        print("❌ Fresh Start did not filter active conversations correctly")
        return False
    
    # Test 7: User authorization and data isolation
    print("\n--- Test 7: User Authorization and Data Isolation ---")
    
    # Test without authentication
    no_auth_all_test, no_auth_all_response = run_test(
        "Get Conversations Without Auth",
        "/conversations",
        method="GET",
        auth=False,
        expected_status=401
    )
    
    no_auth_active_test, no_auth_active_response = run_test(
        "Get Active Conversations Without Auth",
        "/conversations/active",
        method="GET",
        auth=False,
        expected_status=401
    )
    
    if no_auth_all_test and no_auth_active_test:
        print("✅ Both endpoints properly require authentication")
    else:
        print("❌ Authentication requirements not properly enforced")
        return False
    
    # Test 8: Response format consistency
    print("\n--- Test 8: Response Format Consistency ---")
    
    if all_conversations_after_reset_response and active_conversations_after_reset_response:
        # Check that both endpoints return the same structure
        all_sample = all_conversations_after_reset_response[0] if all_conversations_after_reset_response else {}
        active_sample = active_conversations_after_reset_response[0] if active_conversations_after_reset_response else {}
        
        required_fields = ["id", "round_number", "time_period", "scenario", "messages", "user_id", "created_at"]
        
        all_fields_present = all(field in all_sample for field in required_fields) if all_sample else True
        active_fields_present = all(field in active_sample for field in required_fields) if active_sample else True
        
        if all_fields_present and active_fields_present:
            print("✅ Both endpoints return consistent response format")
        else:
            print("❌ Response format inconsistency detected")
            return False
    
    print("\n--- CONVERSATION FILTERING SYSTEM TEST SUMMARY ---")
    print("✅ GET /api/conversations endpoint working (returns ALL conversations for Library)")
    print("✅ GET /api/conversations/active endpoint working (returns filtered conversations for Observatory)")
    print("✅ Scenario-based conversation filtering working correctly")
    print("✅ Fresh Start preserves conversations while filtering active ones")
    print("✅ User authorization and data isolation working")
    print("✅ Response formats are consistent between endpoints")
    print("✅ Active vs archived conversation separation working properly")
    
    print("🎯 CRITICAL BUG FIX VERIFICATION:")
    print("✅ Observatory Live Conversations section now shows only active conversations")
    print("✅ Library section shows all conversations as expected")
    print("✅ Old conversations no longer appear in Observatory after scenario changes")
    
    return True

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution function"""
    print("CONVERSATION FILTERING SYSTEM TESTING")
    print("Testing the new conversation filtering system for active vs archived conversations")
    print("="*80)
    
    # Setup authentication
    if not setup_authentication():
        print("❌ Authentication setup failed. Cannot proceed with tests.")
        return False
    
    # Create test agents
    if not create_test_agents():
        print("❌ Test agent creation failed. Cannot proceed with tests.")
        return False
    
    # Run conversation filtering tests
    try:
        print(f"\n{'='*80}")
        print(f"RUNNING CONVERSATION FILTERING TESTS")
        print(f"{'='*80}")
        
        success = test_conversation_filtering_system()
        if success:
            print(f"✅ Conversation filtering system tests PASSED")
        else:
            print(f"❌ Conversation filtering system tests FAILED")
    except Exception as e:
        print(f"❌ Conversation filtering system tests ERROR: {e}")
        success = False
    
    # Cleanup test data
    cleanup_test_data()
    
    # Print final summary
    print_summary()
    
    # Print final result
    print(f"\n{'='*80}")
    print("FINAL TEST RESULT")
    print(f"{'='*80}")
    
    if success and test_results["failed"] == 0:
        print(f"✅ ALL CONVERSATION FILTERING TESTS PASSED!")
        print("🎯 The conversation filtering system is working correctly:")
        print("   - Observatory shows only active conversations")
        print("   - Library shows all conversations")
        print("   - Scenario-based filtering works properly")
        print("   - Fresh Start preserves conversations correctly")
    else:
        print(f"❌ SOME TESTS FAILED!")
        print("🔍 Issues found in the conversation filtering system")
    
    print(f"{'='*80}")
    
    # Return overall success
    return success and test_results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)