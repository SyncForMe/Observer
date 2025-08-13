#!/usr/bin/env python3
"""
REPORTS FUNCTIONALITY TESTING
Testing the specific user-reported issue: Reports are being generated but not visible/accessible in the reports section.

Investigation Areas:
1. Test the `/api/simulation/generate-daily-report` endpoint to see if reports are being generated and stored correctly
2. Check if there's a missing endpoint to retrieve reports (like `/api/reports`)
3. Test the `/api/simulation/state` endpoint to see if reports should be included there
4. Verify if reports are being stored in the database correctly
5. Test with authentication and verify the complete flow from report generation to retrieval
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

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "critical_findings": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
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
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text}")
            response_data = {"raw_text": response.text}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
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
            "result": result,
            "response_data": response_data
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

def add_critical_finding(finding):
    """Add a critical finding to the results"""
    test_results["critical_findings"].append(finding)
    print(f"🚨 CRITICAL FINDING: {finding}")

def test_authentication():
    """Test authentication to get a valid token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("1. AUTHENTICATION SETUP")
    print("="*80)
    
    # Test guest login
    guest_test, guest_response = run_test(
        "Guest Login for Reports Testing",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Authentication failed - cannot proceed with reports testing")
        add_critical_finding("Authentication failed - reports testing cannot proceed")
        return False

def test_report_generation():
    """Test the report generation endpoint"""
    print("\n" + "="*80)
    print("2. REPORT GENERATION TESTING")
    print("="*80)
    
    print("🔍 Testing the user's specific issue: Generate Daily Report functionality")
    
    # Test 1: Generate a daily report manually
    print("\n--- Test 1: Manual Daily Report Generation ---")
    generate_test, generate_response = run_test(
        "Generate Daily Report (Manual)",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True
    )
    
    report_generated = False
    report_id = None
    
    if generate_test and generate_response:
        success = generate_response.get("success", False)
        message = generate_response.get("message", "No message")
        
        if success:
            print(f"✅ Report generation successful: {message}")
            report_generated = True
            
            # Check if report ID is returned
            if "report" in generate_response:
                report_data = generate_response["report"]
                report_id = report_data.get("id")
                print(f"✅ Report ID returned: {report_id}")
            elif "report_id" in generate_response:
                report_id = generate_response["report_id"]
                print(f"✅ Report ID returned: {report_id}")
            else:
                print("⚠️ No report ID returned in response")
                add_critical_finding("Report generation successful but no report ID returned")
        else:
            print(f"❌ Report generation failed: {message}")
            add_critical_finding(f"Report generation failed: {message}")
            return False
    else:
        print("❌ Report generation endpoint failed")
        add_critical_finding("Report generation endpoint is not working")
        return False
    
    # Test 2: Try different report generation parameters
    print("\n--- Test 2: Auto Daily Report Generation ---")
    auto_generate_test, auto_generate_response = run_test(
        "Generate Daily Report (Auto)",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": False},
        auth=True,
        measure_time=True
    )
    
    if auto_generate_test:
        print("✅ Auto report generation works")
    else:
        print("⚠️ Auto report generation has issues")
    
    return report_generated, report_id

def test_report_retrieval():
    """Test if there are endpoints to retrieve generated reports"""
    print("\n" + "="*80)
    print("3. REPORT RETRIEVAL TESTING")
    print("="*80)
    
    print("🔍 Testing if users can retrieve generated reports")
    
    # Test 1: Check for /api/reports endpoint
    print("\n--- Test 1: Check /api/reports endpoint ---")
    reports_test, reports_response = run_test(
        "Get All Reports",
        "/reports",
        method="GET",
        auth=True,
        expected_status=[200, 404]  # Either works or doesn't exist
    )
    
    reports_endpoint_exists = False
    if reports_test and reports_response:
        if "reports" in str(reports_response).lower() or isinstance(reports_response, list):
            print("✅ /api/reports endpoint exists and returns data")
            reports_endpoint_exists = True
        else:
            print("⚠️ /api/reports endpoint exists but response format unclear")
    else:
        print("❌ /api/reports endpoint does not exist")
        add_critical_finding("Missing /api/reports endpoint - users cannot retrieve generated reports")
    
    # Test 2: Check for /api/reports/{id} endpoint
    print("\n--- Test 2: Check /api/reports/{id} endpoint ---")
    specific_report_test, specific_report_response = run_test(
        "Get Specific Report",
        "/reports/test-report-id",
        method="GET",
        auth=True,
        expected_status=[200, 404]  # Either works or doesn't exist
    )
    
    if specific_report_test:
        print("✅ /api/reports/{id} endpoint exists")
    else:
        print("❌ /api/reports/{id} endpoint does not exist")
        add_critical_finding("Missing /api/reports/{id} endpoint - users cannot retrieve specific reports")
    
    # Test 3: Check for reports in simulation state
    print("\n--- Test 3: Check if reports are included in simulation state ---")
    state_test, state_response = run_test(
        "Get Simulation State (Check for Reports)",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    reports_in_state = False
    if state_test and state_response:
        # Check if reports are included in simulation state
        state_keys = list(state_response.keys())
        print(f"Simulation state keys: {state_keys}")
        
        if any("report" in key.lower() for key in state_keys):
            print("✅ Report-related data found in simulation state")
            reports_in_state = True
        else:
            print("❌ No report-related data in simulation state")
            add_critical_finding("Reports not included in simulation state - users cannot see report status")
    
    # Test 4: Check for reports in documents endpoint
    print("\n--- Test 4: Check if reports are stored as documents ---")
    documents_test, documents_response = run_test(
        "Get All Documents (Check for Reports)",
        "/documents",
        method="GET",
        auth=True
    )
    
    reports_as_documents = False
    if documents_test and documents_response:
        if isinstance(documents_response, list) and len(documents_response) > 0:
            # Check if any documents are reports
            for doc in documents_response:
                if isinstance(doc, dict):
                    title = doc.get("title", "").lower()
                    category = doc.get("category", "").lower()
                    metadata = doc.get("metadata", {})
                    if isinstance(metadata, dict):
                        meta_title = metadata.get("title", "").lower()
                        meta_category = metadata.get("category", "").lower()
                        
                        if any("report" in field for field in [title, category, meta_title, meta_category]):
                            print(f"✅ Found report as document: {doc.get('title', 'Unknown')}")
                            reports_as_documents = True
                            break
            
            if not reports_as_documents:
                print("❌ No reports found in documents collection")
                add_critical_finding("Generated reports not accessible through documents endpoint")
        else:
            print("⚠️ No documents found or empty response")
    
    return reports_endpoint_exists, reports_in_state, reports_as_documents

def test_database_storage():
    """Test if reports are being stored in the database correctly"""
    print("\n" + "="*80)
    print("4. DATABASE STORAGE VERIFICATION")
    print("="*80)
    
    print("🔍 Testing if reports are properly stored in database")
    
    # Since we can't directly access the database, we'll infer from API responses
    # and check for consistency in report generation
    
    # Test 1: Generate multiple reports and check for consistency
    print("\n--- Test 1: Multiple Report Generation Consistency ---")
    
    report_ids = []
    for i in range(3):
        print(f"\nGenerating report {i+1}/3...")
        generate_test, generate_response = run_test(
            f"Generate Report {i+1}",
            "/simulation/generate-daily-report",
            method="POST",
            data={"manual": True},
            auth=True,
            measure_time=True
        )
        
        if generate_test and generate_response:
            success = generate_response.get("success", False)
            if success:
                # Try to extract report ID
                report_id = None
                if "report" in generate_response:
                    report_data = generate_response["report"]
                    report_id = report_data.get("id")
                elif "report_id" in generate_response:
                    report_id = generate_response["report_id"]
                
                if report_id:
                    report_ids.append(report_id)
                    print(f"✅ Report {i+1} generated with ID: {report_id}")
                else:
                    print(f"⚠️ Report {i+1} generated but no ID returned")
            else:
                print(f"❌ Report {i+1} generation failed")
        else:
            print(f"❌ Report {i+1} generation request failed")
    
    print(f"\nGenerated {len(report_ids)} reports with IDs: {report_ids}")
    
    if len(report_ids) > 0:
        print("✅ Reports are being generated consistently")
    else:
        print("❌ Report generation is inconsistent")
        add_critical_finding("Report generation is inconsistent - database storage may be failing")
    
    # Test 2: Check if simulation state reflects report generation
    print("\n--- Test 2: Simulation State Report Tracking ---")
    state_test, state_response = run_test(
        "Check Simulation State After Report Generation",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_test and state_response:
        # Look for report-related fields
        report_fields = [key for key in state_response.keys() if "report" in key.lower()]
        if report_fields:
            print(f"✅ Found report-related fields in simulation state: {report_fields}")
            for field in report_fields:
                print(f"  {field}: {state_response[field]}")
        else:
            print("❌ No report-related fields in simulation state")
            add_critical_finding("Simulation state not tracking report generation")
    
    return len(report_ids) > 0

def test_complete_workflow():
    """Test the complete workflow from report generation to retrieval"""
    print("\n" + "="*80)
    print("5. COMPLETE WORKFLOW TESTING")
    print("="*80)
    
    print("🔍 Testing the complete user workflow: Generate → View Reports")
    
    # Step 1: Generate a report
    print("\n--- Step 1: Generate Report ---")
    generate_test, generate_response = run_test(
        "Workflow: Generate Report",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True
    )
    
    if not generate_test or not generate_response.get("success", False):
        print("❌ Workflow failed at report generation step")
        add_critical_finding("Complete workflow fails at report generation")
        return False
    
    print("✅ Step 1 completed: Report generated")
    
    # Step 2: Try to retrieve the report
    print("\n--- Step 2: Retrieve Generated Report ---")
    
    # Try multiple retrieval methods
    retrieval_methods = [
        ("/reports", "GET", "All Reports"),
        ("/documents", "GET", "Documents (may include reports)"),
        ("/simulation/state", "GET", "Simulation State (may include report info)")
    ]
    
    report_found = False
    for endpoint, method, description in retrieval_methods:
        print(f"\nTrying to retrieve report via {description}...")
        retrieve_test, retrieve_response = run_test(
            f"Workflow: {description}",
            endpoint,
            method=method,
            auth=True
        )
        
        if retrieve_test and retrieve_response:
            # Check if the response contains report data
            response_str = json.dumps(retrieve_response).lower()
            if "report" in response_str and "day" in response_str:
                print(f"✅ Report data found via {description}")
                report_found = True
                break
            else:
                print(f"⚠️ {description} accessible but no report data found")
        else:
            print(f"❌ {description} not accessible")
    
    if report_found:
        print("✅ Complete workflow successful: Generate → Retrieve")
        return True
    else:
        print("❌ Complete workflow failed: Reports generated but not retrievable")
        add_critical_finding("CRITICAL: Reports are generated but users cannot retrieve them - this is the root cause of the user's issue")
        return False

def print_summary():
    """Print a comprehensive summary of all test results"""
    print("\n" + "="*80)
    print("REPORTS FUNCTIONALITY TEST SUMMARY")
    print("="*80)
    
    print(f"Total Tests: {len(test_results['tests'])}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    print("\n" + "="*80)
    print("CRITICAL FINDINGS")
    print("="*80)
    
    if test_results["critical_findings"]:
        for i, finding in enumerate(test_results["critical_findings"], 1):
            print(f"{i}. 🚨 {finding}")
    else:
        print("✅ No critical issues found")
    
    print("\n" + "="*80)
    print("DETAILED TEST RESULTS")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌" if test["result"] == "FAILED" else "⚠️"
        print(f"{i}. {result_symbol} {test['name']} ({test['method']} {test['endpoint']}) - Status: {test.get('status_code', 'N/A')}")
    
    print("\n" + "="*80)
    print("ROOT CAUSE ANALYSIS")
    print("="*80)
    
    # Analyze the findings to determine root cause
    if any("cannot retrieve" in finding.lower() for finding in test_results["critical_findings"]):
        print("🎯 ROOT CAUSE IDENTIFIED:")
        print("   The user's issue is caused by missing report retrieval endpoints.")
        print("   Reports are being generated and stored, but there's no way for users to access them.")
        print("\n📋 RECOMMENDED FIXES:")
        print("   1. Implement GET /api/reports endpoint to list all user reports")
        print("   2. Implement GET /api/reports/{id} endpoint to retrieve specific reports")
        print("   3. Include report data in simulation state or documents endpoint")
        print("   4. Add report metadata to help users identify and access their reports")
    elif any("generation failed" in finding.lower() for finding in test_results["critical_findings"]):
        print("🎯 ROOT CAUSE IDENTIFIED:")
        print("   The user's issue is caused by report generation failures.")
        print("   The generate-daily-report endpoint is not working correctly.")
        print("\n📋 RECOMMENDED FIXES:")
        print("   1. Debug the generate_ai_daily_report function")
        print("   2. Check LLM API integration and quota limits")
        print("   3. Verify database connection and report storage")
        print("   4. Add better error handling and logging")
    else:
        print("🔍 ANALYSIS INCONCLUSIVE:")
        print("   Multiple issues detected. Manual investigation required.")
    
    print("="*80)

def main():
    """Main test execution function"""
    print("REPORTS FUNCTIONALITY TESTING")
    print("Investigating user issue: Reports generated but not visible/accessible")
    print("="*80)
    
    # Test sequence
    test_functions = [
        ("Authentication Setup", test_authentication),
        ("Report Generation", test_report_generation),
        ("Report Retrieval", test_report_retrieval),
        ("Database Storage", test_database_storage),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    failed_tests = []
    
    for test_name, test_function in test_functions:
        try:
            print(f"\n{'='*80}")
            print(f"RUNNING: {test_name}")
            print(f"{'='*80}")
            
            if test_name == "Authentication Setup":
                success = test_function()
                if not success:
                    print("❌ Cannot proceed without authentication")
                    break
            elif test_name == "Report Generation":
                report_generated, report_id = test_function()
                if not report_generated:
                    failed_tests.append(test_name)
            elif test_name == "Report Retrieval":
                reports_endpoint, reports_in_state, reports_as_docs = test_function()
                if not any([reports_endpoint, reports_in_state, reports_as_docs]):
                    failed_tests.append(test_name)
            else:
                success = test_function()
                if not success:
                    failed_tests.append(test_name)
                    
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed_tests.append(test_name)
            add_critical_finding(f"{test_name} failed with error: {e}")
    
    # Print comprehensive summary
    print_summary()
    
    # Return overall success
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)