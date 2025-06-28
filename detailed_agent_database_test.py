#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv
import uuid
import time

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

def login_as_admin():
    """Login with admin credentials"""
    global auth_token, test_user_id
    
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    print(f"\n{'='*80}\nLogging in as admin user (dino@cytonic.com)")
    
    url = f"{API_URL}/auth/login"
    response = requests.post(url, json=login_data)
    
    if response.status_code == 200:
        response_data = response.json()
        auth_token = response_data.get("access_token")
        user_data = response_data.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Login successful. User ID: {test_user_id}")
        return True
    else:
        print(f"❌ Login failed. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False

def get_all_agents_debug():
    """Get all agents in the database using the debug endpoint"""
    if not auth_token:
        print("❌ No auth token available. Please login first.")
        return []
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    url = f"{API_URL}/debug/agents"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get all agents. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return []

def get_user_agents():
    """Get agents for the current user"""
    if not auth_token:
        print("❌ No auth token available. Please login first.")
        return []
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    url = f"{API_URL}/agents"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get user agents. Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return []

def fix_observer_message_endpoint():
    """Test a fix for the observer message endpoint"""
    print(f"\n{'='*80}\nTESTING FIX FOR OBSERVER MESSAGE ENDPOINT")
    
    # Create a test script to fix the observer message endpoint
    fix_script = """
import pymongo
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Load environment variables
load_dotenv('/app/backend/.env')

# Connect to MongoDB
mongo_url = os.environ.get('MONGO_URL')
client = pymongo.MongoClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'ai_simulation')]

# Get all agents
agents = list(db.agents.find())
print(f"Found {len(agents)} agents in the database")

# Count agents by user_id
user_agents = {}
for agent in agents:
    user_id = agent.get('user_id', 'none')
    if user_id in user_agents:
        user_agents[user_id] += 1
    else:
        user_agents[user_id] = 1

print("\\nAgents by user_id:")
for user_id, count in user_agents.items():
    print(f"  - {user_id}: {count} agents")

# Count agents by archetype
archetype_counts = {}
for agent in agents:
    archetype = agent.get('archetype', 'unknown')
    if archetype in archetype_counts:
        archetype_counts[archetype] += 1
    else:
        archetype_counts[archetype] = 1

print("\\nAgents by archetype:")
for archetype, count in archetype_counts.items():
    print(f"  - {archetype}: {count} agents")

# Check for agents without user_id
no_user_id = [agent for agent in agents if not agent.get('user_id')]
print(f"\\nFound {len(no_user_id)} agents without user_id")

# Check for test agents
test_agents = []
for agent in agents:
    name = agent.get('name', '').lower()
    if 'test' in name or 'dummy' in name or 'sample' in name:
        test_agents.append(agent)

print(f"Found {len(test_agents)} potential test agents")
if test_agents:
    for agent in test_agents:
        print(f"  - {agent.get('name')} (ID: {agent.get('_id')}, User ID: {agent.get('user_id', 'None')})")

# Check observer messages
observer_messages = list(db.observer_messages.find().sort("timestamp", -1))
print(f"\\nFound {len(observer_messages)} observer messages")

# Check conversations
conversations = list(db.conversations.find())
print(f"Found {len(conversations)} conversations")

# Count conversations by user_id
user_conversations = {}
for conv in conversations:
    user_id = conv.get('user_id', 'none')
    if user_id in user_conversations:
        user_conversations[user_id] += 1
    else:
        user_conversations[user_id] = 1

print("\\nConversations by user_id:")
for user_id, count in user_conversations.items():
    print(f"  - {user_id}: {count} conversations")

# Check for conversations without user_id
no_user_id_convs = [conv for conv in conversations if not conv.get('user_id')]
print(f"Found {len(no_user_id_convs)} conversations without user_id")

# Check simulation states
simulation_states = list(db.simulation_state.find())
print(f"\\nFound {len(simulation_states)} simulation states")

# Count simulation states by user_id
user_states = {}
for state in simulation_states:
    user_id = state.get('user_id', 'none')
    if user_id in user_states:
        user_states[user_id] += 1
    else:
        user_states[user_id] = 1

print("\\nSimulation states by user_id:")
for user_id, count in user_states.items():
    print(f"  - {user_id}: {count} states")
"""
    
    # Write the fix script to a file
    with open('/app/fix_observer_endpoint.py', 'w') as f:
        f.write(fix_script)
    
    # Run the fix script
    print("\nRunning database analysis script...")
    os.system('python /app/fix_observer_endpoint.py')

def send_observer_message_with_user_filter():
    """Test sending an observer message with user filtering"""
    print(f"\n{'='*80}\nTESTING OBSERVER MESSAGE WITH USER FILTERING")
    
    if not auth_token:
        print("❌ No auth token available. Please login first.")
        return False
    
    # Get user agents
    user_agents = get_user_agents()
    print(f"Found {len(user_agents)} agents for the current user")
    
    # Create a test script to send observer message with user filtering
    test_script = f"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{{BACKEND_URL}}/api"

# Auth token
auth_token = "{auth_token}"
user_id = "{test_user_id}"

# Send observer message with user filtering
headers = {{"Authorization": f"Bearer {{auth_token}}"}}
url = f"{{API_URL}}/observer/send-message"
data = {{
    "observer_message": "This is a test message with user filtering. Please acknowledge."
}}

print(f"Sending observer message with user filtering...")
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    response_data = response.json()
    print("✅ Observer message sent successfully")
    
    # Check agent responses
    agent_responses = response_data.get("agent_responses", {{}}).get("messages", [])
    
    # Count agent responses
    agent_response_count = len(agent_responses) - 1  # Subtract 1 for the observer message
    print(f"Received responses from {{agent_response_count}} agents")
    
    # Print agent names
    print("\\nResponding agents:")
    for i, msg in enumerate(agent_responses):
        if i == 0:  # Skip observer message
            continue
        print(f"  - {{msg.get('agent_name')}}")
else:
    print(f"❌ Failed to send observer message. Status code: {{response.status_code}}")
    try:
        print(f"Response: {{response.json()}}")
    except:
        print(f"Response: {{response.text}}")
"""
    
    # Write the test script to a file
    with open('/app/test_observer_with_filter.py', 'w') as f:
        f.write(test_script)
    
    # Run the test script
    print("\nRunning observer message test with user filtering...")
    os.system('python /app/test_observer_with_filter.py')

def main():
    """Main test function"""
    print(f"\n{'='*80}")
    print("DETAILED AGENT DATABASE AND OBSERVER MESSAGE TESTING")
    print(f"{'='*80}")
    
    # Login as admin
    if not login_as_admin():
        print("❌ Cannot proceed with testing without admin login")
        sys.exit(1)
    
    # Get user agents
    user_agents = get_user_agents()
    print(f"\nFound {len(user_agents)} agents for the current user (filtered by user_id)")
    
    # Try to get all agents using debug endpoint
    all_agents = get_all_agents_debug()
    if all_agents:
        print(f"\nFound {len(all_agents)} total agents in the database (unfiltered)")
        
        # Analyze all agents
        print(f"\n{'='*80}\nANALYZING ALL AGENTS IN DATABASE")
        
        # Count agents by user_id
        user_agents_count = {}
        for agent in all_agents:
            user_id = agent.get("user_id", "none")
            if user_id in user_agents_count:
                user_agents_count[user_id] += 1
            else:
                user_agents_count[user_id] = 1
        
        print("\nAgents by user_id:")
        for user_id, count in user_agents_count.items():
            print(f"  - {user_id}: {count} agents")
        
        # Count agents by archetype
        archetype_counts = {}
        for agent in all_agents:
            archetype = agent.get("archetype", "unknown")
            if archetype in archetype_counts:
                archetype_counts[archetype] += 1
            else:
                archetype_counts[archetype] = 1
        
        print("\nAgents by archetype:")
        for archetype, count in archetype_counts.items():
            print(f"  - {archetype}: {count} agents")
        
        # Check for agents without user_id
        no_user_id = [agent for agent in all_agents if not agent.get("user_id")]
        print(f"\nFound {len(no_user_id)} agents without user_id")
        
        # Check for test agents
        test_agents = []
        for agent in all_agents:
            name = agent.get("name", "").lower()
            if "test" in name or "dummy" in name or "sample" in name:
                test_agents.append(agent)
        
        print(f"Found {len(test_agents)} potential test agents")
        if test_agents:
            for agent in test_agents:
                print(f"  - {agent.get('name')} (ID: {agent.get('id')}, User ID: {agent.get('user_id', 'None')})")
    else:
        print("❌ Could not access all agents in the database")
    
    # Run fix script for observer message endpoint
    fix_observer_message_endpoint()
    
    # Test observer message with user filtering
    send_observer_message_with_user_filter()
    
    # Print summary and recommendations
    print(f"\n{'='*80}\nSUMMARY AND RECOMMENDATIONS")
    print(f"{'='*80}")
    
    print("\nIssues Found:")
    print("1. The observer message endpoint is not properly filtering agents by user_id")
    print("   - It's getting all agents from the database instead of just the current user's agents")
    print("   - This is why so many agents are responding to observer messages")
    print("2. The observer message endpoint does not require authentication")
    print("   - This is a security issue that allows anyone to send observer messages")
    
    print("\nRecommendations:")
    print("1. Fix the observer message endpoint to filter agents by user_id:")
    print("   - Change line 298 from:")
    print("     agents = await db.agents.find().to_list(100)")
    print("   - To:")
    print("     agents = await db.agents.find({\"user_id\": current_user.id}).to_list(100)")
    print("2. Add authentication requirement to the observer message endpoint:")
    print("   - Change line 289 from:")
    print("     @api_router.post(\"/observer/send-message\")")
    print("   - To:")
    print("     @api_router.post(\"/observer/send-message\")")
    print("     async def send_observer_message(input_data: ObserverInput, current_user: User = Depends(get_current_user)):")
    print("3. Fix the get_observer_messages endpoint to filter by user_id")
    print("4. Add user_id to the ConversationRound when creating observer conversations")

if __name__ == "__main__":
    main()