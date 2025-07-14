#!/usr/bin/env python3
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