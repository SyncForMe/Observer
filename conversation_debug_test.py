#!/usr/bin/env python3
"""
CONVERSATION GENERATION DEBUGGING TEST
Comprehensive investigation of conversation generation issues reported by user:

1. Agents generating 3 messages in a row instead of 1 message per agent
2. Messages stopped generating at 81 messages
3. Last 10-20 messages showed agents generating 3 messages in a row (Dr. Satoshi Nakamura had 5 consecutive messages)
4. When stop button was clicked, it took time to stop and suddenly showed 104 messages
5. No time progression from Day 1 Evening to Day 2 Morning

Investigation Points:
- Test the `/api/conversation/generate` endpoint directly to see what it returns
- Check if there are multiple conversation generation calls happening
- Verify the message count and structure in the database after generation
- Look for any background processes or async tasks that might be duplicating messages
- Check if the time progression system is causing multiple generations
- Investigate why conversation stopped at 81 messages vs continuing
- Test the stop/start simulation functionality to see why it jumped to 104 messages
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

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load JWT secret for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET', "test_secret")

# Global variables
auth_token = None
test_user_id = None
created_agent_ids = []

def authenticate():
    """Authenticate and get JWT token"""
    global auth_token, test_user_id
    
    print("🔐 Authenticating...")
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

def create_test_agents():
    """Create test agents for conversation generation"""
    global created_agent_ids
    
    print("\n🤖 Creating test agents...")
    
    agents_data = [
        {
            "name": "Dr. Satoshi Nakamura",
            "archetype": "scientist",
            "goal": "Research quantum computing applications",
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
            "name": "Prof. Maria Rodriguez",
            "archetype": "leader",
            "goal": "Lead research team and coordinate projects",
            "expertise": "Project Management and Research Leadership",
            "background": "Senior research director with extensive team leadership experience",
            "personality": {
                "extroversion": 8,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Dr. James Wilson",
            "archetype": "skeptic",
            "goal": "Ensure research quality and identify potential issues",
            "expertise": "Quality Assurance and Risk Analysis",
            "background": "Critical thinker focused on research validation",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        }
    ]
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    for agent_data in agents_data:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                agent_id = result.get("agent_id")
                if agent_id:
                    created_agent_ids.append(agent_id)
                    print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
                else:
                    print(f"❌ No agent ID returned for {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    print(f"✅ Created {len(created_agent_ids)} agents total")
    return len(created_agent_ids) > 0

def get_current_conversation_state():
    """Get current conversation state from database"""
    print("\n📊 Getting current conversation state...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        # Get all conversations
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            conversations = response.json()
            
            total_messages = 0
            conversation_count = len(conversations)
            
            print(f"📈 Current state:")
            print(f"  - Total conversations: {conversation_count}")
            
            # Analyze message distribution
            agent_message_counts = {}
            recent_messages = []
            
            for conv in conversations:
                messages = conv.get("messages", [])
                total_messages += len(messages)
                
                # Track messages per agent
                for msg in messages:
                    agent_name = msg.get("agent_name", "Unknown")
                    if agent_name not in agent_message_counts:
                        agent_message_counts[agent_name] = 0
                    agent_message_counts[agent_name] += 1
                
                # Collect recent messages for pattern analysis
                if len(messages) > 0:
                    recent_messages.extend(messages[-5:])  # Last 5 messages from each conversation
            
            print(f"  - Total messages: {total_messages}")
            print(f"  - Messages per agent:")
            for agent, count in agent_message_counts.items():
                print(f"    • {agent}: {count} messages")
            
            # Analyze recent message patterns
            print(f"\n🔍 Recent message pattern analysis:")
            consecutive_patterns = analyze_consecutive_messages(recent_messages[-20:])  # Last 20 messages
            
            return {
                "conversation_count": conversation_count,
                "total_messages": total_messages,
                "agent_message_counts": agent_message_counts,
                "consecutive_patterns": consecutive_patterns
            }
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversation state: {e}")
        return None

def analyze_consecutive_messages(messages):
    """Analyze consecutive message patterns to identify the 3-messages-in-a-row issue"""
    if not messages:
        return {}
    
    consecutive_counts = {}
    current_agent = None
    current_count = 0
    max_consecutive = {}
    
    for msg in messages:
        agent_name = msg.get("agent_name", "Unknown")
        
        if agent_name == current_agent:
            current_count += 1
        else:
            if current_agent and current_count > 1:
                if current_agent not in consecutive_counts:
                    consecutive_counts[current_agent] = []
                consecutive_counts[current_agent].append(current_count)
                
                if current_agent not in max_consecutive or current_count > max_consecutive[current_agent]:
                    max_consecutive[current_agent] = current_count
            
            current_agent = agent_name
            current_count = 1
    
    # Handle the last sequence
    if current_agent and current_count > 1:
        if current_agent not in consecutive_counts:
            consecutive_counts[current_agent] = []
        consecutive_counts[current_agent].append(current_count)
        
        if current_agent not in max_consecutive or current_count > max_consecutive[current_agent]:
            max_consecutive[current_agent] = current_count
    
    print(f"  - Consecutive message patterns found:")
    for agent, sequences in consecutive_counts.items():
        print(f"    • {agent}: {sequences} (max: {max_consecutive.get(agent, 1)})")
    
    return {
        "consecutive_counts": consecutive_counts,
        "max_consecutive": max_consecutive
    }

def test_single_conversation_generation():
    """Test a single conversation generation call to see exactly what it returns"""
    print("\n🧪 Testing single conversation generation...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get state before generation
    before_state = get_current_conversation_state()
    
    try:
        print("📤 Calling /api/conversation/generate...")
        start_time = time.time()
        
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️ Response time: {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Response structure:")
            print(f"  - Keys: {list(result.keys())}")
            
            conversation = result.get("conversation", {})
            if conversation:
                messages = conversation.get("messages", [])
                print(f"  - Messages generated: {len(messages)}")
                print(f"  - Conversation ID: {conversation.get('id', 'N/A')}")
                print(f"  - Round number: {conversation.get('round_number', 'N/A')}")
                print(f"  - Time period: {conversation.get('time_period', 'N/A')}")
                
                # Analyze message distribution in this single generation
                agent_counts = {}
                for msg in messages:
                    agent_name = msg.get("agent_name", "Unknown")
                    if agent_name not in agent_counts:
                        agent_counts[agent_name] = 0
                    agent_counts[agent_name] += 1
                
                print(f"  - Messages per agent in this generation:")
                for agent, count in agent_counts.items():
                    print(f"    • {agent}: {count} messages")
                
                # Check for consecutive messages from same agent
                consecutive_issues = []
                prev_agent = None
                consecutive_count = 0
                
                for i, msg in enumerate(messages):
                    agent_name = msg.get("agent_name", "Unknown")
                    if agent_name == prev_agent:
                        consecutive_count += 1
                    else:
                        if consecutive_count > 0:
                            consecutive_issues.append(f"{prev_agent}: {consecutive_count + 1} consecutive messages")
                        consecutive_count = 0
                        prev_agent = agent_name
                
                if consecutive_count > 0:
                    consecutive_issues.append(f"{prev_agent}: {consecutive_count + 1} consecutive messages")
                
                if consecutive_issues:
                    print(f"  ⚠️ CONSECUTIVE MESSAGE ISSUES FOUND:")
                    for issue in consecutive_issues:
                        print(f"    • {issue}")
                else:
                    print(f"  ✅ No consecutive message issues in this generation")
            
            # Get state after generation
            print("\n📊 Checking state after generation...")
            after_state = get_current_conversation_state()
            
            if before_state and after_state:
                message_diff = after_state["total_messages"] - before_state["total_messages"]
                conv_diff = after_state["conversation_count"] - before_state["conversation_count"]
                
                print(f"📈 Changes:")
                print(f"  - Conversations added: {conv_diff}")
                print(f"  - Messages added: {message_diff}")
                
                if message_diff != len(messages):
                    print(f"  ⚠️ MISMATCH: API returned {len(messages)} messages but database shows {message_diff} new messages")
                else:
                    print(f"  ✅ Message count matches between API response and database")
            
            return True
        else:
            print(f"❌ Conversation generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversation generation: {e}")
        return False

def test_multiple_rapid_generations():
    """Test multiple rapid conversation generations to see if they cause duplication"""
    print("\n🔄 Testing multiple rapid conversation generations...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get initial state
    initial_state = get_current_conversation_state()
    
    num_generations = 3
    generation_results = []
    
    for i in range(num_generations):
        print(f"\n📤 Generation {i+1}/{num_generations}...")
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            end_time = time.time()
            
            result = {
                "generation": i+1,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                conversation = data.get("conversation", {})
                messages = conversation.get("messages", [])
                result["messages_count"] = len(messages)
                result["conversation_id"] = conversation.get("id")
                
                # Check for agent message distribution
                agent_counts = {}
                for msg in messages:
                    agent_name = msg.get("agent_name", "Unknown")
                    agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
                result["agent_distribution"] = agent_counts
                
                print(f"  ✅ Generated {len(messages)} messages")
                print(f"  📊 Agent distribution: {agent_counts}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                result["error"] = response.text
            
            generation_results.append(result)
            
            # Small delay between generations
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error in generation {i+1}: {e}")
            generation_results.append({
                "generation": i+1,
                "success": False,
                "error": str(e)
            })
    
    # Analyze results
    print(f"\n📊 Multiple generation analysis:")
    successful_generations = [r for r in generation_results if r.get("success")]
    
    if successful_generations:
        total_messages_generated = sum(r.get("messages_count", 0) for r in successful_generations)
        avg_response_time = sum(r.get("response_time", 0) for r in successful_generations) / len(successful_generations)
        
        print(f"  - Successful generations: {len(successful_generations)}/{num_generations}")
        print(f"  - Total messages generated: {total_messages_generated}")
        print(f"  - Average response time: {avg_response_time:.2f} seconds")
        
        # Check for consistency in agent distribution
        agent_distributions = [r.get("agent_distribution", {}) for r in successful_generations]
        print(f"  - Agent distributions per generation:")
        for i, dist in enumerate(agent_distributions):
            print(f"    Generation {i+1}: {dist}")
    
    # Get final state and compare
    final_state = get_current_conversation_state()
    
    if initial_state and final_state:
        total_message_diff = final_state["total_messages"] - initial_state["total_messages"]
        total_conv_diff = final_state["conversation_count"] - initial_state["conversation_count"]
        
        print(f"\n📈 Overall changes:")
        print(f"  - Conversations added: {total_conv_diff}")
        print(f"  - Messages added: {total_message_diff}")
        
        expected_messages = sum(r.get("messages_count", 0) for r in successful_generations)
        if total_message_diff != expected_messages:
            print(f"  ⚠️ MISMATCH: Expected {expected_messages} messages but database shows {total_message_diff}")
        else:
            print(f"  ✅ Message count matches expectations")
    
    return generation_results

def test_simulation_control_and_generation():
    """Test simulation start/stop/pause functionality and its effect on conversation generation"""
    print("\n⚙️ Testing simulation control and conversation generation...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get initial state
    print("📊 Getting initial simulation state...")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        if response.status_code == 200:
            initial_sim_state = response.json()
            print(f"  - Current day: {initial_sim_state.get('current_day')}")
            print(f"  - Current time period: {initial_sim_state.get('current_time_period')}")
            print(f"  - Is active: {initial_sim_state.get('is_active')}")
        else:
            print(f"❌ Failed to get simulation state: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting simulation state: {e}")
        return False
    
    # Test simulation start
    print("\n▶️ Starting simulation...")
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if response.status_code == 200:
            print("✅ Simulation started successfully")
        else:
            print(f"❌ Failed to start simulation: {response.status_code}")
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
    
    # Generate some conversations while active
    print("\n🔄 Generating conversations while simulation is active...")
    active_state = get_current_conversation_state()
    
    # Generate 2 conversations
    for i in range(2):
        print(f"  📤 Generation {i+1}/2...")
        try:
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            if response.status_code == 200:
                data = response.json()
                messages = data.get("conversation", {}).get("messages", [])
                print(f"    ✅ Generated {len(messages)} messages")
            else:
                print(f"    ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
        time.sleep(1)
    
    # Test simulation pause
    print("\n⏸️ Pausing simulation...")
    try:
        response = requests.post(f"{API_URL}/simulation/pause", headers=headers)
        if response.status_code == 200:
            print("✅ Simulation paused successfully")
            
            # Check state after pause
            paused_state = get_current_conversation_state()
            if active_state and paused_state:
                message_diff = paused_state["total_messages"] - active_state["total_messages"]
                print(f"  📊 Messages added during active period: {message_diff}")
        else:
            print(f"❌ Failed to pause simulation: {response.status_code}")
    except Exception as e:
        print(f"❌ Error pausing simulation: {e}")
    
    # Try to generate conversation while paused
    print("\n🚫 Testing conversation generation while paused...")
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        if response.status_code == 200:
            data = response.json()
            messages = data.get("conversation", {}).get("messages", [])
            print(f"  ⚠️ Generated {len(messages)} messages while paused (unexpected)")
        else:
            print(f"  ✅ Conversation generation blocked while paused (expected)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test simulation resume
    print("\n▶️ Resuming simulation...")
    try:
        response = requests.post(f"{API_URL}/simulation/resume", headers=headers)
        if response.status_code == 200:
            print("✅ Simulation resumed successfully")
            
            # Generate conversation after resume
            print("  📤 Testing generation after resume...")
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            if response.status_code == 200:
                data = response.json()
                messages = data.get("conversation", {}).get("messages", [])
                print(f"    ✅ Generated {len(messages)} messages after resume")
            else:
                print(f"    ❌ Failed to generate after resume: {response.status_code}")
        else:
            print(f"❌ Failed to resume simulation: {response.status_code}")
    except Exception as e:
        print(f"❌ Error resuming simulation: {e}")
    
    # Final state check
    print("\n📊 Final simulation state check...")
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        if response.status_code == 200:
            final_sim_state = response.json()
            print(f"  - Current day: {final_sim_state.get('current_day')}")
            print(f"  - Current time period: {final_sim_state.get('current_time_period')}")
            print(f"  - Is active: {final_sim_state.get('is_active')}")
            
            # Check for time progression
            if (initial_sim_state.get('current_day') != final_sim_state.get('current_day') or 
                initial_sim_state.get('current_time_period') != final_sim_state.get('current_time_period')):
                print(f"  ✅ Time progression detected")
            else:
                print(f"  ⚠️ No time progression detected")
        else:
            print(f"❌ Failed to get final simulation state: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting final simulation state: {e}")
    
    return True

def test_background_processes():
    """Test for background processes that might be generating duplicate messages"""
    print("\n🔍 Testing for background processes and async tasks...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get initial state
    initial_state = get_current_conversation_state()
    
    # Wait and monitor for any background activity
    print("⏳ Monitoring for background activity (30 seconds)...")
    
    for i in range(6):  # Check every 5 seconds for 30 seconds
        time.sleep(5)
        current_state = get_current_conversation_state()
        
        if initial_state and current_state:
            message_diff = current_state["total_messages"] - initial_state["total_messages"]
            conv_diff = current_state["conversation_count"] - initial_state["conversation_count"]
            
            if message_diff > 0 or conv_diff > 0:
                print(f"  ⚠️ Background activity detected at {(i+1)*5}s:")
                print(f"    - Messages added: {message_diff}")
                print(f"    - Conversations added: {conv_diff}")
            else:
                print(f"  ✅ No background activity at {(i+1)*5}s")
        
        initial_state = current_state
    
    print("✅ Background monitoring completed")
    
    # Check for any auto-generation endpoints or scheduled tasks
    print("\n🔍 Checking for auto-generation endpoints...")
    
    # Test if there's an auto-generation endpoint
    try:
        response = requests.post(f"{API_URL}/conversation/auto-generate", headers=headers)
        if response.status_code != 404:
            print(f"  ⚠️ Auto-generation endpoint exists: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    Response: {data}")
        else:
            print(f"  ✅ No auto-generation endpoint found")
    except Exception as e:
        print(f"  ✅ No auto-generation endpoint (error: {e})")
    
    # Check for contextual message endpoint
    try:
        response = requests.post(f"{API_URL}/conversation/add-contextual-message", headers=headers)
        if response.status_code != 404:
            print(f"  ⚠️ Contextual message endpoint exists: {response.status_code}")
        else:
            print(f"  ✅ No contextual message endpoint found")
    except Exception as e:
        print(f"  ✅ No contextual message endpoint (error: {e})")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Delete created agents
    for agent_id in created_agent_ids:
        try:
            response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
            if response.status_code == 200:
                print(f"✅ Deleted agent {agent_id}")
            else:
                print(f"❌ Failed to delete agent {agent_id}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error deleting agent {agent_id}: {e}")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution"""
    print("🔍 CONVERSATION GENERATION DEBUGGING TEST")
    print("=" * 80)
    print("Investigating reported issues:")
    print("1. Agents generating 3 messages in a row instead of 1 message per agent")
    print("2. Messages stopped generating at 81 messages")
    print("3. Stop button issues and sudden jump to 104 messages")
    print("4. No time progression from Day 1 Evening to Day 2 Morning")
    print("=" * 80)
    
    # Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return False
    
    # Create test agents
    if not create_test_agents():
        print("❌ Failed to create test agents. Cannot proceed with conversation tests.")
        return False
    
    try:
        # Run investigation tests
        print("\n" + "=" * 80)
        print("🧪 INVESTIGATION TEST SUITE")
        print("=" * 80)
        
        # Test 1: Single conversation generation
        print("\n1️⃣ SINGLE CONVERSATION GENERATION TEST")
        test_single_conversation_generation()
        
        # Test 2: Multiple rapid generations
        print("\n2️⃣ MULTIPLE RAPID GENERATION TEST")
        test_multiple_rapid_generations()
        
        # Test 3: Simulation control and generation
        print("\n3️⃣ SIMULATION CONTROL TEST")
        test_simulation_control_and_generation()
        
        # Test 4: Background processes
        print("\n4️⃣ BACKGROUND PROCESS TEST")
        test_background_processes()
        
        # Final state analysis
        print("\n" + "=" * 80)
        print("📊 FINAL STATE ANALYSIS")
        print("=" * 80)
        final_state = get_current_conversation_state()
        
        if final_state:
            print(f"Final conversation count: {final_state['conversation_count']}")
            print(f"Final message count: {final_state['total_messages']}")
            print(f"Agent message distribution: {final_state['agent_message_counts']}")
            
            # Check for the specific issues reported
            consecutive_patterns = final_state.get('consecutive_patterns', {})
            max_consecutive = consecutive_patterns.get('max_consecutive', {})
            
            print(f"\n🔍 ISSUE ANALYSIS:")
            
            # Issue 1: 3 messages in a row
            three_plus_consecutive = {agent: count for agent, count in max_consecutive.items() if count >= 3}
            if three_plus_consecutive:
                print(f"  ❌ ISSUE CONFIRMED: Agents with 3+ consecutive messages:")
                for agent, count in three_plus_consecutive.items():
                    print(f"    • {agent}: {count} consecutive messages")
            else:
                print(f"  ✅ No agents with 3+ consecutive messages found")
            
            # Issue 2: Message count analysis
            if final_state['total_messages'] > 80:
                print(f"  ⚠️ Message count ({final_state['total_messages']}) exceeds reported stopping point (81)")
            else:
                print(f"  ✅ Message count ({final_state['total_messages']}) within expected range")
        
    finally:
        # Cleanup
        cleanup_test_data()
    
    print("\n" + "=" * 80)
    print("🏁 DEBUGGING TEST COMPLETED")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
Conversation Generation Debug Test
==================================

This script tests the complete conversation generation flow to debug why conversations
are not being generated when the simulation starts.

Test Flow:
1. Authenticate as guest user
2. Create test agents (at least 2) via POST /api/agents
3. Start simulation via POST /api/simulation/start
4. Generate conversation via POST /api/conversation/generate
5. Check conversations via GET /api/conversations

This will help identify where the conversation generation is failing.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def test_guest_authentication():
    """Test guest authentication"""
    print("\n🔐 Testing Guest Authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_info = data.get('user', {})
            
            if token and user_info.get('id'):
                log_test("Guest Authentication", True, f"User ID: {user_info.get('id')}")
                return token, user_info.get('id')
            else:
                log_test("Guest Authentication", False, "Missing token or user ID in response")
                return None, None
        else:
            log_test("Guest Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
            return None, None
            
    except Exception as e:
        log_test("Guest Authentication", False, f"Exception: {str(e)}")
        return None, None

def test_create_agents(token, user_id):
    """Create test agents for conversation generation"""
    print("\n🤖 Creating Test Agents...")
    
    headers = {"Authorization": f"Bearer {token}"}
    created_agents = []
    
    # Agent 1: Scientist
    agent1_data = {
        "name": "Dr. Sarah Chen",
        "archetype": "scientist",
        "personality": {
            "extroversion": 4,
            "optimism": 6,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": "Advance quantum computing research",
        "expertise": "Quantum Physics and Computing",
        "background": "PhD in Quantum Physics from MIT, 10 years research experience",
        "avatar_prompt": "Professional scientist in lab coat"
    }
    
    # Agent 2: Leader
    agent2_data = {
        "name": "Marcus Johnson",
        "archetype": "leader",
        "personality": {
            "extroversion": 9,
            "optimism": 8,
            "curiosity": 6,
            "cooperativeness": 8,
            "energy": 8
        },
        "goal": "Lead successful project implementations",
        "expertise": "Project Management and Leadership",
        "background": "MBA from Harvard, 15 years in tech leadership",
        "avatar_prompt": "Professional business leader in suit"
    }
    
    # Agent 3: Artist (for variety)
    agent3_data = {
        "name": "Elena Rodriguez",
        "archetype": "artist",
        "personality": {
            "extroversion": 6,
            "optimism": 7,
            "curiosity": 8,
            "cooperativeness": 6,
            "energy": 7
        },
        "goal": "Create innovative user experiences",
        "expertise": "UX Design and Creative Direction",
        "background": "Design degree from RISD, 8 years in tech design",
        "avatar_prompt": "Creative designer with artistic flair"
    }
    
    agents_to_create = [agent1_data, agent2_data, agent3_data]
    
    for i, agent_data in enumerate(agents_to_create, 1):
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                agent = response.json()
                created_agents.append(agent)
                log_test(f"Create Agent {i} ({agent_data['name']})", True, f"Agent ID: {agent.get('id')}")
            else:
                log_test(f"Create Agent {i} ({agent_data['name']})", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            log_test(f"Create Agent {i} ({agent_data['name']})", False, f"Exception: {str(e)}")
    
    return created_agents

def test_simulation_start(token):
    """Test starting the simulation"""
    print("\n▶️ Testing Simulation Start...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # First, set a scenario
        scenario_data = {
            "scenario": "The team is working on a breakthrough quantum computing project with a tight deadline. They need to collaborate to solve technical challenges and make critical decisions.",
            "scenario_name": "Quantum Computing Project"
        }
        
        scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        
        if scenario_response.status_code == 200:
            log_test("Set Scenario", True, "Scenario set successfully")
        else:
            log_test("Set Scenario", False, f"Status: {scenario_response.status_code}, Response: {scenario_response.text}")
        
        # Now start the simulation
        start_data = {
            "time_limit_hours": None  # No time limit for testing
        }
        
        response = requests.post(f"{API_URL}/simulation/start", json=start_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Start Simulation", True, f"Simulation started: {data.get('message', 'No message')}")
            return True
        else:
            log_test("Start Simulation", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Start Simulation", False, f"Exception: {str(e)}")
        return False

def test_simulation_state(token):
    """Check simulation state"""
    print("\n📊 Checking Simulation State...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
        
        if response.status_code == 200:
            state = response.json()
            is_active = state.get('is_active', False)
            scenario = state.get('scenario', 'No scenario')
            
            log_test("Get Simulation State", True, f"Active: {is_active}, Scenario: {scenario[:50]}...")
            return state
        else:
            log_test("Get Simulation State", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Get Simulation State", False, f"Exception: {str(e)}")
        return None

def test_conversation_generation(token):
    """Test conversation generation"""
    print("\n💬 Testing Conversation Generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            conversation = data.get('conversation')
            
            if conversation and conversation.get('messages'):
                message_count = len(conversation['messages'])
                log_test("Generate Conversation", True, f"Generated {message_count} messages")
                
                # Show first few messages for debugging
                print("   📝 Sample messages:")
                for i, msg in enumerate(conversation['messages'][:3]):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_text = msg.get('message', '')[:100]
                    print(f"      {i+1}. {agent_name}: {message_text}...")
                
                return conversation
            else:
                log_test("Generate Conversation", False, "No conversation or messages in response")
                return None
        else:
            log_test("Generate Conversation", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Generate Conversation", False, f"Exception: {str(e)}")
        return None

def test_get_conversations(token):
    """Test retrieving conversations"""
    print("\n📚 Testing Get Conversations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=10)
        
        if response.status_code == 200:
            conversations = response.json()
            
            if isinstance(conversations, list):
                count = len(conversations)
                log_test("Get Conversations", True, f"Retrieved {count} conversations")
                
                if count > 0:
                    # Show details of the most recent conversation
                    latest = conversations[0]
                    round_num = latest.get('round_number', 'Unknown')
                    message_count = len(latest.get('messages', []))
                    scenario_name = latest.get('scenario_name', 'No name')
                    
                    print(f"   📄 Latest conversation: Round {round_num}, {message_count} messages, Scenario: {scenario_name}")
                
                return conversations
            else:
                log_test("Get Conversations", False, f"Expected list, got: {type(conversations)}")
                return None
        else:
            log_test("Get Conversations", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Get Conversations", False, f"Exception: {str(e)}")
        return None

def test_agents_list(token):
    """Test getting agents list to verify they exist"""
    print("\n👥 Testing Get Agents List...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        
        if response.status_code == 200:
            agents = response.json()
            
            if isinstance(agents, list):
                count = len(agents)
                log_test("Get Agents List", True, f"Found {count} agents")
                
                if count >= 2:
                    print("   🤖 Agents available for conversation:")
                    for agent in agents:
                        name = agent.get('name', 'Unknown')
                        archetype = agent.get('archetype', 'Unknown')
                        print(f"      - {name} ({archetype})")
                    return agents
                else:
                    log_test("Insufficient Agents", False, f"Need at least 2 agents, found {count}")
                    return agents
            else:
                log_test("Get Agents List", False, f"Expected list, got: {type(agents)}")
                return None
        else:
            log_test("Get Agents List", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Get Agents List", False, f"Exception: {str(e)}")
        return None

def cleanup_test_data(token, created_agents):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Delete created agents
    for agent in created_agents:
        agent_id = agent.get('id')
        if agent_id:
            try:
                response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Deleted agent: {agent.get('name', 'Unknown')}")
                else:
                    print(f"   ❌ Failed to delete agent {agent.get('name', 'Unknown')}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting agent {agent.get('name', 'Unknown')}: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Starting Conversation Generation Debug Test")
    print("=" * 60)
    
    # Step 1: Authenticate as guest user
    token, user_id = test_guest_authentication()
    if not token:
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Create test agents (at least 2)
    created_agents = test_create_agents(token, user_id)
    if len(created_agents) < 2:
        print(f"\n❌ Need at least 2 agents for conversation generation. Created: {len(created_agents)}")
        return
    
    # Step 2.5: Verify agents exist
    agents_list = test_agents_list(token)
    if not agents_list or len(agents_list) < 2:
        print("\n❌ Insufficient agents available for conversation generation.")
        cleanup_test_data(token, created_agents)
        return
    
    # Step 3: Start simulation
    simulation_started = test_simulation_start(token)
    if not simulation_started:
        print("\n❌ Simulation failed to start. Cannot proceed with conversation generation.")
        cleanup_test_data(token, created_agents)
        return
    
    # Step 3.5: Check simulation state
    sim_state = test_simulation_state(token)
    if not sim_state or not sim_state.get('is_active'):
        print("\n❌ Simulation is not active. Cannot generate conversations.")
        cleanup_test_data(token, created_agents)
        return
    
    # Step 4: Generate conversation
    conversation = test_conversation_generation(token)
    if not conversation:
        print("\n❌ Conversation generation failed.")
        cleanup_test_data(token, created_agents)
        return
    
    # Step 5: Check conversations
    conversations = test_get_conversations(token)
    if not conversations:
        print("\n❌ Failed to retrieve conversations.")
        cleanup_test_data(token, created_agents)
        return
    
    # Clean up
    cleanup_test_data(token, created_agents)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {test_results['passed']/(test_results['passed']+test_results['failed'])*100:.1f}%")
    
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"   - {test['name']}: {test['details']}")
    
    print("\n🎯 CONVERSATION GENERATION FLOW ANALYSIS:")
    if test_results['passed'] >= 8:  # Most tests passed
        print("✅ The conversation generation flow appears to be working correctly.")
        print("   If users report issues, check:")
        print("   - Frontend JavaScript errors")
        print("   - Network connectivity issues")
        print("   - Browser console for API call failures")
    else:
        print("❌ Issues found in the conversation generation flow.")
        print("   Priority fixes needed for conversation generation to work properly.")

if __name__ == "__main__":
    main()