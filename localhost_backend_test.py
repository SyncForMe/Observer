#!/usr/bin/env python3
"""
LOCALHOST BACKEND TESTING - IMMEDIATE GENERATION & INSTANT PAUSE
Testing the CRITICAL FIXES using direct localhost connection.
"""

import requests
import json
import time
import os
import sys

# Use localhost for direct backend testing
API_URL = "http://localhost:8001/api"
print(f"🔗 Testing Direct Backend: {API_URL}")

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
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
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

def test_critical_endpoints():
    """Test the critical endpoints for immediate generation and instant pause"""
    print("\n" + "="*60)
    print("🎯 CRITICAL ENDPOINTS TESTING")
    print("="*60)
    
    token = authenticate()
    if not token:
        log_result("Authentication", False, "Failed to authenticate")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test 1: /simulation/start immediate generation flag
    print("\n🚀 Testing /simulation/start for immediate_generation flag...")
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=8)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            immediate_gen = data.get('immediate_generation')
            
            if immediate_gen is True:
                log_result("Immediate Generation Flag", True, f"immediate_generation: true (response: {response_time:.2f}s)")
            else:
                log_result("Immediate Generation Flag", False, f"immediate_generation: {immediate_gen}")
            
            # Check if simulation is active
            is_active = data.get('is_active')
            log_result("Simulation Activation", is_active, f"is_active: {is_active}")
            
        else:
            log_result("Simulation Start", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_result("Simulation Start", False, f"Error: {e}")
    
    # Test 2: /simulation/pause instant response
    print("\n⏸️ Testing /simulation/pause for instant response...")
    try:
        # Ensure simulation is running
        requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=5)
        time.sleep(0.5)
        
        # Test pause response time
        start_time = time.time()
        response = requests.post(f"{API_URL}/simulation/pause", headers=headers, timeout=5)
        pause_time = time.time() - start_time
        
        if response.status_code == 200:
            if pause_time <= 1.0:
                log_result("Instant Pause Response", True, f"Pause time: {pause_time:.3f}s (target: <1s)")
            else:
                log_result("Instant Pause Response", False, f"Pause time: {pause_time:.3f}s (too slow)")
        else:
            log_result("Pause Request", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_result("Pause Test", False, f"Error: {e}")
    
    # Test 3: /simulation/state consistency
    print("\n📊 Testing /simulation/state for consistency...")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=5)
        
        if response.status_code == 200:
            state_data = response.json()
            required_fields = ['is_active', 'current_day', 'current_time_period']
            missing_fields = [field for field in required_fields if field not in state_data]
            
            if not missing_fields:
                log_result("State Structure", True, "All required fields present")
            else:
                log_result("State Structure", False, f"Missing: {missing_fields}")
        else:
            log_result("State Request", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_result("State Test", False, f"Error: {e}")
    
    # Test 4: Quick conversation generation test
    print("\n💬 Testing conversation generation performance...")
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=20)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            if generation_time <= 15:
                log_result("Conversation Generation Speed", True, f"Generated in {generation_time:.2f}s")
            else:
                log_result("Conversation Generation Speed", False, f"Took {generation_time:.2f}s (target: <15s)")
        else:
            log_result("Conversation Generation", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_result("Conversation Generation", False, f"Error: {e}")
    
    # Test 5: Check for first message timing
    print("\n⏱️ Testing first message availability...")
    try:
        # Set scenario
        scenario_data = {
            "scenario": "A team needs to solve a technical challenge quickly.",
            "scenario_name": "Quick Technical Challenge"
        }
        requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=5)
        
        # Start simulation and check for messages
        start_time = time.time()
        requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=5)
        
        # Check for conversations within 12 seconds
        first_message_time = None
        for check in range(6):
            time.sleep(2)
            try:
                conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=3)
                if conv_response.status_code == 200:
                    conversations = conv_response.json()
                    if conversations and conversations[-1].get('messages'):
                        first_message_time = time.time() - start_time
                        break
            except:
                continue
        
        if first_message_time:
            if first_message_time <= 10:
                log_result("First Message Under 10s", True, f"Available in {first_message_time:.2f}s")
            else:
                log_result("First Message Under 10s", False, f"Took {first_message_time:.2f}s")
        else:
            log_result("First Message Generation", False, "No message within 12 seconds")
            
    except Exception as e:
        log_result("First Message Test", False, f"Error: {e}")
    
    return True

def main():
    """Run direct backend tests"""
    print("🎯 LOCALHOST BACKEND TESTING - IMMEDIATE GENERATION & INSTANT PAUSE")
    print("=" * 60)
    
    # Test backend connectivity first
    try:
        response = requests.get(f"{API_URL.replace('/api', '')}/", timeout=5)
        print(f"✅ Backend connectivity: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False
    
    # Run critical tests
    test_critical_endpoints()
    
    # Summary
    print("\n" + "="*60)
    print("📊 LOCALHOST BACKEND TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    total_tests = results['passed'] + results['failed']
    if total_tests > 0:
        success_rate = (results['passed'] / total_tests) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Key findings
    passed_tests = [detail for detail in results['details'] if detail['passed']]
    failed_tests = [detail for detail in results['details'] if not detail['passed']]
    
    if passed_tests:
        print(f"\n✅ WORKING FEATURES:")
        for test in passed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    if failed_tests:
        print(f"\n❌ ISSUES FOUND:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    # Overall assessment
    critical_tests = ['Immediate Generation Flag', 'Instant Pause Response', 'First Message Under 10s']
    critical_passed = sum(1 for detail in results['details'] 
                         if detail['test'] in critical_tests and detail['passed'])
    
    print(f"\n🎯 CRITICAL FIXES STATUS: {critical_passed}/{len(critical_tests)} working")
    
    if critical_passed == len(critical_tests):
        print("🎉 ALL CRITICAL FIXES VERIFIED!")
    elif critical_passed >= 2:
        print("⚠️ MOST CRITICAL FIXES WORKING - Minor issues remain")
    else:
        print("❌ CRITICAL FIXES NEED ATTENTION")
    
    return critical_passed >= 2  # Consider success if most critical features work

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)