#!/usr/bin/env python3
"""
REPORT GENERATION IMPROVEMENTS TESTING
Testing the specific fixes for:
1. Text Contrast Issue - verify content has good contrast (dark text on light background)
2. Double Icons Issue - check for duplicate icons, specifically double 🚀 icons in "Strategic Developments" section
3. Overall Formatting - verify professional HTML structure, proper formatting, no generic introductions

This test addresses the user's specific reported issues with report generation.
"""

import requests
import json
import time
import os
import sys
import re
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

# Global variables for auth testing
auth_token = None
test_user_id = None

def setup_test_data():
    """Set up test data (agents and conversations) needed for report generation"""
    print("\n🔧 Setting up test data for report generation...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create test agents
    agent_data_1 = {
        "name": "Dr. Alice Research",
        "archetype": "scientist",
        "goal": "Conduct quantum research",
        "expertise": "Quantum physics and cryptography",
        "background": "PhD in Quantum Physics with 10 years experience",
        "personality": {
            "extroversion": 6,
            "optimism": 8,
            "curiosity": 9,
            "cooperativeness": 7,
            "energy": 7
        }
    }
    
    agent_data_2 = {
        "name": "Prof. Bob Engineer",
        "archetype": "leader",
        "goal": "Lead engineering projects",
        "expertise": "Engineering management and system architecture",
        "background": "Senior Engineering Manager with enterprise experience",
        "personality": {
            "extroversion": 8,
            "optimism": 7,
            "curiosity": 6,
            "cooperativeness": 8,
            "energy": 8
        }
    }
    
    created_agents = []
    
    # Create agents
    for i, agent_data in enumerate([agent_data_1, agent_data_2], 1):
        try:
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers)
            print(f"Agent creation response {i}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Agent creation data {i}: {json.dumps(data, indent=2)}")
                agent_id = data.get("agent_id") or data.get("id")
                if agent_id:
                    created_agents.append(agent_id)
                    print(f"✅ Created agent {i}: {agent_data['name']} (ID: {agent_id})")
                else:
                    print(f"❌ Failed to get agent ID for agent {i}")
            else:
                print(f"❌ Failed to create agent {i}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error data: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
        except Exception as e:
            print(f"❌ Error creating agent {i}: {e}")
    
    if len(created_agents) < 2:
        print("❌ Failed to create enough agents for conversation generation")
        return False
    
    # Start simulation
    try:
        response = requests.post(f"{API_URL}/simulation/start", headers=headers)
        if response.status_code == 200:
            print("✅ Simulation started")
        else:
            print(f"⚠️ Simulation start returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error starting simulation: {e}")
    
    # Generate some conversations
    print("🗣️ Generating test conversations...")
    conversation_count = 0
    
    for i in range(3):  # Generate 3 conversations
        try:
            response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
            if response.status_code == 200:
                conversation_count += 1
                print(f"✅ Generated conversation {i+1}")
                time.sleep(1)  # Brief pause between generations
            else:
                print(f"⚠️ Conversation generation {i+1} returned: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error generating conversation {i+1}: {e}")
    
    print(f"✅ Setup complete: {len(created_agents)} agents, {conversation_count} conversations")
    return conversation_count > 0

def authenticate():
    """Authenticate and get JWT token"""
    global auth_token, test_user_id
    
    print("🔐 Authenticating with guest login...")
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_data = data.get("user", {})
            test_user_id = user_data.get("id")
            print(f"✅ Authentication successful. User ID: {test_user_id}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def generate_daily_report():
    """Generate a daily report for testing"""
    print("\n📊 Generating daily report for testing...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.post(
            f"{API_URL}/simulation/generate-daily-report",
            json={"manual": True},
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Daily report generated successfully")
            
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            if "report" in data:
                report = data["report"]
                report_id = report.get("id")
                print(f"📄 Report ID: {report_id}")
                return report_id, report
            elif "report_id" in data:
                report_id = data["report_id"]
                print(f"📄 Report ID from response: {report_id}")
                return report_id, None
            else:
                print("⚠️ Report data not included in response")
                # Try to get the latest report from reports list
                return "latest", data
        else:
            print(f"❌ Daily report generation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error generating daily report: {e}")
        return None, None

def get_latest_report():
    """Get the latest report from the reports list"""
    print(f"\n📖 Retrieving latest report from reports list")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/reports",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "reports" in data and data["reports"]:
                # Get the most recent report (first in list, assuming sorted by date)
                latest_report = data["reports"][0]
                report_id = latest_report.get("id")
                print(f"✅ Found latest report ID: {report_id}")
                return report_id
            else:
                print("❌ No reports found in response")
                return None
        else:
            print(f"❌ Failed to retrieve reports list: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving reports list: {e}")
        return None

def get_report_content(report_id):
    """Get the full content of a specific report"""
    print(f"\n📖 Retrieving report content for ID: {report_id}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/reports/{report_id}",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "report" in data:
                report = data["report"]
                content = report.get("content", "")
                print(f"✅ Retrieved report content ({len(content)} characters)")
                return content
            else:
                print("❌ No report content found in response")
                return None
        else:
            print(f"❌ Failed to retrieve report: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving report: {e}")
        return None

def analyze_text_contrast(content):
    """Analyze the HTML content for text contrast issues"""
    print("\n🎨 ANALYZING TEXT CONTRAST...")
    
    issues_found = []
    
    # Check for light text on light background patterns
    light_text_patterns = [
        r'color:\s*#[fF]{3,6}',  # White or very light colors
        r'color:\s*white',
        r'color:\s*#[eE]{3,6}',  # Very light gray
        r'color:\s*rgb\(25[0-5],\s*25[0-5],\s*25[0-5]\)',  # Very light RGB
    ]
    
    light_bg_patterns = [
        r'background-color:\s*#[fF]{3,6}',  # White or very light backgrounds
        r'background-color:\s*white',
        r'background-color:\s*#[eE]{3,6}',  # Very light gray backgrounds
    ]
    
    # Check for problematic combinations
    for light_text in light_text_patterns:
        if re.search(light_text, content, re.IGNORECASE):
            for light_bg in light_bg_patterns:
                if re.search(light_bg, content, re.IGNORECASE):
                    issues_found.append("Light text on light background detected")
                    break
    
    # Check for good contrast patterns (dark text)
    dark_text_patterns = [
        r'color:\s*#[0-5]{3,6}',  # Dark colors
        r'color:\s*black',
        r'color:\s*#333',
        r'color:\s*rgb\([0-9]{1,2},\s*[0-9]{1,2},\s*[0-9]{1,2}\)',  # Dark RGB
    ]
    
    good_contrast_found = False
    for pattern in dark_text_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            good_contrast_found = True
            break
    
    # Check for default text (no explicit color = usually dark)
    if not re.search(r'color:', content, re.IGNORECASE):
        good_contrast_found = True
        print("✅ Using default text color (typically dark)")
    
    if good_contrast_found and not issues_found:
        print("✅ TEXT CONTRAST: Good contrast detected (dark text)")
        return True
    elif issues_found:
        print("❌ TEXT CONTRAST: Issues found:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("⚠️ TEXT CONTRAST: Unable to determine contrast")
        return None

def analyze_double_icons(content):
    """Analyze the content for double icons, specifically in Strategic Developments section"""
    print("\n🚀 ANALYZING DOUBLE ICONS...")
    
    issues_found = []
    
    # Look for Strategic Developments section
    strategic_section_pattern = r'Strategic Developments.*?(?=<h[1-6]|$)'
    strategic_match = re.search(strategic_section_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if strategic_match:
        strategic_content = strategic_match.group(0)
        print("✅ Found Strategic Developments section")
        
        # Check for double rocket icons specifically
        double_rocket_patterns = [
            r'🚀\s*🚀',  # Two rockets with optional space
            r'🚀🚀',     # Two rockets directly together
        ]
        
        for pattern in double_rocket_patterns:
            matches = re.findall(pattern, strategic_content)
            if matches:
                issues_found.append(f"Double rocket icons found: {len(matches)} instances")
                print(f"❌ Found double rocket icons: {matches}")
        
        # Check for any double emoji patterns
        double_emoji_pattern = r'([\U0001F300-\U0001F9FF])\s*\1'
        double_emoji_matches = re.findall(double_emoji_pattern, strategic_content)
        if double_emoji_matches:
            for emoji in set(double_emoji_matches):
                issues_found.append(f"Double emoji found: {emoji}{emoji}")
                print(f"❌ Found double emoji: {emoji}{emoji}")
        
        if not issues_found:
            print("✅ DOUBLE ICONS: No double icons found in Strategic Developments section")
            return True
        else:
            print("❌ DOUBLE ICONS: Issues found:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False
    else:
        print("⚠️ Strategic Developments section not found")
        
        # Check for double icons in entire content
        double_emoji_pattern = r'([\U0001F300-\U0001F9FF])\s*\1'
        double_emoji_matches = re.findall(double_emoji_pattern, content)
        if double_emoji_matches:
            for emoji in set(double_emoji_matches):
                issues_found.append(f"Double emoji found: {emoji}{emoji}")
                print(f"❌ Found double emoji: {emoji}{emoji}")
        
        if not issues_found:
            print("✅ DOUBLE ICONS: No double icons found in content")
            return True
        else:
            print("❌ DOUBLE ICONS: Issues found:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False

def analyze_overall_formatting(content):
    """Analyze the overall HTML formatting and structure"""
    print("\n📋 ANALYZING OVERALL FORMATTING...")
    
    issues_found = []
    good_practices_found = []
    
    # Check for professional HTML structure
    if re.search(r'<html', content, re.IGNORECASE):
        good_practices_found.append("Proper HTML document structure")
    
    if re.search(r'<head', content, re.IGNORECASE):
        good_practices_found.append("HTML head section present")
    
    if re.search(r'<body', content, re.IGNORECASE):
        good_practices_found.append("HTML body section present")
    
    # Check for proper heading hierarchy
    headings = re.findall(r'<h([1-6])', content, re.IGNORECASE)
    if headings:
        good_practices_found.append(f"Proper heading structure (h1-h6): {len(headings)} headings")
    
    # Check for CSS styling
    if re.search(r'<style|style=', content, re.IGNORECASE):
        good_practices_found.append("CSS styling present")
    
    # Check for generic introductions (problematic patterns)
    generic_patterns = [
        r'This is a generic report',
        r'Lorem ipsum',
        r'Placeholder text',
        r'Sample content',
        r'Default report template'
    ]
    
    for pattern in generic_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues_found.append(f"Generic content found: {pattern}")
    
    # Check for markdown separators in HTML (should be converted)
    markdown_separators = [
        r'---+',  # Markdown horizontal rules
        r'===+',  # Markdown horizontal rules
        r'```',   # Code blocks
        r'###+',  # Markdown headers not converted
    ]
    
    for pattern in markdown_separators:
        matches = re.findall(pattern, content)
        if matches:
            issues_found.append(f"Markdown separators found (should be HTML): {len(matches)} instances")
    
    # Check for proper section organization
    sections = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', content, re.IGNORECASE)
    if len(sections) >= 3:
        good_practices_found.append(f"Well-organized content with {len(sections)} sections")
    
    # Print results
    if good_practices_found:
        print("✅ GOOD FORMATTING PRACTICES:")
        for practice in good_practices_found:
            print(f"   + {practice}")
    
    if issues_found:
        print("❌ FORMATTING ISSUES:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ OVERALL FORMATTING: Professional HTML structure maintained")
        return True

def main():
    """Main test execution function"""
    print("="*80)
    print("REPORT GENERATION IMPROVEMENTS TESTING")
    print("Testing fixes for: Text Contrast, Double Icons, Overall Formatting")
    print("="*80)
    
    # Step 1: Authenticate
    if not authenticate():
        print("❌ Authentication failed. Cannot proceed with testing.")
        return False
    
    # Step 1.5: Set up test data (agents and conversations)
    if not setup_test_data():
        print("❌ Failed to set up test data. Cannot proceed with report generation.")
        return False
    
    # Step 2: Generate a daily report
    report_id, report_data = generate_daily_report()
    if not report_id:
        print("❌ Failed to generate daily report. Cannot proceed with content analysis.")
        return False
    
    # If we got "latest" as report_id, get the actual latest report ID
    if report_id == "latest":
        report_id = get_latest_report()
        if not report_id:
            print("❌ Failed to get latest report ID. Cannot proceed with content analysis.")
            return False
    
    # Step 3: Get the full report content
    content = None
    if report_data and "content" in report_data:
        content = report_data["content"]
        print(f"✅ Using report content from generation response ({len(content)} characters)")
    else:
        content = get_report_content(report_id)
    
    if not content:
        print("❌ Failed to retrieve report content. Cannot proceed with analysis.")
        return False
    
    print(f"\n📄 REPORT CONTENT PREVIEW (first 500 chars):")
    print("-" * 60)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("-" * 60)
    
    # Step 4: Analyze the content for the specific issues
    print("\n" + "="*80)
    print("ANALYZING REPORT CONTENT FOR SPECIFIC ISSUES")
    print("="*80)
    
    # Test 1: Text Contrast
    contrast_result = analyze_text_contrast(content)
    
    # Test 2: Double Icons
    icons_result = analyze_double_icons(content)
    
    # Test 3: Overall Formatting
    formatting_result = analyze_overall_formatting(content)
    
    # Step 5: Summary
    print("\n" + "="*80)
    print("REPORT IMPROVEMENTS TEST SUMMARY")
    print("="*80)
    
    results = {
        "Text Contrast": contrast_result,
        "Double Icons": icons_result,
        "Overall Formatting": formatting_result
    }
    
    passed_tests = 0
    total_tests = 0
    
    for test_name, result in results.items():
        total_tests += 1
        if result is True:
            passed_tests += 1
            print(f"✅ {test_name}: PASSED")
        elif result is False:
            print(f"❌ {test_name}: FAILED")
        else:
            print(f"⚠️ {test_name}: INCONCLUSIVE")
    
    print(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL REPORT IMPROVEMENT FIXES ARE WORKING!")
        return True
    else:
        print("⚠️ Some report improvement issues may still exist.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)