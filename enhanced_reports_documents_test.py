#!/usr/bin/env python3
"""
ENHANCED REPORTS AND DOCUMENTS SYSTEM TESTING
Testing the complete enhanced reports and documents system as requested in the review.

Focus Areas:
1. Enhanced Report Generation with professional HTML format
2. Document Generation System with auto-generation during conversations
3. Document Creation Logic with strategic document creation
4. Complete Workflow testing with visual quality assessment
5. PDF download functionality testing
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
import re

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
    "tests": []
}

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []
created_document_ids = []
created_report_ids = []

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

def setup_authentication():
    """Set up authentication for testing"""
    global auth_token, test_user_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION SETUP")
    print("="*80)
    
    # Test guest login
    guest_test, guest_response = run_test(
        "Guest Login Setup",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if guest_test and guest_response:
        auth_token = guest_response.get("access_token")
        user_data = guest_response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication setup successful. User ID: {test_user_id}")
        return True
    else:
        print("❌ Authentication setup failed")
        return False

def setup_test_agents():
    """Create test agents for conversation generation"""
    global created_agent_ids
    
    print("\n" + "="*80)
    print("TEST AGENTS SETUP")
    print("="*80)
    
    # Create diverse agents for rich conversations
    agents_data = [
        {
            "name": "Dr. Sarah Quantum",
            "archetype": "scientist",
            "goal": "Advance quantum computing research",
            "expertise": "Quantum physics and cryptography",
            "background": "PhD in Quantum Physics from MIT, 10 years experience in quantum computing",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Marcus Engineering",
            "archetype": "leader",
            "goal": "Lead technical implementation projects",
            "expertise": "Systems engineering and project management",
            "background": "Senior Engineering Manager with 15 years in tech leadership",
            "personality": {
                "extroversion": 8,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Dr. Alex Skeptic",
            "archetype": "skeptic",
            "goal": "Ensure rigorous analysis and risk assessment",
            "expertise": "Risk analysis and quality assurance",
            "background": "Former NASA quality assurance specialist",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        }
    ]
    
    for i, agent_data in enumerate(agents_data, 1):
        create_test, create_response = run_test(
            f"Create Test Agent {i}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True,
            expected_keys=["id", "name", "archetype"]
        )
        
        if create_test and create_response:
            agent_id = create_response.get("id")
            if agent_id:
                created_agent_ids.append(agent_id)
                print(f"✅ Created agent {agent_data['name']} with ID: {agent_id}")
            else:
                print(f"❌ No agent ID returned for {agent_data['name']}")
                return False
        else:
            print(f"❌ Failed to create agent {agent_data['name']}")
            return False
    
    print(f"✅ Successfully created {len(created_agent_ids)} test agents")
    return True

def test_enhanced_report_generation():
    """Test Enhanced Report Generation with professional HTML format"""
    print("\n" + "="*80)
    print("1. ENHANCED REPORT GENERATION TESTING")
    print("="*80)
    
    print("🔍 Testing enhanced report generation with professional HTML format")
    print("Expected: Reports with distinct visual sections, colors, and no generic intros")
    
    # Test daily report generation
    daily_report_test, daily_report_response = run_test(
        "Generate Enhanced Daily Report",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True,
        expected_keys=["success", "report"]
    )
    
    if not daily_report_test or not daily_report_response:
        print("❌ Enhanced daily report generation failed")
        return False
    
    if not daily_report_response.get("success"):
        print("❌ Daily report generation returned success=false")
        return False
    
    report_data = daily_report_response.get("report", {})
    report_content = report_data.get("content", "")
    
    if not report_content:
        print("❌ No report content generated")
        return False
    
    print(f"✅ Generated report with {len(report_content)} characters")
    
    # Test HTML format and professional presentation
    html_checks = {
        "HTML Structure": "<html>" in report_content and "</html>" in report_content,
        "CSS Styling": "<style>" in report_content or "style=" in report_content,
        "Visual Sections": "<div" in report_content or "<section" in report_content,
        "Professional Headers": any(header in report_content for header in ["<h1>", "<h2>", "<h3>"]),
        "Color Usage": any(color in report_content.lower() for color in ["color:", "background", "#", "rgb"]),
        "No Generic Intro": not any(generic in report_content.lower() for generic in ["welcome to", "this report", "generated report"]),
        "No Markdown Separators": "---" not in report_content and "***" not in report_content
    }
    
    print("\n--- HTML Format Quality Assessment ---")
    for check_name, passed in html_checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {'PASSED' if passed else 'FAILED'}")
    
    # Store report ID for later testing
    report_id = report_data.get("id")
    if report_id:
        created_report_ids.append(report_id)
        print(f"✅ Report stored with ID: {report_id}")
    
    # Test report retrieval
    if report_id:
        get_report_test, get_report_response = run_test(
            "Retrieve Generated Report",
            f"/reports/{report_id}",
            method="GET",
            auth=True,
            expected_keys=["success", "report"]
        )
        
        if get_report_test and get_report_response:
            retrieved_report = get_report_response.get("report", {})
            retrieved_content = retrieved_report.get("content", "")
            
            if retrieved_content == report_content:
                print("✅ Report content matches between generation and retrieval")
            else:
                print("❌ Report content mismatch between generation and retrieval")
                return False
        else:
            print("❌ Failed to retrieve generated report")
            return False
    
    # Calculate overall HTML quality score
    html_score = sum(html_checks.values()) / len(html_checks) * 100
    print(f"\n📊 HTML Quality Score: {html_score:.1f}%")
    
    if html_score >= 80:
        print("✅ Enhanced report generation meets professional HTML standards")
        return True
    else:
        print("❌ Enhanced report generation needs improvement in HTML formatting")
        return False

def test_document_generation_system():
    """Test Document Generation System with auto-generation during conversations"""
    print("\n" + "="*80)
    print("2. DOCUMENT GENERATION SYSTEM TESTING")
    print("="*80)
    
    print("🔍 Testing auto-generation of documents during conversation generation")
    print("Expected: Documents created automatically with professional HTML formatting")
    
    # First, check initial document count
    initial_docs_test, initial_docs_response = run_test(
        "Get Initial Document Count",
        "/documents",
        method="GET",
        auth=True
    )
    
    initial_doc_count = len(initial_docs_response) if initial_docs_response else 0
    print(f"📊 Initial document count: {initial_doc_count}")
    
    # Generate multiple conversation rounds to trigger document creation
    conversation_rounds = 3
    generated_conversations = []
    
    for round_num in range(1, conversation_rounds + 1):
        print(f"\n--- Conversation Round {round_num} ---")
        
        conv_test, conv_response = run_test(
            f"Generate Conversation Round {round_num}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True,
            expected_keys=["message", "conversation"]
        )
        
        if conv_test and conv_response:
            conversation = conv_response.get("conversation", {})
            conv_id = conversation.get("id")
            messages = conversation.get("messages", [])
            
            print(f"✅ Generated conversation {conv_id} with {len(messages)} messages")
            generated_conversations.append(conv_id)
            
            # Wait a moment for potential document generation
            time.sleep(2)
        else:
            print(f"❌ Failed to generate conversation round {round_num}")
            return False
    
    # Check if documents were auto-generated
    final_docs_test, final_docs_response = run_test(
        "Get Final Document Count",
        "/documents",
        method="GET",
        auth=True
    )
    
    final_doc_count = len(final_docs_response) if final_docs_response else 0
    new_documents = final_doc_count - initial_doc_count
    
    print(f"📊 Final document count: {final_doc_count}")
    print(f"📊 New documents created: {new_documents}")
    
    if new_documents > 0:
        print(f"✅ Auto-document generation working: {new_documents} documents created")
        
        # Analyze the newly created documents
        if final_docs_response:
            recent_docs = final_docs_response[-new_documents:] if new_documents <= len(final_docs_response) else final_docs_response
            
            print("\n--- Document Quality Analysis ---")
            for i, doc in enumerate(recent_docs, 1):
                doc_id = doc.get("id")
                metadata = doc.get("metadata", {})
                content = doc.get("content", "")
                
                print(f"\nDocument {i}:")
                print(f"  ID: {doc_id}")
                print(f"  Title: {metadata.get('title', 'N/A')}")
                print(f"  Category: {metadata.get('category', 'N/A')}")
                print(f"  Content Length: {len(content)} characters")
                
                # Test professional HTML formatting
                html_quality = {
                    "HTML Structure": "<html>" in content or "<div>" in content,
                    "Professional Styling": "<style>" in content or "style=" in content,
                    "Structured Content": any(tag in content for tag in ["<h1>", "<h2>", "<h3>", "<p>", "<ul>", "<ol>"]),
                    "Visual Elements": any(element in content.lower() for element in ["color:", "background", "border", "margin", "padding"])
                }
                
                quality_score = sum(html_quality.values()) / len(html_quality) * 100
                print(f"  HTML Quality Score: {quality_score:.1f}%")
                
                for check, passed in html_quality.items():
                    status = "✅" if passed else "❌"
                    print(f"    {status} {check}")
                
                # Store document ID for cleanup
                if doc_id:
                    created_document_ids.append(doc_id)
        
        return True
    else:
        print("❌ No documents were auto-generated during conversations")
        print("🔍 This could indicate:")
        print("   1. Document creation logic is not triggered")
        print("   2. Conversation content doesn't meet document creation criteria")
        print("   3. Document creation system is disabled")
        return False

def test_document_creation_logic():
    """Test Document Creation Logic with strategic document creation"""
    print("\n" + "="*80)
    print("3. DOCUMENT CREATION LOGIC TESTING")
    print("="*80)
    
    print("🔍 Testing strategic document creation based on conversation context")
    print("Expected: Different document types based on conversation content")
    
    # Test manual document creation with different types
    document_types = [
        {
            "title": "Quantum Computing Research Protocol",
            "category": "Protocol",
            "description": "Research protocol for quantum computing experiments",
            "content": """<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; background: #f8f9fa; }
        .highlight { background: #e3f2fd; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Quantum Computing Research Protocol</h1>
        <p>Strategic research framework for quantum computing advancement</p>
    </div>
    
    <div class="section">
        <h2>Research Objectives</h2>
        <ul>
            <li>Develop quantum error correction protocols</li>
            <li>Improve qubit coherence times</li>
            <li>Optimize quantum gate operations</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Methodology</h2>
        <div class="highlight">
            <p>Our approach focuses on systematic testing of quantum systems with emphasis on scalability and error mitigation.</p>
        </div>
    </div>
</body>
</html>""",
            "keywords": ["quantum", "research", "protocol"],
            "authors": ["Dr. Sarah Quantum"]
        },
        {
            "title": "Project Implementation Roadmap",
            "category": "Training",
            "description": "Training document for project implementation",
            "content": """<html>
<head>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .title { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .phase { background: linear-gradient(90deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 15px; margin: 15px 0; border-radius: 8px; }
        .milestone { background: #dff0d8; border: 1px solid #d6e9c6; padding: 10px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Project Implementation Roadmap</h1>
        
        <div class="phase">
            <h2>Phase 1: Planning & Design</h2>
            <p>Strategic planning and system architecture design</p>
        </div>
        
        <div class="milestone">
            <h3>Key Milestones</h3>
            <ul>
                <li>Requirements gathering complete</li>
                <li>Architecture design approved</li>
                <li>Resource allocation finalized</li>
            </ul>
        </div>
        
        <div class="phase">
            <h2>Phase 2: Implementation</h2>
            <p>Core system development and testing</p>
        </div>
    </div>
</body>
</html>""",
            "keywords": ["implementation", "roadmap", "training"],
            "authors": ["Marcus Engineering"]
        }
    ]
    
    created_docs = []
    
    for doc_type in document_types:
        create_test, create_response = run_test(
            f"Create {doc_type['category']} Document",
            "/documents/create",
            method="POST",
            data=doc_type,
            auth=True,
            expected_keys=["success", "document_id"]
        )
        
        if create_test and create_response:
            doc_id = create_response.get("document_id")
            if doc_id:
                created_docs.append({
                    "id": doc_id,
                    "type": doc_type["category"],
                    "title": doc_type["title"]
                })
                created_document_ids.append(doc_id)
                print(f"✅ Created {doc_type['category']} document: {doc_id}")
            else:
                print(f"❌ No document ID returned for {doc_type['category']}")
                return False
        else:
            print(f"❌ Failed to create {doc_type['category']} document")
            return False
    
    # Test document accessibility via /api/documents endpoint
    docs_test, docs_response = run_test(
        "Access Documents via API",
        "/documents",
        method="GET",
        auth=True
    )
    
    if docs_test and docs_response:
        accessible_docs = [doc for doc in docs_response if doc.get("id") in [d["id"] for d in created_docs]]
        print(f"✅ {len(accessible_docs)} documents accessible via /api/documents")
        
        # Verify document structure and content
        for doc in accessible_docs:
            doc_id = doc.get("id")
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            print(f"\nDocument Analysis: {doc_id}")
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Category: {metadata.get('category', 'N/A')}")
            print(f"  Content Length: {len(content)} characters")
            
            # Check professional formatting
            formatting_checks = {
                "HTML Structure": "<html>" in content and "</html>" in content,
                "CSS Styling": "<style>" in content,
                "Visual Design": any(style in content.lower() for style in ["background:", "color:", "border:", "gradient"]),
                "Structured Layout": any(tag in content for tag in ["<div", "<section", "<header"]),
                "Typography": "font-family" in content.lower(),
                "Color Scheme": any(color in content for color in ["#", "rgb", "rgba"])
            }
            
            formatting_score = sum(formatting_checks.values()) / len(formatting_checks) * 100
            print(f"  Professional Formatting Score: {formatting_score:.1f}%")
            
            for check, passed in formatting_checks.items():
                status = "✅" if passed else "❌"
                print(f"    {status} {check}")
    else:
        print("❌ Failed to access documents via API")
        return False
    
    print(f"\n✅ Document creation logic test completed: {len(created_docs)} documents created")
    return True

def test_document_pdf_download():
    """Test Document PDF Download functionality"""
    print("\n" + "="*80)
    print("4. DOCUMENT PDF DOWNLOAD TESTING")
    print("="*80)
    
    print("🔍 Testing PDF download functionality for documents")
    
    if not created_document_ids:
        print("❌ No documents available for PDF testing")
        return False
    
    # Test PDF download for the first created document
    test_doc_id = created_document_ids[0]
    
    pdf_test, pdf_response = run_test(
        "Download Document as PDF",
        f"/documents/{test_doc_id}/pdf",
        method="GET",
        auth=True,
        expected_status=200
    )
    
    if pdf_test:
        print("✅ PDF download endpoint is accessible")
        
        # Check if response is actually a PDF (binary content)
        if pdf_response and isinstance(pdf_response, dict):
            # If we get JSON, it might be an error or redirect
            print("⚠️ PDF endpoint returned JSON instead of binary PDF")
            print(f"Response: {json.dumps(pdf_response, indent=2)}")
            return False
        else:
            print("✅ PDF download appears to return binary content")
            return True
    else:
        print("❌ PDF download failed")
        
        # Test if PDF generation endpoint exists
        pdf_gen_test, pdf_gen_response = run_test(
            "Generate PDF for Document",
            f"/documents/{test_doc_id}/generate-pdf",
            method="POST",
            auth=True
        )
        
        if pdf_gen_test:
            print("✅ PDF generation endpoint exists")
        else:
            print("❌ PDF generation endpoint not found")
        
        return False

def test_complete_workflow():
    """Test Complete Workflow: Generate conversation → Create documents → Access reports"""
    print("\n" + "="*80)
    print("5. COMPLETE WORKFLOW TESTING")
    print("="*80)
    
    print("🔍 Testing complete workflow from conversation to documents and reports")
    print("Expected: End-to-end functionality with professional presentation")
    
    # Step 1: Generate a conversation round
    print("\n--- Step 1: Generate Conversation ---")
    workflow_conv_test, workflow_conv_response = run_test(
        "Workflow Conversation Generation",
        "/conversation/generate",
        method="POST",
        auth=True,
        measure_time=True,
        expected_keys=["message", "conversation"]
    )
    
    if not workflow_conv_test:
        print("❌ Workflow conversation generation failed")
        return False
    
    conversation = workflow_conv_response.get("conversation", {})
    conv_messages = conversation.get("messages", [])
    print(f"✅ Generated conversation with {len(conv_messages)} messages")
    
    # Step 2: Check if documents appear in /api/documents
    print("\n--- Step 2: Check Document Creation ---")
    time.sleep(3)  # Wait for potential document creation
    
    workflow_docs_test, workflow_docs_response = run_test(
        "Workflow Document Check",
        "/documents",
        method="GET",
        auth=True
    )
    
    if workflow_docs_test and workflow_docs_response:
        doc_count = len(workflow_docs_response)
        print(f"✅ Found {doc_count} documents in system")
        
        # Check for recent documents (created in last few minutes)
        recent_docs = []
        current_time = datetime.utcnow()
        
        for doc in workflow_docs_response:
            metadata = doc.get("metadata", {})
            created_at = metadata.get("created_at")
            if created_at:
                try:
                    # Parse the created_at timestamp
                    if isinstance(created_at, str):
                        doc_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        doc_time = created_at
                    
                    # Check if document was created in last 10 minutes
                    time_diff = (current_time - doc_time.replace(tzinfo=None)).total_seconds()
                    if time_diff < 600:  # 10 minutes
                        recent_docs.append(doc)
                except:
                    pass
        
        if recent_docs:
            print(f"✅ Found {len(recent_docs)} recently created documents")
        else:
            print("⚠️ No recently created documents found")
    else:
        print("❌ Failed to check documents")
        return False
    
    # Step 3: Generate and verify reports
    print("\n--- Step 3: Generate Reports ---")
    workflow_report_test, workflow_report_response = run_test(
        "Workflow Report Generation",
        "/simulation/generate-daily-report",
        method="POST",
        data={"manual": True},
        auth=True,
        measure_time=True,
        expected_keys=["success", "report"]
    )
    
    if workflow_report_test and workflow_report_response:
        if workflow_report_response.get("success"):
            report_data = workflow_report_response.get("report", {})
            report_content = report_data.get("content", "")
            
            print(f"✅ Generated workflow report with {len(report_content)} characters")
            
            # Check report accessibility via /api/reports
            reports_test, reports_response = run_test(
                "Workflow Reports Access",
                "/reports",
                method="GET",
                auth=True,
                expected_keys=["success", "reports"]
            )
            
            if reports_test and reports_response:
                reports_list = reports_response.get("reports", [])
                print(f"✅ Reports accessible via /api/reports: {len(reports_list)} reports")
            else:
                print("❌ Reports not accessible via /api/reports")
                return False
        else:
            print("❌ Workflow report generation failed")
            return False
    else:
        print("❌ Workflow report generation failed")
        return False
    
    # Step 4: Verify visual quality and professional presentation
    print("\n--- Step 4: Visual Quality Assessment ---")
    
    # Assess report visual quality
    visual_quality_checks = {
        "Professional HTML Structure": "<html>" in report_content and "<head>" in report_content,
        "CSS Styling Present": "<style>" in report_content,
        "Visual Sections": "<div" in report_content or "<section" in report_content,
        "Color Scheme": any(color in report_content.lower() for color in ["color:", "background", "#"]),
        "Typography": "font-family" in report_content.lower(),
        "Layout Structure": any(layout in report_content.lower() for layout in ["margin", "padding", "border"]),
        "No Generic Content": not any(generic in report_content.lower() for generic in ["lorem ipsum", "placeholder", "example"]),
        "Professional Headers": any(header in report_content for header in ["<h1>", "<h2>", "<h3>"])
    }
    
    visual_score = sum(visual_quality_checks.values()) / len(visual_quality_checks) * 100
    
    print(f"\n📊 Visual Quality Assessment Score: {visual_score:.1f}%")
    for check, passed in visual_quality_checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    # Overall workflow assessment
    workflow_success = (
        workflow_conv_test and 
        workflow_docs_test and 
        workflow_report_test and 
        visual_score >= 75
    )
    
    if workflow_success:
        print("\n✅ Complete workflow test PASSED")
        print("   - Conversations generate successfully")
        print("   - Documents are accessible via API")
        print("   - Reports generate with professional formatting")
        print(f"   - Visual quality score: {visual_score:.1f}%")
        return True
    else:
        print("\n❌ Complete workflow test FAILED")
        return False

def cleanup_test_data():
    """Clean up test data created during testing"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete created agents
    for agent_id in created_agent_ids:
        delete_test, delete_response = run_test(
            f"Delete Agent {agent_id}",
            f"/agents/{agent_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted agent {agent_id}")
        else:
            print(f"❌ Failed to delete agent {agent_id}")
    
    # Delete created documents
    for doc_id in created_document_ids:
        delete_test, delete_response = run_test(
            f"Delete Document {doc_id}",
            f"/documents/{doc_id}",
            method="DELETE",
            auth=True
        )
        if delete_test:
            print(f"✅ Deleted document {doc_id}")
        else:
            print(f"❌ Failed to delete document {doc_id}")
    
    print("✅ Cleanup completed")

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
    print("ENHANCED REPORTS AND DOCUMENTS SYSTEM TESTING")
    print("Testing complete enhanced reports and documents system")
    print("="*80)
    
    # Setup phase
    if not setup_authentication():
        print("❌ Authentication setup failed - cannot continue")
        return False
    
    if not setup_test_agents():
        print("❌ Test agents setup failed - cannot continue")
        return False
    
    # Run test suites
    test_suites = [
        ("Enhanced Report Generation", test_enhanced_report_generation),
        ("Document Generation System", test_document_generation_system),
        ("Document Creation Logic", test_document_creation_logic),
        ("Document PDF Download", test_document_pdf_download),
        ("Complete Workflow", test_complete_workflow)
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
    print("ENHANCED REPORTS & DOCUMENTS TEST SUMMARY")
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