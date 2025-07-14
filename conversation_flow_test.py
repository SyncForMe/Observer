#!/usr/bin/env python3
"""
Test script for the complete conversation generation flow after fixing the play button logic.

This test verifies:
1. Guest user authentication and JWT token retrieval
2. Creating at least 2 test agents via POST /api/agents
3. Starting simulation via POST /api/simulation/start
4. Generating conversation via POST /api/conversation/generate
5. Verifying conversations exist via GET /api/conversations
6. Testing multiple conversation generation (2-3 conversations in sequence)
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
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def test_guest_authentication():
    """Test 1: Authenticate as guest user and get valid JWT token"""
    print("\n🔐 Testing Guest Authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                token = data['access_token']
                user_info = data.get('user', {})
                log_test("Guest Authentication", True, f"Token received, User: {user_info.get('email', 'Unknown')}")
                return token, user_info.get('id')
            else:
                log_test("Guest Authentication", False, "No access_token in response")
                return None, None
        else:
            log_test("Guest Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
            return None, None
            
    except Exception as e:
        log_test("Guest Authentication", False, f"Exception: {str(e)}")
        return None, None

def test_create_agents(token):
    """Test 2: Create at least 2 test agents via POST /api/agents"""
    print("\n🤖 Testing Agent Creation...")
    
    if not token:
        log_test("Agent Creation", False, "No authentication token available")
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    created_agents = []
    
    # Agent 1: Scientist
    agent1_data = {
        "name": "Dr. Sarah Chen",
        "archetype": "scientist",
        "goal": "Advance quantum computing research",
        "expertise": "Quantum Physics and Computing",
        "background": "PhD in Quantum Physics from MIT, 10 years research experience",
        "avatar_prompt": "Professional scientist with lab coat"
    }
    
    # Agent 2: Leader
    agent2_data = {
        "name": "Marcus Johnson",
        "archetype": "leader",
        "goal": "Lead successful project implementation",
        "expertise": "Project Management and Leadership",
        "background": "MBA, 15 years leading tech teams",
        "avatar_prompt": "Professional business leader"
    }
    
    # Agent 3: Artist (for multiple conversation testing)
    agent3_data = {
        "name": "Elena Rodriguez",
        "archetype": "artist",
        "goal": "Create innovative user experiences",
        "expertise": "UX Design and Creative Direction",
        "background": "MFA in Design, 8 years in tech industry",
        "avatar_prompt": "Creative designer with artistic flair"
    }
    
    agents_to_create = [agent1_data, agent2_data, agent3_data]
    
    for i, agent_data in enumerate(agents_to_create, 1):
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            
            if response.status_code == 200:
                agent = response.json()
                created_agents.append(agent)
                log_test(f"Create Agent {i} ({agent_data['name']})", True, f"Agent ID: {agent.get('id', 'Unknown')}")
            else:
                log_test(f"Create Agent {i} ({agent_data['name']})", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            log_test(f"Create Agent {i} ({agent_data['name']})", False, f"Exception: {str(e)}")
    
    if len(created_agents) >= 2:
        log_test("Agent Creation (Overall)", True, f"Created {len(created_agents)} agents successfully")
    else:
        log_test("Agent Creation (Overall)", False, f"Only created {len(created_agents)} agents, need at least 2")
    
    return created_agents

def test_start_simulation(token):
    """Test 3: Start simulation via POST /api/simulation/start"""
    print("\n🚀 Testing Simulation Start...")
    
    if not token:
        log_test("Start Simulation", False, "No authentication token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get('is_active', False)
            log_test("Start Simulation", True, f"Simulation active: {is_active}")
            return True
        else:
            log_test("Start Simulation", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Start Simulation", False, f"Exception: {str(e)}")
        return False

def test_generate_conversation(token, conversation_number=1):
    """Test 4: Generate conversation via POST /api/conversation/generate"""
    print(f"\n💬 Testing Conversation Generation #{conversation_number}...")
    
    if not token:
        log_test(f"Generate Conversation #{conversation_number}", False, "No authentication token available")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        if response.status_code == 200:
            conversation = response.json()
            # The API returns the conversation object directly, not wrapped in a 'conversation' key
            if conversation and 'messages' in conversation:
                messages = conversation.get('messages', [])
                log_test(f"Generate Conversation #{conversation_number}", True, 
                        f"Generated conversation with {len(messages)} messages")
                return conversation
            else:
                log_test(f"Generate Conversation #{conversation_number}", False, "Invalid conversation response format")
                return None
        else:
            log_test(f"Generate Conversation #{conversation_number}", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test(f"Generate Conversation #{conversation_number}", False, f"Exception: {str(e)}")
        return None

def test_verify_conversations(token):
    """Test 5: Verify conversations exist via GET /api/conversations"""
    print("\n📋 Testing Conversation Retrieval...")
    
    if not token:
        log_test("Verify Conversations", False, "No authentication token available")
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        
        if response.status_code == 200:
            conversations = response.json()
            if isinstance(conversations, list):
                log_test("Verify Conversations", True, f"Retrieved {len(conversations)} conversations")
                return conversations
            else:
                log_test("Verify Conversations", False, "Response is not a list")
                return []
        else:
            log_test("Verify Conversations", False, f"Status: {response.status_code}, Response: {response.text}")
            return []
            
    except Exception as e:
        log_test("Verify Conversations", False, f"Exception: {str(e)}")
        return []

def test_multiple_conversation_generation(token):
    """Test 6: Test multiple conversation generation (2-3 conversations in sequence)"""
    print("\n🔄 Testing Multiple Conversation Generation...")
    
    if not token:
        log_test("Multiple Conversation Generation", False, "No authentication token available")
        return False
    
    generated_conversations = []
    
    # Generate 3 conversations in sequence
    for i in range(1, 4):
        print(f"\n   Generating conversation {i}/3...")
        conversation = test_generate_conversation(token, i)
        if conversation:
            generated_conversations.append(conversation)
        
        # Small delay between generations
        time.sleep(1)
    
    if len(generated_conversations) >= 2:
        log_test("Multiple Conversation Generation", True, 
                f"Successfully generated {len(generated_conversations)} conversations in sequence")
        return True
    else:
        log_test("Multiple Conversation Generation", False, 
                f"Only generated {len(generated_conversations)} conversations, expected at least 2")
        return False

def test_conversation_consistency(token):
    """Additional Test: Verify conversation consistency and data integrity"""
    print("\n🔍 Testing Conversation Consistency...")
    
    if not token:
        log_test("Conversation Consistency", False, "No authentication token available")
        return False
    
    # Get all conversations
    conversations = test_verify_conversations(token)
    
    if not conversations:
        log_test("Conversation Consistency", False, "No conversations to verify")
        return False
    
    consistent = True
    issues = []
    
    for i, conv in enumerate(conversations):
        # Check required fields
        if 'id' not in conv:
            issues.append(f"Conversation {i+1}: Missing 'id' field")
            consistent = False
        
        if 'messages' not in conv:
            issues.append(f"Conversation {i+1}: Missing 'messages' field")
            consistent = False
        elif not isinstance(conv['messages'], list):
            issues.append(f"Conversation {i+1}: 'messages' is not a list")
            consistent = False
        elif len(conv['messages']) == 0:
            issues.append(f"Conversation {i+1}: Empty messages list")
            consistent = False
        
        if 'user_id' not in conv:
            issues.append(f"Conversation {i+1}: Missing 'user_id' field")
            consistent = False
    
    if consistent:
        log_test("Conversation Consistency", True, f"All {len(conversations)} conversations have consistent structure")
    else:
        log_test("Conversation Consistency", False, f"Issues found: {'; '.join(issues)}")
    
    return consistent

def cleanup_test_data(token):
    """Clean up test data after testing"""
    print("\n🧹 Cleaning up test data...")
    
    if not token:
        print("   No token available for cleanup")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get all agents
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            
            # Delete test agents
            for agent in agents:
                if agent.get('name') in ['Dr. Sarah Chen', 'Marcus Johnson', 'Elena Rodriguez']:
                    delete_response = requests.delete(f"{API_URL}/agents/{agent['id']}", headers=headers)
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted agent: {agent['name']}")
                    else:
                        print(f"   ❌ Failed to delete agent: {agent['name']}")
        
        # Clear conversations (via simulation start which clears conversations)
        requests.post(f"{API_URL}/simulation/start", headers=headers)
        requests.post(f"{API_URL}/simulation/pause", headers=headers)
        print("   ✅ Cleared conversations")
        
    except Exception as e:
        print(f"   ❌ Cleanup error: {str(e)}")

def main():
    """Main test execution"""
    print("🧪 CONVERSATION GENERATION FLOW TEST")
    print("=" * 50)
    print("Testing the complete conversation generation flow after fixing the play button logic")
    print()
    
    # Test 1: Authentication
    token, user_id = test_guest_authentication()
    
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print_summary()
        return
    
    # Test 2: Create agents
    agents = test_create_agents(token)
    
    if len(agents) < 2:
        print("\n❌ Cannot proceed without at least 2 agents")
        print_summary()
        return
    
    # Test 3: Start simulation
    simulation_started = test_start_simulation(token)
    
    if not simulation_started:
        print("\n❌ Cannot proceed without active simulation")
        print_summary()
        return
    
    # Test 4: Generate first conversation
    first_conversation = test_generate_conversation(token, 1)
    
    # Test 5: Verify conversations exist
    conversations = test_verify_conversations(token)
    
    # Test 6: Multiple conversation generation
    multiple_success = test_multiple_conversation_generation(token)
    
    # Additional test: Conversation consistency
    consistency_check = test_conversation_consistency(token)
    
    # Cleanup
    cleanup_test_data(token)
    
    # Print summary
    print_summary()

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  • {test['name']}: {test['details']}")
    
    print("\n🎯 CONCLUSION:")
    if test_results["failed"] == 0:
        print("✅ All tests passed! The conversation generation flow is working correctly.")
        print("✅ Backend conversation generation is consistently working.")
        print("✅ Users should see conversations when clicking the play button.")
    else:
        print("❌ Some tests failed. The conversation generation flow needs attention.")
        print("❌ Check the failed tests above for specific issues.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()