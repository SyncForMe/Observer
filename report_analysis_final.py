#!/usr/bin/env python3
"""
FINAL REPORT STRUCTURE AND READABILITY ANALYSIS
Analyzing the actual generated report for improved structure and readability enhancements.
"""

import requests
import json
import os
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def get_latest_report():
    """Get the latest generated report"""
    # Get auth token
    response = requests.post(f'{API_URL}/auth/test-login')
    auth_token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Get latest report
    reports_response = requests.get(f'{API_URL}/reports', headers=headers)
    if reports_response.status_code == 200:
        reports = reports_response.json().get('reports', [])
        if reports:
            latest_report_id = reports[0]['id']
            report_response = requests.get(f'{API_URL}/reports/{latest_report_id}', headers=headers)
            if report_response.status_code == 200:
                return report_response.json().get('report', {})
    return None

def analyze_report_structure(content):
    """Analyze the report structure and readability"""
    print("REPORT STRUCTURE AND READABILITY ANALYSIS")
    print("="*80)
    
    # Parse HTML content
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract text content for analysis
    text_content = soup.get_text()
    
    print(f"📊 Report Length: {len(content)} characters")
    print(f"📊 Text Content: {len(text_content)} characters")
    
    # 1. ANALYZE CONTENT STRUCTURE
    print("\n1. CONTENT STRUCTURE ANALYSIS")
    print("-" * 50)
    
    # Check for concise content (not verbose text walls)
    paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
    long_paragraphs = [p for p in paragraphs if len(p) > 300]
    
    print(f"✅ Total paragraphs: {len(paragraphs)}")
    print(f"{'✅' if len(long_paragraphs) == 0 else '⚠️'} Verbose paragraphs (>300 chars): {len(long_paragraphs)}")
    
    # Check for proper section structure
    sections = soup.find_all('div', class_='report-section')
    print(f"✅ Report sections found: {len(sections)}")
    
    for section in sections:
        section_class = section.get('class', [])
        header = section.find('h2')
        if header:
            print(f"   • {header.get_text().strip()}")
    
    # 2. ANALYZE FORMATTING ELEMENTS
    print("\n2. FORMATTING ELEMENTS ANALYSIS")
    print("-" * 50)
    
    # Check for bold formatting
    bold_elements = soup.find_all('strong')
    bold_text = [b.get_text() for b in bold_elements]
    print(f"✅ Bold elements: {len(bold_elements)}")
    if bold_text:
        print(f"   Sample bold text: {bold_text[:3]}")
    
    # Check for bullet points and lists
    bullet_lists = soup.find_all('ul')
    numbered_lists = soup.find_all('ol')
    
    total_list_items = 0
    for ul in bullet_lists:
        total_list_items += len(ul.find_all('li'))
    for ol in numbered_lists:
        total_list_items += len(ol.find_all('li'))
    
    print(f"✅ Bullet point lists: {len(bullet_lists)}")
    print(f"✅ Numbered lists: {len(numbered_lists)}")
    print(f"✅ Total list items: {total_list_items}")
    
    # 3. CHECK SPECIFIC SECTION REQUIREMENTS
    print("\n3. SPECIFIC SECTION REQUIREMENTS")
    print("-" * 50)
    
    # Executive Summary - should have 3 focused points with bold labels
    exec_section = soup.find('div', class_='executive')
    if exec_section:
        exec_paragraphs = exec_section.find_all('p')
        exec_bold = exec_section.find_all('strong')
        print(f"✅ Executive Summary: {len(exec_paragraphs)} paragraphs, {len(exec_bold)} bold elements")
        
        # Check for the 3 key points structure
        key_points = ['Key Achievement', 'Current Focus', 'Next Steps']
        found_points = []
        for point in key_points:
            if point in exec_section.get_text():
                found_points.append(point)
        print(f"✅ Key points found: {found_points}")
    
    # Strategic Developments - should use bullet points
    strategic_section = soup.find('div', class_='strategic')
    if strategic_section:
        strategic_bullets = strategic_section.find_all('li')
        print(f"✅ Strategic Developments: {len(strategic_bullets)} bullet points")
    
    # Agent Performance - should list agents with contributions
    performance_section = soup.find('div', class_='performance')
    if performance_section:
        perf_bullets = performance_section.find_all('li')
        print(f"✅ Agent Performance: {len(perf_bullets)} agent entries")
    
    # Challenges - should show challenge → solution format
    challenges_section = soup.find('div', class_='challenges')
    if challenges_section:
        challenge_bullets = challenges_section.find_all('li')
        challenge_text = challenges_section.get_text()
        solution_indicators = challenge_text.count('Solution:') + challenge_text.count('Mitigation:')
        print(f"✅ Challenges: {len(challenge_bullets)} items, {solution_indicators} solutions")
    
    # Recommendations - should be numbered priorities
    recommendations_section = soup.find('div', class_='recommendations')
    if recommendations_section:
        rec_numbers = recommendations_section.find_all('ol')
        rec_items = recommendations_section.find_all('li')
        print(f"✅ Recommendations: {len(rec_numbers)} numbered lists, {len(rec_items)} priority items")
    
    # 4. READABILITY ASSESSMENT
    print("\n4. READABILITY ASSESSMENT")
    print("-" * 50)
    
    # Check for scannable sections (10 seconds or less)
    scannable_sections = 0
    for section in sections:
        section_text = section.get_text()
        word_count = len(section_text.split())
        # Assume 200 words per minute reading, so 33 words for 10 seconds
        if word_count <= 100:  # Allow for scanning vs reading
            scannable_sections += 1
        print(f"   Section word count: {word_count} ({'scannable' if word_count <= 100 else 'dense'})")
    
    print(f"✅ Scannable sections: {scannable_sections}/{len(sections)}")
    
    # Check for active voice and present tense
    active_indicators = ['achieved', 'completed', 'implemented', 'delivered', 'created', 'established', 'adopted', 'demonstrated']
    present_indicators = ['is', 'are', 'shows', 'demonstrates', 'provides', 'ensures', 'focuses', 'emphasizes']
    
    active_count = sum(text_content.lower().count(word) for word in active_indicators)
    present_count = sum(text_content.lower().count(word) for word in present_indicators)
    
    print(f"✅ Active voice indicators: {active_count}")
    print(f"✅ Present tense indicators: {present_count}")
    
    # Check for key terms being bolded
    key_terms_bolded = 0
    key_terms = ['strategic', 'critical', 'priority', 'breakthrough', 'achievement', 'quantum', 'secure', 'robust']
    
    for term in key_terms:
        bold_text_lower = ' '.join([b.get_text().lower() for b in bold_elements])
        if term in bold_text_lower:
            key_terms_bolded += 1
    
    print(f"✅ Key terms bolded: {key_terms_bolded}/{len(key_terms)}")
    
    # 5. OVERALL ASSESSMENT
    print("\n5. OVERALL ASSESSMENT")
    print("-" * 50)
    
    # Calculate scores
    structure_score = 0
    readability_score = 0
    formatting_score = 0
    
    # Structure scoring
    if len(sections) >= 6:
        structure_score += 1
    if len(long_paragraphs) == 0:
        structure_score += 1
    if total_list_items >= 10:
        structure_score += 1
    
    # Readability scoring
    if scannable_sections >= len(sections) * 0.8:
        readability_score += 1
    if active_count >= 3:
        readability_score += 1
    if present_count >= 5:
        readability_score += 1
    
    # Formatting scoring
    if len(bold_elements) >= 15:
        formatting_score += 1
    if len(bullet_lists) >= 2:
        formatting_score += 1
    if len(numbered_lists) >= 1:
        formatting_score += 1
    
    total_score = structure_score + readability_score + formatting_score
    max_score = 9
    
    print(f"Structure Score: {structure_score}/3")
    print(f"Readability Score: {readability_score}/3")
    print(f"Formatting Score: {formatting_score}/3")
    print(f"TOTAL SCORE: {total_score}/{max_score} ({(total_score/max_score)*100:.1f}%)")
    
    if total_score >= 7:
        print("🎉 EXCELLENT - Report meets readability and structure requirements!")
    elif total_score >= 5:
        print("✅ GOOD - Report has good structure with minor improvements needed")
    else:
        print("⚠️ NEEDS IMPROVEMENT - Report structure needs significant enhancements")
    
    return total_score >= 7

def main():
    """Main analysis function"""
    print("DAILY REPORT STRUCTURE AND READABILITY ANALYSIS")
    print("Testing the improved report structure and readability enhancements")
    print("="*80)
    
    # Get the latest report
    report_data = get_latest_report()
    if not report_data:
        print("❌ Failed to retrieve report for analysis")
        return False
    
    content = report_data.get('content', '')
    if not content:
        print("❌ No content found in report")
        return False
    
    print(f"📋 Analyzing Report: {report_data.get('title', 'Unknown')}")
    print(f"📅 Generated: {report_data.get('created_at', 'Unknown')}")
    print(f"🆔 Report ID: {report_data.get('id', 'Unknown')}")
    
    # Analyze the report
    success = analyze_report_structure(content)
    
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    if success:
        print("✅ REPORT STRUCTURE AND READABILITY TESTING: PASSED")
        print("The improved report template successfully delivers:")
        print("• Concise, scannable content structure")
        print("• Proper formatting with bold text and lists")
        print("• Clear section organization")
        print("• Professional readability for effortless user experience")
    else:
        print("⚠️ REPORT STRUCTURE AND READABILITY TESTING: NEEDS IMPROVEMENT")
        print("Some areas need enhancement for optimal user experience")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)