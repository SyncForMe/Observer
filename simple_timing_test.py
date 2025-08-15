#!/usr/bin/env python3
"""
SIMPLE CONVERSATION TIMING TEST
Quick test to measure conversation generation timing and identify bulk display issues.
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"Testing API: {API_URL}")

def test_auth_and_timing():
    """Test authentication and basic timing"""
    
    # Test 1: Authentication timing
    print("\n🔐 Testing Authentication...")
    auth_start = time.time()
    
    login_data = {
        "email": "dino@cytonic.com", 
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
        auth_end = time.time()
        auth_time = auth_end - auth_start
        
        print(f"   Auth time: {auth_time:.2f} seconds")
        
        if response.status_code == 200:
            print("   ✅ Authentication successful")
            token = response.json().get("access_token")
            
            # Test 2: Conversation generation timing
            print("\n💬 Testing Conversation Generation...")
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Set scenario first
            scenario_data = {
                "scenario": "Team needs to solve a technical problem quickly",
                "scenario_name": "Quick Problem Solving"
            }
            
            scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=30)
            print(f"   Scenario setup: {scenario_response.status_code}")
            
            # Get initial conversation count
            conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=30)
            initial_count = 0
            if conv_response.status_code == 200:
                initial_count = len(conv_response.json())
                print(f"   Initial conversations: {initial_count}")
            
            # Generate conversation with timing
            gen_start = time.time()
            print("   🚀 Starting conversation generation...")
            
            gen_response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=180)
            
            gen_end = time.time()
            gen_time = gen_end - gen_start
            
            print(f"   Generation time: {gen_time:.2f} seconds")
            print(f"   Response status: {gen_response.status_code}")
            
            if gen_response.status_code == 200:
                response_data = gen_response.json()
                print(f"   Response size: {len(str(response_data))} characters")
                
                # Check final conversation count
                final_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=30)
                if final_response.status_code == 200:
                    final_conversations = final_response.json()
                    final_count = len(final_conversations)
                    new_conversations = final_count - initial_count
                    
                    print(f"   Final conversations: {final_count} (+{new_conversations})")
                    
                    if new_conversations > 0:
                        latest_conv = final_conversations[-1]
                        messages = latest_conv.get('messages', [])
                        print(f"   Messages in latest: {len(messages)}")
                        
                        # Check timestamps for bulk creation detection
                        if len(messages) > 1:
                            timestamps = [msg.get('timestamp', '') for msg in messages if 'timestamp' in msg]
                            unique_timestamps = len(set(timestamps))
                            
                            print(f"   Unique timestamps: {unique_timestamps}/{len(timestamps)}")
                            
                            if unique_timestamps == 1:
                                print("   ⚠️  BULK CREATION DETECTED - All messages have same timestamp")
                                print("   🔍 This explains '10 messages appearing at once' issue")
                            else:
                                print("   ✅ Sequential creation - Different timestamps found")
                        
                        # Show timing analysis
                        print(f"\n📊 TIMING ANALYSIS:")
                        print(f"   Authentication: {auth_time:.2f}s")
                        print(f"   Conversation generation: {gen_time:.2f}s")
                        print(f"   Messages created: {len(messages)}")
                        
                        if gen_time > 30:
                            print(f"   ⚠️  SLOW GENERATION: {gen_time:.2f}s is too long")
                            print(f"   🔍 This causes long waits before bulk message display")
                        
                        if gen_time > 10:
                            print(f"   ⚠️  ABOVE TARGET: Should be under 10-15 seconds")
                
            else:
                print(f"   ❌ Generation failed: {gen_response.status_code}")
                try:
                    print(f"   Error: {gen_response.json()}")
                except:
                    print(f"   Error: {gen_response.text[:200]}")
            
            # Test 3: Simulation control timing
            print("\n⏯️  Testing Simulation Controls...")
            
            # Start
            start_time = time.time()
            start_response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=30)
            start_duration = time.time() - start_time
            print(f"   Start: {start_duration:.2f}s (status: {start_response.status_code})")
            
            time.sleep(0.5)
            
            # Pause  
            pause_time = time.time()
            pause_response = requests.post(f"{API_URL}/simulation/pause", headers=headers, timeout=30)
            pause_duration = time.time() - pause_time
            print(f"   Pause: {pause_duration:.2f}s (status: {pause_response.status_code})")
            
            time.sleep(0.5)
            
            # Resume
            resume_time = time.time()
            resume_response = requests.post(f"{API_URL}/simulation/resume", headers=headers, timeout=30)
            resume_duration = time.time() - resume_time
            print(f"   Resume: {resume_duration:.2f}s (status: {resume_response.status_code})")
            
            # Check for slow operations
            slow_ops = []
            if start_duration > 2:
                slow_ops.append(f"Start({start_duration:.1f}s)")
            if pause_duration > 2:
                slow_ops.append(f"Pause({pause_duration:.1f}s)")
            if resume_duration > 2:
                slow_ops.append(f"Resume({resume_duration:.1f}s)")
            
            if slow_ops:
                print(f"   ⚠️  SLOW OPERATIONS: {', '.join(slow_ops)}")
                print(f"   🔍 This explains long delays in play/pause operations")
            else:
                print(f"   ✅ All operations under 2 seconds")
                
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_auth_and_timing()