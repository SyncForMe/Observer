#!/usr/bin/env python3
"""
Conversation Quality Test - Testing the specific issues mentioned in the review:
1. Not answering direct questions
2. Using repetitive phrases 
3. Lacking context awareness
4. No collaborative building
"""

import requests
import json
import time
import os
import sys
import re
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"
JWT_SECRET = os.environ.get('JWT_SECRET')

def authenticate():
    """Get authentication token"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token"), data.get("user", {}).get("id")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def setup_test_agents(auth_token):
    """Create test agents with different archetypes for conversation testing"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Clear existing agents first
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            existing_agents = response.json()
            for agent in existing_agents:
                requests.delete(f"{API_URL}/agents/{agent['id']}", headers=headers)
    except:
        pass
    
    # Create diverse test agents
    test_agents = [
        {
            "name": "Dr. Tesla",
            "archetype": "scientist",
            "personality": {
                "extroversion": 7,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 6,
                "energy": 8
            },
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics and Computing",
            "background": "Leading quantum physicist with 15 years of research experience"
        },
        {
            "name": "Darth Vader",
            "archetype": "skeptic",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 6,
                "cooperativeness": 4,
                "energy": 7
            },
            "goal": "Ensure project feasibility and identify risks",
            "expertise": "Risk Assessment and Strategic Planning",
            "background": "Former military strategist, now focused on project risk management"
        },
        {
            "name": "Captain Optimism",
            "archetype": "optimist",
            "personality": {
                "extroversion": 9,
                "optimism": 10,
                "curiosity": 7,
                "cooperativeness": 9,
                "energy": 9
            },
            "goal": "Motivate team and find positive solutions",
            "expertise": "Team Leadership and Motivation",
            "background": "Experienced team leader with a track record of successful projects"
        }
    ]
    
    created_agents = []
    for agent_data in test_agents:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                agent = response.json()
                created_agents.append(agent)
                print(f"✅ Created agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    return created_agents

def start_simulation(auth_token):
    """Start simulation and set scenario"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Start simulation
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to start simulation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Set scenario
    scenario_data = {
        "scenario": "The team is working on a breakthrough quantum computing project. They need to discuss the technical approach, potential risks, and resource allocation.",
        "scenario_name": "Quantum Computing Project"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        if response.status_code == 200:
            print("✅ Simulation started and scenario set")
            return True
        else:
            print(f"❌ Failed to set scenario: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False

def generate_conversation(auth_token):
    """Generate a conversation and return the response"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return None

def analyze_conversation_quality(conversation_data):
    """Analyze conversation for the specific issues mentioned in the review"""
    if not conversation_data or 'messages' not in conversation_data:
        return {
            "error": "No conversation data to analyze",
            "issues": ["No conversation generated"]
        }
    
    messages = conversation_data['messages']
    issues = []
    analysis = {
        "total_messages": len(messages),
        "agents_participated": set(),
        "repetitive_phrases": [],
        "direct_questions": [],
        "question_responses": [],
        "context_references": [],
        "collaborative_building": [],
        "issues": []
    }
    
    # Track agents and their messages
    agent_messages = {}
    for msg in messages:
        agent_name = msg.get('agent_name', 'Unknown')
        analysis["agents_participated"].add(agent_name)
        
        if agent_name not in agent_messages:
            agent_messages[agent_name] = []
        agent_messages[agent_name].append(msg.get('message', ''))
    
    # 1. Check for repetitive phrases (Tesla saying "Fascinating challenge")
    print("\n🔍 ANALYZING REPETITIVE PHRASES:")
    repetitive_phrases = [
        "fascinating challenge",
        "interesting challenge", 
        "exciting opportunity",
        "great opportunity",
        "as an expert",
        "from my perspective",
        "in my experience",
        "based on my background"
    ]
    
    phrase_counts = Counter()
    for msg in messages:
        message_text = msg.get('message', '').lower()
        for phrase in repetitive_phrases:
            if phrase in message_text:
                phrase_counts[phrase] += 1
                analysis["repetitive_phrases"].append({
                    "agent": msg.get('agent_name'),
                    "phrase": phrase,
                    "message": message_text[:100] + "..."
                })
    
    for phrase, count in phrase_counts.items():
        if count > 1:
            issues.append(f"Repetitive phrase '{phrase}' used {count} times")
            print(f"❌ Repetitive phrase '{phrase}' used {count} times")
        else:
            print(f"✅ Phrase '{phrase}' used appropriately ({count} times)")
    
    # 2. Check for direct questions and responses
    print("\n🔍 ANALYZING DIRECT QUESTIONS AND RESPONSES:")
    question_patterns = [
        r'\b(what\'s your take|your take|what do you think)\b',
        r'\b(darth vader|tesla|captain optimism),?\s*(what|how|why|do you)\b',
        r'\?.*\b(darth vader|tesla|captain optimism)\b',
        r'\b(darth vader|tesla|captain optimism).*\?'
    ]
    
    for i, msg in enumerate(messages):
        message_text = msg.get('message', '').lower()
        agent_name = msg.get('agent_name', '')
        
        # Check if this message contains a direct question
        for pattern in question_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                analysis["direct_questions"].append({
                    "asker": agent_name,
                    "question": msg.get('message', ''),
                    "message_index": i
                })
                
                # Check if the next message(s) respond to this question
                target_agent = None
                if 'darth vader' in message_text.lower():
                    target_agent = 'Darth Vader'
                elif 'tesla' in message_text.lower():
                    target_agent = 'Dr. Tesla'
                elif 'captain optimism' in message_text.lower():
                    target_agent = 'Captain Optimism'
                
                if target_agent and i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    if next_msg.get('agent_name') == target_agent:
                        analysis["question_responses"].append({
                            "question": msg.get('message', ''),
                            "response": next_msg.get('message', ''),
                            "responder": target_agent
                        })
                        print(f"✅ Direct question answered by {target_agent}")
                    else:
                        issues.append(f"Direct question to {target_agent} not answered directly")
                        print(f"❌ Direct question to {target_agent} not answered directly")
    
    # 3. Check for context awareness and references to previous messages
    print("\n🔍 ANALYZING CONTEXT AWARENESS:")
    context_indicators = [
        r'\b(you mentioned|as you said|building on|your point about|what you said)\b',
        r'\b(tesla|darth|captain).*\b(said|mentioned|pointed out)\b',
        r'\b(that\'s interesting|i agree with|building on that)\b',
        r'\b(your idea about|your suggestion|your approach)\b'
    ]
    
    context_found = False
    for msg in messages:
        message_text = msg.get('message', '').lower()
        for pattern in context_indicators:
            if re.search(pattern, message_text, re.IGNORECASE):
                analysis["context_references"].append({
                    "agent": msg.get('agent_name'),
                    "reference": msg.get('message', '')[:100] + "...",
                    "pattern": pattern
                })
                context_found = True
                print(f"✅ Context reference found: {msg.get('agent_name')} - {pattern}")
    
    if not context_found:
        issues.append("No context awareness - agents don't reference each other's points")
        print("❌ No context awareness - agents don't reference each other's points")
    
    # 4. Check for collaborative building
    print("\n🔍 ANALYZING COLLABORATIVE BUILDING:")
    collaboration_indicators = [
        r'\b(yes, and|building on|let\'s combine|together we could)\b',
        r'\b(that\'s a great point|excellent idea|i like that approach)\b',
        r'\b(we should|let\'s work together|combining our)\b',
        r'\b(your expertise.*my|my.*your expertise)\b'
    ]
    
    collaboration_found = False
    for msg in messages:
        message_text = msg.get('message', '').lower()
        for pattern in collaboration_indicators:
            if re.search(pattern, message_text, re.IGNORECASE):
                analysis["collaborative_building"].append({
                    "agent": msg.get('agent_name'),
                    "collaboration": msg.get('message', '')[:100] + "...",
                    "pattern": pattern
                })
                collaboration_found = True
                print(f"✅ Collaborative building found: {msg.get('agent_name')} - {pattern}")
    
    if not collaboration_found:
        issues.append("No collaborative building - agents work in isolation")
        print("❌ No collaborative building - agents work in isolation")
    
    # 5. Check message length and substance
    print("\n🔍 ANALYZING MESSAGE QUALITY:")
    short_messages = 0
    for msg in messages:
        message_text = msg.get('message', '')
        if len(message_text.split()) < 10:
            short_messages += 1
    
    if short_messages > len(messages) * 0.5:
        issues.append(f"Too many short messages ({short_messages}/{len(messages)})")
        print(f"❌ Too many short messages ({short_messages}/{len(messages)})")
    else:
        print(f"✅ Message length appropriate ({short_messages}/{len(messages)} short)")
    
    analysis["issues"] = issues
    return analysis

def test_specific_question_scenario(auth_token):
    """Test the specific scenario mentioned in the review: Tesla asks Darth Vader a direct question"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print("\n🎯 TESTING SPECIFIC QUESTION SCENARIO")
    print("Sending observer message: 'Tesla, ask Darth Vader what his take is on the quantum approach'")
    
    observer_data = {
        "observer_message": "Tesla, ask Darth Vader what his take is on the quantum approach. Darth Vader, please give your honest assessment of the risks."
    }
    
    try:
        response = requests.post(f"{API_URL}/observer/send-message", json=observer_data, headers=headers)
        if response.status_code == 200:
            observer_response = response.json()
            print("✅ Observer message sent successfully")
            
            # Analyze the observer response
            if 'agent_responses' in observer_response:
                messages = observer_response['agent_responses'].get('messages', [])
                
                # Look for Tesla asking Darth Vader a question
                tesla_asked_question = False
                vader_responded = False
                
                for i, msg in enumerate(messages):
                    if msg.get('agent_name') == 'Dr. Tesla':
                        message_text = msg.get('message', '').lower()
                        if 'darth vader' in message_text and '?' in message_text:
                            tesla_asked_question = True
                            print(f"✅ Tesla asked Darth Vader a question: {msg.get('message', '')}")
                            
                            # Check if Darth Vader responded in the next message
                            if i + 1 < len(messages) and messages[i + 1].get('agent_name') == 'Darth Vader':
                                vader_response = messages[i + 1].get('message', '')
                                if len(vader_response) > 20:  # Substantial response
                                    vader_responded = True
                                    print(f"✅ Darth Vader responded: {vader_response}")
                                else:
                                    print(f"❌ Darth Vader's response too short: {vader_response}")
                
                if not tesla_asked_question:
                    print("❌ Tesla did not ask Darth Vader a direct question")
                if not vader_responded:
                    print("❌ Darth Vader did not respond appropriately to Tesla's question")
                
                return tesla_asked_question and vader_responded
            else:
                print("❌ No agent responses in observer message")
                return False
        else:
            print(f"❌ Failed to send observer message: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending observer message: {e}")
        return False

def run_conversation_quality_test():
    """Main test function"""
    print("="*80)
    print("🧪 CONVERSATION QUALITY TEST")
    print("Testing specific issues mentioned in the review:")
    print("1. Not answering direct questions")
    print("2. Using repetitive phrases (Tesla saying 'Fascinating challenge')")
    print("3. Lacking context awareness")
    print("4. No collaborative building")
    print("="*80)
    
    # Authenticate
    auth_token, user_id = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Setup test agents
    print("\n📋 SETTING UP TEST AGENTS")
    agents = setup_test_agents(auth_token)
    if len(agents) < 3:
        print("❌ Failed to create enough test agents")
        return False
    
    # Start simulation
    print("\n🚀 STARTING SIMULATION")
    if not start_simulation(auth_token):
        print("❌ Failed to start simulation")
        return False
    
    # Test 1: Generate multiple conversations and analyze patterns
    print("\n📊 TEST 1: ANALYZING CONVERSATION PATTERNS")
    all_issues = []
    conversation_count = 3
    
    for i in range(conversation_count):
        print(f"\n--- Conversation {i+1}/{conversation_count} ---")
        conversation_data = generate_conversation(auth_token)
        
        if conversation_data:
            print(f"✅ Generated conversation with {len(conversation_data.get('messages', []))} messages")
            
            # Print the conversation for manual review
            print("\n💬 CONVERSATION CONTENT:")
            for msg in conversation_data.get('messages', []):
                agent_name = msg.get('agent_name', 'Unknown')
                message = msg.get('message', '')
                print(f"{agent_name}: {message}")
            
            # Analyze quality
            analysis = analyze_conversation_quality(conversation_data)
            all_issues.extend(analysis['issues'])
            
            print(f"\n📈 ANALYSIS RESULTS:")
            print(f"- Total messages: {analysis['total_messages']}")
            print(f"- Agents participated: {len(analysis['agents_participated'])}")
            print(f"- Repetitive phrases found: {len(analysis['repetitive_phrases'])}")
            print(f"- Direct questions: {len(analysis['direct_questions'])}")
            print(f"- Question responses: {len(analysis['question_responses'])}")
            print(f"- Context references: {len(analysis['context_references'])}")
            print(f"- Collaborative building: {len(analysis['collaborative_building'])}")
            print(f"- Issues found: {len(analysis['issues'])}")
            
            if analysis['issues']:
                print("❌ Issues found:")
                for issue in analysis['issues']:
                    print(f"  - {issue}")
            else:
                print("✅ No issues found in this conversation")
        else:
            print("❌ Failed to generate conversation")
            all_issues.append("Failed to generate conversation")
        
        # Wait between conversations
        if i < conversation_count - 1:
            time.sleep(2)
    
    # Test 2: Test specific question scenario
    print("\n📊 TEST 2: SPECIFIC QUESTION SCENARIO")
    specific_test_passed = test_specific_question_scenario(auth_token)
    
    # Final summary
    print("\n" + "="*80)
    print("📋 FINAL SUMMARY")
    print("="*80)
    
    unique_issues = list(set(all_issues))
    
    print(f"Total conversations tested: {conversation_count}")
    print(f"Unique issues found: {len(unique_issues)}")
    
    if unique_issues:
        print("\n❌ ISSUES CONFIRMED:")
        for i, issue in enumerate(unique_issues, 1):
            print(f"{i}. {issue}")
    else:
        print("\n✅ NO ISSUES FOUND - Conversation system working well!")
    
    print(f"\nSpecific question scenario test: {'✅ PASSED' if specific_test_passed else '❌ FAILED'}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if "repetitive phrase" in str(unique_issues).lower():
        print("- Implement phrase repetition prevention in conversation generation")
    if "direct question" in str(unique_issues).lower():
        print("- Improve question detection logic to work without requiring agent name + expertise")
    if "context awareness" in str(unique_issues).lower():
        print("- Increase context memory beyond last 5 messages")
    if "collaborative building" in str(unique_issues).lower():
        print("- Strengthen collaboration validation and encourage building on others' ideas")
    
    return len(unique_issues) == 0

if __name__ == "__main__":
    success = run_conversation_quality_test()
    sys.exit(0 if success else 1)