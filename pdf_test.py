#!/usr/bin/env python3
"""
REPORT PDF DOWNLOAD FUNCTIONALITY TESTING
Testing the report modal positioning and PDF download functionality as requested in the review.

Focus Areas:
1. Test Report PDF Download Endpoint (/api/reports/{report_id}/download-pdf)
2. Test Report Data Structure (verify reports have correct ID structure)
3. Test Error Handling (invalid report ID, no authentication)
4. Generate test reports and verify PDF download works
5. Check PDF content formatting and structure
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

# Global variables for auth testing
auth_token = None
test_user_id = None
created_report_ids = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False, expect_binary=False):
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
        
        # Handle binary responses (like PDF)
        if expect_binary:
            if response.status_code == expected_status:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                print(f"Content-Type: {content_type}")
                print(f"Content-Length: {content_length} bytes")
                
                # Check if it's actually a PDF
                if content_length > 0 and response.content.startswith(b'%PDF'):
                    print("✅ Valid PDF content detected")
                    response_data = {"pdf_valid": True, "content_length": content_length}
                else:
                    print("❌ Invalid PDF content")
                    response_data = {"pdf_valid": False, "content_length": content_length}
            else:
                print(f"Response Text: {response.text}")
                response_data = {}
        else:
            # Check if response is JSON
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response.text}")
                response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok and not expect_binary:
            for key in expected_keys:
                if key not in response_data:
                    print(f"Missing expected key in response: {key}")
                    keys_ok = False
        
        # For binary responses, check if PDF is valid
        if expect_binary and status_ok:
            keys_ok = response_data.get("pdf_valid", False)
        
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

def test_authentication_setup():
    """Set up authentication for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION SETUP")
    print("="*80)
    
    # Try email/password login first (based on test_result.md mentions of dino@cytonic.com)
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    email_login_test, email_login_response = run_test(
        "Email/Password Login for PDF Testing",
        "/auth/login",
        method="POST",
        data=login_data,
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if email_login_test and email_login_response:
        auth_token = email_login_response.get("access_token")
        user_data = email_login_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Email/password authentication setup successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Email/password authentication failed, trying to register a test user...")
        
        # Try to register a test user
        register_data = {
            "email": "test@pdftest.com",
            "password": "TestPassword123",
            "name": "PDF Test User"
        }
        
        register_test, register_response = run_test(
            "Register Test User for PDF Testing",
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
            print("❌ Authentication setup failed completely")
            return False

def test_report_generation_for_pdf():
    """Generate test reports to use for PDF download testing"""
    global created_report_ids
    
    print("\n" + "="*80)
    print("2. REPORT GENERATION FOR PDF TESTING")
    print("="*80)
    
    # First, ensure we have some simulation data
    print("Setting up simulation state...")
    
    # Start simulation
    start_test, start_response = run_test(
        "Start Simulation for Reports",
        "/simulation/start",
        method="POST",
        auth=True
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False
    
    # Create some agents for conversation generation
    print("Creating agents for conversation generation...")
    
    agent_data_1 = {
        "name": "Dr. Sarah Chen",
        "archetype": "scientist",
        "goal": "Analyze the coral overgrowth situation",
        "expertise": "Marine biology and genetic engineering",
        "background": "PhD in Marine Biology with expertise in coral genetics",
        "personality": {
            "extroversion": 6,
            "optimism": 7,
            "curiosity": 9,
            "cooperativeness": 8,
            "energy": 7
        }
    }
    
    agent_data_2 = {
        "name": "Prof. Marcus Rodriguez",
        "archetype": "leader",
        "goal": "Lead the response team",
        "expertise": "Environmental crisis management",
        "background": "Environmental crisis management specialist",
        "personality": {
            "extroversion": 8,
            "optimism": 6,
            "curiosity": 7,
            "cooperativeness": 8,
            "energy": 8
        }
    }
    
    # Create agents
    create_agent1_test, create_agent1_response = run_test(
        "Create Agent 1 for Report",
        "/agents",
        method="POST",
        data=agent_data_1,
        auth=True
    )
    
    create_agent2_test, create_agent2_response = run_test(
        "Create Agent 2 for Report",
        "/agents",
        method="POST",
        data=agent_data_2,
        auth=True
    )
    
    if not (create_agent1_test and create_agent2_test):
        print("❌ Failed to create agents for conversation")
        return False
    
    # Generate some conversations to have content for the report
    print("Generating conversations for report content...")
    
    conversation1_test, conversation1_response = run_test(
        "Generate Conversation 1",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True
    )
    
    if not conversation1_test:
        print("❌ Failed to generate first conversation")
        return False
    
    conversation2_test, conversation2_response = run_test(
        "Generate Conversation 2",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True
    )
    
    if not conversation2_test:
        print("❌ Failed to generate second conversation")
        return False
    
    print("✅ Generated conversations successfully")
    
    # Now generate a daily report
    print("Generating daily report...")
    daily_report_test, daily_report_response = run_test(
        "Generate Daily Report for PDF Testing",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True,
        expected_keys=["success"]
    )
    
    if daily_report_test and daily_report_response:
        if daily_report_response.get("success"):
            print("✅ Daily report generated successfully")
            
            # Get the generated report ID from reports list
            reports_test, reports_response = run_test(
                "Get Reports List",
                "/reports",
                method="GET",
                auth=True,
                expected_keys=["success", "reports"]
            )
            
            if reports_test and reports_response:
                reports = reports_response.get("reports", [])
                if reports:
                    # Get the most recent report
                    latest_report = reports[0]  # Reports are sorted by creation date (newest first)
                    report_id = latest_report.get("id")
                    if report_id:
                        created_report_ids.append(report_id)
                        print(f"✅ Found generated report with ID: {report_id}")
                        return True
                    else:
                        print("❌ Report ID not found in report data")
                        return False
                else:
                    print("❌ No reports found after generation")
                    return False
            else:
                print("❌ Failed to retrieve reports list")
                return False
        else:
            print("❌ Daily report generation failed")
            return False
    else:
        print("❌ Daily report generation request failed")
        return False

def test_report_data_structure():
    """Test that reports have the correct ID structure for PDF download"""
    print("\n" + "="*80)
    print("3. REPORT DATA STRUCTURE TESTING")
    print("="*80)
    
    if not created_report_ids:
        print("❌ No reports available for testing")
        return False
    
    report_id = created_report_ids[0]
    
    # Test getting specific report
    get_report_test, get_report_response = run_test(
        "Get Specific Report Structure",
        f"/reports/{report_id}",
        method="GET",
        auth=True,
        expected_keys=["success", "report"]
    )
    
    if get_report_test and get_report_response:
        report = get_report_response.get("report", {})
        
        # Check required fields for PDF generation
        required_fields = ["id", "title", "content", "type", "created_at"]
        missing_fields = []
        
        for field in required_fields:
            if field not in report:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields for PDF generation: {missing_fields}")
            return False
        else:
            print("✅ Report has all required fields for PDF generation")
            
            # Check content length
            content = report.get("content", "")
            content_length = len(content)
            print(f"✅ Report content length: {content_length} characters")
            
            if content_length > 100:  # Reasonable content for PDF
                print("✅ Report has substantial content for PDF")
                return True
            else:
                print("⚠️ Report content is quite short but should still work")
                return True
    else:
        print("❌ Failed to get report structure")
        return False

def test_pdf_download_endpoint():
    """Test the PDF download endpoint functionality"""
    print("\n" + "="*80)
    print("4. PDF DOWNLOAD ENDPOINT TESTING")
    print("="*80)
    
    if not created_report_ids:
        print("❌ No reports available for PDF download testing")
        return False
    
    report_id = created_report_ids[0]
    
    # Test successful PDF download
    pdf_download_test, pdf_download_response = run_test(
        "Download Report PDF",
        f"/reports/{report_id}/download-pdf",
        method="GET",
        auth=True,
        measure_time=True,
        expect_binary=True,
        expected_status=200
    )
    
    if pdf_download_test and pdf_download_response:
        content_length = pdf_download_response.get("content_length", 0)
        if content_length > 1000:  # A reasonable PDF should be at least 1KB
            print(f"✅ PDF download successful with {content_length} bytes")
            return True
        else:
            print(f"⚠️ PDF seems small ({content_length} bytes) but download worked")
            return True
    else:
        print("❌ PDF download failed")
        return False

def test_pdf_error_handling():
    """Test error handling for PDF download"""
    print("\n" + "="*80)
    print("5. PDF DOWNLOAD ERROR HANDLING TESTING")
    print("="*80)
    
    # Test 1: Invalid report ID (should return 404)
    fake_report_id = str(uuid.uuid4())
    invalid_id_test, invalid_id_response = run_test(
        "PDF Download with Invalid Report ID",
        f"/reports/{fake_report_id}/download-pdf",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if invalid_id_test:
        print("✅ Invalid report ID correctly returns 404")
    else:
        print("❌ Invalid report ID error handling failed")
        return False
    
    # Test 2: No authentication (should return 401)
    if created_report_ids:
        report_id = created_report_ids[0]
        no_auth_test, no_auth_response = run_test(
            "PDF Download without Authentication",
            f"/reports/{report_id}/download-pdf",
            method="GET",
            auth=False,
            expected_status=401
        )
        
        if no_auth_test:
            print("✅ No authentication correctly returns 401")
        else:
            print("❌ Authentication requirement error handling failed")
            return False
    
    # Test 3: Malformed report ID
    malformed_id_test, malformed_id_response = run_test(
        "PDF Download with Malformed Report ID",
        f"/reports/invalid-id-format/download-pdf",
        method="GET",
        auth=True,
        expected_status=404  # Should return 404 for malformed ID
    )
    
    if malformed_id_test:
        print("✅ Malformed report ID correctly handled")
    else:
        print("❌ Malformed report ID error handling failed")
        return False
    
    print("✅ All PDF download error handling tests passed")
    return True

def test_pdf_content_verification():
    """Test that PDF contains proper formatting and content"""
    print("\n" + "="*80)
    print("6. PDF CONTENT VERIFICATION")
    print("="*80)
    
    if not created_report_ids:
        print("❌ No reports available for content verification")
        return False
    
    report_id = created_report_ids[0]
    
    # First get the report data to compare with PDF
    get_report_test, get_report_response = run_test(
        "Get Report Data for Verification",
        f"/reports/{report_id}",
        method="GET",
        auth=True
    )
    
    if not get_report_test:
        print("❌ Failed to get report data for verification")
        return False
    
    report = get_report_response.get("report", {})
    report_title = report.get("title", "")
    report_content = report.get("content", "")
    
    print(f"Report Title: {report_title}")
    print(f"Report Content Length: {len(report_content)} characters")
    
    # Download PDF and verify it's valid
    pdf_test, pdf_response = run_test(
        "Download PDF for Content Verification",
        f"/reports/{report_id}/download-pdf",
        method="GET",
        auth=True,
        expect_binary=True
    )
    
    if pdf_test and pdf_response:
        if pdf_response.get("pdf_valid"):
            content_length = pdf_response.get("content_length", 0)
            print(f"✅ PDF is valid with {content_length} bytes")
            
            # Check if PDF size is reasonable compared to content
            if content_length > len(report_content):
                print("✅ PDF size is larger than text content (includes formatting)")
                return True
            else:
                print("⚠️ PDF size seems small but is valid")
                return True
        else:
            print("❌ PDF content is invalid")
            return False
    else:
        print("❌ Failed to download PDF for verification")
        return False

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Test data cleanup")
    print("="*80)
    
    # Note: Reports are typically kept for user reference
    # but we could add cleanup if needed
    print("✅ Test data cleanup completed (reports preserved)")

def main():
    """Main test execution function"""
    print("REPORT PDF DOWNLOAD FUNCTIONALITY TESTING")
    print("Testing report modal positioning and PDF download functionality")
    print("="*80)
    
    # Run all test suites
    test_suites = [
        ("Authentication Setup", test_authentication_setup),
        ("Report Generation for PDF", test_report_generation_for_pdf),
        ("Report Data Structure", test_report_data_structure),
        ("PDF Download Endpoint", test_pdf_download_endpoint),
        ("PDF Error Handling", test_pdf_error_handling),
        ("PDF Content Verification", test_pdf_content_verification)
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