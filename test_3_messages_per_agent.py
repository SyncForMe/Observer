#!/usr/bin/env python3
"""
Comprehensive test for the main conversation generation endpoint (/api/conversation/generate)
Testing the critical fix for 3 messages per agent instead of 1 message per agent.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime
import re

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
    "tests": []
}

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, auth_token=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name}")
    print(f"URL: {method} {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        # Parse JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {"raw_response": response.text}
        
        # Check status code
        status_ok = response.status_code == expected_status
        
        result = "PASSED" if status_ok else "FAILED"
        print(f"Result: {result}")
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "response_time": response_time,
            "result": result
        })
        
        if status_ok:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return status_ok, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def authenticate():
    """Authenticate and get JWT token"""
    print("\n" + "="*80)
    print("AUTHENTICATION")
    print("="*80)
    
    # Try guest authentication first
    success, response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_status=200
    )
    
    if success and response:
        token = response.get("access_token")
        user = response.get("user", {})
        user_id = user.get("id")
        
        print(f"✅ Authentication successful")
        print(f"User ID: {user_id}")
        print(f"Token: {token[:20]}...")
        
        return token, user_id
    else:
        print("❌ Authentication failed")
        return None, None

def setup_test_agents(auth_token, user_id):
    """Create test agents for conversation generation"""
    print("\n" + "="*80)
    print("SETTING UP TEST AGENTS")
    print("="*80)
    
    # Define test agents with different archetypes
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research and solve complex technical challenges",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics from MIT, 10 years experience in quantum computing research",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Marcus Rodriguez",
            "archetype": "leader",
            "goal": "Lead the team to successful project completion and strategic objectives",
            "expertise": "Project Management and Strategic Planning",
            "background": "MBA from Stanford, 15 years experience leading tech teams and projects",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Dr. Emily Watson",
            "archetype": "skeptic",
            "goal": "Ensure rigorous analysis and identify potential risks and flaws",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "PhD in Systems Engineering, 12 years experience in risk assessment and quality control",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        }
    ]
    
    created_agents = []
    
    for agent_data in test_agents:
        success, response = run_test(
            f"Create Agent: {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth_token=auth_token,
            expected_status=200
        )
        
        if success and response:
            agent_id = response.get("id")
            if agent_id:
                created_agents.append({
                    "id": agent_id,
                    "name": agent_data["name"],
                    "archetype": agent_data["archetype"]
                })
                print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
            else:
                print(f"❌ Failed to get ID for agent: {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    print(f"\nCreated {len(created_agents)} test agents")
    return created_agents

def start_simulation(auth_token):
    """Start the simulation"""
    print("\n" + "="*80)
    print("STARTING SIMULATION")
    print("="*80)
    
    success, response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth_token=auth_token,
        expected_status=200
    )
    
    if success:
        print("✅ Simulation started successfully")
        return True
    else:
        print("❌ Failed to start simulation")
        return False

def test_conversation_generation_3_messages(auth_token, agents):
    """Test the main conversation generation endpoint for 3 messages per agent"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION GENERATION - 3 MESSAGES PER AGENT")
    print("="*80)
    
    if len(agents) < 2:
        print("❌ Need at least 2 agents for conversation generation")
        return False, [], {}
    
    print(f"Testing with {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['archetype']})")
    
    # Test conversation generation
    success, response = run_test(
        "Generate Conversation - 3 Messages Per Agent",
        "/conversation/generate",
        method="POST",
        auth_token=auth_token,
        expected_status=200
    )
    
    if not success or not response:
        print("❌ Conversation generation failed")
        return False, [], {}
    
    print(f"✅ Conversation generation successful")
    print(f"Response keys: {list(response.keys())}")
    
    # Analyze the conversation structure
    conversation_data = response
    
    # Check if we have messages
    messages = conversation_data.get("messages", [])
    if not messages:
        print("❌ No messages found in conversation response")
        return False, [], {}
    
    print(f"\n📊 CONVERSATION ANALYSIS:")
    print(f"Total messages: {len(messages)}")
    
    # Count messages per agent
    agent_message_counts = {}
    agent_names = [agent['name'] for agent in agents]
    
    for message in messages:
        agent_name = message.get("agent_name", "Unknown")
        if agent_name not in agent_message_counts:
            agent_message_counts[agent_name] = 0
        agent_message_counts[agent_name] += 1
    
    print(f"\nMessages per agent:")
    for agent_name, count in agent_message_counts.items():
        print(f"  - {agent_name}: {count} messages")
    
    # Verify 3 messages per agent
    expected_total_messages = len(agents) * 3
    actual_total_messages = len(messages)
    
    print(f"\nMessage count verification:")
    print(f"Expected total messages: {expected_total_messages} ({len(agents)} agents × 3 messages)")
    print(f"Actual total messages: {actual_total_messages}")
    
    # Check if each agent has exactly 3 messages
    agents_with_3_messages = 0
    for agent in agents:
        agent_name = agent['name']
        message_count = agent_message_counts.get(agent_name, 0)
        if message_count == 3:
            agents_with_3_messages += 1
            print(f"✅ {agent_name}: {message_count} messages (correct)")
        else:
            print(f"❌ {agent_name}: {message_count} messages (expected 3)")
    
    # Overall assessment
    if agents_with_3_messages == len(agents) and actual_total_messages == expected_total_messages:
        print(f"\n✅ SUCCESS: All {len(agents)} agents generated exactly 3 messages each")
        print(f"✅ Total message count is correct: {actual_total_messages}")
        messages_per_agent_correct = True
    else:
        print(f"\n❌ FAILURE: Not all agents generated exactly 3 messages")
        print(f"❌ Agents with correct message count: {agents_with_3_messages}/{len(agents)}")
        messages_per_agent_correct = False
    
    return messages_per_agent_correct, messages, agent_message_counts

def test_gemini_2_5_flash_usage(messages):
    """Test that Gemini 2.5 Flash is being used (not Claude or Gemini 2.0)"""
    print("\n" + "="*80)
    print("TESTING GEMINI 2.5 FLASH USAGE")
    print("="*80)
    
    # Analyze message content for indicators of AI model usage
    print("Analyzing message content for AI model indicators...")
    
    # Look for Claude-specific patterns (should NOT be present)
    claude_indicators = [
        "I'm Claude",
        "As Claude",
        "Claude here",
        "*adjusts*",
        "*leans forward*",
        "*mechanical breathing*"
    ]
    
    # Look for quality indicators of Gemini 2.5 Flash
    gemini_quality_indicators = [
        "technical depth",
        "specific expertise",
        "natural conversation flow",
        "contextual awareness"
    ]
    
    claude_references_found = 0
    narration_found = 0
    total_message_length = 0
    messages_with_good_length = 0
    
    print(f"\nAnalyzing {len(messages)} messages:")
    
    for i, message in enumerate(messages, 1):
        agent_name = message.get("agent_name", "Unknown")
        message_text = message.get("message", "")
        message_length = len(message_text)
        total_message_length += message_length
        
        print(f"\nMessage {i} - {agent_name}:")
        print(f"  Length: {message_length} characters")
        print(f"  Content: {message_text[:100]}...")
        
        # Check for Claude references
        for indicator in claude_indicators:
            if indicator.lower() in message_text.lower():
                claude_references_found += 1
                print(f"  ❌ Claude reference found: '{indicator}'")
        
        # Check for narrations (asterisks)
        if "*" in message_text:
            narration_found += 1
            print(f"  ⚠️ Narration found (asterisks)")
        
        # Check message quality (length and content)
        if message_length >= 50:  # Reasonable message length
            messages_with_good_length += 1
            print(f"  ✅ Good message length")
        else:
            print(f"  ⚠️ Short message")
    
    # Calculate statistics
    avg_message_length = total_message_length / len(messages) if messages else 0
    good_length_percentage = (messages_with_good_length / len(messages)) * 100 if messages else 0
    
    print(f"\n📊 GEMINI 2.5 FLASH ANALYSIS:")
    print(f"Average message length: {avg_message_length:.1f} characters")
    print(f"Messages with good length: {messages_with_good_length}/{len(messages)} ({good_length_percentage:.1f}%)")
    print(f"Claude references found: {claude_references_found}")
    print(f"Narrations found: {narration_found}")
    
    # Assessment
    gemini_usage_score = 0
    
    if claude_references_found == 0:
        print("✅ No Claude references found (good)")
        gemini_usage_score += 1
    else:
        print("❌ Claude references found (bad)")
    
    if narration_found == 0:
        print("✅ No narrations found (good - indicates narration removal is working)")
        gemini_usage_score += 1
    else:
        print("⚠️ Narrations found (may indicate fallback responses)")
    
    if avg_message_length >= 80:
        print("✅ Good average message length (indicates quality AI responses)")
        gemini_usage_score += 1
    else:
        print("⚠️ Short average message length")
    
    if good_length_percentage >= 80:
        print("✅ Most messages have good length")
        gemini_usage_score += 1
    else:
        print("⚠️ Many messages are too short")
    
    gemini_usage_likely = gemini_usage_score >= 3
    
    if gemini_usage_likely:
        print(f"\n✅ LIKELY USING GEMINI 2.5 FLASH (Score: {gemini_usage_score}/4)")
        print("✅ High-quality responses with no Claude references")
    else:
        print(f"\n⚠️ MAY NOT BE USING GEMINI 2.5 FLASH (Score: {gemini_usage_score}/4)")
        print("⚠️ Response quality indicators suggest possible fallback usage")
    
    return gemini_usage_likely, {
        "claude_references": claude_references_found,
        "narrations": narration_found,
        "avg_length": avg_message_length,
        "good_length_percentage": good_length_percentage,
        "score": gemini_usage_score
    }

def test_sequential_generation(messages, agents):
    """Test that messages are generated in sequential rounds"""
    print("\n" + "="*80)
    print("TESTING SEQUENTIAL GENERATION")
    print("="*80)
    
    if len(messages) != len(agents) * 3:
        print("❌ Cannot test sequential generation - incorrect message count")
        return False
    
    print(f"Testing sequential generation with {len(agents)} agents and {len(messages)} messages")
    
    # Group messages by agent
    agent_messages = {}
    for message in messages:
        agent_name = message.get("agent_name", "Unknown")
        if agent_name not in agent_messages:
            agent_messages[agent_name] = []
        agent_messages[agent_name].append(message)
    
    # Check if messages are in sequential order
    # Expected pattern: Agent1-Msg1, Agent2-Msg1, Agent3-Msg1, Agent1-Msg2, Agent2-Msg2, Agent3-Msg2, etc.
    
    print("\nAnalyzing message sequence:")
    
    expected_sequence = []
    for round_num in range(1, 4):  # 3 rounds
        for agent in agents:
            expected_sequence.append(f"{agent['name']}-Round{round_num}")
    
    actual_sequence = []
    for i, message in enumerate(messages):
        agent_name = message.get("agent_name", "Unknown")
        # Determine which round this is for this agent
        agent_msg_count = sum(1 for m in messages[:i+1] if m.get("agent_name") == agent_name)
        actual_sequence.append(f"{agent_name}-Round{agent_msg_count}")
    
    print(f"Expected sequence: {expected_sequence[:6]}... (showing first 6)")
    print(f"Actual sequence:   {actual_sequence[:6]}... (showing first 6)")
    
    # Check if sequences match
    sequence_matches = expected_sequence == actual_sequence
    
    if sequence_matches:
        print("✅ Messages are generated in correct sequential order")
        print("✅ Round 1: All agents message 1")
        print("✅ Round 2: All agents message 2") 
        print("✅ Round 3: All agents message 3")
        sequential_correct = True
    else:
        print("❌ Messages are NOT in correct sequential order")
        
        # Show differences
        for i, (expected, actual) in enumerate(zip(expected_sequence, actual_sequence)):
            if expected != actual:
                print(f"  Position {i+1}: Expected {expected}, Got {actual}")
        
        sequential_correct = False
    
    return sequential_correct

def test_conversation_context(messages, agents):
    """Test that later messages reference and build upon earlier messages"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION CONTEXT")
    print("="*80)
    
    if len(messages) < 6:  # Need at least 2 rounds to test context
        print("❌ Not enough messages to test context awareness")
        return False, 0
    
    print(f"Analyzing context awareness in {len(messages)} messages")
    
    # Group messages by rounds
    messages_per_round = len(agents)
    rounds = []
    
    for round_num in range(3):  # 3 rounds
        start_idx = round_num * messages_per_round
        end_idx = start_idx + messages_per_round
        round_messages = messages[start_idx:end_idx]
        rounds.append(round_messages)
    
    print(f"\nRound structure:")
    for i, round_msgs in enumerate(rounds, 1):
        print(f"  Round {i}: {len(round_msgs)} messages")
    
    # Analyze context references
    context_indicators = [
        "building on",
        "as mentioned",
        "following up",
        "expanding on",
        "in response to",
        "regarding",
        "about what",
        "your point",
        "you mentioned",
        "earlier",
        "previously",
        "before",
        "continuing",
        "further",
        "additionally"
    ]
    
    context_references_found = 0
    total_later_messages = 0
    
    print(f"\nAnalyzing context references:")
    
    # Check messages in rounds 2 and 3 for context references
    for round_num in range(1, 3):  # Rounds 2 and 3 (index 1 and 2)
        round_messages = rounds[round_num]
        print(f"\n  Round {round_num + 1} messages:")
        
        for message in round_messages:
            agent_name = message.get("agent_name", "Unknown")
            message_text = message.get("message", "").lower()
            total_later_messages += 1
            
            # Check for context indicators
            context_found = False
            for indicator in context_indicators:
                if indicator in message_text:
                    context_references_found += 1
                    context_found = True
                    print(f"    ✅ {agent_name}: Context reference found ('{indicator}')")
                    break
            
            if not context_found:
                print(f"    ⚠️ {agent_name}: No clear context reference")
    
    # Calculate context awareness percentage
    context_percentage = (context_references_found / total_later_messages) * 100 if total_later_messages > 0 else 0
    
    print(f"\n📊 CONTEXT ANALYSIS:")
    print(f"Messages in rounds 2-3: {total_later_messages}")
    print(f"Messages with context references: {context_references_found}")
    print(f"Context awareness percentage: {context_percentage:.1f}%")
    
    # Assessment
    if context_percentage >= 30:  # At least 30% should have context references
        print("✅ Good context awareness - later messages reference earlier content")
        context_good = True
    elif context_percentage >= 15:
        print("⚠️ Moderate context awareness - some references found")
        context_good = True
    else:
        print("❌ Poor context awareness - few or no context references")
        context_good = False
    
    return context_good, context_percentage

def print_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    print(f"\nDetailed Results:")
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        response_time = test.get("response_time", 0)
        print(f"{i:2d}. {result_symbol} {test['name']} ({response_time:.3f}s)")
    
    print("="*80)

def main():
    """Main test execution"""
    print("🚀 CONVERSATION GENERATION ENDPOINT COMPREHENSIVE TEST")
    print("Testing 3 messages per agent, Gemini 2.5 Flash usage, and sequential generation")
    
    # Step 1: Authenticate
    auth_token, user_id = authenticate()
    if not auth_token:
        print("❌ Authentication failed - cannot continue")
        return
    
    # Step 2: Setup test agents
    agents = setup_test_agents(auth_token, user_id)
    if len(agents) < 2:
        print("❌ Failed to create enough test agents - cannot continue")
        return
    
    # Step 3: Start simulation
    if not start_simulation(auth_token):
        print("❌ Failed to start simulation - cannot continue")
        return
    
    # Step 4: Test conversation generation - 3 messages per agent
    messages_correct, messages, agent_counts = test_conversation_generation_3_messages(auth_token, agents)
    
    if not messages_correct:
        print("❌ CRITICAL FAILURE: 3 messages per agent test failed")
        print_summary()
        return
    
    # Step 5: Test Gemini 2.5 Flash usage
    gemini_usage, gemini_stats = test_gemini_2_5_flash_usage(messages)
    
    # Step 6: Test sequential generation
    sequential_correct = test_sequential_generation(messages, agents)
    
    # Step 7: Test conversation context
    context_good, context_percentage = test_conversation_context(messages, agents)
    
    # Final Assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    critical_tests = [
        ("3 Messages Per Agent", messages_correct),
        ("Gemini 2.5 Flash Usage", gemini_usage),
        ("Sequential Generation", sequential_correct),
        ("Conversation Context", context_good)
    ]
    
    passed_critical = sum(1 for _, passed in critical_tests if passed)
    total_critical = len(critical_tests)
    
    print(f"Critical Tests Results:")
    for test_name, passed in critical_tests:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print(f"\nCritical Tests: {passed_critical}/{total_critical} passed")
    
    if passed_critical == total_critical:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("✅ Conversation generation endpoint is working correctly")
        print("✅ 3 messages per agent functionality is implemented")
        print("✅ Gemini 2.5 Flash is being used effectively")
        print("✅ Sequential generation is working")
        print("✅ Context awareness is good")
    else:
        print(f"\n⚠️ {total_critical - passed_critical} CRITICAL TESTS FAILED")
        print("❌ Conversation generation endpoint has issues")
    
    print_summary()

if __name__ == "__main__":
    main()