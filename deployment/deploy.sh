#!/bin/bash

# SynOS Environment Management Script
# Usage: ./deploy.sh [environment] [action]
# Environments: development, staging, production
# Actions: up, down, restart, logs, status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENTS_DIR="$SCRIPT_DIR/environments"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-development}
ACTION=${2:-up}

# Available environments
AVAILABLE_ENVS=("development" "staging" "production")

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "SynOS Environment Management"
    echo ""
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments:"
    echo "  development  - Local development with minimal services"
    echo "  staging      - Production-like testing environment"  
    echo "  production   - Full production deployment with HA"
    echo ""
    echo "Actions:"
    echo "  up           - Start the environment"
    echo "  down         - Stop the environment"
    echo "  restart      - Restart all services"
    echo "  logs         - Show logs for all services"
    echo "  status       - Show status of all services"
    echo "  build        - Build all images"
    echo "  clean        - Remove all containers and volumes"
    echo ""
    echo "Examples:"
    echo "  $0 development up"
    echo "  $0 production logs"
    echo "  $0 staging restart"
}

validate_environment() {
    if [[ ! " ${AVAILABLE_ENVS[@]} " =~ " ${ENVIRONMENT} " ]]; then
        log_error "Invalid environment: $ENVIRONMENT"
        log_info "Available environments: ${AVAILABLE_ENVS[*]}"
        exit 1
    fi
}

check_environment_setup() {
    local env_dir="$ENVIRONMENTS_DIR/$ENVIRONMENT"
    
    if [[ ! -d "$env_dir" ]]; then
        log_error "Environment directory not found: $env_dir"
        exit 1
    fi
    
    if [[ ! -f "$env_dir/docker-compose.yml" ]]; then
        log_error "docker-compose.yml not found in $env_dir"
        exit 1
    fi
    
    # Check for .env file
    if [[ ! -f "$env_dir/.env" ]]; then
        if [[ -f "$env_dir/.env.template" ]]; then
            log_warning ".env file not found. Creating from template..."
            cp "$env_dir/.env.template" "$env_dir/.env"
            log_warning "Please edit $env_dir/.env with your configuration"
            if [[ "$ENVIRONMENT" == "production" ]]; then
                log_error "CRITICAL: Production .env file must be properly configured!"
                exit 1
            fi
        else
            log_error "No .env or .env.template found in $env_dir"
            exit 1
        fi
    fi
}

run_docker_compose() {
    local env_dir="$ENVIRONMENTS_DIR/$ENVIRONMENT"
    local cmd="docker-compose -f $env_dir/docker-compose.yml --env-file $env_dir/.env"
    
    log_info "Running: $cmd $*"
    eval "$cmd $*"
}

# Validate inputs
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

validate_environment
check_environment_setup

# Change to environment directory
cd "$ENVIRONMENTS_DIR/$ENVIRONMENT"

log_info "Managing SynOS $ENVIRONMENT environment"

# Execute action
case $ACTION in
    up)
        log_info "Starting $ENVIRONMENT environment..."
        run_docker_compose up -d
        log_success "$ENVIRONMENT environment started"
        echo ""
        log_info "Services status:"
        run_docker_compose ps
        ;;
    
    down)
        log_info "Stopping $ENVIRONMENT environment..."
        run_docker_compose down
        log_success "$ENVIRONMENT environment stopped"
        ;;
    
    restart)
        log_info "Restarting $ENVIRONMENT environment..."
        run_docker_compose restart
        log_success "$ENVIRONMENT environment restarted"
        ;;
    
    logs)
        log_info "Showing logs for $ENVIRONMENT environment..."
        run_docker_compose logs -f
        ;;
    
    status)
        log_info "Status of $ENVIRONMENT environment:"
        run_docker_compose ps
        echo ""
        log_info "Resource usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q 2>/dev/null || echo "")
        ;;
    
    build)
        log_info "Building images for $ENVIRONMENT environment..."
        run_docker_compose build
        log_success "Images built successfully"
        ;;
    
    clean)
        log_warning "This will remove ALL containers and volumes for $ENVIRONMENT environment"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleaning $ENVIRONMENT environment..."
            run_docker_compose down -v --remove-orphans
            log_success "$ENVIRONMENT environment cleaned"
        else
            log_info "Clean operation cancelled"
        fi
        ;;
    
    *)
        log_error "Invalid action: $ACTION"
        show_usage
        exit 1
        ;;
esac

log_success "Operation completed successfully"
