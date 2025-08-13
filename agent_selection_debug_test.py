#!/usr/bin/env python3
"""
Agent Selection Debug Test for POST /api/conversation/add-message

This test debugs the reported issue where only "Bob Marley" is generating messages
even though the user has 3 agents configured (Darth Vader, Nikola Tesla, Bob Marley).

The test will:
1. Verify all 3 agents exist in the database
2. Test the random selection multiple times
3. Analyze if there's a bias in agent selection
4. Check for any filtering issues
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
from collections import Counter
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

def authenticate():
    """Authenticate and get JWT token"""
    print("\n" + "="*80)
    print("AUTHENTICATING USER")
    print("="*80)
    
    # Try guest authentication first
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            user_id = user.get("id")
            print(f"✅ Guest authentication successful")
            print(f"User ID: {user_id}")
            print(f"User Email: {user.get('email', 'N/A')}")
            return token, user_id
        else:
            print(f"❌ Guest authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def get_all_agents(token):
    """Get all agents for the authenticated user"""
    print("\n" + "="*80)
    print("RETRIEVING ALL USER AGENTS")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Successfully retrieved {len(agents)} agents")
            
            print("\nAgent Details:")
            for i, agent in enumerate(agents, 1):
                print(f"{i}. Name: {agent.get('name', 'NO_NAME')}")
                print(f"   ID: {agent.get('id', 'NO_ID')}")
                print(f"   Archetype: {agent.get('archetype', 'NO_ARCHETYPE')}")
                print(f"   User ID: {agent.get('user_id', 'NO_USER_ID')}")
                print(f"   Created: {agent.get('created_at', 'NO_DATE')}")
                print()
            
            return agents
        else:
            print(f"❌ Failed to retrieve agents: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error retrieving agents: {e}")
        return []

def setup_simulation(token):
    """Set up simulation state for testing"""
    print("\n" + "="*80)
    print("SETTING UP SIMULATION")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Set scenario
    scenario_data = {
        "scenario": "Agent Selection Debug Test",
        "scenario_name": "Debug Test Scenario"
    }
    
    try:
        response = requests.post(f"{API_URL}/simulation/set-scenario", 
                               json=scenario_data, headers=headers)
        print(f"Set Scenario Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Scenario set successfully")
        else:
            print(f"❌ Failed to set scenario: {response.text}")
            return False
        
        # Start simulation
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        print(f"Start Simulation Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Simulation started successfully")
            return True
        else:
            print(f"❌ Failed to start simulation: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up simulation: {e}")
        return False

def test_add_message_multiple_times(token, num_tests=10):
    """Test the add-message endpoint multiple times to analyze agent selection"""
    print("\n" + "="*80)
    print(f"TESTING ADD-MESSAGE ENDPOINT {num_tests} TIMES")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    agent_selections = []
    response_times = []
    successful_calls = 0
    
    for i in range(num_tests):
        print(f"\n--- Test {i+1}/{num_tests} ---")
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/conversation/add-message", headers=headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.3f}s")
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                
                if messages:
                    # Get the last message (the newly added one)
                    last_message = messages[-1]
                    agent_name = last_message.get('agent_name', 'UNKNOWN')
                    message_text = last_message.get('message', '')
                    
                    print(f"✅ Selected Agent: {agent_name}")
                    print(f"Message: {message_text[:100]}...")
                    
                    agent_selections.append(agent_name)
                    successful_calls += 1
                else:
                    print("❌ No messages in response")
            else:
                print(f"❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in test {i+1}: {e}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    return agent_selections, response_times, successful_calls

def analyze_agent_selection(agent_selections, expected_agents):
    """Analyze the agent selection patterns"""
    print("\n" + "="*80)
    print("ANALYZING AGENT SELECTION PATTERNS")
    print("="*80)
    
    if not agent_selections:
        print("❌ No agent selections to analyze")
        return
    
    # Count selections
    selection_counts = Counter(agent_selections)
    total_selections = len(agent_selections)
    
    print(f"Total successful selections: {total_selections}")
    print(f"Expected agents: {expected_agents}")
    print()
    
    print("Selection Results:")
    for agent_name, count in selection_counts.most_common():
        percentage = (count / total_selections) * 100
        print(f"  {agent_name}: {count} times ({percentage:.1f}%)")
    
    print()
    
    # Check if all expected agents were selected
    selected_agents = set(agent_selections)
    expected_agents_set = set(expected_agents)
    
    missing_agents = expected_agents_set - selected_agents
    unexpected_agents = selected_agents - expected_agents_set
    
    if missing_agents:
        print(f"❌ Missing agents (never selected): {list(missing_agents)}")
    else:
        print("✅ All expected agents were selected at least once")
    
    if unexpected_agents:
        print(f"⚠️ Unexpected agents selected: {list(unexpected_agents)}")
    
    # Check for bias (should be roughly equal distribution)
    if len(expected_agents) > 1 and total_selections >= len(expected_agents):
        expected_per_agent = total_selections / len(expected_agents)
        print(f"\nExpected selections per agent (if random): ~{expected_per_agent:.1f}")
        
        # Calculate deviation from expected
        deviations = []
        for agent in expected_agents:
            actual_count = selection_counts.get(agent, 0)
            deviation = abs(actual_count - expected_per_agent)
            deviations.append(deviation)
            print(f"  {agent}: {actual_count} (deviation: {deviation:.1f})")
        
        avg_deviation = sum(deviations) / len(deviations)
        print(f"\nAverage deviation from expected: {avg_deviation:.1f}")
        
        # Determine if there's significant bias
        if avg_deviation > expected_per_agent * 0.3:  # 30% threshold
            print("⚠️ SIGNIFICANT BIAS DETECTED - Selection is not random")
        else:
            print("✅ Selection appears to be reasonably random")
    
    # Check for the specific reported issue
    bob_marley_count = selection_counts.get("Bob Marley", 0)
    if bob_marley_count == total_selections and total_selections > 1:
        print(f"\n🚨 CONFIRMED BUG: Only 'Bob Marley' was selected in all {total_selections} tests!")
        print("This confirms the user's reported issue.")
    elif bob_marley_count > total_selections * 0.8:  # More than 80%
        print(f"\n⚠️ POTENTIAL BUG: 'Bob Marley' was selected {bob_marley_count}/{total_selections} times ({(bob_marley_count/total_selections)*100:.1f}%)")
        print("This suggests a bias towards Bob Marley.")
    else:
        print(f"\n✅ No obvious bias towards 'Bob Marley' detected")

def check_agent_filtering(agents, user_id):
    """Check if there are any agent filtering issues"""
    print("\n" + "="*80)
    print("CHECKING AGENT FILTERING ISSUES")
    print("="*80)
    
    print(f"User ID from authentication: {user_id}")
    print(f"Total agents retrieved: {len(agents)}")
    
    # Check user_id association
    correct_user_agents = []
    incorrect_user_agents = []
    
    for agent in agents:
        agent_user_id = agent.get('user_id')
        if agent_user_id == user_id:
            correct_user_agents.append(agent)
        else:
            incorrect_user_agents.append(agent)
    
    print(f"Agents with correct user_id: {len(correct_user_agents)}")
    print(f"Agents with incorrect user_id: {len(incorrect_user_agents)}")
    
    if incorrect_user_agents:
        print("\n❌ FILTERING ISSUE DETECTED:")
        print("The following agents have incorrect user_id associations:")
        for agent in incorrect_user_agents:
            print(f"  - {agent.get('name', 'NO_NAME')} (user_id: {agent.get('user_id', 'NO_USER_ID')})")
        return False
    else:
        print("\n✅ All agents have correct user_id associations")
        return True

def main():
    """Main test function"""
    print("🔍 AGENT SELECTION DEBUG TEST")
    print("="*80)
    print("Testing POST /api/conversation/add-message endpoint")
    print("Investigating why only 'Bob Marley' generates messages")
    print("="*80)
    
    # Step 1: Authenticate
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Get all agents
    agents = get_all_agents(token)
    if not agents:
        print("❌ No agents found. Cannot proceed with tests.")
        return
    
    # Step 3: Check for expected agents
    agent_names = [agent.get('name', 'NO_NAME') for agent in agents]
    expected_agents = ["Darth Vader", "Nikola Tesla", "Bob Marley"]
    
    print(f"\nExpected agents: {expected_agents}")
    print(f"Found agents: {agent_names}")
    
    # Check if expected agents exist
    missing_expected = [name for name in expected_agents if name not in agent_names]
    if missing_expected:
        print(f"⚠️ Missing expected agents: {missing_expected}")
        print("Using actual agent names for testing...")
        expected_agents = agent_names
    else:
        print("✅ All expected agents found")
    
    # Step 4: Check agent filtering
    filtering_ok = check_agent_filtering(agents, user_id)
    
    # Step 5: Setup simulation
    if not setup_simulation(token):
        print("❌ Failed to setup simulation. Cannot proceed with add-message tests.")
        return
    
    # Step 6: Test add-message endpoint multiple times
    print(f"\nTesting with agents: {expected_agents}")
    agent_selections, response_times, successful_calls = test_add_message_multiple_times(token, 10)
    
    # Step 7: Analyze results
    if successful_calls > 0:
        analyze_agent_selection(agent_selections, expected_agents)
        
        # Performance analysis
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            print(f"\nPerformance Analysis:")
            print(f"  Average response time: {avg_time:.3f}s")
            print(f"  Min response time: {min_time:.3f}s")
            print(f"  Max response time: {max_time:.3f}s")
    else:
        print("❌ No successful calls to analyze")
    
    # Step 8: Summary and recommendations
    print("\n" + "="*80)
    print("SUMMARY AND RECOMMENDATIONS")
    print("="*80)
    
    if successful_calls == 0:
        print("❌ CRITICAL ISSUE: No successful calls to add-message endpoint")
        print("Recommendations:")
        print("  1. Check endpoint implementation")
        print("  2. Verify authentication is working")
        print("  3. Check simulation state setup")
    elif not filtering_ok:
        print("❌ AGENT FILTERING ISSUE: Agents have incorrect user_id associations")
        print("Recommendations:")
        print("  1. Fix agent user_id associations in database")
        print("  2. Ensure agent creation properly sets user_id")
    elif len(set(agent_selections)) == 1 and len(agent_selections) > 1:
        only_agent = list(set(agent_selections))[0]
        print(f"🚨 CONFIRMED BUG: Only '{only_agent}' is being selected")
        print("Recommendations:")
        print("  1. Check random.choice() implementation in add-message endpoint")
        print("  2. Verify all agents are being included in the selection pool")
        print("  3. Check if there's any filtering happening before random selection")
    elif len(expected_agents) > 1 and len(set(agent_selections)) < len(expected_agents):
        print("⚠️ PARTIAL SELECTION ISSUE: Not all agents are being selected")
        print("Recommendations:")
        print("  1. Increase test iterations to confirm pattern")
        print("  2. Check if some agents are being filtered out")
    else:
        print("✅ Agent selection appears to be working correctly")
        print("The random selection is distributing across multiple agents")
    
    print(f"\nTest completed: {successful_calls}/{10} successful calls")

if __name__ == "__main__":
    main()