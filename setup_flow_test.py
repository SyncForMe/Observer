#!/usr/bin/env python3
"""
SETUP FLOW COMPLETION ISSUE TESTING
Testing the specific issue where after running the setup flow:
- Agents are created successfully 
- But scenario is not persisting properly (console shows "✅ Scenario restored: No")
- UI conditional logic isn't switching from "Ready to Begin?" to "Live Conversations"

Focus Areas:
1. Login as dino@cytonic.com (password: Observerinho8)
2. Check simulation state to see what agents and scenario are currently set
3. Test GET /api/simulation/state endpoint to verify scenario persistence
4. Check GET /api/agents to see if the 2 agents (expert 30 and expert 50) are present
5. Verify what's causing the "Ready to Begin?" card to still show
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

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

# Global variables
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

def test_login_as_dino():
    """Test login as dino@cytonic.com with password Observerinho8"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. LOGIN AS DINO@CYTONIC.COM")
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
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Login successful. User ID: {test_user_id}")
        print(f"✅ User Name: {user_data.get('name')}")
        print(f"✅ User Email: {user_data.get('email')}")
        return True
    else:
        print("❌ Login failed")
        return False

def test_simulation_state():
    """Test GET /api/simulation/state endpoint to verify scenario persistence"""
    print("\n" + "="*80)
    print("2. SIMULATION STATE TESTING")
    print("="*80)
    
    # Test simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period", "is_active"]
    )
    
    if state_test and state_response:
        print("\n--- SIMULATION STATE ANALYSIS ---")
        
        # Check scenario persistence
        scenario = state_response.get("scenario", "")
        scenario_name = state_response.get("scenario_name", "")
        is_active = state_response.get("is_active", False)
        current_day = state_response.get("current_day", 1)
        current_time_period = state_response.get("current_time_period", "morning")
        
        print(f"📋 Scenario: '{scenario}'")
        print(f"📋 Scenario Name: '{scenario_name}'")
        print(f"🔄 Is Active: {is_active}")
        print(f"📅 Current Day: {current_day}")
        print(f"⏰ Current Time Period: {current_time_period}")
        
        # Check if scenario is properly set
        if scenario and scenario.strip():
            print("✅ Scenario is set and not empty")
            scenario_restored = True
        else:
            print("❌ Scenario is empty or not set")
            print("🔍 This matches the console message: '✅ Scenario restored: No'")
            scenario_restored = False
        
        # Check if scenario name is properly set
        if scenario_name and scenario_name.strip():
            print("✅ Scenario name is set and not empty")
        else:
            print("❌ Scenario name is empty or not set")
        
        # Check simulation activity status
        if is_active:
            print("✅ Simulation is marked as active")
        else:
            print("⚠️ Simulation is not marked as active")
            print("🔍 This could affect UI conditional logic")
        
        return state_response, scenario_restored
    else:
        print("❌ Failed to get simulation state")
        return None, False

def test_agents_list():
    """Test GET /api/agents to see if the 2 agents (expert 30 and expert 50) are present"""
    print("\n" + "="*80)
    print("3. AGENTS LIST TESTING")
    print("="*80)
    
    # Test get agents
    agents_test, agents_response = run_test(
        "Get All Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if agents_test and agents_response:
        agent_count = len(agents_response)
        print(f"\n--- AGENTS ANALYSIS ---")
        print(f"👥 Total Agents Found: {agent_count}")
        
        if agent_count == 0:
            print("❌ No agents found")
            print("🔍 This could be why UI shows 'Ready to Begin?' instead of 'Live Conversations'")
            return agents_response, False
        
        # Analyze each agent
        expert_30_found = False
        expert_50_found = False
        
        for i, agent in enumerate(agents_response, 1):
            agent_name = agent.get("name", "Unknown")
            agent_expertise = agent.get("expertise", "")
            agent_archetype = agent.get("archetype", "")
            agent_id = agent.get("id", "")
            
            print(f"\n🤖 Agent {i}:")
            print(f"   Name: {agent_name}")
            print(f"   Expertise: {agent_expertise}")
            print(f"   Archetype: {agent_archetype}")
            print(f"   ID: {agent_id}")
            
            # Check for expert 30 and expert 50 patterns
            if "30" in agent_name or "30" in agent_expertise:
                expert_30_found = True
                print("   ✅ This appears to be the 'expert 30' agent")
            
            if "50" in agent_name or "50" in agent_expertise:
                expert_50_found = True
                print("   ✅ This appears to be the 'expert 50' agent")
        
        # Summary of expected agents
        print(f"\n--- EXPECTED AGENTS CHECK ---")
        if expert_30_found:
            print("✅ Expert 30 agent found")
        else:
            print("❌ Expert 30 agent NOT found")
        
        if expert_50_found:
            print("✅ Expert 50 agent found")
        else:
            print("❌ Expert 50 agent NOT found")
        
        both_experts_found = expert_30_found and expert_50_found
        
        if both_experts_found:
            print("✅ Both expected agents (expert 30 and expert 50) are present")
        else:
            print("❌ Expected agents are missing")
            print("🔍 This could affect the UI conditional logic")
        
        return agents_response, both_experts_found
    else:
        print("❌ Failed to get agents list")
        return None, False

def analyze_ui_conditional_logic(simulation_state, agents_present, scenario_restored):
    """Analyze what's causing the 'Ready to Begin?' card to still show"""
    print("\n" + "="*80)
    print("4. UI CONDITIONAL LOGIC ANALYSIS")
    print("="*80)
    
    print("🔍 Analyzing why UI shows 'Ready to Begin?' instead of 'Live Conversations'")
    
    # Common UI conditions for switching from setup to live conversations:
    # 1. Agents must be present (usually at least 2)
    # 2. Scenario must be set
    # 3. Simulation might need to be active
    # 4. User must be properly authenticated
    
    conditions_met = []
    conditions_failed = []
    
    # Check agents condition
    if agents_present and len(agents_present) >= 2:
        conditions_met.append("✅ Sufficient agents present (2+ agents)")
    else:
        agent_count = len(agents_present) if agents_present else 0
        conditions_failed.append(f"❌ Insufficient agents ({agent_count} agents, need 2+)")
    
    # Check scenario condition
    if scenario_restored:
        conditions_met.append("✅ Scenario is set and not empty")
    else:
        conditions_failed.append("❌ Scenario is empty or not set")
    
    # Check simulation state
    if simulation_state:
        is_active = simulation_state.get("is_active", False)
        if is_active:
            conditions_met.append("✅ Simulation is marked as active")
        else:
            conditions_failed.append("❌ Simulation is not active")
    else:
        conditions_failed.append("❌ Simulation state not available")
    
    # Check authentication (we know this is working since we got here)
    conditions_met.append("✅ User authentication working")
    
    print("\n--- CONDITIONS ANALYSIS ---")
    print("Conditions that are MET:")
    for condition in conditions_met:
        print(f"  {condition}")
    
    print("\nConditions that FAILED:")
    for condition in conditions_failed:
        print(f"  {condition}")
    
    # Determine likely root cause
    print("\n--- ROOT CAUSE ANALYSIS ---")
    if len(conditions_failed) == 0:
        print("🤔 All conditions appear to be met, but UI still shows 'Ready to Begin?'")
        print("🔍 Possible causes:")
        print("   1. Frontend state management issue")
        print("   2. Frontend not properly checking these conditions")
        print("   3. Different conditions than expected")
        print("   4. Caching issue in frontend")
    else:
        print("🎯 LIKELY ROOT CAUSE IDENTIFIED:")
        for condition in conditions_failed:
            print(f"   {condition}")
        
        if "Scenario is empty" in str(conditions_failed):
            print("\n💡 RECOMMENDATION: Fix scenario persistence")
            print("   - Check if scenario setting endpoint is working")
            print("   - Verify scenario is saved to database")
            print("   - Ensure frontend properly sets scenario during setup")
        
        if "Insufficient agents" in str(conditions_failed):
            print("\n💡 RECOMMENDATION: Fix agent creation/association")
            print("   - Check if agents are properly associated with user")
            print("   - Verify agent creation during setup flow")
            print("   - Ensure agents persist after creation")
    
    return len(conditions_failed) == 0

def test_scenario_setting():
    """Test scenario setting to see if it works properly"""
    print("\n" + "="*80)
    print("5. SCENARIO SETTING TEST")
    print("="*80)
    
    # Test setting a scenario
    test_scenario_data = {
        "scenario": "Test Scenario for Setup Flow",
        "scenario_name": "Setup Flow Test"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Test Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=test_scenario_data,
        auth=True,
        expected_keys=["message", "scenario"]
    )
    
    if scenario_test and scenario_response:
        print("✅ Scenario setting endpoint works")
        
        # Verify scenario was actually saved
        verify_test, verify_response = run_test(
            "Verify Scenario Was Saved",
            "/simulation/state",
            method="GET",
            auth=True
        )
        
        if verify_test and verify_response:
            saved_scenario = verify_response.get("scenario", "")
            if saved_scenario == test_scenario_data["scenario"]:
                print("✅ Scenario properly persisted to database")
                return True
            else:
                print(f"❌ Scenario not properly saved: expected '{test_scenario_data['scenario']}', got '{saved_scenario}'")
                return False
        else:
            print("❌ Could not verify scenario persistence")
            return False
    else:
        print("❌ Scenario setting endpoint failed")
        return False

def test_conversations_endpoint():
    """Test conversations endpoint to see if there are any existing conversations"""
    print("\n" + "="*80)
    print("6. CONVERSATIONS ENDPOINT TEST")
    print("="*80)
    
    # Test get conversations
    conversations_test, conversations_response = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if conversations_test and conversations_response:
        conversation_count = len(conversations_response)
        print(f"💬 Total Conversations Found: {conversation_count}")
        
        if conversation_count > 0:
            print("✅ Conversations exist")
            # Show first few conversations
            for i, conv in enumerate(conversations_response[:3], 1):
                conv_scenario = conv.get("scenario", "No scenario")
                conv_messages = conv.get("messages", [])
                message_count = len(conv_messages)
                print(f"   Conversation {i}: '{conv_scenario}' ({message_count} messages)")
        else:
            print("⚠️ No conversations found")
            print("🔍 This might affect UI logic if it expects conversations for 'Live Conversations' mode")
        
        return conversations_response
    else:
        print("❌ Failed to get conversations")
        return None

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"SETUP FLOW TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution function"""
    print("SETUP FLOW COMPLETION ISSUE TESTING")
    print("Testing the specific issue where setup flow doesn't properly switch to Live Conversations")
    print("="*80)
    
    # Step 1: Login as dino@cytonic.com
    if not test_login_as_dino():
        print("❌ Cannot proceed without successful login")
        return
    
    # Step 2: Check simulation state
    simulation_state, scenario_restored = test_simulation_state()
    
    # Step 3: Check agents list
    agents_list, agents_present = test_agents_list()
    
    # Step 4: Analyze UI conditional logic
    all_conditions_met = analyze_ui_conditional_logic(simulation_state, agents_list, scenario_restored)
    
    # Step 5: Test scenario setting functionality
    scenario_setting_works = test_scenario_setting()
    
    # Step 6: Check conversations
    conversations = test_conversations_endpoint()
    
    # Final analysis
    print("\n" + "="*80)
    print("FINAL DIAGNOSIS")
    print("="*80)
    
    print("🔍 SETUP FLOW COMPLETION ISSUE ANALYSIS:")
    
    if not scenario_restored:
        print("🎯 PRIMARY ISSUE: Scenario not persisting properly")
        print("   - Console shows '✅ Scenario restored: No' because scenario is empty")
        print("   - This prevents UI from switching to 'Live Conversations'")
        
        if scenario_setting_works:
            print("   - Scenario setting endpoint works, so issue is in setup flow")
            print("   - Frontend setup flow may not be calling scenario endpoint")
            print("   - Or scenario is being cleared after being set")
        else:
            print("   - Scenario setting endpoint is broken")
            print("   - This needs to be fixed first")
    
    if not agents_present or len(agents_list or []) < 2:
        print("🎯 SECONDARY ISSUE: Insufficient agents")
        print("   - Expected 2 agents (expert 30 and expert 50)")
        print(f"   - Found {len(agents_list or [])} agents")
        print("   - UI may require minimum number of agents")
    
    if all_conditions_met:
        print("🤔 MYSTERY: All backend conditions appear met")
        print("   - Issue may be in frontend conditional logic")
        print("   - Frontend may be checking different conditions")
        print("   - Could be a state management or caching issue")
    
    print("\n💡 RECOMMENDED ACTIONS:")
    if not scenario_restored:
        print("1. Fix scenario persistence in setup flow")
        print("   - Ensure frontend calls /api/simulation/scenario during setup")
        print("   - Verify scenario is not cleared by other operations")
    
    if not agents_present or len(agents_list or []) < 2:
        print("2. Fix agent creation/association in setup flow")
        print("   - Ensure agents are created and associated with user")
        print("   - Verify agents persist after creation")
    
    print("3. Check frontend conditional logic")
    print("   - Verify what conditions frontend checks for 'Live Conversations'")
    print("   - Ensure frontend state is updated after setup completion")
    
    # Print test summary
    print_summary()

if __name__ == "__main__":
    main()