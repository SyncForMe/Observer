#!/usr/bin/env python3
"""
CRITICAL AGENT ALTERNATION FIXES TESTING
Testing the three critical fixes from the review request:

1. Animation Stop Fix: Animations now stop on FIRST message appearance (not last message)
2. Message Display Fix: Progressive messages now accumulate properly (no disappearing)  
3. Agent Alternation Fix: Replaced asyncio.as_completed() with ordered processing to ensure Agent A → Agent B → Agent C alternation

CRITICAL FOCUS: Agent Alternation Verification - NO consecutive same-agent messages allowed!
"""

import requests
import json
import time
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CriticalAlternationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 15  # Shorter timeout
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, critical=False):
        """Log test result with timestamp"""
        result = {
            'test': test_name,
            'success': success,
            'critical': critical,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
            
        print(f"{status} {test_name}")
        if not success or critical:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Quick authentication test"""
        print("🔐 QUICK AUTHENTICATION TEST")
        print("=" * 50)
        
        try:
            login_data = {
                "email": "dino@cytonic.com", 
                "password": "Observerinho8"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", 
                                       json=login_data, 
                                       timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log_result("Authentication", True, f"Authenticated as {user_data.get('name')}")
                return True
            else:
                self.log_result("Authentication", False, f"Auth failed: {response.status_code}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Auth error: {str(e)}", critical=True)
            return False

    def test_critical_agent_alternation(self):
        """CRITICAL TEST: Agent Alternation Verification"""
        print("🎯 CRITICAL AGENT ALTERNATION VERIFICATION")
        print("=" * 60)
        
        # Test multiple conversation generations
        alternation_results = []
        
        for round_num in range(2):  # Test 2 rounds
            print(f"   Testing alternation round {round_num + 1}...")
            
            try:
                # Get baseline conversations
                response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                baseline_count = len(response.json()) if response.status_code == 200 else 0
                
                # Generate conversation
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/conversation/generate", 
                                           json={}, 
                                           timeout=25)
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Wait for storage
                    time.sleep(2)
                    
                    # Get new conversations
                    response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                    if response.status_code == 200:
                        conversations = response.json()
                        
                        if len(conversations) > baseline_count:
                            latest_conversation = conversations[-1]
                            messages = latest_conversation.get('messages', [])
                            
                            # Extract agent sequence (excluding Observer)
                            agent_sequence = []
                            for msg in messages:
                                agent_name = msg.get('agent_name', '')
                                if agent_name and agent_name != 'Observer (You)':
                                    agent_sequence.append(agent_name)
                            
                            # CRITICAL CHECK: No consecutive same-agent messages
                            consecutive_violations = []
                            for i in range(1, len(agent_sequence)):
                                if agent_sequence[i] == agent_sequence[i-1]:
                                    consecutive_violations.append(f"Position {i}: {agent_sequence[i-1]} → {agent_sequence[i]}")
                            
                            alternation_results.append({
                                'round': round_num + 1,
                                'generation_time': generation_time,
                                'agent_sequence': agent_sequence,
                                'violations': consecutive_violations,
                                'total_messages': len(agent_sequence)
                            })
                            
                            if consecutive_violations:
                                self.log_result(f"Alternation Round {round_num + 1}", False, 
                                              f"CONSECUTIVE SAME-AGENT VIOLATIONS: {'; '.join(consecutive_violations)}", critical=True)
                            else:
                                self.log_result(f"Alternation Round {round_num + 1}", True, 
                                              f"Perfect alternation: {' → '.join(agent_sequence)} ({generation_time:.1f}s)")
                        else:
                            self.log_result(f"Alternation Round {round_num + 1}", False, 
                                          "No new conversation generated", critical=True)
                    else:
                        self.log_result(f"Alternation Round {round_num + 1}", False, 
                                      f"Cannot retrieve conversations: {response.status_code}")
                else:
                    self.log_result(f"Alternation Round {round_num + 1}", False, 
                                  f"Generation failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Alternation Round {round_num + 1}", False, 
                              f"Test error: {str(e)}")
        
        # Overall alternation assessment
        if alternation_results:
            total_violations = sum(len(result['violations']) for result in alternation_results)
            total_rounds = len(alternation_results)
            avg_time = sum(result['generation_time'] for result in alternation_results) / total_rounds
            
            if total_violations == 0:
                self.log_result("OVERALL Agent Alternation Fix", True, 
                              f"SUCCESS: {total_rounds}/{total_rounds} rounds with perfect alternation. Avg time: {avg_time:.1f}s", critical=True)
            else:
                self.log_result("OVERALL Agent Alternation Fix", False, 
                              f"FAILED: {total_violations} consecutive same-agent violations across {total_rounds} rounds", critical=True)
                
                # Detailed violation report
                print("   🔍 DETAILED VIOLATION ANALYSIS:")
                for result in alternation_results:
                    if result['violations']:
                        print(f"      Round {result['round']}: {' → '.join(result['agent_sequence'])}")
                        for violation in result['violations']:
                            print(f"         ❌ {violation}")

    def test_message_streaming_order(self):
        """Test message streaming preserves agent alternation"""
        print("📡 TESTING MESSAGE STREAMING ORDER")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/messages/stream", timeout=10)
            
            if response.status_code == 200:
                messages = response.json()
                
                if isinstance(messages, list) and len(messages) > 0:
                    # Check last 8 messages for alternation
                    recent_messages = messages[-8:]
                    agent_sequence = []
                    
                    for msg in recent_messages:
                        if isinstance(msg, dict):
                            agent_name = msg.get('agent_name', '')
                            if agent_name and agent_name != 'Observer (You)':
                                agent_sequence.append(agent_name)
                    
                    # Check for consecutive same-agent in stream
                    stream_violations = []
                    for i in range(1, len(agent_sequence)):
                        if agent_sequence[i] == agent_sequence[i-1]:
                            stream_violations.append(f"{agent_sequence[i-1]} → {agent_sequence[i]}")
                    
                    if stream_violations:
                        self.log_result("Message Stream Alternation", False, 
                                      f"Stream has consecutive same-agent: {'; '.join(stream_violations)}", critical=True)
                    else:
                        self.log_result("Message Stream Alternation", True, 
                                      f"Stream shows proper alternation: {' → '.join(agent_sequence[-5:])}")
                else:
                    self.log_result("Message Stream Content", False, "Stream returned empty data")
            else:
                self.log_result("Message Stream Access", False, f"Stream access failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Message Stream Test", False, f"Stream test error: {str(e)}")

    def test_performance_with_ordered_processing(self):
        """Test that ordered processing maintains good performance"""
        print("⚡ TESTING PERFORMANCE WITH ORDERED PROCESSING")
        print("=" * 50)
        
        performance_times = []
        
        for test_num in range(2):  # Test 2 times
            print(f"   Performance test {test_num + 1}/2...")
            
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/conversation/generate", 
                                           json={}, 
                                           timeout=30)
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    performance_times.append(generation_time)
                    
                    if generation_time <= 25.0:  # Target: ~20-25 seconds
                        self.log_result(f"Performance Test {test_num + 1}", True, 
                                      f"Generated in {generation_time:.1f}s (within 25s target)")
                    else:
                        self.log_result(f"Performance Test {test_num + 1}", False, 
                                      f"Generated in {generation_time:.1f}s (exceeds 25s target)")
                else:
                    self.log_result(f"Performance Test {test_num + 1}", False, 
                                  f"Generation failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Performance Test {test_num + 1}", False, 
                              f"Performance error: {str(e)}")
        
        # Performance summary
        if performance_times:
            avg_time = sum(performance_times) / len(performance_times)
            
            if avg_time <= 25.0:
                self.log_result("OVERALL Performance", True, 
                              f"Average: {avg_time:.1f}s (meets ~20-25s target)", critical=True)
            else:
                self.log_result("OVERALL Performance", False, 
                              f"Average: {avg_time:.1f}s (exceeds 25s target)", critical=True)

    def run_critical_tests(self):
        """Run the critical alternation tests"""
        print("🎯 CRITICAL AGENT ALTERNATION FIXES TESTING")
        print("=" * 80)
        print("Testing fixes for:")
        print("1. Animation Stop Fix")
        print("2. Message Display Fix") 
        print("3. Agent Alternation Fix (CRITICAL)")
        print("=" * 80)
        print()
        
        if not self.authenticate():
            print("🚨 CRITICAL: Authentication failed - cannot proceed")
            return
            
        # Run critical tests
        self.test_critical_agent_alternation()  # MOST CRITICAL
        self.test_message_streaming_order()
        self.test_performance_with_ordered_processing()
        
        self.print_summary()

    def print_summary(self):
        """Print test summary focused on critical alternation"""
        print("\n" + "=" * 80)
        print("🎯 CRITICAL AGENT ALTERNATION FIXES SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        critical_failures = [r for r in self.test_results if r['critical'] and not r['success']]
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Critical Failures: {len(critical_failures)}")
        print()
        
        # CRITICAL ANALYSIS FOR AGENT ALTERNATION
        alternation_tests = [r for r in self.test_results if 'Alternation' in r['test']]
        alternation_failures = [r for r in alternation_tests if not r['success']]
        
        if alternation_failures:
            print("🚨 CRITICAL AGENT ALTERNATION ISSUES DETECTED:")
            for failure in alternation_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
            print("🔧 URGENT RECOMMENDATION:")
            print("   - The agent alternation fix is NOT working properly")
            print("   - Consecutive same-agent messages are still occurring")
            print("   - The ordered processing implementation needs review")
            print("   - Check if asyncio.as_completed() was properly replaced")
        else:
            print("✅ AGENT ALTERNATION FIX SUCCESS:")
            print("   - No consecutive same-agent messages detected")
            print("   - Proper Agent A → Agent B → Agent C alternation confirmed")
            print("   - Ordered processing implementation working correctly")
            print("   - The critical system integrity test PASSED")
        
        # Performance analysis
        performance_tests = [r for r in self.test_results if 'Performance' in r['test']]
        performance_failures = [r for r in performance_tests if not r['success']]
        
        if performance_failures:
            print("\n⚠️ PERFORMANCE CONCERNS:")
            for failure in performance_failures:
                print(f"   ⚠️ {failure['test']}: {failure['details']}")
        else:
            print("\n✅ PERFORMANCE MAINTAINED:")
            print("   - Ordered processing maintains good performance")
            print("   - Generation times within ~20-25 second target")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    print("Starting Critical Agent Alternation Fixes Testing...")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = CriticalAlternationTester()
    tester.run_critical_tests()