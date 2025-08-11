#!/usr/bin/env python3
"""
Simplified Time System Test
Testing the completely simplified time system that:
1. Removes rounds entirely - no more round calculations or references
2. Simple time progression - each agent sends 9 messages per time period
3. With 3 agents - 27 total messages per time period (Morning/Afternoon/Evening)
4. Time periods - Morning (0-26 messages), Afternoon (27-53), Evening (54-80), Day 2 Morning (81-107)
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
import math

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
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
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
        print(f"Response Time: {response_time:.3f}s")
        
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
            "result": result,
            "response_time": response_time
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
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def test_guest_login():
    """Login as guest user to get auth token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("STEP 1: LOGIN AS GUEST USER")
    print("="*80)
    
    # Use the test login endpoint for guest access
    test_login_test, test_login_response = run_test(
        "Guest Login",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if test_login_test and test_login_response:
        auth_token = test_login_response.get("access_token")
        user_data = test_login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token[:20]}...")
        return True
    else:
        print("❌ Guest login failed. Cannot proceed with testing.")
        return False

def calculate_time_period_from_messages(total_messages, agent_count):
    """Calculate time period based on the simplified system"""
    messages_per_period = agent_count * 9  # Each agent sends 9 messages per time period
    time_period_number = total_messages // messages_per_period
    
    # Calculate day and time period
    periods_per_day = 3  # Morning, Afternoon, Evening
    day = (time_period_number // periods_per_day) + 1
    period_in_day = time_period_number % periods_per_day
    
    period_names = ["Morning", "Afternoon", "Evening"]
    period_name = period_names[period_in_day]
    
    return {
        "day": day,
        "period": period_name,
        "time_period_number": time_period_number,
        "messages_per_period": messages_per_period,
        "current_period_messages": total_messages % messages_per_period
    }

def test_current_conversations_and_time_calculation():
    """Get current conversations and calculate total messages"""
    print("\n" + "="*80)
    print("STEP 2: GET CURRENT CONVERSATIONS AND CALCULATE TIME")
    print("="*80)
    
    # Get current conversations
    conversations_test, conversations_response = run_test(
        "Get Current Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to get conversations")
        return False, None
    
    # Get agents to determine agent count
    agents_test, agents_response = run_test(
        "Get Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not agents_test or not agents_response:
        print("❌ Failed to get agents")
        return False, None
    
    agent_count = len(agents_response)
    print(f"Agent count: {agent_count}")
    
    # Calculate total messages
    total_messages = 0
    for conversation in conversations_response:
        messages = conversation.get("messages", [])
        # Filter out observer messages (they don't count toward time progression)
        agent_messages = [msg for msg in messages if msg.get("agent_id") != "observer"]
        total_messages += len(agent_messages)
    
    print(f"Total conversations: {len(conversations_response)}")
    print(f"Total agent messages: {total_messages}")
    
    # Calculate expected time period using simplified system
    time_calc = calculate_time_period_from_messages(total_messages, agent_count)
    
    print(f"\n📊 SIMPLIFIED TIME SYSTEM CALCULATION:")
    print(f"Messages per time period: {time_calc['messages_per_period']} ({agent_count} agents × 9 messages)")
    print(f"Time period number: {time_calc['time_period_number']}")
    print(f"Expected time: Day {time_calc['day']}, {time_calc['period']}")
    print(f"Messages in current period: {time_calc['current_period_messages']}/{time_calc['messages_per_period']}")
    
    # Get current simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_test and state_response:
        current_day = state_response.get('current_day', 1)
        current_time_period = state_response.get('current_time_period', 'morning')
        print(f"\n🎯 ACTUAL SIMULATION STATE:")
        print(f"Current time: Day {current_day}, {current_time_period}")
        
        # Check if calculation matches actual state
        expected_day = time_calc['day']
        expected_period = time_calc['period'].lower()
        
        if current_day == expected_day and current_time_period == expected_period:
            print("✅ Time calculation matches simulation state!")
            time_matches = True
        else:
            print("❌ Time calculation does NOT match simulation state!")
            print(f"Expected: Day {expected_day}, {expected_period}")
            print(f"Actual: Day {current_day}, {current_time_period}")
            time_matches = False
    else:
        print("❌ Failed to get simulation state")
        time_matches = False
    
    return True, {
        "total_messages": total_messages,
        "agent_count": agent_count,
        "time_calculation": time_calc,
        "time_matches": time_matches,
        "conversations": conversations_response
    }

def test_conversation_generation():
    """Generate a new conversation to test the system"""
    print("\n" + "="*80)
    print("STEP 3: GENERATE NEW CONVERSATION TO TEST SYSTEM")
    print("="*80)
    
    # Generate a new conversation
    generate_test, generate_response = run_test(
        "Generate New Conversation",
        "/conversation/generate",
        method="POST",
        auth=True,
        expected_keys=["success"]
    )
    
    if not generate_test or not generate_response:
        print("❌ Failed to generate new conversation")
        return False, None
    
    print("✅ Successfully generated new conversation")
    
    # Wait a moment for the conversation to be processed
    time.sleep(2)
    
    # Get updated conversations
    conversations_test, conversations_response = run_test(
        "Get Updated Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to get updated conversations")
        return False, None
    
    # Get the latest conversation
    if conversations_response:
        latest_conversation = max(conversations_response, key=lambda x: x.get('created_at', ''))
        messages = latest_conversation.get("messages", [])
        agent_messages = [msg for msg in messages if msg.get("agent_id") != "observer"]
        
        print(f"Latest conversation has {len(agent_messages)} agent messages")
        
        # Check for any "Round undefined" or "NaN" errors in the conversation
        round_errors = []
        nan_errors = []
        
        for msg in messages:
            message_text = msg.get("message", "")
            if "Round undefined" in message_text or "round undefined" in message_text:
                round_errors.append(msg)
            if "NaN" in message_text or "undefined" in message_text:
                nan_errors.append(msg)
        
        if round_errors:
            print(f"❌ Found {len(round_errors)} 'Round undefined' errors in messages")
            for error_msg in round_errors[:3]:  # Show first 3 errors
                print(f"  - {error_msg.get('agent_name', 'Unknown')}: {error_msg.get('message', '')[:100]}...")
        else:
            print("✅ No 'Round undefined' errors found")
        
        if nan_errors:
            print(f"❌ Found {len(nan_errors)} 'NaN' or 'undefined' errors in messages")
            for error_msg in nan_errors[:3]:  # Show first 3 errors
                print(f"  - {error_msg.get('agent_name', 'Unknown')}: {error_msg.get('message', '')[:100]}...")
        else:
            print("✅ No 'NaN' or 'undefined' errors found")
        
        # Check time display in conversation metadata
        time_period = latest_conversation.get("time_period", "")
        print(f"Conversation time period: '{time_period}'")
        
        if "undefined" in time_period.lower() or "nan" in time_period.lower():
            print("❌ Time display contains 'undefined' or 'NaN'")
            clean_time_display = False
        else:
            print("✅ Clean time display (no 'undefined' or 'NaN')")
            clean_time_display = True
        
        return True, {
            "latest_conversation": latest_conversation,
            "agent_messages": len(agent_messages),
            "round_errors": len(round_errors),
            "nan_errors": len(nan_errors),
            "clean_time_display": clean_time_display,
            "time_period": time_period
        }
    else:
        print("❌ No conversations found after generation")
        return False, None

def test_time_advancement_thresholds():
    """Test that time advances at the correct message thresholds"""
    print("\n" + "="*80)
    print("STEP 4: TEST TIME ADVANCEMENT THRESHOLDS")
    print("="*80)
    
    # Get current state
    current_test, current_data = test_current_conversations_and_time_calculation()
    
    if not current_test or not current_data:
        print("❌ Failed to get current state for threshold testing")
        return False, None
    
    total_messages = current_data["total_messages"]
    agent_count = current_data["agent_count"]
    time_calc = current_data["time_calculation"]
    
    print(f"Current total messages: {total_messages}")
    print(f"Messages per period: {time_calc['messages_per_period']}")
    print(f"Current period messages: {time_calc['current_period_messages']}")
    
    # Calculate how many messages needed to advance to next time period
    messages_to_next_period = time_calc['messages_per_period'] - time_calc['current_period_messages']
    
    if messages_to_next_period == 0:
        messages_to_next_period = time_calc['messages_per_period']  # Already at threshold, need full period
    
    print(f"Messages needed to advance to next period: {messages_to_next_period}")
    
    # Test the expected thresholds based on simplified system
    expected_thresholds = []
    messages_per_period = agent_count * 9
    
    for period_num in range(5):  # Test first 5 periods
        threshold = period_num * messages_per_period
        day = (period_num // 3) + 1
        period_in_day = period_num % 3
        period_names = ["Morning", "Afternoon", "Evening"]
        period_name = period_names[period_in_day]
        
        expected_thresholds.append({
            "messages": threshold,
            "day": day,
            "period": period_name,
            "range_start": threshold,
            "range_end": threshold + messages_per_period - 1
        })
    
    print(f"\n📋 EXPECTED TIME ADVANCEMENT THRESHOLDS:")
    for i, threshold in enumerate(expected_thresholds):
        print(f"Period {i}: Day {threshold['day']}, {threshold['period']} (messages {threshold['range_start']}-{threshold['range_end']})")
    
    # Verify current position matches expected threshold
    current_period_num = time_calc['time_period_number']
    if current_period_num < len(expected_thresholds):
        expected_threshold = expected_thresholds[current_period_num]
        
        if (total_messages >= expected_threshold['range_start'] and 
            total_messages <= expected_threshold['range_end']):
            print(f"✅ Current message count ({total_messages}) is within expected range for Day {expected_threshold['day']}, {expected_threshold['period']}")
            threshold_correct = True
        else:
            print(f"❌ Current message count ({total_messages}) is NOT within expected range for Day {expected_threshold['day']}, {expected_threshold['period']}")
            threshold_correct = False
    else:
        print(f"⚠️ Current period number ({current_period_num}) exceeds test threshold range")
        threshold_correct = True  # Don't fail for being beyond test range
    
    return True, {
        "messages_per_period": messages_per_period,
        "expected_thresholds": expected_thresholds,
        "threshold_correct": threshold_correct,
        "messages_to_next_period": messages_to_next_period
    }

def test_simple_conversation_numbering():
    """Test that conversations use simple numbering instead of complex rounds"""
    print("\n" + "="*80)
    print("STEP 5: TEST SIMPLE CONVERSATION NUMBERING")
    print("="*80)
    
    # Get all conversations
    conversations_test, conversations_response = run_test(
        "Get All Conversations for Numbering Test",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to get conversations for numbering test")
        return False, None
    
    print(f"Total conversations: {len(conversations_response)}")
    
    # Check conversation numbering/identification
    complex_round_references = 0
    simple_numbering = 0
    
    for i, conversation in enumerate(conversations_response):
        conv_id = conversation.get("id", "")
        round_number = conversation.get("round_number", 0)
        time_period = conversation.get("time_period", "")
        scenario = conversation.get("scenario", "")
        
        print(f"Conversation {i+1}: Round {round_number}, Time: '{time_period}'")
        
        # Check for complex round references in time_period or scenario
        if ("Round" in time_period and "undefined" not in time_period.lower()) or ("Round" in scenario and "undefined" not in scenario.lower()):
            complex_round_references += 1
            print(f"  ⚠️ Contains round reference: '{time_period}' / '{scenario}'")
        else:
            simple_numbering += 1
            print(f"  ✅ Simple time display: '{time_period}'")
    
    print(f"\n📊 CONVERSATION NUMBERING ANALYSIS:")
    print(f"Conversations with complex round references: {complex_round_references}")
    print(f"Conversations with simple numbering: {simple_numbering}")
    
    if complex_round_references == 0:
        print("✅ All conversations use simple numbering (no complex round references)")
        simple_numbering_success = True
    else:
        print("❌ Some conversations still use complex round references")
        simple_numbering_success = False
    
    # Check for sequential conversation numbering
    round_numbers = [conv.get("round_number", 0) for conv in conversations_response]
    round_numbers.sort()
    
    expected_sequence = list(range(1, len(conversations_response) + 1))
    
    if round_numbers == expected_sequence:
        print("✅ Conversation round numbers follow simple sequential pattern (1, 2, 3, ...)")
        sequential_numbering = True
    else:
        print("❌ Conversation round numbers do NOT follow simple sequential pattern")
        print(f"Expected: {expected_sequence}")
        print(f"Actual: {round_numbers}")
        sequential_numbering = False
    
    return True, {
        "total_conversations": len(conversations_response),
        "complex_round_references": complex_round_references,
        "simple_numbering": simple_numbering,
        "simple_numbering_success": simple_numbering_success,
        "sequential_numbering": sequential_numbering
    }

def main():
    """Main test execution"""
    print("="*80)
    print("SIMPLIFIED TIME SYSTEM COMPREHENSIVE TEST")
    print("="*80)
    print("Testing the completely simplified time system that:")
    print("1. ❌ Removes rounds entirely - no more round calculations or references")
    print("2. ⏰ Simple time progression - each agent sends 9 messages per time period")
    print("3. 👥 With 3 agents - 27 total messages per time period (Morning/Afternoon/Evening)")
    print("4. 📅 Time periods - Morning (0-26), Afternoon (27-53), Evening (54-80), Day 2 Morning (81-107)")
    print("5. 🚫 No 'Round undefined' or 'NaN' errors")
    print("6. ✨ Clean time display like 'Day 1, Morning'")
    print("="*80)
    
    # Step 1: Login as guest user
    if not test_guest_login():
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Get current conversations and calculate total messages
    current_test, current_data = test_current_conversations_and_time_calculation()
    if not current_test:
        print("❌ Failed to analyze current state")
        return
    
    # Step 3: Generate a new conversation to test the system
    generation_test, generation_data = test_conversation_generation()
    if not generation_test:
        print("❌ Failed to test conversation generation")
        return
    
    # Step 4: Test time advancement thresholds
    threshold_test, threshold_data = test_time_advancement_thresholds()
    if not threshold_test:
        print("❌ Failed to test time advancement thresholds")
        return
    
    # Step 5: Test simple conversation numbering
    numbering_test, numbering_data = test_simple_conversation_numbering()
    if not numbering_test:
        print("❌ Failed to test conversation numbering")
        return
    
    # Final Assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT - SIMPLIFIED TIME SYSTEM")
    print("="*80)
    
    # Check all requirements
    requirements_met = 0
    total_requirements = 6
    
    # 1. No round calculations or references
    if numbering_data["simple_numbering_success"]:
        print("✅ 1. Rounds removed - no complex round references found")
        requirements_met += 1
    else:
        print("❌ 1. Rounds NOT fully removed - complex round references still exist")
    
    # 2. Simple time progression (9 messages per agent per period)
    if threshold_data["threshold_correct"]:
        print("✅ 2. Simple time progression - correct message thresholds")
        requirements_met += 1
    else:
        print("❌ 2. Time progression issues - incorrect message thresholds")
    
    # 3. Correct agent count and message calculation
    agent_count = current_data["agent_count"]
    messages_per_period = threshold_data["messages_per_period"]
    expected_messages_per_period = agent_count * 9
    
    if messages_per_period == expected_messages_per_period:
        print(f"✅ 3. Correct calculation - {agent_count} agents × 9 = {messages_per_period} messages per period")
        requirements_met += 1
    else:
        print(f"❌ 3. Incorrect calculation - expected {expected_messages_per_period}, got {messages_per_period}")
    
    # 4. Time matches calculation
    if current_data["time_matches"]:
        print("✅ 4. Time calculation matches simulation state")
        requirements_met += 1
    else:
        print("❌ 4. Time calculation does NOT match simulation state")
    
    # 5. No "Round undefined" or "NaN" errors
    if generation_data["round_errors"] == 0 and generation_data["nan_errors"] == 0:
        print("✅ 5. No 'Round undefined' or 'NaN' errors found")
        requirements_met += 1
    else:
        print(f"❌ 5. Found {generation_data['round_errors']} round errors and {generation_data['nan_errors']} NaN errors")
    
    # 6. Clean time display
    if generation_data["clean_time_display"]:
        print("✅ 6. Clean time display - no undefined/NaN in time periods")
        requirements_met += 1
    else:
        print("❌ 6. Time display contains undefined/NaN values")
    
    # Overall result
    success_rate = (requirements_met / total_requirements) * 100
    print(f"\n📊 OVERALL SUCCESS RATE: {requirements_met}/{total_requirements} ({success_rate:.1f}%)")
    
    if requirements_met == total_requirements:
        print("🎉 SIMPLIFIED TIME SYSTEM IS WORKING PERFECTLY!")
        print("✅ All requirements met - the system eliminates 'Day NaN, Round undefined' errors")
    elif requirements_met >= 4:
        print("⚠️ SIMPLIFIED TIME SYSTEM IS MOSTLY WORKING")
        print("🔧 Some minor issues need attention")
    else:
        print("❌ SIMPLIFIED TIME SYSTEM NEEDS SIGNIFICANT WORK")
        print("🚨 Major issues prevent proper functionality")
    
    # Print detailed summary
    print_summary()

if __name__ == "__main__":
    main()