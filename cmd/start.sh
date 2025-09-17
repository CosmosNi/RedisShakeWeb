#!/bin/bash

# Redis-Shake Management Platform - Linux/macOS Startup Script
# This script helps you quickly start the Redis-Shake Management Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REDIS_SHAKE_BIN="$PROJECT_ROOT/bin/redis-shake"

# PID files
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    info "Found Python $PYTHON_VERSION"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    info "Found Node.js $NODE_VERSION"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        error "npm is not installed. Please install npm."
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    info "Found npm $NPM_VERSION"
    
    # Check Redis-Shake binary
    if [ ! -f "$REDIS_SHAKE_BIN" ]; then
        warn "Redis-Shake binary not found at $REDIS_SHAKE_BIN"
        warn "Please download Redis-Shake from: https://github.com/tair-opensource/RedisShake/releases"
        warn "And place it at: $REDIS_SHAKE_BIN"
    else
        info "Found Redis-Shake binary"
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Backend dependencies
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        log "Installing Python dependencies..."
        cd "$BACKEND_DIR"
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            info "Creating Python virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
        
        log "Python dependencies installed successfully"
    else
        error "Backend requirements.txt not found"
        exit 1
    fi
    
    # Frontend dependencies
    if [ -f "$FRONTEND_DIR/package.json" ]; then
        log "Installing Node.js dependencies..."
        cd "$FRONTEND_DIR"
        
        if [ ! -d "node_modules" ]; then
            npm install
        else
            info "Node.js dependencies already installed"
        fi
        
        log "Node.js dependencies installed successfully"
    else
        error "Frontend package.json not found"
        exit 1
    fi
}

# Start backend service
start_backend() {
    log "Starting backend service..."

    cd "$BACKEND_DIR"

    # Check if backend is already running
    if [ -f "$BACKEND_PID_FILE" ] && kill -0 $(cat "$BACKEND_PID_FILE") 2>/dev/null; then
        warn "Backend service is already running (PID: $(cat $BACKEND_PID_FILE))"
        return 0
    fi

    # Activate virtual environment and start backend
    source venv/bin/activate

    # Install missing dependencies if needed
    log "Ensuring all dependencies are installed..."
    pip install -r requirements.txt > ../logs/pip-install.log 2>&1

    # Start backend in background
    nohup ./venv/bin/python -m app.main > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"

    # Wait a moment and check if the process is still running
    sleep 3
    if kill -0 $BACKEND_PID 2>/dev/null; then
        log "Backend service started successfully (PID: $BACKEND_PID)"
        info "Backend API: http://localhost:8000"
        info "API Documentation: http://localhost:8000/docs"
    else
        error "Failed to start backend service"
        error "Check the log file: $PROJECT_ROOT/logs/backend.log"
        if [ -f "../logs/backend.log" ]; then
            error "Last few lines of backend log:"
            tail -10 ../logs/backend.log
        fi
        rm -f "$BACKEND_PID_FILE"
        deactivate
        exit 1
    fi

    deactivate
}

# Start frontend service
start_frontend() {
    log "Starting frontend service..."

    cd "$FRONTEND_DIR"

    # Check if frontend is already running by checking port 3000
    if lsof -ti:3000 >/dev/null 2>&1; then
        warn "Port 3000 is already in use. Frontend may already be running."
        EXISTING_PID=$(lsof -ti:3000)
        echo $EXISTING_PID > "$FRONTEND_PID_FILE"
        info "Frontend Application: http://localhost:3000"
        return 0
    fi

    # Check if PID file exists and process is running
    if [ -f "$FRONTEND_PID_FILE" ] && kill -0 $(cat "$FRONTEND_PID_FILE") 2>/dev/null; then
        warn "Frontend service is already running (PID: $(cat $FRONTEND_PID_FILE))"
        return 0
    fi

    # Start frontend in background
    nohup npm start > ../logs/frontend.log 2>&1 &
    NPM_PID=$!

    # Wait for the actual React dev server to start and get its PID
    log "Waiting for React dev server to start..."
    for i in {1..30}; do
        sleep 1
        if lsof -ti:3000 >/dev/null 2>&1; then
            REACT_PID=$(lsof -ti:3000)
            echo $REACT_PID > "$FRONTEND_PID_FILE"
            log "Frontend service started successfully (PID: $REACT_PID)"
            info "Frontend Application: http://localhost:3000"
            return 0
        fi
    done

    error "Failed to start frontend service - React dev server didn't start within 30 seconds"
    kill $NPM_PID 2>/dev/null || true
    rm -f "$FRONTEND_PID_FILE"
    exit 1
}

# Create logs directory
create_logs_dir() {
    if [ ! -d "$PROJECT_ROOT/logs" ]; then
        mkdir -p "$PROJECT_ROOT/logs"
        info "Created logs directory"
    fi
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  Redis-Shake Management Platform"
    echo "  Linux/macOS Startup Script"
    echo "=========================================="
    echo -e "${NC}"
    
    create_logs_dir
    check_prerequisites
    install_dependencies
    start_backend
    start_frontend
    
    echo -e "${GREEN}"
    echo "=========================================="
    echo "  🎉 All services started successfully!"
    echo "=========================================="
    echo -e "${NC}"
    echo ""
    echo "📊 Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 Log files:"
    echo "   Backend: $PROJECT_ROOT/logs/backend.log"
    echo "   Frontend: $PROJECT_ROOT/logs/frontend.log"
    echo ""
    echo "🛑 To stop services, run: ./cmd/stop.sh"
    echo ""
}

# Run main function
main "$@"
