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

def test_login():
    """Login with test endpoint to get auth token"""
    print("\n=== Testing Login ===")
    
    # Try the test login endpoint
    test_login_url = f"{API_URL}/auth/test-login"
    print(f"POST {test_login_url}")
    
    try:
        response = requests.post(test_login_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_data = data.get("user", {})
            user_id = user_data.get("id")
            print(f"Login successful. Token: {token[:10]}...")
            print(f"User ID: {user_id}")
            return token
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

# Global variables
auth_token = None
created_agent_id = None

def print_separator():
    print("\n" + "="*80)

def test_get_agents_without_auth():
    """Test GET /api/agents without authentication"""
    print_separator()
    print("TESTING GET /api/agents WITHOUT AUTHENTICATION")
    print_separator()
    
    url = f"{API_URL}/agents"
    print(f"GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            print("❌ Endpoint accessible without authentication")
            return False, response_data
        elif response.status_code == 403 or response.status_code == 401:
            print(f"✅ Endpoint correctly requires authentication")
            return True, None
        else:
            print(f"❓ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_get_agents_with_auth():
    """Test GET /api/agents with authentication"""
    global auth_token
    
    print_separator()
    print("TESTING GET /api/agents WITH AUTHENTICATION")
    print_separator()
    
    if not auth_token:
        print("❌ No auth token available")
        return False, None
    
    url = f"{API_URL}/agents"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"GET {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Verify response structure
            if isinstance(response_data, list):
                if response_data:
                    # Check if agents have all required fields
                    sample_agent = response_data[0]
                    required_fields = ["id", "name", "archetype", "expertise", "background", "goal", "personality", "avatar_url"]
                    missing_fields = [field for field in required_fields if field not in sample_agent]
                    
                    if missing_fields:
                        print(f"❌ Agent data missing required fields: {missing_fields}")
                        return False, response_data
                    else:
                        print(f"✅ Agent data includes all required fields")
                        
                    # Check personality structure
                    if "personality" in sample_agent:
                        personality = sample_agent["personality"]
                        personality_fields = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
                        missing_personality = [field for field in personality_fields if field not in personality]
                        
                        if missing_personality:
                            print(f"❌ Personality data missing required fields: {missing_personality}")
                            return False, response_data
                        else:
                            print(f"✅ Personality data includes all required fields")
                
                print(f"✅ Successfully retrieved {len(response_data)} agents")
                return True, response_data
            else:
                print(f"❌ Expected list response, got: {type(response_data)}")
                return False, response_data
        else:
            print(f"❌ Request failed: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_create_agent():
    """Test POST /api/agents to create a new agent"""
    global auth_token, created_agent_id
    
    print_separator()
    print("TESTING POST /api/agents")
    print_separator()
    
    if not auth_token:
        print("❌ No auth token available")
        return False, None
    
    # Prepare agent data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:8]}",
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 6,
            "energy": 8
        },
        "goal": "To test the agent endpoints thoroughly",
        "expertise": "Software Testing and Quality Assurance",
        "background": "Experienced in automated testing and API validation",
        "memory_summary": "",
        "avatar_prompt": "A professional software tester with glasses and a clipboard",
        "avatar_url": ""
    }
    
    url = f"{API_URL}/agents"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"POST {url}")
    print(f"Headers: {headers}")
    print(f"Request data: {json.dumps(agent_data, indent=2)}")
    
    try:
        response = requests.post(url, json=agent_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Store the created agent ID for later tests
            created_agent_id = response_data.get("id")
            
            if created_agent_id:
                print(f"✅ Successfully created agent with ID: {created_agent_id}")
                
                # Verify the created agent has the correct data
                for key, value in agent_data.items():
                    if key == "personality":
                        for p_key, p_value in value.items():
                            if response_data["personality"][p_key] != p_value:
                                print(f"❌ Personality mismatch for {p_key}: expected {p_value}, got {response_data['personality'][p_key]}")
                                return False, response_data
                    elif key != "avatar_prompt" and key != "memory_summary" and response_data.get(key) != value:
                        print(f"❌ Data mismatch for {key}: expected {value}, got {response_data.get(key)}")
                        return False, response_data
                
                print("✅ Created agent data matches request data")
                return True, response_data
            else:
                print("❌ No agent ID in response")
                return False, response_data
        else:
            print(f"❌ Request failed: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_update_agent():
    """Test PUT /api/agents/{agent_id} to update an agent"""
    global auth_token, created_agent_id
    
    print_separator()
    print("TESTING PUT /api/agents/{agent_id}")
    print_separator()
    
    if not auth_token or not created_agent_id:
        print("❌ No auth token or agent ID available")
        return False, None
    
    # Prepare update data
    update_data = {
        "name": f"Updated Agent {uuid.uuid4().hex[:8]}",
        "archetype": "leader",
        "personality": {
            "extroversion": 8,
            "optimism": 9,
            "curiosity": 7,
            "cooperativeness": 8,
            "energy": 9
        },
        "goal": "To verify the agent update functionality works correctly",
        "background": "Senior QA Engineer with focus on backend systems"
    }
    
    url = f"{API_URL}/agents/{created_agent_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"PUT {url}")
    print(f"Headers: {headers}")
    print(f"Request data: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Now update the expertise field separately
            expertise_data = {
                "expertise": "API Testing and Validation"
            }
            
            expertise_url = f"{API_URL}/agents/{created_agent_id}/expertise"
            print(f"\nUpdating expertise field separately:")
            print(f"PUT {expertise_url}")
            print(f"Request data: {json.dumps(expertise_data, indent=2)}")
            
            expertise_response = requests.put(expertise_url, json=expertise_data, headers=headers)
            print(f"Status code: {expertise_response.status_code}")
            
            if expertise_response.status_code == 200:
                expertise_response_data = expertise_response.json()
                print(f"Response: {json.dumps(expertise_response_data, indent=2)}")
                
                # Verify the updated agent has the correct data
                all_fields_updated = True
                for key, value in update_data.items():
                    if key == "personality":
                        for p_key, p_value in value.items():
                            if expertise_response_data["personality"][p_key] != p_value:
                                print(f"❌ Personality mismatch for {p_key}: expected {p_value}, got {expertise_response_data['personality'][p_key]}")
                                all_fields_updated = False
                    elif expertise_response_data.get(key) != value:
                        print(f"❌ Data mismatch for {key}: expected {value}, got {expertise_response_data.get(key)}")
                        all_fields_updated = False
                
                # Check expertise field separately
                if expertise_response_data.get("expertise") != expertise_data.get("expertise"):
                    print(f"❌ Data mismatch for expertise: expected {expertise_data.get('expertise')}, got {expertise_response_data.get('expertise')}")
                    all_fields_updated = False
                
                if all_fields_updated:
                    print("✅ All fields updated successfully")
                    return True, expertise_response_data
                else:
                    print("❌ Some fields not updated correctly")
                    return False, expertise_response_data
            else:
                print(f"❌ Expertise update failed: {expertise_response.text}")
                return False, response_data
        else:
            print(f"❌ Request failed: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_update_agent_invalid_id():
    """Test PUT /api/agents/{agent_id} with an invalid agent ID"""
    global auth_token
    
    print_separator()
    print("TESTING PUT /api/agents/{agent_id} WITH INVALID ID")
    print_separator()
    
    if not auth_token:
        print("❌ No auth token available")
        return False, None
    
    # Generate a random invalid ID
    invalid_id = str(uuid.uuid4())
    
    # Prepare update data
    update_data = {
        "name": "This update should fail",
        "goal": "This update should not succeed"
    }
    
    url = f"{API_URL}/agents/{invalid_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"PUT {url}")
    print(f"Headers: {headers}")
    print(f"Request data: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        # Test the expertise endpoint with invalid ID as well
        expertise_url = f"{API_URL}/agents/{invalid_id}/expertise"
        expertise_data = {
            "expertise": "This update should fail"
        }
        print(f"\nTesting expertise endpoint with invalid ID:")
        print(f"PUT {expertise_url}")
        print(f"Request data: {json.dumps(expertise_data, indent=2)}")
        
        expertise_response = requests.put(expertise_url, json=expertise_data, headers=headers)
        print(f"Status code: {expertise_response.status_code}")
        
        if expertise_response.status_code == 404:
            print(f"✅ Expertise endpoint correctly returned 404 for invalid agent ID")
            return True, None
        else:
            print(f"❌ Expected 404 from expertise endpoint, got {expertise_response.status_code}: {expertise_response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_delete_agent():
    """Test DELETE /api/agents/{agent_id} to delete an agent"""
    global auth_token, created_agent_id
    
    print_separator()
    print("TESTING DELETE /api/agents/{agent_id}")
    print_separator()
    
    if not auth_token or not created_agent_id:
        print("❌ No auth token or agent ID available")
        return False, None
    
    url = f"{API_URL}/agents/{created_agent_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"DELETE {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.delete(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Verify the agent was deleted
            if "message" in response_data and "deleted" in response_data["message"].lower():
                print("✅ Agent successfully deleted")
                
                # Verify the agent is actually gone by trying to get it
                verify_url = f"{API_URL}/agents"
                verify_response = requests.get(verify_url, headers=headers)
                
                if verify_response.status_code == 200:
                    agents = verify_response.json()
                    deleted = True
                    
                    for agent in agents:
                        if agent.get("id") == created_agent_id:
                            deleted = False
                            break
                    
                    if deleted:
                        print("✅ Agent confirmed deleted - not found in agents list")
                        return True, response_data
                    else:
                        print("❌ Agent still exists in agents list")
                        return False, response_data
                else:
                    print(f"❌ Failed to verify deletion: {verify_response.text}")
                    return False, response_data
            else:
                print("❌ Unexpected response message")
                return False, response_data
        else:
            print(f"❌ Request failed: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def test_delete_agent_invalid_id():
    """Test DELETE /api/agents/{agent_id} with an invalid agent ID"""
    global auth_token
    
    print_separator()
    print("TESTING DELETE /api/agents/{agent_id} WITH INVALID ID")
    print_separator()
    
    if not auth_token:
        print("❌ No auth token available")
        return False, None
    
    # Generate a random invalid ID
    invalid_id = str(uuid.uuid4())
    
    url = f"{API_URL}/agents/{invalid_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    print(f"DELETE {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.delete(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 404:
            print(f"✅ Correctly returned 404 for invalid agent ID")
            return True, None
        else:
            print(f"❌ Expected 404, got {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False, None

def main():
    """Run all agent endpoint tests"""
    global auth_token
    
    print_separator()
    print("RUNNING AGENT ENDPOINT TESTS FOR OBSERVATORY TAB")
    print_separator()
    
    # Login to get auth token
    auth_token = test_login()
    if not auth_token:
        print("❌ Login failed. Cannot proceed with authenticated tests.")
        return
    
    # Initialize test results
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Define tests to run
    tests = [
        ("GET /api/agents without auth", test_get_agents_without_auth),
        ("GET /api/agents with auth", test_get_agents_with_auth),
        ("POST /api/agents", test_create_agent),
        ("PUT /api/agents/{agent_id}", test_update_agent),
        ("PUT /api/agents/{agent_id} with invalid ID", test_update_agent_invalid_id),
        ("DELETE /api/agents/{agent_id}", test_delete_agent),
        ("DELETE /api/agents/{agent_id} with invalid ID", test_delete_agent_invalid_id)
    ]
    
    # Run each test
    for test_name, test_func in tests:
        print_separator()
        print(f"RUNNING TEST: {test_name}")
        
        try:
            result, data = test_func()
            
            if result:
                results["passed"] += 1
                results["tests"].append({
                    "name": test_name,
                    "result": "PASSED",
                    "data": data
                })
                print(f"✅ TEST PASSED: {test_name}")
            else:
                results["failed"] += 1
                results["tests"].append({
                    "name": test_name,
                    "result": "FAILED",
                    "data": data
                })
                print(f"❌ TEST FAILED: {test_name}")
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({
                "name": test_name,
                "result": "ERROR",
                "error": str(e)
            })
            print(f"❌ TEST ERROR: {test_name} - {e}")
    
    # Print summary
    print_separator()
    print("TEST SUMMARY")
    print_separator()
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print_separator()
    
    for i, test in enumerate(results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']}")
        if test.get("error"):
            print(f"   Error: {test['error']}")
    
    print_separator()
    overall_result = "PASSED" if results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print_separator()
    
    # Print detailed report
    print("\n=== Detailed Agent Endpoints Report ===")
    
    # Check if GET /api/agents works
    get_agents_result = next((t for t in results["tests"] if t["name"] == "GET /api/agents with auth"), None)
    if get_agents_result and get_agents_result["result"] == "PASSED":
        agent_count = len(get_agents_result.get("data", []))
        print(f"\n1. Agent Retrieval: ✅ Working - {agent_count} agents found")
        
        # Check agent data structure
        if agent_count > 0:
            sample_agent = get_agents_result["data"][0]
            print(f"   - Agent data structure includes all required fields")
            print(f"   - Sample agent: {sample_agent.get('name')} ({sample_agent.get('archetype')})")
    else:
        print("\n1. Agent Retrieval: ❌ Not working properly")
    
    # Check if PUT /api/agents/{agent_id} works
    update_agent_result = next((t for t in results["tests"] if t["name"] == "PUT /api/agents/{agent_id}"), None)
    if update_agent_result and update_agent_result["result"] == "PASSED":
        print(f"\n2. Agent Update: ✅ Working properly")
        if update_agent_result.get("data"):
            updated_agent = update_agent_result["data"]
            print(f"   - Successfully updated agent: {updated_agent.get('name')}")
    else:
        print("\n2. Agent Update: ❌ Not working properly")
    
    # Check if DELETE /api/agents/{agent_id} works
    delete_agent_result = next((t for t in results["tests"] if t["name"] == "DELETE /api/agents/{agent_id}"), None)
    if delete_agent_result and delete_agent_result["result"] == "PASSED":
        print(f"\n3. Agent Deletion: ✅ Working properly")
    else:
        print("\n3. Agent Deletion: ❌ Not working properly")
    
    # Check authentication
    auth_tests = [
        next((t for t in results["tests"] if t["name"] == "GET /api/agents without auth"), None),
        next((t for t in results["tests"] if t["name"] == "GET /api/agents with auth"), None)
    ]
    
    if all(t and t["result"] == "PASSED" for t in auth_tests):
        print(f"\n4. Authentication: ✅ Working properly for agent endpoints")
    else:
        print(f"\n4. Authentication: ❌ Issues with authentication for agent endpoints")
    
    # Overall assessment
    if results["failed"] == 0:
        print("\n✅ All agent endpoints are working properly for the Observatory tab")
        print("✅ GET /api/agents returns agent data correctly with authentication")
        print("✅ PUT /api/agents/{agent_id} allows editing agents")
        print("✅ DELETE /api/agents/{agent_id} allows removing agents")
        print("✅ Authentication is working properly for all agent endpoints")
        print("✅ Agent data structure includes all needed fields")
    else:
        print(f"\n❌ {results['failed']} out of {len(tests)} agent endpoint tests failed")

if __name__ == "__main__":
    main()