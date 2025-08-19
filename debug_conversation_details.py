#!/usr/bin/env python3
"""
DEBUG CONVERSATION DETAILS
Examine the conversation with violations in detail to understand the root cause
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def authenticate():
    """Quick authentication"""
    session = requests.Session()
    
    try:
        login_data = {
            "email": "dino@cytonic.com", 
            "password": "Observerinho8"
        }
        
        response = session.post(f"{API_BASE}/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
            print("✅ Authentication successful")
            return session
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def debug_conversation_details(session):
    """Debug the conversation with violations"""
    print("\n🔍 DEBUGGING CONVERSATION DETAILS")
    print("=" * 60)
    
    try:
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"Found {len(conversations)} conversations")
            
            if conversations:
                # Get the latest conversation (the one with violations)
                latest_conversation = conversations[-1]
                
                print(f"\n📋 CONVERSATION DETAILS:")
                print(f"  ID: {latest_conversation.get('id', 'N/A')}")
                print(f"  Round: {latest_conversation.get('round_number', 'N/A')}")
                print(f"  Scenario: {latest_conversation.get('scenario', 'N/A')}")
                print(f"  Created: {latest_conversation.get('created_at', 'N/A')}")
                
                messages = latest_conversation.get('messages', [])
                print(f"  Total messages: {len(messages)}")
                
                print(f"\n📝 MESSAGE SEQUENCE ANALYSIS:")
                agent_sequence = []
                
                for i, msg in enumerate(messages):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_text = msg.get('message', '')
                    timestamp = msg.get('timestamp', 'N/A')
                    mood = msg.get('mood', 'N/A')
                    
                    if agent_name != 'Observer (You)':
                        agent_sequence.append(agent_name)
                        
                        print(f"  {i+1:2d}. {agent_name}")
                        print(f"      Message: {message_text[:100]}...")
                        print(f"      Timestamp: {timestamp}")
                        print(f"      Mood: {mood}")
                        print()
                
                print(f"🎯 AGENT SEQUENCE: {' → '.join(agent_sequence)}")
                
                # Analyze violations in detail
                print(f"\n❌ VIOLATION ANALYSIS:")
                violations = []
                for i in range(1, len(agent_sequence)):
                    if agent_sequence[i] == agent_sequence[i-1]:
                        violations.append({
                            'position': i,
                            'agent': agent_sequence[i],
                            'previous_agent': agent_sequence[i-1]
                        })
                        print(f"  Position {i+1}: {agent_sequence[i-1]} → {agent_sequence[i]} (VIOLATION)")
                
                print(f"\nTotal violations: {len(violations)}")
                
                # Check if this might be from multiple conversation rounds merged
                print(f"\n🔍 INVESTIGATING POTENTIAL CAUSES:")
                
                # Check timestamps for clustering
                timestamps = []
                for msg in messages:
                    if msg.get('agent_name') != 'Observer (You)':
                        ts = msg.get('timestamp')
                        if ts:
                            timestamps.append(ts)
                
                if len(timestamps) > 1:
                    print(f"  First message timestamp: {timestamps[0]}")
                    print(f"  Last message timestamp: {timestamps[-1]}")
                    
                    # Check for time gaps that might indicate separate generations
                    time_gaps = []
                    for i in range(1, len(timestamps)):
                        try:
                            # Simple string comparison for now
                            if timestamps[i] != timestamps[i-1]:
                                time_gaps.append(f"Gap between message {i} and {i+1}")
                        except:
                            pass
                    
                    if time_gaps:
                        print(f"  Time gaps detected: {len(time_gaps)}")
                    else:
                        print(f"  All messages have similar timestamps")
                
                # Check if this is from observer messages or multiple rounds
                observer_messages = [msg for msg in messages if msg.get('agent_name') == 'Observer (You)']
                if observer_messages:
                    print(f"  Observer messages found: {len(observer_messages)}")
                    print(f"  This might be from observer interactions causing multiple generations")
                
                return True
            else:
                print("No conversations found")
                return False
                
        else:
            print(f"❌ Cannot access conversations: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        return False

def check_message_stream(session):
    """Check the message stream for additional insights"""
    print("\n📡 CHECKING MESSAGE STREAM")
    print("=" * 40)
    
    try:
        response = session.get(f"{API_BASE}/messages/stream", timeout=10)
        
        if response.status_code == 200:
            messages = response.json()
            print(f"Stream contains {len(messages)} messages")
            
            if messages:
                # Check the last 10 messages
                recent_messages = messages[-10:]
                
                print(f"\n📝 RECENT STREAM MESSAGES:")
                for i, msg in enumerate(recent_messages):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_index = msg.get('message_index', 'N/A')
                    conversation_id = msg.get('conversation_id', 'N/A')
                    status = msg.get('status', 'N/A')
                    
                    print(f"  {i+1:2d}. {agent_name} (Index: {message_index}, Status: {status})")
                    print(f"      Conv ID: {conversation_id}")
                
                # Check for alternation in stream
                stream_agents = [msg.get('agent_name') for msg in recent_messages if msg.get('agent_name') != 'Observer (You)']
                print(f"\n🎯 STREAM AGENT SEQUENCE: {' → '.join(stream_agents)}")
                
                # Check for violations in stream
                stream_violations = []
                for i in range(1, len(stream_agents)):
                    if stream_agents[i] == stream_agents[i-1]:
                        stream_violations.append(f"Position {i+1}: {stream_agents[i-1]} → {stream_agents[i]}")
                
                if stream_violations:
                    print(f"❌ STREAM VIOLATIONS: {'; '.join(stream_violations)}")
                else:
                    print(f"✅ Stream shows proper alternation")
            
        else:
            print(f"❌ Cannot access message stream: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stream check error: {str(e)}")

def main():
    print("🔍 DEBUG CONVERSATION DETAILS")
    print("=" * 50)
    print("Investigating the agent alternation violations")
    print()
    
    # Authenticate
    session = authenticate()
    if not session:
        print("🚨 Cannot proceed without authentication")
        return
    
    # Debug conversation details
    debug_conversation_details(session)
    
    # Check message stream
    check_message_stream(session)
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()