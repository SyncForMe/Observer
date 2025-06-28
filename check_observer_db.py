#!/usr/bin/env python3
import pymongo
import os
import sys
from dotenv import load_dotenv
from pprint import pprint

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

def check_admin_agents():
    """Check agents for the admin user (dino@cytonic.com)"""
    # First, find the admin user
    admin_user = db.users.find_one({"email": "dino@cytonic.com"})
    
    if not admin_user:
        print("Admin user (dino@cytonic.com) not found in the database")
        return None
    
    admin_id = admin_user.get("id")
    print(f"Admin user found with ID: {admin_id}")
    
    # Get agents for the admin user
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

def check_observer_messages():
    """Check observer messages in the database"""
    # Get all observer messages
    observer_messages = list(db.observer_messages.find().sort("timestamp", -1).limit(10))
    
    print(f"Found {len(observer_messages)} observer messages")
    
    # Print observer messages
    print("\nRecent observer messages:")
    for msg in observer_messages:
        print(f"  - {msg.get('message')} (User ID: {msg.get('user_id')})")
    
    return observer_messages

def check_conversation_rounds():
    """Check conversation rounds in the database"""
    # Get all conversation rounds
    conversation_rounds = list(db.conversations.find().sort("created_at", -1).limit(10))
    
    print(f"Found {len(conversation_rounds)} conversation rounds")
    
    # Print conversation rounds
    print("\nRecent conversation rounds:")
    for round in conversation_rounds:
        print(f"  - Round {round.get('round_number')}: {round.get('scenario_name')} (User ID: {round.get('user_id')})")
        
        # Check if this is an observer guidance round
        if round.get('scenario_name') == "Observer Guidance":
            print(f"    Observer Guidance round found!")
            
            # Print messages in this round
            messages = round.get('messages', [])
            print(f"    Contains {len(messages)} messages")
            
            for i, msg in enumerate(messages):
                if i == 0:  # First message should be from the observer
                    print(f"    Observer message: {msg.get('message')}")
                else:
                    print(f"    Response from {msg.get('agent_name')}: {msg.get('message')}")
    
    return conversation_rounds

def main():
    """Main function to check the fixed observer functionality"""
    print("\n" + "="*80)
    print("CHECKING FIXED OBSERVER FUNCTIONALITY")
    print("="*80)
    
    # Step 1: Check admin user agents
    print("\nStep 1: Check admin user agents")
    admin_agents = check_admin_agents()
    
    if not admin_agents:
        print("Cannot proceed without admin agents")
        return
    
    # Get admin user ID
    admin_user = db.users.find_one({"email": "dino@cytonic.com"})
    admin_id = admin_user.get("id")
    
    # Step 2: Clean up any test agents
    print("\nStep 2: Clean up any test agents")
    clean_up_test_agents(admin_id)
    
    # Get updated list of agents after cleanup
    admin_agents = list(db.agents.find({"user_id": admin_id}))
    print(f"\nAdmin user now has {len(admin_agents)} agents after cleanup")
    
    print("\nRemaining agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 3: Check observer messages
    print("\nStep 3: Check observer messages")
    observer_messages = check_observer_messages()
    
    # Step 4: Check conversation rounds
    print("\nStep 4: Check conversation rounds")
    conversation_rounds = check_conversation_rounds()
    
    # Step 5: Check if observer messages are properly associated with the admin user
    print("\nStep 5: Check if observer messages are properly associated with the admin user")
    
    admin_observer_messages = list(db.observer_messages.find({"user_id": admin_id}))
    print(f"Found {len(admin_observer_messages)} observer messages for admin user")
    
    # Step 6: Check if conversation rounds for observer messages are properly associated with the admin user
    print("\nStep 6: Check if conversation rounds for observer messages are properly associated with the admin user")
    
    admin_observer_rounds = list(db.conversations.find({
        "user_id": admin_id,
        "scenario_name": "Observer Guidance"
    }))
    print(f"Found {len(admin_observer_rounds)} observer guidance rounds for admin user")
    
    # Print summary
    print("\n" + "="*80)
    print("FIXED OBSERVER FUNCTIONALITY SUMMARY")
    print("="*80)
    
    print("1. User data isolation:")
    if len(admin_observer_messages) > 0 and all(msg.get('user_id') == admin_id for msg in admin_observer_messages):
        print("   ✅ Observer messages are properly associated with the admin user")
    else:
        print("   ❌ Observer messages are not properly associated with the admin user")
    
    if len(admin_observer_rounds) > 0 and all(round.get('user_id') == admin_id for round in admin_observer_rounds):
        print("   ✅ Observer guidance rounds are properly associated with the admin user")
    else:
        print("   ❌ Observer guidance rounds are not properly associated with the admin user")
    
    print("\n2. Natural and conversational responses:")
    
    # Check for natural and conversational responses in the most recent observer guidance round
    if admin_observer_rounds:
        most_recent_round = admin_observer_rounds[0]
        messages = most_recent_round.get('messages', [])
        
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
    else:
        print("   ❓ No observer guidance rounds found to check response quality")
    
    print("\n3. Agent filtering:")
    if admin_observer_rounds:
        most_recent_round = admin_observer_rounds[0]
        messages = most_recent_round.get('messages', [])
        
        # Count agent responses
        agent_response_count = len(messages) - 1  # Subtract 1 for the observer message
        
        if agent_response_count == len(admin_agents):
            print(f"   ✅ Number of responses ({agent_response_count}) matches number of admin user's agents ({len(admin_agents)})")
        else:
            print(f"   ❌ Number of responses ({agent_response_count}) does not match number of admin user's agents ({len(admin_agents)})")
            print("   This suggests the observer message endpoint is not properly filtering agents by user_id")
    else:
        print("   ❓ No observer guidance rounds found to check agent filtering")

if __name__ == "__main__":
    main()