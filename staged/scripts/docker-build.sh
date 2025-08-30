#!/bin/bash
# Syn_OS Docker Build and Deployment Script
# Automated setup for consciousness-aware cybersecurity education platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

# Build options
BUILD_DEV_ONLY=false
BUILD_EDUCATIONAL_ONLY=false
BUILD_ALL=true
SKIP_TESTS=false
VERBOSE=false

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🐳 $1${NC}"
}

# Help function
show_help() {
    echo "Syn_OS Docker Build Script"
    echo "========================="
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build         Build all Docker images (default)"
    echo "  dev           Build development environment only"
    echo "  educational   Build educational platform only"
    echo "  start         Start all services"
    echo "  stop          Stop all services"
    echo "  clean         Clean up containers and images"
    echo "  test          Run integration tests"
    echo "  status        Show service status"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -v, --verbose           Verbose output"
    echo "  --skip-tests           Skip integration tests"
    echo "  --dev-only             Build development environment only"
    echo "  --educational-only     Build educational platform only"
    echo ""
    echo "Examples:"
    echo "  $0 build                Build all images"
    echo "  $0 dev                  Build and start development environment"
    echo "  $0 educational          Build and start educational platform"
    echo "  $0 start                Start all services"
    echo "  $0 clean                Clean up everything"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --dev-only)
                BUILD_DEV_ONLY=true
                BUILD_ALL=false
                shift
                ;;
            --educational-only)
                BUILD_EDUCATIONAL_ONLY=true
                BUILD_ALL=false
                shift
                ;;
            build|dev|educational|start|stop|clean|test|status)
                COMMAND="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check available disk space (at least 10GB)
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    required_space=10485760  # 10GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        print_warning "Low disk space. At least 10GB recommended for full build"
    fi
    
    print_status "Prerequisites check passed"
}

# Build Docker images
build_images() {
    print_header "Building Syn_OS Docker Images"
    echo "=============================="
    
    cd "$PROJECT_ROOT"
    
    if [ "$BUILD_ALL" = true ] || [ "$BUILD_DEV_ONLY" = true ]; then
        print_info "Building development environment..."
        
        if [ "$VERBOSE" = true ]; then
            docker-compose build kernel-dev
        else
            docker-compose build kernel-dev > /dev/null 2>&1
        fi
        
        print_status "Development environment built"
    fi
    
    if [ "$BUILD_ALL" = true ] || [ "$BUILD_EDUCATIONAL_ONLY" = true ]; then
        print_info "Building educational platform..."
        
        if [ "$VERBOSE" = true ]; then
            docker-compose build educational-sandbox consciousness-monitor learning-analytics
        else
            docker-compose build educational-sandbox consciousness-monitor learning-analytics > /dev/null 2>&1
        fi
        
        print_status "Educational platform built"
    fi
    
    if [ "$BUILD_ALL" = true ]; then
        print_info "Building infrastructure services..."
        
        if [ "$VERBOSE" = true ]; then
            docker-compose build
        else
            docker-compose build > /dev/null 2>&1
        fi
        
        print_status "All images built successfully"
    fi
}

# Start services
start_services() {
    print_header "Starting Syn_OS Services"
    echo "========================"
    
    cd "$PROJECT_ROOT"
    
    if [ "$BUILD_DEV_ONLY" = true ]; then
        print_info "Starting development services..."
        docker-compose up -d kernel-dev consciousness-monitor consciousness-db consciousness-cache
        
    elif [ "$BUILD_EDUCATIONAL_ONLY" = true ]; then
        print_info "Starting educational services..."
        docker-compose up -d educational-sandbox learning-analytics consciousness-monitor consciousness-db consciousness-cache educational-gateway
        
    else
        print_info "Starting all services..."
        docker-compose up -d
    fi
    
    # Wait for services to be ready
    print_info "Waiting for services to initialize..."
    sleep 10
    
    # Check service health
    check_service_health
    
    print_status "Services started successfully"
    display_service_info
}

# Stop services
stop_services() {
    print_header "Stopping Syn_OS Services"
    echo "========================"
    
    cd "$PROJECT_ROOT"
    
    print_info "Stopping all services..."
    docker-compose down
    
    print_status "All services stopped"
}

# Clean up
clean_up() {
    print_header "Cleaning Up Syn_OS Docker Environment"
    echo "====================================="
    
    cd "$PROJECT_ROOT"
    
    print_warning "This will remove all containers, images, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping and removing containers..."
        docker-compose down -v --remove-orphans
        
        print_info "Removing images..."
        docker images | grep -E "(syn-os|consciousness|educational)" | awk '{print $3}' | xargs -r docker rmi -f
        
        print_info "Cleaning up unused resources..."
        docker system prune -f
        
        print_status "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Check service health
check_service_health() {
    print_info "Checking service health..."
    
    local services=()
    local unhealthy_services=()
    
    # Get list of running services
    while IFS= read -r service; do
        services+=("$service")
    done < <(docker-compose ps --services --filter "status=running")
    
    # Check each service
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "healthy\|Up"; then
            print_status "$service is healthy"
        else
            print_warning "$service is not healthy"
            unhealthy_services+=("$service")
        fi
    done
    
    if [ ${#unhealthy_services[@]} -gt 0 ]; then
        print_warning "Some services are not healthy: ${unhealthy_services[*]}"
        print_info "Check logs with: docker-compose logs <service-name>"
    fi
}

# Run integration tests
run_tests() {
    print_header "Running Integration Tests"
    echo "========================="
    
    cd "$PROJECT_ROOT"
    
    if [ "$SKIP_TESTS" = true ]; then
        print_warning "Skipping tests"
        return 0
    fi
    
    # Ensure services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_info "Starting services for testing..."
        start_services
    fi
    
    print_info "Running kernel development tests..."
    if docker-compose exec -T kernel-dev bash -c "cd /workspace/syn_os && cargo test --target x86_64-unknown-none" > /dev/null 2>&1; then
        print_status "Kernel tests passed"
    else
        print_error "Kernel tests failed"
    fi
    
    print_info "Testing consciousness monitoring API..."
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_status "Consciousness monitor API is responding"
    else
        print_error "Consciousness monitor API test failed"
    fi
    
    print_info "Testing educational sandbox..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Educational sandbox is responding"
    else
        print_error "Educational sandbox test failed"
    fi
    
    print_info "Testing database connectivity..."
    if docker-compose exec -T consciousness-db pg_isready -U synaptic > /dev/null 2>&1; then
        print_status "Database connectivity test passed"
    else
        print_error "Database connectivity test failed"
    fi
    
    print_status "Integration tests completed"
}

# Show service status
show_status() {
    print_header "Syn_OS Service Status"
    echo "===================="
    
    cd "$PROJECT_ROOT"
    
    # Show container status
    print_info "Container Status:"
    docker-compose ps
    
    echo ""
    
    # Show resource usage
    print_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    echo ""
    
    # Show service URLs
    display_service_info
}

# Display service information
display_service_info() {
    echo ""
    print_header "Syn_OS Services Ready"
    echo "===================="
    echo ""
    
    if docker-compose ps kernel-dev | grep -q "Up"; then
        echo -e "${GREEN}🔧 Development Environment:${NC}"
        echo "  • VS Code Server: http://localhost:9000"
        echo "  • Development Server: http://localhost:8080"
        echo "  • Secure Dev Server: https://localhost:8443"
        echo ""
    fi
    
    if docker-compose ps educational-sandbox | grep -q "Up"; then
        echo -e "${BLUE}🎓 Educational Platform:${NC}"
        echo "  • Educational Dashboard: http://localhost:8000"
        echo "  • Learning Analytics: http://localhost:8001"
        echo "  • Student Progress: http://localhost:8002"
        echo ""
    fi
    
    if docker-compose ps consciousness-monitor | grep -q "Up"; then
        echo -e "${PURPLE}🧠 Consciousness Platform:${NC}"
        echo "  • Consciousness API: http://localhost:5000"
        echo "  • Real-time WebSocket: ws://localhost:5001"
        echo "  • Health Check: http://localhost:5000/health"
        echo ""
    fi
    
    if docker-compose ps learning-analytics | grep -q "Up"; then
        echo -e "${YELLOW}📊 Analytics Platform:${NC}"
        echo "  • Analytics API: http://localhost:6000"
        echo "  • Analytics Dashboard: http://localhost:6001"
        echo ""
    fi
    
    if docker-compose ps educational-gateway | grep -q "Up"; then
        echo -e "${GREEN}🌐 Educational Gateway:${NC}"
        echo "  • Main Platform: http://localhost"
        echo "  • Secure Platform: https://localhost"
        echo ""
    fi
    
    echo -e "${BLUE}📚 Quick Start Commands:${NC}"
    echo "  • Access development: docker-compose exec kernel-dev bash"
    echo "  • Access educational: docker-compose exec educational-sandbox educational-shell"
    echo "  • View logs: docker-compose logs -f <service-name>"
    echo "  • Stop services: docker-compose down"
    echo ""
}

# Main execution
main() {
    local command="${COMMAND:-build}"
    
    print_header "Syn_OS Docker Build System"
    echo "=========================="
    echo ""
    
    check_prerequisites
    
    case "$command" in
        build)
            build_images
            if [ "$SKIP_TESTS" = false ]; then
                run_tests
            fi
            ;;
        dev)
            BUILD_DEV_ONLY=true
            BUILD_ALL=false
            build_images
            start_services
            ;;
        educational)
            BUILD_EDUCATIONAL_ONLY=true
            BUILD_ALL=false
            build_images
            start_services
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        clean)
            clean_up
            ;;
        test)
            run_tests
            ;;
        status)
            show_status
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments and run main function
parse_args "$@"
main