#!/usr/bin/env python3
"""
Enhanced Conversation Generation Test
Tests the ENHANCED conversation generation system to verify fixes for conversational flow issues.
"""

import requests
import json
import time
import os
import sys
import uuid
import re
from datetime import datetime
from collections import Counter, defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"
JWT_SECRET = os.environ.get('JWT_SECRET')

class ConversationAnalyzer:
    """Analyzes conversations for natural flow, emotional reactions, and collaborative patterns"""
    
    def __init__(self):
        self.emotional_indicators = {
            'excitement': ['brilliant!', 'exactly!', 'that\'s it!', 'perfect!', 'amazing!', 'fantastic!', 'yes!', 'wow!', 'incredible!'],
            'concern': ['wait', 'worried', 'risky', 'dangerous', 'problem', 'issue', 'concern', 'careful', 'cautious'],
            'confusion': ['don\'t follow', 'what do you mean', 'confused', 'unclear', 'explain', 'clarify', 'how so?', 'what?'],
            'building': ['yes, and', 'building on', 'adding to', 'expanding', 'also', 'furthermore', 'plus'],
            'challenging': ['disagree', 'however', 'but', 'actually', 'i think differently', 'not sure about', 'what about']
        }
        
        self.formulaic_phrases = [
            'from my perspective',
            'in my experience',
            'as an expert',
            'based on my background',
            'given my expertise',
            'fascinating challenge',
            'interesting problem',
            'let me share my thoughts'
        ]
        
        self.direct_response_patterns = [
            r'\b\w+,\s+(?:when you|your point|what you|you mentioned)',
            r'\b\w+,\s+(?:that\'s|i agree|exactly|yes)',
            r'building on (?:what )?\w+',
            r'(?:tesla|marcus|alex|sarah|dr\.\s+\w+),\s+',
            r'you said.*?(?:what|how|why)',
            r'when you mentioned'
        ]

    def analyze_conversation(self, messages):
        """Analyze a conversation for natural flow and collaborative patterns"""
        analysis = {
            'total_messages': len(messages),
            'emotional_reactions': defaultdict(int),
            'direct_responses': 0,
            'formulaic_usage': 0,
            'specific_detail_questions': 0,
            'collaborative_building': 0,
            'agent_interactions': defaultdict(list),
            'conversation_flow_score': 0,
            'natural_authenticity_score': 0,
            'issues': []
        }
        
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue
                
            agent_name = msg.get('agent_name', '')
            message_text = msg.get('message', '').lower()
            
            # Skip observer messages
            if 'observer' in agent_name.lower():
                continue
            
            # Analyze emotional reactions
            for emotion, indicators in self.emotional_indicators.items():
                for indicator in indicators:
                    if indicator in message_text:
                        analysis['emotional_reactions'][emotion] += 1
            
            # Check for formulaic phrases
            for phrase in self.formulaic_phrases:
                if phrase in message_text:
                    analysis['formulaic_usage'] += 1
                    analysis['issues'].append(f"Formulaic phrase '{phrase}' in {agent_name}'s message")
            
            # Check for direct responses
            for pattern in self.direct_response_patterns:
                if re.search(pattern, message_text, re.IGNORECASE):
                    analysis['direct_responses'] += 1
                    break
            
            # Check for specific detail questions
            if '?' in message_text:
                # Look for specific technical terms or detailed questions
                technical_terms = ['frequency', 'algorithm', 'protocol', 'implementation', 'mechanism', 'process']
                if any(term in message_text for term in technical_terms):
                    analysis['specific_detail_questions'] += 1
            
            # Check for collaborative building
            building_phrases = ['building on', 'yes, and', 'adding to', 'expanding']
            if any(phrase in message_text for phrase in building_phrases):
                analysis['collaborative_building'] += 1
            
            # Track agent interactions
            if i > 0:
                prev_msg = messages[i-1]
                prev_agent = prev_msg.get('agent_name', '')
                if prev_agent != agent_name and 'observer' not in prev_agent.lower():
                    analysis['agent_interactions'][agent_name].append(prev_agent)
        
        # Calculate scores
        if analysis['total_messages'] > 0:
            # Conversation flow score (0-100)
            flow_factors = [
                analysis['direct_responses'] / max(1, analysis['total_messages'] - 1) * 30,  # 30% weight
                min(sum(analysis['emotional_reactions'].values()) / analysis['total_messages'] * 25, 25),  # 25% weight
                analysis['collaborative_building'] / max(1, analysis['total_messages']) * 20,  # 20% weight
                max(0, 25 - analysis['formulaic_usage'] / analysis['total_messages'] * 25)  # 25% weight (penalty)
            ]
            analysis['conversation_flow_score'] = sum(flow_factors)
            
            # Natural authenticity score (0-100)
            auth_factors = [
                min(sum(analysis['emotional_reactions'].values()) / analysis['total_messages'] * 40, 40),  # 40% weight
                analysis['specific_detail_questions'] / max(1, analysis['total_messages']) * 30,  # 30% weight
                max(0, 30 - analysis['formulaic_usage'] / analysis['total_messages'] * 30)  # 30% weight (penalty)
            ]
            analysis['natural_authenticity_score'] = sum(auth_factors)
        
        return analysis

def test_enhanced_conversation_generation():
    """Test the enhanced conversation generation system"""
    print("\n" + "="*80)
    print("TESTING ENHANCED CONVERSATION GENERATION SYSTEM")
    print("="*80)
    
    # Login to get auth token
    print("\nStep 1: Authenticating...")
    login_response = requests.post(f"{API_URL}/auth/test-login")
    if login_response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    auth_data = login_response.json()
    auth_token = auth_data.get("access_token")
    user_id = auth_data.get("user", {}).get("id")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"✅ Authenticated as user: {user_id}")
    
    # Step 2: Create diverse test agents for natural conversation
    print("\nStep 2: Creating diverse test agents...")
    
    test_agents = [
        {
            "name": "Dr. Tesla Vance",
            "archetype": "scientist",
            "personality": {"extroversion": 6, "optimism": 8, "curiosity": 9, "cooperativeness": 7, "energy": 8},
            "goal": "Develop breakthrough quantum communication technology",
            "expertise": "Quantum Physics and Signal Processing",
            "background": "Leading researcher in quantum entanglement and resonant frequency applications"
        },
        {
            "name": "Marcus Chen",
            "archetype": "skeptic", 
            "personality": {"extroversion": 5, "optimism": 4, "curiosity": 8, "cooperativeness": 6, "energy": 6},
            "goal": "Ensure all solutions are practical and risk-assessed",
            "expertise": "Systems Engineering and Risk Analysis",
            "background": "Experienced engineer who questions assumptions and identifies potential problems"
        },
        {
            "name": "Sarah Kim",
            "archetype": "optimist",
            "personality": {"extroversion": 8, "optimism": 9, "curiosity": 7, "cooperativeness": 9, "energy": 8},
            "goal": "Foster team collaboration and find creative solutions",
            "expertise": "Team Leadership and Innovation Strategy", 
            "background": "Enthusiastic leader who builds on others' ideas and maintains team morale"
        },
        {
            "name": "Dr. Alex Rivera",
            "archetype": "researcher",
            "personality": {"extroversion": 4, "optimism": 6, "curiosity": 10, "cooperativeness": 8, "energy": 7},
            "goal": "Investigate technical details and implementation specifics",
            "expertise": "Technical Implementation and Protocol Design",
            "background": "Detail-oriented researcher who asks probing questions about technical specifications"
        }
    ]
    
    created_agents = []
    for agent_data in test_agents:
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        if response.status_code == 200:
            agent = response.json()
            created_agents.append(agent)
            print(f"✅ Created agent: {agent_data['name']} ({agent_data['archetype']})")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    if len(created_agents) < 3:
        print("❌ Need at least 3 agents for conversation testing")
        return False
    
    # Step 3: Set up simulation with scenario designed to trigger natural responses
    print("\nStep 3: Setting up simulation with natural conversation scenario...")
    
    scenario_data = {
        "scenario": "The team has discovered unusual quantum signal patterns that could revolutionize communication technology. Dr. Tesla has identified specific resonant frequencies that seem to enable instantaneous data transmission across vast distances. However, the mechanism is not yet understood and there are concerns about stability and practical implementation.",
        "scenario_name": "Quantum Signal Discovery"
    }
    
    scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
    if scenario_response.status_code != 200:
        print("❌ Failed to set scenario")
        return False
    
    print("✅ Scenario set: Quantum Signal Discovery")
    
    # Start simulation
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code != 200:
        print("❌ Failed to start simulation")
        return False
    
    print("✅ Simulation started")
    
    # Step 4: Generate multiple conversations and analyze them
    print("\nStep 4: Generating and analyzing conversations...")
    
    analyzer = ConversationAnalyzer()
    conversation_analyses = []
    
    for i in range(3):
        print(f"\n--- Generating Conversation {i+1} ---")
        
        # Generate conversation
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if conv_response.status_code != 200:
            print(f"❌ Failed to generate conversation {i+1}")
            continue
        
        conv_data = conv_response.json()
        messages = conv_data.get('messages', [])
        
        print(f"✅ Generated conversation with {len(messages)} messages")
        
        # Display conversation for manual review
        print("\n📝 CONVERSATION CONTENT:")
        for j, msg in enumerate(messages, 1):
            agent_name = msg.get('agent_name', 'Unknown')
            message_text = msg.get('message', '')
            print(f"{j}. {agent_name}: {message_text}")
        
        # Analyze conversation
        analysis = analyzer.analyze_conversation(messages)
        conversation_analyses.append(analysis)
        
        print(f"\n📊 CONVERSATION {i+1} ANALYSIS:")
        print(f"Total Messages: {analysis['total_messages']}")
        print(f"Direct Responses: {analysis['direct_responses']}")
        print(f"Emotional Reactions: {dict(analysis['emotional_reactions'])}")
        print(f"Formulaic Usage: {analysis['formulaic_usage']}")
        print(f"Specific Detail Questions: {analysis['specific_detail_questions']}")
        print(f"Collaborative Building: {analysis['collaborative_building']}")
        print(f"Flow Score: {analysis['conversation_flow_score']:.1f}/100")
        print(f"Authenticity Score: {analysis['natural_authenticity_score']:.1f}/100")
        
        if analysis['issues']:
            print(f"Issues Found: {len(analysis['issues'])}")
            for issue in analysis['issues'][:3]:  # Show first 3 issues
                print(f"  - {issue}")
        
        time.sleep(2)  # Brief pause between generations
    
    # Step 5: Test observer message interaction for natural responses
    print("\nStep 5: Testing observer message interaction...")
    
    observer_message = "Tesla, when you mentioned resonant frequencies, what specific frequency ranges are we talking about? And Marcus, what are your main concerns about stability?"
    
    observer_response = requests.post(
        f"{API_URL}/observer/send-message",
        json={"observer_message": observer_message},
        headers=headers
    )
    
    if observer_response.status_code == 200:
        observer_data = observer_response.json()
        agent_responses = observer_data.get('agent_responses', {})
        messages = agent_responses.get('messages', [])
        
        print(f"✅ Observer message sent, received {len(messages)} responses")
        
        print("\n📝 OBSERVER INTERACTION:")
        for msg in messages:
            agent_name = msg.get('agent_name', 'Unknown')
            message_text = msg.get('message', '')
            print(f"{agent_name}: {message_text}")
        
        # Analyze observer responses
        observer_analysis = analyzer.analyze_conversation(messages)
        conversation_analyses.append(observer_analysis)
        
        print(f"\n📊 OBSERVER INTERACTION ANALYSIS:")
        print(f"Direct Responses: {observer_analysis['direct_responses']}")
        print(f"Emotional Reactions: {dict(observer_analysis['emotional_reactions'])}")
        print(f"Specific Detail Questions: {observer_analysis['specific_detail_questions']}")
    else:
        print("❌ Failed to send observer message")
    
    # Step 6: Overall analysis and scoring
    print("\nStep 6: Overall Analysis and Scoring")
    print("="*50)
    
    if not conversation_analyses:
        print("❌ No conversations to analyze")
        return False
    
    # Calculate overall metrics
    total_conversations = len(conversation_analyses)
    avg_flow_score = sum(a['conversation_flow_score'] for a in conversation_analyses) / total_conversations
    avg_auth_score = sum(a['natural_authenticity_score'] for a in conversation_analyses) / total_conversations
    total_emotional_reactions = sum(sum(a['emotional_reactions'].values()) for a in conversation_analyses)
    total_direct_responses = sum(a['direct_responses'] for a in conversation_analyses)
    total_formulaic = sum(a['formulaic_usage'] for a in conversation_analyses)
    total_messages = sum(a['total_messages'] for a in conversation_analyses)
    
    print(f"📊 OVERALL RESULTS:")
    print(f"Total Conversations Analyzed: {total_conversations}")
    print(f"Total Messages: {total_messages}")
    print(f"Average Flow Score: {avg_flow_score:.1f}/100")
    print(f"Average Authenticity Score: {avg_auth_score:.1f}/100")
    print(f"Total Emotional Reactions: {total_emotional_reactions}")
    print(f"Total Direct Responses: {total_direct_responses}")
    print(f"Total Formulaic Phrases: {total_formulaic}")
    
    # Success criteria evaluation
    print(f"\n✅ SUCCESS CRITERIA EVALUATION:")
    
    criteria_results = []
    
    # 1. Direct responses to previous speaker's points
    direct_response_rate = total_direct_responses / max(1, total_messages - total_conversations) * 100
    if direct_response_rate >= 30:
        print(f"✅ Direct Response Patterns: {direct_response_rate:.1f}% (Target: ≥30%)")
        criteria_results.append(True)
    else:
        print(f"❌ Direct Response Patterns: {direct_response_rate:.1f}% (Target: ≥30%)")
        criteria_results.append(False)
    
    # 2. Natural emotional reactions
    emotion_rate = total_emotional_reactions / max(1, total_messages) * 100
    if emotion_rate >= 25:
        print(f"✅ Emotional Reactions: {emotion_rate:.1f}% (Target: ≥25%)")
        criteria_results.append(True)
    else:
        print(f"❌ Emotional Reactions: {emotion_rate:.1f}% (Target: ≥25%)")
        criteria_results.append(False)
    
    # 3. Reduced formulaic patterns
    formulaic_rate = total_formulaic / max(1, total_messages) * 100
    if formulaic_rate <= 15:
        print(f"✅ Reduced Formulaic Patterns: {formulaic_rate:.1f}% (Target: ≤15%)")
        criteria_results.append(True)
    else:
        print(f"❌ Reduced Formulaic Patterns: {formulaic_rate:.1f}% (Target: ≤15%)")
        criteria_results.append(False)
    
    # 4. Overall conversation flow
    if avg_flow_score >= 60:
        print(f"✅ Conversation Flow Score: {avg_flow_score:.1f}/100 (Target: ≥60)")
        criteria_results.append(True)
    else:
        print(f"❌ Conversation Flow Score: {avg_flow_score:.1f}/100 (Target: ≥60)")
        criteria_results.append(False)
    
    # 5. Natural authenticity
    if avg_auth_score >= 55:
        print(f"✅ Natural Authenticity Score: {avg_auth_score:.1f}/100 (Target: ≥55)")
        criteria_results.append(True)
    else:
        print(f"❌ Natural Authenticity Score: {avg_auth_score:.1f}/100 (Target: ≥55)")
        criteria_results.append(False)
    
    # Final assessment
    passed_criteria = sum(criteria_results)
    total_criteria = len(criteria_results)
    success_rate = passed_criteria / total_criteria * 100
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"Criteria Passed: {passed_criteria}/{total_criteria} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Enhanced conversation system is working exceptionally well!")
        result = "excellent"
    elif success_rate >= 60:
        print("✅ GOOD: Enhanced conversation system shows significant improvements!")
        result = "good"
    elif success_rate >= 40:
        print("⚠️ FAIR: Enhanced conversation system shows some improvements but needs work!")
        result = "fair"
    else:
        print("❌ POOR: Enhanced conversation system needs significant improvements!")
        result = "poor"
    
    # Specific recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if direct_response_rate < 30:
        print("- Enhance prompts to encourage more direct responses to previous speakers")
    if emotion_rate < 25:
        print("- Strengthen emotional reaction prompts and personality expression")
    if formulaic_rate > 15:
        print("- Further reduce formulaic phrase usage in agent responses")
    if avg_flow_score < 60:
        print("- Improve conversation flow and collaborative building patterns")
    if avg_auth_score < 55:
        print("- Enhance natural authenticity and reduce robotic responses")
    
    return result in ["excellent", "good"]

if __name__ == "__main__":
    success = test_enhanced_conversation_generation()
    sys.exit(0 if success else 1)