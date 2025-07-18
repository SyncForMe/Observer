#!/usr/bin/env python3
"""
Focused test script for the specific issues reported by the user:
1. Set Scenario Functionality - scenario not being set properly
2. Agent Creation - agents not showing in agent list
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test results"""
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

def test_guest_authentication():
    """Test guest authentication to get JWT token"""
    print("\n🔐 Testing Guest Authentication...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data and 'user' in data:
                token = data['access_token']
                user = data['user']
                log_test("Guest Authentication", True, f"Token received, user_id: {user.get('id', 'N/A')}")
                return token, user['id']
            else:
                log_test("Guest Authentication", False, "Missing access_token or user in response")
                return None, None
        else:
            log_test("Guest Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
            return None, None
            
    except Exception as e:
        log_test("Guest Authentication", False, f"Exception: {str(e)}")
        return None, None

def test_simulation_reset(token):
    """Test simulation reset to clear existing state"""
    print("\n🔄 Testing Simulation Reset...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_URL}/simulation/reset", headers=headers, timeout=10)
        
        if response.status_code == 200:
            log_test("Simulation Reset", True, "Reset successful")
            return True
        else:
            log_test("Simulation Reset", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Simulation Reset", False, f"Exception: {str(e)}")
        return False

def test_set_scenario(token):
    """Test setting a scenario"""
    print("\n📝 Testing Set Scenario Functionality...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    scenario_data = {
        "scenario": "A team of scientists discovers a mysterious quantum signal",
        "scenario_name": "Quantum Signal Discovery"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", 
                               headers=headers, 
                               json=scenario_data, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Set Scenario Request", True, f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            log_test("Set Scenario Request", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Set Scenario Request", False, f"Exception: {str(e)}")
        return False

def test_get_simulation_state(token):
    """Test getting simulation state to verify scenario was saved"""
    print("\n📊 Testing Get Simulation State...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if scenario and scenario_name are present
            scenario = data.get('scenario', '')
            scenario_name = data.get('scenario_name', '')
            
            print(f"   📋 Scenario: {scenario}")
            print(f"   🏷️  Scenario Name: {scenario_name}")
            
            # Verify the scenario was saved correctly
            expected_scenario = "A team of scientists discovers a mysterious quantum signal"
            expected_name = "Quantum Signal Discovery"
            
            scenario_match = expected_scenario in scenario or scenario == expected_scenario
            name_match = scenario_name == expected_name
            
            if scenario_match and name_match:
                log_test("Scenario Persistence", True, "Scenario and name saved correctly")
                return True, data
            else:
                log_test("Scenario Persistence", False, f"Expected scenario: '{expected_scenario}', Got: '{scenario}'. Expected name: '{expected_name}', Got: '{scenario_name}'")
                return False, data
        else:
            log_test("Get Simulation State", False, f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("Get Simulation State", False, f"Exception: {str(e)}")
        return False, None

def test_create_agent(token, agent_data):
    """Test creating an agent"""
    print(f"\n🤖 Testing Agent Creation: {agent_data['name']}...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{API_URL}/agents", 
                               headers=headers, 
                               json=agent_data, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            agent_id = data.get('id')
            log_test(f"Create Agent: {agent_data['name']}", True, f"Agent ID: {agent_id}")
            return True, agent_id
        else:
            log_test(f"Create Agent: {agent_data['name']}", False, f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test(f"Create Agent: {agent_data['name']}", False, f"Exception: {str(e)}")
        return False, None

def test_get_agents(token, expected_count=None):
    """Test getting agents list"""
    print(f"\n👥 Testing Get Agents List...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            agent_count = len(data)
            
            print(f"   📊 Found {agent_count} agents")
            for i, agent in enumerate(data, 1):
                print(f"   {i}. {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
            
            if expected_count is not None:
                if agent_count == expected_count:
                    log_test("Agent List Count", True, f"Expected {expected_count}, got {agent_count}")
                else:
                    log_test("Agent List Count", False, f"Expected {expected_count}, got {agent_count}")
            else:
                log_test("Get Agents List", True, f"Retrieved {agent_count} agents")
            
            return True, data
        else:
            log_test("Get Agents List", False, f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("Get Agents List", False, f"Exception: {str(e)}")
        return False, None

def test_start_simulation(token):
    """Test starting simulation"""
    print("\n▶️ Testing Start Simulation...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{API_URL}/simulation/start", 
                               headers=headers, 
                               json={}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log_test("Start Simulation", True, f"Response: {json.dumps(data, indent=2)}")
            return True, data
        else:
            log_test("Start Simulation", False, f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("Start Simulation", False, f"Exception: {str(e)}")
        return False, None

def main():
    """Main test execution"""
    print("🧪 SCENARIO & AGENT CREATION TESTING")
    print("=" * 50)
    
    # Test 1: Authentication
    token, user_id = test_guest_authentication()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test 2: Reset simulation state
    test_simulation_reset(token)
    
    # Test 3: Set Scenario Functionality
    print("\n" + "="*50)
    print("🎯 TEST 1: SET SCENARIO FUNCTIONALITY")
    print("="*50)
    
    scenario_set = test_set_scenario(token)
    if scenario_set:
        scenario_persisted, state_data = test_get_simulation_state(token)
        if not scenario_persisted:
            print("❌ CRITICAL ISSUE: Scenario not persisting after being set!")
    
    # Test 4: Agent Creation Functionality
    print("\n" + "="*50)
    print("🎯 TEST 2: AGENT CREATION FUNCTIONALITY")
    print("="*50)
    
    # Create first agent
    agent1_data = {
        "name": "Dr. Test Agent",
        "archetype": "scientist",
        "goal": "Test goal",
        "expertise": "Testing",
        "background": "Test background",
        "personality": {
            "extroversion": 5,
            "optimism": 6,
            "curiosity": 8,
            "cooperativeness": 7,
            "energy": 6
        }
    }
    
    agent1_created, agent1_id = test_create_agent(token, agent1_data)
    
    # Check if first agent appears in list
    if agent1_created:
        agents_found, agents_data = test_get_agents(token, expected_count=1)
        if not agents_found or len(agents_data or []) == 0:
            print("❌ CRITICAL ISSUE: Created agent not appearing in agent list!")
    
    # Create second agent
    agent2_data = {
        "name": "Prof. Second Agent",
        "archetype": "researcher",
        "goal": "Research goal",
        "expertise": "Research",
        "background": "Research background",
        "personality": {
            "extroversion": 4,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 8,
            "energy": 5
        }
    }
    
    agent2_created, agent2_id = test_create_agent(token, agent2_data)
    
    # Check if both agents appear in list
    if agent2_created:
        agents_found, agents_data = test_get_agents(token, expected_count=2)
        if not agents_found or len(agents_data or []) != 2:
            print("❌ CRITICAL ISSUE: Not all created agents appearing in agent list!")
    
    # Test 5: Combined Functionality
    print("\n" + "="*50)
    print("🎯 TEST 3: COMBINED FUNCTIONALITY")
    print("="*50)
    
    # Verify scenario still persists after agent creation
    scenario_still_there, final_state = test_get_simulation_state(token)
    if not scenario_still_there:
        print("❌ CRITICAL ISSUE: Scenario lost after agent creation!")
    
    # Verify agents still persist
    final_agents_check, final_agents = test_get_agents(token)
    if not final_agents_check or len(final_agents or []) != 2:
        print("❌ CRITICAL ISSUE: Agents lost or not persisting!")
    
    # Try to start simulation with scenario and agents
    if scenario_still_there and final_agents_check:
        simulation_started, sim_data = test_start_simulation(token)
        if simulation_started:
            # Final state check after simulation start
            final_state_check, final_state_data = test_get_simulation_state(token)
            if final_state_check:
                is_active = final_state_data.get('is_active', False)
                scenario_after_start = final_state_data.get('scenario', '')
                print(f"   🎮 Simulation Active: {is_active}")
                print(f"   📋 Scenario After Start: {scenario_after_start}")
                
                if is_active and scenario_after_start:
                    log_test("Complete Workflow", True, "Scenario + Agents + Simulation Start all working")
                else:
                    log_test("Complete Workflow", False, f"Simulation active: {is_active}, Scenario present: {bool(scenario_after_start)}")
    
    # Print final results
    print("\n" + "="*50)
    print("📊 FINAL TEST RESULTS")
    print("="*50)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Pass Rate: {pass_rate:.1f}%")
    
    # Identify critical issues
    critical_issues = []
    for test in test_results["tests"]:
        if not test["passed"]:
            if "Scenario Persistence" in test["name"]:
                critical_issues.append("🚨 SCENARIO NOT PERSISTING - Set Scenario functionality broken")
            elif "Agent List" in test["name"] or "Create Agent" in test["name"]:
                critical_issues.append("🚨 AGENT CREATION/LISTING - Agents not showing in list")
            elif "Complete Workflow" in test["name"]:
                critical_issues.append("🚨 COMBINED FUNCTIONALITY - Scenario + Agent workflow broken")
    
    if critical_issues:
        print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
        for issue in critical_issues:
            print(f"   {issue}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND - Both functionalities working correctly")
    
    return test_results

if __name__ == "__main__":
    main()