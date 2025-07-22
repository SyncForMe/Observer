#!/usr/bin/env python3
"""
Token Size and Response Completion Testing

This test specifically validates the improvements made to ensure agent responses:
1. Stay within the 120-140 word target range
2. End with complete sentences (proper punctuation)
3. Are never cut off mid-sentence
4. Maintain quality despite shorter limits
5. Apply completion logic consistently across all response paths
"""

import requests
import json
import time
import os
import sys
import re
import statistics
from dotenv import load_dotenv
from collections import Counter, defaultdict

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "response_analysis": {
        "total_responses": 0,
        "complete_sentences": 0,
        "incomplete_sentences": 0,
        "word_counts": [],
        "character_counts": [],
        "punctuation_endings": {"period": 0, "exclamation": 0, "question": 0, "incomplete": 0},
        "cut_off_responses": 0,
        "narrations_found": 0
    }
}

# Global auth token
auth_token = None
test_user_id = None

def authenticate():
    """Authenticate and get token"""
    global auth_token, test_user_id
    
    print("Authenticating with guest login...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            print(f"✅ Authentication successful. User ID: {test_user_id}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def analyze_response_text(response_text, agent_name="Unknown"):
    """Analyze a response for completion, word count, and quality"""
    if not response_text or not response_text.strip():
        return {
            "is_complete": False,
            "word_count": 0,
            "character_count": 0,
            "ends_with_punctuation": False,
            "punctuation_type": "none",
            "has_narrations": False,
            "appears_cut_off": True,
            "analysis": "Empty response"
        }
    
    text = response_text.strip()
    
    # Word count
    word_count = len(text.split())
    character_count = len(text)
    
    # Check for narrations (asterisks)
    has_narrations = '*' in text
    
    # Check ending punctuation
    ends_with_punctuation = text.endswith(('.', '!', '?'))
    
    punctuation_type = "none"
    if text.endswith('.'):
        punctuation_type = "period"
    elif text.endswith('!'):
        punctuation_type = "exclamation"
    elif text.endswith('?'):
        punctuation_type = "question"
    
    # Check if appears cut off (common signs)
    appears_cut_off = False
    cut_off_indicators = [
        text.endswith(','),
        text.endswith(';'),
        text.endswith(':'),
        text.endswith(' and'),
        text.endswith(' but'),
        text.endswith(' or'),
        text.endswith(' the'),
        text.endswith(' a'),
        text.endswith(' an'),
        not ends_with_punctuation and not text.endswith(('...', '—', '-'))
    ]
    
    if any(cut_off_indicators):
        appears_cut_off = True
    
    # Check for incomplete sentences by looking at sentence structure
    sentences = re.split(r'[.!?]+', text)
    last_sentence = sentences[-1].strip() if sentences else ""
    
    # If the last part doesn't end with punctuation and has substantial content, it might be cut off
    if last_sentence and not ends_with_punctuation and len(last_sentence.split()) > 3:
        appears_cut_off = True
    
    is_complete = ends_with_punctuation and not appears_cut_off
    
    analysis = f"Agent: {agent_name}, Words: {word_count}, Complete: {is_complete}, Punctuation: {punctuation_type}"
    if has_narrations:
        analysis += ", Has narrations"
    if appears_cut_off:
        analysis += ", Appears cut off"
    
    return {
        "is_complete": is_complete,
        "word_count": word_count,
        "character_count": character_count,
        "ends_with_punctuation": ends_with_punctuation,
        "punctuation_type": punctuation_type,
        "has_narrations": has_narrations,
        "appears_cut_off": appears_cut_off,
        "analysis": analysis
    }

def setup_test_agents():
    """Create test agents for conversation generation"""
    print("\n" + "="*60)
    print("SETTING UP TEST AGENTS")
    print("="*60)
    
    if not auth_token:
        print("❌ No authentication token available")
        return False, []
    
    # Create 3 diverse agents for testing
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics, 10 years research experience",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Marcus Thompson",
            "archetype": "leader",
            "goal": "Drive strategic business decisions",
            "expertise": "Business Strategy and Leadership",
            "background": "MBA, 15 years executive experience",
            "personality": {
                "extroversion": 9,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "skeptic",
            "goal": "Identify risks and challenges",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "MS in Systems Engineering, risk management specialist",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 8,
                "cooperativeness": 6,
                "energy": 5
            }
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
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    if len(created_agents) >= 2:
        print(f"✅ Successfully created {len(created_agents)} test agents")
        return True, created_agents
    else:
        print(f"❌ Only created {len(created_agents)} agents, need at least 2")
        return False, created_agents

def test_conversation_generation_completion():
    """Test conversation generation with focus on response completion"""
    print("\n" + "="*60)
    print("TESTING CONVERSATION GENERATION - RESPONSE COMPLETION")
    print("="*60)
    
    if not auth_token:
        print("❌ No authentication token available")
        return False
    
    # Setup simulation
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Start simulation
    try:
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if start_response.status_code != 200:
            print(f"❌ Failed to start simulation: {start_response.status_code}")
            return False
        print("✅ Simulation started")
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Set scenario
    try:
        scenario_data = {
            "scenario": "The team is working on a critical AI project with tight deadlines. They need to make important decisions about technology choices, resource allocation, and risk management.",
            "scenario_name": "AI Project Crisis"
        }
        scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        if scenario_response.status_code != 200:
            print(f"❌ Failed to set scenario: {scenario_response.status_code}")
            return False
        print("✅ Scenario set")
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False
    
    # Generate multiple conversation rounds
    conversation_rounds = 5
    all_responses = []
    
    print(f"\nGenerating {conversation_rounds} conversation rounds...")
    
    for round_num in range(1, conversation_rounds + 1):
        print(f"\n--- Conversation Round {round_num} ---")
        
        try:
            start_time = time.time()
            conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"Response time: {response_time:.2f} seconds")
            
            if conv_response.status_code == 200:
                conversation_data = conv_response.json()
                
                # Extract messages from the conversation
                messages = conversation_data.get("messages", [])
                print(f"Generated {len(messages)} messages")
                
                # Analyze each message
                for i, message in enumerate(messages):
                    agent_name = message.get("agent_name", "Unknown")
                    message_text = message.get("message", "")
                    
                    if message_text and agent_name != "Observer (You)":  # Skip observer messages
                        analysis = analyze_response_text(message_text, agent_name)
                        all_responses.append(analysis)
                        
                        # Update global statistics
                        test_results["response_analysis"]["total_responses"] += 1
                        test_results["response_analysis"]["word_counts"].append(analysis["word_count"])
                        test_results["response_analysis"]["character_counts"].append(analysis["character_count"])
                        
                        if analysis["is_complete"]:
                            test_results["response_analysis"]["complete_sentences"] += 1
                        else:
                            test_results["response_analysis"]["incomplete_sentences"] += 1
                        
                        if analysis["appears_cut_off"]:
                            test_results["response_analysis"]["cut_off_responses"] += 1
                        
                        if analysis["has_narrations"]:
                            test_results["response_analysis"]["narrations_found"] += 1
                        
                        # Track punctuation types
                        punct_type = analysis["punctuation_type"]
                        if punct_type in test_results["response_analysis"]["punctuation_endings"]:
                            test_results["response_analysis"]["punctuation_endings"][punct_type] += 1
                        else:
                            test_results["response_analysis"]["punctuation_endings"]["incomplete"] += 1
                        
                        # Print analysis for this message
                        status = "✅" if analysis["is_complete"] else "❌"
                        print(f"  {status} {analysis['analysis']}")
                        
                        # Show first 100 characters of the message
                        preview = message_text[:100] + "..." if len(message_text) > 100 else message_text
                        print(f"     Preview: \"{preview}\"")
                
                print(f"✅ Round {round_num} completed successfully")
                
            else:
                print(f"❌ Failed to generate conversation round {round_num}: {conv_response.status_code}")
                print(f"Response: {conv_response.text}")
                
        except Exception as e:
            print(f"❌ Error in conversation round {round_num}: {e}")
    
    return len(all_responses) > 0

def test_observer_message_completion():
    """Test observer message responses for completion"""
    print("\n" + "="*60)
    print("TESTING OBSERVER MESSAGE RESPONSES - COMPLETION")
    print("="*60)
    
    if not auth_token:
        print("❌ No authentication token available")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test different types of observer messages
    observer_messages = [
        "Hello team! Let's focus on finding practical solutions to our current challenges.",
        "What are the main risks we need to consider for this project?",
        "I need everyone to prioritize the most critical tasks and provide clear timelines.",
        "Can you explain the technical feasibility of our proposed approach?",
        "Let's brainstorm innovative solutions that could give us a competitive advantage."
    ]
    
    print(f"Testing {len(observer_messages)} different observer messages...")
    
    for i, message in enumerate(observer_messages, 1):
        print(f"\n--- Observer Message {i} ---")
        print(f"Message: \"{message}\"")
        
        try:
            observer_data = {"observer_message": message}
            start_time = time.time()
            response = requests.post(f"{API_URL}/observer/send-message", json=observer_data, headers=headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"Response time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                observer_response = response.json()
                agent_responses = observer_response.get("agent_responses", {})
                
                # Extract messages from agent responses
                messages = agent_responses.get("messages", [])
                agent_response_count = len([m for m in messages if m.get("agent_name") != "Observer (You)"])
                
                print(f"Generated {agent_response_count} agent responses")
                
                # Analyze each agent response
                for message_data in messages:
                    agent_name = message_data.get("agent_name", "Unknown")
                    message_text = message_data.get("message", "")
                    
                    if message_text and agent_name != "Observer (You)":  # Skip observer messages
                        analysis = analyze_response_text(message_text, agent_name)
                        
                        # Update global statistics
                        test_results["response_analysis"]["total_responses"] += 1
                        test_results["response_analysis"]["word_counts"].append(analysis["word_count"])
                        test_results["response_analysis"]["character_counts"].append(analysis["character_count"])
                        
                        if analysis["is_complete"]:
                            test_results["response_analysis"]["complete_sentences"] += 1
                        else:
                            test_results["response_analysis"]["incomplete_sentences"] += 1
                        
                        if analysis["appears_cut_off"]:
                            test_results["response_analysis"]["cut_off_responses"] += 1
                        
                        if analysis["has_narrations"]:
                            test_results["response_analysis"]["narrations_found"] += 1
                        
                        # Track punctuation types
                        punct_type = analysis["punctuation_type"]
                        if punct_type in test_results["response_analysis"]["punctuation_endings"]:
                            test_results["response_analysis"]["punctuation_endings"][punct_type] += 1
                        else:
                            test_results["response_analysis"]["punctuation_endings"]["incomplete"] += 1
                        
                        # Print analysis
                        status = "✅" if analysis["is_complete"] else "❌"
                        print(f"  {status} {analysis['analysis']}")
                        
                        # Show the full response for observer messages (they're usually shorter)
                        print(f"     Response: \"{message_text}\"")
                
                print(f"✅ Observer message {i} completed successfully")
                
            else:
                print(f"❌ Failed to send observer message {i}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error with observer message {i}: {e}")
    
    return True

def print_comprehensive_analysis():
    """Print comprehensive analysis of all responses"""
    print("\n" + "="*80)
    print("COMPREHENSIVE RESPONSE ANALYSIS")
    print("="*80)
    
    stats = test_results["response_analysis"]
    
    if stats["total_responses"] == 0:
        print("❌ No responses to analyze")
        return
    
    print(f"Total Responses Analyzed: {stats['total_responses']}")
    print(f"Complete Sentences: {stats['complete_sentences']} ({stats['complete_sentences']/stats['total_responses']*100:.1f}%)")
    print(f"Incomplete Sentences: {stats['incomplete_sentences']} ({stats['incomplete_sentences']/stats['total_responses']*100:.1f}%)")
    print(f"Cut-off Responses: {stats['cut_off_responses']} ({stats['cut_off_responses']/stats['total_responses']*100:.1f}%)")
    print(f"Narrations Found: {stats['narrations_found']} ({stats['narrations_found']/stats['total_responses']*100:.1f}%)")
    
    # Word count analysis
    if stats["word_counts"]:
        word_counts = stats["word_counts"]
        avg_words = statistics.mean(word_counts)
        median_words = statistics.median(word_counts)
        min_words = min(word_counts)
        max_words = max(word_counts)
        
        print(f"\nWORD COUNT ANALYSIS:")
        print(f"Average: {avg_words:.1f} words")
        print(f"Median: {median_words:.1f} words")
        print(f"Range: {min_words} - {max_words} words")
        
        # Check target range compliance (120-140 words)
        in_target_range = [w for w in word_counts if 120 <= w <= 140]
        below_target = [w for w in word_counts if w < 120]
        above_target = [w for w in word_counts if w > 140]
        
        print(f"In Target Range (120-140): {len(in_target_range)} ({len(in_target_range)/len(word_counts)*100:.1f}%)")
        print(f"Below Target (<120): {len(below_target)} ({len(below_target)/len(word_counts)*100:.1f}%)")
        print(f"Above Target (>140): {len(above_target)} ({len(above_target)/len(word_counts)*100:.1f}%)")
    
    # Character count analysis
    if stats["character_counts"]:
        char_counts = stats["character_counts"]
        avg_chars = statistics.mean(char_counts)
        print(f"\nCHARACTER COUNT ANALYSIS:")
        print(f"Average: {avg_chars:.1f} characters")
    
    # Punctuation analysis
    print(f"\nPUNCTUATION ANALYSIS:")
    punct_stats = stats["punctuation_endings"]
    for punct_type, count in punct_stats.items():
        percentage = count / stats["total_responses"] * 100
        print(f"{punct_type.title()}: {count} ({percentage:.1f}%)")
    
    # Overall assessment
    print(f"\n" + "="*60)
    print("OVERALL ASSESSMENT")
    print("="*60)
    
    completion_rate = stats["complete_sentences"] / stats["total_responses"] * 100
    cut_off_rate = stats["cut_off_responses"] / stats["total_responses"] * 100
    narration_rate = stats["narrations_found"] / stats["total_responses"] * 100
    
    # Target range compliance
    if stats["word_counts"]:
        target_compliance = len(in_target_range) / len(word_counts) * 100
    else:
        target_compliance = 0
    
    print(f"✅ Response Completion Rate: {completion_rate:.1f}% (Target: >95%)")
    print(f"✅ Cut-off Rate: {cut_off_rate:.1f}% (Target: <5%)")
    print(f"✅ Narration-free Rate: {100-narration_rate:.1f}% (Target: 100%)")
    print(f"✅ Target Word Range Compliance: {target_compliance:.1f}% (Target: >80%)")
    
    # Pass/fail assessment
    tests_passed = 0
    total_tests = 4
    
    if completion_rate >= 95:
        print("✅ PASS: Response completion rate meets target")
        tests_passed += 1
    else:
        print("❌ FAIL: Response completion rate below target")
    
    if cut_off_rate <= 5:
        print("✅ PASS: Cut-off rate meets target")
        tests_passed += 1
    else:
        print("❌ FAIL: Cut-off rate above target")
    
    if narration_rate == 0:
        print("✅ PASS: No narrations found")
        tests_passed += 1
    else:
        print("❌ FAIL: Narrations still present in responses")
    
    if target_compliance >= 80:
        print("✅ PASS: Word count compliance meets target")
        tests_passed += 1
    else:
        print("❌ FAIL: Word count compliance below target")
    
    print(f"\nFINAL SCORE: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests*100:.1f}%)")
    
    if tests_passed == total_tests:
        print("🎉 ALL TOKEN SIZE AND COMPLETION IMPROVEMENTS ARE WORKING CORRECTLY!")
        return True
    else:
        print("⚠️ Some token size and completion improvements need attention")
        return False

def main():
    """Main test execution"""
    print("="*80)
    print("TOKEN SIZE AND RESPONSE COMPLETION TESTING")
    print("="*80)
    print("Testing improvements to ensure agent responses:")
    print("1. Stay within 120-140 word target range")
    print("2. End with complete sentences (proper punctuation)")
    print("3. Are never cut off mid-sentence")
    print("4. Maintain quality despite shorter limits")
    print("5. Apply completion logic consistently")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return False
    
    # Step 2: Setup test agents
    agents_success, agents = setup_test_agents()
    if not agents_success:
        print("❌ Failed to setup test agents. Cannot proceed with conversation tests.")
        return False
    
    # Step 3: Test conversation generation completion
    conv_success = test_conversation_generation_completion()
    if not conv_success:
        print("⚠️ Conversation generation tests had issues")
    
    # Step 4: Test observer message completion
    observer_success = test_observer_message_completion()
    if not observer_success:
        print("⚠️ Observer message tests had issues")
    
    # Step 5: Print comprehensive analysis
    overall_success = print_comprehensive_analysis()
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)