#!/usr/bin/env python3
"""
Detailed Enhanced Features Investigation
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate():
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def investigate_document_endpoints():
    """Investigate document-related endpoints"""
    print("🔍 INVESTIGATING DOCUMENT ENDPOINTS")
    print("="*50)
    
    token = authenticate()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test document creation with detailed response
    doc_data = {
        "title": "Test Document",
        "category": "Test",
        "description": "Testing document creation",
        "content": "# Test\nThis is a test document.",
        "keywords": ["test"],
        "authors": ["Test Agent"]
    }
    
    print("📝 Testing document creation...")
    response = requests.post(f"{API_URL}/documents/create", json=doc_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        doc_data = response.json()
        document_id = doc_data.get("id")
        print(f"✅ Document created: {document_id}")
        
        # Test PDF generation
        print("\n📄 Testing PDF generation...")
        pdf_response = requests.get(f"{API_URL}/documents/{document_id}/pdf", headers=headers)
        print(f"PDF Status: {pdf_response.status_code}")
        print(f"PDF Response: {pdf_response.text[:200]}...")
        
        # Test review workflow
        print("\n🗳️  Testing review workflow...")
        review_response = requests.post(f"{API_URL}/documents/{document_id}/request-review", headers=headers)
        print(f"Review Status: {review_response.status_code}")
        print(f"Review Response: {review_response.text}")

def investigate_conversation_generation():
    """Investigate conversation generation details"""
    print("\n🗣️  INVESTIGATING CONVERSATION GENERATION")
    print("="*50)
    
    token = authenticate()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Get agents
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    if agents_response.status_code == 200:
        agents = agents_response.json()
        print(f"📊 Total agents available: {len(agents)}")
        
        # Show agent details
        for i, agent in enumerate(agents[:10]):  # Show first 10
            print(f"  {i+1}. {agent.get('name', 'Unknown')} ({agent.get('archetype', 'Unknown')})")
    
    # Start simulation
    requests.post(f"{API_URL}/simulation/start", headers=headers)
    
    # Generate conversation
    conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    if conv_response.status_code == 200:
        conv_data = conv_response.json()
        messages = conv_data.get("messages", [])
        
        print(f"\n📊 Conversation Analysis:")
        print(f"Total messages: {len(messages)}")
        
        # Detailed message analysis
        agent_counts = {}
        for msg in messages:
            agent_name = msg.get("agent_name", "Unknown")
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
        
        print(f"Unique agents in conversation: {len(agent_counts)}")
        for agent, count in agent_counts.items():
            print(f"  {agent}: {count} messages")
        
        # Check message content quality
        print(f"\nSample messages:")
        for i, msg in enumerate(messages[:3]):
            agent_name = msg.get("agent_name", "Unknown")
            message_text = msg.get("message", "")
            print(f"  {i+1}. {agent_name}: {message_text[:100]}...")

if __name__ == "__main__":
    investigate_document_endpoints()
    investigate_conversation_generation()