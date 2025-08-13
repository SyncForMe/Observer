#!/usr/bin/env python3
"""
Comprehensive debugging test for the specific issues mentioned in the review request:
1. Agents generating 3 messages in a row instead of 1 message per agent
2. Messages stopped generating at 81 messages  
3. Stop button issues and sudden jump to 104 messages
4. No time progression from Day 1 Evening to Day 2 Morning
"""

import requests
import json
import time

API_URL = "http://localhost:8001/api"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def analyze_all_conversations(headers):
    """Analyze all conversations for consecutive message patterns"""
    print("🔍 ANALYZING ALL CONVERSATIONS FOR CONSECUTIVE MESSAGE PATTERNS")
    print("=" * 80)
    
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get conversations: {response.status_code}")
        return
    
    conversations = response.json()
    print(f"📊 Total conversations: {len(conversations)}")
    
    # Flatten all messages with conversation context
    all_messages = []
    conversation_message_counts = []
    
    for i, conv in enumerate(conversations):
        messages = conv.get("messages", [])
        conversation_message_counts.append(len(messages))
        
        print(f"\n📋 Conversation {i+1}:")
        print(f"  - ID: {conv.get('id', 'N/A')}")
        print(f"  - Round: {conv.get('round_number', 'N/A')}")
        print(f"  - Time period: {conv.get('time_period', 'N/A')}")
        print(f"  - Messages: {len(messages)}")
        
        # Check for consecutive messages within this conversation
        consecutive_in_conv = []
        for j in range(len(messages) - 1):
            if messages[j].get("agent_name") == messages[j + 1].get("agent_name"):
                consecutive_in_conv.append({
                    "agent": messages[j].get("agent_name"),
                    "positions": [j, j + 1],
                    "messages": [messages[j].get("message", "")[:50], messages[j + 1].get("message", "")[:50]]
                })
        
        if consecutive_in_conv:
            print(f"  ⚠️ CONSECUTIVE MESSAGES FOUND:")
            for issue in consecutive_in_conv:
                print(f"    • {issue['agent']} at positions {issue['positions']}")
                print(f"      Msg 1: {issue['messages'][0]}...")
                print(f"      Msg 2: {issue['messages'][1]}...")
        else:
            print(f"  ✅ No consecutive messages in this conversation")
        
        # Add messages to global list with conversation context
        for msg in messages:
            all_messages.append({
                "conversation_id": conv.get('id'),
                "conversation_round": conv.get('round_number'),
                "time_period": conv.get('time_period'),
                "agent_name": msg.get("agent_name"),
                "message": msg.get("message", ""),
                "timestamp": msg.get("timestamp")
            })
    
    # Global analysis
    total_messages = len(all_messages)
    print(f"\n📈 GLOBAL ANALYSIS:")
    print(f"  - Total messages across all conversations: {total_messages}")
    print(f"  - Average messages per conversation: {total_messages / len(conversations) if conversations else 0:.1f}")
    print(f"  - Message counts per conversation: {conversation_message_counts}")
    
    # Check for the specific "81 messages" and "104 messages" issue
    if total_messages >= 81:
        print(f"  ⚠️ Message count ({total_messages}) is at or above the reported stopping point (81)")
        if total_messages >= 104:
            print(f"  ⚠️ Message count ({total_messages}) matches or exceeds the reported jump to 104 messages")
    
    # Agent distribution analysis
    agent_counts = {}
    for msg in all_messages:
        agent = msg["agent_name"]
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    print(f"\n👥 AGENT MESSAGE DISTRIBUTION:")
    for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {agent}: {count} messages")
    
    # Look for agents with significantly more messages (like Dr. Satoshi Nakamura with 5 consecutive)
    max_messages = max(agent_counts.values()) if agent_counts else 0
    avg_messages = sum(agent_counts.values()) / len(agent_counts) if agent_counts else 0
    
    print(f"\n📊 MESSAGE DISTRIBUTION ANALYSIS:")
    print(f"  - Maximum messages by any agent: {max_messages}")
    print(f"  - Average messages per agent: {avg_messages:.1f}")
    
    agents_with_high_counts = {agent: count for agent, count in agent_counts.items() if count > avg_messages * 1.5}
    if agents_with_high_counts:
        print(f"  ⚠️ AGENTS WITH UNUSUALLY HIGH MESSAGE COUNTS:")
        for agent, count in agents_with_high_counts.items():
            print(f"    • {agent}: {count} messages ({count - avg_messages:.1f} above average)")
    
    # Analyze consecutive patterns across all conversations
    print(f"\n🔍 GLOBAL CONSECUTIVE MESSAGE ANALYSIS:")
    consecutive_sequences = []
    current_agent = None
    current_sequence_length = 1
    current_sequence_start = 0
    
    for i, msg in enumerate(all_messages):
        agent = msg["agent_name"]
        
        if agent == current_agent:
            current_sequence_length += 1
        else:
            # End of sequence
            if current_sequence_length > 1:
                consecutive_sequences.append({
                    "agent": current_agent,
                    "length": current_sequence_length,
                    "start_index": current_sequence_start,
                    "end_index": i - 1,
                    "conversations": list(set([all_messages[j]["conversation_round"] for j in range(current_sequence_start, i)]))
                })
            
            current_agent = agent
            current_sequence_length = 1
            current_sequence_start = i
    
    # Handle the last sequence
    if current_sequence_length > 1:
        consecutive_sequences.append({
            "agent": current_agent,
            "length": current_sequence_length,
            "start_index": current_sequence_start,
            "end_index": len(all_messages) - 1,
            "conversations": list(set([all_messages[j]["conversation_round"] for j in range(current_sequence_start, len(all_messages))]))
        })
    
    if consecutive_sequences:
        print(f"  ⚠️ CONSECUTIVE MESSAGE SEQUENCES FOUND:")
        for seq in consecutive_sequences:
            print(f"    • {seq['agent']}: {seq['length']} consecutive messages (positions {seq['start_index']}-{seq['end_index']})")
            print(f"      Spans conversations: {seq['conversations']}")
            
            # Show the specific messages in the sequence
            print(f"      Messages:")
            for j in range(seq['start_index'], min(seq['end_index'] + 1, seq['start_index'] + 5)):  # Show first 5
                msg_preview = all_messages[j]["message"][:60] + "..." if len(all_messages[j]["message"]) > 60 else all_messages[j]["message"]
                print(f"        {j+1}. {msg_preview}")
            if seq['length'] > 5:
                print(f"        ... and {seq['length'] - 5} more messages")
    else:
        print(f"  ✅ No consecutive message sequences found globally")
    
    return {
        "total_messages": total_messages,
        "total_conversations": len(conversations),
        "consecutive_sequences": consecutive_sequences,
        "agent_counts": agent_counts,
        "conversation_message_counts": conversation_message_counts
    }

def test_time_progression(headers):
    """Test time progression system"""
    print(f"\n⏰ TIME PROGRESSION ANALYSIS")
    print("=" * 80)
    
    # Get simulation state
    response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    if response.status_code == 200:
        state = response.json()
        print(f"📊 Current simulation state:")
        print(f"  - Day: {state.get('current_day')}")
        print(f"  - Time period: {state.get('current_time_period')}")
        print(f"  - Active: {state.get('is_active')}")
        
        # Get conversations to analyze time progression
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            conversations = response.json()
            
            print(f"\n📋 Time progression in conversations:")
            time_periods_seen = set()
            for i, conv in enumerate(conversations):
                time_period = conv.get('time_period', 'Unknown')
                time_periods_seen.add(time_period)
                print(f"  Conversation {i+1}: {time_period}")
            
            print(f"\n📈 Time progression analysis:")
            print(f"  - Unique time periods seen: {len(time_periods_seen)}")
            print(f"  - Time periods: {sorted(time_periods_seen)}")
            
            # Check for the specific issue: "No time progression from Day 1 Evening to Day 2 Morning"
            has_day1_evening = any("Day 1" in tp and "Evening" in tp for tp in time_periods_seen)
            has_day2_morning = any("Day 2" in tp and "Morning" in tp for tp in time_periods_seen)
            
            if has_day1_evening and not has_day2_morning:
                print(f"  ⚠️ ISSUE CONFIRMED: Found Day 1 Evening but no Day 2 Morning progression")
            elif has_day1_evening and has_day2_morning:
                print(f"  ✅ Time progression working: Found both Day 1 Evening and Day 2 Morning")
            else:
                print(f"  ℹ️ No Day 1 Evening found in current conversations")
        else:
            print(f"❌ Failed to get conversations for time analysis")
    else:
        print(f"❌ Failed to get simulation state")

def test_simulation_control(headers):
    """Test simulation start/stop functionality"""
    print(f"\n⚙️ SIMULATION CONTROL TESTING")
    print("=" * 80)
    
    # Get initial state
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    initial_message_count = 0
    if response.status_code == 200:
        conversations = response.json()
        initial_message_count = sum(len(conv.get("messages", [])) for conv in conversations)
        print(f"📊 Initial message count: {initial_message_count}")
    
    # Test pause
    print(f"\n⏸️ Testing simulation pause...")
    response = requests.post(f"{API_URL}/simulation/pause", headers=headers)
    if response.status_code == 200:
        print(f"✅ Simulation paused successfully")
        
        # Check if conversation generation is blocked while paused
        print(f"🚫 Testing conversation generation while paused...")
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"  ⚠️ Generated {len(messages)} messages while paused (unexpected)")
        else:
            print(f"  ✅ Conversation generation blocked while paused (expected)")
    else:
        print(f"❌ Failed to pause simulation: {response.status_code}")
    
    # Test resume
    print(f"\n▶️ Testing simulation resume...")
    response = requests.post(f"{API_URL}/simulation/resume", headers=headers)
    if response.status_code == 200:
        print(f"✅ Simulation resumed successfully")
        
        # Test conversation generation after resume
        print(f"📤 Testing conversation generation after resume...")
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"  ✅ Generated {len(messages)} messages after resume")
        else:
            print(f"  ❌ Failed to generate after resume: {response.status_code}")
    else:
        print(f"❌ Failed to resume simulation: {response.status_code}")
    
    # Check final message count
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        final_message_count = sum(len(conv.get("messages", [])) for conv in conversations)
        print(f"\n📊 Final message count: {final_message_count}")
        print(f"📈 Messages added during test: {final_message_count - initial_message_count}")

def main():
    print("🔍 COMPREHENSIVE CONVERSATION GENERATION DEBUG")
    print("Investigating specific issues from user report:")
    print("1. Agents generating 3 messages in a row instead of 1 message per agent")
    print("2. Messages stopped generating at 81 messages")
    print("3. Stop button issues and sudden jump to 104 messages") 
    print("4. No time progression from Day 1 Evening to Day 2 Morning")
    print("=" * 80)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Run comprehensive analysis
    analysis_results = analyze_all_conversations(headers)
    
    # Test time progression
    test_time_progression(headers)
    
    # Test simulation control
    test_simulation_control(headers)
    
    # Final summary
    print(f"\n" + "=" * 80)
    print("🏁 COMPREHENSIVE DEBUG SUMMARY")
    print("=" * 80)
    
    print(f"📊 FINDINGS:")
    print(f"  - Total messages: {analysis_results['total_messages']}")
    print(f"  - Total conversations: {analysis_results['total_conversations']}")
    print(f"  - Consecutive sequences found: {len(analysis_results['consecutive_sequences'])}")
    
    # Check specific issues
    print(f"\n🔍 SPECIFIC ISSUE ANALYSIS:")
    
    # Issue 1: 3 messages in a row
    three_plus_sequences = [seq for seq in analysis_results['consecutive_sequences'] if seq['length'] >= 3]
    if three_plus_sequences:
        print(f"  ❌ ISSUE 1 CONFIRMED: Found {len(three_plus_sequences)} sequences of 3+ consecutive messages")
        for seq in three_plus_sequences:
            print(f"    • {seq['agent']}: {seq['length']} consecutive messages")
    else:
        print(f"  ✅ ISSUE 1 NOT FOUND: No sequences of 3+ consecutive messages")
    
    # Issue 2: Messages stopped at 81
    if analysis_results['total_messages'] >= 81:
        print(f"  ⚠️ ISSUE 2 RELEVANT: Current message count ({analysis_results['total_messages']}) is at/above 81")
    else:
        print(f"  ℹ️ ISSUE 2 NOT APPLICABLE: Current message count ({analysis_results['total_messages']}) is below 81")
    
    # Issue 3: Jump to 104 messages
    if analysis_results['total_messages'] >= 104:
        print(f"  ⚠️ ISSUE 3 RELEVANT: Current message count ({analysis_results['total_messages']}) is at/above 104")
    else:
        print(f"  ℹ️ ISSUE 3 NOT APPLICABLE: Current message count ({analysis_results['total_messages']}) is below 104")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()