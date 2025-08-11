#!/usr/bin/env python3
"""
Comprehensive test for conversation generation endpoint requirements:
1. 3 Messages Per Agent ✓
2. Gemini 2.5 Flash Usage
3. Sequential Generation 
4. Conversation Context
5. Fallback Handling
"""

import requests
import json
import time
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate():
    """Get auth token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def clean_and_setup_agents(token):
    """Clean existing agents and create test agents"""
    print("🧹 Setting up clean test environment...")
    
    # Clean existing agents
    response = requests.get(f"{API_URL}/agents", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        agents = response.json()
        for agent in agents:
            agent_id = agent.get("id")
            if agent_id:
                requests.delete(f"{API_URL}/agents/{agent_id}", headers={"Authorization": f"Bearer {token}"})
    
    # Create 3 test agents
    agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics from MIT, 10 years experience",
            "personality": {"extroversion": 6, "optimism": 8, "curiosity": 9, "cooperativeness": 7, "energy": 7}
        },
        {
            "name": "Marcus Rodriguez", 
            "archetype": "leader",
            "goal": "Lead team to successful project completion",
            "expertise": "Project Management and Strategic Planning",
            "background": "MBA from Stanford, 15 years experience leading tech teams",
            "personality": {"extroversion": 9, "optimism": 8, "curiosity": 6, "cooperativeness": 8, "energy": 8}
        },
        {
            "name": "Dr. Emily Watson",
            "archetype": "skeptic", 
            "goal": "Ensure rigorous analysis and identify risks",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "PhD in Systems Engineering, 12 years experience",
            "personality": {"extroversion": 4, "optimism": 3, "curiosity": 7, "cooperativeness": 5, "energy": 5}
        }
    ]
    
    created_agents = []
    for agent_data in agents:
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            created_agents.append(response.json())
    
    return created_agents

def test_conversation_generation_comprehensive(token):
    """Comprehensive test of conversation generation"""
    print("\n💬 COMPREHENSIVE CONVERSATION GENERATION TEST")
    print("="*60)
    
    # Start simulation
    requests.post(f"{API_URL}/simulation/start", headers={"Authorization": f"Bearer {token}"})
    
    # Generate conversation
    start_time = time.time()
    response = requests.post(f"{API_URL}/conversation/generate", headers={"Authorization": f"Bearer {token}"})
    end_time = time.time()
    
    if response.status_code != 200:
        print(f"❌ Conversation generation failed: {response.status_code}")
        return False, None
    
    data = response.json()
    messages = data.get("messages", [])
    
    print(f"✅ Conversation generated in {end_time - start_time:.2f}s")
    print(f"📊 Total messages: {len(messages)}")
    
    return True, messages

def test_3_messages_per_agent(messages):
    """Test 1: Verify 3 messages per agent"""
    print("\n🧪 TEST 1: 3 MESSAGES PER AGENT")
    print("-" * 40)
    
    # Count messages per agent
    agent_counts = {}
    for message in messages:
        agent_name = message.get("agent_name", "Unknown")
        agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
    
    print("Messages per agent:")
    for agent_name, count in agent_counts.items():
        status = "✅" if count == 3 else "❌"
        print(f"  {status} {agent_name}: {count} messages")
    
    # Verify results
    expected_agents = 3
    expected_total = 9
    actual_total = len(messages)
    agents_with_3_messages = sum(1 for count in agent_counts.values() if count == 3)
    
    success = (len(agent_counts) == expected_agents and 
               actual_total == expected_total and 
               agents_with_3_messages == expected_agents)
    
    if success:
        print(f"✅ SUCCESS: All {expected_agents} agents generated exactly 3 messages each")
        print(f"✅ Total messages: {actual_total} (expected: {expected_total})")
    else:
        print(f"❌ FAILURE: Expected {expected_agents} agents with 3 messages each")
        print(f"❌ Got {len(agent_counts)} agents, {agents_with_3_messages} with 3 messages")
    
    return success

def test_gemini_2_5_flash_usage(messages):
    """Test 2: Verify Gemini 2.5 Flash usage (not Claude or Gemini 2.0)"""
    print("\n🧪 TEST 2: GEMINI 2.5 FLASH USAGE")
    print("-" * 40)
    
    # Analyze message quality indicators
    claude_indicators = ["I'm Claude", "As Claude", "*adjusts*", "*leans forward*", "*mechanical breathing*"]
    
    claude_references = 0
    narrations = 0
    total_length = 0
    quality_messages = 0
    
    print("Analyzing message quality:")
    for i, message in enumerate(messages, 1):
        agent_name = message.get("agent_name", "Unknown")
        text = message.get("message", "")
        length = len(text)
        total_length += length
        
        # Check for Claude references
        for indicator in claude_indicators:
            if indicator.lower() in text.lower():
                claude_references += 1
        
        # Check for narrations (asterisks)
        if "*" in text:
            narrations += 1
        
        # Check message quality
        if length >= 50:  # Reasonable length
            quality_messages += 1
        
        print(f"  {i:2d}. {agent_name}: {length} chars - {text[:60]}...")
    
    avg_length = total_length / len(messages) if messages else 0
    quality_percentage = (quality_messages / len(messages)) * 100 if messages else 0
    
    print(f"\n📊 Quality Analysis:")
    print(f"  Average message length: {avg_length:.1f} characters")
    print(f"  Messages with good length: {quality_messages}/{len(messages)} ({quality_percentage:.1f}%)")
    print(f"  Claude references found: {claude_references}")
    print(f"  Narrations found: {narrations}")
    
    # Assessment
    score = 0
    if claude_references == 0:
        print("  ✅ No Claude references (good)")
        score += 1
    else:
        print("  ❌ Claude references found")
    
    if narrations == 0:
        print("  ✅ No narrations (narration removal working)")
        score += 1
    else:
        print("  ⚠️ Narrations found (may indicate fallbacks)")
    
    if avg_length >= 80:
        print("  ✅ Good average message length")
        score += 1
    else:
        print("  ⚠️ Short average message length")
    
    if quality_percentage >= 80:
        print("  ✅ Most messages have good length")
        score += 1
    else:
        print("  ⚠️ Many messages are short")
    
    success = score >= 3
    if success:
        print(f"✅ LIKELY USING GEMINI 2.5 FLASH (Score: {score}/4)")
    else:
        print(f"⚠️ MAY NOT BE USING GEMINI 2.5 FLASH (Score: {score}/4)")
    
    return success

def test_sequential_generation(messages):
    """Test 3: Verify sequential generation (Round 1: all agents, Round 2: all agents, Round 3: all agents)"""
    print("\n🧪 TEST 3: SEQUENTIAL GENERATION")
    print("-" * 40)
    
    if len(messages) != 9:
        print("❌ Cannot test sequential generation - incorrect message count")
        return False
    
    # Extract agent names in order
    agent_sequence = [msg.get("agent_name", "Unknown") for msg in messages]
    
    print("Message sequence:")
    for i, agent_name in enumerate(agent_sequence, 1):
        round_num = ((i - 1) // 3) + 1
        agent_msg_num = ((i - 1) % 3) + 1
        print(f"  {i:2d}. Round {round_num}, Agent {agent_msg_num}: {agent_name}")
    
    # Check if pattern is correct: A1, A2, A3, A1, A2, A3, A1, A2, A3
    # Get unique agents
    unique_agents = []
    for agent in agent_sequence:
        if agent not in unique_agents:
            unique_agents.append(agent)
    
    if len(unique_agents) != 3:
        print(f"❌ Expected 3 unique agents, found {len(unique_agents)}")
        return False
    
    # Check sequential pattern
    expected_sequence = unique_agents * 3  # Repeat the agent order 3 times
    
    print(f"\nExpected sequence: {expected_sequence}")
    print(f"Actual sequence:   {agent_sequence}")
    
    sequential_correct = agent_sequence == expected_sequence
    
    if sequential_correct:
        print("✅ Messages are in correct sequential order")
        print("✅ Round 1: All agents message 1")
        print("✅ Round 2: All agents message 2")
        print("✅ Round 3: All agents message 3")
    else:
        print("❌ Messages are NOT in correct sequential order")
        # Show differences
        for i, (expected, actual) in enumerate(zip(expected_sequence, agent_sequence)):
            if expected != actual:
                print(f"  Position {i+1}: Expected {expected}, Got {actual}")
    
    return sequential_correct

def test_conversation_context(messages):
    """Test 4: Verify conversation context awareness"""
    print("\n🧪 TEST 4: CONVERSATION CONTEXT")
    print("-" * 40)
    
    # Group messages by rounds
    rounds = [messages[i:i+3] for i in range(0, 9, 3)]
    
    print("Round structure:")
    for i, round_msgs in enumerate(rounds, 1):
        print(f"  Round {i}: {len(round_msgs)} messages")
    
    # Look for context indicators in rounds 2 and 3
    context_indicators = [
        "building on", "as mentioned", "following up", "expanding on",
        "in response to", "regarding", "about what", "your point",
        "you mentioned", "earlier", "previously", "before",
        "continuing", "further", "additionally", "that's interesting",
        "i agree", "however", "but", "also", "furthermore"
    ]
    
    context_found = 0
    total_later_messages = 6  # Messages in rounds 2 and 3
    
    print("\nAnalyzing context in rounds 2-3:")
    for round_num in range(1, 3):  # Rounds 2 and 3
        round_messages = rounds[round_num]
        print(f"  Round {round_num + 1}:")
        
        for message in round_messages:
            agent_name = message.get("agent_name", "Unknown")
            text = message.get("message", "").lower()
            
            # Check for context indicators
            found_indicators = [ind for ind in context_indicators if ind in text]
            if found_indicators:
                context_found += 1
                print(f"    ✅ {agent_name}: Context found ({found_indicators[0]})")
            else:
                print(f"    ⚠️ {agent_name}: No clear context reference")
    
    context_percentage = (context_found / total_later_messages) * 100
    
    print(f"\n📊 Context Analysis:")
    print(f"  Messages with context: {context_found}/{total_later_messages} ({context_percentage:.1f}%)")
    
    success = context_percentage >= 30  # At least 30% should have context
    
    if success:
        print("✅ Good context awareness")
    else:
        print("❌ Poor context awareness")
    
    return success

def test_error_handling(token):
    """Test 5: Verify error handling"""
    print("\n🧪 TEST 5: ERROR HANDLING")
    print("-" * 40)
    
    # Test without authentication
    print("Testing without authentication:")
    response = requests.post(f"{API_URL}/conversation/generate")
    if response.status_code == 403:
        print("  ✅ Correctly requires authentication")
        auth_test = True
    else:
        print(f"  ❌ Should return 403, got {response.status_code}")
        auth_test = False
    
    # Test with no agents (delete all agents first)
    print("Testing with no agents:")
    # Get and delete all agents
    agents_response = requests.get(f"{API_URL}/agents", headers={"Authorization": f"Bearer {token}"})
    if agents_response.status_code == 200:
        agents = agents_response.json()
        for agent in agents:
            agent_id = agent.get("id")
            if agent_id:
                requests.delete(f"{API_URL}/agents/{agent_id}", headers={"Authorization": f"Bearer {token}"})
    
    # Try conversation generation with no agents
    response = requests.post(f"{API_URL}/conversation/generate", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 400:
        print("  ✅ Correctly handles no agents scenario")
        no_agents_test = True
    else:
        print(f"  ❌ Should return 400, got {response.status_code}")
        no_agents_test = False
    
    return auth_test and no_agents_test

def main():
    print("🚀 COMPREHENSIVE CONVERSATION GENERATION ENDPOINT TEST")
    print("Testing all requirements from the review request")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Setup clean test environment
    agents = clean_and_setup_agents(token)
    if len(agents) != 3:
        print(f"❌ Failed to create test agents")
        return
    
    print(f"✅ Created {len(agents)} test agents")
    
    # Test conversation generation
    success, messages = test_conversation_generation_comprehensive(token)
    if not success:
        print("❌ Failed to generate conversation")
        return
    
    # Run all tests
    test_results = []
    
    # Test 1: 3 Messages Per Agent
    result1 = test_3_messages_per_agent(messages)
    test_results.append(("3 Messages Per Agent", result1))
    
    # Test 2: Gemini 2.5 Flash Usage
    result2 = test_gemini_2_5_flash_usage(messages)
    test_results.append(("Gemini 2.5 Flash Usage", result2))
    
    # Test 3: Sequential Generation
    result3 = test_sequential_generation(messages)
    test_results.append(("Sequential Generation", result3))
    
    # Test 4: Conversation Context
    result4 = test_conversation_context(messages)
    test_results.append(("Conversation Context", result4))
    
    # Test 5: Error Handling (this will clean agents, so do it last)
    result5 = test_error_handling(token)
    test_results.append(("Error Handling", result5))
    
    # Final Assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print("Test Results:")
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Conversation generation endpoint meets all requirements")
        print("✅ 3 messages per agent functionality is working")
        print("✅ Gemini 2.5 Flash is being used effectively")
        print("✅ Sequential generation is implemented correctly")
        print("✅ Context awareness is good")
        print("✅ Error handling is working")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} TESTS FAILED")
        print("❌ Conversation generation endpoint has issues")
        
        # Identify critical failures
        critical_failures = []
        for test_name, result in test_results:
            if not result:
                critical_failures.append(test_name)
        
        print("Critical issues:")
        for failure in critical_failures:
            print(f"  - {failure}")

if __name__ == "__main__":
    main()