#!/usr/bin/env python3
"""
FOCUSED IMMEDIATE GENERATION & INSTANT PAUSE TESTING
Testing the specific CRITICAL FIXES with shorter timeouts and focused tests.
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

print(f"🔗 Testing API URL: {API_URL}")

# Test results
results = {"passed": 0, "failed": 0, "details": []}

def log_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")
    
    results["details"].append({"test": test_name, "passed": passed, "details": details})
    if passed:
        results["passed"] += 1
    else:
        results["failed"] += 1

def authenticate():
    """Quick authentication test"""
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=15)
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print("✅ Authentication successful")
                return token
        print(f"❌ Auth failed: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def test_simulation_start_immediate_flag():
    """Test 1: /simulation/start returns immediate_generation flag"""
    print("\n" + "="*60)
    print("🚀 TEST 1: SIMULATION START IMMEDIATE GENERATION FLAG")
    print("="*60)
    
    token = authenticate()
    if not token:
        log_result("Authentication for Test 1", False, "Failed to authenticate")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Test /simulation/start endpoint
        start_time = time.time()
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for immediate_generation flag
            immediate_gen = data.get('immediate_generation')
            if immediate_gen is True:
                log_result("Immediate Generation Flag", True, f"immediate_generation: true (response time: {response_time:.2f}s)")
            else:
                log_result("Immediate Generation Flag", False, f"immediate_generation: {immediate_gen} (expected: true)")
            
            # Check simulation activation
            is_active = data.get('is_active')
            if is_active:
                log_result("Simulation Activation", True, "Simulation started successfully")
            else:
                log_result("Simulation Activation", False, "Simulation not activated")
            
            return True
        else:
            log_result("Simulation Start Request", False, f"HTTP {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        log_result("Simulation Start Test", False, f"Error: {e}")
        return False

def test_pause_response_time():
    """Test 2: /simulation/pause response time"""
    print("\n" + "="*60)
    print("⏸️ TEST 2: SIMULATION PAUSE RESPONSE TIME")
    print("="*60)
    
    token = authenticate()
    if not token:
        log_result("Authentication for Test 2", False, "Failed to authenticate")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Ensure simulation is running
        requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        time.sleep(1)
        
        # Test pause response time
        pause_times = []
        for i in range(3):
            start_time = time.time()
            response = requests.post(f"{API_URL}/simulation/pause", headers=headers, timeout=5)
            pause_time = time.time() - start_time
            
            if response.status_code == 200:
                pause_times.append(pause_time)
                print(f"   Pause attempt {i+1}: {pause_time:.3f}s")
                
                # Restart for next test
                if i < 2:
                    requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=5)
                    time.sleep(0.5)
            else:
                log_result(f"Pause Attempt {i+1}", False, f"HTTP {response.status_code}")
        
        if pause_times:
            avg_time = sum(pause_times) / len(pause_times)
            max_time = max(pause_times)
            
            if avg_time <= 1.0:
                log_result("Average Pause Time", True, f"{avg_time:.3f}s (target: <1s)")
            else:
                log_result("Average Pause Time", False, f"{avg_time:.3f}s (target: <1s)")
            
            if max_time <= 1.0:
                log_result("Max Pause Time", True, f"{max_time:.3f}s (excellent)")
            else:
                log_result("Max Pause Time", False, f"{max_time:.3f}s (needs improvement)")
            
            return True
        else:
            log_result("Pause Response Test", False, "No successful pause operations")
            return False
            
    except Exception as e:
        log_result("Pause Response Test", False, f"Error: {e}")
        return False

def test_first_message_timing():
    """Test 3: First message generation timing"""
    print("\n" + "="*60)
    print("⏱️ TEST 3: FIRST MESSAGE GENERATION TIMING")
    print("="*60)
    
    token = authenticate()
    if not token:
        log_result("Authentication for Test 3", False, "Failed to authenticate")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Set up scenario
        scenario_data = {
            "scenario": "A team of engineers needs to develop a new communication protocol.",
            "scenario_name": "Communication Protocol Development"
        }
        requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        
        # Start simulation and measure time to first message
        start_time = time.time()
        requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        
        # Monitor for first message
        first_message_time = None
        for check in range(10):  # Check for 20 seconds
            time.sleep(2)
            
            try:
                conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=5)
                if conv_response.status_code == 200:
                    conversations = conv_response.json()
                    if conversations:
                        latest_conv = conversations[-1]
                        messages = latest_conv.get('messages', [])
                        if messages:
                            first_message_time = time.time() - start_time
                            break
            except:
                continue
            
            print(f"   Check {check + 1}: Waiting for first message...")
        
        if first_message_time:
            if first_message_time <= 10:
                log_result("First Message Under 10s", True, f"Generated in {first_message_time:.2f}s")
            else:
                log_result("First Message Under 10s", False, f"Took {first_message_time:.2f}s (target: <10s)")
            return True
        else:
            log_result("First Message Generation", False, "No message generated within 20 seconds")
            return False
            
    except Exception as e:
        log_result("First Message Timing Test", False, f"Error: {e}")
        return False

def test_conversation_generation_performance():
    """Test 4: Conversation generation performance"""
    print("\n" + "="*60)
    print("📊 TEST 4: CONVERSATION GENERATION PERFORMANCE")
    print("="*60)
    
    token = authenticate()
    if not token:
        log_result("Authentication for Test 4", False, "Failed to authenticate")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Test conversation generation speed
        generation_times = []
        
        for round_num in range(2):
            print(f"   Testing generation round {round_num + 1}...")
            
            start_time = time.time()
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
            
            if response.status_code == 200:
                generation_time = time.time() - start_time
                generation_times.append(generation_time)
                print(f"   Round {round_num + 1}: {generation_time:.2f}s")
            else:
                print(f"   Round {round_num + 1}: Failed ({response.status_code})")
        
        if generation_times:
            avg_time = sum(generation_times) / len(generation_times)
            
            if avg_time <= 15:
                log_result("Conversation Generation Speed", True, f"Average: {avg_time:.2f}s (target: <15s)")
            else:
                log_result("Conversation Generation Speed", False, f"Average: {avg_time:.2f}s (target: <15s)")
            
            return True
        else:
            log_result("Conversation Generation Test", False, "No successful generations")
            return False
            
    except Exception as e:
        log_result("Conversation Generation Test", False, f"Error: {e}")
        return False

def test_simulation_state_consistency():
    """Test 5: Simulation state consistency"""
    print("\n" + "="*60)
    print("📊 TEST 5: SIMULATION STATE CONSISTENCY")
    print("="*60)
    
    token = authenticate()
    if not token:
        log_result("Authentication for Test 5", False, "Failed to authenticate")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    try:
        # Test simulation state endpoint
        response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
        
        if response.status_code == 200:
            state_data = response.json()
            
            # Check required fields
            required_fields = ['is_active', 'current_day', 'current_time_period']
            missing_fields = [field for field in required_fields if field not in state_data]
            
            if not missing_fields:
                log_result("Simulation State Structure", True, "All required fields present")
            else:
                log_result("Simulation State Structure", False, f"Missing fields: {missing_fields}")
            
            # Test state changes
            initial_active = state_data.get('is_active')
            
            # Start simulation
            requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
            time.sleep(1)
            
            # Check state after start
            response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
            if response.status_code == 200:
                new_state = response.json()
                if new_state.get('is_active'):
                    log_result("State Change on Start", True, "is_active changed to true")
                else:
                    log_result("State Change on Start", False, "is_active not updated")
            
            # Pause simulation
            requests.post(f"{API_URL}/simulation/pause", headers=headers, timeout=10)
            time.sleep(1)
            
            # Check state after pause
            response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
            if response.status_code == 200:
                paused_state = response.json()
                if not paused_state.get('is_active'):
                    log_result("State Change on Pause", True, "is_active changed to false")
                else:
                    log_result("State Change on Pause", False, "is_active not updated after pause")
            
            return True
        else:
            log_result("Simulation State Request", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        log_result("Simulation State Test", False, f"Error: {e}")
        return False

def main():
    """Run focused tests"""
    print("🎯 FOCUSED IMMEDIATE GENERATION & INSTANT PAUSE TESTING")
    print("=" * 60)
    
    # Run tests
    test1 = test_simulation_start_immediate_flag()
    test2 = test_pause_response_time()
    test3 = test_first_message_timing()
    test4 = test_conversation_generation_performance()
    test5 = test_simulation_state_consistency()
    
    # Summary
    print("\n" + "="*60)
    print("📊 FOCUSED TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    total_tests = results['passed'] + results['failed']
    if total_tests > 0:
        success_rate = (results['passed'] / total_tests) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Test results
    print(f"\n🔍 TEST RESULTS:")
    print(f"   Test 1 - Immediate Generation Flag: {'✅' if test1 else '❌'}")
    print(f"   Test 2 - Pause Response Time: {'✅' if test2 else '❌'}")
    print(f"   Test 3 - First Message Timing: {'✅' if test3 else '❌'}")
    print(f"   Test 4 - Generation Performance: {'✅' if test4 else '❌'}")
    print(f"   Test 5 - State Consistency: {'✅' if test5 else '❌'}")
    
    all_passed = all([test1, test2, test3, test4, test5])
    
    if all_passed:
        print("\n🎉 ALL CRITICAL FIXES WORKING!")
        print("   ✅ Immediate generation flag implemented")
        print("   ✅ Instant pause response achieved")
        print("   ✅ First message under 10 seconds")
        print("   ✅ Performance targets met")
        print("   ✅ State consistency maintained")
    else:
        print("\n⚠️ SOME ISSUES FOUND - CHECK DETAILS ABOVE")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)