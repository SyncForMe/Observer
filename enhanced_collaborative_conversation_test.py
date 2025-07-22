#!/usr/bin/env python3
"""
Enhanced Collaborative Conversation System Test

This test verifies the enhanced collaborative conversation system that was just implemented.
It focuses on testing:
1. Agents referencing other agents' points that were made
2. Agents sharing their own opinions on those points  
3. Agents asking questions about points other agents made
4. Agents responding to those questions
5. Agents building conversations on top of what they come up with together
6. Working towards finding solutions or series of solutions regarding the scenario

MAJOR ENHANCEMENTS TESTED:
1. Enhanced generate_agent_response_wrapper with priority-based response system
2. Improved conversation analysis tracking solutions, questions, and discussion points
3. Enhanced system messages with specific collaboration rules
4. Smart conversation stage detection based on content
5. Solution-focused context and prompts
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import re
from collections import defaultdict, Counter

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

# Load JWT secret for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, timeout=120):
    """Run a test against the specified endpoint with extended timeout for conversation generation"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers, params=params, timeout=timeout)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.2f} seconds")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        status_ok = response.status_code == expected_status
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        test_passed = status_ok and keys_ok
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result,
            "response_time": response_time
        })
        
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
    """Create test agents for collaborative conversation testing"""
    print("\n" + "="*80)
    print("CREATING TEST AGENTS FOR COLLABORATIVE CONVERSATION")
    print("="*80)
    
    # Define test agents with different archetypes and expertise
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Find innovative solutions through rigorous analysis",
            "expertise": "Quantum Computing Research",
            "background": "PhD in Quantum Physics, 10 years experience in quantum error correction",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            }
        },
        {
            "name": "Marcus Thompson",
            "archetype": "leader",
            "goal": "Drive team towards practical solutions and implementation",
            "expertise": "Project Management and Strategy",
            "background": "MBA, 15 years leading tech projects, specializes in cross-functional team coordination",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "skeptic",
            "goal": "Identify risks and ensure thorough evaluation of proposals",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "Former auditor, expert in identifying potential problems and failure modes",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 6,
                "energy": 5
            }
        },
        {
            "name": "Alex Kim",
            "archetype": "optimist",
            "goal": "Find opportunities and maintain team morale",
            "expertise": "Innovation and Creative Problem Solving",
            "background": "Design thinking facilitator, specializes in turning challenges into opportunities",
            "personality": {
                "extroversion": 8,
                "optimism": 10,
                "curiosity": 8,
                "cooperativeness": 9,
                "energy": 9
            }
        }
    ]
    
    created_agents = []
    
    for agent_data in test_agents:
        create_test, create_response = run_test(
            f"Create Agent: {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            print(f"✅ Created agent {agent_data['name']} with ID: {agent_id}")
            created_agents.append(create_response)
        else:
            print(f"❌ Failed to create agent {agent_data['name']}")
    
    print(f"\n✅ Successfully created {len(created_agents)} test agents")
    return created_agents

def setup_simulation():
    """Setup simulation for collaborative conversation testing"""
    print("\n" + "="*80)
    print("SETTING UP SIMULATION FOR COLLABORATIVE CONVERSATION")
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
    
    # Set a collaborative scenario
    scenario_data = {
        "scenario": "Your team has been tasked with developing a breakthrough quantum encryption system for secure communications. The project has a tight 6-month deadline and a $2M budget. You need to address technical challenges, resource allocation, timeline management, and risk mitigation. Work together to create a comprehensive implementation plan.",
        "scenario_name": "Quantum Encryption Development Project"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Collaborative Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if scenario_test:
        print("✅ Successfully set up collaborative scenario")
        return True
    else:
        print("❌ Failed to set collaborative scenario")
        return False

def analyze_conversation_collaboration(conversation_data):
    """Analyze conversation for collaborative elements"""
    print("\n" + "="*80)
    print("ANALYZING CONVERSATION FOR COLLABORATIVE ELEMENTS")
    print("="*80)
    
    if not conversation_data or "messages" not in conversation_data:
        print("❌ No conversation data to analyze")
        return {
            "agent_references": 0,
            "questions_asked": 0,
            "questions_answered": 0,
            "solution_building": 0,
            "collaboration_score": 0
        }
    
    messages = conversation_data["messages"]
    agent_names = set()
    agent_references = 0
    questions_asked = 0
    questions_answered = 0
    solution_building = 0
    
    # Extract agent names
    for msg in messages:
        agent_name = msg.get("agent_name", "")
        if agent_name and agent_name != "Observer (You)":
            agent_names.add(agent_name.split()[0])  # Get first name
    
    print(f"Agents in conversation: {list(agent_names)}")
    
    # Analyze each message for collaborative elements
    for i, msg in enumerate(messages):
        message_text = msg.get("message", "").lower()
        agent_name = msg.get("agent_name", "")
        
        if agent_name == "Observer (You)":
            continue
            
        print(f"\nAnalyzing message {i+1} from {agent_name}:")
        print(f"Message: {message_text[:100]}...")
        
        # Check for agent references
        current_agent_first_name = agent_name.split()[0].lower()
        for other_agent in agent_names:
            if other_agent.lower() != current_agent_first_name and other_agent.lower() in message_text:
                agent_references += 1
                print(f"  ✅ References {other_agent}")
                break
        
        # Check for building on others' ideas
        building_phrases = [
            "building on", "i agree with", "as you mentioned", "your point about",
            "that's a good point", "expanding on", "adding to", "following up on",
            "i like your idea", "your suggestion", "what you said about"
        ]
        
        for phrase in building_phrases:
            if phrase in message_text:
                solution_building += 1
                print(f"  ✅ Building on others' ideas: '{phrase}'")
                break
        
        # Check for questions
        if "?" in message_text:
            questions_asked += 1
            print(f"  ✅ Asks a question")
        
        # Check for answering questions (look for direct responses)
        answer_phrases = [
            "to answer", "the answer is", "i think the solution", "my response",
            "to address your question", "regarding your question", "yes,", "no,",
            "i believe", "in my opinion", "from my perspective"
        ]
        
        for phrase in answer_phrases:
            if phrase in message_text:
                questions_answered += 1
                print(f"  ✅ Provides answers/opinions: '{phrase}'")
                break
    
    # Calculate collaboration score
    total_messages = len([m for m in messages if m.get("agent_name") != "Observer (You)"])
    if total_messages > 0:
        collaboration_score = (
            (agent_references / total_messages) * 25 +
            (questions_asked / total_messages) * 25 +
            (questions_answered / total_messages) * 25 +
            (solution_building / total_messages) * 25
        )
    else:
        collaboration_score = 0
    
    results = {
        "total_messages": total_messages,
        "agent_references": agent_references,
        "questions_asked": questions_asked,
        "questions_answered": questions_answered,
        "solution_building": solution_building,
        "collaboration_score": round(collaboration_score, 2)
    }
    
    print(f"\n📊 COLLABORATION ANALYSIS RESULTS:")
    print(f"Total messages analyzed: {results['total_messages']}")
    print(f"Agent references: {results['agent_references']}")
    print(f"Questions asked: {results['questions_asked']}")
    print(f"Questions answered: {results['questions_answered']}")
    print(f"Solution building instances: {results['solution_building']}")
    print(f"Collaboration score: {results['collaboration_score']}/100")
    
    return results

def test_conversation_progression():
    """Test conversation progression through multiple rounds"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION PROGRESSION AND SOLUTION DEVELOPMENT")
    print("="*80)
    
    conversation_rounds = []
    collaboration_scores = []
    
    # Generate multiple conversation rounds
    for round_num in range(1, 4):  # 3 rounds
        print(f"\n--- CONVERSATION ROUND {round_num} ---")
        
        generate_test, generate_response = run_test(
            f"Generate Conversation Round {round_num}",
            "/conversation/generate",
            method="POST",
            auth=True,
            timeout=180,  # Extended timeout for conversation generation
            expected_keys=["id", "messages"]
        )
        
        if generate_test and generate_response:
            print(f"✅ Successfully generated conversation round {round_num}")
            conversation_rounds.append(generate_response)
            
            # Analyze collaboration in this round
            collaboration_analysis = analyze_conversation_collaboration(generate_response)
            collaboration_scores.append(collaboration_analysis["collaboration_score"])
            
            # Brief pause between rounds
            time.sleep(2)
        else:
            print(f"❌ Failed to generate conversation round {round_num}")
            break
    
    # Analyze progression
    if len(collaboration_scores) >= 2:
        print(f"\n📈 COLLABORATION PROGRESSION ANALYSIS:")
        for i, score in enumerate(collaboration_scores, 1):
            print(f"Round {i}: {score}/100")
        
        # Check if collaboration is improving or maintaining high levels
        avg_score = sum(collaboration_scores) / len(collaboration_scores)
        print(f"Average collaboration score: {avg_score:.2f}/100")
        
        if avg_score >= 60:
            print("✅ High level of collaboration maintained across rounds")
            return True, {"rounds": len(conversation_rounds), "avg_collaboration": avg_score}
        elif avg_score >= 40:
            print("⚠️ Moderate collaboration detected")
            return True, {"rounds": len(conversation_rounds), "avg_collaboration": avg_score}
        else:
            print("❌ Low collaboration detected")
            return False, {"rounds": len(conversation_rounds), "avg_collaboration": avg_score}
    else:
        print("❌ Insufficient conversation rounds for progression analysis")
        return False, {"rounds": len(conversation_rounds)}

def test_solution_focus():
    """Test if conversations are solution-focused"""
    print("\n" + "="*80)
    print("TESTING SOLUTION-FOCUSED CONVERSATION DEVELOPMENT")
    print("="*80)
    
    # Get recent conversations
    conversations_test, conversations_response = run_test(
        "Get Recent Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to retrieve conversations for solution analysis")
        return False, "No conversations to analyze"
    
    solution_indicators = 0
    total_messages = 0
    solution_keywords = [
        "solution", "implement", "approach", "strategy", "plan", "proposal",
        "recommend", "suggest", "action", "next steps", "timeline", "budget",
        "allocate", "resource", "milestone", "deliverable", "outcome", "result"
    ]
    
    for conversation in conversations_response[-3:]:  # Analyze last 3 conversations
        messages = conversation.get("messages", [])
        for msg in messages:
            if msg.get("agent_name") != "Observer (You)":
                message_text = msg.get("message", "").lower()
                total_messages += 1
                
                # Check for solution-focused language
                for keyword in solution_keywords:
                    if keyword in message_text:
                        solution_indicators += 1
                        break
    
    if total_messages > 0:
        solution_focus_ratio = solution_indicators / total_messages
        solution_percentage = solution_focus_ratio * 100
        
        print(f"📊 SOLUTION FOCUS ANALYSIS:")
        print(f"Total messages analyzed: {total_messages}")
        print(f"Messages with solution indicators: {solution_indicators}")
        print(f"Solution focus percentage: {solution_percentage:.1f}%")
        
        if solution_percentage >= 70:
            print("✅ Conversations are highly solution-focused")
            return True, {"solution_focus": solution_percentage}
        elif solution_percentage >= 50:
            print("⚠️ Conversations are moderately solution-focused")
            return True, {"solution_focus": solution_percentage}
        else:
            print("❌ Conversations lack solution focus")
            return False, {"solution_focus": solution_percentage}
    else:
        print("❌ No messages to analyze for solution focus")
        return False, {"solution_focus": 0}

def test_priority_response_system():
    """Test the priority-based response system"""
    print("\n" + "="*80)
    print("TESTING PRIORITY-BASED RESPONSE SYSTEM")
    print("="*80)
    
    # Send observer message with direct question
    observer_data = {
        "observer_message": "Dr. Sarah Chen, what's your assessment of the quantum error correction challenges we'll face? And Marcus, how should we structure the project timeline?"
    }
    
    observer_test, observer_response = run_test(
        "Send Observer Message with Direct Questions",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=True,
        expected_keys=["message", "observer_message", "agent_responses"]
    )
    
    if not observer_test or not observer_response:
        print("❌ Failed to send observer message")
        return False, "Observer message failed"
    
    # Analyze responses for priority handling
    agent_responses = observer_response.get("agent_responses", {})
    messages = agent_responses.get("messages", [])
    
    direct_answers = 0
    total_agent_responses = 0
    
    for msg in messages:
        agent_name = msg.get("agent_name", "")
        message_text = msg.get("message", "").lower()
        
        if agent_name == "Observer (You)":
            continue
            
        total_agent_responses += 1
        
        # Check if agents mentioned in question respond appropriately
        if "sarah" in agent_name.lower() or "chen" in agent_name.lower():
            if any(keyword in message_text for keyword in ["quantum", "error", "correction", "challenge"]):
                direct_answers += 1
                print(f"✅ Dr. Sarah Chen provided relevant response to quantum question")
        
        if "marcus" in agent_name.lower() or "thompson" in agent_name.lower():
            if any(keyword in message_text for keyword in ["timeline", "project", "structure", "schedule"]):
                direct_answers += 1
                print(f"✅ Marcus Thompson provided relevant response to timeline question")
    
    if total_agent_responses > 0:
        response_relevance = direct_answers / total_agent_responses * 100
        print(f"📊 PRIORITY RESPONSE ANALYSIS:")
        print(f"Total agent responses: {total_agent_responses}")
        print(f"Direct relevant answers: {direct_answers}")
        print(f"Response relevance: {response_relevance:.1f}%")
        
        if response_relevance >= 50:
            print("✅ Priority-based response system is working")
            return True, {"response_relevance": response_relevance}
        else:
            print("❌ Priority-based response system needs improvement")
            return False, {"response_relevance": response_relevance}
    else:
        print("❌ No agent responses to analyze")
        return False, {"response_relevance": 0}

def run_enhanced_collaborative_conversation_tests():
    """Run all enhanced collaborative conversation tests"""
    print("="*80)
    print("ENHANCED COLLABORATIVE CONVERSATION SYSTEM TESTING")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed - cannot proceed with tests")
        return False
    
    # Step 2: Create test agents
    agents = create_test_agents()
    if len(agents) < 3:
        print("❌ Insufficient agents created - cannot proceed with collaboration tests")
        return False
    
    # Step 3: Setup simulation
    if not setup_simulation():
        print("❌ Simulation setup failed - cannot proceed with tests")
        return False
    
    # Step 4: Test conversation progression and collaboration
    progression_success, progression_data = test_conversation_progression()
    
    # Step 5: Test solution focus
    solution_success, solution_data = test_solution_focus()
    
    # Step 6: Test priority response system
    priority_success, priority_data = test_priority_response_system()
    
    # Calculate overall results
    tests_passed = sum([progression_success, solution_success, priority_success])
    total_tests = 3
    
    print("\n" + "="*80)
    print("ENHANCED COLLABORATIVE CONVERSATION TEST SUMMARY")
    print("="*80)
    
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Overall success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if progression_success:
        print("✅ Conversation progression and collaboration: WORKING")
        avg_collab = progression_data.get("avg_collaboration", 0)
        print(f"   Average collaboration score: {avg_collab}/100")
    else:
        print("❌ Conversation progression and collaboration: FAILED")
    
    if solution_success:
        print("✅ Solution-focused conversations: WORKING")
        solution_focus = solution_data.get("solution_focus", 0)
        print(f"   Solution focus percentage: {solution_focus:.1f}%")
    else:
        print("❌ Solution-focused conversations: FAILED")
    
    if priority_success:
        print("✅ Priority-based response system: WORKING")
        response_relevance = priority_data.get("response_relevance", 0)
        print(f"   Response relevance: {response_relevance:.1f}%")
    else:
        print("❌ Priority-based response system: FAILED")
    
    # Overall assessment
    if tests_passed >= 2:
        print("\n🎉 ENHANCED COLLABORATIVE CONVERSATION SYSTEM: WORKING")
        print("The system demonstrates good collaborative behavior with agents:")
        print("- Referencing each other's points")
        print("- Building on teammates' ideas")
        print("- Asking and answering questions")
        print("- Working toward solutions")
        return True
    else:
        print("\n❌ ENHANCED COLLABORATIVE CONVERSATION SYSTEM: NEEDS IMPROVEMENT")
        print("The system requires further development to achieve full collaboration")
        return False

if __name__ == "__main__":
    success = run_enhanced_collaborative_conversation_tests()
    sys.exit(0 if success else 1)