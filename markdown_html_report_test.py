#!/usr/bin/env python3
"""
MARKDOWN-TO-HTML REPORT FIX TESTING
Testing the specific fix for reports to verify bold formatting issue is resolved.

User reported issue: Seeing literal `**drug safety**` text instead of proper bold formatting.
Expected fix: Reports should use proper HTML `<strong>` tags instead of `**` markdown syntax.

Test Focus:
1. Generate fresh daily report using corrected template
2. Check HTML formatting for proper `<strong>` tags instead of `**` markdown syntax
3. Examine content for any instances of literal `**` asterisks
4. Validate bold rendering with HTML tags
"""

import requests
import json
import time
import os
import sys
import re
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔍 Using API URL: {API_URL}")

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

def log_test_result(test_name, passed, details=""):
    """Log test result"""
    result = "PASSED" if passed else "FAILED"
    symbol = "✅" if passed else "❌"
    
    print(f"{symbol} {test_name}: {result}")
    if details:
        print(f"   Details: {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "result": result,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def authenticate():
    """Authenticate and get JWT token"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("🔐 AUTHENTICATION")
    print("="*80)
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            
            log_test_result("Guest Authentication", True, f"User ID: {test_user_id}")
            return True
        else:
            log_test_result("Guest Authentication", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Guest Authentication", False, f"Error: {e}")
        return False

def create_test_agents():
    """Create test agents for conversation generation"""
    print("\n" + "="*80)
    print("🤖 CREATING TEST AGENTS")
    print("="*80)
    
    agents_data = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Research drug safety protocols",
            "expertise": "Pharmaceutical safety and toxicology",
            "background": "PhD in Pharmacology with 15 years experience in drug safety",
            "personality": {
                "extroversion": 6,
                "optimism": 7,
                "curiosity": 9,
                "cooperativeness": 8,
                "energy": 7
            }
        },
        {
            "name": "Dr. Marcus Rodriguez",
            "archetype": "leader",
            "goal": "Lead clinical trial oversight",
            "expertise": "Clinical research and regulatory compliance",
            "background": "Medical Director with expertise in clinical trials",
            "personality": {
                "extroversion": 8,
                "optimism": 8,
                "curiosity": 7,
                "cooperativeness": 9,
                "energy": 8
            }
        },
        {
            "name": "Dr. Emily Watson",
            "archetype": "skeptic",
            "goal": "Ensure rigorous safety standards",
            "expertise": "Risk assessment and quality assurance",
            "background": "Quality Assurance Director with focus on safety protocols",
            "personality": {
                "extroversion": 5,
                "optimism": 4,
                "curiosity": 8,
                "cooperativeness": 6,
                "energy": 6
            }
        }
    ]
    
    created_agents = []
    
    for agent_data in agents_data:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                agent_id = response_data.get("id")  # Agent endpoint returns 'id' not 'agent_id'
                if agent_id:
                    created_agents.append(agent_id)
                    log_test_result(f"Create Agent: {agent_data['name']}", True, f"ID: {agent_id}")
                else:
                    log_test_result(f"Create Agent: {agent_data['name']}", False, "No agent ID returned")
            else:
                log_test_result(f"Create Agent: {agent_data['name']}", False, f"Status: {response.status_code}")
                
        except Exception as e:
            log_test_result(f"Create Agent: {agent_data['name']}", False, f"Error: {e}")
    
    return len(created_agents) >= 2  # Need at least 2 agents for conversation

def generate_test_conversations():
    """Generate test conversations with drug safety content"""
    print("\n" + "="*80)
    print("💬 GENERATING TEST CONVERSATIONS")
    print("="*80)
    
    # Start simulation first
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        
        if response.status_code == 200:
            log_test_result("Start Simulation", True)
        else:
            log_test_result("Start Simulation", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Start Simulation", False, f"Error: {e}")
        return False
    
    # Generate multiple conversations to create rich content
    conversations_generated = 0
    
    for i in range(3):  # Generate 3 conversations
        try:
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            
            if response.status_code == 200:
                conversations_generated += 1
                log_test_result(f"Generate Conversation {i+1}", True)
                time.sleep(2)  # Brief pause between generations
            else:
                log_test_result(f"Generate Conversation {i+1}", False, f"Status: {response.status_code}")
                
        except Exception as e:
            log_test_result(f"Generate Conversation {i+1}", False, f"Error: {e}")
    
    return conversations_generated >= 2  # Need at least 2 conversations

def generate_daily_report():
    """Generate a fresh daily report using the corrected template"""
    global generated_report_id
    
    print("\n" + "="*80)
    print("📊 GENERATING DAILY REPORT")
    print("="*80)
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {"manual": True}
        
        print("🔍 Calling POST /api/simulation/generate-daily-report...")
        start_time = time.time()
        
        response = requests.post(f"{API_URL}/simulation/generate-daily-report", json=data, headers=headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️ Response time: {response_time:.2f} seconds")
        print(f"📋 Status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            success = response_data.get("success", False)
            if success:
                # Check if report data is included
                report = response_data.get("report")
                if report:
                    generated_report_id = report.get("id")
                    log_test_result("Generate Daily Report", True, f"Report ID: {generated_report_id}")
                    return True, response_data
                else:
                    log_test_result("Generate Daily Report", False, "No report data in response")
                    return False, response_data
            else:
                message = response_data.get("message", "Unknown error")
                log_test_result("Generate Daily Report", False, f"Generation failed: {message}")
                return False, response_data
        else:
            log_test_result("Generate Daily Report", False, f"HTTP {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        log_test_result("Generate Daily Report", False, f"Error: {e}")
        return False, None

def retrieve_report_content(report_id):
    """Retrieve the generated report content"""
    print("\n" + "="*80)
    print("📖 RETRIEVING REPORT CONTENT")
    print("="*80)
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to get report from reports endpoint
        response = requests.get(f"{API_URL}/reports/{report_id}", headers=headers)
        
        if response.status_code == 200:
            report_data = response.json()
            content = report_data.get("content", "")
            log_test_result("Retrieve Report Content", True, f"Content length: {len(content)} characters")
            return content
        else:
            log_test_result("Retrieve Report Content", False, f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        log_test_result("Retrieve Report Content", False, f"Error: {e}")
        return None

def analyze_html_formatting(content):
    """Analyze the report content for HTML formatting vs markdown"""
    print("\n" + "="*80)
    print("🔍 ANALYZING HTML FORMATTING")
    print("="*80)
    
    if not content:
        log_test_result("Content Available", False, "No content to analyze")
        return False
    
    # Test 1: Check for literal ** markdown syntax
    markdown_asterisks = re.findall(r'\*\*[^*]+\*\*', content)
    if markdown_asterisks:
        log_test_result("No Literal ** Markdown", False, f"Found {len(markdown_asterisks)} instances: {markdown_asterisks[:3]}")
        print(f"   🚨 CRITICAL ISSUE: Found literal ** markdown syntax!")
        for i, match in enumerate(markdown_asterisks[:5], 1):
            print(f"      {i}. {match}")
    else:
        log_test_result("No Literal ** Markdown", True, "No literal ** markdown syntax found")
    
    # Test 2: Check for proper HTML <strong> tags
    strong_tags = re.findall(r'<strong>[^<]+</strong>', content)
    if strong_tags:
        log_test_result("HTML Strong Tags Present", True, f"Found {len(strong_tags)} <strong> tags")
        print(f"   ✅ Examples of proper HTML formatting:")
        for i, match in enumerate(strong_tags[:5], 1):
            print(f"      {i}. {match}")
    else:
        log_test_result("HTML Strong Tags Present", False, "No <strong> tags found")
    
    # Test 3: Check for proper HTML structure
    html_elements = {
        'div': len(re.findall(r'<div[^>]*>', content)),
        'h1': len(re.findall(r'<h1[^>]*>', content)),
        'h2': len(re.findall(r'<h2[^>]*>', content)),
        'p': len(re.findall(r'<p[^>]*>', content)),
        'ul': len(re.findall(r'<ul[^>]*>', content)),
        'li': len(re.findall(r'<li[^>]*>', content))
    }
    
    total_html_elements = sum(html_elements.values())
    if total_html_elements > 0:
        log_test_result("HTML Structure Present", True, f"Found {total_html_elements} HTML elements")
        print(f"   📊 HTML element breakdown: {html_elements}")
    else:
        log_test_result("HTML Structure Present", False, "No HTML structure found")
    
    # Test 4: Check for specific drug safety content with proper formatting
    drug_safety_patterns = [
        r'<strong>[^<]*drug[^<]*safety[^<]*</strong>',
        r'<strong>[^<]*safety[^<]*protocol[^<]*</strong>',
        r'<strong>[^<]*clinical[^<]*trial[^<]*</strong>',
        r'<strong>[^<]*pharmaceutical[^<]*</strong>'
    ]
    
    drug_safety_matches = []
    for pattern in drug_safety_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        drug_safety_matches.extend(matches)
    
    if drug_safety_matches:
        log_test_result("Drug Safety Terms Properly Formatted", True, f"Found {len(drug_safety_matches)} properly formatted terms")
        print(f"   🎯 Examples of properly formatted drug safety terms:")
        for i, match in enumerate(drug_safety_matches[:3], 1):
            print(f"      {i}. {match}")
    else:
        # Check if drug safety terms exist but are not properly formatted
        drug_safety_text = re.findall(r'drug[^.]*safety|safety[^.]*protocol|clinical[^.]*trial', content, re.IGNORECASE)
        if drug_safety_text:
            log_test_result("Drug Safety Terms Properly Formatted", False, f"Found terms but not in <strong> tags: {drug_safety_text[:2]}")
        else:
            log_test_result("Drug Safety Terms Properly Formatted", False, "No drug safety terms found in content")
    
    # Test 5: Overall formatting assessment
    has_html_structure = total_html_elements > 5
    has_strong_tags = len(strong_tags) > 0
    no_markdown_asterisks = len(markdown_asterisks) == 0
    
    overall_formatting_good = has_html_structure and has_strong_tags and no_markdown_asterisks
    
    log_test_result("Overall HTML Formatting", overall_formatting_good, 
                   f"HTML: {has_html_structure}, Strong tags: {has_strong_tags}, No markdown: {no_markdown_asterisks}")
    
    return overall_formatting_good

def validate_bold_rendering(content):
    """Validate that bold text will render properly in HTML"""
    print("\n" + "="*80)
    print("🎨 VALIDATING BOLD RENDERING")
    print("="*80)
    
    if not content:
        log_test_result("Content Available for Validation", False, "No content to validate")
        return False
    
    # Test 1: Count bold elements
    strong_tags = re.findall(r'<strong>[^<]+</strong>', content)
    bold_count = len(strong_tags)
    
    if bold_count > 0:
        log_test_result("Bold Elements Present", True, f"Found {bold_count} bold elements")
    else:
        log_test_result("Bold Elements Present", False, "No bold elements found")
        return False
    
    # Test 2: Check for key terms that should be bold
    key_terms = [
        'Key Achievement', 'Current Focus', 'Next Steps',
        'Breakthrough', 'New Approach', 'Impact',
        'Challenge', 'Solution', 'Risk', 'Mitigation',
        'Priority 1', 'Priority 2', 'Priority 3'
    ]
    
    properly_bolded_terms = []
    for term in key_terms:
        pattern = f'<strong>[^<]*{re.escape(term)}[^<]*</strong>'
        if re.search(pattern, content, re.IGNORECASE):
            properly_bolded_terms.append(term)
    
    if properly_bolded_terms:
        log_test_result("Key Terms Properly Bolded", True, f"Found {len(properly_bolded_terms)} properly bolded key terms")
        print(f"   📝 Properly bolded terms: {properly_bolded_terms[:5]}")
    else:
        log_test_result("Key Terms Properly Bolded", False, "No key terms found in bold formatting")
    
    # Test 3: Validate HTML syntax
    unclosed_strong_tags = content.count('<strong>') - content.count('</strong>')
    if unclosed_strong_tags == 0:
        log_test_result("HTML Strong Tags Properly Closed", True, "All <strong> tags are properly closed")
    else:
        log_test_result("HTML Strong Tags Properly Closed", False, f"{abs(unclosed_strong_tags)} unclosed tags")
    
    # Test 4: Check for nested or malformed strong tags
    malformed_strong = re.findall(r'<strong[^>]*<strong|</strong[^>]*</strong>', content)
    if not malformed_strong:
        log_test_result("No Malformed Strong Tags", True, "No nested or malformed <strong> tags")
    else:
        log_test_result("No Malformed Strong Tags", False, f"Found {len(malformed_strong)} malformed tags")
    
    return bold_count > 0 and unclosed_strong_tags == 0 and not malformed_strong

def examine_content_quality(content):
    """Examine the overall content quality and structure"""
    print("\n" + "="*80)
    print("📋 EXAMINING CONTENT QUALITY")
    print("="*80)
    
    if not content:
        log_test_result("Content Available for Examination", False, "No content to examine")
        return False
    
    # Test 1: Content length
    content_length = len(content)
    if content_length > 1000:
        log_test_result("Adequate Content Length", True, f"{content_length} characters")
    else:
        log_test_result("Adequate Content Length", False, f"Only {content_length} characters")
    
    # Test 2: Section structure
    sections = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
    expected_sections = ['Executive Summary', 'Strategic Developments', 'Agent Performance', 'Operational Insights', 'Challenges', 'Recommendations']
    
    found_sections = []
    for expected in expected_sections:
        for found in sections:
            if expected.lower() in found.lower():
                found_sections.append(expected)
                break
    
    if len(found_sections) >= 4:
        log_test_result("Report Sections Present", True, f"Found {len(found_sections)} sections: {found_sections}")
    else:
        log_test_result("Report Sections Present", False, f"Only found {len(found_sections)} sections: {found_sections}")
    
    # Test 3: Professional language
    professional_indicators = ['strategic', 'analysis', 'recommendation', 'implementation', 'optimization', 'assessment']
    professional_count = sum(1 for indicator in professional_indicators if indicator in content.lower())
    
    if professional_count >= 3:
        log_test_result("Professional Language", True, f"Found {professional_count} professional terms")
    else:
        log_test_result("Professional Language", False, f"Only found {professional_count} professional terms")
    
    # Test 4: No placeholder content
    placeholders = re.findall(r'\[[^\]]+\]', content)
    if not placeholders:
        log_test_result("No Placeholder Content", True, "No placeholder brackets found")
    else:
        log_test_result("No Placeholder Content", False, f"Found {len(placeholders)} placeholders: {placeholders[:3]}")
    
    return content_length > 1000 and len(found_sections) >= 4 and not placeholders

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*80)
    print("🧹 CLEANUP")
    print("="*80)
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get all agents and delete test agents
        response = requests.get(f"{API_URL}/agents", headers=headers)
        if response.status_code == 200:
            agents = response.json()
            deleted_count = 0
            
            for agent in agents:
                if agent.get('name', '').startswith('Dr.'):  # Our test agents
                    agent_id = agent.get('id')
                    delete_response = requests.delete(f"{API_URL}/agents/{agent_id}", headers=headers)
                    if delete_response.status_code == 200:
                        deleted_count += 1
            
            log_test_result("Cleanup Test Agents", True, f"Deleted {deleted_count} test agents")
        else:
            log_test_result("Cleanup Test Agents", False, "Could not retrieve agents for cleanup")
            
    except Exception as e:
        log_test_result("Cleanup Test Agents", False, f"Error: {e}")

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}")
    
    for i, test in enumerate(test_results["tests"], 1):
        symbol = "✅" if test["result"] == "PASSED" else "❌"
        print(f"{i:2d}. {symbol} {test['name']}")
        if test.get("details"):
            print(f"     {test['details']}")
    
    # Overall assessment
    critical_tests = [
        "No Literal ** Markdown",
        "HTML Strong Tags Present", 
        "Overall HTML Formatting",
        "Bold Elements Present"
    ]
    
    critical_passed = sum(1 for test in test_results["tests"] 
                         if test["name"] in critical_tests and test["result"] == "PASSED")
    
    print(f"\n{'='*80}")
    print("MARKDOWN-TO-HTML FIX ASSESSMENT")
    print(f"{'='*80}")
    
    if critical_passed == len(critical_tests):
        print("🎉 SUCCESS: Markdown-to-HTML fix is working correctly!")
        print("   ✅ No literal ** markdown syntax found")
        print("   ✅ Proper HTML <strong> tags are being used")
        print("   ✅ Bold formatting will render correctly")
        print("   ✅ User's issue has been resolved")
    else:
        print("❌ ISSUE: Markdown-to-HTML fix needs attention!")
        print(f"   Only {critical_passed}/{len(critical_tests)} critical tests passed")
        print("   The user's bold formatting issue may still exist")
    
    return critical_passed == len(critical_tests)

def main():
    """Main test execution"""
    print("MARKDOWN-TO-HTML REPORT FIX TESTING")
    print("Testing the fix for bold formatting in reports")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed - cannot proceed")
        return False
    
    # Step 2: Create test agents
    if not create_test_agents():
        print("❌ Failed to create test agents - cannot proceed")
        return False
    
    # Step 3: Generate test conversations
    if not generate_test_conversations():
        print("❌ Failed to generate conversations - cannot proceed")
        return False
    
    # Step 4: Generate daily report
    success, report_data = generate_daily_report()
    if not success:
        print("❌ Failed to generate daily report - cannot test formatting")
        cleanup_test_data()
        return False
    
    # Step 5: Retrieve report content
    if generated_report_id:
        content = retrieve_report_content(generated_report_id)
    else:
        # Try to get content from the response
        content = report_data.get("report", {}).get("content", "") if report_data else ""
    
    if not content:
        print("❌ Could not retrieve report content - cannot test formatting")
        cleanup_test_data()
        return False
    
    print(f"\n📄 REPORT CONTENT PREVIEW (first 500 chars):")
    print("-" * 80)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("-" * 80)
    
    # Step 6: Analyze HTML formatting
    formatting_good = analyze_html_formatting(content)
    
    # Step 7: Validate bold rendering
    rendering_good = validate_bold_rendering(content)
    
    # Step 8: Examine content quality
    quality_good = examine_content_quality(content)
    
    # Step 9: Cleanup
    cleanup_test_data()
    
    # Step 10: Print summary
    overall_success = print_summary()
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)