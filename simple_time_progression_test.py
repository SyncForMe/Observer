#!/usr/bin/env python3
"""
Simple Time Progression Fix Test

Tests the specific requirements from the review request:
1. Log in as guest user
2. Generate a new conversation using POST /api/conversation/generate 
3. Check the simulation state with GET /api/simulation/state to see if current_time_period is updating correctly
4. Generate 2 more conversations (total of 3) - time should advance from morning to afternoon
5. Generate 3 more conversations (total of 6) - time should advance from afternoon to evening  
6. Generate 3 more conversations (total of 9) - time should advance from evening to next day morning
7. Verify that both:
   - Individual conversations have proper time_period metadata
   - Simulation state shows the correct current_time_period
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🧪 SIMPLE TIME PROGRESSION FIX TEST")
print(f"Using API URL: {API_URL}")
print("="*80)

# Global variables
auth_token = None
test_user_id = None

def step_1_guest_login():
    """Step 1: Log in as guest user"""
    global auth_token, test_user_id
    
    print("\n📝 STEP 1: Log in as guest user")
    print("-" * 40)
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        print(f"POST /auth/test-login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            
            print(f"✅ Guest login successful")
            print(f"   User ID: {test_user_id}")
            return True
        else:
            print(f"❌ Guest login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during guest login: {e}")
        return False

def get_simulation_state():
    """Get current simulation state"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get simulation state: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
        return None

def generate_conversation():
    """Generate a conversation"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return None

def get_conversations():
    """Get all conversations"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return None

def step_2_initial_state():
    """Step 2: Check initial simulation state"""
    print("\n📝 STEP 2: Check initial simulation state")
    print("-" * 40)
    
    state = get_simulation_state()
    if state:
        day = state.get('current_day', 1)
        period = state.get('current_time_period', 'unknown')
        print(f"✅ Initial state: Day {day}, {period}")
        return state
    else:
        print("❌ Could not get initial simulation state")
        return None

def step_3_generate_conversations():
    """Step 3: Generate conversations and test time progression"""
    print("\n📝 STEP 3: Generate conversations and test time progression")
    print("-" * 40)
    
    # Expected progression based on the review request
    expected_progression = [
        # (conversation_number, expected_day, expected_period, description)
        (1, 1, "morning", "First conversation - should stay morning"),
        (2, 1, "morning", "Second conversation - should stay morning"),
        (3, 1, "afternoon", "Third conversation - should advance to afternoon"),
        (4, 1, "afternoon", "Fourth conversation - should stay afternoon"),
        (5, 1, "afternoon", "Fifth conversation - should stay afternoon"),
        (6, 1, "evening", "Sixth conversation - should advance to evening"),
        (7, 1, "evening", "Seventh conversation - should stay evening"),
        (8, 1, "evening", "Eighth conversation - should stay evening"),
        (9, 2, "morning", "Ninth conversation - should advance to next day morning"),
    ]
    
    results = []
    
    for conv_num, expected_day, expected_period, description in expected_progression:
        print(f"\n🔄 Generating conversation #{conv_num}")
        print(f"   Expected: Day {expected_day}, {expected_period}")
        print(f"   {description}")
        
        # Generate conversation
        conversation = generate_conversation()
        if not conversation:
            print(f"❌ Failed to generate conversation #{conv_num}")
            results.append({
                'conversation': conv_num,
                'success': False,
                'error': 'Failed to generate conversation'
            })
            continue
        
        # Wait for processing
        time.sleep(1)
        
        # Check simulation state
        state = get_simulation_state()
        if not state:
            print(f"❌ Failed to get simulation state after conversation #{conv_num}")
            results.append({
                'conversation': conv_num,
                'success': False,
                'error': 'Failed to get simulation state'
            })
            continue
        
        actual_day = state.get('current_day', 1)
        actual_period = state.get('current_time_period', 'unknown')
        
        print(f"   Actual: Day {actual_day}, {actual_period}")
        
        # Check if progression is correct
        time_correct = (actual_day == expected_day and actual_period == expected_period)
        
        if time_correct:
            print(f"   ✅ Time progression correct")
        else:
            print(f"   ❌ Time progression incorrect")
            print(f"      Expected: Day {expected_day}, {expected_period}")
            print(f"      Actual: Day {actual_day}, {actual_period}")
        
        results.append({
            'conversation': conv_num,
            'expected_day': expected_day,
            'expected_period': expected_period,
            'actual_day': actual_day,
            'actual_period': actual_period,
            'success': time_correct,
            'description': description
        })
        
        # For critical checkpoints (3, 6, 9), do additional verification
        if conv_num in [3, 6, 9]:
            print(f"   🔍 CRITICAL CHECKPOINT #{conv_num}")
            
            # Verify conversations have proper metadata
            conversations = get_conversations()
            if conversations:
                latest_conv = conversations[-1] if conversations else None
                if latest_conv:
                    conv_time_period = latest_conv.get('time_period', 'unknown')
                    print(f"      Latest conversation time_period: {conv_time_period}")
                    
                    # Check if metadata matches simulation state
                    if f"Day {actual_day}" in conv_time_period and actual_period.lower() in conv_time_period.lower():
                        print(f"      ✅ Conversation metadata matches simulation state")
                    else:
                        print(f"      ❌ Conversation metadata doesn't match simulation state")
                        print(f"         Conversation: {conv_time_period}")
                        print(f"         Simulation: Day {actual_day}, {actual_period}")
    
    return results

def step_4_verify_metadata():
    """Step 4: Verify conversation metadata"""
    print("\n📝 STEP 4: Verify conversation metadata")
    print("-" * 40)
    
    conversations = get_conversations()
    if not conversations:
        print("❌ No conversations found")
        return False
    
    print(f"✅ Found {len(conversations)} conversations")
    
    metadata_correct = True
    for i, conv in enumerate(conversations, 1):
        time_period = conv.get('time_period', 'Not set')
        message_count = len(conv.get('messages', []))
        
        print(f"   Conversation {i}: {time_period} ({message_count} messages)")
        
        if time_period == 'Not set':
            print(f"      ❌ Time period not set in metadata")
            metadata_correct = False
        else:
            print(f"      ✅ Time period properly set")
    
    return metadata_correct

def main():
    """Main test execution"""
    print("Testing the time progression fix implementation")
    print("This should fix the issue where frontend displays 'Day 1, Morning' despite having conversations")
    print("="*80)
    
    # Step 1: Guest login
    if not step_1_guest_login():
        print("\n❌ OVERALL TEST FAILED: Guest login failed")
        return False
    
    # Step 2: Check initial state
    initial_state = step_2_initial_state()
    if not initial_state:
        print("\n❌ OVERALL TEST FAILED: Could not get initial state")
        return False
    
    # Step 3: Generate conversations and test progression
    results = step_3_generate_conversations()
    
    # Step 4: Verify metadata
    metadata_ok = step_4_verify_metadata()
    
    # Final assessment
    print("\n" + "="*80)
    print("📊 FINAL TEST RESULTS")
    print("="*80)
    
    passed_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print(f"\nTime Progression Tests: {passed_tests}/{total_tests} passed")
    
    for result in results:
        if result['success']:
            print(f"✅ Conversation {result['conversation']}: Day {result['actual_day']}, {result['actual_period']}")
        else:
            if 'error' in result:
                print(f"❌ Conversation {result['conversation']}: {result['error']}")
            else:
                print(f"❌ Conversation {result['conversation']}: Expected Day {result['expected_day']}, {result['expected_period']} | Got Day {result['actual_day']}, {result['actual_period']}")
    
    print(f"\nConversation Metadata: {'✅ Correct' if metadata_ok else '❌ Issues found'}")
    
    # Overall result
    overall_success = (passed_tests == total_tests) and metadata_ok
    
    if overall_success:
        print(f"\n🎉 OVERALL RESULT: ✅ ALL TESTS PASSED")
        print(f"✅ Time progression advances correctly every 3 conversations")
        print(f"✅ Simulation state shows correct current_time_period")
        print(f"✅ Individual conversations have proper time_period metadata")
        print(f"✅ The time progression fix is working correctly!")
    else:
        print(f"\n💥 OVERALL RESULT: ❌ SOME TESTS FAILED")
        print(f"❌ Time progression fix needs attention")
        
        if passed_tests < total_tests:
            print(f"   - {total_tests - passed_tests} time progression tests failed")
        if not metadata_ok:
            print(f"   - Conversation metadata issues detected")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)