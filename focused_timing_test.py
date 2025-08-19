#!/usr/bin/env python3
"""
FOCUSED MESSAGE TIMING & AGENT ALTERNATION TEST

Testing the specific issues reported:
1. Message timing issues (first/second messages slow, then bursts)
2. Agent alternation issues (same agents in a row instead of A→B→C)
"""

import requests
import json
import time
import os
from datetime import datetime
from collections import defaultdict

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_authentication():
    """Test authentication with longer timeout"""
    print("🔐 Testing Authentication...")
    
    session = requests.Session()
    
    try:
        login_data = {
            "email": "dino@cytonic.com", 
            "password": "Observerinho8"
        }
        
        response = session.post(f"{API_BASE}/auth/login", 
                               json=login_data, 
                               timeout=30)  # Longer timeout
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            user_data = data.get('user', {})
            
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
            print(f"✅ Authenticated as {user_data.get('name', 'Unknown')}")
            return session, user_data.get('id')
        else:
            print(f"❌ Auth failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return None, None

def test_message_streaming():
    """Test the /api/messages/stream endpoint for progressive delivery"""
    print("\n📡 Testing Message Streaming...")
    
    session, user_id = test_authentication()
    if not session:
        return
    
    try:
        response = session.get(f"{API_BASE}/messages/stream", timeout=15)
        
        if response.status_code == 200:
            stream_data = response.json()
            message_count = len(stream_data) if isinstance(stream_data, list) else 0
            
            print(f"✅ Stream endpoint returned {message_count} messages")
            
            if message_count > 0:
                # Analyze first few messages for timing patterns
                for i, msg in enumerate(stream_data[:5]):
                    if isinstance(msg, dict):
                        agent_name = msg.get('agent_name', 'Unknown')
                        timestamp = msg.get('timestamp', 'No timestamp')
                        message_preview = msg.get('message', '')[:50] + '...'
                        print(f"   Message {i+1}: {agent_name} at {timestamp}")
                        print(f"      Content: {message_preview}")
            else:
                print("⚠️ No messages in stream")
                
        else:
            print(f"❌ Stream endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stream test error: {str(e)}")

def test_conversation_generation_timing():
    """Test conversation generation timing"""
    print("\n⏱️ Testing Conversation Generation Timing...")
    
    session, user_id = test_authentication()
    if not session:
        return
    
    # Test 3 conversation generations to measure timing
    timing_results = []
    
    for i in range(3):
        print(f"   Generating conversation {i+1}/3...")
        
        start_time = time.time()
        
        try:
            response = session.post(f"{API_BASE}/conversation/generate", 
                                   json={}, 
                                   timeout=60)  # 1 minute timeout
            
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                timing_results.append(generation_time)
                print(f"   ✅ Generated in {generation_time:.2f}s")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            timeout_time = time.time() - start_time
            print(f"   ⏰ Timed out after {timeout_time:.2f}s")
            
        except Exception as e:
            error_time = time.time() - start_time
            print(f"   ❌ Error after {error_time:.2f}s: {str(e)}")
        
        # Wait between generations
        if i < 2:
            time.sleep(3)
    
    # Analyze timing results
    if timing_results:
        avg_time = sum(timing_results) / len(timing_results)
        min_time = min(timing_results)
        max_time = max(timing_results)
        
        print(f"\n📊 Timing Analysis:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Min: {min_time:.2f}s") 
        print(f"   Max: {max_time:.2f}s")
        
        # Check for reported issue: first messages taking very long
        if timing_results[0] > 30:
            print(f"   🚨 CONFIRMED: First message took {timing_results[0]:.2f}s (>30s)")
        
        if len(timing_results) > 1 and timing_results[1] > 30:
            print(f"   🚨 CONFIRMED: Second message took {timing_results[1]:.2f}s (>30s)")
            
        if avg_time > 20:
            print(f"   ⚠️ SLOW: Average generation time {avg_time:.2f}s is high")
    else:
        print("   ❌ No successful generations to analyze")

def test_agent_alternation():
    """Test agent alternation patterns in conversations"""
    print("\n🤖 Testing Agent Alternation Patterns...")
    
    session, user_id = test_authentication()
    if not session:
        return
    
    try:
        response = session.get(f"{API_BASE}/conversations", timeout=15)
        
        if response.status_code == 200:
            conversations = response.json()
            
            if not conversations:
                print("   ⚠️ No conversations found")
                return
                
            print(f"   Analyzing {len(conversations)} conversations...")
            
            # Analyze agent sequences
            all_sequences = []
            consecutive_same_agent = 0
            total_messages = 0
            agent_counts = defaultdict(int)
            
            for conv in conversations:
                if 'messages' in conv and conv['messages']:
                    sequence = []
                    prev_agent = None
                    
                    for msg in conv['messages']:
                        agent_name = msg.get('agent_name', 'Unknown')
                        sequence.append(agent_name)
                        agent_counts[agent_name] += 1
                        total_messages += 1
                        
                        # Check for consecutive same agent
                        if prev_agent == agent_name:
                            consecutive_same_agent += 1
                            
                        prev_agent = agent_name
                    
                    all_sequences.append(sequence)
            
            # Calculate statistics
            consecutive_percentage = (consecutive_same_agent / total_messages * 100) if total_messages > 0 else 0
            unique_agents = len(agent_counts)
            
            print(f"\n📊 Agent Alternation Analysis:")
            print(f"   Total messages: {total_messages}")
            print(f"   Unique agents: {unique_agents}")
            print(f"   Consecutive same-agent messages: {consecutive_same_agent} ({consecutive_percentage:.1f}%)")
            print(f"   Agent distribution: {dict(agent_counts)}")
            
            # Check for the reported alternation issue
            if consecutive_percentage > 30:
                print(f"   🚨 CONFIRMED ALTERNATION ISSUE: {consecutive_percentage:.1f}% consecutive same-agent messages")
                print("   Expected: Agents should alternate (A→B→C→A→B→C)")
            elif consecutive_percentage > 15:
                print(f"   ⚠️ POOR ALTERNATION: {consecutive_percentage:.1f}% consecutive same-agent messages")
            else:
                print(f"   ✅ Good alternation: {consecutive_percentage:.1f}% consecutive same-agent messages")
            
            # Show some example sequences
            print(f"\n   Example conversation sequences:")
            for i, seq in enumerate(all_sequences[:3]):
                if len(seq) > 1:
                    sequence_str = " → ".join(seq[:10])  # First 10 messages
                    if len(seq) > 10:
                        sequence_str += "..."
                    print(f"   Conversation {i+1}: {sequence_str}")
                    
        else:
            print(f"   ❌ Cannot access conversations: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Agent alternation test error: {str(e)}")

def test_auto_conversation_intervals():
    """Test auto-conversation system for message bursting"""
    print("\n🔄 Testing Auto-Conversation System...")
    
    session, user_id = test_authentication()
    if not session:
        return
    
    try:
        # Check auto-conversation status
        response = session.get(f"{API_BASE}/simulation/auto-status", timeout=10)
        
        if response.status_code == 200:
            auto_status = response.json()
            auto_conversations = auto_status.get('auto_conversations', False)
            interval = auto_status.get('conversation_interval', 0)
            
            print(f"   Auto-conversations enabled: {auto_conversations}")
            print(f"   Configured interval: {interval} seconds")
            
            if not auto_conversations:
                print("   Enabling auto-conversations for testing...")
                response = session.post(f"{API_BASE}/simulation/toggle-auto-mode", 
                                       json={"auto_conversations": True}, 
                                       timeout=10)
                
                if response.status_code == 200:
                    print("   ✅ Auto-conversations enabled")
                else:
                    print(f"   ❌ Failed to enable: {response.status_code}")
                    return
        else:
            print(f"   ❌ Cannot check auto-status: {response.status_code}")
            return
            
        # Get baseline conversation count
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        baseline_count = len(response.json()) if response.status_code == 200 else 0
        
        print(f"   Baseline conversations: {baseline_count}")
        
        # Start simulation and monitor for bursting
        print("   Starting simulation and monitoring for 60 seconds...")
        
        response = session.post(f"{API_BASE}/simulation/start", json={}, timeout=30)
        if response.status_code != 200:
            print(f"   ❌ Failed to start simulation: {response.status_code}")
            return
        
        # Monitor every 10 seconds for 60 seconds
        monitoring_data = []
        start_time = time.time()
        
        for check in range(6):  # 6 checks over 60 seconds
            time.sleep(10)
            elapsed = time.time() - start_time
            
            try:
                response = session.get(f"{API_BASE}/conversations", timeout=10)
                if response.status_code == 200:
                    current_count = len(response.json())
                    new_messages = current_count - baseline_count
                    
                    monitoring_data.append({
                        'elapsed': elapsed,
                        'total': current_count,
                        'new': new_messages
                    })
                    
                    print(f"      {elapsed:.0f}s: {current_count} total ({new_messages} new)")
                    
            except Exception as e:
                print(f"      {elapsed:.0f}s: Error - {str(e)}")
        
        # Analyze for message bursting
        if len(monitoring_data) >= 2:
            increases = []
            for i in range(1, len(monitoring_data)):
                increase = monitoring_data[i]['new'] - monitoring_data[i-1]['new']
                if increase > 0:
                    increases.append({
                        'time': monitoring_data[i]['elapsed'],
                        'increase': increase
                    })
            
            # Check for bursting (6+ messages at once)
            bursts = [inc for inc in increases if inc['increase'] >= 6]
            
            if bursts:
                print(f"\n   🚨 CONFIRMED MESSAGE BURSTING:")
                for burst in bursts:
                    print(f"      {burst['increase']} messages appeared at {burst['time']:.0f}s")
            else:
                print(f"\n   ✅ No message bursting detected")
                if increases:
                    max_increase = max(inc['increase'] for inc in increases)
                    print(f"      Largest single increase: {max_increase} messages")
        else:
            print("   ⚠️ Insufficient monitoring data")
            
    except Exception as e:
        print(f"   ❌ Auto-conversation test error: {str(e)}")

def main():
    """Run focused timing and alternation tests"""
    print("🔍 FOCUSED MESSAGE TIMING & AGENT ALTERNATION TEST")
    print("=" * 60)
    print("Testing specific user-reported issues:")
    print("1. First/second messages take very long")
    print("2. Then 6+ messages appear at once")  
    print("3. Same agents in a row instead of alternating")
    print("=" * 60)
    
    # Run focused tests
    test_message_streaming()
    test_conversation_generation_timing()
    test_agent_alternation()
    test_auto_conversation_intervals()
    
    print("\n" + "=" * 60)
    print("🔍 FOCUSED TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()