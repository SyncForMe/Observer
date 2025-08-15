#!/usr/bin/env python3
"""
Quick test for parallelized conversation generation
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate():
    """Authenticate with the backend"""
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_conversation_generation():
    """Test conversation generation performance"""
    print("🚀 Testing Parallelized Conversation Generation")
    print("=" * 60)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Check agents
    print("\n🤖 Checking agents...")
    response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
    if response.status_code == 200:
        agents = response.json()
        print(f"   Found {len(agents)} agents")
        if len(agents) < 2:
            print("   ⚠️ Need at least 2 agents for conversation generation")
            return
    else:
        print(f"   ❌ Failed to get agents: {response.status_code}")
        return
    
    # Test conversation generation timing
    print("\n⚡ Testing conversation generation performance...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=60)
        end_time = time.time()
        generation_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Conversation generated in {generation_time:.2f} seconds")
            
            # Check if it meets the target time
            if generation_time <= 15:
                print(f"   🎯 EXCELLENT: Within target time (≤15s)")
            elif generation_time <= 30:
                print(f"   ✅ GOOD: Reasonable time (≤30s)")
            else:
                print(f"   ⚠️ SLOW: Exceeds target time (>30s)")
            
            # Get conversation details
            conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
            if conv_response.status_code == 200:
                conversations = conv_response.json()
                if conversations:
                    latest = conversations[-1]
                    messages = latest.get('messages', [])
                    unique_agents = set(msg.get('agent_name', '') for msg in messages)
                    
                    print(f"   📊 Generated {len(messages)} messages from {len(unique_agents)} agents")
                    print(f"   👥 Participating agents: {list(unique_agents)[:3]}...")
                    
                    # Check message quality
                    quality_count = sum(1 for msg in messages if 50 <= len(msg.get('message', '')) <= 500)
                    print(f"   📝 Message quality: {quality_count}/{len(messages)} messages have good length")
                    
        else:
            print(f"   ❌ Failed to generate conversation: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        generation_time = end_time - start_time
        print(f"   ⏰ Request timed out after {generation_time:.2f} seconds")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_conversation_generation()