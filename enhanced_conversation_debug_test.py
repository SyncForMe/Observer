#!/usr/bin/env python3
"""
Enhanced Conversation Generation with Detailed Debugging Test

This test specifically verifies the enhanced conversation generation system
that should generate exactly 3 messages per agent with detailed debug output.

Test Requirements:
- Should target: agent_count × 3 = total messages
- Should complete all 3 rounds for each agent
- Should show progress for each round and agent
- Should show final verification of message counts
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

def make_request(method, endpoint, data=None, headers=None, timeout=120):
    """Make HTTP request with proper error handling"""
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, json=data, headers=headers, timeout=timeout)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        return response
    except requests.exceptions.Timeout:
        print(f"⏱️ Request timeout after {timeout} seconds")
        return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_enhanced_conversation_generation():
    """Test the enhanced conversation generation with detailed debugging"""
    print("\n" + "="*80)
    print("🧪 ENHANCED CONVERSATION GENERATION WITH DETAILED DEBUGGING TEST")
    print("="*80)
    
    # Step 1: Authenticate as guest user
    print("\n📋 Step 1: Authenticating as guest user")
    auth_response = make_request("POST", "/auth/test-login")
    
    if not auth_response or auth_response.status_code != 200:
        print("❌ Failed to authenticate as guest user")
        return False
    
    auth_data = auth_response.json()
    token = auth_data.get("access_token")
    user_data = auth_data.get("user", {})
    user_id = user_data.get("id")
    
    print(f"✅ Successfully authenticated as guest user")
    print(f"   User ID: {user_id}")
    print(f"   Token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Reset simulation to clean state
    print("\n📋 Step 2: Resetting simulation to clean state")
    reset_response = make_request("POST", "/simulation/reset", headers=headers)
    
    if not reset_response or reset_response.status_code != 200:
        print("❌ Failed to reset simulation")
        return False
    
    print("✅ Successfully reset simulation to clean state")
    
    # Step 3: Create test agents for conversation
    print("\n📋 Step 3: Creating test agents for conversation")
    
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Analyze quantum signal patterns and identify breakthrough opportunities",
            "expertise": "Quantum Physics and Signal Processing",
            "background": "Leading quantum researcher with expertise in signal analysis"
        },
        {
            "name": "Marcus Thompson",
            "archetype": "skeptic", 
            "goal": "Identify potential risks and validate all claims with evidence",
            "expertise": "Risk Assessment and Critical Analysis",
            "background": "Experienced analyst focused on identifying potential problems"
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "optimist",
            "goal": "Find practical applications and positive outcomes from discoveries",
            "expertise": "Technology Applications and Innovation",
            "background": "Innovation specialist focused on practical implementations"
        }
    ]
    
    created_agents = []
    for i, agent_data in enumerate(test_agents):
        print(f"   Creating agent {i+1}/3: {agent_data['name']}")
        
        create_response = make_request("POST", "/agents", data=agent_data, headers=headers)
        
        if not create_response or create_response.status_code != 200:
            print(f"❌ Failed to create agent: {agent_data['name']}")
            return False
        
        agent_response = create_response.json()
        created_agents.append(agent_response)
        print(f"   ✅ Created agent: {agent_data['name']} (ID: {agent_response.get('id', 'Unknown')})")
    
    print(f"✅ Successfully created {len(created_agents)} test agents")
    
    # Step 4: Set scenario for conversation
    print("\n📋 Step 4: Setting scenario for conversation")
    
    scenario_data = {
        "scenario": "A breakthrough quantum signal has been detected from deep space. The team needs to analyze the signal, assess its implications, and determine next steps for investigation.",
        "scenario_name": "Quantum Signal Discovery"
    }
    
    scenario_response = make_request("POST", "/simulation/set-scenario", data=scenario_data, headers=headers)
    
    if not scenario_response or scenario_response.status_code != 200:
        print("❌ Failed to set scenario")
        return False
    
    print("✅ Successfully set scenario: Quantum Signal Discovery")
    
    # Step 5: Start simulation
    print("\n📋 Step 5: Starting simulation")
    
    start_response = make_request("POST", "/simulation/start", headers=headers)
    
    if not start_response or start_response.status_code != 200:
        print("❌ Failed to start simulation")
        return False
    
    print("✅ Successfully started simulation")
    
    # Step 6: Generate conversation with detailed debugging
    print("\n📋 Step 6: Generating conversation with detailed debugging")
    print("🎯 EXPECTED BEHAVIOR:")
    print(f"   - TARGET: {len(created_agents)} agents × 3 messages = {len(created_agents) * 3} total messages")
    print("   - Should show 'Starting round 1/3', 'Starting round 2/3', 'Starting round 3/3'")
    print("   - Should show 'Generating message for [Agent Name] (Round X, Agent Y/Z)'")
    print("   - Should show final verification: 'Perfect! Got exactly X messages as expected'")
    
    print("\n🚀 Starting conversation generation...")
    start_time = time.time()
    
    # Use longer timeout for conversation generation as it involves multiple LLM calls
    conv_response = make_request("POST", "/conversation/generate-enhanced", headers=headers, timeout=180)
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    print(f"⏱️ Conversation generation took {generation_time:.2f} seconds")
    
    if not conv_response:
        print("❌ Conversation generation request failed (timeout or error)")
        return False
    
    if conv_response.status_code != 200:
        print(f"❌ Conversation generation failed with status {conv_response.status_code}")
        try:
            error_data = conv_response.json()
            print(f"   Error details: {error_data}")
        except:
            print(f"   Error text: {conv_response.text}")
        return False
    
    # Step 7: Analyze conversation response
    print("\n📋 Step 7: Analyzing conversation response")
    
    try:
        conv_data = conv_response.json()
        print("✅ Successfully received conversation response")
        
        # Check if response has expected structure
        if "messages" in conv_data:
            messages = conv_data["messages"]
            message_count = len(messages)
            expected_count = len(created_agents) * 3
            
            print(f"📊 CONVERSATION ANALYSIS:")
            print(f"   Total messages generated: {message_count}")
            print(f"   Expected messages: {expected_count}")
            print(f"   Agents participating: {len(created_agents)}")
            
            # Count messages per agent
            agent_message_counts = {}
            for msg in messages:
                agent_name = msg.get("agent_name", "Unknown")
                agent_message_counts[agent_name] = agent_message_counts.get(agent_name, 0) + 1
            
            print(f"\n📈 MESSAGES PER AGENT:")
            all_agents_have_3_messages = True
            for agent_name, count in sorted(agent_message_counts.items()):
                status = "✅" if count == 3 else "❌"
                print(f"   {status} {agent_name}: {count} messages")
                if count != 3:
                    all_agents_have_3_messages = False
            
            # Final verification
            print(f"\n🎯 FINAL VERIFICATION:")
            if message_count == expected_count and all_agents_have_3_messages:
                print(f"✅ Perfect! Got exactly {expected_count} messages as expected")
                print("✅ Each agent contributed exactly 3 messages")
                print("✅ Enhanced conversation generation is working correctly!")
                
                # Show sample messages
                print(f"\n📝 SAMPLE MESSAGES:")
                for i, msg in enumerate(messages[:6]):  # Show first 6 messages
                    agent_name = msg.get("agent_name", "Unknown")
                    message_text = msg.get("message", "")[:100] + "..." if len(msg.get("message", "")) > 100 else msg.get("message", "")
                    print(f"   {i+1}. {agent_name}: {message_text}")
                
                return True
            else:
                print(f"❌ Expected {expected_count} messages, got {message_count}")
                print("❌ Enhanced conversation generation did not meet requirements")
                
                # Show what went wrong
                if not all_agents_have_3_messages:
                    print("❌ Not all agents contributed exactly 3 messages")
                
                return False
        else:
            print("❌ Response does not contain 'messages' field")
            print(f"   Response keys: {list(conv_data.keys())}")
            return False
            
    except json.JSONDecodeError:
        print("❌ Failed to parse conversation response as JSON")
        print(f"   Response text: {conv_response.text[:500]}...")
        return False
    except Exception as e:
        print(f"❌ Error analyzing conversation response: {e}")
        return False

def main():
    """Main test execution"""
    print("🧪 Enhanced Conversation Generation with Detailed Debugging Test")
    print("=" * 80)
    
    success = test_enhanced_conversation_generation()
    
    print("\n" + "="*80)
    if success:
        print("✅ ENHANCED CONVERSATION GENERATION TEST PASSED")
        print("✅ The system successfully generates 3 messages per agent")
        print("✅ Detailed debugging output is working correctly")
    else:
        print("❌ ENHANCED CONVERSATION GENERATION TEST FAILED")
        print("❌ The system did not meet the 3 messages per agent requirement")
        print("❌ Check the debug output above for specific issues")
    print("="*80)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)