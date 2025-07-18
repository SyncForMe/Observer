#!/usr/bin/env python3
"""
Debug agent response count issue
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def debug_agent_count():
    print("🔍 Debugging Agent Response Count Issue")
    print("="*50)
    
    # Get authentication
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    auth_data = auth_response.json()
    token = auth_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authenticated as: {auth_data['user']['email']}")
    
    # Check all agents in the system
    print(f"\n🤖 All agents in system:")
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"Found {len(agents)} agents for current user:")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent['name']} (ID: {agent['id']})")
            print(f"     Archetype: {agent['archetype']}")
            print(f"     User ID: {agent.get('user_id', 'Unknown')}")
            print()
    
    # Start simulation
    start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if start_response.status_code == 200:
        print("✅ Simulation started")
    
    # Send observer message and analyze responses
    test_message = "Hello team! Please respond to this message."
    observer_response = requests.post(f"{API_URL}/observer/send-message", 
                                    json={"observer_message": test_message}, 
                                    headers=headers)
    
    if observer_response.status_code == 200:
        data = observer_response.json()
        print("✅ Observer message sent successfully")
        
        if 'agent_responses' in data and 'messages' in data['agent_responses']:
            messages = data['agent_responses']['messages']
            print(f"\n📊 Detailed Message Analysis:")
            print(f"Total messages in response: {len(messages)}")
            
            observer_count = 0
            agent_count = 0
            
            for i, msg in enumerate(messages, 1):
                msg_type = "OBSERVER" if msg['agent_name'] == "Observer (You)" else "AGENT"
                print(f"  {i}. [{msg_type}] {msg['agent_name']}")
                print(f"     Message: {msg['message'][:60]}...")
                print(f"     Agent ID: {msg.get('agent_id', 'Unknown')}")
                print()
                
                if msg['agent_name'] == "Observer (You)":
                    observer_count += 1
                else:
                    agent_count += 1
            
            print(f"Summary:")
            print(f"  Observer messages: {observer_count}")
            print(f"  Agent responses: {agent_count}")
            print(f"  Expected agent responses: {len(agents)}")
            
            if agent_count != len(agents):
                print(f"\n⚠️ MISMATCH DETECTED:")
                print(f"  Expected {len(agents)} agent responses")
                print(f"  Got {agent_count} agent responses")
                
                # Check if there are duplicate responses
                agent_names = [msg['agent_name'] for msg in messages if msg['agent_name'] != "Observer (You)"]
                unique_agents = set(agent_names)
                
                if len(agent_names) != len(unique_agents):
                    print(f"  🔍 DUPLICATE RESPONSES DETECTED:")
                    from collections import Counter
                    name_counts = Counter(agent_names)
                    for name, count in name_counts.items():
                        if count > 1:
                            print(f"    {name}: {count} responses")
                else:
                    print(f"  🔍 NO DUPLICATES - checking for extra agents...")
                    print(f"  Agent names in response: {agent_names}")
                    expected_names = [agent['name'] for agent in agents]
                    print(f"  Expected agent names: {expected_names}")
                    
                    extra_agents = set(agent_names) - set(expected_names)
                    if extra_agents:
                        print(f"  🚨 EXTRA AGENTS RESPONDING: {extra_agents}")
    else:
        print(f"❌ Failed to send observer message: {observer_response.status_code}")

if __name__ == "__main__":
    debug_agent_count()