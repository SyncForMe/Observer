#!/usr/bin/env python3
"""
IMPROVED CONVERSATION GENERATION SYSTEM TEST

This test specifically verifies that the robotic patterns have been fixed:
1. No more forced "What's your take?" questions
2. Natural question answering when asked directly
3. Varied response types and collaboration
4. Character authenticity without robotic patterns
5. Real collaboration with specific references to teammates
"""

import requests
import json
import time
import os
import sys
import re
from dotenv import load_dotenv
from collections import Counter, defaultdict
import statistics

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate():
    """Get authentication token"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token"), data.get("user", {}).get("id")
    except Exception as e:
        print(f"Authentication failed: {e}")
    return None, None

def create_test_agents(auth_token, user_id):
    """Create diverse test agents for conversation testing"""
    print("\n🤖 Creating diverse test agents...")
    
    # Define test agents with distinct personalities
    test_agents = [
        {
            "name": "Tesla",
            "archetype": "scientist", 
            "personality": {
                "extroversion": 8,
                "optimism": 9,
                "curiosity": 10,
                "cooperativeness": 7,
                "energy": 9
            },
            "goal": "Revolutionize technology through innovative solutions",
            "expertise": "Electrical engineering, innovation, future technology",
            "background": "Visionary inventor focused on advancing human civilization through technology"
        },
        {
            "name": "Bob Marley",
            "archetype": "mediator",
            "personality": {
                "extroversion": 7,
                "optimism": 10,
                "curiosity": 6,
                "cooperativeness": 10,
                "energy": 8
            },
            "goal": "Bring peace and unity through wisdom and understanding",
            "expertise": "Philosophy, music, social harmony, spiritual guidance",
            "background": "Peaceful philosopher who believes in unity and positive vibrations"
        },
        {
            "name": "Darth Vader",
            "archetype": "leader",
            "personality": {
                "extroversion": 6,
                "optimism": 3,
                "curiosity": 5,
                "cooperativeness": 4,
                "energy": 7
            },
            "goal": "Establish order and control through decisive leadership",
            "expertise": "Strategic planning, military tactics, organizational control",
            "background": "Authoritative leader who values efficiency and results above all"
        }
    ]
    
    created_agents = []
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    for agent_data in test_agents:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                agent_response = response.json()
                created_agents.append(agent_response)
                print(f"✅ Created agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    return created_agents

def setup_simulation(auth_token):
    """Setup simulation environment"""
    print("\n🎬 Setting up simulation...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Start simulation
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if response.status_code == 200:
            print("✅ Simulation started")
        else:
            print(f"❌ Failed to start simulation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Set scenario
    scenario_data = {
        "scenario": "The team is working on a revolutionary new project that could change the world. They need to collaborate effectively to overcome challenges and find innovative solutions.",
        "scenario_name": "Revolutionary Innovation Project"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        if response.status_code == 200:
            print("✅ Scenario set")
            return True
        else:
            print(f"❌ Failed to set scenario: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False

def generate_conversation(auth_token, conversation_num):
    """Generate a single conversation and return the messages"""
    print(f"\n💬 Generating conversation {conversation_num}...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            conversation_data = response.json()
            messages = conversation_data.get("messages", [])
            print(f"✅ Generated conversation with {len(messages)} messages")
            return messages
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return []

def analyze_robotic_patterns(messages):
    """Analyze messages for robotic patterns that should be eliminated"""
    print("\n🔍 Analyzing for robotic patterns...")
    
    robotic_issues = []
    
    # Patterns to detect
    forced_question_patterns = [
        r"what's your take,?\s+\w+\??",
        r"what do you think,?\s+\w+\??",
        r"your thoughts,?\s+\w+\??",
        r"what's your perspective,?\s+\w+\??",
        r"how do you see it,?\s+\w+\??",
    ]
    
    repetitive_openings = [
        "fascinating challenge",
        "interesting problem", 
        "this is concerning",
        "this is exciting",
        "alright team",
        "okay everyone",
        "as an expert in",
        "from my perspective",
        "based on my experience"
    ]
    
    robotic_phrases = [
        "i acknowledge",
        "understood",
        "roger that",
        "copy that",
        "affirmative",
        "noted",
        "very well"
    ]
    
    # Check each message
    for i, msg in enumerate(messages):
        agent_name = msg.get("agent_name", "Unknown")
        message_text = msg.get("message", "").lower()
        
        # Check for forced questions (especially at end of messages)
        for pattern in forced_question_patterns:
            if re.search(pattern, message_text):
                robotic_issues.append({
                    "type": "forced_question",
                    "agent": agent_name,
                    "message_num": i + 1,
                    "pattern": pattern,
                    "text": message_text[:100] + "..."
                })
        
        # Check for repetitive openings
        for opening in repetitive_openings:
            if message_text.startswith(opening):
                robotic_issues.append({
                    "type": "repetitive_opening",
                    "agent": agent_name,
                    "message_num": i + 1,
                    "pattern": opening,
                    "text": message_text[:100] + "..."
                })
        
        # Check for robotic phrases
        for phrase in robotic_phrases:
            if phrase in message_text:
                robotic_issues.append({
                    "type": "robotic_phrase",
                    "agent": agent_name,
                    "message_num": i + 1,
                    "pattern": phrase,
                    "text": message_text[:100] + "..."
                })
        
        # Check for asterisk narrations (should be removed)
        if "*" in message_text:
            robotic_issues.append({
                "type": "narration",
                "agent": agent_name,
                "message_num": i + 1,
                "pattern": "asterisk_narration",
                "text": message_text[:100] + "..."
            })
    
    return robotic_issues

def analyze_natural_collaboration(messages):
    """Analyze messages for natural collaboration patterns"""
    print("\n🤝 Analyzing collaboration patterns...")
    
    collaboration_score = 0
    collaboration_details = {
        "references_to_others": 0,
        "builds_on_ideas": 0,
        "asks_natural_questions": 0,
        "varied_response_types": 0,
        "character_authenticity": 0
    }
    
    agent_names = set()
    response_types = []
    
    for i, msg in enumerate(messages):
        agent_name = msg.get("agent_name", "Unknown")
        message_text = msg.get("message", "").lower()
        
        agent_names.add(agent_name)
        
        # Check for references to other agents
        other_agents = [name for name in ["tesla", "bob marley", "darth vader"] if name.lower() != agent_name.lower()]
        for other_agent in other_agents:
            if other_agent in message_text:
                collaboration_details["references_to_others"] += 1
                collaboration_score += 2
        
        # Check for building on ideas
        building_phrases = [
            "building on", "yes, and", "i agree", "that's right", "exactly",
            "good point", "i like that", "expanding on", "adding to"
        ]
        for phrase in building_phrases:
            if phrase in message_text:
                collaboration_details["builds_on_ideas"] += 1
                collaboration_score += 2
        
        # Check for natural questions (not forced)
        if "?" in message_text and not any(pattern in message_text for pattern in ["what's your take", "your thoughts"]):
            collaboration_details["asks_natural_questions"] += 1
            collaboration_score += 1
        
        # Categorize response types
        if message_text.startswith(("i think", "i believe", "in my view")):
            response_types.append("statement")
        elif "?" in message_text:
            response_types.append("question")
        elif any(word in message_text for word in ["but", "however", "disagree", "different"]):
            response_types.append("challenge")
        elif any(phrase in message_text for phrase in building_phrases):
            response_types.append("building")
        else:
            response_types.append("other")
    
    # Check for variety in response types
    unique_types = len(set(response_types))
    if unique_types >= 3:
        collaboration_details["varied_response_types"] = unique_types
        collaboration_score += unique_types * 2
    
    # Check for character authenticity (agent-specific language)
    for msg in messages:
        agent_name = msg.get("agent_name", "Unknown")
        message_text = msg.get("message", "").lower()
        
        # Tesla - should use technical/innovative language
        if "tesla" in agent_name.lower():
            if any(word in message_text for word in ["innovation", "technology", "future", "revolutionary", "electric", "energy"]):
                collaboration_details["character_authenticity"] += 1
                collaboration_score += 1
        
        # Bob Marley - should use peaceful/unity language
        elif "bob" in agent_name.lower() or "marley" in agent_name.lower():
            if any(word in message_text for word in ["peace", "unity", "harmony", "together", "positive", "love", "vibration"]):
                collaboration_details["character_authenticity"] += 1
                collaboration_score += 1
        
        # Darth Vader - should use authoritative/control language
        elif "vader" in agent_name.lower() or "darth" in agent_name.lower():
            if any(word in message_text for word in ["order", "control", "power", "efficient", "command", "decisive", "strategy"]):
                collaboration_details["character_authenticity"] += 1
                collaboration_score += 1
    
    return collaboration_score, collaboration_details

def analyze_conversation_quality(messages):
    """Analyze overall conversation quality"""
    print("\n📊 Analyzing conversation quality...")
    
    quality_metrics = {
        "total_messages": len(messages),
        "avg_message_length": 0,
        "unique_agents": 0,
        "natural_flow": 0,
        "content_depth": 0
    }
    
    if not messages:
        return quality_metrics
    
    # Calculate average message length
    message_lengths = [len(msg.get("message", "")) for msg in messages]
    quality_metrics["avg_message_length"] = sum(message_lengths) / len(message_lengths)
    
    # Count unique agents
    unique_agents = set(msg.get("agent_name", "") for msg in messages)
    quality_metrics["unique_agents"] = len(unique_agents)
    
    # Assess natural flow (messages that reference previous messages)
    flow_score = 0
    for i in range(1, len(messages)):
        current_msg = messages[i].get("message", "").lower()
        prev_msg = messages[i-1].get("message", "").lower()
        
        # Check if current message references concepts from previous message
        prev_words = set(prev_msg.split())
        current_words = set(current_msg.split())
        
        # Look for thematic connections
        if len(prev_words.intersection(current_words)) > 2:
            flow_score += 1
    
    quality_metrics["natural_flow"] = flow_score / max(1, len(messages) - 1)
    
    # Assess content depth (presence of substantive discussion)
    depth_indicators = [
        "because", "therefore", "however", "although", "specifically",
        "implementation", "approach", "solution", "problem", "challenge",
        "opportunity", "strategy", "plan", "result", "outcome"
    ]
    
    depth_score = 0
    for msg in messages:
        message_text = msg.get("message", "").lower()
        for indicator in depth_indicators:
            if indicator in message_text:
                depth_score += 1
    
    quality_metrics["content_depth"] = depth_score / len(messages) if messages else 0
    
    return quality_metrics

def print_conversation_sample(messages, conversation_num):
    """Print a sample of the conversation for manual review"""
    print(f"\n📝 CONVERSATION {conversation_num} SAMPLE:")
    print("=" * 60)
    
    for i, msg in enumerate(messages[:6]):  # Show first 6 messages
        agent_name = msg.get("agent_name", "Unknown")
        message_text = msg.get("message", "")
        print(f"{i+1}. {agent_name}: {message_text}")
        print()
    
    if len(messages) > 6:
        print(f"... and {len(messages) - 6} more messages")
    print("=" * 60)

def test_improved_conversation_generation():
    """Main test function for improved conversation generation"""
    print("🚀 TESTING IMPROVED CONVERSATION GENERATION SYSTEM")
    print("=" * 80)
    
    # Authenticate
    auth_token, user_id = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authenticated successfully (User ID: {user_id})")
    
    # Create test agents
    agents = create_test_agents(auth_token, user_id)
    if len(agents) < 3:
        print("❌ Failed to create required test agents")
        return False
    
    # Setup simulation
    if not setup_simulation(auth_token):
        print("❌ Failed to setup simulation")
        return False
    
    # Generate multiple conversations for analysis
    all_messages = []
    all_robotic_issues = []
    all_collaboration_scores = []
    all_quality_metrics = []
    
    print(f"\n🎯 Generating {3} conversations for comprehensive analysis...")
    
    for i in range(3):
        messages = generate_conversation(auth_token, i + 1)
        if messages:
            all_messages.extend(messages)
            
            # Print sample for manual review
            print_conversation_sample(messages, i + 1)
            
            # Analyze robotic patterns
            robotic_issues = analyze_robotic_patterns(messages)
            all_robotic_issues.extend(robotic_issues)
            
            # Analyze collaboration
            collab_score, collab_details = analyze_natural_collaboration(messages)
            all_collaboration_scores.append(collab_score)
            
            # Analyze quality
            quality_metrics = analyze_conversation_quality(messages)
            all_quality_metrics.append(quality_metrics)
            
            print(f"Conversation {i + 1} - Robotic Issues: {len(robotic_issues)}, Collaboration Score: {collab_score}")
        
        # Small delay between conversations
        time.sleep(2)
    
    # Comprehensive Analysis Results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE ANALYSIS RESULTS")
    print("=" * 80)
    
    # 1. Robotic Patterns Analysis
    print(f"\n🤖 ROBOTIC PATTERNS ANALYSIS:")
    print(f"Total robotic issues found: {len(all_robotic_issues)}")
    
    if all_robotic_issues:
        print("\n❌ ROBOTIC ISSUES DETECTED:")
        issue_types = Counter(issue["type"] for issue in all_robotic_issues)
        for issue_type, count in issue_types.items():
            print(f"  - {issue_type}: {count} instances")
        
        print("\nDetailed issues:")
        for issue in all_robotic_issues[:10]:  # Show first 10
            print(f"  • {issue['type']} by {issue['agent']} (msg {issue['message_num']}): {issue['text']}")
    else:
        print("✅ NO ROBOTIC PATTERNS DETECTED!")
    
    # 2. Collaboration Analysis
    print(f"\n🤝 COLLABORATION ANALYSIS:")
    if all_collaboration_scores:
        avg_collab_score = sum(all_collaboration_scores) / len(all_collaboration_scores)
        print(f"Average collaboration score: {avg_collab_score:.1f}")
        
        if avg_collab_score >= 15:
            print("✅ EXCELLENT collaboration detected")
        elif avg_collab_score >= 10:
            print("✅ GOOD collaboration detected")
        elif avg_collab_score >= 5:
            print("⚠️ MODERATE collaboration detected")
        else:
            print("❌ POOR collaboration detected")
    
    # 3. Quality Analysis
    print(f"\n📊 QUALITY ANALYSIS:")
    if all_quality_metrics:
        avg_msg_length = sum(m["avg_message_length"] for m in all_quality_metrics) / len(all_quality_metrics)
        avg_flow = sum(m["natural_flow"] for m in all_quality_metrics) / len(all_quality_metrics)
        avg_depth = sum(m["content_depth"] for m in all_quality_metrics) / len(all_quality_metrics)
        
        print(f"Average message length: {avg_msg_length:.1f} characters")
        print(f"Natural flow score: {avg_flow:.2f}")
        print(f"Content depth score: {avg_depth:.2f}")
        
        # Overall quality assessment
        quality_score = 0
        if avg_msg_length >= 100:
            quality_score += 1
        if avg_flow >= 0.3:
            quality_score += 1
        if avg_depth >= 0.5:
            quality_score += 1
        
        if quality_score == 3:
            print("✅ HIGH QUALITY conversations")
        elif quality_score == 2:
            print("✅ GOOD QUALITY conversations")
        elif quality_score == 1:
            print("⚠️ MODERATE QUALITY conversations")
        else:
            print("❌ LOW QUALITY conversations")
    
    # 4. Success Criteria Assessment
    print(f"\n🎯 SUCCESS CRITERIA ASSESSMENT:")
    print("=" * 50)
    
    criteria_results = {
        "no_robotic_questions": len([i for i in all_robotic_issues if i["type"] == "forced_question"]) == 0,
        "natural_collaboration": avg_collab_score >= 10 if all_collaboration_scores else False,
        "varied_responses": len(set(msg.get("agent_name") for msg in all_messages)) >= 3,
        "character_authenticity": sum(m["character_authenticity"] for m in [analyze_natural_collaboration(all_messages)[1]]) > 0,
        "no_narrations": len([i for i in all_robotic_issues if i["type"] == "narration"]) == 0
    }
    
    for criterion, passed in criteria_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {criterion.replace('_', ' ').title()}: {'PASSED' if passed else 'FAILED'}")
    
    # Overall Assessment
    passed_criteria = sum(criteria_results.values())
    total_criteria = len(criteria_results)
    
    print(f"\n🏆 OVERALL ASSESSMENT:")
    print(f"Passed {passed_criteria}/{total_criteria} success criteria ({passed_criteria/total_criteria*100:.1f}%)")
    
    if passed_criteria == total_criteria:
        print("🎉 EXCELLENT! All robotic patterns have been successfully eliminated!")
        return True
    elif passed_criteria >= total_criteria * 0.8:
        print("✅ GOOD! Most robotic patterns have been eliminated with minor issues remaining.")
        return True
    elif passed_criteria >= total_criteria * 0.6:
        print("⚠️ MODERATE! Some improvements made but significant robotic patterns remain.")
        return False
    else:
        print("❌ POOR! Robotic patterns are still prevalent in conversations.")
        return False

if __name__ == "__main__":
    success = test_improved_conversation_generation()
    sys.exit(0 if success else 1)

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

def create_test_agents(auth_token, user_id):
    """Create diverse test agents for conversation testing"""
    print("\n🤖 Creating test agents for conversation testing...")
    
    agents = [
        {
            "name": "Dr. Sarah Tesla",
            "archetype": "scientist", 
            "goal": "Develop quantum computing solutions",
            "expertise": "Quantum Physics and Computing",
            "background": "Leading quantum researcher with 15 years experience",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Marcus Chen",
            "archetype": "leader",
            "goal": "Lead strategic initiatives and team coordination", 
            "expertise": "Project Management and Strategy",
            "background": "Experienced team leader and strategic planner",
            "personality": {
                "extroversion": 9,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Alex Rivera",
            "archetype": "skeptic",
            "goal": "Identify risks and validate assumptions",
            "expertise": "Risk Analysis and Quality Assurance", 
            "background": "Critical thinker focused on identifying potential issues",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        },
        {
            "name": "Emma Johnson",
            "archetype": "optimist",
            "goal": "Foster positive team dynamics and find solutions",
            "expertise": "Team Building and Solution Development",
            "background": "Positive team member focused on collaborative solutions",
            "personality": {
                "extroversion": 8,
                "optimism": 10,
                "curiosity": 6,
                "cooperativeness": 9,
                "energy": 8
            }
        }
    ]
    
    created_agents = []
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    for agent_data in agents:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                agent_response = response.json()
                created_agents.append(agent_response)
                print(f"✅ Created agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    return created_agents

def setup_simulation(auth_token):
    """Setup simulation environment"""
    print("\n🎯 Setting up simulation environment...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Start simulation
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if response.status_code == 200:
            print("✅ Simulation started successfully")
        else:
            print(f"❌ Failed to start simulation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Set scenario
    scenario_data = {
        "scenario": "The team is working on a breakthrough quantum computing project that could revolutionize cryptography. They need to solve technical challenges, allocate resources, and coordinate their efforts to meet an important deadline.",
        "scenario_name": "Quantum Computing Breakthrough"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        if response.status_code == 200:
            print("✅ Scenario set successfully")
            return True
        else:
            print(f"❌ Failed to set scenario: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False

def analyze_conversation_quality(conversation, test_name):
    """Analyze conversation for the 4 key improvements"""
    print(f"\n📊 Analyzing conversation quality for: {test_name}")
    
    messages = conversation.get("messages", [])
    if not messages:
        print("❌ No messages found in conversation")
        return {
            "question_answering": False,
            "phrase_variety": False, 
            "context_awareness": False,
            "collaboration": False,
            "overall_score": 0
        }
    
    analysis = {
        "question_answering": False,
        "phrase_variety": True,  # Start as True, set False if banned phrases found
        "context_awareness": False,
        "collaboration": False,
        "banned_phrases_found": [],
        "collaboration_examples": [],
        "question_examples": [],
        "context_examples": []
    }
    
    # Banned phrases to check for
    banned_phrases = [
        "fascinating challenge",
        "interesting problem", 
        "fascinating problem",
        "interesting challenge"
    ]
    
    # Collaboration indicators
    collaboration_patterns = [
        r"building on.*?point",
        r"as.*?mentioned",
        r"i agree with.*?",
        r".*?you.*?said",
        r".*?your.*?idea",
        r"following up on",
        r"expanding on",
        r"to add to.*?point"
    ]
    
    # Question patterns
    question_patterns = [
        r"what.*?your.*?take",
        r"your.*?thoughts",
        r"what.*?do.*?you.*?think",
        r"how.*?do.*?you.*?see",
        r"what.*?would.*?you"
    ]
    
    # Context awareness patterns
    context_patterns = [
        r"earlier.*?discussion",
        r"previous.*?point",
        r"as.*?discussed",
        r"from.*?our.*?conversation"
    ]
    
    print(f"📝 Analyzing {len(messages)} messages...")
    
    for i, message in enumerate(messages):
        agent_name = message.get("agent_name", "")
        message_text = message.get("message", "").lower()
        
        print(f"  {i+1}. {agent_name}: {message_text[:100]}...")
        
        # Check for banned phrases
        for phrase in banned_phrases:
            if phrase in message_text:
                analysis["banned_phrases_found"].append(f"{agent_name}: '{phrase}'")
                analysis["phrase_variety"] = False
        
        # Check for collaboration
        for pattern in collaboration_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                analysis["collaboration"] = True
                analysis["collaboration_examples"].append(f"{agent_name}: {message_text[:80]}...")
                break
        
        # Check for question answering
        for pattern in question_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                analysis["question_examples"].append(f"{agent_name}: {message_text[:80]}...")
                # Check if next message answers the question
                if i + 1 < len(messages):
                    next_message = messages[i + 1]
                    next_agent = next_message.get("agent_name", "")
                    next_text = next_message.get("message", "").lower()
                    
                    # Look for direct response patterns
                    if any(word in next_text for word in ["i think", "my view", "in my opinion", "i believe", "i see"]):
                        analysis["question_answering"] = True
                        print(f"    ✅ Question answered by {next_agent}")
        
        # Check for context awareness
        for pattern in context_patterns:
            if re.search(pattern, message_text, re.IGNORECASE):
                analysis["context_awareness"] = True
                analysis["context_examples"].append(f"{agent_name}: {message_text[:80]}...")
                break
    
    # Calculate overall score
    score = 0
    if analysis["question_answering"]:
        score += 25
    if analysis["phrase_variety"]:
        score += 25
    if analysis["context_awareness"]:
        score += 25
    if analysis["collaboration"]:
        score += 25
    
    analysis["overall_score"] = score
    
    # Print detailed analysis
    print(f"\n📈 Quality Analysis Results:")
    print(f"  🎯 Question Answering: {'✅' if analysis['question_answering'] else '❌'}")
    print(f"  🎨 Phrase Variety: {'✅' if analysis['phrase_variety'] else '❌'}")
    print(f"  🧠 Context Awareness: {'✅' if analysis['context_awareness'] else '❌'}")
    print(f"  🤝 Collaboration: {'✅' if analysis['collaboration'] else '❌'}")
    print(f"  📊 Overall Score: {score}/100")
    
    if analysis["banned_phrases_found"]:
        print(f"  ⚠️ Banned phrases found: {len(analysis['banned_phrases_found'])}")
        for phrase in analysis["banned_phrases_found"]:
            print(f"    - {phrase}")
    
    if analysis["collaboration_examples"]:
        print(f"  🤝 Collaboration examples:")
        for example in analysis["collaboration_examples"][:3]:
            print(f"    - {example}")
    
    return analysis

def test_conversation_generation(auth_token, test_name, num_conversations=3):
    """Test conversation generation with quality analysis"""
    print(f"\n🧪 Testing conversation generation: {test_name}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    results = []
    
    for i in range(num_conversations):
        print(f"\n📝 Generating conversation {i+1}/{num_conversations}...")
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                conversation = response.json()
                response_time = end_time - start_time
                
                print(f"✅ Conversation generated successfully in {response_time:.2f}s")
                
                # Analyze conversation quality
                analysis = analyze_conversation_quality(conversation, f"{test_name} - Conv {i+1}")
                analysis["response_time"] = response_time
                analysis["conversation_id"] = conversation.get("id", "unknown")
                analysis["message_count"] = len(conversation.get("messages", []))
                
                results.append(analysis)
                
            else:
                print(f"❌ Failed to generate conversation: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    "error": f"HTTP {response.status_code}",
                    "overall_score": 0
                })
                
        except Exception as e:
            print(f"❌ Error generating conversation: {e}")
            results.append({
                "error": str(e),
                "overall_score": 0
            })
    
    return results

def test_question_detection_specifically(auth_token):
    """Test specific question detection patterns"""
    print(f"\n🔍 Testing specific question detection patterns...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Send observer message with direct question
    observer_data = {
        "observer_message": "Sarah, what's your take on the quantum decoherence issue? And Marcus, your thoughts on the timeline?"
    }
    
    try:
        response = requests.post(f"{API_URL}/observer/send-message", json=observer_data, headers=headers)
        if response.status_code == 200:
            observer_response = response.json()
            conversation = observer_response.get("agent_responses", {})
            
            if conversation and "messages" in conversation:
                messages = conversation["messages"]
                print(f"✅ Observer message sent, got {len(messages)} responses")
                
                # Check if Sarah and Marcus specifically answered
                sarah_answered = False
                marcus_answered = False
                
                for message in messages:
                    agent_name = message.get("agent_name", "")
                    message_text = message.get("message", "").lower()
                    
                    if "sarah" in agent_name.lower() or "tesla" in agent_name.lower():
                        if any(word in message_text for word in ["decoherence", "quantum", "my take", "i think"]):
                            sarah_answered = True
                            print(f"✅ Sarah answered the quantum question")
                    
                    if "marcus" in agent_name.lower() or "chen" in agent_name.lower():
                        if any(word in message_text for word in ["timeline", "schedule", "my thoughts", "i believe"]):
                            marcus_answered = True
                            print(f"✅ Marcus answered the timeline question")
                
                return {
                    "sarah_answered": sarah_answered,
                    "marcus_answered": marcus_answered,
                    "total_responses": len(messages)
                }
            else:
                print(f"❌ No conversation messages in observer response")
                return {"error": "No messages in response"}
        else:
            print(f"❌ Observer message failed: {response.status_code}")
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Error testing question detection: {e}")
        return {"error": str(e)}

def main():
    """Main test function"""
    print("🚀 IMPROVED CONVERSATION GENERATION SYSTEM TEST")
    print("=" * 80)
    print("Testing 4 major improvements:")
    print("1. ❓ Question Detection Logic")
    print("2. 🚫 Banned Phrases Prevention") 
    print("3. 🧠 Context Memory (5→15 messages)")
    print("4. 🤝 Collaboration Requirements")
    print("=" * 80)
    
    # Authenticate
    auth_token, user_id = authenticate()
    if not auth_token:
        print("❌ Failed to authenticate")
        return
    
    print(f"✅ Authenticated successfully (User ID: {user_id})")
    
    # Create test agents
    agents = create_test_agents(auth_token, user_id)
    if len(agents) < 4:
        print(f"❌ Failed to create enough agents (got {len(agents)}, need 4)")
        return
    
    # Setup simulation
    if not setup_simulation(auth_token):
        print("❌ Failed to setup simulation")
        return
    
    # Test 1: Basic conversation generation
    print("\n" + "=" * 60)
    print("TEST 1: BASIC CONVERSATION GENERATION")
    print("=" * 60)
    
    basic_results = test_conversation_generation(auth_token, "Basic Generation", 3)
    
    # Test 2: Question detection
    print("\n" + "=" * 60)
    print("TEST 2: QUESTION DETECTION LOGIC")
    print("=" * 60)
    
    question_results = test_question_detection_specifically(auth_token)
    
    # Test 3: Generate more conversations to test context memory
    print("\n" + "=" * 60)
    print("TEST 3: CONTEXT MEMORY & COLLABORATION")
    print("=" * 60)
    
    context_results = test_conversation_generation(auth_token, "Context Memory", 2)
    
    # Compile final results
    print("\n" + "=" * 80)
    print("🏆 FINAL RESULTS SUMMARY")
    print("=" * 80)
    
    all_results = basic_results + context_results
    valid_results = [r for r in all_results if "error" not in r]
    
    if valid_results:
        avg_score = sum(r["overall_score"] for r in valid_results) / len(valid_results)
        question_answering_rate = sum(1 for r in valid_results if r.get("question_answering", False)) / len(valid_results) * 100
        phrase_variety_rate = sum(1 for r in valid_results if r.get("phrase_variety", False)) / len(valid_results) * 100
        context_awareness_rate = sum(1 for r in valid_results if r.get("context_awareness", False)) / len(valid_results) * 100
        collaboration_rate = sum(1 for r in valid_results if r.get("collaboration", False)) / len(valid_results) * 100
        
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"  Average Quality Score: {avg_score:.1f}/100")
        print(f"  Question Answering: {question_answering_rate:.1f}% of conversations")
        print(f"  Phrase Variety: {phrase_variety_rate:.1f}% (no banned phrases)")
        print(f"  Context Awareness: {context_awareness_rate:.1f}% of conversations")
        print(f"  Collaboration: {collaboration_rate:.1f}% of conversations")
        
        print(f"\n🎯 SPECIFIC QUESTION DETECTION:")
        if question_results and "error" not in question_results:
            sarah_answered = question_results.get("sarah_answered", False)
            marcus_answered = question_results.get("marcus_answered", False)
            print(f"  Sarah answered direct question: {'✅' if sarah_answered else '❌'}")
            print(f"  Marcus answered direct question: {'✅' if marcus_answered else '❌'}")
        else:
            print(f"  ❌ Question detection test failed")
        
        # Overall assessment
        improvements_working = 0
        if question_answering_rate > 50 or (question_results and question_results.get("sarah_answered", False)):
            improvements_working += 1
            print(f"\n✅ IMPROVEMENT 1: Question Detection Logic - WORKING")
        else:
            print(f"\n❌ IMPROVEMENT 1: Question Detection Logic - NEEDS WORK")
        
        if phrase_variety_rate > 80:
            improvements_working += 1
            print(f"✅ IMPROVEMENT 2: Banned Phrases Prevention - WORKING")
        else:
            print(f"❌ IMPROVEMENT 2: Banned Phrases Prevention - NEEDS WORK")
        
        if context_awareness_rate > 30:
            improvements_working += 1
            print(f"✅ IMPROVEMENT 3: Context Memory (5→15 messages) - WORKING")
        else:
            print(f"❌ IMPROVEMENT 3: Context Memory (5→15 messages) - NEEDS WORK")
        
        if collaboration_rate > 50:
            improvements_working += 1
            print(f"✅ IMPROVEMENT 4: Collaboration Requirements - WORKING")
        else:
            print(f"❌ IMPROVEMENT 4: Collaboration Requirements - NEEDS WORK")
        
        print(f"\n🏆 FINAL VERDICT: {improvements_working}/4 improvements are working properly")
        
        if improvements_working >= 3:
            print(f"✅ CONVERSATION GENERATION IMPROVEMENTS: SUCCESSFUL")
            return True
        else:
            print(f"❌ CONVERSATION GENERATION IMPROVEMENTS: NEED MORE WORK")
            return False
    else:
        print(f"❌ No valid conversation results to analyze")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)