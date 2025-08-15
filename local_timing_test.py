#!/usr/bin/env python3
"""
LOCAL TIMING TEST
Test conversation generation timing using local backend connection.
"""

import requests
import json
import time
import os

# Test local backend directly
LOCAL_API = "http://localhost:8001/api"

print(f"Testing local API: {LOCAL_API}")

def test_local_timing():
    """Test timing using local backend"""
    
    try:
        # Test 1: Authentication
        print("\n🔐 Testing Local Authentication...")
        auth_start = time.time()
        
        login_data = {
            "email": "dino@cytonic.com",
            "password": "Observerinho8"
        }
        
        response = requests.post(f"{LOCAL_API}/auth/login", json=login_data, timeout=10)
        auth_end = time.time()
        auth_time = auth_end - auth_start
        
        print(f"   Auth time: {auth_time:.2f} seconds")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Local authentication successful")
            token = response.json().get("access_token")
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Test 2: Get current conversations
            print("\n📊 Checking Current State...")
            conv_response = requests.get(f"{LOCAL_API}/conversations", headers=headers, timeout=10)
            
            if conv_response.status_code == 200:
                conversations = conv_response.json()
                print(f"   Current conversations: {len(conversations)}")
                
                if conversations:
                    latest = conversations[-1]
                    messages = latest.get('messages', [])
                    print(f"   Latest conversation messages: {len(messages)}")
                    
                    # Analyze message timestamps
                    if len(messages) > 1:
                        timestamps = []
                        for msg in messages:
                            if 'timestamp' in msg:
                                timestamps.append(msg['timestamp'])
                        
                        if timestamps:
                            unique_timestamps = len(set(timestamps))
                            print(f"   Unique timestamps: {unique_timestamps}/{len(timestamps)}")
                            
                            if unique_timestamps == 1:
                                print("   ⚠️  BULK CREATION: All messages have same timestamp")
                            elif unique_timestamps == len(timestamps):
                                print("   ✅ SEQUENTIAL: Each message has unique timestamp")
                            else:
                                print("   ⚠️  MIXED: Some messages share timestamps")
                            
                            # Show first few timestamps
                            print(f"   Sample timestamps:")
                            for i, ts in enumerate(timestamps[:3]):
                                print(f"     {i+1}: {ts}")
            
            # Test 3: Conversation generation timing
            print("\n💬 Testing Conversation Generation...")
            
            # Set scenario
            scenario_data = {
                "scenario": "Engineers need to design a new system quickly",
                "scenario_name": "Quick System Design"
            }
            
            scenario_response = requests.post(f"{LOCAL_API}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
            print(f"   Scenario setup: {scenario_response.status_code}")
            
            # Get initial count
            initial_response = requests.get(f"{LOCAL_API}/conversations", headers=headers, timeout=10)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_count = len(initial_response.json())
            
            # Generate conversation
            gen_start = time.time()
            print("   🚀 Starting conversation generation...")
            
            gen_response = requests.post(f"{LOCAL_API}/conversation/generate", headers=headers, timeout=120)
            
            gen_end = time.time()
            gen_time = gen_end - gen_start
            
            print(f"   ⏱️  Generation time: {gen_time:.2f} seconds")
            print(f"   📊 Response status: {gen_response.status_code}")
            
            if gen_response.status_code == 200:
                # Check what was created
                final_response = requests.get(f"{LOCAL_API}/conversations", headers=headers, timeout=10)
                if final_response.status_code == 200:
                    final_conversations = final_response.json()
                    final_count = len(final_conversations)
                    new_conversations = final_count - initial_count
                    
                    print(f"   📈 New conversations: {new_conversations}")
                    
                    if new_conversations > 0:
                        latest_conv = final_conversations[-1]
                        messages = latest_conv.get('messages', [])
                        print(f"   💬 Messages in latest: {len(messages)}")
                        
                        # Detailed timestamp analysis
                        if len(messages) > 1:
                            timestamps = []
                            for i, msg in enumerate(messages):
                                ts = msg.get('timestamp', '')
                                agent = msg.get('agent_name', 'Unknown')
                                timestamps.append(ts)
                                print(f"     Message {i+1}: {agent} at {ts}")
                            
                            unique_timestamps = len(set(timestamps))
                            print(f"   🕐 Timestamp analysis: {unique_timestamps}/{len(timestamps)} unique")
                            
                            if unique_timestamps == 1:
                                print("   🚨 ISSUE FOUND: Bulk message creation")
                                print("   🔍 All messages created simultaneously")
                                print("   💡 This explains '10 messages appearing at once'")
                            else:
                                print("   ✅ Sequential message creation detected")
                        
                        # Performance analysis
                        print(f"\n📊 PERFORMANCE ANALYSIS:")
                        print(f"   Generation time: {gen_time:.2f}s")
                        print(f"   Messages created: {len(messages)}")
                        print(f"   Time per message: {gen_time/len(messages):.2f}s" if messages else "N/A")
                        
                        if gen_time > 30:
                            print(f"   ⚠️  SLOW: {gen_time:.2f}s is too long")
                            print(f"   🔍 Causes long wait before bulk display")
                        elif gen_time > 15:
                            print(f"   ⚠️  ABOVE TARGET: Should be under 15s")
                        else:
                            print(f"   ✅ GOOD: Within target time")
            
            # Test 4: Simulation controls
            print("\n⏯️  Testing Simulation Controls...")
            
            controls = [
                ("start", "/simulation/start"),
                ("pause", "/simulation/pause"), 
                ("resume", "/simulation/resume")
            ]
            
            for name, endpoint in controls:
                start_time = time.time()
                response = requests.post(f"{LOCAL_API}{endpoint}", headers=headers, timeout=10)
                duration = time.time() - start_time
                
                print(f"   {name.capitalize()}: {duration:.2f}s (status: {response.status_code})")
                
                if duration > 2:
                    print(f"     ⚠️  SLOW: {duration:.2f}s causes UI delays")
                
                time.sleep(0.2)  # Small delay between operations
            
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to local backend")
        print("   🔍 Backend may not be running on localhost:8001")
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_local_timing()