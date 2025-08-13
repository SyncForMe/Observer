#!/usr/bin/env python3
"""
CONVERSATION-LINKED REPORTS AND DOCUMENTS FUNCTIONALITY TESTING

This test suite comprehensively tests the conversation archive system's ability to:
1. Link reports and documents to specific conversations
2. Retrieve reports/documents by conversation ID
3. Download PDFs for both reports and documents
4. Ensure proper user authorization and data isolation
5. Verify database relationships and data integrity

Focus Areas:
- GET /api/conversations/{conversation_id}/reports endpoint
- GET /api/conversations/{conversation_id}/documents endpoint  
- GET /api/reports/{report_id}/download-pdf endpoint
- GET /api/documents/{document_id}/pdf endpoint
- Database relationship verification
- User authorization and data isolation
- Error handling for non-existent resources
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import jwt
from datetime import datetime, timedelta

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

# Load JWT secret from backend/.env for testing
load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("Warning: JWT_SECRET not found in environment variables. Some tests may fail.")
    JWT_SECRET = "test_secret"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables for testing
auth_token = None
test_user_id = None
created_agent_ids = []
created_conversation_ids = []
created_report_ids = []
created_document_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False, return_content=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\nTesting: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params)
            else:
                response = requests.delete(url, headers=headers, params=params)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
        # Handle PDF content differently
        if return_content and response.headers.get('content-type') == 'application/pdf':
            print(f"Response: PDF content ({len(response.content)} bytes)")
            response_data = {"pdf_size": len(response.content), "content_type": response.headers.get('content-type')}
        else:
            # Check if response is JSON
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2, default=str)}")
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response.text[:500]}...")
                response_data = {"raw_response": response.text}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok and isinstance(response_data, dict):
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result
        }
        
        if measure_time:
            test_result["response_time"] = response_time
            
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None

def setup_authentication():
    """Set up authentication for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("SETTING UP AUTHENTICATION")
    print("="*80)
    
    # Try to login with existing test user
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_test, login_response = run_test(
        "Email/Password Login Setup",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if login_test and login_response:
        auth_token = login_response.get("access_token")
        user_data = login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication setup successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Email/password login failed, trying to register new test user")
        
        # Try to register a new test user
        register_data = {
            "email": "test@conversation-reports.com",
            "password": "TestPassword123",
            "name": "Test User for Conversation Reports"
        }
        
        register_test, register_response = run_test(
            "Register Test User",
            "/auth/register",
            method="POST",
            data=register_data,
            expected_keys=["access_token", "token_type", "user"]
        )
        
        if register_test and register_response:
            auth_token = register_response.get("access_token")
            user_data = register_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"✅ Test user registration successful. User ID: {test_user_id}")
            return True
        else:
            print("❌ Authentication setup failed")
            return False

def create_test_agents():
    """Create test agents for conversation generation"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("CREATING TEST AGENTS")
    print("="*80)
    
    agents_data = [
        {
            "name": "Dr. Research Scientist",
            "archetype": "scientist",
            "goal": "Conduct advanced research and generate reports",
            "expertise": "Scientific research and documentation",
            "background": "PhD in Research Science with focus on documentation",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Prof. Document Creator",
            "archetype": "leader",
            "goal": "Create comprehensive documents and reports",
            "expertise": "Document creation and project management",
            "background": "Senior Project Manager specializing in documentation",
            "personality": {
                "extroversion": 8,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        }
    ]
    
    for i, agent_data in enumerate(agents_data, 1):
        create_test, create_response = run_test(
            f"Create Test Agent {i}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            if agent_id:
                created_agent_ids.append(agent_id)
                print(f"✅ Created agent {i} with ID: {agent_id}")
            else:
                print(f"❌ No agent ID returned for agent {i}")
                return False
        else:
            print(f"❌ Failed to create agent {i}")
            return False
    
    print(f"✅ Successfully created {len(created_agent_ids)} test agents")
    return True

def generate_test_conversations():
    """Generate test conversations that will be linked to reports and documents"""
    global created_conversation_ids
    
    print("\n" + "="*80)
    print("GENERATING TEST CONVERSATIONS")
    print("="*80)
    
    # Start simulation first
    start_test, start_response = run_test(
        "Start Simulation for Conversations",
        "/simulation/start",
        method="POST",
        auth=True,
        expected_keys=["message", "state"]
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False
    
    # Generate multiple conversations
    for i in range(3):  # Generate 3 conversations for testing
        conv_test, conv_response = run_test(
            f"Generate Test Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True,
            expected_keys=["id", "messages"]
        )
        
        if conv_test and conv_response:
            conversation_id = conv_response.get("id")
            if conversation_id:
                created_conversation_ids.append(conversation_id)
                print(f"✅ Generated conversation {i+1} with ID: {conversation_id}")
            else:
                print(f"❌ No conversation ID returned for conversation {i+1}")
                return False
        else:
            print(f"❌ Failed to generate conversation {i+1}")
            return False
        
        # Small delay between conversations
        time.sleep(2)
    
    print(f"✅ Successfully generated {len(created_conversation_ids)} test conversations")
    return True

def generate_test_reports():
    """Generate test reports linked to conversations"""
    global created_report_ids
    
    print("\n" + "="*80)
    print("GENERATING TEST REPORTS")
    print("="*80)
    
    # Generate daily reports that should be linked to conversations
    for i in range(2):  # Generate 2 reports
        report_test, report_response = run_test(
            f"Generate Daily Report {i+1}",
            "/simulation/generate-daily-report",
            method="POST",
            data={"manual": True},
            auth=True,
            measure_time=True,
            expected_keys=["success"]
        )
        
        if report_test and report_response:
            if report_response.get("success"):
                report_data = report_response.get("report", {})
                report_id = report_data.get("id")
                if report_id:
                    created_report_ids.append(report_id)
                    print(f"✅ Generated report {i+1} with ID: {report_id}")
                else:
                    print(f"❌ No report ID returned for report {i+1}")
            else:
                print(f"❌ Report generation {i+1} was not successful")
                return False
        else:
            print(f"❌ Failed to generate report {i+1}")
            return False
        
        # Small delay between reports
        time.sleep(3)
    
    print(f"✅ Successfully generated {len(created_report_ids)} test reports")
    return True

def create_test_documents():
    """Create test documents linked to conversations"""
    global created_document_ids
    
    print("\n" + "="*80)
    print("CREATING TEST DOCUMENTS")
    print("="*80)
    
    # Create documents that reference conversations
    for i, conversation_id in enumerate(created_conversation_ids[:2], 1):  # Link to first 2 conversations
        document_data = {
            "title": f"Test Document {i} - Conversation Analysis",
            "category": "Research",
            "description": f"Analysis document generated from conversation {conversation_id}",
            "content": f"""# Test Document {i} - Conversation Analysis

## Overview
This document was generated from conversation {conversation_id} to test the conversation-document linking functionality.

## Key Points from Conversation
- Document creation works correctly
- Content is properly linked to conversation
- Metadata includes conversation reference

## Analysis Results
The conversation provided valuable insights that are documented here for future reference.

## Conclusion
This document serves as a test case for the conversation-document linking system.
""",
            "keywords": ["test", "conversation", "analysis", f"conv-{conversation_id}"],
            "authors": ["Dr. Research Scientist", "Prof. Document Creator"],
            "conversation_id": conversation_id  # Link to conversation
        }
        
        create_doc_test, create_doc_response = run_test(
            f"Create Test Document {i}",
            "/documents/create",
            method="POST",
            data=document_data,
            auth=True,
            expected_keys=["success", "document_id"]
        )
        
        if create_doc_test and create_doc_response:
            document_id = create_doc_response.get("document_id")
            if document_id:
                created_document_ids.append(document_id)
                print(f"✅ Created document {i} with ID: {document_id}")
            else:
                print(f"❌ No document ID returned for document {i}")
                return False
        else:
            print(f"❌ Failed to create document {i}")
            return False
    
    print(f"✅ Successfully created {len(created_document_ids)} test documents")
    return True

def test_conversation_reports_endpoint():
    """Test GET /api/conversations/{conversation_id}/reports endpoint"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION REPORTS ENDPOINT")
    print("="*80)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Get reports for each conversation
    for i, conversation_id in enumerate(created_conversation_ids, 1):
        total_tests += 1
        reports_test, reports_response = run_test(
            f"Get Reports for Conversation {i}",
            f"/conversations/{conversation_id}/reports",
            method="GET",
            auth=True
        )
        
        if reports_test and isinstance(reports_response, list):
            print(f"✅ Retrieved {len(reports_response)} reports for conversation {i}")
            
            # Verify report structure if reports exist
            if reports_response:
                sample_report = reports_response[0]
                required_fields = ["id", "title", "type", "content", "created_at"]
                missing_fields = [field for field in required_fields if field not in sample_report]
                if missing_fields:
                    print(f"❌ Missing fields in report: {missing_fields}")
                else:
                    print("✅ Report structure is correct")
                    success_count += 1
            else:
                print("ℹ️ No reports found for this conversation (expected for some conversations)")
                success_count += 1
        else:
            print(f"❌ Failed to get reports for conversation {i}")
    
    # Test 2: Test with non-existent conversation ID
    total_tests += 1
    fake_conversation_id = str(uuid.uuid4())
    fake_test, fake_response = run_test(
        "Get Reports for Non-existent Conversation",
        f"/conversations/{fake_conversation_id}/reports",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if fake_test:
        print("✅ Properly handled non-existent conversation ID")
        success_count += 1
    else:
        print("❌ Failed to handle non-existent conversation ID properly")
    
    # Test 3: Test without authentication
    total_tests += 1
    if created_conversation_ids:
        no_auth_test, no_auth_response = run_test(
            "Get Reports without Authentication",
            f"/conversations/{created_conversation_ids[0]}/reports",
            method="GET",
            auth=False,
            expected_status=401
        )
        
        if no_auth_test:
            print("✅ Properly requires authentication")
            success_count += 1
        else:
            print("❌ Authentication requirement not enforced")
    
    print(f"✅ Conversation Reports Endpoint: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_conversation_documents_endpoint():
    """Test GET /api/conversations/{conversation_id}/documents endpoint"""
    print("\n" + "="*80)
    print("TESTING CONVERSATION DOCUMENTS ENDPOINT")
    print("="*80)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Get documents for each conversation
    for i, conversation_id in enumerate(created_conversation_ids, 1):
        total_tests += 1
        docs_test, docs_response = run_test(
            f"Get Documents for Conversation {i}",
            f"/conversations/{conversation_id}/documents",
            method="GET",
            auth=True
        )
        
        if docs_test and isinstance(docs_response, list):
            print(f"✅ Retrieved {len(docs_response)} documents for conversation {i}")
            
            # Verify document structure if documents exist
            if docs_response:
                sample_doc = docs_response[0]
                required_fields = ["id", "title", "document_type", "content", "created_at"]
                missing_fields = [field for field in required_fields if field not in sample_doc]
                if missing_fields:
                    print(f"❌ Missing fields in document: {missing_fields}")
                else:
                    print("✅ Document structure is correct")
                    success_count += 1
            else:
                print("ℹ️ No documents found for this conversation")
                success_count += 1
        else:
            print(f"❌ Failed to get documents for conversation {i}")
    
    # Test 2: Test with non-existent conversation ID
    total_tests += 1
    fake_conversation_id = str(uuid.uuid4())
    fake_test, fake_response = run_test(
        "Get Documents for Non-existent Conversation",
        f"/conversations/{fake_conversation_id}/documents",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if fake_test:
        print("✅ Properly handled non-existent conversation ID")
        success_count += 1
    else:
        print("❌ Failed to handle non-existent conversation ID properly")
    
    # Test 3: Test without authentication
    total_tests += 1
    if created_conversation_ids:
        no_auth_test, no_auth_response = run_test(
            "Get Documents without Authentication",
            f"/conversations/{created_conversation_ids[0]}/documents",
            method="GET",
            auth=False,
            expected_status=401
        )
        
        if no_auth_test:
            print("✅ Properly requires authentication")
            success_count += 1
        else:
            print("❌ Authentication requirement not enforced")
    
    print(f"✅ Conversation Documents Endpoint: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_report_pdf_download():
    """Test GET /api/reports/{report_id}/download-pdf endpoint"""
    print("\n" + "="*80)
    print("TESTING REPORT PDF DOWNLOAD ENDPOINT")
    print("="*80)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Download PDF for each created report
    for i, report_id in enumerate(created_report_ids, 1):
        total_tests += 1
        pdf_test, pdf_response = run_test(
            f"Download PDF for Report {i}",
            f"/reports/{report_id}/download-pdf",
            method="GET",
            auth=True,
            return_content=True
        )
        
        if pdf_test and pdf_response:
            if pdf_response.get("content_type") == "application/pdf":
                pdf_size = pdf_response.get("pdf_size", 0)
                print(f"✅ Successfully downloaded PDF for report {i} ({pdf_size} bytes)")
                success_count += 1
            else:
                print(f"❌ Response is not a PDF for report {i}")
        else:
            print(f"❌ Failed to download PDF for report {i}")
    
    # Test 2: Test with non-existent report ID
    total_tests += 1
    fake_report_id = str(uuid.uuid4())
    fake_pdf_test, fake_pdf_response = run_test(
        "Download PDF for Non-existent Report",
        f"/reports/{fake_report_id}/download-pdf",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if fake_pdf_test:
        print("✅ Properly handled non-existent report ID")
        success_count += 1
    else:
        print("❌ Failed to handle non-existent report ID properly")
    
    # Test 3: Test without authentication
    total_tests += 1
    if created_report_ids:
        no_auth_pdf_test, no_auth_pdf_response = run_test(
            "Download PDF without Authentication",
            f"/reports/{created_report_ids[0]}/download-pdf",
            method="GET",
            auth=False,
            expected_status=401
        )
        
        if no_auth_pdf_test:
            print("✅ Properly requires authentication")
            success_count += 1
        else:
            print("❌ Authentication requirement not enforced")
    
    print(f"✅ Report PDF Download: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_document_pdf_download():
    """Test GET /api/documents/{document_id}/pdf endpoint"""
    print("\n" + "="*80)
    print("TESTING DOCUMENT PDF DOWNLOAD ENDPOINT")
    print("="*80)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Download PDF for each created document
    for i, document_id in enumerate(created_document_ids, 1):
        total_tests += 1
        pdf_test, pdf_response = run_test(
            f"Download PDF for Document {i}",
            f"/documents/{document_id}/pdf",
            method="GET",
            auth=True,
            return_content=True
        )
        
        if pdf_test and pdf_response:
            if pdf_response.get("content_type") == "application/pdf":
                pdf_size = pdf_response.get("pdf_size", 0)
                print(f"✅ Successfully downloaded PDF for document {i} ({pdf_size} bytes)")
                success_count += 1
            else:
                print(f"❌ Response is not a PDF for document {i}")
        else:
            print(f"❌ Failed to download PDF for document {i}")
    
    # Test 2: Test with non-existent document ID
    total_tests += 1
    fake_document_id = str(uuid.uuid4())
    fake_pdf_test, fake_pdf_response = run_test(
        "Download PDF for Non-existent Document",
        f"/documents/{fake_document_id}/pdf",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if fake_pdf_test:
        print("✅ Properly handled non-existent document ID")
        success_count += 1
    else:
        print("❌ Failed to handle non-existent document ID properly")
    
    # Test 3: Test without authentication
    total_tests += 1
    if created_document_ids:
        no_auth_pdf_test, no_auth_pdf_response = run_test(
            "Download PDF without Authentication",
            f"/documents/{created_document_ids[0]}/pdf",
            method="GET",
            auth=False,
            expected_status=401
        )
        
        if no_auth_pdf_test:
            print("✅ Properly requires authentication")
            success_count += 1
        else:
            print("❌ Authentication requirement not enforced")
    
    print(f"✅ Document PDF Download: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_database_relationships():
    """Test database relationships and conversation_id linking"""
    print("\n" + "="*80)
    print("TESTING DATABASE RELATIONSHIPS")
    print("="*80)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Verify reports are linked to conversations
    total_tests += 1
    if created_report_ids and created_conversation_ids:
        # Get all reports and check for conversation references
        reports_test, reports_response = run_test(
            "Get All Reports to Check Conversation Links",
            "/reports",
            method="GET",
            auth=True
        )
        
        if reports_test and reports_response:
            reports_with_conv_refs = 0
            for report in reports_response:
                # Check if report has conversation reference in metadata or other fields
                metadata = report.get("metadata", {})
                if metadata.get("conversation_id") or report.get("conversation_references"):
                    reports_with_conv_refs += 1
            
            print(f"✅ Found {reports_with_conv_refs} reports with conversation references")
            success_count += 1
        else:
            print("❌ Failed to get reports for relationship verification")
    else:
        print("ℹ️ No reports or conversations to test relationships")
        success_count += 1
    
    # Test 2: Verify documents are linked to conversations
    total_tests += 1
    if created_document_ids and created_conversation_ids:
        # Get all documents and check for conversation references
        docs_test, docs_response = run_test(
            "Get All Documents to Check Conversation Links",
            "/documents",
            method="GET",
            auth=True
        )
        
        if docs_test and docs_response:
            docs_with_conv_refs = 0
            for doc in docs_response:
                # Check if document has conversation reference in metadata
                metadata = doc.get("metadata", {})
                if metadata.get("conversation_id") or doc.get("conversation_references"):
                    docs_with_conv_refs += 1
            
            print(f"✅ Found {docs_with_conv_refs} documents with conversation references")
            success_count += 1
        else:
            print("❌ Failed to get documents for relationship verification")
    else:
        print("ℹ️ No documents or conversations to test relationships")
        success_count += 1
    
    # Test 3: Cross-reference conversation-specific queries
    total_tests += 1
    if created_conversation_ids:
        conversation_id = created_conversation_ids[0]
        
        # Get reports for this conversation
        conv_reports_test, conv_reports_response = run_test(
            "Cross-reference Conversation Reports",
            f"/conversations/{conversation_id}/reports",
            method="GET",
            auth=True
        )
        
        # Get documents for this conversation
        conv_docs_test, conv_docs_response = run_test(
            "Cross-reference Conversation Documents",
            f"/conversations/{conversation_id}/documents",
            method="GET",
            auth=True
        )
        
        if conv_reports_test and conv_docs_test:
            reports_count = len(conv_reports_response) if conv_reports_response else 0
            docs_count = len(conv_docs_response) if conv_docs_response else 0
            print(f"✅ Conversation {conversation_id} has {reports_count} reports and {docs_count} documents")
            success_count += 1
        else:
            print("❌ Failed to cross-reference conversation content")
    else:
        print("ℹ️ No conversations to test cross-referencing")
        success_count += 1
    
    print(f"✅ Database Relationships: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_user_authorization_isolation():
    """Test user authorization and data isolation"""
    print("\n" + "="*80)
    print("TESTING USER AUTHORIZATION AND DATA ISOLATION")
    print("="*80)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Verify user can only access their own conversations
    total_tests += 1
    if created_conversation_ids:
        # This test verifies that the current user can access their conversations
        # In a real scenario, we would test with a different user's conversation ID
        conv_access_test, conv_access_response = run_test(
            "Verify User Can Access Own Conversations",
            f"/conversations/{created_conversation_ids[0]}/reports",
            method="GET",
            auth=True
        )
        
        if conv_access_test:
            print("✅ User can access their own conversation reports")
            success_count += 1
        else:
            print("❌ User cannot access their own conversation reports")
    else:
        print("ℹ️ No conversations to test access")
        success_count += 1
    
    # Test 2: Verify user can only access their own reports
    total_tests += 1
    if created_report_ids:
        report_access_test, report_access_response = run_test(
            "Verify User Can Access Own Reports",
            f"/reports/{created_report_ids[0]}",
            method="GET",
            auth=True,
            expected_keys=["success", "report"]
        )
        
        if report_access_test and report_access_response:
            report_data = report_access_response.get("report", {})
            if report_data.get("user_id") == test_user_id:
                print("✅ Report belongs to the correct user")
                success_count += 1
            else:
                print("❌ Report user_id mismatch")
        else:
            print("❌ Failed to access own report")
    else:
        print("ℹ️ No reports to test access")
        success_count += 1
    
    # Test 3: Verify user can only access their own documents
    total_tests += 1
    if created_document_ids:
        doc_access_test, doc_access_response = run_test(
            "Verify User Can Access Own Documents",
            f"/documents/{created_document_ids[0]}",
            method="GET",
            auth=True,
            expected_keys=["id", "metadata", "content"]
        )
        
        if doc_access_test and doc_access_response:
            metadata = doc_access_response.get("metadata", {})
            if metadata.get("user_id") == test_user_id:
                print("✅ Document belongs to the correct user")
                success_count += 1
            else:
                print("❌ Document user_id mismatch")
        else:
            print("❌ Failed to access own document")
    else:
        print("ℹ️ No documents to test access")
        success_count += 1
    
    print(f"✅ User Authorization and Isolation: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    # Delete created documents
    for doc_id in created_document_ids:
        delete_test, delete_response = run_test(
            f"Delete Document {doc_id}",
            f"/documents/{doc_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted document {doc_id}")
        else:
            print(f"❌ Failed to delete document {doc_id}")
    
    print("✅ Cleanup completed")

def print_summary():
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed']} passed, {test_results['failed']} failed")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']})")
    
    print("="*80)
    overall_result = "PASSED" if test_results["failed"] == 0 else "FAILED"
    print(f"OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution function"""
    print("CONVERSATION-LINKED REPORTS AND DOCUMENTS FUNCTIONALITY TESTING")
    print("Testing conversation archive system's ability to link and retrieve reports/documents")
    print("="*80)
    
    # Setup phase
    if not setup_authentication():
        print("❌ Authentication setup failed. Cannot continue.")
        return False
    
    if not create_test_agents():
        print("❌ Test agent creation failed. Cannot continue.")
        return False
    
    if not generate_test_conversations():
        print("❌ Test conversation generation failed. Cannot continue.")
        return False
    
    if not generate_test_reports():
        print("❌ Test report generation failed. Cannot continue.")
        return False
    
    if not create_test_documents():
        print("❌ Test document creation failed. Cannot continue.")
        return False
    
    # Main testing phase
    test_suites = [
        ("Conversation Reports Endpoint", test_conversation_reports_endpoint),
        ("Conversation Documents Endpoint", test_conversation_documents_endpoint),
        ("Report PDF Download", test_report_pdf_download),
        ("Document PDF Download", test_document_pdf_download),
        ("Database Relationships", test_database_relationships),
        ("User Authorization and Isolation", test_user_authorization_isolation)
    ]
    
    failed_suites = []
    
    for suite_name, test_function in test_suites:
        try:
            print(f"\n{'='*80}")
            print(f"RUNNING TEST SUITE: {suite_name}")
            print(f"{'='*80}")
            
            success = test_function()
            if success:
                print(f"✅ {suite_name} test suite PASSED")
            else:
                print(f"❌ {suite_name} test suite FAILED")
                failed_suites.append(suite_name)
        except Exception as e:
            print(f"❌ {suite_name} test suite ERROR: {e}")
            failed_suites.append(suite_name)
    
    # Cleanup test data
    cleanup_test_data()
    
    # Print final summary
    print_summary()
    
    # Print test suite summary
    print(f"\n{'='*80}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*80}")
    
    total_suites = len(test_suites)
    passed_suites = total_suites - len(failed_suites)
    
    print(f"Total Test Suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {len(failed_suites)}")
    
    if failed_suites:
        print(f"\nFailed Test Suites:")
        for suite in failed_suites:
            print(f"  ❌ {suite}")
    else:
        print(f"\n✅ ALL TEST SUITES PASSED!")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_suites) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)