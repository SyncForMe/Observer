#!/usr/bin/env python3
"""
Critical Conversation Pause/Play Persistence Test
Testing the user-reported issue: Generated 27 messages, clicked pause, then play - ALL MESSAGES DELETED
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

# Global auth token
auth_token = None

def login():
    """Login to get auth token"""
    global auth_token
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            print(f"✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def make_request(method, endpoint, data=None):
    """Make authenticated request"""
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except Exception as e:
        return None, str(e)

def test_conversation_persistence():
    """Test the critical conversation pause/play persistence issue"""
    print("\n" + "="*80)
    print("CRITICAL CONVERSATION PAUSE/PLAY PERSISTENCE TEST")
    print("User Issue: Generated 27 messages, clicked pause, then play - ALL MESSAGES DELETED")
    print("="*80)
    
    # Step 1: Login
    print("\nStep 1: Authenticating...")
    if not login():
        print("❌ Cannot proceed without authentication")
        return False
    
    # Step 2: Get initial conversation state
    print("\nStep 2: Getting initial conversation state...")
    response, error = make_request("GET", "/conversations")
    if error:
        print(f"❌ Failed to get conversations: {error}")
        return False
    
    if response.status_code != 200:
        print(f"❌ Failed to get conversations: {response.status_code}")
        return False
    
    initial_conversations = response.json()
    initial_count = len(initial_conversations)
    initial_messages = sum(len(conv.get('messages', [])) for conv in initial_conversations)
    
    print(f"Initial state: {initial_count} conversations, {initial_messages} messages")
    
    # Step 3: Start simulation if not active
    print("\nStep 3: Ensuring simulation is active...")
    response, error = make_request("GET", "/simulation/state")
    if response and response.status_code == 200:
        state = response.json()
        is_active = state.get('is_active', False)
        
        if not is_active:
            print("Starting simulation...")
            response, error = make_request("POST", "/simulation/start")
            if not response or response.status_code != 200:
                print(f"❌ Failed to start simulation")
                return False
            print("✅ Simulation started")
        else:
            print("✅ Simulation already active")
    
    # Step 4: Generate some conversations to simulate user's scenario
    print("\nStep 4: Generating conversations to simulate user's scenario...")
    
    # Generate 3-5 conversations to get some messages
    for i in range(3):
        print(f"Generating conversation {i+1}...")
        response, error = make_request("POST", "/conversation/generate")
        if response and response.status_code == 200:
            print(f"✅ Generated conversation {i+1}")
            time.sleep(2)  # Small delay between generations
        else:
            print(f"⚠️ Failed to generate conversation {i+1}")
    
    # Step 5: Get conversation state before pause
    print("\nStep 5: Getting conversation state before pause...")
    response, error = make_request("GET", "/conversations")
    if error or response.status_code != 200:
        print(f"❌ Failed to get conversations before pause")
        return False
    
    before_pause_conversations = response.json()
    before_pause_count = len(before_pause_conversations)
    before_pause_messages = sum(len(conv.get('messages', [])) for conv in before_pause_conversations)
    
    print(f"Before pause: {before_pause_count} conversations, {before_pause_messages} messages")
    
    # Create detailed snapshot
    conversation_ids_before = [conv.get('id') for conv in before_pause_conversations]
    message_details_before = []
    
    for conv in before_pause_conversations:
        for msg in conv.get('messages', []):
            message_details_before.append({
                "conversation_id": conv.get('id'),
                "agent_name": msg.get('agent_name'),
                "message_preview": msg.get('message', '')[:50] + "...",
                "timestamp": msg.get('timestamp')
            })
    
    print(f"Detailed snapshot: {len(message_details_before)} individual messages recorded")
    
    # Step 6: PAUSE simulation (critical test point)
    print("\nStep 6: PAUSING simulation...")
    response, error = make_request("POST", "/simulation/pause")
    if error or response.status_code != 200:
        print(f"❌ Failed to pause simulation: {error or response.status_code}")
        return False
    
    print("✅ Simulation paused successfully")
    
    # Step 7: Verify conversations still exist after pause
    print("\nStep 7: Verifying conversations exist after pause...")
    response, error = make_request("GET", "/conversations")
    if error or response.status_code != 200:
        print(f"❌ Failed to get conversations after pause")
        return False
    
    after_pause_conversations = response.json()
    after_pause_count = len(after_pause_conversations)
    after_pause_messages = sum(len(conv.get('messages', [])) for conv in after_pause_conversations)
    
    print(f"After pause: {after_pause_count} conversations, {after_pause_messages} messages")
    
    # Check for data loss after pause
    pause_data_loss = False
    if after_pause_count < before_pause_count:
        print(f"❌ CONVERSATION DATA LOSS AFTER PAUSE: {before_pause_count - after_pause_count} conversations lost")
        pause_data_loss = True
    
    if after_pause_messages < before_pause_messages:
        print(f"❌ MESSAGE DATA LOSS AFTER PAUSE: {before_pause_messages - after_pause_messages} messages lost")
        pause_data_loss = True
    
    if not pause_data_loss:
        print("✅ No data loss detected after pause")
    
    # Step 8: RESUME simulation (this is where user reports ALL MESSAGES DELETED)
    print("\nStep 8: RESUMING simulation - CRITICAL TEST POINT")
    response, error = make_request("POST", "/simulation/resume")
    if error or response.status_code != 200:
        print(f"❌ Failed to resume simulation: {error or response.status_code}")
        return False
    
    print("✅ Simulation resumed successfully")
    
    # Step 9: CRITICAL CHECK - Verify conversations after resume
    print("\nStep 9: CRITICAL CHECK - Verifying conversations after resume...")
    response, error = make_request("GET", "/conversations")
    if error or response.status_code != 200:
        print(f"❌ Failed to get conversations after resume")
        return False
    
    after_resume_conversations = response.json()
    after_resume_count = len(after_resume_conversations)
    after_resume_messages = sum(len(conv.get('messages', [])) for conv in after_resume_conversations)
    
    print(f"After resume: {after_resume_count} conversations, {after_resume_messages} messages")
    
    # CRITICAL DATA LOSS CHECK
    resume_data_loss = False
    critical_issues = []
    
    if after_resume_count < before_pause_count:
        conversations_lost = before_pause_count - after_resume_count
        print(f"🚨 CRITICAL DATA LOSS: {conversations_lost} conversations DELETED after resume")
        critical_issues.append(f"{conversations_lost} conversations deleted")
        resume_data_loss = True
    
    if after_resume_messages < before_pause_messages:
        messages_lost = before_pause_messages - after_resume_messages
        print(f"🚨 CRITICAL DATA LOSS: {messages_lost} messages DELETED after resume")
        critical_issues.append(f"{messages_lost} messages deleted")
        resume_data_loss = True
    
    # Check if ALL messages were deleted (user's specific issue)
    if after_resume_messages == 0 and before_pause_messages > 0:
        print("🚨 CONFIRMED USER ISSUE: ALL MESSAGES DELETED after pause/resume cycle")
        critical_issues.append("ALL messages deleted (user's reported issue)")
        resume_data_loss = True
    
    if not resume_data_loss:
        print("✅ No data loss detected after resume")
    
    # Step 10: Test for message counter inconsistencies
    print("\nStep 10: Testing for message counter inconsistencies...")
    
    # Make multiple rapid requests to check for inconsistent counts
    message_counts = []
    conversation_counts = []
    
    for i in range(5):
        response, error = make_request("GET", "/conversations")
        if response and response.status_code == 200:
            conversations = response.json()
            conv_count = len(conversations)
            msg_count = sum(len(conv.get('messages', [])) for conv in conversations)
            
            conversation_counts.append(conv_count)
            message_counts.append(msg_count)
            
            print(f"Check {i+1}: {conv_count} conversations, {msg_count} messages")
            time.sleep(0.5)
    
    # Analyze consistency
    unique_conv_counts = set(conversation_counts)
    unique_msg_counts = set(message_counts)
    
    inconsistent_counts = False
    if len(unique_conv_counts) > 1:
        print(f"⚠️ INCONSISTENT CONVERSATION COUNTS: {list(unique_conv_counts)}")
        print("This could explain the UI glitch where counters jump between values")
        inconsistent_counts = True
    else:
        print("✅ Conversation counts are consistent across requests")
    
    if len(unique_msg_counts) > 1:
        print(f"⚠️ INCONSISTENT MESSAGE COUNTS: {list(unique_msg_counts)}")
        print("This could explain the UI glitch where message counts jump")
        inconsistent_counts = True
    else:
        print("✅ Message counts are consistent across requests")
    
    # Step 11: Final diagnosis
    print("\nStep 11: FINAL DIAGNOSIS")
    print("="*60)
    
    issues_found = []
    
    if pause_data_loss:
        issues_found.append("Data loss detected after pause operation")
    
    if resume_data_loss:
        issues_found.append("CRITICAL: Data loss detected after resume operation")
        if "ALL messages deleted" in str(critical_issues):
            issues_found.append("CONFIRMED: User's reported issue - ALL messages deleted after pause/resume")
    
    if inconsistent_counts:
        issues_found.append("Inconsistent message/conversation counts (explains UI glitches)")
    
    if issues_found:
        print("🚨 CRITICAL ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"{i}. {issue}")
        
        print("\nROOT CAUSE ANALYSIS:")
        if resume_data_loss:
            print("- The pause/resume functionality has a critical bug that deletes conversation data")
            print("- This confirms the user's report of losing messages after pause/play cycle")
        
        if inconsistent_counts:
            print("- Message counts are inconsistent, explaining the UI glitch of counters jumping")
            print("- This suggests database queries are returning different results")
        
        print("\nRECOMMENDATIONS:")
        print("1. Fix the pause/resume endpoints to preserve conversation data")
        print("2. Add data integrity checks before and after pause/resume operations")
        print("3. Implement proper transaction handling for conversation state changes")
        print("4. Add logging to track conversation data changes during pause/resume")
        
        return False
    else:
        print("✅ NO CRITICAL ISSUES FOUND")
        print("- Pause/resume functionality preserves all conversation data")
        print("- Message counts are consistent across requests")
        print("- No data loss detected in pause/resume cycle")
        
        return True

if __name__ == "__main__":
    print("Starting Critical Conversation Pause/Play Persistence Test...")
    success = test_conversation_persistence()
    
    if success:
        print("\n🎉 TEST PASSED: Conversation pause/play persistence is working correctly")
    else:
        print("\n❌ TEST FAILED: Critical issues found in conversation pause/play persistence")
    
    print("\nTest completed.")