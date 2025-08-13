#!/usr/bin/env python3
"""
Focused test for conversation generation endpoint - 3 messages per agent
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate():
    """Get auth token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def clean_agents(token):
    """Remove all existing agents"""
    print("🧹 Cleaning up existing agents...")
    
    # Get all agents
    response = requests.get(f"{API_URL}/agents", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        agents = response.json()
        print(f"Found {len(agents)} existing agents")
        
        # Delete each agent
        for agent in agents:
            agent_id = agent.get("id")
            if agent_id:
                delete_response = requests.delete(
                    f"{API_URL}/agents/{agent_id}", 
                    headers={"Authorization": f"Bearer {token}"}
                )
                if delete_response.status_code == 200:
                    print(f"✅ Deleted agent: {agent.get('name', 'Unknown')}")
                else:
                    print(f"❌ Failed to delete agent: {agent.get('name', 'Unknown')}")

def create_test_agents(token):
    """Create exactly 3 test agents"""
    print("\n🤖 Creating test agents...")
    
    agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics",
            "background": "PhD in Quantum Physics from MIT",
            "personality": {
                "extroversion": 6, "optimism": 8, "curiosity": 9, 
                "cooperativeness": 7, "energy": 7
            }
        },
        {
            "name": "Marcus Rodriguez", 
            "archetype": "leader",
            "goal": "Lead team to success",
            "expertise": "Project Management",
            "background": "MBA from Stanford",
            "personality": {
                "extroversion": 9, "optimism": 8, "curiosity": 6,
                "cooperativeness": 8, "energy": 8
            }
        },
        {
            "name": "Dr. Emily Watson",
            "archetype": "skeptic", 
            "goal": "Ensure rigorous analysis",
            "expertise": "Risk Analysis",
            "background": "PhD in Systems Engineering",
            "personality": {
                "extroversion": 4, "optimism": 3, "curiosity": 7,
                "cooperativeness": 5, "energy": 5
            }
        }
    ]
    
    created_agents = []
    for agent_data in agents:
        response = requests.post(
            f"{API_URL}/agents",
            json=agent_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            agent = response.json()
            created_agents.append(agent)
            print(f"✅ Created: {agent_data['name']}")
        else:
            print(f"❌ Failed to create: {agent_data['name']}")
    
    return created_agents

def start_simulation(token):
    """Start simulation"""
    print("\n🚀 Starting simulation...")
    response = requests.post(
        f"{API_URL}/simulation/start",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code == 200

def test_conversation_generation(token):
    """Test conversation generation"""
    print("\n💬 Testing conversation generation...")
    
    start_time = time.time()
    response = requests.post(
        f"{API_URL}/conversation/generate",
        headers={"Authorization": f"Bearer {token}"}
    )
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f}s")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get("messages", [])
        
        print(f"\n📊 CONVERSATION ANALYSIS:")
        print(f"Total messages: {len(messages)}")
        
        # Count messages per agent
        agent_counts = {}
        for message in messages:
            agent_name = message.get("agent_name", "Unknown")
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
        
        print(f"\nMessages per agent:")
        for agent_name, count in agent_counts.items():
            print(f"  - {agent_name}: {count} messages")
        
        # Show first few messages for analysis
        print(f"\nFirst 6 messages:")
        for i, message in enumerate(messages[:6], 1):
            agent_name = message.get("agent_name", "Unknown")
            message_text = message.get("message", "")
            print(f"{i}. {agent_name}: {message_text[:80]}...")
        
        # Analysis
        expected_agents = 3
        expected_total_messages = expected_agents * 3  # 3 messages per agent
        actual_total_messages = len(messages)
        
        print(f"\n🔍 ANALYSIS:")
        print(f"Expected agents: {expected_agents}")
        print(f"Actual agents: {len(agent_counts)}")
        print(f"Expected total messages: {expected_total_messages}")
        print(f"Actual total messages: {actual_total_messages}")
        
        # Check if each agent has exactly 3 messages
        agents_with_3_messages = sum(1 for count in agent_counts.values() if count == 3)
        
        if len(agent_counts) == expected_agents and actual_total_messages == expected_total_messages:
            if agents_with_3_messages == expected_agents:
                print(f"\n✅ SUCCESS: All {expected_agents} agents generated exactly 3 messages each!")
                print(f"✅ Total message count is correct: {actual_total_messages}")
                return True
            else:
                print(f"\n❌ FAILURE: Not all agents generated exactly 3 messages")
                print(f"❌ Agents with 3 messages: {agents_with_3_messages}/{expected_agents}")
        else:
            print(f"\n❌ FAILURE: Incorrect agent count or total message count")
            print(f"❌ Expected {expected_agents} agents with {expected_total_messages} total messages")
            print(f"❌ Got {len(agent_counts)} agents with {actual_total_messages} total messages")
        
        return False
    else:
        print(f"❌ Conversation generation failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    print("🧪 FOCUSED CONVERSATION GENERATION TEST")
    print("Testing 3 messages per agent functionality")
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Clean up existing agents
    clean_agents(token)
    
    # Create test agents
    agents = create_test_agents(token)
    if len(agents) != 3:
        print(f"❌ Expected 3 agents, got {len(agents)}")
        return
    
    # Start simulation
    if not start_simulation(token):
        print("❌ Failed to start simulation")
        return
    
    print("✅ Simulation started")
    
    # Test conversation generation
    success = test_conversation_generation(token)
    
    if success:
        print("\n🎉 TEST PASSED: 3 messages per agent functionality is working!")
    else:
        print("\n❌ TEST FAILED: 3 messages per agent functionality has issues")

if __name__ == "__main__":
    main()