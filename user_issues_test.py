#!/usr/bin/env python3
"""
USER REPORTED ISSUES TESTING
Testing specific issues reported by the user:

1. **3 messages per agent in bulk** - User reported agents generating 3 messages in a row instead of 1 message per agent
2. **Messages stopping at 81** - User reported conversations stopped generating at 81 messages  
3. **Stop button delay + jump to 104 messages** - User reported when clicking stop, it took time to stop and suddenly showed 104 messages

Testing Protocol:
1. Reset simulation to clean state
2. Create 3 test agents 
3. Generate multiple conversations to test:
   - 1 message per agent per conversation (not 3 in bulk)
   - Continuous generation beyond 81 messages
   - Start/stop simulation behavior
4. Monitor for any race conditions or background processes
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

# Global variables for testing
auth_token = None
test_user_id = None
created_agent_ids = []

def make_request(endpoint, method="GET", data=None, auth=True, timeout=30):
    """Make a request to the API with proper error handling"""
    url = f"{API_URL}{endpoint}"
    headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"text": response.text}
        
        return response.status_code, response_data
    
    except requests.exceptions.Timeout:
        print(f"⚠️ Request timeout for {method} {endpoint}")
        return 408, {"error": "Request timeout"}
    except Exception as e:
        print(f"❌ Request error for {method} {endpoint}: {e}")
        return 500, {"error": str(e)}

def authenticate():
    """Authenticate as guest user"""
    global auth_token, test_user_id
    
    print("🔐 Authenticating as guest user...")
    status, response = make_request("/auth/test-login", method="POST", auth=False)
    
    if status == 200 and "access_token" in response:
        auth_token = response["access_token"]
        user_data = response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication successful. User ID: {test_user_id}")
        return True
    else:
        print(f"❌ Authentication failed: {response}")
        return False

def reset_simulation():
    """Reset simulation to clean state"""
    print("\n🔄 Resetting simulation to clean state...")
    
    # Stop simulation if running
    status, response = make_request("/simulation/pause", method="POST")
    if status == 200:
        print("✅ Simulation paused")
    
    # Clear existing agents
    status, agents = make_request("/agents", method="GET")
    if status == 200 and agents:
        for agent in agents:
            agent_id = agent.get("id")
            if agent_id:
                status, response = make_request(f"/agents/{agent_id}", method="DELETE")
                if status == 200:
                    print(f"✅ Deleted existing agent: {agent.get('name', agent_id)}")
    
    print("✅ Simulation reset complete")

def create_test_agents():
    """Create 3 test agents for testing"""
    global created_agent_ids
    
    print("\n🤖 Creating 3 test agents...")
    
    agents_data = [
        {
            "name": "Dr. Alice Quantum",
            "archetype": "scientist",
            "goal": "Research quantum computing applications",
            "expertise": "Quantum physics and computing",
            "background": "PhD in Quantum Physics with 10 years research experience",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Prof. Bob Engineer",
            "archetype": "leader",
            "goal": "Lead engineering implementation",
            "expertise": "Systems engineering and project management",
            "background": "Senior Engineering Manager with 15 years experience",
            "personality": {
                "extroversion": 8,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Dr. Carol Analyst",
            "archetype": "skeptic",
            "goal": "Analyze risks and challenges",
            "expertise": "Risk analysis and quality assurance",
            "background": "Senior Risk Analyst with expertise in technology assessment",
            "personality": {
                "extroversion": 4,
                "optimism": 4,
                "curiosity": 8,
                "cooperativeness": 6,
                "energy": 5
            }
        }
    ]
    
    created_agents = []
    
    for i, agent_data in enumerate(agents_data, 1):
        print(f"Creating agent {i}: {agent_data['name']}")
        status, response = make_request("/agents", method="POST", data=agent_data)
        
        if status == 200:
            # Handle different response formats
            if "agent_id" in response:
                agent_id = response["agent_id"]
            elif "id" in response:
                agent_id = response["id"]
            else:
                print(f"❌ No agent ID found in response: {response}")
                return None
            created_agent_ids.append(agent_id)
            created_agents.append({
                "id": agent_id,
                "name": agent_data["name"],
                "archetype": agent_data["archetype"]
            })
            print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent {agent_data['name']}: {response}")
            return None
    
    print(f"✅ Successfully created {len(created_agents)} test agents")
    return created_agents

def test_messages_per_agent():
    """Test Issue #1: 3 messages per agent in bulk vs 1 message per agent"""
    print("\n" + "="*80)
    print("🧪 TESTING ISSUE #1: Messages Per Agent (3 vs 1)")
    print("="*80)
    
    # Get initial conversation count
    status, conversations = make_request("/conversations", method="GET")
    initial_count = len(conversations) if status == 200 and conversations else 0
    print(f"Initial conversation count: {initial_count}")
    
    # Get initial message count
    total_initial_messages = 0
    if status == 200 and conversations:
        for conv in conversations:
            messages = conv.get("messages", [])
            total_initial_messages += len(messages)
    print(f"Initial total messages: {total_initial_messages}")
    
    # Generate a conversation
    print("\n🔄 Generating conversation to test message count per agent...")
    start_time = time.time()
    status, response = make_request("/conversation/generate", method="POST", timeout=45)
    end_time = time.time()
    
    if status != 200:
        print(f"❌ Conversation generation failed: {response}")
        return False
    
    print(f"✅ Conversation generation completed in {end_time - start_time:.2f} seconds")
    
    # Get updated conversations
    status, updated_conversations = make_request("/conversations", method="GET")
    if status != 200:
        print(f"❌ Failed to get updated conversations: {updated_conversations}")
        return False
    
    new_count = len(updated_conversations)
    print(f"Updated conversation count: {new_count}")
    
    # Find the new conversation
    if new_count > initial_count:
        # Get the latest conversation
        latest_conversation = max(updated_conversations, key=lambda x: x.get("created_at", ""))
        messages = latest_conversation.get("messages", [])
        message_count = len(messages)
        
        print(f"\n📊 ANALYSIS:")
        print(f"- New conversation generated: {latest_conversation.get('id', 'Unknown')}")
        print(f"- Messages in new conversation: {message_count}")
        print(f"- Expected: 3 messages (1 per agent)")
        
        # Analyze message distribution by agent
        agent_message_counts = {}
        for msg in messages:
            agent_name = msg.get("agent_name", "Unknown")
            agent_message_counts[agent_name] = agent_message_counts.get(agent_name, 0) + 1
        
        print(f"\n📈 MESSAGE DISTRIBUTION BY AGENT:")
        for agent_name, count in agent_message_counts.items():
            print(f"- {agent_name}: {count} messages")
        
        # Check if each agent has exactly 1 message
        expected_agents = 3
        if len(agent_message_counts) == expected_agents:
            all_agents_one_message = all(count == 1 for count in agent_message_counts.values())
            if all_agents_one_message:
                print(f"✅ ISSUE #1 RESOLVED: Each agent generated exactly 1 message")
                return True
            else:
                max_messages = max(agent_message_counts.values())
                if max_messages == 3:
                    print(f"❌ ISSUE #1 CONFIRMED: Some agents generated 3 messages instead of 1")
                else:
                    print(f"❌ ISSUE #1 PARTIAL: Inconsistent message counts (max: {max_messages})")
                return False
        else:
            print(f"❌ Unexpected number of agents in conversation: {len(agent_message_counts)} (expected {expected_agents})")
            return False
    else:
        print(f"❌ No new conversation was generated")
        return False

def test_continuous_generation():
    """Test Issue #2: Messages stopping at 81"""
    print("\n" + "="*80)
    print("🧪 TESTING ISSUE #2: Continuous Generation Beyond 81 Messages")
    print("="*80)
    
    # Get current total message count
    status, conversations = make_request("/conversations", method="GET")
    if status != 200:
        print(f"❌ Failed to get conversations: {conversations}")
        return False
    
    total_messages = 0
    for conv in conversations:
        messages = conv.get("messages", [])
        total_messages += len(messages)
    
    print(f"Current total messages: {total_messages}")
    
    # If we're already above 81, test if we can generate more
    if total_messages >= 81:
        print(f"✅ Already have {total_messages} messages (above 81 threshold)")
        
        # Try to generate more conversations
        print("🔄 Testing if we can generate more conversations beyond 81 messages...")
        
        for i in range(3):  # Try to generate 3 more conversations
            print(f"\nGenerating conversation {i+1}/3...")
            start_time = time.time()
            status, response = make_request("/conversation/generate", method="POST", timeout=45)
            end_time = time.time()
            
            if status == 200:
                print(f"✅ Conversation {i+1} generated successfully in {end_time - start_time:.2f} seconds")
                
                # Check updated message count
                status, updated_conversations = make_request("/conversations", method="GET")
                if status == 200:
                    new_total_messages = 0
                    for conv in updated_conversations:
                        messages = conv.get("messages", [])
                        new_total_messages += len(messages)
                    print(f"Updated total messages: {new_total_messages}")
                    
                    if new_total_messages > total_messages:
                        total_messages = new_total_messages
                        print(f"✅ Message count increased to {total_messages}")
                    else:
                        print(f"⚠️ Message count did not increase")
                else:
                    print(f"❌ Failed to get updated conversations")
            else:
                print(f"❌ Conversation {i+1} generation failed: {response}")
                return False
            
            # Small delay between generations
            time.sleep(2)
        
        if total_messages > 81:
            print(f"✅ ISSUE #2 RESOLVED: Successfully generated {total_messages} messages (beyond 81)")
            return True
        else:
            print(f"❌ ISSUE #2 CONFIRMED: Generation stopped at {total_messages} messages")
            return False
    
    else:
        # Need to generate conversations to reach 81+ messages
        print(f"Need to generate more conversations to reach 81+ messages...")
        target_conversations = (81 - total_messages) // 3 + 5  # Add buffer
        
        print(f"Generating {target_conversations} conversations to test 81 message threshold...")
        
        for i in range(target_conversations):
            print(f"Generating conversation {i+1}/{target_conversations}...")
            status, response = make_request("/conversation/generate", method="POST", timeout=45)
            
            if status == 200:
                # Check current message count
                status, updated_conversations = make_request("/conversations", method="GET")
                if status == 200:
                    current_total = 0
                    for conv in updated_conversations:
                        messages = conv.get("messages", [])
                        current_total += len(messages)
                    
                    print(f"Current total messages: {current_total}")
                    
                    if current_total >= 81:
                        print(f"✅ Reached {current_total} messages. Testing if generation continues...")
                        
                        # Try to generate one more
                        status, response = make_request("/conversation/generate", method="POST", timeout=45)
                        if status == 200:
                            # Check if message count increased
                            status, final_conversations = make_request("/conversations", method="GET")
                            if status == 200:
                                final_total = 0
                                for conv in final_conversations:
                                    messages = conv.get("messages", [])
                                    final_total += len(messages)
                                
                                if final_total > current_total:
                                    print(f"✅ ISSUE #2 RESOLVED: Generation continued beyond 81 to {final_total} messages")
                                    return True
                                else:
                                    print(f"❌ ISSUE #2 CONFIRMED: Generation stopped at {current_total} messages")
                                    return False
                        else:
                            print(f"❌ ISSUE #2 CONFIRMED: Failed to generate beyond 81 messages")
                            return False
                else:
                    print(f"❌ Failed to get updated conversations")
                    return False
            else:
                print(f"❌ Conversation generation failed: {response}")
                return False
            
            # Small delay between generations
            time.sleep(1)
        
        print(f"❌ Could not reach 81 messages after {target_conversations} attempts")
        return False

def test_start_stop_behavior():
    """Test Issue #3: Stop button delay + jump to 104 messages"""
    print("\n" + "="*80)
    print("🧪 TESTING ISSUE #3: Start/Stop Simulation Behavior")
    print("="*80)
    
    # Get initial state
    status, initial_state = make_request("/simulation/state", method="GET")
    if status != 200:
        print(f"❌ Failed to get initial simulation state: {initial_state}")
        return False
    
    print(f"Initial simulation state: {initial_state.get('is_active', 'Unknown')}")
    
    # Get initial message count
    status, conversations = make_request("/conversations", method="GET")
    if status != 200:
        print(f"❌ Failed to get conversations: {conversations}")
        return False
    
    initial_message_count = 0
    for conv in conversations:
        messages = conv.get("messages", [])
        initial_message_count += len(messages)
    
    print(f"Initial message count: {initial_message_count}")
    
    # Start simulation
    print("\n🚀 Starting simulation...")
    start_time = time.time()
    status, start_response = make_request("/simulation/start", method="POST")
    end_time = time.time()
    
    if status != 200:
        print(f"❌ Failed to start simulation: {start_response}")
        return False
    
    print(f"✅ Simulation started in {end_time - start_time:.2f} seconds")
    
    # Verify simulation is active
    status, active_state = make_request("/simulation/state", method="GET")
    if status == 200 and active_state.get("is_active"):
        print("✅ Simulation is active")
    else:
        print(f"❌ Simulation is not active: {active_state}")
        return False
    
    # Let simulation run for a short time (simulate user letting it run)
    print("\n⏳ Letting simulation run for 10 seconds...")
    time.sleep(10)
    
    # Check message count during run
    status, running_conversations = make_request("/conversations", method="GET")
    if status == 200:
        running_message_count = 0
        for conv in running_conversations:
            messages = conv.get("messages", [])
            running_message_count += len(messages)
        print(f"Message count during run: {running_message_count}")
    
    # Stop simulation and measure response time
    print("\n🛑 Stopping simulation...")
    stop_start_time = time.time()
    status, stop_response = make_request("/simulation/pause", method="POST")
    stop_end_time = time.time()
    
    stop_response_time = stop_end_time - stop_start_time
    print(f"Stop response time: {stop_response_time:.2f} seconds")
    
    if status != 200:
        print(f"❌ Failed to stop simulation: {stop_response}")
        return False
    
    print(f"✅ Simulation stopped")
    
    # Immediately check message count after stop
    status, stopped_conversations = make_request("/conversations", method="GET")
    if status != 200:
        print(f"❌ Failed to get conversations after stop: {stopped_conversations}")
        return False
    
    immediate_message_count = 0
    for conv in stopped_conversations:
        messages = conv.get("messages", [])
        immediate_message_count += len(messages)
    
    print(f"Message count immediately after stop: {immediate_message_count}")
    
    # Wait a few seconds and check again for any delayed messages
    print("\n⏳ Waiting 5 seconds to check for delayed messages...")
    time.sleep(5)
    
    status, final_conversations = make_request("/conversations", method="GET")
    if status == 200:
        final_message_count = 0
        for conv in final_conversations:
            messages = conv.get("messages", [])
            final_message_count += len(messages)
        
        print(f"Final message count after delay: {final_message_count}")
        
        # Analyze results
        print(f"\n📊 ANALYSIS:")
        print(f"- Initial messages: {initial_message_count}")
        print(f"- Messages during run: {running_message_count}")
        print(f"- Messages immediately after stop: {immediate_message_count}")
        print(f"- Final messages after delay: {final_message_count}")
        print(f"- Stop response time: {stop_response_time:.2f} seconds")
        
        # Check for issues
        issues_found = []
        
        # Check stop response time
        if stop_response_time > 3.0:
            issues_found.append(f"Slow stop response time: {stop_response_time:.2f}s (expected < 3s)")
        
        # Check for message jumps after stop
        if final_message_count > immediate_message_count:
            jump_amount = final_message_count - immediate_message_count
            issues_found.append(f"Message jump after stop: +{jump_amount} messages")
        
        # Check for specific jump to 104 messages
        if final_message_count == 104 and immediate_message_count < 104:
            issues_found.append("Specific jump to 104 messages detected")
        
        if issues_found:
            print(f"\n❌ ISSUE #3 CONFIRMED:")
            for issue in issues_found:
                print(f"  - {issue}")
            return False
        else:
            print(f"\n✅ ISSUE #3 RESOLVED: No stop button delays or message jumps detected")
            return True
    
    else:
        print(f"❌ Failed to get final conversations: {final_conversations}")
        return False

def cleanup():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    for agent_id in created_agent_ids:
        status, response = make_request(f"/agents/{agent_id}", method="DELETE")
        if status == 200:
            print(f"✅ Deleted agent: {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}: {response}")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution function"""
    print("USER REPORTED ISSUES TESTING")
    print("Testing specific issues reported by the user")
    print("="*80)
    
    # Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return False
    
    # Reset simulation
    reset_simulation()
    
    # Create test agents
    agents = create_test_agents()
    if not agents:
        print("❌ Failed to create test agents. Cannot proceed with tests.")
        return False
    
    # Run tests
    test_results = {}
    
    tests = [
        ("Issue #1: Messages Per Agent", test_messages_per_agent),
        ("Issue #2: Continuous Generation", test_continuous_generation),
        ("Issue #3: Start/Stop Behavior", test_start_stop_behavior)
    ]
    
    for test_name, test_function in tests:
        print(f"\n{'='*80}")
        print(f"RUNNING TEST: {test_name}")
        print(f"{'='*80}")
        
        try:
            result = test_function()
            test_results[test_name] = result
            
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            test_results[test_name] = False
    
    # Cleanup
    cleanup()
    
    # Print final summary
    print(f"\n{'='*80}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*80}")
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    print(f"\nDetailed Results:")
    for test_name, result in test_results.items():
        status = "✅ RESOLVED" if result else "❌ CONFIRMED"
        print(f"  {status} {test_name}")
    
    print(f"{'='*80}")
    
    if passed_tests == total_tests:
        print("🎉 ALL ISSUES RESOLVED!")
        return True
    else:
        print("⚠️ SOME ISSUES STILL EXIST")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)