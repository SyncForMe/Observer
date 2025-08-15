#!/usr/bin/env python3
"""
CONVERSATION GENERATION AGENT ALTERNATION TESTING
Testing the specific issue where the same agent (Dr. James Park) is sending multiple consecutive messages 
instead of different agents alternating properly.

SPECIFIC ISSUES TO INVESTIGATE:
1. Check if the agent list has duplicate agents (same agent appearing multiple times)
2. Verify that the conversation generation loop is actually iterating through different agents
3. Test that the generated messages are saved with different agent_names
4. Examine the agent ordering and selection logic

EXPECTED BEHAVIOR:
- Each agent should send exactly 1 message per conversation round
- Agents should alternate (Agent A → Agent B → Agent C), not repeat (Agent A → Agent A → Agent A)
- The /api/conversation/generate endpoint should produce a conversation with different agent names
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

# Global variables for auth testing
auth_token = None
test_user_id = None
created_agent_ids = []

def authenticate():
    """Authenticate with the backend using email/password"""
    global auth_token, test_user_id
    
    print("🔐 Authenticating with backend...")
    
    # Test email/password login with known test user
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            auth_token = login_response.get("access_token")
            user_data = login_response.get("user", {})
            test_user_id = user_data.get("id")
            print(f"✅ Authentication successful. User ID: {test_user_id}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def get_agents():
    """Get all agents for the current user"""
    print("\n" + "="*80)
    print("1. GETTING AGENT LIST")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{API_URL}/agents", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            agents = response.json()
            print(f"Response: {json.dumps(agents, indent=2)}")
            
            print(f"\n📊 AGENT ANALYSIS:")
            print(f"Total agents found: {len(agents)}")
            
            # Check for duplicates by name
            agent_names = [agent.get('name', 'Unknown') for agent in agents]
            unique_names = set(agent_names)
            
            print(f"Unique agent names: {len(unique_names)}")
            print(f"Agent names: {agent_names}")
            
            if len(agent_names) != len(unique_names):
                print("🚨 DUPLICATE AGENTS DETECTED!")
                name_counts = {}
                for name in agent_names:
                    name_counts[name] = name_counts.get(name, 0) + 1
                
                for name, count in name_counts.items():
                    if count > 1:
                        print(f"  - '{name}' appears {count} times")
                        
                        # Find all instances of this duplicate agent
                        duplicate_agents = [agent for agent in agents if agent.get('name') == name]
                        print(f"  - Duplicate agent details:")
                        for i, dup_agent in enumerate(duplicate_agents):
                            print(f"    [{i+1}] ID: {dup_agent.get('id')}, Name: {dup_agent.get('name')}, Archetype: {dup_agent.get('archetype')}")
                
                return agents, True  # Has duplicates
            else:
                print("✅ No duplicate agents found")
                
                # Show agent details
                print(f"\n📋 AGENT DETAILS:")
                for i, agent in enumerate(agents, 1):
                    print(f"  [{i}] ID: {agent.get('id')}, Name: {agent.get('name')}, Archetype: {agent.get('archetype')}")
                
                return agents, False  # No duplicates
                
        else:
            print(f"❌ Failed to get agents: {response.status_code} - {response.text}")
            return [], False
            
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return [], False

def generate_conversation():
    """Generate a conversation and analyze the agent ordering"""
    print("\n" + "="*80)
    print("2. GENERATING CONVERSATION")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            conversation_data = response.json()
            print(f"Response: {json.dumps(conversation_data, indent=2)}")
            
            # Extract conversation details
            conversation = conversation_data.get("conversation", {})
            messages = conversation.get("messages", [])
            
            print(f"\n📊 CONVERSATION ANALYSIS:")
            print(f"Total messages: {len(messages)}")
            
            if messages:
                print(f"\n📋 MESSAGE DETAILS:")
                agent_message_count = {}
                
                for i, message in enumerate(messages, 1):
                    agent_name = message.get("agent_name", "Unknown")
                    agent_id = message.get("agent_id", "Unknown")
                    message_text = message.get("message", "")
                    
                    print(f"  [{i}] Agent: {agent_name} (ID: {agent_id})")
                    print(f"      Message: {message_text[:100]}...")
                    
                    # Count messages per agent
                    agent_message_count[agent_name] = agent_message_count.get(agent_name, 0) + 1
                
                print(f"\n📊 AGENT MESSAGE COUNT:")
                for agent_name, count in agent_message_count.items():
                    status = "✅" if count == 1 else "🚨"
                    print(f"  {status} {agent_name}: {count} message(s)")
                
                # Check for the specific issue: same agent multiple times
                if any(count > 1 for count in agent_message_count.values()):
                    print(f"\n🚨 ISSUE DETECTED: Same agent sending multiple messages!")
                    
                    # Show the sequence
                    print(f"\n📋 MESSAGE SEQUENCE:")
                    for i, message in enumerate(messages, 1):
                        agent_name = message.get("agent_name", "Unknown")
                        print(f"  [{i}] {agent_name}")
                    
                    # Check for consecutive messages from same agent
                    consecutive_issues = []
                    for i in range(1, len(messages)):
                        if messages[i].get("agent_name") == messages[i-1].get("agent_name"):
                            consecutive_issues.append((i, messages[i].get("agent_name")))
                    
                    if consecutive_issues:
                        print(f"\n🚨 CONSECUTIVE MESSAGE ISSUES:")
                        for pos, agent_name in consecutive_issues:
                            print(f"  - Position {pos}: {agent_name} sent consecutive messages")
                    
                    return conversation_data, True  # Has issues
                else:
                    print(f"\n✅ PERFECT ALTERNATION: Each agent sent exactly 1 message")
                    
                    # Show the alternation pattern
                    print(f"\n📋 ALTERNATION PATTERN:")
                    agent_sequence = [msg.get("agent_name") for msg in messages]
                    print(f"  {' → '.join(agent_sequence)}")
                    
                    return conversation_data, False  # No issues
            else:
                print(f"❌ No messages found in conversation")
                return conversation_data, True  # Has issues
                
        else:
            print(f"❌ Failed to generate conversation: {response.status_code} - {response.text}")
            return None, True
            
    except Exception as e:
        print(f"❌ Error generating conversation: {e}")
        return None, True

def analyze_agent_selection_logic():
    """Analyze the agent selection logic by examining multiple conversation generations"""
    print("\n" + "="*80)
    print("3. ANALYZING AGENT SELECTION LOGIC")
    print("="*80)
    
    print("🔍 Generating multiple conversations to analyze agent selection patterns...")
    
    all_patterns = []
    issue_count = 0
    
    for i in range(3):  # Generate 3 conversations to see patterns
        print(f"\n--- Conversation {i+1} ---")
        
        conversation_data, has_issues = generate_conversation()
        
        if conversation_data:
            conversation = conversation_data.get("conversation", {})
            messages = conversation.get("messages", [])
            
            if messages:
                # Extract agent sequence
                agent_sequence = [msg.get("agent_name") for msg in messages]
                all_patterns.append(agent_sequence)
                
                print(f"Pattern {i+1}: {' → '.join(agent_sequence)}")
                
                if has_issues:
                    issue_count += 1
            else:
                print(f"No messages in conversation {i+1}")
                issue_count += 1
        else:
            print(f"Failed to generate conversation {i+1}")
            issue_count += 1
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n📊 PATTERN ANALYSIS:")
    print(f"Total conversations analyzed: {len(all_patterns)}")
    print(f"Conversations with issues: {issue_count}")
    
    if all_patterns:
        print(f"\n📋 ALL PATTERNS:")
        for i, pattern in enumerate(all_patterns, 1):
            print(f"  [{i}] {' → '.join(pattern)}")
        
        # Check if patterns are identical (indicating deterministic ordering)
        if len(set(tuple(pattern) for pattern in all_patterns)) == 1:
            print(f"\n🔍 OBSERVATION: All patterns are identical - agent ordering is deterministic")
        else:
            print(f"\n🔍 OBSERVATION: Patterns vary - agent ordering has some randomness")
        
        # Check for common issues across patterns
        common_duplicates = set()
        for pattern in all_patterns:
            agent_counts = {}
            for agent in pattern:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            for agent, count in agent_counts.items():
                if count > 1:
                    common_duplicates.add(agent)
        
        if common_duplicates:
            print(f"\n🚨 AGENTS CONSISTENTLY APPEARING MULTIPLE TIMES:")
            for agent in common_duplicates:
                print(f"  - {agent}")
    
    return issue_count == 0

def investigate_backend_logic():
    """Investigate the backend logic by examining the agent list and conversation generation"""
    print("\n" + "="*80)
    print("4. INVESTIGATING BACKEND LOGIC")
    print("="*80)
    
    print("🔍 This investigation examines the backend conversation generation logic...")
    
    # Get agents again to double-check
    agents, has_duplicates = get_agents()
    
    if has_duplicates:
        print(f"\n🚨 ROOT CAUSE IDENTIFIED: Duplicate agents in database")
        print(f"   - The conversation generation loop iterates through ALL agents")
        print(f"   - If the same agent appears multiple times, it will generate multiple messages")
        print(f"   - This explains why Dr. James Park (or other agents) send consecutive messages")
        
        print(f"\n🔧 RECOMMENDED FIXES:")
        print(f"   1. Remove duplicate agents from the database")
        print(f"   2. Add deduplication logic in the conversation generation endpoint")
        print(f"   3. Add unique constraints to prevent duplicate agent creation")
        
        return False
    else:
        print(f"\n✅ No duplicate agents found in database")
        print(f"   - The issue might be in the conversation generation logic itself")
        print(f"   - Or there might be a race condition during agent selection")
        
        print(f"\n🔍 FURTHER INVESTIGATION NEEDED:")
        print(f"   1. Check if agents are being modified during conversation generation")
        print(f"   2. Examine the agent ordering logic in the backend")
        print(f"   3. Look for any agent filtering or selection logic")
        
        return True

def cleanup():
    """Clean up any test data created"""
    print("\n" + "="*80)
    print("CLEANUP")
    print("="*80)
    
    # No cleanup needed for this test as we're only reading data
    print("✅ No cleanup needed - test only read existing data")

def main():
    """Main test execution function"""
    print("CONVERSATION GENERATION AGENT ALTERNATION TESTING")
    print("Investigating why the same agent sends multiple consecutive messages")
    print("="*80)
    
    # Authenticate
    if not authenticate():
        print("❌ Authentication failed - cannot proceed with tests")
        return False
    
    # Run investigation steps
    test_results = []
    
    # Step 1: Check agent list for duplicates
    print(f"\n🔍 STEP 1: Checking for duplicate agents...")
    agents, has_duplicates = get_agents()
    test_results.append(("Agent List Check", not has_duplicates))
    
    # Step 2: Generate conversation and analyze
    print(f"\n🔍 STEP 2: Generating conversation and analyzing agent alternation...")
    conversation_data, has_issues = generate_conversation()
    test_results.append(("Conversation Generation", not has_issues))
    
    # Step 3: Analyze patterns across multiple conversations
    print(f"\n🔍 STEP 3: Analyzing agent selection patterns...")
    patterns_ok = analyze_agent_selection_logic()
    test_results.append(("Agent Selection Patterns", patterns_ok))
    
    # Step 4: Investigate backend logic
    print(f"\n🔍 STEP 4: Investigating backend logic...")
    backend_ok = investigate_backend_logic()
    test_results.append(("Backend Logic Investigation", backend_ok))
    
    # Cleanup
    cleanup()
    
    # Print final summary
    print(f"\n" + "="*80)
    print("FINAL INVESTIGATION SUMMARY")
    print("="*80)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    for test_name, result in test_results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    # Provide specific conclusions
    print(f"\n🎯 CONCLUSIONS:")
    
    if has_duplicates:
        print(f"🚨 ISSUE CONFIRMED: Duplicate agents in database causing multiple messages")
        print(f"   - Same agent appears multiple times in agent list")
        print(f"   - Conversation generation iterates through all agents including duplicates")
        print(f"   - This causes the same agent to send multiple consecutive messages")
        
        print(f"\n🔧 IMMEDIATE ACTIONS NEEDED:")
        print(f"   1. Remove duplicate agents from database")
        print(f"   2. Add agent deduplication in conversation generation")
        print(f"   3. Implement unique constraints to prevent future duplicates")
        
    elif has_issues:
        print(f"🚨 ISSUE CONFIRMED: Agent alternation problems detected")
        print(f"   - No duplicate agents in database")
        print(f"   - Issue is in the conversation generation logic")
        print(f"   - Agents are not alternating properly")
        
        print(f"\n🔧 INVESTIGATION NEEDED:")
        print(f"   1. Examine conversation generation loop logic")
        print(f"   2. Check for race conditions in agent selection")
        print(f"   3. Verify agent ordering and filtering logic")
        
    else:
        print(f"✅ NO ISSUES DETECTED: Agent alternation working correctly")
        print(f"   - No duplicate agents found")
        print(f"   - Conversations show proper agent alternation")
        print(f"   - Each agent sends exactly one message per round")
        
        print(f"\n🤔 IF USER STILL REPORTS ISSUES:")
        print(f"   1. Issue might be intermittent or user-specific")
        print(f"   2. Check for browser caching or frontend display issues")
        print(f"   3. Examine specific conversation IDs reported by user")
    
    print("="*80)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)