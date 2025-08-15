#!/usr/bin/env python3
"""
CONVERSATION GENERATION TIMING ISSUES TESTING
Testing backend conversation generation system to understand timing and display issues.

SPECIFIC ISSUES TO INVESTIGATE:
1. 10 messages appearing at once instead of progressive/sequential display
2. Long delays in play/pause operations
3. Missing loading animations

BACKEND TESTS:
- Test 1: Conversation Generation Timing - measure /api/conversation/generate endpoint
- Test 2: Simulation Start/Pause Performance - test simulation control endpoints  
- Test 3: Progressive Message Display - check /api/conversations/active for progressive updates
- Test 4: Database Storage Pattern - verify how conversations are stored
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import threading
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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "timing_data": {}
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

def log_test_result(test_name, passed, details="", timing_data=None):
    """Log test result with optional timing data"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details,
        "timing": timing_data
    })
    
    if timing_data:
        test_results["timing_data"][test_name] = timing_data
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def test_conversation_generation_timing():
    """Test 1: Conversation Generation Timing - measure how long it takes to generate a conversation"""
    print("\n" + "="*80)
    print("🕐 TEST 1: CONVERSATION GENERATION TIMING")
    print("="*80)
    
    # Set up scenario first
    scenario_data = {
        "scenario": "A team of engineers needs to design a new communication system for emergency response teams.",
        "scenario_name": "Emergency Communication System Design"
    }
    
    response = make_authenticated_request('POST', '/simulation/set-scenario', scenario_data)
    if not response or response.status_code != 200:
        log_test_result("Scenario Setup for Timing Test", False, "Failed to set scenario")
        return False
    
    # Get initial conversation count
    response = make_authenticated_request('GET', '/conversations')
    initial_count = 0
    if response and response.status_code == 200:
        initial_count = len(response.json())
    
    print(f"📊 Initial conversation count: {initial_count}")
    
    # Test conversation generation timing
    print("🚀 Starting conversation generation...")
    start_time = time.time()
    
    response = make_authenticated_request('POST', '/conversation/generate', timeout=120)
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    timing_data = {
        "generation_time_seconds": generation_time,
        "start_time": start_time,
        "end_time": end_time
    }
    
    if response and response.status_code == 200:
        response_data = response.json()
        
        # Check if messages are returned immediately or if it waits
        messages_in_response = response_data.get('messages', [])
        message_count_in_response = len(messages_in_response)
        
        timing_data["messages_in_response"] = message_count_in_response
        timing_data["response_size_chars"] = len(str(response_data))
        
        log_test_result(
            "Conversation Generation Timing", 
            True, 
            f"Generated in {generation_time:.2f} seconds with {message_count_in_response} messages in response",
            timing_data
        )
        
        # Check if this is causing bulk display (all messages at once)
        if generation_time > 30:
            print("⚠️  WARNING: Long generation time may cause bulk message display")
        
        if message_count_in_response > 5:
            print("⚠️  WARNING: Many messages returned at once - may cause bulk display issue")
        
    else:
        log_test_result(
            "Conversation Generation Timing", 
            False, 
            f"Failed after {generation_time:.2f} seconds: {response.status_code if response else 'No response'}",
            timing_data
        )
        return False
    
    # Check database state after generation
    response = make_authenticated_request('GET', '/conversations')
    if response and response.status_code == 200:
        final_conversations = response.json()
        final_count = len(final_conversations)
        new_conversations = final_count - initial_count
        
        timing_data["conversations_created"] = new_conversations
        
        if new_conversations > 0:
            latest_conversation = final_conversations[-1]
            messages = latest_conversation.get('messages', [])
            timing_data["messages_in_latest_conversation"] = len(messages)
            
            print(f"📈 Database state: {new_conversations} new conversation(s), {len(messages)} messages in latest")
            
            # Check if all messages have similar timestamps (bulk creation)
            if len(messages) > 1:
                timestamps = []
                for msg in messages:
                    if 'timestamp' in msg:
                        timestamps.append(msg['timestamp'])
                
                if len(timestamps) > 1:
                    # Check if all timestamps are very close (indicating bulk creation)
                    first_time = timestamps[0]
                    last_time = timestamps[-1]
                    
                    # Simple string comparison for ISO timestamps
                    if first_time == last_time:
                        print("⚠️  WARNING: All messages have identical timestamps - bulk creation detected")
                        timing_data["bulk_creation_detected"] = True
                    else:
                        print("✅ Messages have different timestamps - sequential creation")
                        timing_data["bulk_creation_detected"] = False
        
    return True

def test_simulation_control_performance():
    """Test 2: Simulation Start/Pause Performance - test simulation control endpoints"""
    print("\n" + "="*80)
    print("⏯️  TEST 2: SIMULATION START/PAUSE PERFORMANCE")
    print("="*80)
    
    timing_results = {}
    
    # Test simulation start
    print("🚀 Testing simulation start...")
    start_time = time.time()
    response = make_authenticated_request('POST', '/simulation/start')
    end_time = time.time()
    
    start_timing = end_time - start_time
    timing_results["start_time"] = start_timing
    
    if response and response.status_code == 200:
        log_test_result("Simulation Start Performance", True, f"Started in {start_timing:.2f} seconds")
    else:
        log_test_result("Simulation Start Performance", False, f"Failed after {start_timing:.2f} seconds")
        return False
    
    # Wait a moment
    time.sleep(1)
    
    # Test simulation pause
    print("⏸️  Testing simulation pause...")
    start_time = time.time()
    response = make_authenticated_request('POST', '/simulation/pause')
    end_time = time.time()
    
    pause_timing = end_time - start_time
    timing_results["pause_time"] = pause_timing
    
    if response and response.status_code == 200:
        log_test_result("Simulation Pause Performance", True, f"Paused in {pause_timing:.2f} seconds")
    else:
        log_test_result("Simulation Pause Performance", False, f"Failed after {pause_timing:.2f} seconds")
    
    # Test simulation resume
    print("▶️  Testing simulation resume...")
    start_time = time.time()
    response = make_authenticated_request('POST', '/simulation/resume')
    end_time = time.time()
    
    resume_timing = end_time - start_time
    timing_results["resume_time"] = resume_timing
    
    if response and response.status_code == 200:
        log_test_result("Simulation Resume Performance", True, f"Resumed in {resume_timing:.2f} seconds")
    else:
        log_test_result("Simulation Resume Performance", False, f"Failed after {resume_timing:.2f} seconds")
    
    # Check if any operations are taking too long (causing UI delays)
    slow_operations = []
    if start_timing > 2:
        slow_operations.append(f"Start: {start_timing:.2f}s")
    if pause_timing > 2:
        slow_operations.append(f"Pause: {pause_timing:.2f}s")
    if resume_timing > 2:
        slow_operations.append(f"Resume: {resume_timing:.2f}s")
    
    if slow_operations:
        print(f"⚠️  WARNING: Slow operations detected: {', '.join(slow_operations)}")
        print("   This may cause long delays in play/pause operations")
    
    timing_results["slow_operations"] = slow_operations
    test_results["timing_data"]["simulation_control"] = timing_results
    
    return True

def test_progressive_message_display():
    """Test 3: Progressive Message Display - check if messages appear progressively"""
    print("\n" + "="*80)
    print("📈 TEST 3: PROGRESSIVE MESSAGE DISPLAY")
    print("="*80)
    
    # Check if there's an active conversations endpoint
    print("🔍 Checking for active conversations endpoint...")
    response = make_authenticated_request('GET', '/conversations/active')
    
    if response and response.status_code == 200:
        print("✅ /api/conversations/active endpoint exists")
        active_conversations = response.json()
        print(f"📊 Active conversations: {len(active_conversations) if isinstance(active_conversations, list) else 'Not a list'}")
    else:
        print("❌ /api/conversations/active endpoint not found or failed")
        print("   Testing with regular /api/conversations endpoint instead")
    
    # Monitor conversation updates during generation
    print("🔄 Starting conversation generation with monitoring...")
    
    # Get initial state
    response = make_authenticated_request('GET', '/conversations')
    if not response or response.status_code != 200:
        log_test_result("Progressive Display Setup", False, "Failed to get initial conversations")
        return False
    
    initial_conversations = response.json()
    initial_count = len(initial_conversations)
    
    # Start monitoring in a separate thread
    monitoring_data = {"snapshots": [], "stop": False}
    
    def monitor_conversations():
        """Monitor conversations during generation"""
        snapshot_count = 0
        while not monitoring_data["stop"] and snapshot_count < 20:  # Max 20 snapshots
            try:
                response = make_authenticated_request('GET', '/conversations', timeout=5)
                if response and response.status_code == 200:
                    conversations = response.json()
                    snapshot = {
                        "timestamp": time.time(),
                        "conversation_count": len(conversations),
                        "snapshot_number": snapshot_count
                    }
                    
                    # Check latest conversation for message count
                    if len(conversations) > initial_count:
                        latest_conv = conversations[-1]
                        snapshot["latest_message_count"] = len(latest_conv.get('messages', []))
                    
                    monitoring_data["snapshots"].append(snapshot)
                    snapshot_count += 1
                
                time.sleep(0.5)  # Check every 500ms
            except:
                break
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_conversations)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Generate conversation
    start_time = time.time()
    response = make_authenticated_request('POST', '/conversation/generate', timeout=120)
    end_time = time.time()
    
    # Stop monitoring
    monitoring_data["stop"] = True
    monitor_thread.join(timeout=2)
    
    generation_time = end_time - start_time
    snapshots = monitoring_data["snapshots"]
    
    if response and response.status_code == 200:
        log_test_result("Progressive Display Generation", True, f"Generated in {generation_time:.2f}s with {len(snapshots)} monitoring snapshots")
        
        # Analyze snapshots for progressive updates
        if len(snapshots) > 1:
            print(f"📊 Monitoring analysis ({len(snapshots)} snapshots):")
            
            progressive_updates = False
            message_count_changes = []
            
            for i, snapshot in enumerate(snapshots):
                print(f"   Snapshot {i+1}: {snapshot.get('conversation_count', 0)} conversations, {snapshot.get('latest_message_count', 0)} messages in latest")
                
                if i > 0:
                    prev_messages = snapshots[i-1].get('latest_message_count', 0)
                    curr_messages = snapshot.get('latest_message_count', 0)
                    if curr_messages > prev_messages:
                        message_count_changes.append(curr_messages - prev_messages)
                        progressive_updates = True
            
            if progressive_updates:
                log_test_result("Progressive Message Updates", True, f"Messages appeared progressively: {message_count_changes}")
            else:
                log_test_result("Progressive Message Updates", False, "No progressive updates detected - messages may appear all at once")
                print("⚠️  This could explain the '10 messages appearing at once' issue")
        
        else:
            log_test_result("Progressive Display Monitoring", False, "Insufficient monitoring data collected")
    
    else:
        log_test_result("Progressive Display Generation", False, f"Generation failed after {generation_time:.2f}s")
        return False
    
    return True

def test_database_storage_pattern():
    """Test 4: Database Storage Pattern - verify how conversations are stored"""
    print("\n" + "="*80)
    print("💾 TEST 4: DATABASE STORAGE PATTERN")
    print("="*80)
    
    # Get current conversations for baseline
    response = make_authenticated_request('GET', '/conversations')
    if not response or response.status_code != 200:
        log_test_result("Database Pattern Setup", False, "Failed to get conversations")
        return False
    
    initial_conversations = response.json()
    initial_count = len(initial_conversations)
    
    print(f"📊 Initial database state: {initial_count} conversations")
    
    # Generate a conversation
    print("🔄 Generating conversation to analyze storage pattern...")
    response = make_authenticated_request('POST', '/conversation/generate', timeout=120)
    
    if not response or response.status_code != 200:
        log_test_result("Database Pattern Generation", False, "Failed to generate conversation")
        return False
    
    # Check database state after generation
    response = make_authenticated_request('GET', '/conversations')
    if not response or response.status_code != 200:
        log_test_result("Database Pattern Analysis", False, "Failed to get conversations after generation")
        return False
    
    final_conversations = response.json()
    final_count = len(final_conversations)
    new_conversations = final_count - initial_count
    
    print(f"📈 Final database state: {final_count} conversations ({new_conversations} new)")
    
    storage_analysis = {
        "conversations_created": new_conversations,
        "storage_pattern": "unknown"
    }
    
    if new_conversations == 1:
        # Single conversation with multiple messages
        latest_conversation = final_conversations[-1]
        messages = latest_conversation.get('messages', [])
        message_count = len(messages)
        
        storage_analysis["storage_pattern"] = "single_conversation_multiple_messages"
        storage_analysis["message_count"] = message_count
        
        log_test_result("Database Storage Pattern", True, f"Single conversation with {message_count} messages")
        
        # Check if messages have incremental timestamps or creation pattern
        if len(messages) > 1:
            timestamps = []
            for msg in messages:
                if 'timestamp' in msg:
                    timestamps.append(msg['timestamp'])
            
            if len(timestamps) > 1:
                unique_timestamps = len(set(timestamps))
                if unique_timestamps == 1:
                    print("⚠️  All messages have identical timestamps - bulk storage detected")
                    storage_analysis["bulk_storage"] = True
                else:
                    print(f"✅ Messages have {unique_timestamps} different timestamps - incremental storage")
                    storage_analysis["bulk_storage"] = False
    
    elif new_conversations > 1:
        # Multiple conversations created
        storage_analysis["storage_pattern"] = "multiple_conversations"
        
        total_messages = 0
        for conv in final_conversations[-new_conversations:]:
            total_messages += len(conv.get('messages', []))
        
        storage_analysis["total_messages"] = total_messages
        
        log_test_result("Database Storage Pattern", True, f"{new_conversations} conversations with {total_messages} total messages")
    
    else:
        log_test_result("Database Storage Pattern", False, "No new conversations created")
        return False
    
    test_results["timing_data"]["database_storage"] = storage_analysis
    
    # Additional check: Look for conversation metadata that might indicate progressive vs bulk creation
    if new_conversations > 0:
        latest_conversation = final_conversations[-1]
        
        # Check for round numbers, time periods, etc.
        round_number = latest_conversation.get('round_number')
        time_period = latest_conversation.get('time_period')
        created_at = latest_conversation.get('created_at')
        
        print(f"📋 Conversation metadata:")
        print(f"   Round number: {round_number}")
        print(f"   Time period: {time_period}")
        print(f"   Created at: {created_at}")
        
        # Check if this indicates incremental vs bulk processing
        if round_number and round_number > 1:
            print("✅ Round number > 1 suggests incremental conversation system")
        
    return True

def run_conversation_timing_tests():
    """Run all conversation timing tests"""
    print("🕐 CONVERSATION GENERATION TIMING ISSUES TESTING")
    print("=" * 80)
    print("Investigating backend issues causing:")
    print("- 10 messages appearing at once instead of progressive display")
    print("- Long delays in play/pause operations")
    print("- Missing loading animations")
    print("=" * 80)
    
    # Run all tests
    test1_passed = test_conversation_generation_timing()
    test2_passed = test_simulation_control_performance()
    test3_passed = test_progressive_message_display()
    test4_passed = test_database_storage_pattern()
    
    # Print detailed timing analysis
    print("\n" + "="*80)
    print("📊 TIMING ANALYSIS SUMMARY")
    print("="*80)
    
    timing_data = test_results["timing_data"]
    
    # Conversation generation analysis
    if "Conversation Generation Timing" in timing_data:
        gen_data = timing_data["Conversation Generation Timing"]
        gen_time = gen_data.get("generation_time_seconds", 0)
        messages_count = gen_data.get("messages_in_latest_conversation", 0)
        bulk_creation = gen_data.get("bulk_creation_detected", False)
        
        print(f"🕐 Conversation Generation:")
        print(f"   Time: {gen_time:.2f} seconds")
        print(f"   Messages: {messages_count}")
        print(f"   Bulk creation: {'Yes' if bulk_creation else 'No'}")
        
        if gen_time > 30:
            print("   ⚠️  ISSUE: Long generation time may cause bulk display")
        if bulk_creation:
            print("   ⚠️  ISSUE: Bulk creation detected - explains '10 messages at once'")
    
    # Simulation control analysis
    if "simulation_control" in timing_data:
        sim_data = timing_data["simulation_control"]
        slow_ops = sim_data.get("slow_operations", [])
        
        print(f"⏯️  Simulation Control:")
        print(f"   Start: {sim_data.get('start_time', 0):.2f}s")
        print(f"   Pause: {sim_data.get('pause_time', 0):.2f}s")
        print(f"   Resume: {sim_data.get('resume_time', 0):.2f}s")
        
        if slow_ops:
            print(f"   ⚠️  ISSUE: Slow operations - {', '.join(slow_ops)}")
    
    # Database storage analysis
    if "database_storage" in timing_data:
        db_data = timing_data["database_storage"]
        pattern = db_data.get("storage_pattern", "unknown")
        bulk_storage = db_data.get("bulk_storage", False)
        
        print(f"💾 Database Storage:")
        print(f"   Pattern: {pattern}")
        print(f"   Bulk storage: {'Yes' if bulk_storage else 'No'}")
        
        if bulk_storage:
            print("   ⚠️  ISSUE: Bulk storage explains progressive display problems")
    
    # Overall test results
    print(f"\n📈 Test Results:")
    print(f"   ✅ Passed: {test_results['passed']}")
    print(f"   ❌ Failed: {test_results['failed']}")
    print(f"   📊 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    # Root cause analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    
    issues_found = []
    
    # Check for bulk message creation
    if timing_data.get("Conversation Generation Timing", {}).get("bulk_creation_detected"):
        issues_found.append("Bulk message creation - all messages created simultaneously")
    
    # Check for slow generation
    gen_time = timing_data.get("Conversation Generation Timing", {}).get("generation_time_seconds", 0)
    if gen_time > 30:
        issues_found.append(f"Slow generation ({gen_time:.1f}s) - causes long waits before bulk display")
    
    # Check for slow simulation controls
    slow_ops = timing_data.get("simulation_control", {}).get("slow_operations", [])
    if slow_ops:
        issues_found.append(f"Slow simulation controls - {', '.join(slow_ops)}")
    
    # Check for bulk database storage
    if timing_data.get("database_storage", {}).get("bulk_storage"):
        issues_found.append("Bulk database storage - no progressive message saving")
    
    if issues_found:
        print("   ❌ ISSUES IDENTIFIED:")
        for i, issue in enumerate(issues_found, 1):
            print(f"      {i}. {issue}")
    else:
        print("   ✅ No major timing issues detected")
    
    print("\n" + "="*80)
    
    return all([test1_passed, test2_passed, test3_passed, test4_passed])

if __name__ == "__main__":
    success = run_conversation_timing_tests()
    sys.exit(0 if success else 1)