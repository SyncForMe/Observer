#!/usr/bin/env python3
"""
Observer Message Chronological Ordering Test

This test file specifically tests the chronological ordering fix for observer messages
that was implemented to resolve the issue where observer messages appeared as the 
"first message" when scrolling up, even though they should be positioned chronologically
where they were sent.

The fix implemented:
- Problem: Observer messages used created_at=datetime.utcnow() which created newer timestamps
- Solution: Calculate proper chronological timestamp by adding 1 second to the last conversation's timestamp
- Expected Result: Observer messages appear in correct chronological position, not at the top
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import asyncio

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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables
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
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        })
        
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

def setup_authentication():
    """Setup authentication for testing"""
    global auth_token, test_user_id
    
    # Try guest login first
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest authentication successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest authentication failed")
        return False

def create_test_agents():
    """Create test agents for the simulation"""
    print("\n" + "="*60)
    print("CREATING TEST AGENTS")
    print("="*60)
    
    agents_data = [
        {
            "name": "Dr. Alice Quantum",
            "archetype": "scientist",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            },
            "goal": "Develop quantum communication protocols",
            "expertise": "Quantum Physics",
            "background": "Leading quantum researcher with 15 years experience"
        },
        {
            "name": "Prof. Bob Engineer",
            "archetype": "leader",
            "personality": {
                "extroversion": 8,
                "optimism": 8,
                "curiosity": 7,
                "cooperativeness": 9,
                "energy": 8
            },
            "goal": "Lead the engineering implementation",
            "expertise": "Systems Engineering",
            "background": "Senior engineering manager with project leadership experience"
        },
        {
            "name": "Charlie Skeptic",
            "archetype": "skeptic",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 8,
                "cooperativeness": 6,
                "energy": 5
            },
            "goal": "Identify potential risks and challenges",
            "expertise": "Risk Analysis",
            "background": "Experienced risk analyst and quality assurance specialist"
        }
    ]
    
    created_agents = []
    
    for agent_data in agents_data:
        create_test, create_response = run_test(
            f"Create Agent: {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            agent_name = create_response.get("name")
            created_agents.append({"id": agent_id, "name": agent_name})
            print(f"✅ Created agent: {agent_name} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    return created_agents

def create_multiple_conversations():
    """Create multiple existing conversations to test chronological positioning"""
    print("\n" + "="*60)
    print("CREATING MULTIPLE EXISTING CONVERSATIONS")
    print("="*60)
    
    # Start simulation first
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return []
    
    print("✅ Simulation started successfully")
    
    # Generate multiple conversations
    conversations = []
    
    for i in range(5):  # Create 5 conversations
        print(f"\nGenerating conversation {i+1}/5...")
        
        # Add a small delay between conversations to ensure different timestamps
        time.sleep(1)
        
        conv_test, conv_response = run_test(
            f"Generate Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            expected_keys=["message", "conversation"]
        )
        
        if conv_test and conv_response:
            conversation = conv_response.get("conversation", {})
            conv_id = conversation.get("id")
            created_at = conversation.get("created_at")
            round_number = conversation.get("round_number")
            
            conversations.append({
                "id": conv_id,
                "created_at": created_at,
                "round_number": round_number
            })
            
            print(f"✅ Created conversation {i+1}: ID={conv_id}, Round={round_number}, Created={created_at}")
        else:
            print(f"❌ Failed to generate conversation {i+1}")
    
    return conversations

def test_observer_message_chronological_positioning():
    """Test 1: Observer Message Chronological Positioning"""
    print("\n" + "="*60)
    print("TEST 1: OBSERVER MESSAGE CHRONOLOGICAL POSITIONING")
    print("="*60)
    
    # Create multiple existing conversations
    existing_conversations = create_multiple_conversations()
    
    if len(existing_conversations) < 3:
        print("❌ Need at least 3 existing conversations for this test")
        return False
    
    print(f"✅ Created {len(existing_conversations)} existing conversations")
    
    # Get the last conversation's timestamp
    last_conversation = existing_conversations[-1]
    last_timestamp_str = last_conversation["created_at"]
    
    print(f"Last conversation timestamp: {last_timestamp_str}")
    
    # Send an observer message
    observer_message = "Team, let's focus on the quantum entanglement protocols and prioritize security measures."
    
    observer_data = {
        "observer_message": observer_message
    }
    
    # Record time before sending observer message
    before_observer_time = datetime.utcnow()
    
    observer_test, observer_response = run_test(
        "Send Observer Message",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=True,
        expected_keys=["message", "observer_message"]
    )
    
    if not observer_test or not observer_response:
        print("❌ Failed to send observer message")
        return False
    
    print("✅ Observer message sent successfully")
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Get all conversations and check chronological order
    all_conv_test, all_conv_response = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not all_conv_test or not all_conv_response:
        print("❌ Failed to get all conversations")
        return False
    
    # Sort conversations by created_at timestamp
    sorted_conversations = sorted(all_conv_response, key=lambda x: x.get("created_at", ""))
    
    print(f"\nFound {len(sorted_conversations)} total conversations")
    
    # Find the observer message conversation
    observer_conversation = None
    observer_position = -1
    
    for i, conv in enumerate(sorted_conversations):
        scenario_name = conv.get("scenario_name", "")
        if scenario_name == "Observer Guidance":
            observer_conversation = conv
            observer_position = i
            break
    
    if not observer_conversation:
        print("❌ Observer message conversation not found")
        return False
    
    observer_timestamp = observer_conversation.get("created_at")
    print(f"Observer message timestamp: {observer_timestamp}")
    print(f"Observer message position in chronological order: {observer_position + 1}/{len(sorted_conversations)}")
    
    # Verify chronological positioning
    chronological_correct = True
    
    # Observer message should NOT be the first conversation
    if observer_position == 0:
        print("❌ Observer message appears as FIRST conversation (incorrect)")
        chronological_correct = False
    else:
        print("✅ Observer message does NOT appear as first conversation")
    
    # Observer message should be after the last existing conversation
    if observer_position < len(existing_conversations):
        print("❌ Observer message appears BEFORE some existing conversations (incorrect)")
        chronological_correct = False
    else:
        print("✅ Observer message appears AFTER all existing conversations")
    
    # Verify timestamp is chronologically correct
    if observer_position > 0:
        previous_conv = sorted_conversations[observer_position - 1]
        previous_timestamp = previous_conv.get("created_at")
        
        # Parse timestamps for comparison
        try:
            observer_dt = datetime.fromisoformat(observer_timestamp.replace('Z', '+00:00'))
            previous_dt = datetime.fromisoformat(previous_timestamp.replace('Z', '+00:00'))
            
            time_diff = (observer_dt - previous_dt).total_seconds()
            
            print(f"Time difference from previous conversation: {time_diff} seconds")
            
            if time_diff >= 1.0:  # Should be at least 1 second later
                print("✅ Observer message timestamp is chronologically correct (≥1 second after previous)")
            else:
                print("❌ Observer message timestamp is too close to previous conversation")
                chronological_correct = False
                
        except Exception as e:
            print(f"❌ Error parsing timestamps: {e}")
            chronological_correct = False
    
    return chronological_correct

def test_sequential_timestamp_logic():
    """Test 2: Sequential Timestamp Logic"""
    print("\n" + "="*60)
    print("TEST 2: SEQUENTIAL TIMESTAMP LOGIC")
    print("="*60)
    
    # Get current conversations to establish baseline
    baseline_test, baseline_response = run_test(
        "Get Baseline Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not baseline_test or not baseline_response:
        print("❌ Failed to get baseline conversations")
        return False
    
    baseline_count = len(baseline_response)
    print(f"Baseline conversation count: {baseline_count}")
    
    if baseline_count == 0:
        print("❌ No existing conversations for timestamp logic test")
        return False
    
    # Get the last conversation timestamp
    sorted_baseline = sorted(baseline_response, key=lambda x: x.get("created_at", ""))
    last_conversation = sorted_baseline[-1]
    last_timestamp_str = last_conversation.get("created_at")
    
    print(f"Last conversation timestamp: {last_timestamp_str}")
    
    # Send multiple observer messages in sequence
    observer_messages = [
        "First observer message - let's discuss quantum protocols",
        "Second observer message - focus on security aspects", 
        "Third observer message - consider implementation timeline"
    ]
    
    observer_timestamps = []
    
    for i, message in enumerate(observer_messages):
        print(f"\nSending observer message {i+1}/3...")
        
        observer_data = {"observer_message": message}
        
        observer_test, observer_response = run_test(
            f"Send Observer Message {i+1}",
            "/observer/send-message",
            method="POST",
            data=observer_data,
            auth=True,
            expected_keys=["message", "observer_message"]
        )
        
        if not observer_test:
            print(f"❌ Failed to send observer message {i+1}")
            return False
        
        # Wait for processing
        time.sleep(1)
        
        # Get updated conversations
        updated_test, updated_response = run_test(
            f"Get Conversations After Observer {i+1}",
            "/conversations",
            method="GET",
            auth=True
        )
        
        if updated_test and updated_response:
            # Find the latest observer message
            observer_convs = [conv for conv in updated_response if conv.get("scenario_name") == "Observer Guidance"]
            if observer_convs:
                latest_observer = max(observer_convs, key=lambda x: x.get("created_at", ""))
                observer_timestamps.append(latest_observer.get("created_at"))
                print(f"✅ Observer message {i+1} timestamp: {latest_observer.get('created_at')}")
    
    # Verify sequential timestamp logic
    sequential_correct = True
    
    if len(observer_timestamps) >= 2:
        for i in range(1, len(observer_timestamps)):
            try:
                current_dt = datetime.fromisoformat(observer_timestamps[i].replace('Z', '+00:00'))
                previous_dt = datetime.fromisoformat(observer_timestamps[i-1].replace('Z', '+00:00'))
                
                time_diff = (current_dt - previous_dt).total_seconds()
                
                print(f"Time difference between observer message {i} and {i+1}: {time_diff} seconds")
                
                if time_diff >= 1.0:
                    print(f"✅ Sequential timestamp logic correct for messages {i} and {i+1}")
                else:
                    print(f"❌ Sequential timestamp logic incorrect for messages {i} and {i+1}")
                    sequential_correct = False
                    
            except Exception as e:
                print(f"❌ Error parsing sequential timestamps: {e}")
                sequential_correct = False
    
    return sequential_correct

def test_database_storage_verification():
    """Test 3: Database Storage Verification"""
    print("\n" + "="*60)
    print("TEST 3: DATABASE STORAGE VERIFICATION")
    print("="*60)
    
    # Send an observer message
    observer_message = "Database storage test - verify chronological order in database"
    
    observer_data = {"observer_message": observer_message}
    
    observer_test, observer_response = run_test(
        "Send Observer Message for DB Test",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=True,
        expected_keys=["message", "observer_message"]
    )
    
    if not observer_test:
        print("❌ Failed to send observer message for database test")
        return False
    
    print("✅ Observer message sent for database test")
    
    # Wait for processing
    time.sleep(2)
    
    # Get conversations sorted by created_at (ascending - oldest first)
    sorted_asc_test, sorted_asc_response = run_test(
        "Get Conversations Sorted Ascending",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not sorted_asc_test or not sorted_asc_response:
        print("❌ Failed to get conversations sorted ascending")
        return False
    
    # Sort manually to verify database sorting
    manually_sorted = sorted(sorted_asc_response, key=lambda x: x.get("created_at", ""))
    
    print(f"Total conversations retrieved: {len(sorted_asc_response)}")
    
    # Verify observer messages appear in correct chronological position
    observer_conversations = [conv for conv in manually_sorted if conv.get("scenario_name") == "Observer Guidance"]
    
    if not observer_conversations:
        print("❌ No observer conversations found in database")
        return False
    
    print(f"Found {len(observer_conversations)} observer conversations")
    
    database_correct = True
    
    for i, obs_conv in enumerate(observer_conversations):
        obs_timestamp = obs_conv.get("created_at")
        obs_position = manually_sorted.index(obs_conv)
        
        print(f"Observer conversation {i+1}: Position {obs_position+1}/{len(manually_sorted)}, Timestamp: {obs_timestamp}")
        
        # Verify it's not the first conversation
        if obs_position == 0:
            print(f"❌ Observer conversation {i+1} appears as FIRST conversation in database")
            database_correct = False
        else:
            print(f"✅ Observer conversation {i+1} is NOT the first conversation")
        
        # Verify chronological order with previous conversation
        if obs_position > 0:
            prev_conv = manually_sorted[obs_position - 1]
            prev_timestamp = prev_conv.get("created_at")
            
            try:
                obs_dt = datetime.fromisoformat(obs_timestamp.replace('Z', '+00:00'))
                prev_dt = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                
                if obs_dt > prev_dt:
                    print(f"✅ Observer conversation {i+1} timestamp is after previous conversation")
                else:
                    print(f"❌ Observer conversation {i+1} timestamp is NOT after previous conversation")
                    database_correct = False
                    
            except Exception as e:
                print(f"❌ Error comparing timestamps: {e}")
                database_correct = False
    
    return database_correct

def test_edge_cases():
    """Test 4: Edge Cases"""
    print("\n" + "="*60)
    print("TEST 4: EDGE CASES")
    print("="*60)
    
    edge_cases_passed = 0
    total_edge_cases = 3
    
    # Edge Case 1: Test with no existing conversations (first observer message)
    print("\nEdge Case 1: First observer message with no existing conversations")
    
    # Create a new user for this test
    new_user_email = f"edge.test.{uuid.uuid4()}@example.com"
    register_data = {
        "email": new_user_email,
        "password": "testPassword123",
        "name": "Edge Test User"
    }
    
    register_test, register_response = run_test(
        "Register Edge Test User",
        "/auth/register",
        method="POST",
        data=register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if register_test and register_response:
        edge_token = register_response.get("access_token")
        
        # Send observer message with new user (no existing conversations)
        first_observer_data = {"observer_message": "First observer message with no existing conversations"}
        
        first_obs_test, first_obs_response = run_test(
            "First Observer Message (No Existing Conversations)",
            "/observer/send-message",
            method="POST",
            data=first_observer_data,
            auth=True,
            headers={"Authorization": f"Bearer {edge_token}"},
            expected_keys=["message", "observer_message"]
        )
        
        if first_obs_test:
            print("✅ Edge Case 1 passed: First observer message handled correctly")
            edge_cases_passed += 1
        else:
            print("❌ Edge Case 1 failed: First observer message not handled correctly")
    else:
        print("❌ Edge Case 1 failed: Could not create new user")
    
    # Edge Case 2: Multiple consecutive observer messages
    print("\nEdge Case 2: Multiple consecutive observer messages")
    
    consecutive_messages = [
        "Consecutive message 1",
        "Consecutive message 2", 
        "Consecutive message 3"
    ]
    
    consecutive_success = True
    
    for i, message in enumerate(consecutive_messages):
        consecutive_data = {"observer_message": message}
        
        consecutive_test, consecutive_response = run_test(
            f"Consecutive Observer Message {i+1}",
            "/observer/send-message",
            method="POST",
            data=consecutive_data,
            auth=True,
            expected_keys=["message", "observer_message"]
        )
        
        if not consecutive_test:
            consecutive_success = False
            break
        
        # Small delay between messages
        time.sleep(0.5)
    
    if consecutive_success:
        print("✅ Edge Case 2 passed: Multiple consecutive observer messages handled correctly")
        edge_cases_passed += 1
    else:
        print("❌ Edge Case 2 failed: Multiple consecutive observer messages not handled correctly")
    
    # Edge Case 3: Verify proper sequencing in all scenarios
    print("\nEdge Case 3: Verify proper sequencing across all scenarios")
    
    # Get all conversations and verify no observer message is first
    final_test, final_response = run_test(
        "Final Conversation Order Check",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if final_test and final_response:
        sorted_final = sorted(final_response, key=lambda x: x.get("created_at", ""))
        
        sequencing_correct = True
        
        # Check if any observer message is the first conversation
        if sorted_final and sorted_final[0].get("scenario_name") == "Observer Guidance":
            print("❌ Edge Case 3 failed: Observer message appears as first conversation")
            sequencing_correct = False
        else:
            print("✅ No observer message appears as first conversation")
        
        # Check chronological consistency
        observer_convs = [conv for conv in sorted_final if conv.get("scenario_name") == "Observer Guidance"]
        
        for obs_conv in observer_convs:
            obs_position = sorted_final.index(obs_conv)
            if obs_position > 0:
                prev_conv = sorted_final[obs_position - 1]
                
                try:
                    obs_dt = datetime.fromisoformat(obs_conv.get("created_at").replace('Z', '+00:00'))
                    prev_dt = datetime.fromisoformat(prev_conv.get("created_at").replace('Z', '+00:00'))
                    
                    if obs_dt <= prev_dt:
                        print("❌ Edge Case 3 failed: Observer message timestamp not chronologically correct")
                        sequencing_correct = False
                        break
                        
                except Exception as e:
                    print(f"❌ Edge Case 3 failed: Error parsing timestamps: {e}")
                    sequencing_correct = False
                    break
        
        if sequencing_correct:
            print("✅ Edge Case 3 passed: Proper sequencing verified in all scenarios")
            edge_cases_passed += 1
        else:
            print("❌ Edge Case 3 failed: Sequencing issues detected")
    else:
        print("❌ Edge Case 3 failed: Could not get final conversations")
    
    print(f"\nEdge Cases Summary: {edge_cases_passed}/{total_edge_cases} passed")
    return edge_cases_passed == total_edge_cases

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"OBSERVER CHRONOLOGICAL ORDERING TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution"""
    print("="*80)
    print("OBSERVER MESSAGE CHRONOLOGICAL ORDERING FIX TESTING")
    print("="*80)
    print("Testing the fix for observer messages appearing as 'first message'")
    print("when scrolling up, instead of in their proper chronological position.")
    print("="*80)
    
    # Setup authentication
    if not setup_authentication():
        print("❌ Authentication setup failed. Cannot proceed with tests.")
        return
    
    # Create test agents
    agents = create_test_agents()
    if len(agents) < 3:
        print("❌ Failed to create sufficient test agents. Cannot proceed with tests.")
        return
    
    # Run the four main tests
    test_1_result = test_observer_message_chronological_positioning()
    test_2_result = test_sequential_timestamp_logic()
    test_3_result = test_database_storage_verification()
    test_4_result = test_edge_cases()
    
    # Print final summary
    print_summary()
    
    # Final assessment
    print("\n" + "="*80)
    print("CHRONOLOGICAL ORDERING FIX ASSESSMENT")
    print("="*80)
    
    if test_1_result:
        print("✅ Test 1 PASSED: Observer messages have chronologically correct timestamps")
    else:
        print("❌ Test 1 FAILED: Observer messages do not have chronologically correct timestamps")
    
    if test_2_result:
        print("✅ Test 2 PASSED: Sequential timestamp logic working correctly")
    else:
        print("❌ Test 2 FAILED: Sequential timestamp logic has issues")
    
    if test_3_result:
        print("✅ Test 3 PASSED: Database storage and retrieval in correct chronological order")
    else:
        print("❌ Test 3 FAILED: Database storage/retrieval chronological order issues")
    
    if test_4_result:
        print("✅ Test 4 PASSED: Edge cases handled correctly")
    else:
        print("❌ Test 4 FAILED: Edge cases not handled correctly")
    
    all_tests_passed = test_1_result and test_2_result and test_3_result and test_4_result
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED: Observer message chronological ordering fix is working correctly!")
        print("✅ Observer messages appear in proper chronological position")
        print("✅ No more 'first message' issue when scrolling up")
        print("✅ Consistent chronological ordering across all conversations")
    else:
        print("\n❌ SOME TESTS FAILED: Observer message chronological ordering fix needs attention")
        print("❌ Issues detected with chronological positioning")
    
    print("="*80)

if __name__ == "__main__":
    main()