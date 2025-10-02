#!/bin/bash
# Kubernetes deployment script for Syn_OS
# Usage: ./deploy-k8s.sh [environment]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
KUBE_DIR="$PROJECT_ROOT/deploy/kubernetes"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        return 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "kubectl cannot connect to cluster"
        return 1
    fi
    
    log_success "kubectl is available and connected"
    return 0
}

# Function to check if kustomize is available
check_kustomize() {
    if ! command -v kustomize &> /dev/null; then
        log_warning "kustomize not found, using kubectl with -k flag"
        return 1
    fi
    
    log_success "kustomize is available"
    return 0
}

# Function to validate kubernetes manifests
validate_manifests() {
    local env="$1"
    local overlay_path="$KUBE_DIR/overlays/$env"
    
    log_info "Validating Kubernetes manifests for environment: $env"
    
    if [[ ! -d "$overlay_path" ]]; then
        log_error "Environment overlay not found: $overlay_path"
        return 1
    fi
    
    # Use kustomize if available, otherwise use kubectl
    if check_kustomize; then
        if kustomize build "$overlay_path" | kubectl apply --dry-run=client -f -; then
            log_success "Manifest validation passed"
        else
            log_error "Manifest validation failed"
            return 1
        fi
    else
        if kubectl apply --dry-run=client -k "$overlay_path"; then
            log_success "Manifest validation passed"
        else
            log_error "Manifest validation failed"
            return 1
        fi
    fi
}

# Function to deploy to kubernetes
deploy_to_k8s() {
    local env="$1"
    local overlay_path="$KUBE_DIR/overlays/$env"
    
    log_info "Deploying Syn_OS to Kubernetes environment: $env"
    
    # Create namespaces first
    log_info "Creating namespaces..."
    kubectl apply -f "$KUBE_DIR/base/namespace.yaml"
    
    # Deploy the environment overlay
    log_info "Applying manifests..."
    if check_kustomize; then
        kustomize build "$overlay_path" | kubectl apply -f -
    else
        kubectl apply -k "$overlay_path"
    fi
    
    log_success "Deployment completed"
}

# Function to check deployment status
check_deployment_status() {
    local env="$1"
    local namespace
    
    case "$env" in
        "development")
            namespace="synos-development"
            ;;
        "production")
            namespace="synos-core"
            ;;
        *)
            namespace="synos-core"
            ;;
    esac
    
    log_info "Checking deployment status in namespace: $namespace"
    
    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment --all -n "$namespace" || {
        log_warning "Some deployments may not be ready yet"
    }
    
    # Show deployment status
    echo
    log_info "Deployment Status:"
    kubectl get deployments -n "$namespace"
    
    echo
    log_info "Pod Status:"
    kubectl get pods -n "$namespace"
    
    echo
    log_info "Service Status:"
    kubectl get services -n "$namespace"
}

# Function to cleanup deployment
cleanup_deployment() {
    local env="$1"
    local overlay_path="$KUBE_DIR/overlays/$env"
    
    log_warning "Cleaning up Syn_OS deployment for environment: $env"
    
    if check_kustomize; then
        kustomize build "$overlay_path" | kubectl delete -f - || true
    else
        kubectl delete -k "$overlay_path" || true
    fi
    
    log_success "Cleanup completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command] [environment]"
    echo
    echo "Commands:"
    echo "  deploy      Deploy to Kubernetes (default)"
    echo "  validate    Validate manifests only"
    echo "  status      Check deployment status"
    echo "  cleanup     Remove deployment"
    echo
    echo "Environments:"
    echo "  development Development environment (default)"
    echo "  production  Production environment"
    echo
    echo "Examples:"
    echo "  $0 deploy development"
    echo "  $0 validate production"
    echo "  $0 status development"
    echo "  $0 cleanup development"
}

# Main execution
main() {
    local command="${1:-deploy}"
    local environment="${2:-development}"
    
    # Validate environment parameter
    if [[ "$environment" != "development" && "$environment" != "production" ]]; then
        log_error "Invalid environment: $environment"
        log_error "Valid environments: development, production"
        exit 1
    fi
    
    # Check prerequisites
    if ! check_kubectl; then
        exit 1
    fi
    
    case "$command" in
        "deploy")
            validate_manifests "$environment"
            deploy_to_k8s "$environment"
            check_deployment_status "$environment"
            ;;
        "validate")
            validate_manifests "$environment"
            ;;
        "status")
            check_deployment_status "$environment"
            ;;
        "cleanup")
            cleanup_deployment "$environment"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
