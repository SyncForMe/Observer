#!/bin/bash

# 🧪 Final Validation Script
# Comprehensive test of the complete application

echo "🧪 AI Agent Simulation Observatory - Final Validation"
echo "===================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="http://localhost:8001/api"
FRONTEND_URL="http://localhost:3000"

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Test backend health
test_backend_health() {
    print_test "Testing backend health..."
    
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        print_pass "Backend is responding"
    else
        print_fail "Backend not responding at $API_URL"
        return 1
    fi
}

# Test authentication
test_authentication() {
    print_test "Testing authentication..."
    
    TOKEN=$(curl -s -X POST "$API_URL/auth/test-login" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$TOKEN" ]; then
        print_pass "Authentication successful"
        echo "$TOKEN" > /tmp/test_token
        return 0
    else
        print_fail "Authentication failed"
        return 1
    fi
}

# Test agent management
test_agent_management() {
    print_test "Testing agent management..."
    
    TOKEN=$(cat /tmp/test_token 2>/dev/null)
    if [ -z "$TOKEN" ]; then
        print_fail "No authentication token available"
        return 1
    fi
    
    # Create test agent
    AGENT_RESPONSE=$(curl -s -X POST "$API_URL/agents" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Agent",
            "archetype": "scientist",
            "goal": "Test scientific collaboration",
            "expertise": "Testing and validation",
            "background": "Created for system testing"
        }')
    
    AGENT_ID=$(echo "$AGENT_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$AGENT_ID" ]; then
        print_pass "Agent created successfully (ID: ${AGENT_ID:0:8}...)"
        echo "$AGENT_ID" > /tmp/test_agent_id
        
        # Test agent retrieval
        if curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/agents" | grep -q "$AGENT_ID"; then
            print_pass "Agent retrieval working"
        else
            print_fail "Agent retrieval failed"
        fi
        
        return 0
    else
        print_fail "Agent creation failed"
        return 1
    fi
}

# Test simulation control
test_simulation_control() {
    print_test "Testing simulation control..."
    
    TOKEN=$(cat /tmp/test_token 2>/dev/null)
    if [ -z "$TOKEN" ]; then
        print_fail "No authentication token available"
        return 1
    fi
    
    # Start simulation
    START_RESPONSE=$(curl -s -X POST "$API_URL/simulation/start" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$START_RESPONSE" | grep -q "success"; then
        print_pass "Simulation start successful"
        
        # Check simulation state
        if curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/simulation/state" | grep -q "is_active"; then
            print_pass "Simulation state retrieval working"
        else
            print_fail "Simulation state retrieval failed"
        fi
        
        return 0
    else
        print_fail "Simulation start failed"
        return 1
    fi
}

# Test conversation generation
test_conversation_generation() {
    print_test "Testing conversation generation..."
    
    TOKEN=$(cat /tmp/test_token 2>/dev/null)
    AGENT_ID=$(cat /tmp/test_agent_id 2>/dev/null)
    
    if [ -z "$TOKEN" ] || [ -z "$AGENT_ID" ]; then
        print_fail "Missing prerequisites for conversation test"
        return 1
    fi
    
    # Create second agent for conversation
    AGENT2_RESPONSE=$(curl -s -X POST "$API_URL/agents" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Agent 2",
            "archetype": "analyst",
            "goal": "Analyze and provide insights",
            "expertise": "Data analysis",
            "background": "Second agent for testing conversations"
        }')
    
    AGENT2_ID=$(echo "$AGENT2_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$AGENT2_ID" ]; then
        print_pass "Second agent created"
        
        # Generate conversation
        CONV_RESPONSE=$(curl -s -X POST "$API_URL/conversation/generate" \
            -H "Authorization: Bearer $TOKEN")
        
        if echo "$CONV_RESPONSE" | grep -q "conversation"; then
            print_pass "Conversation generation successful"
            return 0
        else
            print_fail "Conversation generation failed"
            return 1
        fi
    else
        print_fail "Failed to create second agent"
        return 1
    fi
}

# Test frontend accessibility
test_frontend() {
    print_test "Testing frontend accessibility..."
    
    if curl -s "$FRONTEND_URL" | grep -q "AI Agent"; then
        print_pass "Frontend is accessible"
        return 0
    else
        print_fail "Frontend not accessible at $FRONTEND_URL"
        return 1
    fi
}

# Cleanup test data
cleanup_test_data() {
    print_test "Cleaning up test data..."
    
    TOKEN=$(cat /tmp/test_token 2>/dev/null)
    if [ -z "$TOKEN" ]; then
        print_info "No token available for cleanup"
        return 0
    fi
    
    # Get all agents and delete test agents
    AGENTS=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/agents")
    
    # Extract agent IDs and delete test agents
    echo "$AGENTS" | grep -o '"id":"[^"]*' | cut -d'"' -f4 | while read -r agent_id; do
        if [ -n "$agent_id" ]; then
            curl -s -X DELETE "$API_URL/agents/$agent_id" \
                -H "Authorization: Bearer $TOKEN" > /dev/null
        fi
    done
    
    print_pass "Test data cleaned up"
    
    # Remove temporary files
    rm -f /tmp/test_token /tmp/test_agent_id
}

# Display test results
show_results() {
    echo ""
    echo "📊 Validation Results"
    echo "===================="
    
    if [ $TOTAL_TESTS -eq $PASSED_TESTS ]; then
        print_pass "✅ All tests passed ($PASSED_TESTS/$TOTAL_TESTS)"
        print_info "🚀 Application is ready for production use!"
    else
        FAILED_TESTS=$((TOTAL_TESTS - PASSED_TESTS))
        print_fail "❌ $FAILED_TESTS out of $TOTAL_TESTS tests failed"
        print_info "Please check the failed tests and fix issues before deployment"
    fi
    
    echo ""
    print_info "Next steps:"
    echo "  1. If all tests pass, your application is ready!"
    echo "  2. Push to GitHub repository"
    echo "  3. Set up production environment with API keys"
    echo "  4. Deploy using provided Docker/Kubernetes configs"
}

# Main test execution
main() {
    print_info "Starting comprehensive validation..."
    print_info "This will test all major application components"
    echo ""
    
    TOTAL_TESTS=0
    PASSED_TESTS=0
    
    # Check if services are running
    print_info "Checking if services are running..."
    if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
        print_fail "Backend not running. Please start with: ./setup.sh start"
        exit 1
    fi
    
    if ! curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
        print_fail "Frontend not running. Please start with: ./setup.sh start"
        exit 1
    fi
    
    # Run all tests
    tests=(
        "test_backend_health"
        "test_authentication"
        "test_agent_management"
        "test_simulation_control"
        "test_conversation_generation"
        "test_frontend"
    )
    
    for test in "${tests[@]}"; do
        ((TOTAL_TESTS++))
        if $test; then
            ((PASSED_TESTS++))
        fi
        echo ""
    done
    
    # Cleanup
    cleanup_test_data
    
    # Show results
    show_results
    
    # Exit with appropriate code
    if [ $TOTAL_TESTS -eq $PASSED_TESTS ]; then
        exit 0
    else
        exit 1
    fi
}

# Handle different modes
case "$1" in
    "quick")
        test_backend_health && test_frontend
        ;;
    "auth")
        test_authentication
        ;;
    "agents")
        test_authentication && test_agent_management
        ;;
    "conv")
        test_authentication && test_agent_management && test_conversation_generation
        ;;
    "cleanup")
        cleanup_test_data
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [quick|auth|agents|conv|cleanup]"
        echo ""
        echo "Modes:"
        echo "  (none)  - Run all tests (default)"
        echo "  quick   - Quick health check"
        echo "  auth    - Test authentication only"
        echo "  agents  - Test agent management"
        echo "  conv    - Test conversation generation"
        echo "  cleanup - Clean test data"
        exit 1
        ;;
esac