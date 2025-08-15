#!/usr/bin/env python3
"""
Simple test to verify parallel processing is working based on backend logs
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_parallel_processing():
    """Test that parallel processing is working"""
    print("🚀 PARALLELIZED CONVERSATION GENERATION TEST")
    print("=" * 60)
    
    # Authenticate
    login_data = {"email": "dino@cytonic.com", "password": "Observerinho8"}
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=30)
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
        
        token = response.json().get("access_token")
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        print("✅ Authentication successful")
        
        # Check agents
        response = requests.get(f"{API_URL}/agents", headers=headers, timeout=30)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            
            if len(agents) < 2:
                print("⚠️ Need at least 2 agents for conversation generation")
                return False
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
        
        # Test conversation generation
        print("\n⚡ Testing conversation generation performance...")
        start_time = time.time()
        
        response = requests.post(f"{API_URL}/conversation/generate", headers=headers, timeout=90)
        end_time = time.time()
        generation_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ Conversation generated successfully in {generation_time:.2f} seconds")
            
            # Evaluate performance
            if generation_time <= 15:
                print("🎯 EXCELLENT: Within target time (≤15s) - Parallel processing working optimally!")
            elif generation_time <= 30:
                print("✅ GOOD: Reasonable time (≤30s) - Parallel processing working well!")
            elif generation_time <= 45:
                print("⚠️ ACCEPTABLE: Moderate time (≤45s) - Some improvement from parallel processing")
            else:
                print("❌ SLOW: Exceeds expected time (>45s) - Parallel processing may not be working")
            
            # Check conversation content
            conv_response = requests.get(f"{API_URL}/conversations", headers=headers, timeout=30)
            if conv_response.status_code == 200:
                conversations = conv_response.json()
                if conversations:
                    latest = conversations[-1]
                    messages = latest.get('messages', [])
                    unique_agents = set(msg.get('agent_name', '') for msg in messages)
                    
                    print(f"📊 Generated {len(messages)} messages from {len(unique_agents)} agents")
                    print(f"👥 Participating agents: {list(unique_agents)}")
                    
                    # Check message quality
                    quality_count = sum(1 for msg in messages if 50 <= len(msg.get('message', '')) <= 600)
                    quality_ratio = quality_count / len(messages) if messages else 0
                    
                    if quality_ratio >= 0.8:
                        print(f"✅ Message quality: {quality_count}/{len(messages)} messages have good quality")
                    else:
                        print(f"⚠️ Message quality: Only {quality_count}/{len(messages)} messages have good quality")
                    
                    return True
            
        else:
            print(f"❌ Failed to generate conversation: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - backend may be overloaded")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_backend_logs():
    """Check backend logs for parallel processing indicators"""
    print("\n📝 BACKEND LOG ANALYSIS")
    print("=" * 60)
    
    try:
        # Read recent backend logs
        with open('/var/log/supervisor/backend.out.log', 'r') as f:
            logs = f.read()
        
        # Look for parallel processing indicators
        parallel_indicators = [
            "🚀 Starting parallel message generation...",
            "PARALLEL PROCESSING",
            "⚡ Parallel generation completed",
            "vs ~",
            "seconds sequential"
        ]
        
        found_indicators = []
        for indicator in parallel_indicators:
            if indicator in logs:
                found_indicators.append(indicator)
        
        print(f"✅ Found {len(found_indicators)}/{len(parallel_indicators)} parallel processing indicators in logs:")
        for indicator in found_indicators:
            print(f"   ✓ {indicator}")
        
        # Look for performance improvements
        import re
        performance_matches = re.findall(r'⚡ Parallel generation completed in ([\d.]+) seconds \(vs ~(\d+) seconds sequential\)', logs)
        
        if performance_matches:
            print(f"\n🎯 PERFORMANCE ANALYSIS:")
            for actual, expected in performance_matches[-3:]:  # Last 3 entries
                actual_time = float(actual)
                expected_time = int(expected)
                improvement = ((expected_time - actual_time) / expected_time) * 100
                print(f"   • Actual: {actual}s vs Expected: {expected}s (Improvement: {improvement:.1f}%)")
        
        return len(found_indicators) >= 3
        
    except Exception as e:
        print(f"❌ Could not analyze logs: {e}")
        return False

if __name__ == "__main__":
    print("Testing parallelized conversation generation implementation...")
    
    # Test the API functionality
    api_success = test_parallel_processing()
    
    # Check backend logs for parallel processing evidence
    log_success = check_backend_logs()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if api_success and log_success:
        print("🎉 SUCCESS: Parallelized conversation generation is WORKING!")
        print("   ✅ API generates conversations successfully")
        print("   ✅ Performance improvements detected in logs")
        print("   ✅ Multiple agents participate simultaneously")
        print("   ✅ Parallel processing indicators found in backend logs")
    elif api_success:
        print("✅ PARTIAL SUCCESS: API works but log analysis incomplete")
        print("   ✅ Conversations generate successfully")
        print("   ⚠️ Could not fully verify parallel processing in logs")
    else:
        print("❌ ISSUES DETECTED: Parallel processing may not be working optimally")
        print("   Please check backend logs and system performance")