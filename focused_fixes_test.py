#!/usr/bin/env python3
"""
Focused testing for the specific fixes mentioned in the review request:
1. Conversation Generation Fixed - uses ALL agents, generates 3 messages per agent
2. Document PDF Generation Fixed - creates and downloads PDFs without 404 errors  
3. Document Auto-Generation Fixed - proper user_id association
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
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def get_auth_token():
    """Get authentication token for testing"""
    try:
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token'), data.get('user', {}).get('id')
        else:
            print(f"❌ Auth failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None, None

def test_conversation_generation_fix():
    """Test that conversation generation uses ALL available agents and generates correct message count"""
    print("\n🧪 TESTING: Conversation Generation Fix")
    
    # Get auth token
    token, user_id = get_auth_token()
    if not token:
        log_test("Conversation Generation - Authentication", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get all available agents for this user
    try:
        agents_response = requests.get(f"{API_URL}/agents", headers=headers, timeout=10)
        if agents_response.status_code != 200:
            log_test("Conversation Generation - Get Agents", False, f"Status: {agents_response.status_code}")
            return
        
        agents = agents_response.json()
        agent_count = len(agents)
        print(f"📊 Found {agent_count} agents for user")
        
        if agent_count == 0:
            log_test("Conversation Generation - Agent Count", False, "No agents found for user")
            return
        
        log_test("Conversation Generation - Get Agents", True, f"Found {agent_count} agents")
        
    except Exception as e:
        log_test("Conversation Generation - Get Agents", False, f"Error: {e}")
        return
    
    # Start simulation to ensure proper state
    try:
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        if start_response.status_code == 200:
            log_test("Conversation Generation - Start Simulation", True)
        else:
            log_test("Conversation Generation - Start Simulation", False, f"Status: {start_response.status_code}")
    except Exception as e:
        log_test("Conversation Generation - Start Simulation", False, f"Error: {e}")
    
    # Test conversation generation
    try:
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        
        if conv_response.status_code != 200:
            log_test("Conversation Generation - Generate", False, f"Status: {conv_response.status_code} - {conv_response.text}")
            return
        
        conversation_data = conv_response.json()
        log_test("Conversation Generation - Generate", True, "Conversation generated successfully")
        
        # Check if conversation has messages
        if 'messages' in conversation_data:
            messages = conversation_data['messages']
            message_count = len(messages)
            
            # Expected: 3 messages per agent
            expected_messages = agent_count * 3
            
            print(f"📊 Generated {message_count} messages (expected: {expected_messages} for {agent_count} agents)")
            
            if message_count == expected_messages:
                log_test("Conversation Generation - Message Count", True, f"{message_count} messages for {agent_count} agents (3 per agent)")
            else:
                log_test("Conversation Generation - Message Count", False, f"Got {message_count} messages, expected {expected_messages}")
            
            # Check agent distribution
            agent_message_count = {}
            for msg in messages:
                agent_name = msg.get('agent_name', 'Unknown')
                agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
            
            print(f"📊 Message distribution: {agent_message_count}")
            
            # Verify each agent has exactly 3 messages
            all_agents_correct = True
            for agent_name, count in agent_message_count.items():
                if count != 3:
                    all_agents_correct = False
                    break
            
            if all_agents_correct and len(agent_message_count) == agent_count:
                log_test("Conversation Generation - Agent Distribution", True, "All agents have exactly 3 messages")
            else:
                log_test("Conversation Generation - Agent Distribution", False, f"Uneven distribution: {agent_message_count}")
        
        # Check user_id association
        if 'user_id' in conversation_data and conversation_data['user_id'] == user_id:
            log_test("Conversation Generation - User Association", True, "Conversation properly associated with user")
        else:
            log_test("Conversation Generation - User Association", False, f"User ID mismatch or missing")
            
    except Exception as e:
        log_test("Conversation Generation - Generate", False, f"Error: {e}")

def test_document_pdf_generation_fix():
    """Test document creation and PDF generation without 404 errors"""
    print("\n🧪 TESTING: Document PDF Generation Fix")
    
    # Get auth token
    token, user_id = get_auth_token()
    if not token:
        log_test("Document PDF - Authentication", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test document
    test_document = {
        "title": "Test Document for PDF Generation",
        "category": "Protocol",
        "description": "A test document to verify PDF generation functionality",
        "content": "# Test Document\n\nThis is a test document created to verify that PDF generation is working correctly.\n\n## Key Points\n\n- PDF generation should work without 404 errors\n- Document should be properly associated with user\n- Content should be formatted correctly\n\n## Conclusion\n\nThis document serves as a test case for the PDF generation fix.",
        "keywords": ["test", "pdf", "generation"],
        "authors": ["Test System"]
    }
    
    try:
        # Create document
        create_response = requests.post(f"{API_URL}/documents/create", 
                                      headers=headers, 
                                      json=test_document, 
                                      timeout=15)
        
        if create_response.status_code != 200:
            log_test("Document PDF - Create Document", False, f"Status: {create_response.status_code} - {create_response.text}")
            return
        
        doc_data = create_response.json()
        document_id = doc_data.get('id') or doc_data.get('document_id')
        
        if not document_id:
            log_test("Document PDF - Create Document", False, "No document ID returned")
            return
        
        log_test("Document PDF - Create Document", True, f"Document created with ID: {document_id}")
        
        # Test PDF generation
        pdf_response = requests.get(f"{API_URL}/documents/{document_id}/pdf", 
                                   headers=headers, 
                                   timeout=20)
        
        if pdf_response.status_code == 200:
            # Check if response is actually a PDF
            content_type = pdf_response.headers.get('content-type', '')
            content_length = len(pdf_response.content)
            
            if 'pdf' in content_type.lower() or pdf_response.content.startswith(b'%PDF'):
                log_test("Document PDF - Generate PDF", True, f"PDF generated successfully ({content_length} bytes)")
            else:
                log_test("Document PDF - Generate PDF", False, f"Response not a PDF (content-type: {content_type})")
        elif pdf_response.status_code == 404:
            log_test("Document PDF - Generate PDF", False, "404 error - PDF generation endpoint not found or document missing")
        else:
            log_test("Document PDF - Generate PDF", False, f"Status: {pdf_response.status_code} - {pdf_response.text}")
            
    except Exception as e:
        log_test("Document PDF - Generate PDF", False, f"Error: {e}")

def test_document_auto_generation_fix():
    """Test that documents created during conversation generation have proper user_id"""
    print("\n🧪 TESTING: Document Auto-Generation Fix")
    
    # Get auth token
    token, user_id = get_auth_token()
    if not token:
        log_test("Document Auto-Gen - Authentication", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get initial document count
    try:
        initial_docs_response = requests.get(f"{API_URL}/documents", headers=headers, timeout=10)
        if initial_docs_response.status_code == 200:
            initial_docs = initial_docs_response.json()
            initial_count = len(initial_docs)
            log_test("Document Auto-Gen - Get Initial Documents", True, f"Found {initial_count} existing documents")
        else:
            initial_count = 0
            log_test("Document Auto-Gen - Get Initial Documents", False, f"Status: {initial_docs_response.status_code}")
    except Exception as e:
        initial_count = 0
        log_test("Document Auto-Gen - Get Initial Documents", False, f"Error: {e}")
    
    # Start simulation and generate conversation (which should auto-generate documents)
    try:
        # Start simulation
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        if start_response.status_code == 200:
            log_test("Document Auto-Gen - Start Simulation", True)
        else:
            log_test("Document Auto-Gen - Start Simulation", False, f"Status: {start_response.status_code}")
            return
        
        # Generate conversation (this should trigger document auto-generation)
        conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
        
        if conv_response.status_code == 200:
            log_test("Document Auto-Gen - Generate Conversation", True, "Conversation generated")
            
            # Wait a moment for document processing
            time.sleep(2)
            
            # Check for new documents
            final_docs_response = requests.get(f"{API_URL}/documents", headers=headers, timeout=10)
            if final_docs_response.status_code == 200:
                final_docs = final_docs_response.json()
                final_count = len(final_docs)
                
                print(f"📊 Documents before: {initial_count}, after: {final_count}")
                
                if final_count > initial_count:
                    new_docs_count = final_count - initial_count
                    log_test("Document Auto-Gen - Documents Created", True, f"{new_docs_count} new documents created")
                    
                    # Check user_id association for new documents
                    all_properly_associated = True
                    for doc in final_docs[-new_docs_count:]:  # Check the newest documents
                        doc_user_id = doc.get('metadata', {}).get('user_id') or doc.get('user_id')
                        if not doc_user_id or doc_user_id != user_id:
                            all_properly_associated = False
                            break
                    
                    if all_properly_associated:
                        log_test("Document Auto-Gen - User Association", True, "All auto-generated documents properly associated with user")
                    else:
                        log_test("Document Auto-Gen - User Association", False, "Some documents missing proper user_id")
                else:
                    log_test("Document Auto-Gen - Documents Created", False, "No new documents were auto-generated")
            else:
                log_test("Document Auto-Gen - Get Final Documents", False, f"Status: {final_docs_response.status_code}")
        else:
            log_test("Document Auto-Gen - Generate Conversation", False, f"Status: {conv_response.status_code}")
            
    except Exception as e:
        log_test("Document Auto-Gen - Process", False, f"Error: {e}")

def main():
    """Run all focused fix tests"""
    print("🚀 FOCUSED FIXES TESTING")
    print("=" * 50)
    print("Testing specific fixes mentioned in review:")
    print("1. Conversation Generation - ALL agents, 3 messages per agent")
    print("2. Document PDF Generation - No 404 errors")
    print("3. Document Auto-Generation - Proper user_id association")
    print("=" * 50)
    
    # Run focused tests
    test_conversation_generation_fix()
    test_document_pdf_generation_fix()
    test_document_auto_generation_fix()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 FOCUSED FIXES TEST SUMMARY")
    print("=" * 50)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  - {test['name']}: {test['details']}")
    
    print("\n🎯 FOCUS AREAS:")
    if pass_rate >= 80:
        print("✅ Most fixes are working correctly")
    else:
        print("⚠️ Several fixes need attention")
    
    return test_results["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)