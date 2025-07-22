#!/usr/bin/env python3
"""
Quick Conversation Analysis Test - Direct API testing for conversation quality issues
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

def quick_test():
    print("🧪 QUICK CONVERSATION QUALITY TEST")
    print("="*60)
    
    # Authenticate
    try:
        auth_response = requests.post(f"{API_URL}/auth/test-login")
        if auth_response.status_code != 200:
            print("❌ Authentication failed")
            return
        
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authenticated successfully")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Check current agents
    try:
        agents_response = requests.get(f"{API_URL}/agents", headers=headers)
        if agents_response.status_code == 200:
            agents = agents_response.json()
            print(f"✅ Found {len(agents)} agents in simulation")
            
            for agent in agents:
                print(f"  - {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
        else:
            print("❌ Failed to get agents")
            return
            
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return
    
    if len(agents) < 2:
        print("❌ Need at least 2 agents for conversation testing")
        return
    
    # Start simulation if not active
    try:
        sim_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        print("✅ Simulation started/verified")
    except Exception as e:
        print(f"⚠️ Simulation start warning: {e}")
    
    # Set a scenario that encourages questions
    scenario_data = {
        "scenario": "The team needs to make critical decisions about their quantum computing project. Tesla should ask Darth Vader for his risk assessment, and everyone should build on each other's ideas.",
        "scenario_name": "Decision Making Session"
    }
    
    try:
        scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        print("✅ Scenario set for question-focused discussion")
    except Exception as e:
        print(f"⚠️ Scenario setting warning: {e}")
    
    # Generate conversation
    print("\n🔄 Generating conversation...")
    try:
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if conv_response.status_code == 200:
            conversation = conv_response.json()
            messages = conversation.get('messages', [])
            print(f"✅ Generated conversation with {len(messages)} messages")
            
            # Analyze the conversation
            analyze_conversation_issues(messages)
            
        else:
            print(f"❌ Failed to generate conversation: {conv_response.status_code}")
            print(f"Response: {conv_response.text}")
            
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")

def analyze_conversation_issues(messages):
    """Analyze conversation for the specific issues mentioned in the review"""
    print("\n📊 CONVERSATION ANALYSIS")
    print("="*60)
    
    # Print the conversation first
    print("\n💬 CONVERSATION CONTENT:")
    for i, msg in enumerate(messages, 1):
        agent_name = msg.get('agent_name', 'Unknown')
        message = msg.get('message', '')
        print(f"{i}. {agent_name}: {message}")
    
    print("\n🔍 ISSUE ANALYSIS:")
    
    # Issue 1: Repetitive phrases (especially Tesla saying "Fascinating challenge")
    print("\n1. REPETITIVE PHRASES CHECK:")
    repetitive_phrases = [
        "fascinating challenge",
        "interesting challenge", 
        "exciting opportunity",
        "great opportunity",
        "as an expert",
        "from my perspective",
        "in my experience"
    ]
    
    phrase_counts = Counter()
    tesla_repetition = False
    
    for msg in messages:
        message_text = msg.get('message', '').lower()
        agent_name = msg.get('agent_name', '')
        
        for phrase in repetitive_phrases:
            if phrase in message_text:
                phrase_counts[phrase] += 1
                if agent_name == 'Dr. Tesla' and 'fascinating' in phrase:
                    tesla_repetition = True
                    print(f"❌ Tesla used repetitive phrase: '{phrase}' in: {message_text[:80]}...")
    
    if tesla_repetition:
        print("❌ CONFIRMED: Tesla uses repetitive 'fascinating' phrases")
    else:
        print("✅ No Tesla 'fascinating' repetition detected")
    
    for phrase, count in phrase_counts.items():
        if count > 1:
            print(f"❌ Repetitive phrase '{phrase}' used {count} times")
    
    # Issue 2: Not answering direct questions
    print("\n2. DIRECT QUESTION RESPONSE CHECK:")
    questions_found = []
    responses_found = []
    
    for i, msg in enumerate(messages):
        message_text = msg.get('message', '').lower()
        agent_name = msg.get('agent_name', '')
        
        # Look for direct questions to specific agents
        if '?' in message_text:
            # Check if it mentions another agent by name
            agent_names = ['tesla', 'darth vader', 'vader', 'captain optimism', 'optimism']
            for target_agent in agent_names:
                if target_agent in message_text:
                    questions_found.append({
                        'asker': agent_name,
                        'target': target_agent,
                        'question': msg.get('message', ''),
                        'index': i
                    })
                    print(f"❓ Direct question found: {agent_name} asks {target_agent}")
                    
                    # Check if the target agent responds in subsequent messages
                    target_responded = False
                    for j in range(i+1, min(i+3, len(messages))):  # Check next 2 messages
                        next_msg = messages[j]
                        next_agent = next_msg.get('agent_name', '').lower()
                        if target_agent in next_agent or (target_agent == 'vader' and 'darth' in next_agent):
                            target_responded = True
                            responses_found.append({
                                'responder': next_msg.get('agent_name', ''),
                                'response': next_msg.get('message', ''),
                                'question_index': i
                            })
                            print(f"✅ {next_msg.get('agent_name', '')} responded to the question")
                            break
                    
                    if not target_responded:
                        print(f"❌ {target_agent} did not respond to direct question")
    
    if len(questions_found) == 0:
        print("❌ CONFIRMED: No direct questions asked between agents")
    elif len(responses_found) < len(questions_found):
        print(f"❌ CONFIRMED: {len(questions_found) - len(responses_found)} direct questions went unanswered")
    else:
        print("✅ All direct questions were answered")
    
    # Issue 3: Lacking context awareness
    print("\n3. CONTEXT AWARENESS CHECK:")
    context_indicators = [
        r'\b(you mentioned|as you said|building on|your point about)\b',
        r'\b(tesla|darth|vader|captain).*\b(said|mentioned|pointed out)\b',
        r'\b(that\'s interesting|i agree with|building on that)\b',
        r'\b(your idea|your suggestion|your approach)\b'
    ]
    
    context_references = 0
    for msg in messages:
        message_text = msg.get('message', '').lower()
        for pattern in context_indicators:
            if re.search(pattern, message_text):
                context_references += 1
                print(f"✅ Context reference: {msg.get('agent_name', '')} - {message_text[:60]}...")
                break
    
    if context_references == 0:
        print("❌ CONFIRMED: No context awareness - agents don't reference each other's points")
    else:
        print(f"✅ Found {context_references} context references")
    
    # Issue 4: No collaborative building
    print("\n4. COLLABORATIVE BUILDING CHECK:")
    collaboration_indicators = [
        r'\b(yes, and|building on|let\'s combine|together we could)\b',
        r'\b(that\'s a great point|excellent idea|i like that)\b',
        r'\b(we should|let\'s work together|combining our)\b'
    ]
    
    collaboration_instances = 0
    for msg in messages:
        message_text = msg.get('message', '').lower()
        for pattern in collaboration_indicators:
            if re.search(pattern, message_text):
                collaboration_instances += 1
                print(f"✅ Collaboration: {msg.get('agent_name', '')} - {message_text[:60]}...")
                break
    
    if collaboration_instances == 0:
        print("❌ CONFIRMED: No collaborative building - agents work in isolation")
    else:
        print(f"✅ Found {collaboration_instances} collaborative building instances")
    
    # Summary
    print("\n📋 ISSUE SUMMARY:")
    issues_confirmed = []
    
    if tesla_repetition or any(count > 1 for count in phrase_counts.values()):
        issues_confirmed.append("Repetitive phrases detected")
    
    if len(questions_found) == 0 or len(responses_found) < len(questions_found):
        issues_confirmed.append("Direct questions not answered properly")
    
    if context_references == 0:
        issues_confirmed.append("Lacking context awareness")
    
    if collaboration_instances == 0:
        issues_confirmed.append("No collaborative building")
    
    if issues_confirmed:
        print("❌ ISSUES CONFIRMED:")
        for issue in issues_confirmed:
            print(f"  - {issue}")
    else:
        print("✅ NO MAJOR ISSUES DETECTED")
    
    return issues_confirmed

if __name__ == "__main__":
    quick_test()