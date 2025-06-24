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

def main():
    print("=== Agent Library API Testing ===")
    
    # Login to get auth token
    token = test_login()
    if not token:
        print("❌ Login failed. Cannot proceed with authenticated tests.")
        return
    
    # Test all agent-related endpoints
    endpoints = [
        {"method": "GET", "url": "/agents", "name": "Get all agents"},
        {"method": "GET", "url": "/saved-agents", "name": "Get saved agents", "auth": True},
        {"method": "GET", "url": "/archetypes", "name": "Get agent archetypes"},
        {"method": "POST", "url": "/agents", "name": "Create agent", "data": {
            "name": f"Test Agent {uuid.uuid4().hex[:8]}",
            "archetype": "scientist",
            "goal": "Test the agent creation endpoint",
            "expertise": "API Testing",
            "background": "Created for testing purposes",
            "memory_summary": "This agent was created to test the API",
            "avatar_prompt": "A robot scientist in a lab coat"
        }}
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n=== Testing {endpoint['method']} {endpoint['url']} ===")
        
        url = f"{API_URL}{endpoint['url']}"
        method = endpoint['method']
        headers = {}
        
        if endpoint.get('auth', False) and token:
            headers["Authorization"] = f"Bearer {token}"
        
        if 'data' in endpoint:
            headers["Content-Type"] = "application/json"
            print(f"Request data: {json.dumps(endpoint['data'], indent=2)}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=endpoint.get('data'), headers=headers)
            else:
                print(f"Unsupported method: {method}")
                continue
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    print(f"Found {len(data)} items")
                    if data and len(data) > 0:
                        print("\nSample item structure:")
                        sample = data[0]
                        for key, value in sample.items():
                            if isinstance(value, dict):
                                print(f"- {key}: {type(value)}")
                            else:
                                print(f"- {key}: {value}")
                else:
                    print("\nResponse structure:")
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"- {key}: {type(value)}")
                        else:
                            print(f"- {key}: {value}")
                
                results.append({
                    "endpoint": endpoint['url'],
                    "method": method,
                    "name": endpoint['name'],
                    "status": response.status_code,
                    "success": True,
                    "data": data if isinstance(data, dict) else {"count": len(data)}
                })
            else:
                print(f"Request failed: {response.text}")
                results.append({
                    "endpoint": endpoint['url'],
                    "method": method,
                    "name": endpoint['name'],
                    "status": response.status_code,
                    "success": False,
                    "error": response.text
                })
        except Exception as e:
            print(f"Error during request: {e}")
            results.append({
                "endpoint": endpoint['url'],
                "method": method,
                "name": endpoint['name'],
                "status": 0,
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    print("\n=== Test Summary ===")
    for i, result in enumerate(results, 1):
        status = "✅ Success" if result["success"] else "❌ Failed"
        print(f"{i}. {status} - {result['method']} {result['endpoint']} ({result['name']})")
    
    # Print detailed report
    print("\n=== Detailed Agent Library Report ===")
    
    # Check if agents exist
    agents_result = next((r for r in results if r["endpoint"] == "/agents" and r["method"] == "GET"), None)
    if agents_result and agents_result["success"]:
        agent_count = agents_result["data"].get("count", 0)
        print(f"\n1. Agent Availability: {agent_count} agents found")
    else:
        print("\n1. Agent Availability: Could not retrieve agents")
    
    # Check if saved agents exist
    saved_agents_result = next((r for r in results if r["endpoint"] == "/saved-agents" and r["method"] == "GET"), None)
    if saved_agents_result and saved_agents_result["success"]:
        saved_agent_count = saved_agents_result["data"].get("count", 0)
        print(f"\n2. Saved Agent Availability: {saved_agent_count} saved agents found")
    else:
        print("\n2. Saved Agent Availability: Could not retrieve saved agents")
    
    # Check if archetypes exist
    archetypes_result = next((r for r in results if r["endpoint"] == "/archetypes" and r["method"] == "GET"), None)
    if archetypes_result and archetypes_result["success"]:
        print(f"\n3. Agent Archetypes: Available")
    else:
        print("\n3. Agent Archetypes: Could not retrieve archetypes")
    
    # Check if agent creation works
    create_agent_result = next((r for r in results if r["endpoint"] == "/agents" and r["method"] == "POST"), None)
    if create_agent_result and create_agent_result["success"]:
        print(f"\n4. Agent Creation: Working properly")
    else:
        print("\n4. Agent Creation: Not working properly")
    
    # Overall assessment
    success_count = sum(1 for r in results if r["success"])
    if success_count == len(results):
        print("\n✅ All agent-related endpoints are working properly")
    else:
        print(f"\n❌ {len(results) - success_count} out of {len(results)} agent-related endpoints have issues")

if __name__ == "__main__":
    main()