#!/usr/bin/env python3
"""
Extended Agent Selection Test - 50 iterations to get better statistical data
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from collections import Counter
import statistics

# Load environment variables
load_dotenv('/app/frontend/.env')
API_URL = f"{os.environ.get('REACT_APP_BACKEND_URL')}/api"

def authenticate():
    """Authenticate and get JWT token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user", {}).get("id")
    return None, None

def setup_simulation(token):
    """Set up simulation state for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Set scenario
    scenario_data = {
        "scenario": "Extended Agent Selection Test",
        "scenario_name": "Extended Debug Test"
    }
    
    response = requests.post(f"{API_URL}/simulation/set-scenario", 
                           json=scenario_data, headers=headers)
    if response.status_code != 200:
        return False
    
    # Start simulation
    response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    return response.status_code == 200

def test_add_message_extended(token, num_tests=50):
    """Test the add-message endpoint multiple times"""
    print(f"\n🔍 EXTENDED AGENT SELECTION TEST - {num_tests} ITERATIONS")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    agent_selections = []
    successful_calls = 0
    
    for i in range(num_tests):
        if i % 10 == 0:
            print(f"Progress: {i}/{num_tests} tests completed...")
        
        try:
            response = requests.post(f"{API_URL}/conversation/add-message", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                
                if messages:
                    # Get the last message (the newly added one)
                    last_message = messages[-1]
                    agent_name = last_message.get('agent_name', 'UNKNOWN')
                    agent_selections.append(agent_name)
                    successful_calls += 1
                    
        except Exception as e:
            print(f"Error in test {i+1}: {e}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    print(f"Completed: {successful_calls}/{num_tests} successful tests")
    return agent_selections, successful_calls

def analyze_extended_results(agent_selections):
    """Analyze the extended test results"""
    print("\n📊 EXTENDED ANALYSIS RESULTS")
    print("="*80)
    
    if not agent_selections:
        print("❌ No agent selections to analyze")
        return
    
    # Count selections
    selection_counts = Counter(agent_selections)
    total_selections = len(agent_selections)
    
    print(f"Total successful selections: {total_selections}")
    print()
    
    print("Detailed Selection Results:")
    for agent_name, count in selection_counts.most_common():
        percentage = (count / total_selections) * 100
        print(f"  {agent_name}: {count} times ({percentage:.1f}%)")
    
    # Statistical analysis
    expected_per_agent = total_selections / 3  # 3 agents
    print(f"\nExpected selections per agent (if truly random): {expected_per_agent:.1f}")
    
    # Calculate chi-square test for randomness
    chi_square = 0
    for agent in ["Darth Vader", "Nikola Tesla", "Bob Marley"]:
        observed = selection_counts.get(agent, 0)
        expected = expected_per_agent
        chi_square += ((observed - expected) ** 2) / expected
        print(f"  {agent}: {observed} observed vs {expected:.1f} expected (diff: {observed - expected:.1f})")
    
    print(f"\nChi-square statistic: {chi_square:.2f}")
    
    # Critical value for 2 degrees of freedom at 95% confidence is 5.991
    if chi_square > 5.991:
        print("🚨 STATISTICALLY SIGNIFICANT BIAS DETECTED!")
        print("The selection is NOT random (p < 0.05)")
    else:
        print("✅ Selection appears to be random (p >= 0.05)")
    
    # Check for the specific reported issue
    bob_marley_count = selection_counts.get("Bob Marley", 0)
    bob_marley_percentage = (bob_marley_count / total_selections) * 100
    
    nikola_tesla_count = selection_counts.get("Nikola Tesla", 0)
    nikola_tesla_percentage = (nikola_tesla_count / total_selections) * 100
    
    darth_vader_count = selection_counts.get("Darth Vader", 0)
    darth_vader_percentage = (darth_vader_count / total_selections) * 100
    
    print(f"\n🎯 SPECIFIC ISSUE ANALYSIS:")
    print(f"Bob Marley: {bob_marley_count}/{total_selections} ({bob_marley_percentage:.1f}%)")
    print(f"Nikola Tesla: {nikola_tesla_count}/{total_selections} ({nikola_tesla_percentage:.1f}%)")
    print(f"Darth Vader: {darth_vader_count}/{total_selections} ({darth_vader_percentage:.1f}%)")
    
    if bob_marley_count == total_selections:
        print("🚨 CONFIRMED: Only Bob Marley is being selected!")
    elif bob_marley_percentage > 80:
        print("⚠️ STRONG BIAS: Bob Marley is heavily favored")
    elif nikola_tesla_percentage > 80:
        print("⚠️ STRONG BIAS: Nikola Tesla is heavily favored")
    elif darth_vader_percentage > 80:
        print("⚠️ STRONG BIAS: Darth Vader is heavily favored")
    elif max(bob_marley_percentage, nikola_tesla_percentage, darth_vader_percentage) > 50:
        most_selected = max(
            ("Bob Marley", bob_marley_percentage),
            ("Nikola Tesla", nikola_tesla_percentage),
            ("Darth Vader", darth_vader_percentage),
            key=lambda x: x[1]
        )
        print(f"⚠️ MODERATE BIAS: {most_selected[0]} is favored ({most_selected[1]:.1f}%)")
    else:
        print("✅ No significant bias detected")

def main():
    print("🔬 EXTENDED AGENT SELECTION DEBUG TEST")
    print("="*80)
    
    # Authenticate
    token, user_id = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Setup simulation
    if not setup_simulation(token):
        print("❌ Failed to setup simulation")
        return
    
    print("✅ Simulation setup complete")
    
    # Run extended test
    agent_selections, successful_calls = test_add_message_extended(token, 50)
    
    if successful_calls > 0:
        analyze_extended_results(agent_selections)
    else:
        print("❌ No successful calls to analyze")

if __name__ == "__main__":
    main()