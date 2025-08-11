#!/usr/bin/env python3
"""
Comprehensive Observer Chat Performance Testing Script
Tests performance issues, response times, concurrent interactions, and system behavior
"""
import requests
import json
import time
import os
import sys
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import statistics
from datetime import datetime
import uuid

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

# Test results tracking
performance_results = {
    "message_sending_times": [],
    "response_generation_times": [],
    "concurrent_test_results": [],
    "database_performance": [],
    "system_stability": [],
    "passed_tests": 0,
    "failed_tests": 0,
    "total_tests": 0
}

def log_test_result(test_name, passed, details="", response_time=None):
    """Log test results with performance metrics"""
    global performance_results
    performance_results["total_tests"] += 1
    
    if passed:
        performance_results["passed_tests"] += 1
        status = "✅ PASS"
    else:
        performance_results["failed_tests"] += 1
        status = "❌ FAIL"
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status} - {test_name}")
    if details:
        print(f"    📋 {details}")
    if response_time:
        print(f"    ⏱️  Response Time: {response_time:.3f}s")
    print()

def authenticate_guest():
    """Authenticate as guest user and return token"""
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
        auth_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user', {}).get('id')
            log_test_result("Guest Authentication", True, f"User ID: {user_id}", auth_time)
            return token, user_id
        else:
            log_test_result("Guest Authentication", False, f"Status: {response.status_code}")
            return None, None
    except Exception as e:
        log_test_result("Guest Authentication", False, f"Error: {str(e)}")
        return None, None

def setup_test_agents(token):
    """Create test agents for observer chat testing"""
    headers = {"Authorization": f"Bearer {token}"}
    agents_created = []
    
    test_agents = [
        {
            "name": "Dr. Performance Tester",
            "archetype": "scientist",
            "goal": "Test system performance and response times",
            "expertise": "Performance analysis and system optimization",
            "background": "Expert in measuring and optimizing system performance"
        },
        {
            "name": "Prof. Concurrent Handler", 
            "archetype": "researcher",
            "goal": "Handle multiple simultaneous requests efficiently",
            "expertise": "Concurrent processing and load testing",
            "background": "Specialist in concurrent system behavior"
        },
        {
            "name": "Agent Response Timer",
            "archetype": "optimist", 
            "goal": "Provide quick and efficient responses",
            "expertise": "Rapid response generation and communication",
            "background": "Focused on fast, quality communication"
        }
    ]
    
    for agent_data in test_agents:
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/agents", json=agent_data, headers=headers, timeout=15)
            creation_time = time.time() - start_time
            
            if response.status_code == 200:
                agent = response.json()
                agents_created.append(agent)
                log_test_result(f"Agent Creation: {agent_data['name']}", True, 
                              f"Agent ID: {agent.get('id', 'Unknown')}", creation_time)
            else:
                log_test_result(f"Agent Creation: {agent_data['name']}", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            log_test_result(f"Agent Creation: {agent_data['name']}", False, f"Error: {str(e)}")
    
    return agents_created

def test_message_sending_performance(token):
    """Test 1: Message Sending Delays - Measure how long it takes to send observer messages"""
    print("🚀 TESTING MESSAGE SENDING PERFORMANCE")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_messages = [
        "Hello agents! Please focus on performance optimization.",
        "Can you analyze the current system bottlenecks?", 
        "What are your recommendations for improving response times?",
        "Please prioritize the most critical performance issues.",
        "Let's discuss concurrent processing capabilities."
    ]
    
    sending_times = []
    
    for i, message in enumerate(test_messages, 1):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": message},
                headers=headers,
                timeout=30
            )
            end_time = time.time()
            sending_time = end_time - start_time
            sending_times.append(sending_time)
            
            if response.status_code == 200:
                data = response.json()
                agent_responses = data.get('agent_responses', {})
                messages_count = len(agent_responses.get('messages', []))
                
                log_test_result(f"Observer Message {i} Sending", True, 
                              f"Messages received: {messages_count}, Content: '{message[:50]}...'", 
                              sending_time)
                
                # Track performance metrics
                performance_results["message_sending_times"].append(sending_time)
                
            else:
                log_test_result(f"Observer Message {i} Sending", False, 
                              f"Status: {response.status_code}, Message: '{message[:50]}...'")
        except Exception as e:
            log_test_result(f"Observer Message {i} Sending", False, f"Error: {str(e)}")
    
    # Performance Analysis
    if sending_times:
        avg_time = statistics.mean(sending_times)
        min_time = min(sending_times)
        max_time = max(sending_times)
        
        print(f"📊 MESSAGE SENDING PERFORMANCE ANALYSIS:")
        print(f"    Average Time: {avg_time:.3f}s")
        print(f"    Fastest Time: {min_time:.3f}s") 
        print(f"    Slowest Time: {max_time:.3f}s")
        print(f"    Performance Rating: {'🟢 EXCELLENT' if avg_time < 5 else '🟡 GOOD' if avg_time < 15 else '🔴 NEEDS IMPROVEMENT'}")
        print()

def test_response_generation_performance(token):
    """Test 2: Response Generation Time - Measure agent response times to observer messages"""
    print("🤖 TESTING RESPONSE GENERATION PERFORMANCE")
    headers = {"Authorization": f"Bearer {token}"}
    
    complex_messages = [
        "Analyze the quantum computing implications for our current architecture and provide detailed technical recommendations.",
        "What are the performance bottlenecks in concurrent message processing and how can we optimize the system?",
        "Please evaluate the database query performance and suggest indexing strategies for better response times."
    ]
    
    generation_times = []
    
    for i, message in enumerate(complex_messages, 1):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": message},
                headers=headers,
                timeout=45  # Longer timeout for complex responses
            )
            end_time = time.time()
            generation_time = end_time - start_time
            generation_times.append(generation_time)
            
            if response.status_code == 200:
                data = response.json()
                agent_responses = data.get('agent_responses', {})
                messages = agent_responses.get('messages', [])
                
                # Analyze response quality
                total_chars = sum(len(msg.get('message', '')) for msg in messages if isinstance(msg, dict))
                avg_response_length = total_chars / len(messages) if messages else 0
                
                log_test_result(f"Complex Response Generation {i}", True,
                              f"Agents: {len(messages)}, Avg Length: {avg_response_length:.0f} chars",
                              generation_time)
                
                performance_results["response_generation_times"].append(generation_time)
                
            else:
                log_test_result(f"Complex Response Generation {i}", False,
                              f"Status: {response.status_code}")
                
        except Exception as e:
            log_test_result(f"Complex Response Generation {i}", False, f"Error: {str(e)}")
    
    # Performance Analysis
    if generation_times:
        avg_time = statistics.mean(generation_times)
        min_time = min(generation_times)
        max_time = max(generation_times)
        
        print(f"📊 RESPONSE GENERATION PERFORMANCE ANALYSIS:")
        print(f"    Average Time: {avg_time:.3f}s")
        print(f"    Fastest Time: {min_time:.3f}s")
        print(f"    Slowest Time: {max_time:.3f}s")
        print(f"    Performance Rating: {'🟢 EXCELLENT' if avg_time < 10 else '🟡 GOOD' if avg_time < 25 else '🔴 NEEDS IMPROVEMENT'}")
        print()

def test_concurrent_interactions(token):
    """Test 3: Concurrent Interactions - Test observer messages while conversations are running"""
    print("🔄 TESTING CONCURRENT INTERACTIONS")
    headers = {"Authorization": f"Bearer {token}"}
    
    def send_observer_message(message_data):
        """Send observer message in separate thread"""
        message, thread_id = message_data
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": f"[Thread {thread_id}] {message}"},
                headers=headers,
                timeout=30
            )
            end_time = time.time()
            
            return {
                "thread_id": thread_id,
                "success": response.status_code == 200,
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "message": message
            }
        except Exception as e:
            return {
                "thread_id": thread_id,
                "success": False,
                "response_time": 0,
                "error": str(e),
                "message": message
            }
    
    # Test concurrent observer messages
    concurrent_messages = [
        ("Quick performance check", 1),
        ("System status report please", 2), 
        ("Any bottlenecks detected?", 3),
        ("Response time analysis needed", 4),
        ("Concurrent processing test", 5)
    ]
    
    print("    🔀 Sending 5 concurrent observer messages...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_message = {executor.submit(send_observer_message, msg_data): msg_data for msg_data in concurrent_messages}
        
        concurrent_results = []
        for future in as_completed(future_to_message):
            result = future.result()
            concurrent_results.append(result)
    
    total_time = time.time() - start_time
    
    # Analyze concurrent performance
    successful_requests = [r for r in concurrent_results if r["success"]]
    failed_requests = [r for r in concurrent_results if not r["success"]]
    
    if successful_requests:
        avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
        max_response_time = max([r["response_time"] for r in successful_requests])
        min_response_time = min([r["response_time"] for r in successful_requests])
        
        log_test_result("Concurrent Observer Messages", True,
                      f"Success: {len(successful_requests)}/5, Avg: {avg_response_time:.3f}s, Range: {min_response_time:.3f}-{max_response_time:.3f}s",
                      total_time)
        
        performance_results["concurrent_test_results"].append({
            "total_requests": 5,
            "successful": len(successful_requests),
            "failed": len(failed_requests),
            "avg_response_time": avg_response_time,
            "total_time": total_time
        })
    else:
        log_test_result("Concurrent Observer Messages", False,
                      f"All requests failed. Errors: {[r.get('error', 'Unknown') for r in failed_requests]}")

def test_system_performance_impact(token):
    """Test 4: System Performance - Check if observer chat impacts overall system performance"""
    print("⚡ TESTING SYSTEM PERFORMANCE IMPACT")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Baseline performance test - regular API calls
    baseline_times = []
    print("    📊 Measuring baseline API performance...")
    
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                baseline_times.append(end_time - start_time)
        except Exception as e:
            print(f"    ⚠️  Baseline test {i+1} failed: {e}")
    
    # Send observer messages and measure impact
    print("    📨 Sending observer messages and measuring system impact...")
    observer_times = []
    system_times = []
    
    for i in range(3):
        try:
            # Send observer message
            obs_start = time.time()
            obs_response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": f"Performance impact test {i+1}"},
                headers=headers,
                timeout=30
            )
            obs_end = time.time()
            
            if obs_response.status_code == 200:
                observer_times.append(obs_end - obs_start)
                
                # Immediately test system responsiveness
                sys_start = time.time()
                sys_response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
                sys_end = time.time()
                
                if sys_response.status_code == 200:
                    system_times.append(sys_end - sys_start)
                    
        except Exception as e:
            print(f"    ⚠️  Performance impact test {i+1} failed: {e}")
    
    # Analyze performance impact
    if baseline_times and system_times:
        baseline_avg = statistics.mean(baseline_times)
        system_avg = statistics.mean(system_times)
        performance_impact = ((system_avg - baseline_avg) / baseline_avg) * 100
        
        impact_rating = "🟢 MINIMAL" if abs(performance_impact) < 20 else "🟡 MODERATE" if abs(performance_impact) < 50 else "🔴 SIGNIFICANT"
        
        log_test_result("System Performance Impact", True,
                      f"Baseline: {baseline_avg:.3f}s, During Observer: {system_avg:.3f}s, Impact: {performance_impact:+.1f}% ({impact_rating})")
        
        performance_results["system_stability"].append({
            "baseline_avg": baseline_avg,
            "during_observer_avg": system_avg,
            "performance_impact_percent": performance_impact
        })
    else:
        log_test_result("System Performance Impact", False, "Insufficient data for analysis")

def test_database_performance(token):
    """Test 5: Database Performance - Check database performance with observer message operations"""
    print("🗄️ TESTING DATABASE PERFORMANCE")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test observer message storage performance
    storage_times = []
    retrieval_times = []
    
    print("    💾 Testing observer message storage performance...")
    for i in range(5):
        try:
            # Store observer message
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": f"Database performance test message {i+1}"},
                headers=headers,
                timeout=25
            )
            storage_time = time.time() - start_time
            
            if response.status_code == 200:
                storage_times.append(storage_time)
                
                # Test message retrieval
                retrieval_start = time.time()
                retrieval_response = requests.get(f"{API_URL}/observer/messages", headers=headers, timeout=10)
                retrieval_time = time.time() - retrieval_start
                
                if retrieval_response.status_code == 200:
                    retrieval_times.append(retrieval_time)
                    messages = retrieval_response.json()
                    
                    log_test_result(f"Database Operation {i+1}", True,
                                  f"Storage: {storage_time:.3f}s, Retrieval: {retrieval_time:.3f}s, Messages: {len(messages)}")
                else:
                    log_test_result(f"Database Operation {i+1}", False,
                                  f"Retrieval failed: {retrieval_response.status_code}")
            else:
                log_test_result(f"Database Operation {i+1}", False,
                              f"Storage failed: {response.status_code}")
                
        except Exception as e:
            log_test_result(f"Database Operation {i+1}", False, f"Error: {str(e)}")
    
    # Analyze database performance
    if storage_times and retrieval_times:
        avg_storage = statistics.mean(storage_times)
        avg_retrieval = statistics.mean(retrieval_times)
        
        print(f"📊 DATABASE PERFORMANCE ANALYSIS:")
        print(f"    Average Storage Time: {avg_storage:.3f}s")
        print(f"    Average Retrieval Time: {avg_retrieval:.3f}s")
        print(f"    Storage Rating: {'🟢 EXCELLENT' if avg_storage < 5 else '🟡 GOOD' if avg_storage < 15 else '🔴 NEEDS IMPROVEMENT'}")
        print(f"    Retrieval Rating: {'🟢 EXCELLENT' if avg_retrieval < 1 else '🟡 GOOD' if avg_retrieval < 3 else '🔴 NEEDS IMPROVEMENT'}")
        print()
        
        performance_results["database_performance"].append({
            "avg_storage_time": avg_storage,
            "avg_retrieval_time": avg_retrieval,
            "total_operations": len(storage_times)
        })

def test_observer_workflow_integration(token):
    """Test 6: Complete Observer Workflow - Test integration with conversation generation"""
    print("🔗 TESTING OBSERVER WORKFLOW INTEGRATION")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Step 1: Start simulation
        start_time = time.time()
        start_response = requests.post(f"{API_URL}/simulation/start", headers=headers, timeout=10)
        start_time_taken = time.time() - start_time
        
        if start_response.status_code == 200:
            log_test_result("Simulation Start", True, "Simulation started successfully", start_time_taken)
            
            # Step 2: Send observer message
            obs_start = time.time()
            obs_response = requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": "Please analyze the current situation and provide your expert recommendations."},
                headers=headers,
                timeout=30
            )
            obs_time = time.time() - obs_start
            
            if obs_response.status_code == 200:
                obs_data = obs_response.json()
                messages = obs_data.get('agent_responses', {}).get('messages', [])
                log_test_result("Observer Message in Active Simulation", True,
                              f"Received {len(messages)} agent responses", obs_time)
                
                # Step 3: Generate regular conversation after observer message
                conv_start = time.time()
                conv_response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=30)
                conv_time = time.time() - conv_start
                
                if conv_response.status_code == 200:
                    conv_data = conv_response.json()
                    conv_messages = conv_data.get('messages', [])
                    log_test_result("Conversation After Observer Message", True,
                                  f"Generated {len(conv_messages)} conversation messages", conv_time)
                    
                    # Step 4: Check simulation state persistence
                    state_start = time.time()
                    state_response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=10)
                    state_time = time.time() - state_start
                    
                    if state_response.status_code == 200:
                        state_data = state_response.json()
                        is_active = state_data.get('is_active', False)
                        log_test_result("Simulation State Persistence", True,
                                      f"Simulation active: {is_active}", state_time)
                    else:
                        log_test_result("Simulation State Persistence", False,
                                      f"Status: {state_response.status_code}")
                else:
                    log_test_result("Conversation After Observer Message", False,
                                  f"Status: {conv_response.status_code}")
            else:
                log_test_result("Observer Message in Active Simulation", False,
                              f"Status: {obs_response.status_code}")
        else:
            log_test_result("Simulation Start", False, f"Status: {start_response.status_code}")
            
    except Exception as e:
        log_test_result("Observer Workflow Integration", False, f"Error: {str(e)}")

def generate_performance_report():
    """Generate comprehensive performance report"""
    print("=" * 80)
    print("📊 COMPREHENSIVE OBSERVER CHAT PERFORMANCE REPORT")
    print("=" * 80)
    
    # Test Summary
    total_tests = performance_results["total_tests"]
    passed_tests = performance_results["passed_tests"]
    failed_tests = performance_results["failed_tests"]
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"🎯 TEST SUMMARY:")
    print(f"    Total Tests: {total_tests}")
    print(f"    Passed: {passed_tests}")
    print(f"    Failed: {failed_tests}")
    print(f"    Success Rate: {success_rate:.1f}%")
    print()
    
    # Performance Metrics
    if performance_results["message_sending_times"]:
        avg_sending = statistics.mean(performance_results["message_sending_times"])
        print(f"📨 MESSAGE SENDING PERFORMANCE:")
        print(f"    Average Time: {avg_sending:.3f}s")
        print(f"    Rating: {'🟢 EXCELLENT' if avg_sending < 5 else '🟡 GOOD' if avg_sending < 15 else '🔴 NEEDS IMPROVEMENT'}")
        print()
    
    if performance_results["response_generation_times"]:
        avg_generation = statistics.mean(performance_results["response_generation_times"])
        print(f"🤖 RESPONSE GENERATION PERFORMANCE:")
        print(f"    Average Time: {avg_generation:.3f}s")
        print(f"    Rating: {'🟢 EXCELLENT' if avg_generation < 10 else '🟡 GOOD' if avg_generation < 25 else '🔴 NEEDS IMPROVEMENT'}")
        print()
    
    if performance_results["concurrent_test_results"]:
        concurrent_data = performance_results["concurrent_test_results"][0]
        print(f"🔄 CONCURRENT PROCESSING:")
        print(f"    Success Rate: {concurrent_data['successful']}/{concurrent_data['total_requests']}")
        print(f"    Average Response Time: {concurrent_data['avg_response_time']:.3f}s")
        print()
    
    if performance_results["database_performance"]:
        db_data = performance_results["database_performance"][0]
        print(f"🗄️ DATABASE PERFORMANCE:")
        print(f"    Storage Time: {db_data['avg_storage_time']:.3f}s")
        print(f"    Retrieval Time: {db_data['avg_retrieval_time']:.3f}s")
        print()
    
    # Overall Assessment
    print(f"🏆 OVERALL ASSESSMENT:")
    if success_rate >= 90:
        print(f"    Status: 🟢 EXCELLENT - Observer Chat system is performing optimally")
    elif success_rate >= 75:
        print(f"    Status: 🟡 GOOD - Observer Chat system is functional with minor issues")
    else:
        print(f"    Status: 🔴 NEEDS IMPROVEMENT - Observer Chat system has significant issues")
    
    print()
    print("=" * 80)

def main():
    """Main test execution function"""
    print("🚀 STARTING COMPREHENSIVE OBSERVER CHAT PERFORMANCE TESTING")
    print("=" * 80)
    
    # Authenticate
    token, user_id = authenticate_guest()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    print(f"✅ Authenticated as user: {user_id}")
    print()
    
    # Setup test agents
    agents = setup_test_agents(token)
    if len(agents) < 2:
        print("⚠️  Warning: Insufficient agents created. Some tests may be limited.")
    
    print(f"✅ Created {len(agents)} test agents")
    print()
    
    # Run performance tests
    try:
        test_message_sending_performance(token)
        test_response_generation_performance(token)
        test_concurrent_interactions(token)
        test_system_performance_impact(token)
        test_database_performance(token)
        test_observer_workflow_integration(token)
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
    
    # Generate final report
    generate_performance_report()

if __name__ == "__main__":
    main()