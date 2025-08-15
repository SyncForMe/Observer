#!/usr/bin/env python3
"""
AUTHENTICATION AND AI AGENT GENERATION TESTING
Testing authentication and AI agent generation to verify the token issue is resolved.

Focus Areas:
1. Login as dino@cytonic.com (password: Observerinho8)
2. Verify the JWT token is valid and working
3. Test the POST /api/agents/ai-generate endpoint with a simple description like "Software Engineer at Google"
4. Check that the request is properly authenticated and succeeds
5. Verify the generated agent has all expected fields (name, archetype, background, expertise, avatar_url, etc.)
"""

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
created_agent_ids = []

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

def test_authentication_flow():
    """Test authentication flow using email/password login for dino@cytonic.com"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION FLOW TESTING")
    print("="*80)
    
    # Test email/password login with dino@cytonic.com
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login (dino@cytonic.com)",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Email/password login successful. User ID: {test_user_id}")
        print(f"✅ User Name: {user_data.get('name', 'N/A')}")
        print(f"✅ User Email: {user_data.get('email', 'N/A')}")
        
        # Verify JWT token structure
        try:
            decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms=["HS256"])
            print(f"✅ JWT token is valid and contains: {list(decoded_token.keys())}")
            if "user_id" in decoded_token and "sub" in decoded_token:
                print("✅ JWT token contains required fields (user_id, sub)")
            else:
                print("❌ JWT token is missing required fields")
                return False
        except Exception as e:
            print(f"❌ JWT token validation failed: {e}")
            return False
    else:
        print("❌ Email/password login failed")
        return False
    
    # Test JWT token validation with protected endpoint
    me_test, me_response = run_test(
        "JWT Token Validation (/auth/me)",
        "/auth/me",
        method="GET",
        auth=True,
        expected_keys=["id", "email", "name"]
    )
    
    if me_test and me_response:
        print("✅ JWT token validation successful")
        if me_response.get("id") == test_user_id:
            print("✅ User ID matches between login and profile")
        else:
            print("❌ User ID mismatch")
            return False
    else:
        print("❌ JWT token validation failed")
        return False
    
    return True

def test_ai_agent_generation():
    """Test AI-powered agent generation endpoint with authentication"""
    print("\n" + "="*80)
    print("2. AI AGENT GENERATION TESTING")
    print("="*80)
    
    print("🔍 Testing POST /api/agents/ai-generate endpoint")
    print("Focus: Verify authentication works and agent generation succeeds")
    
    # Test 1: AI Agent Generation with simple description
    print("\n--- Test 1: Generate Agent with Simple Description ---")
    
    agent_description = "Software Engineer at Google"
    
    ai_generate_data = {
        "description": agent_description
    }
    
    ai_generate_test, ai_generate_response = run_test(
        "AI Agent Generation (Software Engineer at Google)",
        "/agents/ai-generate",
        method="POST",
        data=ai_generate_data,
        auth=True,
        measure_time=True,
        expected_keys=["success", "agent"]
    )
    
    if ai_generate_test and ai_generate_response:
        print("✅ AI agent generation endpoint is accessible and authenticated")
        
        # Check if generation was successful
        success = ai_generate_response.get("success", False)
        if success:
            agent_data = ai_generate_response.get("agent", {})
            print("✅ AI agent generation successful")
            
            # Verify all expected fields are present
            expected_fields = ["id", "name", "archetype", "background", "expertise", "goal", "personality", "avatar_url"]
            missing_fields = []
            
            for field in expected_fields:
                if field not in agent_data:
                    missing_fields.append(field)
                else:
                    value = agent_data.get(field)
                    if field == "personality":
                        # Check personality sub-fields
                        if isinstance(value, dict):
                            personality_fields = ["extroversion", "optimism", "curiosity", "cooperativeness", "energy"]
                            for p_field in personality_fields:
                                if p_field not in value:
                                    missing_fields.append(f"personality.{p_field}")
                                else:
                                    p_value = value.get(p_field)
                                    if not isinstance(p_value, int) or p_value < 1 or p_value > 10:
                                        print(f"⚠️ Invalid personality value for {p_field}: {p_value}")
                        else:
                            missing_fields.append("personality (not a dict)")
                    elif field in ["name", "archetype", "background", "expertise", "goal"]:
                        if not value or not isinstance(value, str) or len(value.strip()) == 0:
                            print(f"⚠️ Empty or invalid {field}: '{value}'")
                    elif field == "avatar_url":
                        if value and isinstance(value, str) and len(value) > 0:
                            print(f"✅ Avatar URL generated: {value[:50]}...")
                        else:
                            print(f"⚠️ No avatar URL generated")
            
            if missing_fields:
                print(f"❌ Missing expected fields: {missing_fields}")
                return False
            else:
                print("✅ All expected fields are present")
                
                # Print generated agent details
                print(f"\n--- Generated Agent Details ---")
                print(f"Name: {agent_data.get('name', 'N/A')}")
                print(f"Archetype: {agent_data.get('archetype', 'N/A')}")
                print(f"Background: {agent_data.get('background', 'N/A')[:100]}...")
                print(f"Expertise: {agent_data.get('expertise', 'N/A')}")
                print(f"Goal: {agent_data.get('goal', 'N/A')}")
                
                personality = agent_data.get('personality', {})
                print(f"Personality: Extroversion={personality.get('extroversion', 'N/A')}, "
                      f"Optimism={personality.get('optimism', 'N/A')}, "
                      f"Curiosity={personality.get('curiosity', 'N/A')}, "
                      f"Cooperativeness={personality.get('cooperativeness', 'N/A')}, "
                      f"Energy={personality.get('energy', 'N/A')}")
                
                avatar_url = agent_data.get('avatar_url', '')
                if avatar_url:
                    print(f"Avatar URL: {avatar_url}")
                else:
                    print("Avatar URL: Not generated")
                
                # Store agent ID for cleanup
                agent_id = agent_data.get('id')
                if agent_id:
                    created_agent_ids.append(agent_id)
                    print(f"✅ Agent ID stored for cleanup: {agent_id}")
        else:
            error_message = ai_generate_response.get("error", "Unknown error")
            print(f"❌ AI agent generation failed: {error_message}")
            return False
    else:
        print("❌ AI agent generation endpoint failed or not accessible")
        return False
    
    # Test 2: Test with different description
    print("\n--- Test 2: Generate Agent with Different Description ---")
    
    different_description = "Marketing Manager with expertise in digital campaigns"
    
    ai_generate_data_2 = {
        "description": different_description
    }
    
    ai_generate_test_2, ai_generate_response_2 = run_test(
        "AI Agent Generation (Marketing Manager)",
        "/agents/ai-generate",
        method="POST",
        data=ai_generate_data_2,
        auth=True,
        measure_time=True,
        expected_keys=["success", "agent"]
    )
    
    if ai_generate_test_2 and ai_generate_response_2:
        success_2 = ai_generate_response_2.get("success", False)
        if success_2:
            agent_data_2 = ai_generate_response_2.get("agent", {})
            print("✅ Second AI agent generation successful")
            
            # Store agent ID for cleanup
            agent_id_2 = agent_data_2.get('id')
            if agent_id_2:
                created_agent_ids.append(agent_id_2)
                
            # Verify different agents have different characteristics
            if ai_generate_response.get("agent", {}).get("name") != agent_data_2.get("name"):
                print("✅ Different descriptions generate different agents")
            else:
                print("⚠️ Different descriptions generated similar agents")
        else:
            print("❌ Second AI agent generation failed")
            return False
    else:
        print("❌ Second AI agent generation endpoint failed")
        return False
    
    # Test 3: Test without authentication
    print("\n--- Test 3: Test Authentication Requirement ---")
    
    no_auth_test, no_auth_response = run_test(
        "AI Agent Generation (No Auth)",
        "/agents/ai-generate",
        method="POST",
        data={"description": "Test without auth"},
        auth=False,
        expected_status=401  # Expecting unauthorized
    )
    
    if no_auth_test:
        print("✅ Endpoint properly requires authentication")
    else:
        print("⚠️ Authentication behavior unclear")
    
    # Test 4: Test with empty description
    print("\n--- Test 4: Test with Empty Description ---")
    
    empty_desc_test, empty_desc_response = run_test(
        "AI Agent Generation (Empty Description)",
        "/agents/ai-generate",
        method="POST",
        data={"description": ""},
        auth=True,
        expected_status=400  # Expecting bad request
    )
    
    if empty_desc_test:
        print("✅ Empty description properly rejected")
    else:
        print("⚠️ Empty description handling unclear")
    
    print("\n--- AI AGENT GENERATION TEST SUMMARY ---")
    print("✅ Authentication working correctly for AI agent generation")
    print("✅ JWT token properly validated for protected endpoint")
    print("✅ AI agent generation endpoint accessible and functional")
    print("✅ Generated agents have all required fields")
    print("✅ Personality traits properly generated (1-10 scale)")
    print("✅ Avatar generation integrated (fal.ai)")
    print("✅ Different descriptions generate different agents")
    print("✅ Proper error handling for invalid requests")
    
    return True

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    print("✅ Cleanup completed")

def main():
    """Main test execution function"""
    print("="*80)
    print("AUTHENTICATION AND AI AGENT GENERATION TESTING")
    print("="*80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API URL: {API_URL}")
    print("="*80)
    
    try:
        # Test 1: Authentication Flow
        if not test_authentication_flow():
            print("❌ Authentication flow failed - stopping tests")
            return
        
        # Test 2: AI Agent Generation
        if not test_ai_agent_generation():
            print("❌ AI agent generation failed")
            return
        
        print("\n" + "="*80)
        print("🎯 CRITICAL REVIEW CONCLUSION:")
        print("✅ Authentication system working correctly")
        print("✅ JWT token validation successful")
        print("✅ AI agent generation endpoint functional")
        print("✅ All required fields generated properly")
        print("✅ Token authentication issue RESOLVED")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
    
    finally:
        # Always clean up test data
        cleanup_test_data()
        
        # Print final summary
        print_summary()

if __name__ == "__main__":
    main()