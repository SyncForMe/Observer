#!/usr/bin/env python3
"""
Debug agent creation to understand the response format
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate():
    """Authenticate with the backend"""
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def debug_agent_creation():
    """Debug agent creation endpoint"""
    print("🔍 DEBUGGING AGENT CREATION ENDPOINT")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test agent creation
    agent_data = {
        "name": "Debug Test Agent",
        "archetype": "scientist",
        "goal": "Test agent creation",
        "expertise": "Testing",
        "background": "Debug test agent",
        "personality": {
            "extroversion": 5,
            "optimism": 5,
            "curiosity": 5,
            "cooperativeness": 5,
            "energy": 5
        }
    }
    
    print("\n1. TESTING AGENT CREATION...")
    print(f"   Endpoint: POST {API_URL}/agents")
    print(f"   Agent data: {json.dumps(agent_data, indent=2)}")
    
    try:
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        
        print(f"\n2. RESPONSE ANALYSIS...")
        print(f"   Status code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Response JSON: {json.dumps(response_data, indent=2)}")
            
            # Check for different possible ID fields
            possible_id_fields = ["id", "agent_id", "_id", "uuid"]
            agent_id = None
            
            for field in possible_id_fields:
                if field in response_data:
                    agent_id = response_data[field]
                    print(f"   Found agent ID in field '{field}': {agent_id}")
                    break
            
            if not agent_id:
                print("   ❌ No agent ID found in response")
                print(f"   Available fields: {list(response_data.keys())}")
            else:
                print(f"   ✅ Agent ID: {agent_id}")
                
                # Try to get the created agent
                print(f"\n3. VERIFYING AGENT CREATION...")
                get_response = requests.get(f"{API_URL}/agents/{agent_id}", headers=headers)
                if get_response.status_code == 200:
                    agent_details = get_response.json()
                    print(f"   ✅ Agent retrieved successfully: {agent_details.get('name', 'Unknown')}")
                    
                    # Clean up
                    delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
                    if delete_response.status_code == 200:
                        print(f"   ✅ Agent deleted successfully")
                    else:
                        print(f"   ❌ Failed to delete agent: {delete_response.status_code}")
                else:
                    print(f"   ❌ Failed to retrieve agent: {get_response.status_code}")
            
        except json.JSONDecodeError:
            print(f"   Response is not JSON: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during agent creation: {e}")
        return False
    
    # Also test getting all agents
    print(f"\n4. TESTING GET ALL AGENTS...")
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            print(f"   ✅ Found {len(agents)} total agents")
            
            if agents:
                sample_agent = agents[0]
                print(f"   Sample agent structure: {json.dumps(sample_agent, indent=2)}")
        else:
            print(f"   ❌ Failed to get agents: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting agents: {e}")

def main():
    """Main debug execution"""
    debug_agent_creation()

if __name__ == "__main__":
    main()