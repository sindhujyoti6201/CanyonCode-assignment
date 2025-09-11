#!/bin/bash

# Camera Feed Query System - Unified Start Script
set -e

echo "🚀 Camera Feed Query System - Starting Services"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if .env file exists
check_env() {
    print_status "Checking environment configuration..."
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f env_example.txt ]; then
            cp env_example.txt .env
            print_warning "Please edit .env file and add your OPENAI_API_KEY"
        else
            print_error "env_example.txt not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Start React frontend
start_frontend() {
    print_status "Starting React frontend..."
    
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found"
        exit 1
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend in background
    print_status "Starting React development server..."
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../.frontend.pid
    
    cd ..
    print_success "Frontend started (PID: $FRONTEND_PID)"
}

# Start backend services
start_backend() {
    local profile=${1:-""}
    print_status "Starting backend services..."
    
    if [ -n "$profile" ]; then
        docker-compose --profile $profile up -d
        print_success "Backend services started with profile: $profile"
    else
        docker-compose up -d
        print_success "Backend services started"
    fi
}

# Show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
}

# Show logs
show_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        docker-compose logs -f $service
    else
        docker-compose logs -f
    fi
}

# Stop all services
stop_all() {
    print_status "Stopping all services..."
    
    # Stop frontend if running
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_status "Stopping frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            rm .frontend.pid
            print_success "Frontend stopped"
        fi
    fi
    
    # Stop backend services
    docker-compose down
    print_success "Backend services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    # Wait for services to start
    sleep 5
    
    # Check API health
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        print_success "API health check passed"
    else
        print_warning "API health check failed"
    fi
    
    # Check Web UI
    if curl -f http://localhost:8502 > /dev/null 2>&1; then
        print_success "Web UI health check passed"
    else
        print_warning "Web UI health check failed"
    fi
    
    # Check Frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend health check passed"
    else
        print_warning "Frontend health check failed"
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [profile]  - Start all services (frontend + backend)"
    echo "  stop             - Stop all services"
    echo "  restart [profile]- Restart all services"
    echo "  status           - Show service status"
    echo "  logs [service]   - Show logs (optionally for specific service)"
    echo "  health           - Perform health checks"
    echo "  cleanup          - Clean up Docker resources"
    echo "  help             - Show this help"
    echo ""
    echo "Profiles:"
    echo "  dev              - Development mode with hot reload"
    echo "  demo             - Run demo only"
    echo "  nginx            - Include nginx reverse proxy"
    echo ""
    echo "Examples:"
    echo "  $0 start         - Start all services"
    echo "  $0 start dev     - Start in development mode"
    echo "  $0 logs api      - Show API logs"
    echo "  $0 health        - Check service health"
}

# Main script logic
case "${1:-start}" in
    start)
        check_env
        start_frontend
        start_backend "$2"
        show_status
        health_check
        echo ""
        print_success "All services are running!"
        echo "Frontend: http://localhost:3000"
        echo "API: http://localhost:8001"
        echo "Web UI: http://localhost:8502"
        echo "API Docs: http://localhost:8001/docs"
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        check_env
        start_frontend
        start_backend "$2"
        show_status
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    health)
        health_check
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
