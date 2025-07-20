#!/usr/bin/env python3
"""
Comprehensive test for narration removal functionality in AI agent conversations.

This test verifies that:
1. Generated conversations do NOT contain asterisks or narrations
2. Character descriptions and stage directions are properly filtered out
3. Normal content is preserved while narrations are removed
4. Agent personalities still come through without narrations
5. Both normal conversation generation and fallback scenarios work correctly
"""

import requests
import json
import time
import os
import sys
import re
import uuid
from dotenv import load_dotenv

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

# Global variables
auth_token = None
test_user_id = None
test_agents = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
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
    """Authenticate and get auth token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATING FOR NARRATION REMOVAL TESTS")
    print("="*80)
    
    # Try guest authentication first
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest authentication successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest authentication failed")
        return False

def create_test_agents():
    """Create diverse test agents for narration testing"""
    global test_agents
    
    print("\n" + "="*80)
    print("CREATING TEST AGENTS FOR NARRATION REMOVAL TESTING")
    print("="*80)
    
    # Define diverse agents with different archetypes and personalities
    agent_configs = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            },
            "goal": "Advance quantum computing research through rigorous scientific methodology",
            "expertise": "Quantum Physics and Computing",
            "background": "Leading quantum physicist with 15 years of research experience"
        },
        {
            "name": "Marcus Rodriguez",
            "archetype": "leader",
            "personality": {
                "extroversion": 9,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            },
            "goal": "Lead the team to successful project completion",
            "expertise": "Project Management and Leadership",
            "background": "Experienced project manager with a track record of delivering complex technical projects"
        },
        {
            "name": "Elena Vasquez",
            "archetype": "skeptic",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 8,
                "cooperativeness": 5,
                "energy": 6
            },
            "goal": "Identify potential risks and ensure thorough analysis",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "Critical thinker specializing in identifying potential problems and risks"
        },
        {
            "name": "Alex Thompson",
            "archetype": "optimist",
            "personality": {
                "extroversion": 8,
                "optimism": 10,
                "curiosity": 7,
                "cooperativeness": 9,
                "energy": 9
            },
            "goal": "Foster positive team dynamics and find creative solutions",
            "expertise": "Creative Problem Solving",
            "background": "Enthusiastic innovator known for finding positive solutions to complex challenges"
        }
    ]
    
    created_agents = []
    
    for agent_config in agent_configs:
        create_test, create_response = run_test(
            f"Create Agent: {agent_config['name']}",
            "/agents",
            method="POST",
            data=agent_config,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            agent_name = create_response.get("name")
            print(f"✅ Created agent: {agent_name} (ID: {agent_id})")
            created_agents.append(create_response)
        else:
            print(f"❌ Failed to create agent: {agent_config['name']}")
    
    test_agents = created_agents
    print(f"\n✅ Successfully created {len(test_agents)} test agents")
    return len(test_agents) >= 2  # Need at least 2 agents for conversation

def setup_simulation():
    """Set up simulation for testing"""
    print("\n" + "="*80)
    print("SETTING UP SIMULATION FOR NARRATION TESTING")
    print("="*80)
    
    # Start simulation
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False
    
    # Set scenario
    scenario_data = {
        "scenario": "The team is working on a breakthrough quantum computing project that could revolutionize cryptography. They need to discuss technical approaches, potential challenges, and implementation strategies.",
        "scenario_name": "Quantum Computing Breakthrough"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if scenario_test:
        print("✅ Simulation setup complete")
        return True
    else:
        print("❌ Failed to set scenario")
        return False

def check_for_narrations(text):
    """Check if text contains narrations (asterisks) and return details"""
    if not text:
        return False, []
    
    # Find all text within asterisks
    narration_pattern = r'\*([^*]*)\*'
    narrations = re.findall(narration_pattern, text)
    
    # Also check for common narration patterns
    common_narrations = [
        r'\*[^*]*\*',  # Any text in asterisks
        r'\*leans forward\*',
        r'\*adjusts glasses\*',
        r'\*mechanical breathing\*',
        r'\*nods\*',
        r'\*smiles\*',
        r'\*pauses\*',
        r'\*looks around\*',
        r'\*gestures\*'
    ]
    
    found_patterns = []
    for pattern in common_narrations:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found_patterns.extend(matches)
    
    has_narrations = len(narrations) > 0 or len(found_patterns) > 0
    all_narrations = narrations + found_patterns
    
    return has_narrations, all_narrations

def analyze_conversation_quality(conversation_data):
    """Analyze the quality and naturalness of conversation"""
    if not conversation_data or "messages" not in conversation_data:
        return {
            "total_messages": 0,
            "avg_length": 0,
            "personality_indicators": 0,
            "natural_language": False
        }
    
    messages = conversation_data["messages"]
    total_messages = len(messages)
    
    if total_messages == 0:
        return {
            "total_messages": 0,
            "avg_length": 0,
            "personality_indicators": 0,
            "natural_language": False
        }
    
    # Calculate average message length
    message_lengths = [len(msg.get("message", "")) for msg in messages]
    avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
    
    # Count personality indicators (questions, exclamations, etc.)
    personality_indicators = 0
    natural_language_indicators = 0
    
    for msg in messages:
        message_text = msg.get("message", "")
        
        # Count personality indicators
        if "?" in message_text:
            personality_indicators += 1
        if "!" in message_text:
            personality_indicators += 1
        if any(word in message_text.lower() for word in ["i think", "i believe", "in my opinion", "i suggest"]):
            personality_indicators += 1
        
        # Count natural language indicators
        if any(word in message_text.lower() for word in ["actually", "however", "but", "although", "because"]):
            natural_language_indicators += 1
        if len(message_text.split()) > 10:  # Substantial messages
            natural_language_indicators += 1
    
    return {
        "total_messages": total_messages,
        "avg_length": avg_length,
        "personality_indicators": personality_indicators,
        "natural_language": natural_language_indicators > 0,
        "natural_language_score": natural_language_indicators
    }

def test_conversation_generation_narration_removal():
    """Test conversation generation for narration removal"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION GENERATION - NARRATION REMOVAL")
    print("="*80)
    
    narration_issues = []
    conversation_quality_scores = []
    
    # Generate multiple conversations to test consistency
    for i in range(3):
        print(f"\n--- Testing Conversation Generation #{i+1} ---")
        
        generate_test, generate_response = run_test(
            f"Generate Conversation #{i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            expected_keys=["id", "messages"]
        )
        
        if not generate_test or not generate_response:
            print(f"❌ Failed to generate conversation #{i+1}")
            continue
        
        # Analyze the conversation for narrations
        messages = generate_response.get("messages", [])
        print(f"Generated {len(messages)} messages")
        
        conversation_narrations = []
        
        for j, message in enumerate(messages):
            agent_name = message.get("agent_name", "Unknown")
            message_text = message.get("message", "")
            
            print(f"\nMessage {j+1} from {agent_name}:")
            print(f"Content: {message_text[:200]}{'...' if len(message_text) > 200 else ''}")
            
            # Check for narrations
            has_narrations, found_narrations = check_for_narrations(message_text)
            
            if has_narrations:
                print(f"❌ NARRATION FOUND in message from {agent_name}:")
                for narration in found_narrations:
                    print(f"   - '{narration}'")
                conversation_narrations.append({
                    "agent": agent_name,
                    "message_index": j,
                    "narrations": found_narrations
                })
            else:
                print(f"✅ No narrations found in message from {agent_name}")
        
        # Analyze conversation quality
        quality = analyze_conversation_quality(generate_response)
        conversation_quality_scores.append(quality)
        
        print(f"\nConversation Quality Analysis:")
        print(f"  - Total messages: {quality['total_messages']}")
        print(f"  - Average message length: {quality['avg_length']:.1f} characters")
        print(f"  - Personality indicators: {quality['personality_indicators']}")
        print(f"  - Natural language score: {quality['natural_language_score']}")
        
        if conversation_narrations:
            narration_issues.append({
                "conversation": i+1,
                "narrations": conversation_narrations
            })
    
    # Summary of narration removal testing
    print(f"\n{'='*80}")
    print("NARRATION REMOVAL TEST SUMMARY")
    print(f"{'='*80}")
    
    total_conversations = 3
    conversations_with_narrations = len(narration_issues)
    conversations_clean = total_conversations - conversations_with_narrations
    
    print(f"Total conversations tested: {total_conversations}")
    print(f"Conversations without narrations: {conversations_clean}")
    print(f"Conversations with narrations: {conversations_with_narrations}")
    
    if conversations_with_narrations == 0:
        print("✅ ALL CONVERSATIONS ARE FREE OF NARRATIONS!")
        print("✅ Narration removal functionality is working perfectly")
        narration_success = True
    else:
        print("❌ SOME CONVERSATIONS STILL CONTAIN NARRATIONS")
        print("❌ Narration removal functionality needs improvement")
        
        for issue in narration_issues:
            conv_num = issue["conversation"]
            print(f"\nConversation #{conv_num} narration issues:")
            for narration_data in issue["narrations"]:
                agent = narration_data["agent"]
                narrations = narration_data["narrations"]
                print(f"  - {agent}: {', '.join(narrations)}")
        
        narration_success = False
    
    # Analyze conversation quality
    if conversation_quality_scores:
        avg_messages = sum(q["total_messages"] for q in conversation_quality_scores) / len(conversation_quality_scores)
        avg_length = sum(q["avg_length"] for q in conversation_quality_scores) / len(conversation_quality_scores)
        avg_personality = sum(q["personality_indicators"] for q in conversation_quality_scores) / len(conversation_quality_scores)
        natural_conversations = sum(1 for q in conversation_quality_scores if q["natural_language"])
        
        print(f"\nCONVERSATION QUALITY SUMMARY:")
        print(f"  - Average messages per conversation: {avg_messages:.1f}")
        print(f"  - Average message length: {avg_length:.1f} characters")
        print(f"  - Average personality indicators: {avg_personality:.1f}")
        print(f"  - Natural language conversations: {natural_conversations}/{len(conversation_quality_scores)}")
        
        quality_good = (
            avg_messages >= 3 and  # At least 3 messages per conversation
            avg_length >= 50 and   # At least 50 characters per message
            avg_personality >= 2 and  # Some personality indicators
            natural_conversations >= 2  # Most conversations sound natural
        )
        
        if quality_good:
            print("✅ Conversation quality is good - personalities come through without narrations")
        else:
            print("⚠️ Conversation quality could be improved")
    
    return narration_success, {
        "conversations_tested": total_conversations,
        "conversations_clean": conversations_clean,
        "conversations_with_narrations": conversations_with_narrations,
        "narration_issues": narration_issues,
        "quality_scores": conversation_quality_scores
    }

def test_observer_message_narration_removal():
    """Test observer message functionality for narration removal"""
    print("\n" + "="*80)
    print("TESTING OBSERVER MESSAGE - NARRATION REMOVAL")
    print("="*80)
    
    # Send observer message
    observer_data = {
        "observer_message": "Hello team! I need you to focus on the most critical technical challenges we're facing. Please share your expert perspectives on the quantum decoherence problem."
    }
    
    observer_test, observer_response = run_test(
        "Send Observer Message",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=True,
        expected_keys=["message", "observer_message", "agent_responses"]
    )
    
    if not observer_test or not observer_response:
        print("❌ Failed to send observer message")
        return False, "Observer message failed"
    
    # Analyze agent responses for narrations
    agent_responses = observer_response.get("agent_responses", {})
    messages = agent_responses.get("messages", [])
    
    print(f"Received {len(messages)} responses to observer message")
    
    observer_narrations = []
    
    for i, message in enumerate(messages):
        agent_name = message.get("agent_name", "Unknown")
        message_text = message.get("message", "")
        
        # Skip the observer message itself
        if agent_name == "Observer (You)":
            continue
        
        print(f"\nResponse from {agent_name}:")
        print(f"Content: {message_text}")
        
        # Check for narrations
        has_narrations, found_narrations = check_for_narrations(message_text)
        
        if has_narrations:
            print(f"❌ NARRATION FOUND in response from {agent_name}:")
            for narration in found_narrations:
                print(f"   - '{narration}'")
            observer_narrations.append({
                "agent": agent_name,
                "narrations": found_narrations
            })
        else:
            print(f"✅ No narrations found in response from {agent_name}")
    
    # Summary
    print(f"\n{'='*40}")
    print("OBSERVER MESSAGE NARRATION SUMMARY")
    print(f"{'='*40}")
    
    if len(observer_narrations) == 0:
        print("✅ ALL OBSERVER RESPONSES ARE FREE OF NARRATIONS!")
        print("✅ Observer message narration removal is working")
        return True, "Observer message narration removal working"
    else:
        print("❌ SOME OBSERVER RESPONSES CONTAIN NARRATIONS")
        for issue in observer_narrations:
            agent = issue["agent"]
            narrations = issue["narrations"]
            print(f"  - {agent}: {', '.join(narrations)}")
        return False, f"{len(observer_narrations)} agents had narrations in observer responses"

def test_fallback_response_narration_removal():
    """Test fallback responses for narration removal"""
    print("\n" + "="*80)
    print("TESTING FALLBACK RESPONSE - NARRATION REMOVAL")
    print("="*80)
    
    # This test is harder to trigger directly, but we can test by generating
    # multiple conversations and checking if any fallback responses contain narrations
    
    print("Generating multiple conversations to potentially trigger fallback responses...")
    
    fallback_narrations = []
    
    # Generate several conversations quickly to potentially trigger fallbacks
    for i in range(5):
        print(f"\nTesting conversation #{i+1} for potential fallbacks...")
        
        generate_test, generate_response = run_test(
            f"Generate Conversation for Fallback Test #{i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            expected_keys=["id", "messages"]
        )
        
        if generate_test and generate_response:
            messages = generate_response.get("messages", [])
            
            for message in messages:
                agent_name = message.get("agent_name", "Unknown")
                message_text = message.get("message", "")
                
                # Check if this might be a fallback response (shorter, more generic)
                is_potential_fallback = (
                    len(message_text) < 100 or  # Short responses
                    any(phrase in message_text.lower() for phrase in [
                        "got it", "sounds good", "i agree", "that works",
                        "good point", "makes sense", "i think", "let's"
                    ])
                )
                
                if is_potential_fallback:
                    print(f"Potential fallback response from {agent_name}: {message_text[:100]}...")
                    
                    # Check for narrations in potential fallback
                    has_narrations, found_narrations = check_for_narrations(message_text)
                    
                    if has_narrations:
                        print(f"❌ NARRATION FOUND in potential fallback from {agent_name}:")
                        for narration in found_narrations:
                            print(f"   - '{narration}'")
                        fallback_narrations.append({
                            "agent": agent_name,
                            "message": message_text,
                            "narrations": found_narrations
                        })
                    else:
                        print(f"✅ No narrations in potential fallback from {agent_name}")
    
    # Summary
    print(f"\n{'='*40}")
    print("FALLBACK RESPONSE NARRATION SUMMARY")
    print(f"{'='*40}")
    
    if len(fallback_narrations) == 0:
        print("✅ NO NARRATIONS FOUND IN POTENTIAL FALLBACK RESPONSES!")
        print("✅ Fallback response narration removal appears to be working")
        return True, "Fallback narration removal working"
    else:
        print("❌ SOME POTENTIAL FALLBACK RESPONSES CONTAIN NARRATIONS")
        for issue in fallback_narrations:
            agent = issue["agent"]
            narrations = issue["narrations"]
            print(f"  - {agent}: {', '.join(narrations)}")
        return False, f"{len(fallback_narrations)} potential fallback responses had narrations"

def print_final_summary():
    """Print final test summary"""
    print("\n" + "="*80)
    print("NARRATION REMOVAL FUNCTIONALITY - FINAL TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {test_results['passed']}")
    print(f"Tests failed: {test_results['failed']}")
    print(f"Pass rate: {pass_rate:.1f}%")
    
    print(f"\nTest Results:")
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']}")
    
    print(f"\n{'='*80}")
    if test_results["failed"] == 0:
        print("🎉 ALL TESTS PASSED! Narration removal functionality is working correctly!")
    else:
        print("⚠️ Some tests failed. Narration removal functionality needs attention.")
    print("="*80)

def main():
    """Main test execution"""
    print("🧪 STARTING COMPREHENSIVE NARRATION REMOVAL TESTING")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return False
    
    # Step 2: Create test agents
    if not create_test_agents():
        print("❌ Failed to create sufficient test agents. Cannot proceed with tests.")
        return False
    
    # Step 3: Setup simulation
    if not setup_simulation():
        print("❌ Failed to setup simulation. Cannot proceed with tests.")
        return False
    
    # Step 4: Test conversation generation narration removal
    conv_success, conv_results = test_conversation_generation_narration_removal()
    
    # Step 5: Test observer message narration removal
    obs_success, obs_results = test_observer_message_narration_removal()
    
    # Step 6: Test fallback response narration removal
    fallback_success, fallback_results = test_fallback_response_narration_removal()
    
    # Step 7: Print final summary
    print_final_summary()
    
    # Overall assessment
    overall_success = conv_success and obs_success and fallback_success
    
    print(f"\n🎯 OVERALL NARRATION REMOVAL ASSESSMENT:")
    print(f"  - Conversation Generation: {'✅ PASS' if conv_success else '❌ FAIL'}")
    print(f"  - Observer Messages: {'✅ PASS' if obs_success else '❌ FAIL'}")
    print(f"  - Fallback Responses: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    print(f"  - Overall Result: {'✅ SUCCESS' if overall_success else '❌ NEEDS IMPROVEMENT'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)