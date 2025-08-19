#!/usr/bin/env python3
"""
INVESTIGATE STREAM CONVERSION
Check how streaming messages are being converted to conversations
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

def check_message_stream(session):
    """Check the message stream collection"""
    print("\n📡 CHECKING MESSAGE STREAM COLLECTION")
    print("=" * 50)
    
    try:
        response = session.get(f"{API_BASE}/messages/stream", timeout=10)
        
        if response.status_code == 200:
            messages = response.json()
            print(f"Stream contains {len(messages)} messages")
            
            if messages:
                # Group by conversation_id
                conversations = {}
                for msg in messages:
                    if isinstance(msg, dict):
                        conv_id = msg.get('conversation_id', 'unknown')
                        if conv_id not in conversations:
                            conversations[conv_id] = []
                        conversations[conv_id].append(msg)
                    else:
                        print(f"  Warning: Non-dict message: {type(msg)} - {msg}")
                
                print(f"\n📊 STREAM CONVERSATIONS:")
                for conv_id, msgs in conversations.items():
                    print(f"  {conv_id}: {len(msgs)} messages")
                    
                    # Check agent sequence in this stream conversation
                    agent_sequence = []
                    for msg in msgs:
                        agent_name = msg.get('agent_name', 'Unknown')
                        if agent_name != 'Observer (You)':
                            agent_sequence.append(agent_name)
                    
                    print(f"    Agent sequence: {' → '.join(agent_sequence)}")
                    
                    # Check for violations in this stream
                    violations = []
                    for i in range(1, len(agent_sequence)):
                        if agent_sequence[i] == agent_sequence[i-1]:
                            violations.append(f"Position {i+1}: {agent_sequence[i-1]} → {agent_sequence[i]}")
                    
                    if violations:
                        print(f"    ❌ VIOLATIONS: {'; '.join(violations)}")
                    else:
                        print(f"    ✅ Perfect alternation")
                    
                    # Check message indexes
                    indexes = [msg.get('message_index', 0) for msg in msgs]
                    print(f"    Message indexes: {indexes}")
                    print()
            
        else:
            print(f"❌ Cannot access message stream: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stream check error: {str(e)}")

def check_conversations_vs_stream(session):
    """Compare conversations collection with message stream"""
    print("\n🔍 COMPARING CONVERSATIONS VS STREAM")
    print("=" * 50)
    
    try:
        # Get conversations
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        if response.status_code == 200:
            conversations = response.json()
            print(f"Conversations collection: {len(conversations)} conversations")
            
            if conversations:
                latest_conv = conversations[-1]
                conv_messages = latest_conv.get('messages', [])
                print(f"Latest conversation has {len(conv_messages)} messages")
                
                # Get agent sequence from conversation
                conv_agent_sequence = []
                for msg in conv_messages:
                    agent_name = msg.get('agent_name', 'Unknown')
                    if agent_name != 'Observer (You)':
                        conv_agent_sequence.append(agent_name)
                
                print(f"Conversation agent sequence: {' → '.join(conv_agent_sequence)}")
        
        # Get stream messages
        response = session.get(f"{API_BASE}/messages/stream", timeout=10)
        if response.status_code == 200:
            stream_messages = response.json()
            print(f"Stream collection: {len(stream_messages)} messages")
            
            if stream_messages:
                # Get agent sequence from stream
                stream_agent_sequence = []
                for msg in stream_messages:
                    agent_name = msg.get('agent_name', 'Unknown')
                    if agent_name != 'Observer (You)':
                        stream_agent_sequence.append(agent_name)
                
                print(f"Stream agent sequence: {' → '.join(stream_agent_sequence)}")
                
                # Check if they match
                if conv_agent_sequence == stream_agent_sequence:
                    print("✅ Conversation and stream sequences MATCH")
                else:
                    print("❌ Conversation and stream sequences DO NOT MATCH")
                    print("This suggests the issue is in the conversion process")
        
    except Exception as e:
        print(f"❌ Comparison error: {str(e)}")

def main():
    print("🔍 INVESTIGATE STREAM CONVERSION")
    print("=" * 50)
    print("Checking how streaming messages become conversations")
    print()
    
    # Authenticate
    session = authenticate()
    if not session:
        print("🚨 Cannot proceed without authentication")
        return
    
    # Check message stream
    check_message_stream(session)
    
    # Compare conversations vs stream
    check_conversations_vs_stream(session)
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()