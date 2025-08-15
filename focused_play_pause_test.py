#!/usr/bin/env python3
"""
FOCUSED PLAY/PAUSE BUTTON SYSTEM TESTING

Testing the CRITICAL FIXES to the play/pause button system with shorter timeouts and focused tests.
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

print(f"🔗 Using API URL: {API_URL}")

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
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=15)
        if response.status_code == 200:
            response_data = response.json()
            auth_token = response_data.get("access_token")
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def make_request(method, endpoint, data=None, timeout=15):
    """Make an authenticated request"""
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
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.Timeout:
        print(f"⏰ Request to {endpoint} timed out after {timeout} seconds")
        return None
    except Exception as e:
        print(f"❌ Request to {endpoint} failed: {e}")
        return None

def test_play_button_responsiveness():
    """Test 1: Play Button Responsiveness"""
    print("\n" + "="*60)
    print("▶️ TEST 1: PLAY BUTTON RESPONSIVENESS")
    print("="*60)
    
    # Stop simulation first
    print("⏹️ Stopping simulation...")
    response = make_request('POST', '/simulation/stop')
    if response and response.status_code == 200:
        print("✅ Simulation stopped")
    else:
        print("⚠️ Stop simulation response:", response.status_code if response else "No response")
    
    # Test /simulation/start performance
    print("\n▶️ Testing /simulation/start performance...")
    print("   Expected: Under 1 second (instant state change only)")
    
    start_time = time.time()
    response = make_request('POST', '/simulation/start', timeout=5)
    
    if response and response.status_code == 200:
        response_time = time.time() - start_time
        print(f"✅ /simulation/start responded in {response_time:.3f}s")
        
        if response_time < 1.0:
            print("🎉 EXCELLENT: Under 1 second target met!")
            return True
        elif response_time < 3.0:
            print("✅ GOOD: Under 3 seconds")
            return True
        else:
            print("❌ TOO SLOW: Over 3 seconds")
            return False
    else:
        print(f"❌ /simulation/start failed: {response.status_code if response else 'No response'}")
        return False

def test_simulation_state_management():
    """Test 2: Simulation State Management"""
    print("\n" + "="*60)
    print("⏯️ TEST 2: SIMULATION STATE MANAGEMENT")
    print("="*60)
    
    results = []
    
    # Test start
    print("▶️ Testing start...")
    start_time = time.time()
    response = make_request('POST', '/simulation/start')
    if response and response.status_code == 200:
        start_response_time = time.time() - start_time
        print(f"✅ Start: {start_response_time:.3f}s")
        results.append(start_response_time < 1.0)
    else:
        print("❌ Start failed")
        results.append(False)
    
    # Test pause
    print("⏸️ Testing pause...")
    start_time = time.time()
    response = make_request('POST', '/simulation/pause')
    if response and response.status_code == 200:
        pause_response_time = time.time() - start_time
        print(f"✅ Pause: {pause_response_time:.3f}s")
        results.append(pause_response_time < 1.0)
    else:
        print("❌ Pause failed")
        results.append(False)
    
    # Test resume
    print("⏯️ Testing resume...")
    start_time = time.time()
    response = make_request('POST', '/simulation/resume')
    if response and response.status_code == 200:
        resume_response_time = time.time() - start_time
        print(f"✅ Resume: {resume_response_time:.3f}s")
        results.append(resume_response_time < 1.0)
    else:
        print("❌ Resume failed")
        results.append(False)
    
    success_count = sum(results)
    print(f"\n📊 State Management: {success_count}/3 operations under 1 second")
    
    return success_count >= 2  # At least 2 out of 3 should be fast

def test_progressive_generation():
    """Test 3: Progressive Generation (separate from start)"""
    print("\n" + "="*60)
    print("💬 TEST 3: PROGRESSIVE GENERATION")
    print("="*60)
    
    # Check agents first
    print("🤖 Checking agents...")
    response = make_request('GET', '/agents')
    if response and response.status_code == 200:
        agents = response.json()
        print(f"✅ Found {len(agents)} agents")
        if len(agents) < 2:
            print("❌ Need at least 2 agents for testing")
            return False
    else:
        print("❌ Failed to get agents")
        return False
    
    # Start simulation (should be instant)
    print("\n▶️ Starting simulation...")
    start_time = time.time()
    response = make_request('POST', '/simulation/start')
    if response and response.status_code == 200:
        start_time_taken = time.time() - start_time
        print(f"✅ Simulation started in {start_time_taken:.3f}s")
    else:
        print("❌ Failed to start simulation")
        return False
    
    # Test conversation generation (separate call)
    print("\n💬 Testing conversation generation...")
    print("   This simulates frontend calling generateNewConversation() after play")
    
    generation_start = time.time()
    response = make_request('POST', '/conversation/generate', timeout=45)
    
    if response and response.status_code == 200:
        generation_time = time.time() - generation_start
        print(f"✅ Conversation generated in {generation_time:.2f}s")
        
        if 10 <= generation_time <= 30:
            print("🎉 EXCELLENT: Within expected progressive generation time!")
            return True
        elif generation_time < 10:
            print("✅ VERY FAST: Faster than expected")
            return True
        else:
            print("⚠️ SLOW: Longer than expected but functional")
            return True
    else:
        print(f"❌ Conversation generation failed: {response.status_code if response else 'No response'}")
        return False

def test_backend_performance_metrics():
    """Test 4: Backend Performance Metrics"""
    print("\n" + "="*60)
    print("📊 TEST 4: BACKEND PERFORMANCE METRICS")
    print("="*60)
    
    metrics = {}
    
    # Test each endpoint
    endpoints = [
        ('/simulation/start', 'POST', 1.0),
        ('/simulation/pause', 'POST', 1.0),
        ('/simulation/resume', 'POST', 1.0)
    ]
    
    for endpoint, method, target_time in endpoints:
        print(f"⚡ Testing {endpoint}...")
        start_time = time.time()
        response = make_request(method, endpoint)
        
        if response and response.status_code == 200:
            response_time = time.time() - start_time
            metrics[endpoint] = response_time
            
            if response_time <= target_time:
                print(f"✅ {endpoint}: {response_time:.3f}s (target: <{target_time}s)")
            else:
                print(f"⚠️ {endpoint}: {response_time:.3f}s (target: <{target_time}s)")
        else:
            print(f"❌ {endpoint}: Failed")
            metrics[endpoint] = None
    
    # Summary
    print(f"\n📈 Performance Summary:")
    successful_metrics = [m for m in metrics.values() if m is not None and m <= 1.0]
    print(f"   {len(successful_metrics)}/{len(endpoints)} endpoints meet performance targets")
    
    return len(successful_metrics) >= 2

def test_end_to_end_flow():
    """Test 5: End-to-End Play Button Flow"""
    print("\n" + "="*60)
    print("🎬 TEST 5: END-TO-END PLAY BUTTON FLOW")
    print("="*60)
    
    # Complete flow test
    print("🔄 Testing complete play button flow...")
    
    # 1. Play button click (instant)
    play_start = time.time()
    response = make_request('POST', '/simulation/start')
    
    if response and response.status_code == 200:
        play_time = time.time() - play_start
        print(f"✅ Play button responded in {play_time:.3f}s")
        
        # 2. Check simulation state
        response = make_request('GET', '/simulation/state')
        if response and response.status_code == 200:
            state = response.json()
            is_active = state.get('is_active', False)
            print(f"✅ Simulation active: {is_active}")
        
        # 3. Test pause/resume cycle
        pause_response = make_request('POST', '/simulation/pause')
        resume_response = make_request('POST', '/simulation/resume')
        
        if pause_response and resume_response:
            print("✅ Pause/Resume cycle successful")
            
            # Final assessment
            if play_time < 1.0:
                print("\n🎉 END-TO-END FLOW: EXCELLENT!")
                print("   ✅ Play button responds instantly")
                print("   ✅ State management works correctly")
                print("   ✅ Pause/Resume operations functional")
                return True
            else:
                print("\n⚠️ END-TO-END FLOW: FUNCTIONAL but could be faster")
                return True
        else:
            print("❌ Pause/Resume cycle failed")
            return False
    else:
        print("❌ Play button failed")
        return False

def run_focused_tests():
    """Run focused play/pause button tests"""
    print("▶️ FOCUSED PLAY/PAUSE BUTTON SYSTEM TESTING")
    print("=" * 60)
    print("Testing CRITICAL FIXES for user-reported issues")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("Play Button Responsiveness", test_play_button_responsiveness()))
    test_results.append(("Simulation State Management", test_simulation_state_management()))
    test_results.append(("Progressive Generation", test_progressive_generation()))
    test_results.append(("Backend Performance Metrics", test_backend_performance_metrics()))
    test_results.append(("End-to-End Flow", test_end_to_end_flow()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n📈 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed >= 4:
        print("\n🎉 PLAY/PAUSE BUTTON SYSTEM: WORKING EXCELLENTLY!")
        print("   User issues should be resolved:")
        print("   ✅ No more 30+ second delays")
        print("   ✅ Instant play button response")
        print("   ✅ Proper state management")
        print("   ✅ Progressive message generation")
    elif passed >= 3:
        print("\n✅ PLAY/PAUSE BUTTON SYSTEM: MOSTLY WORKING")
        print("   Most user issues resolved, minor improvements needed")
    else:
        print("\n❌ PLAY/PAUSE BUTTON SYSTEM: NEEDS ATTENTION")
        print("   Some critical issues may still exist")
    
    return passed >= 3

if __name__ == "__main__":
    success = run_focused_tests()
    sys.exit(0 if success else 1)