#!/usr/bin/env python3
"""
Enhanced Features Testing Script for AI Agent Simulation Platform
Tests the specific enhanced features mentioned in the review request:
1. Enhanced Conversation Generation (using ALL agents, 3 messages per agent)
2. Document PDF Generation (single and bulk PDF endpoints)
3. Enhanced Document Review System (voting-based workflow)
4. Memory Architecture (rolling context window and summarization)
"""

import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import base64
import uuid
from datetime import datetime, timedelta
import tempfile

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🚀 Testing Enhanced Features at: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Global variables
auth_token = None
test_user_id = None
test_agents = []
test_documents = []
test_conversations = []

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, expected_keys=None, auth=True, headers=None, params=None):
    """Run a test against the specified endpoint"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"📍 {method} {url}")
    
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
            response = requests.delete(url, json=data, headers=headers, params=params)
        else:
            print(f"❌ Unsupported method: {method}")
            return False, None
        
        response_time = time.time() - start_time
        
        print(f"⏱️  Response Time: {response_time:.3f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        # Parse response
        try:
            response_data = response.json()
            print(f"📄 Response Size: {len(json.dumps(response_data))} chars")
        except json.JSONDecodeError:
            print(f"📄 Non-JSON Response: {response.text[:200]}...")
            response_data = {"raw_text": response.text}
        
        # Check status code
        status_ok = response.status_code == expected_status
        
        # Check expected keys
        keys_ok = True
        if expected_keys and status_ok and isinstance(response_data, dict):
            for key in expected_keys:
                if key not in response_data:
                    print(f"❌ Missing expected key: {key}")
                    keys_ok = False
        
        test_passed = status_ok and keys_ok
        result = "✅ PASSED" if test_passed else "❌ FAILED"
        print(f"🎯 Result: {result}")
        
        # Track results
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": "PASSED" if test_passed else "FAILED",
            "response_time": response_time
        })
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data
    
    except Exception as e:
        print(f"❌ Error: {e}")
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
    """Setup authentication for testing"""
    global auth_token, test_user_id
    
    print("\n🔐 Setting up authentication...")
    
    # Try guest login first
    success, response = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_keys=["access_token", "token_type", "user"]
    )
    
    if success and response:
        auth_token = response.get("access_token")
        user_data = response.get("user", {})
        test_user_id = user_data.get("id")
        print(f"✅ Authentication successful. User ID: {test_user_id}")
        return True
    
    print("❌ Authentication failed")
    return False

def setup_test_agents():
    """Create test agents for conversation generation"""
    global test_agents
    
    print("\n🤖 Setting up test agents...")
    
    # Create diverse agents for testing
    agent_configs = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Advance renewable energy research through rigorous scientific analysis",
            "expertise": "Solar Energy Systems",
            "background": "PhD in Materials Science with 15 years in photovoltaic research",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Marcus Rodriguez",
            "archetype": "leader",
            "goal": "Drive strategic implementation of sustainable technology solutions",
            "expertise": "Project Management & Strategy",
            "background": "Former VP of Operations at clean tech startup, MBA from Stanford",
            "personality": {
                "extroversion": 9,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Elena Vasquez",
            "archetype": "skeptic",
            "goal": "Ensure realistic assessment of risks and challenges",
            "expertise": "Risk Analysis & Financial Modeling",
            "background": "Senior analyst with experience in technology investment evaluation",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        },
        {
            "name": "Alex Thompson",
            "archetype": "optimist",
            "goal": "Inspire innovation and identify breakthrough opportunities",
            "expertise": "Innovation Strategy",
            "background": "Former innovation director at Fortune 500 company",
            "personality": {
                "extroversion": 8,
                "optimism": 10,
                "curiosity": 8,
                "cooperativeness": 9,
                "energy": 9
            }
        },
        {
            "name": "Dr. Raj Patel",
            "archetype": "researcher",
            "goal": "Conduct thorough analysis and provide evidence-based insights",
            "expertise": "Data Analysis & Research Methodology",
            "background": "Research scientist with expertise in quantitative analysis",
            "personality": {
                "extroversion": 3,
                "optimism": 6,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 5
            }
        }
    ]
    
    created_agents = 0
    for agent_config in agent_configs:
        success, response = run_test(
            f"Create Agent: {agent_config['name']}",
            "/agents",
            method="POST",
            data=agent_config,
            expected_status=200
        )
        
        if success and response:
            test_agents.append(response)
            created_agents += 1
    
    print(f"✅ Created {created_agents} test agents")
    return created_agents >= 3  # Need at least 3 agents for meaningful testing

def test_enhanced_conversation_generation():
    """Test enhanced conversation generation with ALL agents and 3 messages per agent"""
    print("\n🗣️  TESTING ENHANCED CONVERSATION GENERATION")
    print("="*60)
    
    if len(test_agents) < 3:
        print("❌ Need at least 3 agents for conversation testing")
        return False
    
    # Start simulation first
    success, response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        expected_keys=["message"]
    )
    
    if not success:
        print("❌ Failed to start simulation")
        return False
    
    # Set a scenario
    scenario_data = {
        "scenario": "The team is tasked with developing a comprehensive strategy for implementing renewable energy solutions in urban environments. They must address technical challenges, economic viability, regulatory requirements, and community adoption strategies.",
        "scenario_name": "Urban Renewable Energy Implementation"
    }
    
    success, response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        expected_keys=["message"]
    )
    
    if not success:
        print("❌ Failed to set scenario")
        return False
    
    # Test conversation generation
    print(f"\n🎯 Testing conversation generation with {len(test_agents)} agents")
    
    success, response = run_test(
        "Generate Enhanced Conversation",
        "/conversation/generate",
        method="POST",
        expected_keys=["messages", "round_number"]
    )
    
    if not success or not response:
        print("❌ Conversation generation failed")
        return False
    
    # Analyze the conversation
    messages = response.get("messages", [])
    total_messages = len(messages)
    agent_message_count = {}
    
    print(f"\n📊 CONVERSATION ANALYSIS:")
    print(f"Total messages generated: {total_messages}")
    print(f"Expected messages (3 per agent): {len(test_agents) * 3}")
    
    # Count messages per agent
    for message in messages:
        agent_name = message.get("agent_name", "Unknown")
        agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
    
    print(f"\n👥 Messages per agent:")
    for agent_name, count in agent_message_count.items():
        print(f"  {agent_name}: {count} messages")
    
    # Check if we're using ALL agents (not limiting to 3)
    unique_agents = len(agent_message_count)
    print(f"\n🤖 Agents participating: {unique_agents} out of {len(test_agents)} available")
    
    # Verify 3 messages per agent per round
    expected_total = len(test_agents) * 3
    messages_per_agent_ok = all(count == 3 for count in agent_message_count.values())
    
    print(f"\n✅ Using ALL agents: {'Yes' if unique_agents == len(test_agents) else 'No'}")
    print(f"✅ 3 messages per agent: {'Yes' if messages_per_agent_ok else 'No'}")
    print(f"✅ Total message count: {total_messages} (expected: {expected_total})")
    
    # Store conversation for cross-round reference testing
    if response:
        test_conversations.append(response)
    
    return unique_agents == len(test_agents) and messages_per_agent_ok

def test_cross_round_references():
    """Test that agents reference previous conversations in new rounds"""
    print("\n🔄 TESTING CROSS-ROUND REFERENCES")
    print("="*60)
    
    if not test_conversations:
        print("❌ No previous conversations to reference")
        return False
    
    # Generate a second conversation round
    success, response = run_test(
        "Generate Second Conversation Round",
        "/conversation/generate",
        method="POST",
        expected_keys=["messages", "round_number"]
    )
    
    if not success or not response:
        print("❌ Second conversation generation failed")
        return False
    
    messages = response.get("messages", [])
    round_number = response.get("round_number", 0)
    
    print(f"📊 Second round analysis:")
    print(f"Round number: {round_number}")
    print(f"Messages in round: {len(messages)}")
    
    # Check for references to previous conversations
    reference_indicators = [
        "previous", "earlier", "before", "mentioned", "discussed",
        "as we talked about", "building on", "following up",
        "from our last", "continuing", "as I said"
    ]
    
    references_found = 0
    for message in messages:
        message_text = message.get("message", "").lower()
        for indicator in reference_indicators:
            if indicator in message_text:
                references_found += 1
                agent_name = message.get("agent_name", "Unknown")
                print(f"  📝 {agent_name}: Found reference indicator '{indicator}'")
                break
    
    print(f"\n✅ Cross-round references found: {references_found} out of {len(messages)} messages")
    
    # Store this conversation too
    test_conversations.append(response)
    
    return references_found > 0

def test_document_focused_guidance():
    """Test that agents suggest document creation during conversations"""
    print("\n📄 TESTING DOCUMENT-FOCUSED CONVERSATION GUIDANCE")
    print("="*60)
    
    # Generate conversation with document-focused prompting
    success, response = run_test(
        "Generate Document-Focused Conversation",
        "/conversation/generate",
        method="POST",
        expected_keys=["messages"]
    )
    
    if not success or not response:
        print("❌ Document-focused conversation generation failed")
        return False
    
    messages = response.get("messages", [])
    
    # Look for document creation suggestions
    document_indicators = [
        "document", "report", "protocol", "plan", "proposal",
        "write up", "formalize", "capture", "record",
        "create a", "draft a", "prepare a", "develop a"
    ]
    
    document_suggestions = 0
    for message in messages:
        message_text = message.get("message", "").lower()
        for indicator in document_indicators:
            if indicator in message_text:
                document_suggestions += 1
                agent_name = message.get("agent_name", "Unknown")
                print(f"  📝 {agent_name}: Suggested document creation with '{indicator}'")
                break
    
    print(f"\n✅ Document creation suggestions: {document_suggestions} out of {len(messages)} messages")
    
    return document_suggestions > 0

def create_test_documents():
    """Create test documents for PDF generation testing"""
    print("\n📄 CREATING TEST DOCUMENTS")
    print("="*60)
    
    global test_documents
    
    document_configs = [
        {
            "title": "Urban Renewable Energy Implementation Strategy",
            "category": "Strategy",
            "description": "Comprehensive strategy for implementing renewable energy solutions in urban environments",
            "content": """# Urban Renewable Energy Implementation Strategy

## Executive Summary
This document outlines a comprehensive strategy for implementing renewable energy solutions in urban environments, addressing technical challenges, economic viability, regulatory requirements, and community adoption strategies.

## Technical Analysis
### Solar Panel Integration
- Rooftop installations on residential and commercial buildings
- Building-integrated photovoltaics (BIPV) for new construction
- Community solar gardens in available urban spaces

### Energy Storage Solutions
- Battery storage systems for grid stabilization
- Distributed storage at building level
- Integration with smart grid infrastructure

## Economic Considerations
### Investment Requirements
- Initial capital investment: $50M over 5 years
- Expected ROI: 15-20% within 10 years
- Job creation: 500+ direct jobs, 1,200+ indirect jobs

### Financing Mechanisms
- Public-private partnerships
- Green bonds and sustainability financing
- Federal and state incentive programs

## Implementation Timeline
### Phase 1 (Months 1-12): Planning and Preparation
- Regulatory approval and permitting
- Site assessment and selection
- Stakeholder engagement and community outreach

### Phase 2 (Months 13-36): Pilot Implementation
- Installation of first 100 residential systems
- Community solar garden development
- Grid integration testing

### Phase 3 (Months 37-60): Full-Scale Deployment
- City-wide rollout of renewable energy systems
- Performance monitoring and optimization
- Community education and adoption programs

## Risk Assessment
### Technical Risks
- Grid integration challenges
- Weather-dependent performance variability
- Technology obsolescence

### Financial Risks
- Regulatory changes affecting incentives
- Market volatility in equipment costs
- Competition from traditional energy sources

## Conclusion
The implementation of renewable energy solutions in urban environments presents significant opportunities for sustainable development, economic growth, and environmental benefits. Success requires coordinated effort across technical, financial, and regulatory domains.""",
            "keywords": ["renewable energy", "urban planning", "sustainability", "solar power"],
            "authors": ["Dr. Sarah Chen", "Marcus Rodriguez", "Elena Vasquez"]
        },
        {
            "title": "Risk Assessment and Mitigation Protocol",
            "category": "Protocol",
            "description": "Detailed risk assessment protocol for renewable energy projects",
            "content": """# Risk Assessment and Mitigation Protocol

## Purpose
This protocol establishes standardized procedures for identifying, assessing, and mitigating risks in renewable energy implementation projects.

## Risk Categories

### 1. Technical Risks
#### Equipment Failure
- **Probability**: Medium (30-40%)
- **Impact**: High
- **Mitigation**: Redundant systems, regular maintenance, warranty coverage

#### Grid Integration Issues
- **Probability**: Low (10-20%)
- **Impact**: Very High
- **Mitigation**: Extensive testing, phased rollout, backup systems

### 2. Financial Risks
#### Cost Overruns
- **Probability**: High (60-70%)
- **Impact**: Medium
- **Mitigation**: Detailed budgeting, contingency funds (15%), fixed-price contracts

#### Regulatory Changes
- **Probability**: Medium (40-50%)
- **Impact**: High
- **Mitigation**: Policy monitoring, diversified incentive portfolio, lobbying efforts

### 3. Environmental Risks
#### Weather Dependencies
- **Probability**: High (80-90%)
- **Impact**: Medium
- **Mitigation**: Weather forecasting integration, energy storage, grid balancing

## Risk Monitoring Framework
- Monthly risk assessment reviews
- Quarterly stakeholder risk briefings
- Annual comprehensive risk audit
- Real-time monitoring dashboards

## Escalation Procedures
1. **Low Risk**: Project manager handles
2. **Medium Risk**: Department head involvement
3. **High Risk**: Executive committee review
4. **Critical Risk**: Board-level decision required

## Documentation Requirements
All risk assessments must include:
- Risk identification methodology
- Probability and impact analysis
- Mitigation strategy details
- Monitoring and review schedules
- Responsible parties and timelines""",
            "keywords": ["risk assessment", "mitigation", "protocol", "project management"],
            "authors": ["Elena Vasquez", "Dr. Raj Patel"]
        }
    ]
    
    created_docs = 0
    for doc_config in document_configs:
        success, response = run_test(
            f"Create Document: {doc_config['title']}",
            "/documents",
            method="POST",
            data=doc_config,
            expected_keys=["id", "metadata"]
        )
        
        if success and response:
            test_documents.append(response)
            created_docs += 1
    
    print(f"✅ Created {created_docs} test documents")
    return created_docs > 0

def test_single_document_pdf():
    """Test single document PDF generation"""
    print("\n📄 TESTING SINGLE DOCUMENT PDF GENERATION")
    print("="*60)
    
    if not test_documents:
        print("❌ No test documents available")
        return False
    
    document_id = test_documents[0].get("id")
    if not document_id:
        print("❌ No document ID available")
        return False
    
    success, response = run_test(
        "Generate Single Document PDF",
        f"/documents/{document_id}/pdf",
        method="GET",
        expected_status=200
    )
    
    if success:
        # Check if response is PDF content
        if isinstance(response, dict) and "raw_text" in response:
            pdf_content = response["raw_text"]
            if pdf_content.startswith("%PDF"):
                print("✅ Valid PDF content received")
                print(f"📊 PDF size: {len(pdf_content)} bytes")
                return True
            else:
                print("❌ Response is not valid PDF content")
        else:
            print("❌ Unexpected response format")
    
    return False

def test_bulk_document_pdf():
    """Test bulk document PDF generation"""
    print("\n📄 TESTING BULK DOCUMENT PDF GENERATION")
    print("="*60)
    
    if len(test_documents) < 2:
        print("❌ Need at least 2 documents for bulk PDF testing")
        return False
    
    document_ids = [doc.get("id") for doc in test_documents[:2]]
    bulk_data = {"document_ids": document_ids}
    
    success, response = run_test(
        "Generate Bulk Document PDFs",
        "/documents/bulk-pdf",
        method="POST",
        data=bulk_data,
        expected_status=200
    )
    
    if success:
        # Check if response contains PDF data
        if isinstance(response, dict) and "raw_text" in response:
            pdf_content = response["raw_text"]
            if "PDF" in pdf_content or len(pdf_content) > 1000:
                print("✅ Bulk PDF content received")
                print(f"📊 Bulk PDF size: {len(pdf_content)} bytes")
                return True
        elif isinstance(response, dict) and "pdfs" in response:
            pdfs = response.get("pdfs", [])
            print(f"✅ Received {len(pdfs)} PDFs in bulk response")
            return len(pdfs) == len(document_ids)
    
    return False

def test_document_review_workflow():
    """Test the enhanced document review system with voting"""
    print("\n🗳️  TESTING DOCUMENT REVIEW WORKFLOW")
    print("="*60)
    
    if not test_documents:
        print("❌ No test documents available")
        return False
    
    document_id = test_documents[0].get("id")
    if not document_id:
        print("❌ No document ID available")
        return False
    
    # Test 1: Request document review
    success, response = run_test(
        "Request Document Review",
        f"/documents/{document_id}/request-review",
        method="POST",
        expected_keys=["message", "status"]
    )
    
    if not success:
        print("❌ Failed to request document review")
        return False
    
    # Test 2: Vote on document (approval)
    vote_data = {
        "vote": "approve",
        "comment": "Excellent comprehensive strategy with solid technical and financial analysis"
    }
    
    success, response = run_test(
        "Vote on Document (Approve)",
        f"/documents/{document_id}/vote",
        method="POST",
        data=vote_data,
        expected_keys=["message"]
    )
    
    if not success:
        print("❌ Failed to vote on document")
        return False
    
    # Test 3: Get review status
    success, response = run_test(
        "Get Document Review Status",
        f"/documents/{document_id}/review-status",
        method="GET",
        expected_keys=["status", "votes"]
    )
    
    if success and response:
        status = response.get("status", "unknown")
        votes = response.get("votes", {})
        print(f"📊 Review Status: {status}")
        print(f"📊 Votes: {votes}")
        return True
    
    return False

def test_memory_architecture():
    """Test the rolling context window and summarization"""
    print("\n🧠 TESTING MEMORY ARCHITECTURE")
    print("="*60)
    
    # Generate multiple conversations to test context window
    conversations_generated = 0
    
    for i in range(3):
        success, response = run_test(
            f"Generate Conversation {i+1} (Memory Test)",
            "/conversation/generate",
            method="POST",
            expected_keys=["messages"]
        )
        
        if success:
            conversations_generated += 1
            messages = response.get("messages", [])
            print(f"  Round {i+1}: {len(messages)} messages generated")
    
    # Test conversation summaries endpoint
    success, response = run_test(
        "Get Conversation Summaries",
        "/internal/conversation-summaries",
        method="GET",
        expected_status=200
    )
    
    if success and response:
        summaries = response if isinstance(response, list) else []
        print(f"📊 Conversation summaries available: {len(summaries)}")
        
        if summaries:
            latest_summary = summaries[0]
            print(f"📝 Latest summary preview: {str(latest_summary)[:200]}...")
        
        return len(summaries) > 0
    
    return conversations_generated >= 2

def print_final_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("🎯 ENHANCED FEATURES TEST SUMMARY")
    print("="*80)
    
    total_tests = len(test_results["tests"])
    passed = test_results["passed"]
    failed = test_results["failed"]
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/total_tests*100):.1f}%")
    
    print("\n📋 DETAILED RESULTS:")
    for i, test in enumerate(test_results["tests"], 1):
        status_icon = "✅" if test["result"] == "PASSED" else "❌"
        time_info = f" ({test.get('response_time', 0):.3f}s)" if 'response_time' in test else ""
        print(f"{i:2d}. {status_icon} {test['name']}{time_info}")
    
    print("\n" + "="*80)
    overall_result = "✅ PASSED" if failed == 0 else "❌ FAILED"
    print(f"🏆 OVERALL RESULT: {overall_result}")
    print("="*80)

def main():
    """Main test execution"""
    print("🚀 ENHANCED FEATURES TESTING SUITE")
    print("="*80)
    print("Testing enhanced conversation generation, PDF generation,")
    print("document review workflow, and memory architecture.")
    print("="*80)
    
    # Setup phase
    if not setup_authentication():
        print("❌ Authentication setup failed. Exiting.")
        return
    
    if not setup_test_agents():
        print("❌ Agent setup failed. Exiting.")
        return
    
    # Test enhanced conversation generation
    print("\n🎯 PHASE 1: ENHANCED CONVERSATION GENERATION")
    test_enhanced_conversation_generation()
    test_cross_round_references()
    test_document_focused_guidance()
    
    # Test document PDF generation
    print("\n🎯 PHASE 2: DOCUMENT PDF GENERATION")
    if create_test_documents():
        test_single_document_pdf()
        test_bulk_document_pdf()
    
    # Test document review workflow
    print("\n🎯 PHASE 3: DOCUMENT REVIEW WORKFLOW")
    test_document_review_workflow()
    
    # Test memory architecture
    print("\n🎯 PHASE 4: MEMORY ARCHITECTURE")
    test_memory_architecture()
    
    # Final summary
    print_final_summary()

if __name__ == "__main__":
    main()