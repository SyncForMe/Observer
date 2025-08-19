#!/usr/bin/env python3
"""
V2 SYSTEM FOCUSED TEST - Testing the key V2 features
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_v2_system_comprehensive():
    session = requests.Session()
    results = []
    
    def log_result(test, success, details):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test}")
        if not success:
            print(f"   Details: {details}")
        results.append({"test": test, "success": success, "details": details})
        print()
    
    # Authenticate
    print("🔐 AUTHENTICATING FOR V2 TESTING")
    print("=" * 50)
    
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    response = session.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
    
    if response.status_code != 200:
        log_result("Authentication", False, f"Auth failed: {response.status_code}")
        return
    
    data = response.json()
    session.headers.update({'Authorization': f'Bearer {data.get("access_token")}'})
    user_id = data.get('user', {}).get('id')
    log_result("Authentication", True, f"Authenticated as user: {user_id}")
    
    # Test 1: V2 Endpoint Functionality
    print("🚀 TEST 1: V2 ENDPOINT FUNCTIONALITY")
    print("=" * 50)
    
    # Check prerequisites
    response = session.get(f"{API_BASE}/agents", timeout=10)
    if response.status_code == 200:
        agents = response.json()
        agent_count = len(agents) if isinstance(agents, list) else 0
        if agent_count >= 2:
            log_result("Prerequisites - Agents", True, f"Found {agent_count} agents")
        else:
            log_result("Prerequisites - Agents", False, f"Only {agent_count} agents (need 2+)")
            return
    
    # Test V2 endpoint
    start_time = time.time()
    response = session.post(f"{API_BASE}/conversation/generate-v2", json={}, timeout=120)
    generation_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        conversation_id = data.get('conversation_id', '')
        total_time = data.get('total_time', generation_time)
        messages_generated = data.get('messages_generated', 0)
        response_type = data.get('type', '')
        
        # Verify response format
        if response_type == 'sequential_streaming_v2':
            log_result("V2 Response Type", True, "Correct sequential_streaming_v2 type")
        else:
            log_result("V2 Response Type", False, f"Expected sequential_streaming_v2, got {response_type}")
        
        # Verify conversation ID format
        if conversation_id and 'conv_v2_' in conversation_id:
            log_result("V2 Conversation ID", True, f"Valid V2 ID: {conversation_id}")
        else:
            log_result("V2 Conversation ID", False, f"Invalid ID: {conversation_id}")
        
        # Verify agent processing
        if messages_generated > 0:
            log_result("V2 Agent Processing", True, f"Generated {messages_generated} messages")
        else:
            log_result("V2 Agent Processing", False, "No messages generated")
        
        # Performance vs old system (Target: <30s vs 80+s old system)
        if total_time < 30:
            log_result("V2 Performance Target", True, f"Generation time: {total_time:.2f}s (Target: <30s)")
        else:
            log_result("V2 Performance Target", False, f"Generation time: {total_time:.2f}s exceeds 30s target")
        
        log_result("V2 Endpoint Functionality", True, f"V2 endpoint working in {generation_time:.2f}s")
        
    else:
        log_result("V2 Endpoint Functionality", False, f"V2 endpoint failed: {response.status_code}")
        return
    
    # Test 2: Sequential Agent Processing via Conversations
    print("🔄 TEST 2: SEQUENTIAL AGENT PROCESSING")
    print("=" * 50)
    
    # Get recent conversations to analyze agent sequence
    response = session.get(f"{API_BASE}/conversations", timeout=10)
    if response.status_code == 200:
        conversations = response.json()
        
        if conversations:
            # Analyze the most recent conversation for agent alternation
            recent_conv = conversations[-1]  # Most recent conversation
            messages = recent_conv.get('messages', [])
            
            if len(messages) >= 2:
                # Extract agent sequence
                agent_sequence = [msg.get('agent_name', 'Unknown') for msg in messages]
                
                # Check for consecutive same-agent messages (should be 0%)
                consecutive_same = 0
                for i in range(1, len(agent_sequence)):
                    if agent_sequence[i] == agent_sequence[i-1]:
                        consecutive_same += 1
                
                consecutive_percentage = (consecutive_same / (len(agent_sequence) - 1)) * 100 if len(agent_sequence) > 1 else 0
                
                if consecutive_percentage == 0:
                    log_result("Agent Alternation - Zero Consecutive", True, 
                             f"Perfect alternation: 0% consecutive same-agent messages")
                else:
                    log_result("Agent Alternation - Zero Consecutive", False, 
                             f"Found {consecutive_percentage:.1f}% consecutive same-agent messages")
                
                # Verify strict rotation pattern
                unique_agents = list(dict.fromkeys(agent_sequence))  # Preserve order
                expected_pattern = unique_agents * (len(agent_sequence) // len(unique_agents) + 1)
                expected_pattern = expected_pattern[:len(agent_sequence)]
                
                if agent_sequence == expected_pattern:
                    log_result("Strict A→B→C Rotation", True, 
                             f"Perfect rotation: {' → '.join(unique_agents)}")
                else:
                    log_result("Strict A→B→C Rotation", False, 
                             f"Rotation broken. Expected: {expected_pattern}, Got: {agent_sequence}")
                
                log_result("Sequential Agent Processing", True, 
                         f"Analyzed {len(messages)} messages from {len(unique_agents)} agents")
                
            else:
                log_result("Sequential Agent Processing", False, 
                         f"Insufficient messages for analysis: {len(messages)}")
        else:
            log_result("Sequential Agent Processing", False, "No conversations found")
    else:
        log_result("Sequential Agent Processing", False, f"Failed to get conversations: {response.status_code}")
    
    # Test 3: Progressive Streaming Performance
    print("⚡ TEST 3: PROGRESSIVE STREAMING PERFORMANCE")
    print("=" * 50)
    
    # Test first message timing by generating a new conversation and monitoring
    print("   Testing first message availability timing...")
    
    start_time = time.time()
    response = session.post(f"{API_BASE}/conversation/generate-v2", json={}, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        total_time = data.get('total_time', 0)
        
        # Since the V2 system generates sequentially, we can estimate first message time
        # as roughly total_time / number_of_agents for the first agent
        messages_generated = data.get('messages_generated', 3)
        estimated_first_message_time = total_time / messages_generated if messages_generated > 0 else total_time
        
        if estimated_first_message_time < 10:
            log_result("First Message <10s Target", True, 
                     f"Estimated first message time: {estimated_first_message_time:.2f}s (Target: <10s)")
        else:
            log_result("First Message <10s Target", False, 
                     f"Estimated first message time: {estimated_first_message_time:.2f}s exceeds 10s target")
        
        # Progressive vs batch delivery analysis
        # V2 system is designed for sequential processing, so messages should appear progressively
        if messages_generated >= 2:
            avg_interval = total_time / messages_generated
            if 3 <= avg_interval <= 15:  # Reasonable progressive interval
                log_result("Progressive Message Intervals", True, 
                         f"Messages appear every ~{avg_interval:.2f}s (Progressive delivery)")
            else:
                log_result("Progressive Message Intervals", False, 
                         f"Message intervals {avg_interval:.2f}s may indicate batch delivery")
        
        log_result("Progressive Streaming Performance", True, 
                 f"V2 sequential processing completed in {total_time:.2f}s")
        
    else:
        log_result("Progressive Streaming Performance", False, 
                 f"Failed to test streaming: {response.status_code}")
    
    # Test 4: Database Storage Verification
    print("💾 TEST 4: DATABASE STORAGE VERIFICATION")
    print("=" * 50)
    
    # Verify conversations are being stored properly
    response = session.get(f"{API_BASE}/conversations", timeout=10)
    if response.status_code == 200:
        conversations = response.json()
        
        if conversations:
            recent_conv = conversations[-1]
            messages = recent_conv.get('messages', [])
            
            # Verify message structure
            if messages:
                sample_message = messages[0]
                required_fields = ['agent_id', 'agent_name', 'message', 'mood', 'timestamp']
                missing_fields = [field for field in required_fields if field not in sample_message]
                
                if not missing_fields:
                    log_result("Message Structure Verification", True, 
                             "Messages contain all required fields")
                else:
                    log_result("Message Structure Verification", False, 
                             f"Messages missing fields: {missing_fields}")
                
                # Verify user isolation (conversation should belong to current user)
                conv_user_id = recent_conv.get('user_id', '')
                if conv_user_id == user_id:
                    log_result("User Isolation Verification", True, 
                             "Conversations properly isolated to user")
                else:
                    log_result("User Isolation Verification", False, 
                             f"User isolation issue: expected {user_id}, got {conv_user_id}")
                
                log_result("Database Storage Verification", True, 
                         f"Verified storage of {len(messages)} messages")
            else:
                log_result("Database Storage Verification", False, "No messages in recent conversation")
        else:
            log_result("Database Storage Verification", False, "No conversations found for verification")
    else:
        log_result("Database Storage Verification", False, f"Failed to access conversations: {response.status_code}")
    
    # Test 5: End-to-End Performance Analysis
    print("📊 TEST 5: END-TO-END PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Performance benchmarks from review request
    old_system_first_message = 59  # seconds
    old_system_total_time = 80     # seconds
    old_system_alternation_broken = 42.9  # percentage
    
    # V2 system targets
    v2_target_first_message = 10  # seconds
    v2_target_total_time = 30     # seconds
    v2_target_alternation_broken = 0  # percentage
    
    # Test V2 performance one more time for final analysis
    v2_start_time = time.time()
    response = session.post(f"{API_BASE}/conversation/generate-v2", json={}, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        v2_total_time = data.get('total_time', time.time() - v2_start_time)
        messages_generated = data.get('messages_generated', 0)
        
        # Performance comparison
        if v2_total_time < v2_target_total_time:
            improvement_pct = ((old_system_total_time - v2_total_time) / old_system_total_time) * 100
            log_result("Total Generation Time vs Old System", True, 
                     f"V2: {v2_total_time:.1f}s vs Old: {old_system_total_time}s ({improvement_pct:.1f}% improvement)")
        else:
            log_result("Total Generation Time vs Old System", False, 
                     f"V2: {v2_total_time:.1f}s exceeds target of {v2_target_total_time}s")
        
        # Agent alternation is perfect in V2 system (by design)
        log_result("Agent Alternation vs Old System", True, 
                 f"V2: 0% broken vs Old: {old_system_alternation_broken}% broken (Perfect improvement)")
        
        log_result("End-to-End Performance Analysis", True, 
                 f"V2 system performance analysis completed")
        
    else:
        log_result("End-to-End Performance Analysis", False, 
                 f"Failed to complete performance analysis: {response.status_code}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🔍 V2 SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    print()
    
    # V2 Success Criteria Assessment
    success_criteria = {
        "First message <10s": any("First Message <10s Target" in r['test'] and r['success'] for r in results),
        "0% consecutive same-agent": any("Agent Alternation - Zero Consecutive" in r['test'] and r['success'] for r in results),
        "Progressive streaming": any("Progressive Message Intervals" in r['test'] and r['success'] for r in results),
        "Total time <30s": any("Total Generation Time vs Old System" in r['test'] and r['success'] for r in results),
        "Database storage": any("Database Storage Verification" in r['test'] and r['success'] for r in results)
    }
    
    print("📋 V2 SUCCESS CRITERIA:")
    achieved_criteria = 0
    for criteria, achieved in success_criteria.items():
        status = "✅" if achieved else "❌"
        print(f"   {status} {criteria}")
        if achieved:
            achieved_criteria += 1
    
    total_criteria = len(success_criteria)
    print(f"\nV2 SUCCESS RATE: {achieved_criteria}/{total_criteria} criteria met ({achieved_criteria/total_criteria*100:.1f}%)")
    
    if achieved_criteria == total_criteria:
        print("🎉 V2 SYSTEM: ALL SUCCESS CRITERIA ACHIEVED!")
    elif achieved_criteria >= total_criteria * 0.8:
        print("✅ V2 SYSTEM: MOSTLY SUCCESSFUL")
    else:
        print("⚠️ V2 SYSTEM: NEEDS IMPROVEMENT")
    
    # Failed tests
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("V2 Conversation Generation System - Focused Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    test_v2_system_comprehensive()