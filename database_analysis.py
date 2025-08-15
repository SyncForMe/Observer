#!/usr/bin/env python3
"""
DATABASE ANALYSIS FOR CONVERSATION TIMING
Analyze conversation data directly from MongoDB to understand timing patterns.
"""

import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ai_simulation')

print(f"Connecting to MongoDB: {MONGO_URL}")
print(f"Database: {DB_NAME}")

async def analyze_conversation_timing():
    """Analyze conversation timing patterns from database"""
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        print("\n📊 DATABASE ANALYSIS")
        print("="*50)
        
        # Get conversation count
        conv_count = await db.conversations.count_documents({})
        print(f"Total conversations: {conv_count}")
        
        if conv_count == 0:
            print("❌ No conversations found in database")
            return
        
        # Get recent conversations
        conversations = await db.conversations.find({}).sort("created_at", -1).limit(5).to_list(5)
        
        print(f"\n🔍 ANALYZING RECENT CONVERSATIONS:")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n--- Conversation {i} ---")
            print(f"ID: {conv.get('id', 'N/A')}")
            print(f"Round: {conv.get('round_number', 'N/A')}")
            print(f"Created: {conv.get('created_at', 'N/A')}")
            print(f"Scenario: {conv.get('scenario_name', 'N/A')}")
            
            messages = conv.get('messages', [])
            print(f"Messages: {len(messages)}")
            
            if len(messages) > 1:
                print(f"Message timing analysis:")
                
                timestamps = []
                for j, msg in enumerate(messages):
                    agent_name = msg.get('agent_name', 'Unknown')
                    timestamp = msg.get('timestamp', 'N/A')
                    message_text = msg.get('message', '')[:50] + "..."
                    
                    print(f"  {j+1}. {agent_name}: {timestamp}")
                    print(f"     {message_text}")
                    
                    if timestamp != 'N/A':
                        timestamps.append(timestamp)
                
                # Analyze timestamp patterns
                if len(timestamps) > 1:
                    unique_timestamps = len(set(timestamps))
                    print(f"\n  📊 Timestamp Analysis:")
                    print(f"     Total messages: {len(timestamps)}")
                    print(f"     Unique timestamps: {unique_timestamps}")
                    
                    if unique_timestamps == 1:
                        print(f"     🚨 BULK CREATION: All messages have same timestamp")
                        print(f"     🔍 This explains '10 messages appearing at once'")
                    elif unique_timestamps == len(timestamps):
                        print(f"     ✅ SEQUENTIAL: Each message has unique timestamp")
                    else:
                        print(f"     ⚠️  MIXED: Some messages share timestamps")
                    
                    # Check time differences
                    if unique_timestamps > 1:
                        sorted_timestamps = sorted(set(timestamps))
                        print(f"     Time span: {sorted_timestamps[0]} to {sorted_timestamps[-1]}")
        
        # Check simulation state
        print(f"\n🎮 SIMULATION STATE ANALYSIS:")
        sim_states = await db.simulation_state.find({}).to_list(10)
        
        for state in sim_states:
            user_id = state.get('user_id', 'N/A')
            is_active = state.get('is_active', False)
            current_day = state.get('current_day', 'N/A')
            time_period = state.get('current_time_period', 'N/A')
            scenario = state.get('scenario_name', state.get('scenario', 'N/A'))
            
            print(f"User: {user_id[:8]}...")
            print(f"  Active: {is_active}")
            print(f"  Time: Day {current_day}, {time_period}")
            print(f"  Scenario: {scenario}")
        
        # Check for any background processing indicators
        print(f"\n🔄 BACKGROUND PROCESSING ANALYSIS:")
        
        # Check observer messages
        observer_count = await db.observer_messages.count_documents({})
        print(f"Observer messages: {observer_count}")
        
        # Check conversation summaries
        summary_count = await db.conversation_summaries.count_documents({})
        print(f"Conversation summaries: {summary_count}")
        
        # Check API usage
        usage_docs = await db.api_usage.find({}).sort("date", -1).limit(3).to_list(3)
        print(f"Recent API usage:")
        for usage in usage_docs:
            date = usage.get('date', 'N/A')
            requests_used = usage.get('requests_used', 0)
            print(f"  {date}: {requests_used} requests")
        
        # Performance insights
        print(f"\n💡 PERFORMANCE INSIGHTS:")
        
        if conv_count > 0:
            # Get latest conversation for detailed analysis
            latest_conv = conversations[0] if conversations else None
            if latest_conv:
                messages = latest_conv.get('messages', [])
                if len(messages) > 5:
                    print(f"⚠️  Large message count ({len(messages)}) may cause bulk display")
                
                # Check creation pattern
                created_at = latest_conv.get('created_at')
                if created_at:
                    print(f"Latest conversation created: {created_at}")
                
                # Check if messages have sequential timestamps
                timestamps = [msg.get('timestamp') for msg in messages if msg.get('timestamp')]
                if timestamps:
                    unique_count = len(set(timestamps))
                    if unique_count == 1:
                        print(f"🚨 CRITICAL: Bulk message creation detected")
                        print(f"   All {len(messages)} messages created simultaneously")
                        print(f"   This is the root cause of '10 messages appearing at once'")
                    else:
                        print(f"✅ Sequential message creation working")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Database analysis error: {e}")

async def main():
    await analyze_conversation_timing()

if __name__ == "__main__":
    asyncio.run(main())