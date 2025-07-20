#!/usr/bin/env python3
"""
Local Backend Test for Conversation Generation
Tests the backend directly using localhost to avoid external URL timeouts
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Test locally using internal backend port
API_URL = "http://localhost:8001/api"

print(f"Testing Local API URL: {API_URL}")

def test_endpoint(name, method, endpoint, data=None, auth_token=None, timeout=10):
    """Test endpoint with timeout"""
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    print(f"\n🧪 {name}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                print(f"   ✅ SUCCESS")
                return True, data
            except:
                print(f"   ✅ SUCCESS (non-JSON)")
                return True, response.text
        else:
            print(f"   ❌ FAILED")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT")
        return False, None
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False, None

def main():
    print("🚀 LOCAL BACKEND CONVERSATION TESTS")
    print("="*50)
    
    # Test 1: Authentication
    print("\n1️⃣ AUTHENTICATION")
    auth_success, auth_data = test_endpoint(
        "Guest Login", "POST", "/auth/test-login"
    )
    
    if not auth_success:
        print("❌ Cannot proceed without auth")
        return
    
    token = auth_data.get("access_token")
    user_id = auth_data.get("user", {}).get("id")
    print(f"   User ID: {user_id}")
    
    # Test 2: Get Conversations
    print("\n2️⃣ CONVERSATIONS ENDPOINT")
    conv_success, conv_data = test_endpoint(
        "Get Conversations", "GET", "/conversations", auth_token=token
    )
    
    if conv_success:
        count = len(conv_data) if conv_data else 0
        print(f"   📊 Found {count} conversations")
        
        if count > 0:
            sample = conv_data[0]
            print(f"   📋 Fields: {list(sample.keys())}")
            
            # Check structure
            messages = sample.get("messages", [])
            print(f"   💬 Messages in first conversation: {len(messages)}")
            
            if messages:
                msg = messages[0]
                print(f"   📝 Message fields: {list(msg.keys())}")
                agent_name = msg.get("agent_name", "Unknown")
                message_text = msg.get("message", "")[:50] + "..."
                print(f"   📄 Sample: {agent_name}: {message_text}")
    
    # Test 3: Simulation State
    print("\n3️⃣ SIMULATION STATE")
    state_success, state_data = test_endpoint(
        "Get Simulation State", "GET", "/simulation/state", auth_token=token
    )
    
    if state_success and state_data:
        is_active = state_data.get("is_active", False)
        scenario = state_data.get("scenario", "Unknown")
        print(f"   🎮 Active: {is_active}")
        print(f"   🎭 Scenario: {scenario}")
    
    # Test 4: Agents
    print("\n4️⃣ AGENTS")
    agents_success, agents_data = test_endpoint(
        "Get Agents", "GET", "/agents", auth_token=token
    )
    
    if agents_success:
        count = len(agents_data) if agents_data else 0
        print(f"   🤖 Found {count} agents")
        
        if count > 0:
            for i, agent in enumerate(agents_data[:3]):
                name = agent.get("name", "Unknown")
                archetype = agent.get("archetype", "Unknown")
                print(f"   Agent {i+1}: {name} ({archetype})")
    
    # Test 5: Conversation Generation (if we have agents)
    print("\n5️⃣ CONVERSATION GENERATION")
    if agents_success and agents_data and len(agents_data) >= 2:
        gen_success, gen_data = test_endpoint(
            "Generate Conversation", "POST", "/conversation/generate", 
            auth_token=token, timeout=30
        )
        
        if gen_success and gen_data:
            conv_id = gen_data.get("id")
            messages = gen_data.get("messages", [])
            print(f"   🆔 Generated ID: {conv_id}")
            print(f"   💬 Generated {len(messages)} messages")
            
            if messages:
                for i, msg in enumerate(messages[:2]):
                    agent_name = msg.get("agent_name", "Unknown")
                    message_text = msg.get("message", "")[:80] + "..."
                    print(f"   Msg {i+1}: {agent_name}: {message_text}")
        else:
            print("   ❌ Generation failed")
    else:
        print("   ⚠️  Need at least 2 agents")
    
    # Test 6: Verify persistence
    print("\n6️⃣ PERSISTENCE CHECK")
    final_conv_success, final_conv_data = test_endpoint(
        "Get Conversations Again", "GET", "/conversations", auth_token=token
    )
    
    if final_conv_success:
        final_count = len(final_conv_data) if final_conv_data else 0
        initial_count = len(conv_data) if conv_data else 0
        print(f"   📊 Before: {initial_count}, After: {final_count}")
        
        if final_count > initial_count:
            print("   ✅ New conversations saved")
        else:
            print("   ⚠️  No new conversations")
    
    # Summary
    print("\n" + "="*50)
    print("📋 SUMMARY")
    print("="*50)
    
    tests = [
        ("Authentication", auth_success),
        ("Get Conversations", conv_success),
        ("Get Simulation State", state_success),
        ("Get Agents", agents_success),
        ("Final Check", final_conv_success)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 RESULT: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()