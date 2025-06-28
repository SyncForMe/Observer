#!/usr/bin/env python3
import requests
import json
import os
import sys
from dotenv import load_dotenv
import uuid
import time

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

def send_observer_message_without_auth():
    """Send an observer message without authentication"""
    url = f"{API_URL}/observer/send-message"
    data = {
        "observer_message": "This is a test message without authentication."
    }
    
    print(f"\n{'='*80}\nSENDING OBSERVER MESSAGE WITHOUT AUTHENTICATION")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data)}")
    
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("❌ Observer message sent successfully without authentication")
        print("This is a security issue - the endpoint should require authentication")
        return True
    elif response.status_code == 403:
        print("✅ Observer message endpoint correctly rejected unauthenticated request with 403 Forbidden")
        return False
    else:
        print(f"⚠️ Observer message endpoint rejected unauthenticated request with unexpected status code: {response.status_code}")
        return False

def get_observer_messages_without_auth():
    """Get observer messages without authentication"""
    url = f"{API_URL}/observer/messages"
    
    print(f"\n{'='*80}\nGETTING OBSERVER MESSAGES WITHOUT AUTHENTICATION")
    print(f"URL: {url}")
    
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("❌ Observer messages retrieved successfully without authentication")
        print("This is a security issue - the endpoint should require authentication")
        return True
    elif response.status_code == 403:
        print("✅ Observer messages endpoint correctly rejected unauthenticated request with 403 Forbidden")
        return False
    else:
        print(f"⚠️ Observer messages endpoint rejected unauthenticated request with unexpected status code: {response.status_code}")
        return False

def main():
    """Main test function"""
    print(f"\n{'='*80}")
    print("OBSERVER MESSAGE AUTHENTICATION TEST")
    print(f"{'='*80}")
    
    # Test sending observer message without authentication
    send_success = send_observer_message_without_auth()
    
    # Test getting observer messages without authentication
    get_success = get_observer_messages_without_auth()
    
    # Print summary
    print(f"\n{'='*80}\nSUMMARY")
    print(f"{'='*80}")
    
    if send_success:
        print("❌ The observer message endpoint does not require authentication")
        print("   - This is a security issue that allows anyone to send observer messages")
    else:
        print("✅ The observer message endpoint requires authentication")
    
    if get_success:
        print("❌ The observer messages endpoint does not require authentication")
        print("   - This is a security issue that allows anyone to view observer messages")
    else:
        print("✅ The observer messages endpoint requires authentication")
    
    if send_success or get_success:
        print("\nRecommendations:")
        
        if send_success:
            print("1. Add authentication requirement to the observer message endpoint:")
            print("   - Change line 289 from:")
            print("     @api_router.post(\"/observer/send-message\")")
            print("     async def send_observer_message(input_data: ObserverInput):")
            print("   - To:")
            print("     @api_router.post(\"/observer/send-message\")")
            print("     async def send_observer_message(input_data: ObserverInput, current_user: User = Depends(get_current_user)):")
        
        if get_success:
            print("2. Add authentication requirement to the observer messages endpoint:")
            print("   - Change line 433 from:")
            print("     @api_router.get(\"/observer/messages\")")
            print("     async def get_observer_messages():")
            print("   - To:")
            print("     @api_router.get(\"/observer/messages\")")
            print("     async def get_observer_messages(current_user: User = Depends(get_current_user)):")

if __name__ == "__main__":
    main()