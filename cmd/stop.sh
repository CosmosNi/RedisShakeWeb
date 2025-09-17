#!/bin/bash

# Redis-Shake Management Platform - Linux/macOS Stop Script
# This script helps you stop the Redis-Shake Management Platform services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

# Stop backend service
stop_backend() {
    log "Stopping backend service..."
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            
            # Wait for process to stop
            for i in {1..10}; do
                if ! kill -0 $BACKEND_PID 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 $BACKEND_PID 2>/dev/null; then
                warn "Backend service didn't stop gracefully, force killing..."
                kill -9 $BACKEND_PID 2>/dev/null || true
            fi
            
            log "Backend service stopped successfully"
        else
            warn "Backend service was not running"
        fi
        
        rm -f "$BACKEND_PID_FILE"
    else
        warn "Backend PID file not found, service may not be running"
    fi
}

# Stop frontend service
stop_frontend() {
    log "Stopping frontend service..."

    # First try to stop using PID file
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")

        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID

            # Wait for process to stop
            for i in {1..10}; do
                if ! kill -0 $FRONTEND_PID 2>/dev/null; then
                    break
                fi
                sleep 1
            done

            # Force kill if still running
            if kill -0 $FRONTEND_PID 2>/dev/null; then
                warn "Frontend service didn't stop gracefully, force killing..."
                kill -9 $FRONTEND_PID 2>/dev/null || true
            fi
        fi

        rm -f "$FRONTEND_PID_FILE"
    fi

    # Also check for any processes using port 3000 (React dev server)
    if lsof -ti:3000 >/dev/null 2>&1; then
        warn "Found process still using port 3000, stopping it..."
        PORT_PID=$(lsof -ti:3000)
        kill $PORT_PID 2>/dev/null || true

        # Wait for port to be free
        for i in {1..10}; do
            if ! lsof -ti:3000 >/dev/null 2>&1; then
                break
            fi
            sleep 1
        done

        # Force kill if still running
        if lsof -ti:3000 >/dev/null 2>&1; then
            warn "Process didn't stop gracefully, force killing..."
            PORT_PID=$(lsof -ti:3000)
            kill -9 $PORT_PID 2>/dev/null || true
        fi
    fi

    log "Frontend service stopped successfully"
}



# Show Redis-Shake processes status without stopping them
show_redis_shake_status() {
    REDIS_SHAKE_PIDS=$(pgrep -f "redis-shake" || true)
    if [ -n "$REDIS_SHAKE_PIDS" ]; then
        info "Found running Redis-Shake processes:"
        echo "$REDIS_SHAKE_PIDS" | while read -r pid; do
            if [ -n "$pid" ]; then
                info "  - PID: $pid"
            fi
        done
        info "These sync tasks will continue running after service restart."
    else
        info "No Redis-Shake processes found"
    fi
}

# Clean up temporary files
cleanup() {
    log "Cleaning up temporary files..."

    # Remove PID files
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"

    # Note: We don't delete task_*.toml files here because they contain user data
    # Task configuration files should only be deleted when tasks are explicitly deleted
    # If you need to clean up all task configurations, use: ./stop.sh clean-all

    log "Cleanup completed"
}

# Show status
show_status() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  Service Status"
    echo "=========================================="
    echo -e "${NC}"
    
    # Check backend
    if [ -f "$BACKEND_PID_FILE" ] && kill -0 $(cat "$BACKEND_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✓ Backend: Running (PID: $(cat $BACKEND_PID_FILE))${NC}"
    else
        echo -e "${RED}✗ Backend: Stopped${NC}"
    fi
    
    # Check frontend
    if [ -f "$FRONTEND_PID_FILE" ] && kill -0 $(cat "$FRONTEND_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✓ Frontend: Running (PID: $(cat $FRONTEND_PID_FILE))${NC}"
    else
        echo -e "${RED}✗ Frontend: Stopped${NC}"
    fi
    
    # Check Redis-Shake processes (sync tasks)
    REDIS_SHAKE_PIDS=$(pgrep -f "redis-shake" || true)
    if [ -n "$REDIS_SHAKE_PIDS" ]; then
        REDIS_SHAKE_COUNT=$(echo "$REDIS_SHAKE_PIDS" | wc -l | tr -d ' ')
        echo -e "${GREEN}✓ Sync Tasks: $REDIS_SHAKE_COUNT task(s) running${NC}"
        echo "$REDIS_SHAKE_PIDS" | while read -r pid; do
            if [ -n "$pid" ]; then
                echo -e "${BLUE}  - Task PID: $pid${NC}"
            fi
        done
    else
        echo -e "${YELLOW}○ Sync Tasks: No tasks running${NC}"
    fi
    
    echo ""
}

# Deep cleanup - removes all task configurations
deep_cleanup() {
    log "Performing deep cleanup (removing all task configurations)..."

    # Remove PID files
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"

    # Clean up task configuration files
    if [ -d "$PROJECT_ROOT/configs" ]; then
        find "$PROJECT_ROOT/configs" -name "task_*.toml" -delete 2>/dev/null || true
        log "Removed all task configuration files"
    fi

    # Reset task list
    if [ -f "$PROJECT_ROOT/configs/sync_tasks.json" ]; then
        echo "[]" > "$PROJECT_ROOT/configs/sync_tasks.json"
        log "Reset task list"
    fi

    # Clear logs
    if [ -f "$PROJECT_ROOT/logs/task_logs.json" ]; then
        echo "[]" > "$PROJECT_ROOT/logs/task_logs.json"
        log "Cleared task logs"
    fi

    log "Deep cleanup completed"
}

# Main function
main() {
    case "${1:-stop}" in
        "status")
            show_status
            ;;
        "stop"|"")
            echo -e "${BLUE}"
            echo "=========================================="
            echo "  Redis-Shake Management Platform"
            echo "  Linux/macOS Stop Script"
            echo "=========================================="
            echo -e "${NC}"

            stop_frontend
            stop_backend
            show_redis_shake_status
            cleanup

            echo -e "${GREEN}"
            echo "=========================================="
            echo "  🛑 Web services stopped successfully!"
            echo "  📊 Sync tasks continue running"
            echo "=========================================="
            echo -e "${NC}"
            ;;
        "clean-all")
            echo -e "${YELLOW}"
            echo "=========================================="
            echo "  ⚠️  DEEP CLEANUP WARNING"
            echo "=========================================="
            echo "This will remove ALL task configurations"
            echo "and logs. This action cannot be undone!"
            echo -e "${NC}"

            read -p "Are you sure you want to continue? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                stop_frontend
                stop_backend
                deep_cleanup

                echo -e "${GREEN}"
                echo "=========================================="
                echo "  🧹 Deep cleanup completed!"
                echo "=========================================="
                echo -e "${NC}"
            else
                echo "Operation cancelled."
            fi
            ;;
        *)
            echo "Usage: $0 [stop|status|clean-all]"
            echo "  stop      - Stop web services only (default)"
            echo "  status    - Show service status"
            echo "  clean-all - Stop services and remove all task data (DESTRUCTIVE)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
