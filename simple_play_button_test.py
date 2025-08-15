#!/usr/bin/env python3
"""
Simple Play Button Test - Quick verification of the fix
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
    """Authenticate with the backend"""
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_play_button_fix():
    """Test the play button fix"""
    print("🎮 SIMPLE PLAY BUTTON TEST")
    print("=" * 50)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Set scenario
    scenario_data = {
        "scenario": "Test quantum communication development",
        "scenario_name": "Quick Test"
    }
    
    response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to set scenario")
        return False
    print("✅ Scenario set")
    
    # Check agents
    response = requests.get(f"{API_URL}/agents", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get agents")
        return False
    
    agents = response.json()
    print(f"✅ Found {len(agents)} agents")
    
    if len(agents) < 2:
        print("⚠️ Need at least 2 agents, creating test agents...")
        
        # Create test agents
        test_agents = [
            {
                "name": "Dr. Quantum Alice",
                "archetype": "scientist",
                "goal": "Develop quantum communication protocols",
                "expertise": "Quantum Physics",
                "background": "Expert in quantum entanglement",
                "personality": {
                    "extroversion": 6, "optimism": 8, "curiosity": 9,
                    "cooperativeness": 7, "energy": 7
                }
            },
            {
                "name": "Engineer Bob",
                "archetype": "researcher", 
                "goal": "Build practical quantum devices",
                "expertise": "Quantum Engineering",
                "background": "Hardware implementation specialist",
                "personality": {
                    "extroversion": 5, "optimism": 7, "curiosity": 8,
                    "cooperativeness": 8, "energy": 6
                }
            }
        ]
        
        for agent_data in test_agents:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                print(f"✅ Created agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent: {agent_data['name']}")
                return False
        
        print("✅ Test agents created successfully")
    
    # Count conversations before
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get conversations")
        return False
    
    conversations_before = len(response.json())
    print(f"✅ Conversations before start: {conversations_before}")
    
    # Start simulation (the play button action)
    print("▶️ Starting simulation (this may take 30-60 seconds for AI generation)...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=90)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Simulation started successfully in {elapsed:.1f}s")
            
            # Check if conversations were generated
            time.sleep(2)  # Brief wait for any async operations
            response = requests.get(f"{API_URL}/conversations", headers=headers)
            if response.status_code == 200:
                conversations_after = len(response.json())
                print(f"✅ Conversations after start: {conversations_after}")
                
                if conversations_after > conversations_before:
                    print(f"🎉 SUCCESS: Generated {conversations_after - conversations_before} new conversations automatically!")
                    return True
                else:
                    print("❌ No new conversations generated")
                    return False
            else:
                print("❌ Failed to check conversations after start")
                return False
        else:
            print(f"❌ Simulation start failed: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - but this might be normal for AI generation")
        print("   Let's check if conversations were generated anyway...")
        
        # Check conversations even after timeout
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            conversations_after = len(response.json())
            print(f"✅ Conversations after timeout: {conversations_after}")
            
            if conversations_after > conversations_before:
                print(f"🎉 SUCCESS: Generated {conversations_after - conversations_before} new conversations (despite timeout)!")
                return True
        
        return False

if __name__ == "__main__":
    success = test_play_button_fix()
    if success:
        print("\n🎉 PLAY BUTTON FIX IS WORKING!")
        print("   ✅ Simulation starts successfully")
        print("   ✅ Conversations are generated automatically")
    else:
        print("\n❌ PLAY BUTTON FIX NEEDS ATTENTION")