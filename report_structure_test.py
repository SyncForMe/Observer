#!/usr/bin/env python3
"""
DAILY REPORT STRUCTURE AND READABILITY TESTING
Testing the improved report structure and readability enhancements as requested in the review.

Focus Areas:
1. Generate New Report: Create a fresh daily report using the updated template
2. Analyze Content Structure: Verify concise content, proper formatting, bold text, bullet points
3. Check Specific Formatting: Executive Summary, Strategic Developments, Agent Performance, etc.
4. Readability Assessment: 10-second scannable sections, active voice, key terms bolded
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import re
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables
auth_token = None
test_user_id = None
generated_report_id = None

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=False, headers=None, measure_time=False):
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
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return False, None
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        if measure_time:
            print(f"Response Time: {response_time:.2f} seconds")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            if len(str(response_data)) > 2000:
                print(f"Response: {json.dumps(response_data, indent=2)[:2000]}... (truncated)")
            else:
                print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text[:500]}...")
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
    """Authenticate and get access token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION")
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

def generate_fresh_daily_report():
    """Generate a new daily report using the updated template"""
    global generated_report_id
    
    print("\n" + "="*80)
    print("1. GENERATE NEW DAILY REPORT")
    print("="*80)
    
    print("🔍 Generating fresh daily report to test updated template...")
    
    # Generate daily report
    report_test, report_response = run_test(
        "Generate Daily Report",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True,
        expected_keys=["success"]
    )
    
    if report_test and report_response:
        success = report_response.get("success", False)
        if success:
            print("✅ Daily report generated successfully")
            
            # Get the report ID if available
            if "report" in report_response:
                report_data = report_response["report"]
                generated_report_id = report_data.get("id")
                print(f"✅ Report ID: {generated_report_id}")
                return True, report_data
            else:
                print("⚠️ Report data not included in response, will retrieve separately")
                return True, None
        else:
            print(f"❌ Report generation failed: {report_response.get('message', 'Unknown error')}")
            return False, None
    else:
        print("❌ Report generation endpoint failed")
        return False, None

def retrieve_latest_report():
    """Retrieve the latest generated report for analysis"""
    print("\n" + "="*80)
    print("2. RETRIEVE LATEST REPORT")
    print("="*80)
    
    # Get all reports
    reports_test, reports_response = run_test(
        "Get All Reports",
        "/reports",
        method="GET",
        auth=True,
        expected_keys=["success", "reports"]
    )
    
    if reports_test and reports_response:
        reports = reports_response.get("reports", [])
        if reports:
            # Get the most recent report
            latest_report = reports[0]  # Reports should be sorted by creation date
            report_id = latest_report.get("id")
            print(f"✅ Found {len(reports)} reports, latest ID: {report_id}")
            
            # Get full report content
            report_test, report_response = run_test(
                "Get Specific Report",
                f"/reports/{report_id}",
                method="GET",
                auth=True,
                expected_keys=["success", "report"]
            )
            
            if report_test and report_response:
                report_data = report_response.get("report", {})
                print(f"✅ Retrieved report content ({len(report_data.get('content', ''))} characters)")
                return True, report_data
            else:
                print("❌ Failed to retrieve specific report")
                return False, None
        else:
            print("❌ No reports found")
            return False, None
    else:
        print("❌ Failed to retrieve reports list")
        return False, None

def analyze_content_structure(report_data):
    """Analyze the report content structure for readability enhancements"""
    print("\n" + "="*80)
    print("3. ANALYZE CONTENT STRUCTURE")
    print("="*80)
    
    if not report_data or "content" not in report_data:
        print("❌ No report content to analyze")
        return False
    
    content = report_data["content"]
    print(f"📊 Analyzing report content ({len(content)} characters)")
    
    # Test 1: Check for concise content (not verbose text walls)
    print("\n--- Test 1: Content Conciseness ---")
    paragraphs = content.split('\n\n')
    long_paragraphs = [p for p in paragraphs if len(p) > 500]
    
    if len(long_paragraphs) == 0:
        print("✅ No verbose text walls found - content is concise")
        test_results["passed"] += 1
    else:
        print(f"❌ Found {len(long_paragraphs)} verbose paragraphs (>500 chars)")
        test_results["failed"] += 1
    
    # Test 2: Check for proper paragraph structure with clear breaks
    print("\n--- Test 2: Paragraph Structure ---")
    paragraph_breaks = content.count('\n\n')
    if paragraph_breaks >= 5:
        print(f"✅ Good paragraph structure with {paragraph_breaks} clear breaks")
        test_results["passed"] += 1
    else:
        print(f"❌ Poor paragraph structure - only {paragraph_breaks} breaks found")
        test_results["failed"] += 1
    
    # Test 3: Check for bold formatting for key points
    print("\n--- Test 3: Bold Formatting ---")
    bold_patterns = re.findall(r'\*\*([^*]+)\*\*', content)
    if len(bold_patterns) >= 10:
        print(f"✅ Good use of bold formatting - {len(bold_patterns)} bold elements found")
        print(f"   Sample bold text: {bold_patterns[:3]}")
        test_results["passed"] += 1
    else:
        print(f"❌ Insufficient bold formatting - only {len(bold_patterns)} bold elements")
        test_results["failed"] += 1
    
    # Test 4: Check for bullet points and numbered lists
    print("\n--- Test 4: Lists and Bullet Points ---")
    bullet_points = content.count('- ')
    numbered_lists = len(re.findall(r'\n\d+\.', content))
    
    if bullet_points >= 5 or numbered_lists >= 3:
        print(f"✅ Good use of lists - {bullet_points} bullet points, {numbered_lists} numbered items")
        test_results["passed"] += 1
    else:
        print(f"❌ Insufficient list formatting - {bullet_points} bullets, {numbered_lists} numbered")
        test_results["failed"] += 1
    
    # Test 5: Check for improved readability indicators
    print("\n--- Test 5: Readability Indicators ---")
    
    # Check for active voice indicators
    active_voice_indicators = ['implemented', 'achieved', 'completed', 'delivered', 'created']
    active_count = sum(content.lower().count(word) for word in active_voice_indicators)
    
    # Check for present tense usage
    present_tense_indicators = ['is', 'are', 'shows', 'demonstrates', 'provides']
    present_count = sum(content.lower().count(word) for word in present_tense_indicators)
    
    if active_count >= 5 and present_count >= 5:
        print(f"✅ Good readability - {active_count} active voice, {present_count} present tense indicators")
        test_results["passed"] += 1
    else:
        print(f"❌ Poor readability - {active_count} active voice, {present_count} present tense indicators")
        test_results["failed"] += 1
    
    return True

def check_specific_formatting(report_data):
    """Check specific formatting requirements for different sections"""
    print("\n" + "="*80)
    print("4. CHECK SPECIFIC FORMATTING")
    print("="*80)
    
    if not report_data or "content" not in report_data:
        print("❌ No report content to analyze")
        return False
    
    content = report_data["content"]
    
    # Test 1: Executive Summary with 3 focused points and bold labels
    print("\n--- Test 1: Executive Summary Format ---")
    exec_summary_match = re.search(r'Executive Summary.*?(?=\n##|\n#|$)', content, re.DOTALL | re.IGNORECASE)
    if exec_summary_match:
        exec_content = exec_summary_match.group(0)
        bold_labels = re.findall(r'\*\*([^*]+)\*\*', exec_content)
        
        if len(bold_labels) >= 3:
            print(f"✅ Executive Summary has {len(bold_labels)} bold labels")
            print(f"   Sample labels: {bold_labels[:3]}")
            test_results["passed"] += 1
        else:
            print(f"❌ Executive Summary has only {len(bold_labels)} bold labels (expected 3+)")
            test_results["failed"] += 1
    else:
        print("❌ Executive Summary section not found")
        test_results["failed"] += 1
    
    # Test 2: Strategic Developments with bullet points
    print("\n--- Test 2: Strategic Developments Format ---")
    strategic_match = re.search(r'Strategic Developments.*?(?=\n##|\n#|$)', content, re.DOTALL | re.IGNORECASE)
    if strategic_match:
        strategic_content = strategic_match.group(0)
        bullet_count = strategic_content.count('- ')
        
        if bullet_count >= 3:
            print(f"✅ Strategic Developments has {bullet_count} bullet points")
            test_results["passed"] += 1
        else:
            print(f"❌ Strategic Developments has only {bullet_count} bullet points (expected 3+)")
            test_results["failed"] += 1
    else:
        print("❌ Strategic Developments section not found")
        test_results["failed"] += 1
    
    # Test 3: Agent Performance with agent list and contributions
    print("\n--- Test 3: Agent Performance Format ---")
    agent_perf_match = re.search(r'Agent Performance.*?(?=\n##|\n#|$)', content, re.DOTALL | re.IGNORECASE)
    if agent_perf_match:
        agent_content = agent_perf_match.group(0)
        # Look for agent names or contribution patterns
        agent_patterns = re.findall(r'(?:Agent|Dr\.|Prof\.|Mr\.|Ms\.)\s+\w+', agent_content)
        
        if len(agent_patterns) >= 2:
            print(f"✅ Agent Performance lists {len(agent_patterns)} agents with contributions")
            test_results["passed"] += 1
        else:
            print(f"❌ Agent Performance has insufficient agent listings ({len(agent_patterns)} found)")
            test_results["failed"] += 1
    else:
        print("❌ Agent Performance section not found")
        test_results["failed"] += 1
    
    # Test 4: Challenges with challenge → solution format
    print("\n--- Test 4: Challenges Format ---")
    challenges_match = re.search(r'Challenges.*?(?=\n##|\n#|$)', content, re.DOTALL | re.IGNORECASE)
    if challenges_match:
        challenges_content = challenges_match.group(0)
        # Look for challenge-solution patterns
        solution_indicators = ['solution', 'resolved', 'addressed', 'mitigated', 'approach']
        solution_count = sum(challenges_content.lower().count(word) for word in solution_indicators)
        
        if solution_count >= 2:
            print(f"✅ Challenges section shows challenge → solution format ({solution_count} solution indicators)")
            test_results["passed"] += 1
        else:
            print(f"❌ Challenges section lacks solution format ({solution_count} solution indicators)")
            test_results["failed"] += 1
    else:
        print("❌ Challenges section not found")
        test_results["failed"] += 1
    
    # Test 5: Recommendations with numbered priorities
    print("\n--- Test 5: Recommendations Format ---")
    recommendations_match = re.search(r'Recommendations.*?(?=\n##|\n#|$)', content, re.DOTALL | re.IGNORECASE)
    if recommendations_match:
        rec_content = recommendations_match.group(0)
        numbered_items = len(re.findall(r'\n\d+\.', rec_content))
        
        if numbered_items >= 3:
            print(f"✅ Recommendations has {numbered_items} numbered priorities")
            test_results["passed"] += 1
        else:
            print(f"❌ Recommendations has only {numbered_items} numbered items (expected 3+)")
            test_results["failed"] += 1
    else:
        print("❌ Recommendations section not found")
        test_results["failed"] += 1
    
    return True

def assess_readability(report_data):
    """Assess overall readability for effortless user reading experience"""
    print("\n" + "="*80)
    print("5. READABILITY ASSESSMENT")
    print("="*80)
    
    if not report_data or "content" not in report_data:
        print("❌ No report content to analyze")
        return False
    
    content = report_data["content"]
    
    # Test 1: Section scannability (10 seconds or less)
    print("\n--- Test 1: Section Scannability ---")
    sections = re.split(r'\n##\s+', content)
    scannable_sections = 0
    
    for i, section in enumerate(sections[1:], 1):  # Skip first split part
        section_lines = section.split('\n')
        # Count meaningful content lines (not empty or just headers)
        content_lines = [line for line in section_lines if line.strip() and not line.startswith('#')]
        
        if len(content_lines) <= 8:  # Roughly 10 seconds of scanning
            scannable_sections += 1
        
        print(f"   Section {i}: {len(content_lines)} content lines")
    
    if scannable_sections >= len(sections) - 2:  # Allow 1-2 longer sections
        print(f"✅ {scannable_sections}/{len(sections)-1} sections are scannable in 10 seconds")
        test_results["passed"] += 1
    else:
        print(f"❌ Only {scannable_sections}/{len(sections)-1} sections are scannable")
        test_results["failed"] += 1
    
    # Test 2: Active voice usage
    print("\n--- Test 2: Active Voice Usage ---")
    passive_indicators = ['was', 'were', 'been', 'being']
    active_indicators = ['achieved', 'completed', 'implemented', 'delivered', 'created', 'developed']
    
    passive_count = sum(content.lower().count(word) for word in passive_indicators)
    active_count = sum(content.lower().count(word) for word in active_indicators)
    
    if active_count > passive_count:
        print(f"✅ Active voice dominant - {active_count} active vs {passive_count} passive indicators")
        test_results["passed"] += 1
    else:
        print(f"❌ Passive voice dominant - {active_count} active vs {passive_count} passive indicators")
        test_results["failed"] += 1
    
    # Test 3: Present tense usage
    print("\n--- Test 3: Present Tense Usage ---")
    present_indicators = ['is', 'are', 'shows', 'demonstrates', 'provides', 'includes', 'contains']
    past_indicators = ['was', 'were', 'showed', 'demonstrated', 'provided']
    
    present_count = sum(content.lower().count(word) for word in present_indicators)
    past_count = sum(content.lower().count(word) for word in past_indicators)
    
    if present_count > past_count:
        print(f"✅ Present tense dominant - {present_count} present vs {past_count} past indicators")
        test_results["passed"] += 1
    else:
        print(f"❌ Past tense dominant - {present_count} present vs {past_count} past indicators")
        test_results["failed"] += 1
    
    # Test 4: Key terms bolded
    print("\n--- Test 4: Key Terms Bolded ---")
    key_terms = ['strategic', 'critical', 'important', 'priority', 'success', 'achievement', 'challenge', 'solution']
    bolded_key_terms = 0
    
    for term in key_terms:
        if f"**{term}" in content.lower() or f"**{term.title()}" in content:
            bolded_key_terms += 1
    
    if bolded_key_terms >= 3:
        print(f"✅ {bolded_key_terms} key terms are properly bolded")
        test_results["passed"] += 1
    else:
        print(f"❌ Only {bolded_key_terms} key terms are bolded (expected 3+)")
        test_results["failed"] += 1
    
    # Test 5: Overall user-friendly structure
    print("\n--- Test 5: User-Friendly Structure ---")
    structure_score = 0
    
    # Check for clear headings
    headings = re.findall(r'\n##\s+([^\n]+)', content)
    if len(headings) >= 5:
        structure_score += 1
        print(f"   ✅ Good heading structure ({len(headings)} headings)")
    
    # Check for visual breaks
    visual_breaks = content.count('\n\n')
    if visual_breaks >= 10:
        structure_score += 1
        print(f"   ✅ Good visual breaks ({visual_breaks} paragraph breaks)")
    
    # Check for consistent formatting
    if content.count('**') >= 20:  # Consistent bold usage
        structure_score += 1
        print(f"   ✅ Consistent bold formatting")
    
    if structure_score >= 2:
        print(f"✅ User-friendly structure achieved (score: {structure_score}/3)")
        test_results["passed"] += 1
    else:
        print(f"❌ Poor user-friendly structure (score: {structure_score}/3)")
        test_results["failed"] += 1
    
    return True

def print_summary():
    """Print a comprehensive summary of all test results"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED - Report structure and readability enhancements are working perfectly!")
    else:
        print(f"\n⚠️ {test_results['failed']} tests failed - Some improvements needed")
    
    # Detailed test breakdown
    print(f"\n{'='*80}")
    print("DETAILED TEST RESULTS")
    print(f"{'='*80}")
    
    for i, test in enumerate(test_results["tests"], 1):
        result_symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i}. {result_symbol} {test['name']}")
        if test.get("response_time"):
            print(f"   Response Time: {test['response_time']:.2f}s")
    
    # Calculate success rate
    total_tests = test_results['passed'] + test_results['failed']
    if total_tests > 0:
        success_rate = (test_results['passed'] / total_tests) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    print("="*80)

def main():
    """Main test execution function"""
    print("DAILY REPORT STRUCTURE AND READABILITY TESTING")
    print("Testing improved report structure and readability enhancements")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed - cannot proceed with testing")
        return False
    
    # Step 2: Generate fresh daily report
    success, report_data = generate_fresh_daily_report()
    if not success:
        print("❌ Failed to generate daily report - cannot proceed with analysis")
        return False
    
    # Step 3: Retrieve latest report if not included in generation response
    if not report_data:
        success, report_data = retrieve_latest_report()
        if not success:
            print("❌ Failed to retrieve report - cannot proceed with analysis")
            return False
    
    # Step 4: Analyze content structure
    if not analyze_content_structure(report_data):
        print("❌ Content structure analysis failed")
        return False
    
    # Step 5: Check specific formatting requirements
    if not check_specific_formatting(report_data):
        print("❌ Specific formatting check failed")
        return False
    
    # Step 6: Assess overall readability
    if not assess_readability(report_data):
        print("❌ Readability assessment failed")
        return False
    
    # Step 7: Print comprehensive summary
    print_summary()
    
    # Return overall success
    return test_results['failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)