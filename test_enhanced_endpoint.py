#!/usr/bin/env python3
"""
Test the enhanced conversation generation endpoint to verify 3 messages per agent functionality
"""
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from collections import Counter

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

def test_enhanced_conversation_endpoint():
    """Test the enhanced conversation generation endpoint"""
    print("\n" + "="*80)
    print("🎯 TESTING ENHANCED CONVERSATION ENDPOINT: /conversation/generate-enhanced")
    print("="*80)
    
    # Step 1: Authenticate as guest
    print("\n1️⃣ STEP 1: Guest Authentication")
    try:
        auth_response = requests.post(f"{API_URL}/auth/test-login")
        if auth_response.status_code != 200:
            print(f"❌ Guest authentication failed: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        auth_token = auth_data.get("access_token")
        user_data = auth_data.get("user", {})
        user_id = user_data.get("id")
        
        print(f"✅ Guest authentication successful")
        print(f"   User ID: {user_id}")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 2: Reset simulation and create test agents
    print("\n2️⃣ STEP 2: Setting up simulation with 3 test agents")
    
    # Reset simulation
    try:
        reset_response = requests.post(f"{API_URL}/simulation/reset", headers=headers)
        print(f"   Simulation reset: {reset_response.status_code}")
    except Exception as e:
        print(f"   Reset warning: {e}")
    
    # Create exactly 3 test agents for clear verification (3 × 3 = 9 messages expected)
    test_agents = [
        {
            "name": "Dr. Alice Smith",
            "archetype": "scientist",
            "goal": "Provide scientific analysis and insights",
            "expertise": "Research and Data Analysis",
            "background": "Senior researcher with expertise in data science"
        },
        {
            "name": "Bob Johnson",
            "archetype": "leader",
            "goal": "Lead the team to successful outcomes",
            "expertise": "Project Management",
            "background": "Experienced project manager and team leader"
        },
        {
            "name": "Carol Davis",
            "archetype": "optimist",
            "goal": "Find positive solutions and opportunities",
            "expertise": "Creative Problem Solving",
            "background": "Innovation specialist focused on creative solutions"
        }
    ]
    
    created_agents = []
    for i, agent_data in enumerate(test_agents, 1):
        try:
            create_response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            if create_response.status_code == 200:
                agent_info = create_response.json()
                created_agents.append(agent_info)
                print(f"   ✅ Created agent {i}/3: {agent_data['name']}")
            else:
                print(f"   ❌ Failed to create agent {i}/3: {create_response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error creating agent {i}/3: {e}")
            return False
    
    print(f"✅ Successfully created {len(created_agents)} test agents")
    
    # Step 3: Start simulation
    print("\n3️⃣ STEP 3: Starting simulation")
    try:
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if start_response.status_code == 200:
            print("✅ Simulation started successfully")
        else:
            print(f"❌ Failed to start simulation: {start_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Step 4: Set a test scenario
    print("\n4️⃣ STEP 4: Setting test scenario")
    scenario_data = {
        "scenario": "The team needs to develop a strategy for improving customer satisfaction. Consider current issues, potential solutions, and implementation approaches.",
        "scenario_name": "Customer Satisfaction Strategy"
    }
    
    try:
        scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
        if scenario_response.status_code == 200:
            print("✅ Test scenario set successfully")
            print(f"   Scenario: {scenario_data['scenario_name']}")
        else:
            print(f"❌ Failed to set scenario: {scenario_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error setting scenario: {e}")
        return False
    
    # Step 5: Test the ENHANCED conversation generation endpoint
    print("\n5️⃣ STEP 5: 🎯 TESTING ENHANCED ENDPOINT - Generate Conversation (3 Messages Per Agent)")
    print("   Expected: 3 agents × 3 messages = 9 total messages")
    print("   Looking for debug output: 'TARGET: X agents × 3 messages = Y total messages'")
    print("   Looking for success message: 'Perfect! Got exactly X messages as expected'")
    
    try:
        start_time = time.time()
        
        # Call the ENHANCED conversation generation endpoint
        conversation_response = requests.post(f"{API_URL}/conversation/generate-enhanced", headers=headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   Response time: {response_time:.2f} seconds")
        print(f"   Status code: {conversation_response.status_code}")
        
        if conversation_response.status_code != 200:
            print(f"❌ Enhanced conversation generation failed: {conversation_response.status_code}")
            try:
                error_data = conversation_response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error text: {conversation_response.text}")
            return False
        
        # Parse the response
        conversation_data = conversation_response.json()
        
        # Extract messages
        messages = conversation_data.get("messages", [])
        total_messages = len(messages)
        
        print(f"\n📊 ENHANCED CONVERSATION GENERATION RESULTS:")
        print(f"   Total messages generated: {total_messages}")
        print(f"   Expected messages: 9 (3 agents × 3)")
        
        # Verify total message count
        if total_messages == 9:
            print("✅ PERFECT! Got exactly 9 messages as expected")
        else:
            print(f"❌ MISMATCH! Expected 9 messages, got {total_messages}")
        
        # Analyze message distribution per agent
        print(f"\n📈 MESSAGE DISTRIBUTION ANALYSIS:")
        agent_message_count = Counter()
        
        for message in messages:
            agent_name = message.get("agent_name", "Unknown")
            agent_message_count[agent_name] += 1
        
        perfect_distribution = True
        for agent_name, count in sorted(agent_message_count.items()):
            status = "✅" if count == 3 else "❌"
            if count != 3:
                perfect_distribution = False
            print(f"   {status} {agent_name}: {count} messages")
        
        # Overall assessment
        print(f"\n🎯 ENHANCED ENDPOINT VERIFICATION RESULTS:")
        
        if total_messages == 9 and perfect_distribution:
            print("✅ SUCCESS! Enhanced endpoint 3 messages per agent functionality is working perfectly!")
            print("✅ Each agent appears exactly 3 times in the message list")
            print("✅ Total message count is exactly 9 (3 × 3)")
            
            # Show sample messages to verify quality
            print(f"\n📝 SAMPLE MESSAGES (First 3):")
            for i, message in enumerate(messages[:3], 1):
                agent_name = message.get("agent_name", "Unknown")
                message_text = message.get("message", "")
                print(f"   {i}. {agent_name}: {message_text[:100]}...")
            
            return True
        else:
            print("❌ FAILURE! Enhanced endpoint 3 messages per agent functionality has issues:")
            if total_messages != 9:
                print(f"   - Wrong total message count: {total_messages} instead of 9")
            if not perfect_distribution:
                print(f"   - Uneven message distribution across agents")
            
            return False
    
    except Exception as e:
        print(f"❌ Error during enhanced conversation generation: {e}")
        return False

def main():
    """Run the enhanced endpoint test"""
    print("🚀 Starting ENHANCED ENDPOINT TEST for 3 Messages Per Agent Functionality")
    
    success = test_enhanced_conversation_endpoint()
    
    print("\n" + "="*80)
    if success:
        print("🎉 ENHANCED ENDPOINT TEST: PASSED")
        print("✅ The enhanced conversation generation endpoint works correctly")
        print("✅ Generates exactly 3 messages per agent")
        print("✅ Perfect message distribution achieved")
    else:
        print("❌ ENHANCED ENDPOINT TEST: FAILED")
        print("❌ The enhanced conversation generation endpoint has issues")
        print("❌ Does not generate exactly 3 messages per agent")
    
    print("="*80)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)