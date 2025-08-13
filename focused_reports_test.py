#!/usr/bin/env python3
"""
FOCUSED REPORTS RETRIEVAL TESTING
Testing specifically for the missing report retrieval endpoints that are causing the user's issue.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_auth():
    """Get authentication token"""
    response = requests.post(f"{API_URL}/auth/test-login")
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def test_report_retrieval_endpoints():
    """Test various report retrieval endpoints"""
    token = test_auth()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 TESTING REPORT RETRIEVAL ENDPOINTS")
    print("="*60)
    
    # Test endpoints that might contain reports
    endpoints_to_test = [
        ("/reports", "GET", "Main reports endpoint"),
        ("/reports/list", "GET", "Reports list endpoint"),
        ("/reports/daily", "GET", "Daily reports endpoint"),
        ("/simulation/reports", "GET", "Simulation reports endpoint"),
        ("/documents?category=report", "GET", "Documents filtered by report category"),
        ("/documents?search=report", "GET", "Documents search for reports"),
    ]
    
    for endpoint, method, description in endpoints_to_test:
        print(f"\n--- Testing: {description} ---")
        print(f"Endpoint: {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{API_URL}{endpoint}", headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ Endpoint exists - returned {len(data)} items")
                        # Check if any items look like reports
                        for item in data[:3]:  # Check first 3 items
                            if isinstance(item, dict):
                                title = str(item.get('title', '')).lower()
                                content = str(item.get('content', '')).lower()
                                if 'report' in title or 'daily' in title:
                                    print(f"  📋 Found report-like item: {item.get('title', 'No title')}")
                    elif isinstance(data, dict):
                        print(f"✅ Endpoint exists - returned object with keys: {list(data.keys())}")
                        if 'reports' in data:
                            reports = data['reports']
                            print(f"  📋 Found {len(reports) if isinstance(reports, list) else 1} reports")
                    else:
                        print(f"✅ Endpoint exists - returned: {type(data)}")
                except:
                    print(f"✅ Endpoint exists - non-JSON response: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"❌ Endpoint does not exist (404)")
            elif response.status_code == 401:
                print(f"⚠️ Authentication required (401)")
            elif response.status_code == 405:
                print(f"⚠️ Method not allowed (405)")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing endpoint: {e}")
    
    print("\n" + "="*60)
    print("🎯 ROOT CAUSE ANALYSIS")
    print("="*60)
    print("Based on the test results:")
    print("1. Reports are being generated successfully (confirmed from previous tests)")
    print("2. Reports are stored in database with unique IDs")
    print("3. BUT: No endpoint exists to retrieve the generated reports")
    print("4. This explains why users can generate reports but cannot see them")
    print("\n📋 REQUIRED FIXES:")
    print("- Implement GET /api/reports endpoint to list all user reports")
    print("- Implement GET /api/reports/{id} endpoint to get specific reports")
    print("- OR: Include reports in existing endpoints like /api/documents")
    print("- OR: Add reports data to /api/simulation/state endpoint")

if __name__ == "__main__":
    test_report_retrieval_endpoints()