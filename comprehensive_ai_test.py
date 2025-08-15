#!/usr/bin/env python3
"""
COMPREHENSIVE AI AGENT GENERATION TESTING
Testing multiple scenarios for the AI-powered agent generation endpoint.
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

# Global variables
auth_token = None
created_agent_ids = []

def authenticate():
    """Authenticate and get token"""
    global auth_token
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        auth_token = response.json().get("access_token")
        return True
    return False

def test_ai_agent_generation(description, test_name):
    """Test AI agent generation with a specific description"""
    print(f"\n--- {test_name} ---")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    data = {"description": description}
    
    start_time = time.time()
    response = requests.post(f"{API_URL}/agents/ai-generate", json=data, headers=headers)
    end_time = time.time()
    
    print(f"Status: {response.status_code}")
    print(f"Response Time: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        agent_data = response.json()
        
        # Store for cleanup
        created_agent_ids.append(agent_data.get("id"))
        
        print(f"✅ Generated: {agent_data.get('name')}")
        print(f"   Archetype: {agent_data.get('archetype')}")
        print(f"   Avatar: {'✅' if agent_data.get('avatar_url') else '❌'}")
        print(f"   Goal: {agent_data.get('goal', '')[:80]}...")
        print(f"   Expertise: {agent_data.get('expertise', '')[:80]}...")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def cleanup():
    """Clean up created agents"""
    print(f"\n--- Cleanup: Deleting {len(created_agent_ids)} agents ---")
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    for agent_id in created_agent_ids:
        response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Deleted {agent_id}")
        else:
            print(f"❌ Failed to delete {agent_id}")

def main():
    print("COMPREHENSIVE AI AGENT GENERATION TESTING")
    print("="*80)
    
    if not authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test various agent descriptions
    test_cases = [
        ("CEO of Facebook", "CEO of Facebook Test"),
        ("Senior Software Engineer at Google", "Software Engineer Test"),
        ("NASA Astronaut", "Astronaut Test"),
        ("Nobel Prize winning physicist", "Physicist Test"),
        ("Professional chef at Michelin star restaurant", "Chef Test"),
        ("Emergency room doctor", "Doctor Test"),
        ("Investment banker on Wall Street", "Banker Test"),
        ("Professional soccer player", "Soccer Player Test"),
    ]
    
    results = []
    
    for description, test_name in test_cases:
        success = test_ai_agent_generation(description, test_name)
        results.append((test_name, success))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎯 ALL TESTS PASSED - AI Agent Generation is working perfectly!")
    else:
        print("⚠️ Some tests failed - AI Agent Generation needs attention")
    
    cleanup()

if __name__ == "__main__":
    main()