#!/usr/bin/env python3
"""
Extended timeout testing for conversation generation to handle the 20+ agents
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def get_auth_token():
    """Get authentication token for testing"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token'), data.get('user', {}).get('id')
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None, None

def test_conversation_generation_detailed():
    """Test conversation generation with extended timeout and detailed analysis"""
    print("🧪 DETAILED CONVERSATION GENERATION TEST")
    print("=" * 50)
    
    # Get auth token
    token, user_id = get_auth_token()
    if not token:
        print("❌ Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get agent count
    try:
        agents_response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if agents_response.status_code == 200:
            agents = agents_response.json()
            agent_count = len(agents)
            print(f"📊 Found {agent_count} agents")
            
            # Show agent details
            for i, agent in enumerate(agents[:5], 1):  # Show first 5
                print(f"  {i}. {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
            if agent_count > 5:
                print(f"  ... and {agent_count - 5} more agents")
        else:
            print(f"❌ Failed to get agents: {agents_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return
    
    # Start simulation
    try:
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        if start_response.status_code == 200:
            print("✅ Simulation started")
        else:
            print(f"⚠️ Simulation start status: {start_response.status_code}")
    except Exception as e:
        print(f"⚠️ Simulation start error: {e}")
    
    # Test conversation generation with extended timeout
    print(f"\n🚀 Generating conversation with {agent_count} agents...")
    print("⏱️ This may take up to 2 minutes with 20+ agents...")
    
    start_time = time.time()
    
    try:
        conv_response = requests.post(f"{API_URL}/conversation/generate", 
                                     headers=headers, 
                                     timeout=120)  # 2 minute timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Request completed in {duration:.1f} seconds")
        
        if conv_response.status_code == 200:
            print("✅ Conversation generation successful!")
            
            conversation_data = conv_response.json()
            
            # Analyze the response
            if 'messages' in conversation_data:
                messages = conversation_data['messages']
                message_count = len(messages)
                expected_messages = agent_count * 3
                
                print(f"📊 CONVERSATION ANALYSIS:")
                print(f"  - Total messages: {message_count}")
                print(f"  - Expected messages: {expected_messages} ({agent_count} agents × 3)")
                print(f"  - Match: {'✅ YES' if message_count == expected_messages else '❌ NO'}")
                
                # Agent distribution analysis
                agent_message_count = {}
                for msg in messages:
                    agent_name = msg.get('agent_name', 'Unknown')
                    agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
                
                print(f"\n📊 AGENT MESSAGE DISTRIBUTION:")
                for agent_name, count in sorted(agent_message_count.items()):
                    status = "✅" if count == 3 else "❌"
                    print(f"  {status} {agent_name}: {count} messages")
                
                # Check if all agents have exactly 3 messages
                all_correct = all(count == 3 for count in agent_message_count.values())
                agent_participation = len(agent_message_count)
                
                print(f"\n📊 SUMMARY:")
                print(f"  - Agents participated: {agent_participation}/{agent_count}")
                print(f"  - All agents have 3 messages: {'✅ YES' if all_correct else '❌ NO'}")
                print(f"  - User ID associated: {'✅ YES' if conversation_data.get('user_id') == user_id else '❌ NO'}")
                
                # Show sample messages
                print(f"\n📝 SAMPLE MESSAGES:")
                for i, msg in enumerate(messages[:3], 1):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_text = msg.get('message', '')[:100]
                    print(f"  {i}. {agent_name}: {message_text}...")
                
                return {
                    "success": True,
                    "agent_count": agent_count,
                    "message_count": message_count,
                    "expected_messages": expected_messages,
                    "correct_count": message_count == expected_messages,
                    "all_agents_correct": all_correct,
                    "duration": duration
                }
            else:
                print("❌ No messages in response")
                return {"success": False, "error": "No messages in response"}
        else:
            print(f"❌ Conversation generation failed: {conv_response.status_code}")
            print(f"Response: {conv_response.text[:500]}")
            return {"success": False, "error": f"Status {conv_response.status_code}"}
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ Request timed out after {duration:.1f} seconds")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Error after {duration:.1f} seconds: {e}")
        return {"success": False, "error": str(e)}

def test_document_auto_generation():
    """Test document auto-generation separately"""
    print("\n🧪 DOCUMENT AUTO-GENERATION TEST")
    print("=" * 50)
    
    # Get auth token
    token, user_id = get_auth_token()
    if not token:
        print("❌ Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check existing documents
    try:
        docs_response = requests.get(f"{API_URL}/documents", headers=headers, timeout=10)
        if docs_response.status_code == 200:
            docs = docs_response.json()
            print(f"📊 Found {len(docs)} existing documents")
            
            # Check user_id association
            properly_associated = 0
            for doc in docs:
                doc_user_id = doc.get('metadata', {}).get('user_id') or doc.get('user_id')
                if doc_user_id == user_id:
                    properly_associated += 1
            
            print(f"✅ {properly_associated}/{len(docs)} documents properly associated with user")
            
            # Show recent documents
            if docs:
                print(f"\n📄 RECENT DOCUMENTS:")
                for i, doc in enumerate(docs[-3:], 1):  # Show last 3
                    title = doc.get('metadata', {}).get('title') or doc.get('title', 'Untitled')
                    doc_user_id = doc.get('metadata', {}).get('user_id') or doc.get('user_id')
                    status = "✅" if doc_user_id == user_id else "❌"
                    print(f"  {i}. {status} {title}")
            
            return {
                "success": True,
                "total_docs": len(docs),
                "properly_associated": properly_associated
            }
        else:
            print(f"❌ Failed to get documents: {docs_response.status_code}")
            return {"success": False, "error": f"Status {docs_response.status_code}"}
    except Exception as e:
        print(f"❌ Error getting documents: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Run detailed tests"""
    print("🎯 DETAILED FIXES ANALYSIS")
    print("=" * 60)
    
    # Test conversation generation
    conv_result = test_conversation_generation_detailed()
    
    # Test document auto-generation
    doc_result = test_document_auto_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DETAILED TEST SUMMARY")
    print("=" * 60)
    
    if conv_result and conv_result.get("success"):
        print("✅ CONVERSATION GENERATION:")
        print(f"  - Used {conv_result['agent_count']} agents")
        print(f"  - Generated {conv_result['message_count']} messages")
        print(f"  - Correct count: {'✅' if conv_result['correct_count'] else '❌'}")
        print(f"  - All agents correct: {'✅' if conv_result['all_agents_correct'] else '❌'}")
        print(f"  - Duration: {conv_result['duration']:.1f}s")
    else:
        print("❌ CONVERSATION GENERATION: Failed")
        if conv_result:
            print(f"  - Error: {conv_result.get('error', 'Unknown')}")
    
    if doc_result and doc_result.get("success"):
        print("\n✅ DOCUMENT AUTO-GENERATION:")
        print(f"  - Total documents: {doc_result['total_docs']}")
        print(f"  - Properly associated: {doc_result['properly_associated']}")
    else:
        print("\n❌ DOCUMENT AUTO-GENERATION: Failed")
        if doc_result:
            print(f"  - Error: {doc_result.get('error', 'Unknown')}")

if __name__ == "__main__":
    main()