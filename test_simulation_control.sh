#!/bin/bash

# Set the API URL
API_URL="http://localhost:8001/api"
echo "Using API URL: $API_URL"

# Function to print section header
print_header() {
    echo ""
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    echo ""
}

# Test 1: Get a test login token
print_header "TEST 1: Get a test login token"
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/test-login")
echo "Response: $TOKEN_RESPONSE"

# Extract the token
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
    echo "❌ Failed to get token"
    exit 1
else
    echo "✅ Successfully got token"
fi

# Test 2: Get initial simulation state
print_header "TEST 2: Get initial simulation state"
STATE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/state")
echo "Response: $STATE_RESPONSE"

# Extract is_active
IS_ACTIVE=$(echo $STATE_RESPONSE | jq -r '.is_active')
echo "is_active: $IS_ACTIVE"

# Test 3: Start simulation
print_header "TEST 3: Start simulation"
START_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"time_limit_hours": 2, "time_limit_display": "2 hours"}' "$API_URL/simulation/start")
echo "Response: $START_RESPONSE"

# Check if start was successful
START_SUCCESS=$(echo $START_RESPONSE | jq -r '.success')
if [ "$START_SUCCESS" == "true" ]; then
    echo "✅ Successfully started simulation"
else
    echo "❌ Failed to start simulation"
fi

# Test 4: Get simulation state after starting
print_header "TEST 4: Get simulation state after starting"
STATE_AFTER_START=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/state")
echo "Response: $STATE_AFTER_START"

# Extract is_active
IS_ACTIVE_AFTER_START=$(echo $STATE_AFTER_START | jq -r '.is_active')
echo "is_active after start: $IS_ACTIVE_AFTER_START"

if [ "$IS_ACTIVE_AFTER_START" == "true" ]; then
    echo "✅ Simulation is active after starting"
else
    echo "❌ Simulation is not active after starting"
fi

# Test 5: Pause simulation
print_header "TEST 5: Pause simulation"
PAUSE_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/pause")
echo "Response: $PAUSE_RESPONSE"

# Check if pause was successful
PAUSE_SUCCESS=$(echo $PAUSE_RESPONSE | jq -r '.success')
if [ "$PAUSE_SUCCESS" == "true" ]; then
    echo "✅ Successfully paused simulation"
else
    echo "❌ Failed to pause simulation"
fi

# Test 6: Get simulation state after pausing
print_header "TEST 6: Get simulation state after pausing"
STATE_AFTER_PAUSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/state")
echo "Response: $STATE_AFTER_PAUSE"

# Extract is_active
IS_ACTIVE_AFTER_PAUSE=$(echo $STATE_AFTER_PAUSE | jq -r '.is_active')
echo "is_active after pause: $IS_ACTIVE_AFTER_PAUSE"

if [ "$IS_ACTIVE_AFTER_PAUSE" == "false" ]; then
    echo "✅ Simulation is not active after pausing"
else
    echo "❌ Simulation is still active after pausing"
fi

# Test 7: Resume simulation
print_header "TEST 7: Resume simulation"
RESUME_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/resume")
echo "Response: $RESUME_RESPONSE"

# Check if resume was successful
RESUME_SUCCESS=$(echo $RESUME_RESPONSE | jq -r '.success')
if [ "$RESUME_SUCCESS" == "true" ]; then
    echo "✅ Successfully resumed simulation"
else
    echo "❌ Failed to resume simulation"
fi

# Test 8: Get simulation state after resuming
print_header "TEST 8: Get simulation state after resuming"
STATE_AFTER_RESUME=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/state")
echo "Response: $STATE_AFTER_RESUME"

# Extract is_active
IS_ACTIVE_AFTER_RESUME=$(echo $STATE_AFTER_RESUME | jq -r '.is_active')
echo "is_active after resume: $IS_ACTIVE_AFTER_RESUME"

if [ "$IS_ACTIVE_AFTER_RESUME" == "true" ]; then
    echo "✅ Simulation is active after resuming"
else
    echo "❌ Simulation is not active after resuming"
fi

# Test 9: Fast-forward simulation
print_header "TEST 9: Fast-forward simulation"
FAST_FORWARD_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"target_days": 1, "conversations_per_period": 1}' "$API_URL/simulation/fast-forward")
echo "Response: $FAST_FORWARD_RESPONSE"

# Check if fast-forward was successful or if it failed due to expected reasons
if echo $FAST_FORWARD_RESPONSE | jq -e '.message' > /dev/null 2>&1; then
    echo "✅ Successfully fast-forwarded simulation"
elif echo $FAST_FORWARD_RESPONSE | jq -e '.detail' > /dev/null 2>&1; then
    DETAIL=$(echo $FAST_FORWARD_RESPONSE | jq -r '.detail')
    if [[ $DETAIL == *"Need at least 2 agents"* ]]; then
        echo "ℹ️ Fast-forward failed because there are not enough agents (expected in test environment)"
    elif [[ $DETAIL == *"Not enough API requests"* ]]; then
        echo "ℹ️ Fast-forward failed because of API request limits (expected in test environment)"
    else
        echo "❌ Fast-forward failed with unexpected error: $DETAIL"
    fi
else
    echo "❌ Fast-forward failed with unknown error"
fi

# Test 10: Test authentication requirements
print_header "TEST 10: Test authentication requirements"

# Test start without auth
START_NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"time_limit_hours": 2, "time_limit_display": "2 hours"}' "$API_URL/simulation/start")
if [ "$START_NO_AUTH" == "403" ]; then
    echo "✅ Start simulation correctly requires authentication"
else
    echo "❌ Start simulation does not properly enforce authentication (got $START_NO_AUTH)"
fi

# Test pause without auth
PAUSE_NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/simulation/pause")
if [ "$PAUSE_NO_AUTH" == "403" ]; then
    echo "✅ Pause simulation correctly requires authentication"
else
    echo "❌ Pause simulation does not properly enforce authentication (got $PAUSE_NO_AUTH)"
fi

# Test resume without auth
RESUME_NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/simulation/resume")
if [ "$RESUME_NO_AUTH" == "403" ]; then
    echo "✅ Resume simulation correctly requires authentication"
else
    echo "❌ Resume simulation does not properly enforce authentication (got $RESUME_NO_AUTH)"
fi

# Test get state without auth
STATE_NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/simulation/state")
if [ "$STATE_NO_AUTH" == "403" ]; then
    echo "✅ Get simulation state correctly requires authentication"
else
    echo "❌ Get simulation state does not properly enforce authentication (got $STATE_NO_AUTH)"
fi

# Print summary
print_header "SUMMARY"

# Check if all critical tests passed
if [ "$START_SUCCESS" == "true" ] && [ "$PAUSE_SUCCESS" == "true" ] && [ "$RESUME_SUCCESS" == "true" ] && 
   [ "$IS_ACTIVE_AFTER_START" == "true" ] && [ "$IS_ACTIVE_AFTER_PAUSE" == "false" ] && [ "$IS_ACTIVE_AFTER_RESUME" == "true" ] &&
   [ "$START_NO_AUTH" == "403" ] && [ "$PAUSE_NO_AUTH" == "403" ] && [ "$RESUME_NO_AUTH" == "403" ] && [ "$STATE_NO_AUTH" == "403" ]; then
    echo "✅ Simulation control flow is working correctly!"
    echo "✅ Start simulation is functioning properly"
    echo "✅ Pause simulation is functioning properly"
    echo "✅ Resume simulation is functioning properly"
    echo "✅ Get simulation state is functioning properly"
    echo "✅ Authentication is properly enforced for all endpoints"
else
    echo "❌ Simulation control flow has issues:"
    
    if [ "$START_SUCCESS" != "true" ]; then
        echo "  - Start simulation is not functioning properly"
    fi
    
    if [ "$PAUSE_SUCCESS" != "true" ]; then
        echo "  - Pause simulation is not functioning properly"
    fi
    
    if [ "$RESUME_SUCCESS" != "true" ]; then
        echo "  - Resume simulation is not functioning properly"
    fi
    
    if [ "$IS_ACTIVE_AFTER_START" != "true" ]; then
        echo "  - Simulation is not active after starting"
    fi
    
    if [ "$IS_ACTIVE_AFTER_PAUSE" != "false" ]; then
        echo "  - Simulation is still active after pausing"
    fi
    
    if [ "$IS_ACTIVE_AFTER_RESUME" != "true" ]; then
        echo "  - Simulation is not active after resuming"
    fi
    
    if [ "$START_NO_AUTH" != "403" ] || [ "$PAUSE_NO_AUTH" != "403" ] || [ "$RESUME_NO_AUTH" != "403" ] || [ "$STATE_NO_AUTH" != "403" ]; then
        echo "  - Authentication is not properly enforced for all endpoints"
    fi
fi