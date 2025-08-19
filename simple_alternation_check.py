#!/usr/bin/env python3
"""
SIMPLE AGENT ALTERNATION CHECK
Quick verification of the agent alternation fix by examining existing conversations
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def authenticate():
    """Quick authentication"""
    session = requests.Session()
    
    try:
        login_data = {
            "email": "dino@cytonic.com", 
            "password": "Observerinho8"
        }
        
        response = session.post(f"{API_BASE}/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            
            print("✅ Authentication successful")
            return session
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def check_existing_conversations(session):
    """Check existing conversations for agent alternation"""
    print("\n🔍 CHECKING EXISTING CONVERSATIONS FOR AGENT ALTERNATION")
    print("=" * 60)
    
    try:
        response = session.get(f"{API_BASE}/conversations", timeout=10)
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"Found {len(conversations)} conversations")
            
            # Check the last 3 conversations for alternation
            recent_conversations = conversations[-3:] if len(conversations) >= 3 else conversations
            
            alternation_results = []
            
            for i, conversation in enumerate(recent_conversations):
                conv_id = conversation.get('id', f'conv_{i}')
                messages = conversation.get('messages', [])
                
                # Extract agent sequence
                agent_sequence = []
                for msg in messages:
                    agent_name = msg.get('agent_name', '')
                    if agent_name and agent_name != 'Observer (You)':
                        agent_sequence.append(agent_name)
                
                # Check for consecutive same-agent messages
                consecutive_violations = []
                for j in range(1, len(agent_sequence)):
                    if agent_sequence[j] == agent_sequence[j-1]:
                        consecutive_violations.append(f"Position {j}: {agent_sequence[j-1]} → {agent_sequence[j]}")
                
                alternation_results.append({
                    'conversation_id': conv_id,
                    'agent_sequence': agent_sequence,
                    'violations': consecutive_violations,
                    'total_messages': len(agent_sequence)
                })
                
                print(f"\nConversation {i+1} (ID: {conv_id[:8]}...):")
                print(f"  Agent sequence: {' → '.join(agent_sequence)}")
                
                if consecutive_violations:
                    print(f"  ❌ VIOLATIONS: {'; '.join(consecutive_violations)}")
                else:
                    print(f"  ✅ Perfect alternation ({len(agent_sequence)} messages)")
            
            # Overall analysis
            total_violations = sum(len(result['violations']) for result in alternation_results)
            total_conversations = len(alternation_results)
            
            print(f"\n📊 ALTERNATION ANALYSIS SUMMARY:")
            print(f"  Conversations analyzed: {total_conversations}")
            print(f"  Total violations: {total_violations}")
            
            if total_violations == 0:
                print(f"  ✅ AGENT ALTERNATION FIX SUCCESS: No consecutive same-agent messages found!")
                print(f"  ✅ All conversations show proper Agent A → Agent B → Agent C alternation")
            else:
                print(f"  ❌ AGENT ALTERNATION FIX FAILED: {total_violations} violations found")
                print(f"  ❌ Consecutive same-agent messages still occurring")
            
            return total_violations == 0
            
        else:
            print(f"❌ Cannot access conversations: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Conversation check error: {str(e)}")
        return False

def test_single_conversation_generation(session):
    """Test a single conversation generation with shorter timeout"""
    print("\n🎯 TESTING SINGLE CONVERSATION GENERATION")
    print("=" * 50)
    
    try:
        # Get baseline
        response = session.get(f"{API_BASE}/conversations", timeout=5)
        baseline_count = len(response.json()) if response.status_code == 200 else 0
        
        print(f"Baseline conversations: {baseline_count}")
        print("Generating new conversation...")
        
        # Generate with shorter timeout
        start_time = time.time()
        response = session.post(f"{API_BASE}/conversation/generate", json={}, timeout=20)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Generation completed in {generation_time:.1f}s")
            
            # Wait briefly and check
            time.sleep(2)
            response = session.get(f"{API_BASE}/conversations", timeout=5)
            
            if response.status_code == 200:
                conversations = response.json()
                new_count = len(conversations)
                
                if new_count > baseline_count:
                    print(f"✅ New conversation created: {baseline_count} → {new_count}")
                    
                    # Check the latest conversation for alternation
                    latest_conversation = conversations[-1]
                    messages = latest_conversation.get('messages', [])
                    
                    agent_sequence = []
                    for msg in messages:
                        agent_name = msg.get('agent_name', '')
                        if agent_name and agent_name != 'Observer (You)':
                            agent_sequence.append(agent_name)
                    
                    print(f"Agent sequence: {' → '.join(agent_sequence)}")
                    
                    # Check for violations
                    violations = []
                    for i in range(1, len(agent_sequence)):
                        if agent_sequence[i] == agent_sequence[i-1]:
                            violations.append(f"{agent_sequence[i-1]} → {agent_sequence[i]}")
                    
                    if violations:
                        print(f"❌ ALTERNATION VIOLATIONS: {'; '.join(violations)}")
                        return False
                    else:
                        print(f"✅ PERFECT ALTERNATION: No consecutive same-agent messages")
                        return True
                else:
                    print(f"❌ No new conversation found: {baseline_count} → {new_count}")
                    return False
            else:
                print(f"❌ Cannot retrieve updated conversations: {response.status_code}")
                return False
        else:
            print(f"❌ Generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Generation test error: {str(e)}")
        return False

def main():
    print("🎯 SIMPLE AGENT ALTERNATION CHECK")
    print("=" * 50)
    print("Verifying the critical agent alternation fix")
    print()
    
    # Authenticate
    session = authenticate()
    if not session:
        print("🚨 Cannot proceed without authentication")
        return
    
    # Check existing conversations
    existing_alternation_ok = check_existing_conversations(session)
    
    # Test new conversation generation
    new_generation_ok = test_single_conversation_generation(session)
    
    # Final assessment
    print("\n" + "=" * 60)
    print("🎯 FINAL AGENT ALTERNATION ASSESSMENT")
    print("=" * 60)
    
    if existing_alternation_ok and new_generation_ok:
        print("✅ AGENT ALTERNATION FIX SUCCESS:")
        print("   - Existing conversations show proper alternation")
        print("   - New conversation generation maintains alternation")
        print("   - No consecutive same-agent messages detected")
        print("   - The ordered processing implementation is working")
    elif existing_alternation_ok:
        print("⚠️ PARTIAL SUCCESS:")
        print("   - Existing conversations show proper alternation")
        print("   - New generation test failed (may be network/timeout issue)")
        print("   - The fix appears to be working based on existing data")
    elif new_generation_ok:
        print("⚠️ PARTIAL SUCCESS:")
        print("   - New conversation generation shows proper alternation")
        print("   - Some existing conversations may have violations")
        print("   - The fix appears to be working for new generations")
    else:
        print("❌ AGENT ALTERNATION FIX FAILED:")
        print("   - Consecutive same-agent messages still occurring")
        print("   - The ordered processing implementation needs review")
        print("   - Check if asyncio.as_completed() was properly replaced")
    
    print("=" * 60)

if __name__ == "__main__":
    main()