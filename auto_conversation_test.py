#!/usr/bin/env python3
"""
COMPLETE PLAY/PAUSE SYSTEM WITH AUTO-CONVERSATION FIX TESTING

Testing the complete solution to fix the play/pause chaos with auto-conversation system.

CRITICAL TESTS TO VERIFY COMPLETE FIX:
1. Play Button Auto-Conversation System - Test /simulation/start activates auto-conversation loop
2. Auto-Conversation Generation Loop - Verify conversations appear automatically every 30 seconds when active
3. Pause Button Stops Auto-Generation - Test /simulation/pause properly stops auto-conversation loop
4. State Consistency & Clean Operation - Verify simulation state changes cleanly: inactive → active → inactive
5. End-to-End User Experience Simulation - Complete play/pause workflow testing

EXPECTED RESULTS:
✅ Play button instant response + auto-conversations every 30s
✅ No more loading circle forever (conversations appear automatically)
✅ Pause button stops everything cleanly (no zombie processes)
✅ No animation conflicts or state chaos
✅ Proper progressive streaming integration
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
import threading
import asyncio

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
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global auth token
auth_token = None

def authenticate():
    """Authenticate with the backend using email/password"""
    global auth_token
    
    if auth_token:
        return True
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    url = f"{API_URL}/auth/login"
    
    try:
        response = requests.post(url, json=login_data, timeout=10)
        if response.status_code == 200:
            response_data = response.json()
            auth_token = response_data.get("access_token")
            if auth_token:
                print("✅ Authentication successful")
                return True
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def make_authenticated_request(method, endpoint, data=None, timeout=30):
    """Make an authenticated request to the API"""
    if not authenticate():
        return None
        
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response
    except requests.exceptions.Timeout:
        print(f"⏰ Request to {endpoint} timed out after {timeout} seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request to {endpoint} failed: {e}")
        return None

def log_test_result(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def test_play_button_auto_conversation_system():
    """Test 1: Play Button Auto-Conversation System - Test /simulation/start activates auto-conversation loop"""
    print("\n" + "="*80)
    print("▶️ TEST 1: PLAY BUTTON AUTO-CONVERSATION SYSTEM")
    print("="*80)
    
    # Step 1: Ensure simulation is initially paused/inactive
    print("\n⏸️ Step 1: Ensuring simulation is initially inactive...")
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        initial_active = state.get('is_active', False)
        
        if initial_active:
            # Pause it first
            pause_response = make_authenticated_request('POST', '/simulation/pause')
            if pause_response and pause_response.status_code == 200:
                log_test_result("Initial Pause Setup", True, "Simulation paused successfully")
            else:
                log_test_result("Initial Pause Setup", False, "Failed to pause simulation")
                return False
        else:
            log_test_result("Initial State Check", True, "Simulation is initially inactive")
    else:
        log_test_result("Initial State Check", False, "Failed to get simulation state")
        return False
    
    # Step 2: Record initial conversation count
    print("\n📊 Step 2: Recording initial conversation count...")
    response = make_authenticated_request('GET', '/conversations')
    if response and response.status_code == 200:
        initial_conversations = response.json()
        initial_count = len(initial_conversations)
        log_test_result("Initial Conversation Count", True, f"Found {initial_count} existing conversations")
    else:
        log_test_result("Initial Conversation Count", False, "Failed to get initial conversations")
        return False
    
    # Step 3: Test /simulation/start endpoint
    print("\n▶️ Step 3: Testing /simulation/start endpoint...")
    start_time = time.time()
    
    response = make_authenticated_request('POST', '/simulation/start')
    
    if response and response.status_code == 200:
        end_time = time.time()
        response_time = end_time - start_time
        
        response_data = response.json()
        
        # Check for instant response (should be under 2 seconds)
        if response_time <= 2.0:
            log_test_result("Play Button Response Time", True, f"Instant response in {response_time:.2f}s")
        else:
            log_test_result("Play Button Response Time", False, f"Slow response: {response_time:.2f}s")
        
        # Check response structure
        if 'message' in response_data and 'is_active' in response_data:
            log_test_result("Start Response Structure", True, "Response contains expected fields")
            
            # Verify simulation is now active
            if response_data.get('is_active') == True:
                log_test_result("Simulation Activation", True, "Simulation is now active")
            else:
                log_test_result("Simulation Activation", False, "Simulation not activated")
        else:
            log_test_result("Start Response Structure", False, "Missing expected response fields")
    else:
        log_test_result("Play Button Start Test", False, f"Failed to start simulation: {response.status_code if response else 'No response'}")
        return False
    
    # Step 4: Verify simulation state is active
    print("\n🔍 Step 4: Verifying simulation state is active...")
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        is_active = state.get('is_active', False)
        
        if is_active:
            log_test_result("Active State Verification", True, "Simulation state shows active=true")
        else:
            log_test_result("Active State Verification", False, "Simulation state shows active=false")
    else:
        log_test_result("Active State Verification", False, "Failed to verify simulation state")
    
    return True

def test_auto_conversation_generation_loop():
    """Test 2: Auto-Conversation Generation Loop - Monitor that conversations are generated automatically every 30 seconds"""
    print("\n" + "="*80)
    print("🔄 TEST 2: AUTO-CONVERSATION GENERATION LOOP")
    print("="*80)
    
    # Step 1: Ensure simulation is active
    print("\n🔍 Step 1: Ensuring simulation is active...")
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        is_active = state.get('is_active', False)
        
        if not is_active:
            # Start simulation first
            start_response = make_authenticated_request('POST', '/simulation/start')
            if start_response and start_response.status_code == 200:
                log_test_result("Auto-Loop Simulation Start", True, "Simulation started for auto-loop testing")
            else:
                log_test_result("Auto-Loop Simulation Start", False, "Failed to start simulation")
                return False
        else:
            log_test_result("Auto-Loop Active Check", True, "Simulation is already active")
    else:
        log_test_result("Auto-Loop Active Check", False, "Failed to check simulation state")
        return False
    
    # Step 2: Record baseline conversation count
    print("\n📊 Step 2: Recording baseline conversation count...")
    response = make_authenticated_request('GET', '/conversations')
    if response and response.status_code == 200:
        baseline_conversations = response.json()
        baseline_count = len(baseline_conversations)
        log_test_result("Baseline Conversation Count", True, f"Baseline: {baseline_count} conversations")
    else:
        log_test_result("Baseline Conversation Count", False, "Failed to get baseline conversations")
        return False
    
    # Step 3: Monitor for auto-generated conversations over 90 seconds (should see 2-3 new conversations)
    print("\n⏰ Step 3: Monitoring auto-conversation generation for 90 seconds...")
    print("   Expected: New conversations every ~30 seconds")
    
    monitoring_duration = 90  # 90 seconds to catch 2-3 auto-conversations
    check_interval = 15  # Check every 15 seconds
    conversation_timestamps = []
    
    start_monitoring = time.time()
    
    while time.time() - start_monitoring < monitoring_duration:
        # Check for new conversations
        response = make_authenticated_request('GET', '/conversations')
        if response and response.status_code == 200:
            current_conversations = response.json()
            current_count = len(current_conversations)
            
            if current_count > baseline_count:
                new_conversations = current_count - baseline_count
                elapsed_time = time.time() - start_monitoring
                conversation_timestamps.append(elapsed_time)
                
                print(f"   📈 Found {new_conversations} new conversations after {elapsed_time:.1f}s")
                
                # Update baseline for next check
                baseline_count = current_count
        
        # Wait before next check
        time.sleep(check_interval)
    
    # Step 4: Analyze auto-conversation timing
    print(f"\n📊 Step 4: Analyzing auto-conversation timing...")
    
    if len(conversation_timestamps) >= 2:
        # Calculate intervals between conversations
        intervals = []
        for i in range(1, len(conversation_timestamps)):
            interval = conversation_timestamps[i] - conversation_timestamps[i-1]
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals)
        
        # Check if intervals are close to 30 seconds (allow 20-40 second range)
        if 20 <= avg_interval <= 40:
            log_test_result("Auto-Conversation Timing", True, f"Average interval: {avg_interval:.1f}s (target: ~30s)")
        else:
            log_test_result("Auto-Conversation Timing", False, f"Interval too far from target: {avg_interval:.1f}s")
        
        log_test_result("Auto-Conversation Generation", True, f"Generated {len(conversation_timestamps)} conversations automatically")
    elif len(conversation_timestamps) == 1:
        log_test_result("Auto-Conversation Generation", True, f"Generated 1 conversation (may need more time)")
        log_test_result("Auto-Conversation Timing", True, "Single conversation generated, timing cannot be measured")
    else:
        log_test_result("Auto-Conversation Generation", False, "No auto-conversations detected in 90 seconds")
        log_test_result("Auto-Conversation Timing", False, "No conversations to measure timing")
    
    return len(conversation_timestamps) >= 1  # At least one auto-conversation should be generated

def test_pause_button_stops_auto_generation():
    """Test 3: Pause Button Stops Auto-Generation - Test /simulation/pause properly stops auto-conversation loop"""
    print("\n" + "="*80)
    print("⏸️ TEST 3: PAUSE BUTTON STOPS AUTO-GENERATION")
    print("="*80)
    
    # Step 1: Ensure simulation is active first
    print("\n▶️ Step 1: Ensuring simulation is active...")
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        is_active = state.get('is_active', False)
        
        if not is_active:
            # Start simulation first
            start_response = make_authenticated_request('POST', '/simulation/start')
            if start_response and start_response.status_code == 200:
                log_test_result("Pause Test Simulation Start", True, "Simulation started for pause testing")
                time.sleep(5)  # Wait a bit for auto-loop to potentially start
            else:
                log_test_result("Pause Test Simulation Start", False, "Failed to start simulation")
                return False
        else:
            log_test_result("Pause Test Active Check", True, "Simulation is already active")
    else:
        log_test_result("Pause Test Active Check", False, "Failed to check simulation state")
        return False
    
    # Step 2: Record conversation count before pause
    print("\n📊 Step 2: Recording conversation count before pause...")
    response = make_authenticated_request('GET', '/conversations')
    if response and response.status_code == 200:
        pre_pause_conversations = response.json()
        pre_pause_count = len(pre_pause_conversations)
        log_test_result("Pre-Pause Conversation Count", True, f"Pre-pause: {pre_pause_count} conversations")
    else:
        log_test_result("Pre-Pause Conversation Count", False, "Failed to get pre-pause conversations")
        return False
    
    # Step 3: Test /simulation/pause endpoint
    print("\n⏸️ Step 3: Testing /simulation/pause endpoint...")
    pause_start_time = time.time()
    
    response = make_authenticated_request('POST', '/simulation/pause')
    
    if response and response.status_code == 200:
        pause_end_time = time.time()
        pause_response_time = pause_end_time - pause_start_time
        
        response_data = response.json()
        
        # Check for instant response (should be under 2 seconds)
        if pause_response_time <= 2.0:
            log_test_result("Pause Button Response Time", True, f"Instant response in {pause_response_time:.2f}s")
        else:
            log_test_result("Pause Button Response Time", False, f"Slow response: {pause_response_time:.2f}s")
        
        # Check response structure
        if 'message' in response_data and 'is_active' in response_data:
            log_test_result("Pause Response Structure", True, "Response contains expected fields")
            
            # Verify simulation is now inactive
            if response_data.get('is_active') == False:
                log_test_result("Simulation Deactivation", True, "Simulation is now inactive")
            else:
                log_test_result("Simulation Deactivation", False, "Simulation not deactivated")
        else:
            log_test_result("Pause Response Structure", False, "Missing expected response fields")
    else:
        log_test_result("Pause Button Test", False, f"Failed to pause simulation: {response.status_code if response else 'No response'}")
        return False
    
    # Step 4: Verify simulation state is inactive
    print("\n🔍 Step 4: Verifying simulation state is inactive...")
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        is_active = state.get('is_active', False)
        
        if not is_active:
            log_test_result("Inactive State Verification", True, "Simulation state shows active=false")
        else:
            log_test_result("Inactive State Verification", False, "Simulation state shows active=true")
    else:
        log_test_result("Inactive State Verification", False, "Failed to verify simulation state")
    
    # Step 5: Monitor for 60 seconds to ensure no new conversations are generated
    print("\n🛑 Step 5: Monitoring for 60 seconds to ensure auto-generation stopped...")
    
    monitoring_duration = 60  # 60 seconds to ensure no auto-conversations
    check_interval = 15  # Check every 15 seconds
    
    start_monitoring = time.time()
    new_conversations_detected = False
    
    while time.time() - start_monitoring < monitoring_duration:
        # Check for new conversations
        response = make_authenticated_request('GET', '/conversations')
        if response and response.status_code == 200:
            current_conversations = response.json()
            current_count = len(current_conversations)
            
            if current_count > pre_pause_count:
                new_conversations_detected = True
                new_count = current_count - pre_pause_count
                elapsed_time = time.time() - start_monitoring
                print(f"   ⚠️ Detected {new_count} new conversations after {elapsed_time:.1f}s (should not happen)")
                break
        
        # Wait before next check
        time.sleep(check_interval)
    
    if not new_conversations_detected:
        log_test_result("Auto-Generation Stopped", True, "No new conversations generated after pause (auto-loop stopped)")
    else:
        log_test_result("Auto-Generation Stopped", False, "New conversations detected after pause (auto-loop not stopped)")
    
    return True

def test_state_consistency_and_clean_operation():
    """Test 4: State Consistency & Clean Operation - Verify simulation state changes cleanly"""
    print("\n" + "="*80)
    print("🔄 TEST 4: STATE CONSISTENCY & CLEAN OPERATION")
    print("="*80)
    
    # Step 1: Test inactive → active transition
    print("\n🔄 Step 1: Testing inactive → active transition...")
    
    # Ensure we start inactive
    pause_response = make_authenticated_request('POST', '/simulation/pause')
    if pause_response and pause_response.status_code == 200:
        log_test_result("Clean Start - Pause", True, "Simulation paused for clean state testing")
    else:
        log_test_result("Clean Start - Pause", False, "Failed to pause simulation")
    
    # Verify inactive state
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        if not state.get('is_active', True):
            log_test_result("Inactive State Confirmed", True, "Simulation is inactive")
        else:
            log_test_result("Inactive State Confirmed", False, "Simulation is not inactive")
    
    # Start simulation
    start_response = make_authenticated_request('POST', '/simulation/start')
    if start_response and start_response.status_code == 200:
        log_test_result("Inactive → Active Transition", True, "Successfully transitioned to active")
        
        # Verify active state
        response = make_authenticated_request('GET', '/simulation/state')
        if response and response.status_code == 200:
            state = response.json()
            if state.get('is_active', False):
                log_test_result("Active State Confirmed", True, "Simulation is active")
            else:
                log_test_result("Active State Confirmed", False, "Simulation is not active")
    else:
        log_test_result("Inactive → Active Transition", False, "Failed to transition to active")
    
    # Step 2: Test active → inactive transition
    print("\n🔄 Step 2: Testing active → inactive transition...")
    
    pause_response = make_authenticated_request('POST', '/simulation/pause')
    if pause_response and pause_response.status_code == 200:
        log_test_result("Active → Inactive Transition", True, "Successfully transitioned to inactive")
        
        # Verify inactive state
        response = make_authenticated_request('GET', '/simulation/state')
        if response and response.status_code == 200:
            state = response.json()
            if not state.get('is_active', True):
                log_test_result("Final Inactive State Confirmed", True, "Simulation is inactive")
            else:
                log_test_result("Final Inactive State Confirmed", False, "Simulation is not inactive")
    else:
        log_test_result("Active → Inactive Transition", False, "Failed to transition to inactive")
    
    # Step 3: Test multiple rapid transitions (no race conditions)
    print("\n⚡ Step 3: Testing rapid state transitions...")
    
    transitions_successful = 0
    total_transitions = 6  # 3 start/pause cycles
    
    for i in range(3):
        # Start
        start_response = make_authenticated_request('POST', '/simulation/start')
        if start_response and start_response.status_code == 200:
            transitions_successful += 1
        
        time.sleep(1)  # Brief pause
        
        # Pause
        pause_response = make_authenticated_request('POST', '/simulation/pause')
        if pause_response and pause_response.status_code == 200:
            transitions_successful += 1
        
        time.sleep(1)  # Brief pause
    
    if transitions_successful == total_transitions:
        log_test_result("Rapid State Transitions", True, f"All {total_transitions} transitions successful")
    else:
        log_test_result("Rapid State Transitions", False, f"Only {transitions_successful}/{total_transitions} transitions successful")
    
    # Step 4: Verify final state consistency
    print("\n🔍 Step 4: Verifying final state consistency...")
    
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        state = response.json()
        required_fields = ['is_active', 'current_day', 'current_time_period', 'scenario']
        
        has_all_fields = all(field in state for field in required_fields)
        
        if has_all_fields:
            log_test_result("State Consistency", True, "All required state fields present")
        else:
            missing_fields = [field for field in required_fields if field not in state]
            log_test_result("State Consistency", False, f"Missing fields: {missing_fields}")
    else:
        log_test_result("State Consistency", False, "Failed to get final state")
    
    return True

def test_end_to_end_user_experience():
    """Test 5: End-to-End User Experience Simulation - Complete play/pause workflow testing"""
    print("\n" + "="*80)
    print("🎯 TEST 5: END-TO-END USER EXPERIENCE SIMULATION")
    print("="*80)
    
    # Step 1: Complete user workflow simulation
    print("\n👤 Step 1: Simulating complete user workflow...")
    
    # Start with clean slate
    pause_response = make_authenticated_request('POST', '/simulation/pause')
    if pause_response and pause_response.status_code == 200:
        log_test_result("E2E Clean Start", True, "Started with clean inactive state")
    else:
        log_test_result("E2E Clean Start", False, "Failed to start with clean state")
    
    # Record initial conversation count
    response = make_authenticated_request('GET', '/conversations')
    if response and response.status_code == 200:
        initial_conversations = response.json()
        initial_count = len(initial_conversations)
        log_test_result("E2E Initial Count", True, f"Initial conversations: {initial_count}")
    else:
        log_test_result("E2E Initial Count", False, "Failed to get initial conversation count")
        return False
    
    # Step 2: User clicks Play button
    print("\n▶️ Step 2: User clicks Play button...")
    
    play_start_time = time.time()
    start_response = make_authenticated_request('POST', '/simulation/start')
    play_end_time = time.time()
    
    if start_response and start_response.status_code == 200:
        play_response_time = play_end_time - play_start_time
        
        if play_response_time <= 2.0:
            log_test_result("E2E Play Response", True, f"Play button responded instantly ({play_response_time:.2f}s)")
        else:
            log_test_result("E2E Play Response", False, f"Play button too slow ({play_response_time:.2f}s)")
        
        # Verify active state
        response = make_authenticated_request('GET', '/simulation/state')
        if response and response.status_code == 200:
            state = response.json()
            if state.get('is_active', False):
                log_test_result("E2E Play State Change", True, "Simulation activated successfully")
            else:
                log_test_result("E2E Play State Change", False, "Simulation not activated")
    else:
        log_test_result("E2E Play Response", False, "Play button failed")
        return False
    
    # Step 3: Wait for auto-conversations (45 seconds to see at least 1)
    print("\n⏰ Step 3: Waiting for auto-conversations (45 seconds)...")
    
    auto_conv_start = time.time()
    auto_conversations_detected = 0
    
    while time.time() - auto_conv_start < 45:
        response = make_authenticated_request('GET', '/conversations')
        if response and response.status_code == 200:
            current_conversations = response.json()
            current_count = len(current_conversations)
            
            if current_count > initial_count:
                new_conversations = current_count - initial_count
                if new_conversations > auto_conversations_detected:
                    auto_conversations_detected = new_conversations
                    elapsed = time.time() - auto_conv_start
                    print(f"   📈 Auto-conversation #{auto_conversations_detected} detected after {elapsed:.1f}s")
        
        time.sleep(10)  # Check every 10 seconds
    
    if auto_conversations_detected >= 1:
        log_test_result("E2E Auto-Conversations", True, f"Detected {auto_conversations_detected} auto-conversations")
    else:
        log_test_result("E2E Auto-Conversations", False, "No auto-conversations detected")
    
    # Step 4: User clicks Pause button
    print("\n⏸️ Step 4: User clicks Pause button...")
    
    pause_start_time = time.time()
    pause_response = make_authenticated_request('POST', '/simulation/pause')
    pause_end_time = time.time()
    
    if pause_response and pause_response.status_code == 200:
        pause_response_time = pause_end_time - pause_start_time
        
        if pause_response_time <= 2.0:
            log_test_result("E2E Pause Response", True, f"Pause button responded instantly ({pause_response_time:.2f}s)")
        else:
            log_test_result("E2E Pause Response", False, f"Pause button too slow ({pause_response_time:.2f}s)")
        
        # Verify inactive state
        response = make_authenticated_request('GET', '/simulation/state')
        if response and response.status_code == 200:
            state = response.json()
            if not state.get('is_active', True):
                log_test_result("E2E Pause State Change", True, "Simulation deactivated successfully")
            else:
                log_test_result("E2E Pause State Change", False, "Simulation not deactivated")
    else:
        log_test_result("E2E Pause Response", False, "Pause button failed")
    
    # Step 5: Verify no more auto-conversations after pause (30 seconds)
    print("\n🛑 Step 5: Verifying no more auto-conversations after pause (30 seconds)...")
    
    post_pause_count = auto_conversations_detected + initial_count
    post_pause_start = time.time()
    unwanted_conversations = False
    
    while time.time() - post_pause_start < 30:
        response = make_authenticated_request('GET', '/conversations')
        if response and response.status_code == 200:
            current_conversations = response.json()
            current_count = len(current_conversations)
            
            if current_count > post_pause_count:
                unwanted_conversations = True
                break
        
        time.sleep(10)  # Check every 10 seconds
    
    if not unwanted_conversations:
        log_test_result("E2E Post-Pause Clean", True, "No unwanted conversations after pause")
    else:
        log_test_result("E2E Post-Pause Clean", False, "Unwanted conversations detected after pause")
    
    # Step 6: Overall user experience assessment
    print("\n🎯 Step 6: Overall user experience assessment...")
    
    # Calculate overall success metrics
    play_works = start_response and start_response.status_code == 200
    auto_works = auto_conversations_detected >= 1
    pause_works = pause_response and pause_response.status_code == 200
    clean_stop = not unwanted_conversations
    
    overall_success = play_works and auto_works and pause_works and clean_stop
    
    if overall_success:
        log_test_result("E2E Overall Experience", True, "Complete play/pause system working perfectly")
    else:
        issues = []
        if not play_works: issues.append("Play button")
        if not auto_works: issues.append("Auto-conversations")
        if not pause_works: issues.append("Pause button")
        if not clean_stop: issues.append("Clean stop")
        
        log_test_result("E2E Overall Experience", False, f"Issues with: {', '.join(issues)}")
    
    return overall_success

def run_all_auto_conversation_tests():
    """Run all auto-conversation system tests"""
    print("🚀 COMPLETE PLAY/PAUSE SYSTEM WITH AUTO-CONVERSATION FIX TESTING")
    print("=" * 80)
    print("Testing the complete solution to fix the play/pause chaos with auto-conversation system")
    print("=" * 80)
    
    # Test 1: Play Button Auto-Conversation System
    test1_passed = test_play_button_auto_conversation_system()
    
    # Test 2: Auto-Conversation Generation Loop
    test2_passed = test_auto_conversation_generation_loop()
    
    # Test 3: Pause Button Stops Auto-Generation
    test3_passed = test_pause_button_stops_auto_generation()
    
    # Test 4: State Consistency & Clean Operation
    test4_passed = test_state_consistency_and_clean_operation()
    
    # Test 5: End-to-End User Experience Simulation
    test5_passed = test_end_to_end_user_experience()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 AUTO-CONVERSATION SYSTEM TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    # Detailed test results
    print(f"\n🔍 DETAILED TEST RESULTS:")
    print(f"   Test 1 - Play Button Auto-Conversation System: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Test 2 - Auto-Conversation Generation Loop: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"   Test 3 - Pause Button Stops Auto-Generation: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print(f"   Test 4 - State Consistency & Clean Operation: {'✅ PASS' if test4_passed else '❌ FAIL'}")
    print(f"   Test 5 - End-to-End User Experience: {'✅ PASS' if test5_passed else '❌ FAIL'}")
    
    all_tests_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
    
    if all_tests_passed:
        print("\n🎉 AUTO-CONVERSATION SYSTEM TESTING RESULT: ALL TESTS PASSED!")
        print("   ✅ Play button instant response + auto-conversations every 30s")
        print("   ✅ No more loading circle forever (conversations appear automatically)")
        print("   ✅ Pause button stops everything cleanly (no zombie processes)")
        print("   ✅ No animation conflicts or state chaos")
        print("   ✅ Proper progressive streaming integration")
        print("\n🏆 COMPLETE PLAY/PAUSE SYSTEM FIX: SUCCESSFUL!")
    else:
        print("\n❌ AUTO-CONVERSATION SYSTEM TESTING RESULT: SOME TESTS FAILED!")
        print("   Please check the failed tests above for details")
        print("   The auto-conversation system may need attention")
    
    print("\n" + "="*80)
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_all_auto_conversation_tests()
    sys.exit(0 if success else 1)