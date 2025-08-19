#!/usr/bin/env python3
"""
STREAMING ENDPOINT AND DATABASE ANALYSIS

Testing the /api/messages/stream endpoint and analyzing database patterns
for the reported timing and alternation issues.
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

def authenticate():
    """Authenticate and return session"""
    session = requests.Session()
    
    try:
        login_data = {
            "email": "dino@cytonic.com", 
            "password": "Observerinho8"
        }
        
        response = session.post(f"{API_BASE}/auth/login", 
                               json=login_data, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
            return session
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return None

def test_streaming_endpoint():
    """Test the /api/messages/stream endpoint"""
    print("📡 TESTING STREAMING ENDPOINT")
    print("=" * 50)
    
    session = authenticate()
    if not session:
        return
    
    try:
        print("Testing /api/messages/stream endpoint...")
        response = session.get(f"{API_BASE}/messages/stream", timeout=20)
        
        if response.status_code == 200:
            stream_data = response.json()
            
            if isinstance(stream_data, list):
                print(f"✅ Stream returned {len(stream_data)} messages")
                
                # Analyze message timing patterns
                timestamps = []
                agents = []
                
                for i, msg in enumerate(stream_data):
                    if isinstance(msg, dict):
                        timestamp = msg.get('timestamp')
                        agent_name = msg.get('agent_name', 'Unknown')
                        message_preview = msg.get('message', '')[:60] + '...'
                        
                        agents.append(agent_name)
                        
                        if timestamp:
                            timestamps.append(timestamp)
                            
                        print(f"   Message {i+1}: {agent_name}")
                        print(f"      Time: {timestamp}")
                        print(f"      Content: {message_preview}")
                        print()
                
                # Analyze agent sequence in stream
                if len(agents) > 1:
                    consecutive_same = 0
                    for i in range(1, len(agents)):
                        if agents[i] == agents[i-1]:
                            consecutive_same += 1
                    
                    consecutive_percentage = (consecutive_same / len(agents) * 100)
                    print(f"📊 Stream Agent Analysis:")
                    print(f"   Consecutive same-agent: {consecutive_same}/{len(agents)} ({consecutive_percentage:.1f}%)")
                    
                    if consecutive_percentage > 30:
                        print(f"   🚨 STREAM CONFIRMS ALTERNATION ISSUE")
                    else:
                        print(f"   ✅ Stream shows good alternation")
                
                # Analyze timestamp patterns
                if len(timestamps) > 1:
                    print(f"\n📊 Stream Timing Analysis:")
                    
                    # Try to parse timestamps and calculate gaps
                    parsed_timestamps = []
                    for ts in timestamps:
                        try:
                            if isinstance(ts, str):
                                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                parsed_timestamps.append(dt)
                            elif isinstance(ts, dict) and '$date' in ts:
                                dt = datetime.fromisoformat(ts['$date'].replace('Z', '+00:00'))
                                parsed_timestamps.append(dt)
                        except:
                            continue
                    
                    if len(parsed_timestamps) > 1:
                        gaps = []
                        for i in range(1, len(parsed_timestamps)):
                            gap = (parsed_timestamps[i] - parsed_timestamps[i-1]).total_seconds()
                            gaps.append(gap)
                        
                        small_gaps = [g for g in gaps if g < 5]  # Less than 5 seconds
                        burst_percentage = len(small_gaps) / len(gaps) * 100
                        
                        print(f"   Time gaps between messages: {len(gaps)} gaps analyzed")
                        print(f"   Small gaps (<5s): {len(small_gaps)} ({burst_percentage:.1f}%)")
                        
                        if burst_percentage > 50:
                            print(f"   🚨 STREAM CONFIRMS MESSAGE BURSTING")
                        else:
                            print(f"   ✅ Stream shows progressive delivery")
                    else:
                        print(f"   ⚠️ Could not parse timestamps for gap analysis")
                else:
                    print(f"   ⚠️ Insufficient timestamp data")
                    
            else:
                print(f"⚠️ Stream returned non-list data: {type(stream_data)}")
                
        else:
            print(f"❌ Stream endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Stream test error: {str(e)}")

def test_conversation_database_patterns():
    """Analyze conversation database for patterns"""
    print("\n🗄️ TESTING DATABASE PATTERNS")
    print("=" * 50)
    
    session = authenticate()
    if not session:
        return
    
    try:
        print("Analyzing conversation database patterns...")
        response = session.get(f"{API_BASE}/conversations", timeout=20)
        
        if response.status_code == 200:
            conversations = response.json()
            
            if not conversations:
                print("⚠️ No conversations in database")
                return
                
            print(f"✅ Found {len(conversations)} conversations in database")
            
            # Analyze all messages across all conversations
            all_messages = []
            conversation_patterns = []
            
            for conv in conversations:
                conv_id = conv.get('id', 'unknown')
                round_num = conv.get('round_number', 0)
                time_period = conv.get('time_period', 'unknown')
                
                if 'messages' in conv and conv['messages']:
                    conv_agents = []
                    conv_timestamps = []
                    
                    for msg in conv['messages']:
                        agent_name = msg.get('agent_name', 'Unknown')
                        timestamp = msg.get('timestamp')
                        message_text = msg.get('message', '')
                        
                        all_messages.append({
                            'agent': agent_name,
                            'timestamp': timestamp,
                            'conversation': conv_id,
                            'round': round_num,
                            'time_period': time_period,
                            'message_length': len(message_text)
                        })
                        
                        conv_agents.append(agent_name)
                        if timestamp:
                            conv_timestamps.append(timestamp)
                    
                    conversation_patterns.append({
                        'id': conv_id,
                        'round': round_num,
                        'time_period': time_period,
                        'agents': conv_agents,
                        'timestamps': conv_timestamps,
                        'message_count': len(conv_agents)
                    })
            
            print(f"   Total messages across all conversations: {len(all_messages)}")
            
            # Analyze agent alternation across entire database
            if len(all_messages) > 1:
                consecutive_same = 0
                agent_counts = defaultdict(int)
                
                prev_agent = None
                for msg in all_messages:
                    agent = msg['agent']
                    agent_counts[agent] += 1
                    
                    if prev_agent == agent:
                        consecutive_same += 1
                    prev_agent = agent
                
                consecutive_percentage = (consecutive_same / len(all_messages) * 100)
                
                print(f"\n📊 Database Agent Analysis:")
                print(f"   Total messages: {len(all_messages)}")
                print(f"   Unique agents: {len(agent_counts)}")
                print(f"   Agent distribution: {dict(agent_counts)}")
                print(f"   Consecutive same-agent: {consecutive_same} ({consecutive_percentage:.1f}%)")
                
                if consecutive_percentage > 30:
                    print(f"   🚨 DATABASE CONFIRMS ALTERNATION ISSUE")
                elif consecutive_percentage > 15:
                    print(f"   ⚠️ DATABASE SHOWS POOR ALTERNATION")
                else:
                    print(f"   ✅ Database shows good alternation")
            
            # Analyze conversation round patterns
            if conversation_patterns:
                print(f"\n📊 Conversation Round Analysis:")
                
                round_numbers = [p['round'] for p in conversation_patterns]
                unique_rounds = set(round_numbers)
                
                print(f"   Conversation rounds: {sorted(unique_rounds)}")
                print(f"   Total conversations: {len(conversation_patterns)}")
                
                # Check for multiple conversations per round (potential bursting)
                round_counts = defaultdict(int)
                for round_num in round_numbers:
                    round_counts[round_num] += 1
                
                multiple_per_round = [r for r, count in round_counts.items() if count > 1]
                
                if multiple_per_round:
                    print(f"   🚨 MULTIPLE CONVERSATIONS PER ROUND DETECTED:")
                    for round_num in multiple_per_round:
                        count = round_counts[round_num]
                        print(f"      Round {round_num}: {count} conversations")
                    print(f"   This could explain message bursting!")
                else:
                    print(f"   ✅ One conversation per round (normal pattern)")
            
            # Show detailed conversation sequence examples
            print(f"\n📊 Detailed Conversation Examples:")
            for i, pattern in enumerate(conversation_patterns[:3]):
                agent_sequence = " → ".join(pattern['agents'])
                print(f"   Conversation {i+1} (Round {pattern['round']}):")
                print(f"      Agents: {agent_sequence}")
                print(f"      Time Period: {pattern['time_period']}")
                print(f"      Message Count: {pattern['message_count']}")
                print()
                
        else:
            print(f"❌ Cannot access conversations: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Database analysis error: {str(e)}")

def main():
    """Run streaming and database analysis"""
    print("🔍 STREAMING ENDPOINT AND DATABASE ANALYSIS")
    print("=" * 60)
    print("Investigating:")
    print("- /api/messages/stream progressive delivery")
    print("- Database message patterns and timing")
    print("- Agent alternation in stored data")
    print("=" * 60)
    
    test_streaming_endpoint()
    test_conversation_database_patterns()
    
    print("\n" + "=" * 60)
    print("🔍 STREAMING & DATABASE ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()