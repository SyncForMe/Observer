#!/usr/bin/env python3
"""
Simplified Observer Message Chronological Ordering Test

Direct test of the chronological ordering fix for observer messages.
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

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
        "goal": "Test agent for chronological ordering",
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

def add_contextual_message(token):
    """Add a contextual message to create existing conversations"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/conversation/add-contextual-message", headers=headers)
    return response.status_code == 200, response.json() if response.status_code == 200 else None

def send_observer_message(token, message):
    """Send an observer message"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"observer_message": message}
    response = requests.post(f"{API_URL}/observer/send-message", json=data, headers=headers)
    return response.status_code == 200, response.json() if response.status_code == 200 else None

def get_conversations(token):
    """Get all conversations"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def main():
    print("="*80)
    print("OBSERVER MESSAGE CHRONOLOGICAL ORDERING TEST")
    print("="*80)
    
    # Step 1: Authenticate
    print("\n1. Authenticating...")
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    print(f"✅ Authenticated as user: {user_id}")
    
    # Step 2: Create test agents
    print("\n2. Creating test agents...")
    agent1_id = create_agent(token, "Test Agent 1", "scientist")
    agent2_id = create_agent(token, "Test Agent 2", "leader")
    
    if not agent1_id or not agent2_id:
        print("❌ Failed to create test agents")
        return
    print(f"✅ Created agents: {agent1_id}, {agent2_id}")
    
    # Step 3: Start simulation
    print("\n3. Starting simulation...")
    if not start_simulation(token):
        print("❌ Failed to start simulation")
        return
    print("✅ Simulation started")
    
    # Step 4: Create existing conversations
    print("\n4. Creating existing conversations...")
    existing_conversations = []
    
    for i in range(3):
        print(f"Creating conversation {i+1}/3...")
        success, conv_data = add_contextual_message(token)
        if success and conv_data:
            existing_conversations.append(conv_data)
            print(f"✅ Created conversation {i+1}")
            time.sleep(2)  # Wait between conversations
        else:
            print(f"❌ Failed to create conversation {i+1}")
    
    if len(existing_conversations) < 2:
        print("❌ Need at least 2 existing conversations for chronological test")
        return
    
    print(f"✅ Created {len(existing_conversations)} existing conversations")
    
    # Step 5: Get baseline conversations and their timestamps
    print("\n5. Getting baseline conversations...")
    baseline_conversations = get_conversations(token)
    
    if not baseline_conversations:
        print("❌ No baseline conversations found")
        return
    
    # Sort by created_at to get chronological order
    sorted_baseline = sorted(baseline_conversations, key=lambda x: x.get("created_at", ""))
    
    print(f"✅ Found {len(sorted_baseline)} baseline conversations")
    
    # Print baseline conversation timestamps
    print("\nBaseline conversation timestamps:")
    for i, conv in enumerate(sorted_baseline):
        created_at = conv.get("created_at")
        scenario_name = conv.get("scenario_name", "Unknown")
        print(f"  {i+1}. {created_at} - {scenario_name}")
    
    # Get the last conversation timestamp
    last_conversation = sorted_baseline[-1]
    last_timestamp_str = last_conversation.get("created_at")
    
    print(f"\nLast conversation timestamp: {last_timestamp_str}")
    
    # Step 6: Send observer message
    print("\n6. Sending observer message...")
    observer_message = "Team, let's focus on the quantum security protocols and discuss implementation priorities."
    
    obs_success, obs_response = send_observer_message(token, observer_message)
    
    if not obs_success:
        print("❌ Failed to send observer message")
        return
    
    print("✅ Observer message sent successfully")
    
    # Wait for processing
    print("Waiting for observer message processing...")
    time.sleep(5)
    
    # Step 7: Get updated conversations and verify chronological order
    print("\n7. Verifying chronological order...")
    updated_conversations = get_conversations(token)
    
    if not updated_conversations:
        print("❌ No updated conversations found")
        return
    
    # Sort by created_at timestamp
    sorted_updated = sorted(updated_conversations, key=lambda x: x.get("created_at", ""))
    
    print(f"✅ Found {len(sorted_updated)} total conversations after observer message")
    
    # Print all conversation timestamps
    print("\nAll conversations in chronological order:")
    observer_positions = []
    
    for i, conv in enumerate(sorted_updated):
        created_at = conv.get("created_at")
        scenario_name = conv.get("scenario_name", "Unknown")
        round_number = conv.get("round_number", "Unknown")
        
        if scenario_name == "Observer Guidance":
            observer_positions.append(i)
            print(f"  {i+1}. {created_at} - {scenario_name} ⭐ OBSERVER MESSAGE")
        else:
            print(f"  {i+1}. {created_at} - {scenario_name} (Round {round_number})")
    
    # Step 8: Analyze chronological positioning
    print("\n8. Analyzing chronological positioning...")
    
    test_results = {
        "chronological_positioning": False,
        "not_first_message": False,
        "proper_timestamp_calculation": False,
        "database_storage_correct": False
    }
    
    if observer_positions:
        print(f"Observer message(s) found at position(s): {[pos+1 for pos in observer_positions]}")
        
        # Test 1: Observer message should NOT be the first message
        if 0 not in observer_positions:
            print("✅ Observer message does NOT appear as first message")
            test_results["not_first_message"] = True
        else:
            print("❌ Observer message appears as FIRST message (BUG)")
        
        # Test 2: Observer message should be after existing conversations
        baseline_count = len(baseline_conversations)
        observer_after_baseline = all(pos >= baseline_count for pos in observer_positions)
        
        if observer_after_baseline:
            print("✅ Observer message appears AFTER all existing conversations")
            test_results["chronological_positioning"] = True
        else:
            print("❌ Observer message appears BEFORE some existing conversations")
        
        # Test 3: Verify timestamp calculation
        observer_conv = None
        for conv in sorted_updated:
            if conv.get("scenario_name") == "Observer Guidance":
                observer_conv = conv
                break
        
        if observer_conv:
            observer_timestamp = observer_conv.get("created_at")
            
            try:
                # Parse timestamps
                observer_dt = datetime.fromisoformat(observer_timestamp.replace('Z', '+00:00'))
                last_baseline_dt = datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
                
                time_diff = (observer_dt - last_baseline_dt).total_seconds()
                
                print(f"Time difference from last baseline conversation: {time_diff} seconds")
                
                if time_diff >= 1.0:
                    print("✅ Observer message timestamp is ≥1 second after last conversation (CORRECT)")
                    test_results["proper_timestamp_calculation"] = True
                else:
                    print("❌ Observer message timestamp is <1 second after last conversation (INCORRECT)")
                    
            except Exception as e:
                print(f"❌ Error parsing timestamps: {e}")
        
        # Test 4: Database storage verification
        if test_results["chronological_positioning"] and test_results["proper_timestamp_calculation"]:
            print("✅ Database storage and retrieval in correct chronological order")
            test_results["database_storage_correct"] = True
        else:
            print("❌ Database storage/retrieval has chronological order issues")
    
    else:
        print("❌ No observer messages found in conversations")
    
    # Step 9: Final Assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT - CHRONOLOGICAL ORDERING FIX")
    print("="*80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Observer messages have chronologically correct timestamps")
        print("✅ Observer messages appear in proper position when sorted by created_at")
        print("✅ No more 'first message' issue when scrolling up")
        print("✅ Consistent chronological ordering across all conversations")
        print("\n✅ THE CHRONOLOGICAL ORDERING FIX IS WORKING CORRECTLY!")
    else:
        print(f"\n❌ {total_tests - passed_tests} TESTS FAILED")
        print("❌ Observer message chronological ordering fix needs attention")
        
        if not test_results["not_first_message"]:
            print("❌ CRITICAL: Observer messages still appear as first message")
        if not test_results["chronological_positioning"]:
            print("❌ CRITICAL: Observer messages not positioned chronologically")
        if not test_results["proper_timestamp_calculation"]:
            print("❌ CRITICAL: Timestamp calculation logic not working")
        if not test_results["database_storage_correct"]:
            print("❌ CRITICAL: Database storage/retrieval issues")
    
    print("="*80)

if __name__ == "__main__":
    main()