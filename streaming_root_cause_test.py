#!/usr/bin/env python3
"""
PROGRESSIVE STREAMING ROOT CAUSE VERIFICATION TEST
Quick test to verify the root cause of progressive streaming breakdown.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import threading
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

auth_token = None

def authenticate():
    global auth_token
    if auth_token:
        return True
    
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            auth_token = response.json().get("access_token")
            return auth_token is not None
    except:
        pass
    return False

def make_request(method, endpoint, data=None, timeout=30):
    if not authenticate():
        return None
        
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    url = f"{API_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            return requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            return requests.post(url, headers=headers, json=data, timeout=timeout)
    except:
        return None

def test_progressive_streaming_root_cause():
    """Test to verify the root cause of progressive streaming breakdown"""
    print("🔍 PROGRESSIVE STREAMING ROOT CAUSE VERIFICATION")
    print("="*60)
    
    # Step 1: Clear baseline and start monitoring
    print("\n📊 Step 1: Getting baseline message count...")
    baseline_response = make_request('GET', '/messages/stream')
    baseline_count = 0
    if baseline_response and baseline_response.status_code == 200:
        baseline_count = baseline_response.json().get('count', 0)
        print(f"   Baseline: {baseline_count} messages")
    
    # Step 2: Start conversation generation and monitor stream in real-time
    print("\n⚡ Step 2: Starting conversation generation with real-time monitoring...")
    
    stream_timeline = []
    generation_complete = False
    
    def monitor_stream():
        """Monitor message stream every 2 seconds"""
        nonlocal stream_timeline, generation_complete
        start_time = time.time()
        
        while not generation_complete:
            current_time = time.time() - start_time
            
            response = make_request('GET', '/messages/stream', timeout=5)
            if response and response.status_code == 200:
                data = response.json()
                message_count = data.get('count', 0)
                new_messages = message_count - baseline_count
                
                stream_timeline.append({
                    'time': current_time,
                    'total_count': message_count,
                    'new_messages': new_messages
                })
                
                print(f"   [{current_time:5.1f}s] Stream messages: {new_messages} new")
            
            time.sleep(2)
    
    def generate_conversation():
        """Generate conversation and track completion"""
        nonlocal generation_complete
        print("   🔄 Starting conversation generation...")
        start_time = time.time()
        
        response = make_request('POST', '/conversation/generate', timeout=120)
        
        end_time = time.time()
        generation_time = end_time - start_time
        generation_complete = True
        
        if response and response.status_code == 200:
            print(f"   ✅ Generation completed in {generation_time:.2f}s")
            return True
        else:
            print(f"   ❌ Generation failed")
            return False
    
    # Start monitoring and generation
    monitor_thread = threading.Thread(target=monitor_stream)
    generation_thread = threading.Thread(target=generate_conversation)
    
    monitor_thread.start()
    generation_thread.start()
    
    generation_thread.join()
    generation_complete = True
    monitor_thread.join()
    
    # Step 3: Analyze the timeline to confirm root cause
    print(f"\n📊 Step 3: Analyzing timeline to confirm root cause...")
    
    if not stream_timeline:
        print("   ❌ No timeline data collected")
        return False
    
    # Find when messages first appeared
    first_message_time = None
    message_events = []
    
    for entry in stream_timeline:
        if entry['new_messages'] > 0:
            if first_message_time is None:
                first_message_time = entry['time']
            message_events.append(entry)
    
    if first_message_time is None:
        print("   ❌ NO MESSAGES DETECTED: Stream never populated")
        return False
    
    print(f"   🎯 First messages appeared at: {first_message_time:.1f}s")
    
    # Check if messages appeared progressively or all at once
    if len(message_events) == 1:
        print("   ❌ BATCH BEHAVIOR CONFIRMED: All messages appeared at once")
        print("   🔍 ROOT CAUSE: asyncio.gather() waits for ALL agents before saving ANY messages")
        return True  # We confirmed the root cause
    else:
        # Check intervals between message appearances
        intervals = []
        for i in range(1, len(message_events)):
            if message_events[i]['new_messages'] > message_events[i-1]['new_messages']:
                interval = message_events[i]['time'] - message_events[i-1]['time']
                intervals.append(interval)
        
        if intervals and min(intervals) < 10:
            print("   ✅ PROGRESSIVE BEHAVIOR: Messages appeared with intervals")
            print("   🤔 Unexpected: Progressive streaming appears to be working")
            return False
        else:
            print("   ❌ BATCH BEHAVIOR: Long intervals suggest batch processing")
            print("   🔍 ROOT CAUSE: asyncio.gather() waits for ALL agents before saving ANY messages")
            return True

if __name__ == "__main__":
    success = test_progressive_streaming_root_cause()
    print(f"\n{'✅ ROOT CAUSE CONFIRMED' if success else '❌ UNEXPECTED RESULTS'}")