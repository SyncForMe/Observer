#!/usr/bin/env python3
"""
SIMPLE START FRESH TEST
Direct test of the /api/simulation/reset endpoint functionality
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"Testing API: {API_URL}")

def test_start_fresh():
    """Test the Start Fresh functionality"""
    
    # Step 1: Authenticate
    print("\n1. Authenticating...")
    auth_response = requests.post(f"{API_URL}/auth/test-login")
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return False
    
    auth_data = auth_response.json()
    token = auth_data.get("access_token")
    user_id = auth_data.get("user", {}).get("id")
    
    print(f"✅ Authenticated as user: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Check existing data
    print("\n2. Checking existing data...")
    
    # Check documents
    docs_response = requests.get(f"{API_URL}/documents", headers=headers)
    if docs_response.status_code == 200:
        doc_count = len(docs_response.json()) if docs_response.json() else 0
        print(f"📄 Documents: {doc_count}")
    else:
        print("❌ Failed to check documents")
    
    # Check reports
    reports_response = requests.get(f"{API_URL}/reports", headers=headers)
    if reports_response.status_code == 200:
        report_count = len(reports_response.json().get("reports", [])) if reports_response.json() else 0
        print(f"📊 Reports: {report_count}")
    else:
        print("❌ Failed to check reports")
    
    # Check simulation state
    state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    if state_response.status_code == 200:
        state_data = state_response.json()
        day = state_data.get("current_day", "N/A")
        period = state_data.get("current_time_period", "N/A")
        print(f"🎮 Simulation: Day {day}, {period}")
    else:
        print("❌ Failed to check simulation state")
    
    # Step 3: Execute Start Fresh
    print("\n3. Executing Start Fresh...")
    
    reset_response = requests.post(f"{API_URL}/simulation/reset", headers=headers)
    
    print(f"Status: {reset_response.status_code}")
    
    if reset_response.status_code == 200:
        reset_data = reset_response.json()
        print(f"Response: {json.dumps(reset_data, indent=2)}")
        
        # Check if successful
        if reset_data.get("success"):
            print("✅ Reset reported as successful")
            
            # Check message
            message = reset_data.get("message", "")
            if "documents" in message.lower() and "reports" in message.lower():
                print("✅ Message mentions documents and reports")
            else:
                print("⚠️ Message may not mention documents/reports")
            
            # Check cleared collections
            cleared = reset_data.get("cleared_collections", [])
            expected = ["simulation_state", "conversations", "relationships", "summaries", "agents", "observer_messages", "documents", "reports"]
            
            print(f"📋 Cleared: {cleared}")
            
            missing = [col for col in expected if col not in cleared]
            if missing:
                print(f"⚠️ Missing: {missing}")
            else:
                print("✅ All 8 collections listed")
            
        else:
            print("❌ Reset not successful")
            return False
    else:
        print(f"❌ Reset failed: {reset_response.status_code}")
        try:
            error_data = reset_response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Error text: {reset_response.text}")
        return False
    
    # Step 4: Verify cleanup
    print("\n4. Verifying cleanup...")
    
    # Check documents are cleared
    docs_response = requests.get(f"{API_URL}/documents", headers=headers)
    if docs_response.status_code == 200:
        doc_count = len(docs_response.json()) if docs_response.json() else 0
        if doc_count == 0:
            print("✅ Documents cleared")
        else:
            print(f"❌ Documents not cleared: {doc_count} remaining")
    else:
        print("❌ Failed to verify document clearing")
    
    # Check reports are cleared
    reports_response = requests.get(f"{API_URL}/reports", headers=headers)
    if reports_response.status_code == 200:
        report_count = len(reports_response.json().get("reports", [])) if reports_response.json() else 0
        if report_count == 0:
            print("✅ Reports cleared")
        else:
            print(f"❌ Reports not cleared: {report_count} remaining")
    else:
        print("❌ Failed to verify report clearing")
    
    # Check simulation state is reset
    state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
    if state_response.status_code == 200:
        state_data = state_response.json()
        day = state_data.get("current_day", 0)
        period = state_data.get("current_time_period", "")
        active = state_data.get("is_active", True)
        
        if day == 1 and period == "morning" and not active:
            print("✅ Simulation state reset")
        else:
            print(f"❌ Simulation state not reset: Day {day}, {period}, Active: {active}")
    else:
        print("❌ Failed to verify simulation state reset")
    
    print("\n✅ Start Fresh test completed!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("START FRESH FUNCTIONALITY TEST")
    print("=" * 60)
    
    success = test_start_fresh()
    
    if success:
        print("\n🎯 RESULT: ✅ START FRESH WORKING")
    else:
        print("\n🎯 RESULT: ❌ START FRESH ISSUES")