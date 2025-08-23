# Kubernetes Configuration for Syn_OS

This directory contains the Kubernetes configuration files for deploying Syn_OS in various environments.

## Structure

```
deploy/kubernetes/
├── base/                           # Base Kubernetes manifests
│   ├── namespace.yaml             # Namespace definitions
│   ├── core-deployment.yaml       # Core system deployment
│   ├── security-deployment.yaml   # Security manager deployment
│   └── kustomization.yaml         # Base kustomization
├── overlays/                      # Environment-specific overlays
│   ├── development/
│   │   └── kustomization.yaml     # Development environment
│   └── production/
│       └── kustomization.yaml     # Production environment
└── phase4-integration.yaml       # Phase 4 specific deployment
```

## Deployment

### Development Environment
```bash
kubectl apply -k deploy/kubernetes/overlays/development
```

### Production Environment
```bash
kubectl apply -k deploy/kubernetes/overlays/production
```

### Base Resources Only
```bash
kubectl apply -k deploy/kubernetes/base
```

## Components

### Namespaces
- `synos-core`: Core system components
- `synos-security`: Security management services
- `synos-monitoring`: Monitoring and observability
- `synos-development`: Development environment

### Core Services
- **syn-os-core**: Main kernel and API services
- **syn-os-security-manager**: Security policies and threat detection
- **phase4-integration**: Advanced integration services

### Security Features
- RBAC with least privilege principle
- Network policies for inter-service communication
- Security contexts with non-root users
- Read-only root filesystems
- Capability dropping

### Monitoring
- Liveness and readiness probes
- Resource limits and requests
- Service monitors for Prometheus integration
- Health check endpoints

## Configuration

All configurations use Kustomize for environment-specific overlays:
- Development: Debug logging, single replicas, development images
- Production: Optimized performance, multiple replicas, stable images

## Secrets Management

Secrets are managed through:
- Base64 encoded secrets in manifests (for development)
- External secret files for production
- Kubernetes secret objects with proper RBAC

## Scaling

Horizontal Pod Autoscaler (HPA) is configured for:
- CPU utilization: 70%
- Memory utilization: 80%
- Min replicas: 2 (production), 1 (development)
- Max replicas: 10

## Network Policies

Network policies enforce:
- Ingress restrictions based on namespace labels
- Egress controls for external communications
- Inter-service communication rules
