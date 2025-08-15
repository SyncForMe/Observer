#!/usr/bin/env python3
"""
INTERNAL PARALLEL MESSAGE GENERATION TESTING
Testing parallel processing using internal backend connection.
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Use internal backend connection
API_URL = "http://localhost:8001/api"

print(f"🚀 PARALLEL MESSAGE GENERATION TESTING (INTERNAL)")
print(f"Using Internal API URL: {API_URL}")
print("="*80)

# Test authentication
print("\n🔐 Testing Authentication...")
login_data = {
    "email": "dino@cytonic.com",
    "password": "Observerinho8"
}

try:
    response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        auth_data = response.json()
        auth_token = auth_data.get("access_token")
        print("✅ Authentication successful")
        
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        
        # Test 1: Check agents
        print("\n🤖 Testing Agent Availability...")
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            for agent in agents[:3]:
                print(f"   - {agent.get('name', 'Unknown')}")
                
            if len(agents) < 3:
                print("⚠️ Creating additional agents for parallel testing...")
                # Create a test agent
                test_agent = {
                    "name": "Dr. Parallel Test",
                    "archetype": "scientist",
                    "goal": "Test parallel processing",
                    "expertise": "Parallel Computing",
                    "background": "Expert in parallel processing systems",
                    "personality": {
                        "extroversion": 6,
                        "optimism": 7,
                        "curiosity": 8,
                        "cooperativeness": 7,
                        "energy": 6
                    }
                }
                response = requests.post(f"{API_URL}/agents", json=test_agent, headers=headers, timeout=10)
                if response.status_code == 200:
                    print("✅ Created additional test agent")
                else:
                    print(f"❌ Failed to create test agent: {response.status_code}")
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
        
        # Test 2: Set scenario
        print("\n📋 Testing Scenario Setup...")
        scenario_data = {
            "scenario": "A team of quantum physicists needs to develop a breakthrough quantum communication device for secure military communications. The team must collaborate to solve technical challenges and create implementation plans.",
            "scenario_name": "Quantum Communication Device Development"
        }
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Scenario set successfully")
        else:
            print(f"❌ Failed to set scenario: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test 3: Test parallel conversation generation (CRITICAL TEST)
        print("\n⚡ Testing PARALLEL Conversation Generation...")
        print("   This is the key test for parallel processing performance!")
        print("   Expected: ~27 seconds (vs ~81s sequential for 3 agents)")
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            generation_time = end_time - start_time
            response_data = response.json()
            
            print(f"✅ Conversation generated in {generation_time:.2f} seconds")
            print(f"   Conversation ID: {response_data.get('id', 'Unknown')}")
            
            # Check if it's within parallel processing target
            if generation_time <= 45:
                # Calculate improvement assuming 3 agents * 27s = 81s sequential
                sequential_estimate = 81  # 3 agents * 27s each
                improvement = sequential_estimate / generation_time
                efficiency = (sequential_estimate - generation_time) / sequential_estimate * 100
                
                print(f"🎉 PARALLEL PROCESSING SUCCESS!")
                print(f"   Performance: {improvement:.1f}x faster than sequential")
                print(f"   Efficiency: {efficiency:.1f}% time reduction")
                print(f"   Target: ~27s, Actual: {generation_time:.2f}s")
                
                if generation_time <= 30:
                    print("🏆 EXCELLENT: Within target performance range!")
                else:
                    print("✅ GOOD: Acceptable performance, room for optimization")
            else:
                print(f"⚠️ Performance below target: {generation_time:.2f}s (target: ~27s)")
                print("   May indicate sequential processing instead of parallel")
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}")
        
        # Test 4: Test message streaming
        print("\n📤 Testing Message Streaming...")
        response = requests.get(f"{API_URL}/messages/stream", headers=headers, timeout=10)
        if response.status_code == 200:
            stream_data = response.json()
            message_count = stream_data.get('count', 0)
            print(f"✅ Streaming endpoint working - {message_count} messages available")
            
            # Check required fields
            required_fields = ['messages', 'count', 'since', 'timestamp']
            has_all_fields = all(field in stream_data for field in required_fields)
            if has_all_fields:
                print("✅ Streaming response has all required fields")
                
                # Check message structure if messages exist
                messages = stream_data.get('messages', [])
                if messages:
                    first_message = messages[0]
                    message_fields = ['id', 'agent_name', 'message', 'timestamp']
                    has_message_fields = all(field in first_message for field in message_fields)
                    if has_message_fields:
                        print("✅ Message structure is correct")
                    else:
                        print("❌ Message structure missing required fields")
            else:
                print("❌ Missing required fields in streaming response")
        else:
            print(f"❌ Failed to access streaming endpoint: {response.status_code}")
        
        # Test 5: Verify conversation was created
        print("\n📋 Testing Conversation Retrieval...")
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        if response.status_code == 200:
            conversations = response.json()
            if conversations:
                latest_conv = conversations[-1]
                messages = latest_conv.get('messages', [])
                print(f"✅ Latest conversation has {len(messages)} messages")
                
                # Check agent participation
                unique_agents = set(msg.get('agent_name', '') for msg in messages)
                print(f"✅ {len(unique_agents)} different agents participated")
                for agent_name in unique_agents:
                    print(f"   - {agent_name}")
                
                # Check message quality
                if messages:
                    avg_length = sum(len(msg.get('message', '')) for msg in messages) / len(messages)
                    print(f"✅ Average message length: {avg_length:.0f} characters")
                    
                    # Check for parallel processing indicators in content
                    total_content = ' '.join(msg.get('message', '') for msg in messages)
                    if len(total_content) > 500:
                        print("✅ Messages have substantial content (good quality)")
                    else:
                        print("⚠️ Messages seem short (may indicate fallback responses)")
            else:
                print("❌ No conversations found")
        else:
            print(f"❌ Failed to retrieve conversations: {response.status_code}")
        
        # Test 6: Test stream completion endpoint
        print("\n🔄 Testing Stream Completion...")
        fake_conversation_id = "test_stream_12345"
        response = requests.post(f"{API_URL}/messages/stream/complete?conversation_id={fake_conversation_id}", headers=headers, timeout=10)
        if response.status_code in [400, 404]:
            print(f"✅ Stream completion endpoint working (proper error handling: {response.status_code})")
        else:
            print(f"⚠️ Unexpected response from stream completion: {response.status_code}")
            
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Test failed with error: {e}")

print("\n" + "="*80)
print("🏁 PARALLEL MESSAGE GENERATION TEST COMPLETE")
print("="*80)
print("\nKEY FINDINGS:")
print("- Parallel processing should reduce generation time from ~81s to ~27s")
print("- Message streaming should work with parallel generation")
print("- Database operations should handle parallel processing correctly")
print("- Error handling should work in parallel system")
print("="*80)