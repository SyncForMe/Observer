#!/usr/bin/env python3
"""
QUICK REPORT GENERATION IMPROVEMENTS TEST
Testing the specific fixes for report generation improvements by using existing data.
"""

import requests
import json
import time
import os
import sys
import re
from dotenv import load_dotenv

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Global variables for auth testing
auth_token = None

def authenticate():
    """Authenticate and get JWT token"""
    global auth_token
    
    try:
        response = requests.post(f"{API_URL}/auth/test-login")
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            print(f"✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def check_existing_reports():
    """Check if there are existing reports we can analyze"""
    print("\n📊 Checking for existing reports...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/reports", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "reports" in data and data["reports"]:
                reports = data["reports"]
                print(f"✅ Found {len(reports)} existing reports")
                return reports[0]["id"]  # Return the first (most recent) report ID
            else:
                print("⚠️ No existing reports found")
                return None
        else:
            print(f"❌ Failed to get reports: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking reports: {e}")
        return None

def generate_new_report():
    """Try to generate a new report"""
    print("\n📊 Attempting to generate new report...")
    
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
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("success"):
                print("✅ Report generated successfully")
                # Check for report ID in various possible locations
                report_id = data.get("report_id") or data.get("id")
                if "report" in data:
                    report_id = data["report"].get("id")
                return report_id
            else:
                print(f"❌ Report generation failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

def get_report_content(report_id):
    """Get the content of a specific report"""
    print(f"\n📖 Retrieving report content for ID: {report_id}")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/reports/{report_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "report" in data:
                content = data["report"].get("content", "")
                print(f"✅ Retrieved report content ({len(content)} characters)")
                return content
            else:
                print("❌ No report content found")
                return None
        else:
            print(f"❌ Failed to retrieve report: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving report: {e}")
        return None

def analyze_text_contrast(content):
    """Analyze text contrast in the report content"""
    print("\n🎨 ANALYZING TEXT CONTRAST...")
    
    # Check for good contrast indicators
    good_contrast_indicators = [
        r'color:\s*#[0-5]{3}',  # Dark colors
        r'color:\s*black',
        r'color:\s*#333',
        r'color:\s*rgb\([0-9]{1,2},\s*[0-9]{1,2},\s*[0-9]{1,2}\)',  # Dark RGB
    ]
    
    # Check for poor contrast indicators
    poor_contrast_indicators = [
        r'color:\s*#[fF]{3,6}.*background.*#[fF]{3,6}',  # Light on light
        r'color:\s*white.*background.*white',
    ]
    
    has_good_contrast = False
    has_poor_contrast = False
    
    for pattern in good_contrast_indicators:
        if re.search(pattern, content, re.IGNORECASE):
            has_good_contrast = True
            break
    
    for pattern in poor_contrast_indicators:
        if re.search(pattern, content, re.IGNORECASE):
            has_poor_contrast = True
            break
    
    # If no explicit color styling, assume default (good contrast)
    if not re.search(r'color:', content, re.IGNORECASE):
        has_good_contrast = True
        print("✅ Using default text color (good contrast)")
    
    if has_good_contrast and not has_poor_contrast:
        print("✅ TEXT CONTRAST: Good contrast detected")
        return True
    elif has_poor_contrast:
        print("❌ TEXT CONTRAST: Poor contrast detected")
        return False
    else:
        print("⚠️ TEXT CONTRAST: Unable to determine")
        return None

def analyze_double_icons(content):
    """Analyze for double icons, especially in Strategic Developments"""
    print("\n🚀 ANALYZING DOUBLE ICONS...")
    
    # Look for double emoji patterns
    double_emoji_pattern = r'([\U0001F300-\U0001F9FF])\s*\1'
    double_emojis = re.findall(double_emoji_pattern, content)
    
    # Specifically check for double rockets
    double_rockets = re.findall(r'🚀\s*🚀', content)
    
    if double_rockets:
        print(f"❌ DOUBLE ICONS: Found {len(double_rockets)} double rocket icons")
        return False
    elif double_emojis:
        print(f"❌ DOUBLE ICONS: Found double emojis: {set(double_emojis)}")
        return False
    else:
        print("✅ DOUBLE ICONS: No double icons found")
        return True

def analyze_formatting(content):
    """Analyze overall formatting quality"""
    print("\n📋 ANALYZING FORMATTING...")
    
    issues = []
    good_practices = []
    
    # Check for HTML structure
    if re.search(r'<html|<body|<head', content, re.IGNORECASE):
        good_practices.append("Proper HTML structure")
    
    # Check for headings
    headings = re.findall(r'<h[1-6]', content, re.IGNORECASE)
    if headings:
        good_practices.append(f"Structured headings ({len(headings)} found)")
    
    # Check for markdown artifacts (should be converted to HTML)
    if re.search(r'#{2,}|---+|```', content):
        issues.append("Markdown artifacts found (should be HTML)")
    
    # Check for generic content
    if re.search(r'lorem ipsum|placeholder|generic|sample', content, re.IGNORECASE):
        issues.append("Generic placeholder content found")
    
    if issues:
        print("❌ FORMATTING ISSUES:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ FORMATTING: Professional structure maintained")
        if good_practices:
            for practice in good_practices:
                print(f"   + {practice}")
        return True

def main():
    """Main test function"""
    print("="*80)
    print("QUICK REPORT IMPROVEMENTS TEST")
    print("Testing: Text Contrast, Double Icons, Overall Formatting")
    print("="*80)
    
    # Authenticate
    if not authenticate():
        return False
    
    # Try to find existing report first
    report_id = check_existing_reports()
    
    # If no existing reports, try to generate one
    if not report_id:
        report_id = generate_new_report()
    
    if not report_id:
        print("❌ No reports available for testing")
        return False
    
    # Get report content
    content = get_report_content(report_id)
    if not content:
        print("❌ Failed to get report content")
        return False
    
    print(f"\n📄 ANALYZING REPORT CONTENT ({len(content)} characters)")
    print("="*60)
    
    # Show a preview of the content
    preview = content[:800] + "..." if len(content) > 800 else content
    print(preview)
    print("="*60)
    
    # Run analyses
    contrast_result = analyze_text_contrast(content)
    icons_result = analyze_double_icons(content)
    formatting_result = analyze_formatting(content)
    
    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    results = [
        ("Text Contrast", contrast_result),
        ("Double Icons", icons_result),
        ("Overall Formatting", formatting_result)
    ]
    
    passed = 0
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
        else:
            print(f"⚠️ {test_name}: INCONCLUSIVE")
    
    print(f"\nOVERALL: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL REPORT IMPROVEMENT FIXES VERIFIED!")
        return True
    else:
        print("⚠️ Some issues may still exist")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)