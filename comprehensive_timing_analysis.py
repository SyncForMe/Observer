#!/usr/bin/env python3
"""
COMPREHENSIVE TIMING ANALYSIS
Based on database analysis, create comprehensive tests for conversation generation timing issues.
"""

import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ai_simulation')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print("🕐 COMPREHENSIVE CONVERSATION TIMING ANALYSIS")
print("="*80)
print("Based on database analysis findings:")
print("✅ Sequential message creation is working (unique timestamps)")
print("🔍 Need to investigate why users experience '10 messages at once'")
print("🔍 Need to measure actual generation timing and bottlenecks")
print("="*80)

class TimingAnalyzer:
    def __init__(self):
        self.client = None
        self.db = None
        self.auth_token = None
        self.results = {
            "tests": [],
            "timing_data": {},
            "root_causes": []
        }
    
    async def connect_db(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            print("✅ Connected to MongoDB")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def authenticate_api(self):
        """Authenticate with the API"""
        try:
            login_data = {
                "email": "dino@cytonic.com",
                "password": "Observerinho8"
            }
            
            # Try with a longer timeout and the external URL
            response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
            
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                print("✅ API authentication successful")
                return True
            else:
                print(f"❌ API authentication failed: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ API authentication timed out")
            return False
        except Exception as e:
            print(f"❌ API authentication error: {e}")
            return False
    
    def make_api_request(self, method, endpoint, data=None, timeout=60):
        """Make authenticated API request"""
        if not self.auth_token:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{API_URL}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            else:
                return None
            
            return response
        except Exception as e:
            print(f"❌ API request failed: {e}")
            return None
    
    async def analyze_existing_patterns(self):
        """Analyze existing conversation patterns in database"""
        print("\n📊 ANALYZING EXISTING CONVERSATION PATTERNS")
        print("-" * 50)
        
        try:
            # Get recent conversations with detailed timing
            conversations = await self.db.conversations.find({}).sort("created_at", -1).limit(10).to_list(10)
            
            timing_patterns = {
                "bulk_creation_count": 0,
                "sequential_creation_count": 0,
                "average_messages_per_conversation": 0,
                "generation_time_estimates": []
            }
            
            total_messages = 0
            
            for i, conv in enumerate(conversations):
                messages = conv.get('messages', [])
                message_count = len(messages)
                total_messages += message_count
                
                print(f"\nConversation {i+1}:")
                print(f"  ID: {conv.get('id', 'N/A')[:8]}...")
                print(f"  Messages: {message_count}")
                print(f"  Created: {conv.get('created_at', 'N/A')}")
                
                if message_count > 1:
                    timestamps = [msg.get('timestamp') for msg in messages if msg.get('timestamp')]
                    
                    if timestamps:
                        unique_timestamps = len(set(timestamps))
                        
                        if unique_timestamps == 1:
                            timing_patterns["bulk_creation_count"] += 1
                            print(f"  ⚠️  BULK CREATION: All messages same timestamp")
                        else:
                            timing_patterns["sequential_creation_count"] += 1
                            print(f"  ✅ SEQUENTIAL: {unique_timestamps} unique timestamps")
                            
                            # Calculate time span for sequential messages
                            sorted_timestamps = sorted(timestamps)
                            first_time = datetime.fromisoformat(sorted_timestamps[0].replace('Z', '+00:00'))
                            last_time = datetime.fromisoformat(sorted_timestamps[-1].replace('Z', '+00:00'))
                            time_span = (last_time - first_time).total_seconds()
                            
                            print(f"  ⏱️  Time span: {time_span:.2f} seconds")
                            timing_patterns["generation_time_estimates"].append(time_span)
            
            # Calculate averages
            if conversations:
                timing_patterns["average_messages_per_conversation"] = total_messages / len(conversations)
            
            if timing_patterns["generation_time_estimates"]:
                avg_gen_time = sum(timing_patterns["generation_time_estimates"]) / len(timing_patterns["generation_time_estimates"])
                print(f"\n📊 TIMING ANALYSIS SUMMARY:")
                print(f"  Average messages per conversation: {timing_patterns['average_messages_per_conversation']:.1f}")
                print(f"  Sequential creation: {timing_patterns['sequential_creation_count']}")
                print(f"  Bulk creation: {timing_patterns['bulk_creation_count']}")
                print(f"  Average generation time: {avg_gen_time:.2f} seconds")
                
                if avg_gen_time > 30:
                    self.results["root_causes"].append(f"Long generation time ({avg_gen_time:.1f}s) causes delayed bulk display")
                
                if timing_patterns["bulk_creation_count"] > 0:
                    self.results["root_causes"].append("Some conversations show bulk message creation")
            
            self.results["timing_data"]["existing_patterns"] = timing_patterns
            
        except Exception as e:
            print(f"❌ Pattern analysis error: {e}")
    
    async def test_conversation_generation_timing(self):
        """Test actual conversation generation timing"""
        print("\n🚀 TESTING CONVERSATION GENERATION TIMING")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No API authentication - skipping API tests")
            return
        
        try:
            # Set up scenario
            scenario_data = {
                "scenario": "A team of specialists needs to solve a critical technical problem under time pressure",
                "scenario_name": "Critical Problem Solving Test"
            }
            
            response = self.make_api_request('POST', '/simulation/set-scenario', scenario_data)
            if not response or response.status_code != 200:
                print("❌ Failed to set scenario")
                return
            
            print("✅ Scenario set successfully")
            
            # Get initial conversation count
            response = self.make_api_request('GET', '/conversations')
            initial_count = 0
            if response and response.status_code == 200:
                initial_count = len(response.json())
                print(f"📊 Initial conversation count: {initial_count}")
            
            # Monitor database during generation
            monitoring_data = {"snapshots": [], "stop": False}
            
            async def monitor_database():
                """Monitor database changes during generation"""
                snapshot_count = 0
                while not monitoring_data["stop"] and snapshot_count < 30:
                    try:
                        # Get current conversation count
                        current_count = await self.db.conversations.count_documents({})
                        
                        # Get latest conversation if exists
                        latest_conv = await self.db.conversations.find_one({}, sort=[("created_at", -1)])
                        latest_message_count = 0
                        if latest_conv:
                            latest_message_count = len(latest_conv.get('messages', []))
                        
                        snapshot = {
                            "timestamp": time.time(),
                            "conversation_count": current_count,
                            "latest_message_count": latest_message_count,
                            "snapshot_number": snapshot_count
                        }
                        
                        monitoring_data["snapshots"].append(snapshot)
                        snapshot_count += 1
                        
                        await asyncio.sleep(0.5)  # Check every 500ms
                        
                    except Exception as e:
                        print(f"Monitor error: {e}")
                        break
            
            # Start monitoring
            monitor_task = asyncio.create_task(monitor_database())
            
            # Generate conversation with timing
            print("🔄 Starting conversation generation...")
            gen_start = time.time()
            
            response = self.make_api_request('POST', '/conversation/generate', timeout=120)
            
            gen_end = time.time()
            generation_time = gen_end - gen_start
            
            # Stop monitoring
            monitoring_data["stop"] = True
            await monitor_task
            
            print(f"⏱️  Total generation time: {generation_time:.2f} seconds")
            
            if response and response.status_code == 200:
                print("✅ Conversation generated successfully")
                
                # Analyze what was created
                final_response = self.make_api_request('GET', '/conversations')
                if final_response and final_response.status_code == 200:
                    final_conversations = final_response.json()
                    final_count = len(final_conversations)
                    new_conversations = final_count - initial_count
                    
                    print(f"📈 New conversations created: {new_conversations}")
                    
                    if new_conversations > 0:
                        latest_conv = final_conversations[-1]
                        messages = latest_conv.get('messages', [])
                        print(f"💬 Messages in latest conversation: {len(messages)}")
                        
                        # Analyze monitoring data
                        snapshots = monitoring_data["snapshots"]
                        print(f"📊 Database monitoring snapshots: {len(snapshots)}")
                        
                        if len(snapshots) > 1:
                            print("Database changes during generation:")
                            for i, snapshot in enumerate(snapshots[::3]):  # Show every 3rd snapshot
                                print(f"  {i*3+1:2d}. Conversations: {snapshot['conversation_count']}, Messages: {snapshot['latest_message_count']}")
                            
                            # Check for progressive updates
                            message_counts = [s['latest_message_count'] for s in snapshots]
                            progressive_updates = any(message_counts[i] < message_counts[i+1] for i in range(len(message_counts)-1))
                            
                            if progressive_updates:
                                print("✅ Progressive message updates detected during generation")
                            else:
                                print("⚠️  No progressive updates - messages may appear all at once")
                                self.results["root_causes"].append("No progressive message updates during generation")
                        
                        # Performance analysis
                        timing_analysis = {
                            "generation_time": generation_time,
                            "messages_created": len(messages),
                            "time_per_message": generation_time / len(messages) if messages else 0,
                            "progressive_updates": progressive_updates if 'progressive_updates' in locals() else False
                        }
                        
                        self.results["timing_data"]["generation_test"] = timing_analysis
                        
                        if generation_time > 30:
                            print(f"⚠️  SLOW GENERATION: {generation_time:.2f}s is too long")
                            self.results["root_causes"].append(f"Slow generation time ({generation_time:.1f}s)")
                        elif generation_time > 15:
                            print(f"⚠️  ABOVE TARGET: {generation_time:.2f}s (target: <15s)")
                        else:
                            print(f"✅ GOOD TIMING: {generation_time:.2f}s within target")
                
            else:
                print(f"❌ Conversation generation failed: {response.status_code if response else 'No response'}")
                
        except Exception as e:
            print(f"❌ Generation timing test error: {e}")
    
    async def test_simulation_controls(self):
        """Test simulation control timing"""
        print("\n⏯️  TESTING SIMULATION CONTROL TIMING")
        print("-" * 50)
        
        if not self.auth_token:
            print("❌ No API authentication - skipping control tests")
            return
        
        controls = [
            ("start", "/simulation/start"),
            ("pause", "/simulation/pause"),
            ("resume", "/simulation/resume")
        ]
        
        control_timings = {}
        
        for name, endpoint in controls:
            print(f"Testing {name}...")
            start_time = time.time()
            
            response = self.make_api_request('POST', endpoint)
            
            end_time = time.time()
            duration = end_time - start_time
            
            control_timings[name] = {
                "duration": duration,
                "status_code": response.status_code if response else None
            }
            
            print(f"  {name.capitalize()}: {duration:.2f}s (status: {response.status_code if response else 'Failed'})")
            
            if duration > 2:
                print(f"    ⚠️  SLOW: {duration:.2f}s causes UI delays")
                self.results["root_causes"].append(f"Slow {name} operation ({duration:.1f}s)")
            
            time.sleep(0.5)  # Small delay between operations
        
        self.results["timing_data"]["simulation_controls"] = control_timings
    
    async def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TIMING ANALYSIS REPORT")
        print("="*80)
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        if self.results["root_causes"]:
            for i, cause in enumerate(self.results["root_causes"], 1):
                print(f"  {i}. {cause}")
        else:
            print("  ✅ No major timing issues identified")
        
        print("\n📊 TIMING DATA SUMMARY:")
        
        # Existing patterns
        if "existing_patterns" in self.results["timing_data"]:
            patterns = self.results["timing_data"]["existing_patterns"]
            print(f"  Database Analysis:")
            print(f"    - Average messages per conversation: {patterns.get('average_messages_per_conversation', 0):.1f}")
            print(f"    - Sequential creation instances: {patterns.get('sequential_creation_count', 0)}")
            print(f"    - Bulk creation instances: {patterns.get('bulk_creation_count', 0)}")
            
            if patterns.get("generation_time_estimates"):
                avg_time = sum(patterns["generation_time_estimates"]) / len(patterns["generation_time_estimates"])
                print(f"    - Average generation time: {avg_time:.2f}s")
        
        # Generation test
        if "generation_test" in self.results["timing_data"]:
            gen_data = self.results["timing_data"]["generation_test"]
            print(f"  Live Generation Test:")
            print(f"    - Generation time: {gen_data.get('generation_time', 0):.2f}s")
            print(f"    - Messages created: {gen_data.get('messages_created', 0)}")
            print(f"    - Time per message: {gen_data.get('time_per_message', 0):.2f}s")
            print(f"    - Progressive updates: {gen_data.get('progressive_updates', False)}")
        
        # Simulation controls
        if "simulation_controls" in self.results["timing_data"]:
            controls = self.results["timing_data"]["simulation_controls"]
            print(f"  Simulation Controls:")
            for name, data in controls.items():
                duration = data.get('duration', 0)
                status = data.get('status_code', 'N/A')
                print(f"    - {name.capitalize()}: {duration:.2f}s (status: {status})")
        
        print("\n💡 RECOMMENDATIONS:")
        
        recommendations = []
        
        # Check for slow generation
        gen_time = self.results["timing_data"].get("generation_test", {}).get("generation_time", 0)
        if gen_time > 30:
            recommendations.append("Optimize conversation generation to reduce wait time before bulk display")
        
        # Check for lack of progressive updates
        progressive = self.results["timing_data"].get("generation_test", {}).get("progressive_updates", True)
        if not progressive:
            recommendations.append("Implement progressive message display during generation")
        
        # Check for slow controls
        controls = self.results["timing_data"].get("simulation_controls", {})
        slow_controls = [name for name, data in controls.items() if data.get('duration', 0) > 2]
        if slow_controls:
            recommendations.append(f"Optimize simulation controls: {', '.join(slow_controls)}")
        
        # Check for bulk creation
        bulk_count = self.results["timing_data"].get("existing_patterns", {}).get("bulk_creation_count", 0)
        if bulk_count > 0:
            recommendations.append("Investigate and fix bulk message creation instances")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ System performance appears to be within acceptable ranges")
        
        print("\n🎯 CONCLUSION:")
        
        if len(self.results["root_causes"]) == 0:
            print("  ✅ No critical timing issues found in backend")
            print("  🔍 User experience issues may be frontend-related")
        elif len(self.results["root_causes"]) <= 2:
            print("  ⚠️  Minor timing issues identified")
            print("  🔧 Addressable with targeted optimizations")
        else:
            print("  ❌ Multiple timing issues identified")
            print("  🚨 Requires comprehensive performance optimization")
        
        print("\n" + "="*80)

async def main():
    """Main analysis function"""
    analyzer = TimingAnalyzer()
    
    # Connect to database
    if not await analyzer.connect_db():
        print("❌ Cannot proceed without database connection")
        return
    
    # Try to authenticate with API (optional)
    analyzer.authenticate_api()
    
    # Run analysis
    await analyzer.analyze_existing_patterns()
    await analyzer.test_conversation_generation_timing()
    await analyzer.test_simulation_controls()
    await analyzer.generate_final_report()
    
    # Close database connection
    if analyzer.client:
        analyzer.client.close()

if __name__ == "__main__":
    asyncio.run(main())