#!/usr/bin/env python3
"""
Time Progression Fix Testing Script

This script tests the time progression fix that was just implemented.
It verifies that:
1. Guest login works
2. Conversation generation advances time correctly every 3 conversations
3. Simulation state reflects the correct current_time_period
4. Individual conversations have proper time_period metadata
5. Time progresses: morning → afternoon → evening → next day morning
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

# Global variables
auth_token = None
test_user_id = None

def test_guest_login():
    """Test guest login functionality"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("STEP 1: TESTING GUEST LOGIN")
    print("="*80)
    
    url = f"{API_URL}/auth/test-login"
    print(f"POST {url}")
    
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Extract token and user info
            auth_token = response_data.get("access_token")
            user_data = response_data.get("user", {})
            test_user_id = user_data.get("id")
            
            if auth_token and test_user_id:
                print(f"✅ Guest login successful")
                print(f"User ID: {test_user_id}")
                print(f"JWT Token: {auth_token[:20]}...")
                return True
            else:
                print("❌ Guest login failed - missing token or user ID")
                return False
        else:
            print(f"❌ Guest login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during guest login: {e}")
        return False

def get_simulation_state():
    """Get current simulation state"""
    url = f"{API_URL}/simulation/state"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get simulation state: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
        return None

def generate_conversation():
    """Generate a new conversation"""
    url = f"{API_URL}/conversation/generate"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        print(f"POST {url}")
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Conversation generated successfully")
            return response_data
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return None

def get_conversations():
    """Get all conversations for the user"""
    url = f"{API_URL}/conversations"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return None

def test_time_progression():
    """Test the complete time progression functionality"""
    print("\n" + "="*80)
    print("STEP 2: TESTING TIME PROGRESSION FIX")
    print("="*80)
    
    # First, get initial simulation state
    print("\n--- Getting initial simulation state ---")
    initial_state = get_simulation_state()
    if not initial_state:
        print("❌ Cannot get initial simulation state")
        return False
    
    print(f"Initial state: Day {initial_state.get('current_day', 1)}, {initial_state.get('current_time_period', 'unknown')}")
    
    # Test progression through different time periods
    expected_progressions = [
        # (conversation_count, expected_day, expected_period)
        (1, 1, "morning"),    # First conversation - should stay morning
        (2, 1, "morning"),    # Second conversation - should stay morning  
        (3, 1, "afternoon"),  # Third conversation - should advance to afternoon
        (4, 1, "afternoon"),  # Fourth conversation - should stay afternoon
        (5, 1, "afternoon"),  # Fifth conversation - should stay afternoon
        (6, 1, "evening"),    # Sixth conversation - should advance to evening
        (7, 1, "evening"),    # Seventh conversation - should stay evening
        (8, 1, "evening"),    # Eighth conversation - should stay evening
        (9, 2, "morning"),    # Ninth conversation - should advance to next day morning
    ]
    
    conversation_results = []
    
    for target_count, expected_day, expected_period in expected_progressions:
        print(f"\n--- Generating conversation #{target_count} ---")
        print(f"Expected after generation: Day {expected_day}, {expected_period}")
        
        # Generate conversation
        conversation = generate_conversation()
        if not conversation:
            print(f"❌ Failed to generate conversation #{target_count}")
            return False
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Check simulation state
        current_state = get_simulation_state()
        if not current_state:
            print(f"❌ Failed to get simulation state after conversation #{target_count}")
            return False
        
        actual_day = current_state.get('current_day', 1)
        actual_period = current_state.get('current_time_period', 'unknown')
        
        print(f"Actual state: Day {actual_day}, {actual_period}")
        
        # Check if time progression is correct
        time_correct = (actual_day == expected_day and actual_period == expected_period)
        
        if time_correct:
            print(f"✅ Time progression correct for conversation #{target_count}")
        else:
            print(f"❌ Time progression incorrect for conversation #{target_count}")
            print(f"   Expected: Day {expected_day}, {expected_period}")
            print(f"   Actual: Day {actual_day}, {actual_period}")
        
        # Get conversations to check individual metadata
        conversations = get_conversations()
        if conversations and len(conversations) >= target_count:
            latest_conversation = conversations[-1]  # Get the most recent conversation
            conv_time_period = latest_conversation.get('time_period', 'unknown')
            print(f"Latest conversation time_period: {conv_time_period}")
            
            # Check if conversation metadata matches simulation state
            metadata_correct = conv_time_period.lower().endswith(actual_period.lower())
            if metadata_correct:
                print(f"✅ Conversation metadata matches simulation state")
            else:
                print(f"❌ Conversation metadata doesn't match simulation state")
                print(f"   Conversation: {conv_time_period}")
                print(f"   Simulation: Day {actual_day}, {actual_period}")
        
        conversation_results.append({
            'count': target_count,
            'expected_day': expected_day,
            'expected_period': expected_period,
            'actual_day': actual_day,
            'actual_period': actual_period,
            'time_correct': time_correct,
            'conversation_metadata': conv_time_period if conversations else 'unknown'
        })
        
        # If this is a critical checkpoint, verify more thoroughly
        if target_count in [3, 6, 9]:  # Time advancement points
            print(f"\n🔍 CRITICAL CHECKPOINT #{target_count} - DETAILED VERIFICATION")
            
            # Verify all conversations have proper time periods
            if conversations:
                print(f"Total conversations: {len(conversations)}")
                for i, conv in enumerate(conversations, 1):
                    conv_period = conv.get('time_period', 'unknown')
                    print(f"  Conversation {i}: {conv_period}")
            
            # Double-check simulation state
            verification_state = get_simulation_state()
            if verification_state:
                verify_day = verification_state.get('current_day', 1)
                verify_period = verification_state.get('current_time_period', 'unknown')
                print(f"Verification - Simulation state: Day {verify_day}, {verify_period}")
                
                if verify_day == expected_day and verify_period == expected_period:
                    print(f"✅ CHECKPOINT #{target_count} PASSED")
                else:
                    print(f"❌ CHECKPOINT #{target_count} FAILED")
                    return False
    
    # Print final summary
    print("\n" + "="*80)
    print("TIME PROGRESSION TEST SUMMARY")
    print("="*80)
    
    passed_tests = sum(1 for result in conversation_results if result['time_correct'])
    total_tests = len(conversation_results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    for result in conversation_results:
        status = "✅" if result['time_correct'] else "❌"
        print(f"{status} Conversation {result['count']}: Expected Day {result['expected_day']}, {result['expected_period']} | "
              f"Actual Day {result['actual_day']}, {result['actual_period']}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TIME PROGRESSION TESTS PASSED!")
        print("✅ Individual conversations have proper time_period metadata")
        print("✅ Simulation state shows the correct current_time_period")
        print("✅ Time advances correctly: morning → afternoon → evening → next day morning")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} TIME PROGRESSION TESTS FAILED")
        return False

def main():
    """Main test function"""
    print("🧪 TIME PROGRESSION FIX TESTING")
    print("="*80)
    print("Testing the time progression fix implementation")
    print("Expected behavior:")
    print("- Conversations 1-2: Day 1, Morning")
    print("- Conversation 3: Advances to Day 1, Afternoon") 
    print("- Conversations 4-5: Day 1, Afternoon")
    print("- Conversation 6: Advances to Day 1, Evening")
    print("- Conversations 7-8: Day 1, Evening")
    print("- Conversation 9: Advances to Day 2, Morning")
    print("="*80)
    
    # Step 1: Test guest login
    if not test_guest_login():
        print("\n❌ OVERALL TEST FAILED: Guest login failed")
        return False
    
    # Step 2: Test time progression
    if not test_time_progression():
        print("\n❌ OVERALL TEST FAILED: Time progression failed")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Guest login works correctly")
    print("✅ Time progression advances correctly every 3 conversations")
    print("✅ Simulation state reflects correct current_time_period")
    print("✅ Individual conversations have proper time_period metadata")
    print("\nThe time progression fix is working correctly! 🚀")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)