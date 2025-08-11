#!/usr/bin/env python3
"""
Observer Message Edge Cases Test

Test edge cases for the chronological ordering fix:
1. First observer message with no existing conversations
2. Multiple consecutive observer messages
3. Observer messages mixed with regular conversations
"""

import requests
import json
import time
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def create_new_user():
    """Create a new user for edge case testing"""
    user_email = f"edge.test.{uuid.uuid4()}@example.com"
    register_data = {
        "email": user_email,
        "password": "testPassword123",
        "name": "Edge Test User"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=register_data)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user", {}).get("id")
    return None, None

def authenticate():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user", {}).get("id")
    return None, None

def create_agent(token, name, archetype):
    """Create a test agent"""
    agent_data = {
        "name": name,
        "archetype": archetype,
        "personality": {
            "extroversion": 6,
            "optimism": 7,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": "Test agent for edge cases",
        "expertise": "Testing",
        "background": "Test agent background"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("id")
    return None

def start_simulation(token):
    """Start the simulation"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    return response.status_code == 200

def send_observer_message(token, message):
    """Send an observer message"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"observer_message": message}
    response = requests.post(f"{API_URL}/observer/send-message", json=data, headers=headers)
    return response.status_code == 200, response.json() if response.status_code == 200 else None

def add_contextual_message(token):
    """Add a contextual message"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/conversation/add-contextual-message", headers=headers)
    return response.status_code == 200, response.json() if response.status_code == 200 else None

def get_conversations(token):
    """Get all conversations"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def test_first_observer_message_no_existing_conversations():
    """Edge Case 1: First observer message with no existing conversations"""
    print("\n" + "="*80)
    print("EDGE CASE 1: FIRST OBSERVER MESSAGE (NO EXISTING CONVERSATIONS)")
    print("="*80)
    
    # Create a new user with no existing conversations
    token, user_id = create_new_user()
    if not token:
        print("❌ Failed to create new user")
        return False
    
    print(f"✅ Created new user: {user_id}")
    
    # Create agents
    agent1_id = create_agent(token, "Edge Test Agent 1", "scientist")
    agent2_id = create_agent(token, "Edge Test Agent 2", "leader")
    
    if not agent1_id or not agent2_id:
        print("❌ Failed to create test agents")
        return False
    
    print("✅ Created test agents")
    
    # Start simulation
    if not start_simulation(token):
        print("❌ Failed to start simulation")
        return False
    
    print("✅ Started simulation")
    
    # Verify no existing conversations
    initial_conversations = get_conversations(token)
    if initial_conversations:
        print(f"❌ Expected no conversations, but found {len(initial_conversations)}")
        return False
    
    print("✅ Confirmed no existing conversations")
    
    # Send first observer message
    obs_success, obs_response = send_observer_message(token, "First observer message with no existing conversations")
    
    if not obs_success:
        print("❌ Failed to send first observer message")
        return False
    
    print("✅ Sent first observer message")
    
    # Wait and get conversations
    time.sleep(3)
    conversations = get_conversations(token)
    
    if not conversations:
        print("❌ No conversations found after observer message")
        return False
    
    # Verify observer message was created successfully
    observer_convs = [conv for conv in conversations if conv.get("scenario_name") == "Observer Guidance"]
    
    if not observer_convs:
        print("❌ Observer message conversation not found")
        return False
    
    print("✅ Observer message conversation created successfully")
    
    # Verify timestamp is reasonable (should be recent)
    observer_conv = observer_convs[0]
    observer_timestamp = observer_conv.get("created_at")
    
    try:
        observer_dt = datetime.fromisoformat(observer_timestamp.replace('Z', '+00:00'))
        now = datetime.utcnow().replace(tzinfo=observer_dt.tzinfo)
        time_diff = (now - observer_dt).total_seconds()
        
        if time_diff < 60:  # Should be within last minute
            print(f"✅ Observer message timestamp is recent ({time_diff:.1f} seconds ago)")
            return True
        else:
            print(f"❌ Observer message timestamp is too old ({time_diff:.1f} seconds ago)")
            return False
            
    except Exception as e:
        print(f"❌ Error parsing timestamp: {e}")
        return False

def test_multiple_consecutive_observer_messages():
    """Edge Case 2: Multiple consecutive observer messages"""
    print("\n" + "="*80)
    print("EDGE CASE 2: MULTIPLE CONSECUTIVE OBSERVER MESSAGES")
    print("="*80)
    
    # Use existing authentication
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Get baseline conversations
    baseline_conversations = get_conversations(token)
    baseline_count = len(baseline_conversations)
    
    print(f"✅ Baseline conversations: {baseline_count}")
    
    # Send multiple consecutive observer messages
    observer_messages = [
        "Consecutive observer message 1 - discussing quantum protocols",
        "Consecutive observer message 2 - focusing on security measures",
        "Consecutive observer message 3 - implementation timeline review"
    ]
    
    observer_timestamps = []
    
    for i, message in enumerate(observer_messages):
        print(f"\nSending observer message {i+1}/3...")
        
        obs_success, obs_response = send_observer_message(token, message)
        
        if not obs_success:
            print(f"❌ Failed to send observer message {i+1}")
            return False
        
        print(f"✅ Sent observer message {i+1}")
        
        # Wait between messages
        time.sleep(2)
        
        # Get updated conversations
        updated_conversations = get_conversations(token)
        observer_convs = [conv for conv in updated_conversations if conv.get("scenario_name") == "Observer Guidance"]
        
        if observer_convs:
            # Get the latest observer message
            latest_observer = max(observer_convs, key=lambda x: x.get("created_at", ""))
            observer_timestamps.append(latest_observer.get("created_at"))
            print(f"✅ Observer message {i+1} timestamp: {latest_observer.get('created_at')}")
    
    # Verify sequential timestamps
    if len(observer_timestamps) >= 2:
        sequential_correct = True
        
        for i in range(1, len(observer_timestamps)):
            try:
                current_dt = datetime.fromisoformat(observer_timestamps[i].replace('Z', '+00:00'))
                previous_dt = datetime.fromisoformat(observer_timestamps[i-1].replace('Z', '+00:00'))
                
                time_diff = (current_dt - previous_dt).total_seconds()
                
                print(f"Time difference between message {i} and {i+1}: {time_diff} seconds")
                
                if time_diff >= 1.0:
                    print(f"✅ Sequential timestamp correct for messages {i} and {i+1}")
                else:
                    print(f"❌ Sequential timestamp incorrect for messages {i} and {i+1}")
                    sequential_correct = False
                    
            except Exception as e:
                print(f"❌ Error parsing sequential timestamps: {e}")
                sequential_correct = False
        
        return sequential_correct
    else:
        print("❌ Not enough observer messages for sequential test")
        return False

def test_observer_messages_mixed_with_regular_conversations():
    """Edge Case 3: Observer messages mixed with regular conversations"""
    print("\n" + "="*80)
    print("EDGE CASE 3: OBSERVER MESSAGES MIXED WITH REGULAR CONVERSATIONS")
    print("="*80)
    
    # Use existing authentication
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Create a pattern: Regular -> Observer -> Regular -> Observer
    print("\nCreating mixed conversation pattern...")
    
    # Add regular conversation
    print("Adding regular conversation 1...")
    reg_success1, reg_data1 = add_contextual_message(token)
    if reg_success1:
        print("✅ Added regular conversation 1")
    else:
        print("❌ Failed to add regular conversation 1")
        return False
    
    time.sleep(2)
    
    # Add observer message
    print("Adding observer message 1...")
    obs_success1, obs_data1 = send_observer_message(token, "Observer message between regular conversations")
    if obs_success1:
        print("✅ Added observer message 1")
    else:
        print("❌ Failed to add observer message 1")
        return False
    
    time.sleep(2)
    
    # Add another regular conversation
    print("Adding regular conversation 2...")
    reg_success2, reg_data2 = add_contextual_message(token)
    if reg_success2:
        print("✅ Added regular conversation 2")
    else:
        print("❌ Failed to add regular conversation 2")
        return False
    
    time.sleep(2)
    
    # Add another observer message
    print("Adding observer message 2...")
    obs_success2, obs_data2 = send_observer_message(token, "Final observer message in mixed pattern")
    if obs_success2:
        print("✅ Added observer message 2")
    else:
        print("❌ Failed to add observer message 2")
        return False
    
    time.sleep(3)
    
    # Get all conversations and verify chronological order
    all_conversations = get_conversations(token)
    
    if not all_conversations:
        print("❌ No conversations found")
        return False
    
    # Sort by timestamp
    sorted_conversations = sorted(all_conversations, key=lambda x: x.get("created_at", ""))
    
    print(f"\n✅ Found {len(sorted_conversations)} total conversations")
    print("\nChronological order verification:")
    
    chronological_correct = True
    
    for i, conv in enumerate(sorted_conversations):
        created_at = conv.get("created_at")
        scenario_name = conv.get("scenario_name", "Unknown")
        round_number = conv.get("round_number", "Unknown")
        
        if scenario_name == "Observer Guidance":
            print(f"  {i+1}. {created_at} - {scenario_name} ⭐ OBSERVER")
        else:
            print(f"  {i+1}. {created_at} - {scenario_name} (Round {round_number})")
        
        # Verify timestamp is after previous conversation
        if i > 0:
            prev_conv = sorted_conversations[i-1]
            prev_timestamp = prev_conv.get("created_at")
            
            try:
                current_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                prev_dt = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                
                if current_dt <= prev_dt:
                    print(f"❌ Conversation {i+1} timestamp is not after previous conversation")
                    chronological_correct = False
                    
            except Exception as e:
                print(f"❌ Error comparing timestamps: {e}")
                chronological_correct = False
    
    if chronological_correct:
        print("✅ All conversations are in correct chronological order")
        return True
    else:
        print("❌ Chronological order issues detected")
        return False

def main():
    print("="*80)
    print("OBSERVER MESSAGE CHRONOLOGICAL ORDERING - EDGE CASES TEST")
    print("="*80)
    
    # Run edge case tests
    test1_result = test_first_observer_message_no_existing_conversations()
    test2_result = test_multiple_consecutive_observer_messages()
    test3_result = test_observer_messages_mixed_with_regular_conversations()
    
    # Final assessment
    print("\n" + "="*80)
    print("EDGE CASES TEST RESULTS")
    print("="*80)
    
    passed_tests = sum([test1_result, test2_result, test3_result])
    total_tests = 3
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if test1_result:
        print("✅ PASSED: First observer message with no existing conversations")
    else:
        print("❌ FAILED: First observer message with no existing conversations")
    
    if test2_result:
        print("✅ PASSED: Multiple consecutive observer messages")
    else:
        print("❌ FAILED: Multiple consecutive observer messages")
    
    if test3_result:
        print("✅ PASSED: Observer messages mixed with regular conversations")
    else:
        print("❌ FAILED: Observer messages mixed with regular conversations")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL EDGE CASE TESTS PASSED!")
        print("✅ Observer message chronological ordering is robust")
        print("✅ Edge cases are handled correctly")
        print("✅ The fix works in all scenarios")
    else:
        print(f"\n❌ {total_tests - passed_tests} EDGE CASE TESTS FAILED")
        print("❌ Some edge cases need attention")
    
    print("="*80)

if __name__ == "__main__":
    main()