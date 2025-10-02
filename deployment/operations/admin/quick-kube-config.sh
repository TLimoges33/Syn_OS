#!/bin/bash
#
# Quick Kubernetes Config Setup for Syn_OS Development
# Creates a minimal kubeconfig for local development
#

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Create .kube directory if it doesn't exist
create_kube_directory() {
    log_info "Creating ~/.kube directory..."
    mkdir -p ~/.kube
    log_success "Directory created"
}

# Create a minimal kubeconfig for local development
create_minimal_kubeconfig() {
    log_info "Creating minimal kubeconfig for Syn_OS development..."
    
    cat > ~/.kube/config << EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: ""
    server: http://localhost:8080
  name: syn-os-local
contexts:
- context:
    cluster: syn-os-local
    namespace: syn-os
    user: syn-os-dev
  name: syn-os-local
current-context: syn-os-local
preferences: {}
users:
- name: syn-os-dev
  user:
    token: "development-token"
EOF
    
    chmod 600 ~/.kube/config
    log_success "Minimal kubeconfig created"
}

# Display information
display_info() {
    log_success "Quick kubeconfig setup complete!"
    echo
    log_info "Note: This is a minimal configuration for development."
    log_info "For a full Kubernetes environment, run: ./scripts/setup-k8s-dev.sh"
    echo
    log_info "Current kubeconfig location: ~/.kube/config"
    log_info "Current context: syn-os-local"
    echo
    log_info "To set up a real cluster, you can:"
    echo "  1. Run: ./scripts/setup-k8s-dev.sh (recommended)"
    echo "  2. Or connect to an existing cluster by updating ~/.kube/config"
}

# Main execution
main() {
    log_info "Setting up quick Kubernetes config for Syn_OS..."
    echo
    
    create_kube_directory
    create_minimal_kubeconfig
    
    echo
    display_info
}

# Execute main function
main "$@"
