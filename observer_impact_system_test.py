#!/usr/bin/env python3
"""
Comprehensive Observer Impact System Testing
Tests the complete Observer Impact System implementation including:
1. Observer Message Impact Classification
2. Observer Guidance Storage
3. Observer Guidance Integration in Conversations
4. Observer Guidance Retrieval
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
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🚀 Testing Observer Impact System at: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test_result(test_name, passed, details=""):
    """Log test result"""
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

def authenticate_guest():
    """Authenticate as guest user"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user', {}).get('id')
            print(f"✅ Guest authentication successful. User ID: {user_id}")
            return token, user_id
        else:
            print(f"❌ Guest authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def setup_test_agents(auth_token):
    """Create test agents for the simulation"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create test agents
    test_agents = [
        {
            "name": "Dr. Security Expert",
            "archetype": "scientist",
            "goal": "Ensure maximum security and data protection",
            "expertise": "Cybersecurity and encryption protocols",
            "background": "Expert in secure communication systems"
        },
        {
            "name": "Prof. Budget Analyst", 
            "archetype": "researcher",
            "goal": "Provide accurate cost analysis and budget planning",
            "expertise": "Financial analysis and cost optimization",
            "background": "Specialist in technology project budgeting"
        },
        {
            "name": "Engineer Solutions",
            "archetype": "leader", 
            "goal": "Design practical implementation solutions",
            "expertise": "System architecture and implementation",
            "background": "Lead engineer for complex technical projects"
        }
    ]
    
    created_agents = []
    for agent_data in test_agents:
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if response.status_code == 200:
                agent = response.json()
                created_agents.append(agent)
                print(f"✅ Created agent: {agent_data['name']}")
            else:
                print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating agent {agent_data['name']}: {e}")
    
    return created_agents

def test_observer_message_impact_classification(auth_token):
    """Test 1: Observer Message Impact Classification"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Observer Message Impact Classification")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test messages with expected impact levels
    test_messages = [
        {
            "message": "Change our strategy - focus only on security protocols for the device",
            "expected_impact": "high",
            "description": "Strategic direction change"
        },
        {
            "message": "Please provide detailed cost analysis for each proposed solution",
            "expected_impact": "medium", 
            "description": "Specific tactical request"
        },
        {
            "message": "hello agents, how are you doing?",
            "expected_impact": "low",
            "description": "Routine greeting"
        }
    ]
    
    classification_results = []
    
    for test_case in test_messages:
        print(f"\n📝 Testing message: '{test_case['message']}'")
        print(f"   Expected impact: {test_case['expected_impact'].upper()}")
        
        try:
            # Send observer message to trigger classification
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": test_case["message"]},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                observer_impact = data.get('observer_impact', {})
                
                impact_level = observer_impact.get('impact_level', '').lower()
                classification = observer_impact.get('classification', '')
                reasoning = observer_impact.get('reasoning', '')
                
                print(f"   Actual impact: {impact_level.upper()}")
                print(f"   Classification: {classification}")
                print(f"   Reasoning: {reasoning}")
                
                # Check if classification matches expected
                impact_correct = impact_level == test_case['expected_impact']
                has_classification = bool(classification)
                has_reasoning = bool(reasoning)
                
                classification_results.append({
                    "message": test_case["message"],
                    "expected": test_case['expected_impact'],
                    "actual": impact_level,
                    "correct": impact_correct,
                    "classification": classification,
                    "reasoning": reasoning
                })
                
                log_test_result(
                    f"Impact Classification - {test_case['description']}", 
                    impact_correct and has_classification and has_reasoning,
                    f"Expected: {test_case['expected_impact']}, Got: {impact_level}, Classification: {classification}"
                )
                
            else:
                log_test_result(
                    f"Impact Classification - {test_case['description']}", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            log_test_result(
                f"Impact Classification - {test_case['description']}", 
                False,
                f"Exception: {e}"
            )
    
    return classification_results

def test_observer_guidance_storage(auth_token, classification_results):
    """Test 2: Observer Guidance Storage"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Observer Guidance Storage")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Check if high/medium impact messages were stored
    high_medium_messages = [r for r in classification_results if r['actual'] in ['high', 'medium']]
    low_impact_messages = [r for r in classification_results if r['actual'] == 'low']
    
    print(f"📊 Expected stored messages: {len(high_medium_messages)} (high/medium impact)")
    print(f"📊 Expected non-stored messages: {len(low_impact_messages)} (low impact)")
    
    try:
        # Get stored observer guidance
        response = requests.get(f"{API_URL}/observer/guidance", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            stored_guidance = data.get('guidance', [])
            guidance_count = data.get('guidance_count', 0)
            current_scenario = data.get('current_scenario', '')
            
            print(f"✅ Retrieved {guidance_count} stored guidance entries")
            print(f"📍 Current scenario: {current_scenario}")
            
            # Verify high/medium impact messages are stored
            stored_messages = [g.get('observer_message', '') for g in stored_guidance]
            
            high_medium_stored = 0
            for result in high_medium_messages:
                if result['message'] in stored_messages:
                    high_medium_stored += 1
                    print(f"✅ Found stored: '{result['message'][:50]}...'")
                else:
                    print(f"❌ Missing: '{result['message'][:50]}...'")
            
            # Verify low impact messages are NOT stored (performance optimization)
            low_impact_stored = 0
            for result in low_impact_messages:
                if result['message'] in stored_messages:
                    low_impact_stored += 1
                    print(f"⚠️ Unexpectedly stored low impact: '{result['message'][:50]}...'")
            
            # Check metadata completeness
            metadata_complete = True
            for guidance in stored_guidance:
                required_fields = ['user_id', 'observer_message', 'impact_level', 'classification', 'reasoning', 'scenario', 'created_at']
                missing_fields = [field for field in required_fields if not guidance.get(field)]
                if missing_fields:
                    print(f"❌ Missing metadata fields: {missing_fields}")
                    metadata_complete = False
            
            # Test results
            storage_success = (high_medium_stored == len(high_medium_messages))
            optimization_success = (low_impact_stored == 0)  # Low impact should not be stored
            
            log_test_result(
                "High/Medium Impact Storage",
                storage_success,
                f"Stored {high_medium_stored}/{len(high_medium_messages)} high/medium impact messages"
            )
            
            log_test_result(
                "Low Impact Optimization", 
                optimization_success,
                f"Correctly avoided storing {len(low_impact_messages) - low_impact_stored}/{len(low_impact_messages)} low impact messages"
            )
            
            log_test_result(
                "Guidance Metadata Completeness",
                metadata_complete,
                "All stored guidance has complete metadata"
            )
            
            return stored_guidance
            
        else:
            log_test_result(
                "Observer Guidance Retrieval",
                False, 
                f"HTTP {response.status_code}: {response.text}"
            )
            return []
            
    except Exception as e:
        log_test_result(
            "Observer Guidance Storage Test",
            False,
            f"Exception: {e}"
        )
        return []

def test_observer_guidance_integration(auth_token, stored_guidance):
    """Test 3: Observer Guidance Integration in Conversations"""
    print("\n" + "="*80)
    print("🧪 TEST 3: Observer Guidance Integration in Conversations")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    if not stored_guidance:
        log_test_result(
            "Observer Guidance Integration",
            False,
            "No stored guidance available for integration testing"
        )
        return
    
    print(f"📋 Testing integration with {len(stored_guidance)} stored guidance entries")
    
    # Set up simulation scenario
    try:
        # Set scenario
        scenario_response = requests.post(
            f"{API_URL}/simulation/set-scenario",
            json={
                "scenario": "Building a secure communication device with budget constraints",
                "scenario_name": "Secure Device Development"
            },
            headers=headers
        )
        
        if scenario_response.status_code != 200:
            print(f"❌ Failed to set scenario: {scenario_response.status_code}")
            return
        
        # Start simulation
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if start_response.status_code != 200:
            print(f"❌ Failed to start simulation: {start_response.status_code}")
            return
        
        print("✅ Simulation setup complete")
        
        # Generate contextual conversation
        print("\n🗣️ Generating contextual conversation to test guidance integration...")
        
        conversation_response = requests.post(
            f"{API_URL}/conversation/generate",
            headers=headers
        )
        
        if conversation_response.status_code == 200:
            conversation_data = conversation_response.json()
            messages = conversation_data.get('messages', [])
            
            print(f"✅ Generated conversation with {len(messages)} messages")
            
            # Analyze messages for observer guidance references
            guidance_references = 0
            security_focus_count = 0
            budget_analysis_count = 0
            observer_directive_mentions = 0
            
            guidance_keywords = []
            for guidance in stored_guidance:
                message = guidance.get('observer_message', '').lower()
                if 'security' in message or 'encryption' in message:
                    guidance_keywords.extend(['security', 'encryption', 'protection', 'secure'])
                if 'cost' in message or 'budget' in message or 'analysis' in message:
                    guidance_keywords.extend(['cost', 'budget', 'analysis', 'financial'])
            
            for i, message in enumerate(messages):
                agent_name = message.get('agent_name', '')
                message_text = message.get('message', '').lower()
                
                print(f"\n📝 Message {i+1} from {agent_name}:")
                print(f"   {message.get('message', '')[:100]}...")
                
                # Check for guidance keyword references
                keyword_matches = [kw for kw in guidance_keywords if kw in message_text]
                if keyword_matches:
                    guidance_references += 1
                    print(f"   ✅ References guidance keywords: {keyword_matches}")
                
                # Check for specific focus areas from observer guidance
                if any(word in message_text for word in ['security', 'encryption', 'protection', 'secure']):
                    security_focus_count += 1
                    print(f"   🔒 Security focus detected")
                
                if any(word in message_text for word in ['cost', 'budget', 'analysis', 'financial']):
                    budget_analysis_count += 1
                    print(f"   💰 Budget analysis detected")
                
                # Check for explicit observer directive mentions
                if any(phrase in message_text for phrase in ['observer', 'directive', 'guidance', 'priority', 'focus']):
                    observer_directive_mentions += 1
                    print(f"   🎯 Observer directive mention detected")
            
            # Evaluate integration success
            has_guidance_references = guidance_references > 0
            has_security_focus = security_focus_count > 0  # Should be high due to strategic guidance
            has_budget_analysis = budget_analysis_count > 0  # Should be present due to tactical guidance
            has_observer_mentions = observer_directive_mentions > 0
            
            integration_score = sum([has_guidance_references, has_security_focus, has_budget_analysis, has_observer_mentions])
            integration_success = integration_score >= 2  # At least 2 out of 4 criteria
            
            print(f"\n📊 INTEGRATION ANALYSIS:")
            print(f"   Guidance keyword references: {guidance_references}")
            print(f"   Security focus messages: {security_focus_count}")
            print(f"   Budget analysis messages: {budget_analysis_count}")
            print(f"   Observer directive mentions: {observer_directive_mentions}")
            print(f"   Integration score: {integration_score}/4")
            
            log_test_result(
                "Observer Guidance Integration in Conversations",
                integration_success,
                f"Integration score: {integration_score}/4 - Agents referenced observer guidance appropriately"
            )
            
            # Test system message includes guidance section
            # This would require checking the actual system message sent to agents
            # For now, we verify through agent behavior
            
        else:
            log_test_result(
                "Contextual Conversation Generation",
                False,
                f"HTTP {conversation_response.status_code}: {conversation_response.text}"
            )
            
    except Exception as e:
        log_test_result(
            "Observer Guidance Integration Test",
            False,
            f"Exception: {e}"
        )

def test_observer_guidance_retrieval(auth_token):
    """Test 4: Observer Guidance Retrieval Endpoint"""
    print("\n" + "="*80)
    print("🧪 TEST 4: Observer Guidance Retrieval Endpoint")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/observer/guidance", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            required_fields = ['current_scenario', 'guidance_count', 'guidance']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                log_test_result(
                    "Guidance Retrieval Response Structure",
                    False,
                    f"Missing fields: {missing_fields}"
                )
                return
            
            guidance_list = data.get('guidance', [])
            guidance_count = data.get('guidance_count', 0)
            current_scenario = data.get('current_scenario', '')
            
            print(f"✅ Retrieved {guidance_count} guidance entries")
            print(f"📍 Current scenario: {current_scenario}")
            
            # Verify guidance is sorted by impact and recency
            if guidance_list:
                impact_order_correct = True
                recency_order_correct = True
                
                # Check impact level ordering (high should come before medium/low)
                high_indices = [i for i, g in enumerate(guidance_list) if g.get('impact_level') == 'high']
                medium_indices = [i for i, g in enumerate(guidance_list) if g.get('impact_level') == 'medium']
                low_indices = [i for i, g in enumerate(guidance_list) if g.get('impact_level') == 'low']
                
                # High impact should come first
                if high_indices and medium_indices:
                    if max(high_indices) > min(medium_indices):
                        impact_order_correct = False
                
                # Check recency within same impact level
                for impact_level in ['high', 'medium', 'low']:
                    same_impact = [g for g in guidance_list if g.get('impact_level') == impact_level]
                    if len(same_impact) > 1:
                        dates = [g.get('created_at') for g in same_impact]
                        # Should be sorted by recency (newest first)
                        if dates != sorted(dates, reverse=True):
                            recency_order_correct = False
                
                log_test_result(
                    "Guidance Sorting by Impact",
                    impact_order_correct,
                    "High impact guidance appears before medium/low impact"
                )
                
                log_test_result(
                    "Guidance Sorting by Recency",
                    recency_order_correct,
                    "Within same impact level, newer guidance appears first"
                )
                
                # Verify guidance metadata completeness
                metadata_complete = True
                for guidance in guidance_list:
                    required_guidance_fields = ['id', 'user_id', 'observer_message', 'impact_level', 'classification', 'reasoning', 'scenario', 'created_at']
                    missing_guidance_fields = [field for field in required_guidance_fields if not guidance.get(field)]
                    if missing_guidance_fields:
                        print(f"❌ Guidance missing fields: {missing_guidance_fields}")
                        metadata_complete = False
                
                log_test_result(
                    "Guidance Metadata Completeness",
                    metadata_complete,
                    "All guidance entries have complete metadata"
                )
                
                # Test current scenario context inclusion
                scenario_context_included = bool(current_scenario)
                log_test_result(
                    "Current Scenario Context",
                    scenario_context_included,
                    f"Current scenario included: {current_scenario}"
                )
                
            else:
                log_test_result(
                    "Guidance Retrieval Content",
                    True,
                    "No guidance stored yet (expected for clean test environment)"
                )
            
            log_test_result(
                "Observer Guidance Retrieval Endpoint",
                True,
                f"Successfully retrieved {guidance_count} guidance entries with proper structure"
            )
            
        else:
            log_test_result(
                "Observer Guidance Retrieval Endpoint",
                False,
                f"HTTP {response.status_code}: {response.text}"
            )
            
    except Exception as e:
        log_test_result(
            "Observer Guidance Retrieval Test",
            False,
            f"Exception: {e}"
        )

def run_comprehensive_observer_impact_tests():
    """Run all Observer Impact System tests"""
    print("🚀 COMPREHENSIVE OBSERVER IMPACT SYSTEM TESTING")
    print("="*80)
    
    # Step 1: Authenticate
    auth_token, user_id = authenticate_guest()
    if not auth_token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Setup test environment
    print("\n🔧 Setting up test environment...")
    test_agents = setup_test_agents(auth_token)
    if len(test_agents) < 3:
        print("⚠️ Warning: Not all test agents created. Tests may be limited.")
    
    # Step 3: Run Observer Impact System tests
    print("\n🧪 Starting Observer Impact System Tests...")
    
    # Test 1: Observer Message Impact Classification
    classification_results = test_observer_message_impact_classification(auth_token)
    
    # Test 2: Observer Guidance Storage
    stored_guidance = test_observer_guidance_storage(auth_token, classification_results)
    
    # Test 3: Observer Guidance Integration in Conversations
    test_observer_guidance_integration(auth_token, stored_guidance)
    
    # Test 4: Observer Guidance Retrieval
    test_observer_guidance_retrieval(auth_token)
    
    # Final Results
    print("\n" + "="*80)
    print("🏁 OBSERVER IMPACT SYSTEM TEST RESULTS")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print(f"\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"   • {test['name']}: {test['details']}")
    
    print(f"\n🎯 OBSERVER IMPACT SYSTEM STATUS: {'✅ WORKING' if pass_rate >= 80 else '❌ NEEDS ATTENTION'}")
    
    return test_results

if __name__ == "__main__":
    results = run_comprehensive_observer_impact_tests()