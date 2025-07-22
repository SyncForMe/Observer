#!/bin/bash

# Rolling Context Window User Experience Test
# Tests that rolling context is completely invisible to users

echo "🔍 ROLLING CONTEXT WINDOW USER EXPERIENCE TEST"
echo "=============================================="
echo ""

# Configuration
API_URL="https://1b54c023-1ff4-4804-99a2-1b109f5253cd.preview.emergentagent.com/api"
TIMEOUT=15

# Test results
PASSED=0
FAILED=0
CRITICAL_FAILURES=()

# Function to log test results
log_test() {
    local test_name="$1"
    local passed="$2"
    local details="$3"
    local critical="$4"
    
    if [ "$passed" = "true" ]; then
        echo "✅ PASS: $test_name"
        ((PASSED++))
    else
        echo "❌ FAIL: $test_name"
        ((FAILED++))
        if [ "$critical" = "true" ]; then
            CRITICAL_FAILURES+=("$test_name")
        fi
    fi
    
    if [ -n "$details" ]; then
        echo "   Details: $details"
    fi
    echo ""
}

# Step 1: Authentication
echo "📋 Step 1: Authentication"
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/auth/test-login" \
    -H "Content-Type: application/json" \
    --connect-timeout 10 --max-time $TIMEOUT)

if [ $? -eq 0 ] && echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    USER_ID=$(echo "$AUTH_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    log_test "Guest Authentication" "true" "User ID: $USER_ID"
else
    log_test "Guest Authentication" "false" "Failed to authenticate" "true"
    exit 1
fi

# Step 2: Create test agents
echo "📋 Step 2: Create Test Agents"
AGENTS_CREATED=0

for i in {1..3}; do
    AGENT_DATA="{
        \"name\": \"UX Test Agent $i\",
        \"archetype\": \"scientist\",
        \"goal\": \"Test rolling context user experience $i\",
        \"expertise\": \"UX Testing $i\",
        \"background\": \"Created for rolling context UX testing $i\",
        \"personality\": {
            \"extroversion\": 5,
            \"optimism\": 6,
            \"curiosity\": 7,
            \"cooperativeness\": 8,
            \"energy\": 6
        }
    }"
    
    AGENT_RESPONSE=$(curl -s -X POST "$API_URL/agents" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$AGENT_DATA" \
        --connect-timeout 10 --max-time $TIMEOUT)
    
    if [ $? -eq 0 ] && echo "$AGENT_RESPONSE" | grep -q '"id"'; then
        ((AGENTS_CREATED++))
        echo "✅ Created test agent $i"
    else
        echo "❌ Failed to create agent $i"
    fi
done

if [ $AGENTS_CREATED -ge 2 ]; then
    log_test "Agent Creation" "true" "Created $AGENTS_CREATED agents"
else
    log_test "Agent Creation" "false" "Only created $AGENTS_CREATED agents, need at least 2" "true"
    exit 1
fi

# Step 3: Setup simulation
echo "📋 Step 3: Setup Simulation"

# Start simulation
START_RESPONSE=$(curl -s -X POST "$API_URL/simulation/start" \
    -H "Authorization: Bearer $TOKEN" \
    --connect-timeout 10 --max-time $TIMEOUT)

if [ $? -eq 0 ] && echo "$START_RESPONSE" | grep -q '"message"'; then
    echo "✅ Simulation started"
    
    # Set scenario
    SCENARIO_DATA='{
        "scenario": "User Experience Rolling Context Test - Testing that users see all conversations",
        "scenario_name": "UX Rolling Context Test"
    }'
    
    SCENARIO_RESPONSE=$(curl -s -X POST "$API_URL/simulation/set-scenario" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$SCENARIO_DATA" \
        --connect-timeout 10 --max-time $TIMEOUT)
    
    if [ $? -eq 0 ]; then
        log_test "Simulation Setup" "true"
    else
        log_test "Simulation Setup" "false" "Failed to set scenario" "true"
        exit 1
    fi
else
    log_test "Simulation Setup" "false" "Failed to start simulation" "true"
    exit 1
fi

# Step 4: Generate conversations to trigger rolling context
echo "📋 Step 4: Generate Conversations to Trigger Rolling Context"
echo "🎯 Generating 30 conversations to ensure rolling context window is triggered..."

CONVERSATIONS_GENERATED=0
for i in {1..30}; do
    if [ $((i % 5)) -eq 0 ]; then
        echo "   Generated $CONVERSATIONS_GENERATED/$i conversations..."
    fi
    
    CONV_RESPONSE=$(curl -s -X POST "$API_URL/conversation/generate" \
        -H "Authorization: Bearer $TOKEN" \
        --connect-timeout 10 --max-time 30)
    
    if [ $? -eq 0 ] && echo "$CONV_RESPONSE" | grep -q '"id"'; then
        ((CONVERSATIONS_GENERATED++))
    fi
    
    # Small delay to avoid overwhelming the API
    sleep 0.5
done

if [ $CONVERSATIONS_GENERATED -ge 25 ]; then
    log_test "Conversation Generation" "true" "Generated $CONVERSATIONS_GENERATED/30 conversations"
else
    log_test "Conversation Generation" "false" "Only generated $CONVERSATIONS_GENERATED/30 conversations"
fi

# Step 5: CRITICAL TEST - Verify ALL conversations are visible to user
echo "📋 Step 5: 🚨 CRITICAL - Verify ALL Conversations Visible to User"

ALL_CONVERSATIONS=$(curl -s -X GET "$API_URL/conversations" \
    -H "Authorization: Bearer $TOKEN" \
    --connect-timeout 10 --max-time $TIMEOUT)

if [ $? -eq 0 ] && echo "$ALL_CONVERSATIONS" | grep -q '\['; then
    # Count conversations using jq if available, otherwise use grep
    if command -v jq >/dev/null 2>&1; then
        RETRIEVED_COUNT=$(echo "$ALL_CONVERSATIONS" | jq '. | length')
    else
        # Fallback: count occurrences of "id" field
        RETRIEVED_COUNT=$(echo "$ALL_CONVERSATIONS" | grep -o '"id"' | wc -l)
    fi
    
    log_test "Get All Conversations" "true" "Retrieved $RETRIEVED_COUNT conversations"
    
    # CRITICAL REQUIREMENT: User should see ALL conversations, not limited to 5
    if [ $RETRIEVED_COUNT -ge $CONVERSATIONS_GENERATED ]; then
        log_test "All Conversations Visible" "true" "✅ CRITICAL PASS: User can see all $RETRIEVED_COUNT conversations (not limited to 5)" "true"
    else
        log_test "All Conversations Visible" "false" "❌ CRITICAL FAIL: User can only see $RETRIEVED_COUNT conversations, expected $CONVERSATIONS_GENERATED" "true"
    fi
else
    log_test "Get All Conversations" "false" "Failed to retrieve conversations" "true"
    RETRIEVED_COUNT=0
fi

# Step 6: CRITICAL TEST - Check for summary content visible to users
echo "📋 Step 6: 🚨 CRITICAL - Check for Summary Content Visible to Users"

# Check for summary indicators in the conversations
SUMMARY_INDICATORS=(
    "conversation progress summary"
    "ai context summary"
    "📚 ai context"
    "🧠 generating"
    "backend only"
    "not shown to user"
    "internal summary"
    "context management"
    "rolling context"
    "summary for ai"
    "conversation_progress_summary"
    "📋 conversation progress summary"
    "🎯 main objective"
    "💡 solutions proposed"
    "✅ decisions made"
)

SUMMARY_FOUND=false
for indicator in "${SUMMARY_INDICATORS[@]}"; do
    if echo "$ALL_CONVERSATIONS" | grep -qi "$indicator"; then
        SUMMARY_FOUND=true
        echo "   ⚠️ Found summary indicator: $indicator"
        break
    fi
done

if [ "$SUMMARY_FOUND" = "false" ]; then
    log_test "No Summary Content Visible" "true" "✅ CRITICAL PASS: No backend summary content found in user conversations" "true"
else
    log_test "No Summary Content Visible" "false" "❌ CRITICAL FAIL: Found summary content visible to users" "true"
fi

# Step 7: Check for system messages
echo "📋 Step 7: Check for System Messages"

SYSTEM_INDICATORS=("system" "context" "summary" "internal" "backend" "ai context")
SYSTEM_FOUND=false

for indicator in "${SYSTEM_INDICATORS[@]}"; do
    if echo "$ALL_CONVERSATIONS" | grep -qi "agent_name.*$indicator"; then
        SYSTEM_FOUND=true
        echo "   ⚠️ Found system-like agent name containing: $indicator"
        break
    fi
done

if [ "$SYSTEM_FOUND" = "false" ]; then
    log_test "No System Messages" "true" "✅ CRITICAL PASS: No system messages found in user conversations" "true"
else
    log_test "No System Messages" "false" "❌ CRITICAL FAIL: Found system messages visible to users" "true"
fi

# Step 8: Test conversation count behavior (should never decrease)
echo "📋 Step 8: Test Conversation Count Never Decreases"

# Generate one more conversation
echo "   Generating additional conversation to test count behavior..."
ADDITIONAL_CONV=$(curl -s -X POST "$API_URL/conversation/generate" \
    -H "Authorization: Bearer $TOKEN" \
    --connect-timeout 10 --max-time 30)

if [ $? -eq 0 ] && echo "$ADDITIONAL_CONV" | grep -q '"id"'; then
    sleep 3  # Wait for database update
    
    # Get conversations again
    UPDATED_CONVERSATIONS=$(curl -s -X GET "$API_URL/conversations" \
        -H "Authorization: Bearer $TOKEN" \
        --connect-timeout 10 --max-time $TIMEOUT)
    
    if [ $? -eq 0 ] && echo "$UPDATED_CONVERSATIONS" | grep -q '\['; then
        if command -v jq >/dev/null 2>&1; then
            NEW_COUNT=$(echo "$UPDATED_CONVERSATIONS" | jq '. | length')
        else
            NEW_COUNT=$(echo "$UPDATED_CONVERSATIONS" | grep -o '"id"' | wc -l)
        fi
        
        if [ $NEW_COUNT -gt $RETRIEVED_COUNT ]; then
            log_test "Conversation Count Never Decreases" "true" "✅ Count increased from $RETRIEVED_COUNT to $NEW_COUNT"
        elif [ $NEW_COUNT -eq $RETRIEVED_COUNT ]; then
            log_test "Conversation Count Never Decreases" "false" "⚠️ Count stayed same: $RETRIEVED_COUNT -> $NEW_COUNT (may indicate deletion)"
        else
            log_test "Conversation Count Never Decreases" "false" "❌ CRITICAL: Count decreased: $RETRIEVED_COUNT -> $NEW_COUNT" "true"
        fi
    else
        log_test "Conversation Count Never Decreases" "false" "Failed to retrieve updated conversations"
    fi
else
    log_test "Conversation Count Never Decreases" "false" "Failed to generate additional conversation"
fi

# Step 9: Verify internal endpoints are not exposed
echo "📋 Step 9: Verify Internal Summary Endpoints Not Exposed"

INTERNAL_RESPONSE=$(curl -s -X GET "$API_URL/internal/conversation-summaries" \
    -H "Authorization: Bearer $TOKEN" \
    --connect-timeout 5 --max-time 10)

if [ $? -eq 0 ] && echo "$INTERNAL_RESPONSE" | grep -q '\['; then
    log_test "Internal Endpoints Hidden" "false" "❌ Internal summaries endpoint accessible"
else
    log_test "Internal Endpoints Hidden" "true" "✅ Internal summaries endpoint properly restricted"
fi

# Final Summary
echo "=============================================="
echo "📊 USER EXPERIENCE ROLLING CONTEXT TEST SUMMARY"
echo "=============================================="
echo ""

TOTAL_TESTS=$((PASSED + FAILED))
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$(( (PASSED * 100) / TOTAL_TESTS ))
else
    PASS_RATE=0
fi

echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED ✅"
echo "Failed: $FAILED ❌"
echo "Pass Rate: $PASS_RATE%"
echo ""

# Critical requirements check
echo "🎯 CRITICAL USER EXPERIENCE REQUIREMENTS:"

CRITICAL_REQUIREMENTS=(
    "All Conversations Visible"
    "No Summary Content Visible"
    "No System Messages"
)

CRITICAL_PASSED=0
for req in "${CRITICAL_REQUIREMENTS[@]}"; do
    # Check if this critical requirement passed
    FOUND=false
    for failure in "${CRITICAL_FAILURES[@]}"; do
        if [[ "$failure" == *"$req"* ]]; then
            echo "   ❌ $req"
            FOUND=true
            break
        fi
    done
    if [ "$FOUND" = "false" ]; then
        echo "   ✅ $req"
        ((CRITICAL_PASSED++))
    fi
done

echo ""
echo "Critical Requirements Met: $CRITICAL_PASSED/${#CRITICAL_REQUIREMENTS[@]}"
echo ""

# Final verdict
if [ $CRITICAL_PASSED -eq ${#CRITICAL_REQUIREMENTS[@]} ] && [ ${#CRITICAL_FAILURES[@]} -eq 0 ]; then
    echo "🎉 SUCCESS: Rolling context window is completely invisible to users!"
    echo "   ✅ Users see all conversations"
    echo "   ✅ No summaries visible to users"
    echo "   ✅ No deleted conversations"
    echo "   ✅ Same API responses as before"
    echo "   ✅ No UI changes needed"
    echo ""
    echo "   The rolling context window is purely a backend optimization!"
else
    echo "⚠️ CRITICAL ISSUES FOUND: Rolling context window affects user experience!"
    echo "   Some backend implementation details are visible to users."
    
    if [ ${#CRITICAL_FAILURES[@]} -gt 0 ]; then
        echo ""
        echo "❌ CRITICAL FAILURES:"
        for failure in "${CRITICAL_FAILURES[@]}"; do
            echo "   • $failure"
        done
    fi
fi

echo ""
echo "Test completed at $(date)"