#!/usr/bin/env python3
"""
CRITICAL SYSTEM BREAKDOWN INVESTIGATION
Backend Testing for AI Agent Simulation Platform

URGENT INVESTIGATION: Complete system failure reported
- Two animation systems fighting for space
- No messages generated when clicking play (waited 1 minute)

This test focuses on the 5 critical areas from the review request:
1. Conversation Generation System Status
2. Auto-Conversation System Status  
3. Backend State Investigation
4. Authentication & Authorization
5. System Dependencies
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

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
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
        """Test 4: Authentication & Authorization - Test if authentication is working"""
        print("🔐 TESTING AUTHENTICATION & AUTHORIZATION")
        print("=" * 60)
        
        try:
            # Test email/password login (as mentioned in test_result.md)
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
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log_result("Email/Password Authentication", True, 
                              f"Successfully authenticated as {user_data.get('name', 'Unknown')}. User ID: {self.user_id}", critical=True)
                return True
            else:
                self.log_result("Email/Password Authentication", False, 
                              f"Auth failed with status {response.status_code}: {response.text}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Email/Password Authentication", False, 
                          f"Auth exception: {str(e)}", critical=True)
            return False

    def test_system_dependencies(self):
        """Test 5: System Dependencies - Test if all required services are running"""
        print("🔧 TESTING SYSTEM DEPENDENCIES")
        print("=" * 60)
        
        # Test API usage endpoint (indicates backend services are running)
        try:
            response = self.session.get(f"{API_BASE}/usage", timeout=10)
            if response.status_code == 200:
                usage_data = response.json()
                self.log_result("API Usage Service", True, 
                              f"Usage service responding. Requests: {usage_data.get('requests', 0)}")
            else:
                self.log_result("API Usage Service", False, 
                              f"Usage service failed: {response.status_code}")
        except Exception as e:
            self.log_result("API Usage Service", False, f"Usage service error: {str(e)}")

        # Test database connectivity (via agents endpoint)
        try:
            response = self.session.get(f"{API_BASE}/agents", timeout=10)
            if response.status_code in [200, 401, 403]:  # Any response means DB is connected
                self.log_result("Database Connectivity", True, 
                              f"Database responding via agents endpoint")
            else:
                self.log_result("Database Connectivity", False, 
                              f"Database connection issue: {response.status_code}")
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Database error: {str(e)}")

    def test_backend_state(self):
        """Test 3: Backend State Investigation - Check simulation state and data availability"""
        print("🔍 TESTING BACKEND STATE INVESTIGATION")
        print("=" * 60)
        
        # Test simulation state endpoint
        try:
            response = self.session.get(f"{API_BASE}/simulation/state", timeout=10)
            if response.status_code == 200:
                state = response.json()
                is_active = state.get('is_active', False)
                scenario = state.get('scenario', '')
                current_day = state.get('current_day', 0)
                
                self.log_result("Simulation State Access", True, 
                              f"State accessible. Active: {is_active}, Scenario: '{scenario}', Day: {current_day}")
                
                # Check if simulation thinks it's active
                if is_active:
                    self.log_result("Simulation Active State", True, 
                                  "Backend thinks simulation is active")
                else:
                    self.log_result("Simulation Active State", False, 
                                  "Backend shows simulation as inactive", critical=True)
                    
            else:
                self.log_result("Simulation State Access", False, 
                              f"Cannot access simulation state: {response.status_code}", critical=True)
                
        except Exception as e:
            self.log_result("Simulation State Access", False, 
                          f"Simulation state error: {str(e)}", critical=True)

        # Test agents availability
        try:
            response = self.session.get(f"{API_BASE}/agents", timeout=10)
            if response.status_code == 200:
                agents = response.json()
                agent_count = len(agents) if isinstance(agents, list) else 0
                
                if agent_count >= 2:
                    self.log_result("Agent Availability", True, 
                                  f"Found {agent_count} agents (minimum 2 required)")
                else:
                    self.log_result("Agent Availability", False, 
                                  f"Only {agent_count} agents found (need at least 2)", critical=True)
                    
            else:
                self.log_result("Agent Availability", False, 
                              f"Cannot access agents: {response.status_code}", critical=True)
                
        except Exception as e:
            self.log_result("Agent Availability", False, 
                          f"Agents access error: {str(e)}", critical=True)

    def test_conversation_generation(self):
        """Test 1: Conversation Generation System Status - Test if conversation generation works at all"""
        print("💬 TESTING CONVERSATION GENERATION SYSTEM")
        print("=" * 60)
        
        # First, get baseline conversation count
        try:
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            if response.status_code == 200:
                conversations = response.json()
                baseline_count = len(conversations) if isinstance(conversations, list) else 0
                self.log_result("Conversation History Access", True, 
                              f"Baseline conversations: {baseline_count}")
            else:
                baseline_count = 0
                self.log_result("Conversation History Access", False, 
                              f"Cannot access conversations: {response.status_code}")
        except Exception as e:
            baseline_count = 0
            self.log_result("Conversation History Access", False, 
                          f"Conversation access error: {str(e)}")

        # Test manual conversation generation
        print("   Testing manual conversation generation...")
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/conversation/generate", 
                                       json={}, 
                                       timeout=120)  # 2 minute timeout
            
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Manual Conversation Generation", True, 
                              f"Generated in {generation_time:.1f}s. Response: {str(data)[:200]}...")
                
                # Check if conversation was actually created
                time.sleep(2)  # Brief wait for database consistency
                response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                if response.status_code == 200:
                    conversations = response.json()
                    new_count = len(conversations) if isinstance(conversations, list) else 0
                    
                    if new_count > baseline_count:
                        self.log_result("Conversation Database Storage", True, 
                                      f"Conversation count increased: {baseline_count} → {new_count}")
                    else:
                        self.log_result("Conversation Database Storage", False, 
                                      f"No new conversations in database: {baseline_count} → {new_count}", critical=True)
                        
            else:
                self.log_result("Manual Conversation Generation", False, 
                              f"Generation failed: {response.status_code} - {response.text}", critical=True)
                
        except requests.exceptions.Timeout:
            self.log_result("Manual Conversation Generation", False, 
                          "Conversation generation timed out after 2 minutes", critical=True)
        except Exception as e:
            self.log_result("Manual Conversation Generation", False, 
                          f"Generation error: {str(e)}", critical=True)

    def test_auto_conversation_system(self):
        """Test 2: Auto-Conversation System Status - Test if auto-conversation system works"""
        print("🤖 TESTING AUTO-CONVERSATION SYSTEM")
        print("=" * 60)
        
        # Check auto-mode status
        try:
            response = self.session.get(f"{API_BASE}/simulation/auto-status", timeout=10)
            if response.status_code == 200:
                auto_status = response.json()
                auto_conversations = auto_status.get('auto_conversations', False)
                
                self.log_result("Auto-Mode Status Check", True, 
                              f"Auto-conversations enabled: {auto_conversations}")
                
                if not auto_conversations:
                    # Try to enable auto-mode
                    print("   Attempting to enable auto-mode...")
                    response = self.session.post(f"{API_BASE}/simulation/toggle-auto-mode", 
                                               json={"auto_conversations": True}, 
                                               timeout=10)
                    
                    if response.status_code == 200:
                        self.log_result("Auto-Mode Activation", True, 
                                      "Successfully enabled auto-conversations")
                    else:
                        self.log_result("Auto-Mode Activation", False, 
                                      f"Failed to enable auto-mode: {response.status_code}")
                        
            else:
                self.log_result("Auto-Mode Status Check", False, 
                              f"Cannot check auto-status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Auto-Mode Status Check", False, 
                          f"Auto-status error: {str(e)}")

        # Test simulation start (should trigger auto-conversation)
        print("   Testing simulation start with auto-conversation...")
        try:
            # Get baseline conversation count
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            baseline_count = len(response.json()) if response.status_code == 200 else 0
            
            # Start simulation
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/simulation/start", 
                                       json={}, 
                                       timeout=120)
            
            if response.status_code == 200:
                start_duration = time.time() - start_time
                self.log_result("Simulation Start", True, 
                              f"Simulation started in {start_duration:.1f}s")
                
                # Wait and check if conversations were generated
                print("   Waiting 10 seconds for auto-conversation...")
                time.sleep(10)
                
                response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                if response.status_code == 200:
                    conversations = response.json()
                    new_count = len(conversations) if isinstance(conversations, list) else 0
                    
                    if new_count > baseline_count:
                        self.log_result("Auto-Conversation Generation", True, 
                                      f"Auto-conversations working: {baseline_count} → {new_count}")
                    else:
                        self.log_result("Auto-Conversation Generation", False, 
                                      f"No auto-conversations generated: {baseline_count} → {new_count}", critical=True)
                        
            else:
                self.log_result("Simulation Start", False, 
                              f"Simulation start failed: {response.status_code} - {response.text}", critical=True)
                
        except requests.exceptions.Timeout:
            self.log_result("Simulation Start", False, 
                          "Simulation start timed out", critical=True)
        except Exception as e:
            self.log_result("Simulation Start", False, 
                          f"Simulation start error: {str(e)}", critical=True)

    def test_play_button_simulation(self):
        """Simulate the exact play button workflow that's failing"""
        print("▶️ TESTING PLAY BUTTON WORKFLOW SIMULATION")
        print("=" * 60)
        
        # Step 1: Check if we have agents and scenario (prerequisites)
        try:
            # Check agents
            response = self.session.get(f"{API_BASE}/agents", timeout=10)
            if response.status_code == 200:
                agents = response.json()
                agent_count = len(agents) if isinstance(agents, list) else 0
                
                if agent_count < 2:
                    self.log_result("Play Button Prerequisites", False, 
                                  f"Insufficient agents for play button: {agent_count} (need 2+)", critical=True)
                    return
                    
            # Check scenario
            response = self.session.get(f"{API_BASE}/simulation/state", timeout=10)
            if response.status_code == 200:
                state = response.json()
                scenario = state.get('scenario', '')
                
                if not scenario or scenario.strip() == '':
                    self.log_result("Play Button Prerequisites", False, 
                                  "No scenario set for play button", critical=True)
                    return
                    
            self.log_result("Play Button Prerequisites", True, 
                          f"Prerequisites met: {agent_count} agents, scenario: '{scenario[:50]}...'")
            
        except Exception as e:
            self.log_result("Play Button Prerequisites", False, 
                          f"Prerequisites check failed: {str(e)}", critical=True)
            return

        # Step 2: Simulate clicking play button (start simulation)
        print("   Simulating play button click...")
        try:
            baseline_conversations = 0
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            if response.status_code == 200:
                conversations = response.json()
                baseline_conversations = len(conversations) if isinstance(conversations, list) else 0

            # Click play (start simulation)
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/simulation/start", json={}, timeout=120)
            
            if response.status_code == 200:
                play_duration = time.time() - start_time
                self.log_result("Play Button Response", True, 
                              f"Play button responded in {play_duration:.1f}s")
                
                # Step 3: Wait 1 minute (as user reported) and check for messages
                print("   Waiting 60 seconds for messages (as user reported)...")
                time.sleep(60)
                
                # Check if any conversations were generated
                response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                if response.status_code == 200:
                    conversations = response.json()
                    final_count = len(conversations) if isinstance(conversations, list) else 0
                    
                    if final_count > baseline_conversations:
                        self.log_result("Play Button Message Generation", True, 
                                      f"Messages generated after play: {baseline_conversations} → {final_count}")
                    else:
                        self.log_result("Play Button Message Generation", False, 
                                      f"NO MESSAGES GENERATED after 60s: {baseline_conversations} → {final_count}", critical=True)
                        
                        # This matches the user's exact complaint!
                        print("   🚨 CRITICAL: This matches user's report - 'No messages generated when clicking play'")
                        
            else:
                self.log_result("Play Button Response", False, 
                              f"Play button failed: {response.status_code} - {response.text}", critical=True)
                
        except Exception as e:
            self.log_result("Play Button Response", False, 
                          f"Play button error: {str(e)}", critical=True)

    def run_all_tests(self):
        """Run all critical system tests"""
        print("🚨 CRITICAL SYSTEM BREAKDOWN INVESTIGATION")
        print("=" * 80)
        print("User Report: Two animation systems fighting + No messages when clicking play")
        print("=" * 80)
        print()
        
        # Test in order of criticality
        if not self.authenticate():
            print("🚨 CRITICAL: Authentication failed - cannot proceed with tests")
            return
            
        self.test_system_dependencies()
        self.test_backend_state()
        self.test_conversation_generation()
        self.test_auto_conversation_system()
        self.test_play_button_simulation()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🔍 CRITICAL SYSTEM BREAKDOWN INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        critical_failures = [r for r in self.test_results if r['critical'] and not r['success']]
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Critical Failures: {len(critical_failures)}")
        print()
        
        if critical_failures:
            print("🚨 CRITICAL FAILURES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Specific analysis for user's issues
        print("📋 USER ISSUE ANALYSIS:")
        
        # Check for conversation generation issues
        conv_gen_tests = [r for r in self.test_results if 'Conversation' in r['test'] and 'Generation' in r['test']]
        if any(not r['success'] for r in conv_gen_tests):
            print("   🚨 CONFIRMED: Conversation generation system is broken")
        else:
            print("   ✅ Conversation generation system appears functional")
            
        # Check for play button issues
        play_tests = [r for r in self.test_results if 'Play Button' in r['test']]
        if any(not r['success'] for r in play_tests):
            print("   🚨 CONFIRMED: Play button workflow is broken")
        else:
            print("   ✅ Play button workflow appears functional")
            
        # Check for auto-conversation issues
        auto_tests = [r for r in self.test_results if 'Auto' in r['test']]
        if any(not r['success'] for r in auto_tests):
            print("   🚨 CONFIRMED: Auto-conversation system has issues")
        else:
            print("   ✅ Auto-conversation system appears functional")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    print("Starting Critical System Breakdown Investigation...")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = BackendTester()
    tester.run_all_tests()