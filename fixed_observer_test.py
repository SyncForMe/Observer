#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

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

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
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
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
        test_results["tests"].append(test_result)
        
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

def login_as_admin():
    """Login with admin credentials"""
    global auth_token, test_user_id
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        return True
    else:
        print("Login failed. Cannot proceed with testing.")
        return False

def get_admin_agents():
    """Get all agents for the admin user"""
    if not auth_token:
        print("No auth token available. Cannot get agents.")
        return []
    
    agents_test, agents_response = run_test(
        "Get admin user agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if agents_test and agents_response:
        print(f"Found {len(agents_response)} agents for admin user")
        return agents_response
    else:
        print("Failed to get admin user agents")
        return []

def clean_up_test_agents():
    """Clean up any test agents that belong to the admin user"""
    admin_agents = get_admin_agents()
    
    if not admin_agents:
        print("No agents found for admin user")
        return False
    
    # Identify test agents
    test_agent_ids = []
    for agent in admin_agents:
        agent_name = agent.get("name", "").lower()
        if any(keyword in agent_name for keyword in ["test", "workflow", "demo", "sample"]):
            test_agent_ids.append(agent.get("id"))
            print(f"Identified test agent: {agent.get('name')} ({agent.get('id')})")
    
    if not test_agent_ids:
        print("No test agents found to clean up")
        return True
    
    # Delete test agents
    print(f"Deleting {len(test_agent_ids)} test agents...")
    
    delete_data = {
        "agent_ids": test_agent_ids
    }
    
    delete_test, delete_response = run_test(
        "Delete test agents",
        "/agents/bulk-delete",
        method="POST",
        data=delete_data,
        auth=True,
        expected_keys=["message", "deleted_count"]
    )
    
    if delete_test and delete_response:
        deleted_count = delete_response.get("deleted_count", 0)
        if deleted_count == len(test_agent_ids):
            print(f"Successfully deleted all {len(test_agent_ids)} test agents")
            return True
        else:
            print(f"Deleted only {deleted_count} out of {len(test_agent_ids)} test agents")
            return False
    else:
        print("Failed to delete test agents")
        return False

def send_observer_message(message):
    """Send an observer message"""
    if not auth_token:
        print("No auth token available. Cannot send observer message.")
        return None
    
    data = {
        "observer_message": message
    }
    
    observer_test, observer_response = run_test(
        "Send observer message",
        "/observer/send-message",
        method="POST",
        data=data,
        auth=True,
        expected_keys=["message", "agent_responses"]
    )
    
    if observer_test and observer_response:
        return observer_response
    else:
        print("Failed to send observer message")
        return None

def send_observer_message_without_auth(message):
    """Send an observer message without authentication"""
    data = {
        "observer_message": message
    }
    
    observer_test, observer_response = run_test(
        "Send observer message without authentication",
        "/observer/send-message",
        method="POST",
        data=data,
        auth=False,
        expected_status=403
    )
    
    return observer_test

def test_observer_message_functionality():
    """Test the fixed observer message functionality"""
    print("\n" + "="*80)
    print("TESTING FIXED OBSERVER MESSAGE FUNCTIONALITY")
    print("="*80)
    
    # Step 1: Login as admin user
    print("\nStep 1: Login as admin user (dino@cytonic.com/Observerinho8)")
    if not login_as_admin():
        print("Cannot proceed with testing without admin login")
        return False
    
    # Step 2: Check current agents for admin user
    print("\nStep 2: Check current agents for admin user")
    admin_agents = get_admin_agents()
    
    if not admin_agents:
        print("No agents found for admin user")
        return False
    
    print("\nAdmin user's agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 3: Clean up any test agents
    print("\nStep 3: Clean up any test agents")
    clean_up_test_agents()
    
    # Get updated list of agents after cleanup
    admin_agents = get_admin_agents()
    print(f"\nAdmin user now has {len(admin_agents)} agents after cleanup")
    
    print("\nRemaining agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 4: Test the fixed observer message functionality
    print("\nStep 4: Test the fixed observer message functionality")
    message = "hello agents"
    print(f"\nSending observer message: '{message}'")
    
    response = send_observer_message(message)
    
    if not response:
        print("Failed to send observer message")
        return False
    
    # Check agent responses
    agent_responses = response.get("agent_responses", {}).get("messages", [])
    
    # Count agent responses
    agent_response_count = len(agent_responses) - 1  # Subtract 1 for the observer message
    print(f"Received responses from {agent_response_count} agents")
    
    # Compare with number of agents for the admin user
    if agent_response_count == len(admin_agents):
        print("✅ Number of responses matches number of admin user's agents")
    else:
        print(f"❌ Number of responses ({agent_response_count}) does not match number of admin user's agents ({len(admin_agents)})")
        print("This suggests the observer message endpoint is not properly filtering agents by user_id")
    
    # Check for natural and conversational responses
    print("\nChecking for natural and conversational responses:")
    robotic_phrases = ["understood", "acknowledges", "acknowledge", "received", "directive", "instruction"]
    natural_phrases = ["hello", "hi", "hey", "good to hear", "greetings"]
    
    robotic_responses = 0
    natural_responses = 0
    
    print("\nResponding agents:")
    for i, msg in enumerate(agent_responses):
        if i == 0:  # Skip observer message
            continue
        
        agent_name = msg.get('agent_name', '')
        agent_message = msg.get('message', '')
        print(f"  - {agent_name}: {agent_message}")
        
        # Check for robotic phrases
        if any(phrase in agent_message.lower() for phrase in robotic_phrases):
            robotic_responses += 1
            print(f"    ❌ Response contains robotic phrases")
        
        # Check for natural phrases
        if any(phrase in agent_message.lower() for phrase in natural_phrases):
            natural_responses += 1
            print(f"    ✅ Response contains natural greeting phrases")
    
    print(f"\nNatural responses: {natural_responses}/{agent_response_count}")
    print(f"Robotic responses: {robotic_responses}/{agent_response_count}")
    
    # Step 5: Test authentication requirement
    print("\nStep 5: Test authentication requirement")
    auth_required = send_observer_message_without_auth("This should fail")
    
    if auth_required:
        print("✅ Observer message endpoint correctly requires authentication")
    else:
        print("❌ Observer message endpoint is not properly enforcing authentication")
    
    # Print summary
    print("\n" + "="*80)
    print("FIXED OBSERVER MESSAGE FUNCTIONALITY TEST SUMMARY")
    print("="*80)
    
    print("1. User data isolation:")
    if agent_response_count == len(admin_agents):
        print("   ✅ Only the admin user's agents respond to observer messages")
    else:
        print("   ❌ User data isolation is not working properly")
    
    print("\n2. Natural and conversational responses:")
    if robotic_responses == 0:
        print("   ✅ No robotic 'Understood. [Agent Name] acknowledges...' responses")
    else:
        print("   ❌ Some responses still contain robotic phrases")
    
    if natural_responses > 0:
        print("   ✅ Agents respond with natural greetings like 'Hello! Good to hear from you'")
    else:
        print("   ❌ No natural greeting responses found")
    
    print("\n3. Authentication requirement:")
    if auth_required:
        print("   ✅ Authentication is now required for observer messages")
    else:
        print("   ❌ Authentication is not properly enforced")
    
    return True

if __name__ == "__main__":
    test_observer_message_functionality()
    print_summary()