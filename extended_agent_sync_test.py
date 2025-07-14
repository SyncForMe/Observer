#!/usr/bin/env python3
"""
Extended Agent Synchronization Test
Tests edge cases and multiple scenarios for agent synchronization between Agent Library and Observatory.
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
API_URL = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "dino@cytonic.com"
TEST_PASSWORD = "Observerinho8"

def authenticate():
    """Authenticate and return token"""
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_multiple_agent_creation_and_retrieval():
    """Test creating multiple agents and ensuring they all appear in GET /api/agents"""
    print("\n🔄 Testing Multiple Agent Creation and Retrieval...")
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    created_agents = []
    
    # Create 3 different agents
    agents_to_create = [
        {
            "name": "Dr. Maria Rodriguez",
            "archetype": "scientist",
            "goal": "Develop sustainable energy solutions",
            "expertise": "Renewable Energy Engineering",
            "background": "PhD in Energy Systems, 15 years experience"
        },
        {
            "name": "Alex Thompson",
            "archetype": "leader",
            "goal": "Lead innovative tech projects",
            "expertise": "Project Management and Strategy",
            "background": "MBA, 12 years in tech leadership"
        },
        {
            "name": "Dr. James Wilson",
            "archetype": "skeptic",
            "goal": "Ensure rigorous analysis and risk assessment",
            "expertise": "Risk Analysis and Quality Assurance",
            "background": "PhD in Statistics, former NASA quality engineer"
        }
    ]
    
    # Create agents
    for agent_data in agents_to_create:
        agent_data["personality"] = {
            "extroversion": 6, "optimism": 7, "curiosity": 8,
            "cooperativeness": 7, "energy": 6
        }
        
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        if response.status_code == 200:
            agent_id = response.json()["id"]
            created_agents.append(agent_id)
            print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
            return False
    
    # Retrieve all agents
    response = requests.get(f"{API_URL}/agents", headers=headers)
    if response.status_code == 200:
        all_agents = response.json()
        retrieved_agent_ids = [agent["id"] for agent in all_agents]
        
        # Check if all created agents are in the retrieved list
        all_found = all(agent_id in retrieved_agent_ids for agent_id in created_agents)
        
        if all_found:
            print(f"✅ All {len(created_agents)} created agents found in GET /api/agents")
            print(f"   Total agents in system: {len(all_agents)}")
        else:
            print(f"❌ Not all created agents found in GET /api/agents")
            return False
    else:
        print(f"❌ Failed to retrieve agents: {response.status_code}")
        return False
    
    # Clean up - delete created agents
    for agent_id in created_agents:
        delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
        if delete_response.status_code == 200:
            print(f"✅ Cleaned up agent: {agent_id}")
        else:
            print(f"⚠️ Failed to clean up agent: {agent_id}")
    
    return True

def test_user_isolation():
    """Test that agents are properly isolated by user_id"""
    print("\n🔒 Testing User Isolation...")
    
    # Test with main user
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get initial agent count
    response = requests.get(f"{API_URL}/agents", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get initial agent count")
        return False
    
    initial_count = len(response.json())
    print(f"📊 Initial agent count for user: {initial_count}")
    
    # Create an agent
    agent_data = {
        "name": "Test Isolation Agent",
        "archetype": "scientist",
        "goal": "Test user isolation",
        "expertise": "Testing",
        "background": "Test agent for isolation testing",
        "personality": {
            "extroversion": 5, "optimism": 5, "curiosity": 5,
            "cooperativeness": 5, "energy": 5
        }
    }
    
    response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to create test agent")
        return False
    
    created_agent_id = response.json()["id"]
    print(f"✅ Created test agent: {created_agent_id}")
    
    # Verify agent count increased by 1
    response = requests.get(f"{API_URL}/agents", headers=headers)
    if response.status_code == 200:
        new_count = len(response.json())
        if new_count == initial_count + 1:
            print(f"✅ Agent count correctly increased to {new_count}")
        else:
            print(f"❌ Expected {initial_count + 1} agents, got {new_count}")
            return False
    else:
        print("❌ Failed to verify agent count")
        return False
    
    # Test guest user isolation
    guest_response = requests.post(f"{API_URL}/auth/guest")
    if guest_response.status_code == 200:
        guest_token = guest_response.json()["access_token"]
        guest_headers = {"Authorization": f"Bearer {guest_token}"}
        
        # Guest should have different agents
        guest_agents_response = requests.get(f"{API_URL}/agents", headers=guest_headers)
        if guest_agents_response.status_code == 200:
            guest_agents = guest_agents_response.json()
            guest_agent_ids = [agent["id"] for agent in guest_agents]
            
            if created_agent_id not in guest_agent_ids:
                print("✅ User isolation working - guest cannot see main user's agents")
            else:
                print("❌ User isolation failed - guest can see main user's agents")
                return False
        else:
            print("⚠️ Could not test guest isolation due to API error")
    else:
        print("⚠️ Could not create guest user for isolation test")
    
    # Clean up
    delete_response = requests.delete(f"{API_URL}/agents/{created_agent_id}", headers=headers)
    if delete_response.status_code == 200:
        print(f"✅ Cleaned up test agent")
    else:
        print(f"⚠️ Failed to clean up test agent")
    
    return True

def test_conversation_generation_with_specific_agents():
    """Test that conversation generation uses exactly the user's agents"""
    print("\n💬 Testing Conversation Generation with Specific Agents...")
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create 2 specific agents for testing
    test_agents = [
        {
            "name": "Dr. Quantum Alice",
            "archetype": "scientist",
            "goal": "Advance quantum computing",
            "expertise": "Quantum Physics",
            "background": "Leading quantum researcher"
        },
        {
            "name": "Bob the Builder",
            "archetype": "leader",
            "goal": "Build amazing things",
            "expertise": "Construction Management",
            "background": "Expert builder and project manager"
        }
    ]
    
    created_agent_ids = []
    
    for agent_data in test_agents:
        agent_data["personality"] = {
            "extroversion": 7, "optimism": 8, "curiosity": 9,
            "cooperativeness": 8, "energy": 7
        }
        
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        if response.status_code == 200:
            agent_id = response.json()["id"]
            created_agent_ids.append(agent_id)
            print(f"✅ Created test agent: {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
            return False
    
    # Set up simulation
    scenario_data = {
        "scenario": "Quantum computing project planning meeting",
        "scenario_name": "Quantum Project Planning"
    }
    
    scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
    if scenario_response.status_code != 200:
        print(f"❌ Failed to set scenario: {scenario_response.status_code}")
        return False
    
    # Start simulation
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code != 200:
        print(f"❌ Failed to start simulation: {start_response.status_code}")
        return False
    
    # Generate conversation
    conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    
    if conversation_response.status_code == 200:
        conversation_data = conversation_response.json()
        
        if "messages" in conversation_data:
            messages = conversation_data["messages"]
            participating_agents = set()
            
            for message in messages:
                if "agent_name" in message:
                    participating_agents.add(message["agent_name"])
            
            # Check if our specific test agents participated
            expected_names = {"Dr. Quantum Alice", "Bob the Builder"}
            found_names = participating_agents.intersection(expected_names)
            
            if len(found_names) >= 2:
                print(f"✅ Conversation generated with expected agents: {found_names}")
            else:
                print(f"❌ Expected agents not found in conversation. Found: {participating_agents}")
                return False
        else:
            print("❌ Conversation response missing messages")
            return False
    else:
        print(f"❌ Conversation generation failed: {conversation_response.status_code}")
        return False
    
    # Clean up
    for agent_id in created_agent_ids:
        delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
        if delete_response.status_code == 200:
            print(f"✅ Cleaned up agent: {agent_id}")
        else:
            print(f"⚠️ Failed to clean up agent: {agent_id}")
    
    return True

def test_agent_persistence_across_operations():
    """Test that agents persist across various operations"""
    print("\n🔄 Testing Agent Persistence Across Operations...")
    
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a test agent
    agent_data = {
        "name": "Persistent Test Agent",
        "archetype": "scientist",
        "goal": "Test persistence",
        "expertise": "Persistence Testing",
        "background": "Agent for testing persistence across operations",
        "personality": {
            "extroversion": 5, "optimism": 5, "curiosity": 5,
            "cooperativeness": 5, "energy": 5
        }
    }
    
    response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to create test agent")
        return False
    
    agent_id = response.json()["id"]
    print(f"✅ Created persistent test agent: {agent_id}")
    
    # Test persistence across different operations
    operations = [
        ("set scenario", lambda: requests.post(f"{API_URL}/simulation/set-scenario", 
                                             json={"scenario": "Test scenario", "scenario_name": "Test"}, 
                                             headers=headers)),
        ("start simulation", lambda: requests.post(f"{API_URL}/simulation/start", headers=headers)),
        ("pause simulation", lambda: requests.post(f"{API_URL}/simulation/pause", headers=headers)),
        ("resume simulation", lambda: requests.post(f"{API_URL}/simulation/resume", headers=headers)),
        ("get simulation state", lambda: requests.get(f"{API_URL}/simulation/state", headers=headers))
    ]
    
    for operation_name, operation_func in operations:
        # Perform operation
        op_response = operation_func()
        if op_response.status_code not in [200, 201]:
            print(f"⚠️ Operation '{operation_name}' failed with status {op_response.status_code}")
        
        # Check if agent still exists
        agents_response = requests.get(f"{API_URL}/agents", headers=headers)
        if agents_response.status_code == 200:
            agents = agents_response.json()
            agent_ids = [agent["id"] for agent in agents]
            
            if agent_id in agent_ids:
                print(f"✅ Agent persisted after '{operation_name}'")
            else:
                print(f"❌ Agent lost after '{operation_name}'")
                return False
        else:
            print(f"❌ Failed to check agents after '{operation_name}'")
            return False
    
    # Clean up
    delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
    if delete_response.status_code == 200:
        print(f"✅ Cleaned up persistent test agent")
    else:
        print(f"⚠️ Failed to clean up persistent test agent")
    
    return True

def main():
    """Run extended agent synchronization tests"""
    print("🚀 Starting Extended Agent Synchronization Tests...")
    print(f"API URL: {API_URL}")
    
    tests = [
        ("Multiple Agent Creation and Retrieval", test_multiple_agent_creation_and_retrieval),
        ("User Isolation", test_user_isolation),
        ("Conversation Generation with Specific Agents", test_conversation_generation_with_specific_agents),
        ("Agent Persistence Across Operations", test_agent_persistence_across_operations)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                print(f"✅ PASSED: {test_name}")
                passed += 1
            else:
                print(f"❌ FAILED: {test_name}")
                failed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - Exception: {str(e)}")
            failed += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print("🏁 EXTENDED TEST SUMMARY")
    print('='*60)
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Pass Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("🎉 All extended agent synchronization tests passed!")
        return True
    else:
        print("💥 Some extended tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)