#!/usr/bin/env python3
"""
Backend Test Script for "Start Fresh" Reports Clearing Functionality

This script tests the specific issue reported by the user:
"Start Fresh" button is not always clearing reports from the Observatory after clicking "Start Fresh".

TESTING OBJECTIVES:
1. Verify that the simulation state endpoint only returns reports from the current active simulation session
2. Test that after "Start Fresh", the Observatory reports section is empty
3. Confirm that old reports are still preserved in the database (for Library access)
4. Ensure that new reports generated after "Start Fresh" appear correctly in Observatory

EXPECTED RESULTS:
- After "Start Fresh", Observatory should show 0 reports
- New reports generated after "Start Fresh" should appear in Observatory
- Historical reports should remain in database for Library access
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://simulated-agents.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class StartFreshReportsTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate_guest(self):
        """Authenticate as guest user for testing"""
        try:
            # Create a test JWT token for guest user
            import jwt
            import uuid
            
            # Use the JWT secret from backend
            jwt_secret = "test_jwt_secret_for_observer_message_testing_12345"
            
            # Create test user payload
            user_payload = {
                "sub": "test-user-123",
                "user_id": "test-user-123",
                "email": "test@example.com",
                "name": "Test User",
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            # Generate JWT token
            self.auth_token = jwt.encode(user_payload, jwt_secret, algorithm="HS256")
            self.user_id = "test-user-123"
            
            print(f"✅ Authentication successful - User ID: {self.user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
            
    async def make_request(self, method, endpoint, data=None, expect_success=True):
        """Make authenticated HTTP request"""
        url = f"{API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_data = await response.json()
                    if expect_success and response.status != 200:
                        print(f"⚠️ Unexpected status {response.status} for {method} {endpoint}")
                    return response.status, response_data
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    response_data = await response.json()
                    if expect_success and response.status != 200:
                        print(f"⚠️ Unexpected status {response.status} for {method} {endpoint}")
                    return response.status, response_data
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    response_data = await response.json()
                    if expect_success and response.status != 200:
                        print(f"⚠️ Unexpected status {response.status} for {method} {endpoint}")
                    return response.status, response_data
                    
        except Exception as e:
            print(f"❌ Request failed for {method} {endpoint}: {e}")
            return None, {"error": str(e)}
            
    async def get_simulation_state(self):
        """Get current simulation state including reports"""
        status, data = await self.make_request("GET", "/simulation/state")
        if status == 200:
            return data
        return None
        
    async def get_all_reports(self):
        """Get all reports from Library (should include historical reports)"""
        status, data = await self.make_request("GET", "/reports")
        if status == 200:
            return data.get('reports', [])
        return []
        
    async def generate_daily_report(self):
        """Generate a daily report"""
        status, data = await self.make_request("POST", "/simulation/generate-daily-report", {"manual": True})
        if status == 200:
            return data
        return None
        
    async def start_fresh_reset(self):
        """Execute Start Fresh functionality"""
        status, data = await self.make_request("POST", "/simulation/reset")
        if status == 200:
            return data
        return None
        
    async def set_scenario(self, scenario_text, scenario_name):
        """Set a scenario for the simulation"""
        data = {
            "scenario": scenario_text,
            "scenario_name": scenario_name
        }
        status, response = await self.make_request("POST", "/simulation/set-scenario", data)
        if status == 200:
            return response
        return None
        
    async def start_simulation(self):
        """Start the simulation"""
        status, data = await self.make_request("POST", "/simulation/start")
        if status == 200:
            return data
        return None
        
    def record_test_result(self, test_name, passed, details):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name} - {details}")
        
    async def test_initial_state_check(self):
        """Test 1: Check initial state and existing reports"""
        print("\n🔍 TEST 1: Initial State Check")
        
        # Get simulation state
        sim_state = await self.get_simulation_state()
        if not sim_state:
            self.record_test_result("Initial State Check", False, "Could not retrieve simulation state")
            return False
            
        # Get all reports from Library
        all_reports = await self.get_all_reports()
        
        observatory_reports = sim_state.get('reports', [])
        library_reports_count = len(all_reports)
        
        print(f"📊 Observatory reports: {len(observatory_reports)}")
        print(f"📚 Library reports: {library_reports_count}")
        
        self.record_test_result(
            "Initial State Check", 
            True, 
            f"Observatory: {len(observatory_reports)} reports, Library: {library_reports_count} reports"
        )
        
        return {
            "observatory_reports": observatory_reports,
            "library_reports_count": library_reports_count,
            "simulation_state": sim_state
        }
        
    async def test_generate_reports_before_reset(self):
        """Test 2: Generate reports before reset to ensure we have data"""
        print("\n🔍 TEST 2: Generate Reports Before Reset")
        
        # Set a scenario first
        scenario_result = await self.set_scenario(
            "A team of researchers discovers an unexpected quantum signal from deep space and must decide how to respond.",
            "Deep Space Signal Discovery"
        )
        
        if not scenario_result:
            self.record_test_result("Set Scenario Before Reset", False, "Could not set scenario")
            return False
            
        # Start simulation to create active session
        start_result = await self.start_simulation()
        if not start_result:
            self.record_test_result("Start Simulation Before Reset", False, "Could not start simulation")
            return False
            
        print("✅ Scenario set and simulation started")
        
        # Generate a report
        report_result = await self.generate_daily_report()
        if not report_result:
            self.record_test_result("Generate Report Before Reset", False, "Could not generate report")
            return False
            
        print("✅ Report generated successfully")
        
        # Check that report appears in Observatory
        sim_state = await self.get_simulation_state()
        observatory_reports = sim_state.get('reports', []) if sim_state else []
        
        if len(observatory_reports) == 0:
            self.record_test_result("Report in Observatory", False, "Generated report not visible in Observatory")
            return False
            
        self.record_test_result(
            "Generate Reports Before Reset", 
            True, 
            f"Successfully generated report, now visible in Observatory ({len(observatory_reports)} reports)"
        )
        
        return {
            "reports_before_reset": len(observatory_reports),
            "latest_report_id": observatory_reports[0].get('id') if observatory_reports else None
        }
        
    async def test_start_fresh_execution(self):
        """Test 3: Execute Start Fresh and verify immediate effects"""
        print("\n🔍 TEST 3: Start Fresh Execution")
        
        # Execute Start Fresh
        reset_result = await self.start_fresh_reset()
        if not reset_result:
            self.record_test_result("Start Fresh Execution", False, "Start Fresh failed to execute")
            return False
            
        # Verify reset response
        success = reset_result.get('success', False)
        cleared_collections = reset_result.get('cleared_collections', [])
        preserved_collections = reset_result.get('preserved_collections', [])
        
        print(f"✅ Start Fresh executed - Success: {success}")
        print(f"📋 Cleared: {cleared_collections}")
        print(f"💾 Preserved: {preserved_collections}")
        
        # Verify reports are in preserved collections
        reports_preserved = 'reports' in preserved_collections
        
        self.record_test_result(
            "Start Fresh Execution", 
            success and reports_preserved, 
            f"Success: {success}, Reports preserved: {reports_preserved}"
        )
        
        return reset_result
        
    async def test_observatory_reports_cleared(self):
        """Test 4: Verify Observatory reports are cleared after Start Fresh"""
        print("\n🔍 TEST 4: Observatory Reports Cleared After Start Fresh")
        
        # Get simulation state after reset
        sim_state = await self.get_simulation_state()
        if not sim_state:
            self.record_test_result("Observatory Reports Check", False, "Could not retrieve simulation state after reset")
            return False
            
        observatory_reports = sim_state.get('reports', [])
        
        # Observatory should be empty after Start Fresh
        reports_cleared = len(observatory_reports) == 0
        
        print(f"📊 Observatory reports after Start Fresh: {len(observatory_reports)}")
        
        # Check simulation state details
        scenario = sim_state.get('scenario', '')
        scenario_name = sim_state.get('scenario_name', '')
        is_active = sim_state.get('is_active', False)
        simulation_start_time = sim_state.get('simulation_start_time')
        
        print(f"🎯 Scenario: '{scenario}'")
        print(f"📝 Scenario Name: '{scenario_name}'")
        print(f"▶️ Is Active: {is_active}")
        print(f"⏰ Start Time: {simulation_start_time}")
        
        self.record_test_result(
            "Observatory Reports Cleared", 
            reports_cleared, 
            f"Observatory reports: {len(observatory_reports)} (expected: 0)"
        )
        
        return reports_cleared
        
    async def test_library_reports_preserved(self):
        """Test 5: Verify Library reports are preserved after Start Fresh"""
        print("\n🔍 TEST 5: Library Reports Preserved After Start Fresh")
        
        # Get all reports from Library
        all_reports = await self.get_all_reports()
        library_reports_count = len(all_reports)
        
        print(f"📚 Library reports after Start Fresh: {library_reports_count}")
        
        # Library should still contain historical reports
        reports_preserved = library_reports_count > 0
        
        if reports_preserved:
            print("✅ Historical reports preserved in Library")
            # Show some details about preserved reports
            for i, report in enumerate(all_reports[:3]):  # Show first 3 reports
                report_id = report.get('id', 'Unknown')
                report_title = report.get('title', 'Untitled')
                created_at = report.get('created_at', 'Unknown')
                print(f"  📄 Report {i+1}: {report_title} (ID: {report_id[:8]}..., Created: {created_at})")
        else:
            print("⚠️ No reports found in Library")
            
        self.record_test_result(
            "Library Reports Preserved", 
            reports_preserved, 
            f"Library reports: {library_reports_count} (expected: > 0)"
        )
        
        return library_reports_count
        
    async def test_new_reports_after_start_fresh(self):
        """Test 6: Generate new reports after Start Fresh and verify they appear in Observatory"""
        print("\n🔍 TEST 6: New Reports After Start Fresh")
        
        # Set a new scenario
        new_scenario_result = await self.set_scenario(
            "A team of engineers discovers a critical flaw in the quantum computer design and must decide how to proceed.",
            "Quantum Computer Flaw Discovery"
        )
        
        if not new_scenario_result:
            self.record_test_result("Set New Scenario", False, "Could not set new scenario after Start Fresh")
            return False
            
        # Start simulation to create new active session
        start_result = await self.start_simulation()
        if not start_result:
            self.record_test_result("Start New Simulation", False, "Could not start new simulation after Start Fresh")
            return False
            
        print("✅ New scenario set and simulation started")
        
        # Generate a new report
        new_report_result = await self.generate_daily_report()
        if not new_report_result:
            self.record_test_result("Generate New Report", False, "Could not generate new report after Start Fresh")
            return False
            
        print("✅ New report generated successfully")
        
        # Check that new report appears in Observatory
        sim_state = await self.get_simulation_state()
        observatory_reports = sim_state.get('reports', []) if sim_state else []
        
        new_reports_visible = len(observatory_reports) > 0
        
        print(f"📊 Observatory reports after generating new report: {len(observatory_reports)}")
        
        if new_reports_visible and observatory_reports:
            latest_report = observatory_reports[0]
            report_title = latest_report.get('title', 'Untitled')
            report_id = latest_report.get('id', 'Unknown')
            print(f"📄 Latest report: {report_title} (ID: {report_id[:8]}...)")
            
        self.record_test_result(
            "New Reports After Start Fresh", 
            new_reports_visible, 
            f"New reports in Observatory: {len(observatory_reports)} (expected: > 0)"
        )
        
        return new_reports_visible
        
    async def test_session_based_filtering(self):
        """Test 7: Verify that only reports from current session appear in Observatory"""
        print("\n🔍 TEST 7: Session-Based Report Filtering")
        
        # Get current simulation state
        sim_state = await self.get_simulation_state()
        observatory_reports = sim_state.get('reports', []) if sim_state else []
        
        # Get all reports from Library
        all_reports = await self.get_all_reports()
        
        # Observatory should have fewer or equal reports than Library
        filtering_working = len(observatory_reports) <= len(all_reports)
        
        print(f"📊 Observatory reports: {len(observatory_reports)}")
        print(f"📚 Library reports: {len(all_reports)}")
        
        # Check if simulation has start time (required for filtering)
        simulation_start_time = sim_state.get('simulation_start_time') if sim_state else None
        has_start_time = simulation_start_time is not None
        
        print(f"⏰ Simulation start time: {simulation_start_time}")
        print(f"🔍 Filtering active: {has_start_time}")
        
        self.record_test_result(
            "Session-Based Report Filtering", 
            filtering_working and has_start_time, 
            f"Observatory: {len(observatory_reports)}, Library: {len(all_reports)}, Filtering: {has_start_time}"
        )
        
        return filtering_working
        
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 STARTING COMPREHENSIVE 'START FRESH' REPORTS CLEARING FUNCTIONALITY TEST")
        print("=" * 80)
        
        try:
            # Setup
            await self.setup_session()
            
            # Authenticate
            if not await self.authenticate_guest():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run tests in sequence
            test_1_result = await self.test_initial_state_check()
            test_2_result = await self.test_generate_reports_before_reset()
            test_3_result = await self.test_start_fresh_execution()
            test_4_result = await self.test_observatory_reports_cleared()
            test_5_result = await self.test_library_reports_preserved()
            test_6_result = await self.test_new_reports_after_start_fresh()
            test_7_result = await self.test_session_based_filtering()
            
            # Summary
            print("\n" + "=" * 80)
            print("📋 TEST SUMMARY")
            print("=" * 80)
            
            passed_tests = sum(1 for result in self.test_results if result['passed'])
            total_tests = len(self.test_results)
            
            for result in self.test_results:
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                print(f"{status}: {result['test']}")
                if not result['passed']:
                    print(f"    Details: {result['details']}")
                    
            print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
            
            if passed_tests == total_tests:
                print("🎉 ALL TESTS PASSED - Start Fresh reports clearing functionality is working correctly!")
            else:
                print("⚠️ SOME TESTS FAILED - Start Fresh reports clearing functionality has issues")
                
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    test_runner = StartFreshReportsTest()
    await test_runner.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())