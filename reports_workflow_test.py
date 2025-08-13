#!/usr/bin/env python3
"""
COMPREHENSIVE REPORTS WORKFLOW TESTING
Testing the complete reports workflow to verify the user's issue is now fully resolved.

Test Focus:
1. Generate a daily report to ensure one exists
2. Test the updated `/api/simulation/state` endpoint to verify it includes reports in the response
3. Verify the reports array contains the generated report with all required fields
4. Test that the report generation and retrieval workflow is working end-to-end

This addresses the user's specific issue where reports were being generated but not visible in the Daily Reports section.
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
print(f"🔗 Using API URL: {API_URL}")

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
generated_report_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, params=None, measure_time=False):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*80}\n🧪 Testing: {test_name} ({method} {url})")
    
    # Set up headers with auth token if needed
    if headers is None:
        headers = {}
    
    if auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=60)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, params=params, timeout=60)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, params=params, timeout=60)
        elif method == "DELETE":
            if data is not None:
                response = requests.delete(url, json=data, headers=headers, params=params, timeout=60)
            else:
                response = requests.delete(url, headers=headers, params=params, timeout=60)
        else:
            print(f"❌ Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"📊 Status Code: {response.status_code}")
        if measure_time:
            print(f"⏱️ Response Time: {response_time:.2f} seconds")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📄 Response is not JSON: {response.text}")
            response_data = {}
        
        # Verify status code
        status_ok = response.status_code == expected_status
        
        # Verify expected keys if provided
        keys_ok = True
        if expected_keys and status_ok:
            for key in expected_keys:
                if key not in response_data:
                    print(f"❌ Missing expected key in response: {key}")
                    keys_ok = False
        
        # Determine test result
        test_passed = status_ok and keys_ok
        
        # Update test results
        result = "PASSED" if test_passed else "FAILED"
        result_emoji = "✅" if test_passed else "❌"
        print(f"{result_emoji} Test Result: {result}")
        
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
        print(f"❌ Error during test: {e}")
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
    print("🔐 AUTHENTICATION SETUP")
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
        print("❌ Authentication failed")
        return False

def test_daily_report_generation():
    """Test 1: Generate a daily report to ensure one exists"""
    global generated_report_id
    
    print("\n" + "="*80)
    print("📊 TEST 1: DAILY REPORT GENERATION")
    print("="*80)
    print("🎯 Goal: Generate a daily report to ensure one exists for testing")
    
    # Test daily report generation
    report_data = {"manual": True}
    
    report_test, report_response = run_test(
        "Generate Daily Report",
        "/simulation/generate-daily-report",
        method="POST",
        data=report_data,
        auth=True,
        measure_time=True,
        expected_keys=["success"]
    )
    
    if report_test and report_response:
        success = report_response.get("success", False)
        if success:
            print("✅ Daily report generation successful")
            
            # Extract report ID if available
            if "report" in report_response:
                report = report_response["report"]
                generated_report_id = report.get("id")
                print(f"📋 Generated Report ID: {generated_report_id}")
                print(f"📅 Report Day: {report.get('day', 'N/A')}")
                print(f"🕐 Report Time Period: {report.get('time_period', 'N/A')}")
                print(f"📝 Report Title: {report.get('title', 'N/A')}")
                
                # Check content length
                content = report.get("content", "")
                print(f"📄 Report Content Length: {len(content)} characters")
                
                if len(content) > 100:
                    print("✅ Report has substantial content")
                else:
                    print("⚠️ Report content seems short")
                    
            else:
                print("⚠️ Report data not included in response")
                
            return True
        else:
            error_message = report_response.get("message", "Unknown error")
            print(f"❌ Daily report generation failed: {error_message}")
            return False
    else:
        print("❌ Daily report generation endpoint failed")
        return False

def test_simulation_state_includes_reports():
    """Test 2: Test the updated `/api/simulation/state` endpoint to verify it includes reports"""
    print("\n" + "="*80)
    print("🔄 TEST 2: SIMULATION STATE INCLUDES REPORTS")
    print("="*80)
    print("🎯 Goal: Verify /api/simulation/state endpoint includes reports in the response")
    
    # Test simulation state endpoint
    state_test, state_response = run_test(
        "Get Simulation State with Reports",
        "/simulation/state",
        method="GET",
        auth=True,
        expected_keys=["current_day", "current_time_period", "is_active"]
    )
    
    if state_test and state_response:
        print("✅ Simulation state endpoint accessible")
        
        # Check if reports are included
        if "reports" in state_response:
            reports = state_response["reports"]
            print(f"📊 Reports found in simulation state: {len(reports)} reports")
            
            if len(reports) > 0:
                print("✅ Reports array is populated")
                
                # Examine first report structure
                first_report = reports[0]
                print(f"📋 First Report Structure: {list(first_report.keys())}")
                
                # Check required fields
                required_fields = ["id", "title"]
                missing_fields = [field for field in required_fields if field not in first_report]
                
                if not missing_fields:
                    print("✅ Report has all required fields")
                    
                    # Check if our generated report is in the list
                    if generated_report_id:
                        report_ids = [r.get("id") for r in reports]
                        if generated_report_id in report_ids:
                            print(f"✅ Generated report {generated_report_id} found in simulation state")
                        else:
                            print(f"⚠️ Generated report {generated_report_id} not found in simulation state")
                            print(f"Available report IDs: {report_ids}")
                    
                    return True
                else:
                    print(f"❌ Report missing required fields: {missing_fields}")
                    return False
            else:
                print("⚠️ Reports array is empty")
                return False
        else:
            print("❌ Reports not found in simulation state response")
            print(f"Available keys: {list(state_response.keys())}")
            return False
    else:
        print("❌ Simulation state endpoint failed")
        return False

def test_reports_retrieval_endpoints():
    """Test 3: Verify the reports array contains the generated report with all required fields"""
    print("\n" + "="*80)
    print("📚 TEST 3: REPORTS RETRIEVAL ENDPOINTS")
    print("="*80)
    print("🎯 Goal: Test dedicated reports endpoints and verify report structure")
    
    # Test GET /api/reports endpoint
    reports_test, reports_response = run_test(
        "Get All Reports",
        "/reports",
        method="GET",
        auth=True,
        expected_keys=["success", "reports", "count"]
    )
    
    if reports_test and reports_response:
        success = reports_response.get("success", False)
        if success:
            reports = reports_response.get("reports", [])
            count = reports_response.get("count", 0)
            
            print(f"✅ Reports endpoint successful: {count} reports found")
            
            if count > 0:
                print("✅ Reports are available")
                
                # Examine report structure
                first_report = reports[0]
                print(f"📋 Report Structure: {list(first_report.keys())}")
                
                # Check all required fields for a complete report
                required_fields = ["id", "type", "title", "content", "created_at", "user_id"]
                missing_fields = [field for field in required_fields if field not in first_report]
                
                if not missing_fields:
                    print("✅ Report has all required fields")
                    
                    # Verify content quality
                    content = first_report.get("content", "")
                    content_length = len(content)
                    print(f"📄 Report Content Length: {content_length} characters")
                    
                    if content_length > 500:
                        print("✅ Report has substantial content")
                    else:
                        print("⚠️ Report content seems short")
                    
                    # Check if our generated report is in the list
                    if generated_report_id:
                        report_ids = [r.get("id") for r in reports]
                        if generated_report_id in report_ids:
                            print(f"✅ Generated report {generated_report_id} found in reports list")
                            
                            # Test specific report retrieval
                            specific_report_test, specific_report_response = run_test(
                                f"Get Specific Report {generated_report_id}",
                                f"/reports/{generated_report_id}",
                                method="GET",
                                auth=True,
                                expected_keys=["success", "report"]
                            )
                            
                            if specific_report_test and specific_report_response:
                                specific_success = specific_report_response.get("success", False)
                                if specific_success:
                                    specific_report = specific_report_response.get("report", {})
                                    if specific_report.get("id") == generated_report_id:
                                        print("✅ Specific report retrieval successful")
                                        return True
                                    else:
                                        print("❌ Specific report ID mismatch")
                                        return False
                                else:
                                    print("❌ Specific report retrieval failed")
                                    return False
                            else:
                                print("❌ Specific report endpoint failed")
                                return False
                        else:
                            print(f"⚠️ Generated report {generated_report_id} not found in reports list")
                            print(f"Available report IDs: {report_ids}")
                            return False
                    else:
                        print("⚠️ No generated report ID to verify")
                        return True  # Still pass if we have reports
                        
                else:
                    print(f"❌ Report missing required fields: {missing_fields}")
                    return False
            else:
                print("⚠️ No reports found")
                return False
        else:
            error_message = reports_response.get("message", "Unknown error")
            print(f"❌ Reports endpoint failed: {error_message}")
            return False
    else:
        print("❌ Reports endpoint not accessible")
        return False

def test_end_to_end_workflow():
    """Test 4: Test that the report generation and retrieval workflow is working end-to-end"""
    print("\n" + "="*80)
    print("🔄 TEST 4: END-TO-END WORKFLOW VERIFICATION")
    print("="*80)
    print("🎯 Goal: Verify complete workflow from generation to frontend visibility")
    
    # Step 1: Generate a new report
    print("\n--- Step 1: Generate New Report ---")
    new_report_test, new_report_response = run_test(
        "Generate New Report for E2E Test",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True
    )
    
    if not new_report_test or not new_report_response.get("success"):
        print("❌ Failed to generate new report for E2E test")
        return False
    
    new_report_id = None
    if "report" in new_report_response:
        new_report_id = new_report_response["report"].get("id")
        print(f"✅ Generated new report: {new_report_id}")
    
    # Step 2: Verify report appears in simulation state
    print("\n--- Step 2: Verify Report in Simulation State ---")
    state_check_test, state_check_response = run_test(
        "Check Simulation State for New Report",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if state_check_test and state_check_response:
        reports_in_state = state_check_response.get("reports", [])
        if new_report_id:
            state_report_ids = [r.get("id") for r in reports_in_state]
            if new_report_id in state_report_ids:
                print("✅ New report appears in simulation state")
            else:
                print("❌ New report not found in simulation state")
                return False
        else:
            print("⚠️ No new report ID to verify")
    else:
        print("❌ Failed to check simulation state")
        return False
    
    # Step 3: Verify report appears in reports endpoint
    print("\n--- Step 3: Verify Report in Reports Endpoint ---")
    reports_check_test, reports_check_response = run_test(
        "Check Reports Endpoint for New Report",
        "/reports",
        method="GET",
        auth=True
    )
    
    if reports_check_test and reports_check_response:
        if reports_check_response.get("success"):
            reports_list = reports_check_response.get("reports", [])
            if new_report_id:
                reports_endpoint_ids = [r.get("id") for r in reports_list]
                if new_report_id in reports_endpoint_ids:
                    print("✅ New report appears in reports endpoint")
                else:
                    print("❌ New report not found in reports endpoint")
                    return False
            else:
                print("⚠️ No new report ID to verify")
        else:
            print("❌ Reports endpoint returned failure")
            return False
    else:
        print("❌ Failed to check reports endpoint")
        return False
    
    # Step 4: Verify report can be retrieved individually
    print("\n--- Step 4: Verify Individual Report Retrieval ---")
    if new_report_id:
        individual_test, individual_response = run_test(
            f"Retrieve Individual Report {new_report_id}",
            f"/reports/{new_report_id}",
            method="GET",
            auth=True
        )
        
        if individual_test and individual_response:
            if individual_response.get("success"):
                individual_report = individual_response.get("report", {})
                if individual_report.get("id") == new_report_id:
                    print("✅ Individual report retrieval successful")
                    
                    # Check content quality
                    content = individual_report.get("content", "")
                    if len(content) > 100:
                        print("✅ Report has good content quality")
                    else:
                        print("⚠️ Report content quality could be better")
                    
                else:
                    print("❌ Individual report ID mismatch")
                    return False
            else:
                print("❌ Individual report retrieval failed")
                return False
        else:
            print("❌ Individual report endpoint failed")
            return False
    
    print("\n✅ END-TO-END WORKFLOW VERIFICATION SUCCESSFUL")
    print("🎉 Reports can be generated, stored, and retrieved through all endpoints")
    print("🎉 Frontend should now be able to display reports in Daily Reports section")
    
    return True

def print_summary():
    """Print a comprehensive summary of all test results"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE REPORTS WORKFLOW TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results['passed'] + test_results['failed']
    success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 Total Tests: {total_tests}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    print("\n" + "="*80)
    print("📋 DETAILED TEST RESULTS")
    print("="*80)
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        test_name = test["name"]
        endpoint = test["endpoint"]
        method = test["method"]
        
        print(f"{i:2d}. {result_symbol} {test_name}")
        print(f"     {method} {endpoint}")
        
        if "response_time" in test:
            print(f"     ⏱️ Response Time: {test['response_time']:.2f}s")
        
        if test["result"] == "FAILED":
            print(f"     ❌ Status: {test.get('status_code', 'N/A')} (Expected: {test.get('expected_status', 'N/A')})")
        
        if "error" in test:
            print(f"     ❌ Error: {test['error']}")
    
    print("\n" + "="*80)
    overall_result = "✅ PASSED" if test_results["failed"] == 0 else "❌ FAILED"
    print(f"🏆 OVERALL RESULT: {overall_result}")
    
    if test_results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("🎉 The reports workflow is working correctly!")
        print("🎉 Users should now be able to see generated reports in their Daily Reports section!")
    else:
        print(f"\n⚠️ {test_results['failed']} test(s) failed.")
        print("⚠️ The reports workflow may have issues that need to be addressed.")
    
    print("="*80)

def main():
    """Main test execution function"""
    print("🚀 COMPREHENSIVE REPORTS WORKFLOW TESTING")
    print("Testing the complete reports workflow to verify the user's issue is now fully resolved")
    print("="*80)
    print("📋 Test Plan:")
    print("1. Generate a daily report to ensure one exists")
    print("2. Test the updated `/api/simulation/state` endpoint to verify it includes reports")
    print("3. Verify the reports array contains the generated report with all required fields")
    print("4. Test that the report generation and retrieval workflow is working end-to-end")
    print("="*80)
    
    # Setup authentication
    if not setup_authentication():
        print("❌ Authentication setup failed. Cannot proceed with tests.")
        return False
    
    # Run test sequence
    test_sequence = [
        ("Daily Report Generation", test_daily_report_generation),
        ("Simulation State Includes Reports", test_simulation_state_includes_reports),
        ("Reports Retrieval Endpoints", test_reports_retrieval_endpoints),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    failed_tests = []
    
    for test_name, test_function in test_sequence:
        try:
            print(f"\n{'='*80}")
            print(f"🧪 RUNNING: {test_name}")
            print(f"{'='*80}")
            
            success = test_function()
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed_tests.append(test_name)
    
    # Print comprehensive summary
    print_summary()
    
    # Print test sequence summary
    print(f"\n{'='*80}")
    print("🧪 TEST SEQUENCE SUMMARY")
    print(f"{'='*80}")
    
    total_sequences = len(test_sequence)
    passed_sequences = total_sequences - len(failed_tests)
    
    print(f"📊 Total Test Sequences: {total_sequences}")
    print(f"✅ Passed: {passed_sequences}")
    print(f"❌ Failed: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\n❌ Failed Test Sequences:")
        for test in failed_tests:
            print(f"   • {test}")
    else:
        print(f"\n🎉 ALL TEST SEQUENCES PASSED!")
        print(f"🎉 The user's reports issue has been fully resolved!")
        print(f"🎉 Reports are now properly generated and accessible!")
    
    print(f"{'='*80}")
    
    # Return overall success
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)