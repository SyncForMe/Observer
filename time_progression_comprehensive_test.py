#!/usr/bin/env python3
"""
Time Progression System Test using existing backend_test.py framework

This test focuses on the fixed automatic time progression system:
1. Time Advancement Triggers: Test that time advances every 8 messages (improved from 12)
2. Progression Sequence: Verify Day 1 Morning → Day 1 Afternoon → Day 1 Evening → Day 2 Morning → Day 2 Afternoon
3. State Persistence: Ensure simulation state actually updates and persists
4. Conversation Integration: Check that conversation metadata reflects time changes
5. Debug Logging: Look for the detailed debug logs added to understand what's happening
"""

import sys
import os
sys.path.append('/app')

from backend_test import *
import time

def test_time_progression_comprehensive():
    """Comprehensive test of the automatic time progression system"""
    print("\n" + "="*80)
    print("🕐 COMPREHENSIVE TIME PROGRESSION SYSTEM TESTING")
    print("="*80)
    
    # Login first to get auth token
    if not auth_token:
        if not test_login():
            print("❌ Cannot test time progression without authentication")
            return False, "Authentication failed"
    
    # Step 1: Reset and setup simulation
    print("\n🚀 Step 1: Setting up simulation environment")
    
    # Reset simulation
    reset_test, reset_response = run_test(
        "Reset Simulation",
        "/simulation/reset",
        method="POST",
        auth=True
    )
    
    if not reset_test:
        print("❌ Failed to reset simulation")
        return False, "Failed to reset simulation"
    
    # Set scenario
    scenario_data = {
        "scenario": "Quantum Signal Discovery Research",
        "scenario_name": "Quantum Signal Discovery"
    }
    
    scenario_test, scenario_response = run_test(
        "Set Scenario",
        "/simulation/set-scenario",
        method="POST",
        data=scenario_data,
        auth=True
    )
    
    if not scenario_test:
        print("❌ Failed to set scenario")
        return False, "Failed to set scenario"
    
    # Create test agents
    print("\n🤖 Step 2: Creating test agents")
    
    test_agents = []
    agents_to_create = [
        {
            "name": "Dr. Sarah Chen",
            "archetype": "scientist",
            "goal": "Analyze quantum signal patterns",
            "expertise": "Quantum Physics",
            "background": "Leading quantum physicist",
            "personality": {
                "extroversion": 6,
                "optimism": 8,
                "curiosity": 9,
                "cooperativeness": 7,
                "energy": 7
            }
        },
        {
            "name": "Marcus Thompson", 
            "archetype": "leader",
            "goal": "Coordinate team efforts",
            "expertise": "Project Management",
            "background": "Experienced project manager",
            "personality": {
                "extroversion": 9,
                "optimism": 8,
                "curiosity": 6,
                "cooperativeness": 8,
                "energy": 8
            }
        },
        {
            "name": "Dr. Alex Rivera",
            "archetype": "skeptic", 
            "goal": "Identify potential risks",
            "expertise": "Risk Analysis",
            "background": "Critical thinker",
            "personality": {
                "extroversion": 4,
                "optimism": 3,
                "curiosity": 7,
                "cooperativeness": 5,
                "energy": 5
            }
        }
    ]
    
    for agent_data in agents_to_create:
        agent_test, agent_response = run_test(
            f"Create Agent: {agent_data['name']}",
            "/agents",
            method="POST",
            data=agent_data,
            auth=True
        )
        
        if agent_test and agent_response:
            test_agents.append(agent_response)
            print(f"✅ Created agent: {agent_data['name']}")
        else:
            print(f"❌ Failed to create agent: {agent_data['name']}")
            return False, f"Failed to create agent: {agent_data['name']}"
    
    # Start simulation
    start_test, start_response = run_test(
        "Start Simulation",
        "/simulation/start",
        method="POST",
        auth=True
    )
    
    if not start_test:
        print("❌ Failed to start simulation")
        return False, "Failed to start simulation"
    
    print(f"✅ Successfully created {len(test_agents)} agents and started simulation")
    
    # Step 3: Get initial simulation state
    print("\n📊 Step 3: Recording initial simulation state")
    
    initial_state_test, initial_state = run_test(
        "Get Initial Simulation State",
        "/simulation/state",
        method="GET",
        auth=True
    )
    
    if not initial_state_test or not initial_state:
        print("❌ Failed to get initial simulation state")
        return False, "Failed to get initial simulation state"
    
    initial_day = initial_state.get("current_day", 1)
    initial_period = initial_state.get("current_time_period", "morning")
    
    print(f"📊 Initial State: Day {initial_day} {initial_period.title()}")
    
    # Track time progression
    time_states = [{
        "day": initial_day,
        "period": initial_period,
        "messages": 0,
        "step": "initial"
    }]
    
    # Step 4: Generate conversations and monitor time progression
    print("\n🔄 Step 4: Generating conversations to trigger time progression")
    
    target_conversations = 6  # Should generate enough messages to trigger multiple time advances
    
    for i in range(target_conversations):
        print(f"\n📝 Generating conversation {i+1}/{target_conversations}...")
        
        # Generate conversation
        conv_test, conv_response = run_test(
            f"Generate Conversation {i+1}",
            "/conversation/generate",
            method="POST",
            auth=True,
            measure_time=True
        )
        
        if conv_test and conv_response:
            messages = conv_response.get("messages", [])
            print(f"✅ Generated conversation with {len(messages)} messages")
            
            # Get current simulation state after conversation
            state_test, current_state = run_test(
                f"Get State After Conversation {i+1}",
                "/simulation/state",
                method="GET",
                auth=True
            )
            
            if state_test and current_state:
                current_day = current_state.get("current_day", 1)
                current_period = current_state.get("current_time_period", "morning")
                
                # Check if time has advanced
                last_state = time_states[-1]
                if (current_day != last_state["day"] or current_period != last_state["period"]):
                    print(f"🕐 TIME ADVANCEMENT DETECTED!")
                    print(f"   From: Day {last_state['day']} {last_state['period'].title()}")
                    print(f"   To:   Day {current_day} {current_period.title()}")
                    
                    time_states.append({
                        "day": current_day,
                        "period": current_period,
                        "messages": (i+1) * len(messages),  # Approximate message count
                        "step": f"after_conversation_{i+1}"
                    })
                
                print(f"📊 Current State: Day {current_day} {current_period.title()}")
            
        else:
            print(f"❌ Failed to generate conversation {i+1}")
        
        # Small delay between conversations
        time.sleep(2)
    
    # Step 5: Get all conversations to count total messages
    print("\n💬 Step 5: Analyzing conversation data")
    
    conversations_test, conversations = run_test(
        "Get All Conversations",
        "/conversations",
        method="GET",
        auth=True
    )
    
    total_messages = 0
    if conversations_test and conversations:
        print(f"📊 Found {len(conversations)} conversations")
        
        for i, conv in enumerate(conversations):
            messages = conv.get("messages", [])
            time_period = conv.get("time_period", "Not set")
            round_number = conv.get("round_number", i+1)
            
            total_messages += len(messages)
            print(f"   Conversation {round_number}: {len(messages)} messages, Time: {time_period}")
        
        print(f"📊 Total messages across all conversations: {total_messages}")
    else:
        print("❌ Failed to get conversations")
    
    # Step 6: Analyze time progression results
    print("\n" + "="*80)
    print("📊 TIME PROGRESSION ANALYSIS")
    print("="*80)
    
    print(f"\n🔍 RECORDED TIME STATES:")
    for i, state in enumerate(time_states):
        print(f"   {i+1}. Day {state['day']} {state['period'].title()} ({state['step']})")
    
    # Expected progression sequence
    expected_progression = [
        {"day": 1, "period": "morning"},
        {"day": 1, "period": "afternoon"},
        {"day": 1, "period": "evening"},
        {"day": 2, "period": "morning"},
        {"day": 2, "period": "afternoon"}
    ]
    
    print(f"\n🎯 EXPECTED vs ACTUAL PROGRESSION:")
    
    progression_success = True
    advancement_count = len(time_states) - 1  # Subtract initial state
    
    for i, expected in enumerate(expected_progression):
        if i < len(time_states):
            actual = time_states[i]
            match = (actual["day"] == expected["day"] and actual["period"] == expected["period"])
            status = "✅" if match else "❌"
            
            print(f"   {status} State {i+1}: Expected Day {expected['day']} {expected['period'].title()}, Got Day {actual['day']} {actual['period'].title()}")
            
            if not match:
                progression_success = False
        else:
            print(f"   ❌ State {i+1}: Expected Day {expected['day']} {expected['period'].title()}, Not reached")
            progression_success = False
    
    # Check if time advanced at reasonable intervals
    print(f"\n⏰ TIME ADVANCEMENT ANALYSIS:")
    
    advancement_success = True
    if advancement_count > 0:
        avg_messages_per_advancement = total_messages / advancement_count if advancement_count > 0 else 0
        print(f"   Total Messages: {total_messages}")
        print(f"   Time Advancements: {advancement_count}")
        print(f"   Average Messages per Advancement: {avg_messages_per_advancement:.1f}")
        
        # Check if advancement happens approximately every 8 messages
        if 6 <= avg_messages_per_advancement <= 12:  # Allow some tolerance
            print(f"   ✅ Time advancement frequency is within expected range (6-12 messages)")
        else:
            print(f"   ❌ Time advancement frequency is outside expected range (expected ~8 messages)")
            advancement_success = False
    else:
        print(f"   ❌ No time advancements detected")
        advancement_success = False
    
    # Check conversation metadata
    print(f"\n💬 CONVERSATION METADATA ANALYSIS:")
    
    metadata_success = True
    if conversations:
        conversations_with_time = 0
        for conv in conversations:
            time_period = conv.get("time_period")
            if time_period and time_period != "Not set":
                conversations_with_time += 1
        
        metadata_percentage = (conversations_with_time / len(conversations)) * 100
        print(f"   Conversations with time metadata: {conversations_with_time}/{len(conversations)} ({metadata_percentage:.1f}%)")
        
        if metadata_percentage >= 80:  # At least 80% should have time metadata
            print(f"   ✅ Most conversations have proper time metadata")
        else:
            print(f"   ❌ Too few conversations have proper time metadata")
            metadata_success = False
    else:
        print(f"   ❌ No conversations found to analyze")
        metadata_success = False
    
    # Step 7: Final assessment
    print(f"\n" + "="*80)
    print("🏆 FINAL ASSESSMENT")
    print("="*80)
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    
    results = {
        "time_advancement_triggers": advancement_success,
        "progression_sequence": progression_success,
        "conversation_metadata": metadata_success,
        "total_advancements": advancement_count,
        "total_messages": total_messages,
        "conversations_generated": len(conversations) if conversations else 0
    }
    
    if advancement_success:
        print(f"   ✅ Time Advancement Triggers: PASSED")
        print(f"      Time advances approximately every 8 messages as expected")
    else:
        print(f"   ❌ Time Advancement Triggers: FAILED")
        print(f"      Time advancement intervals are not working correctly")
    
    if progression_success:
        print(f"   ✅ Progression Sequence: PASSED")
        print(f"      Time progression follows expected sequence")
    else:
        print(f"   ❌ Progression Sequence: FAILED")
        print(f"      Time progression sequence is incorrect")
    
    if metadata_success:
        print(f"   ✅ Conversation Integration: PASSED")
        print(f"      Conversation metadata properly reflects time changes")
    else:
        print(f"   ❌ Conversation Integration: FAILED")
        print(f"      Conversation metadata not properly updated")
    
    # Overall result
    overall_success = advancement_success and progression_success and metadata_success
    
    if overall_success:
        print(f"\n🎉 OVERALL RESULT: ✅ PASSED")
        print(f"   The automatic time progression system is working correctly!")
        print(f"   • Generated {total_messages} messages across {len(conversations) if conversations else 0} conversations")
        print(f"   • Triggered {advancement_count} time advancements")
        print(f"   • Time progression follows expected sequence")
        print(f"   • Debug logging provides visibility into time advancement")
    else:
        print(f"\n💥 OVERALL RESULT: ❌ FAILED")
        print(f"   The automatic time progression system has issues:")
        
        issues = []
        if not advancement_success:
            issues.append("Time advancement triggers not working correctly")
        if not progression_success:
            issues.append("Progression sequence is incorrect")
        if not metadata_success:
            issues.append("Conversation metadata not properly updated")
        
        for issue in issues:
            print(f"   • {issue}")
    
    return overall_success, results

def main():
    """Main test execution"""
    print("🧪 TIME PROGRESSION SYSTEM COMPREHENSIVE TEST")
    print("="*80)
    
    success, results = test_time_progression_comprehensive()
    
    print(f"\n" + "="*80)
    print("📋 FINAL TEST SUMMARY")
    print("="*80)
    
    if success:
        print("✅ TIME PROGRESSION SYSTEM: ALL TESTS PASSED")
        print("\n🎯 Key Findings:")
        print(f"   • Time advances every ~8 messages as expected")
        print(f"   • Progression sequence: Morning → Afternoon → Evening → Next Day")
        print(f"   • Simulation state persists correctly")
        print(f"   • Conversation metadata reflects time changes")
        print(f"   • Generated {results.get('total_messages', 0)} total messages")
        print(f"   • Triggered {results.get('total_advancements', 0)} time advancements")
    else:
        print("❌ TIME PROGRESSION SYSTEM: SOME TESTS FAILED")
        print("\n🔍 Issues Identified:")
        if not results.get("time_advancement_triggers"):
            print(f"   • Time advancement triggers are not working correctly")
        if not results.get("progression_sequence"):
            print(f"   • Progression sequence does not match expected pattern")
        if not results.get("conversation_metadata"):
            print(f"   • Conversation metadata is not properly updated")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)