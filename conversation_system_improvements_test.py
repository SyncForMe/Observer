#!/usr/bin/env python3
"""
Comprehensive test script for the three conversation system improvements:
1. Speed Optimization (15-second intervals)
2. Invisible Conversation Summary (15+ messages)
3. Automatic Time Progression (every 8 messages)
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import statistics

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
    "performance_data": {
        "conversation_times": [],
        "summary_data": [],
        "time_progression_data": []
    }
}

# Global variables
auth_token = None
test_user_id = None
simulation_agents = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
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
        
        print(f"Status Code: {response.status_code}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
        try:
            response_data = response.json()
            if len(str(response_data)) > 1000:
                print(f"Response: {json.dumps(response_data, indent=2)[:1000]}... (truncated)")
            else:
                print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text[:500]}...")
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
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
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

def setup_authentication():
    """Set up authentication for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("SETTING UP AUTHENTICATION")
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

def setup_simulation():
    """Set up simulation with test agents"""
    global simulation_agents
    
    print("\n" + "="*80)
    print("SETTING UP SIMULATION WITH TEST AGENTS")
    print("="*80)
    
    # Reset simulation first
    reset_test, reset_response = run_test(
        "Reset Simulation",
        "/simulation/reset",
        method="POST",
        auth=True
    )
    
    if not reset_test:
        print("⚠️ Simulation reset failed, continuing anyway")
    
    # Create 3 test agents for conversation testing
    test_agents = [
        {
            "name": "Dr. Quantum Researcher",
            "archetype": "scientist",
            "goal": "Develop quantum computing solutions for cryptographic applications",
            "expertise": "Quantum mechanics, cryptography, quantum error correction",
            "background": "PhD in Quantum Physics with 10 years experience in quantum computing research"
        },
        {
            "name": "Prof. AI Strategist", 
            "archetype": "leader",
            "goal": "Lead strategic planning for AI integration projects",
            "expertise": "AI strategy, project management, technology leadership",
            "background": "Former tech executive with expertise in AI implementation and team leadership"
        },
        {
            "name": "Dr. Security Analyst",
            "archetype": "skeptic", 
            "goal": "Ensure security and identify potential risks in new technologies",
            "expertise": "Cybersecurity, risk assessment, security protocols",
            "background": "Cybersecurity expert with focus on emerging technology threats and vulnerabilities"
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
            expected_keys=["id", "name"]
        )
        
        if create_test and create_response:
            created_agents.append(create_response)
            print(f"✅ Created agent: {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    simulation_agents = created_agents
    
    if len(created_agents) >= 3:
        print(f"✅ Successfully created {len(created_agents)} test agents")
        
        # Start simulation
        start_test, start_response = run_test(
            "Start Simulation",
            "/simulation/start",
            method="POST",
            auth=True,
            expected_keys=["message", "state"]
        )
        
        if start_test:
            print("✅ Simulation started successfully")
            return True
        else:
            print("❌ Failed to start simulation")
            return False
    else:
        print(f"❌ Only created {len(created_agents)} agents, need at least 3")
        return False

def test_speed_optimization():
    """Test the speed optimization (15-second intervals)"""
    print("\n" + "="*80)
    print("TESTING SPEED OPTIMIZATION (15-SECOND INTERVALS)")
    print("="*80)
    
    if not simulation_agents:
        print("❌ No simulation agents available for testing")
        return False
    
    print(f"Testing conversation generation speed with {len(simulation_agents)} agents")
    
    # Test multiple conversation generations to measure speed
    conversation_times = []
    conversation_data = []
    
    for i in range(5):
        print(f"\n--- Conversation Generation Test {i+1}/5 ---")
        
        start_time = time.time()
        
        conv_test, conv_response = run_test(
            f"Generate Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True,
            expected_keys=["round_number", "messages"]
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        conversation_times.append(response_time)
        
        if conv_test and conv_response:
            messages = conv_response.get("messages", [])
            message_count = len(messages)
            total_chars = sum(len(msg.get("message", "")) for msg in messages)
            
            conversation_data.append({
                "test_number": i+1,
                "response_time": response_time,
                "message_count": message_count,
                "total_characters": total_chars,
                "avg_chars_per_message": total_chars / message_count if message_count > 0 else 0
            })
            
            print(f"✅ Generated {message_count} messages in {response_time:.2f}s")
            print(f"   Total characters: {total_chars}, Avg per message: {total_chars/message_count:.0f}")
        else:
            print(f"❌ Conversation generation {i+1} failed")
            conversation_data.append({
                "test_number": i+1,
                "response_time": response_time,
                "failed": True
            })
        
        # Small delay between tests
        time.sleep(2)
    
    # Analyze speed performance
    if conversation_times:
        avg_time = statistics.mean(conversation_times)
        median_time = statistics.median(conversation_times)
        min_time = min(conversation_times)
        max_time = max(conversation_times)
        
        print(f"\n📊 SPEED OPTIMIZATION RESULTS:")
        print(f"Average response time: {avg_time:.2f} seconds")
        print(f"Median response time: {median_time:.2f} seconds")
        print(f"Fastest response: {min_time:.2f} seconds")
        print(f"Slowest response: {max_time:.2f} seconds")
        
        # Evaluate performance against 15-second target
        target_time = 15.0
        if avg_time <= target_time:
            performance_rating = "EXCELLENT" if avg_time <= 10 else "GOOD"
            print(f"✅ Speed optimization is working: {performance_rating} (avg {avg_time:.2f}s ≤ {target_time}s target)")
            speed_success = True
        else:
            print(f"❌ Speed optimization needs improvement: avg {avg_time:.2f}s > {target_time}s target")
            speed_success = False
        
        # Store performance data
        test_results["performance_data"]["conversation_times"] = conversation_data
        
        return speed_success
    else:
        print("❌ No valid conversation times recorded")
        return False

def test_invisible_summary_system():
    """Test the invisible conversation summary system (15+ messages)"""
    print("\n" + "="*80)
    print("TESTING INVISIBLE CONVERSATION SUMMARY SYSTEM (15+ MESSAGES)")
    print("="*80)
    
    if not simulation_agents:
        print("❌ No simulation agents available for testing")
        return False
    
    # Generate multiple conversations to reach 15+ messages
    print("Generating multiple conversations to test summary system...")
    
    total_messages = 0
    conversation_rounds = []
    
    # Generate conversations until we have 15+ messages
    round_count = 0
    while total_messages < 15 and round_count < 10:  # Safety limit
        round_count += 1
        print(f"\n--- Generating Conversation Round {round_count} ---")
        
        conv_test, conv_response = run_test(
            f"Generate Conversation Round {round_count}",
            "/conversation/generate", 
            method="POST",
            auth=True,
            expected_keys=["round_number", "messages"]
        )
        
        if conv_test and conv_response:
            messages = conv_response.get("messages", [])
            message_count = len(messages)
            total_messages += message_count
            
            conversation_rounds.append({
                "round": round_count,
                "messages": message_count,
                "total_messages": total_messages
            })
            
            print(f"✅ Round {round_count}: {message_count} messages (total: {total_messages})")
            
            # Check for context awareness in messages
            context_indicators = []
            for msg in messages:
                message_text = msg.get("message", "").lower()
                if any(phrase in message_text for phrase in [
                    "building on", "as mentioned", "earlier", "previously", 
                    "discussed", "agreed", "decided", "established"
                ]):
                    context_indicators.append(msg.get("agent_name", "Unknown"))
            
            if context_indicators:
                print(f"   📝 Context awareness detected in messages from: {', '.join(set(context_indicators))}")
        else:
            print(f"❌ Failed to generate conversation round {round_count}")
            break
        
        time.sleep(1)  # Brief pause between generations
    
    print(f"\n📊 CONVERSATION GENERATION SUMMARY:")
    print(f"Total conversation rounds: {round_count}")
    print(f"Total messages generated: {total_messages}")
    
    if total_messages < 15:
        print(f"⚠️ Only generated {total_messages} messages, need 15+ for summary testing")
        return False
    
    # Test 1: Check for conversation summaries in database
    print(f"\n--- Testing Summary Storage ---")
    
    summaries_test, summaries_response = run_test(
        "Get Conversation Summaries",
        "/internal/conversation-summaries",
        method="GET",
        auth=True
    )
    
    summary_count = 0
    if summaries_test and summaries_response:
        summary_count = len(summaries_response)
        print(f"✅ Found {summary_count} conversation summaries in database")
        
        if summary_count > 0:
            # Analyze summary content
            for i, summary in enumerate(summaries_response[:3]):  # Show first 3
                summary_text = summary.get("summary", "")
                summary_length = len(summary_text)
                created_at = summary.get("created_at", "Unknown")
                
                print(f"   Summary {i+1}: {summary_length} chars, created: {created_at}")
                if summary_length > 100:
                    print(f"   Preview: {summary_text[:200]}...")
    else:
        print("❌ Failed to retrieve conversation summaries")
    
    # Test 2: Check for context awareness in recent conversations
    print(f"\n--- Testing Context Awareness ---")
    
    # Generate one more conversation to test if it references previous context
    context_test, context_response = run_test(
        "Generate Context-Aware Conversation",
        "/conversation/generate",
        method="POST", 
        auth=True,
        expected_keys=["round_number", "messages"]
    )
    
    context_awareness_detected = False
    if context_test and context_response:
        messages = context_response.get("messages", [])
        
        for msg in messages:
            message_text = msg.get("message", "").lower()
            agent_name = msg.get("agent_name", "Unknown")
            
            # Look for context references
            context_phrases = [
                "building on", "as we discussed", "earlier conversation", 
                "previously mentioned", "as established", "continuing from",
                "based on our discussion", "following up on"
            ]
            
            found_phrases = [phrase for phrase in context_phrases if phrase in message_text]
            if found_phrases:
                context_awareness_detected = True
                print(f"✅ Context awareness detected in {agent_name}: {found_phrases}")
                print(f"   Message: {msg.get('message', '')[:150]}...")
    
    # Test 3: Verify summary system is invisible (no UI delays)
    print(f"\n--- Testing Invisibility (No UI Delays) ---")
    
    # Measure response times to ensure no significant delays from summary processing
    quick_times = []
    for i in range(3):
        start_time = time.time()
        
        quick_test, quick_response = run_test(
            f"Quick Response Test {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        quick_times.append(response_time)
        
        if quick_test:
            print(f"✅ Quick test {i+1}: {response_time:.2f}s")
        
        time.sleep(1)
    
    if quick_times:
        avg_quick_time = statistics.mean(quick_times)
        print(f"📊 Average response time with summaries: {avg_quick_time:.2f}s")
        
        # Check if response times are reasonable (no significant UI delays)
        if avg_quick_time <= 20.0:  # Reasonable threshold
            print("✅ No significant UI delays detected from summary system")
            invisibility_success = True
        else:
            print("⚠️ Response times may be affected by summary processing")
            invisibility_success = False
    else:
        invisibility_success = False
    
    # Overall assessment
    print(f"\n📊 INVISIBLE SUMMARY SYSTEM RESULTS:")
    print(f"Messages generated: {total_messages}")
    print(f"Summaries stored: {summary_count}")
    print(f"Context awareness: {'✅ Detected' if context_awareness_detected else '❌ Not detected'}")
    print(f"System invisibility: {'✅ Confirmed' if invisibility_success else '❌ Issues detected'}")
    
    # Store summary data
    test_results["performance_data"]["summary_data"] = {
        "total_messages": total_messages,
        "summary_count": summary_count,
        "context_awareness": context_awareness_detected,
        "invisibility_success": invisibility_success,
        "conversation_rounds": conversation_rounds
    }
    
    # Success criteria: summaries exist, context awareness detected, no UI delays
    summary_success = (summary_count > 0 and context_awareness_detected and invisibility_success)
    
    if summary_success:
        print("✅ Invisible conversation summary system is working correctly")
    else:
        print("❌ Invisible conversation summary system has issues")
    
    return summary_success

def test_automatic_time_progression():
    """Test the automatic time progression system (every 8 messages)"""
    print("\n" + "="*80)
    print("TESTING AUTOMATIC TIME PROGRESSION (EVERY 8 MESSAGES)")
    print("="*80)
    
    if not simulation_agents:
        print("❌ No simulation agents available for testing")
        return False
    
    # Reset simulation to start fresh
    reset_test, reset_response = run_test(
        "Reset Simulation for Time Testing",
        "/simulation/reset",
        method="POST",
        auth=True
    )
    
    if reset_test:
        print("✅ Simulation reset for time progression testing")
    
    # Start simulation
    start_test, start_response = run_test(
        "Start Simulation for Time Testing",
        "/simulation/start",
        method="POST",
        auth=True
    )
    
    if not start_test:
        print("❌ Failed to start simulation for time testing")
        return False
    
    # Get initial simulation state
    initial_state_test, initial_state = run_test(
        "Get Initial Simulation State",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period"]
    )
    
    if not initial_state_test:
        print("❌ Failed to get initial simulation state")
        return False
    
    initial_day = initial_state.get("current_day", 1)
    initial_time_period = initial_state.get("current_time_period", "morning")
    
    print(f"📅 Initial state: Day {initial_day} {initial_time_period}")
    
    # Track time progression
    time_progression_data = [{
        "messages": 0,
        "day": initial_day,
        "time_period": initial_time_period,
        "state": f"Day {initial_day} {initial_time_period}"
    }]
    
    total_messages = 0
    expected_progressions = [
        {"messages": 8, "expected": "Day 1 afternoon"},
        {"messages": 16, "expected": "Day 1 evening"}, 
        {"messages": 24, "expected": "Day 2 morning"}
    ]
    
    # Generate conversations and monitor time progression
    conversation_count = 0
    while total_messages < 25 and conversation_count < 15:  # Safety limits
        conversation_count += 1
        print(f"\n--- Conversation {conversation_count} (Total messages: {total_messages}) ---")
        
        # Test both endpoints that should trigger time advancement
        if conversation_count % 2 == 0:
            # Use contextual message endpoint (known to work)
            conv_test, conv_response = run_test(
                f"Generate Contextual Conversation {conversation_count}",
                "/conversation/add-contextual-message",
                method="POST",
                data={"message": f"Let's continue our discussion about the project status - round {conversation_count}"},
                auth=True,
                expected_keys=["round_number", "messages"]
            )
        else:
            # Use main conversation endpoint (needs to be tested)
            conv_test, conv_response = run_test(
                f"Generate Main Conversation {conversation_count}",
                "/conversation/generate",
                method="POST",
                auth=True,
                expected_keys=["round_number", "messages"]
            )
        
        if conv_test and conv_response:
            messages = conv_response.get("messages", [])
            message_count = len(messages)
            total_messages += message_count
            
            print(f"✅ Generated {message_count} messages (total: {total_messages})")
            
            # Check simulation state after conversation
            state_test, current_state = run_test(
                f"Check State After {total_messages} Messages",
                "/simulation/state",
                method="GET",
                auth=True
            )
            
            if state_test and current_state:
                current_day = current_state.get("current_day", 1)
                current_time_period = current_state.get("current_time_period", "morning")
                current_state_str = f"Day {current_day} {current_time_period}"
                
                time_progression_data.append({
                    "messages": total_messages,
                    "day": current_day,
                    "time_period": current_time_period,
                    "state": current_state_str,
                    "conversation_round": conversation_count
                })
                
                print(f"📅 Current state: {current_state_str}")
                
                # Check if time advanced as expected
                for expected in expected_progressions:
                    if total_messages >= expected["messages"]:
                        expected_state = expected["expected"]
                        if current_state_str.lower() == expected_state.lower():
                            print(f"✅ Time progression correct at {total_messages} messages: {current_state_str}")
                        elif total_messages == expected["messages"]:
                            print(f"❌ Time progression incorrect at {total_messages} messages:")
                            print(f"   Expected: {expected_state}")
                            print(f"   Actual: {current_state_str}")
            else:
                print("❌ Failed to get simulation state")
        else:
            print(f"❌ Failed to generate conversation {conversation_count}")
            break
        
        time.sleep(1)  # Brief pause
    
    # Analyze time progression results
    print(f"\n📊 TIME PROGRESSION ANALYSIS:")
    print(f"Total messages generated: {total_messages}")
    print(f"Time progression history:")
    
    for entry in time_progression_data:
        messages = entry["messages"]
        state = entry["state"]
        print(f"   {messages:2d} messages: {state}")
    
    # Check if time advanced correctly
    progression_success = True
    progression_issues = []
    
    final_state = time_progression_data[-1] if time_progression_data else {}
    final_day = final_state.get("day", 1)
    final_time_period = final_state.get("time_period", "morning")
    
    # Expected progression based on message count
    if total_messages >= 24:
        expected_day = 2
        expected_time_period = "morning"
    elif total_messages >= 16:
        expected_day = 1
        expected_time_period = "evening"
    elif total_messages >= 8:
        expected_day = 1
        expected_time_period = "afternoon"
    else:
        expected_day = 1
        expected_time_period = "morning"
    
    if final_day != expected_day or final_time_period != expected_time_period:
        progression_success = False
        progression_issues.append(f"Expected Day {expected_day} {expected_time_period}, got Day {final_day} {final_time_period}")
    
    # Check for time advancement at key milestones
    milestones_hit = 0
    for expected in expected_progressions:
        milestone_messages = expected["messages"]
        if total_messages >= milestone_messages:
            # Find the state at or after this milestone
            milestone_state = None
            for entry in time_progression_data:
                if entry["messages"] >= milestone_messages:
                    milestone_state = entry
                    break
            
            if milestone_state:
                actual_state = milestone_state["state"].lower()
                expected_state = expected["expected"].lower()
                if actual_state == expected_state:
                    milestones_hit += 1
                    print(f"✅ Milestone {milestone_messages} messages: {milestone_state['state']}")
                else:
                    print(f"❌ Milestone {milestone_messages} messages: Expected {expected['expected']}, got {milestone_state['state']}")
    
    # Store time progression data
    test_results["performance_data"]["time_progression_data"] = {
        "total_messages": total_messages,
        "progression_history": time_progression_data,
        "milestones_hit": milestones_hit,
        "total_milestones": len([e for e in expected_progressions if total_messages >= e["messages"]]),
        "progression_success": progression_success,
        "issues": progression_issues
    }
    
    # Overall assessment
    print(f"\n📊 AUTOMATIC TIME PROGRESSION RESULTS:")
    print(f"Messages generated: {total_messages}")
    print(f"Milestones hit: {milestones_hit}/{len([e for e in expected_progressions if total_messages >= e['messages']])}")
    print(f"Final state: Day {final_day} {final_time_period}")
    print(f"Progression success: {'✅ Yes' if progression_success else '❌ No'}")
    
    if progression_issues:
        print("Issues found:")
        for issue in progression_issues:
            print(f"   - {issue}")
    
    if progression_success and milestones_hit > 0:
        print("✅ Automatic time progression is working correctly")
    else:
        print("❌ Automatic time progression has issues")
    
    return progression_success and milestones_hit > 0

def test_integration():
    """Test all three systems working together"""
    print("\n" + "="*80)
    print("TESTING COMPLETE SYSTEM INTEGRATION")
    print("="*80)
    
    if not simulation_agents:
        print("❌ No simulation agents available for integration testing")
        return False
    
    print("Testing all three improvements working together...")
    
    # Reset for fresh integration test
    reset_test, reset_response = run_test(
        "Reset for Integration Test",
        "/simulation/reset",
        method="POST",
        auth=True
    )
    
    start_test, start_response = run_test(
        "Start Integration Test",
        "/simulation/start", 
        method="POST",
        auth=True
    )
    
    if not start_test:
        print("❌ Failed to start integration test")
        return False
    
    # Track integration metrics
    integration_data = {
        "conversations": [],
        "speed_performance": [],
        "time_states": [],
        "summary_indicators": []
    }
    
    total_messages = 0
    conversation_round = 0
    
    # Generate conversations to test all systems
    while total_messages < 20 and conversation_round < 12:
        conversation_round += 1
        print(f"\n--- Integration Test Round {conversation_round} ---")
        
        # Measure speed
        start_time = time.time()
        
        conv_test, conv_response = run_test(
            f"Integration Conversation {conversation_round}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if conv_test and conv_response:
            messages = conv_response.get("messages", [])
            message_count = len(messages)
            total_messages += message_count
            
            # Record speed performance
            integration_data["speed_performance"].append({
                "round": conversation_round,
                "response_time": response_time,
                "messages": message_count
            })
            
            # Check for context awareness (summary system)
            context_detected = False
            for msg in messages:
                message_text = msg.get("message", "").lower()
                if any(phrase in message_text for phrase in [
                    "building on", "as discussed", "previously", "earlier"
                ]):
                    context_detected = True
                    break
            
            integration_data["summary_indicators"].append({
                "round": conversation_round,
                "context_detected": context_detected,
                "total_messages": total_messages
            })
            
            # Check simulation state (time progression)
            state_test, state_response = run_test(
                f"Integration State Check {conversation_round}",
                "/simulation/state",
                method="GET",
                auth=True
            )
            
            if state_test and state_response:
                current_day = state_response.get("current_day", 1)
                current_time_period = state_response.get("current_time_period", "morning")
                
                integration_data["time_states"].append({
                    "round": conversation_round,
                    "messages": total_messages,
                    "day": current_day,
                    "time_period": current_time_period
                })
            
            print(f"✅ Round {conversation_round}: {message_count} msgs in {response_time:.2f}s (total: {total_messages})")
            print(f"   Context awareness: {'✅' if context_detected else '❌'}")
            print(f"   Current state: Day {current_day} {current_time_period}")
        else:
            print(f"❌ Integration test round {conversation_round} failed")
            break
        
        time.sleep(1)
    
    # Analyze integration results
    print(f"\n📊 INTEGRATION TEST RESULTS:")
    
    # Speed analysis
    if integration_data["speed_performance"]:
        avg_speed = statistics.mean([r["response_time"] for r in integration_data["speed_performance"]])
        speed_success = avg_speed <= 15.0
        print(f"Speed optimization: {'✅' if speed_success else '❌'} (avg {avg_speed:.2f}s)")
    else:
        speed_success = False
        print("Speed optimization: ❌ No data")
    
    # Summary system analysis
    context_rounds = sum(1 for r in integration_data["summary_indicators"] if r["context_detected"])
    summary_success = context_rounds > 0 and total_messages >= 15
    print(f"Summary system: {'✅' if summary_success else '❌'} ({context_rounds} rounds with context)")
    
    # Time progression analysis
    time_changes = 0
    if len(integration_data["time_states"]) > 1:
        initial_state = integration_data["time_states"][0]
        final_state = integration_data["time_states"][-1]
        
        if (final_state["day"] > initial_state["day"] or 
            final_state["time_period"] != initial_state["time_period"]):
            time_changes = 1
    
    time_success = time_changes > 0 and total_messages >= 8
    print(f"Time progression: {'✅' if time_success else '❌'} ({time_changes} time changes)")
    
    # Overall integration success
    integration_success = speed_success and summary_success and time_success
    
    print(f"\n🎯 OVERALL INTEGRATION: {'✅ SUCCESS' if integration_success else '❌ ISSUES DETECTED'}")
    
    return integration_success

def print_final_summary():
    """Print final test summary"""
    print("\n" + "="*80)
    print("CONVERSATION SYSTEM IMPROVEMENTS - FINAL SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {test_results['passed']}")
    print(f"Tests failed: {test_results['failed']}")
    print(f"Success rate: {success_rate:.1f}%")
    
    # Performance data summary
    perf_data = test_results["performance_data"]
    
    if perf_data["conversation_times"]:
        avg_time = statistics.mean([c["response_time"] for c in perf_data["conversation_times"] if "response_time" in c])
        print(f"\n📊 SPEED OPTIMIZATION: Avg response time {avg_time:.2f}s")
    
    if perf_data["summary_data"]:
        summary_info = perf_data["summary_data"]
        print(f"📊 SUMMARY SYSTEM: {summary_info['summary_count']} summaries, context awareness: {summary_info['context_awareness']}")
    
    if perf_data["time_progression_data"]:
        time_info = perf_data["time_progression_data"]
        print(f"📊 TIME PROGRESSION: {time_info['milestones_hit']}/{time_info['total_milestones']} milestones hit")
    
    print("\n" + "="*80)

def main():
    """Main test execution"""
    print("🚀 STARTING CONVERSATION SYSTEM IMPROVEMENTS TESTING")
    print("="*80)
    
    # Setup
    if not setup_authentication():
        print("❌ Authentication setup failed, cannot continue")
        return False
    
    if not setup_simulation():
        print("❌ Simulation setup failed, cannot continue")
        return False
    
    # Run individual tests
    print("\n🎯 RUNNING INDIVIDUAL SYSTEM TESTS")
    
    speed_success = test_speed_optimization()
    summary_success = test_invisible_summary_system()
    time_success = test_automatic_time_progression()
    
    # Run integration test
    print("\n🎯 RUNNING INTEGRATION TEST")
    integration_success = test_integration()
    
    # Final summary
    print_final_summary()
    
    # Overall result
    overall_success = speed_success and summary_success and time_success and integration_success
    
    print(f"\n🏁 FINAL RESULT: {'✅ ALL SYSTEMS WORKING' if overall_success else '❌ ISSUES DETECTED'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)