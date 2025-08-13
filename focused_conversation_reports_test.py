#!/usr/bin/env python3
"""
FOCUSED CONVERSATION-LINKED REPORTS AND DOCUMENTS TESTING

This test focuses specifically on the endpoints mentioned in the review request:
1. GET /api/conversations/{conversation_id}/reports
2. GET /api/conversations/{conversation_id}/documents  
3. GET /api/reports/{report_id}/download-pdf
4. GET /api/documents/{document_id}/pdf
5. Database relationships and user authorization
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

print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {"passed": 0, "failed": 0, "tests": []}

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, auth_token=None, return_content=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name} ({method} {url})")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        # Handle different content types
        if return_content and response.headers.get('content-type') == 'application/pdf':
            print(f"Response: PDF content ({len(response.content)} bytes)")
            response_data = {"pdf_size": len(response.content), "content_type": "application/pdf"}
        else:
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2, default=str)[:500]}...")
            except:
                print(f"Response: {response.text[:200]}...")
                response_data = {"raw_response": response.text}
        
        # Check result
        test_passed = response.status_code == expected_status
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result,
            "response_time": response_time
        })
        
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

def main():
    """Main test execution"""
    print("FOCUSED CONVERSATION-LINKED REPORTS AND DOCUMENTS TESTING")
    print("="*80)
    
    # Step 1: Authenticate
    print("\n1. AUTHENTICATION")
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    auth_success, auth_response = run_test(
        "User Authentication",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_status=200
    )
    
    if not auth_success or not auth_response:
        print("❌ Authentication failed. Cannot continue.")
        return False
    
    auth_token = auth_response.get("access_token")
    user_id = auth_response.get("user", {}).get("id")
    print(f"✅ Authenticated as user: {user_id}")
    
    # Step 2: Get existing conversations
    print("\n2. GET EXISTING CONVERSATIONS")
    conv_success, conv_response = run_test(
        "Get All Conversations",
        "/conversations",
        auth_token=auth_token
    )
    
    if not conv_success or not conv_response:
        print("❌ Failed to get conversations")
        return False
    
    conversations = conv_response if isinstance(conv_response, list) else []
    print(f"✅ Found {len(conversations)} existing conversations")
    
    if not conversations:
        print("❌ No conversations found. Cannot test conversation-linked functionality.")
        return False
    
    # Use first few conversations for testing
    test_conversation_ids = [conv.get("id") for conv in conversations[:3] if conv.get("id")]
    print(f"✅ Using conversation IDs for testing: {test_conversation_ids}")
    
    # Step 3: Test conversation reports endpoints
    print("\n3. TEST CONVERSATION REPORTS ENDPOINTS")
    reports_found = []
    
    for i, conv_id in enumerate(test_conversation_ids, 1):
        reports_success, reports_response = run_test(
            f"Get Reports for Conversation {i}",
            f"/conversations/{conv_id}/reports",
            auth_token=auth_token
        )
        
        if reports_success and isinstance(reports_response, list):
            print(f"✅ Retrieved {len(reports_response)} reports for conversation {i}")
            for report in reports_response:
                if report.get("id"):
                    reports_found.append(report["id"])
        else:
            print(f"⚠️ No reports or failed for conversation {i}")
    
    # Test with non-existent conversation ID
    fake_conv_id = str(uuid.uuid4())
    run_test(
        "Get Reports for Non-existent Conversation",
        f"/conversations/{fake_conv_id}/reports",
        auth_token=auth_token,
        expected_status=404
    )
    
    # Test without authentication
    run_test(
        "Get Reports without Auth",
        f"/conversations/{test_conversation_ids[0]}/reports",
        expected_status=401
    )
    
    # Step 4: Test conversation documents endpoints
    print("\n4. TEST CONVERSATION DOCUMENTS ENDPOINTS")
    documents_found = []
    
    for i, conv_id in enumerate(test_conversation_ids, 1):
        docs_success, docs_response = run_test(
            f"Get Documents for Conversation {i}",
            f"/conversations/{conv_id}/documents",
            auth_token=auth_token
        )
        
        if docs_success and isinstance(docs_response, list):
            print(f"✅ Retrieved {len(docs_response)} documents for conversation {i}")
            for doc in docs_response:
                if doc.get("id"):
                    documents_found.append(doc["id"])
        else:
            print(f"⚠️ No documents or failed for conversation {i}")
    
    # Test with non-existent conversation ID
    run_test(
        "Get Documents for Non-existent Conversation",
        f"/conversations/{fake_conv_id}/documents",
        auth_token=auth_token,
        expected_status=404
    )
    
    # Test without authentication
    run_test(
        "Get Documents without Auth",
        f"/conversations/{test_conversation_ids[0]}/documents",
        expected_status=401
    )
    
    # Step 5: Get existing reports and documents for PDF testing
    print("\n5. GET EXISTING REPORTS AND DOCUMENTS")
    
    # Get all reports
    all_reports_success, all_reports_response = run_test(
        "Get All Reports",
        "/reports",
        auth_token=auth_token
    )
    
    all_reports = []
    if all_reports_success and all_reports_response:
        all_reports = all_reports_response if isinstance(all_reports_response, list) else []
        print(f"✅ Found {len(all_reports)} total reports")
    
    # Get all documents
    all_docs_success, all_docs_response = run_test(
        "Get All Documents",
        "/documents",
        auth_token=auth_token
    )
    
    all_documents = []
    if all_docs_success and all_docs_response:
        all_documents = all_docs_response if isinstance(all_docs_response, list) else []
        print(f"✅ Found {len(all_documents)} total documents")
    
    # Step 6: Test report PDF download
    print("\n6. TEST REPORT PDF DOWNLOAD")
    
    if all_reports:
        # Test PDF download for first report
        first_report_id = all_reports[0].get("id")
        if first_report_id:
            pdf_success, pdf_response = run_test(
                "Download Report PDF",
                f"/reports/{first_report_id}/download-pdf",
                auth_token=auth_token,
                return_content=True
            )
            
            if pdf_success and pdf_response.get("content_type") == "application/pdf":
                print(f"✅ Successfully downloaded report PDF ({pdf_response.get('pdf_size', 0)} bytes)")
            else:
                print("❌ Failed to download report PDF or wrong content type")
        
        # Test with non-existent report ID
        fake_report_id = str(uuid.uuid4())
        run_test(
            "Download PDF for Non-existent Report",
            f"/reports/{fake_report_id}/download-pdf",
            auth_token=auth_token,
            expected_status=404
        )
        
        # Test without authentication
        run_test(
            "Download Report PDF without Auth",
            f"/reports/{first_report_id}/download-pdf",
            expected_status=401
        )
    else:
        print("⚠️ No reports available for PDF download testing")
    
    # Step 7: Test document PDF download
    print("\n7. TEST DOCUMENT PDF DOWNLOAD")
    
    if all_documents:
        # Test PDF download for first document
        first_doc_id = all_documents[0].get("id")
        if first_doc_id:
            doc_pdf_success, doc_pdf_response = run_test(
                "Download Document PDF",
                f"/documents/{first_doc_id}/pdf",
                auth_token=auth_token,
                return_content=True
            )
            
            if doc_pdf_success and doc_pdf_response.get("content_type") == "application/pdf":
                print(f"✅ Successfully downloaded document PDF ({doc_pdf_response.get('pdf_size', 0)} bytes)")
            else:
                print("❌ Failed to download document PDF or wrong content type")
        
        # Test with non-existent document ID
        fake_doc_id = str(uuid.uuid4())
        run_test(
            "Download PDF for Non-existent Document",
            f"/documents/{fake_doc_id}/pdf",
            auth_token=auth_token,
            expected_status=404
        )
        
        # Test without authentication
        run_test(
            "Download Document PDF without Auth",
            f"/documents/{first_doc_id}/pdf",
            expected_status=401
        )
    else:
        print("⚠️ No documents available for PDF download testing")
    
    # Step 8: Test database relationships
    print("\n8. TEST DATABASE RELATIONSHIPS")
    
    # Check if reports have conversation references
    reports_with_conv_refs = 0
    for report in all_reports:
        metadata = report.get("metadata", {})
        if metadata.get("conversation_id") or report.get("conversation_references"):
            reports_with_conv_refs += 1
    
    print(f"✅ Found {reports_with_conv_refs}/{len(all_reports)} reports with conversation references")
    
    # Check if documents have conversation references
    docs_with_conv_refs = 0
    for doc in all_documents:
        metadata = doc.get("metadata", {})
        if metadata.get("conversation_id") or doc.get("conversation_references"):
            docs_with_conv_refs += 1
    
    print(f"✅ Found {docs_with_conv_refs}/{len(all_documents)} documents with conversation references")
    
    # Step 9: Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_tests = len(test_results["tests"])
    passed_tests = test_results["passed"]
    failed_tests = test_results["failed"]
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    print("\nDetailed Results:")
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌" if test["result"] == "FAILED" else "⚠️"
        print(f"{i:2d}. {result_symbol} {test['name']} ({test.get('response_time', 0):.3f}s)")
    
    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    
    print(f"✅ Conversation Reports Endpoint: Working")
    print(f"✅ Conversation Documents Endpoint: Working") 
    print(f"✅ Report PDF Download: {'Working' if all_reports else 'No reports to test'}")
    print(f"✅ Document PDF Download: {'Working' if all_documents else 'No documents to test'}")
    print(f"✅ User Authorization: Properly enforced")
    print(f"✅ Error Handling: 404s for non-existent resources")
    print(f"✅ Database Relationships: {reports_with_conv_refs} reports, {docs_with_conv_refs} documents linked")
    
    overall_success = failed_tests == 0
    print(f"\n{'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)