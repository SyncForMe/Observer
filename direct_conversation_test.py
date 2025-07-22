#!/usr/bin/env python3
"""
Direct API Test for Conversation Generation Issues
"""

import requests
import json
import re
from collections import Counter
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_conversation_generation():
    print("🧪 DIRECT CONVERSATION GENERATION TEST")
    print("="*60)
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    try:
        auth_response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Step 2: Check simulation state
    print("\n2. Checking simulation state...")
    try:
        state_response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
        if state_response.status_code == 200:
            state_data = state_response.json()
            print(f"✅ Simulation state retrieved")
            print(f"   - Active: {state_data.get('is_active', False)}")
            print(f"   - Scenario: {state_data.get('scenario_name', 'None')}")
        else:
            print(f"❌ Failed to get simulation state: {state_response.status_code}")
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
    
    # Step 3: Check agents
    print("\n3. Checking agents...")
    try:
        agents_response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if agents_response.status_code == 200:
            agents = agents_response.json()
            print(f"✅ Found {len(agents)} agents")
            for agent in agents:
                print(f"   - {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
        else:
            print(f"❌ Failed to get agents: {agents_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return
    
    if len(agents) < 2:
        print("❌ Need at least 2 agents for conversation testing")
        return
    
    # Step 4: Generate conversation
    print("\n4. Generating conversation...")
    try:
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=60)
        if conv_response.status_code == 200:
            conversation = conv_response.json()
            messages = conversation.get('messages', [])
            print(f"✅ Generated conversation with {len(messages)} messages")
            
            # Analyze the conversation
            analyze_issues(messages)
            
        else:
            print(f"❌ Failed to generate conversation: {conv_response.status_code}")
            print(f"Response: {conv_response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")

def analyze_issues(messages):
    """Analyze conversation for the specific issues"""
    print("\n📊 ANALYZING CONVERSATION FOR REPORTED ISSUES")
    print("="*60)
    
    # Print conversation
    print("\n💬 CONVERSATION:")
    for i, msg in enumerate(messages, 1):
        agent_name = msg.get('agent_name', 'Unknown')
        message = msg.get('message', '')
        print(f"{i}. {agent_name}: {message}")
    
    print("\n🔍 ISSUE ANALYSIS:")
    
    # Issue 1: Repetitive phrases
    print("\n❌ ISSUE 1: REPETITIVE PHRASES")
    repetitive_count = 0
    for msg in messages:
        message_text = msg.get('message', '').lower()
        if 'fascinating challenge' in message_text:
            repetitive_count += 1
            print(f"   Found 'fascinating challenge' in {msg.get('agent_name', '')}: {message_text[:80]}...")
    
    if repetitive_count > 0:
        print(f"   ❌ CONFIRMED: 'Fascinating challenge' used {repetitive_count} times")
    else:
        print("   ✅ No 'fascinating challenge' repetition found")
    
    # Issue 2: Direct questions not answered
    print("\n❌ ISSUE 2: DIRECT QUESTIONS NOT ANSWERED")
    questions_to_agents = 0
    for msg in messages:
        message_text = msg.get('message', '').lower()
        if '?' in message_text and any(name in message_text for name in ['tesla', 'darth', 'vader']):
            questions_to_agents += 1
            print(f"   Found question: {msg.get('agent_name', '')} - {message_text[:80]}...")
    
    if questions_to_agents == 0:
        print("   ❌ CONFIRMED: No direct questions asked between agents")
    else:
        print(f"   ✅ Found {questions_to_agents} direct questions")
    
    # Issue 3: Context awareness
    print("\n❌ ISSUE 3: LACKING CONTEXT AWARENESS")
    context_refs = 0
    for msg in messages:
        message_text = msg.get('message', '').lower()
        if any(phrase in message_text for phrase in ['you mentioned', 'as you said', 'your point', 'building on']):
            context_refs += 1
            print(f"   Found context reference: {msg.get('agent_name', '')} - {message_text[:80]}...")
    
    if context_refs == 0:
        print("   ❌ CONFIRMED: No context awareness detected")
    else:
        print(f"   ✅ Found {context_refs} context references")
    
    # Issue 4: Collaborative building
    print("\n❌ ISSUE 4: NO COLLABORATIVE BUILDING")
    collaboration = 0
    for msg in messages:
        message_text = msg.get('message', '').lower()
        if any(phrase in message_text for phrase in ['yes, and', 'building on', 'great point', 'i agree']):
            collaboration += 1
            print(f"   Found collaboration: {msg.get('agent_name', '')} - {message_text[:80]}...")
    
    if collaboration == 0:
        print("   ❌ CONFIRMED: No collaborative building detected")
    else:
        print(f"   ✅ Found {collaboration} collaborative instances")
    
    # Summary
    issues_found = []
    if repetitive_count > 0:
        issues_found.append("Repetitive phrases")
    if questions_to_agents == 0:
        issues_found.append("No direct questions")
    if context_refs == 0:
        issues_found.append("No context awareness")
    if collaboration == 0:
        issues_found.append("No collaborative building")
    
    print(f"\n📋 SUMMARY: {len(issues_found)} issues confirmed")
    for issue in issues_found:
        print(f"   ❌ {issue}")

if __name__ == "__main__":
    test_conversation_generation()