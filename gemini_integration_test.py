#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
from dotenv import load_dotenv
import uuid
import statistics
from collections import Counter

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

def test_gemini_integration():
    """Test the Gemini API integration for conversation generation"""
    print("\n" + "="*80)
    print("TESTING GEMINI API INTEGRATION FOR CONVERSATION GENERATION")
    print("="*80)
    
    # Step 1: Login with admin credentials
    print("\nStep 1: Logging in with admin credentials")
    login_data = {
        "email": "dino@cytonic.com",
        "password": "Observerinho8"
    }
    
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed with status code {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False, "Login failed"
    
    login_data = login_response.json()
    auth_token = login_data.get("access_token")
    user_data = login_data.get("user", {})
    user_id = user_data.get("id")
    
    print(f"✅ Login successful. User ID: {user_id}")
    
    # Set up headers with auth token
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 2: Check if Gemini API key is configured
    print("\nStep 2: Checking Gemini API key configuration")
    
    # Load backend/.env to check for Gemini API key
    load_dotenv('/app/backend/.env')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
        print("❌ Gemini API key not configured in backend/.env")
        return False, "Gemini API key not configured"
    
    print(f"✅ Gemini API key found in backend/.env: {gemini_api_key[:5]}...{gemini_api_key[-5:]}")
    
    # Check the usage endpoint to see if API is configured
    usage_response = requests.get(f"{API_URL}/usage", headers=headers)
    
    if usage_response.status_code != 200:
        print(f"❌ Failed to get API usage with status code {usage_response.status_code}")
        print(f"Response: {usage_response.text}")
    else:
        usage_data = usage_response.json()
        print(f"✅ API usage endpoint working. Current usage: {usage_data.get('requests', 0)} requests")
    
    # Step 3: Get current agents
    print("\nStep 3: Getting current agents")
    
    agents_response = requests.get(f"{API_URL}/agents", headers=headers)
    
    if agents_response.status_code != 200:
        print(f"❌ Failed to get agents with status code {agents_response.status_code}")
        print(f"Response: {agents_response.text}")
        return False, "Failed to get agents"
    
    agents = agents_response.json()
    agent_count = len(agents)
    
    print(f"✅ Found {agent_count} agents")
    
    # If no agents, add some test agents
    if agent_count < 2:
        print("\nAdding test agents since we need at least 2 for conversation generation")
        
        # Add a scientist agent
        scientist_data = {
            "name": "Dr. Emma Watson",
            "archetype": "scientist",
            "personality": {
                "extroversion": 4,
                "optimism": 6,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 6
            },
            "goal": "Advance scientific understanding through rigorous research",
            "expertise": "Quantum physics and computational modeling",
            "background": "PhD in Theoretical Physics with 10 years of research experience"
        }
        
        scientist_response = requests.post(f"{API_URL}/agents", json=scientist_data, headers=headers)
        
        if scientist_response.status_code != 200:
            print(f"❌ Failed to add scientist agent with status code {scientist_response.status_code}")
            print(f"Response: {scientist_response.text}")
        else:
            print(f"✅ Added scientist agent: {scientist_data['name']}")
        
        # Add a leader agent
        leader_data = {
            "name": "Marcus Chen",
            "archetype": "leader",
            "personality": {
                "extroversion": 8,
                "optimism": 7,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 9
            },
            "goal": "Lead the team to successful project completion",
            "expertise": "Project management and strategic planning",
            "background": "MBA with 15 years of leadership experience in tech companies"
        }
        
        leader_response = requests.post(f"{API_URL}/agents", json=leader_data, headers=headers)
        
        if leader_response.status_code != 200:
            print(f"❌ Failed to add leader agent with status code {leader_response.status_code}")
            print(f"Response: {leader_response.text}")
        else:
            print(f"✅ Added leader agent: {leader_data['name']}")
        
        # Add a skeptic agent
        skeptic_data = {
            "name": "Dr. Sarah Johnson",
            "archetype": "skeptic",
            "personality": {
                "extroversion": 5,
                "optimism": 3,
                "curiosity": 8,
                "cooperativeness": 6,
                "energy": 7
            },
            "goal": "Ensure all decisions are based on solid evidence",
            "expertise": "Risk assessment and critical analysis",
            "background": "PhD in Economics with focus on decision theory"
        }
        
        skeptic_response = requests.post(f"{API_URL}/agents", json=skeptic_data, headers=headers)
        
        if skeptic_response.status_code != 200:
            print(f"❌ Failed to add skeptic agent with status code {skeptic_response.status_code}")
            print(f"Response: {skeptic_response.text}")
        else:
            print(f"✅ Added skeptic agent: {skeptic_data['name']}")
        
        # Get updated agent list
        agents_response = requests.get(f"{API_URL}/agents", headers=headers)
        
        if agents_response.status_code != 200:
            print(f"❌ Failed to get updated agents with status code {agents_response.status_code}")
            print(f"Response: {agents_response.text}")
            return False, "Failed to get updated agents"
        
        agents = agents_response.json()
        agent_count = len(agents)
        
        print(f"✅ Now have {agent_count} agents")
    
    # Step 4: Start simulation if not already started
    print("\nStep 4: Starting simulation")
    
    simulation_start_response = requests.post(f"{API_URL}/simulation/start", headers=headers)
    
    if simulation_start_response.status_code not in [200, 201]:
        print(f"❌ Failed to start simulation with status code {simulation_start_response.status_code}")
        print(f"Response: {simulation_start_response.text}")
        return False, "Failed to start simulation"
    
    print(f"✅ Simulation started or was already running")
    
    # Step 5: Set a scenario
    print("\nStep 5: Setting a scenario")
    
    scenario_data = {
        "scenario": "The team is working on a quantum computing project that could revolutionize cryptography. They need to discuss the technical challenges, potential applications, and ethical implications.",
        "scenario_name": "Quantum Computing Project"
    }
    
    scenario_response = requests.post(f"{API_URL}/simulation/set-scenario", json=scenario_data, headers=headers)
    
    if scenario_response.status_code != 200:
        print(f"❌ Failed to set scenario with status code {scenario_response.status_code}")
        print(f"Response: {scenario_response.text}")
        return False, "Failed to set scenario"
    
    print(f"✅ Scenario set: {scenario_data['scenario_name']}")
    
    # Step 6: Generate conversation
    print("\nStep 6: Generating conversation with Gemini API")
    
    # Measure response time
    start_time = time.time()
    
    conversation_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
    
    end_time = time.time()
    response_time = end_time - start_time
    
    if conversation_response.status_code != 200:
        print(f"❌ Failed to generate conversation with status code {conversation_response.status_code}")
        print(f"Response: {conversation_response.text}")
        return False, "Failed to generate conversation"
    
    conversation_data = conversation_response.json()
    messages = conversation_data.get("messages", [])
    
    print(f"✅ Conversation generated with {len(messages)} messages in {response_time:.2f} seconds")
    
    # Step 7: Analyze conversation quality
    print("\nStep 7: Analyzing conversation quality")
    
    # Print the conversation
    print("\nGenerated Conversation:")
    print("-" * 50)
    
    message_lengths = []
    
    for msg in messages:
        agent_name = msg.get("agent_name", "Unknown")
        message = msg.get("message", "")
        message_lengths.append(len(message))
        
        print(f"{agent_name}: {message}")
        print("-" * 50)
    
    # Calculate statistics
    avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
    max_length = max(message_lengths) if message_lengths else 0
    min_length = min(message_lengths) if message_lengths else 0
    
    print("\nMessage Length Statistics:")
    print(f"Average: {avg_length:.1f} characters")
    print(f"Maximum: {max_length} characters")
    print(f"Minimum: {min_length} characters")
    
    # Check for quality indicators
    quality_score = 0
    max_quality_score = 5
    
    # 1. Message length - good responses should be substantial
    if avg_length > 200:
        quality_score += 1
        print("✅ Messages have substantial length (avg > 200 chars)")
    else:
        print("❌ Messages are too short (avg <= 200 chars)")
    
    # 2. Coherence - check if messages reference each other
    coherence_detected = False
    for i in range(1, len(messages)):
        current_msg = messages[i].get("message", "").lower()
        prev_agent_name = messages[i-1].get("agent_name", "").split()[0].lower()  # Get first name
        
        if prev_agent_name in current_msg:
            coherence_detected = True
            break
    
    if coherence_detected:
        quality_score += 1
        print("✅ Messages reference each other (coherence detected)")
    else:
        print("❌ Messages don't reference each other (low coherence)")
    
    # 3. Relevance to scenario
    scenario_keywords = scenario_data["scenario"].lower().split()
    scenario_keywords = [word for word in scenario_keywords if len(word) > 4]  # Only consider substantial words
    
    relevance_count = 0
    for msg in messages:
        message = msg.get("message", "").lower()
        for keyword in scenario_keywords:
            if keyword in message:
                relevance_count += 1
                break
    
    relevance_ratio = relevance_count / len(messages) if messages else 0
    
    if relevance_ratio > 0.5:
        quality_score += 1
        print(f"✅ Messages are relevant to the scenario (relevance ratio: {relevance_ratio:.2f})")
    else:
        print(f"❌ Messages have low relevance to the scenario (relevance ratio: {relevance_ratio:.2f})")
    
    # 4. Response time - good for real-time conversation
    if response_time < 5.0:
        quality_score += 1
        print(f"✅ Fast response time: {response_time:.2f} seconds")
    else:
        print(f"❌ Slow response time: {response_time:.2f} seconds")
    
    # 5. Variety in responses - not repetitive
    unique_phrases = set()
    repetition_detected = False
    
    for msg in messages:
        message = msg.get("message", "").lower()
        # Extract 5-word phrases
        words = message.split()
        for i in range(len(words) - 4):
            phrase = " ".join(words[i:i+5])
            if phrase in unique_phrases:
                repetition_detected = True
                break
            unique_phrases.add(phrase)
    
    if not repetition_detected:
        quality_score += 1
        print("✅ No significant repetition detected in messages")
    else:
        print("❌ Repetition detected in messages")
    
    # Overall quality assessment
    quality_percentage = (quality_score / max_quality_score) * 100
    
    print(f"\nOverall Quality Score: {quality_score}/{max_quality_score} ({quality_percentage:.1f}%)")
    
    if quality_percentage >= 80:
        print("✅ EXCELLENT: Conversation quality indicates successful Gemini API integration")
    elif quality_percentage >= 60:
        print("✅ GOOD: Conversation quality suggests Gemini API is working properly")
    elif quality_percentage >= 40:
        print("⚠️ FAIR: Conversation quality is acceptable but could be improved")
    else:
        print("❌ POOR: Conversation quality suggests issues with Gemini API integration")
    
    # Step 8: Test observer message integration
    print("\nStep 8: Testing observer message integration")
    
    observer_data = {
        "observer_message": "Please focus your discussion on the ethical implications of quantum computing in cryptography."
    }
    
    observer_response = requests.post(f"{API_URL}/observer/send-message", json=observer_data, headers=headers)
    
    if observer_response.status_code != 200:
        print(f"❌ Failed to send observer message with status code {observer_response.status_code}")
        print(f"Response: {observer_response.text}")
    else:
        print("✅ Observer message sent successfully")
        
        # Generate another conversation to see if it incorporates the observer message
        print("\nGenerating conversation after observer message...")
        
        post_observer_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        
        if post_observer_response.status_code != 200:
            print(f"❌ Failed to generate conversation after observer message with status code {post_observer_response.status_code}")
            print(f"Response: {post_observer_response.text}")
        else:
            post_observer_data = post_observer_response.json()
            post_observer_messages = post_observer_data.get("messages", [])
            
            print(f"✅ Generated conversation with {len(post_observer_messages)} messages after observer input")
            
            # Check if the conversation incorporates the observer's directive
            ethics_keywords = ["ethic", "moral", "privacy", "security", "responsibility", "implication"]
            ethics_mentions = 0
            
            for msg in post_observer_messages:
                message = msg.get("message", "").lower()
                for keyword in ethics_keywords:
                    if keyword in message:
                        ethics_mentions += 1
                        break
            
            if ethics_mentions >= 2:
                print(f"✅ Conversation incorporates observer's directive about ethics ({ethics_mentions} mentions)")
            else:
                print(f"⚠️ Conversation may not fully incorporate observer's directive ({ethics_mentions} mentions)")
    
    # Step 9: Check for rate limiting or quota issues
    print("\nStep 9: Checking for rate limiting or quota issues")
    
    # Generate multiple conversations in quick succession to check for rate limiting
    success_count = 0
    failure_count = 0
    response_times = []
    
    for i in range(3):
        print(f"\nGenerating conversation {i+1}/3...")
        
        start_time = time.time()
        rate_test_response = requests.post(f"{API_URL}/conversation/generate", headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
        
        if rate_test_response.status_code == 200:
            print(f"✅ Conversation generated successfully in {response_time:.2f} seconds")
            success_count += 1
        else:
            print(f"❌ Failed to generate conversation with status code {rate_test_response.status_code}")
            print(f"Response: {rate_test_response.text}")
            failure_count += 1
    
    if success_count == 3:
        print("\n✅ No rate limiting issues detected - all requests succeeded")
    else:
        print(f"\n⚠️ Possible rate limiting issues - {failure_count}/3 requests failed")
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        print(f"Average response time: {avg_response_time:.2f} seconds")
        
        if avg_response_time < 5.0:
            print("✅ Response times are good (< 5 seconds)")
        else:
            print("⚠️ Response times are slow (>= 5 seconds)")
    
    # Final summary
    print("\n" + "="*80)
    print("GEMINI API INTEGRATION TEST SUMMARY")
    print("="*80)
    
    if quality_score >= 3 and success_count >= 2:
        print("✅ PASSED: Gemini API integration is working properly")
        print(f"✅ Quality Score: {quality_score}/{max_quality_score} ({quality_percentage:.1f}%)")
        print(f"✅ Success Rate: {success_count}/3 ({success_count/3*100:.1f}%)")
        return True, {
            "quality_score": quality_score,
            "quality_percentage": quality_percentage,
            "success_rate": success_count/3,
            "avg_response_time": avg_response_time if response_times else None
        }
    else:
        print("❌ FAILED: Issues detected with Gemini API integration")
        print(f"❌ Quality Score: {quality_score}/{max_quality_score} ({quality_percentage:.1f}%)")
        print(f"❌ Success Rate: {success_count}/3 ({success_count/3*100:.1f}%)")
        return False, {
            "quality_score": quality_score,
            "quality_percentage": quality_percentage,
            "success_rate": success_count/3,
            "avg_response_time": avg_response_time if response_times else None
        }

if __name__ == "__main__":
    success, results = test_gemini_integration()
    sys.exit(0 if success else 1)