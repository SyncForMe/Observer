#!/usr/bin/env python3
"""
Time Progression Diagnostic Test
Specifically tests the user's reported issue: time display stuck on "Day 1, Morning"
"""
import requests
import json
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

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

# Global variables
auth_token = None
test_user_id = None

def login_as_guest():
    """Step 1: Log in as guest user"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("STEP 1: LOGGING IN AS GUEST USER")
    print("="*80)
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            
            print(f"✅ Guest login successful")
            print(f"User ID: {test_user_id}")
            print(f"Token: {auth_token[:20]}...")
            return True
        else:
            print(f"❌ Guest login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during guest login: {e}")
        return False

def get_all_conversations():
    """Step 2: Get all conversations for the user via GET /api/conversations"""
    print("\n" + "="*80)
    print("STEP 2: GETTING ALL CONVERSATIONS VIA GET /api/conversations")
    print("="*80)
    
    if not auth_token:
        print("❌ No auth token available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Request URL: {API_URL}/conversations")
        print(f"Headers: Authorization: Bearer {auth_token[:20]}...")
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Retrieved {len(conversations)} conversations")
            
            if len(conversations) == 0:
                print("⚠️ No conversations found - this explains why frontend shows 'Day 1, Morning'")
                print("   The user has no conversation history to display time progression")
                return []
            
            return conversations
        else:
            print(f"❌ Failed to get conversations")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return None

def analyze_conversation_metadata(conversations):
    """Step 3: Check each conversation's round_number, time_period, created timestamps"""
    print("\n" + "="*80)
    print("STEP 3: ANALYZING CONVERSATION METADATA")
    print("="*80)
    
    if not conversations:
        print("❌ No conversations to analyze")
        return False
    
    print(f"Total conversations to analyze: {len(conversations)}")
    
    # Sort conversations by created_at timestamp for chronological analysis
    try:
        sorted_conversations = sorted(conversations, key=lambda x: x.get('created_at', ''))
    except:
        sorted_conversations = conversations
    
    time_periods_found = []
    round_numbers_found = []
    
    print("\nDETAILED CONVERSATION ANALYSIS:")
    print("-" * 80)
    
    for i, conv in enumerate(sorted_conversations):
        round_number = conv.get('round_number', 'Missing')
        time_period = conv.get('time_period', 'Missing')
        created_at = conv.get('created_at', 'Missing')
        scenario_name = conv.get('scenario_name', 'Missing')
        message_count = len(conv.get('messages', []))
        
        print(f"\nConversation {i + 1}:")
        print(f"  Round Number: {round_number}")
        print(f"  Time Period: {time_period}")
        print(f"  Created At: {created_at}")
        print(f"  Scenario: {scenario_name}")
        print(f"  Message Count: {message_count}")
        
        # Collect data for analysis
        if time_period != 'Missing':
            time_periods_found.append(time_period)
        if round_number != 'Missing':
            round_numbers_found.append(round_number)
    
    # Analyze time progression patterns
    print("\n" + "-"*60)
    print("TIME PROGRESSION PATTERN ANALYSIS")
    print("-"*60)
    
    unique_time_periods = list(set(time_periods_found))
    unique_round_numbers = list(set(round_numbers_found))
    
    print(f"Unique time periods found: {unique_time_periods}")
    print(f"Unique round numbers found: {unique_round_numbers}")
    
    # Check for the specific issue: stuck on "Day 1, Morning"
    if len(unique_time_periods) == 1:
        stuck_period = unique_time_periods[0]
        if stuck_period in ["Day 1 - Morning", "morning", "Day 1 Morning"]:
            print("\n❌ TIME PROGRESSION ISSUE CONFIRMED:")
            print(f"   All {len(conversations)} conversations are stuck on '{stuck_period}'")
            print("   Expected progression: Morning → Afternoon → Evening → Next Day")
            print("   This is exactly the issue reported by the user")
            return False
        else:
            print(f"\n⚠️ All conversations have same time period: {stuck_period}")
            print("   This may indicate a time progression issue")
            return False
    elif len(unique_time_periods) > 1:
        print("\n✅ TIME PROGRESSION IS WORKING:")
        print(f"   Found {len(unique_time_periods)} different time periods")
        
        # Count occurrences of each time period
        for period in unique_time_periods:
            count = time_periods_found.count(period)
            print(f"   - {period}: {count} conversations")
        
        # Check if progression follows expected pattern
        expected_sequence = ["Day 1 - Morning", "Day 1 - Afternoon", "Day 1 - Evening", "Day 2 - Morning"]
        found_expected = [period for period in expected_sequence if period in unique_time_periods]
        
        if len(found_expected) > 1:
            print(f"   ✅ Found expected progression sequence: {found_expected}")
        
        return True
    else:
        print("\n⚠️ NO TIME PERIOD DATA FOUND")
        print("   Conversations exist but have no time_period metadata")
        return False

def verify_time_progression_system():
    """Step 4: Verify if the time progression system is working correctly"""
    print("\n" + "="*80)
    print("STEP 4: VERIFYING TIME PROGRESSION SYSTEM")
    print("="*80)
    
    # Get simulation state to see current time
    if not auth_token:
        print("❌ No auth token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            state = response.json()
            print(f"✅ Retrieved simulation state")
            
            # Display key state information
            current_day = state.get('current_day', 'Unknown')
            current_time_period = state.get('current_time_period', 'Unknown')
            scenario = state.get('scenario', 'Unknown')
            is_active = state.get('is_active', False)
            
            print(f"\nSIMULATION STATE:")
            print(f"  Current Day: {current_day}")
            print(f"  Current Time Period: {current_time_period}")
            print(f"  Scenario: {scenario}")
            print(f"  Is Active: {is_active}")
            
            # Check if simulation state matches the issue
            if current_time_period in ["morning", "Day 1 - Morning"]:
                print(f"\n⚠️ SIMULATION STATE CONFIRMS ISSUE:")
                print(f"   Simulation state shows time period as '{current_time_period}'")
                print("   This matches the user's report of being stuck on 'Day 1, Morning'")
            
            return state
        else:
            print(f"❌ Failed to get simulation state: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
        return None

def diagnose_frontend_vs_backend_issue(conversations, simulation_state):
    """Step 5: Diagnose if this is a backend data issue or frontend display issue"""
    print("\n" + "="*80)
    print("STEP 5: DIAGNOSING FRONTEND VS BACKEND ISSUE")
    print("="*80)
    
    # Analyze the data to determine root cause
    has_conversations = conversations and len(conversations) > 0
    has_time_progression = False
    backend_time_stuck = False
    
    if has_conversations:
        # Check if conversations show time progression
        time_periods = [conv.get('time_period', '') for conv in conversations]
        unique_periods = list(set(time_periods))
        has_time_progression = len(unique_periods) > 1
        
        # Check if backend data is stuck on morning
        morning_variants = ["Day 1 - Morning", "morning", "Day 1 Morning"]
        backend_time_stuck = len(unique_periods) == 1 and unique_periods[0] in morning_variants
    
    simulation_stuck_on_morning = False
    if simulation_state:
        sim_period = simulation_state.get('current_time_period', '')
        simulation_stuck_on_morning = sim_period in ["morning", "Day 1 - Morning"]
    
    print("DIAGNOSTIC ANALYSIS:")
    print(f"  Has conversations: {has_conversations}")
    print(f"  Has time progression in data: {has_time_progression}")
    print(f"  Backend time stuck on morning: {backend_time_stuck}")
    print(f"  Simulation state stuck on morning: {simulation_stuck_on_morning}")
    
    print("\nDIAGNOSIS:")
    
    if not has_conversations:
        print("❌ ROOT CAUSE: NO CONVERSATION DATA")
        print("   The user has no conversations in the database")
        print("   Frontend correctly shows 'Day 1, Morning' as default")
        print("   SOLUTION: User needs to generate conversations to see time progression")
        return "no_conversations"
    
    elif backend_time_stuck and simulation_stuck_on_morning:
        print("❌ ROOT CAUSE: BACKEND DATA ISSUE")
        print("   Both conversation data and simulation state are stuck on morning")
        print("   The time progression system is not working in the backend")
        print("   SOLUTION: Fix the backend time advancement logic")
        return "backend_issue"
    
    elif has_time_progression and not simulation_stuck_on_morning:
        print("✅ ROOT CAUSE: LIKELY FRONTEND DISPLAY ISSUE")
        print("   Backend data shows proper time progression")
        print("   Simulation state shows advanced time")
        print("   But frontend still displays 'Day 1, Morning'")
        print("   SOLUTION: Check frontend code that displays time period")
        return "frontend_issue"
    
    elif has_time_progression and simulation_stuck_on_morning:
        print("⚠️ ROOT CAUSE: MIXED ISSUE")
        print("   Conversation data shows time progression")
        print("   But simulation state is stuck on morning")
        print("   SOLUTION: Check simulation state update logic")
        return "mixed_issue"
    
    else:
        print("⚠️ ROOT CAUSE: UNCLEAR")
        print("   Data patterns don't match expected scenarios")
        print("   SOLUTION: Manual investigation required")
        return "unclear"

def main():
    """Main diagnostic function"""
    print("="*80)
    print("TIME PROGRESSION DIAGNOSTIC TEST")
    print("Investigating: Time display stuck on 'Day 1, Morning'")
    print("="*80)
    
    # Step 1: Login as guest
    if not login_as_guest():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Step 2: Get all conversations
    conversations = get_all_conversations()
    if conversations is None:
        print("❌ Cannot analyze time progression without conversation data")
        return False
    
    # Step 3: Analyze conversation metadata
    time_progression_working = analyze_conversation_metadata(conversations)
    
    # Step 4: Get simulation state
    simulation_state = verify_time_progression_system()
    
    # Step 5: Diagnose the issue
    diagnosis = diagnose_frontend_vs_backend_issue(conversations, simulation_state)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL DIAGNOSTIC SUMMARY")
    print("="*80)
    
    print(f"Conversations found: {len(conversations) if conversations else 0}")
    print(f"Time progression working: {time_progression_working}")
    print(f"Diagnosis: {diagnosis}")
    
    if diagnosis == "backend_issue":
        print("\n❌ BACKEND ISSUE CONFIRMED")
        print("The time progression system has backend problems that need fixing")
        return False
    elif diagnosis == "frontend_issue":
        print("\n✅ BACKEND IS WORKING")
        print("The issue is in frontend display - backend data is correct")
        return True
    elif diagnosis == "no_conversations":
        print("\n⚠️ NO DATA TO PROGRESS")
        print("User needs to generate conversations to see time progression")
        return True
    else:
        print(f"\n⚠️ DIAGNOSIS: {diagnosis.upper()}")
        print("Further investigation needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)