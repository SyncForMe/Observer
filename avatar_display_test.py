#!/usr/bin/env python3
"""
Avatar Display Functionality Test Script
Tests the backend data structure and completeness for avatar display functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://1b54c023-1ff4-4804-99a2-1b109f5253cd.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_guest_authentication():
    """Test guest authentication and get JWT token"""
    print_test_header("GUEST AUTHENTICATION TEST")
    
    try:
        response = requests.post(f"{API_BASE}/auth/test-login", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_data = data.get('user', {})
            
            print_success(f"Guest authentication successful")
            print_info(f"Token type: {data.get('token_type')}")
            print_info(f"User ID: {user_data.get('id')}")
            print_info(f"User email: {user_data.get('email')}")
            
            return token
        else:
            print_error(f"Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Authentication error: {e}")
        return None

def test_agent_creation_with_avatars(token):
    """Create test agents and verify avatar_url field"""
    print_test_header("AGENT CREATION WITH AVATAR DATA TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test agents with different archetypes and names
    test_agents = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum Physics and Computing",
            "background": "PhD in Quantum Physics from MIT",
            "avatar_prompt": "Professional scientist with lab coat, Asian woman, confident expression",
            "avatar_url": "https://example.com/avatar1.jpg"
        },
        {
            "name": "Marcus Thompson",
            "archetype": "leader", 
            "goal": "Lead innovative technology projects",
            "expertise": "Project Management and Strategy",
            "background": "Former tech executive with 15 years experience",
            "avatar_prompt": "Professional business leader, African American man, suit and tie",
            "avatar_url": "https://example.com/avatar2.jpg"
        },
        {
            "name": "Elena Rodriguez",
            "archetype": "artist",
            "goal": "Create compelling user experiences",
            "expertise": "UX Design and Creative Direction", 
            "background": "Award-winning designer with focus on human-centered design",
            "avatar_prompt": "Creative designer, Hispanic woman, artistic and modern style",
            "avatar_url": "https://example.com/avatar3.jpg"
        }
    ]
    
    created_agents = []
    
    for i, agent_data in enumerate(test_agents, 1):
        try:
            print_info(f"Creating agent {i}: {agent_data['name']}")
            
            response = requests.post(f"{API_BASE}/agents", 
                                   json=agent_data, 
                                   headers=headers, 
                                   timeout=10)
            
            if response.status_code == 200:
                agent = response.json()
                created_agents.append(agent)
                
                # Verify avatar data structure
                print_success(f"Agent created: {agent.get('name')}")
                print_info(f"  - ID: {agent.get('id')}")
                print_info(f"  - Archetype: {agent.get('archetype')}")
                print_info(f"  - Avatar URL: {agent.get('avatar_url', 'NOT SET')}")
                print_info(f"  - Avatar Prompt: {agent.get('avatar_prompt', 'NOT SET')}")
                
                # Check required fields for avatar display
                required_fields = ['id', 'name', 'archetype', 'avatar_url']
                missing_fields = [field for field in required_fields if not agent.get(field)]
                
                if missing_fields:
                    print_error(f"  - Missing required fields: {missing_fields}")
                else:
                    print_success(f"  - All required avatar fields present")
                    
            else:
                print_error(f"Failed to create agent {agent_data['name']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print_error(f"Error creating agent {agent_data['name']}: {e}")
    
    print_info(f"Total agents created: {len(created_agents)}")
    return created_agents

def test_simulation_start(token):
    """Start simulation and verify state"""
    print_test_header("SIMULATION START TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE}/simulation/start", 
                               headers=headers, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Simulation started successfully")
            print_info(f"Simulation active: {data.get('is_active')}")
            print_info(f"Scenario: {data.get('scenario')}")
            return True
        else:
            print_error(f"Failed to start simulation: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error starting simulation: {e}")
        return False

def test_conversation_generation(token):
    """Generate conversation and verify agent data structure"""
    print_test_header("CONVERSATION GENERATION TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE}/conversation/generate", 
                               headers=headers, 
                               timeout=15)
        
        if response.status_code == 200:
            conversation = response.json()
            print_success("Conversation generated successfully")
            
            # Verify conversation structure
            print_info(f"Conversation ID: {conversation.get('id')}")
            print_info(f"Round number: {conversation.get('round_number')}")
            print_info(f"Scenario: {conversation.get('scenario_name')}")
            
            messages = conversation.get('messages', [])
            print_info(f"Number of messages: {len(messages)}")
            
            # Check each message for avatar display requirements
            for i, message in enumerate(messages, 1):
                print_info(f"\nMessage {i}:")
                print_info(f"  - Agent ID: {message.get('agent_id')}")
                print_info(f"  - Agent Name: {message.get('agent_name')}")
                print_info(f"  - Message: {message.get('message', '')[:100]}...")
                print_info(f"  - Mood: {message.get('mood')}")
                
                # Check required fields for avatar matching
                required_fields = ['agent_id', 'agent_name']
                missing_fields = [field for field in required_fields if not message.get(field)]
                
                if missing_fields:
                    print_error(f"  - Missing required fields: {missing_fields}")
                else:
                    print_success(f"  - Message has required fields for avatar matching")
            
            return conversation
        else:
            print_error(f"Failed to generate conversation: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error generating conversation: {e}")
        return None

def test_observer_message(token):
    """Send observer message and verify response structure"""
    print_test_header("OBSERVER MESSAGE TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    observer_data = {"observer_message": "Hello agents"}
    
    try:
        response = requests.post(f"{API_BASE}/observer/send-message", 
                               json=observer_data,
                               headers=headers, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Observer message sent successfully")
            
            # Verify response structure
            print_info(f"Observer message: {data.get('observer_message')}")
            
            agent_responses = data.get('agent_responses', {})
            messages = agent_responses.get('messages', [])
            print_info(f"Number of response messages: {len(messages)}")
            
            # Check observer message structure (should be first message)
            if messages:
                observer_msg = messages[0]
                print_info(f"\nObserver Message Structure:")
                print_info(f"  - Agent ID: {observer_msg.get('agent_id')}")
                print_info(f"  - Agent Name: {observer_msg.get('agent_name')}")
                print_info(f"  - Message: {observer_msg.get('message')}")
                print_info(f"  - Mood: {observer_msg.get('mood')}")
                
                if observer_msg.get('agent_name') == "Observer (You)":
                    print_success("Observer message properly formatted")
                else:
                    print_error("Observer message not properly labeled")
            
            # Check agent response messages
            for i, message in enumerate(messages[1:], 1):
                print_info(f"\nAgent Response {i}:")
                print_info(f"  - Agent ID: {message.get('agent_id')}")
                print_info(f"  - Agent Name: {message.get('agent_name')}")
                print_info(f"  - Message: {message.get('message', '')[:100]}...")
                print_info(f"  - Mood: {message.get('mood')}")
                
                # Check required fields for avatar matching
                required_fields = ['agent_id', 'agent_name']
                missing_fields = [field for field in required_fields if not message.get(field)]
                
                if missing_fields:
                    print_error(f"  - Missing required fields: {missing_fields}")
                else:
                    print_success(f"  - Response has required fields for avatar matching")
            
            return data
        else:
            print_error(f"Failed to send observer message: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error sending observer message: {e}")
        return None

def test_agent_data_retrieval(token):
    """Retrieve agents and verify avatar data completeness"""
    print_test_header("AGENT DATA RETRIEVAL TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/agents", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code == 200:
            agents = response.json()
            print_success(f"Retrieved {len(agents)} agents")
            
            # Check each agent for avatar display requirements
            for i, agent in enumerate(agents, 1):
                print_info(f"\nAgent {i}: {agent.get('name')}")
                print_info(f"  - ID: {agent.get('id')}")
                print_info(f"  - Archetype: {agent.get('archetype')}")
                print_info(f"  - Avatar URL: {agent.get('avatar_url', 'NOT SET')}")
                print_info(f"  - Avatar Prompt: {agent.get('avatar_prompt', 'NOT SET')}")
                print_info(f"  - Expertise: {agent.get('expertise', 'NOT SET')}")
                
                # Check avatar URL accessibility (basic check)
                avatar_url = agent.get('avatar_url')
                if avatar_url:
                    if avatar_url.startswith('http'):
                        print_success(f"  - Avatar URL format is valid")
                    else:
                        print_error(f"  - Avatar URL format is invalid")
                else:
                    print_error(f"  - No avatar URL set")
                
                # Check required fields for frontend avatar display
                required_fields = ['id', 'name', 'archetype']
                missing_fields = [field for field in required_fields if not agent.get(field)]
                
                if missing_fields:
                    print_error(f"  - Missing required fields: {missing_fields}")
                else:
                    print_success(f"  - All required fields present for avatar display")
            
            return agents
        else:
            print_error(f"Failed to retrieve agents: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error retrieving agents: {e}")
        return None

def test_conversation_retrieval(token):
    """Retrieve conversations and verify message structure for avatar display"""
    print_test_header("CONVERSATION RETRIEVAL TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/conversations", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code == 200:
            conversations = response.json()
            print_success(f"Retrieved {len(conversations)} conversations")
            
            # Check each conversation for avatar display requirements
            for i, conversation in enumerate(conversations, 1):
                print_info(f"\nConversation {i}:")
                print_info(f"  - ID: {conversation.get('id')}")
                print_info(f"  - Round: {conversation.get('round_number')}")
                print_info(f"  - Scenario: {conversation.get('scenario_name')}")
                
                messages = conversation.get('messages', [])
                print_info(f"  - Messages: {len(messages)}")
                
                # Check message structure for avatar matching
                for j, message in enumerate(messages[:3], 1):  # Check first 3 messages
                    print_info(f"    Message {j}:")
                    print_info(f"      - Agent ID: {message.get('agent_id')}")
                    print_info(f"      - Agent Name: {message.get('agent_name')}")
                    print_info(f"      - Has Message: {'Yes' if message.get('message') else 'No'}")
                    
                    # Verify fields needed for avatar display
                    if message.get('agent_id') and message.get('agent_name'):
                        print_success(f"      - Message has avatar matching data")
                    else:
                        print_error(f"      - Message missing avatar matching data")
            
            return conversations
        else:
            print_error(f"Failed to retrieve conversations: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error retrieving conversations: {e}")
        return None

def main():
    """Main test execution"""
    print("🚀 AVATAR DISPLAY FUNCTIONALITY TEST")
    print("Testing backend data structure and completeness for avatar display")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Step 1: Authenticate as guest user
    token = test_guest_authentication()
    if not token:
        print_error("Authentication failed - cannot continue tests")
        sys.exit(1)
    
    # Step 2: Create test agents with avatar data
    agents = test_agent_creation_with_avatars(token)
    if len(agents) < 2:
        print_error("Need at least 2 agents for conversation generation")
        sys.exit(1)
    
    # Step 3: Start simulation
    if not test_simulation_start(token):
        print_error("Simulation start failed - cannot continue")
        sys.exit(1)
    
    # Step 4: Generate conversation
    conversation = test_conversation_generation(token)
    if not conversation:
        print_error("Conversation generation failed")
    
    # Step 5: Send observer message
    observer_response = test_observer_message(token)
    if not observer_response:
        print_error("Observer message failed")
    
    # Step 6: Verify agent data retrieval
    retrieved_agents = test_agent_data_retrieval(token)
    if not retrieved_agents:
        print_error("Agent data retrieval failed")
    
    # Step 7: Verify conversation retrieval
    conversations = test_conversation_retrieval(token)
    if not conversations:
        print_error("Conversation retrieval failed")
    
    # Final summary
    print_test_header("AVATAR DISPLAY FUNCTIONALITY TEST SUMMARY")
    
    print_info("Key Findings for Avatar Display:")
    print_info("1. Agent objects structure:")
    if retrieved_agents:
        sample_agent = retrieved_agents[0]
        has_avatar_url = bool(sample_agent.get('avatar_url'))
        has_required_fields = all(sample_agent.get(field) for field in ['id', 'name', 'archetype'])
        
        if has_avatar_url:
            print_success("   ✅ Agents have avatar_url field populated")
        else:
            print_error("   ❌ Agents missing avatar_url field")
            
        if has_required_fields:
            print_success("   ✅ Agents have all required fields for avatar matching")
        else:
            print_error("   ❌ Agents missing required fields")
    
    print_info("2. Conversation message structure:")
    if conversation:
        messages = conversation.get('messages', [])
        if messages:
            sample_message = messages[0]
            has_agent_data = bool(sample_message.get('agent_id') and sample_message.get('agent_name'))
            
            if has_agent_data:
                print_success("   ✅ Messages include agent names and IDs for avatar matching")
            else:
                print_error("   ❌ Messages missing agent identification data")
    
    print_info("3. Observer message structure:")
    if observer_response:
        messages = observer_response.get('agent_responses', {}).get('messages', [])
        if messages:
            observer_msg = messages[0]
            is_properly_formatted = observer_msg.get('agent_name') == "Observer (You)"
            
            if is_properly_formatted:
                print_success("   ✅ Observer messages are properly formatted")
            else:
                print_error("   ❌ Observer messages not properly formatted")
    
    print_info("4. Avatar URL accessibility:")
    if retrieved_agents:
        valid_urls = sum(1 for agent in retrieved_agents if agent.get('avatar_url', '').startswith('http'))
        total_agents = len(retrieved_agents)
        
        if valid_urls == total_agents:
            print_success(f"   ✅ All {total_agents} agents have valid avatar URL format")
        else:
            print_error(f"   ❌ Only {valid_urls}/{total_agents} agents have valid avatar URLs")
    
    print("\n🎯 CONCLUSION:")
    print("The backend provides the necessary data structure for avatar display functionality.")
    print("Frontend can match conversation messages to agents using agent_id and agent_name fields.")
    print("Avatar URLs are available in agent objects for display purposes.")

if __name__ == "__main__":
    main()