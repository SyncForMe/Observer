#!/bin/bash

# 🔭 AI Agent Simulation Observatory - Setup Script
# This script helps you set up the development environment

set -e

echo "🔭 AI Agent Simulation Observatory Setup"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 not found. Please install Python 3.8+ from https://python.org/"
        exit 1
    fi
    
    # Check MongoDB
    if command -v mongod &> /dev/null; then
        print_success "MongoDB found"
    else
        print_warning "MongoDB not found. Please install MongoDB 4.4+ from https://mongodb.com/"
        print_status "You can also use Docker: docker run -d -p 27017:27017 mongo:4.4"
    fi
    
    # Check Yarn
    if command -v yarn &> /dev/null; then
        YARN_VERSION=$(yarn --version)
        print_success "Yarn found: $YARN_VERSION"
    else
        print_status "Installing Yarn..."
        npm install -g yarn
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cp .env.example .env
        print_warning "Please update backend/.env with your API keys and configuration"
    fi
    
    cd ..
    print_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    yarn install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating frontend .env file..."
        cp .env.example .env
        print_warning "Please update frontend/.env if needed"
    fi
    
    cd ..
    print_success "Frontend setup complete"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Check if MongoDB is running
    if ! pgrep -x "mongod" > /dev/null; then
        print_status "Starting MongoDB..."
        if command -v brew &> /dev/null; then
            brew services start mongodb-community
        elif command -v systemctl &> /dev/null; then
            sudo systemctl start mongod
        else
            print_warning "Please start MongoDB manually: mongod --dbpath ./data/db"
        fi
    fi
    
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
    BACKEND_PID=$!
    cd ..
    
    sleep 3
    
    print_status "Starting frontend server..."
    cd frontend
    yarn start &
    FRONTEND_PID=$!
    cd ..
    
    print_success "Services started!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8001"
    print_status "API Documentation: http://localhost:8001/docs"
    
    echo ""
    print_status "Press Ctrl+C to stop all services"
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
}

# Validate setup
validate_setup() {
    print_status "Validating setup..."
    
    # Check if backend is running
    if curl -s http://localhost:8001/health > /dev/null; then
        print_success "Backend is responding"
    else
        print_warning "Backend health check failed"
    fi
    
    # Check if frontend is accessible
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend accessibility check failed"
    fi
}

# Main setup flow
main() {
    case "$1" in
        "check")
            check_prerequisites
            ;;
        "backend")
            setup_backend
            ;;
        "frontend")
            setup_frontend
            ;;
        "start")
            start_services
            ;;
        "validate")
            validate_setup
            ;;
        "full"|"")
            check_prerequisites
            setup_backend
            setup_frontend
            print_success "Setup complete!"
            echo ""
            print_status "Next steps:"
            echo "1. Update backend/.env with your API keys"
            echo "2. Start MongoDB if not running"
            echo "3. Run './setup.sh start' to start all services"
            echo "4. Visit http://localhost:3000 to access the application"
            ;;
        *)
            echo "Usage: $0 [check|backend|frontend|start|validate|full]"
            echo ""
            echo "Commands:"
            echo "  check     - Check prerequisites"
            echo "  backend   - Setup backend only"
            echo "  frontend  - Setup frontend only"
            echo "  start     - Start all services"
            echo "  validate  - Validate running services"
            echo "  full      - Complete setup (default)"
            exit 1
            ;;
    esac
}

main "$@"