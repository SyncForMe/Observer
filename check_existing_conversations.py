#!/usr/bin/env python3
"""
CHECK EXISTING CONVERSATIONS
Analyze existing conversations to identify agent alternation issues.
"""

import requests
import json
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
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def analyze_existing_conversations():
    """Analyze existing conversations for agent alternation issues"""
    print("🔍 ANALYZING EXISTING CONVERSATIONS")
    print("="*60)
    
    # Authenticate
    token = authenticate()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get agents first
    print("\n1. GETTING AGENTS...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents:")
            
            agent_names = []
            for i, agent in enumerate(agents, 1):
                name = agent.get('name', 'Unknown')
                agent_names.append(name)
                print(f"  [{i}] {name}")
            
            # Check for duplicates
            unique_names = set(agent_names)
            if len(agent_names) != len(unique_names):
                print(f"🚨 DUPLICATE AGENTS DETECTED!")
                for name in unique_names:
                    count = agent_names.count(name)
                    if count > 1:
                        print(f"  - '{name}' appears {count} times")
                        
                        # This is likely the root cause
                        print(f"\n🎯 ROOT CAUSE IDENTIFIED:")
                        print(f"   - Agent '{name}' appears {count} times in the agent list")
                        print(f"   - When conversation generation iterates through all agents,")
                        print(f"     it will generate {count} messages from the same agent")
                        print(f"   - This explains why '{name}' sends multiple consecutive messages")
                        return False
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return False
    
    # 2. Get existing conversations
    print(f"\n2. GETTING EXISTING CONVERSATIONS...")
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Found {len(conversations)} conversations")
            
            if not conversations:
                print("ℹ️ No conversations found to analyze")
                return True
            
            # Analyze the most recent conversations
            conversations_to_analyze = conversations[:5]  # Analyze last 5 conversations
            
            total_issues = 0
            
            for i, conv in enumerate(conversations_to_analyze, 1):
                print(f"\n--- CONVERSATION {i} ---")
                messages = conv.get("messages", [])
                round_number = conv.get("round_number", "Unknown")
                scenario = conv.get("scenario", "Unknown")
                
                print(f"Round: {round_number}, Scenario: {scenario[:50]}...")
                print(f"Messages: {len(messages)}")
                
                if messages:
                    # Analyze message sequence
                    agent_sequence = []
                    agent_counts = {}
                    
                    for j, msg in enumerate(messages, 1):
                        agent_name = msg.get("agent_name", "Unknown")
                        agent_sequence.append(agent_name)
                        agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
                        
                        print(f"  [{j}] {agent_name}: {msg.get('message', '')[:50]}...")
                    
                    print(f"Sequence: {' → '.join(agent_sequence)}")
                    
                    # Check for issues
                    conversation_issues = 0
                    for agent_name, count in agent_counts.items():
                        if count > 1:
                            print(f"🚨 {agent_name}: {count} messages (should be 1)")
                            conversation_issues += 1
                    
                    # Check for consecutive messages
                    consecutive_issues = []
                    for k in range(1, len(messages)):
                        if messages[k].get("agent_name") == messages[k-1].get("agent_name"):
                            consecutive_issues.append((k+1, messages[k].get("agent_name")))
                    
                    if consecutive_issues:
                        print(f"🚨 Consecutive message issues:")
                        for pos, agent_name in consecutive_issues:
                            print(f"  - Position {pos}: {agent_name} sent consecutive messages")
                        conversation_issues += len(consecutive_issues)
                    
                    if conversation_issues == 0:
                        print(f"✅ Perfect alternation")
                    else:
                        total_issues += conversation_issues
                        print(f"❌ {conversation_issues} issues found")
                else:
                    print("⚠️ No messages in conversation")
            
            print(f"\n📊 OVERALL ANALYSIS:")
            print(f"Conversations analyzed: {len(conversations_to_analyze)}")
            print(f"Total issues found: {total_issues}")
            
            if total_issues > 0:
                print(f"\n🚨 AGENT ALTERNATION ISSUES CONFIRMED!")
                print(f"   - Found {total_issues} instances of improper agent alternation")
                print(f"   - Same agents are sending multiple messages in conversations")
                print(f"   - This matches the reported issue with Dr. James Park")
                return False
            else:
                print(f"\n✅ NO ALTERNATION ISSUES FOUND")
                print(f"   - All conversations show proper agent alternation")
                print(f"   - Each agent sends exactly one message per conversation")
                return True
                
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return False

if __name__ == "__main__":
    success = analyze_existing_conversations()
    if success:
        print(f"\n✅ ANALYSIS COMPLETE: No agent alternation issues detected")
    else:
        print(f"\n❌ ANALYSIS COMPLETE: Agent alternation issues confirmed")