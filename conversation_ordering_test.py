#!/usr/bin/env python3
"""
CONVERSATION GENERATION AGENT ORDERING TESTING
Testing the conversation generation system to verify the current agent message ordering issue.

Focus Areas:
1. Main Conversation Generation: Test POST /api/conversation/generate endpoint
2. Contextual Message Addition: Test POST /api/conversation/add-contextual-message  
3. Agent Selection Logic: Verify if agents can speak consecutively when both systems are used
4. Message Ordering: Check timestamps and sequence to confirm if same agent appears multiple times

User reported: Dr. James Park is sending two consecutive messages (at 08:07:43 and 08:07:50),
suggesting both main conversation generation and contextual message systems are selecting the same agent.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
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
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        if measure_time:
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

def authenticate_guest_user():
    """Authenticate as guest user for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION: Guest User Login")
    print("="*80)
    
    # Test email/password login with known test user
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Guest User Login",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest user login successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest user login failed")
        return False

def setup_test_agents():
    """Create test agents for conversation testing"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("SETUP: Creating Test Agents")
    print("="*80)
    
    # Create multiple agents with different archetypes to test agent selection
    test_agents = [
        {
            "name": "Dr. James Park",
            "archetype": "scientist",
            "goal": "Conduct quantum research and analysis",
            "expertise": "Quantum physics and computational theory",
            "background": "Senior Research Scientist with PhD in Quantum Physics",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            }
        },
        {
            "name": "Sarah Chen",
            "archetype": "leader",
            "goal": "Lead research initiatives and coordinate team efforts",
            "expertise": "Project management and strategic planning",
            "background": "Research Director with extensive leadership experience",
            "personality": {
                "extroversion": 8,
                "optimism": 8,
                "curiosity": 7,
                "cooperativeness": 9,
                "energy": 8
            }
        },
        {
            "name": "Marcus Rodriguez",
            "archetype": "researcher",
            "goal": "Provide technical analysis and research support",
            "expertise": "Data analysis and technical research",
            "background": "Senior Technical Researcher",
            "personality": {
                "extroversion": 5,
                "optimism": 6,
                "curiosity": 8,
                "cooperativeness": 7,
                "energy": 6
            }
        }
    ]
    
    agent_names = []
    
    for i, agent_data in enumerate(test_agents):
        create_test, create_response = run_test(
            f"Create Test Agent {i+1} ({agent_data['name']})",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            created_agent_ids.append(agent_id)
            agent_names.append(agent_data["name"])
            print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
            return False, []
    
    print(f"\n✅ Successfully created {len(created_agent_ids)} test agents")
    print(f"Agent names: {', '.join(agent_names)}")
    
    return True, agent_names

def test_main_conversation_generation():
    """Test POST /api/conversation/generate endpoint for agent message distribution"""
    print("\n" + "="*80)
    print("TEST 1: MAIN CONVERSATION GENERATION")
    print("="*80)
    
    print("🔍 Testing POST /api/conversation/generate endpoint")
    print("Focus: How many messages each agent gets and verify the order")
    
    # Generate multiple conversations to analyze patterns
    conversation_results = []
    
    for i in range(5):  # Test 5 conversations to see patterns
        print(f"\n--- Generating Conversation {i+1} ---")
        
        conversation_test, conversation_response = run_test(
            f"Generate Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True,
            expected_keys=["message", "conversation"]
        )
        
        if conversation_test and conversation_response:
            conversation = conversation_response.get("conversation", {})
            messages = conversation.get("messages", [])
            
            # Analyze agent message distribution
            agent_message_count = {}
            message_sequence = []
            
            for msg in messages:
                agent_name = msg.get("agent_name", "Unknown")
                timestamp = msg.get("timestamp", "")
                
                agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
                message_sequence.append({
                    "agent": agent_name,
                    "timestamp": timestamp,
                    "message": msg.get("message", "")[:100] + "..."
                })
            
            conversation_results.append({
                "conversation_id": i+1,
                "total_messages": len(messages),
                "agent_counts": agent_message_count,
                "message_sequence": message_sequence
            })
            
            print(f"📊 Conversation {i+1} Results:")
            print(f"   Total messages: {len(messages)}")
            print(f"   Agent distribution: {agent_message_count}")
            
            # Check for consecutive messages from same agent
            consecutive_issues = []
            for j in range(1, len(message_sequence)):
                if message_sequence[j]["agent"] == message_sequence[j-1]["agent"]:
                    consecutive_issues.append((j-1, j, message_sequence[j]["agent"]))
            
            if consecutive_issues:
                print(f"   ⚠️ CONSECUTIVE MESSAGES FOUND:")
                for prev_idx, curr_idx, agent_name in consecutive_issues:
                    print(f"      Messages {prev_idx+1} and {curr_idx+1} both from {agent_name}")
            else:
                print(f"   ✅ No consecutive messages from same agent")
                
        else:
            print(f"❌ Failed to generate conversation {i+1}")
            return False
    
    # Analyze overall patterns
    print(f"\n--- OVERALL ANALYSIS: Main Conversation Generation ---")
    
    total_conversations = len(conversation_results)
    conversations_with_consecutive = 0
    agent_selection_patterns = {}
    
    for result in conversation_results:
        # Check for consecutive messages
        has_consecutive = False
        sequence = result["message_sequence"]
        for j in range(1, len(sequence)):
            if sequence[j]["agent"] == sequence[j-1]["agent"]:
                has_consecutive = True
                break
        
        if has_consecutive:
            conversations_with_consecutive += 1
        
        # Track agent selection patterns
        for agent, count in result["agent_counts"].items():
            if agent not in agent_selection_patterns:
                agent_selection_patterns[agent] = []
            agent_selection_patterns[agent].append(count)
    
    print(f"📊 MAIN CONVERSATION GENERATION ANALYSIS:")
    print(f"   Total conversations tested: {total_conversations}")
    print(f"   Conversations with consecutive messages: {conversations_with_consecutive}")
    print(f"   Consecutive message rate: {(conversations_with_consecutive/total_conversations)*100:.1f}%")
    
    print(f"\n📊 AGENT SELECTION PATTERNS:")
    for agent, counts in agent_selection_patterns.items():
        avg_messages = sum(counts) / len(counts)
        max_messages = max(counts)
        min_messages = min(counts)
        print(f"   {agent}: avg={avg_messages:.1f}, min={min_messages}, max={max_messages} messages per conversation")
    
    # Determine if there's an issue
    if conversations_with_consecutive > 0:
        print(f"\n❌ ISSUE DETECTED: {conversations_with_consecutive} out of {total_conversations} conversations had consecutive messages from the same agent")
        print("This indicates the main conversation generation system may be selecting the same agent multiple times")
        return False
    else:
        print(f"\n✅ NO ISSUES: All conversations properly alternated agents")
        return True

def test_contextual_message_addition():
    """Test POST /api/conversation/add-contextual-message endpoint for agent selection"""
    print("\n" + "="*80)
    print("TEST 2: CONTEXTUAL MESSAGE ADDITION")
    print("="*80)
    
    print("🔍 Testing POST /api/conversation/add-contextual-message endpoint")
    print("Focus: Which agent it selects and how it integrates with existing conversations")
    
    # First, check if this endpoint exists by trying to call it
    contextual_test, contextual_response = run_test(
        "Add Contextual Message",
        "/conversation/add-contextual-message",
        method="POST",
        auth=True,
        measure_time=True,
        expected_status=200  # We expect this to work if endpoint exists
    )
    
    if contextual_test and contextual_response:
        print("✅ Contextual message endpoint exists and is accessible")
        
        # Analyze the response
        if "conversation" in contextual_response:
            conversation = contextual_response["conversation"]
            messages = conversation.get("messages", [])
            
            if messages:
                # Get the last message (should be the contextual one)
                last_message = messages[-1]
                selected_agent = last_message.get("agent_name", "Unknown")
                timestamp = last_message.get("timestamp", "")
                
                print(f"📊 Contextual Message Results:")
                print(f"   Selected agent: {selected_agent}")
                print(f"   Timestamp: {timestamp}")
                print(f"   Message: {last_message.get('message', '')[:100]}...")
                
                return True, selected_agent, timestamp
            else:
                print("❌ No messages in contextual response")
                return False, None, None
        else:
            print("❌ No conversation data in contextual response")
            return False, None, None
            
    elif contextual_response is not None and "detail" in contextual_response:
        # Check if it's a 404 (endpoint doesn't exist)
        if "not found" in contextual_response["detail"].lower():
            print("⚠️ Contextual message endpoint does not exist")
            print("This means the system only uses main conversation generation")
            return None, None, None
        else:
            print(f"❌ Contextual message endpoint error: {contextual_response['detail']}")
            return False, None, None
    else:
        print("❌ Contextual message endpoint failed")
        return False, None, None

def test_agent_selection_logic():
    """Test if agents can speak consecutively when both systems are used"""
    print("\n" + "="*80)
    print("TEST 3: AGENT SELECTION LOGIC")
    print("="*80)
    
    print("🔍 Testing agent selection logic when both systems are used")
    print("Focus: Verify if agents can speak consecutively")
    
    # Generate a conversation first
    print("\n--- Step 1: Generate Initial Conversation ---")
    
    initial_test, initial_response = run_test(
        "Generate Initial Conversation for Logic Test",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True,
        expected_keys=["message", "conversation"]
    )
    
    if not initial_test or not initial_response:
        print("❌ Failed to generate initial conversation")
        return False
    
    initial_conversation = initial_response.get("conversation", {})
    initial_messages = initial_conversation.get("messages", [])
    
    if not initial_messages:
        print("❌ No messages in initial conversation")
        return False
    
    # Get the last agent who spoke
    last_agent = initial_messages[-1].get("agent_name", "Unknown")
    last_timestamp = initial_messages[-1].get("timestamp", "")
    
    print(f"📊 Initial Conversation Results:")
    print(f"   Total messages: {len(initial_messages)}")
    print(f"   Last agent: {last_agent}")
    print(f"   Last timestamp: {last_timestamp}")
    
    # Now try to add a contextual message
    print("\n--- Step 2: Add Contextual Message ---")
    
    contextual_success, contextual_agent, contextual_timestamp = test_contextual_message_addition()
    
    if contextual_success is None:
        print("⚠️ Contextual message system not available - cannot test consecutive agent selection")
        return True  # Not a failure, just not applicable
    elif not contextual_success:
        print("❌ Contextual message addition failed")
        return False
    
    # Compare agents and timestamps
    print(f"\n--- Step 3: Analyze Agent Selection ---")
    
    print(f"📊 Agent Selection Analysis:")
    print(f"   Last agent from main generation: {last_agent}")
    print(f"   Agent from contextual message: {contextual_agent}")
    print(f"   Same agent selected: {'YES' if last_agent == contextual_agent else 'NO'}")
    
    if last_timestamp and contextual_timestamp:
        try:
            # Parse timestamps to compare timing
            last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
            contextual_time = datetime.fromisoformat(contextual_timestamp.replace('Z', '+00:00'))
            time_diff = (contextual_time - last_time).total_seconds()
            
            print(f"   Time difference: {time_diff:.1f} seconds")
            
            # Check if this matches the user's reported issue (08:07:43 and 08:07:50 = 7 seconds apart)
            if last_agent == contextual_agent and 5 <= time_diff <= 10:
                print(f"❌ ISSUE CONFIRMED: Same agent ({last_agent}) selected twice within {time_diff:.1f} seconds")
                print("This matches the user's reported issue!")
                return False
            elif last_agent == contextual_agent:
                print(f"⚠️ POTENTIAL ISSUE: Same agent selected twice, but timing different ({time_diff:.1f}s)")
                return False
            else:
                print(f"✅ NO ISSUE: Different agents selected properly")
                return True
                
        except Exception as e:
            print(f"⚠️ Could not parse timestamps for comparison: {e}")
    
    return last_agent != contextual_agent

def test_message_ordering_in_database():
    """Check the actual message ordering in the database to confirm the issue"""
    print("\n" + "="*80)
    print("TEST 4: MESSAGE ORDERING IN DATABASE")
    print("="*80)
    
    print("🔍 Testing message ordering by examining conversation history")
    print("Focus: Check timestamps and sequence of messages to confirm consecutive agent messages")
    
    # Get all conversations for the user
    conversations_test, conversations_response = run_test(
        "Get All Conversations for Ordering Analysis",
        "/conversations",
        method="GET",
        auth=True
    )
    
    if not conversations_test or not conversations_response:
        print("❌ Failed to get conversations")
        return False
    
    print(f"📊 Found {len(conversations_response)} conversations to analyze")
    
    # Analyze each conversation for consecutive agent messages
    consecutive_issues_found = []
    total_messages_analyzed = 0
    
    for i, conversation in enumerate(conversations_response):
        messages = conversation.get("messages", [])
        total_messages_analyzed += len(messages)
        
        print(f"\n--- Analyzing Conversation {i+1} ---")
        print(f"   Round: {conversation.get('round_number', 'N/A')}")
        print(f"   Time Period: {conversation.get('time_period', 'N/A')}")
        print(f"   Messages: {len(messages)}")
        
        # Check for consecutive messages from same agent
        for j in range(1, len(messages)):
            current_msg = messages[j]
            previous_msg = messages[j-1]
            
            current_agent = current_msg.get("agent_name", "Unknown")
            previous_agent = previous_msg.get("agent_name", "Unknown")
            current_timestamp = current_msg.get("timestamp", "")
            previous_timestamp = previous_msg.get("timestamp", "")
            
            if current_agent == previous_agent and current_agent != "Observer (You)":
                # Found consecutive messages from same agent
                consecutive_issues_found.append({
                    "conversation_round": conversation.get("round_number", i+1),
                    "agent_name": current_agent,
                    "message_indices": [j-1, j],
                    "timestamps": [previous_timestamp, current_timestamp],
                    "messages": [
                        previous_msg.get("message", "")[:100] + "...",
                        current_msg.get("message", "")[:100] + "..."
                    ]
                })
                
                print(f"   ⚠️ CONSECUTIVE MESSAGES FOUND:")
                print(f"      Agent: {current_agent}")
                print(f"      Message {j}: {previous_timestamp}")
                print(f"      Message {j+1}: {current_timestamp}")
                
                # Calculate time difference if possible
                try:
                    if previous_timestamp and current_timestamp:
                        prev_time = datetime.fromisoformat(previous_timestamp.replace('Z', '+00:00'))
                        curr_time = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
                        time_diff = (curr_time - prev_time).total_seconds()
                        print(f"      Time difference: {time_diff:.1f} seconds")
                        
                        # Check if this matches the user's specific report
                        if current_agent == "Dr. James Park" and 5 <= time_diff <= 10:
                            print(f"      🎯 MATCHES USER REPORT: Dr. James Park consecutive messages ~{time_diff:.1f}s apart")
                except:
                    pass
    
    # Summary analysis
    print(f"\n--- DATABASE ORDERING ANALYSIS SUMMARY ---")
    print(f"📊 Total conversations analyzed: {len(conversations_response)}")
    print(f"📊 Total messages analyzed: {total_messages_analyzed}")
    print(f"📊 Consecutive message issues found: {len(consecutive_issues_found)}")
    
    if consecutive_issues_found:
        print(f"\n❌ CONSECUTIVE MESSAGE ISSUES DETECTED:")
        
        # Group by agent
        agent_issues = {}
        for issue in consecutive_issues_found:
            agent = issue["agent_name"]
            if agent not in agent_issues:
                agent_issues[agent] = 0
            agent_issues[agent] += 1
        
        for agent, count in agent_issues.items():
            print(f"   {agent}: {count} consecutive message occurrences")
            
            # Special attention to Dr. James Park (user's specific report)
            if agent == "Dr. James Park":
                print(f"   🎯 Dr. James Park issues match user's report!")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print("The consecutive message issue is confirmed in the database.")
        print("This suggests both the main conversation generation and contextual")
        print("message systems are selecting the same agent, causing duplicate messages.")
        
        return False
    else:
        print(f"\n✅ NO CONSECUTIVE MESSAGE ISSUES FOUND")
        print("All agents are properly alternating in conversations.")
        return True

def print_summary():
    """Print a comprehensive summary of all test results"""
    print("\n" + "="*80)
    print("CONVERSATION ORDERING TEST SUMMARY")
    print("="*80)
    
    print(f"Total tests run: {test_results['passed'] + test_results['failed']}")
    print(f"Tests passed: {test_results['passed']}")
    print(f"Tests failed: {test_results['failed']}")
    
    print(f"\n📋 DETAILED TEST RESULTS:")
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
        if "response_time" in test:
            print(f"   Response time: {test['response_time']:.4f}s")
    
    # Overall assessment
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"\n🎯 OVERALL RESULT: {overall_result}")
    
    if test_results["failed"] > 0:
        print("\n❌ ISSUES IDENTIFIED:")
        print("The conversation generation system has agent ordering issues.")
        print("Both main conversation generation and contextual message systems")
        print("may be selecting the same agent, causing consecutive messages.")
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Implement agent selection exclusion logic")
        print("2. Add timestamp-based agent filtering")
        print("3. Ensure proper agent alternation between systems")
        print("4. Add agent cooldown period to prevent consecutive selection")
    else:
        print("\n✅ NO ISSUES FOUND:")
        print("The conversation generation system is working correctly.")
        print("Agents are properly alternating without consecutive messages.")

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Test Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution function"""
    print("="*80)
    print("CONVERSATION GENERATION AGENT ORDERING TESTING")
    print("="*80)
    print("Testing the conversation generation system for agent message ordering issues")
    print("Focus: Verify if Dr. James Park (or other agents) send consecutive messages")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate_guest_user():
        print("❌ Authentication failed - cannot proceed with tests")
        return
    
    # Step 2: Setup test agents
    setup_success, agent_names = setup_test_agents()
    if not setup_success:
        print("❌ Agent setup failed - cannot proceed with tests")
        return
    
    # Step 3: Test main conversation generation
    main_success = test_main_conversation_generation()
    
    # Step 4: Test contextual message addition
    contextual_success, contextual_agent, contextual_timestamp = test_contextual_message_addition()
    
    # Step 5: Test agent selection logic
    selection_success = test_agent_selection_logic()
    
    # Step 6: Test message ordering in database
    ordering_success = test_message_ordering_in_database()
    
    # Step 7: Print comprehensive summary
    print_summary()
    
    # Step 8: Cleanup
    cleanup_test_data()
    
    # Final assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    if not main_success or not selection_success or not ordering_success:
        print("❌ AGENT ORDERING ISSUE CONFIRMED")
        print("The conversation generation system has issues with agent selection")
        print("that cause the same agent to send consecutive messages.")
        print("\nThis matches the user's report about Dr. James Park sending")
        print("two consecutive messages at 08:07:43 and 08:07:50.")
    else:
        print("✅ NO AGENT ORDERING ISSUES DETECTED")
        print("The conversation generation system is working correctly.")

if __name__ == "__main__":
    main()