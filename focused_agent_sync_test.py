#!/usr/bin/env python3
"""
Focused Agent Synchronization Test

This test specifically focuses on the core synchronization issue:
- Create agent via POST /api/agents
- Immediately fetch via GET /api/agents
- Verify the agent appears
"""

import requests
import json
import time
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_agent_synchronization():
    """Test the core Agent Library → Observatory synchronization"""
    print("🧪 FOCUSED AGENT SYNCHRONIZATION TEST")
    print("="*60)
    
    # Step 1: Get guest authentication
    print("\n1. Getting guest authentication...")
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return False
    
    auth_data = auth_response.json()
    token = auth_data.get("access_token")
    user_id = auth_data.get("user", {}).get("id")
    
    print(f"✅ Authentication successful")
    print(f"   User ID: {user_id}")
    print(f"   Token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Create a test agent
    print("\n2. Creating test agent...")
    agent_name = f"Sync Test Agent {uuid.uuid4().hex[:8]}"
    
    agent_data = {
        "name": agent_name,
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 8,
            "energy": 6
        },
        "goal": "Test synchronization",
        "expertise": "Testing",
        "background": "Test agent for synchronization",
        "memory_summary": "Created for sync test",
        "avatar_prompt": "Test avatar",
        "avatar_url": ""
    }
    
    create_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    
    print(f"   Status: {create_response.status_code}")
    
    if create_response.status_code not in [200, 201]:
        print(f"❌ Agent creation failed")
        print(f"   Response: {create_response.text}")
        return False
    
    create_data = create_response.json()
    agent_id = create_data.get("id")
    
    print(f"✅ Agent created successfully")
    print(f"   Agent ID: {agent_id}")
    print(f"   Agent Name: {agent_name}")
    
    # Step 3: Immediately fetch agents (Observatory view)
    print("\n3. Fetching agents (Observatory view)...")
    
    fetch_response = requests.get(f"{API_URL}/agents", headers=headers)
    
    if fetch_response.status_code != 200:
        print(f"❌ Failed to fetch agents: {fetch_response.status_code}")
        return False
    
    agents = fetch_response.json()
    agent_count = len(agents)
    
    print(f"✅ Agents fetched successfully")
    print(f"   Total agents: {agent_count}")
    
    # Step 4: Check if created agent appears in the list
    print("\n4. Checking synchronization...")
    
    found_agent = None
    for agent in agents:
        if agent.get("id") == agent_id:
            found_agent = agent
            break
    
    if found_agent:
        print(f"✅ SYNCHRONIZATION SUCCESS!")
        print(f"   Created agent '{agent_name}' appears in Observatory")
        print(f"   Agent details:")
        print(f"     - ID: {found_agent.get('id')}")
        print(f"     - Name: {found_agent.get('name')}")
        print(f"     - User ID: {found_agent.get('user_id')}")
        print(f"     - Created: {found_agent.get('created_at')}")
        
        # Step 5: Verify user association
        if found_agent.get('user_id') == user_id:
            print(f"✅ User association correct")
        else:
            print(f"❌ User association incorrect")
            print(f"   Expected: {user_id}")
            print(f"   Got: {found_agent.get('user_id')}")
        
        # Step 6: Clean up
        print("\n5. Cleaning up...")
        delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
        
        if delete_response.status_code == 200:
            print(f"✅ Test agent deleted successfully")
        else:
            print(f"⚠️ Failed to delete test agent: {delete_response.status_code}")
        
        return True
    else:
        print(f"❌ SYNCHRONIZATION FAILED!")
        print(f"   Created agent '{agent_name}' NOT found in Observatory")
        print(f"   Available agents:")
        for agent in agents:
            print(f"     - {agent.get('name')} (ID: {agent.get('id')})")
        
        # Still try to clean up
        print("\n5. Attempting cleanup...")
        delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
        
        if delete_response.status_code == 200:
            print(f"✅ Test agent deleted successfully")
        else:
            print(f"⚠️ Failed to delete test agent: {delete_response.status_code}")
        
        return False

def test_multiple_agents():
    """Test creating multiple agents and checking synchronization"""
    print("\n" + "="*60)
    print("🧪 MULTIPLE AGENTS SYNCHRONIZATION TEST")
    print("="*60)
    
    # Get authentication
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    auth_data = auth_response.json()
    token = auth_data.get("access_token")
    user_id = auth_data.get("user", {}).get("id")
    headers = {"Authorization": f"Bearer {token}"}
    
    created_agents = []
    
    # Create 3 agents
    for i in range(3):
        agent_name = f"Multi Test Agent {i+1}"
        
        agent_data = {
            "name": agent_name,
            "archetype": "scientist",
            "personality": {
                "extroversion": 5,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 6
            },
            "goal": f"Test agent {i+1}",
            "expertise": "Testing",
            "background": f"Test agent {i+1} for multi-sync test",
            "memory_summary": f"Agent {i+1}",
            "avatar_prompt": "Test avatar",
            "avatar_url": ""
        }
        
        create_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        
        if create_response.status_code in [200, 201]:
            agent_id = create_response.json().get("id")
            created_agents.append({"id": agent_id, "name": agent_name})
            print(f"✅ Created agent {i+1}: {agent_name} (ID: {agent_id})")
        else:
            print(f"❌ Failed to create agent {i+1}")
    
    # Fetch all agents
    fetch_response = requests.get(f"{API_URL}/agents", headers=headers)
    agents = fetch_response.json()
    
    # Check synchronization
    found_count = 0
    for created_agent in created_agents:
        found = any(agent.get("id") == created_agent["id"] for agent in agents)
        if found:
            found_count += 1
            print(f"✅ Agent '{created_agent['name']}' found in Observatory")
        else:
            print(f"❌ Agent '{created_agent['name']}' NOT found in Observatory")
    
    print(f"\nSynchronization Result: {found_count}/{len(created_agents)} agents synchronized")
    
    # Cleanup
    for created_agent in created_agents:
        delete_response = requests.delete(f"{API_URL}/agents/{created_agent['id']}", headers=headers)
        if delete_response.status_code == 200:
            print(f"✅ Deleted {created_agent['name']}")
        else:
            print(f"⚠️ Failed to delete {created_agent['name']}")
    
    return found_count == len(created_agents)

def main():
    """Run all synchronization tests"""
    print("🚀 AGENT LIBRARY → OBSERVATORY SYNCHRONIZATION TESTS")
    print("="*60)
    
    # Test 1: Single agent synchronization
    single_success = test_agent_synchronization()
    
    # Test 2: Multiple agents synchronization
    multiple_success = test_multiple_agents()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    print(f"Single Agent Sync: {'✅ PASS' if single_success else '❌ FAIL'}")
    print(f"Multiple Agents Sync: {'✅ PASS' if multiple_success else '❌ FAIL'}")
    
    if single_success and multiple_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Agent Library → Observatory synchronization is working correctly!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("There are issues with Agent Library → Observatory synchronization.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)