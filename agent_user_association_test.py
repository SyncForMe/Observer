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
user1_token = None
user1_id = None
user1_agent_ids = []
user1_email = f"test.user1.{uuid.uuid4()}@example.com"
user1_password = "securePassword123"
user1_name = "Test User 1"

user2_token = None
user2_id = None
user2_agent_ids = []
user2_email = f"test.user2.{uuid.uuid4()}@example.com"
user2_password = "securePassword123"
user2_name = "Test User 2"

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth_token=None, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth_token:
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

def register_user(email, password, name):
    """Register a new test user"""
    register_data = {
        "email": email,
        "password": password,
        "name": name
    }
    
    register_test, register_response = run_test(
        f"Register user {name}",
        "/auth/register",
        method="POST",
        data=register_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if register_test and register_response:
        token = register_response.get("access_token")
        user_data = register_response.get("user", {})
        user_id = user_data.get("id")
        print(f"Registration successful. User ID: {user_id}")
        print(f"JWT Token: {token}")
        return token, user_id
    else:
        print(f"Registration failed for {name}.")
        return None, None

def create_test_agent(name, auth_token, user_id):
    """Create a test agent for the specified user"""
    if not auth_token:
        print("Cannot create test agent without authentication")
        return None
    
    agent_data = {
        "name": name,
        "archetype": "scientist",
        "personality": {
            "extroversion": 5,
            "optimism": 5,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        },
        "goal": f"Test agent for user {user_id}",
        "expertise": "Testing",
        "background": "Created for testing agent bulk delete functionality",
        "memory_summary": "",
        "avatar_prompt": "",
        "avatar_url": ""
    }
    
    create_agent_test, create_agent_response = run_test(
        f"Create Agent: {name}",
        "/agents",
        method="POST",
        data=agent_data,
        auth_token=auth_token,
        expected_keys=["id", "name", "archetype", "goal"]
    )
    
    if create_agent_test and create_agent_response:
        agent_id = create_agent_response.get("id")
        if agent_id:
            print(f"Created test agent with ID: {agent_id}")
            return agent_id
    
    return None

def test_user_association():
    """Test that agents are properly associated with users"""
    global user1_token, user1_id, user2_token, user2_id, user1_agent_ids, user2_agent_ids
    
    print("\n" + "="*80)
    print("TESTING AGENT USER ASSOCIATION")
    print("="*80)
    
    # Step 1: Register two test users
    print("\nStep 1: Register two test users")
    
    user1_token, user1_id = register_user(user1_email, user1_password, user1_name)
    if not user1_token or not user1_id:
        print("❌ Failed to register first test user")
        return False, "Failed to register first test user"
    
    user2_token, user2_id = register_user(user2_email, user2_password, user2_name)
    if not user2_token or not user2_id:
        print("❌ Failed to register second test user")
        return False, "Failed to register second test user"
    
    # Step 2: Create agents for each user
    print("\nStep 2: Create agents for each user")
    
    # Create 3 agents for user 1
    for i in range(3):
        agent_id = create_test_agent(f"User1 Agent {i+1}", user1_token, user1_id)
        if agent_id:
            user1_agent_ids.append(agent_id)
    
    if len(user1_agent_ids) < 3:
        print(f"⚠️ Created only {len(user1_agent_ids)} agents for user 1 instead of 3")
    
    print(f"Created {len(user1_agent_ids)} agents for user 1")
    
    # Create 3 agents for user 2
    for i in range(3):
        agent_id = create_test_agent(f"User2 Agent {i+1}", user2_token, user2_id)
        if agent_id:
            user2_agent_ids.append(agent_id)
    
    if len(user2_agent_ids) < 3:
        print(f"⚠️ Created only {len(user2_agent_ids)} agents for user 2 instead of 3")
    
    print(f"Created {len(user2_agent_ids)} agents for user 2")
    
    # Step 3: Verify each user can only see their own agents
    print("\nStep 3: Verify each user can only see their own agents")
    
    # Get agents for user 1
    get_user1_agents_test, get_user1_agents_response = run_test(
        "Get User 1 Agents",
        "/agents",
        method="GET",
        auth_token=user1_token
    )
    
    if get_user1_agents_test and get_user1_agents_response:
        user1_agent_count = len(get_user1_agents_response)
        print(f"User 1 agent count: {user1_agent_count}")
        
        # Check if all user 1 agent IDs are in the response
        found_ids = [agent.get("id") for agent in get_user1_agents_response]
        missing_ids = [agent_id for agent_id in user1_agent_ids if agent_id not in found_ids]
        
        if missing_ids:
            print(f"❌ {len(missing_ids)} user 1 agents not found in response")
            user1_sees_own = False
        else:
            print("✅ User 1 can see all their own agents")
            user1_sees_own = True
        
        # Check if user 1 can see user 2's agents
        user2_agents_visible = any(agent_id in found_ids for agent_id in user2_agent_ids)
        
        if user2_agents_visible:
            print("❌ User 1 can see user 2's agents")
            user1_isolation = False
        else:
            print("✅ User 1 cannot see user 2's agents")
            user1_isolation = True
    else:
        print("❌ Failed to get user 1's agents")
        user1_sees_own = False
        user1_isolation = False
    
    # Get agents for user 2
    get_user2_agents_test, get_user2_agents_response = run_test(
        "Get User 2 Agents",
        "/agents",
        method="GET",
        auth_token=user2_token
    )
    
    if get_user2_agents_test and get_user2_agents_response:
        user2_agent_count = len(get_user2_agents_response)
        print(f"User 2 agent count: {user2_agent_count}")
        
        # Check if all user 2 agent IDs are in the response
        found_ids = [agent.get("id") for agent in get_user2_agents_response]
        missing_ids = [agent_id for agent_id in user2_agent_ids if agent_id not in found_ids]
        
        if missing_ids:
            print(f"❌ {len(missing_ids)} user 2 agents not found in response")
            user2_sees_own = False
        else:
            print("✅ User 2 can see all their own agents")
            user2_sees_own = True
        
        # Check if user 2 can see user 1's agents
        user1_agents_visible = any(agent_id in found_ids for agent_id in user1_agent_ids)
        
        if user1_agents_visible:
            print("❌ User 2 can see user 1's agents")
            user2_isolation = False
        else:
            print("✅ User 2 cannot see user 1's agents")
            user2_isolation = True
    else:
        print("❌ Failed to get user 2's agents")
        user2_sees_own = False
        user2_isolation = False
    
    # Print summary
    print("\nUSER ASSOCIATION SUMMARY:")
    
    if user1_sees_own and user1_isolation and user2_sees_own and user2_isolation:
        print("✅ Agent user association is working correctly!")
        print("✅ Each user can only see their own agents")
        print("✅ User data isolation is properly implemented")
        return True, "Agent user association is working correctly"
    else:
        issues = []
        if not user1_sees_own:
            issues.append("User 1 cannot see all their own agents")
        if not user1_isolation:
            issues.append("User 1 can see user 2's agents")
        if not user2_sees_own:
            issues.append("User 2 cannot see all their own agents")
        if not user2_isolation:
            issues.append("User 2 can see user 1's agents")
        
        print("❌ Agent user association has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def test_cross_user_agent_deletion():
    """Test that users can only delete their own agents"""
    global user1_token, user1_id, user2_token, user2_id, user1_agent_ids, user2_agent_ids
    
    print("\n" + "="*80)
    print("TESTING CROSS-USER AGENT DELETION")
    print("="*80)
    
    if not user1_token or not user2_token or not user1_agent_ids or not user2_agent_ids:
        print("❌ Cannot test cross-user agent deletion without users and agents")
        return False, "Missing users or agents"
    
    # Step 1: Try to delete user 2's agent with user 1's token
    print("\nStep 1: Try to delete user 2's agent with user 1's token")
    
    if user2_agent_ids:
        user2_agent_id = user2_agent_ids[0]
        
        delete_cross_user_test, delete_cross_user_response = run_test(
            "Delete Another User's Agent",
            f"/agents/{user2_agent_id}",
            method="DELETE",
            auth_token=user1_token,
            expected_status=404
        )
        
        if delete_cross_user_test:
            print("✅ User 1 cannot delete user 2's agent (404 Not Found)")
            individual_cross_protection = True
        else:
            print("❌ User 1 can delete user 2's agent")
            individual_cross_protection = False
    else:
        print("⚠️ No user 2 agents to test with")
        individual_cross_protection = True
    
    # Step 2: Try to bulk delete user 2's agents with user 1's token
    print("\nStep 2: Try to bulk delete user 2's agents with user 1's token")
    
    bulk_delete_data = {
        "agent_ids": user2_agent_ids
    }
    
    bulk_delete_test, bulk_delete_response = run_test(
        "Bulk Delete Another User's Agents",
        "/agents/bulk-delete",
        method="POST",
        data=bulk_delete_data,
        auth_token=user1_token,
        expected_status=404
    )
    
    if bulk_delete_test:
        print("✅ User 1 cannot bulk delete user 2's agents (404 Not Found)")
        bulk_cross_protection = True
    else:
        print("❌ User 1 can bulk delete user 2's agents")
        bulk_cross_protection = False
    
    # Step 3: Verify user 2's agents still exist
    print("\nStep 3: Verify user 2's agents still exist")
    
    get_user2_agents_test, get_user2_agents_response = run_test(
        "Get User 2 Agents After Cross-User Delete Attempts",
        "/agents",
        method="GET",
        auth_token=user2_token
    )
    
    if get_user2_agents_test and get_user2_agents_response:
        user2_agent_count = len(get_user2_agents_response)
        print(f"User 2 agent count: {user2_agent_count}")
        
        # Check if all user 2 agent IDs are still in the response
        found_ids = [agent.get("id") for agent in get_user2_agents_response]
        missing_ids = [agent_id for agent_id in user2_agent_ids if agent_id not in found_ids]
        
        if missing_ids:
            print(f"❌ {len(missing_ids)} user 2 agents missing after cross-user delete attempts")
            agents_preserved = False
        else:
            print("✅ All user 2 agents still exist after cross-user delete attempts")
            agents_preserved = True
    else:
        print("❌ Failed to get user 2's agents")
        agents_preserved = False
    
    # Print summary
    print("\nCROSS-USER AGENT DELETION SUMMARY:")
    
    if individual_cross_protection and bulk_cross_protection and agents_preserved:
        print("✅ Cross-user agent deletion protection is working correctly!")
        print("✅ Users cannot delete other users' agents individually")
        print("✅ Users cannot bulk delete other users' agents")
        print("✅ Agents are preserved after cross-user delete attempts")
        return True, "Cross-user agent deletion protection is working correctly"
    else:
        issues = []
        if not individual_cross_protection:
            issues.append("Users can delete other users' agents individually")
        if not bulk_cross_protection:
            issues.append("Users can bulk delete other users' agents")
        if not agents_preserved:
            issues.append("Agents are not preserved after cross-user delete attempts")
        
        print("❌ Cross-user agent deletion protection has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def test_bulk_delete_with_user_association():
    """Test bulk delete endpoints with proper user association"""
    global user1_token, user1_id, user1_agent_ids
    
    print("\n" + "="*80)
    print("TESTING BULK DELETE WITH USER ASSOCIATION")
    print("="*80)
    
    if not user1_token or not user1_agent_ids:
        print("❌ Cannot test bulk delete without user and agents")
        return False, "Missing user or agents"
    
    # Step 1: Bulk delete half of user 1's agents
    print("\nStep 1: Bulk delete half of user 1's agents")
    
    # Use half of user 1's agents for bulk delete
    delete_ids = user1_agent_ids[:len(user1_agent_ids)//2]
    
    bulk_delete_data = {
        "agent_ids": delete_ids
    }
    
    bulk_delete_test, bulk_delete_response = run_test(
        "Bulk Delete User's Agents",
        "/agents/bulk-delete",
        method="POST",
        data=bulk_delete_data,
        auth_token=user1_token,
        expected_keys=["message", "deleted_count"]
    )
    
    if bulk_delete_test and bulk_delete_response:
        deleted_count = bulk_delete_response.get("deleted_count", 0)
        if deleted_count == len(delete_ids):
            print(f"✅ Successfully deleted {deleted_count} agents")
            bulk_delete_success = True
        else:
            print(f"❌ Deleted {deleted_count} agents instead of {len(delete_ids)}")
            bulk_delete_success = False
    else:
        print("❌ Bulk delete request failed")
        bulk_delete_success = False
    
    # Step 2: Verify deleted agents are gone and remaining agents still exist
    print("\nStep 2: Verify deleted agents are gone and remaining agents still exist")
    
    get_agents_test, get_agents_response = run_test(
        "Get User's Agents After Bulk Delete",
        "/agents",
        method="GET",
        auth_token=user1_token
    )
    
    if get_agents_test and get_agents_response:
        # Check if deleted agents are gone
        found_ids = [agent.get("id") for agent in get_agents_response]
        deleted_agents_found = [agent_id for agent_id in delete_ids if agent_id in found_ids]
        
        if deleted_agents_found:
            print(f"❌ {len(deleted_agents_found)} deleted agents still exist")
            deleted_agents_gone = False
        else:
            print("✅ All deleted agents are gone")
            deleted_agents_gone = True
        
        # Check if remaining agents still exist
        remaining_ids = [agent_id for agent_id in user1_agent_ids if agent_id not in delete_ids]
        missing_remaining = [agent_id for agent_id in remaining_ids if agent_id not in found_ids]
        
        if missing_remaining:
            print(f"❌ {len(missing_remaining)} remaining agents are missing")
            remaining_agents_exist = False
        else:
            print("✅ All remaining agents still exist")
            remaining_agents_exist = True
    else:
        print("❌ Failed to get user's agents after bulk delete")
        deleted_agents_gone = False
        remaining_agents_exist = False
    
    # Step 3: Create more agents for clear all test
    print("\nStep 3: Create more agents for clear all test")
    
    # Create 5 more agents for user 1
    new_agent_ids = []
    for i in range(5):
        agent_id = create_test_agent(f"User1 Clear All Agent {i+1}", user1_token, user1_id)
        if agent_id:
            new_agent_ids.append(agent_id)
    
    if len(new_agent_ids) < 5:
        print(f"⚠️ Created only {len(new_agent_ids)} new agents instead of 5")
    
    print(f"Created {len(new_agent_ids)} new agents for clear all test")
    
    # Step 4: Get all current agents for user 1
    print("\nStep 4: Get all current agents for user 1")
    
    get_all_agents_test, get_all_agents_response = run_test(
        "Get All User's Agents for Clear All",
        "/agents",
        method="GET",
        auth_token=user1_token
    )
    
    if get_all_agents_test and get_all_agents_response:
        all_agent_ids = [agent.get("id") for agent in get_all_agents_response]
        print(f"Found {len(all_agent_ids)} agents for clear all test")
        
        # Step 5: Clear all user 1's agents
        print("\nStep 5: Clear all user 1's agents")
        
        clear_all_data = {
            "agent_ids": all_agent_ids
        }
        
        clear_all_test, clear_all_response = run_test(
            "Clear All User's Agents",
            "/agents/bulk-delete",
            method="POST",
            data=clear_all_data,
            auth_token=user1_token,
            expected_keys=["message", "deleted_count"]
        )
        
        if clear_all_test and clear_all_response:
            deleted_count = clear_all_response.get("deleted_count", 0)
            if deleted_count == len(all_agent_ids):
                print(f"✅ Successfully cleared all {deleted_count} agents")
                clear_all_success = True
            else:
                print(f"❌ Cleared only {deleted_count} agents instead of {len(all_agent_ids)}")
                clear_all_success = False
        else:
            print("❌ Clear all request failed")
            clear_all_success = False
        
        # Step 6: Verify all user 1's agents are gone
        print("\nStep 6: Verify all user 1's agents are gone")
        
        verify_clear_test, verify_clear_response = run_test(
            "Verify All User's Agents Cleared",
            "/agents",
            method="GET",
            auth_token=user1_token
        )
        
        if verify_clear_test and verify_clear_response:
            if len(verify_clear_response) == 0:
                print("✅ Verified all user's agents are cleared")
                all_agents_cleared = True
            else:
                print(f"❌ {len(verify_clear_response)} agents still exist after clear all")
                all_agents_cleared = False
        else:
            print("❌ Failed to verify clear all")
            all_agents_cleared = False
    else:
        print("❌ Failed to get all user's agents for clear all test")
        clear_all_success = False
        all_agents_cleared = False
    
    # Step 7: Verify user 2's agents are not affected
    print("\nStep 7: Verify user 2's agents are not affected")
    
    get_user2_agents_test, get_user2_agents_response = run_test(
        "Get User 2's Agents After User 1 Clear All",
        "/agents",
        method="GET",
        auth_token=user2_token
    )
    
    if get_user2_agents_test and get_user2_agents_response:
        user2_agent_count = len(get_user2_agents_response)
        print(f"User 2 agent count after user 1 clear all: {user2_agent_count}")
        
        # Check if all user 2 agent IDs are still in the response
        found_ids = [agent.get("id") for agent in get_user2_agents_response]
        missing_ids = [agent_id for agent_id in user2_agent_ids if agent_id not in found_ids]
        
        if missing_ids:
            print(f"❌ {len(missing_ids)} user 2 agents missing after user 1 clear all")
            other_user_unaffected = False
        else:
            print("✅ All user 2 agents still exist after user 1 clear all")
            other_user_unaffected = True
    else:
        print("❌ Failed to get user 2's agents")
        other_user_unaffected = False
    
    # Print summary
    print("\nBULK DELETE WITH USER ASSOCIATION SUMMARY:")
    
    if bulk_delete_success and deleted_agents_gone and remaining_agents_exist and clear_all_success and all_agents_cleared and other_user_unaffected:
        print("✅ Bulk delete with user association is working correctly!")
        print("✅ Users can bulk delete their own agents")
        print("✅ Deleted agents are removed from the database")
        print("✅ Remaining agents are preserved")
        print("✅ Users can clear all their agents")
        print("✅ Other users' agents are not affected")
        return True, "Bulk delete with user association is working correctly"
    else:
        issues = []
        if not bulk_delete_success:
            issues.append("Bulk delete request failed")
        if not deleted_agents_gone:
            issues.append("Deleted agents still exist in the database")
        if not remaining_agents_exist:
            issues.append("Remaining agents were incorrectly deleted")
        if not clear_all_success:
            issues.append("Clear all request failed")
        if not all_agents_cleared:
            issues.append("Not all agents were cleared")
        if not other_user_unaffected:
            issues.append("Other users' agents were affected")
        
        print("❌ Bulk delete with user association has issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"issues": issues}

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TESTING AGENT BULK DELETE FUNCTIONALITY WITH USER ASSOCIATION")
    print("="*80)
    
    # Run tests
    test_user_association()
    test_cross_user_agent_deletion()
    test_bulk_delete_with_user_association()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()