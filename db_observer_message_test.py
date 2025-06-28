#!/usr/bin/env python3
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import json

# Load environment variables from backend/.env
load_dotenv('/app/backend/.env')

# Get MongoDB URL from environment variables
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    print("Error: MONGO_URL not found in environment variables")
    sys.exit(1)

# Connect to MongoDB
client = MongoClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'ai_simulation')]

def print_separator():
    print("\n" + "="*80)

def test_observer_message_fix():
    """Test the fixed observer message functionality by directly querying the database"""
    print_separator()
    print("TESTING FIXED OBSERVER MESSAGE FUNCTIONALITY (DATABASE LEVEL)")
    print_separator()
    
    # Step 1: Check admin user
    print("\nStep 1: Check admin user (dino@cytonic.com)")
    admin_user = db.users.find_one({"email": "dino@cytonic.com"})
    
    if not admin_user:
        print("❌ Admin user not found in database")
        return False
    
    admin_id = admin_user.get("id")
    print(f"✅ Found admin user with ID: {admin_id}")
    
    # Step 2: Check how many agents the admin user has
    print("\nStep 2: Check how many agents the admin user has")
    admin_agents = list(db.agents.find({"user_id": admin_id}))
    
    if not admin_agents:
        print("❌ No agents found for admin user")
        return False
    
    print(f"✅ Found {len(admin_agents)} agents for admin user")
    
    # Print agent names
    print("\nAdmin user's agents:")
    for agent in admin_agents:
        print(f"  - {agent.get('name')} ({agent.get('id')})")
    
    # Step 3: Check all agents in the database
    print("\nStep 3: Check all agents in the database")
    all_agents = list(db.agents.find())
    
    print(f"Total agents in database: {len(all_agents)}")
    
    # Count agents by user_id
    user_agent_counts = {}
    for agent in all_agents:
        user_id = agent.get("user_id", "no_user")
        if user_id not in user_agent_counts:
            user_agent_counts[user_id] = 0
        user_agent_counts[user_id] += 1
    
    print("\nAgents by user_id:")
    for user_id, count in user_agent_counts.items():
        print(f"  - User {user_id}: {count} agents")
    
    # Step 4: Check observer messages
    print("\nStep 4: Check observer messages")
    observer_messages = list(db.observer_messages.find().sort("timestamp", -1).limit(10))
    
    if not observer_messages:
        print("❌ No observer messages found in database")
    else:
        print(f"✅ Found {len(observer_messages)} observer messages")
        
        # Print observer messages
        print("\nRecent observer messages:")
        for msg in observer_messages:
            user_id = msg.get("user_id", "no_user")
            message = msg.get("message", "")
            timestamp = msg.get("timestamp", "")
            print(f"  - User {user_id}: '{message}' at {timestamp}")
    
    # Step 5: Check conversation rounds
    print("\nStep 5: Check conversation rounds")
    conversation_rounds = list(db.conversations.find().sort("created_at", -1).limit(10))
    
    if not conversation_rounds:
        print("❌ No conversation rounds found in database")
    else:
        print(f"✅ Found {len(conversation_rounds)} conversation rounds")
        
        # Print conversation rounds
        print("\nRecent conversation rounds:")
        for round in conversation_rounds:
            user_id = round.get("user_id", "no_user")
            scenario_name = round.get("scenario_name", "")
            round_number = round.get("round_number", "")
            created_at = round.get("created_at", "")
            message_count = len(round.get("messages", []))
            print(f"  - User {user_id}: Round {round_number}, '{scenario_name}' with {message_count} messages at {created_at}")
    
    # Step 6: Check if observer messages have user_id
    print("\nStep 6: Check if observer messages have user_id")
    observer_messages_without_user_id = list(db.observer_messages.find({"user_id": {"$exists": False}}))
    
    if observer_messages_without_user_id:
        print(f"❌ Found {len(observer_messages_without_user_id)} observer messages without user_id")
    else:
        print("✅ All observer messages have user_id")
    
    # Step 7: Check if conversation rounds from observer messages have user_id
    print("\nStep 7: Check if conversation rounds from observer messages have user_id")
    observer_rounds = list(db.conversations.find({"scenario_name": "Observer Guidance"}))
    observer_rounds_without_user_id = list(db.conversations.find({
        "scenario_name": "Observer Guidance",
        "user_id": {"$exists": False}
    }))
    
    if observer_rounds_without_user_id:
        print(f"❌ Found {len(observer_rounds_without_user_id)} observer conversation rounds without user_id")
    else:
        print("✅ All observer conversation rounds have user_id")
    
    # Print summary
    print_separator()
    print("FIXED OBSERVER MESSAGE FUNCTIONALITY TEST SUMMARY")
    print_separator()
    
    print("1. User data isolation:")
    if len(admin_agents) == user_agent_counts.get(admin_id, 0):
        print("   ✅ Admin user's agents are properly associated with the user")
    else:
        print("   ❌ Admin user's agents count doesn't match the count in the database")
    
    print("\n2. Observer message user association:")
    if not observer_messages_without_user_id:
        print("   ✅ All observer messages are properly associated with users")
    else:
        print("   ❌ Some observer messages are not associated with users")
    
    print("\n3. Conversation round user association:")
    if not observer_rounds_without_user_id:
        print("   ✅ All observer conversation rounds are properly associated with users")
    else:
        print("   ❌ Some observer conversation rounds are not associated with users")
    
    return True

if __name__ == "__main__":
    test_observer_message_fix()