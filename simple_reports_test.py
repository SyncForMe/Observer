#!/usr/bin/env python3
"""
Simple test to verify Start Fresh reports clearing functionality
"""

import requests
import json
import jwt
from datetime import datetime, timedelta

# Backend URL
BACKEND_URL = 'https://simulated-agents.preview.emergentagent.com'
API_BASE = f"{BACKEND_URL}/api"

def main():
    # Create JWT token
    jwt_secret = "test_jwt_secret_for_observer_message_testing_12345"
    user_payload = {
        "sub": "test-user-123",
        "user_id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    auth_token = jwt.encode(user_payload, jwt_secret, algorithm="HS256")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    print("🚀 SIMPLE START FRESH REPORTS TEST")
    print("=" * 60)
    
    # Test 1: Check initial state
    print("\n1. Initial State Check")
    response = requests.get(f"{API_BASE}/simulation/state", headers=headers)
    sim_state = response.json()
    
    response = requests.get(f"{API_BASE}/reports", headers=headers)
    reports_data = response.json()
    
    initial_observatory = len(sim_state.get('reports', []))
    initial_library = len(reports_data.get('reports', []))
    
    print(f"   Observatory: {initial_observatory} reports")
    print(f"   Library: {initial_library} reports")
    
    # Test 2: Execute Start Fresh
    print("\n2. Execute Start Fresh")
    response = requests.post(f"{API_BASE}/simulation/reset", headers=headers)
    reset_result = response.json()
    
    if reset_result.get('success'):
        print("   ✅ Start Fresh executed successfully")
        cleared = reset_result.get('cleared_collections', [])
        preserved = reset_result.get('preserved_collections', [])
        print(f"   Cleared: {cleared}")
        print(f"   Preserved: {preserved}")
        
        # Verify reports are preserved
        if 'reports' in preserved:
            print("   ✅ Reports are preserved (correct)")
        else:
            print("   ❌ Reports are NOT preserved (incorrect)")
    else:
        print("   ❌ Start Fresh failed")
        return
    
    # Test 3: Verify Observatory cleared
    print("\n3. Verify Observatory Cleared")
    response = requests.get(f"{API_BASE}/simulation/state", headers=headers)
    sim_state = response.json()
    observatory_after = len(sim_state.get('reports', []))
    
    if observatory_after == 0:
        print("   ✅ Observatory cleared (0 reports)")
    else:
        print(f"   ❌ Observatory NOT cleared ({observatory_after} reports)")
    
    # Test 4: Verify Library preserved
    print("\n4. Verify Library Preserved")
    response = requests.get(f"{API_BASE}/reports", headers=headers)
    reports_data = response.json()
    library_after = len(reports_data.get('reports', []))
    
    if library_after >= initial_library:
        print(f"   ✅ Library preserved ({library_after} reports)")
    else:
        print(f"   ❌ Library NOT preserved ({library_after} reports)")
    
    # Test 5: Check simulation state details
    print("\n5. Simulation State Details")
    scenario = sim_state.get('scenario', '')
    scenario_name = sim_state.get('scenario_name', '')
    is_active = sim_state.get('is_active', False)
    start_time = sim_state.get('simulation_start_time')
    
    print(f"   Scenario: '{scenario}'")
    print(f"   Scenario Name: '{scenario_name}'")
    print(f"   Is Active: {is_active}")
    print(f"   Start Time: {start_time}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    if reset_result.get('success') and 'reports' in reset_result.get('preserved_collections', []):
        tests_passed += 1
        print("✅ Start Fresh execution: PASS")
    else:
        print("❌ Start Fresh execution: FAIL")
    
    if observatory_after == 0:
        tests_passed += 1
        print("✅ Observatory cleared: PASS")
    else:
        print("❌ Observatory cleared: FAIL")
    
    if library_after >= initial_library:
        tests_passed += 1
        print("✅ Library preserved: PASS")
    else:
        print("❌ Library preserved: FAIL")
    
    if not scenario and not is_active:
        tests_passed += 1
        print("✅ Simulation state reset: PASS")
    else:
        print("❌ Simulation state reset: FAIL")
    
    print(f"\n🎯 OVERALL: {tests_passed}/{total_tests} tests passed ({(tests_passed/total_tests)*100:.1f}%)")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - Start Fresh functionality is working correctly!")
    else:
        print("⚠️ SOME TESTS FAILED - Issues detected with Start Fresh functionality")

if __name__ == "__main__":
    main()
