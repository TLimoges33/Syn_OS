# Syn_OS Deployment Infrastructure

This directory contains comprehensive deployment configurations for Syn_OS across multiple environments and orchestration platforms.

## 🏗️ Infrastructure Overview

### Architecture

- **Kubernetes**: Production-ready container orchestration
- **Helm**: Package management and templating
- **Docker**: Containerization and local development
- **HAProxy**: Load balancing and ingress
- **Monitoring**: Prometheus-based observability

### Directory Structure

```text
deploy/
├── docker-compose.ha.yml          # High-availability Docker setup
├── haproxy/                       # Load balancer configuration
│   ├── haproxy.cfg               # HAProxy configuration
│   └── Dockerfile                # HAProxy container image
├── helm/                         # Helm chart for Kubernetes
│   └── syn-os/                   # Complete Helm chart
│       ├── Chart.yaml            # Chart metadata
│       ├── values.yaml           # Default configuration
│       └── templates/            # Kubernetes manifests
├── kubernetes/                   # Raw Kubernetes manifests
│   ├── base/                     # Base configurations
│   └── overlays/                 # Environment overlays
├── environments/                 # Environment-specific configs
│   ├── development.yaml          # Development settings
│   ├── staging.yaml             # Staging settings
│   └── production.yaml          # Production settings
├── monitoring/                   # Observability configuration
├── nats/                        # Message queue setup
└── scripts/                     # Deployment automation
    ├── deploy.sh                # Main deployment script
    └── health-check.sh          # Health monitoring
```

## 🚀 Quick Deployment

### Development Environment

```bash
# Using Helm (Recommended)
cd deploy
./scripts/deploy.sh development

# Using Kustomize
kubectl apply -k kubernetes/overlays/development/
```

### Production Environment

```bash
# Using Helm with production values
cd deploy
./scripts/deploy.sh production

# Using Kustomize
kubectl apply -k kubernetes/overlays/production/
```

### Local Development

```bash
# Docker Compose for local testing
docker-compose -f docker-compose.ha.yml up -d
```

## 🔧 Configuration Management

### Environment-Specific Configurations

Each environment has optimized settings:

- **Development**: Minimal resources, debug logging, single replicas
- **Staging**: Balanced resources, info logging, moderate replicas
- **Production**: Maximum resources, warn logging, high availability

### Helm Values Override

```bash
# Deploy with custom values
helm upgrade --install syn-os ./helm/syn-os \
    --namespace syn-os-prod \
    --values environments/production.yaml \
    --set core.logLevel=debug
```

## 📊 Monitoring & Observability

### Prometheus Integration

- Metrics collection from all components
- Custom dashboards for consciousness and security
- Alerting rules for critical events

### Health Checks

```bash
# Automated health monitoring
./scripts/health-check.sh

# Manual health verification
kubectl get pods -l app.kubernetes.io/name=syn-os
```

## 🔒 Security Configuration

### Multi-Layer Security

- **Network**: Zero-trust networking with service mesh
- **Container**: Non-root users, read-only filesystems
- **Access**: RBAC policies and service accounts
- **Data**: Encryption at rest and in transit

### Security Namespaces

- `syn-os`: Core application components
- `syn-os-security`: Security management services
- `syn-os-monitoring`: Observability infrastructure

## 🎯 High Availability

### Production Features

- **Auto-scaling**: HPA with CPU/memory targets
- **Load Balancing**: HAProxy with health checks
- **Data Persistence**: Persistent volumes with backup
- **Service Mesh**: Istio integration for resilience

### Disaster Recovery

- Multi-region deployment capability
- Automated backup and restore procedures
- Database replication and failover

## 🔄 CI/CD Integration

### GitOps Workflow

```bash
# Deploy from CI/CD pipeline
./scripts/deploy.sh ${ENVIRONMENT} \
    --set image.core.tag=${BUILD_VERSION} \
    --set image.security.tag=${BUILD_VERSION}
```

### Rollback Procedures

```bash
# Helm rollback
helm rollback syn-os-production 1 -n syn-os-prod

# Kubernetes rollback
kubectl rollout undo deployment/syn-os-core -n syn-os-prod
```

## 🛠️ Troubleshooting

### Common Issues

1. **Pod Startup Failures**: Check resource limits and image availability
2. **Service Discovery**: Verify network policies and DNS resolution
3. **Storage Issues**: Confirm PVC bindings and storage classes

### Debug Commands

```bash
# Comprehensive status check
kubectl get all -n syn-os-prod
kubectl describe pods -l app=syn-os-core
kubectl logs -f deployment/syn-os-core -n syn-os-prod

# Resource utilization
kubectl top pods -n syn-os-prod
kubectl top nodes
```

## 📚 Documentation References

- [Kubernetes Configuration](./kubernetes/README.md)
- [Helm Chart Documentation](./helm/syn-os/README.md)
- [Environment Configuration Guide](./environments/README.md)
- [Monitoring Setup](./monitoring/README.md)

## 🔧 Maintenance

### Regular Tasks

- Update container images
- Review and rotate secrets
- Monitor resource usage
- Test disaster recovery procedures

### Upgrade Process

1. Test in development environment
2. Deploy to staging for validation
3. Schedule production maintenance window
4. Execute rolling deployment
5. Verify functionality and performance

---

**Status**: ✅ **FULLY OPTIMIZED AND PRODUCTION-READY**

This deployment infrastructure supports enterprise-grade operations with comprehensive automation, monitoring, and security features.
