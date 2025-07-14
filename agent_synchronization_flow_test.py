#!/usr/bin/env python3
"""
Agent Library → Observatory Synchronization Flow Test

This test script specifically tests the complete synchronization flow between
Agent Library and Observatory to identify why agents aren't appearing in Observatory.

Test Flow:
1. Use guest authentication to get a token
2. Create a test agent via POST /api/agents (simulating Agent Library add)
3. Immediately fetch agents via GET /api/agents (simulating Observatory fetch)
4. Check if the created agent appears in the response
5. Test timing and caching issues
6. Test user association
7. Test the actual synchronization
"""

import requests
import json
import time
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class AgentSyncTester:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        self.created_agents = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        result = "✅ PASS" if success else "❌ FAIL"
        print(f"{result}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper error handling"""
        url = f"{API_URL}{endpoint}"
        headers = {}
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            print(f"\n{method} {url}")
            print(f"Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
            except:
                response_data = {}
                print(f"Response (non-JSON): {response.text}")
                
            success = response.status_code == expected_status
            return success, response_data
            
        except Exception as e:
            print(f"Request failed: {e}")
            return False, {}
    
    def test_guest_authentication(self):
        """Test 1: Use guest authentication to get a token"""
        print("\n" + "="*80)
        print("TEST 1: GUEST AUTHENTICATION")
        print("="*80)
        
        success, response = self.make_request("POST", "/auth/test-login")
        
        if success and response:
            self.auth_token = response.get("access_token")
            user_data = response.get("user", {})
            self.user_id = user_data.get("id")
            
            if self.auth_token and self.user_id:
                self.log_test("Guest Authentication", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("Guest Authentication", False, "Missing token or user_id in response")
                return False
        else:
            self.log_test("Guest Authentication", False, "Failed to get valid response")
            return False
    
    def test_create_agent(self, agent_name=None):
        """Test 2: Create a test agent via POST /api/agents"""
        print("\n" + "="*80)
        print("TEST 2: CREATE TEST AGENT")
        print("="*80)
        
        if not agent_name:
            agent_name = f"Test Agent {uuid.uuid4().hex[:8]}"
        
        agent_data = {
            "name": agent_name,
            "archetype": "scientist",
            "personality": {
                "extroversion": 5,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 6
            },
            "goal": "Test the synchronization between Agent Library and Observatory",
            "expertise": "Software Testing and Quality Assurance",
            "background": "Experienced in testing distributed systems and API synchronization",
            "memory_summary": "Created for testing agent synchronization flow",
            "avatar_prompt": "Professional software tester",
            "avatar_url": ""
        }
        
        success, response = self.make_request("POST", "/agents", agent_data, 201)
        
        if success and response:
            agent_id = response.get("id")
            if agent_id:
                self.created_agents.append(agent_id)
                self.log_test("Create Test Agent", True, f"Agent ID: {agent_id}, Name: {agent_name}")
                return agent_id, agent_name
            else:
                self.log_test("Create Test Agent", False, "No agent ID in response")
                return None, None
        else:
            self.log_test("Create Test Agent", False, "Failed to create agent")
            return None, None
    
    def test_fetch_agents(self, expected_agent_id=None, expected_agent_name=None):
        """Test 3: Immediately fetch agents via GET /api/agents"""
        print("\n" + "="*80)
        print("TEST 3: FETCH AGENTS (OBSERVATORY VIEW)")
        print("="*80)
        
        success, response = self.make_request("GET", "/agents")
        
        if success and isinstance(response, list):
            agent_count = len(response)
            print(f"Total agents returned: {agent_count}")
            
            # Check if the expected agent appears
            if expected_agent_id:
                found_agent = None
                for agent in response:
                    if agent.get("id") == expected_agent_id:
                        found_agent = agent
                        break
                
                if found_agent:
                    self.log_test("Agent Synchronization", True, 
                                f"Created agent '{expected_agent_name}' appears in Observatory")
                    return True, response
                else:
                    self.log_test("Agent Synchronization", False, 
                                f"Created agent '{expected_agent_name}' NOT found in Observatory")
                    print("Available agents:")
                    for agent in response:
                        print(f"  - {agent.get('name')} (ID: {agent.get('id')})")
                    return False, response
            else:
                self.log_test("Fetch Agents", True, f"Retrieved {agent_count} agents")
                return True, response
        else:
            self.log_test("Fetch Agents", False, "Failed to fetch agents or invalid response format")
            return False, []
    
    def test_timing_and_caching(self):
        """Test 4: Test timing and caching issues"""
        print("\n" + "="*80)
        print("TEST 4: TIMING AND CACHING ISSUES")
        print("="*80)
        
        # Create multiple agents in sequence and test immediate retrieval
        timing_results = []
        
        for i in range(3):
            print(f"\n--- Creating Agent {i+1}/3 ---")
            
            # Record start time
            start_time = time.time()
            
            # Create agent
            agent_id, agent_name = self.test_create_agent(f"Timing Test Agent {i+1}")
            
            if not agent_id:
                self.log_test(f"Timing Test {i+1} - Create", False, "Failed to create agent")
                continue
            
            # Immediately fetch agents
            create_time = time.time()
            success, agents = self.test_fetch_agents(agent_id, agent_name)
            fetch_time = time.time()
            
            # Calculate timing
            create_duration = create_time - start_time
            fetch_duration = fetch_time - create_time
            total_duration = fetch_time - start_time
            
            timing_results.append({
                "agent_id": agent_id,
                "agent_name": agent_name,
                "create_duration": create_duration,
                "fetch_duration": fetch_duration,
                "total_duration": total_duration,
                "sync_success": success
            })
            
            print(f"Create time: {create_duration:.3f}s")
            print(f"Fetch time: {fetch_duration:.3f}s")
            print(f"Total time: {total_duration:.3f}s")
            print(f"Sync success: {success}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Analyze timing results
        successful_syncs = [r for r in timing_results if r["sync_success"]]
        failed_syncs = [r for r in timing_results if not r["sync_success"]]
        
        if len(successful_syncs) == len(timing_results):
            self.log_test("Timing and Caching", True, 
                        f"All {len(timing_results)} agents synchronized immediately")
        elif len(successful_syncs) > 0:
            self.log_test("Timing and Caching", False, 
                        f"Only {len(successful_syncs)}/{len(timing_results)} agents synchronized")
        else:
            self.log_test("Timing and Caching", False, "No agents synchronized properly")
        
        return timing_results
    
    def test_user_association(self):
        """Test 5: Test user association"""
        print("\n" + "="*80)
        print("TEST 5: USER ASSOCIATION")
        print("="*80)
        
        # Get all agents for current user
        success, agents = self.test_fetch_agents()
        
        if not success:
            self.log_test("User Association", False, "Failed to fetch agents")
            return False
        
        # Check user_id association
        user_id_issues = []
        for agent in agents:
            agent_user_id = agent.get("user_id")
            if agent_user_id != self.user_id:
                user_id_issues.append({
                    "agent_name": agent.get("name"),
                    "agent_id": agent.get("id"),
                    "expected_user_id": self.user_id,
                    "actual_user_id": agent_user_id
                })
        
        if not user_id_issues:
            self.log_test("User Association", True, 
                        f"All {len(agents)} agents correctly associated with user {self.user_id}")
            return True
        else:
            self.log_test("User Association", False, 
                        f"{len(user_id_issues)} agents have incorrect user_id association")
            for issue in user_id_issues:
                print(f"  - Agent '{issue['agent_name']}': expected {issue['expected_user_id']}, got {issue['actual_user_id']}")
            return False
    
    def test_multiple_operations(self):
        """Test 6: Test multiple create/fetch operations"""
        print("\n" + "="*80)
        print("TEST 6: MULTIPLE OPERATIONS")
        print("="*80)
        
        operations_results = []
        
        # Perform 5 create-fetch cycles
        for i in range(5):
            print(f"\n--- Operation Cycle {i+1}/5 ---")
            
            # Create agent
            agent_id, agent_name = self.test_create_agent(f"Multi-Op Agent {i+1}")
            
            if not agent_id:
                operations_results.append(False)
                continue
            
            # Fetch and verify
            success, agents = self.test_fetch_agents(agent_id, agent_name)
            operations_results.append(success)
            
            # Brief pause
            time.sleep(0.2)
        
        success_count = sum(operations_results)
        total_count = len(operations_results)
        
        if success_count == total_count:
            self.log_test("Multiple Operations", True, 
                        f"All {total_count} create-fetch cycles successful")
        else:
            self.log_test("Multiple Operations", False, 
                        f"Only {success_count}/{total_count} create-fetch cycles successful")
        
        return operations_results
    
    def test_api_consistency(self):
        """Test 7: Test API consistency"""
        print("\n" + "="*80)
        print("TEST 7: API CONSISTENCY")
        print("="*80)
        
        # Make multiple GET requests and compare results
        responses = []
        
        for i in range(3):
            print(f"\nFetch attempt {i+1}/3:")
            success, agents = self.make_request("GET", "/agents")
            
            if success:
                responses.append(agents)
                print(f"Retrieved {len(agents)} agents")
            else:
                responses.append(None)
                print("Failed to retrieve agents")
            
            time.sleep(0.1)
        
        # Check consistency
        valid_responses = [r for r in responses if r is not None]
        
        if len(valid_responses) < 2:
            self.log_test("API Consistency", False, "Not enough valid responses to compare")
            return False
        
        # Compare agent counts
        agent_counts = [len(r) for r in valid_responses]
        consistent_count = len(set(agent_counts)) == 1
        
        # Compare agent IDs
        agent_id_sets = [set(agent.get("id") for agent in r) for r in valid_responses]
        consistent_ids = all(ids == agent_id_sets[0] for ids in agent_id_sets)
        
        if consistent_count and consistent_ids:
            self.log_test("API Consistency", True, 
                        f"All responses consistent with {agent_counts[0]} agents")
        else:
            self.log_test("API Consistency", False, 
                        f"Inconsistent responses: counts={agent_counts}, ids_match={consistent_ids}")
        
        return consistent_count and consistent_ids
    
    def cleanup_test_agents(self):
        """Clean up created test agents"""
        print("\n" + "="*80)
        print("CLEANUP: REMOVING TEST AGENTS")
        print("="*80)
        
        cleanup_results = []
        
        for agent_id in self.created_agents:
            print(f"\nDeleting agent {agent_id}")
            success, response = self.make_request("DELETE", f"/agents/{agent_id}", expected_status=200)
            cleanup_results.append(success)
            
            if success:
                print(f"✅ Successfully deleted agent {agent_id}")
            else:
                print(f"❌ Failed to delete agent {agent_id}")
        
        successful_deletions = sum(cleanup_results)
        total_agents = len(self.created_agents)
        
        print(f"\nCleanup Summary: {successful_deletions}/{total_agents} agents deleted")
        
        return successful_deletions == total_agents
    
    def print_final_summary(self):
        """Print final test summary"""
        print("\n" + "="*80)
        print("AGENT SYNCHRONIZATION FLOW TEST SUMMARY")
        print("="*80)
        
        passed_tests = [t for t in self.test_results if t["success"]]
        failed_tests = [t for t in self.test_results if not t["success"]]
        
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  ❌ {test['name']}: {test['details']}")
        
        if passed_tests:
            print("\nPassed Tests:")
            for test in passed_tests:
                print(f"  ✅ {test['name']}")
        
        # Overall assessment
        success_rate = len(passed_tests) / len(self.test_results) * 100
        
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Agent synchronization is working very well!")
        elif success_rate >= 70:
            print("✅ GOOD: Agent synchronization is mostly working with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Agent synchronization has significant issues")
        else:
            print("❌ CRITICAL: Agent synchronization is severely broken")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    print("🧪 AGENT LIBRARY → OBSERVATORY SYNCHRONIZATION FLOW TEST")
    print("="*80)
    print("This test verifies the complete synchronization flow between")
    print("Agent Library (create agents) and Observatory (view agents)")
    print("="*80)
    
    tester = AgentSyncTester()
    
    try:
        # Run all tests in sequence
        if not tester.test_guest_authentication():
            print("❌ CRITICAL: Cannot proceed without authentication")
            return False
        
        # Test basic create-fetch flow
        agent_id, agent_name = tester.test_create_agent("Primary Test Agent")
        if agent_id:
            tester.test_fetch_agents(agent_id, agent_name)
        
        # Run comprehensive tests
        tester.test_timing_and_caching()
        tester.test_user_association()
        tester.test_multiple_operations()
        tester.test_api_consistency()
        
        # Print results
        overall_success = tester.print_final_summary()
        
        # Cleanup
        tester.cleanup_test_agents()
        
        return overall_success
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        tester.cleanup_test_agents()
        return False
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        tester.cleanup_test_agents()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)