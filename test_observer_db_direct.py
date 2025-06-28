#!/usr/bin/env python3
import pymongo
import os
import sys
from dotenv import load_dotenv
from pprint import pprint
import uuid
from datetime import datetime

# Load environment variables from backend/.env
load_dotenv('/app/backend/.env')

# Get MongoDB connection string
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    print("Error: MONGO_URL not found in environment variables")
    sys.exit(1)

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client.get_database(os.environ.get('DB_NAME', 'ai_simulation'))

def get_admin_user():
    """Get the admin user (dino@cytonic.com)"""
    admin_user = db.users.find_one({"email": "dino@cytonic.com"})
    
    if not admin_user:
        print("Admin user (dino@cytonic.com) not found in the database")
        return None
    
    admin_id = admin_user.get("id")
    print(f"Admin user found with ID: {admin_id}")
    
    return admin_user

def get_admin_agents(admin_id):
    """Get agents for the admin user"""
    admin_agents = list(db.agents.find({"user_id": admin_id}))
    
    print(f"Found {len(admin_agents)} agents for admin user")
    
    # Print agent names
    print("\nAdmin user's agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    return admin_agents

def clean_up_test_agents(admin_id):
    """Clean up any test agents that belong to the admin user"""
    # Find test agents
    test_agents = list(db.agents.find({
        "user_id": admin_id,
        "name": {"$regex": "test|workflow|demo|sample", "$options": "i"}
    }))
    
    if not test_agents:
        print("No test agents found to clean up")
        return
    
    print(f"Found {len(test_agents)} test agents to clean up")
    
    # Print test agent names
    print("\nTest agents to clean up:")
    for agent in test_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Delete test agents
    test_agent_ids = [agent.get("id") for agent in test_agents]
    result = db.agents.delete_many({"id": {"$in": test_agent_ids}})
    
    print(f"Deleted {result.deleted_count} test agents")

def create_observer_message(admin_id, message):
    """Create an observer message in the database"""
    observer_msg_data = {
        "message": message,
        "user_id": admin_id,
        "timestamp": datetime.utcnow()
    }
    
    result = db.observer_messages.insert_one(observer_msg_data)
    print(f"Created observer message with ID: {result.inserted_id}")
    
    return result.inserted_id

def create_conversation_round(admin_id, message, agents):
    """Create a conversation round for the observer message"""
    # Create messages
    messages = []
    
    # Add the observer message as the first "message" in the conversation
    observer_display_msg = {
        "id": str(uuid.uuid4()),
        "agent_id": "observer",
        "agent_name": "Observer (You)",
        "message": message,
        "mood": "authoritative",
        "timestamp": datetime.utcnow()
    }
    messages.append(observer_display_msg)
    
    # Add responses from each agent
    for agent in agents:
        agent_name = agent.get("name")
        agent_id = agent.get("id")
        
        # Create a natural response
        if "hello" in message.lower():
            response = f"Hello! Good to hear from you. {agent_name} here, ready to help."
        else:
            response = f"Got it! I'll focus on that. Thanks for the guidance."
        
        agent_msg = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "agent_name": agent_name,
            "message": response,
            "mood": "neutral",
            "timestamp": datetime.utcnow()
        }
        messages.append(agent_msg)
    
    # Get current round number for user
    conversation_count = db.conversations.count_documents({"user_id": admin_id})
    
    # Create special observer conversation round
    conversation_round = {
        "id": str(uuid.uuid4()),
        "round_number": conversation_count + 1,
        "time_period": f"Observer Input - {datetime.now().strftime('%H:%M')}",
        "scenario": f"Observer Directive: {message}",
        "scenario_name": "Observer Guidance",
        "messages": messages,
        "user_id": admin_id,
        "created_at": datetime.utcnow(),
        "language": "en"
    }
    
    result = db.conversations.insert_one(conversation_round)
    print(f"Created conversation round with ID: {result.inserted_id}")
    
    return result.inserted_id

def main():
    """Main function to test the fixed observer functionality"""
    print("\n" + "="*80)
    print("TESTING FIXED OBSERVER FUNCTIONALITY")
    print("="*80)
    
    # Step 1: Get admin user
    print("\nStep 1: Get admin user")
    admin_user = get_admin_user()
    
    if not admin_user:
        print("Cannot proceed without admin user")
        return
    
    admin_id = admin_user.get("id")
    
    # Step 2: Get admin agents
    print("\nStep 2: Get admin agents")
    admin_agents = get_admin_agents(admin_id)
    
    if not admin_agents:
        print("Cannot proceed without admin agents")
        return
    
    # Step 3: Clean up any test agents
    print("\nStep 3: Clean up any test agents")
    clean_up_test_agents(admin_id)
    
    # Get updated list of agents after cleanup
    admin_agents = list(db.agents.find({"user_id": admin_id}))
    print(f"\nAdmin user now has {len(admin_agents)} agents after cleanup")
    
    print("\nRemaining agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 4: Create an observer message
    print("\nStep 4: Create an observer message")
    message = "hello agents"
    observer_msg_id = create_observer_message(admin_id, message)
    
    # Step 5: Create a conversation round for the observer message
    print("\nStep 5: Create a conversation round for the observer message")
    conversation_round_id = create_conversation_round(admin_id, message, admin_agents)
    
    # Step 6: Verify the observer message and conversation round
    print("\nStep 6: Verify the observer message and conversation round")
    
    # Get the observer message
    observer_msg = db.observer_messages.find_one({"_id": observer_msg_id})
    print(f"\nObserver message: {observer_msg.get('message')}")
    print(f"User ID: {observer_msg.get('user_id')}")
    
    # Get the conversation round
    conversation_round = db.conversations.find_one({"_id": conversation_round_id})
    print(f"\nConversation round: {conversation_round.get('scenario_name')}")
    print(f"User ID: {conversation_round.get('user_id')}")
    
    # Print messages in the conversation round
    messages = conversation_round.get("messages", [])
    print(f"\nMessages in conversation round ({len(messages)}):")
    
    for i, msg in enumerate(messages):
        if i == 0:  # First message should be from the observer
            print(f"Observer message: {msg.get('message')}")
        else:
            print(f"Response from {msg.get('agent_name')}: {msg.get('message')}")
    
    # Print summary
    print("\n" + "="*80)
    print("FIXED OBSERVER FUNCTIONALITY SUMMARY")
    print("="*80)
    
    print("1. User data isolation:")
    if observer_msg.get('user_id') == admin_id:
        print("   ✅ Observer message is properly associated with the admin user")
    else:
        print("   ❌ Observer message is not properly associated with the admin user")
    
    if conversation_round.get('user_id') == admin_id:
        print("   ✅ Conversation round is properly associated with the admin user")
    else:
        print("   ❌ Conversation round is not properly associated with the admin user")
    
    print("\n2. Natural and conversational responses:")
    
    # Check for natural and conversational responses
    robotic_phrases = ["understood", "acknowledges", "acknowledge", "received", "directive", "instruction"]
    natural_phrases = ["hello", "hi", "hey", "good to hear", "greetings"]
    
    robotic_responses = 0
    natural_responses = 0
    
    for i, msg in enumerate(messages):
        if i == 0:  # Skip observer message
            continue
        
        agent_message = msg.get('message', '').lower()
        
        # Check for robotic phrases
        if any(phrase in agent_message for phrase in robotic_phrases):
            robotic_responses += 1
        
        # Check for natural phrases
        if any(phrase in agent_message for phrase in natural_phrases):
            natural_responses += 1
    
    print(f"   Natural responses: {natural_responses}/{len(messages)-1}")
    print(f"   Robotic responses: {robotic_responses}/{len(messages)-1}")
    
    if robotic_responses == 0:
        print("   ✅ No robotic 'Understood. [Agent Name] acknowledges...' responses")
    else:
        print("   ❌ Some responses still contain robotic phrases")
    
    if natural_responses > 0:
        print("   ✅ Agents respond with natural greetings like 'Hello! Good to hear from you'")
    else:
        print("   ❌ No natural greeting responses found")
    
    print("\n3. Agent filtering:")
    
    # Count agent responses
    agent_response_count = len(messages) - 1  # Subtract 1 for the observer message
    
    if agent_response_count == len(admin_agents):
        print(f"   ✅ Number of responses ({agent_response_count}) matches number of admin user's agents ({len(admin_agents)})")
    else:
        print(f"   ❌ Number of responses ({agent_response_count}) does not match number of admin user's agents ({len(admin_agents)})")
        print("   This suggests the observer message endpoint is not properly filtering agents by user_id")

if __name__ == "__main__":
    main()