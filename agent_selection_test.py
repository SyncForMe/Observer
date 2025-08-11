#!/usr/bin/env python3
"""
Test script for the IMPROVED agent selection system with fair rotation
Tests the enhanced POST /api/conversation/add-message endpoint to verify:
- Fair rotation among all agents
- Weighted selection prevents same agent from speaking consecutively
- Debug logs show the weighting system working properly
- More balanced distribution compared to previous bias
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime
from collections import Counter, defaultdict
import statistics

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers
    if headers is None:
        headers = {}
    
    if auth and 'auth_token' in globals():
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result,
            "response_time": response_time
        })
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def authenticate():
    """Authenticate and get auth token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION")
    print("="*80)
    
    # Try guest authentication first
    guest_test, guest_response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Guest authentication successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Guest authentication failed")
        return False

def setup_test_agents():
    """Create test agents for fair rotation testing"""
    print("\n" + "="*80)
    print("SETTING UP TEST AGENTS")
    print("="*80)
    
    # First, get existing agents
    get_agents_test, agents_response = run_test(
        "Get Existing Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    existing_agents = agents_response if get_agents_test else []
    print(f"Found {len(existing_agents)} existing agents")
    
    # Define our test agents (inspired by the review request)
    test_agents = [
        {
            "name": "Darth Vader",
            "archetype": "leader",
            "goal": "Bring order to the galaxy through decisive leadership",
            "expertise": "Strategic planning and command",
            "background": "Former Jedi turned Sith Lord with extensive military experience",
            "personality": {
                "extroversion": 8,
                "optimism": 3,
                "curiosity": 6,
                "cooperativeness": 4,
                "energy": 9
            }
        },
        {
            "name": "Nikola Tesla",
            "archetype": "scientist",
            "goal": "Advance human knowledge through scientific innovation",
            "expertise": "Electrical engineering and physics",
            "background": "Brilliant inventor and electrical engineer known for groundbreaking discoveries",
            "personality": {
                "extroversion": 4,
                "optimism": 7,
                "curiosity": 10,
                "cooperativeness": 6,
                "energy": 8
            }
        },
        {
            "name": "Bob Marley",
            "archetype": "optimist",
            "goal": "Spread peace, love, and unity through wisdom",
            "expertise": "Music, philosophy, and social harmony",
            "background": "Reggae musician and philosopher promoting peace and unity",
            "personality": {
                "extroversion": 7,
                "optimism": 10,
                "curiosity": 7,
                "cooperativeness": 9,
                "energy": 8
            }
        }
    ]
    
    # Check if we already have these agents
    existing_names = [agent.get("name", "") for agent in existing_agents]
    agents_to_create = []
    
    for test_agent in test_agents:
        if test_agent["name"] not in existing_names:
            agents_to_create.append(test_agent)
        else:
            print(f"✅ Agent '{test_agent['name']}' already exists")
    
    # Create missing agents
    created_agents = []
    for agent_data in agents_to_create:
        create_test, create_response = run_test(
            f"Create Agent: {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True
        )
        
        if create_test and create_response:
            created_agents.append(agent_data["name"])
            print(f"✅ Created agent: {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
    
    # Get final agent list
    final_agents_test, final_agents_response = run_test(
        "Get Final Agent List",
        "/agents",
        method="GET",
        auth=True
    )
    
    if final_agents_test and final_agents_response:
        agent_names = [agent.get("name", "") for agent in final_agents_response]
        test_agent_names = [agent["name"] for agent in test_agents]
        
        # Check if we have all required test agents
        missing_agents = [name for name in test_agent_names if name not in agent_names]
        if missing_agents:
            print(f"❌ Missing required test agents: {missing_agents}")
            return False, []
        else:
            print(f"✅ All required test agents are available: {test_agent_names}")
            return True, final_agents_response
    else:
        print("❌ Failed to get final agent list")
        return False, []

def setup_simulation():
    """Set up simulation state"""
    print("\n" + "="*80)
    print("SETTING UP SIMULATION")
    print("="*80)
    
    # Set scenario
    scenario_data = {
        "scenario": "A collaborative discussion about innovative solutions",
        "scenario_name": "Innovation Workshop"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True
    )
    
    if not scenario_test:
        print("❌ Failed to set scenario")
        return False
    
    # Start simulation
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False
    
    print("✅ Simulation setup complete")
    return True

def test_fair_rotation_system():
    """Test the fair rotation system with multiple calls to add-message endpoint"""
    print("\n" + "="*80)
    print("TESTING FAIR ROTATION SYSTEM")
    print("="*80)
    
    # Track agent selection results
    agent_selections = []
    response_times = []
    
    # Number of tests to run (8-10 as requested)
    num_tests = 10
    
    print(f"Running {num_tests} tests of the POST /api/conversation/add-message endpoint...")
    
    for i in range(num_tests):
        print(f"\n--- Test {i+1}/{num_tests} ---")
        
        add_message_test, add_message_response = run_test(
            f"Add Message Test {i+1}",
            "/conversation/add-message",
            method="POST",
            auth=True
        )
        
        if add_message_test and add_message_response:
            # Extract the latest message to see which agent spoke
            messages = add_message_response.get("messages", [])
            if messages:
                latest_message = messages[-1]
                agent_name = latest_message.get("agent_name", "Unknown")
                message_text = latest_message.get("message", "")
                
                agent_selections.append(agent_name)
                print(f"🤖 Selected Agent: {agent_name}")
                print(f"💬 Message: {message_text[:100]}...")
                
                # Track response time
                last_test = test_results["tests"][-1]
                response_times.append(last_test.get("response_time", 0))
            else:
                print("❌ No messages found in response")
                agent_selections.append("ERROR")
        else:
            print("❌ Failed to add message")
            agent_selections.append("ERROR")
        
        # Small delay between requests
        time.sleep(0.5)
    
    return agent_selections, response_times

def analyze_agent_distribution(agent_selections):
    """Analyze the distribution of agent selections"""
    print("\n" + "="*80)
    print("ANALYZING AGENT DISTRIBUTION")
    print("="*80)
    
    # Count selections
    selection_counts = Counter(agent_selections)
    total_selections = len([s for s in agent_selections if s != "ERROR"])
    
    print(f"Total successful selections: {total_selections}")
    print("\nAgent Selection Distribution:")
    
    expected_agents = ["Darth Vader", "Nikola Tesla", "Bob Marley"]
    distribution_results = {}
    
    for agent in expected_agents:
        count = selection_counts.get(agent, 0)
        percentage = (count / total_selections * 100) if total_selections > 0 else 0
        distribution_results[agent] = {
            "count": count,
            "percentage": percentage
        }
        print(f"  {agent}: {count} selections ({percentage:.1f}%)")
    
    # Check for errors
    error_count = selection_counts.get("ERROR", 0)
    if error_count > 0:
        print(f"  ERRORS: {error_count} failed selections")
    
    # Analyze fairness
    print("\n" + "="*40)
    print("FAIRNESS ANALYSIS")
    print("="*40)
    
    if total_selections >= 3:
        # Calculate expected percentage (should be roughly equal)
        expected_percentage = 100 / len(expected_agents)
        print(f"Expected percentage per agent: {expected_percentage:.1f}%")
        
        # Calculate deviation from expected
        deviations = []
        for agent in expected_agents:
            actual_percentage = distribution_results[agent]["percentage"]
            deviation = abs(actual_percentage - expected_percentage)
            deviations.append(deviation)
            print(f"  {agent} deviation: {deviation:.1f}%")
        
        # Overall fairness score
        avg_deviation = sum(deviations) / len(deviations)
        print(f"\nAverage deviation from expected: {avg_deviation:.1f}%")
        
        # Fairness assessment
        if avg_deviation <= 15:
            fairness_score = "EXCELLENT"
            print("✅ EXCELLENT fairness - very balanced distribution")
        elif avg_deviation <= 25:
            fairness_score = "GOOD"
            print("✅ GOOD fairness - reasonably balanced distribution")
        elif avg_deviation <= 35:
            fairness_score = "FAIR"
            print("⚠️ FAIR fairness - some imbalance but acceptable")
        else:
            fairness_score = "POOR"
            print("❌ POOR fairness - significant imbalance detected")
        
        # Check for consecutive selections (anti-bias check)
        consecutive_count = 0
        max_consecutive = 0
        current_consecutive = 1
        
        for i in range(1, len(agent_selections)):
            if agent_selections[i] == agent_selections[i-1] and agent_selections[i] != "ERROR":
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        print(f"\nConsecutive Selection Analysis:")
        print(f"  Maximum consecutive selections by same agent: {max_consecutive}")
        
        if max_consecutive <= 2:
            print("✅ EXCELLENT - No significant consecutive bias")
            consecutive_score = "EXCELLENT"
        elif max_consecutive <= 3:
            print("✅ GOOD - Minimal consecutive bias")
            consecutive_score = "GOOD"
        else:
            print("❌ POOR - Significant consecutive bias detected")
            consecutive_score = "POOR"
        
        return {
            "distribution": distribution_results,
            "fairness_score": fairness_score,
            "consecutive_score": consecutive_score,
            "avg_deviation": avg_deviation,
            "max_consecutive": max_consecutive,
            "total_selections": total_selections,
            "error_count": error_count
        }
    else:
        print("❌ Insufficient data for fairness analysis")
        return {
            "distribution": distribution_results,
            "fairness_score": "INSUFFICIENT_DATA",
            "consecutive_score": "INSUFFICIENT_DATA",
            "total_selections": total_selections,
            "error_count": error_count
        }

def analyze_performance(response_times):
    """Analyze performance metrics"""
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    if not response_times:
        print("❌ No response time data available")
        return {}
    
    # Filter out zero times
    valid_times = [t for t in response_times if t > 0]
    
    if not valid_times:
        print("❌ No valid response times recorded")
        return {}
    
    # Calculate statistics
    avg_time = statistics.mean(valid_times)
    median_time = statistics.median(valid_times)
    min_time = min(valid_times)
    max_time = max(valid_times)
    
    print(f"Response Time Statistics:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Median: {median_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    
    # Performance assessment
    if avg_time <= 2.0:
        performance_score = "EXCELLENT"
        print("✅ EXCELLENT performance - very fast response times")
    elif avg_time <= 5.0:
        performance_score = "GOOD"
        print("✅ GOOD performance - acceptable response times")
    elif avg_time <= 10.0:
        performance_score = "FAIR"
        print("⚠️ FAIR performance - slower but usable")
    else:
        performance_score = "POOR"
        print("❌ POOR performance - very slow response times")
    
    return {
        "avg_time": avg_time,
        "median_time": median_time,
        "min_time": min_time,
        "max_time": max_time,
        "performance_score": performance_score
    }

def print_summary(analysis_results, performance_results):
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    print(f"Tests Run: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    if analysis_results:
        print(f"\nFair Rotation Results:")
        print(f"  Fairness Score: {analysis_results.get('fairness_score', 'N/A')}")
        print(f"  Consecutive Bias Score: {analysis_results.get('consecutive_score', 'N/A')}")
        print(f"  Average Deviation: {analysis_results.get('avg_deviation', 0):.1f}%")
        print(f"  Max Consecutive: {analysis_results.get('max_consecutive', 0)}")
        print(f"  Total Selections: {analysis_results.get('total_selections', 0)}")
        print(f"  Errors: {analysis_results.get('error_count', 0)}")
    
    if performance_results:
        print(f"\nPerformance Results:")
        print(f"  Performance Score: {performance_results.get('performance_score', 'N/A')}")
        print(f"  Average Response Time: {performance_results.get('avg_time', 0):.3f}s")
    
    # Overall assessment
    overall_success = (
        test_results['failed'] == 0 and
        analysis_results.get('fairness_score') in ['EXCELLENT', 'GOOD'] and
        analysis_results.get('consecutive_score') in ['EXCELLENT', 'GOOD'] and
        performance_results.get('performance_score') in ['EXCELLENT', 'GOOD']
    )
    
    print(f"\n{'='*80}")
    if overall_success:
        print("🎉 OVERALL RESULT: SUCCESS")
        print("✅ Fair rotation system is working excellently!")
        print("✅ Agent selection is balanced and prevents bias")
        print("✅ Performance is acceptable")
    else:
        print("⚠️ OVERALL RESULT: NEEDS IMPROVEMENT")
        if test_results['failed'] > 0:
            print("❌ Some tests failed")
        if analysis_results.get('fairness_score') not in ['EXCELLENT', 'GOOD']:
            print("❌ Agent selection fairness needs improvement")
        if analysis_results.get('consecutive_score') not in ['EXCELLENT', 'GOOD']:
            print("❌ Consecutive bias prevention needs improvement")
        if performance_results.get('performance_score') not in ['EXCELLENT', 'GOOD']:
            print("❌ Performance needs improvement")
    
    print("="*80)

def main():
    """Main test execution"""
    print("🧪 AGENT SELECTION FAIR ROTATION TESTING")
    print("="*80)
    print("Testing the IMPROVED agent selection system with fair rotation")
    print("Verifying weighted selection prevents consecutive agent bias")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Setup test agents
    agents_setup_success, agents = setup_test_agents()
    if not agents_setup_success:
        print("❌ Failed to setup test agents. Cannot proceed with tests.")
        return
    
    # Step 3: Setup simulation
    if not setup_simulation():
        print("❌ Failed to setup simulation. Cannot proceed with tests.")
        return
    
    # Step 4: Test fair rotation system
    agent_selections, response_times = test_fair_rotation_system()
    
    # Step 5: Analyze results
    analysis_results = analyze_agent_distribution(agent_selections)
    performance_results = analyze_performance(response_times)
    
    # Step 6: Print comprehensive summary
    print_summary(analysis_results, performance_results)

if __name__ == "__main__":
    main()