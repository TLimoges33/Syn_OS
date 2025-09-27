# Kubernetes Configuration for Syn_OS

This directory contains the Kubernetes configuration files for deploying Syn_OS in various environments using **Kustomize**.

## Directory Structure

```text
deploy/kubernetes/
├── base/                           # Base Kubernetes manifests
│   ├── namespace.yaml             # Namespace definitions
│   ├── core-deployment.yaml       # Core system deployment
│   ├── security-deployment.yaml   # Security manager deployment
│   └── kustomization.yaml         # Base kustomization
├── overlays/                      # Environment-specific overlays
│   ├── development/
│   │   ├── kustomization.yaml     # Development environment
│   │   └── deployment-patches.yaml # Development patches
│   └── production/
│       ├── kustomization.yaml     # Production environment
│       ├── deployment-patches.yaml # Production patches
│       └── hpa.yaml               # Horizontal Pod Autoscaler
└── README.md                      # This file
```

## Quick Start

### 1. Development Environment

Deploy to development with reduced resources:

```bash
kubectl apply -k deploy/kubernetes/overlays/development/
```

### 2. Production Environment

Deploy to production with full HA configuration:

```bash
kubectl apply -k deploy/kubernetes/overlays/production/
```

## Environment Configurations

### Development

- **Namespace**: `syn-os-dev`
- **Replicas**: 1 core, 1 security
- **Resources**: Minimal for local development
- **Features**: Debug logging, detailed metrics

### Production

- **Namespace**: `syn-os-prod`
- **Replicas**: 5 core, 3 security (with HPA)
- **Resources**: High-performance configuration
- **Features**: Optimized performance, audit logging

## Manual Deployment Steps

If you prefer manual deployment:

```bash
# 1. Deploy base configuration
kubectl apply -k deploy/kubernetes/base/

# 2. Apply environment-specific patches
kubectl apply -k deploy/kubernetes/overlays/production/

# 3. Verify deployment
kubectl get all -n syn-os-prod
```

## Monitoring

Check deployment status:

```bash
# Core services
kubectl get pods -n syn-os-prod -l component=core

# Security services
kubectl get pods -n syn-os-security -l component=security

# View logs
kubectl logs -f deployment/prod-syn-os-core -n syn-os-prod
```

## Scaling

Manual scaling:

```bash
# Scale core deployment
kubectl scale deployment prod-syn-os-core --replicas=10 -n syn-os-prod

# Scale security deployment
kubectl scale deployment prod-syn-os-security-manager --replicas=5 -n syn-os-security
```

## Cleanup

Remove deployment:

```bash
# Development
kubectl delete -k deploy/kubernetes/overlays/development/

# Production
kubectl delete -k deploy/kubernetes/overlays/production/
```

## Security Considerations

- All containers run as non-root users
- Read-only root filesystems enabled
- Security contexts enforce strict policies
- Network policies isolate components
- RBAC controls access to resources

## Troubleshooting

### Common Issues

1. **ImagePullBackOff**: Verify image tags and registry access
2. **Pending Pods**: Check resource requests vs cluster capacity
3. **CrashLoopBackOff**: Review container logs and configuration

### Debug Commands

```bash
# Describe pod for detailed information
kubectl describe pod <pod-name> -n syn-os-prod

# Get events for troubleshooting
kubectl get events -n syn-os-prod --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n syn-os-prod
```

````bash

```bash
kubectl apply -k deploy/kubernetes/overlays/development
```text

```text

```text
```text

### Production Environment

```bash
```bash

```bash

```bash
kubectl apply -k deploy/kubernetes/overlays/production
```text

```text

```text
```text

### Base Resources Only

```bash
```bash

```bash

```bash
kubectl apply -k deploy/kubernetes/base
```text

```text

```text
```text

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
````
