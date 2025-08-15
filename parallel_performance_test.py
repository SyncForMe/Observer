#!/usr/bin/env python3
"""
FOCUSED PARALLEL MESSAGE GENERATION PERFORMANCE TEST
Testing the FIXED parallel processing implementation to verify the critical performance improvements.

CRITICAL FOCUS: Test the user's reported fix where database operations were moved outside parallel execution.
Expected: ~27 seconds instead of 85+ seconds (3x performance improvement)
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Use internal backend URL for reliable testing
BACKEND_URL = "http://localhost:8001"
API_URL = f"{BACKEND_URL}/api"

print(f"🔧 Using internal API URL: {API_URL}")

def test_authentication():
    """Test authentication with the backend"""
    print("\n🔐 Testing Authentication...")
    
    login_data = {
        "email": "dino@cytonic.com", 
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("✅ Authentication successful")
                return token
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_parallel_conversation_generation(auth_token):
    """Test the CRITICAL parallel conversation generation performance"""
    print("\n" + "="*80)
    print("🚀 CRITICAL TEST: PARALLEL CONVERSATION GENERATION PERFORMANCE")
    print("="*80)
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    # Step 1: Set up scenario
    print("\n📋 Step 1: Setting up test scenario...")
    scenario_data = {
        "scenario": "A team of quantum physicists needs to develop a breakthrough quantum communication device. The team must collaborate to solve technical challenges.",
        "scenario_name": "Quantum Communication Device Development"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Scenario set successfully")
        else:
            print(f"⚠️ Scenario setup issue: {response.status_code} - continuing anyway")
    except Exception as e:
        print(f"⚠️ Scenario setup error: {e} - continuing anyway")
    
    # Step 2: Check agents
    print("\n🤖 Step 2: Checking available agents...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if response.status_code == 200:
            agents = response.json()
            agent_count = len(agents)
            print(f"✅ Found {agent_count} agents for parallel testing")
            if agent_count >= 3:
                print(f"   Agents: {[agent.get('name', 'Unknown')[:20] for agent in agents[:5]]}")
            else:
                print("⚠️ Limited agents available - test will still proceed")
        else:
            print(f"⚠️ Could not get agents: {response.status_code}")
            agent_count = 3  # Assume minimum for calculation
    except Exception as e:
        print(f"⚠️ Agent check error: {e}")
        agent_count = 3  # Assume minimum for calculation
    
    # Step 3: THE CRITICAL TEST - Parallel Conversation Generation
    print(f"\n⚡ Step 3: TESTING FIXED PARALLEL PROCESSING PERFORMANCE")
    print(f"   🎯 Target: ~27 seconds (vs ~{27 * agent_count}s sequential)")
    print(f"   🔧 Fix: Database operations moved outside parallel execution")
    print(f"   📊 Expected improvement: ~{agent_count}x faster")
    
    print(f"\n⏱️ Starting parallel conversation generation...")
    start_time = time.time()
    
    try:
        # Allow generous timeout for the parallel processing
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=120)
        
        if response.status_code == 200:
            end_time = time.time()
            generation_time = end_time - start_time
            
            print(f"\n🎉 PARALLEL GENERATION COMPLETED!")
            print(f"   ⏱️ Total time: {generation_time:.2f} seconds")
            
            # Performance analysis
            expected_sequential = 27 * agent_count
            if generation_time <= 45:  # Target ~27s, allow buffer to 45s
                improvement_factor = expected_sequential / generation_time
                efficiency = (expected_sequential - generation_time) / expected_sequential * 100
                
                print(f"   ✅ PERFORMANCE SUCCESS!")
                print(f"   📈 Performance improvement: {improvement_factor:.1f}x faster")
                print(f"   ⚡ Efficiency gain: {efficiency:.1f}%")
                print(f"   🎯 Target met: {generation_time:.2f}s ≤ 45s threshold")
                
                if generation_time <= 30:
                    print(f"   🏆 EXCELLENT: Under 30 seconds!")
                
                return True, generation_time, improvement_factor
            else:
                print(f"   ❌ PERFORMANCE ISSUE!")
                print(f"   ⏱️ Time: {generation_time:.2f}s > 45s threshold")
                print(f"   📉 Expected: ~27s, Got: {generation_time:.2f}s")
                return False, generation_time, expected_sequential / generation_time
                
        else:
            print(f"❌ Conversation generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, 0, 0
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Conversation generation took longer than 120 seconds")
        print(f"   This suggests the parallel processing fix may not be working")
        return False, 120, 0
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False, 0, 0

def test_streaming_after_parallel_generation(auth_token):
    """Test that streaming still works after parallel generation"""
    print("\n" + "="*60)
    print("📤 TESTING: STREAMING AFTER PARALLEL GENERATION")
    print("="*60)
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{API_URL}/messages/stream", headers=headers, timeout=10)
        if response.status_code == 200:
            stream_data = response.json()
            message_count = stream_data.get('count', 0)
            
            print(f"✅ Streaming endpoint accessible")
            print(f"   📊 Messages available: {message_count}")
            
            if message_count > 0:
                messages = stream_data.get('messages', [])
                if messages:
                    sample_message = messages[0]
                    print(f"   📝 Sample message: {sample_message.get('agent_name', 'Unknown')}: {sample_message.get('message', '')[:50]}...")
                    return True
            else:
                print(f"   ℹ️ No streaming messages (expected if messages were already converted)")
                return True
        else:
            print(f"❌ Streaming test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return False

def test_performance_logs_verification():
    """Check backend logs for parallel processing performance indicators"""
    print("\n" + "="*60)
    print("📋 TESTING: PERFORMANCE LOGS VERIFICATION")
    print("="*60)
    
    try:
        # Check recent backend logs for performance indicators
        import subprocess
        result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            log_content = result.stdout
            
            # Look for parallel processing indicators
            performance_indicators = [
                "🚀 PARALLEL generation completed",
                "⚡ PERFORMANCE IMPROVEMENT:",
                "faster!",
                "PROGRESSIVE STREAMING COMPLETE"
            ]
            
            found_indicators = []
            for indicator in performance_indicators:
                if indicator in log_content:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"✅ Found {len(found_indicators)} performance indicators in logs:")
                for indicator in found_indicators:
                    print(f"   🔍 '{indicator}'")
                
                # Extract performance improvement if available
                lines = log_content.split('\n')
                for line in lines:
                    if "PERFORMANCE IMPROVEMENT:" in line and "faster!" in line:
                        print(f"   📈 Performance log: {line.strip()}")
                        break
                
                return True
            else:
                print(f"⚠️ No performance indicators found in recent logs")
                return False
        else:
            print(f"⚠️ Could not read backend logs")
            return False
            
    except Exception as e:
        print(f"⚠️ Log verification error: {e}")
        return False

def run_focused_parallel_test():
    """Run the focused parallel processing performance test"""
    print("🚀 FOCUSED PARALLEL MESSAGE GENERATION PERFORMANCE TEST")
    print("=" * 80)
    print("Testing the FIXED parallel processing implementation")
    print("Expected: ~27 seconds instead of 85+ seconds (3x improvement)")
    print("=" * 80)
    
    # Test 1: Authentication
    auth_token = test_authentication()
    if not auth_token:
        print("\n❌ CRITICAL FAILURE: Could not authenticate")
        return False
    
    # Test 2: Parallel Conversation Generation Performance (CRITICAL)
    success, generation_time, improvement = test_parallel_conversation_generation(auth_token)
    
    # Test 3: Streaming After Parallel Generation
    streaming_success = test_streaming_after_parallel_generation(auth_token)
    
    # Test 4: Performance Logs Verification
    logs_success = test_performance_logs_verification()
    
    # Summary
    print("\n" + "="*80)
    print("📊 FOCUSED PARALLEL PROCESSING TEST SUMMARY")
    print("="*80)
    
    if success:
        print(f"✅ PARALLEL PROCESSING FIX: SUCCESS")
        print(f"   ⏱️ Generation time: {generation_time:.2f} seconds")
        print(f"   📈 Performance improvement: {improvement:.1f}x faster")
        print(f"   🎯 Target achieved: Under 45 seconds")
        
        if generation_time <= 30:
            print(f"   🏆 EXCELLENT PERFORMANCE: Under 30 seconds!")
    else:
        print(f"❌ PARALLEL PROCESSING FIX: NEEDS ATTENTION")
        if generation_time > 0:
            print(f"   ⏱️ Generation time: {generation_time:.2f} seconds")
            print(f"   📉 Performance: {improvement:.1f}x improvement (target: 3x+)")
    
    print(f"✅ Streaming functionality: {'Working' if streaming_success else 'Issues detected'}")
    print(f"✅ Performance logs: {'Found indicators' if logs_success else 'No clear indicators'}")
    
    overall_success = success and streaming_success
    
    if overall_success:
        print(f"\n🎉 OVERALL RESULT: PARALLEL PROCESSING FIX IS WORKING!")
        print(f"   The user's fix (moving database operations outside parallel execution) is successful")
        print(f"   Performance target achieved with {improvement:.1f}x speed improvement")
    else:
        print(f"\n⚠️ OVERALL RESULT: PARALLEL PROCESSING NEEDS REVIEW")
        print(f"   Some aspects of the parallel processing fix may need attention")
    
    print("\n" + "="*80)
    return overall_success

if __name__ == "__main__":
    success = run_focused_parallel_test()
    sys.exit(0 if success else 1)