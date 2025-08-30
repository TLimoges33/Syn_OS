#!/bin/bash
set -euo pipefail

# Production Deployment Script for Syn_OS
# Supports Docker Compose and Kubernetes deployments

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
DEPLOYMENT_TYPE="docker"
ENVIRONMENT="production"
TAG="latest"
REGISTRY="ghcr.io/syn-os"
DRY_RUN=false
FORCE=false
BACKUP_BEFORE_DEPLOY=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy Syn_OS to production environment

Options:
    -t, --type TYPE         Deployment type: docker, kubernetes (default: docker)
    -e, --environment ENV   Environment: staging, production (default: production)
    -r, --registry URL      Container registry URL (default: ghcr.io/syn-os)
    -T, --tag TAG          Image tag to deploy (default: latest)
    -n, --dry-run          Show what would be deployed without making changes
    -f, --force            Force deployment without confirmation
    -b, --no-backup        Skip backup before deployment
    -h, --help             Show this help message

Examples:
    $0                                          # Deploy to production with Docker
    $0 -t kubernetes -e staging               # Deploy to staging with Kubernetes
    $0 -n -T v1.2.3                          # Dry run with specific tag
    $0 -f -t kubernetes --tag=latest         # Force Kubernetes deployment

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -T|--tag)
            TAG="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -b|--no-backup)
            BACKUP_BEFORE_DEPLOY=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate inputs
if [[ ! "$DEPLOYMENT_TYPE" =~ ^(docker|kubernetes)$ ]]; then
    log_error "Invalid deployment type: $DEPLOYMENT_TYPE"
    exit 1
fi

if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    exit 1
fi

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    
    # Common tools
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    
    # Kubernetes tools
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
        command -v helm >/dev/null 2>&1 || missing_tools+=("helm")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Load environment configuration
load_environment() {
    log_info "Loading environment configuration..."
    
    local env_file="$PROJECT_ROOT/.env.$ENVIRONMENT"
    if [[ -f "$env_file" ]]; then
        source "$env_file"
        log_success "Loaded environment from $env_file"
    else
        log_warning "Environment file not found: $env_file"
        log_info "Using default configuration"
    fi
    
    # Set registry and tag in environment
    export REGISTRY="$REGISTRY"
    export TAG="$TAG"
}

# Validate environment
validate_environment() {
    log_info "Validating environment configuration..."
    
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD" 
        "JWT_SECRET_KEY"
        "ENCRYPTION_KEY"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        log_error "Please set these in .env.$ENVIRONMENT file"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Create backup
create_backup() {
    if [[ "$BACKUP_BEFORE_DEPLOY" == false ]]; then
        log_info "Skipping backup as requested"
        return 0
    fi
    
    log_info "Creating backup before deployment..."
    
    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        # Backup Docker volumes
        log_info "Backing up Docker volumes..."
        docker run --rm -v syn_os_postgres_primary_data:/source -v "$backup_dir":/backup busybox tar czf /backup/postgres_data.tar.gz -C /source .
        docker run --rm -v syn_os_consciousness_1_data:/source -v "$backup_dir":/backup busybox tar czf /backup/consciousness_data.tar.gz -C /source .
        docker run --rm -v syn_os_redis_master_data:/source -v "$backup_dir":/backup busybox tar czf /backup/redis_data.tar.gz -C /source .
    else
        # Backup Kubernetes persistent volumes
        log_info "Backing up Kubernetes persistent volumes..."
        kubectl get pv -o yaml > "$backup_dir/persistent_volumes.yaml"
        kubectl get pvc -n syn-os-$ENVIRONMENT -o yaml > "$backup_dir/persistent_volume_claims.yaml"
    fi
    
    log_success "Backup created at $backup_dir"
}

# Deploy with Docker Compose
deploy_docker() {
    log_info "Deploying with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would execute:"
        echo "docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml up -d"
        return 0
    fi
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml pull
    
    # Deploy services
    log_info "Starting services..."
    docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be ready..."
    local max_attempts=60
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml ps | grep -q "unhealthy\|Exit"; then
            log_info "Waiting for services... ($((attempt + 1))/$max_attempts)"
            sleep 10
            ((attempt++))
        else
            break
        fi
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        log_error "Services failed to start within timeout"
        docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml ps
        exit 1
    fi
    
    log_success "Docker deployment completed successfully"
}

# Deploy with Kubernetes
deploy_kubernetes() {
    log_info "Deploying with Kubernetes..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would execute:"
        echo "helm upgrade --install syn-os-$ENVIRONMENT ./deploy/helm/syn-os \\"
        echo "  --namespace syn-os-$ENVIRONMENT \\"
        echo "  --create-namespace \\"
        echo "  --set-string image.tag=$TAG \\"
        echo "  --set-string global.environment=$ENVIRONMENT"
        return 0
    fi
    
    # Deploy with Helm
    log_info "Deploying with Helm..."
    helm upgrade --install "syn-os-$ENVIRONMENT" ./deploy/helm/syn-os \
        --namespace "syn-os-$ENVIRONMENT" \
        --create-namespace \
        --set-string image.tag="$TAG" \
        --set-string global.environment="$ENVIRONMENT" \
        --set-string image.registry="$REGISTRY" \
        --wait \
        --timeout=600s
    
    # Wait for rollout
    log_info "Waiting for deployment rollout..."
    kubectl rollout status deployment/syn-os-orchestrator -n "syn-os-$ENVIRONMENT" --timeout=300s
    kubectl rollout status deployment/syn-os-consciousness -n "syn-os-$ENVIRONMENT" --timeout=300s
    kubectl rollout status deployment/syn-os-security-dashboard -n "syn-os-$ENVIRONMENT" --timeout=300s
    
    log_success "Kubernetes deployment completed successfully"
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        # Docker health checks
        local services=("orchestrator-1" "consciousness-1" "security-dashboard-1")
        for service in "${services[@]}"; do
            local container="syn_os_$service"
            if docker ps --filter "name=$container" --filter "health=healthy" | grep -q "$container"; then
                log_success "$service is healthy"
            else
                log_error "$service is not healthy"
                docker logs "$container" --tail=20
                exit 1
            fi
        done
    else
        # Kubernetes health checks
        kubectl get pods -n "syn-os-$ENVIRONMENT" | grep -E "(orchestrator|consciousness|security-dashboard)" | grep -v Running && {
            log_error "Some pods are not running"
            kubectl get pods -n "syn-os-$ENVIRONMENT"
            exit 1
        }
        log_success "All Kubernetes pods are running"
    fi
    
    log_success "Health checks passed"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would run smoke tests"
        return 0
    fi
    
    # Get service URL
    local base_url
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        base_url="http://localhost"
    else
        base_url=$(kubectl get ingress -n "syn-os-$ENVIRONMENT" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "localhost")
        base_url="https://$base_url"
    fi
    
    # Test endpoints
    local endpoints=("/health" "/api/health" "/consciousness/health" "/security/health")
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$base_url$endpoint" >/dev/null; then
            log_success "✓ $endpoint is responding"
        else
            log_warning "✗ $endpoint is not responding"
        fi
    done
    
    log_success "Smoke tests completed"
}

# Confirmation prompt
confirm_deployment() {
    if [[ "$FORCE" == true || "$DRY_RUN" == true ]]; then
        return 0
    fi
    
    echo
    log_warning "About to deploy Syn_OS with the following configuration:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Deployment Type: $DEPLOYMENT_TYPE"
    echo "  Registry: $REGISTRY"
    echo "  Tag: $TAG"
    echo "  Backup: $BACKUP_BEFORE_DEPLOY"
    echo
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
}

# Main deployment flow
main() {
    log_info "Starting Syn_OS $ENVIRONMENT deployment..."
    
    check_prerequisites
    load_environment
    validate_environment
    confirm_deployment
    create_backup
    
    case "$DEPLOYMENT_TYPE" in
        docker)
            deploy_docker
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
    esac
    
    run_health_checks
    run_smoke_tests
    
    log_success "🎉 Syn_OS deployment completed successfully!"
    log_info "Environment: $ENVIRONMENT"
    log_info "Tag: $TAG"
    log_info "Deployment type: $DEPLOYMENT_TYPE"
}

# Run main function
main "$@"