# ☸️ Kubernetes Deployment

**For**: K8s Administrators  
**Prerequisites**: Kubernetes cluster, kubectl, Helm

Deploy SynOS to Kubernetes for scalability and orchestration.

---

## Quick Start

```bash
# Add Helm repo
helm repo add synos https://charts.synos.dev
helm repo update

# Install
helm install synos synos/synos \
  --namespace synos \
  --create-namespace

# Check status
kubectl get pods -n synos
```

---

## Manual Deployment

### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: synos
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synos
  namespace: synos
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synos
  template:
    metadata:
      labels:
        app: synos
    spec:
      containers:
      - name: synos
        image: synos/synos:latest
        ports:
        - containerPort: 80
        env:
        - name: SYNOS_DB_HOST
          value: postgres-service
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: synos-service
  namespace: synos
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
    name: http
  - port: 443
    targetPort: 443
    name: https
  selector:
    app: synos
```

### Apply

```bash
kubectl apply -f namespace.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## Helm Chart

### values.yaml

```yaml
replicaCount: 3

image:
  repository: synos/synos
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  httpsPort: 443

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: synos.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: synos-tls
      hosts:
        - synos.example.com

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    username: synos
    password: changeme
    database: synos

redis:
  enabled: true
```

### Install

```bash
helm install synos synos/synos -f values.yaml
```

---

## Scaling

```bash
# Manual scaling
kubectl scale deployment synos --replicas=5 -n synos

# Autoscaling
kubectl autoscale deployment synos \
  --min=3 --max=10 \
  --cpu-percent=80 \
  -n synos
```

---

## Monitoring

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: synos
  namespace: synos
spec:
  selector:
    matchLabels:
      app: synos
  endpoints:
  - port: metrics
```

---

**Last Updated**: October 4, 2025
