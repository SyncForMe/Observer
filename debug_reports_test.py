#!/usr/bin/env python3
"""
Debug script to investigate why reports aren't showing in Observatory
"""

import asyncio
import aiohttp
import json
import jwt
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = 'https://simulated-agents.preview.emergentagent.com'
API_BASE = f"{BACKEND_URL}/api"

async def debug_reports_issue():
    """Debug the reports visibility issue"""
    
    # Setup session
    session = aiohttp.ClientSession()
    
    try:
        # Create JWT token
        jwt_secret = "test_jwt_secret_for_observer_message_testing_12345"
        user_payload = {
            "sub": "test-user-123",
            "user_id": "test-user-123",
            "email": "test@example.com",
            "name": "Test User",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        auth_token = jwt.encode(user_payload, jwt_secret, algorithm="HS256")
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        print("🔍 DEBUGGING REPORTS VISIBILITY ISSUE")
        print("=" * 60)
        
        # Step 1: Check initial simulation state
        print("\n1. Initial Simulation State:")
        async with session.get(f"{API_BASE}/simulation/state", headers=headers) as response:
            state_data = await response.json()
            print(f"   Scenario: '{state_data.get('scenario', '')}'")
            print(f"   Scenario Name: '{state_data.get('scenario_name', '')}'")
            print(f"   Is Active: {state_data.get('is_active', False)}")
            print(f"   Start Time: {state_data.get('simulation_start_time')}")
            print(f"   Reports: {len(state_data.get('reports', []))}")
        
        # Step 2: Set scenario
        print("\n2. Setting Scenario:")
        scenario_data = {
            "scenario": "Debug test scenario for reports investigation",
            "scenario_name": "Debug Reports Test"
        }
        async with session.post(f"{API_BASE}/simulation/set-scenario", headers=headers, json=scenario_data) as response:
            scenario_result = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Response: {scenario_result}")
        
        # Step 3: Start simulation
        print("\n3. Starting Simulation:")
        async with session.post(f"{API_BASE}/simulation/start", headers=headers) as response:
            start_result = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Response: {start_result}")
        
        # Step 4: Check simulation state after start
        print("\n4. Simulation State After Start:")
        async with session.get(f"{API_BASE}/simulation/state", headers=headers) as response:
            state_data = await response.json()
            print(f"   Scenario: '{state_data.get('scenario', '')}'")
            print(f"   Scenario Name: '{state_data.get('scenario_name', '')}'")
            print(f"   Is Active: {state_data.get('is_active', False)}")
            print(f"   Start Time: {state_data.get('simulation_start_time')}")
            print(f"   Reports: {len(state_data.get('reports', []))}")
            
            # Store start time for comparison
            simulation_start_time = state_data.get('simulation_start_time')
        
        # Step 5: Generate report
        print("\n5. Generating Daily Report:")
        async with session.post(f"{API_BASE}/simulation/generate-daily-report", headers=headers, json={"manual": True}) as response:
            report_result = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Success: {report_result.get('success', False)}")
            if 'report_id' in report_result:
                print(f"   Report ID: {report_result['report_id']}")
        
        # Step 6: Check all reports in library
        print("\n6. All Reports in Library:")
        async with session.get(f"{API_BASE}/reports", headers=headers) as response:
            reports_data = await response.json()
            all_reports = reports_data.get('reports', [])
            print(f"   Total reports: {len(all_reports)}")
            
            if all_reports:
                latest_report = all_reports[0]  # Should be newest first
                print(f"   Latest report ID: {latest_report.get('id')}")
                print(f"   Latest report created: {latest_report.get('created_at')}")
                print(f"   Latest report title: {latest_report.get('title')}")
                
                # Compare times
                if simulation_start_time:
                    print(f"   Simulation start: {simulation_start_time}")
                    print(f"   Report created:   {latest_report.get('created_at')}")
                    
                    # Parse times for comparison
                    try:
                        if isinstance(simulation_start_time, str):
                            sim_start = datetime.fromisoformat(simulation_start_time.replace('Z', '+00:00'))
                        else:
                            sim_start = simulation_start_time
                            
                        report_created = datetime.fromisoformat(latest_report.get('created_at'))
                        
                        print(f"   Report after start: {report_created > sim_start}")
                        print(f"   Time difference: {report_created - sim_start}")
                    except Exception as e:
                        print(f"   Time comparison error: {e}")
        
        # Step 7: Check simulation state after report generation
        print("\n7. Simulation State After Report Generation:")
        async with session.get(f"{API_BASE}/simulation/state", headers=headers) as response:
            state_data = await response.json()
            print(f"   Scenario: '{state_data.get('scenario', '')}'")
            print(f"   Scenario Name: '{state_data.get('scenario_name', '')}'")
            print(f"   Is Active: {state_data.get('is_active', False)}")
            print(f"   Start Time: {state_data.get('simulation_start_time')}")
            print(f"   Reports: {len(state_data.get('reports', []))}")
            
            # Check filtering conditions
            current_scenario = state_data.get('scenario', '')
            simulation_start_time = state_data.get('simulation_start_time')
            
            print(f"\n   FILTERING CONDITIONS:")
            print(f"   Has scenario: {bool(current_scenario)} ('{current_scenario}')")
            print(f"   Has start time: {bool(simulation_start_time)} ({simulation_start_time})")
            print(f"   Should show reports: {bool(current_scenario and simulation_start_time)}")
        
        print("\n" + "=" * 60)
        print("🎯 ANALYSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(debug_reports_issue())