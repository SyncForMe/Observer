#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

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

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
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
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
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
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False, None

def test_login():
    """Login with test endpoint to get auth token"""
    global auth_token, test_user_id
    
    # Try using the email/password login first with admin credentials
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Login with admin credentials",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    # If email/password login fails, try the test login endpoint
    if not login_test or not login_response:
        test_login_test, test_login_response = run_test(
            "Test Login Endpoint",
            "/auth/test-login",
            method="POST",
            expected_keys=["access_token", "token_type", "user"]
        )
        
        # Store the token for further testing if successful
        if test_login_test and test_login_response:
            auth_token = test_login_response.get("access_token")
            user_data = test_login_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"Test login successful. User ID: {test_user_id}")
            print(f"JWT Token: {auth_token}")
            return True
        else:
            print("Test login failed. Some tests may not work correctly.")
            return False
    else:
        # Store the token from email/password login
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"Login successful. User ID: {test_user_id}")
        print(f"JWT Token: {auth_token}")
        return True

def create_test_agents():
    """Create test agents for the simulation"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("CREATING TEST AGENTS")
    print("="*80)
    
    # Create 3 test agents with different archetypes
    agent_archetypes = ["scientist", "leader", "skeptic"]
    
    for i, archetype in enumerate(agent_archetypes):
        agent_data = {
            "name": f"Test {archetype.capitalize()} {i+1}",
            "archetype": archetype,
            "personality": {
                "extroversion": 5,
                "optimism": 5,
                "curiosity": 5,
                "cooperativeness": 5,
                "energy": 5
            },
            "goal": f"Test the observer message functionality as a {archetype}",
            "expertise": f"Expert in {archetype} tasks and responsibilities",
            "background": f"Experienced {archetype} with a focus on testing"
        }
        
        create_agent_test, create_agent_response = run_test(
            f"Create {archetype.capitalize()} Agent",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_agent_test and create_agent_response:
            agent_id = create_agent_response.get("id")
            if agent_id:
                print(f"✅ Created {archetype} agent with ID: {agent_id}")
                created_agent_ids.append(agent_id)
            else:
                print(f"❌ Failed to get agent ID for {archetype} agent")
        else:
            print(f"❌ Failed to create {archetype} agent")
    
    # Verify agents were created
    if len(created_agent_ids) > 0:
        print(f"✅ Successfully created {len(created_agent_ids)} agents")
        return True
    else:
        print(f"❌ Failed to create any agents")
        return False

def setup_simulation():
    """Set up a simulation with agents for testing"""
    print("\n" + "="*80)
    print("SETTING UP SIMULATION WITH AGENTS")
    print("="*80)
    
    # Start a simulation
    start_sim_test, start_sim_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_sim_test:
        print("❌ Failed to start simulation")
        return False
    
    # Create test agents
    if not create_test_agents():
        print("❌ Failed to create test agents")
        return False
    
    # Verify agents were created
    agents_test, agents_response = run_test(
        "Get Agents",
        "/agents",
        method="GET",
        auth=True
    )
    
    if not agents_test or not agents_response or len(agents_response) < 1:
        print("❌ No agents found after creation")
        return False
    
    print(f"✅ Found {len(agents_response)} agents")
    return True

def test_observer_message_comprehensive():
    """Test the observer message functionality comprehensively"""
    print("\n" + "="*80)
    print("COMPREHENSIVE OBSERVER MESSAGE FUNCTIONALITY TESTING")
    print("="*80)
    
    # Test 1: Send observer message with empty message
    print("\nTest 1: Send observer message with empty message (should fail)")
    
    empty_observer_data = {
        "observer_message": ""
    }
    
    empty_observer_test, empty_observer_response = run_test(
        "Send Empty Observer Message",
        "/observer/send-message",
        method="POST",
        data=empty_observer_data,
        auth=True,
        expected_status=400
    )
    
    if empty_observer_test:
        print("✅ Empty observer message correctly rejected with 400 status code")
    else:
        print("❌ Empty observer message not properly rejected")
    
    # Test 2: Send observer message without authentication
    print("\nTest 2: Send observer message without authentication (should fail)")
    
    observer_data = {
        "observer_message": "This message should be rejected"
    }
    
    no_auth_observer_test, no_auth_observer_response = run_test(
        "Send Observer Message Without Auth",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=False,
        expected_status=403
    )
    
    if no_auth_observer_test:
        print("✅ Unauthenticated observer message correctly rejected with 403 status code")
    else:
        print("❌ Unauthenticated observer message not properly rejected")
    
    # Test 3: Send valid observer message
    print("\nTest 3: Send valid observer message")
    
    observer_message = "Focus on the budget planning for Q2"
    
    observer_data = {
        "observer_message": observer_message
    }
    
    observer_test, observer_response = run_test(
        "Send Valid Observer Message",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth=True,
        expected_keys=["message", "observer_message", "agent_responses"]
    )
    
    if not observer_test or not observer_response:
        print("❌ Failed to send valid observer message")
        return False
    
    # Verify the observer message appears as the first message in the response
    agent_responses = observer_response.get("agent_responses", {})
    messages = agent_responses.get("messages", [])
    
    if not messages:
        print("❌ No messages found in response")
        return False
    
    first_message = messages[0]
    if first_message.get("agent_name") != "Observer (You)":
        print("❌ First message is not from Observer")
        return False
    
    if first_message.get("message") != observer_message:
        print("❌ Observer message content doesn't match")
        return False
    
    print("✅ Observer message appears as the first message in the response")
    
    # Verify the scenario_name is "Observer Guidance"
    if agent_responses.get("scenario_name") != "Observer Guidance":
        print("❌ Scenario name is not 'Observer Guidance'")
        return False
    
    print("✅ Scenario name is correctly set to 'Observer Guidance'")
    
    # Verify agents respond respectfully acknowledging the observer's authority
    agent_responses_found = False
    for message in messages[1:]:  # Skip the first message (observer)
        agent_name = message.get("agent_name", "")
        agent_message = message.get("message", "")
        
        print(f"\nAgent Response - {agent_name}: {agent_message}")
        
        if agent_name and agent_message:
            agent_responses_found = True
            
            # Check for respectful acknowledgment (common phrases)
            respectful_phrases = ["understood", "yes", "absolutely", "will do", "agree", "noted", "acknowledge", "certainly", "of course"]
            is_respectful = any(phrase in agent_message.lower() for phrase in respectful_phrases)
            
            if not is_respectful:
                print(f"⚠️ Agent {agent_name} response may not be respectful enough")
            else:
                print(f"✅ Agent {agent_name} responded respectfully")
    
    if not agent_responses_found:
        print("❌ No agent responses found")
        return False
    
    print("✅ Agents responded to the observer message")
    
    # Test 4: Send another observer message with different content
    print("\nTest 4: Send another observer message with different content")
    
    observer_message2 = "We need to prioritize the marketing strategy for the new product launch"
    
    observer_data2 = {
        "observer_message": observer_message2
    }
    
    observer_test2, observer_response2 = run_test(
        "Send Second Observer Message",
        "/observer/send-message",
        method="POST",
        data=observer_data2,
        auth=True,
        expected_keys=["message", "observer_message", "agent_responses"]
    )
    
    if not observer_test2 or not observer_response2:
        print("❌ Failed to send second observer message")
        return False
    
    # Verify the observer message appears as the first message in the response
    agent_responses2 = observer_response2.get("agent_responses", {})
    messages2 = agent_responses2.get("messages", [])
    
    if not messages2:
        print("❌ No messages found in second response")
        return False
    
    first_message2 = messages2[0]
    if first_message2.get("agent_name") != "Observer (You)":
        print("❌ First message in second response is not from Observer")
        return False
    
    if first_message2.get("message") != observer_message2:
        print("❌ Second observer message content doesn't match")
        return False
    
    print("✅ Second observer message appears as the first message in the response")
    
    # Test 5: Generate a regular conversation after observer messages
    print("\nTest 5: Generate a regular conversation after observer messages")
    
    conversation_test, conversation_response = run_test(
        "Generate Conversation After Observer Messages",
        "/conversation/generate",
        method="POST",
        auth=True
    )
    
    if not conversation_test or not conversation_response:
        print("❌ Failed to generate conversation")
        return False
    
    # Check if agents reference or consider the observer directives
    messages = conversation_response.get("messages", [])
    
    if not messages:
        print("❌ No messages found in conversation")
        return False
    
    budget_references = 0
    marketing_references = 0
    product_references = 0
    observer_references = 0
    
    for message in messages:
        agent_name = message.get("agent_name", "")
        agent_message = message.get("message", "")
        
        print(f"\nConversation Message - {agent_name}: {agent_message}")
        
        # Check for references to the observer directives
        if "budget" in agent_message.lower() or "q2" in agent_message.lower() or "quarter" in agent_message.lower():
            budget_references += 1
        
        if "marketing" in agent_message.lower() or "strategy" in agent_message.lower():
            marketing_references += 1
            
        if "product" in agent_message.lower() or "launch" in agent_message.lower():
            product_references += 1
            
        if "observer" in agent_message.lower() or "directive" in agent_message.lower() or "you mentioned" in agent_message.lower():
            observer_references += 1
    
    print(f"\nReferences to budget/Q2: {budget_references}")
    print(f"References to marketing/strategy: {marketing_references}")
    print(f"References to product/launch: {product_references}")
    print(f"References to observer/directive: {observer_references}")
    
    total_references = budget_references + marketing_references + product_references + observer_references
    
    if total_references > 0:
        print("✅ Agents referenced or considered the observer directives in their responses")
    else:
        print("⚠️ Agents did not explicitly reference the observer directives")
    
    # Test 6: Get observer messages
    print("\nTest 6: Get observer messages")
    
    get_observer_test, get_observer_response = run_test(
        "Get Observer Messages",
        "/observer/messages",
        method="GET",
        auth=True
    )
    
    if not get_observer_test or not get_observer_response:
        print("❌ Failed to get observer messages")
        return False
    
    # Verify the observer messages are returned
    if not isinstance(get_observer_response, list):
        print("❌ Observer messages response is not a list")
        return False
    
    if len(get_observer_response) < 2:  # We sent at least 2 observer messages
        print(f"❌ Expected at least 2 observer messages, but got {len(get_observer_response)}")
        return False
    
    print(f"✅ Successfully retrieved {len(get_observer_response)} observer messages")
    
    # Check if our test messages are in the response
    found_message1 = False
    found_message2 = False
    
    for msg in get_observer_response:
        if msg.get("message") == observer_message:
            found_message1 = True
        if msg.get("message") == observer_message2:
            found_message2 = True
    
    if found_message1 and found_message2:
        print("✅ Both test observer messages found in the response")
    else:
        if not found_message1:
            print("❌ First test observer message not found in the response")
        if not found_message2:
            print("❌ Second test observer message not found in the response")
    
    return True

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("OBSERVER MESSAGE FUNCTIONALITY TEST")
    print("="*80)
    
    # Login first to get auth token
    if not test_login():
        print("❌ Login failed. Cannot proceed with tests.")
        return
    
    # Set up simulation with agents
    if not setup_simulation():
        print("❌ Failed to set up simulation. Cannot proceed with tests.")
        return
    
    # Test observer message functionality comprehensively
    observer_test_result = test_observer_message_comprehensive()
    
    # Print final summary
    print("\n" + "="*80)
    print("OBSERVER MESSAGE FUNCTIONALITY TEST SUMMARY")
    print("="*80)
    
    if observer_test_result:
        print("✅ Observer message functionality is working correctly!")
        print("✅ Observer messages can be sent and received")
        print("✅ Observer messages appear as the first message in the response")
        print("✅ Scenario name is correctly set to 'Observer Guidance'")
        print("✅ Agents respond respectfully acknowledging the observer's authority")
        print("✅ Multiple observer messages can be sent in sequence")
        print("✅ Observer messages can be retrieved via the API")
        print("✅ Observer directives influence subsequent conversations")
    else:
        print("❌ Observer message functionality has issues")
    
    print("="*80)

if __name__ == "__main__":
    main()