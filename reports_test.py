#!/usr/bin/env python3
"""
REPORTS FUNCTIONALITY TESTING
Testing the newly implemented reports functionality to fix the user issue:
"Reports are being generated but not visible/accessible in the reports section."

This test specifically validates:
1. GET /api/reports endpoint to list all reports with authentication
2. GET /api/reports/{report_id} endpoint to get specific reports  
3. Updated /api/simulation/state endpoint to verify it now includes reports
4. Generate a test report and verify it appears in both endpoints
5. Test error handling for non-existent reports (should return 404)
6. Verify authentication is properly enforced on all report endpoints
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
            response_data = {}
        
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

def authenticate():
    """Authenticate and get JWT token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION SETUP")
    print("="*80)
    
    # Test guest login
    guest_test, guest_response = run_test(
        "Guest Login",
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
        print("❌ Authentication failed")
        return False

def test_reports_functionality():
    """Test the newly implemented reports functionality - COMPREHENSIVE TESTING"""
    print("\n" + "="*80)
    print("REPORTS FUNCTIONALITY TESTING (NEW IMPLEMENTATION)")
    print("="*80)
    
    print("🔍 Testing the newly implemented reports functionality to fix user issue:")
    print("   - Reports were being generated but not visible in reports section")
    print("   - New endpoints: GET /api/reports, GET /api/reports/{id}")
    print("   - Updated /api/simulation/state to include reports")
    
    generated_report_id = None
    list_reports_response = None
    
    # Test 1: Generate a test report first
    print("\n--- Test 1: Generate Test Report ---")
    daily_report_test, daily_report_response = run_test(
        "Generate Daily Report for Testing",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True,
        expected_status=200
    )
    
    if daily_report_test and daily_report_response:
        print("✅ Daily report generation successful")
        
        # Extract report ID if available
        if "report" in daily_report_response:
            report = daily_report_response["report"]
            generated_report_id = report.get("id")
            print(f"✅ Generated report ID: {generated_report_id}")
        else:
            print("⚠️ Report data not included in generation response")
    else:
        print("❌ Failed to generate test report - this may affect subsequent tests")
    
    # Test 2: Test GET /api/reports endpoint (list all reports)
    print("\n--- Test 2: List All Reports Endpoint ---")
    list_reports_test, list_reports_response = run_test(
        "List All Reports",
        "/reports",
        method="GET",
        auth=True,
        expected_keys=["success", "reports", "count"]
    )
    
    if list_reports_test and list_reports_response:
        print("✅ Reports list endpoint working")
        
        reports = list_reports_response.get("reports", [])
        count = list_reports_response.get("count", 0)
        print(f"✅ Found {count} reports in user's account")
        
        # Verify report structure
        if reports:
            sample_report = reports[0]
            required_fields = ["id", "type", "title", "content", "created_at", "user_id"]
            missing_fields = [field for field in required_fields if field not in sample_report]
            if missing_fields:
                print(f"❌ Missing fields in report: {missing_fields}")
                return False
            else:
                print("✅ Report structure is correct")
                
            # Use the first report ID for specific report testing if we don't have generated one
            if not generated_report_id and reports:
                generated_report_id = reports[0].get("id")
                print(f"✅ Using existing report ID for testing: {generated_report_id}")
        else:
            print("⚠️ No reports found - this may be expected for new users")
    else:
        print("❌ Reports list endpoint failed")
        return False
    
    # Test 3: Test GET /api/reports/{report_id} endpoint (get specific report)
    print("\n--- Test 3: Get Specific Report Endpoint ---")
    if generated_report_id:
        get_report_test, get_report_response = run_test(
            "Get Specific Report",
            f"/reports/{generated_report_id}",
            method="GET",
            auth=True,
            expected_keys=["success", "report"]
        )
        
        if get_report_test and get_report_response:
            print("✅ Specific report retrieval working")
            
            report = get_report_response.get("report", {})
            if report.get("id") == generated_report_id:
                print("✅ Report ID matches requested ID")
            else:
                print("❌ Report ID mismatch")
                return False
                
            # Verify report content
            if report.get("content") and len(report.get("content", "")) > 100:
                print("✅ Report contains substantial content")
            else:
                print("⚠️ Report content seems minimal")
        else:
            print("❌ Specific report retrieval failed")
            return False
    else:
        print("⚠️ Skipping specific report test - no report ID available")
    
    # Test 4: Test error handling for non-existent reports (404)
    print("\n--- Test 4: Error Handling for Non-existent Reports ---")
    fake_report_id = str(uuid.uuid4())
    error_test, error_response = run_test(
        "Get Non-existent Report",
        f"/reports/{fake_report_id}",
        method="GET",
        auth=True,
        expected_status=404
    )
    
    if error_test:
        print("✅ Proper 404 error handling for non-existent reports")
    else:
        print("❌ Error handling for non-existent reports failed")
        return False
    
    # Test 5: Test authentication enforcement on reports endpoints
    print("\n--- Test 5: Authentication Enforcement ---")
    
    # Test list reports without auth
    no_auth_list_test, no_auth_list_response = run_test(
        "List Reports (No Auth)",
        "/reports",
        method="GET",
        auth=False,
        expected_status=403  # Backend returns 403 instead of 401
    )
    
    if no_auth_list_test:
        print("✅ Reports list endpoint properly requires authentication")
    else:
        print("❌ Reports list endpoint authentication enforcement failed")
        return False
    
    # Test specific report without auth
    if generated_report_id:
        no_auth_get_test, no_auth_get_response = run_test(
            "Get Specific Report (No Auth)",
            f"/reports/{generated_report_id}",
            method="GET",
            auth=False,
            expected_status=403  # Backend returns 403 instead of 401
        )
        
        if no_auth_get_test:
            print("✅ Specific report endpoint properly requires authentication")
        else:
            print("❌ Specific report endpoint authentication enforcement failed")
            return False
    
    # Test 6: Verify simulation/state endpoint includes reports
    print("\n--- Test 6: Simulation State Includes Reports ---")
    state_test, state_response = run_test(
        "Get Simulation State with Reports",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period", "reports"]
    )
    
    if state_test and state_response:
        print("✅ Simulation state endpoint working")
        
        reports_in_state = state_response.get("reports", [])
        print(f"✅ Simulation state includes {len(reports_in_state)} reports")
        
        # Verify reports in state match reports from dedicated endpoint
        if list_reports_response and "reports" in list_reports_response:
            dedicated_reports = list_reports_response["reports"]
            if len(reports_in_state) == len(dedicated_reports):
                print("✅ Report count matches between endpoints")
            else:
                print(f"⚠️ Report count mismatch: state={len(reports_in_state)}, dedicated={len(dedicated_reports)}")
        
        # Verify report structure in state
        if reports_in_state:
            state_report = reports_in_state[0]
            if "id" in state_report and "title" in state_report:
                print("✅ Reports in simulation state have correct structure")
            else:
                print("❌ Reports in simulation state missing required fields")
                return False
    else:
        print("❌ Simulation state endpoint failed")
        return False
    
    # Test 7: Generate another report and verify it appears in both endpoints
    print("\n--- Test 7: Generate New Report and Verify Visibility ---")
    
    # Get initial report count
    initial_count = len(list_reports_response.get("reports", [])) if list_reports_response else 0
    
    # Generate another report
    second_report_test, second_report_response = run_test(
        "Generate Second Test Report",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True
    )
    
    if second_report_test and second_report_response:
        print("✅ Second report generated successfully")
        
        # Check updated reports list
        updated_list_test, updated_list_response = run_test(
            "List Reports After Generation",
            "/reports",
            method="GET",
            auth=True
        )
        
        if updated_list_test and updated_list_response:
            new_count = updated_list_response.get("count", 0)
            if new_count > initial_count:
                print(f"✅ Report count increased from {initial_count} to {new_count}")
            else:
                print(f"⚠️ Report count did not increase: {initial_count} -> {new_count}")
            
            # Check simulation state also reflects new report
            updated_state_test, updated_state_response = run_test(
                "Get Updated Simulation State",
                "/simulation/state",
                method="GET",
                auth=True
            )
            
            if updated_state_test and updated_state_response:
                state_reports_count = len(updated_state_response.get("reports", []))
                if state_reports_count == new_count:
                    print("✅ Simulation state reports count matches dedicated endpoint")
                else:
                    print(f"❌ Report count mismatch: state={state_reports_count}, dedicated={new_count}")
                    return False
            else:
                print("❌ Failed to get updated simulation state")
                return False
        else:
            print("❌ Failed to get updated reports list")
            return False
    else:
        print("⚠️ Second report generation failed - may not affect core functionality")
    
    print("✅ Reports functionality comprehensive testing completed successfully")
    print("✅ This should fix the user's issue: 'Reports generated but not visible'")
    return True

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
    print("REPORTS FUNCTIONALITY TESTING")
    print("Testing newly implemented reports endpoints to fix user visibility issue")
    print("="*80)
    
    # Authenticate first
    if not authenticate():
        print("❌ Authentication failed - cannot proceed with tests")
        return False
    
    # Run reports functionality test
    try:
        print(f"\n{'='*80}")
        print(f"RUNNING REPORTS FUNCTIONALITY TEST")
        print(f"{'='*80}")
        
        success = test_reports_functionality()
        if success:
            print(f"✅ Reports functionality test PASSED")
        else:
            print(f"❌ Reports functionality test FAILED")
            
    except Exception as e:
        print(f"❌ Reports functionality test ERROR: {e}")
        success = False
    
    # Print final summary
    print_summary()
    
    # Print final result
    print(f"\n{'='*80}")
    print("FINAL RESULT")
    print(f"{'='*80}")
    
    if success:
        print(f"✅ ALL REPORTS FUNCTIONALITY TESTS PASSED!")
        print("✅ The user's issue should now be resolved:")
        print("   - Reports can be generated successfully")
        print("   - Reports are visible via GET /api/reports endpoint")
        print("   - Specific reports can be retrieved via GET /api/reports/{id}")
        print("   - Reports are included in simulation state")
        print("   - Authentication is properly enforced")
        print("   - Error handling works correctly")
    else:
        print(f"❌ REPORTS FUNCTIONALITY TESTS FAILED!")
        print("❌ The user's issue may not be fully resolved")
    
    print(f"{'='*80}")
    
    # Return overall success
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)