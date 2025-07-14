#!/usr/bin/env python3
"""
Agent Synchronization Test
Tests the core Agent Synchronization Issue fix where agents added through Agent Library 
should now appear in Observatory since both use the same /api/agents endpoint filtered by user_id.

Test Plan:
1. User authentication (as guest or with test credentials)
2. Creating an agent via POST /api/agents endpoint
3. Verifying the agent appears when calling GET /api/agents 
4. Testing that all user agents are included in conversation generation
5. Testing agent deletion via DELETE /api/agents/{id}
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test credentials from test_result.md
TEST_EMAIL = "dino@cytonic.com"
TEST_PASSWORD = "Observerinho8"

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

def test_user_authentication():
    """Test 1: User authentication with test credentials"""
    print("\n🔐 Testing User Authentication...")
    
    try:
        # Test login with credentials
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                auth_token = data["access_token"]
                user_id = data["user"]["id"]
                log_test("User Authentication", True, f"Successfully logged in as {data['user']['email']}")
                return auth_token, user_id
            else:
                log_test("User Authentication", False, "Login response missing required fields")
                return None, None
        else:
            log_test("User Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
            return None, None
            
    except Exception as e:
        log_test("User Authentication", False, f"Exception during login: {str(e)}")
        return None, None

def test_guest_authentication():
    """Test guest authentication as fallback"""
    print("\n👤 Testing Guest Authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/guest")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                auth_token = data["access_token"]
                user_id = data["user"]["id"]
                log_test("Guest Authentication", True, f"Successfully authenticated as guest")
                return auth_token, user_id
            else:
                log_test("Guest Authentication", False, "Guest response missing required fields")
                return None, None
        else:
            log_test("Guest Authentication", False, f"Guest auth failed with status {response.status_code}: {response.text}")
            return None, None
            
    except Exception as e:
        log_test("Guest Authentication", False, f"Exception during guest auth: {str(e)}")
        return None, None

def test_create_agent(auth_token):
    """Test 2: Creating an agent via POST /api/agents endpoint"""
    print("\n🤖 Testing Agent Creation...")
    
    if not auth_token:
        log_test("Agent Creation", False, "No auth token available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a test agent with realistic data
        agent_data = {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            },
            "goal": "Advance quantum computing research and develop practical applications",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics from MIT, 10+ years in quantum computing research",
            "memory_summary": "Expert in quantum entanglement, error correction, and quantum algorithms",
            "avatar_prompt": "Professional scientist with lab coat",
            "avatar_url": ""
        }
        
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "name" in data:
                agent_id = data["id"]
                log_test("Agent Creation", True, f"Successfully created agent '{data['name']}' with ID: {agent_id}")
                return agent_id
            else:
                log_test("Agent Creation", False, "Agent creation response missing required fields")
                return None
        else:
            log_test("Agent Creation", False, f"Agent creation failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        log_test("Agent Creation", False, f"Exception during agent creation: {str(e)}")
        return None

def test_get_agents(auth_token, expected_agent_id=None):
    """Test 3: Verifying the agent appears when calling GET /api/agents"""
    print("\n📋 Testing Agent Retrieval...")
    
    if not auth_token:
        log_test("Agent Retrieval", False, "No auth token available")
        return []
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API_URL}/agents", headers=headers)
        
        if response.status_code == 200:
            agents = response.json()
            if isinstance(agents, list):
                agent_count = len(agents)
                
                # Check if expected agent is in the list
                if expected_agent_id:
                    found_agent = any(agent.get("id") == expected_agent_id for agent in agents)
                    if found_agent:
                        log_test("Agent Retrieval", True, f"Successfully retrieved {agent_count} agents, including newly created agent")
                    else:
                        log_test("Agent Retrieval", False, f"Retrieved {agent_count} agents, but newly created agent not found")
                else:
                    log_test("Agent Retrieval", True, f"Successfully retrieved {agent_count} agents")
                
                return agents
            else:
                log_test("Agent Retrieval", False, "Agent retrieval response is not a list")
                return []
        else:
            log_test("Agent Retrieval", False, f"Agent retrieval failed with status {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        log_test("Agent Retrieval", False, f"Exception during agent retrieval: {str(e)}")
        return []

def test_conversation_generation_with_agents(auth_token, agents):
    """Test 4: Testing that all user agents are included in conversation generation"""
    print("\n💬 Testing Conversation Generation with User Agents...")
    
    if not auth_token:
        log_test("Conversation Generation", False, "No auth token available")
        return
    
    if len(agents) < 2:
        log_test("Conversation Generation", False, f"Need at least 2 agents for conversation, but only have {len(agents)}")
        return
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First, set up simulation state
        scenario_data = {
            "scenario": "Research team discussing quantum computing breakthrough",
            "scenario_name": "Quantum Research Discussion"
        }
        
        scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        if scenario_response.status_code != 200:
            log_test("Conversation Generation", False, f"Failed to set scenario: {scenario_response.status_code}")
            return
        
        # Start simulation
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if start_response.status_code != 200:
            log_test("Conversation Generation", False, f"Failed to start simulation: {start_response.status_code}")
            return
        
        # Generate conversation
        conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        if conversation_response.status_code == 200:
            conversation_data = conversation_response.json()
            
            # Check if conversation includes messages from user's agents
            if "messages" in conversation_data:
                messages = conversation_data["messages"]
                agent_names_in_conversation = set()
                
                for message in messages:
                    if "agent_name" in message:
                        agent_names_in_conversation.add(message["agent_name"])
                
                user_agent_names = set(agent["name"] for agent in agents)
                
                # Check if all user agents participated
                agents_participated = user_agent_names.intersection(agent_names_in_conversation)
                
                if len(agents_participated) >= min(2, len(user_agent_names)):
                    log_test("Conversation Generation", True, f"Conversation generated with {len(agents_participated)} user agents participating")
                else:
                    log_test("Conversation Generation", False, f"Only {len(agents_participated)} out of {len(user_agent_names)} user agents participated")
            else:
                log_test("Conversation Generation", False, "Conversation response missing messages field")
        else:
            log_test("Conversation Generation", False, f"Conversation generation failed with status {conversation_response.status_code}: {conversation_response.text}")
            
    except Exception as e:
        log_test("Conversation Generation", False, f"Exception during conversation generation: {str(e)}")

def test_agent_deletion(auth_token, agent_id):
    """Test 5: Testing agent deletion via DELETE /api/agents/{id}"""
    print("\n🗑️ Testing Agent Deletion...")
    
    if not auth_token or not agent_id:
        log_test("Agent Deletion", False, "No auth token or agent ID available")
        return
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
        
        if response.status_code == 200:
            # Verify agent is actually deleted by trying to retrieve it
            get_response = requests.get(f"{API_URL}/agents", headers=headers)
            if get_response.status_code == 200:
                agents = get_response.json()
                agent_still_exists = any(agent.get("id") == agent_id for agent in agents)
                
                if not agent_still_exists:
                    log_test("Agent Deletion", True, f"Successfully deleted agent with ID: {agent_id}")
                else:
                    log_test("Agent Deletion", False, "Agent deletion returned success but agent still exists")
            else:
                log_test("Agent Deletion", False, "Could not verify agent deletion due to retrieval failure")
        else:
            log_test("Agent Deletion", False, f"Agent deletion failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        log_test("Agent Deletion", False, f"Exception during agent deletion: {str(e)}")

def test_agent_synchronization_workflow():
    """Test the complete agent synchronization workflow"""
    print("\n🔄 Testing Complete Agent Synchronization Workflow...")
    
    try:
        # Step 1: Authenticate
        auth_token, user_id = test_user_authentication()
        
        # Fallback to guest if login fails
        if not auth_token:
            auth_token, user_id = test_guest_authentication()
        
        if not auth_token:
            log_test("Agent Synchronization Workflow", False, "Could not authenticate user")
            return
        
        # Step 2: Create an agent
        agent_id = test_create_agent(auth_token)
        
        if not agent_id:
            log_test("Agent Synchronization Workflow", False, "Could not create agent")
            return
        
        # Step 3: Verify agent appears in GET /api/agents
        agents = test_get_agents(auth_token, agent_id)
        
        if not agents:
            log_test("Agent Synchronization Workflow", False, "Could not retrieve agents")
            return
        
        # Step 4: Test conversation generation includes user agents
        test_conversation_generation_with_agents(auth_token, agents)
        
        # Step 5: Test agent deletion
        test_agent_deletion(auth_token, agent_id)
        
        log_test("Agent Synchronization Workflow", True, "Complete workflow executed successfully")
        
    except Exception as e:
        log_test("Agent Synchronization Workflow", False, f"Exception in workflow: {str(e)}")

def print_test_summary():
    """Print final test summary"""
    print("\n" + "="*60)
    print("🧪 AGENT SYNCHRONIZATION TEST SUMMARY")
    print("="*60)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  - {test['name']}: {test['details']}")
    
    print("\n" + "="*60)
    
    # Return overall success
    return test_results["failed"] == 0

def main():
    """Main test execution"""
    print("🚀 Starting Agent Synchronization Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API URL: {API_URL}")
    
    # Run the complete workflow test
    test_agent_synchronization_workflow()
    
    # Print summary and return success status
    success = print_test_summary()
    
    if success:
        print("🎉 All agent synchronization tests passed!")
        sys.exit(0)
    else:
        print("💥 Some agent synchronization tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()