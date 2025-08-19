#!/usr/bin/env python3
"""
COMPREHENSIVE INVESTIGATION: MESSAGE TIMING & AGENT ALTERNATION ISSUES

User reports critical issues with the conversation system:
1. First message takes very long time to appear
2. Second message also takes very long time  
3. Subsequent messages: Suddenly 6+ messages appear immediately at once
4. Same agents sending multiple messages in a row (should be round-robin: A→B→C→A→B→C)

This investigation focuses on the 5 critical test areas requested:
- Test 1: Message Generation Timing Analysis
- Test 2: Agent Selection & Alternation Analysis  
- Test 3: Auto-Conversation System Investigation
- Test 4: Progressive Streaming Analysis
- Test 5: Database Message Analysis
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
import sys
import threading
from collections import defaultdict

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class MessageTimingInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.message_timestamps = []
        self.agent_sequence = []
        self.streaming_data = []
        
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
        """Authenticate with the backend"""
        print("🔐 AUTHENTICATING FOR MESSAGE TIMING INVESTIGATION")
        print("=" * 60)
        
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
                
                self.log_result("Authentication", True, 
                              f"Authenticated as {user_data.get('name', 'Unknown')}")
                return True
            else:
                self.log_result("Authentication", False, 
                              f"Auth failed: {response.status_code}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, 
                          f"Auth exception: {str(e)}", critical=True)
            return False

    def test_1_message_generation_timing_analysis(self):
        """Test 1: Message Generation Timing Analysis - Measure exact timing for each message"""
        print("⏱️ TEST 1: MESSAGE GENERATION TIMING ANALYSIS")
        print("=" * 60)
        
        # Get baseline conversation count
        try:
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            baseline_count = len(response.json()) if response.status_code == 200 else 0
            print(f"   Baseline conversations: {baseline_count}")
        except:
            baseline_count = 0
            
        # Clear previous timing data
        self.message_timestamps = []
        
        # Generate multiple conversations and measure timing
        print("   Generating 3 conversations to measure timing patterns...")
        
        for i in range(3):
            print(f"   \n   🔄 Generating conversation {i+1}/3...")
            
            # Record start time
            start_time = time.time()
            
            try:
                response = self.session.post(f"{API_BASE}/conversation/generate", 
                                           json={}, 
                                           timeout=120)
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.message_timestamps.append({
                        'conversation': i+1,
                        'generation_time': generation_time,
                        'timestamp': datetime.now(),
                        'success': True
                    })
                    print(f"      ✅ Conversation {i+1} generated in {generation_time:.2f}s")
                else:
                    self.message_timestamps.append({
                        'conversation': i+1,
                        'generation_time': generation_time,
                        'timestamp': datetime.now(),
                        'success': False,
                        'error': f"Status {response.status_code}"
                    })
                    print(f"      ❌ Conversation {i+1} failed in {generation_time:.2f}s")
                    
            except requests.exceptions.Timeout:
                timeout_time = time.time() - start_time
                self.message_timestamps.append({
                    'conversation': i+1,
                    'generation_time': timeout_time,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': 'Timeout after 120s'
                })
                print(f"      ⏰ Conversation {i+1} timed out after {timeout_time:.2f}s")
                
            except Exception as e:
                error_time = time.time() - start_time
                self.message_timestamps.append({
                    'conversation': i+1,
                    'generation_time': error_time,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': str(e)
                })
                print(f"      ❌ Conversation {i+1} error after {error_time:.2f}s: {str(e)}")
            
            # Wait between generations to avoid rate limiting
            if i < 2:  # Don't wait after the last one
                time.sleep(2)
        
        # Analyze timing patterns
        successful_times = [t['generation_time'] for t in self.message_timestamps if t['success']]
        
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            min_time = min(successful_times)
            max_time = max(successful_times)
            
            # Check for the reported issue: first messages taking very long
            first_message_slow = successful_times[0] > 30 if successful_times else False
            second_message_slow = successful_times[1] > 30 if len(successful_times) > 1 else False
            
            timing_analysis = f"Average: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s"
            
            if first_message_slow or second_message_slow:
                self.log_result("Message Generation Timing", False, 
                              f"CONFIRMED SLOW START: {timing_analysis}. First/second messages taking >30s", critical=True)
            elif avg_time > 20:
                self.log_result("Message Generation Timing", False, 
                              f"SLOW GENERATION: {timing_analysis}. Average >20s indicates performance issues", critical=True)
            else:
                self.log_result("Message Generation Timing", True, 
                              f"Normal timing: {timing_analysis}")
        else:
            self.log_result("Message Generation Timing", False, 
                          "No successful message generations to analyze", critical=True)

    def test_2_agent_selection_alternation_analysis(self):
        """Test 2: Agent Selection & Alternation Analysis - Check if agents alternate properly"""
        print("🤖 TEST 2: AGENT SELECTION & ALTERNATION ANALYSIS")
        print("=" * 60)
        
        # Get current conversations to analyze agent patterns
        try:
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            if response.status_code != 200:
                self.log_result("Agent Alternation Analysis", False, 
                              f"Cannot access conversations: {response.status_code}", critical=True)
                return
                
            conversations = response.json()
            if not conversations:
                self.log_result("Agent Alternation Analysis", False, 
                              "No conversations available for analysis", critical=True)
                return
                
            print(f"   Analyzing {len(conversations)} conversations for agent patterns...")
            
            # Analyze agent sequences across all conversations
            agent_sequences = []
            consecutive_same_agent = 0
            total_messages = 0
            agent_message_counts = defaultdict(int)
            
            for conv in conversations:
                if 'messages' in conv and conv['messages']:
                    conv_sequence = []
                    prev_agent = None
                    
                    for msg in conv['messages']:
                        agent_name = msg.get('agent_name', 'Unknown')
                        agent_id = msg.get('agent_id', 'unknown')
                        
                        conv_sequence.append({
                            'agent_name': agent_name,
                            'agent_id': agent_id,
                            'message': msg.get('message', '')[:100]  # First 100 chars
                        })
                        
                        agent_message_counts[agent_name] += 1
                        total_messages += 1
                        
                        # Check for consecutive same agent (the reported issue)
                        if prev_agent == agent_name:
                            consecutive_same_agent += 1
                            
                        prev_agent = agent_name
                    
                    agent_sequences.append({
                        'conversation_id': conv.get('id', 'unknown'),
                        'round_number': conv.get('round_number', 0),
                        'sequence': conv_sequence
                    })
            
            # Analyze patterns
            unique_agents = len(agent_message_counts)
            consecutive_percentage = (consecutive_same_agent / total_messages * 100) if total_messages > 0 else 0
            
            print(f"   📊 Analysis Results:")
            print(f"      Total messages analyzed: {total_messages}")
            print(f"      Unique agents found: {unique_agents}")
            print(f"      Consecutive same-agent messages: {consecutive_same_agent} ({consecutive_percentage:.1f}%)")
            print(f"      Agent message distribution: {dict(agent_message_counts)}")
            
            # Check for the reported alternation issue
            if consecutive_percentage > 30:  # More than 30% consecutive same-agent messages
                self.log_result("Agent Alternation Pattern", False, 
                              f"CONFIRMED ALTERNATION ISSUE: {consecutive_percentage:.1f}% consecutive same-agent messages (should be <10%)", critical=True)
            elif consecutive_percentage > 15:
                self.log_result("Agent Alternation Pattern", False, 
                              f"POOR ALTERNATION: {consecutive_percentage:.1f}% consecutive same-agent messages", critical=False)
            else:
                self.log_result("Agent Alternation Pattern", True, 
                              f"Good alternation: {consecutive_percentage:.1f}% consecutive same-agent messages")
            
            # Check for agent distribution balance
            if unique_agents >= 2:
                message_counts = list(agent_message_counts.values())
                max_messages = max(message_counts)
                min_messages = min(message_counts)
                imbalance_ratio = max_messages / min_messages if min_messages > 0 else float('inf')
                
                if imbalance_ratio > 3:  # One agent has 3x more messages than another
                    self.log_result("Agent Distribution Balance", False, 
                                  f"UNBALANCED DISTRIBUTION: Ratio {imbalance_ratio:.1f}:1 between most/least active agents")
                else:
                    self.log_result("Agent Distribution Balance", True, 
                                  f"Balanced distribution: Ratio {imbalance_ratio:.1f}:1")
            
            # Store sequence data for further analysis
            self.agent_sequence = agent_sequences
            
        except Exception as e:
            self.log_result("Agent Alternation Analysis", False, 
                          f"Analysis error: {str(e)}", critical=True)

    def test_3_auto_conversation_system_investigation(self):
        """Test 3: Auto-Conversation System Investigation - Check 25-second interval system"""
        print("🔄 TEST 3: AUTO-CONVERSATION SYSTEM INVESTIGATION")
        print("=" * 60)
        
        # Check current auto-conversation status
        try:
            response = self.session.get(f"{API_BASE}/simulation/auto-status", timeout=10)
            if response.status_code == 200:
                auto_status = response.json()
                auto_conversations = auto_status.get('auto_conversations', False)
                interval = auto_status.get('conversation_interval', 0)
                
                print(f"   Current auto-conversation status: {auto_conversations}")
                print(f"   Configured interval: {interval} seconds")
                
                if not auto_conversations:
                    print("   Enabling auto-conversations for testing...")
                    response = self.session.post(f"{API_BASE}/simulation/toggle-auto-mode", 
                                               json={"auto_conversations": True, "conversation_interval": 25}, 
                                               timeout=10)
                    
                    if response.status_code == 200:
                        print("   ✅ Auto-conversations enabled")
                    else:
                        self.log_result("Auto-Conversation Enable", False, 
                                      f"Failed to enable: {response.status_code}")
                        return
                        
            else:
                self.log_result("Auto-Conversation Status", False, 
                              f"Cannot check status: {response.status_code}")
                return
                
        except Exception as e:
            self.log_result("Auto-Conversation Status", False, 
                          f"Status check error: {str(e)}")
            return
        
        # Test the 25-second interval system behavior
        print("   Testing 25-second interval behavior...")
        print("   Starting simulation and monitoring for 90 seconds...")
        
        # Get baseline
        try:
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            baseline_count = len(response.json()) if response.status_code == 200 else 0
        except:
            baseline_count = 0
            
        # Start simulation
        try:
            response = self.session.post(f"{API_BASE}/simulation/start", json={}, timeout=30)
            if response.status_code != 200:
                self.log_result("Auto-Conversation Simulation Start", False, 
                              f"Failed to start: {response.status_code}")
                return
        except Exception as e:
            self.log_result("Auto-Conversation Simulation Start", False, 
                          f"Start error: {str(e)}")
            return
        
        # Monitor for 90 seconds, checking every 10 seconds
        monitoring_data = []
        start_time = time.time()
        
        for check in range(9):  # 9 checks over 90 seconds
            time.sleep(10)
            elapsed = time.time() - start_time
            
            try:
                response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                if response.status_code == 200:
                    current_count = len(response.json())
                    new_messages = current_count - baseline_count
                    
                    monitoring_data.append({
                        'elapsed_seconds': elapsed,
                        'total_conversations': current_count,
                        'new_conversations': new_messages,
                        'timestamp': datetime.now()
                    })
                    
                    print(f"      {elapsed:.0f}s: {current_count} total conversations ({new_messages} new)")
                    
            except Exception as e:
                print(f"      {elapsed:.0f}s: Error checking conversations: {str(e)}")
        
        # Analyze the monitoring data
        if monitoring_data:
            final_new = monitoring_data[-1]['new_conversations']
            expected_intervals = 90 // 25  # Should be 3 intervals in 90 seconds
            
            # Check for message bursting (the reported issue)
            conversation_increases = []
            for i in range(1, len(monitoring_data)):
                increase = monitoring_data[i]['new_conversations'] - monitoring_data[i-1]['new_conversations']
                if increase > 0:
                    conversation_increases.append({
                        'time': monitoring_data[i]['elapsed_seconds'],
                        'increase': increase
                    })
            
            # Detect bursting pattern (6+ messages appearing at once)
            burst_detected = any(inc['increase'] >= 6 for inc in conversation_increases)
            
            if burst_detected:
                burst_details = [f"{inc['increase']} at {inc['time']:.0f}s" for inc in conversation_increases if inc['increase'] >= 6]
                self.log_result("Auto-Conversation Bursting", False, 
                              f"CONFIRMED MESSAGE BURSTING: {', '.join(burst_details)} conversations appeared simultaneously", critical=True)
            else:
                self.log_result("Auto-Conversation Bursting", True, 
                              "No message bursting detected")
            
            # Check interval timing
            if final_new >= expected_intervals:
                self.log_result("Auto-Conversation Intervals", True, 
                              f"Expected ~{expected_intervals} conversations, got {final_new}")
            else:
                self.log_result("Auto-Conversation Intervals", False, 
                              f"Expected ~{expected_intervals} conversations, only got {final_new}")
                              
        else:
            self.log_result("Auto-Conversation Monitoring", False, 
                          "No monitoring data collected", critical=True)

    def test_4_progressive_streaming_analysis(self):
        """Test 4: Progressive Streaming Analysis - Test /api/messages/stream endpoint"""
        print("📡 TEST 4: PROGRESSIVE STREAMING ANALYSIS")
        print("=" * 60)
        
        # Test the streaming endpoint
        try:
            print("   Testing /api/messages/stream endpoint...")
            response = self.session.get(f"{API_BASE}/messages/stream", timeout=10)
            
            if response.status_code == 200:
                stream_data = response.json()
                message_count = len(stream_data) if isinstance(stream_data, list) else 0
                
                print(f"   Stream endpoint returned {message_count} messages")
                
                if message_count > 0:
                    # Analyze streaming message timestamps
                    timestamps = []
                    for msg in stream_data:
                        if isinstance(msg, dict) and 'timestamp' in msg:
                            timestamps.append(msg['timestamp'])
                    
                    if timestamps:
                        # Check for progressive vs batch appearance
                        # Convert timestamps to datetime objects for analysis
                        dt_timestamps = []
                        for ts in timestamps:
                            try:
                                if isinstance(ts, str):
                                    dt_timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                                elif isinstance(ts, dict) and '$date' in ts:
                                    dt_timestamps.append(datetime.fromisoformat(ts['$date'].replace('Z', '+00:00')))
                            except:
                                continue
                        
                        if len(dt_timestamps) >= 2:
                            # Calculate time gaps between messages
                            time_gaps = []
                            for i in range(1, len(dt_timestamps)):
                                gap = (dt_timestamps[i] - dt_timestamps[i-1]).total_seconds()
                                time_gaps.append(gap)
                            
                            # Check for batching (multiple messages with very small gaps)
                            small_gaps = [gap for gap in time_gaps if gap < 5]  # Less than 5 seconds
                            batch_percentage = len(small_gaps) / len(time_gaps) * 100 if time_gaps else 0
                            
                            if batch_percentage > 50:
                                self.log_result("Progressive Streaming", False, 
                                              f"BATCH DELIVERY DETECTED: {batch_percentage:.1f}% of messages have <5s gaps", critical=True)
                            else:
                                self.log_result("Progressive Streaming", True, 
                                              f"Progressive delivery: {batch_percentage:.1f}% batch messages")
                        else:
                            self.log_result("Progressive Streaming", True, 
                                          "Insufficient timestamp data for gap analysis")
                    else:
                        self.log_result("Progressive Streaming", False, 
                                      "No valid timestamps in stream data")
                else:
                    self.log_result("Progressive Streaming", False, 
                                  "Stream endpoint returned no messages")
                    
            else:
                self.log_result("Progressive Streaming", False, 
                              f"Stream endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Progressive Streaming", False, 
                          f"Stream analysis error: {str(e)}")

    def test_5_database_message_analysis(self):
        """Test 5: Database Message Analysis - Check message_stream collection and agent sequences"""
        print("🗄️ TEST 5: DATABASE MESSAGE ANALYSIS")
        print("=" * 60)
        
        # Since we can't directly access MongoDB, we'll analyze through API endpoints
        try:
            # Get all conversations for database analysis
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            if response.status_code != 200:
                self.log_result("Database Message Analysis", False, 
                              f"Cannot access conversation data: {response.status_code}", critical=True)
                return
                
            conversations = response.json()
            if not conversations:
                self.log_result("Database Message Analysis", False, 
                              "No conversation data available for analysis")
                return
                
            print(f"   Analyzing {len(conversations)} conversations from database...")
            
            # Analyze conversation IDs for uniqueness
            conversation_ids = [conv.get('id', '') for conv in conversations]
            unique_ids = set(conversation_ids)
            
            if len(unique_ids) != len(conversation_ids):
                duplicate_count = len(conversation_ids) - len(unique_ids)
                self.log_result("Conversation ID Uniqueness", False, 
                              f"DUPLICATE CONVERSATION IDs: {duplicate_count} duplicates found", critical=True)
            else:
                self.log_result("Conversation ID Uniqueness", True, 
                              "All conversation IDs are unique")
            
            # Analyze agent distribution across all messages
            all_agents = []
            message_timestamps = []
            agent_sequences_by_conversation = {}
            
            for conv in conversations:
                conv_id = conv.get('id', 'unknown')
                agent_sequences_by_conversation[conv_id] = []
                
                if 'messages' in conv:
                    for msg in conv['messages']:
                        agent_name = msg.get('agent_name', 'Unknown')
                        agent_id = msg.get('agent_id', 'unknown')
                        timestamp = msg.get('timestamp')
                        
                        all_agents.append(agent_name)
                        agent_sequences_by_conversation[conv_id].append(agent_name)
                        
                        if timestamp:
                            message_timestamps.append({
                                'agent': agent_name,
                                'timestamp': timestamp,
                                'conversation': conv_id
                            })
            
            # Check agent alternation patterns in database
            total_messages = len(all_agents)
            consecutive_same = 0
            
            for conv_id, sequence in agent_sequences_by_conversation.items():
                for i in range(1, len(sequence)):
                    if sequence[i] == sequence[i-1]:
                        consecutive_same += 1
            
            consecutive_percentage = (consecutive_same / total_messages * 100) if total_messages > 0 else 0
            
            print(f"   📊 Database Analysis Results:")
            print(f"      Total messages in database: {total_messages}")
            print(f"      Consecutive same-agent messages: {consecutive_same} ({consecutive_percentage:.1f}%)")
            
            # Check for the reported alternation issue in database
            if consecutive_percentage > 25:
                self.log_result("Database Agent Alternation", False, 
                              f"DATABASE CONFIRMS ALTERNATION ISSUE: {consecutive_percentage:.1f}% consecutive same-agent messages", critical=True)
            else:
                self.log_result("Database Agent Alternation", True, 
                              f"Database shows good alternation: {consecutive_percentage:.1f}% consecutive")
            
            # Analyze message timing patterns in database
            if message_timestamps:
                # Sort by timestamp to check for timing patterns
                sorted_messages = sorted(message_timestamps, key=lambda x: x['timestamp'])
                
                # Check for timestamp clustering (messages appearing in bursts)
                time_gaps = []
                for i in range(1, len(sorted_messages)):
                    try:
                        ts1 = sorted_messages[i-1]['timestamp']
                        ts2 = sorted_messages[i]['timestamp']
                        
                        # Handle different timestamp formats
                        if isinstance(ts1, str):
                            dt1 = datetime.fromisoformat(ts1.replace('Z', '+00:00'))
                        elif isinstance(ts1, dict):
                            dt1 = datetime.fromisoformat(ts1['$date'].replace('Z', '+00:00'))
                        else:
                            continue
                            
                        if isinstance(ts2, str):
                            dt2 = datetime.fromisoformat(ts2.replace('Z', '+00:00'))
                        elif isinstance(ts2, dict):
                            dt2 = datetime.fromisoformat(ts2['$date'].replace('Z', '+00:00'))
                        else:
                            continue
                        
                        gap = (dt2 - dt1).total_seconds()
                        time_gaps.append(gap)
                        
                    except Exception as e:
                        continue
                
                if time_gaps:
                    # Check for message bursting in database timestamps
                    very_small_gaps = [gap for gap in time_gaps if gap < 2]  # Less than 2 seconds
                    burst_percentage = len(very_small_gaps) / len(time_gaps) * 100
                    
                    if burst_percentage > 40:
                        self.log_result("Database Message Timing", False, 
                                      f"DATABASE CONFIRMS MESSAGE BURSTING: {burst_percentage:.1f}% of messages have <2s gaps", critical=True)
                    else:
                        self.log_result("Database Message Timing", True, 
                                      f"Database shows normal timing: {burst_percentage:.1f}% burst messages")
                else:
                    self.log_result("Database Message Timing", False, 
                                  "Could not analyze message timing from database")
            else:
                self.log_result("Database Message Timing", False, 
                              "No timestamp data available for analysis")
                
        except Exception as e:
            self.log_result("Database Message Analysis", False, 
                          f"Database analysis error: {str(e)}", critical=True)

    def run_comprehensive_investigation(self):
        """Run all investigation tests"""
        print("🔍 COMPREHENSIVE INVESTIGATION: MESSAGE TIMING & AGENT ALTERNATION ISSUES")
        print("=" * 80)
        print("User Reports:")
        print("- First message takes very long time to appear")
        print("- Second message also takes very long time")  
        print("- Subsequent messages: 6+ messages appear immediately at once")
        print("- Same agents sending multiple messages in a row (should alternate)")
        print("=" * 80)
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("🚨 CRITICAL: Authentication failed - cannot proceed with investigation")
            return
            
        # Run all 5 investigation tests
        self.test_1_message_generation_timing_analysis()
        self.test_2_agent_selection_alternation_analysis()
        self.test_3_auto_conversation_system_investigation()
        self.test_4_progressive_streaming_analysis()
        self.test_5_database_message_analysis()
        
        # Print comprehensive summary
        self.print_investigation_summary()

    def print_investigation_summary(self):
        """Print comprehensive investigation summary"""
        print("\n" + "=" * 80)
        print("🔍 MESSAGE TIMING & AGENT ALTERNATION INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        critical_failures = [r for r in self.test_results if r['critical'] and not r['success']]
        
        print(f"Total Investigation Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Critical Issues Found: {len(critical_failures)}")
        print()
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES CONFIRMED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Specific analysis for user's reported issues
        print("📋 USER ISSUE INVESTIGATION RESULTS:")
        
        # Check timing issues
        timing_tests = [r for r in self.test_results if 'Timing' in r['test'] or 'timing' in r['test']]
        timing_issues = [r for r in timing_tests if not r['success']]
        
        if timing_issues:
            print("   🚨 CONFIRMED: Message timing issues detected")
            for issue in timing_issues:
                print(f"      - {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No significant message timing issues detected")
        
        # Check alternation issues  
        alternation_tests = [r for r in self.test_results if 'Alternation' in r['test'] or 'alternation' in r['test']]
        alternation_issues = [r for r in alternation_tests if not r['success']]
        
        if alternation_issues:
            print("   🚨 CONFIRMED: Agent alternation issues detected")
            for issue in alternation_issues:
                print(f"      - {issue['test']}: {issue['details']}")
        else:
            print("   ✅ Agent alternation appears to be working correctly")
        
        # Check bursting issues
        bursting_tests = [r for r in self.test_results if 'Bursting' in r['test'] or 'bursting' in r['test']]
        bursting_issues = [r for r in bursting_tests if not r['success']]
        
        if bursting_issues:
            print("   🚨 CONFIRMED: Message bursting issues detected")
            for issue in bursting_issues:
                print(f"      - {issue['test']}: {issue['details']}")
        else:
            print("   ✅ No message bursting issues detected")
        
        # Check streaming issues
        streaming_tests = [r for r in self.test_results if 'Streaming' in r['test'] or 'streaming' in r['test']]
        streaming_issues = [r for r in streaming_tests if not r['success']]
        
        if streaming_issues:
            print("   🚨 CONFIRMED: Progressive streaming issues detected")
            for issue in streaming_issues:
                print(f"      - {issue['test']}: {issue['details']}")
        else:
            print("   ✅ Progressive streaming appears to be working correctly")
        
        print()
        
        # Root cause analysis
        print("🔬 ROOT CAUSE ANALYSIS:")
        
        if critical_failures:
            print("   Based on the investigation, the following root causes are likely:")
            
            # Analyze patterns in failures
            if any('timing' in f['test'].lower() for f in critical_failures):
                print("   - Backend conversation generation has performance bottlenecks")
                print("   - LLM API calls may be timing out or taking excessive time")
                
            if any('alternation' in f['test'].lower() for f in critical_failures):
                print("   - Agent selection logic is not properly implementing round-robin")
                print("   - Multiple conversation generations may be overlapping")
                
            if any('bursting' in f['test'].lower() for f in critical_failures):
                print("   - Auto-conversation system is generating multiple conversations simultaneously")
                print("   - Frontend polling may be missing progressive updates")
                
            if any('streaming' in f['test'].lower() for f in critical_failures):
                print("   - Message streaming endpoint is delivering messages in batches")
                print("   - Real-time updates are not working as designed")
        else:
            print("   No critical root causes identified in this investigation")
            print("   Issues may be intermittent or related to specific usage patterns")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    print("Starting Comprehensive Message Timing & Agent Alternation Investigation...")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    investigator = MessageTimingInvestigator()
    investigator.run_comprehensive_investigation()