#!/usr/bin/env python3
"""
Focused debugging test for conversation generation issues
"""

import requests
import json
import time

# Use localhost since external URL has timeout issues
API_URL = "http://localhost:8001/api"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def main():
    print("🔍 FOCUSED CONVERSATION GENERATION DEBUG")
    print("=" * 60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # 1. Check current state
    print("\n1. 📊 Current State Analysis")
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            conversations = response.json()
            total_messages = 0
            agent_message_counts = {}
            
            print(f"  - Total conversations: {len(conversations)}")
            
            # Analyze all messages
            all_messages = []
            for conv in conversations:
                messages = conv.get("messages", [])
                total_messages += len(messages)
                all_messages.extend(messages)
                
                for msg in messages:
                    agent_name = msg.get("agent_name", "Unknown")
                    agent_message_counts[agent_name] = agent_message_counts.get(agent_name, 0) + 1
            
            print(f"  - Total messages: {total_messages}")
            print(f"  - Agent distribution:")
            for agent, count in agent_message_counts.items():
                print(f"    • {agent}: {count} messages")
            
            # Check for consecutive message patterns
            print(f"\n  🔍 Consecutive Message Analysis:")
            consecutive_issues = []
            consecutive_counts = {}
            
            for i in range(len(all_messages) - 1):
                current_agent = all_messages[i].get("agent_name")
                next_agent = all_messages[i + 1].get("agent_name")
                
                if current_agent == next_agent:
                    if current_agent not in consecutive_counts:
                        consecutive_counts[current_agent] = []
                    
                    # Find the length of this consecutive sequence
                    seq_length = 2  # At least 2 consecutive
                    j = i + 2
                    while j < len(all_messages) and all_messages[j].get("agent_name") == current_agent:
                        seq_length += 1
                        j += 1
                    
                    consecutive_counts[current_agent].append(seq_length)
                    consecutive_issues.append(f"{current_agent}: {seq_length} consecutive messages starting at position {i}")
                    
                    # Skip ahead to avoid double counting
                    i = j - 1
            
            if consecutive_issues:
                print(f"    ⚠️ CONSECUTIVE MESSAGE ISSUES FOUND:")
                for issue in consecutive_issues[:10]:  # Show first 10
                    print(f"      • {issue}")
                
                print(f"    📊 Summary by agent:")
                for agent, sequences in consecutive_counts.items():
                    max_consecutive = max(sequences)
                    total_sequences = len(sequences)
                    print(f"      • {agent}: {total_sequences} sequences, max {max_consecutive} consecutive")
            else:
                print(f"    ✅ No consecutive message issues found")
                
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error analyzing current state: {e}")
        return
    
    # 2. Test single conversation generation
    print(f"\n2. 🧪 Single Conversation Generation Test")
    try:
        print("  📤 Calling /api/conversation/generate...")
        start_time = time.time()
        
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"  ⏱️ Response time: {response_time:.2f} seconds")
        print(f"  📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # The endpoint returns the conversation object directly, not wrapped
            conversation = data
            messages = conversation.get("messages", [])
            
            print(f"  ✅ Generated {len(messages)} messages")
            print(f"  📋 Conversation details:")
            print(f"    - ID: {conversation.get('id')}")
            print(f"    - Round: {conversation.get('round_number')}")
            print(f"    - Time period: {conversation.get('time_period')}")
            
            # Analyze this generation's agent distribution
            gen_agent_counts = {}
            for msg in messages:
                agent_name = msg.get("agent_name", "Unknown")
                gen_agent_counts[agent_name] = gen_agent_counts.get(agent_name, 0) + 1
            
            print(f"  📊 Agent distribution in this generation:")
            for agent, count in gen_agent_counts.items():
                print(f"    • {agent}: {count} messages")
            
            # Check for consecutive messages in this generation
            gen_consecutive = []
            for i in range(len(messages) - 1):
                if messages[i].get("agent_name") == messages[i + 1].get("agent_name"):
                    gen_consecutive.append(f"{messages[i].get('agent_name')} at positions {i}-{i+1}")
            
            if gen_consecutive:
                print(f"  ⚠️ CONSECUTIVE ISSUES IN THIS GENERATION:")
                for issue in gen_consecutive:
                    print(f"    • {issue}")
            else:
                print(f"  ✅ No consecutive issues in this generation")
                
            # Show actual message sequence
            print(f"  📝 Message sequence:")
            for i, msg in enumerate(messages):
                agent_name = msg.get("agent_name", "Unknown")
                message_preview = msg.get("message", "")[:50] + "..." if len(msg.get("message", "")) > 50 else msg.get("message", "")
                print(f"    {i+1}. {agent_name}: {message_preview}")
                
        else:
            print(f"  ❌ Generation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error during generation test: {e}")
    
    # 3. Check simulation state
    print(f"\n3. ⚙️ Simulation State Check")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        if response.status_code == 200:
            state = response.json()
            print(f"  ✅ Simulation state:")
            print(f"    - Day: {state.get('current_day')}")
            print(f"    - Time period: {state.get('current_time_period')}")
            print(f"    - Active: {state.get('is_active')}")
            print(f"    - Scenario: {state.get('scenario', 'N/A')}")
        else:
            print(f"  ❌ Failed to get simulation state: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
    
    # 4. Check agents
    print(f"\n4. 🤖 Agent Check")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            print(f"  ✅ Found {len(agents)} agents:")
            for agent in agents:
                print(f"    • {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
        else:
            print(f"  ❌ Failed to get agents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
    
    print(f"\n" + "=" * 60)
    print("🏁 DEBUG TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()