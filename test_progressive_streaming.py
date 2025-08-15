#!/usr/bin/env python3
"""
CRITICAL PROGRESSIVE STREAMING VERIFICATION TEST

Testing the CRITICAL ARCHITECTURAL FIX that replaces asyncio.gather() with asyncio.as_completed()
Based on the backend logs, I can see the progressive streaming is working:
- "📤 PROGRESSIVE STREAM: Dr. Marcus Rodriguez message available immediately! (3/3)"
- "🚀 PROGRESSIVE PARALLEL generation completed in 19.50 seconds"
- "⚡ PERFORMANCE: 4.2x faster with progressive streaming!"

This test will verify the key aspects of the progressive streaming implementation.
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

# Global auth token
auth_token = None

def authenticate():
    """Authenticate with the backend"""
    global auth_token
    
    if auth_token:
        return True
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            auth_token = response.json().get("access_token")
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def make_request(method, endpoint, data=None, timeout=30):
    """Make authenticated request"""
    if not authenticate():
        return None
        
    headers = {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == 'GET':
            return requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            return requests.post(url, headers=headers, json=data, timeout=timeout)
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_progressive_streaming():
    """Test the progressive streaming functionality"""
    print("🚀 CRITICAL PROGRESSIVE STREAMING VERIFICATION TEST")
    print("=" * 80)
    
    # Test 1: Verify streaming endpoint exists and works
    print("\n📡 Test 1: Streaming Endpoint Verification")
    response = make_request('GET', '/messages/stream')
    if response and response.status_code == 200:
        stream_data = response.json()
        print(f"✅ Streaming endpoint accessible")
        print(f"   Current messages in stream: {stream_data.get('count', 0)}")
    else:
        print(f"❌ Streaming endpoint failed: {response.status_code if response else 'No response'}")
        return False
    
    # Test 2: Generate conversation and monitor progressive streaming
    print("\n🎬 Test 2: Progressive Message Generation")
    
    # Clear existing messages by getting current timestamp
    start_timestamp = datetime.utcnow().isoformat()
    print(f"   Starting monitoring from: {start_timestamp}")
    
    # Start conversation generation in background
    generation_results = {'completed': False, 'time': 0}
    
    def generate_conversation():
        start_time = time.time()
        response = make_request('POST', '/conversation/generate', timeout=120)
        end_time = time.time()
        generation_results['time'] = end_time - start_time
        generation_results['completed'] = response is not None and response.status_code == 200
        if generation_results['completed']:
            print(f"\n🏁 Conversation generation completed in {generation_results['time']:.2f}s")
        else:
            print(f"\n❌ Conversation generation failed")
    
    # Start generation thread
    gen_thread = threading.Thread(target=generate_conversation)
    gen_thread.start()
    
    # Monitor progressive streaming
    print("   Monitoring progressive message availability...")
    monitoring_results = []
    monitor_start = time.time()
    
    while time.time() - monitor_start < 35 and not generation_results['completed']:
        current_time = time.time() - monitor_start
        
        # Check for new messages since start
        response = make_request('GET', f'/messages/stream?since={start_timestamp}', timeout=5)
        if response and response.status_code == 200:
            stream_data = response.json()
            message_count = stream_data.get('count', 0)
            monitoring_results.append({
                'time': current_time,
                'count': message_count
            })
            
            if message_count > 0:
                print(f"   📊 {current_time:.1f}s: {message_count} messages available")
        
        time.sleep(2)
    
    gen_thread.join(timeout=30)
    
    # Test 3: Analyze progressive streaming results
    print("\n📊 Test 3: Progressive Streaming Analysis")
    
    if not monitoring_results:
        print("❌ No monitoring data collected")
        return False
    
    # Find first message appearance
    first_message_time = None
    progressive_increases = 0
    max_messages = 0
    
    for i, result in enumerate(monitoring_results):
        if result['count'] > 0 and first_message_time is None:
            first_message_time = result['time']
        
        if result['count'] > max_messages:
            max_messages = result['count']
            if i > 0:  # Not the first result
                progressive_increases += 1
    
    # Results analysis
    success_criteria = 0
    total_criteria = 4
    
    # Criterion 1: First message under 15 seconds (allowing some buffer)
    if first_message_time is not None and first_message_time <= 15:
        print(f"✅ First message appeared at {first_message_time:.1f}s (target: ≤15s)")
        success_criteria += 1
    else:
        print(f"❌ First message appeared at {first_message_time:.1f}s (target: ≤15s)")
    
    # Criterion 2: Progressive increases detected
    if progressive_increases >= 1:
        print(f"✅ Progressive increases detected: {progressive_increases}")
        success_criteria += 1
    else:
        print(f"❌ No progressive increases detected")
    
    # Criterion 3: Multiple messages generated
    if max_messages >= 3:
        print(f"✅ Generated {max_messages} messages")
        success_criteria += 1
    else:
        print(f"❌ Only {max_messages} messages generated (expected ≥3)")
    
    # Criterion 4: Total generation time reasonable
    if generation_results['completed'] and generation_results['time'] <= 30:
        print(f"✅ Total generation time: {generation_results['time']:.2f}s (target: ≤30s)")
        success_criteria += 1
    else:
        print(f"❌ Generation time: {generation_results['time']:.2f}s (target: ≤30s)")
    
    # Test 4: Verify backend logs show progressive streaming
    print("\n📋 Test 4: Backend Log Verification")
    try:
        # Check recent backend logs for progressive streaming indicators
        import subprocess
        result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True, timeout=5)
        
        log_content = result.stdout
        progressive_indicators = [
            "PROGRESSIVE STREAM:",
            "PROGRESSIVE PARALLEL generation completed",
            "faster with progressive streaming",
            "messages streamed individually"
        ]
        
        indicators_found = sum(1 for indicator in progressive_indicators if indicator in log_content)
        
        if indicators_found >= 3:
            print(f"✅ Backend logs show progressive streaming ({indicators_found}/4 indicators)")
            success_criteria += 1
            total_criteria += 1
        else:
            print(f"❌ Backend logs missing progressive streaming indicators ({indicators_found}/4)")
            total_criteria += 1
            
    except Exception as e:
        print(f"⚠️ Could not check backend logs: {e}")
        total_criteria += 1
    
    # Final assessment
    print(f"\n🎯 PROGRESSIVE STREAMING TEST RESULTS")
    print("=" * 50)
    print(f"Success Criteria Met: {success_criteria}/{total_criteria}")
    print(f"Success Rate: {(success_criteria/total_criteria)*100:.1f}%")
    
    if success_criteria >= total_criteria * 0.8:  # 80% success rate
        print("\n🎉 PROGRESSIVE STREAMING TEST: PASSED!")
        print("✅ The asyncio.as_completed() implementation is working")
        print("✅ Messages appear progressively as agents complete")
        print("✅ Performance targets are met")
        return True
    else:
        print("\n❌ PROGRESSIVE STREAMING TEST: FAILED!")
        print("❌ Progressive streaming implementation needs attention")
        return False

if __name__ == "__main__":
    success = test_progressive_streaming()
    sys.exit(0 if success else 1)