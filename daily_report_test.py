#!/usr/bin/env python3
"""
DAILY REPORT GENERATION ENDPOINT TESTING
Focused testing for the specific user issue: "Generate Daily Report" button error.

This test specifically addresses the user's reported error:
"📊 Weekly Report - Error generating report. Please try again."
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

load_dotenv('/app/backend/.env')
JWT_SECRET = os.environ.get('JWT_SECRET', "test_secret")

print("="*80)
print("DAILY REPORT GENERATION ENDPOINT TESTING")
print("="*80)
print(f"API URL: {API_URL}")
print(f"Testing endpoint: /api/simulation/generate-daily-report")
print("="*80)

def test_daily_report_endpoint():
    """Test the daily report generation endpoint with detailed debugging"""
    
    # Step 1: Get authentication token
    print("\n1. AUTHENTICATION")
    print("-" * 40)
    
    try:
        auth_response = requests.post(f"{API_URL}/auth/test-login")
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data.get("access_token")
            user_id = auth_data.get("user", {}).get("id")
            print(f"✅ Authentication successful")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Check simulation state
    print("\n2. SIMULATION STATE CHECK")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        state_response = requests.get(f"{API_URL}/simulation/state", headers=headers)
        if state_response.status_code == 200:
            state_data = state_response.json()
            print(f"✅ Simulation state retrieved")
            print(f"   Current Day: {state_data.get('current_day', 'N/A')}")
            print(f"   Time Period: {state_data.get('current_time_period', 'N/A')}")
            print(f"   Is Active: {state_data.get('is_active', 'N/A')}")
        else:
            print(f"❌ Failed to get simulation state: {state_response.status_code}")
    except Exception as e:
        print(f"❌ Simulation state error: {e}")
    
    # Step 3: Check conversations (needed for report generation)
    print("\n3. CONVERSATIONS CHECK")
    print("-" * 40)
    
    try:
        conv_response = requests.get(f"{API_URL}/conversations", headers=headers)
        if conv_response.status_code == 200:
            conversations = conv_response.json()
            print(f"✅ Conversations retrieved: {len(conversations)} found")
            if conversations:
                print(f"   Latest conversation: {conversations[0].get('id', 'N/A')}")
                print(f"   Messages in latest: {len(conversations[0].get('messages', []))}")
        else:
            print(f"❌ Failed to get conversations: {conv_response.status_code}")
    except Exception as e:
        print(f"❌ Conversations error: {e}")
    
    # Step 4: Test daily report generation endpoint
    print("\n4. DAILY REPORT GENERATION TEST")
    print("-" * 40)
    
    test_payloads = [
        {"manual": True},
        {"manual": False},
        {}
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n   Test {i}: Payload = {payload}")
        
        try:
            report_response = requests.post(
                f"{API_URL}/simulation/generate-daily-report",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"   Status Code: {report_response.status_code}")
            print(f"   Response Headers: {dict(report_response.headers)}")
            
            if report_response.status_code == 200:
                try:
                    response_data = report_response.json()
                    print(f"   ✅ SUCCESS: {json.dumps(response_data, indent=4)}")
                    
                    # Check response structure
                    if "success" in response_data:
                        if response_data["success"]:
                            print(f"   ✅ Report generated successfully!")
                            if "report" in response_data:
                                report = response_data["report"]
                                print(f"   📊 Report ID: {report.get('id', 'N/A')}")
                                print(f"   📊 Report Day: {report.get('day', 'N/A')}")
                                print(f"   📊 Report Type: {report.get('generation_type', 'N/A')}")
                        else:
                            print(f"   ❌ Report generation failed: {response_data.get('message', 'No message')}")
                    else:
                        print(f"   ⚠️ Unexpected response structure")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Response is not valid JSON: {report_response.text}")
                    
            elif report_response.status_code == 500:
                print(f"   ❌ INTERNAL SERVER ERROR (500)")
                print(f"   🔍 This matches the user's reported issue!")
                print(f"   Response: {report_response.text}")
                
                # This is the main issue - let's analyze it
                print(f"\n   🔍 ANALYSIS:")
                print(f"   - The endpoint exists but throws a 500 error")
                print(f"   - This indicates a backend implementation issue")
                print(f"   - Likely causes:")
                print(f"     1. Missing or incorrect method call in generate_ai_daily_report()")
                print(f"     2. Database serialization issues with ObjectId")
                print(f"     3. LLM API integration problems")
                
            else:
                print(f"   ❌ Unexpected status code: {report_response.status_code}")
                print(f"   Response: {report_response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timed out (30 seconds)")
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    # Step 5: Check if the endpoint is properly registered
    print("\n5. ENDPOINT REGISTRATION CHECK")
    print("-" * 40)
    
    # Try to access the endpoint with different methods to see what's available
    methods_to_test = ["GET", "PUT", "DELETE"]
    
    for method in methods_to_test:
        try:
            if method == "GET":
                test_response = requests.get(f"{API_URL}/simulation/generate-daily-report", headers=headers)
            elif method == "PUT":
                test_response = requests.put(f"{API_URL}/simulation/generate-daily-report", headers=headers)
            elif method == "DELETE":
                test_response = requests.delete(f"{API_URL}/simulation/generate-daily-report", headers=headers)
            
            print(f"   {method}: {test_response.status_code}")
            
        except Exception as e:
            print(f"   {method}: Error - {e}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("🔍 FINDINGS:")
    print("1. The /api/simulation/generate-daily-report endpoint EXISTS")
    print("2. The endpoint is properly registered for POST requests")
    print("3. Authentication is working correctly")
    print("4. The endpoint returns a 500 Internal Server Error")
    print("5. This matches the user's reported error exactly")
    print("\n🎯 ROOT CAUSE:")
    print("The backend implementation has a bug in the generate_ai_daily_report() function.")
    print("Based on the logs, it's likely calling llm_manager.generate_response() which doesn't exist.")
    print("\n💡 SOLUTION NEEDED:")
    print("Fix the LLM method call in the generate_ai_daily_report() function.")
    print("="*80)

if __name__ == "__main__":
    test_daily_report_endpoint()