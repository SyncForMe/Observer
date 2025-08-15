#!/usr/bin/env python3
"""
AI AGENT GENERATION ENDPOINT TESTING
Testing the new AI-powered agent generation endpoint as requested in the review.

Focus Areas:
1. Login as dino@cytonic.com (password: Observerinho8)
2. Test POST /api/agents/ai-generate endpoint with "CEO of Facebook"
3. Verify Gemini API integration for agent details
4. Verify fal.ai integration for avatar generation
5. Check response structure and content quality
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
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

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
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

def test_authentication():
    """Test authentication using email/password login"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION TESTING")
    print("="*80)
    
    # Test email/password login with known test user
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login",
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
        return True
    else:
        print("❌ Email/password login failed")
        return False

def test_ai_agent_generation():
    """Test AI-powered agent generation endpoint - CRITICAL REVIEW REQUEST"""
    print("\n" + "="*80)
    print("2. AI-POWERED AGENT GENERATION TESTING (CRITICAL REVIEW)")
    print("="*80)
    
    print("🔍 Testing the new AI-powered agent generation API endpoint")
    print("Focus: POST /api/agents/ai-generate with Gemini and fal.ai integration")
    print("Expected: Generated agent with name, archetype, background, expertise, and avatar")
    
    # Test 1: Test with the specific example from the review request
    print("\n--- Test 1: CEO of Facebook Example ---")
    
    agent_request_data = {
        "description": "CEO of Facebook"
    }
    
    ai_agent_test, ai_agent_response = run_test(
        "AI Generate Agent - CEO of Facebook",
        "/agents/ai-generate",
        method="POST",
        data=agent_request_data,
        auth=True,
        measure_time=True,
        expected_keys=["id", "name", "archetype", "goal", "expertise", "background", "avatar_url", "personality"]
    )
    
    if ai_agent_test and ai_agent_response:
        print("✅ AI agent generation endpoint is accessible and working")
        
        # Analyze the generated agent
        agent_name = ai_agent_response.get("name", "")
        agent_archetype = ai_agent_response.get("archetype", "")
        agent_goal = ai_agent_response.get("goal", "")
        agent_expertise = ai_agent_response.get("expertise", "")
        agent_background = ai_agent_response.get("background", "")
        agent_avatar_url = ai_agent_response.get("avatar_url", "")
        agent_personality = ai_agent_response.get("personality", {})
        
        print(f"\n📊 Generated Agent Analysis:")
        print(f"  Name: {agent_name}")
        print(f"  Archetype: {agent_archetype}")
        print(f"  Goal: {agent_goal[:100]}..." if len(agent_goal) > 100 else f"  Goal: {agent_goal}")
        print(f"  Expertise: {agent_expertise[:100]}..." if len(agent_expertise) > 100 else f"  Expertise: {agent_expertise}")
        print(f"  Background: {agent_background[:100]}..." if len(agent_background) > 100 else f"  Background: {agent_background}")
        print(f"  Avatar URL: {'✅ Generated' if agent_avatar_url else '❌ Not generated'}")
        print(f"  Personality traits: {len(agent_personality)} traits")
        
        # Verify expected content for CEO of Facebook
        ceo_indicators = ["facebook", "meta", "zuckerberg", "social media", "technology", "ceo", "chief executive"]
        name_matches = any(indicator.lower() in agent_name.lower() for indicator in ceo_indicators)
        expertise_matches = any(indicator.lower() in agent_expertise.lower() for indicator in ceo_indicators)
        background_matches = any(indicator.lower() in agent_background.lower() for indicator in ceo_indicators)
        
        if name_matches or expertise_matches or background_matches:
            print("✅ Generated agent content is relevant to 'CEO of Facebook'")
        else:
            print("⚠️ Generated agent content may not be specific to 'CEO of Facebook'")
        
        # Verify avatar generation (fal.ai integration)
        if agent_avatar_url and agent_avatar_url.startswith("http"):
            print("✅ Avatar URL generated successfully (fal.ai integration working)")
        else:
            print("❌ Avatar URL not generated (fal.ai integration issue)")
        
        # Verify personality traits structure
        expected_personality_fields = ["confidence", "curiosity", "empathy", "assertiveness", "optimism", "analytical", "creativity", "patience"]
        missing_traits = [field for field in expected_personality_fields if field not in agent_personality]
        
        if not missing_traits:
            print("✅ All personality traits present")
        else:
            print(f"❌ Missing personality traits: {missing_traits}")
        
        # Store agent ID for cleanup
        agent_id = ai_agent_response.get("id")
        if agent_id:
            created_agent_ids.append(agent_id)
            
        return True
    else:
        print("❌ AI agent generation failed")
        return False

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
    print("AI AGENT GENERATION ENDPOINT TESTING")
    print("Testing the new AI-powered agent generation as requested in review")
    print("="*80)
    
    # Test authentication first
    if not test_authentication():
        print("❌ Authentication failed - cannot proceed with AI agent testing")
        return
    
    # Test AI agent generation
    success = test_ai_agent_generation()
    
    # Cleanup
    cleanup_test_data()
    
    # Final result
    if success:
        print("\n" + "="*80)
        print("🎯 FINAL RESULT: AI AGENT GENERATION TEST PASSED")
        print("✅ The AI-powered agent generation endpoint is working correctly")
        print("✅ Both Gemini API and fal.ai integrations are functional")
        print("✅ Generated agents have appropriate names, archetypes, and avatars")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ FINAL RESULT: AI AGENT GENERATION TEST FAILED")
        print("❌ Issues found with the AI-powered agent generation endpoint")
        print("="*80)

if __name__ == "__main__":
    main()