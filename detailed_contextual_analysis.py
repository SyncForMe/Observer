#!/usr/bin/env python3
"""
Detailed Analysis of Contextual Conversation Features
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://simulated-agents.preview.emergentagent.com/api"

def analyze_contextual_features():
    """Analyze the contextual conversation features in detail"""
    print("🔍 DETAILED CONTEXTUAL CONVERSATION ANALYSIS")
    print("=" * 60)
    
    # Authenticate
    auth_response = requests.post(f"{BACKEND_URL}/auth/test-login", timeout=10)
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    auth_data = auth_response.json()
    auth_token = auth_data.get("access_token")
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get current conversations to analyze
    conversations_response = requests.get(f"{BACKEND_URL}/conversations", headers=headers, timeout=10)
    if conversations_response.status_code != 200:
        print("❌ Failed to get conversations")
        return
    
    conversations = conversations_response.json()
    if not conversations:
        print("❌ No conversations found")
        return
    
    latest_conversation = conversations[0]
    messages = latest_conversation.get("messages", [])
    conversation_state = latest_conversation.get("conversation_state", {})
    
    print(f"📊 CONVERSATION ANALYSIS")
    print(f"Total Messages: {len(messages)}")
    print(f"Conversation Type: {latest_conversation.get('conversation_type', 'N/A')}")
    print(f"Scenario: {latest_conversation.get('scenario_name', 'N/A')}")
    print()
    
    # Analyze each message for contextual features
    contextual_features_found = []
    agent_interactions = {}
    question_answer_pairs = []
    solution_progression = []
    
    for i, message in enumerate(messages):
        agent_name = message.get("agent_name", "Unknown")
        message_text = message.get("message", "")
        message_type = message.get("message_type", "unknown")
        context_info = message.get("context_info", {})
        
        print(f"📝 MESSAGE #{i+1} - {agent_name}")
        print(f"   Type: {message_type}")
        print(f"   Text: {message_text[:100]}...")
        
        # Analyze contextual features
        features = []
        
        # Check for agent addressing
        other_agents = ["Dr. Sarah Chen", "Marcus Rodriguez", "Elena Volkov", "Bob Marley", "Nikola Tesla", "Darth Vader"]
        addressed_agents = [agent for agent in other_agents if agent != agent_name and any(name in message_text for name in [agent, agent.split()[0]])]
        if addressed_agents:
            features.append(f"Addresses: {', '.join(addressed_agents)}")
            for addressed in addressed_agents:
                if addressed not in agent_interactions:
                    agent_interactions[addressed] = []
                agent_interactions[addressed].append(agent_name)
        
        # Check for questions
        if "?" in message_text:
            features.append("Contains question")
            question_answer_pairs.append({"asker": agent_name, "question": message_text[:100]})
        
        # Check for building phrases
        building_phrases = ["building on", "expanding on", "following", "based on what", "as mentioned", "exactly", "yes,"]
        found_building = [phrase for phrase in building_phrases if phrase in message_text.lower()]
        if found_building:
            features.append(f"Building: {', '.join(found_building)}")
        
        # Check for solution language
        solution_phrases = ["solution", "approach", "strategy", "recommend", "propose", "implement", "critical", "focus"]
        found_solutions = [phrase for phrase in solution_phrases if phrase in message_text.lower()]
        if found_solutions:
            features.append(f"Solutions: {', '.join(found_solutions)}")
            solution_progression.append({"agent": agent_name, "solutions": found_solutions})
        
        # Check for emotional/collaborative language
        collaborative_phrases = ["brilliant", "exactly", "absolutely", "great point", "i agree", "building on"]
        found_collaborative = [phrase for phrase in collaborative_phrases if phrase in message_text.lower()]
        if found_collaborative:
            features.append(f"Collaborative: {', '.join(found_collaborative)}")
        
        print(f"   Features: {', '.join(features) if features else 'Basic response'}")
        print()
        
        contextual_features_found.extend(features)
    
    # Summary analysis
    print("🎯 CONTEXTUAL FEATURES SUMMARY")
    print("=" * 40)
    print(f"Total Contextual Features Found: {len(contextual_features_found)}")
    print(f"Agent Interactions: {len(agent_interactions)} agents addressed by others")
    print(f"Questions Asked: {len(question_answer_pairs)}")
    print(f"Solution Progression: {len(solution_progression)} solution-oriented messages")
    print()
    
    # Agent interaction network
    print("👥 AGENT INTERACTION NETWORK")
    for addressed_agent, addressing_agents in agent_interactions.items():
        print(f"   {addressed_agent} ← addressed by: {', '.join(addressing_agents)}")
    print()
    
    # Conversation state analysis
    print("📈 CONVERSATION STATE ANALYSIS")
    print(f"Topics Discussed: {len(conversation_state.get('topics_discussed', []))}")
    print(f"Questions Asked: {len(conversation_state.get('questions_asked', []))}")
    print(f"Solutions Proposed: {len(conversation_state.get('solutions_proposed', []))}")
    print(f"Current Focus: {conversation_state.get('current_focus', 'N/A')}")
    print(f"Goal Progress: {conversation_state.get('goal_progress', 0)}")
    print()
    
    # Quality assessment
    total_messages = len(messages)
    contextual_ratio = len([f for f in contextual_features_found if any(keyword in f.lower() for keyword in ["addresses", "building", "collaborative"])]) / total_messages if total_messages > 0 else 0
    question_ratio = len(question_answer_pairs) / total_messages if total_messages > 0 else 0
    solution_ratio = len(solution_progression) / total_messages if total_messages > 0 else 0
    
    print("🏆 QUALITY ASSESSMENT")
    print(f"Contextual Interaction Ratio: {contextual_ratio:.1%}")
    print(f"Question Engagement Ratio: {question_ratio:.1%}")
    print(f"Solution Focus Ratio: {solution_ratio:.1%}")
    
    overall_quality = (contextual_ratio * 0.4) + (question_ratio * 0.3) + (solution_ratio * 0.3)
    print(f"Overall Contextual Quality Score: {overall_quality:.2f}/1.0")
    
    if overall_quality >= 0.7:
        print("✅ EXCELLENT contextual conversation quality!")
    elif overall_quality >= 0.5:
        print("✅ GOOD contextual conversation quality!")
    else:
        print("⚠️ Contextual conversation quality needs improvement")

if __name__ == "__main__":
    analyze_contextual_features()