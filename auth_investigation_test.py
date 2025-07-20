#!/usr/bin/env python3
"""
Authentication Investigation Test Script
Specifically designed to investigate the authentication issues mentioned in the review request:
- 401 Unauthorized errors from /api/simulation/state, /api/agents, /api/conversations endpoints
- "Authentication failed. Please log in again." when setting scenarios
- JWT token generation, validation, and expiration issues
"""

import requests
import json
import time
import os
import sys
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get URLs and secrets
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
JWT_SECRET = os.environ.get('JWT_SECRET')

if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

if not JWT_SECRET:
    print("⚠️ Warning: JWT_SECRET not found in environment variables")
    JWT_SECRET = "test_secret"

API_URL = f"{BACKEND_URL}/api"
print(f"🔍 Using API URL: {API_URL}")
print(f"🔑 JWT Secret: {JWT_SECRET[:10]}...")

class AuthInvestigator:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def make_request(self, method, endpoint, data=None, auth=True, expected_status=200):
        """Make HTTP request with detailed logging"""
        url = f"{API_URL}{endpoint}"
        headers = {}
        
        if auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        print(f"\n🌐 {method} {url}")
        if auth and self.auth_token:
            print(f"🔑 Authorization: Bearer {self.auth_token[:20]}...")
        if data:
            print(f"📤 Request Data: {json.dumps(data, indent=2)}")
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"📊 Status: {response.status_code} | Time: {response_time:.3f}s")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"📥 Response: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                response_data = {"text": response.text}
                print(f"📥 Response (text): {response.text}")
            
            # Check if status matches expected
            status_ok = response.status_code == expected_status
            if not status_ok:
                print(f"⚠️ Expected status {expected_status}, got {response.status_code}")
            
            return status_ok, response_data, response.status_code
            
        except Exception as e:
            print(f"💥 Request failed: {e}")
            return False, {"error": str(e)}, 0
    
    def test_guest_authentication(self):
        """Test the guest authentication endpoint"""
        print("\n" + "="*80)
        print("🧪 TESTING GUEST AUTHENTICATION ENDPOINT")
        print("="*80)
        
        # Test POST /api/auth/test-login
        success, response_data, status_code = self.make_request(
            "POST", "/auth/test-login", auth=False, expected_status=200
        )
        
        if success and response_data:
            # Check for required fields
            required_fields = ["access_token", "token_type", "user"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if not missing_fields:
                self.auth_token = response_data.get("access_token")
                user_data = response_data.get("user", {})
                self.user_id = user_data.get("id")
                
                self.log_test("Guest Authentication Endpoint", True, 
                             f"Token obtained, User ID: {self.user_id}")
                
                # Test JWT token structure
                self.test_jwt_token_structure()
                return True
            else:
                self.log_test("Guest Authentication Endpoint", False, 
                             f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Guest Authentication Endpoint", False, 
                         f"Request failed with status {status_code}")
            return False
    
    def test_jwt_token_structure(self):
        """Test JWT token structure and validation"""
        print("\n🔍 TESTING JWT TOKEN STRUCTURE")
        
        if not self.auth_token:
            self.log_test("JWT Token Structure", False, "No token available")
            return False
        
        try:
            # Decode token without verification first to see structure
            unverified_payload = jwt.decode(self.auth_token, options={"verify_signature": False})
            print(f"🔓 Unverified Token Payload: {json.dumps(unverified_payload, indent=2, default=str)}")
            
            # Check for required fields
            required_fields = ["sub", "user_id", "exp"]
            missing_fields = [field for field in required_fields if field not in unverified_payload]
            
            if missing_fields:
                self.log_test("JWT Token Structure", False, f"Missing fields: {missing_fields}")
                return False
            
            # Check expiration
            exp_timestamp = unverified_payload.get("exp")
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                time_until_exp = exp_datetime - datetime.now()
                print(f"⏰ Token expires at: {exp_datetime}")
                print(f"⏰ Time until expiration: {time_until_exp}")
                
                if time_until_exp.total_seconds() < 60:
                    self.log_test("JWT Token Expiration", False, "Token expires in less than 1 minute")
                    return False
                else:
                    self.log_test("JWT Token Expiration", True, f"Token valid for {time_until_exp}")
            
            # Try to verify token with secret
            try:
                verified_payload = jwt.decode(self.auth_token, JWT_SECRET, algorithms=["HS256"])
                self.log_test("JWT Token Verification", True, "Token successfully verified with secret")
                return True
            except jwt.ExpiredSignatureError:
                self.log_test("JWT Token Verification", False, "Token has expired")
                return False
            except jwt.InvalidTokenError as e:
                self.log_test("JWT Token Verification", False, f"Token verification failed: {e}")
                return False
                
        except Exception as e:
            self.log_test("JWT Token Structure", False, f"Token parsing failed: {e}")
            return False
    
    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me with valid token"""
        print("\n🧪 TESTING /api/auth/me ENDPOINT")
        
        success, response_data, status_code = self.make_request(
            "GET", "/auth/me", auth=True, expected_status=200
        )
        
        if success and response_data:
            required_fields = ["id", "email", "name"]
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if not missing_fields:
                # Check if user ID matches
                if response_data.get("id") == self.user_id:
                    self.log_test("Auth Me Endpoint", True, "User data retrieved successfully")
                    return True
                else:
                    self.log_test("Auth Me Endpoint", False, 
                                 f"User ID mismatch: expected {self.user_id}, got {response_data.get('id')}")
                    return False
            else:
                self.log_test("Auth Me Endpoint", False, f"Missing fields: {missing_fields}")
                return False
        else:
            self.log_test("Auth Me Endpoint", False, f"Request failed with status {status_code}")
            return False
    
    def test_protected_endpoints(self):
        """Test the problematic protected endpoints mentioned in the review"""
        print("\n🧪 TESTING PROTECTED ENDPOINTS WITH AUTHENTICATION")
        
        endpoints_to_test = [
            ("/simulation/state", "GET"),
            ("/agents", "GET"),
            ("/conversations", "GET"),
            ("/simulation/set-scenario", "POST", {"scenario": "Test Scenario", "scenario_name": "Test"})
        ]
        
        all_passed = True
        
        for endpoint_info in endpoints_to_test:
            endpoint = endpoint_info[0]
            method = endpoint_info[1]
            data = endpoint_info[2] if len(endpoint_info) > 2 else None
            
            print(f"\n🔍 Testing {method} {endpoint}")
            
            success, response_data, status_code = self.make_request(
                method, endpoint, data=data, auth=True, expected_status=200
            )
            
            if success:
                self.log_test(f"{method} {endpoint}", True, "Endpoint accessible with token")
            else:
                self.log_test(f"{method} {endpoint}", False, f"Status {status_code}")
                all_passed = False
                
                # If it's a 401, test without auth to confirm it's an auth issue
                if status_code == 401:
                    print("🔍 Testing same endpoint without authentication...")
                    no_auth_success, no_auth_data, no_auth_status = self.make_request(
                        method, endpoint, data=data, auth=False, expected_status=401
                    )
                    
                    if no_auth_status == 401:
                        print("✅ Endpoint correctly requires authentication")
                    else:
                        print(f"⚠️ Endpoint without auth returned status {no_auth_status}")
        
        return all_passed
    
    def test_token_without_bearer_prefix(self):
        """Test if the issue is with Bearer prefix"""
        print("\n🧪 TESTING TOKEN WITHOUT BEARER PREFIX")
        
        if not self.auth_token:
            self.log_test("Token Without Bearer", False, "No token available")
            return False
        
        # Test with just the token (no "Bearer " prefix)
        headers = {"Authorization": self.auth_token}
        url = f"{API_URL}/auth/me"
        
        print(f"🌐 GET {url}")
        print(f"🔑 Authorization: {self.auth_token[:20]}... (no Bearer prefix)")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                self.log_test("Token Without Bearer", True, "Token works without Bearer prefix")
                return True
            else:
                self.log_test("Token Without Bearer", False, f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Without Bearer", False, f"Request failed: {e}")
            return False
    
    def test_token_expiration_simulation(self):
        """Test what happens with an expired token"""
        print("\n🧪 TESTING TOKEN EXPIRATION BEHAVIOR")
        
        if not JWT_SECRET:
            self.log_test("Token Expiration Test", False, "JWT_SECRET not available")
            return False
        
        # Create an expired token
        expired_payload = {
            "sub": "test@example.com",
            "user_id": "test-user-id",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        try:
            expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")
            print(f"🔑 Created expired token: {expired_token[:20]}...")
            
            # Test with expired token
            headers = {"Authorization": f"Bearer {expired_token}"}
            url = f"{API_URL}/auth/me"
            
            response = requests.get(url, headers=headers)
            print(f"📊 Status with expired token: {response.status_code}")
            
            if response.status_code == 401:
                self.log_test("Expired Token Handling", True, "Expired token correctly rejected")
                return True
            else:
                self.log_test("Expired Token Handling", False, f"Expired token accepted with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Expiration Test", False, f"Failed to create expired token: {e}")
            return False
    
    def test_malformed_token(self):
        """Test behavior with malformed tokens"""
        print("\n🧪 TESTING MALFORMED TOKEN BEHAVIOR")
        
        malformed_tokens = [
            "invalid.token.here",
            "Bearer invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer ",
            "not-a-jwt-token"
        ]
        
        all_rejected = True
        
        for i, token in enumerate(malformed_tokens):
            print(f"\n🔍 Testing malformed token {i+1}: {token[:30]}...")
            
            headers = {"Authorization": f"Bearer {token}" if not token.startswith("Bearer") and token else token}
            url = f"{API_URL}/auth/me"
            
            try:
                response = requests.get(url, headers=headers)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 401:
                    print("✅ Malformed token correctly rejected")
                else:
                    print(f"❌ Malformed token accepted with status {response.status_code}")
                    all_rejected = False
                    
            except Exception as e:
                print(f"💥 Request failed: {e}")
        
        self.log_test("Malformed Token Handling", all_rejected, "All malformed tokens properly rejected" if all_rejected else "Some malformed tokens were accepted")
        return all_rejected
    
    def test_scenario_setting_specifically(self):
        """Test the specific scenario setting issue mentioned in the review"""
        print("\n🧪 TESTING SCENARIO SETTING SPECIFICALLY")
        
        # First, ensure we have a valid token
        if not self.auth_token:
            print("❌ No valid token available for scenario setting test")
            return False
        
        # Test setting a scenario
        scenario_data = {
            "scenario": "Test scenario for authentication investigation",
            "scenario_name": "Auth Test Scenario"
        }
        
        success, response_data, status_code = self.make_request(
            "POST", "/simulation/set-scenario", data=scenario_data, auth=True, expected_status=200
        )
        
        if success:
            self.log_test("Scenario Setting", True, "Scenario set successfully")
            
            # Verify the scenario was actually set by checking simulation state
            state_success, state_data, state_status = self.make_request(
                "GET", "/simulation/state", auth=True, expected_status=200
            )
            
            if state_success and state_data:
                scenario_in_state = state_data.get("scenario")
                if scenario_in_state == scenario_data["scenario"]:
                    self.log_test("Scenario Persistence", True, "Scenario correctly persisted in state")
                    return True
                else:
                    self.log_test("Scenario Persistence", False, f"Scenario not persisted correctly: {scenario_in_state}")
                    return False
            else:
                self.log_test("Scenario State Check", False, f"Could not verify scenario state: status {state_status}")
                return False
        else:
            self.log_test("Scenario Setting", False, f"Failed with status {status_code}")
            
            # If it failed with 401, this confirms the authentication issue
            if status_code == 401:
                print("🚨 CONFIRMED: Scenario setting fails with 401 Unauthorized")
                print("🔍 This matches the issue described in the review request")
            
            return False
    
    def run_comprehensive_investigation(self):
        """Run all authentication tests"""
        print("\n" + "="*100)
        print("🔍 COMPREHENSIVE AUTHENTICATION INVESTIGATION")
        print("="*100)
        print("Investigating the authentication issues mentioned in the review request:")
        print("- 401 Unauthorized errors from protected endpoints")
        print("- 'Authentication failed. Please log in again.' when setting scenarios")
        print("- JWT token generation, validation, and expiration issues")
        print("="*100)
        
        # Run all tests
        tests = [
            self.test_guest_authentication,
            self.test_auth_me_endpoint,
            self.test_protected_endpoints,
            self.test_token_without_bearer_prefix,
            self.test_token_expiration_simulation,
            self.test_malformed_token,
            self.test_scenario_setting_specifically
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"💥 Test {test.__name__} failed with exception: {e}")
                self.log_test(test.__name__, False, f"Exception: {e}")
        
        # Print summary
        self.print_investigation_summary()
    
    def print_investigation_summary(self):
        """Print comprehensive summary of investigation"""
        print("\n" + "="*100)
        print("📊 AUTHENTICATION INVESTIGATION SUMMARY")
        print("="*100)
        
        passed_tests = [t for t in self.test_results if t["passed"]]
        failed_tests = [t for t in self.test_results if not t["passed"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📈 SUCCESS RATE: {len(passed_tests)}/{len(self.test_results)} ({len(passed_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n🚨 FAILED TESTS:")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
        
        if passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   ✅ {test['test']}: {test['details']}")
        
        # Specific analysis for the review request issues
        print("\n" + "="*80)
        print("🎯 SPECIFIC ISSUE ANALYSIS")
        print("="*80)
        
        # Check if guest authentication works
        guest_auth_passed = any(t["test"] == "Guest Authentication Endpoint" and t["passed"] for t in self.test_results)
        if guest_auth_passed:
            print("✅ Guest authentication (POST /api/auth/test-login) is working")
        else:
            print("❌ Guest authentication (POST /api/auth/test-login) is NOT working")
        
        # Check if JWT tokens are valid
        jwt_structure_passed = any(t["test"] == "JWT Token Structure" and t["passed"] for t in self.test_results)
        jwt_verification_passed = any(t["test"] == "JWT Token Verification" and t["passed"] for t in self.test_results)
        
        if jwt_structure_passed and jwt_verification_passed:
            print("✅ JWT tokens are being generated correctly with proper structure and validation")
        else:
            print("❌ JWT tokens have issues with structure or validation")
        
        # Check if protected endpoints work
        protected_endpoints_passed = any(t["test"].startswith("GET /simulation/state") and t["passed"] for t in self.test_results)
        scenario_setting_passed = any(t["test"] == "Scenario Setting" and t["passed"] for t in self.test_results)
        
        if protected_endpoints_passed and scenario_setting_passed:
            print("✅ Protected endpoints are accessible with valid tokens")
            print("✅ Scenario setting is working correctly")
        else:
            print("❌ Protected endpoints are experiencing authentication issues")
            if not scenario_setting_passed:
                print("❌ Scenario setting specifically fails - this matches the reported issue")
        
        # Final diagnosis
        print("\n" + "="*80)
        print("🏥 FINAL DIAGNOSIS")
        print("="*80)
        
        if len(failed_tests) == 0:
            print("✅ AUTHENTICATION SYSTEM IS WORKING CORRECTLY")
            print("   The reported issues may be intermittent or frontend-related")
        elif not guest_auth_passed:
            print("🚨 CRITICAL: Guest authentication endpoint is not working")
            print("   This is the root cause of the authentication issues")
        elif not (jwt_structure_passed and jwt_verification_passed):
            print("🚨 CRITICAL: JWT token generation or validation is broken")
            print("   Tokens are not being created or verified properly")
        elif not (protected_endpoints_passed and scenario_setting_passed):
            print("🚨 CRITICAL: Token validation on protected endpoints is failing")
            print("   Valid tokens are being rejected by the backend")
        else:
            print("⚠️ PARTIAL ISSUES: Some authentication components are failing")
            print("   Review the failed tests above for specific issues")
        
        print("="*100)

if __name__ == "__main__":
    investigator = AuthInvestigator()
    investigator.run_comprehensive_investigation()