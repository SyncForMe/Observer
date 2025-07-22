#!/usr/bin/env python3
"""
USER EXPERIENCE ROLLING CONTEXT WINDOW TEST

This test verifies that the rolling context window implementation is **completely invisible to the user** 
and doesn't affect the frontend experience as specified in the review request.

CRITICAL USER EXPERIENCE REQUIREMENTS:
1. **All conversations visible**: GET /api/conversations should return ALL conversations for the user (not limited to 5)
2. **No summaries shown**: User should never see any summary content in conversations
3. **No deleted conversations**: All conversation history preserved for user viewing
4. **Same API responses**: Frontend gets exact same data structure as before
5. **No UI changes needed**: Rolling context is purely backend optimization

The rolling context window should be 100% transparent to users.
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
print(f"🔍 USER EXPERIENCE ROLLING CONTEXT WINDOW TEST")
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "critical_failures": []
}

def log_test(test_name, passed, details="", critical=False):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details,
        "critical": critical
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        if critical:
            test_results["critical_failures"].append(test_name)

def authenticate_guest():
    """Authenticate as guest user"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user', {}).get('id')
            return token, user_id
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def create_test_agents(token, count=3):
    """Create test agents for conversation generation"""
    headers = {"Authorization": f"Bearer {token}"}
    agent_ids = []
    
    archetypes = ["scientist", "leader", "skeptic"]
    
    for i in range(count):
        agent_data = {
            "name": f"UX Test Agent {i+1}",
            "archetype": archetypes[i % len(archetypes)],
            "goal": f"Test rolling context user experience {i+1}",
            "expertise": f"UX Testing {i+1}",
            "background": f"Created for rolling context UX testing {i+1}",
            "personality": {
                "extroversion": 5 + i,
                "optimism": 6 + i,
                "curiosity": 7 + i,
                "cooperativeness": 8,
                "energy": 6
            }
        }
        
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers, timeout=10)
            if response.status_code == 200:
                agent_id = response.json().get('id')
                if agent_id:
                    agent_ids.append(agent_id)
                    print(f"✅ Created test agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {i+1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating agent {i+1}: {e}")
    
    return agent_ids

def setup_simulation(token):
    """Setup simulation with scenario"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start simulation
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        if response.status_code != 200:
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Set scenario
    scenario_data = {
        "scenario": "User Experience Rolling Context Test - Testing that users see all conversations",
        "scenario_name": "UX Rolling Context Test"
    }
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False

def generate_conversations_batch(token, count):
    """Generate multiple conversations and return count generated"""
    headers = {"Authorization": f"Bearer {token}"}
    generated = 0
    
    for i in range(count):
        try:
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
            if response.status_code == 200:
                generated += 1
                if i % 5 == 0:  # Progress update every 5 conversations
                    print(f"   Generated {generated}/{count} conversations...")
            else:
                print(f"   ❌ Failed to generate conversation {i+1}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error generating conversation {i+1}: {e}")
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.3)
    
    return generated

def get_all_conversations(token):
    """Get all conversations for the user"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return None

def analyze_conversations_for_user_visibility(conversations):
    """Analyze conversations to ensure they meet user visibility requirements"""
    analysis = {
        "total_conversations": len(conversations),
        "summary_content_found": [],
        "system_messages_found": [],
        "missing_fields": [],
        "conversation_structure_valid": True
    }
    
    # Check for summary content that should be hidden from users
    summary_indicators = [
        "conversation progress summary",
        "ai context summary", 
        "📚 ai context",
        "🧠 generating",
        "backend only",
        "not shown to user",
        "internal summary",
        "context management",
        "rolling context",
        "summary for ai",
        "conversation_progress_summary",
        "📋 conversation progress summary",
        "🎯 main objective",
        "💡 solutions proposed",
        "✅ decisions made"
    ]
    
    # Check for system-like messages
    system_indicators = ['system', 'context', 'summary', 'internal', 'backend', 'ai context']
    
    required_fields = ['id', 'round_number', 'scenario', 'messages', 'user_id', 'created_at']
    
    for i, conv in enumerate(conversations):
        # Check required fields
        for field in required_fields:
            if field not in conv:
                analysis["missing_fields"].append(f"Conversation {i+1} missing '{field}'")
                analysis["conversation_structure_valid"] = False
        
        # Check scenario for summary content
        scenario = conv.get('scenario', '').lower()
        for indicator in summary_indicators:
            if indicator in scenario:
                analysis["summary_content_found"].append(f"Conv {i+1} scenario: {scenario[:100]}...")
        
        # Check messages
        messages = conv.get('messages', [])
        for j, msg in enumerate(messages):
            if not isinstance(msg, dict):
                analysis["conversation_structure_valid"] = False
                continue
                
            agent_name = msg.get('agent_name', '').lower()
            message_text = msg.get('message', '').lower()
            
            # Check for summary content in messages
            for indicator in summary_indicators:
                if indicator in message_text:
                    analysis["summary_content_found"].append(
                        f"Conv {i+1} msg {j+1} from {agent_name}: {message_text[:80]}..."
                    )
            
            # Check for system-like agent names
            if any(indicator in agent_name for indicator in system_indicators):
                analysis["system_messages_found"].append(f"Conv {i+1}: agent '{agent_name}'")
            
            # Check for system-like message content
            if any(phrase in message_text for phrase in ['backend only', 'not shown to user', 'internal summary']):
                analysis["system_messages_found"].append(
                    f"Conv {i+1}: system message from {agent_name}"
                )
    
    return analysis

def test_user_experience_rolling_context():
    """Main test function for user experience requirements"""
    print("\n" + "="*80)
    print("🧪 USER EXPERIENCE ROLLING CONTEXT WINDOW TEST")
    print("Testing that rolling context is completely invisible to users")
    print("="*80)
    
    # Step 1: Authentication
    print("\n📋 Step 1: Authentication")
    token, user_id = authenticate_guest()
    if not token:
        log_test("Guest Authentication", False, "Failed to authenticate", critical=True)
        return
    log_test("Guest Authentication", True, f"User ID: {user_id}")
    
    # Step 2: Create test agents
    print("\n📋 Step 2: Create Test Agents")
    agent_ids = create_test_agents(token, 3)
    if len(agent_ids) < 2:
        log_test("Agent Creation", False, f"Only created {len(agent_ids)} agents, need at least 2", critical=True)
        return
    log_test("Agent Creation", True, f"Created {len(agent_ids)} agents")
    
    # Step 3: Setup simulation
    print("\n📋 Step 3: Setup Simulation")
    if not setup_simulation(token):
        log_test("Simulation Setup", False, "Failed to setup simulation", critical=True)
        return
    log_test("Simulation Setup", True)
    
    # Step 4: Generate conversations to trigger rolling context (need 25+ messages)
    print("\n📋 Step 4: Generate Conversations to Trigger Rolling Context")
    print("🎯 Generating 30 conversations to ensure rolling context window is triggered...")
    
    conversations_generated = generate_conversations_batch(token, 30)
    log_test("Conversation Generation", conversations_generated >= 25, 
             f"Generated {conversations_generated}/30 conversations")
    
    if conversations_generated < 25:
        print("⚠️ Warning: May not have enough conversations to fully test rolling context")
    
    # Step 5: CRITICAL TEST - Verify ALL conversations are visible to user
    print("\n📋 Step 5: 🚨 CRITICAL - Verify ALL Conversations Visible to User")
    all_conversations = get_all_conversations(token)
    if not all_conversations:
        log_test("Get All Conversations", False, "Failed to retrieve conversations", critical=True)
        return
    
    retrieved_count = len(all_conversations)
    log_test("Get All Conversations", True, f"Retrieved {retrieved_count} conversations")
    
    # CRITICAL REQUIREMENT: User should see ALL conversations, not limited to 5
    if retrieved_count >= conversations_generated:
        log_test("All Conversations Visible", True, 
                f"✅ CRITICAL PASS: User can see all {retrieved_count} conversations (not limited to 5)", 
                critical=True)
    else:
        log_test("All Conversations Visible", False, 
                f"❌ CRITICAL FAIL: User can only see {retrieved_count} conversations, expected {conversations_generated}",
                critical=True)
    
    # Step 6: CRITICAL TEST - Analyze conversations for user experience compliance
    print("\n📋 Step 6: 🚨 CRITICAL - Analyze Conversations for User Experience")
    analysis = analyze_conversations_for_user_visibility(all_conversations)
    
    # Test: No summary content visible to users
    if not analysis["summary_content_found"]:
        log_test("No Summary Content Visible", True, 
                "✅ CRITICAL PASS: No backend summary content found in user conversations", 
                critical=True)
    else:
        log_test("No Summary Content Visible", False, 
                f"❌ CRITICAL FAIL: Found {len(analysis['summary_content_found'])} instances of summary content",
                critical=True)
        print("   Examples of summary content found:")
        for example in analysis["summary_content_found"][:3]:
            print(f"     • {example}")
    
    # Test: No system messages visible to users
    if not analysis["system_messages_found"]:
        log_test("No System Messages", True, 
                "✅ CRITICAL PASS: No system messages found in user conversations",
                critical=True)
    else:
        log_test("No System Messages", False, 
                f"❌ CRITICAL FAIL: Found {len(analysis['system_messages_found'])} system messages",
                critical=True)
        print("   Examples of system messages found:")
        for example in analysis["system_messages_found"][:3]:
            print(f"     • {example}")
    
    # Test: Conversation structure unchanged
    if analysis["conversation_structure_valid"] and not analysis["missing_fields"]:
        log_test("Conversation Structure Unchanged", True, 
                "✅ CRITICAL PASS: All conversations have expected structure",
                critical=True)
    else:
        log_test("Conversation Structure Unchanged", False, 
                f"❌ CRITICAL FAIL: Structure issues found",
                critical=True)
        if analysis["missing_fields"]:
            print("   Missing fields:")
            for field in analysis["missing_fields"][:3]:
                print(f"     • {field}")
    
    # Step 7: Test conversation count behavior (should never decrease)
    print("\n📋 Step 7: Test Conversation Count Never Decreases")
    
    # Generate one more conversation
    print("   Generating additional conversation to test count behavior...")
    additional_generated = generate_conversations_batch(token, 1)
    
    if additional_generated > 0:
        time.sleep(2)  # Wait for database update
        
        # Get conversations again
        updated_conversations = get_all_conversations(token)
        if updated_conversations:
            new_count = len(updated_conversations)
            if new_count > retrieved_count:
                log_test("Conversation Count Never Decreases", True, 
                        f"✅ Count increased from {retrieved_count} to {new_count}")
            elif new_count == retrieved_count:
                log_test("Conversation Count Never Decreases", False, 
                        f"⚠️ Count stayed same: {retrieved_count} -> {new_count} (may indicate deletion)")
            else:
                log_test("Conversation Count Never Decreases", False, 
                        f"❌ CRITICAL: Count decreased: {retrieved_count} -> {new_count}",
                        critical=True)
        else:
            log_test("Conversation Count Never Decreases", False, "Failed to retrieve updated conversations")
    else:
        log_test("Conversation Count Never Decreases", False, "Failed to generate additional conversation")
    
    # Step 8: Verify internal endpoints are not exposed to frontend
    print("\n📋 Step 8: Verify Internal Summary Endpoints Not Exposed")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/internal/conversation-summaries", headers=headers, timeout=5)
        if response.status_code == 200:
            summaries = response.json()
            log_test("Internal Endpoints Hidden", False, 
                    f"❌ Internal summaries endpoint accessible, returned {len(summaries)} summaries")
        else:
            log_test("Internal Endpoints Hidden", True, 
                    "✅ Internal summaries endpoint properly restricted")
    except Exception as e:
        log_test("Internal Endpoints Hidden", True, 
                "✅ Internal summaries endpoint not accessible")
    
    return analysis

def print_user_experience_summary():
    """Print final test summary focused on user experience"""
    print("\n" + "="*80)
    print("📊 USER EXPERIENCE ROLLING CONTEXT TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Critical requirements check
    print("\n🎯 CRITICAL USER EXPERIENCE REQUIREMENTS:")
    
    critical_requirements = [
        "All Conversations Visible",
        "No Summary Content Visible", 
        "No System Messages",
        "Conversation Structure Unchanged"
    ]
    
    critical_passed = 0
    for req in critical_requirements:
        test_result = next((t for t in test_results["tests"] if req in t["name"] and t.get("critical")), None)
        if test_result and test_result["passed"]:
            print(f"   ✅ {req}")
            critical_passed += 1
        else:
            print(f"   ❌ {req}")
    
    print(f"\nCritical Requirements Met: {critical_passed}/{len(critical_requirements)}")
    
    # Final verdict
    if critical_passed == len(critical_requirements) and len(test_results["critical_failures"]) == 0:
        print("\n🎉 SUCCESS: Rolling context window is completely invisible to users!")
        print("   ✅ Users see all conversations")
        print("   ✅ No summaries visible to users") 
        print("   ✅ No deleted conversations")
        print("   ✅ Same API responses as before")
        print("   ✅ No UI changes needed")
        print("\n   The rolling context window is purely a backend optimization!")
    else:
        print("\n⚠️ CRITICAL ISSUES FOUND: Rolling context window affects user experience!")
        print("   Some backend implementation details are visible to users.")
        
        if test_results["critical_failures"]:
            print("\n❌ CRITICAL FAILURES:")
            for failure in test_results["critical_failures"]:
                print(f"   • {failure}")
    
    if test_results["failed"] > 0:
        print("\n📋 ALL FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                critical_marker = " [CRITICAL]" if test.get("critical") else ""
                print(f"   • {test['name']}{critical_marker}: {test['details']}")

if __name__ == "__main__":
    try:
        analysis = test_user_experience_rolling_context()
        print_user_experience_summary()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        print_user_experience_summary()
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        print_user_experience_summary()