#!/usr/bin/env python3
"""
Focused Enhanced Features Test
Tests the specific enhanced features mentioned in the review request
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

# Global variables
auth_token = None
test_user_id = None
test_agents = []
test_documents = []

def authenticate():
    """Get authentication token"""
    global auth_token, test_user_id
    
    print("🔐 Authenticating...")
    response = requests.post(f"{API_URL}/auth/test-login")
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get("access_token")
        user_data = data.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authenticated as user: {test_user_id}")
        return True
    
    print(f"❌ Authentication failed: {response.status_code}")
    return False

def get_headers():
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

def test_enhanced_conversation_generation():
    """Test enhanced conversation generation features"""
    print("\n🗣️  TESTING ENHANCED CONVERSATION GENERATION")
    print("="*60)
    
    # Get current agents
    response = requests.get(f"{API_URL}/agents", headers=get_headers())
    if response.status_code == 200:
        agents = response.json()
        print(f"📊 Available agents: {len(agents)}")
        
        # Start simulation
        start_response = requests.post(f"{API_URL}/simulation/start", headers=get_headers())
        if start_response.status_code != 200:
            print(f"❌ Failed to start simulation: {start_response.status_code}")
            return False
        
        # Generate conversation
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=get_headers())
        if conv_response.status_code == 200:
            conv_data = conv_response.json()
            messages = conv_data.get("messages", [])
            
            print(f"✅ Conversation generated with {len(messages)} messages")
            
            # Count messages per agent
            agent_counts = {}
            for msg in messages:
                agent_name = msg.get("agent_name", "Unknown")
                agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
            
            print(f"📊 Agents participating: {len(agent_counts)}")
            print(f"📊 Messages per agent: {dict(agent_counts)}")
            
            # Check if using all available agents
            using_all_agents = len(agent_counts) == len(agents)
            print(f"✅ Using ALL agents: {'Yes' if using_all_agents else 'No'}")
            
            # Check for 3 messages per agent
            three_per_agent = all(count == 3 for count in agent_counts.values())
            print(f"✅ 3 messages per agent: {'Yes' if three_per_agent else 'No'}")
            
            return True
        else:
            print(f"❌ Conversation generation failed: {conv_response.status_code}")
            return False
    else:
        print(f"❌ Failed to get agents: {response.status_code}")
        return False

def test_document_pdf_generation():
    """Test document PDF generation"""
    print("\n📄 TESTING DOCUMENT PDF GENERATION")
    print("="*60)
    
    # Create a test document first
    doc_data = {
        "title": "Test Document for PDF Generation",
        "category": "Test",
        "description": "Testing PDF generation capabilities",
        "content": """# Test Document

## Introduction
This is a test document to verify PDF generation.

## Key Features
- Professional formatting
- Proper headers and styling
- Support for markdown content

## Conclusion
PDF generation test document.""",
        "keywords": ["test", "pdf", "document"],
        "authors": ["Test Agent"]
    }
    
    # Create document
    create_response = requests.post(f"{API_URL}/documents/create", json=doc_data, headers=get_headers())
    if create_response.status_code == 200:
        doc_response = create_response.json()
        document_id = doc_response.get("id")
        print(f"✅ Document created with ID: {document_id}")
        
        # Test single PDF generation
        pdf_response = requests.get(f"{API_URL}/documents/{document_id}/pdf", headers=get_headers())
        if pdf_response.status_code == 200:
            print(f"✅ Single PDF generated successfully ({len(pdf_response.content)} bytes)")
            
            # Test bulk PDF generation
            bulk_data = {"document_ids": [document_id]}
            bulk_response = requests.post(f"{API_URL}/documents/bulk-pdf", json=bulk_data, headers=get_headers())
            if bulk_response.status_code == 200:
                print(f"✅ Bulk PDF generated successfully ({len(bulk_response.content)} bytes)")
                return True
            else:
                print(f"❌ Bulk PDF generation failed: {bulk_response.status_code}")
                return False
        else:
            print(f"❌ Single PDF generation failed: {pdf_response.status_code}")
            return False
    else:
        print(f"❌ Document creation failed: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False

def test_document_review_workflow():
    """Test document review workflow"""
    print("\n🗳️  TESTING DOCUMENT REVIEW WORKFLOW")
    print("="*60)
    
    # Get existing documents
    docs_response = requests.get(f"{API_URL}/documents", headers=get_headers())
    if docs_response.status_code == 200:
        documents = docs_response.json()
        if documents:
            document_id = documents[0].get("id")
            print(f"📄 Testing with document ID: {document_id}")
            
            # Request review
            review_response = requests.post(f"{API_URL}/documents/{document_id}/request-review", headers=get_headers())
            if review_response.status_code == 200:
                print("✅ Document review requested successfully")
                
                # Vote on document
                vote_data = {
                    "vote": "approve",
                    "comment": "Excellent document with comprehensive analysis"
                }
                vote_response = requests.post(f"{API_URL}/documents/{document_id}/vote", json=vote_data, headers=get_headers())
                if vote_response.status_code == 200:
                    print("✅ Vote submitted successfully")
                    
                    # Get review status
                    status_response = requests.get(f"{API_URL}/documents/{document_id}/review-status", headers=get_headers())
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"✅ Review status retrieved: {status_data.get('status', 'unknown')}")
                        return True
                    else:
                        print(f"❌ Failed to get review status: {status_response.status_code}")
                else:
                    print(f"❌ Vote submission failed: {vote_response.status_code}")
            else:
                print(f"❌ Review request failed: {review_response.status_code}")
        else:
            print("❌ No documents available for testing")
    else:
        print(f"❌ Failed to get documents: {docs_response.status_code}")
    
    return False

def test_memory_architecture():
    """Test memory architecture and conversation summaries"""
    print("\n🧠 TESTING MEMORY ARCHITECTURE")
    print("="*60)
    
    # Generate multiple conversations to test memory
    for i in range(2):
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=get_headers())
        if conv_response.status_code == 200:
            print(f"✅ Generated conversation round {i+1}")
        else:
            print(f"❌ Failed to generate conversation {i+1}")
    
    # Test conversation summaries
    summaries_response = requests.get(f"{API_URL}/internal/conversation-summaries", headers=get_headers())
    if summaries_response.status_code == 200:
        summaries = summaries_response.json()
        print(f"✅ Retrieved {len(summaries)} conversation summaries")
        
        if summaries:
            latest = summaries[0]
            summary_text = latest.get("summary", "")
            print(f"📝 Latest summary preview: {summary_text[:200]}...")
            return True
    else:
        print(f"❌ Failed to get conversation summaries: {summaries_response.status_code}")
    
    return False

def main():
    """Main test execution"""
    print("🚀 FOCUSED ENHANCED FEATURES TEST")
    print("="*60)
    
    if not authenticate():
        return
    
    results = {
        "Enhanced Conversation Generation": test_enhanced_conversation_generation(),
        "Document PDF Generation": test_document_pdf_generation(),
        "Document Review Workflow": test_document_review_workflow(),
        "Memory Architecture": test_memory_architecture()
    }
    
    print("\n" + "="*60)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🏆 ALL ENHANCED FEATURES WORKING!")
    else:
        print("⚠️  Some enhanced features need attention")

if __name__ == "__main__":
    main()