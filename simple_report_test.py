#!/usr/bin/env python3
"""
SIMPLE MARKDOWN-TO-HTML REPORT TEST
Direct test of the daily report generation to check for markdown-to-HTML fix
"""

import requests
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_report_generation():
    """Test daily report generation and HTML formatting"""
    print("🔍 TESTING DAILY REPORT GENERATION AND HTML FORMATTING")
    print("="*80)
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    auth_data = auth_response.json()
    token = auth_data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Generate daily report
    print("\n2. Generating daily report...")
    report_response = requests.post(
        f"{API_URL}/simulation/generate-daily-report",
        json={"manual": True},
        headers=headers
    )
    
    print(f"Status: {report_response.status_code}")
    
    if report_response.status_code != 200:
        print(f"❌ Report generation failed: {report_response.text}")
        return False
    
    report_data = report_response.json()
    print(f"Response: {json.dumps(report_data, indent=2)}")
    
    success = report_data.get("success", False)
    if not success:
        print(f"❌ Report generation unsuccessful: {report_data.get('message', 'Unknown error')}")
        return False
    
    print("✅ Report generation successful")
    
    # Step 3: Get report content
    report = report_data.get("report", {})
    content = report.get("content", "")
    
    if not content:
        print("❌ No content in report")
        return False
    
    print("✅ Report content available")
    print(f"Content length: {len(content)} characters")
    
    # Step 4: Analyze HTML formatting
    print(f"\n4. Analyzing HTML formatting...")
    
    # Check for literal ** markdown
    markdown_asterisks = re.findall(r'\*\*[^*]+\*\*', content)
    print(f"Literal ** markdown found: {len(markdown_asterisks)}")
    if markdown_asterisks:
        print("❌ ISSUE: Found literal ** markdown syntax!")
        for i, match in enumerate(markdown_asterisks[:5], 1):
            print(f"   {i}. {match}")
    else:
        print("✅ No literal ** markdown syntax found")
    
    # Check for HTML strong tags
    strong_tags = re.findall(r'<strong>[^<]+</strong>', content)
    print(f"HTML <strong> tags found: {len(strong_tags)}")
    if strong_tags:
        print("✅ Proper HTML <strong> tags found")
        for i, match in enumerate(strong_tags[:5], 1):
            print(f"   {i}. {match}")
    else:
        print("❌ No HTML <strong> tags found")
    
    # Check HTML structure
    html_elements = {
        'div': len(re.findall(r'<div[^>]*>', content)),
        'h1': len(re.findall(r'<h1[^>]*>', content)),
        'h2': len(re.findall(r'<h2[^>]*>', content)),
        'strong': len(strong_tags)
    }
    
    print(f"HTML elements: {html_elements}")
    
    # Step 5: Show content preview
    print(f"\n5. Content preview (first 1000 characters):")
    print("-" * 80)
    print(content[:1000])
    print("-" * 80)
    
    # Step 6: Assessment
    print(f"\n6. ASSESSMENT:")
    
    has_html_structure = sum(html_elements.values()) > 5
    has_strong_tags = len(strong_tags) > 0
    no_markdown_asterisks = len(markdown_asterisks) == 0
    
    print(f"✅ HTML structure present: {has_html_structure}")
    print(f"✅ Strong tags present: {has_strong_tags}")
    print(f"✅ No markdown asterisks: {no_markdown_asterisks}")
    
    if has_html_structure and has_strong_tags and no_markdown_asterisks:
        print("\n🎉 SUCCESS: Markdown-to-HTML fix is working!")
        print("   - Reports use proper HTML <strong> tags")
        print("   - No literal ** markdown syntax found")
        print("   - Bold formatting will render correctly")
        return True
    else:
        print("\n❌ ISSUE: Markdown-to-HTML fix needs attention!")
        print("   - The user's bold formatting issue may still exist")
        return False

if __name__ == "__main__":
    success = test_report_generation()
    exit(0 if success else 1)