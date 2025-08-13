#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Natural Conversation Flow System
Tests the NEW NATURAL CONVERSATION FLOW SYSTEM with contextual awareness
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration
BACKEND_URL = "https://7739ef7b-2781-4fb3-8a8b-8d104f76b04c.preview.emergentagent.com/api"
TEST_USER_EMAIL = "dino@cytonic.com"

class ConversationFlowTester:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.test_agents = []
        self.conversation_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_time=0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": f"{response_time:.3f}s",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        print(f"{status} | {test_name} | {details} | {response_time:.3f}s")
        
    def authenticate(self):
        """Authenticate as guest user"""
        print("\n🔐 AUTHENTICATION TEST")
        print("=" * 50)
        
        start_time = time.time()
        try:
            response = requests.post(f"{BACKEND_URL}/auth/test-login", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                user_data = data.get("user", {})
                self.user_id = user_data.get("id")
                
                if self.auth_token and self.user_id:
                    self.log_test("Guest Authentication", True, 
                                f"Token received, User ID: {self.user_id[:8]}...", response_time)
                    return True
                else:
                    self.log_test("Guest Authentication", False, 
                                "Missing token or user_id in response", response_time)
                    return False
            else:
                self.log_test("Guest Authentication", False, 
                            f"HTTP {response.status_code}: {response.text[:100]}", response_time)
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Guest Authentication", False, f"Exception: {str(e)}", response_time)
            return False
    
    def setup_test_agents(self):
        """Create test agents for conversation"""
        print("\n🤖 AGENT SETUP TEST")
        print("=" * 50)
        
        test_agents_data = [
            {
                "name": "Dr. Sarah Chen",
                "archetype": "scientist",
                "goal": "Advance quantum computing research for practical applications",
                "expertise": "Quantum Computing & Cryptography",
                "background": "PhD in Quantum Physics, 10 years at IBM Research"
            },
            {
                "name": "Marcus Rodriguez",
                "archetype": "leader", 
                "goal": "Lead strategic technology initiatives and team coordination",
                "expertise": "Technology Strategy & Project Management",
                "background": "Former CTO at tech startups, MBA from Stanford"
            },
            {
                "name": "Elena Volkov",
                "archetype": "skeptic",
                "goal": "Identify risks and ensure realistic project planning",
                "expertise": "Risk Analysis & Financial Modeling",
                "background": "15 years in venture capital and risk assessment"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        for agent_data in test_agents_data:
            start_time = time.time()
            try:
                response = requests.post(f"{BACKEND_URL}/agents", 
                                       json=agent_data, headers=headers, timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    agent = response.json()
                    self.test_agents.append(agent)
                    self.log_test(f"Create Agent: {agent_data['name']}", True,
                                f"Agent ID: {agent.get('id', 'N/A')[:8]}...", response_time)
                else:
                    self.log_test(f"Create Agent: {agent_data['name']}", False,
                                f"HTTP {response.status_code}", response_time)
                    
            except Exception as e:
                response_time = time.time() - start_time
                self.log_test(f"Create Agent: {agent_data['name']}", False,
                            f"Exception: {str(e)}", response_time)
        
        return len(self.test_agents) >= 2
    
    def set_scenario(self):
        """Set a scenario for contextual conversation"""
        print("\n📋 SCENARIO SETUP TEST")
        print("=" * 50)
        
        scenario_data = {
            "scenario": "A breakthrough in quantum computing has been achieved, but it requires massive international cooperation and investment to scale globally. The team must develop a comprehensive strategy for implementation, addressing technical, economic, and geopolitical challenges.",
            "scenario_name": "Quantum Computing Global Initiative"
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        start_time = time.time()
        
        try:
            response = requests.post(f"{BACKEND_URL}/simulation/set-scenario",
                                   json=scenario_data, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Set Scenario", True, 
                            f"Scenario: {scenario_data['scenario_name']}", response_time)
                return True
            else:
                self.log_test("Set Scenario", False,
                            f"HTTP {response.status_code}: {response.text[:100]}", response_time)
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Set Scenario", False, f"Exception: {str(e)}", response_time)
            return False
    
    def test_contextual_message_generation(self, call_number):
        """Test the enhanced contextual message generation"""
        print(f"\n💬 CONTEXTUAL MESSAGE TEST #{call_number}")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        start_time = time.time()
        
        try:
            response = requests.post(f"{BACKEND_URL}/conversation/add-contextual-message",
                                   headers=headers, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                conversation_data = response.json()
                
                # Store conversation ID for tracking
                if not self.conversation_id:
                    self.conversation_id = conversation_data.get("id")
                
                # Analyze the response
                messages = conversation_data.get("messages", [])
                conversation_state = conversation_data.get("conversation_state", {})
                
                if messages:
                    latest_message = messages[-1]
                    agent_name = latest_message.get("agent_name", "Unknown")
                    message_text = latest_message.get("message", "")
                    message_type = latest_message.get("message_type", "unknown")
                    context_info = latest_message.get("context_info", {})
                    
                    # Check for contextual awareness features
                    contextual_features = []
                    
                    # Check if message references other agents
                    other_agent_names = [agent.get("name", "") for agent in self.test_agents 
                                       if agent.get("name", "") != agent_name]
                    references_others = any(name.split()[0] in message_text for name in other_agent_names)
                    if references_others:
                        contextual_features.append("References other agents")
                    
                    # Check for questions
                    if "?" in message_text:
                        contextual_features.append("Contains question")
                    
                    # Check for building on previous ideas
                    building_phrases = ["building on", "expanding on", "following", "based on what", "as mentioned"]
                    if any(phrase in message_text.lower() for phrase in building_phrases):
                        contextual_features.append("Builds on previous ideas")
                    
                    # Check for solution-oriented language
                    solution_phrases = ["solution", "approach", "strategy", "recommend", "propose", "implement"]
                    if any(phrase in message_text.lower() for phrase in solution_phrases):
                        contextual_features.append("Solution-oriented")
                    
                    # Check conversation state evolution
                    topics_discussed = conversation_state.get("topics_discussed", [])
                    questions_asked = conversation_state.get("questions_asked", [])
                    solutions_proposed = conversation_state.get("solutions_proposed", [])
                    current_focus = conversation_state.get("current_focus", "unknown")
                    goal_progress = conversation_state.get("goal_progress", 0.0)
                    
                    details = f"Agent: {agent_name} | Features: {', '.join(contextual_features) if contextual_features else 'Basic response'} | Focus: {current_focus} | Progress: {goal_progress}"
                    
                    self.log_test(f"Contextual Message #{call_number}", True, details, response_time)
                    
                    # Print detailed analysis
                    print(f"  🤖 Agent: {agent_name}")
                    print(f"  📝 Message: {message_text[:100]}...")
                    print(f"  🎯 Features: {', '.join(contextual_features) if contextual_features else 'Basic response'}")
                    print(f"  📊 State: Focus={current_focus}, Progress={goal_progress}")
                    print(f"  📈 Tracking: {len(topics_discussed)} topics, {len(questions_asked)} questions, {len(solutions_proposed)} solutions")
                    
                    return True, {
                        "agent_name": agent_name,
                        "message_length": len(message_text),
                        "contextual_features": contextual_features,
                        "conversation_state": conversation_state,
                        "message_text": message_text
                    }
                else:
                    self.log_test(f"Contextual Message #{call_number}", False,
                                "No messages in response", response_time)
                    return False, {}
            else:
                self.log_test(f"Contextual Message #{call_number}", False,
                            f"HTTP {response.status_code}: {response.text[:100]}", response_time)
                return False, {}
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(f"Contextual Message #{call_number}", False,
                        f"Exception: {str(e)}", response_time)
            return False, {}
    
    def analyze_conversation_flow(self, message_results):
        """Analyze the overall conversation flow for natural progression"""
        print("\n📊 CONVERSATION FLOW ANALYSIS")
        print("=" * 50)
        
        if len(message_results) < 3:
            self.log_test("Conversation Flow Analysis", False,
                        "Need at least 3 messages for flow analysis", 0)
            return False
        
        # Check for agent diversity
        agents_participated = set(result.get("agent_name") for result in message_results)
        agent_diversity = len(agents_participated) / len(self.test_agents) if self.test_agents else 0
        
        # Check for contextual progression
        contextual_messages = sum(1 for result in message_results 
                                if result.get("contextual_features"))
        contextual_ratio = contextual_messages / len(message_results)
        
        # Check for question/answer patterns
        questions_asked = sum(1 for result in message_results 
                            if "Contains question" in result.get("contextual_features", []))
        
        # Check for solution progression
        solution_messages = sum(1 for result in message_results 
                              if "Solution-oriented" in result.get("contextual_features", []))
        
        # Check for building on ideas
        building_messages = sum(1 for result in message_results 
                              if "Builds on previous ideas" in result.get("contextual_features", []))
        
        # Check conversation state evolution
        final_state = message_results[-1].get("conversation_state", {}) if message_results else {}
        goal_progress = final_state.get("goal_progress", 0.0)
        current_focus = final_state.get("current_focus", "unknown")
        
        # Calculate flow quality score
        flow_score = (
            (agent_diversity * 0.3) +
            (contextual_ratio * 0.3) +
            (min(questions_asked / len(message_results), 0.5) * 0.2) +
            (min(solution_messages / len(message_results), 0.8) * 0.2)
        )
        
        analysis_details = f"Diversity: {agent_diversity:.1%} | Contextual: {contextual_ratio:.1%} | Questions: {questions_asked} | Solutions: {solution_messages} | Building: {building_messages} | Score: {flow_score:.2f}"
        
        success = flow_score >= 0.6  # 60% threshold for good conversation flow
        
        self.log_test("Conversation Flow Analysis", success, analysis_details, 0)
        
        print(f"  👥 Agent Diversity: {agent_diversity:.1%} ({len(agents_participated)}/{len(self.test_agents)} agents)")
        print(f"  🧠 Contextual Messages: {contextual_ratio:.1%} ({contextual_messages}/{len(message_results)})")
        print(f"  ❓ Questions Asked: {questions_asked}")
        print(f"  💡 Solution-Oriented: {solution_messages}")
        print(f"  🔗 Building on Ideas: {building_messages}")
        print(f"  📈 Goal Progress: {goal_progress}")
        print(f"  🎯 Current Focus: {current_focus}")
        print(f"  🏆 Flow Quality Score: {flow_score:.2f}/1.0")
        
        return success
    
    def test_conversation_state_tracking(self):
        """Test conversation state tracking and evolution"""
        print("\n📈 CONVERSATION STATE TRACKING TEST")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        start_time = time.time()
        
        try:
            # Get current conversation
            response = requests.get(f"{BACKEND_URL}/conversations", headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                conversations = response.json()
                if conversations:
                    latest_conversation = conversations[0]  # Most recent
                    conversation_state = latest_conversation.get("conversation_state", {})
                    messages = latest_conversation.get("messages", [])
                    
                    # Check state components
                    has_topics = len(conversation_state.get("topics_discussed", [])) > 0
                    has_questions = len(conversation_state.get("questions_asked", [])) > 0
                    has_solutions = len(conversation_state.get("solutions_proposed", [])) > 0
                    has_focus = conversation_state.get("current_focus") != "unknown"
                    has_progress = conversation_state.get("goal_progress", 0) > 0
                    
                    state_features = []
                    if has_topics: state_features.append("Topics tracked")
                    if has_questions: state_features.append("Questions tracked")
                    if has_solutions: state_features.append("Solutions tracked")
                    if has_focus: state_features.append("Focus defined")
                    if has_progress: state_features.append("Progress measured")
                    
                    success = len(state_features) >= 3  # At least 3 state features working
                    details = f"Messages: {len(messages)} | Features: {', '.join(state_features)}"
                    
                    self.log_test("Conversation State Tracking", success, details, response_time)
                    
                    print(f"  📊 State Features: {', '.join(state_features)}")
                    print(f"  📝 Total Messages: {len(messages)}")
                    print(f"  🎯 Current Focus: {conversation_state.get('current_focus', 'N/A')}")
                    print(f"  📈 Goal Progress: {conversation_state.get('goal_progress', 0)}")
                    
                    return success
                else:
                    self.log_test("Conversation State Tracking", False,
                                "No conversations found", response_time)
                    return False
            else:
                self.log_test("Conversation State Tracking", False,
                            f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Conversation State Tracking", False,
                        f"Exception: {str(e)}", response_time)
            return False
    
    def run_comprehensive_test(self):
        """Run the complete contextual conversation flow test"""
        print("🚀 NATURAL CONVERSATION FLOW SYSTEM TEST")
        print("=" * 60)
        print("Testing the NEW NATURAL CONVERSATION FLOW SYSTEM with contextual awareness")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue")
            return False
        
        # Step 2: Setup test agents
        if not self.setup_test_agents():
            print("❌ Agent setup failed - cannot continue")
            return False
        
        # Step 3: Set scenario
        if not self.set_scenario():
            print("❌ Scenario setup failed - cannot continue")
            return False
        
        # Step 4: Generate multiple contextual messages (5-6 calls as requested)
        message_results = []
        for i in range(1, 7):  # 6 sequential calls
            success, result = self.test_contextual_message_generation(i)
            if success:
                message_results.append(result)
            time.sleep(2)  # Brief pause between calls
        
        # Step 5: Analyze conversation flow
        flow_success = self.analyze_conversation_flow(message_results)
        
        # Step 6: Test conversation state tracking
        state_success = self.test_conversation_state_tracking()
        
        # Final Results Summary
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        if len(message_results) >= 5:
            print("✅ Successfully generated 5+ contextual messages")
        else:
            print("❌ Failed to generate sufficient contextual messages")
        
        if flow_success:
            print("✅ Natural conversation flow with contextual awareness working")
        else:
            print("❌ Conversation flow needs improvement")
        
        if state_success:
            print("✅ Conversation state tracking and evolution working")
        else:
            print("❌ Conversation state tracking needs improvement")
        
        # Comparison with old system
        print("\n🆚 COMPARISON WITH OLD SYSTEM:")
        print("OLD: Random individual messages with no context")
        print("NEW: Contextually aware collaborative discussion with natural flow")
        
        if success_rate >= 70:
            print("\n🎉 OVERALL RESULT: NEW CONTEXTUAL SYSTEM IS WORKING WELL!")
        else:
            print("\n⚠️ OVERALL RESULT: NEW CONTEXTUAL SYSTEM NEEDS IMPROVEMENTS")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = ConversationFlowTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ All critical tests passed - Natural Conversation Flow System is operational!")
        sys.exit(0)
    else:
        print("\n❌ Some critical tests failed - System needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()