#!/usr/bin/env python3
"""
Agent Library → Observatory Synchronization Flow Test
Testing the complete flow after fixing the data validation issue with personality and avatar_prompt fields.
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
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth_token=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        print(f"Status Code: {response.status_code}")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        })
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def test_guest_authentication():
    """Test 1: Verify /auth/test-login returns valid JWT token"""
    print("\n" + "="*80)
    print("TEST 1: GUEST AUTHENTICATION")
    print("="*80)
    
    test_passed, response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if test_passed and response:
        auth_token = response.get("access_token")
        user_data = response.get("user", {})
        user_id = user_data.get("id")
        
        print(f"✅ Guest authentication successful")
        print(f"User ID: {user_id}")
        print(f"JWT Token: {auth_token[:50]}...")
        
        return True, auth_token, user_id
    else:
        print("❌ Guest authentication failed")
        return False, None, None

def create_agent_with_fixed_structure(auth_token, agent_name, archetype="scientist"):
    """Create an agent with the new data structure including personality and avatar_prompt"""
    
    # Generate personality based on archetype (as mentioned in the review request)
    personality_map = {
        "scientist": {"extroversion": 4, "optimism": 6, "curiosity": 9, "cooperativeness": 7, "energy": 6},
        "artist": {"extroversion": 6, "optimism": 7, "curiosity": 8, "cooperativeness": 6, "energy": 7},
        "leader": {"extroversion": 9, "optimism": 8, "curiosity": 6, "cooperativeness": 8, "energy": 8},
        "skeptic": {"extroversion": 4, "optimism": 3, "curiosity": 7, "cooperativeness": 5, "energy": 5},
        "optimist": {"extroversion": 8, "optimism": 10, "curiosity": 6, "cooperativeness": 9, "energy": 8}
    }
    
    personality = personality_map.get(archetype, personality_map["scientist"])
    
    agent_data = {
        "name": agent_name,
        "archetype": archetype,
        "personality": personality,  # Required personality object with all 5 traits
        "goal": f"To excel as a {archetype} and contribute valuable insights to the team",
        "expertise": f"{archetype.title()} with specialized knowledge in relevant domains",
        "background": f"Experienced {archetype} with proven track record in collaborative environments",
        "avatar_prompt": f"Professional headshot of a {archetype}, confident and approachable, modern office setting"  # Required avatar_prompt field
    }
    
    test_passed, response = run_test(
        f"Create Agent: {agent_name}",
        "/agents",
        method="POST",
        data=agent_data,
        auth_token=auth_token,
        expected_keys=["id", "name", "archetype", "personality", "avatar_prompt"]
    )
    
    if test_passed and response:
        agent_id = response.get("id")
        print(f"✅ Agent created successfully with ID: {agent_id}")
        
        # Verify the personality structure
        returned_personality = response.get("personality", {})
        required_traits = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
        
        missing_traits = [trait for trait in required_traits if trait not in returned_personality]
        if missing_traits:
            print(f"❌ Missing personality traits: {missing_traits}")
            return False, None
        else:
            print(f"✅ All personality traits present: {list(returned_personality.keys())}")
        
        # Verify avatar_prompt is present
        if response.get("avatar_prompt"):
            print(f"✅ Avatar prompt present: {response.get('avatar_prompt')[:50]}...")
        else:
            print("❌ Avatar prompt missing")
            return False, None
        
        return True, agent_id
    else:
        print(f"❌ Failed to create agent: {agent_name}")
        return False, None

def test_agent_creation_with_fixed_structure(auth_token):
    """Test 2: Create an agent via POST /api/agents with the new data structure"""
    print("\n" + "="*80)
    print("TEST 2: AGENT CREATION WITH FIXED DATA STRUCTURE")
    print("="*80)
    
    # Create a single agent with the fixed structure
    agent_name = f"Dr. Sarah Test-{uuid.uuid4().hex[:8]}"
    success, agent_id = create_agent_with_fixed_structure(auth_token, agent_name, "scientist")
    
    if success:
        print(f"✅ Agent creation with fixed data structure successful")
        return True, [agent_id]
    else:
        print("❌ Agent creation with fixed data structure failed")
        return False, []

def test_agent_retrieval(auth_token, expected_agent_ids):
    """Test 3: Immediately fetch agents via GET /api/agents to verify the agent was saved"""
    print("\n" + "="*80)
    print("TEST 3: AGENT RETRIEVAL (OBSERVATORY VIEW)")
    print("="*80)
    
    test_passed, response = run_test(
        "Retrieve All Agents",
        "/agents",
        method="GET",
        auth_token=auth_token
    )
    
    if test_passed and response:
        retrieved_agents = response if isinstance(response, list) else []
        retrieved_agent_ids = [agent.get("id") for agent in retrieved_agents]
        
        print(f"✅ Retrieved {len(retrieved_agents)} agents")
        
        # Verify all expected agents are present
        missing_agents = [agent_id for agent_id in expected_agent_ids if agent_id not in retrieved_agent_ids]
        
        if missing_agents:
            print(f"❌ Missing agents: {missing_agents}")
            return False
        else:
            print(f"✅ All expected agents found in Observatory view")
            
            # Verify data structure of retrieved agents
            for agent in retrieved_agents:
                agent_name = agent.get("name", "Unknown")
                print(f"\nAgent: {agent_name}")
                
                # Check required fields
                required_fields = ["id", "name", "archetype", "personality", "goal", "expertise", "background", "avatar_prompt"]
                missing_fields = [field for field in required_fields if field not in agent]
                
                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                    return False
                else:
                    print(f"✅ All required fields present")
                
                # Check personality structure
                personality = agent.get("personality", {})
                required_traits = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
                missing_traits = [trait for trait in required_traits if trait not in personality]
                
                if missing_traits:
                    print(f"❌ Missing personality traits: {missing_traits}")
                    return False
                else:
                    print(f"✅ All personality traits present: {list(personality.keys())}")
            
            return True
    else:
        print("❌ Failed to retrieve agents")
        return False

def test_multiple_agent_creation(auth_token):
    """Test 4: Create 2-3 agents to verify synchronization works for multiple agents"""
    print("\n" + "="*80)
    print("TEST 4: MULTIPLE AGENT CREATION")
    print("="*80)
    
    agents_to_create = [
        ("Dr. Michael Engineer", "leader"),
        ("Sarah Artist", "artist"),
        ("Tom Skeptic", "skeptic")
    ]
    
    created_agent_ids = []
    
    for agent_name, archetype in agents_to_create:
        success, agent_id = create_agent_with_fixed_structure(auth_token, agent_name, archetype)
        if success:
            created_agent_ids.append(agent_id)
        else:
            print(f"❌ Failed to create agent: {agent_name}")
            return False, []
    
    print(f"✅ Successfully created {len(created_agent_ids)} agents")
    return True, created_agent_ids

def test_data_structure_verification(auth_token, all_agent_ids):
    """Test 5: Verify Data Structure - Confirm all agents have proper personality data and required fields"""
    print("\n" + "="*80)
    print("TEST 5: DATA STRUCTURE VERIFICATION")
    print("="*80)
    
    test_passed, response = run_test(
        "Final Data Structure Verification",
        "/agents",
        method="GET",
        auth_token=auth_token
    )
    
    if test_passed and response:
        agents = response if isinstance(response, list) else []
        
        print(f"Total agents in system: {len(agents)}")
        
        # Verify each agent has the complete data structure
        structure_issues = []
        
        for agent in agents:
            agent_name = agent.get("name", "Unknown")
            agent_id = agent.get("id", "Unknown")
            
            print(f"\nVerifying agent: {agent_name} ({agent_id})")
            
            # Check all required fields
            required_fields = {
                "id": str,
                "name": str,
                "archetype": str,
                "personality": dict,
                "goal": str,
                "expertise": str,
                "background": str,
                "avatar_prompt": str,
                "user_id": str
            }
            
            for field, expected_type in required_fields.items():
                if field not in agent:
                    structure_issues.append(f"Agent {agent_name}: Missing field '{field}'")
                elif not isinstance(agent[field], expected_type):
                    structure_issues.append(f"Agent {agent_name}: Field '{field}' has wrong type (expected {expected_type.__name__})")
                else:
                    print(f"  ✅ {field}: {type(agent[field]).__name__}")
            
            # Detailed personality verification
            personality = agent.get("personality", {})
            required_traits = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
            
            for trait in required_traits:
                if trait not in personality:
                    structure_issues.append(f"Agent {agent_name}: Missing personality trait '{trait}'")
                elif not isinstance(personality[trait], int) or not (1 <= personality[trait] <= 10):
                    structure_issues.append(f"Agent {agent_name}: Personality trait '{trait}' should be integer 1-10")
                else:
                    print(f"  ✅ personality.{trait}: {personality[trait]}")
            
            # Verify avatar_prompt is not empty
            avatar_prompt = agent.get("avatar_prompt", "")
            if not avatar_prompt or len(avatar_prompt.strip()) == 0:
                structure_issues.append(f"Agent {agent_name}: Avatar prompt is empty")
            else:
                print(f"  ✅ avatar_prompt: {len(avatar_prompt)} characters")
        
        if structure_issues:
            print(f"\n❌ Found {len(structure_issues)} data structure issues:")
            for issue in structure_issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"\n✅ All {len(agents)} agents have proper data structure")
            print("✅ All personality objects contain all 5 required traits")
            print("✅ All agents have non-empty avatar_prompt fields")
            print("✅ All agents are properly associated with user_id")
            return True
    else:
        print("❌ Failed to retrieve agents for data structure verification")
        return False

def cleanup_test_agents(auth_token, agent_ids):
    """Clean up test agents after testing"""
    print("\n" + "="*80)
    print("CLEANUP: REMOVING TEST AGENTS")
    print("="*80)
    
    for agent_id in agent_ids:
        test_passed, response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth_token=auth_token,
            expected_status=200
        )
        
        if test_passed:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution"""
    print("="*80)
    print("AGENT LIBRARY → OBSERVATORY SYNCHRONIZATION FLOW TEST")
    print("Testing after fixing data validation issue with personality and avatar_prompt fields")
    print("="*80)
    
    all_agent_ids = []
    
    try:
        # Test 1: Guest Authentication
        auth_success, auth_token, user_id = test_guest_authentication()
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return
        
        # Test 2: Agent Creation with Fixed Data Structure
        creation_success, initial_agent_ids = test_agent_creation_with_fixed_structure(auth_token)
        if creation_success:
            all_agent_ids.extend(initial_agent_ids)
        
        # Test 3: Agent Retrieval (Observatory View)
        if creation_success:
            retrieval_success = test_agent_retrieval(auth_token, initial_agent_ids)
        else:
            retrieval_success = False
        
        # Test 4: Multiple Agent Creation
        multiple_success, multiple_agent_ids = test_multiple_agent_creation(auth_token)
        if multiple_success:
            all_agent_ids.extend(multiple_agent_ids)
        
        # Test 5: Data Structure Verification
        if multiple_success:
            structure_success = test_data_structure_verification(auth_token, all_agent_ids)
        else:
            structure_success = False
        
        # Print final results
        print_summary()
        
        # Final assessment
        print("\n" + "="*80)
        print("FINAL ASSESSMENT")
        print("="*80)
        
        if test_results["failed"] == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Guest authentication works correctly")
            print("✅ Agent creation with fixed data structure works")
            print("✅ Agent Library → Observatory synchronization is working")
            print("✅ Multiple agent creation and synchronization works")
            print("✅ All agents have proper personality data and required fields")
            print("✅ The '7 validation errors for Agent' issue has been resolved")
        else:
            print("❌ SOME TESTS FAILED")
            print(f"Failed tests: {test_results['failed']}")
            print("The synchronization flow may still have issues")
        
    finally:
        # Cleanup
        if all_agent_ids and auth_token:
            cleanup_test_agents(auth_token, all_agent_ids)

if __name__ == "__main__":
    main()