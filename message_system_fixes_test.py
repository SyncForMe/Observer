#!/usr/bin/env python3
"""
Message System Fixes Testing
Testing the major fixes implemented for user's issues:

1. **1 message per agent system** - Changed from 3 messages per agent to 1 message per agent
2. **Time progression fix** - Updated logic for 1 message per agent system
3. **Concurrency controls** - Added conversationUpdateRef to prevent message jumping

ISSUES TO TEST:
1. **Message generation** - Each conversation should now generate exactly 1 message per agent (not 3)
2. **Time progression** - With 3 agents, time should advance every 27 messages:
   - Day 1 Morning: Messages 1-27
   - Day 1 Afternoon: Messages 28-54  
   - Day 1 Evening: Messages 55-81
3. **No more message jumping** - Message counts should be stable, no more 15→18→17 jumps
4. **Pause/resume functionality** - Should preserve conversations
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime
from collections import Counter

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

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
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
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
            response = requests.delete(url, json=data, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        status_ok = response.status_code == expected_status
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        test_passed = status_ok and keys_ok
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

def login_as_guest():
    """Login as guest user to get auth token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("LOGGING IN AS GUEST USER")
    print("="*80)
    
    login_test, login_response = run_test(
        "Guest Login",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest login successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest login failed")
        return False

def get_current_state():
    """Get current simulation state and conversation data"""
    print("\n" + "="*60)
    print("GETTING CURRENT STATE")
    print("="*60)
    
    # Get simulation state
    state_test, state_response = run_test(
        "Get Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    # Get conversations
    conv_test, conv_response = run_test(
        "Get Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    # Get agents
    agents_test, agents_response = run_test(
        "Get Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not all([state_test, conv_test, agents_test]):
        return None, None, None
    
    return state_response, conv_response, agents_response

def count_messages_in_conversations(conversations):
    """Count total messages across all conversations"""
    total_messages = 0
    conversation_details = []
    
    for conv in conversations:
        messages = conv.get("messages", [])
        message_count = len(messages)
        total_messages += message_count
        
        conversation_details.append({
            "id": conv.get("id"),
            "round_number": conv.get("round_number"),
            "time_period": conv.get("time_period"),
            "message_count": message_count,
            "scenario": conv.get("scenario", "")[:50] + "..." if len(conv.get("scenario", "")) > 50 else conv.get("scenario", "")
        })
    
    return total_messages, conversation_details

def analyze_time_progression(conversations, agent_count):
    """Analyze time progression based on message counts and agent count"""
    total_messages, conv_details = count_messages_in_conversations(conversations)
    
    print(f"\n📊 TIME PROGRESSION ANALYSIS:")
    print(f"Total messages: {total_messages}")
    print(f"Agent count: {agent_count}")
    print(f"Messages per time period (expected): {agent_count * 9} = {agent_count} agents × 9 messages each")
    
    # Calculate expected time progression with 1 message per agent system
    # With 3 agents: 27 messages per time period (3 agents × 9 messages each)
    messages_per_period = agent_count * 9
    
    if total_messages == 0:
        expected_time = "Day 1 Morning"
        expected_day = 1
        expected_period = "morning"
    else:
        # Calculate which time period we should be in
        period_index = (total_messages - 1) // messages_per_period
        day = (period_index // 3) + 1
        period_names = ["morning", "afternoon", "evening"]
        period = period_names[period_index % 3]
        expected_time = f"Day {day} {period.title()}"
        expected_day = day
        expected_period = period
    
    print(f"Expected time based on {total_messages} messages: {expected_time}")
    
    return {
        "total_messages": total_messages,
        "expected_time": expected_time,
        "expected_day": expected_day,
        "expected_period": expected_period,
        "messages_per_period": messages_per_period,
        "conversation_details": conv_details
    }

def test_message_generation_system():
    """Test that each conversation generates exactly 1 message per agent (not 3)"""
    print("\n" + "="*80)
    print("TESTING MESSAGE GENERATION SYSTEM (1 MESSAGE PER AGENT)")
    print("="*80)
    
    # Get current state
    state, conversations, agents = get_current_state()
    if not all([state, conversations is not None, agents]):
        print("❌ Failed to get current state")
        return False
    
    agent_count = len(agents)
    print(f"Agent count: {agent_count}")
    
    if agent_count == 0:
        print("⚠️ No agents found. Cannot test message generation.")
        return False
    
    # Record initial state
    initial_total, initial_details = count_messages_in_conversations(conversations)
    print(f"Initial total messages: {initial_total}")
    
    # Generate 1-2 conversations to test the system
    print("\n🔄 Generating test conversations...")
    
    conversation_results = []
    
    for i in range(2):
        print(f"\nGenerating conversation {i+1}/2...")
        
        # Generate conversation
        gen_test, gen_response = run_test(
            f"Generate Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True
        )
        
        if gen_test and gen_response:
            print(f"✅ Conversation {i+1} generated successfully")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Get updated conversations
            conv_test, conv_response = run_test(
                f"Get Conversations After Gen {i+1}",
                "/conversations",
                method="GET",
                auth=True
            )
            
            if conv_test and conv_response:
                new_total, new_details = count_messages_in_conversations(conv_response)
                messages_added = new_total - initial_total
                
                conversation_results.append({
                    "conversation_num": i+1,
                    "messages_before": initial_total,
                    "messages_after": new_total,
                    "messages_added": messages_added,
                    "expected_messages": agent_count,  # Should be 1 message per agent
                    "correct": messages_added == agent_count
                })
                
                print(f"Messages before: {initial_total}")
                print(f"Messages after: {new_total}")
                print(f"Messages added: {messages_added}")
                print(f"Expected messages (1 per agent): {agent_count}")
                
                if messages_added == agent_count:
                    print(f"✅ Correct! Added exactly {agent_count} messages (1 per agent)")
                else:
                    print(f"❌ Incorrect! Added {messages_added} messages instead of {agent_count}")
                
                # Update initial total for next iteration
                initial_total = new_total
            else:
                print(f"❌ Failed to get conversations after generation {i+1}")
                conversation_results.append({
                    "conversation_num": i+1,
                    "error": "Failed to get conversations after generation"
                })
        else:
            print(f"❌ Failed to generate conversation {i+1}")
            conversation_results.append({
                "conversation_num": i+1,
                "error": "Failed to generate conversation"
            })
    
    # Analyze results
    print(f"\n📊 MESSAGE GENERATION ANALYSIS:")
    successful_tests = [r for r in conversation_results if "error" not in r]
    correct_tests = [r for r in successful_tests if r.get("correct", False)]
    
    print(f"Successful conversation generations: {len(successful_tests)}/2")
    print(f"Correct message counts: {len(correct_tests)}/{len(successful_tests)}")
    
    if len(successful_tests) > 0:
        for result in successful_tests:
            status = "✅" if result.get("correct", False) else "❌"
            print(f"{status} Conversation {result['conversation_num']}: Added {result['messages_added']} messages (expected {result['expected_messages']})")
    
    # Overall assessment
    if len(correct_tests) == len(successful_tests) and len(successful_tests) > 0:
        print("\n✅ MESSAGE GENERATION SYSTEM IS WORKING CORRECTLY!")
        print("✅ Each conversation generates exactly 1 message per agent")
        return True
    else:
        print("\n❌ MESSAGE GENERATION SYSTEM HAS ISSUES!")
        if len(successful_tests) == 0:
            print("❌ No conversations could be generated successfully")
        else:
            print(f"❌ Only {len(correct_tests)}/{len(successful_tests)} conversations had correct message counts")
        return False

def test_time_progression_logic():
    """Test time progression with 1 message per agent system"""
    print("\n" + "="*80)
    print("TESTING TIME PROGRESSION LOGIC (1 MESSAGE PER AGENT SYSTEM)")
    print("Expected: With 3 agents, time should advance every 27 messages")
    print("Day 1 Morning: Messages 1-27")
    print("Day 1 Afternoon: Messages 28-54")
    print("Day 1 Evening: Messages 55-81")
    print("="*80)
    
    # Get current state
    state, conversations, agents = get_current_state()
    if not all([state, conversations is not None, agents]):
        print("❌ Failed to get current state")
        return False
    
    agent_count = len(agents)
    print(f"Agent count: {agent_count}")
    
    if agent_count == 0:
        print("⚠️ No agents found. Cannot test time progression.")
        return False
    
    # Analyze current time progression
    progression_analysis = analyze_time_progression(conversations, agent_count)
    
    # Get simulation state
    current_time = state.get("current_time_period", "unknown")
    current_day = state.get("current_day", 0)
    
    print(f"\n🕐 CURRENT STATE:")
    print(f"Simulation state time: Day {current_day} {current_time.title()}")
    print(f"Expected time based on messages: {progression_analysis['expected_time']}")
    
    # Check if simulation state matches expected time
    expected_day = progression_analysis['expected_day']
    expected_period = progression_analysis['expected_period']
    
    time_matches = (current_day == expected_day and current_time.lower() == expected_period.lower())
    
    if time_matches:
        print("✅ Simulation state matches expected time based on message count!")
    else:
        print("❌ Simulation state does NOT match expected time based on message count!")
        print(f"   Expected: Day {expected_day} {expected_period.title()}")
        print(f"   Actual: Day {current_day} {current_time.title()}")
    
    # Show conversation details
    print(f"\n📋 CONVERSATION BREAKDOWN:")
    for i, conv in enumerate(progression_analysis['conversation_details'], 1):
        print(f"{i:2d}. Round {conv['round_number']:2d} | {conv['time_period']:15s} | {conv['message_count']:2d} messages | {conv['scenario']}")
    
    return time_matches

def test_message_count_stability():
    """Test that message counts are stable and don't jump around"""
    print("\n" + "="*80)
    print("TESTING MESSAGE COUNT STABILITY (NO MORE MESSAGE JUMPING)")
    print("Testing for issue: Message counter jumping from 29→15→17, messages appearing/disappearing")
    print("="*80)
    
    # Get current state multiple times to check for consistency
    print("🔄 Checking message count consistency across multiple requests...")
    
    message_counts = []
    conversation_counts = []
    
    for i in range(5):
        print(f"\nRequest {i+1}/5:")
        
        conv_test, conv_response = run_test(
            f"Get Conversations - Stability Check {i+1}",
            "/conversations",
            method="GET",
            auth=True
        )
        
        if conv_test and conv_response:
            total_messages, conv_details = count_messages_in_conversations(conv_response)
            conversation_count = len(conv_response)
            
            message_counts.append(total_messages)
            conversation_counts.append(conversation_count)
            
            print(f"Total messages: {total_messages}")
            print(f"Total conversations: {conversation_count}")
        else:
            print("❌ Failed to get conversations")
            return False
        
        # Small delay between requests
        time.sleep(1)
    
    # Analyze stability
    print(f"\n📊 STABILITY ANALYSIS:")
    print(f"Message counts across 5 requests: {message_counts}")
    print(f"Conversation counts across 5 requests: {conversation_counts}")
    
    # Check for consistency
    message_count_stable = len(set(message_counts)) == 1
    conversation_count_stable = len(set(conversation_counts)) == 1
    
    if message_count_stable:
        print(f"✅ Message count is STABLE: {message_counts[0]} messages across all requests")
    else:
        print(f"❌ Message count is UNSTABLE: Varies between {min(message_counts)} and {max(message_counts)}")
        print(f"   Variation detected: {set(message_counts)}")
    
    if conversation_count_stable:
        print(f"✅ Conversation count is STABLE: {conversation_counts[0]} conversations across all requests")
    else:
        print(f"❌ Conversation count is UNSTABLE: Varies between {min(conversation_counts)} and {max(conversation_counts)}")
        print(f"   Variation detected: {set(conversation_counts)}")
    
    # Overall stability assessment
    overall_stable = message_count_stable and conversation_count_stable
    
    if overall_stable:
        print("\n✅ MESSAGE COUNT STABILITY TEST PASSED!")
        print("✅ No message jumping detected")
        print("✅ Counts remain consistent across multiple requests")
        return True
    else:
        print("\n❌ MESSAGE COUNT STABILITY TEST FAILED!")
        print("❌ Message jumping detected - counts are inconsistent")
        return False

def test_pause_resume_functionality():
    """Test pause/resume functionality preserves conversations"""
    print("\n" + "="*80)
    print("TESTING PAUSE/RESUME FUNCTIONALITY")
    print("Testing for issue: Data loss when pausing and resuming simulation")
    print("="*80)
    
    # Get initial state
    print("📊 Recording initial state...")
    state, conversations, agents = get_current_state()
    if not all([state, conversations is not None, agents]):
        print("❌ Failed to get initial state")
        return False
    
    initial_message_count, initial_details = count_messages_in_conversations(conversations)
    initial_conversation_count = len(conversations)
    
    print(f"Initial message count: {initial_message_count}")
    print(f"Initial conversation count: {initial_conversation_count}")
    
    # Test pause functionality
    print("\n⏸️ Testing PAUSE functionality...")
    
    pause_test, pause_response = run_test(
        "Pause Simulation",
        "/simulation/pause",
        method="POST",
        auth=True,
        expected_keys=["message"]
    )
    
    if not pause_test:
        print("❌ Failed to pause simulation")
        return False
    
    print("✅ Simulation paused successfully")
    
    # Check data persistence after pause
    print("\n🔍 Checking data persistence after PAUSE...")
    
    state_after_pause, conv_after_pause, agents_after_pause = get_current_state()
    if not all([state_after_pause, conv_after_pause is not None, agents_after_pause]):
        print("❌ Failed to get state after pause")
        return False
    
    pause_message_count, pause_details = count_messages_in_conversations(conv_after_pause)
    pause_conversation_count = len(conv_after_pause)
    
    print(f"Message count after pause: {pause_message_count}")
    print(f"Conversation count after pause: {pause_conversation_count}")
    
    # Check for data loss after pause
    pause_data_preserved = (pause_message_count == initial_message_count and 
                           pause_conversation_count == initial_conversation_count)
    
    if pause_data_preserved:
        print("✅ Data preserved after PAUSE - no data loss detected")
    else:
        print("❌ Data loss detected after PAUSE!")
        print(f"   Messages: {initial_message_count} → {pause_message_count}")
        print(f"   Conversations: {initial_conversation_count} → {pause_conversation_count}")
    
    # Test resume functionality
    print("\n▶️ Testing RESUME functionality...")
    
    resume_test, resume_response = run_test(
        "Resume Simulation",
        "/simulation/resume",
        method="POST",
        auth=True,
        expected_keys=["message"]
    )
    
    if not resume_test:
        print("❌ Failed to resume simulation")
        return False
    
    print("✅ Simulation resumed successfully")
    
    # Check data persistence after resume
    print("\n🔍 Checking data persistence after RESUME...")
    
    state_after_resume, conv_after_resume, agents_after_resume = get_current_state()
    if not all([state_after_resume, conv_after_resume is not None, agents_after_resume]):
        print("❌ Failed to get state after resume")
        return False
    
    resume_message_count, resume_details = count_messages_in_conversations(conv_after_resume)
    resume_conversation_count = len(conv_after_resume)
    
    print(f"Message count after resume: {resume_message_count}")
    print(f"Conversation count after resume: {resume_conversation_count}")
    
    # Check for data loss after resume
    resume_data_preserved = (resume_message_count == initial_message_count and 
                            resume_conversation_count == initial_conversation_count)
    
    if resume_data_preserved:
        print("✅ Data preserved after RESUME - no data loss detected")
    else:
        print("❌ Data loss detected after RESUME!")
        print(f"   Messages: {initial_message_count} → {resume_message_count}")
        print(f"   Conversations: {initial_conversation_count} → {resume_conversation_count}")
    
    # Overall assessment
    overall_success = pause_data_preserved and resume_data_preserved
    
    if overall_success:
        print("\n✅ PAUSE/RESUME FUNCTIONALITY TEST PASSED!")
        print("✅ No data loss during pause/resume cycle")
        print("✅ All conversations and messages preserved")
        return True
    else:
        print("\n❌ PAUSE/RESUME FUNCTIONALITY TEST FAILED!")
        print("❌ Data loss detected during pause/resume cycle")
        return False

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"MESSAGE SYSTEM FIXES TEST SUMMARY")
    print(f"PASSED: {test_results['passed']} | FAILED: {test_results['failed']}")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i:2d}. {result_symbol} {test['name']}")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution"""
    print("="*80)
    print("MESSAGE SYSTEM FIXES COMPREHENSIVE TESTING")
    print("Testing fixes for: 1 message per agent, time progression, message jumping")
    print("="*80)
    
    # Step 1: Login as guest
    if not login_as_guest():
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Test message generation system (1 message per agent)
    print("\n" + "🔄" * 20)
    message_gen_success = test_message_generation_system()
    
    # Step 3: Test time progression logic
    print("\n" + "🕐" * 20)
    time_progression_success = test_time_progression_logic()
    
    # Step 4: Test message count stability
    print("\n" + "📊" * 20)
    stability_success = test_message_count_stability()
    
    # Step 5: Test pause/resume functionality
    print("\n" + "⏸️" * 20)
    pause_resume_success = test_pause_resume_functionality()
    
    # Print final summary
    print_summary()
    
    # Final assessment
    all_tests_passed = all([
        message_gen_success,
        time_progression_success,
        stability_success,
        pause_resume_success
    ])
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"✅ Message Generation (1 per agent): {'PASSED' if message_gen_success else 'FAILED'}")
    print(f"✅ Time Progression Logic: {'PASSED' if time_progression_success else 'FAILED'}")
    print(f"✅ Message Count Stability: {'PASSED' if stability_success else 'FAILED'}")
    print(f"✅ Pause/Resume Functionality: {'PASSED' if pause_resume_success else 'FAILED'}")
    
    if all_tests_passed:
        print(f"\n🎉 ALL MESSAGE SYSTEM FIXES ARE WORKING CORRECTLY!")
        print(f"✅ The user's issues have been successfully resolved")
    else:
        print(f"\n⚠️ SOME MESSAGE SYSTEM FIXES NEED ATTENTION")
        print(f"❌ Not all user issues have been resolved")

if __name__ == "__main__":
    main()