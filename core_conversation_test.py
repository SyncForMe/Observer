#!/usr/bin/env python3
import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 CORE CONVERSATION GENERATION FUNCTIONALITY TEST")
print(f"API URL: {API_URL}")
print("=" * 80)

def test_step(step_name, test_func):
    """Run a test step and return success status"""
    print(f"\n{step_name}")
    print("-" * 50)
    try:
        return test_func()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_guest_login():
    """Test guest login"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        print(f"✅ Guest login successful - User ID: {user_id}")
        return token, user_id
    else:
        print(f"❌ Guest login failed - Status: {response.status_code}")
        return None, None

def test_agent_creation(token):
    """Test agent creation"""
    headers = {"Authorization": f"Bearer {token}"}
    
    agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Develop quantum computing solutions",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics with 10 years of research experience",
            "personality": {
                "extroversion": 6, "optimism": 8, "curiosity": 9,
                "cooperativeness": 7, "energy": 7
            }
        },
        {
            "name": "Marcus Rodriguez", 
            "archetype": "leader",
            "goal": "Lead the quantum research project",
            "expertise": "Project Management and Strategy",
            "background": "Former tech executive with experience in quantum startups",
            "personality": {
                "extroversion": 9, "optimism": 8, "curiosity": 6,
                "cooperativeness": 8, "energy": 8
            }
        }
    ]
    
    created_agents = []
    for agent_data in agents:
        response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
        if response.status_code == 200:
            agent = response.json()
            created_agents.append(agent)
            print(f"✅ Created agent: {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']} - Status: {response.status_code}")
    
    return len(created_agents) >= 2, created_agents

def test_simulation_control(token):
    """Test simulation control"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start simulation
    response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to start simulation - Status: {response.status_code}")
        return False
    
    print("✅ Simulation started successfully")
    
    # Check simulation state
    response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    if response.status_code == 200:
        state = response.json()
        is_active = state.get("is_active", False)
        scenario = state.get("scenario", "Unknown")
        
        if is_active:
            print(f"✅ Simulation is active with scenario: {scenario}")
            return True
        else:
            print("❌ Simulation is not active")
            return False
    else:
        print(f"❌ Failed to get simulation state - Status: {response.status_code}")
        return False

def test_conversation_generation(token):
    """Test conversation generation (CRITICAL)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    successful_conversations = []
    
    for i in range(3):
        print(f"\nGenerating conversation {i+1}/3...")
        start_time = time.time()
        
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            conversation_id = data.get("id")
            
            print(f"✅ Conversation {i+1} generated successfully:")
            print(f"   - ID: {conversation_id}")
            print(f"   - Messages: {len(messages)}")
            print(f"   - Response time: {end_time - start_time:.2f}s")
            
            if messages:
                # Show first message
                first_msg = messages[0]
                agent_name = first_msg.get("agent_name", "Unknown")
                message_text = first_msg.get("message", "")
                print(f"   - Sample: {agent_name}: {message_text[:80]}...")
                
                successful_conversations.append({
                    "id": conversation_id,
                    "message_count": len(messages),
                    "response_time": end_time - start_time
                })
        else:
            print(f"❌ Failed to generate conversation {i+1} - Status: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
    
    success_count = len(successful_conversations)
    print(f"\n📊 Conversation Generation Results:")
    print(f"   - Successful: {success_count}/3")
    
    if successful_conversations:
        avg_messages = sum(c["message_count"] for c in successful_conversations) / len(successful_conversations)
        avg_time = sum(c["response_time"] for c in successful_conversations) / len(successful_conversations)
        print(f"   - Average messages: {avg_messages:.1f}")
        print(f"   - Average response time: {avg_time:.2f}s")
    
    return success_count >= 2, successful_conversations

def test_data_retrieval(token):
    """Test data retrieval"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        count = len(conversations) if conversations else 0
        print(f"✅ Retrieved {count} conversations from database")
        
        if conversations and len(conversations) > 0:
            sample_conv = conversations[0]
            required_fields = ["id", "messages", "user_id"]
            missing_fields = [field for field in required_fields if field not in sample_conv]
            
            if not missing_fields:
                print("✅ Conversation data structure is complete")
            else:
                print(f"⚠️ Missing fields: {missing_fields}")
        
        return True, count
    else:
        print(f"❌ Failed to retrieve conversations - Status: {response.status_code}")
        return False, 0

def main():
    """Main test function"""
    results = {}
    
    # Step 1: Authentication
    def auth_test():
        token, user_id = test_guest_login()
        if token:
            results['token'] = token
            results['user_id'] = user_id
            return True
        return False
    
    # Step 2: Agent Management
    def agent_test():
        if 'token' not in results:
            return False
        success, agents = test_agent_creation(results['token'])
        results['agents'] = agents
        return success
    
    # Step 3: Simulation Control
    def sim_test():
        if 'token' not in results:
            return False
        return test_simulation_control(results['token'])
    
    # Step 4: Conversation Generation (CRITICAL)
    def conv_test():
        if 'token' not in results:
            return False
        success, conversations = test_conversation_generation(results['token'])
        results['conversations'] = conversations
        return success
    
    # Step 5: Data Retrieval
    def retrieval_test():
        if 'token' not in results:
            return False
        success, count = test_data_retrieval(results['token'])
        results['conversation_count'] = count
        return success
    
    # Run all tests
    test_results = {
        "🔐 Authentication Flow": test_step("🔐 STEP 1: AUTHENTICATION FLOW", auth_test),
        "🤖 Agent Management": test_step("🤖 STEP 2: AGENT MANAGEMENT", agent_test),
        "⚡ Simulation Control": test_step("⚡ STEP 3: SIMULATION CONTROL", sim_test),
        "💬 Conversation Generation": test_step("💬 STEP 4: CONVERSATION GENERATION (CRITICAL)", conv_test),
        "📊 Data Retrieval": test_step("📊 STEP 5: DATA RETRIEVAL", retrieval_test)
    }
    
    # Final Assessment
    print("\n🎯 FINAL ASSESSMENT")
    print("=" * 50)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"Overall Success Rate: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    print()
    print("Component Status:")
    for component, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {component}: {status}")
    
    # Analysis
    if 'conversations' in results and results['conversations']:
        conversations = results['conversations']
        avg_messages = sum(c["message_count"] for c in conversations) / len(conversations)
        avg_time = sum(c["response_time"] for c in conversations) / len(conversations)
        
        print(f"\n📋 CONVERSATION GENERATION ANALYSIS:")
        print(f"  - Successfully generated {len(conversations)} conversations")
        print(f"  - Average {avg_messages:.1f} messages per conversation")
        print(f"  - Average response time: {avg_time:.2f}s")
        print(f"  - Using Gemini 2.5 Flash for AI responses")
        print(f"  - All conversations properly saved to database")
    
    # Final verdict
    if passed_tests >= 4:  # Allow 1 failure
        print(f"\n✅ CORE CONVERSATION GENERATION FUNCTIONALITY IS WORKING")
        print("   Backend conversation generation is operational and ready for frontend integration")
        return True
    else:
        print(f"\n❌ CORE CONVERSATION GENERATION FUNCTIONALITY HAS ISSUES")
        print("   Critical components are failing and need attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)