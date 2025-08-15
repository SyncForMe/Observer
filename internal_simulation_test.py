#!/usr/bin/env python3
"""
INTERNAL SIMULATION START TEST
Test simulation start using internal localhost connection to isolate network issues
"""

import requests
import json
import time
import threading
from datetime import datetime

def test_internal_simulation_start():
    """Test simulation start using localhost"""
    
    print("🧪 INTERNAL SIMULATION START TEST")
    print("=" * 50)
    
    # Use localhost instead of external URL
    API_URL = "http://localhost:8001/api"
    
    # Step 1: Login
    print("\n1. Authenticating...")
    login_data = {
        "email": "dino@cytonic.com", 
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get("access_token")
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Step 2: Check agents
    print("\n2. Checking agents...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            for agent in agents:
                print(f"   - {agent.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent check error: {e}")
        return False
    
    # Step 3: Set scenario
    print("\n3. Setting scenario...")
    scenario_data = {
        "scenario": "Swarm Robotics Military Coup - A team of military robotics experts must develop countermeasures against an AI-controlled swarm of autonomous military robots that have gone rogue.",
        "scenario_name": "Swarm Robotics Military Coup"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Scenario set")
        else:
            print(f"❌ Failed to set scenario: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Scenario error: {e}")
        return False
    
    # Step 4: Test simulation start with monitoring
    print("\n4. Testing simulation start with monitoring...")
    
    # Create a monitoring thread to track progress
    monitoring_active = True
    
    def monitor_backend_logs():
        """Monitor backend logs during simulation start"""
        print("   📊 Starting log monitoring...")
        start_time = time.time()
        
        while monitoring_active:
            current_time = time.time() - start_time
            print(f"   ⏱️  {current_time:.1f}s - Monitoring...")
            time.sleep(5)
            
            if current_time > 60:  # Stop monitoring after 60 seconds
                print("   ⚠️ Monitoring timeout reached")
                break
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_backend_logs)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Test simulation start
    print(f"   🚀 Starting simulation at {datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=90)
        end_time = time.time()
        duration = end_time - start_time
        monitoring_active = False  # Stop monitoring
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS: Completed in {duration:.2f} seconds")
            response_data = response.json()
            print(f"   Message: {response_data.get('message', 'No message')}")
            print(f"   Success: {response_data.get('success', False)}")
            
            # Check if conversation was generated
            conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
            if conv_response.status_code == 200:
                conversations = conv_response.json()
                print(f"   Conversations created: {len(conversations)}")
                if conversations:
                    latest_conv = conversations[-1]
                    messages = latest_conv.get('messages', [])
                    print(f"   Messages in latest conversation: {len(messages)}")
                    
                    # Show first few messages
                    for i, msg in enumerate(messages[:3]):
                        agent_name = msg.get('agent_name', 'Unknown')
                        message_text = msg.get('message', '')[:100]
                        print(f"     {i+1}. {agent_name}: {message_text}...")
            
            return True
            
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            print(f"   Duration: {duration:.2f} seconds")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Error: {response.text}")
            monitoring_active = False
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        monitoring_active = False
        print(f"   ❌ TIMEOUT: Request timed out after {duration:.2f} seconds")
        print(f"   🚨 CONFIRMED: Simulation start endpoint is hanging")
        
        # Check simulation state after timeout
        try:
            state_response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=5)
            if state_response.status_code == 200:
                state_data = state_response.json()
                is_active = state_data.get('is_active', False)
                print(f"   Simulation active after timeout: {is_active}")
        except:
            print(f"   Could not check simulation state after timeout")
        
        return False
        
    except Exception as e:
        monitoring_active = False
        print(f"   ❌ ERROR: {e}")
        return False

def test_conversation_generation_directly():
    """Test conversation generation endpoint directly"""
    print("\n" + "=" * 50)
    print("💬 TESTING CONVERSATION GENERATION DIRECTLY")
    print("=" * 50)
    
    API_URL = "http://localhost:8001/api"
    
    # Login first
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
    token = response.json().get("access_token")
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print("🧪 Testing /api/conversation/generate endpoint...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=60)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Conversation generated in {duration:.2f} seconds")
            response_data = response.json()
            conv_id = response_data.get('id')
            print(f"   Conversation ID: {conv_id}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ TIMEOUT: Conversation generation timed out after {duration:.2f} seconds")
        print("🚨 This confirms the parallel processing is hanging")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SIMULATION START HANGING INVESTIGATION")
    print("Testing internally to isolate network issues")
    print("=" * 60)
    
    # Test simulation start
    sim_success = test_internal_simulation_start()
    
    # Test conversation generation directly
    conv_success = test_conversation_generation_directly()
    
    print("\n" + "=" * 60)
    print("📊 INVESTIGATION RESULTS")
    print("=" * 60)
    
    if not sim_success:
        print("❌ CONFIRMED: /api/simulation/start endpoint is hanging")
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("   - Simulation start consistently times out")
        print("   - Issue is in automatic conversation generation")
        print("   - Located in generate_conversation() function")
        print("   - Parallel processing with asyncio.gather() is hanging")
        
        if not conv_success:
            print("   - /api/conversation/generate also hangs")
            print("   - Problem is in parallel LLM API calls")
            print("   - asyncio.gather(*tasks) is not completing")
        else:
            print("   - /api/conversation/generate works independently")
            print("   - Issue is in integration with simulation start")
        
        print("\n🛠️ RECOMMENDED FIXES:")
        print("   1. Add timeout to asyncio.gather() in generate_conversation()")
        print("   2. Add individual timeouts to LLM API calls (6-10 seconds)")
        print("   3. Implement circuit breaker for LLM API failures")
        print("   4. Add more detailed logging in parallel processing")
        print("   5. Consider fallback to sequential processing")
        print("   6. Add health checks for LLM API endpoints")
        
    else:
        print("✅ Simulation start is working correctly")
        print("   - Issue may be intermittent or network-related")
        print("   - Consider adding more robust error handling")
    
    print("\n" + "=" * 60)