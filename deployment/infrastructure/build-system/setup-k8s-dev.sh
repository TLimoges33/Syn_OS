#!/bin/bash
#
# Syn_OS Kubernetes Development Environment Setup
# Creates a local Kubernetes cluster for Syn_OS development and testing
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker service."
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install kind (Kubernetes in Docker)
install_kind() {
    if command -v kind &> /dev/null; then
        log_info "kind is already installed"
        return 0
    fi
    
    log_info "Installing kind..."
    
    # Download kind
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    
    log_success "kind installed successfully"
}

# Create kind cluster configuration
create_kind_config() {
    log_info "Creating kind cluster configuration..."
    
    cat > /tmp/syn-os-kind-config.yaml << EOF
# Syn_OS Kind Cluster Configuration
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: syn-os-dev
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
  - containerPort: 30443
    hostPort: 30443
    protocol: TCP
- role: worker
  labels:
    syn-os/node-type: "worker"
- role: worker
  labels:
    syn-os/node-type: "worker"
networking:
  # WARNING: It is _strongly_ recommended that you keep this the default
  # (127.0.0.1) for security reasons. However it is possible to change this.
  apiServerAddress: "127.0.0.1"
  # By default the API server listens on a random open port.
  # You may choose a specific port but probably don't need to in most cases.
  # Using a random port makes it easier to spin up multiple clusters.
  apiServerPort: 6443
EOF
    
    log_success "Kind configuration created"
}

# Create the kind cluster
create_cluster() {
    log_info "Creating Syn_OS development cluster..."
    
    # Check if cluster already exists
    if kind get clusters | grep -q "syn-os-dev"; then
        log_warning "Cluster 'syn-os-dev' already exists. Deleting..."
        kind delete cluster --name syn-os-dev
    fi
    
    # Create the cluster
    kind create cluster --config /tmp/syn-os-kind-config.yaml
    
    log_success "Cluster created successfully"
}

# Configure kubectl context
configure_kubectl() {
    log_info "Configuring kubectl context..."
    
    # Ensure .kube directory exists
    mkdir -p ~/.kube
    
    # Set context to the new cluster
    kubectl cluster-info --context kind-syn-os-dev
    kubectl config use-context kind-syn-os-dev
    
    # Verify the connection
    kubectl get nodes
    
    log_success "kubectl configured successfully"
}

# Install essential cluster components
install_cluster_components() {
    log_info "Installing essential cluster components..."
    
    # Install NGINX Ingress Controller
    log_info "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    
    # Wait for ingress controller to be ready
    log_info "Waiting for ingress controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=90s
    
    # Install metrics-server for local development
    log_info "Installing metrics-server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    # Patch metrics-server for kind
    kubectl patch deployment metrics-server -n kube-system --type='merge' -p='{"spec":{"template":{"spec":{"containers":[{"name":"metrics-server","args":["--cert-dir=/tmp","--secure-port=4443","--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname","--kubelet-use-node-status-port","--metric-resolution=15s","--kubelet-insecure-tls"]}]}}}}'
    
    log_success "Essential components installed"
}

# Create Syn_OS namespace and base resources
setup_synos_namespace() {
    log_info "Setting up Syn_OS namespace and base resources..."
    
    # Create the namespace
    kubectl apply -f - << EOF
apiVersion: v1
kind: Namespace
metadata:
  name: syn-os
  labels:
    name: syn-os
    environment: development
    project: syn-os
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: syn-os-config
  namespace: syn-os
data:
  environment: "development"
  log_level: "debug"
  cluster_name: "syn-os-dev"
---
apiVersion: v1
kind: Secret
metadata:
  name: syn-os-secrets
  namespace: syn-os
type: Opaque
data:
  # Base64 encoded development secrets
  database_url: cG9zdGdyZXNxbDovL3N5bm9zOnN5bm9zQGxvY2FsaG9zdDo1NDMyL3N5bm9z  # postgresql://synos:synos@localhost:5432/synos
  jwt_secret: ZGV2ZWxvcG1lbnRfc2VjcmV0X2tleQ==  # development_secret_key
EOF
    
    log_success "Syn_OS namespace configured"
}

# Create development kubeconfig backup
create_kubeconfig_backup() {
    log_info "Creating kubeconfig backup..."
    
    if [ -f ~/.kube/config ]; then
        cp ~/.kube/config ~/.kube/config.backup.$(date +%Y%m%d_%H%M%S)
        log_success "Kubeconfig backup created"
    fi
}

# Display cluster information
display_cluster_info() {
    log_success "Syn_OS Kubernetes development environment setup complete!"
    echo
    log_info "Cluster Information:"
    echo "  - Cluster Name: syn-os-dev"
    echo "  - Context: kind-syn-os-dev"
    echo "  - Namespace: syn-os"
    echo "  - API Server: $(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')"
    echo
    log_info "Useful Commands:"
    echo "  - View cluster info: kubectl cluster-info"
    echo "  - View nodes: kubectl get nodes"
    echo "  - View pods: kubectl get pods -n syn-os"
    echo "  - Switch to syn-os namespace: kubectl config set-context --current --namespace=syn-os"
    echo "  - Delete cluster: kind delete cluster --name syn-os-dev"
    echo
    log_info "Next Steps:"
    echo "  1. Deploy Syn_OS components: cd deploy/kubernetes && kubectl apply -k overlays/development"
    echo "  2. Access services via: http://localhost:30080 (HTTP) or https://localhost:30443 (HTTPS)"
    echo "  3. View logs: kubectl logs -f deployment/<deployment-name> -n syn-os"
}

# Main execution
main() {
    log_info "Starting Syn_OS Kubernetes Development Environment Setup"
    echo
    
    check_prerequisites
    create_kubeconfig_backup
    install_kind
    create_kind_config
    create_cluster
    configure_kubectl
    install_cluster_components
    setup_synos_namespace
    
    echo
    display_cluster_info
}

# Execute main function
main "$@"
