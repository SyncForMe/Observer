#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv
import uuid
import time

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Global variables
auth_token = None
test_user_id = None
created_agent_id = None
saved_agent_id = None

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def add_test_result(name, endpoint, method, status_code, expected_status, result):
    """Add a test result to the results dictionary"""
    test_result = {
        "name": name,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "expected_status": expected_status,
        "result": result
    }
    
    test_results["tests"].append(test_result)
    
    if result == "PASSED":
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def print_test_summary():
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

def test_login():
    """Login with test endpoint to get auth token"""
    global auth_token, test_user_id
    
    print("\n=== Testing Login ===")
    
    # Try the test login endpoint
    test_login_url = f"{API_URL}/auth/test-login"
    print(f"POST {test_login_url}")
    
    try:
        response = requests.post(test_login_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            print(f"Login successful. Token: {auth_token[:10]}...")
            print(f"User ID: {test_user_id}")
            
            add_test_result("Login", "/auth/test-login", "POST", response.status_code, 200, "PASSED")
            return True
        else:
            print(f"Login failed: {response.text}")
            add_test_result("Login", "/auth/test-login", "POST", response.status_code, 200, "FAILED")
            return False
    except Exception as e:
        print(f"Error during login: {e}")
        add_test_result("Login", "/auth/test-login", "POST", 0, 200, "FAILED")
        return False

def test_get_agents():
    """Test the GET /api/agents endpoint"""
    print("\n=== Testing GET /api/agents ===")
    
    url = f"{API_URL}/agents"
    print(f"GET {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} agents")
            if data:
                print("\nSample agent structure:")
                sample_agent = data[0]
                for key, value in sample_agent.items():
                    if isinstance(value, dict):
                        print(f"- {key}: {type(value)}")
                    else:
                        print(f"- {key}: {value}")
            else:
                print("No agents found")
            
            add_test_result("Get Agents", "/agents", "GET", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Get Agents", "/agents", "GET", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Get Agents", "/agents", "GET", 0, 200, "FAILED")
        return None

def test_get_saved_agents():
    """Test the GET /api/saved-agents endpoint"""
    print("\n=== Testing GET /api/saved-agents ===")
    
    url = f"{API_URL}/saved-agents"
    print(f"GET {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} saved agents")
            if data:
                print("\nSample saved agent structure:")
                sample_agent = data[0]
                for key, value in sample_agent.items():
                    if isinstance(value, dict):
                        print(f"- {key}: {type(value)}")
                    else:
                        print(f"- {key}: {value}")
            else:
                print("No saved agents found")
            
            add_test_result("Get Saved Agents", "/saved-agents", "GET", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Get Saved Agents", "/saved-agents", "GET", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Get Saved Agents", "/saved-agents", "GET", 0, 200, "FAILED")
        return None

def test_get_archetypes():
    """Test the GET /api/archetypes endpoint"""
    print("\n=== Testing GET /api/archetypes ===")
    
    url = f"{API_URL}/archetypes"
    print(f"GET {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} archetypes")
            print("\nAvailable archetypes:")
            for archetype, details in data.items():
                print(f"- {archetype}: {details.get('name')} - {details.get('description')}")
            
            add_test_result("Get Archetypes", "/archetypes", "GET", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Get Archetypes", "/archetypes", "GET", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Get Archetypes", "/archetypes", "GET", 0, 200, "FAILED")
        return None

def test_create_agent():
    """Test the POST /api/agents endpoint"""
    global created_agent_id
    
    print("\n=== Testing POST /api/agents ===")
    
    url = f"{API_URL}/agents"
    print(f"POST {url}")
    
    # Create test agent data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "goal": "Test the agent creation endpoint",
        "expertise": "API Testing",
        "background": "Created for testing purposes",
        "memory_summary": "This agent was created to test the API",
        "avatar_prompt": "A robot scientist in a lab coat"
    }
    
    print(f"Request data: {json.dumps(agent_data, indent=2)}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            created_agent_id = data.get('id')
            print(f"Agent created successfully with ID: {created_agent_id}")
            print("\nCreated agent structure:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"- {key}: {type(value)}")
                else:
                    print(f"- {key}: {value}")
            
            add_test_result("Create Agent", "/agents", "POST", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Create Agent", "/agents", "POST", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Create Agent", "/agents", "POST", 0, 200, "FAILED")
        return None

def test_save_agent():
    """Test the POST /api/saved-agents endpoint"""
    global saved_agent_id
    
    print("\n=== Testing POST /api/saved-agents ===")
    
    url = f"{API_URL}/saved-agents"
    print(f"POST {url}")
    
    # Create test saved agent data
    agent_data = {
        "name": f"Saved Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "researcher",
        "goal": "Test the saved agent creation endpoint",
        "expertise": "API Testing",
        "background": "Created for testing saved agents",
        "avatar_prompt": "A researcher with a clipboard"
    }
    
    print(f"Request data: {json.dumps(agent_data, indent=2)}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            saved_agent_id = data.get('id')
            print(f"Saved agent created successfully with ID: {saved_agent_id}")
            print("\nCreated saved agent structure:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"- {key}: {type(value)}")
                else:
                    print(f"- {key}: {value}")
            
            add_test_result("Save Agent", "/saved-agents", "POST", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Save Agent", "/saved-agents", "POST", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Save Agent", "/saved-agents", "POST", 0, 200, "FAILED")
        return None

def test_update_agent():
    """Test the PUT /api/agents/{agent_id} endpoint"""
    global created_agent_id
    
    if not created_agent_id:
        print("\n=== Skipping Update Agent Test (No Agent Created) ===")
        return None
    
    print(f"\n=== Testing PUT /api/agents/{created_agent_id} ===")
    
    url = f"{API_URL}/agents/{created_agent_id}"
    print(f"PUT {url}")
    
    # Create update data with all required fields
    update_data = {
        "name": f"Updated Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",  # Include archetype
        "personality": {  # Include all personality traits
            "extroversion": 5,
            "optimism": 6,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": "Updated goal for testing",
        "expertise": "Updated API Testing",
        "background": "Updated background for testing purposes"
    }
    
    print(f"Request data: {json.dumps(update_data, indent=2)}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent updated successfully")
            print("\nUpdated agent structure:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"- {key}: {type(value)}")
                else:
                    print(f"- {key}: {value}")
            
            add_test_result("Update Agent", f"/agents/{created_agent_id}", "PUT", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Update Agent", f"/agents/{created_agent_id}", "PUT", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Update Agent", f"/agents/{created_agent_id}", "PUT", 0, 200, "FAILED")
        return None

def test_update_saved_agent():
    """Test the PUT /api/saved-agents/{agent_id} endpoint"""
    global saved_agent_id
    
    if not saved_agent_id:
        print("\n=== Skipping Update Saved Agent Test (No Saved Agent Created) ===")
        return None
    
    print(f"\n=== Testing PUT /api/saved-agents/{saved_agent_id} ===")
    
    url = f"{API_URL}/saved-agents/{saved_agent_id}"
    print(f"PUT {url}")
    
    # Create update data with all required fields
    update_data = {
        "name": f"Updated Saved Agent {uuid.uuid4().hex[:8]}",
        "archetype": "researcher",  # Include archetype
        "personality": {  # Include all personality traits
            "extroversion": 4,
            "optimism": 6,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 5
        },
        "goal": "Updated goal for saved agent",
        "expertise": "Updated Saved Agent Testing",
        "background": "Updated background for saved agent testing"
    }
    
    print(f"Request data: {json.dumps(update_data, indent=2)}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        headers["Content-Type"] = "application/json"
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Saved agent updated successfully")
            print("\nUpdated saved agent structure:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"- {key}: {type(value)}")
                else:
                    print(f"- {key}: {value}")
            
            add_test_result("Update Saved Agent", f"/saved-agents/{saved_agent_id}", "PUT", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Update Saved Agent", f"/saved-agents/{saved_agent_id}", "PUT", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Update Saved Agent", f"/saved-agents/{saved_agent_id}", "PUT", 0, 200, "FAILED")
        return None

def test_delete_saved_agent():
    """Test the DELETE /api/saved-agents/{agent_id} endpoint"""
    global saved_agent_id
    
    if not saved_agent_id:
        print("\n=== Skipping Delete Saved Agent Test (No Saved Agent Created) ===")
        return None
    
    print(f"\n=== Testing DELETE /api/saved-agents/{saved_agent_id} ===")
    
    url = f"{API_URL}/saved-agents/{saved_agent_id}"
    print(f"DELETE {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.delete(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Saved agent deleted successfully")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            add_test_result("Delete Saved Agent", f"/saved-agents/{saved_agent_id}", "DELETE", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Delete Saved Agent", f"/saved-agents/{saved_agent_id}", "DELETE", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Delete Saved Agent", f"/saved-agents/{saved_agent_id}", "DELETE", 0, 200, "FAILED")
        return None

def test_delete_agent():
    """Test the DELETE /api/agents/{agent_id} endpoint"""
    global created_agent_id
    
    if not created_agent_id:
        print("\n=== Skipping Delete Agent Test (No Agent Created) ===")
        return None
    
    print(f"\n=== Testing DELETE /api/agents/{created_agent_id} ===")
    
    url = f"{API_URL}/agents/{created_agent_id}"
    print(f"DELETE {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        response = requests.delete(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent deleted successfully")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            add_test_result("Delete Agent", f"/agents/{created_agent_id}", "DELETE", response.status_code, 200, "PASSED")
            return data
        else:
            print(f"Request failed: {response.text}")
            add_test_result("Delete Agent", f"/agents/{created_agent_id}", "DELETE", response.status_code, 200, "FAILED")
            return None
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Delete Agent", f"/agents/{created_agent_id}", "DELETE", 0, 200, "FAILED")
        return None

def test_authentication_requirements():
    """Test authentication requirements for agent endpoints"""
    print("\n=== Testing Authentication Requirements ===")
    
    # Test GET /api/agents without authentication
    print("\nTesting GET /api/agents without authentication")
    url = f"{API_URL}/agents"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        # This endpoint doesn't require authentication, so it should return 200
        if response.status_code == 200:
            print("✅ GET /api/agents does not require authentication (expected behavior)")
            add_test_result("Get Agents Without Auth", "/agents", "GET", response.status_code, 200, "PASSED")
        else:
            print("❌ GET /api/agents returned unexpected status code without authentication")
            add_test_result("Get Agents Without Auth", "/agents", "GET", response.status_code, 200, "FAILED")
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Get Agents Without Auth", "/agents", "GET", 0, 200, "FAILED")
    
    # Test GET /api/saved-agents without authentication
    print("\nTesting GET /api/saved-agents without authentication")
    url = f"{API_URL}/saved-agents"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        # This endpoint should require authentication
        if response.status_code in [401, 403]:
            print("✅ GET /api/saved-agents correctly requires authentication")
            add_test_result("Get Saved Agents Without Auth", "/saved-agents", "GET", response.status_code, 403, "PASSED")
        else:
            print("❌ GET /api/saved-agents does not properly enforce authentication")
            add_test_result("Get Saved Agents Without Auth", "/saved-agents", "GET", response.status_code, 403, "FAILED")
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Get Saved Agents Without Auth", "/saved-agents", "GET", 0, 403, "FAILED")
    
    # Test POST /api/agents without authentication
    print("\nTesting POST /api/agents without authentication")
    url = f"{API_URL}/agents"
    agent_data = {
        "name": f"Test Agent No Auth {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "goal": "Test authentication requirements",
        "expertise": "API Testing",
        "background": "Created for testing authentication",
        "memory_summary": "This agent was created to test authentication",
        "avatar_prompt": "A robot scientist in a lab coat"
    }
    try:
        response = requests.post(url, json=agent_data)
        print(f"Status Code: {response.status_code}")
        
        # This endpoint should require authentication
        if response.status_code in [401, 403]:
            print("✅ POST /api/agents correctly requires authentication")
            add_test_result("Create Agent Without Auth", "/agents", "POST", response.status_code, 403, "PASSED")
        else:
            print("❌ POST /api/agents does not properly enforce authentication")
            add_test_result("Create Agent Without Auth", "/agents", "POST", response.status_code, 403, "FAILED")
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Create Agent Without Auth", "/agents", "POST", 0, 403, "FAILED")
    
    # Test POST /api/saved-agents without authentication
    print("\nTesting POST /api/saved-agents without authentication")
    url = f"{API_URL}/saved-agents"
    agent_data = {
        "name": f"Saved Test Agent No Auth {uuid.uuid4().hex[:8]}",
        "archetype": "researcher",
        "goal": "Test authentication requirements",
        "expertise": "API Testing",
        "background": "Created for testing authentication",
        "avatar_prompt": "A researcher with a clipboard"
    }
    try:
        response = requests.post(url, json=agent_data)
        print(f"Status Code: {response.status_code}")
        
        # This endpoint should require authentication
        if response.status_code in [401, 403]:
            print("✅ POST /api/saved-agents correctly requires authentication")
            add_test_result("Save Agent Without Auth", "/saved-agents", "POST", response.status_code, 403, "PASSED")
        else:
            print("❌ POST /api/saved-agents does not properly enforce authentication")
            add_test_result("Save Agent Without Auth", "/saved-agents", "POST", response.status_code, 403, "FAILED")
    except Exception as e:
        print(f"Error during request: {e}")
        add_test_result("Save Agent Without Auth", "/saved-agents", "POST", 0, 403, "FAILED")

def main():
    print("=== Agent Library API Testing ===")
    
    # Login to get auth token
    if not test_login():
        print("❌ Login failed. Cannot proceed with authenticated tests.")
        print_test_summary()
        return
    
    # Test GET /api/agents
    agents = test_get_agents()
    
    # Test GET /api/saved-agents
    saved_agents = test_get_saved_agents()
    
    # Test GET /api/archetypes
    archetypes = test_get_archetypes()
    
    # Test POST /api/agents
    created_agent = test_create_agent()
    
    # Test PUT /api/agents/{agent_id}
    updated_agent = test_update_agent()
    
    # Test POST /api/saved-agents
    saved_agent = test_save_agent()
    
    # Test PUT /api/saved-agents/{agent_id}
    updated_saved_agent = test_update_saved_agent()
    
    # Test DELETE /api/saved-agents/{agent_id}
    deleted_saved_agent = test_delete_saved_agent()
    
    # Test DELETE /api/agents/{agent_id}
    deleted_agent = test_delete_agent()
    
    # Test authentication requirements
    test_authentication_requirements()
    
    # Print test summary
    print_test_summary()
    
    # Print detailed report
    print("\n=== DETAILED AGENT LIBRARY REPORT ===")
    
    print("\n1. Agent Availability:")
    if agents is not None:
        agent_count = len(agents) if agents else 0
        print(f"   - {agent_count} agents found in the system")
        if agent_count > 0:
            print("   - Sample agent structure:")
            sample_agent = agents[0]
            for key in sample_agent.keys():
                print(f"     - {key}")
    else:
        print("   - Could not retrieve agents")
    
    print("\n2. Saved Agent Availability:")
    if saved_agents is not None:
        saved_agent_count = len(saved_agents) if saved_agents else 0
        print(f"   - {saved_agent_count} saved agents found for the current user")
        if saved_agent_count > 0:
            print("   - Sample saved agent structure:")
            sample_agent = saved_agents[0]
            for key in sample_agent.keys():
                print(f"     - {key}")
    else:
        print("   - Could not retrieve saved agents")
    
    print("\n3. Agent Archetypes:")
    if archetypes is not None:
        print(f"   - {len(archetypes)} archetypes available")
        print("   - Available archetypes:")
        for archetype, details in archetypes.items():
            print(f"     - {archetype}: {details.get('name')} - {details.get('description')}")
    else:
        print("   - Could not retrieve archetypes")
    
    print("\n4. Agent Creation:")
    if created_agent is not None:
        print("   - Agent creation is working properly")
        print(f"   - Created agent ID: {created_agent.get('id')}")
        print(f"   - Agent name: {created_agent.get('name')}")
        print(f"   - Agent archetype: {created_agent.get('archetype')}")
    else:
        print("   - Agent creation failed or was not tested")
    
    print("\n5. Saved Agent Creation:")
    if saved_agent is not None:
        print("   - Saved agent creation is working properly")
        print(f"   - Created saved agent ID: {saved_agent.get('id')}")
        print(f"   - Saved agent name: {saved_agent.get('name')}")
        print(f"   - Saved agent archetype: {saved_agent.get('archetype')}")
        print(f"   - Saved agent user ID: {saved_agent.get('user_id')}")
    else:
        print("   - Saved agent creation failed or was not tested")
    
    print("\n6. Authentication Requirements:")
    auth_tests = [test for test in test_results["tests"] if "Without Auth" in test["name"]]
    auth_passed = all(test["result"] == "PASSED" for test in auth_tests)
    if auth_passed:
        print("   - All authentication requirements are properly enforced")
    else:
        print("   - Some authentication requirements are not properly enforced:")
        for test in auth_tests:
            if test["result"] == "FAILED":
                print(f"     - {test['name']} ({test['method']} {test['endpoint']})")
    
    print("\n7. Overall Agent Library Status:")
    if test_results["failed"] == 0:
        print("   - The Agent Library API is fully functional")
        print("   - All endpoints are working as expected")
    else:
        print(f"   - The Agent Library API has {test_results['failed']} issues that need to be addressed")
        print("   - Failed tests:")
        for test in test_results["tests"]:
            if test["result"] == "FAILED":
                print(f"     - {test['name']} ({test['method']} {test['endpoint']})")

if __name__ == "__main__":
    main()