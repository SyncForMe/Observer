#!/usr/bin/env python3
"""
Create the specific agents mentioned by the user and test agent selection
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
API_URL = f"{os.environ.get('REACT_APP_BACKEND_URL')}/api"

def authenticate():
    """Authenticate and get JWT token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user", {}).get("id")
    return None, None

def create_agent(token, name, archetype, goal, expertise, background):
    """Create a specific agent"""
    headers = {"Authorization": f"Bearer {token}"}
    
    agent_data = {
        "name": name,
        "archetype": archetype,
        "personality": {
            "extroversion": 7,
            "optimism": 6,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 7
        },
        "goal": goal,
        "expertise": expertise,
        "background": background,
        "memory_summary": f"I am {name}, ready to contribute to discussions.",
        "avatar_prompt": f"Professional headshot of {name}",
        "avatar_url": ""
    }
    
    response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
    return response.status_code == 200, response.json() if response.status_code == 200 else response.text

def main():
    print("Creating specific agents for testing...")
    
    # Authenticate
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Clear existing agents first
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/agents", headers=headers)
    if response.status_code == 200:
        existing_agents = response.json()
        print(f"Found {len(existing_agents)} existing agents. Deleting them...")
        
        for agent in existing_agents:
            agent_id = agent.get('id')
            if agent_id:
                delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
                if delete_response.status_code == 200:
                    print(f"✅ Deleted agent: {agent.get('name', 'Unknown')}")
                else:
                    print(f"❌ Failed to delete agent: {agent.get('name', 'Unknown')}")
    
    # Create the three specific agents
    agents_to_create = [
        {
            "name": "Darth Vader",
            "archetype": "leader",
            "goal": "Bring order to the galaxy through decisive leadership",
            "expertise": "Strategic planning, leadership, and galactic governance",
            "background": "Former Jedi turned Sith Lord, experienced in commanding vast imperial forces and making difficult strategic decisions."
        },
        {
            "name": "Nikola Tesla",
            "archetype": "scientist",
            "goal": "Advance human understanding through revolutionary scientific discoveries",
            "expertise": "Electrical engineering, physics, and innovative technology development",
            "background": "Brilliant inventor and electrical engineer known for groundbreaking work in alternating current, wireless technology, and electromagnetic fields."
        },
        {
            "name": "Bob Marley",
            "archetype": "optimist",
            "goal": "Spread peace, love, and unity through wisdom and music",
            "expertise": "Philosophy, social harmony, and cultural understanding",
            "background": "Jamaican reggae musician and philosopher who promoted messages of love, unity, and social consciousness through his music and teachings."
        }
    ]
    
    created_agents = []
    for agent_info in agents_to_create:
        success, result = create_agent(token, **agent_info)
        if success:
            print(f"✅ Created agent: {agent_info['name']}")
            created_agents.append(result)
        else:
            print(f"❌ Failed to create agent {agent_info['name']}: {result}")
    
    print(f"\nSuccessfully created {len(created_agents)} agents")
    
    # Verify agents were created
    response = requests.get(f"{API_URL}/agents", headers=headers)
    if response.status_code == 200:
        agents = response.json()
        print(f"\nVerification - Total agents in database: {len(agents)}")
        for agent in agents:
            print(f"  - {agent.get('name', 'NO_NAME')} (ID: {agent.get('id', 'NO_ID')})")
    
    return len(created_agents) == 3

if __name__ == "__main__":
    main()