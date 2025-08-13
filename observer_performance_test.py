#!/usr/bin/env python3
"""
Observer Chat Performance Testing
Tests the performance improvements implemented for Observer Chat functionality:
1. Agent Limit: Reduced from unlimited to maximum 3 agents
2. Request Timeout: Added 8-second timeout per agent to prevent hanging
3. Response Caching: Added intelligent caching for common messages
4. Error Handling: Improved fallback responses for timeouts and errors
"""

import requests
import json
import time
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
import statistics
import asyncio
import concurrent.futures
from collections import Counter

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": [],
    "performance_metrics": {}
}

def run_test(test_name, endpoint, method="GET", data=None, expected_status=200, auth_token=None, measure_time=True):
    """Run a test against the specified endpoint with performance measurement"""
    url = f"{API_URL}{endpoint}"
    print(f"\n{'='*60}\nTesting: {test_name}")
    print(f"URL: {method} {url}")
    
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return False, None, 0
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Status Code: {response.status_code}")
        if measure_time:
            print(f"Response Time: {response_time:.4f} seconds")
        
        # Check if response is JSON
        try:
            response_data = response.json()
            if len(json.dumps(response_data)) < 1000:  # Only print short responses
                print(f"Response: {json.dumps(response_data, indent=2)}")
            else:
                print(f"Response: Large response ({len(json.dumps(response_data))} chars)")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text[:200]}...")
            response_data = {}
        
        # Verify status code
        test_passed = response.status_code == expected_status
        
        result = "PASSED" if test_passed else "FAILED"
        print(f"Test Result: {result}")
        
        test_result = {
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "result": result,
            "response_time": response_time
        }
        
        test_results["tests"].append(test_result)
        
        if test_passed:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
        
        return test_passed, response_data, response_time
    
    except Exception as e:
        print(f"Error during test: {e}")
        test_results["tests"].append({
            "name": test_name,
            "endpoint": endpoint,
            "method": method,
            "result": "ERROR",
            "error": str(e)
        })
        test_results["failed"] += 1
        return False, None, 0

def authenticate():
    """Authenticate and get auth token"""
    print("\n" + "="*60)
    print("AUTHENTICATING FOR OBSERVER CHAT TESTING")
    print("="*60)
    
    # Try guest authentication first
    success, response, _ = run_test(
        "Guest Authentication",
        "/auth/test-login",
        method="POST",
        expected_status=200
    )
    
    if success and response:
        auth_token = response.get("access_token")
        user_data = response.get("user", {})
        user_id = user_data.get("id")
        print(f"✅ Authentication successful. User ID: {user_id}")
        return auth_token, user_id
    else:
        print("❌ Authentication failed")
        return None, None

def setup_simulation_with_agents(auth_token, num_agents=5):
    """Set up a simulation with multiple agents for testing"""
    print(f"\n" + "="*60)
    print(f"SETTING UP SIMULATION WITH {num_agents} AGENTS")
    print("="*60)
    
    # Reset simulation first
    success, _, _ = run_test(
        "Reset Simulation",
        "/simulation/reset",
        method="POST",
        auth_token=auth_token
    )
    
    if not success:
        print("⚠️ Failed to reset simulation, continuing anyway")
    
    # Create test agents with different archetypes
    archetypes = ["scientist", "leader", "skeptic", "optimist", "researcher"]
    agent_ids = []
    
    for i in range(num_agents):
        archetype = archetypes[i % len(archetypes)]
        agent_data = {
            "name": f"Test Agent {i+1}",
            "archetype": archetype,
            "goal": f"Test goal for agent {i+1}",
            "expertise": f"Test expertise in {archetype} domain",
            "background": f"Test background for {archetype} agent"
        }
        
        success, response, _ = run_test(
            f"Create Agent {i+1} ({archetype})",
            "/agents",
            method="POST",
            data=agent_data,
            auth_token=auth_token,
            measure_time=False
        )
        
        if success and response:
            agent_id = response.get("id")
            if agent_id:
                agent_ids.append(agent_id)
                print(f"✅ Created agent {i+1}: {agent_data['name']} ({archetype})")
            else:
                print(f"❌ Failed to get agent ID for agent {i+1}")
        else:
            print(f"❌ Failed to create agent {i+1}")
    
    print(f"\n✅ Created {len(agent_ids)} agents for testing")
    
    # Start simulation
    success, _, _ = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth_token=auth_token,
        measure_time=False
    )
    
    if success:
        print("✅ Simulation started successfully")
    else:
        print("❌ Failed to start simulation")
    
    return agent_ids

def test_cached_responses(auth_token):
    """Test cached responses for common messages"""
    print(f"\n" + "="*60)
    print("TESTING CACHED RESPONSES FOR COMMON MESSAGES")
    print("="*60)
    
    # Common messages that should trigger cached responses
    cached_messages = [
        "hello",
        "hello agents",
        "hi",
        "status",
        "what's the status",
        "progress",
        "how are we doing",
        "good work",
        "keep going",
        "well done"
    ]
    
    cached_response_times = []
    cache_hit_indicators = []
    
    for message in cached_messages:
        observer_data = {
            "observer_message": message
        }
        
        success, response, response_time = run_test(
            f"Cached Message: '{message}'",
            "/observer/send-message",
            method="POST",
            data=observer_data,
            auth_token=auth_token,
            expected_status=200
        )
        
        if success:
            cached_response_times.append(response_time)
            
            # Check if response indicates caching was used
            # Look for performance logs or quick response times
            if response_time < 5.0:  # Quick responses likely cached
                cache_hit_indicators.append(True)
                print(f"⚡ Fast response ({response_time:.2f}s) - likely cached")
            else:
                cache_hit_indicators.append(False)
                print(f"🐌 Slow response ({response_time:.2f}s) - likely generated")
        else:
            print(f"❌ Failed to send cached message: {message}")
    
    # Calculate cache performance
    if cached_response_times:
        avg_cached_time = statistics.mean(cached_response_times)
        cache_hit_rate = (sum(cache_hit_indicators) / len(cache_hit_indicators)) * 100
        
        print(f"\n📊 CACHED RESPONSE PERFORMANCE:")
        print(f"   • Average response time: {avg_cached_time:.2f}s")
        print(f"   • Estimated cache hit rate: {cache_hit_rate:.1f}%")
        print(f"   • Fast responses (< 5s): {sum(cache_hit_indicators)}/{len(cache_hit_indicators)}")
        
        test_results["performance_metrics"]["cached_responses"] = {
            "avg_time": avg_cached_time,
            "cache_hit_rate": cache_hit_rate,
            "fast_responses": sum(cache_hit_indicators),
            "total_tests": len(cache_hit_indicators)
        }
        
        return avg_cached_time, cache_hit_rate
    
    return None, 0

def test_complex_messages(auth_token):
    """Test complex messages that should use LLM generation with timeout"""
    print(f"\n" + "="*60)
    print("TESTING COMPLEX MESSAGES (LLM GENERATION WITH TIMEOUT)")
    print("="*60)
    
    complex_messages = [
        "I need you to analyze the quantum entanglement protocols and provide detailed recommendations for improving coherence times while maintaining error correction capabilities.",
        "Please evaluate our current research methodology and suggest improvements to our experimental design, considering both statistical significance and practical implementation constraints.",
        "What are your thoughts on the trade-offs between computational efficiency and accuracy in our current algorithms, and how might we optimize for both?"
    ]
    
    complex_response_times = []
    timeout_indicators = []
    
    for i, message in enumerate(complex_messages, 1):
        observer_data = {
            "observer_message": message
        }
        
        success, response, response_time = run_test(
            f"Complex Message {i}",
            "/observer/send-message",
            method="POST",
            data=observer_data,
            auth_token=auth_token,
            expected_status=200
        )
        
        if success:
            complex_response_times.append(response_time)
            
            # Check if response time indicates timeout protection is working
            if response_time > 8.0:  # Should not exceed timeout significantly
                timeout_indicators.append(False)
                print(f"⚠️ Response time ({response_time:.2f}s) exceeds expected timeout")
            else:
                timeout_indicators.append(True)
                print(f"✅ Response time ({response_time:.2f}s) within timeout limits")
                
            # Check response quality
            if response and "agent_responses" in response:
                agent_responses = response.get("agent_responses", {})
                messages = agent_responses.get("messages", [])
                agent_count = len([msg for msg in messages if msg.get("agent_name") != "Observer (You)"])
                print(f"   • Agent responses received: {agent_count}")
                
                if agent_count <= 3:
                    print(f"✅ Agent limit (≤3) respected: {agent_count} agents responded")
                else:
                    print(f"❌ Agent limit exceeded: {agent_count} agents responded")
        else:
            print(f"❌ Failed to send complex message {i}")
    
    # Calculate complex message performance
    if complex_response_times:
        avg_complex_time = statistics.mean(complex_response_times)
        timeout_success_rate = (sum(timeout_indicators) / len(timeout_indicators)) * 100
        
        print(f"\n📊 COMPLEX MESSAGE PERFORMANCE:")
        print(f"   • Average response time: {avg_complex_time:.2f}s")
        print(f"   • Timeout protection success: {timeout_success_rate:.1f}%")
        print(f"   • Responses within limits: {sum(timeout_indicators)}/{len(timeout_indicators)}")
        
        test_results["performance_metrics"]["complex_messages"] = {
            "avg_time": avg_complex_time,
            "timeout_success_rate": timeout_success_rate,
            "within_limits": sum(timeout_indicators),
            "total_tests": len(timeout_indicators)
        }
        
        return avg_complex_time, timeout_success_rate
    
    return None, 0

def test_agent_limitation(auth_token, total_agents):
    """Test that only 3 agents respond regardless of total agent count"""
    print(f"\n" + "="*60)
    print(f"TESTING AGENT LIMITATION (3 agents max from {total_agents} total)")
    print("="*60)
    
    test_message = "Hello everyone! I'd like to hear from all team members about our current progress."
    
    observer_data = {
        "observer_message": test_message
    }
    
    success, response, response_time = run_test(
        f"Agent Limitation Test ({total_agents} agents available)",
        "/observer/send-message",
        method="POST",
        data=observer_data,
        auth_token=auth_token,
        expected_status=200
    )
    
    if success and response:
        agent_responses = response.get("agent_responses", {})
        messages = agent_responses.get("messages", [])
        
        # Count non-observer messages
        agent_messages = [msg for msg in messages if msg.get("agent_name") != "Observer (You)"]
        responding_agents = len(agent_messages)
        
        print(f"📊 AGENT LIMITATION RESULTS:")
        print(f"   • Total agents in simulation: {total_agents}")
        print(f"   • Agents that responded: {responding_agents}")
        print(f"   • Response time: {response_time:.2f}s")
        
        # List responding agents
        if agent_messages:
            print(f"   • Responding agents:")
            for msg in agent_messages:
                agent_name = msg.get("agent_name", "Unknown")
                message_preview = msg.get("message", "")[:50] + "..."
                print(f"     - {agent_name}: {message_preview}")
        
        # Evaluate agent limitation
        if responding_agents <= 3:
            print(f"✅ Agent limitation working correctly: {responding_agents} ≤ 3")
            agent_limit_success = True
        else:
            print(f"❌ Agent limitation failed: {responding_agents} > 3")
            agent_limit_success = False
        
        test_results["performance_metrics"]["agent_limitation"] = {
            "total_agents": total_agents,
            "responding_agents": responding_agents,
            "limit_respected": agent_limit_success,
            "response_time": response_time
        }
        
        return agent_limit_success, responding_agents
    
    return False, 0

def test_concurrent_requests(auth_token):
    """Test concurrent observer messages to check for hanging/timeout issues"""
    print(f"\n" + "="*60)
    print("TESTING CONCURRENT OBSERVER REQUESTS")
    print("="*60)
    
    concurrent_messages = [
        "Status update please",
        "How are things going?",
        "Any progress to report?",
        "What's our current situation?",
        "Quick check-in needed"
    ]
    
    def send_observer_message(message, index):
        """Send a single observer message"""
        observer_data = {
            "observer_message": f"{message} (Request {index})"
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_URL}/observer/send-message",
                json=observer_data,
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=30  # 30 second timeout for concurrent test
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "index": index,
                "success": response.status_code == 200,
                "response_time": response_time,
                "status_code": response.status_code,
                "message": message
            }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                "index": index,
                "success": False,
                "response_time": response_time,
                "error": str(e),
                "message": message
            }
    
    print(f"Sending {len(concurrent_messages)} concurrent observer messages...")
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(send_observer_message, msg, i+1) 
            for i, msg in enumerate(concurrent_messages)
        ]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Analyze concurrent request results
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    print(f"\n📊 CONCURRENT REQUEST RESULTS:")
    print(f"   • Total requests: {len(concurrent_messages)}")
    print(f"   • Successful: {len(successful_requests)}")
    print(f"   • Failed: {len(failed_requests)}")
    print(f"   • Total time: {total_time:.2f}s")
    
    if successful_requests:
        response_times = [r["response_time"] for r in successful_requests]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"   • Average response time: {avg_response_time:.2f}s")
        print(f"   • Max response time: {max_response_time:.2f}s")
        print(f"   • Min response time: {min_response_time:.2f}s")
        
        # Check for hanging requests (> 30 seconds)
        hanging_requests = [r for r in results if r["response_time"] > 30]
        if hanging_requests:
            print(f"   ⚠️ Hanging requests detected: {len(hanging_requests)}")
        else:
            print(f"   ✅ No hanging requests detected")
    
    if failed_requests:
        print(f"   ❌ Failed requests:")
        for req in failed_requests:
            error = req.get("error", "Unknown error")
            print(f"     - Request {req['index']}: {error}")
    
    # Evaluate concurrent performance
    success_rate = (len(successful_requests) / len(concurrent_messages)) * 100
    no_hanging = len([r for r in results if r["response_time"] <= 30]) == len(results)
    
    test_results["performance_metrics"]["concurrent_requests"] = {
        "total_requests": len(concurrent_messages),
        "successful": len(successful_requests),
        "failed": len(failed_requests),
        "success_rate": success_rate,
        "no_hanging": no_hanging,
        "total_time": total_time
    }
    
    return success_rate, no_hanging

def test_baseline_comparison():
    """Compare current performance against the 17-27s baseline"""
    print(f"\n" + "="*60)
    print("BASELINE PERFORMANCE COMPARISON")
    print("="*60)
    
    metrics = test_results["performance_metrics"]
    
    # Extract key performance indicators
    cached_avg = metrics.get("cached_responses", {}).get("avg_time", 0)
    complex_avg = metrics.get("complex_messages", {}).get("avg_time", 0)
    cache_hit_rate = metrics.get("cached_responses", {}).get("cache_hit_rate", 0)
    agent_limit_working = metrics.get("agent_limitation", {}).get("limit_respected", False)
    concurrent_success = metrics.get("concurrent_requests", {}).get("success_rate", 0)
    
    print(f"📊 PERFORMANCE COMPARISON:")
    print(f"   • Baseline (old): 17-27 seconds")
    print(f"   • Cached responses: {cached_avg:.2f}s")
    print(f"   • Complex messages: {complex_avg:.2f}s")
    print(f"   • Cache hit rate: {cache_hit_rate:.1f}%")
    print(f"   • Agent limitation: {'✅ Working' if agent_limit_working else '❌ Failed'}")
    print(f"   • Concurrent success: {concurrent_success:.1f}%")
    
    # Evaluate improvements
    improvements = []
    issues = []
    
    if cached_avg > 0 and cached_avg < 17:
        improvement = ((17 - cached_avg) / 17) * 100
        improvements.append(f"Cached responses {improvement:.1f}% faster than baseline")
    
    if complex_avg > 0 and complex_avg < 17:
        improvement = ((17 - complex_avg) / 17) * 100
        improvements.append(f"Complex messages {improvement:.1f}% faster than baseline")
    
    if cache_hit_rate >= 70:
        improvements.append(f"High cache hit rate achieved ({cache_hit_rate:.1f}%)")
    elif cache_hit_rate > 0:
        issues.append(f"Cache hit rate below target ({cache_hit_rate:.1f}% < 70%)")
    
    if agent_limit_working:
        improvements.append("Agent limitation working correctly (≤3 agents)")
    else:
        issues.append("Agent limitation not working properly")
    
    if concurrent_success >= 80:
        improvements.append(f"Good concurrent request handling ({concurrent_success:.1f}%)")
    else:
        issues.append(f"Poor concurrent request handling ({concurrent_success:.1f}%)")
    
    print(f"\n✅ IMPROVEMENTS DETECTED:")
    for improvement in improvements:
        print(f"   • {improvement}")
    
    if issues:
        print(f"\n⚠️ ISSUES DETECTED:")
        for issue in issues:
            print(f"   • {issue}")
    
    # Overall assessment
    overall_success = (
        len(improvements) >= 3 and  # At least 3 improvements
        len(issues) <= 1 and       # At most 1 issue
        (cached_avg < 10 or complex_avg < 15)  # Significant speed improvement
    )
    
    return overall_success, improvements, issues

def print_final_summary():
    """Print final test summary"""
    print("\n" + "="*80)
    print("OBSERVER CHAT PERFORMANCE TEST SUMMARY")
    print("="*80)
    
    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 TEST RESULTS:")
    print(f"   • Total tests: {total_tests}")
    print(f"   • Passed: {test_results['passed']}")
    print(f"   • Failed: {test_results['failed']}")
    print(f"   • Success rate: {success_rate:.1f}%")
    
    # Performance metrics summary
    metrics = test_results["performance_metrics"]
    
    if "cached_responses" in metrics:
        cached = metrics["cached_responses"]
        print(f"\n⚡ CACHED RESPONSES:")
        print(f"   • Average time: {cached['avg_time']:.2f}s")
        print(f"   • Cache hit rate: {cached['cache_hit_rate']:.1f}%")
        print(f"   • Fast responses: {cached['fast_responses']}/{cached['total_tests']}")
    
    if "complex_messages" in metrics:
        complex_msg = metrics["complex_messages"]
        print(f"\n🧠 COMPLEX MESSAGES:")
        print(f"   • Average time: {complex_msg['avg_time']:.2f}s")
        print(f"   • Timeout protection: {complex_msg['timeout_success_rate']:.1f}%")
        print(f"   • Within limits: {complex_msg['within_limits']}/{complex_msg['total_tests']}")
    
    if "agent_limitation" in metrics:
        agent_limit = metrics["agent_limitation"]
        print(f"\n👥 AGENT LIMITATION:")
        print(f"   • Total agents: {agent_limit['total_agents']}")
        print(f"   • Responding agents: {agent_limit['responding_agents']}")
        print(f"   • Limit respected: {'✅' if agent_limit['limit_respected'] else '❌'}")
    
    if "concurrent_requests" in metrics:
        concurrent = metrics["concurrent_requests"]
        print(f"\n🔄 CONCURRENT REQUESTS:")
        print(f"   • Success rate: {concurrent['success_rate']:.1f}%")
        print(f"   • No hanging: {'✅' if concurrent['no_hanging'] else '❌'}")
        print(f"   • Total time: {concurrent['total_time']:.2f}s")
    
    print("\n" + "="*80)

def main():
    """Main test execution"""
    print("🚀 OBSERVER CHAT PERFORMANCE TESTING")
    print("Testing performance improvements:")
    print("1. Agent Limit: Maximum 3 agents")
    print("2. Request Timeout: 8-second timeout per agent")
    print("3. Response Caching: Intelligent caching for common messages")
    print("4. Error Handling: Improved fallback responses")
    
    # Step 1: Authenticate
    auth_token, user_id = authenticate()
    if not auth_token:
        print("❌ Authentication failed. Cannot proceed with testing.")
        return False
    
    # Step 2: Set up simulation with 5+ agents to test limitation
    agent_ids = setup_simulation_with_agents(auth_token, num_agents=5)
    if len(agent_ids) < 3:
        print("⚠️ Could not create enough agents for comprehensive testing")
    
    # Step 3: Test cached responses
    print("\n🎯 TESTING PERFORMANCE IMPROVEMENTS...")
    cached_avg, cache_hit_rate = test_cached_responses(auth_token)
    
    # Step 4: Test complex messages with timeout protection
    complex_avg, timeout_success = test_complex_messages(auth_token)
    
    # Step 5: Test agent limitation
    agent_limit_success, responding_agents = test_agent_limitation(auth_token, len(agent_ids))
    
    # Step 6: Test concurrent requests
    concurrent_success, no_hanging = test_concurrent_requests(auth_token)
    
    # Step 7: Compare against baseline
    overall_success, improvements, issues = test_baseline_comparison()
    
    # Step 8: Print final summary
    print_final_summary()
    
    # Final assessment
    if overall_success:
        print("\n🎉 OBSERVER CHAT PERFORMANCE IMPROVEMENTS SUCCESSFUL!")
        print("✅ Significant performance improvements detected")
        print("✅ All key optimizations are working correctly")
        return True
    else:
        print("\n⚠️ OBSERVER CHAT PERFORMANCE NEEDS ATTENTION")
        print("❌ Some performance improvements may not be working as expected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)