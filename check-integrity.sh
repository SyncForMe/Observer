#!/bin/bash

# 🔍 Project Integrity Checker
# Validates all critical files and dependencies for GitHub repository

echo "🔍 AI Agent Simulation Observatory - Integrity Check"
echo "=================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check core backend files
check_backend() {
    print_info "Checking backend files..."
    
    # Critical files
    if [ -f "backend/server.py" ]; then
        FILE_SIZE=$(wc -l < backend/server.py)
        if [ $FILE_SIZE -gt 100 ]; then
            print_success "backend/server.py exists ($FILE_SIZE lines)"
        else
            print_error "backend/server.py is too small ($FILE_SIZE lines)"
        fi
    else
        print_error "backend/server.py missing"
    fi
    
    if [ -f "backend/requirements.txt" ]; then
        DEPS=$(wc -l < backend/requirements.txt)
        print_success "backend/requirements.txt exists ($DEPS dependencies)"
    else
        print_error "backend/requirements.txt missing"
    fi
    
    if [ -f "backend/.env.example" ]; then
        print_success "backend/.env.example exists"
    else
        print_warning "backend/.env.example missing"
    fi
    
    # Check for syntax errors in Python files
    if command -v python3 &> /dev/null; then
        if python3 -m py_compile backend/server.py 2>/dev/null; then
            print_success "backend/server.py syntax valid"
        else
            print_error "backend/server.py has syntax errors"
        fi
    fi
}

# Check core frontend files
check_frontend() {
    print_info "Checking frontend files..."
    
    # Critical files
    FRONTEND_FILES=(
        "src/App.js"
        "src/SimulationControl.js"
        "src/AgentLibraryComplete.js"
        "src/ConversationViewer.js"
        "package.json"
        "tailwind.config.js"
    )
    
    cd frontend
    
    for file in "${FRONTEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            FILE_SIZE=$(wc -l < "$file")
            print_success "frontend/$file exists ($FILE_SIZE lines)"
        else
            print_error "frontend/$file missing"
        fi
    done
    
    # Check package.json structure
    if [ -f "package.json" ]; then
        if command -v node &> /dev/null; then
            if node -e "JSON.parse(require('fs').readFileSync('package.json'))" 2>/dev/null; then
                print_success "package.json is valid JSON"
            else
                print_error "package.json has invalid JSON"
            fi
        fi
    fi
    
    # Check for node_modules
    if [ -d "node_modules" ]; then
        MODULE_COUNT=$(ls node_modules | wc -l)
        print_success "node_modules exists ($MODULE_COUNT packages)"
    else
        print_warning "node_modules missing (run yarn install)"
    fi
    
    cd ..
}

# Check documentation files
check_documentation() {
    print_info "Checking documentation files..."
    
    DOC_FILES=(
        "README.md"
        "API.md"
        "setup.sh"
    )
    
    for file in "${DOC_FILES[@]}"; do
        if [ -f "$file" ]; then
            FILE_SIZE=$(wc -l < "$file")
            if [ $FILE_SIZE -gt 50 ]; then
                print_success "$file exists ($FILE_SIZE lines)"
            else
                print_warning "$file exists but seems incomplete ($FILE_SIZE lines)"
            fi
        else
            print_error "$file missing"
        fi
    done
    
    # Check README structure
    if [ -f "README.md" ]; then
        if grep -q "Quick Start" README.md && grep -q "Installation" README.md; then
            print_success "README.md has proper structure"
        else
            print_warning "README.md missing key sections"
        fi
    fi
}

# Check configuration files
check_configuration() {
    print_info "Checking configuration files..."
    
    # Docker files
    if [ -f "Dockerfile" ]; then
        print_success "Dockerfile exists"
    else
        print_warning "Dockerfile missing"
    fi
    
    if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
        print_success "Docker Compose file exists"
    else
        print_warning "Docker Compose file missing"
    fi
    
    # Kubernetes files
    if [ -d "k8s" ]; then
        K8S_FILES=$(ls k8s/*.yaml 2>/dev/null | wc -l)
        if [ $K8S_FILES -gt 0 ]; then
            print_success "Kubernetes configs exist ($K8S_FILES files)"
        else
            print_warning "k8s directory empty"
        fi
    else
        print_warning "k8s directory missing"
    fi
}

# Check for test files and cleanup
check_cleanup() {
    print_info "Checking for test files and cleanup..."
    
    # Count test files
    TEST_FILES=$(find . -name "*test*.py" -o -name "*test*.js" | grep -v node_modules | wc -l)
    if [ $TEST_FILES -gt 20 ]; then
        print_warning "Many test files found ($TEST_FILES) - consider cleanup for production"
    else
        print_success "Test files manageable ($TEST_FILES found)"
    fi
    
    # Check for large files
    LARGE_FILES=$(find . -size +10M -type f | grep -v node_modules | wc -l)
    if [ $LARGE_FILES -gt 0 ]; then
        print_warning "Large files found ($LARGE_FILES) - check for unnecessary files"
        find . -size +10M -type f | grep -v node_modules | head -5
    else
        print_success "No large files found"
    fi
    
    # Check for sensitive files
    SENSITIVE_PATTERNS=("*.env" "*.key" "*.pem" "*.p12" "*secret*")
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        FOUND=$(find . -name "$pattern" -not -name "*.example" | grep -v node_modules | wc -l)
        if [ $FOUND -gt 0 ]; then
            print_warning "Potential sensitive files found: $pattern ($FOUND files)"
            print_info "Make sure these are in .gitignore"
        fi
    done
}

# Check Git setup
check_git() {
    print_info "Checking Git setup..."
    
    if [ -d ".git" ]; then
        print_success "Git repository initialized"
        
        # Check .gitignore
        if [ -f ".gitignore" ]; then
            if grep -q "node_modules" .gitignore && grep -q "\.env" .gitignore; then
                print_success ".gitignore properly configured"
            else
                print_warning ".gitignore missing important entries"
            fi
        else
            print_error ".gitignore missing"
        fi
        
        # Check for uncommitted changes
        if git diff --quiet && git diff --cached --quiet; then
            print_success "No uncommitted changes"
        else
            print_warning "Uncommitted changes detected"
        fi
        
    else
        print_warning "Not a Git repository"
    fi
}

# Generate integrity report
generate_report() {
    echo ""
    echo "📊 Integrity Check Summary"
    echo "=========================="
    
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        print_success "✅ Repository is ready for GitHub!"
        print_info "All critical files present and valid"
    elif [ $ERRORS -eq 0 ]; then
        print_warning "⚠️  Repository mostly ready with $WARNINGS warnings"
        print_info "Consider addressing warnings before publishing"
    else
        print_error "❌ Repository has $ERRORS errors and $WARNINGS warnings"
        print_info "Please fix errors before publishing to GitHub"
    fi
    
    echo ""
    print_info "Quick Start Test Commands:"
    echo "  ./setup.sh check    # Check prerequisites"
    echo "  ./setup.sh full     # Complete setup"
    echo "  ./setup.sh start    # Start services"
    
    echo ""
    print_info "Manual Verification:"
    echo "  1. Check backend/.env configuration"
    echo "  2. Verify frontend/.env settings"
    echo "  3. Test API endpoints with curl"
    echo "  4. Run frontend in browser"
}

# Run all checks
main() {
    check_backend
    check_frontend
    check_documentation
    check_configuration
    check_cleanup
    check_git
    generate_report
    
    # Exit with error code if there are errors
    if [ $ERRORS -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

main "$@"