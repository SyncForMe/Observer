#!/usr/bin/env python3
"""
Observer Chat Response Quality Testing
=====================================

This test specifically validates the improved Observer Chat agent response quality
as requested in the user review. Tests both caching improvements and response quality.

Test Requirements:
1. Send message: "list me the priority list we should focus when building this device in your opinion"
2. Verify agents provide SPECIFIC, HELPFUL responses instead of generic responses
3. Check agents actually address the request for a priority list
4. Confirm agents use their expertise to provide meaningful priorities
5. Test caching improvements with exact match and complex messages
6. Verify no partial matching causes wrong cached responses
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
API_URL = f"{BACKEND_URL}/api"

# Load JWT secret for token validation
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')

print(f"🔬 OBSERVER CHAT RESPONSE QUALITY TESTING")
print(f"API URL: {API_URL}")
print("="*80)

class ObserverChatQualityTester:
    def __init__(self):
        self.auth_token = None
        self.test_user_id = None
        self.test_results = []
        self.agent_ids = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
        
    def authenticate(self):
        """Authenticate using guest login"""
        print("\n🔐 AUTHENTICATION")
        print("-" * 40)
        
        try:
            response = requests.post(f"{API_URL}/auth/test-login")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                user_data = data.get("user", {})
                self.test_user_id = user_data.get("id")
                
                self.log_test("Guest Authentication", True, f"User ID: {self.test_user_id}")
                return True
            else:
                self.log_test("Guest Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Guest Authentication", False, f"Error: {e}")
            return False
    
    def setup_test_agents(self):
        """Create test agents with different expertise for testing"""
        print("\n🤖 SETTING UP TEST AGENTS")
        print("-" * 40)
        
        # Define test agents with different expertise
        test_agents = [
            {
                "name": "Dr. Sarah Chen",
                "archetype": "scientist",
                "goal": "Develop cutting-edge quantum computing solutions",
                "expertise": "Quantum Computing, Hardware Engineering, Signal Processing",
                "background": "PhD in Quantum Physics, 10+ years in quantum hardware development"
            },
            {
                "name": "Marcus Rodriguez",
                "archetype": "leader", 
                "goal": "Lead successful product development and market strategy",
                "expertise": "Product Management, Strategic Planning, Market Analysis",
                "background": "Former VP of Product at tech startups, MBA in Strategy"
            },
            {
                "name": "Alex Kim",
                "archetype": "engineer",
                "goal": "Build robust and scalable technical solutions",
                "expertise": "Software Engineering, System Architecture, DevOps",
                "background": "Senior Software Engineer with expertise in distributed systems"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        created_agents = 0
        
        for agent_data in test_agents:
            try:
                # Add default personality if not provided
                if "personality" not in agent_data:
                    agent_data["personality"] = {
                        "extroversion": 6,
                        "optimism": 7,
                        "curiosity": 8,
                        "cooperativeness": 7,
                        "energy": 6
                    }
                
                response = requests.post(
                    f"{API_URL}/agents",
                    json=agent_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    agent_response = response.json()
                    agent_id = agent_response.get("id")
                    if agent_id:
                        self.agent_ids.append(agent_id)
                        created_agents += 1
                        print(f"✅ Created agent: {agent_data['name']} (ID: {agent_id})")
                    else:
                        print(f"❌ Failed to get ID for agent: {agent_data['name']}")
                else:
                    print(f"❌ Failed to create agent {agent_data['name']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error creating agent {agent_data['name']}: {e}")
        
        success = created_agents >= 2  # Need at least 2 agents for meaningful testing
        self.log_test("Test Agent Creation", success, f"Created {created_agents}/3 agents")
        return success
    
    def test_complex_priority_request(self):
        """Test the specific complex message from user requirements"""
        print("\n🎯 TESTING COMPLEX PRIORITY REQUEST")
        print("-" * 40)
        
        # The exact message from user requirements
        complex_message = "list me the priority list we should focus when building this device in your opinion"
        
        print(f"Sending message: '{complex_message}'")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": complex_message},
                headers=headers
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                agent_responses = data.get("agent_responses", {})
                messages = agent_responses.get("messages", [])
                
                # Filter out observer message to get only agent responses
                agent_messages = [msg for msg in messages if msg.get("agent_name") != "Observer (You)"]
                
                print(f"📊 Response Analysis:")
                print(f"   Response Time: {response_time:.2f}s")
                print(f"   Agent Responses: {len(agent_messages)}")
                
                # Analyze response quality
                quality_results = self.analyze_response_quality(agent_messages, complex_message)
                
                # Test passes if we get specific, helpful responses
                test_passed = (
                    len(agent_messages) >= 2 and  # At least 2 agents responded
                    quality_results["has_specific_priorities"] and  # Contains specific priorities
                    quality_results["addresses_request"] and  # Addresses the request
                    not quality_results["has_generic_responses"]  # No generic responses
                )
                
                details = f"Agents: {len(agent_messages)}, Specific: {quality_results['has_specific_priorities']}, Addresses Request: {quality_results['addresses_request']}, No Generic: {not quality_results['has_generic_responses']}"
                self.log_test("Complex Priority Request Quality", test_passed, details)
                
                return test_passed, quality_results
                
            else:
                self.log_test("Complex Priority Request", False, f"HTTP {response.status_code}")
                return False, {}
                
        except Exception as e:
            self.log_test("Complex Priority Request", False, f"Error: {e}")
            return False, {}
    
    def analyze_response_quality(self, agent_messages, original_request):
        """Analyze the quality of agent responses"""
        print(f"\n📋 RESPONSE QUALITY ANALYSIS")
        print("-" * 40)
        
        results = {
            "has_specific_priorities": False,
            "addresses_request": False,
            "has_generic_responses": False,
            "uses_expertise": False,
            "response_details": []
        }
        
        # Keywords that indicate specific priorities
        priority_keywords = [
            "priority", "priorities", "first", "second", "third", "1.", "2.", "3.",
            "most important", "critical", "essential", "key", "focus on",
            "start with", "begin with", "initially", "primary", "secondary"
        ]
        
        # Generic response patterns to avoid
        generic_patterns = [
            "ready to work together",
            "great to collaborate",
            "excited to work",
            "looking forward to",
            "happy to help",
            "let's get started"
        ]
        
        # Request-specific keywords
        request_keywords = ["device", "building", "development", "construction", "design"]
        
        for i, message in enumerate(agent_messages):
            agent_name = message.get("agent_name", f"Agent {i+1}")
            message_text = message.get("message", "").lower()
            
            print(f"\n🤖 {agent_name}:")
            print(f"   Message: {message.get('message', '')[:100]}...")
            
            # Check for specific priorities
            has_priorities = any(keyword in message_text for keyword in priority_keywords)
            if has_priorities:
                results["has_specific_priorities"] = True
                print(f"   ✅ Contains specific priorities")
            else:
                print(f"   ❌ No specific priorities found")
            
            # Check if addresses the request
            addresses_request = any(keyword in message_text for keyword in request_keywords)
            if addresses_request:
                results["addresses_request"] = True
                print(f"   ✅ Addresses the request")
            else:
                print(f"   ❌ Doesn't clearly address the request")
            
            # Check for generic responses
            is_generic = any(pattern in message_text for pattern in generic_patterns)
            if is_generic:
                results["has_generic_responses"] = True
                print(f"   ❌ Contains generic response patterns")
            else:
                print(f"   ✅ No generic response patterns")
            
            # Check for expertise usage (longer, detailed responses)
            uses_expertise = len(message_text) > 50 and ("because" in message_text or "since" in message_text or "due to" in message_text)
            if uses_expertise:
                results["uses_expertise"] = True
                print(f"   ✅ Uses expertise/reasoning")
            else:
                print(f"   ⚠️ Limited expertise demonstration")
            
            results["response_details"].append({
                "agent": agent_name,
                "message": message.get("message", ""),
                "has_priorities": has_priorities,
                "addresses_request": addresses_request,
                "is_generic": is_generic,
                "uses_expertise": uses_expertise
            })
        
        return results
    
    def test_caching_system(self):
        """Test the caching system with exact matches and complex messages"""
        print("\n⚡ TESTING CACHING SYSTEM")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test 1: Simple greeting that should use cache
        print("\n1️⃣ Testing exact match caching with 'hello'")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": "hello"},
                headers=headers
            )
            end_time = time.time()
            hello_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                agent_responses = data.get("agent_responses", {})
                messages = agent_responses.get("messages", [])
                agent_messages = [msg for msg in messages if msg.get("agent_name") != "Observer (You)"]
                
                # Cache should make this very fast (under 2 seconds)
                uses_cache = hello_time < 2.0
                self.log_test("Hello Message Caching", uses_cache, f"Response time: {hello_time:.2f}s")
                
                print(f"   Response time: {hello_time:.2f}s")
                print(f"   Agent responses: {len(agent_messages)}")
                
                # Check if responses look cached (short, similar)
                if agent_messages:
                    avg_length = sum(len(msg.get("message", "")) for msg in agent_messages) / len(agent_messages)
                    print(f"   Average response length: {avg_length:.1f} characters")
                
            else:
                self.log_test("Hello Message Caching", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Hello Message Caching", False, f"Error: {e}")
        
        # Test 2: Complex message that should NOT use cache
        print("\n2️⃣ Testing complex message (no cache)")
        
        complex_msg = "analyze the technical feasibility of implementing quantum error correction in our next generation processor design"
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": complex_msg},
                headers=headers
            )
            end_time = time.time()
            complex_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                agent_responses = data.get("agent_responses", {})
                messages = agent_responses.get("messages", [])
                agent_messages = [msg for msg in messages if msg.get("agent_name") != "Observer (You)"]
                
                # Complex message should take longer and provide detailed responses
                no_cache_used = complex_time > hello_time  # Should be slower than cached response
                detailed_responses = False
                
                if agent_messages:
                    avg_length = sum(len(msg.get("message", "")) for msg in agent_messages) / len(agent_messages)
                    detailed_responses = avg_length > 50  # Detailed responses should be longer
                    print(f"   Average response length: {avg_length:.1f} characters")
                
                test_passed = no_cache_used and detailed_responses
                details = f"Time: {complex_time:.2f}s, Detailed: {detailed_responses}"
                self.log_test("Complex Message (No Cache)", test_passed, details)
                
                print(f"   Response time: {complex_time:.2f}s")
                print(f"   Agent responses: {len(agent_messages)}")
                
            else:
                self.log_test("Complex Message (No Cache)", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Complex Message (No Cache)", False, f"Error: {e}")
        
        # Test 3: Verify no partial matching
        print("\n3️⃣ Testing no partial matching")
        
        partial_msg = "hello there everyone"  # Should NOT match "hello" cache
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": partial_msg},
                headers=headers
            )
            end_time = time.time()
            partial_time = end_time - start_time
            
            if response.status_code == 200:
                # This should take longer than exact "hello" match since it shouldn't use cache
                no_partial_match = partial_time > hello_time
                details = f"Time: {partial_time:.2f}s vs hello: {hello_time:.2f}s"
                self.log_test("No Partial Matching", no_partial_match, details)
                
                print(f"   Response time: {partial_time:.2f}s")
                print(f"   No partial cache match: {no_partial_match}")
                
            else:
                self.log_test("No Partial Matching", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("No Partial Matching", False, f"Error: {e}")
    
    def test_additional_quality_scenarios(self):
        """Test additional scenarios to verify response quality"""
        print("\n🔍 TESTING ADDITIONAL QUALITY SCENARIOS")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        test_scenarios = [
            {
                "name": "Technical Analysis Request",
                "message": "what are the main technical challenges we need to solve for this project",
                "expect_technical": True
            },
            {
                "name": "Strategic Planning Request", 
                "message": "what should be our roadmap for the next 6 months",
                "expect_strategic": True
            },
            {
                "name": "Risk Assessment Request",
                "message": "what are the biggest risks we should be aware of",
                "expect_risks": True
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📝 {scenario['name']}")
            
            try:
                response = requests.post(
                    f"{API_URL}/observer/send-message",
                    json={"observer_message": scenario["message"]},
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agent_responses = data.get("agent_responses", {})
                    messages = agent_responses.get("messages", [])
                    agent_messages = [msg for msg in messages if msg.get("agent_name") != "Observer (You)"]
                    
                    # Analyze response quality
                    quality_score = 0
                    total_checks = 0
                    
                    for msg in agent_messages:
                        message_text = msg.get("message", "").lower()
                        
                        # Check for substantive content (not generic)
                        total_checks += 1
                        if len(message_text) > 30 and not any(generic in message_text for generic in ["ready to work", "great to collaborate"]):
                            quality_score += 1
                        
                        # Check for scenario-specific content
                        if scenario.get("expect_technical") and any(word in message_text for word in ["technical", "technology", "implementation", "system"]):
                            quality_score += 1
                            total_checks += 1
                        elif scenario.get("expect_strategic") and any(word in message_text for word in ["strategy", "plan", "roadmap", "timeline", "milestone"]):
                            quality_score += 1
                            total_checks += 1
                        elif scenario.get("expect_risks") and any(word in message_text for word in ["risk", "challenge", "problem", "issue", "concern"]):
                            quality_score += 1
                            total_checks += 1
                    
                    quality_percentage = (quality_score / total_checks * 100) if total_checks > 0 else 0
                    test_passed = quality_percentage >= 70  # 70% quality threshold
                    
                    details = f"Quality: {quality_percentage:.1f}% ({quality_score}/{total_checks})"
                    self.log_test(scenario["name"], test_passed, details)
                    
                    print(f"   Responses: {len(agent_messages)}")
                    print(f"   Quality Score: {quality_percentage:.1f}%")
                    
                else:
                    self.log_test(scenario["name"], False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(scenario["name"], False, f"Error: {e}")
    
    def cleanup_test_agents(self):
        """Clean up test agents"""
        print("\n🧹 CLEANING UP TEST AGENTS")
        print("-" * 40)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        cleaned_count = 0
        
        for agent_id in self.agent_ids:
            try:
                response = requests.delete(
                    f"{API_URL}/agents/{agent_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    cleaned_count += 1
                    print(f"✅ Deleted agent: {agent_id}")
                else:
                    print(f"❌ Failed to delete agent {agent_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error deleting agent {agent_id}: {e}")
        
        self.log_test("Test Agent Cleanup", cleaned_count == len(self.agent_ids), f"Cleaned {cleaned_count}/{len(self.agent_ids)} agents")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏁 OBSERVER CHAT QUALITY TEST SUMMARY")
        print("="*80)
        
        passed_tests = [t for t in self.test_results if t["passed"]]
        failed_tests = [t for t in self.test_results if not t["passed"]]
        
        print(f"📊 Results: {len(passed_tests)} passed, {len(failed_tests)} failed")
        print(f"📈 Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
        for test in passed_tests:
            print(f"   • {test['name']}")
            if test['details']:
                print(f"     {test['details']}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['name']}")
                if test['details']:
                    print(f"     {test['details']}")
        
        # Overall assessment
        critical_tests = [
            "Complex Priority Request Quality",
            "Hello Message Caching", 
            "Complex Message (No Cache)",
            "No Partial Matching"
        ]
        
        critical_passed = [t for t in self.test_results if t["name"] in critical_tests and t["passed"]]
        
        print(f"\n🎯 CRITICAL REQUIREMENTS:")
        print(f"   • Specific priority responses: {'✅' if any('Priority Request' in t['name'] and t['passed'] for t in self.test_results) else '❌'}")
        print(f"   • No generic responses: {'✅' if any('Priority Request' in t['name'] and t['passed'] for t in self.test_results) else '❌'}")
        print(f"   • Caching system working: {'✅' if len([t for t in self.test_results if 'Caching' in t['name'] and t['passed']]) >= 2 else '❌'}")
        print(f"   • No partial matching: {'✅' if any('Partial Matching' in t['name'] and t['passed'] for t in self.test_results) else '❌'}")
        
        overall_success = len(critical_passed) >= 3  # At least 3 of 4 critical tests must pass
        
        print(f"\n🏆 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ NEEDS IMPROVEMENT'}")
        
        if overall_success:
            print("   Observer Chat response quality improvements are working correctly!")
        else:
            print("   Observer Chat response quality needs further improvement.")
        
        return overall_success

def main():
    """Main test execution"""
    tester = ObserverChatQualityTester()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return False
    
    # Step 2: Setup test agents
    if not tester.setup_test_agents():
        print("❌ Failed to setup test agents. Cannot proceed with quality tests.")
        return False
    
    # Step 3: Test the specific complex priority request
    tester.test_complex_priority_request()
    
    # Step 4: Test caching system
    tester.test_caching_system()
    
    # Step 5: Test additional quality scenarios
    tester.test_additional_quality_scenarios()
    
    # Step 6: Cleanup
    tester.cleanup_test_agents()
    
    # Step 7: Print summary
    success = tester.print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)