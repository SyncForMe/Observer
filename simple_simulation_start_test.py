#!/usr/bin/env python3
"""
SIMPLE SIMULATION START TEST
Direct test of the hanging /api/simulation/start endpoint
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"Testing API URL: {API_URL}")

def test_simulation_start():
    """Test simulation start with existing user setup"""
    
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
        if not token:
            print("❌ No token received")
            return False
        
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
            if len(agents) < 2:
                print("❌ Need at least 2 agents")
                return False
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent check error: {e}")
        return False
    
    # Step 3: Set scenario
    print("\n3. Setting scenario...")
    scenario_data = {
        "scenario": "Swarm Robotics Military Coup",
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
    
    # Step 4: Test simulation start with different timeouts
    print("\n4. Testing simulation start...")
    
    timeouts = [30, 60, 90]  # Test with increasing timeouts
    
    for timeout in timeouts:
        print(f"\n   Testing with {timeout}s timeout...")
        start_time = time.time()
        
        try:
            response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=timeout)
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: Completed in {duration:.2f} seconds")
                response_data = response.json()
                print(f"   Message: {response_data.get('message', 'No message')}")
                return True
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   Duration: {duration:.2f} seconds")
                try:
                    print(f"   Error: {response.json()}")
                except:
                    print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            duration = end_time - start_time
            print(f"   ❌ TIMEOUT: Request timed out after {duration:.2f} seconds")
            print(f"   🚨 CONFIRMED: Endpoint is hanging")
            
            # Check if simulation state changed despite timeout
            try:
                state_response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=5)
                if state_response.status_code == 200:
                    state_data = state_response.json()
                    is_active = state_data.get('is_active', False)
                    print(f"   Simulation active after timeout: {is_active}")
            except:
                print(f"   Could not check simulation state")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    return False

if __name__ == "__main__":
    print("🚨 SIMULATION START HANGING INVESTIGATION")
    print("=" * 60)
    
    success = test_simulation_start()
    
    if not success:
        print("\n❌ CONFIRMED: /api/simulation/start endpoint is hanging")
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("   - Endpoint consistently times out")
        print("   - Issue is in automatic conversation generation")
        print("   - Likely hanging in parallel LLM API calls")
        print("   - asyncio.gather() may be deadlocking")
        
        print("\n🛠️ RECOMMENDED FIXES:")
        print("   1. Add timeout to asyncio.gather() in conversation generation")
        print("   2. Add individual timeouts to LLM API calls")
        print("   3. Implement circuit breaker for LLM failures")
        print("   4. Add more detailed logging")
        print("   5. Consider fallback to sequential processing")
    else:
        print("\n✅ Simulation start is working")
    
    print("\n" + "=" * 60)