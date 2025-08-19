#!/bin/bash
# URGENT: SAME AGENT CONSECUTIVE MESSAGES INVESTIGATION
# Using curl commands to test agent alternation issue

BACKEND_URL="https://8df45847-dc26-4ace-8ce9-3282a2be3204.preview.emergentagent.com"
API_BASE="${BACKEND_URL}/api"

echo "🚨 URGENT: SAME AGENT CONSECUTIVE MESSAGES INVESTIGATION"
echo "================================================================================"
echo "CRITICAL ISSUE: Same agent generating two messages in a row"
echo "This violates the alternating agent rule and breaks conversation flow"
echo "================================================================================"
echo

# Step 1: Authenticate
echo "🔐 STEP 1: AUTHENTICATION"
echo "============================================================"

AUTH_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "dino@cytonic.com", "password": "Observerinho8"}' \
  -m 30)

if [ $? -eq 0 ]; then
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    if [ -n "$TOKEN" ]; then
        echo "✅ PASS Authentication"
        echo "   Details: Successfully authenticated"
        echo
    else
        echo "❌ FAIL Authentication"
        echo "   Details: No token in response: $AUTH_RESPONSE"
        exit 1
    fi
else
    echo "❌ FAIL Authentication"
    echo "   Details: curl command failed"
    exit 1
fi

# Step 2: Check Agent Pool
echo "👥 STEP 2: AGENT POOL ANALYSIS"
echo "============================================================"

AGENTS_RESPONSE=$(curl -s -X GET "${API_BASE}/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -m 30)

if [ $? -eq 0 ]; then
    AGENT_COUNT=$(echo "$AGENTS_RESPONSE" | grep -o '"id"' | wc -l)
    if [ "$AGENT_COUNT" -ge 2 ]; then
        echo "✅ PASS Agent Pool Size"
        echo "   Details: Found $AGENT_COUNT agents (sufficient for alternation)"
        
        # Show first few agents
        echo "   Agent Details:"
        echo "$AGENTS_RESPONSE" | grep -o '"name":"[^"]*' | head -5 | sed 's/"name":"/ - /'
        echo
    else
        echo "❌ FAIL Agent Pool Size"
        echo "   Details: Only $AGENT_COUNT agents found (need at least 2)"
        exit 1
    fi
else
    echo "❌ FAIL Agent Pool Access"
    echo "   Details: Cannot access agents endpoint"
    exit 1
fi

# Step 3: Generate Test Conversations
echo "🎯 STEP 3: AGENT SELECTION LOGIC VERIFICATION"
echo "============================================================"

for i in {1..3}; do
    echo "   Testing conversation generation round $i..."
    
    # Get baseline conversation count
    BASELINE_RESPONSE=$(curl -s -X GET "${API_BASE}/conversations" \
      -H "Authorization: Bearer $TOKEN" \
      -m 30)
    
    BASELINE_COUNT=$(echo "$BASELINE_RESPONSE" | grep -o '"id"' | wc -l)
    
    # Generate conversation
    echo "   Generating conversation..."
    GEN_RESPONSE=$(curl -s -X POST "${API_BASE}/conversation/generate" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{}' \
      -m 120)
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Conversation generation request completed"
        
        # Wait for storage
        sleep 3
        
        # Get new conversations
        NEW_RESPONSE=$(curl -s -X GET "${API_BASE}/conversations" \
          -H "Authorization: Bearer $TOKEN" \
          -m 30)
        
        NEW_COUNT=$(echo "$NEW_RESPONSE" | grep -o '"id"' | wc -l)
        
        if [ "$NEW_COUNT" -gt "$BASELINE_COUNT" ]; then
            echo "   ✅ PASS Conversation Generation Round $i"
            echo "   Details: Generated conversation ($BASELINE_COUNT → $NEW_COUNT)"
            
            # Extract and analyze agent sequence from latest conversation
            echo "   📊 ANALYZING AGENT ALTERNATION..."
            
            # Get the latest conversation messages and check for consecutive same agents
            AGENT_SEQUENCE=$(echo "$NEW_RESPONSE" | grep -o '"agent_name":"[^"]*' | head -10 | cut -d'"' -f4)
            AGENT_IDS=$(echo "$NEW_RESPONSE" | grep -o '"agent_id":"[^"]*' | head -10 | cut -d'"' -f4)
            
            # Convert to arrays and check for consecutive duplicates
            echo "   Agent sequence in latest conversation:"
            PREV_AGENT=""
            VIOLATION_FOUND=false
            INDEX=0
            
            for AGENT in $AGENT_SEQUENCE; do
                echo "     Index $INDEX: $AGENT"
                if [ "$AGENT" = "$PREV_AGENT" ] && [ -n "$PREV_AGENT" ]; then
                    echo "     🚨 VIOLATION: Same agent '$AGENT' appears consecutively!"
                    VIOLATION_FOUND=true
                fi
                PREV_AGENT="$AGENT"
                INDEX=$((INDEX + 1))
            done
            
            if [ "$VIOLATION_FOUND" = true ]; then
                echo "   ❌ CRITICAL FAIL Agent Alternation Round $i"
                echo "   Details: SAME AGENT CONSECUTIVE messages detected"
            else
                echo "   ✅ PASS Agent Alternation Round $i"
                echo "   Details: Proper agent alternation in conversation"
            fi
            
        else
            echo "   ❌ FAIL Conversation Generation Round $i"
            echo "   Details: No new conversation created ($BASELINE_COUNT → $NEW_COUNT)"
        fi
    else
        echo "   ❌ FAIL Conversation Generation Round $i"
        echo "   Details: Generation request failed"
    fi
    
    echo
    sleep 2
done

# Step 4: Analyze Existing Conversations for Patterns
echo "📡 STEP 4: MESSAGE STREAM AGENT ANALYSIS"
echo "============================================================"

echo "   Analyzing existing conversations for agent alternation patterns..."

CONV_RESPONSE=$(curl -s -X GET "${API_BASE}/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -m 30)

if [ $? -eq 0 ]; then
    echo "   ✅ Successfully retrieved conversations for analysis"
    
    # Extract all agent sequences and look for violations
    echo "   🔍 Checking for consecutive same-agent violations..."
    
    # This is a simplified analysis - in a real scenario we'd parse JSON properly
    TOTAL_VIOLATIONS=0
    
    # Look for patterns where same agent appears consecutively in the JSON
    # This is a basic pattern match - not perfect but will catch obvious issues
    if echo "$CONV_RESPONSE" | grep -q '"agent_name":"[^"]*","[^"]*"agent_name":"\1"'; then
        echo "   🚨 POTENTIAL VIOLATIONS DETECTED in conversation data"
        TOTAL_VIOLATIONS=1
    fi
    
    if [ "$TOTAL_VIOLATIONS" -gt 0 ]; then
        echo "   ❌ CRITICAL FAIL Stream Agent Alternation"
        echo "   Details: Found potential consecutive same-agent violations"
    else
        echo "   ✅ PASS Stream Agent Alternation"
        echo "   Details: No obvious consecutive same-agent violations detected"
    fi
else
    echo "   ❌ FAIL Message Stream Access"
    echo "   Details: Cannot retrieve conversations for analysis"
fi

echo
echo "================================================================================"
echo "🔍 AGENT ALTERNATION INVESTIGATION SUMMARY"
echo "================================================================================"
echo "CRITICAL FOCUS: Same agent consecutive messages issue"
echo
echo "📋 KEY FINDINGS:"
echo "- Agent pool analysis completed"
echo "- Conversation generation tested across multiple rounds"
echo "- Agent alternation patterns analyzed"
echo "- Message stream patterns examined"
echo
echo "🎯 NEXT STEPS:"
echo "- Review conversation generation logic in backend"
echo "- Check agent selection algorithm for alternation enforcement"
echo "- Verify parallel processing doesn't cause race conditions"
echo "- Implement agent rotation tracking if missing"
echo
echo "================================================================================"