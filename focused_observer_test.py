#!/usr/bin/env python3
"""
Focused Observer Chat Performance Analysis
Tests specific performance bottlenecks and response times
"""
import requests
import json
import time
import os
from dotenv import load_dotenv
import statistics

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def authenticate_guest():
    """Quick authentication"""
    response = requests.post(f"{API_URL}/auth/test-login", timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token'), data.get('user', {}).get('id')
    return None, None

def test_single_observer_message_performance():
    """Test single observer message performance in detail"""
    print("🔍 FOCUSED OBSERVER MESSAGE PERFORMANCE TEST")
    print("=" * 60)
    
    token, user_id = authenticate_guest()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test single observer message with detailed timing
    message = "Please provide a quick status update on system performance."
    
    print(f"📨 Sending observer message: '{message}'")
    print("⏱️  Measuring detailed performance metrics...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/observer/send-message",
            json={"observer_message": message},
            headers=headers,
            timeout=45
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            agent_responses = data.get('agent_responses', {})
            messages = agent_responses.get('messages', [])
            
            # Analyze response details
            observer_msg = None
            agent_msgs = []
            
            for msg in messages:
                if isinstance(msg, dict):
                    if msg.get('agent_name') == 'Observer (You)':
                        observer_msg = msg
                    else:
                        agent_msgs.append(msg)
            
            print(f"✅ SUCCESS - Observer message processed")
            print(f"    📊 Total Response Time: {total_time:.3f}s")
            print(f"    🤖 Agent Responses: {len(agent_msgs)}")
            print(f"    📝 Observer Message Included: {'Yes' if observer_msg else 'No'}")
            
            if agent_msgs:
                avg_length = sum(len(msg.get('message', '')) for msg in agent_msgs) / len(agent_msgs)
                print(f"    📏 Average Response Length: {avg_length:.0f} characters")
                
                # Show sample responses
                print(f"    💬 Sample Agent Responses:")
                for i, msg in enumerate(agent_msgs[:3], 1):
                    agent_name = msg.get('agent_name', 'Unknown')
                    message_text = msg.get('message', '')[:100]
                    print(f"        {i}. {agent_name}: {message_text}...")
            
            # Performance rating
            if total_time < 10:
                rating = "🟢 EXCELLENT"
            elif total_time < 20:
                rating = "🟡 GOOD"
            else:
                rating = "🔴 NEEDS IMPROVEMENT"
            
            print(f"    🏆 Performance Rating: {rating}")
            
        else:
            print(f"❌ FAILED - Status Code: {response.status_code}")
            print(f"    Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Request exceeded 45 seconds")
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")

def test_observer_message_retrieval():
    """Test observer message retrieval performance"""
    print("\n🗄️ OBSERVER MESSAGE RETRIEVAL TEST")
    print("=" * 60)
    
    token, user_id = authenticate_guest()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("📥 Testing observer message retrieval...")
    
    start_time = time.time()
    
    try:
        response = requests.get(f"{API_URL}/observer/messages", headers=headers, timeout=10)
        end_time = time.time()
        retrieval_time = end_time - start_time
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ SUCCESS - Messages retrieved")
            print(f"    ⏱️  Retrieval Time: {retrieval_time:.3f}s")
            print(f"    📊 Messages Count: {len(messages)}")
            
            if messages:
                latest_msg = messages[0]
                print(f"    📝 Latest Message: '{latest_msg.get('message', '')[:50]}...'")
                print(f"    🕐 Timestamp: {latest_msg.get('timestamp', 'Unknown')}")
            
            # Performance rating for retrieval
            if retrieval_time < 1:
                rating = "🟢 EXCELLENT"
            elif retrieval_time < 3:
                rating = "🟡 GOOD"
            else:
                rating = "🔴 NEEDS IMPROVEMENT"
            
            print(f"    🏆 Retrieval Performance: {rating}")
            
        else:
            print(f"❌ FAILED - Status Code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")

def test_system_responsiveness_during_observer():
    """Test system responsiveness while observer messages are being processed"""
    print("\n⚡ SYSTEM RESPONSIVENESS TEST")
    print("=" * 60)
    
    token, user_id = authenticate_guest()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing system responsiveness during observer message processing...")
    
    # Test baseline system response
    print("    📊 Measuring baseline system response...")
    baseline_times = []
    
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                baseline_times.append(end_time - start_time)
        except:
            pass
    
    if baseline_times:
        baseline_avg = statistics.mean(baseline_times)
        print(f"    ✅ Baseline Response Time: {baseline_avg:.3f}s")
    else:
        print(f"    ❌ Could not establish baseline")
        return
    
    # Now test responsiveness after sending observer message
    print("    📨 Sending observer message and testing system response...")
    
    try:
        # Send observer message (don't wait for completion)
        import threading
        
        def send_observer_message():
            requests.post(
                f"{API_URL}/observer/send-message",
                json={"observer_message": "System responsiveness test - please respond briefly."},
                headers=headers,
                timeout=30
            )
        
        # Start observer message in background
        observer_thread = threading.Thread(target=send_observer_message)
        observer_thread.start()
        
        # Wait a moment then test system responsiveness
        time.sleep(2)
        
        response_times = []
        for i in range(3):
            try:
                start_time = time.time()
                response = requests.get(f"{API_URL}/simulation/state", headers=headers, timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            except:
                pass
        
        if response_times:
            during_avg = statistics.mean(response_times)
            impact = ((during_avg - baseline_avg) / baseline_avg) * 100
            
            print(f"    ✅ Response Time During Observer: {during_avg:.3f}s")
            print(f"    📈 Performance Impact: {impact:+.1f}%")
            
            if abs(impact) < 20:
                rating = "🟢 MINIMAL IMPACT"
            elif abs(impact) < 50:
                rating = "🟡 MODERATE IMPACT"
            else:
                rating = "🔴 SIGNIFICANT IMPACT"
            
            print(f"    🏆 Impact Rating: {rating}")
        else:
            print(f"    ❌ Could not measure response during observer processing")
        
        # Wait for observer thread to complete
        observer_thread.join(timeout=30)
        
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")

def main():
    """Run focused performance tests"""
    print("🎯 FOCUSED OBSERVER CHAT PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    test_single_observer_message_performance()
    test_observer_message_retrieval()
    test_system_responsiveness_during_observer()
    
    print("\n" + "=" * 80)
    print("📋 PERFORMANCE ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()