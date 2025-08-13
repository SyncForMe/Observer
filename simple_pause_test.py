#!/usr/bin/env python3
"""
Simple Conversation Pause/Resume Test
Testing the user-reported issue: pause/resume causing message deletion
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_pause_resume_simple():
    """Simple test of pause/resume functionality"""
    print("SIMPLE CONVERSATION PAUSE/RESUME TEST")
    print("="*50)
    
    # Login
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Get initial conversation state
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get conversations")
        return False
    
    initial_conversations = response.json()
    initial_count = len(initial_conversations)
    initial_messages = sum(len(conv.get('messages', [])) for conv in initial_conversations)
    
    print(f"Initial state: {initial_count} conversations, {initial_messages} messages")
    
    # Test pause
    print("\nTesting PAUSE...")
    response = requests.post(f"{API_URL}/simulation/pause", headers=headers)
    if response.status_code != 200:
        print(f"❌ Pause failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    print("✅ Pause successful")
    
    # Check conversations after pause
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get conversations after pause")
        return False
    
    after_pause_conversations = response.json()
    after_pause_count = len(after_pause_conversations)
    after_pause_messages = sum(len(conv.get('messages', [])) for conv in after_pause_conversations)
    
    print(f"After pause: {after_pause_count} conversations, {after_pause_messages} messages")
    
    # Check for data loss after pause
    if after_pause_count < initial_count or after_pause_messages < initial_messages:
        print("🚨 DATA LOSS DETECTED AFTER PAUSE!")
        return False
    
    # Test resume
    print("\nTesting RESUME...")
    response = requests.post(f"{API_URL}/simulation/resume", headers=headers)
    if response.status_code != 200:
        print(f"❌ Resume failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    print("✅ Resume successful")
    
    # Check conversations after resume (CRITICAL TEST)
    response = requests.get(f"{API_URL}/conversations", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get conversations after resume")
        return False
    
    after_resume_conversations = response.json()
    after_resume_count = len(after_resume_conversations)
    after_resume_messages = sum(len(conv.get('messages', [])) for conv in after_resume_conversations)
    
    print(f"After resume: {after_resume_count} conversations, {after_resume_messages} messages")
    
    # CRITICAL CHECK: Data loss after resume
    data_loss = False
    if after_resume_count < initial_count:
        print(f"🚨 CRITICAL: {initial_count - after_resume_count} conversations DELETED after resume!")
        data_loss = True
    
    if after_resume_messages < initial_messages:
        print(f"🚨 CRITICAL: {initial_messages - after_resume_messages} messages DELETED after resume!")
        data_loss = True
    
    if after_resume_messages == 0 and initial_messages > 0:
        print("🚨 CONFIRMED USER ISSUE: ALL MESSAGES DELETED after pause/resume!")
        data_loss = True
    
    # Test message count consistency
    print("\nTesting message count consistency...")
    counts = []
    for i in range(3):
        response = requests.get(f"{API_URL}/conversations", headers=headers)
        if response.status_code == 200:
            conversations = response.json()
            msg_count = sum(len(conv.get('messages', [])) for conv in conversations)
            counts.append(msg_count)
            print(f"Check {i+1}: {msg_count} messages")
    
    if len(set(counts)) > 1:
        print(f"⚠️ INCONSISTENT MESSAGE COUNTS: {counts}")
        print("This explains the UI glitch where counters jump!")
        return False
    else:
        print("✅ Message counts are consistent")
    
    # Final result
    if data_loss:
        print("\n❌ TEST FAILED: Critical data loss detected in pause/resume cycle")
        print("This confirms the user's reported issue!")
        return False
    else:
        print("\n✅ TEST PASSED: No data loss in pause/resume cycle")
        return True

if __name__ == "__main__":
    success = test_pause_resume_simple()
    if success:
        print("\n🎉 Pause/Resume functionality is working correctly")
    else:
        print("\n🚨 CRITICAL ISSUE: Pause/Resume functionality has data loss problems")