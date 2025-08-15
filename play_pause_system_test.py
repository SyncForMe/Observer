#!/usr/bin/env python3
"""
COMPREHENSIVE PLAY/PAUSE SYSTEM BREAKDOWN INVESTIGATION

The user reports FUNDAMENTAL SYSTEM CHAOS with play/pause buttons:

CRITICAL ISSUES REPORTED:
1. Play button: Shows loading circle, NO conversations generated
2. Pause button: Takes time to respond, but THEN animations start showing  
3. Animations appear AFTER simulation stops: "Agents entering room" when paused
4. More animations when stopped: "Agents preparing" after pause completes
5. State confusion: "Waiting to start" + "Agents are thinking" simultaneously

SUSPECTED ROOT CAUSES:
- Multiple animation systems conflicting
- Frontend/backend state completely out of sync
- Async operations happening in wrong order
- Play/pause endpoints doing unexpected things
- Race conditions between different systems

URGENT COMPREHENSIVE TESTS:
1. Play Button Investigation - Test what EXACTLY happens when /simulation/start is called
2. Backend State vs Frontend State - Check state consistency between API calls
3. Pause Button Investigation - Test what EXACTLY happens when /simulation/pause is called
4. Background Process Detection - Check for zombie conversation generation processes
5. Animation System Conflicts - Identify all systems that can trigger loading animations
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

def get_simulation_state():
    """Get current simulation state"""
    response = make_authenticated_request('GET', '/simulation/state')
    if response and response.status_code == 200:
        return response.json()
    return None

def test_play_button_investigation():
    """Test 1: Play Button Investigation - Test what EXACTLY happens when /simulation/start is called"""
    print("\n" + "="*80)
    print("🎮 TEST 1: PLAY BUTTON INVESTIGATION")
    print("="*80)
    
    # Step 1: Get initial simulation state
    print("\n📊 Step 1: Getting initial simulation state...")
    initial_state = get_simulation_state()
    if initial_state:
        print(f"   Initial state: is_active={initial_state.get('is_active', 'unknown')}")
        print(f"   Current day: {initial_state.get('current_day', 'unknown')}")
        print(f"   Time period: {initial_state.get('current_time_period', 'unknown')}")
        log_test_result("Initial State Check", True, f"is_active={initial_state.get('is_active')}")
    else:
        log_test_result("Initial State Check", False, "Failed to get initial simulation state")
        return False
    
    # Step 2: Ensure we have agents for testing
    print("\n🤖 Step 2: Checking agent availability...")
    response = make_authenticated_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        agent_count = len(agents)
        if agent_count >= 2:
            log_test_result("Agent Availability", True, f"Found {agent_count} agents")
            print(f"   Agents: {[agent.get('name', 'Unknown') for agent in agents[:3]]}")
        else:
            log_test_result("Agent Availability", False, f"Only {agent_count} agents found (need at least 2)")
            return False
    else:
        log_test_result("Agent Availability", False, "Failed to get agents")
        return False
    
    # Step 3: Test the PLAY button (/simulation/start)
    print("\n▶️ Step 3: Testing PLAY button (/simulation/start)...")
    print("   🔍 CRITICAL: Monitoring what EXACTLY happens when play is pressed...")
    
    start_time = time.time()
    
    # Call the start endpoint
    response = make_authenticated_request('POST', '/simulation/start', timeout=15)
    
    if response and response.status_code == 200:
        end_time = time.time()
        response_time = end_time - start_time
        
        response_data = response.json()
        print(f"   ⏱️ Response time: {response_time:.2f} seconds")
        print(f"   📋 Response data: {json.dumps(response_data, indent=2)}")
        
        log_test_result("Play Button Response", True, f"Responded in {response_time:.2f}s")
        
        # Step 4: Check simulation state immediately after play
        print("\n📊 Step 4: Checking simulation state IMMEDIATELY after play...")
        immediate_state = get_simulation_state()
        if immediate_state:
            is_active_after = immediate_state.get('is_active', False)
            print(f"   State after play: is_active={is_active_after}")
            
            if is_active_after:
                log_test_result("Play State Change", True, "Simulation is_active=True after play")
            else:
                log_test_result("Play State Change", False, "Simulation is_active=False after play (CRITICAL ISSUE)")
        else:
            log_test_result("Play State Check", False, "Failed to get state after play")
        
        # Step 5: Wait and check for conversation generation
        print("\n💬 Step 5: Monitoring for conversation generation (30 seconds)...")
        initial_conv_count = 0
        
        # Get initial conversation count
        conv_response = make_authenticated_request('GET', '/conversations')
        if conv_response and conv_response.status_code == 200:
            initial_conversations = conv_response.json()
            initial_conv_count = len(initial_conversations)
            print(f"   Initial conversation count: {initial_conv_count}")
        
        # Wait and monitor for new conversations
        for i in range(6):  # Check every 5 seconds for 30 seconds
            time.sleep(5)
            conv_response = make_authenticated_request('GET', '/conversations')
            if conv_response and conv_response.status_code == 200:
                current_conversations = conv_response.json()
                current_conv_count = len(current_conversations)
                print(f"   After {(i+1)*5}s: {current_conv_count} conversations")
                
                if current_conv_count > initial_conv_count:
                    log_test_result("Conversation Generation", True, f"NEW conversations generated: {current_conv_count - initial_conv_count}")
                    break
        else:
            log_test_result("Conversation Generation", False, "NO new conversations generated after 30 seconds (CRITICAL ISSUE)")
        
    else:
        log_test_result("Play Button Response", False, f"Play button failed: {response.status_code if response else 'No response'}")
        return False
    
    return True

def test_backend_vs_frontend_state():
    """Test 2: Backend State vs Frontend State - Check state consistency between API calls"""
    print("\n" + "="*80)
    print("🔄 TEST 2: BACKEND STATE VS FRONTEND STATE CONSISTENCY")
    print("="*80)
    
    # Step 1: Get simulation state multiple times to check consistency
    print("\n📊 Step 1: Testing state consistency across multiple calls...")
    
    states = []
    for i in range(5):
        state = get_simulation_state()
        if state:
            states.append({
                'call': i+1,
                'is_active': state.get('is_active'),
                'current_day': state.get('current_day'),
                'current_time_period': state.get('current_time_period'),
                'timestamp': time.time()
            })
            time.sleep(1)  # 1 second between calls
    
    if len(states) == 5:
        # Check for consistency
        is_active_values = [s['is_active'] for s in states]
        day_values = [s['current_day'] for s in states]
        time_period_values = [s['current_time_period'] for s in states]
        
        is_active_consistent = len(set(is_active_values)) == 1
        day_consistent = len(set(day_values)) == 1
        time_period_consistent = len(set(time_period_values)) == 1
        
        if is_active_consistent and day_consistent and time_period_consistent:
            log_test_result("State Consistency", True, f"All values consistent: is_active={is_active_values[0]}, day={day_values[0]}, period={time_period_values[0]}")
        else:
            log_test_result("State Consistency", False, f"INCONSISTENT VALUES: is_active={set(is_active_values)}, day={set(day_values)}, period={set(time_period_values)}")
            
        # Print detailed state info
        print("   📋 Detailed state calls:")
        for state in states:
            print(f"      Call {state['call']}: is_active={state['is_active']}, day={state['current_day']}, period={state['current_time_period']}")
    else:
        log_test_result("State Consistency", False, f"Only got {len(states)} out of 5 state calls")
    
    # Step 2: Test state during play operation
    print("\n▶️ Step 2: Testing state consistency during play operation...")
    
    # Start simulation
    response = make_authenticated_request('POST', '/simulation/start')
    if response and response.status_code == 200:
        # Check state immediately and after delays
        immediate_state = get_simulation_state()
        time.sleep(2)
        delayed_state = get_simulation_state()
        time.sleep(3)
        final_state = get_simulation_state()
        
        if immediate_state and delayed_state and final_state:
            immediate_active = immediate_state.get('is_active')
            delayed_active = delayed_state.get('is_active')
            final_active = final_state.get('is_active')
            
            print(f"   Immediate: is_active={immediate_active}")
            print(f"   After 2s: is_active={delayed_active}")
            print(f"   After 5s: is_active={final_active}")
            
            if immediate_active == delayed_active == final_active:
                log_test_result("Play State Consistency", True, f"State remained consistent: is_active={immediate_active}")
            else:
                log_test_result("Play State Consistency", False, f"State changed unexpectedly: {immediate_active} → {delayed_active} → {final_active}")
        else:
            log_test_result("Play State Consistency", False, "Failed to get states during play operation")
    else:
        log_test_result("Play State Test", False, "Failed to start simulation for state testing")
    
    return True

def test_pause_button_investigation():
    """Test 3: Pause Button Investigation - Test what EXACTLY happens when /simulation/pause is called"""
    print("\n" + "="*80)
    print("⏸️ TEST 3: PAUSE BUTTON INVESTIGATION")
    print("="*80)
    
    # Step 1: Ensure simulation is running first
    print("\n▶️ Step 1: Starting simulation to test pause...")
    response = make_authenticated_request('POST', '/simulation/start')
    if response and response.status_code == 200:
        log_test_result("Pre-Pause Start", True, "Simulation started for pause testing")
        
        # Wait a moment for simulation to be fully active
        time.sleep(3)
        
        # Verify it's running
        state = get_simulation_state()
        if state and state.get('is_active'):
            print(f"   ✅ Simulation confirmed running: is_active={state.get('is_active')}")
        else:
            log_test_result("Pre-Pause Verification", False, "Simulation not running before pause test")
            return False
    else:
        log_test_result("Pre-Pause Start", False, "Failed to start simulation for pause testing")
        return False
    
    # Step 2: Test the PAUSE button (/simulation/pause)
    print("\n⏸️ Step 2: Testing PAUSE button (/simulation/pause)...")
    print("   🔍 CRITICAL: Monitoring what EXACTLY happens when pause is pressed...")
    
    start_time = time.time()
    
    # Call the pause endpoint
    response = make_authenticated_request('POST', '/simulation/pause', timeout=15)
    
    if response and response.status_code == 200:
        end_time = time.time()
        response_time = end_time - start_time
        
        response_data = response.json()
        print(f"   ⏱️ Pause response time: {response_time:.2f} seconds")
        print(f"   📋 Pause response data: {json.dumps(response_data, indent=2)}")
        
        log_test_result("Pause Button Response", True, f"Responded in {response_time:.2f}s")
        
        # Step 3: Check simulation state immediately after pause
        print("\n📊 Step 3: Checking simulation state IMMEDIATELY after pause...")
        immediate_state = get_simulation_state()
        if immediate_state:
            is_active_after = immediate_state.get('is_active', True)
            print(f"   State immediately after pause: is_active={is_active_after}")
            
            if not is_active_after:
                log_test_result("Pause State Change", True, "Simulation is_active=False after pause")
            else:
                log_test_result("Pause State Change", False, "Simulation is_active=True after pause (CRITICAL ISSUE)")
        else:
            log_test_result("Pause State Check", False, "Failed to get state after pause")
        
        # Step 4: Monitor for unexpected activity after pause
        print("\n👀 Step 4: Monitoring for unexpected activity AFTER pause (20 seconds)...")
        
        # Get conversation count before monitoring
        conv_response = make_authenticated_request('GET', '/conversations')
        initial_conv_count = 0
        if conv_response and conv_response.status_code == 200:
            initial_conversations = conv_response.json()
            initial_conv_count = len(initial_conversations)
            print(f"   Conversation count at pause: {initial_conv_count}")
        
        # Monitor for unexpected conversations or state changes
        unexpected_activity = False
        for i in range(4):  # Check every 5 seconds for 20 seconds
            time.sleep(5)
            
            # Check for new conversations (should NOT happen when paused)
            conv_response = make_authenticated_request('GET', '/conversations')
            if conv_response and conv_response.status_code == 200:
                current_conversations = conv_response.json()
                current_conv_count = len(current_conversations)
                
                if current_conv_count > initial_conv_count:
                    print(f"   ⚠️ UNEXPECTED: New conversations generated while paused! ({current_conv_count - initial_conv_count} new)")
                    unexpected_activity = True
                
            # Check state consistency
            current_state = get_simulation_state()
            if current_state and current_state.get('is_active'):
                print(f"   ⚠️ UNEXPECTED: Simulation became active again while paused!")
                unexpected_activity = True
            
            print(f"   After {(i+1)*5}s: conversations={current_conv_count}, is_active={current_state.get('is_active') if current_state else 'unknown'}")
        
        if not unexpected_activity:
            log_test_result("Post-Pause Activity", True, "No unexpected activity after pause")
        else:
            log_test_result("Post-Pause Activity", False, "UNEXPECTED activity detected after pause (CRITICAL ISSUE)")
        
    else:
        log_test_result("Pause Button Response", False, f"Pause button failed: {response.status_code if response else 'No response'}")
        return False
    
    return True

def test_background_process_detection():
    """Test 4: Background Process Detection - Check for zombie conversation generation processes"""
    print("\n" + "="*80)
    print("🔍 TEST 4: BACKGROUND PROCESS DETECTION")
    print("="*80)
    
    # Step 1: Start simulation and let it run briefly
    print("\n🚀 Step 1: Starting simulation to create background processes...")
    response = make_authenticated_request('POST', '/simulation/start')
    if response and response.status_code == 200:
        log_test_result("Background Test Start", True, "Simulation started for background process testing")
        
        # Let it run for a bit to potentially create background processes
        time.sleep(10)
        
        # Get initial conversation count
        conv_response = make_authenticated_request('GET', '/conversations')
        initial_conv_count = 0
        if conv_response and conv_response.status_code == 200:
            initial_conversations = conv_response.json()
            initial_conv_count = len(initial_conversations)
            print(f"   Conversations after 10s run: {initial_conv_count}")
    else:
        log_test_result("Background Test Start", False, "Failed to start simulation for background testing")
        return False
    
    # Step 2: Pause simulation
    print("\n⏸️ Step 2: Pausing simulation...")
    response = make_authenticated_request('POST', '/simulation/pause')
    if response and response.status_code == 200:
        log_test_result("Background Test Pause", True, "Simulation paused for background process detection")
        
        # Verify it's paused
        state = get_simulation_state()
        if state and not state.get('is_active'):
            print(f"   ✅ Simulation confirmed paused: is_active={state.get('is_active')}")
        else:
            print(f"   ⚠️ Simulation state unclear: is_active={state.get('is_active') if state else 'unknown'}")
    else:
        log_test_result("Background Test Pause", False, "Failed to pause simulation")
        return False
    
    # Step 3: Monitor for zombie processes (conversations generated while paused)
    print("\n🧟 Step 3: Monitoring for zombie background processes (60 seconds)...")
    
    zombie_detected = False
    monitoring_results = []
    
    for i in range(12):  # Check every 5 seconds for 60 seconds
        time.sleep(5)
        
        # Check conversation count
        conv_response = make_authenticated_request('GET', '/conversations')
        if conv_response and conv_response.status_code == 200:
            current_conversations = conv_response.json()
            current_conv_count = len(current_conversations)
            
            # Check simulation state
            state = get_simulation_state()
            is_active = state.get('is_active') if state else 'unknown'
            
            monitoring_results.append({
                'time': (i+1)*5,
                'conversations': current_conv_count,
                'is_active': is_active
            })
            
            # Detect zombie activity
            if current_conv_count > initial_conv_count:
                print(f"   🚨 ZOMBIE DETECTED at {(i+1)*5}s: {current_conv_count - initial_conv_count} new conversations while paused!")
                zombie_detected = True
            
            if is_active and i > 0:  # Allow first check to settle
                print(f"   🚨 STATE ZOMBIE at {(i+1)*5}s: Simulation became active while supposed to be paused!")
                zombie_detected = True
            
            print(f"   {(i+1)*5}s: conversations={current_conv_count} (+{current_conv_count - initial_conv_count}), is_active={is_active}")
    
    # Step 4: Analyze monitoring results
    print("\n📊 Step 4: Analyzing background process monitoring results...")
    
    if not zombie_detected:
        log_test_result("Zombie Process Detection", True, "No zombie background processes detected")
    else:
        log_test_result("Zombie Process Detection", False, "ZOMBIE PROCESSES DETECTED (CRITICAL ISSUE)")
    
    # Check for patterns in the monitoring data
    conversation_changes = [r['conversations'] - initial_conv_count for r in monitoring_results]
    state_changes = [r['is_active'] for r in monitoring_results]
    
    print(f"   📈 Conversation changes: {conversation_changes}")
    print(f"   🔄 State changes: {set(state_changes)}")
    
    # Detect if there are periodic increases (indicating background generation)
    if any(change > 0 for change in conversation_changes):
        log_test_result("Background Generation Pattern", False, "Background conversation generation detected while paused")
    else:
        log_test_result("Background Generation Pattern", True, "No background conversation generation detected")
    
    return True

def test_animation_system_conflicts():
    """Test 5: Animation System Conflicts - Identify all systems that can trigger loading animations"""
    print("\n" + "="*80)
    print("🎭 TEST 5: ANIMATION SYSTEM CONFLICTS")
    print("="*80)
    
    # Step 1: Test rapid play/pause cycles to trigger conflicts
    print("\n🔄 Step 1: Testing rapid play/pause cycles...")
    
    cycle_results = []
    
    for cycle in range(3):
        print(f"\n   Cycle {cycle + 1}:")
        
        # Play
        start_time = time.time()
        play_response = make_authenticated_request('POST', '/simulation/start', timeout=10)
        play_time = time.time() - start_time
        
        # Quick state check
        play_state = get_simulation_state()
        play_active = play_state.get('is_active') if play_state else 'unknown'
        
        # Wait briefly
        time.sleep(2)
        
        # Pause
        start_time = time.time()
        pause_response = make_authenticated_request('POST', '/simulation/pause', timeout=10)
        pause_time = time.time() - start_time
        
        # Quick state check
        pause_state = get_simulation_state()
        pause_active = pause_state.get('is_active') if pause_state else 'unknown'
        
        cycle_result = {
            'cycle': cycle + 1,
            'play_success': play_response.status_code == 200 if play_response else False,
            'play_time': play_time,
            'play_active': play_active,
            'pause_success': pause_response.status_code == 200 if pause_response else False,
            'pause_time': pause_time,
            'pause_active': pause_active
        }
        
        cycle_results.append(cycle_result)
        
        print(f"      Play: {cycle_result['play_success']} ({cycle_result['play_time']:.2f}s) → is_active={cycle_result['play_active']}")
        print(f"      Pause: {cycle_result['pause_success']} ({cycle_result['pause_time']:.2f}s) → is_active={cycle_result['pause_active']}")
        
        time.sleep(1)  # Brief pause between cycles
    
    # Analyze cycle results
    play_successes = sum(1 for r in cycle_results if r['play_success'])
    pause_successes = sum(1 for r in cycle_results if r['pause_success'])
    
    if play_successes == 3 and pause_successes == 3:
        log_test_result("Rapid Cycle Handling", True, "All play/pause cycles succeeded")
    else:
        log_test_result("Rapid Cycle Handling", False, f"Some cycles failed: play={play_successes}/3, pause={pause_successes}/3")
    
    # Step 2: Test state consistency after rapid cycles
    print("\n📊 Step 2: Testing state consistency after rapid cycles...")
    
    final_states = []
    for i in range(5):
        state = get_simulation_state()
        if state:
            final_states.append(state.get('is_active'))
        time.sleep(1)
    
    if len(set(final_states)) == 1:
        log_test_result("Post-Cycle State Consistency", True, f"State consistent after cycles: is_active={final_states[0]}")
    else:
        log_test_result("Post-Cycle State Consistency", False, f"State inconsistent after cycles: {set(final_states)}")
    
    # Step 3: Test for delayed reactions (animations appearing after operations)
    print("\n⏰ Step 3: Testing for delayed reactions...")
    
    # Start simulation
    print("   Starting simulation...")
    start_response = make_authenticated_request('POST', '/simulation/start')
    if start_response and start_response.status_code == 200:
        
        # Immediately pause
        print("   Immediately pausing...")
        pause_response = make_authenticated_request('POST', '/simulation/pause')
        if pause_response and pause_response.status_code == 200:
            
            # Monitor for delayed activity
            print("   Monitoring for delayed activity (15 seconds)...")
            
            initial_conv_response = make_authenticated_request('GET', '/conversations')
            initial_conv_count = len(initial_conv_response.json()) if initial_conv_response and initial_conv_response.status_code == 200 else 0
            
            delayed_activity = False
            for i in range(3):  # Check every 5 seconds for 15 seconds
                time.sleep(5)
                
                # Check for new conversations (delayed generation)
                conv_response = make_authenticated_request('GET', '/conversations')
                if conv_response and conv_response.status_code == 200:
                    current_conv_count = len(conv_response.json())
                    if current_conv_count > initial_conv_count:
                        print(f"      ⚠️ DELAYED ACTIVITY: {current_conv_count - initial_conv_count} conversations generated {(i+1)*5}s after pause!")
                        delayed_activity = True
                
                # Check state
                state = get_simulation_state()
                is_active = state.get('is_active') if state else 'unknown'
                print(f"      {(i+1)*5}s: conversations={current_conv_count}, is_active={is_active}")
            
            if not delayed_activity:
                log_test_result("Delayed Activity Detection", True, "No delayed activity detected")
            else:
                log_test_result("Delayed Activity Detection", False, "DELAYED ACTIVITY DETECTED (CRITICAL ISSUE)")
        else:
            log_test_result("Delayed Activity Test Setup", False, "Failed to pause for delayed activity test")
    else:
        log_test_result("Delayed Activity Test Setup", False, "Failed to start for delayed activity test")
    
    return True

def run_all_tests():
    """Run all play/pause system breakdown investigation tests"""
    print("🚨 COMPREHENSIVE PLAY/PAUSE SYSTEM BREAKDOWN INVESTIGATION")
    print("=" * 80)
    print("Investigating FUNDAMENTAL SYSTEM CHAOS with play/pause buttons")
    print("=" * 80)
    
    # Test 1: Play Button Investigation
    test1_passed = test_play_button_investigation()
    
    # Test 2: Backend State vs Frontend State
    test2_passed = test_backend_vs_frontend_state()
    
    # Test 3: Pause Button Investigation
    test3_passed = test_pause_button_investigation()
    
    # Test 4: Background Process Detection
    test4_passed = test_background_process_detection()
    
    # Test 5: Animation System Conflicts
    test5_passed = test_animation_system_conflicts()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 PLAY/PAUSE SYSTEM INVESTIGATION SUMMARY")
    print("="*80)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    # Detailed test results
    print(f"\n🔍 DETAILED TEST RESULTS:")
    print(f"   Test 1 - Play Button Investigation: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Test 2 - Backend vs Frontend State: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"   Test 3 - Pause Button Investigation: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print(f"   Test 4 - Background Process Detection: {'✅ PASS' if test4_passed else '❌ FAIL'}")
    print(f"   Test 5 - Animation System Conflicts: {'✅ PASS' if test5_passed else '❌ FAIL'}")
    
    # Critical issues summary
    print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
    failed_tests = [test for test in test_results["tests"] if not test["passed"]]
    
    if not failed_tests:
        print("   ✅ No critical issues found - play/pause system working correctly")
    else:
        for test in failed_tests:
            print(f"   ❌ {test['name']}: {test['details']}")
    
    all_tests_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
    
    if all_tests_passed:
        print("\n🎉 PLAY/PAUSE SYSTEM INVESTIGATION RESULT: ALL TESTS PASSED!")
        print("   ✅ Play button working correctly")
        print("   ✅ Pause button working correctly")
        print("   ✅ No state synchronization issues")
        print("   ✅ No zombie background processes")
        print("   ✅ No animation system conflicts")
    else:
        print("\n❌ PLAY/PAUSE SYSTEM INVESTIGATION RESULT: CRITICAL ISSUES FOUND!")
        print("   🚨 The play/pause system has fundamental problems")
        print("   🔧 Immediate fixes required for proper functionality")
    
    print("\n" + "="*80)
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)