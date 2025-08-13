#!/usr/bin/env python3
"""
Test script for conversation generation improvements:
1. Consecutive Messages Prevention (Round-robin rotation)
2. Unanswered Question Detection and Response
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime
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
    "tests": []
}

# Global variables
auth_token = None
test_user_id = None
test_agents = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
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
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.4f} seconds")
        
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
            "result": result,
            "response_time": response_time
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

def setup_test_environment():
    """Set up test environment with authentication and agents"""
    global auth_token, test_user_id, test_agents
    
    print("\n" + "="*80)
    print("SETTING UP TEST ENVIRONMENT")
    print("="*80)
    
    # Step 1: Authenticate
    print("\nStep 1: Authenticating with guest login")
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if not guest_test or not guest_response:
        print("❌ Failed to authenticate")
        return False
    
    auth_token = guest_response.get("access_token")
    user_data = guest_response.get("user", {})
    test_user_id = user_data.get("id")
    print(f"✅ Authenticated as user: {test_user_id}")
    
    # Step 2: Clean up existing agents
    print("\nStep 2: Cleaning up existing agents")
    get_agents_test, get_agents_response = run_test(
        "Get Existing Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if get_agents_test and get_agents_response:
        existing_agents = get_agents_response
        print(f"Found {len(existing_agents)} existing agents")
        
        # Delete existing agents
        for agent in existing_agents:
            agent_id = agent.get("id")
            if agent_id:
                delete_test, delete_response = run_test(
                    f"Delete Agent {agent.get('name', 'Unknown')}",
                    f"/agents/{agent_id}",
                    method="DELETE",
                    auth=True
                )
                if delete_test:
                    print(f"✅ Deleted agent: {agent.get('name', 'Unknown')}")
    
    # Step 3: Create 3 test agents for round-robin testing
    print("\nStep 3: Creating 3 test agents for round-robin testing")
    
    agent_configs = [
        {
            "name": "Agent Alpha",
            "archetype": "scientist",
            "goal": "Analyze problems systematically and propose evidence-based solutions",
            "expertise": "Data analysis and research methodology",
            "background": "PhD in Computer Science with focus on AI systems",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            }
        },
        {
            "name": "Agent Beta",
            "archetype": "leader",
            "goal": "Coordinate team efforts and drive decision-making",
            "expertise": "Project management and strategic planning",
            "background": "MBA with 10 years experience in tech leadership",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 9,
                "energy": 8
            }
        },
        {
            "name": "Agent Gamma",
            "archetype": "skeptic",
            "goal": "Identify risks and challenge assumptions",
            "expertise": "Risk assessment and quality assurance",
            "background": "Senior engineer with expertise in system reliability",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 6,
                "energy": 5
            }
        }
    ]
    
    test_agents = []
    for i, config in enumerate(agent_configs):
        create_test, create_response = run_test(
            f"Create Test Agent {i+1}",
            "/agents",
            method="POST",
            data=config,
            auth=True,
            expected_keys=["id", "name"]
        )
        
        if create_test and create_response:
            test_agents.append(create_response)
            print(f"✅ Created agent: {create_response.get('name')}")
        else:
            print(f"❌ Failed to create agent {i+1}")
            return False
    
    # Step 4: Set up simulation scenario
    print("\nStep 4: Setting up simulation scenario")
    
    scenario_data = {
        "scenario": "Quantum Computing Research Project",
        "scenario_name": "Quantum Signal Discovery"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Simulation Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message"]
    )
    
    if not scenario_test:
        print("❌ Failed to set simulation scenario")
        return False
    
    print("✅ Simulation scenario set successfully")
    
    # Step 5: Start simulation
    print("\nStep 5: Starting simulation")
    
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
    
    print("✅ Simulation started successfully")
    print(f"✅ Test environment setup complete with {len(test_agents)} agents")
    return True

def test_consecutive_messages_prevention():
    """Test that agents never post twice in a row (round-robin rotation)"""
    print("\n" + "="*80)
    print("TESTING CONSECUTIVE MESSAGES PREVENTION")
    print("="*80)
    
    if len(test_agents) < 3:
        print("❌ Need at least 3 agents for round-robin testing")
        return False
    
    # Generate multiple conversation messages to test round-robin
    print(f"\nGenerating 15 conversation messages to test strict round-robin rotation")
    print(f"Expected pattern: {test_agents[0]['name']} → {test_agents[1]['name']} → {test_agents[2]['name']} → repeat")
    
    conversation_messages = []
    agent_sequence = []
    consecutive_violations = []
    
    for i in range(15):
        print(f"\n--- Message {i+1}/15 ---")
        
        message_test, message_response = run_test(
            f"Generate Contextual Message {i+1}",
            "/conversation/add-contextual-message",
            method="POST",
            auth=True
        )
        
        if message_test and message_response:
            messages = message_response.get("messages", [])
            if messages:
                latest_message = messages[-1]
                agent_name = latest_message.get("agent_name")
                message_text = latest_message.get("message", "")
                
                print(f"✅ Message from: {agent_name}")
                print(f"📝 Content: {message_text[:100]}...")
                
                conversation_messages.append(latest_message)
                agent_sequence.append(agent_name)
                
                # Check for consecutive messages from same agent
                if len(agent_sequence) > 1 and agent_sequence[-1] == agent_sequence[-2]:
                    consecutive_violations.append({
                        "position": i+1,
                        "agent": agent_name,
                        "previous_agent": agent_sequence[-2]
                    })
                    print(f"❌ CONSECUTIVE VIOLATION: {agent_name} spoke twice in a row!")
            else:
                print(f"❌ No messages in response for iteration {i+1}")
        else:
            print(f"❌ Failed to generate message {i+1}")
    
    # Analyze round-robin fairness
    print(f"\n{'='*60}")
    print("ROUND-ROBIN ANALYSIS")
    print(f"{'='*60}")
    
    agent_counts = Counter(agent_sequence)
    total_messages = len(agent_sequence)
    expected_per_agent = total_messages / len(test_agents)
    
    print(f"Total messages generated: {total_messages}")
    print(f"Expected messages per agent: {expected_per_agent:.1f}")
    print(f"\nActual distribution:")
    
    fairness_violations = []
    for agent_name, count in agent_counts.items():
        percentage = (count / total_messages) * 100
        deviation = abs(count - expected_per_agent)
        print(f"  {agent_name}: {count} messages ({percentage:.1f}%)")
        
        # Check if deviation is too high (more than 2 messages difference)
        if deviation > 2:
            fairness_violations.append({
                "agent": agent_name,
                "count": count,
                "expected": expected_per_agent,
                "deviation": deviation
            })
    
    print(f"\nSpeaking sequence: {' → '.join(agent_sequence)}")
    
    # Check for perfect round-robin pattern
    expected_pattern = []
    agent_names = [agent['name'] for agent in test_agents]
    sorted_agent_names = sorted(agent_names)  # Should match backend sorting
    
    for i in range(total_messages):
        expected_agent = sorted_agent_names[i % len(sorted_agent_names)]
        expected_pattern.append(expected_agent)
    
    pattern_matches = sum(1 for actual, expected in zip(agent_sequence, expected_pattern) if actual == expected)
    pattern_accuracy = (pattern_matches / total_messages) * 100
    
    print(f"\nExpected pattern: {' → '.join(expected_pattern)}")
    print(f"Pattern accuracy: {pattern_matches}/{total_messages} ({pattern_accuracy:.1f}%)")
    
    # Evaluate results
    print(f"\n{'='*60}")
    print("CONSECUTIVE MESSAGES PREVENTION RESULTS")
    print(f"{'='*60}")
    
    if consecutive_violations:
        print(f"❌ FAILED: Found {len(consecutive_violations)} consecutive message violations:")
        for violation in consecutive_violations:
            print(f"  - Position {violation['position']}: {violation['agent']} spoke after themselves")
        return False
    else:
        print("✅ PASSED: No consecutive messages detected - agents never speak twice in a row")
    
    if fairness_violations:
        print(f"⚠️ WARNING: Found {len(fairness_violations)} fairness violations:")
        for violation in fairness_violations:
            print(f"  - {violation['agent']}: {violation['count']} messages (deviation: {violation['deviation']:.1f})")
    else:
        print("✅ PASSED: Fair distribution - all agents participate equally")
    
    if pattern_accuracy >= 90:
        print(f"✅ PASSED: Excellent round-robin pattern accuracy ({pattern_accuracy:.1f}%)")
    elif pattern_accuracy >= 70:
        print(f"⚠️ WARNING: Good round-robin pattern accuracy ({pattern_accuracy:.1f}%)")
    else:
        print(f"❌ FAILED: Poor round-robin pattern accuracy ({pattern_accuracy:.1f}%)")
        return False
    
    return len(consecutive_violations) == 0 and pattern_accuracy >= 70

def test_unanswered_question_detection():
    """Test that the system detects general questions and encourages agents to answer them"""
    print("\n" + "="*80)
    print("TESTING UNANSWERED QUESTION DETECTION AND RESPONSE")
    print("="*80)
    
    # Reset conversation by creating a new scenario
    print("\nStep 1: Setting up fresh scenario for question testing")
    
    question_scenario_data = {
        "scenario": "AI Ethics Discussion - What are the key ethical considerations for AI deployment?",
        "scenario_name": "AI Ethics Workshop"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Question Testing Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=question_scenario_data,
        auth=True,
        expected_keys=["message"]
    )
    
    if not scenario_test:
        print("❌ Failed to set question testing scenario")
        return False
    
    # Generate initial conversation with questions
    print("\nStep 2: Generating conversation messages with general questions")
    
    question_responses = []
    detected_questions = []
    question_responses_found = []
    
    # Generate several messages to create questions and responses
    for i in range(10):
        print(f"\n--- Question Test Message {i+1}/10 ---")
        
        message_test, message_response = run_test(
            f"Generate Message with Question Context {i+1}",
            "/conversation/add-contextual-message",
            method="POST",
            auth=True
        )
        
        if message_test and message_response:
            messages = message_response.get("messages", [])
            if messages:
                latest_message = messages[-1]
                agent_name = latest_message.get("agent_name")
                message_text = latest_message.get("message", "")
                
                print(f"✅ Message from: {agent_name}")
                print(f"📝 Content: {message_text}")
                
                # Check if message contains a question
                if "?" in message_text:
                    detected_questions.append({
                        "position": i+1,
                        "agent": agent_name,
                        "question": message_text,
                        "is_general": not any(other_agent['name'].lower() in message_text.lower() 
                                            for other_agent in test_agents if other_agent['name'] != agent_name)
                    })
                    print(f"❓ QUESTION DETECTED: {'General' if detected_questions[-1]['is_general'] else 'Directed'}")
                
                # Check if message appears to be responding to a question
                response_indicators = [
                    "i think", "my opinion", "i believe", "in my view", "from my perspective",
                    "yes", "no", "absolutely", "definitely", "i agree", "i disagree",
                    "the answer", "to answer", "responding to", "regarding the question"
                ]
                
                if any(indicator in message_text.lower() for indicator in response_indicators):
                    question_responses_found.append({
                        "position": i+1,
                        "agent": agent_name,
                        "response": message_text,
                        "response_type": "answer_attempt"
                    })
                    print(f"💬 RESPONSE DETECTED: Agent appears to be answering a question")
                
                question_responses.append(latest_message)
            else:
                print(f"❌ No messages in response for question test {i+1}")
        else:
            print(f"❌ Failed to generate question test message {i+1}")
    
    # Analyze question detection and response patterns
    print(f"\n{'='*60}")
    print("QUESTION DETECTION ANALYSIS")
    print(f"{'='*60}")
    
    total_questions = len(detected_questions)
    general_questions = len([q for q in detected_questions if q['is_general']])
    directed_questions = total_questions - general_questions
    total_responses = len(question_responses_found)
    
    print(f"Total questions detected: {total_questions}")
    print(f"  - General questions: {general_questions}")
    print(f"  - Directed questions: {directed_questions}")
    print(f"Total response attempts: {total_responses}")
    
    if detected_questions:
        print(f"\nDetected questions:")
        for i, q in enumerate(detected_questions, 1):
            question_type = "GENERAL" if q['is_general'] else "DIRECTED"
            print(f"  {i}. [{question_type}] {q['agent']}: {q['question'][:100]}...")
    
    if question_responses_found:
        print(f"\nDetected responses:")
        for i, r in enumerate(question_responses_found, 1):
            print(f"  {i}. {r['agent']}: {r['response'][:100]}...")
    
    # Check conversation context for "UNANSWERED QUESTIONS DETECTED"
    print(f"\n{'='*60}")
    print("CHECKING FOR UNANSWERED QUESTIONS CONTEXT")
    print(f"{'='*60}")
    
    # Generate one more message to see if the system detects unanswered questions
    final_test, final_response = run_test(
        "Final Message to Check Question Context",
        "/conversation/add-contextual-message",
        method="POST",
        auth=True
    )
    
    context_includes_questions = False
    if final_test and final_response:
        # Check if the response or any debug info mentions unanswered questions
        response_str = json.dumps(final_response).lower()
        if "unanswered" in response_str or "question" in response_str:
            context_includes_questions = True
            print("✅ FOUND: System appears to be tracking question context")
        else:
            print("⚠️ No explicit question context found in response")
    
    # Evaluate results
    print(f"\n{'='*60}")
    print("UNANSWERED QUESTION DETECTION RESULTS")
    print(f"{'='*60}")
    
    success_criteria = []
    
    # Criterion 1: Questions are being generated
    if total_questions >= 2:
        print("✅ PASSED: Questions are being generated in conversation")
        success_criteria.append(True)
    else:
        print("❌ FAILED: Insufficient questions generated in conversation")
        success_criteria.append(False)
    
    # Criterion 2: General questions are detected
    if general_questions >= 1:
        print("✅ PASSED: General questions (not directed at specific agents) are being generated")
        success_criteria.append(True)
    else:
        print("⚠️ WARNING: No general questions detected")
        success_criteria.append(False)
    
    # Criterion 3: Response attempts are being made
    if total_responses >= 1:
        print("✅ PASSED: Agents are attempting to respond to questions")
        success_criteria.append(True)
    else:
        print("❌ FAILED: No response attempts detected")
        success_criteria.append(False)
    
    # Criterion 4: Question-response ratio is reasonable
    if total_questions > 0:
        response_ratio = total_responses / total_questions
        if response_ratio >= 0.5:
            print(f"✅ PASSED: Good question-response ratio ({response_ratio:.2f})")
            success_criteria.append(True)
        else:
            print(f"⚠️ WARNING: Low question-response ratio ({response_ratio:.2f})")
            success_criteria.append(False)
    else:
        success_criteria.append(False)
    
    # Overall assessment
    passed_criteria = sum(success_criteria)
    total_criteria = len(success_criteria)
    
    if passed_criteria >= 3:
        print(f"\n✅ OVERALL PASSED: {passed_criteria}/{total_criteria} criteria met")
        print("✅ Unanswered question detection and response system is working")
        return True
    else:
        print(f"\n❌ OVERALL FAILED: Only {passed_criteria}/{total_criteria} criteria met")
        print("❌ Unanswered question detection and response system needs improvement")
        return False

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"CONVERSATION IMPROVEMENTS TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        response_time = f" ({test.get('response_time', 0):.3f}s)" if 'response_time' in test else ""
        print(f"{i}. {result_symbol} {test['name']}{response_time}")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution"""
    print("🚀 STARTING CONVERSATION GENERATION IMPROVEMENTS TESTING")
    print("="*80)
    print("Testing two specific improvements:")
    print("1. Consecutive Messages Prevention (Round-robin rotation)")
    print("2. Unanswered Question Detection and Response")
    print("="*80)
    
    # Setup test environment
    if not setup_test_environment():
        print("❌ Failed to set up test environment")
        return False
    
    # Test 1: Consecutive Messages Prevention
    consecutive_test_passed = test_consecutive_messages_prevention()
    
    # Test 2: Unanswered Question Detection
    question_test_passed = test_unanswered_question_detection()
    
    # Print final summary
    print_summary()
    
    # Final assessment
    print(f"\n{'='*80}")
    print("FINAL ASSESSMENT")
    print(f"{'='*80}")
    
    if consecutive_test_passed and question_test_passed:
        print("🎉 SUCCESS: Both conversation improvements are working correctly!")
        print("✅ Round-robin rotation prevents consecutive messages")
        print("✅ Question detection and response system is functional")
        return True
    else:
        print("❌ ISSUES DETECTED:")
        if not consecutive_test_passed:
            print("  - Round-robin rotation has issues")
        if not question_test_passed:
            print("  - Question detection and response system has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)