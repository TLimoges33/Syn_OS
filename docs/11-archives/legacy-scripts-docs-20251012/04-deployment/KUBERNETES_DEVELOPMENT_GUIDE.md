# Syn_OS Kubernetes Development Guide

This guide covers setting up and using Kubernetes for Syn_OS development and deployment.

## Quick Start

### Immediate Setup (for error resolution)
If you're getting "Kubeconfig not found" errors:

```bash
# Quick fix - creates minimal kubeconfig
./scripts/quick-kube-config.sh
```

### Full Development Environment (recommended)
For complete Kubernetes development environment:

```bash
# Full setup with local cluster
./scripts/setup-k8s-dev.sh
```

## Kubernetes Components in Syn_OS

### Directory Structure
```
deploy/kubernetes/
├── base/                          # Base Kubernetes manifests
│   ├── namespace.yaml            # Namespace definitions  
│   ├── core-deployment.yaml      # Core system deployment
│   ├── security-deployment.yaml  # Security manager deployment
│   └── kustomization.yaml        # Base kustomization
├── overlays/                     # Environment-specific overlays
│   ├── development/
│   │   └── kustomization.yaml    # Development environment
│   └── production/
│       └── kustomization.yaml    # Production environment
└── phase4-integration.yaml      # Phase 4 specific deployment
```

### Key Services
- **Core Services**: Consciousness kernel, eBPF monitoring
- **Security Services**: Threat detection, audit logging  
- **Enterprise Services**: Dashboard, MSSP platform
- **Networking**: Service mesh, ingress controllers

## Development Workflows

### 1. Local Development with Kind
```bash
# Setup local cluster
./scripts/setup-k8s-dev.sh

# Deploy development environment
kubectl apply -k deploy/kubernetes/overlays/development

# View status
kubectl get pods -n syn-os
kubectl get services -n syn-os
```

### 2. Testing Deployments
```bash
# Apply changes
kubectl apply -f deploy/kubernetes/base/

# Check rollout status
kubectl rollout status deployment/syn-os-core -n syn-os

# View logs
kubectl logs -f deployment/syn-os-core -n syn-os
```

### 3. Port Forwarding for Development
```bash
# Forward enterprise dashboard
kubectl port-forward service/syn-os-dashboard 8080:80 -n syn-os

# Forward consciousness API
kubectl port-forward service/syn-os-consciousness 9000:9000 -n syn-os

# Access at: http://localhost:8080 and http://localhost:9000
```

## Configuration Management

### ConfigMaps
- `syn-os-config`: Main configuration
- `syn-os-consciousness-config`: Consciousness parameters
- `syn-os-security-config`: Security policies

### Secrets
- `syn-os-secrets`: Database credentials, API keys
- `syn-os-tls`: TLS certificates
- `syn-os-enterprise-secrets`: Enterprise platform credentials

### Environment Variables
Key environment variables used across deployments:

```yaml
env:
- name: SYN_OS_ENVIRONMENT
  value: "development"
- name: SYN_OS_LOG_LEVEL  
  value: "debug"
- name: SYN_OS_CONSCIOUSNESS_ENABLED
  value: "true"
- name: SYN_OS_SECURITY_MODE
  value: "enforcing"
```

## Service Architecture

### Core Services
```yaml
# Core consciousness service
apiVersion: v1
kind: Service
metadata:
  name: syn-os-consciousness
spec:
  selector:
    app: syn-os-core
    component: consciousness
  ports:
  - port: 9000
    targetPort: 9000
```

### Security Services  
```yaml
# Security monitoring service
apiVersion: v1
kind: Service
metadata:
  name: syn-os-security
spec:
  selector:
    app: syn-os-security
  ports:
  - port: 8443
    targetPort: 8443
```

### Enterprise Services
```yaml
# Enterprise dashboard service
apiVersion: v1
kind: Service
metadata:
  name: syn-os-dashboard
spec:
  selector:
    app: syn-os-enterprise
    component: dashboard
  ports:
  - port: 80
    targetPort: 8080
```

## Monitoring and Observability

### Metrics Collection
```bash
# Install Prometheus (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Apply Syn_OS monitoring configuration
kubectl apply -f config/prometheus.yml
```

### Logging
```bash
# View application logs
kubectl logs -f deployment/syn-os-core -n syn-os

# View all namespace logs
kubectl logs -f --all-containers=true -n syn-os

# Follow logs with label selector
kubectl logs -f -l app=syn-os-core -n syn-os
```

### Health Checks
```bash
# Check pod health
kubectl get pods -n syn-os -o wide

# Describe problematic pods
kubectl describe pod <pod-name> -n syn-os

# Check events
kubectl get events -n syn-os --sort-by='.lastTimestamp'
```

## Troubleshooting

### Common Issues

#### 1. "Kubeconfig not found"
```bash
# Quick fix
./scripts/quick-kube-config.sh

# Or full setup
./scripts/setup-k8s-dev.sh
```

#### 2. "No cluster connection"
```bash
# Check cluster status
kubectl cluster-info

# Verify context
kubectl config current-context

# List available contexts
kubectl config get-contexts
```

#### 3. "Pod not starting"
```bash
# Check pod status
kubectl describe pod <pod-name> -n syn-os

# Check logs
kubectl logs <pod-name> -n syn-os

# Check events
kubectl get events -n syn-os
```

#### 4. "Service not accessible"
```bash
# Check service
kubectl get service -n syn-os

# Check endpoints
kubectl get endpoints -n syn-os

# Port forward to test
kubectl port-forward service/<service-name> 8080:80 -n syn-os
```

### Debugging Commands
```bash
# Execute shell in pod
kubectl exec -it <pod-name> -n syn-os -- /bin/bash

# Copy files from pod
kubectl cp <pod-name>:/path/to/file ./local-file -n syn-os

# Proxy to cluster
kubectl proxy --port=8080

# Access dashboard (if deployed)
kubectl dashboard
```

## Security Considerations

### RBAC Configuration
```yaml
# Service account for Syn_OS
apiVersion: v1
kind: ServiceAccount
metadata:
  name: syn-os-service-account
  namespace: syn-os
---
# Role for Syn_OS operations
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: syn-os-role
  namespace: syn-os
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
```

### Network Policies
```yaml
# Restrict network access
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: syn-os-network-policy
  namespace: syn-os
spec:
  podSelector:
    matchLabels:
      app: syn-os-core
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: syn-os
```

### Secret Management
```bash
# Create secret from command line
kubectl create secret generic syn-os-db-secret \
  --from-literal=username=synos \
  --from-literal=password=secure-password \
  -n syn-os

# Create secret from file
kubectl create secret generic syn-os-config-secret \
  --from-file=config.yaml \
  -n syn-os
```

## Production Deployment

### Prerequisites
- Kubernetes cluster (1.24+)
- Ingress controller (NGINX recommended)
- Certificate manager (cert-manager)
- Persistent volumes for data storage

### Deployment Steps
```bash
# 1. Create namespace
kubectl apply -f deploy/kubernetes/base/namespace.yaml

# 2. Apply secrets and configmaps
kubectl apply -f deploy/kubernetes/base/

# 3. Deploy production overlay
kubectl apply -k deploy/kubernetes/overlays/production

# 4. Verify deployment
kubectl get all -n syn-os
```

### Scaling
```bash
# Scale core services
kubectl scale deployment syn-os-core --replicas=3 -n syn-os

# Scale security services  
kubectl scale deployment syn-os-security --replicas=2 -n syn-os

# Auto-scaling (HPA)
kubectl autoscale deployment syn-os-core --cpu-percent=70 --min=2 --max=10 -n syn-os
```

## Useful Commands Reference

### Cluster Management
```bash
# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# Contexts
kubectl config get-contexts
kubectl config use-context <context-name>
kubectl config set-context --current --namespace=syn-os
```

### Resource Management
```bash
# Pods
kubectl get pods -n syn-os
kubectl describe pod <pod-name> -n syn-os
kubectl logs -f <pod-name> -n syn-os

# Services
kubectl get services -n syn-os
kubectl describe service <service-name> -n syn-os

# Deployments
kubectl get deployments -n syn-os
kubectl rollout status deployment/<deployment-name> -n syn-os
kubectl rollout restart deployment/<deployment-name> -n syn-os
```

### Debugging
```bash
# Events
kubectl get events -n syn-os --sort-by='.lastTimestamp'

# Resource usage
kubectl top nodes
kubectl top pods -n syn-os

# Network debugging
kubectl run debug --image=nicolaka/netshoot -it --rm -- bash
```

For more information, see the official Kubernetes documentation and the Syn_OS deployment guides in `/docs/deployment/`.
