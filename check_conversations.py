#!/usr/bin/env python3
"""
Test script to check the MongoDB database for conversation data
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv('/app/backend/.env')

# Get MongoDB connection string
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'ai_simulation')
if not MONGO_URL:
    logging.error("Error: MONGO_URL not found in environment variables")
    exit(1)

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    logging.info("Successfully connected to MongoDB")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

def check_conversations():
    """Check the conversations collection"""
    logging.info("\n=== CHECKING CONVERSATIONS COLLECTION ===")
    
    # Get all conversations
    conversations = list(db.conversations.find())
    logging.info(f"Found {len(conversations)} conversations in the database")
    
    # Print conversation details
    for i, conv in enumerate(conversations, 1):
        logging.info(f"\nConversation {i}:")
        logging.info(f"  ID: {conv.get('id')}")
        logging.info(f"  User ID: {conv.get('user_id')}")
        logging.info(f"  Round Number: {conv.get('round_number')}")
        logging.info(f"  Time Period: {conv.get('time_period')}")
        logging.info(f"  Scenario: {conv.get('scenario')}")
        logging.info(f"  Scenario Name: {conv.get('scenario_name')}")
        logging.info(f"  Created At: {conv.get('created_at')}")
        logging.info(f"  Messages: {len(conv.get('messages', []))}")
    
    # Check if there are any conversations without a user_id
    no_user_id_conversations = [conv for conv in conversations if not conv.get('user_id')]
    if no_user_id_conversations:
        logging.warning(f"\nFound {len(no_user_id_conversations)} conversations without a user_id")
        for i, conv in enumerate(no_user_id_conversations, 1):
            logging.warning(f"  Conversation {i} ID: {conv.get('id')}")
    else:
        logging.info("\nAll conversations have a user_id")
    
    # Check if there are any conversations with the same ID
    conversation_ids = [conv.get('id') for conv in conversations]
    duplicate_ids = set([id for id in conversation_ids if conversation_ids.count(id) > 1])
    if duplicate_ids:
        logging.warning(f"\nFound {len(duplicate_ids)} duplicate conversation IDs")
        for id in duplicate_ids:
            logging.warning(f"  Duplicate ID: {id}")
    else:
        logging.info("\nNo duplicate conversation IDs found")
    
    return conversations

def check_users():
    """Check the users collection"""
    logging.info("\n=== CHECKING USERS COLLECTION ===")
    
    # Get all users
    users = list(db.users.find())
    logging.info(f"Found {len(users)} users in the database")
    
    # Print user details
    for i, user in enumerate(users, 1):
        logging.info(f"\nUser {i}:")
        logging.info(f"  ID: {user.get('id')}")
        logging.info(f"  Email: {user.get('email')}")
        logging.info(f"  Name: {user.get('name')}")
        logging.info(f"  Created At: {user.get('created_at')}")
        logging.info(f"  Last Login: {user.get('last_login')}")
    
    return users

def check_cross_references(conversations, users):
    """Check cross-collection references"""
    logging.info("\n=== CHECKING CROSS-COLLECTION REFERENCES ===")
    
    user_ids = [user.get('id') for user in users]
    
    # Check if there are any conversations with a user_id that doesn't exist in the users collection
    conversations_with_invalid_user_id = [conv for conv in conversations if conv.get('user_id') not in user_ids]
    if conversations_with_invalid_user_id:
        logging.warning(f"\nFound {len(conversations_with_invalid_user_id)} conversations with a user_id that doesn't exist in the users collection")
        for i, conv in enumerate(conversations_with_invalid_user_id, 1):
            logging.warning(f"  Conversation {i} ID: {conv.get('id')}, User ID: {conv.get('user_id')}")
    else:
        logging.info("\nAll conversations have a valid user_id")

def fix_conversations():
    """Fix conversations without a user_id"""
    logging.info("\n=== FIXING CONVERSATIONS WITHOUT USER_ID ===")
    
    # Get all conversations without a user_id
    no_user_id_conversations = list(db.conversations.find({"user_id": {"$exists": False}}))
    if not no_user_id_conversations:
        no_user_id_conversations = list(db.conversations.find({"user_id": None}))
    
    if not no_user_id_conversations:
        logging.info("No conversations without a user_id found")
        return
    
    logging.info(f"Found {len(no_user_id_conversations)} conversations without a user_id")
    
    # Get the first user in the database
    first_user = db.users.find_one()
    if not first_user:
        logging.error("No users found in the database")
        return
    
    first_user_id = first_user.get('id')
    logging.info(f"Using user ID {first_user_id} for conversations without a user_id")
    
    # Update conversations without a user_id
    for conv in no_user_id_conversations:
        conv_id = conv.get('id')
        logging.info(f"Updating conversation {conv_id} with user_id {first_user_id}")
        
        try:
            db.conversations.update_one(
                {"id": conv_id},
                {"$set": {"user_id": first_user_id}}
            )
            logging.info(f"Successfully updated conversation {conv_id}")
        except Exception as e:
            logging.error(f"Failed to update conversation {conv_id}: {e}")

def main():
    """Main function"""
    logging.info("Starting MongoDB check...")
    
    # Check conversations
    conversations = check_conversations()
    
    # Check users
    users = check_users()
    
    # Check cross-references
    check_cross_references(conversations, users)
    
    # Fix conversations without a user_id
    fix_conversations()
    
    # Check conversations again after fixing
    logging.info("\n=== CHECKING CONVERSATIONS AFTER FIXING ===")
    check_conversations()
    
    logging.info("\n=== MongoDB check complete ===")

if __name__ == "__main__":
    main()