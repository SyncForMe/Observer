#!/usr/bin/env python3
"""
Time Progression Investigation Test

This test investigates the specific issue reported by the user:
"The frontend is still stuck at 'Day 1, Morning' despite having more than 9 messages"

The test will:
1. Log in as guest user
2. Check current simulation state with GET /api/simulation/state
3. Get all conversations with GET /api/conversations and count messages
4. Check if time advancement logic should have triggered
5. Identify why time progression is stuck
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔍 TIME PROGRESSION INVESTIGATION")
print(f"Using API URL: {API_URL}")
print("="*80)

def make_request(method, endpoint, data=None, headers=None, params=None):
    """Make HTTP request with error handling"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"{method} {endpoint} -> Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"❌ Error response: {response.text}")
            return None, response.status_code
        
        try:
            return response.json(), response.status_code
        except json.JSONDecodeError:
            return response.text, response.status_code
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None, 500

def investigate_time_progression():
    """Main investigation function"""
    
    # Step 1: Log in as guest user
    print("\n🔐 STEP 1: Logging in as guest user")
    print("-" * 50)
    
    guest_response, status = make_request("POST", "/auth/test-login")
    if not guest_response or status != 200:
        print("❌ Failed to log in as guest user")
        return False
    
    auth_token = guest_response.get("access_token")
    user_data = guest_response.get("user", {})
    user_id = user_data.get("id")
    
    print(f"✅ Guest login successful")
    print(f"   User ID: {user_id}")
    print(f"   Token: {auth_token[:20]}...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 2: Check current simulation state
    print("\n📊 STEP 2: Checking current simulation state")
    print("-" * 50)
    
    sim_state, status = make_request("GET", "/simulation/state", headers=headers)
    if not sim_state or status != 200:
        print("❌ Failed to get simulation state")
        return False
    
    current_day = sim_state.get("current_day", "Unknown")
    current_time_period = sim_state.get("current_time_period", "Unknown")
    is_active = sim_state.get("is_active", False)
    
    print(f"✅ Simulation state retrieved:")
    print(f"   Current Day: {current_day}")
    print(f"   Current Time Period: {current_time_period}")
    print(f"   Is Active: {is_active}")
    print(f"   Full State: {json.dumps(sim_state, indent=2)}")
    
    # Step 3: Get all conversations and analyze
    print("\n💬 STEP 3: Getting all conversations and analyzing messages")
    print("-" * 50)
    
    conversations, status = make_request("GET", "/conversations", headers=headers)
    if not conversations or status != 200:
        print("❌ Failed to get conversations")
        return False
    
    total_conversations = len(conversations)
    total_messages = 0
    conversation_details = []
    time_periods = defaultdict(int)
    
    print(f"✅ Found {total_conversations} conversations")
    
    for i, conv in enumerate(conversations, 1):
        conv_id = conv.get("id", "Unknown")
        round_number = conv.get("round_number", "Unknown")
        time_period = conv.get("time_period", "Unknown")
        scenario = conv.get("scenario", "Unknown")
        messages = conv.get("messages", [])
        message_count = len(messages)
        created_at = conv.get("created_at", "Unknown")
        
        total_messages += message_count
        time_periods[time_period] += 1
        
        conversation_details.append({
            "index": i,
            "id": conv_id,
            "round_number": round_number,
            "time_period": time_period,
            "message_count": message_count,
            "scenario": scenario[:50] + "..." if len(scenario) > 50 else scenario,
            "created_at": created_at
        })
        
        print(f"   Conversation {i}:")
        print(f"     Round: {round_number}")
        print(f"     Time Period: {time_period}")
        print(f"     Messages: {message_count}")
        print(f"     Created: {created_at}")
        print(f"     Scenario: {scenario[:50]}{'...' if len(scenario) > 50 else ''}")
    
    print(f"\n📈 CONVERSATION SUMMARY:")
    print(f"   Total Conversations: {total_conversations}")
    print(f"   Total Messages: {total_messages}")
    print(f"   Time Periods Distribution:")
    for period, count in sorted(time_periods.items()):
        print(f"     {period}: {count} conversations")
    
    # Step 4: Analyze time advancement logic
    print("\n⏰ STEP 4: Analyzing time advancement logic")
    print("-" * 50)
    
    # Based on the backend code, time should advance every 3 conversations
    # Let's check if the logic should have triggered
    
    expected_advancements = total_conversations // 3
    print(f"   Conversations per time advancement: 3")
    print(f"   Total conversations: {total_conversations}")
    print(f"   Expected time advancements: {expected_advancements}")
    
    # Determine what the current time should be
    time_progression = ["morning", "afternoon", "evening"]
    
    if expected_advancements == 0:
        expected_time_period = "morning"
        expected_day = 1
    else:
        # Calculate expected day and time period
        total_periods_passed = expected_advancements
        expected_day = 1 + (total_periods_passed // 3)
        period_index = total_periods_passed % 3
        expected_time_period = time_progression[period_index]
    
    print(f"   Expected Day: {expected_day}")
    print(f"   Expected Time Period: {expected_time_period}")
    print(f"   Actual Day: {current_day}")
    print(f"   Actual Time Period: {current_time_period}")
    
    # Check if there's a mismatch
    time_progression_working = (
        str(current_day) == str(expected_day) and 
        current_time_period == expected_time_period
    )
    
    if time_progression_working:
        print(f"✅ Time progression is working correctly!")
    else:
        print(f"❌ Time progression is NOT working correctly!")
        print(f"   Expected: Day {expected_day}, {expected_time_period}")
        print(f"   Actual: Day {current_day}, {current_time_period}")
    
    # Step 5: Check for specific issues
    print("\n🔍 STEP 5: Investigating specific issues")
    print("-" * 50)
    
    issues_found = []
    
    # Issue 1: Check if conversations have proper time_period metadata
    conversations_with_time_periods = [c for c in conversations if c.get("time_period")]
    if len(conversations_with_time_periods) != total_conversations:
        missing_time_periods = total_conversations - len(conversations_with_time_periods)
        issues_found.append(f"{missing_time_periods} conversations missing time_period metadata")
        print(f"⚠️  {missing_time_periods} conversations are missing time_period metadata")
    
    # Issue 2: Check if time periods are progressing in conversations
    if conversations:
        # Sort conversations by creation time
        sorted_conversations = sorted(conversations, key=lambda x: x.get("created_at", ""))
        
        print(f"   Time period progression in conversations:")
        for i, conv in enumerate(sorted_conversations):
            time_period = conv.get("time_period", "Unknown")
            round_num = conv.get("round_number", "Unknown")
            print(f"     Conv {i+1} (Round {round_num}): {time_period}")
        
        # Check if time periods are advancing
        unique_time_periods = list(set(conv.get("time_period", "") for conv in conversations))
        if len(unique_time_periods) == 1 and total_conversations > 3:
            issues_found.append("All conversations have the same time_period despite having >3 conversations")
            print(f"⚠️  All conversations have the same time_period: {unique_time_periods[0]}")
    
    # Issue 3: Check if simulation state is being updated
    if total_conversations > 3 and current_time_period == "morning":
        issues_found.append("Simulation state not updating despite having >3 conversations")
        print(f"⚠️  Simulation state shows 'morning' despite having {total_conversations} conversations")
    
    # Issue 4: Check for user-specific data isolation
    print(f"   Checking data isolation for user: {user_id}")
    
    # Step 6: Test time advancement manually if needed
    print("\n🧪 STEP 6: Testing manual time advancement (if needed)")
    print("-" * 50)
    
    if not time_progression_working and total_conversations >= 3:
        print("   Attempting to trigger time advancement manually...")
        
        # Try to generate a new conversation to trigger time advancement
        conv_gen_response, status = make_request(
            "POST", 
            "/conversation/generate",
            headers=headers
        )
        
        if conv_gen_response and status == 200:
            print("✅ Generated new conversation successfully")
            
            # Check simulation state again
            new_sim_state, status = make_request("GET", "/simulation/state", headers=headers)
            if new_sim_state and status == 200:
                new_day = new_sim_state.get("current_day")
                new_time_period = new_sim_state.get("current_time_period")
                
                print(f"   New simulation state:")
                print(f"     Day: {current_day} -> {new_day}")
                print(f"     Time Period: {current_time_period} -> {new_time_period}")
                
                if new_day != current_day or new_time_period != current_time_period:
                    print("✅ Time advancement triggered after conversation generation!")
                else:
                    print("❌ Time advancement still not working after conversation generation")
                    issues_found.append("Time advancement not triggered even after new conversation")
        else:
            print("❌ Failed to generate new conversation")
            issues_found.append("Cannot generate new conversation to test time advancement")
    
    # Step 7: Final diagnosis
    print("\n🏥 STEP 7: Final diagnosis")
    print("-" * 50)
    
    if not issues_found:
        print("✅ No issues found - time progression system is working correctly!")
        diagnosis = "WORKING"
    else:
        print("❌ Issues found with time progression system:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        diagnosis = "BROKEN"
    
    # Summary for main agent
    print("\n📋 SUMMARY FOR MAIN AGENT")
    print("=" * 80)
    print(f"USER ISSUE: Frontend stuck at 'Day 1, Morning' despite having >9 messages")
    print(f"INVESTIGATION RESULTS:")
    print(f"  - Total Conversations: {total_conversations}")
    print(f"  - Total Messages: {total_messages}")
    print(f"  - Current Simulation State: Day {current_day}, {current_time_period}")
    print(f"  - Expected State: Day {expected_day}, {expected_time_period}")
    print(f"  - Time Progression Status: {diagnosis}")
    
    if issues_found:
        print(f"  - Issues Found: {len(issues_found)}")
        for issue in issues_found:
            print(f"    • {issue}")
    
    print(f"  - Recommendation: {'Fix time advancement logic' if diagnosis == 'BROKEN' else 'System working correctly'}")
    
    return diagnosis == "WORKING"

if __name__ == "__main__":
    try:
        success = investigate_time_progression()
        if success:
            print("\n✅ Time progression investigation completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Time progression investigation found issues")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Investigation failed with error: {e}")
        sys.exit(1)