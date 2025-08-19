#!/usr/bin/env python3
"""
URGENT: SAME AGENT CONSECUTIVE MESSAGES INVESTIGATION
Backend Testing for Agent Alternation Issue

CRITICAL ISSUE: Same agent generating two messages in a row
This violates the alternating agent rule and is a critical conversation generation bug.

FOCUS TESTS:
1. Agent Selection Logic Verification
2. Message Stream Agent Analysis  
3. Parallel Processing Agent Distribution
4. Agent Pool Analysis
5. Message Index vs Agent Mapping
"""

import requests
import json
import time
import os
from datetime import datetime
import sys
from collections import Counter, defaultdict

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AgentAlternationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.agents_data = []
        
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
        print("🔐 AUTHENTICATING FOR AGENT ALTERNATION TESTING")
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
                          f"Auth error: {str(e)}", critical=True)
            return False

    def test_agent_pool_analysis(self):
        """Test 4: Agent Pool Analysis - Check available agents for conversation"""
        print("👥 TEST 4: AGENT POOL ANALYSIS")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{API_BASE}/agents", timeout=10)
            
            if response.status_code == 200:
                agents = response.json()
                self.agents_data = agents
                agent_count = len(agents)
                
                if agent_count >= 2:
                    self.log_result("Agent Pool Size", True, 
                                  f"Found {agent_count} agents (sufficient for alternation)")
                    
                    # Analyze agent diversity
                    archetypes = [agent.get('archetype', 'unknown') for agent in agents]
                    archetype_counts = Counter(archetypes)
                    unique_archetypes = len(archetype_counts)
                    
                    self.log_result("Agent Diversity", True, 
                                  f"Agent archetypes: {dict(archetype_counts)} ({unique_archetypes} unique)")
                    
                    # Check agent IDs for uniqueness
                    agent_ids = [agent.get('id', '') for agent in agents]
                    unique_ids = len(set(agent_ids))
                    
                    if unique_ids == agent_count:
                        self.log_result("Agent ID Uniqueness", True, 
                                      f"All {agent_count} agents have unique IDs")
                    else:
                        self.log_result("Agent ID Uniqueness", False, 
                                      f"Duplicate agent IDs detected: {agent_count} agents, {unique_ids} unique IDs", critical=True)
                    
                    # Display agent details for debugging
                    print("   Agent Details:")
                    for i, agent in enumerate(agents[:5], 1):  # Show first 5 agents
                        print(f"   {i}. {agent.get('name', 'Unknown')} ({agent.get('archetype', 'unknown')}) - ID: {agent.get('id', 'no-id')[:8]}...")
                    
                else:
                    self.log_result("Agent Pool Size", False, 
                                  f"Insufficient agents: {agent_count} (need at least 2)", critical=True)
                    
            else:
                self.log_result("Agent Pool Access", False, 
                              f"Cannot access agents: {response.status_code}", critical=True)
                
        except Exception as e:
            self.log_result("Agent Pool Access", False, 
                          f"Agent pool error: {str(e)}", critical=True)

    def test_agent_selection_logic(self):
        """Test 1: Agent Selection Logic Verification - Test conversation generation agent selection"""
        print("🎯 TEST 1: AGENT SELECTION LOGIC VERIFICATION")
        print("=" * 60)
        
        # Generate multiple conversations to test agent selection
        agent_sequences = []
        
        for test_round in range(3):  # Test 3 conversation generations
            print(f"   Testing conversation generation round {test_round + 1}...")
            
            try:
                # Get baseline conversation count
                response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                baseline_count = len(response.json()) if response.status_code == 200 else 0
                
                # Generate conversation
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/conversation/generate", 
                                           json={}, 
                                           timeout=60)
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Wait for conversation to be stored
                    time.sleep(2)
                    
                    # Get new conversations
                    response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                    if response.status_code == 200:
                        conversations = response.json()
                        new_count = len(conversations)
                        
                        if new_count > baseline_count:
                            # Get the latest conversation
                            latest_conversation = conversations[0] if conversations else None
                            
                            if latest_conversation and 'messages' in latest_conversation:
                                messages = latest_conversation['messages']
                                agent_sequence = []
                                
                                for msg in messages:
                                    agent_name = msg.get('agent_name', 'Unknown')
                                    agent_id = msg.get('agent_id', 'unknown-id')
                                    agent_sequence.append({
                                        'name': agent_name,
                                        'id': agent_id,
                                        'message': msg.get('message', '')[:50] + '...'
                                    })
                                
                                agent_sequences.append(agent_sequence)
                                
                                self.log_result(f"Conversation Generation Round {test_round + 1}", True, 
                                              f"Generated {len(messages)} messages in {generation_time:.1f}s")
                                
                                # Check for immediate agent alternation issues
                                consecutive_same_agent = False
                                for i in range(1, len(agent_sequence)):
                                    if agent_sequence[i]['id'] == agent_sequence[i-1]['id']:
                                        consecutive_same_agent = True
                                        self.log_result(f"Agent Alternation Round {test_round + 1}", False, 
                                                      f"SAME AGENT CONSECUTIVE: {agent_sequence[i]['name']} appears twice in a row", critical=True)
                                        break
                                
                                if not consecutive_same_agent:
                                    self.log_result(f"Agent Alternation Round {test_round + 1}", True, 
                                                  f"Proper agent alternation in {len(messages)} messages")
                            else:
                                self.log_result(f"Conversation Generation Round {test_round + 1}", False, 
                                              "No messages found in generated conversation", critical=True)
                        else:
                            self.log_result(f"Conversation Generation Round {test_round + 1}", False, 
                                          "No new conversation created", critical=True)
                    else:
                        self.log_result(f"Conversation Generation Round {test_round + 1}", False, 
                                      "Cannot retrieve conversations after generation", critical=True)
                else:
                    self.log_result(f"Conversation Generation Round {test_round + 1}", False, 
                                  f"Generation failed: {response.status_code}", critical=True)
                    
            except Exception as e:
                self.log_result(f"Conversation Generation Round {test_round + 1}", False, 
                              f"Generation error: {str(e)}", critical=True)
            
            # Brief pause between tests
            time.sleep(1)
        
        # Analyze overall agent selection patterns
        if agent_sequences:
            self.analyze_agent_selection_patterns(agent_sequences)

    def analyze_agent_selection_patterns(self, agent_sequences):
        """Analyze agent selection patterns across multiple conversations"""
        print("   📊 ANALYZING AGENT SELECTION PATTERNS...")
        
        total_messages = 0
        total_conversations = len(agent_sequences)
        agent_usage_count = Counter()
        consecutive_violations = 0
        
        for conv_idx, sequence in enumerate(agent_sequences):
            total_messages += len(sequence)
            
            # Count agent usage
            for msg in sequence:
                agent_usage_count[msg['name']] += 1
            
            # Check for consecutive same agent violations
            for i in range(1, len(sequence)):
                if sequence[i]['id'] == sequence[i-1]['id']:
                    consecutive_violations += 1
                    print(f"   🚨 VIOLATION in Conversation {conv_idx + 1}: {sequence[i]['name']} → {sequence[i]['name']}")
        
        # Summary analysis
        if consecutive_violations > 0:
            self.log_result("Overall Agent Alternation Analysis", False, 
                          f"Found {consecutive_violations} consecutive same-agent violations across {total_conversations} conversations", critical=True)
        else:
            self.log_result("Overall Agent Alternation Analysis", True, 
                          f"No consecutive same-agent violations found in {total_conversations} conversations")
        
        # Agent distribution analysis
        if len(agent_usage_count) >= 2:
            most_used = agent_usage_count.most_common(1)[0]
            least_used = agent_usage_count.most_common()[-1]
            usage_ratio = most_used[1] / least_used[1] if least_used[1] > 0 else float('inf')
            
            if usage_ratio <= 2.0:  # Reasonable distribution
                self.log_result("Agent Usage Distribution", True, 
                              f"Balanced usage: {dict(agent_usage_count)} (ratio: {usage_ratio:.1f})")
            else:
                self.log_result("Agent Usage Distribution", False, 
                              f"Unbalanced usage: {dict(agent_usage_count)} (ratio: {usage_ratio:.1f})")
        
        print(f"   📈 Total: {total_messages} messages across {total_conversations} conversations")
        print(f"   👥 Agent usage: {dict(agent_usage_count)}")

    def test_message_stream_agent_analysis(self):
        """Test 2: Message Stream Agent Analysis - Test /api/messages/stream for agent sequence"""
        print("📡 TEST 2: MESSAGE STREAM AGENT ANALYSIS")
        print("=" * 60)
        
        # Check if messages/stream endpoint exists
        try:
            response = self.session.get(f"{API_BASE}/messages/stream", timeout=10)
            
            if response.status_code == 200:
                stream_data = response.json()
                self.log_result("Message Stream Access", True, 
                              f"Stream endpoint accessible, data type: {type(stream_data)}")
                
                # Analyze stream data for agent sequences
                if isinstance(stream_data, list):
                    agent_sequence = []
                    for msg in stream_data:
                        if isinstance(msg, dict):
                            agent_name = msg.get('agent_name', 'Unknown')
                            agent_id = msg.get('agent_id', 'unknown')
                            agent_sequence.append({'name': agent_name, 'id': agent_id})
                    
                    if len(agent_sequence) >= 2:
                        # Check for consecutive same agents
                        consecutive_count = 0
                        for i in range(1, len(agent_sequence)):
                            if agent_sequence[i]['id'] == agent_sequence[i-1]['id']:
                                consecutive_count += 1
                                print(f"   🚨 CONSECUTIVE SAME AGENT: {agent_sequence[i]['name']} at positions {i-1} and {i}")
                        
                        if consecutive_count > 0:
                            self.log_result("Stream Agent Alternation", False, 
                                          f"Found {consecutive_count} consecutive same-agent violations in stream", critical=True)
                        else:
                            self.log_result("Stream Agent Alternation", True, 
                                          f"Proper agent alternation in {len(agent_sequence)} stream messages")
                    else:
                        self.log_result("Stream Message Count", False, 
                                      f"Insufficient messages in stream: {len(agent_sequence)}")
                else:
                    self.log_result("Stream Data Format", False, 
                                  f"Unexpected stream data format: {type(stream_data)}")
                    
            elif response.status_code == 404:
                self.log_result("Message Stream Access", False, 
                              "Messages/stream endpoint does not exist - using alternative analysis")
                # Use conversations endpoint as alternative
                self.analyze_conversations_for_stream_patterns()
            else:
                self.log_result("Message Stream Access", False, 
                              f"Stream endpoint error: {response.status_code}")
                
        except Exception as e:
            self.log_result("Message Stream Access", False, 
                          f"Stream analysis error: {str(e)}")
            # Fallback to conversations analysis
            self.analyze_conversations_for_stream_patterns()

    def analyze_conversations_for_stream_patterns(self):
        """Analyze conversations as alternative to message stream"""
        print("   📋 ANALYZING CONVERSATIONS FOR STREAM PATTERNS...")
        
        try:
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            
            if response.status_code == 200:
                conversations = response.json()
                
                if conversations and len(conversations) > 0:
                    # Analyze the most recent conversation
                    latest_conv = conversations[0]
                    messages = latest_conv.get('messages', [])
                    
                    if len(messages) >= 2:
                        agent_sequence = []
                        consecutive_violations = 0
                        
                        for i, msg in enumerate(messages):
                            agent_name = msg.get('agent_name', 'Unknown')
                            agent_id = msg.get('agent_id', 'unknown')
                            agent_sequence.append({
                                'index': i,
                                'name': agent_name,
                                'id': agent_id
                            })
                            
                            # Check for consecutive same agent
                            if i > 0 and agent_id == messages[i-1].get('agent_id', ''):
                                consecutive_violations += 1
                                print(f"   🚨 CONSECUTIVE VIOLATION: Message {i-1} and {i} both from {agent_name}")
                        
                        if consecutive_violations > 0:
                            self.log_result("Conversation Stream Analysis", False, 
                                          f"Found {consecutive_violations} consecutive same-agent violations", critical=True)
                        else:
                            self.log_result("Conversation Stream Analysis", True, 
                                          f"Proper agent alternation in {len(messages)} messages")
                        
                        # Show agent sequence for debugging
                        print("   Agent sequence:")
                        for item in agent_sequence[:10]:  # Show first 10
                            print(f"   {item['index']}: {item['name']} (ID: {item['id'][:8]}...)")
                    else:
                        self.log_result("Conversation Message Count", False, 
                                      f"Insufficient messages for analysis: {len(messages)}")
                else:
                    self.log_result("Conversation Data", False, 
                                  "No conversations found for stream analysis")
            else:
                self.log_result("Conversation Access", False, 
                              f"Cannot access conversations: {response.status_code}")
                
        except Exception as e:
            self.log_result("Conversation Stream Analysis", False, 
                          f"Analysis error: {str(e)}")

    def test_parallel_processing_agent_distribution(self):
        """Test 3: Parallel Processing Agent Distribution - Check if parallel processing causes same agents"""
        print("⚡ TEST 3: PARALLEL PROCESSING AGENT DISTRIBUTION")
        print("=" * 60)
        
        # Test rapid conversation generation to stress parallel processing
        print("   Testing rapid conversation generation to check parallel processing...")
        
        agent_selections = []
        generation_times = []
        
        for i in range(2):  # Generate 2 conversations rapidly
            try:
                start_time = time.time()
                response = self.session.post(f"{API_BASE}/conversation/generate", 
                                           json={}, 
                                           timeout=30)
                generation_time = time.time() - start_time
                generation_times.append(generation_time)
                
                if response.status_code == 200:
                    # Brief wait for storage
                    time.sleep(1)
                    
                    # Get latest conversation
                    conv_response = self.session.get(f"{API_BASE}/conversations", timeout=10)
                    if conv_response.status_code == 200:
                        conversations = conv_response.json()
                        if conversations:
                            latest_conv = conversations[0]
                            messages = latest_conv.get('messages', [])
                            
                            # Extract agent selection pattern
                            agents_in_conv = []
                            for msg in messages:
                                agents_in_conv.append({
                                    'name': msg.get('agent_name', 'Unknown'),
                                    'id': msg.get('agent_id', 'unknown')
                                })
                            
                            agent_selections.append(agents_in_conv)
                            
                            self.log_result(f"Rapid Generation {i+1}", True, 
                                          f"Generated {len(messages)} messages in {generation_time:.1f}s")
                        else:
                            self.log_result(f"Rapid Generation {i+1}", False, 
                                          "No conversations found after generation")
                else:
                    self.log_result(f"Rapid Generation {i+1}", False, 
                                  f"Generation failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Rapid Generation {i+1}", False, 
                              f"Generation error: {str(e)}")
            
            # Small delay between rapid generations
            time.sleep(0.5)
        
        # Analyze parallel processing effects
        if len(agent_selections) >= 2:
            self.analyze_parallel_processing_effects(agent_selections, generation_times)

    def analyze_parallel_processing_effects(self, agent_selections, generation_times):
        """Analyze effects of parallel processing on agent selection"""
        print("   📊 ANALYZING PARALLEL PROCESSING EFFECTS...")
        
        total_violations = 0
        
        for conv_idx, agents in enumerate(agent_selections):
            consecutive_violations = 0
            
            for i in range(1, len(agents)):
                if agents[i]['id'] == agents[i-1]['id']:
                    consecutive_violations += 1
                    total_violations += 1
                    print(f"   🚨 PARALLEL VIOLATION in Conv {conv_idx+1}: {agents[i]['name']} appears consecutively")
            
            if consecutive_violations == 0:
                print(f"   ✅ Conv {conv_idx+1}: No consecutive violations ({len(agents)} messages)")
        
        # Overall assessment
        if total_violations > 0:
            self.log_result("Parallel Processing Agent Distribution", False, 
                          f"Parallel processing caused {total_violations} consecutive same-agent violations", critical=True)
        else:
            self.log_result("Parallel Processing Agent Distribution", True, 
                          f"No parallel processing violations found across {len(agent_selections)} conversations")
        
        # Performance analysis
        avg_generation_time = sum(generation_times) / len(generation_times) if generation_times else 0
        print(f"   ⏱️ Average generation time: {avg_generation_time:.1f}s")
        
        if avg_generation_time > 30:
            print("   ⚠️ Slow generation times may indicate processing bottlenecks")

    def test_message_index_vs_agent_mapping(self):
        """Test 5: Message Index vs Agent Mapping - Verify message order corresponds to different agents"""
        print("🔢 TEST 5: MESSAGE INDEX VS AGENT MAPPING")
        print("=" * 60)
        
        try:
            # Get recent conversations for analysis
            response = self.session.get(f"{API_BASE}/conversations", timeout=10)
            
            if response.status_code == 200:
                conversations = response.json()
                
                if conversations and len(conversations) > 0:
                    # Analyze multiple conversations
                    total_violations = 0
                    total_messages = 0
                    
                    for conv_idx, conversation in enumerate(conversations[:3]):  # Analyze first 3 conversations
                        messages = conversation.get('messages', [])
                        total_messages += len(messages)
                        
                        if len(messages) >= 2:
                            print(f"   Analyzing Conversation {conv_idx + 1} ({len(messages)} messages):")
                            
                            violations_in_conv = 0
                            for i in range(len(messages)):
                                msg = messages[i]
                                agent_name = msg.get('agent_name', 'Unknown')
                                agent_id = msg.get('agent_id', 'unknown')
                                
                                print(f"     Index {i}: {agent_name} (ID: {agent_id[:8]}...)")
                                
                                # Check if this message has same agent as previous
                                if i > 0:
                                    prev_agent_id = messages[i-1].get('agent_id', '')
                                    if agent_id == prev_agent_id:
                                        violations_in_conv += 1
                                        total_violations += 1
                                        print(f"     🚨 VIOLATION: Index {i-1} and {i} both from same agent!")
                            
                            if violations_in_conv == 0:
                                self.log_result(f"Message Index Mapping Conv {conv_idx + 1}", True, 
                                              f"Proper agent alternation across {len(messages)} message indexes")
                            else:
                                self.log_result(f"Message Index Mapping Conv {conv_idx + 1}", False, 
                                              f"Found {violations_in_conv} index mapping violations", critical=True)
                    
                    # Overall assessment
                    if total_violations > 0:
                        self.log_result("Overall Message Index vs Agent Mapping", False, 
                                      f"Found {total_violations} violations across {total_messages} messages", critical=True)
                    else:
                        self.log_result("Overall Message Index vs Agent Mapping", True, 
                                      f"Perfect agent alternation across {total_messages} messages in multiple conversations")
                else:
                    self.log_result("Message Index Analysis", False, 
                                  "No conversations available for index analysis")
            else:
                self.log_result("Message Index Analysis", False, 
                              f"Cannot access conversations: {response.status_code}")
                
        except Exception as e:
            self.log_result("Message Index Analysis", False, 
                          f"Index analysis error: {str(e)}")

    def run_all_tests(self):
        """Run all agent alternation tests"""
        print("🚨 URGENT: SAME AGENT CONSECUTIVE MESSAGES INVESTIGATION")
        print("=" * 80)
        print("CRITICAL ISSUE: Same agent generating two messages in a row")
        print("This violates the alternating agent rule and breaks conversation flow")
        print("=" * 80)
        print()
        
        if not self.authenticate():
            print("🚨 CRITICAL: Authentication failed - cannot proceed")
            return
        
        # Run tests in logical order
        self.test_agent_pool_analysis()
        self.test_agent_selection_logic()
        self.test_message_stream_agent_analysis()
        self.test_parallel_processing_agent_distribution()
        self.test_message_index_vs_agent_mapping()
        
        # Print comprehensive summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary focused on agent alternation"""
        print("\n" + "=" * 80)
        print("🔍 AGENT ALTERNATION INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        critical_failures = [r for r in self.test_results if r['critical'] and not r['success']]
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Critical Failures: {len(critical_failures)}")
        print()
        
        # Critical issue analysis
        alternation_violations = [r for r in self.test_results if 'Alternation' in r['test'] and not r['success']]
        consecutive_violations = [r for r in self.test_results if 'consecutive' in r['details'].lower() and not r['success']]
        
        if alternation_violations or consecutive_violations:
            print("🚨 AGENT ALTERNATION VIOLATIONS CONFIRMED:")
            for violation in alternation_violations + consecutive_violations:
                print(f"   ❌ {violation['test']}: {violation['details']}")
            print()
            print("🎯 ROOT CAUSE ANALYSIS NEEDED:")
            print("   - Agent selection logic may not be enforcing alternation")
            print("   - Parallel processing might be causing race conditions")
            print("   - Message indexing system may have bugs")
            print("   - Agent pool management could be flawed")
        else:
            print("✅ NO AGENT ALTERNATION VIOLATIONS DETECTED")
            print("   - All tested conversations show proper agent alternation")
            print("   - Agent selection logic appears to be working correctly")
            print("   - No consecutive same-agent messages found")
        
        print()
        
        # Specific recommendations
        print("📋 RECOMMENDATIONS:")
        if critical_failures:
            print("   🚨 IMMEDIATE ACTION REQUIRED:")
            print("   1. Fix agent selection logic to enforce strict alternation")
            print("   2. Add agent alternation validation in conversation generation")
            print("   3. Implement agent rotation tracking to prevent duplicates")
            print("   4. Review parallel processing for race conditions")
        else:
            print("   ✅ System appears to be working correctly")
            print("   - Continue monitoring for intermittent issues")
            print("   - Consider adding automated alternation checks")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    print("Starting Agent Alternation Investigation...")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = AgentAlternationTester()
    tester.run_all_tests()