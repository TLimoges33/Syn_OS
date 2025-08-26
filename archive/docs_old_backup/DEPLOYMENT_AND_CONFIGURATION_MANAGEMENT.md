# SynapticOS Consciousness System V2 Deployment & Configuration Management
## Complete Infrastructure Automation and Deployment Guide

### Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Infrastructure as Code](#infrastructure-as-code)
3. [Container Orchestration](#container-orchestration)
4. [Configuration Management](#configuration-management)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Environment Management](#environment-management)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Security and Compliance](#security-and-compliance)
9. [Disaster Recovery](#disaster-recovery)
10. [Operational Procedures](#operational-procedures)

- --

## Deployment Architecture

### Multi-Environment Strategy

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_LB[Load Balancer]
        DEV_APP[App Servers]
        DEV_DB[(Database)]
    end

    subgraph "Staging Environment"
        STAGE_LB[Load Balancer]
        STAGE_APP[App Servers]
        STAGE_DB[(Database)]
    end

    subgraph "Production Environment"
        PROD_LB[Load Balancer]
        PROD_APP[App Servers x3]
        PROD_DB[(Primary DB)]
        PROD_DB_REPLICA[(Read Replicas)]
    end

    DEV_APP --> STAGE_APP
    STAGE_APP --> PROD_APP
```text
    end

    subgraph "Staging Environment"
        STAGE_LB[Load Balancer]
        STAGE_APP[App Servers]
        STAGE_DB[(Database)]
    end

    subgraph "Production Environment"
        PROD_LB[Load Balancer]
        PROD_APP[App Servers x3]
        PROD_DB[(Primary DB)]
        PROD_DB_REPLICA[(Read Replicas)]
    end

    DEV_APP --> STAGE_APP
    STAGE_APP --> PROD_APP

```text

### Cloud Infrastructure Design

#### AWS Architecture

```yaml
```yaml

## infrastructure/aws/main.tf

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

## VPC Configuration

resource "aws_vpc" "consciousness_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "consciousness-vpc"
    Environment = var.environment
    Project     = "synapticos-consciousness"
  }
}

## Subnets

resource "aws_subnet" "public_subnets" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.consciousness_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "consciousness-public-${count.index + 1}"
    Type = "public"
  }
}

resource "aws_subnet" "private_subnets" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.consciousness_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "consciousness-private-${count.index + 1}"
    Type = "private"
  }
}

## EKS Cluster

resource "aws_eks_cluster" "consciousness_cluster" {
  name     = "consciousness-cluster-${var.environment}"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.allowed_cidr_blocks
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_encryption.arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]
}

## RDS Database

resource "aws_db_instance" "consciousness_db" {
  identifier = "consciousness-db-${var.environment}"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds_encryption.arn

  db_name  = "consciousness"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.consciousness_db_subnet_group.name

  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = var.environment != "production"
  deletion_protection = var.environment == "production"

  performance_insights_enabled = true
  monitoring_interval         = 60
  monitoring_role_arn        = aws_iam_role.rds_monitoring_role.arn

  tags = {
    Name        = "consciousness-db"
    Environment = var.environment
  }
}

## ElastiCache Redis

resource "aws_elasticache_replication_group" "consciousness_redis" {
  replication_group_id       = "consciousness-redis-${var.environment}"
  description                = "Redis cluster for consciousness system"

  node_type                  = var.redis_node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"

  num_cache_clusters         = var.environment == "production" ? 3 : 1
  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled          = var.environment == "production"

  subnet_group_name = aws_elasticache_subnet_group.consciousness_redis_subnet_group.name
  security_group_ids = [aws_security_group.redis_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }

  tags = {
    Name        = "consciousness-redis"
    Environment = var.environment
  }
}
```text
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

## VPC Configuration

resource "aws_vpc" "consciousness_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "consciousness-vpc"
    Environment = var.environment
    Project     = "synapticos-consciousness"
  }
}

## Subnets

resource "aws_subnet" "public_subnets" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.consciousness_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "consciousness-public-${count.index + 1}"
    Type = "public"
  }
}

resource "aws_subnet" "private_subnets" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.consciousness_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "consciousness-private-${count.index + 1}"
    Type = "private"
  }
}

## EKS Cluster

resource "aws_eks_cluster" "consciousness_cluster" {
  name     = "consciousness-cluster-${var.environment}"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.allowed_cidr_blocks
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_encryption.arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]
}

## RDS Database

resource "aws_db_instance" "consciousness_db" {
  identifier = "consciousness-db-${var.environment}"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds_encryption.arn

  db_name  = "consciousness"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.consciousness_db_subnet_group.name

  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = var.environment != "production"
  deletion_protection = var.environment == "production"

  performance_insights_enabled = true
  monitoring_interval         = 60
  monitoring_role_arn        = aws_iam_role.rds_monitoring_role.arn

  tags = {
    Name        = "consciousness-db"
    Environment = var.environment
  }
}

## ElastiCache Redis

resource "aws_elasticache_replication_group" "consciousness_redis" {
  replication_group_id       = "consciousness-redis-${var.environment}"
  description                = "Redis cluster for consciousness system"

  node_type                  = var.redis_node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"

  num_cache_clusters         = var.environment == "production" ? 3 : 1
  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled          = var.environment == "production"

  subnet_group_name = aws_elasticache_subnet_group.consciousness_redis_subnet_group.name
  security_group_ids = [aws_security_group.redis_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }

  tags = {
    Name        = "consciousness-redis"
    Environment = var.environment
  }
}

```text

- --

## Infrastructure as Code

### Terraform Modules Structure

```text

### Terraform Modules Structure

```text
infrastructure/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── development/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
└── shared/
    ├── backend.tf
    ├── providers.tf
    └── variables.tf
```text
│   │   └── outputs.tf
│   ├── eks/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── development/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
└── shared/
    ├── backend.tf
    ├── providers.tf
    └── variables.tf

```text

### Environment-Specific Configurations

#### Production Environment

```hcl
```hcl

## infrastructure/environments/production/terraform.tfvars

environment = "production"
region      = "us-west-2"

## VPC Configuration

availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
allowed_cidr_blocks = ["10.0.0.0/8"]

## EKS Configuration

eks_node_groups = {
  consciousness_nodes = {
    instance_types = ["m5.xlarge"]
    min_size      = 3
    max_size      = 10
    desired_size  = 5
  }
  gpu_nodes = {
    instance_types = ["p3.2xlarge"]
    min_size      = 1
    max_size      = 3
    desired_size  = 2
  }
}

## Database Configuration

db_instance_class      = "db.r6g.xlarge"
db_allocated_storage   = 500
db_max_allocated_storage = 2000

## Redis Configuration

redis_node_type = "cache.r6g.large"

## Monitoring

enable_detailed_monitoring = true
log_retention_days        = 30
```text

## VPC Configuration

availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
allowed_cidr_blocks = ["10.0.0.0/8"]

## EKS Configuration

eks_node_groups = {
  consciousness_nodes = {
    instance_types = ["m5.xlarge"]
    min_size      = 3
    max_size      = 10
    desired_size  = 5
  }
  gpu_nodes = {
    instance_types = ["p3.2xlarge"]
    min_size      = 1
    max_size      = 3
    desired_size  = 2
  }
}

## Database Configuration

db_instance_class      = "db.r6g.xlarge"
db_allocated_storage   = 500
db_max_allocated_storage = 2000

## Redis Configuration

redis_node_type = "cache.r6g.large"

## Monitoring

enable_detailed_monitoring = true
log_retention_days        = 30

```text

#### Development Environment

```hcl
```hcl

## infrastructure/environments/development/terraform.tfvars

environment = "development"
region      = "us-west-2"

## VPC Configuration

availability_zones = ["us-west-2a", "us-west-2b"]
allowed_cidr_blocks = ["0.0.0.0/0"]

## EKS Configuration

eks_node_groups = {
  consciousness_nodes = {
    instance_types = ["t3.medium"]
    min_size      = 1
    max_size      = 3
    desired_size  = 2
  }
}

## Database Configuration

db_instance_class      = "db.t3.micro"
db_allocated_storage   = 20
db_max_allocated_storage = 100

## Redis Configuration

redis_node_type = "cache.t3.micro"

## Monitoring

enable_detailed_monitoring = false
log_retention_days        = 7
```text

## VPC Configuration

availability_zones = ["us-west-2a", "us-west-2b"]
allowed_cidr_blocks = ["0.0.0.0/0"]

## EKS Configuration

eks_node_groups = {
  consciousness_nodes = {
    instance_types = ["t3.medium"]
    min_size      = 1
    max_size      = 3
    desired_size  = 2
  }
}

## Database Configuration

db_instance_class      = "db.t3.micro"
db_allocated_storage   = 20
db_max_allocated_storage = 100

## Redis Configuration

redis_node_type = "cache.t3.micro"

## Monitoring

enable_detailed_monitoring = false
log_retention_days        = 7

```text

- --

## Container Orchestration

### Kubernetes Manifests

#### Namespace and RBAC

```yaml
### Kubernetes Manifests

#### Namespace and RBAC

```yaml

## k8s/base/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: consciousness-system
  labels:
    name: consciousness-system
    istio-injection: enabled

- --
apiVersion: v1
kind: ServiceAccount
metadata:
  name: consciousness-service-account
  namespace: consciousness-system

- --
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: consciousness-cluster-role
rules:

- apiGroups: [""]

  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]

- apiGroups: ["apps"]

  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]

- --
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: consciousness-cluster-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: consciousness-cluster-role
subjects:

- kind: ServiceAccount

  name: consciousness-service-account
  namespace: consciousness-system
```text
metadata:
  name: consciousness-system
  labels:
    name: consciousness-system
    istio-injection: enabled

- --
apiVersion: v1
kind: ServiceAccount
metadata:
  name: consciousness-service-account
  namespace: consciousness-system

- --
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: consciousness-cluster-role
rules:

- apiGroups: [""]

  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]

- apiGroups: ["apps"]

  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]

- --
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: consciousness-cluster-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: consciousness-cluster-role
subjects:

- kind: ServiceAccount

  name: consciousness-service-account
  namespace: consciousness-system

```text

#### Consciousness Bus Deployment

```yaml
```yaml

## k8s/base/consciousness-bus.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: consciousness-bus
  namespace: consciousness-system
  labels:
    app: consciousness-bus
    component: core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: consciousness-bus
  template:
    metadata:
      labels:
        app: consciousness-bus
        component: core
    spec:
      serviceAccountName: consciousness-service-account
      containers:

      - name: consciousness-bus

        image: synapticos/consciousness-bus:v2.0
        ports:

        - containerPort: 8080

          name: http

        - containerPort: 8443

          name: https

        - containerPort: 9090

          name: metrics
        env:

        - name: CONSCIOUSNESS_BUS_PORT

          value: "8080"

        - name: CONSCIOUSNESS_BUS_TLS_PORT

          value: "8443"

        - name: DATABASE_URL

          valueFrom:
            secretKeyRef:
              name: consciousness-secrets
              key: database-url

        - name: REDIS_URL

          valueFrom:
            secretKeyRef:
              name: consciousness-secrets
              key: redis-url

        - name: LOG_LEVEL

          valueFrom:
            configMapKeyRef:
              name: consciousness-config
              key: log-level
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:

        - name: config-volume

          mountPath: /app/config

        - name: certs-volume

          mountPath: /app/certs
      volumes:

      - name: config-volume

        configMap:
          name: consciousness-config

      - name: certs-volume

        secret:
          secretName: consciousness-tls-certs

- --
apiVersion: v1
kind: Service
metadata:
  name: consciousness-bus-service
  namespace: consciousness-system
  labels:
    app: consciousness-bus
spec:
  selector:
    app: consciousness-bus
  ports:

  - name: http

    port: 8080
    targetPort: 8080

  - name: https

    port: 8443
    targetPort: 8443

  - name: metrics

    port: 9090
    targetPort: 9090
  type: ClusterIP
```text
metadata:
  name: consciousness-bus
  namespace: consciousness-system
  labels:
    app: consciousness-bus
    component: core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: consciousness-bus
  template:
    metadata:
      labels:
        app: consciousness-bus
        component: core
    spec:
      serviceAccountName: consciousness-service-account
      containers:

      - name: consciousness-bus

        image: synapticos/consciousness-bus:v2.0
        ports:

        - containerPort: 8080

          name: http

        - containerPort: 8443

          name: https

        - containerPort: 9090

          name: metrics
        env:

        - name: CONSCIOUSNESS_BUS_PORT

          value: "8080"

        - name: CONSCIOUSNESS_BUS_TLS_PORT

          value: "8443"

        - name: DATABASE_URL

          valueFrom:
            secretKeyRef:
              name: consciousness-secrets
              key: database-url

        - name: REDIS_URL

          valueFrom:
            secretKeyRef:
              name: consciousness-secrets
              key: redis-url

        - name: LOG_LEVEL

          valueFrom:
            configMapKeyRef:
              name: consciousness-config
              key: log-level
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:

        - name: config-volume

          mountPath: /app/config

        - name: certs-volume

          mountPath: /app/certs
      volumes:

      - name: config-volume

        configMap:
          name: consciousness-config

      - name: certs-volume

        secret:
          secretName: consciousness-tls-certs

- --
apiVersion: v1
kind: Service
metadata:
  name: consciousness-bus-service
  namespace: consciousness-system
  labels:
    app: consciousness-bus
spec:
  selector:
    app: consciousness-bus
  ports:

  - name: http

    port: 8080
    targetPort: 8080

  - name: https

    port: 8443
    targetPort: 8443

  - name: metrics

    port: 9090
    targetPort: 9090
  type: ClusterIP

```text

#### Neural Darwinism Engine Deployment

```yaml
```yaml

## k8s/base/neural-darwinism-engine.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: neural-darwinism-engine
  namespace: consciousness-system
  labels:
    app: neural-darwinism-engine
    component: intelligence
spec:
  replicas: 2
  selector:
    matchLabels:
      app: neural-darwinism-engine
  template:
    metadata:
      labels:
        app: neural-darwinism-engine
        component: intelligence
    spec:
      serviceAccountName: consciousness-service-account
      nodeSelector:
        node-type: gpu-enabled
      containers:

      - name: neural-darwinism-engine

        image: synapticos/neural-darwinism:v2.0
        env:

        - name: CONSCIOUSNESS_BUS_URL

          value: "http://consciousness-bus-service:8080"

        - name: GPU_ACCELERATION

          value: "true"

        - name: POPULATION_SIZE

          valueFrom:
            configMapKeyRef:
              name: consciousness-config
              key: neural-population-size
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```text
metadata:
  name: neural-darwinism-engine
  namespace: consciousness-system
  labels:
    app: neural-darwinism-engine
    component: intelligence
spec:
  replicas: 2
  selector:
    matchLabels:
      app: neural-darwinism-engine
  template:
    metadata:
      labels:
        app: neural-darwinism-engine
        component: intelligence
    spec:
      serviceAccountName: consciousness-service-account
      nodeSelector:
        node-type: gpu-enabled
      containers:

      - name: neural-darwinism-engine

        image: synapticos/neural-darwinism:v2.0
        env:

        - name: CONSCIOUSNESS_BUS_URL

          value: "http://consciousness-bus-service:8080"

        - name: GPU_ACCELERATION

          value: "true"

        - name: POPULATION_SIZE

          valueFrom:
            configMapKeyRef:
              name: consciousness-config
              key: neural-population-size
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10

```text

### Helm Charts

#### Chart Structure

```text

```text
helm/consciousness-system/
├── Chart.yaml
├── values.yaml
├── values-production.yaml
├── values-development.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   └── pdb.yaml
└── charts/
    ├── postgresql/
    ├── redis/
    └── monitoring/
```text
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   └── pdb.yaml
└── charts/
    ├── postgresql/
    ├── redis/
    └── monitoring/

```text

#### Helm Values

```yaml
```yaml

## helm/consciousness-system/values.yaml

global:
  imageRegistry: "synapticos"
  imageTag: "v2.0"
  environment: "production"

consciousnessBus:
  replicaCount: 3
  image:
    repository: consciousness-bus
    tag: v2.0
  service:
    type: ClusterIP
    port: 8080
    tlsPort: 8443
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

neuralDarwinismEngine:
  replicaCount: 2
  image:
    repository: neural-darwinism
    tag: v2.0
  nodeSelector:
    node-type: gpu-enabled
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"
      nvidia.com/gpu: 1
    limits:
      memory: "4Gi"
      cpu: "2000m"
      nvidia.com/gpu: 1

personalContextEngine:
  replicaCount: 2
  image:
    repository: personal-context
    tag: v2.0
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

securityTutor:
  replicaCount: 2
  image:
    repository: security-tutor
    tag: v2.0
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

lmStudioIntegration:
  replicaCount: 1
  image:
    repository: lm-studio-integration
    tag: v2.0
  resources:
    requests:
      memory: "4Gi"
      cpu: "2000m"
    limits:
      memory: "8Gi"
      cpu: "4000m"

postgresql:
  enabled: true
  auth:
    postgresPassword: "consciousness-db-password"
    database: "consciousness"
  primary:
    persistence:
      enabled: true
      size: 100Gi
      storageClass: "gp3"

redis:
  enabled: true
  auth:
    enabled: true
    password: "consciousness-redis-password"
  master:
    persistence:
      enabled: true
      size: 20Gi
      storageClass: "gp3"

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
  jaeger:
    enabled: true
```text
  imageTag: "v2.0"
  environment: "production"

consciousnessBus:
  replicaCount: 3
  image:
    repository: consciousness-bus
    tag: v2.0
  service:
    type: ClusterIP
    port: 8080
    tlsPort: 8443
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

neuralDarwinismEngine:
  replicaCount: 2
  image:
    repository: neural-darwinism
    tag: v2.0
  nodeSelector:
    node-type: gpu-enabled
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"
      nvidia.com/gpu: 1
    limits:
      memory: "4Gi"
      cpu: "2000m"
      nvidia.com/gpu: 1

personalContextEngine:
  replicaCount: 2
  image:
    repository: personal-context
    tag: v2.0
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

securityTutor:
  replicaCount: 2
  image:
    repository: security-tutor
    tag: v2.0
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

lmStudioIntegration:
  replicaCount: 1
  image:
    repository: lm-studio-integration
    tag: v2.0
  resources:
    requests:
      memory: "4Gi"
      cpu: "2000m"
    limits:
      memory: "8Gi"
      cpu: "4000m"

postgresql:
  enabled: true
  auth:
    postgresPassword: "consciousness-db-password"
    database: "consciousness"
  primary:
    persistence:
      enabled: true
      size: 100Gi
      storageClass: "gp3"

redis:
  enabled: true
  auth:
    enabled: true
    password: "consciousness-redis-password"
  master:
    persistence:
      enabled: true
      size: 20Gi
      storageClass: "gp3"

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
  jaeger:
    enabled: true

```text

- --

## Configuration Management

### Ansible Playbooks

#### Main Playbook

```yaml
### Ansible Playbooks

#### Main Playbook

```yaml

## ansible/site.yml

- --

- name: Deploy SynapticOS Consciousness System

  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    environment: "{{ env | default('development') }}"
    namespace: "consciousness-system"

  tasks:

    - name: Include environment-specific variables

      include_vars: "vars/{{ environment }}.yml"

    - name: Create namespace

      kubernetes.core.k8s:
        name: "{{ namespace }}"
        api_version: v1
        kind: Namespace
        state: present

    - name: Deploy consciousness system using Helm

      kubernetes.core.helm:
        name: consciousness-system
        chart_ref: ./helm/consciousness-system
        release_namespace: "{{ namespace }}"
        values: "{{ consciousness_values }}"
        wait: true
        timeout: 600s

    - name: Wait for all deployments to be ready

      kubernetes.core.k8s_info:
        api_version: apps/v1
        kind: Deployment
        namespace: "{{ namespace }}"
        wait: true
        wait_condition:
          type: Available
          status: "True"
        wait_timeout: 600

- name: Configure monitoring and alerting

  import_playbook: monitoring.yml

- name: Run post-deployment tests

  import_playbook: tests.yml
```text
- name: Deploy SynapticOS Consciousness System

  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    environment: "{{ env | default('development') }}"
    namespace: "consciousness-system"

  tasks:

    - name: Include environment-specific variables

      include_vars: "vars/{{ environment }}.yml"

    - name: Create namespace

      kubernetes.core.k8s:
        name: "{{ namespace }}"
        api_version: v1
        kind: Namespace
        state: present

    - name: Deploy consciousness system using Helm

      kubernetes.core.helm:
        name: consciousness-system
        chart_ref: ./helm/consciousness-system
        release_namespace: "{{ namespace }}"
        values: "{{ consciousness_values }}"
        wait: true
        timeout: 600s

    - name: Wait for all deployments to be ready

      kubernetes.core.k8s_info:
        api_version: apps/v1
        kind: Deployment
        namespace: "{{ namespace }}"
        wait: true
        wait_condition:
          type: Available
          status: "True"
        wait_timeout: 600

- name: Configure monitoring and alerting

  import_playbook: monitoring.yml

- name: Run post-deployment tests

  import_playbook: tests.yml

```text

#### Environment Configuration

```yaml
```yaml

## ansible/vars/production.yml

consciousness_values:
  global:
    environment: production
    imageTag: v2.0

  consciousnessBus:
    replicaCount: 5
    autoscaling:
      enabled: true
      minReplicas: 5
      maxReplicas: 20
      targetCPUUtilizationPercentage: 60

  neuralDarwinismEngine:
    replicaCount: 3
    nodeSelector:
      node-type: gpu-enabled

  postgresql:
    primary:
      persistence:
        size: 500Gi
      resources:
        requests:
          memory: "4Gi"
          cpu: "2000m"
        limits:
          memory: "8Gi"
          cpu: "4000m"

  redis:
    master:
      persistence:
        size: 100Gi
      resources:
        requests:
          memory: "2Gi"
          cpu: "1000m"
        limits:
          memory: "4Gi"
          cpu: "2000m"

  monitoring:
    prometheus:
      enabled: true
      retention: "30d"
      storage: "100Gi"
    grafana:
      enabled: true
      persistence:
        enabled: true
        size: "10Gi"
```text
    environment: production
    imageTag: v2.0

  consciousnessBus:
    replicaCount: 5
    autoscaling:
      enabled: true
      minReplicas: 5
      maxReplicas: 20
      targetCPUUtilizationPercentage: 60

  neuralDarwinismEngine:
    replicaCount: 3
    nodeSelector:
      node-type: gpu-enabled

  postgresql:
    primary:
      persistence:
        size: 500Gi
      resources:
        requests:
          memory: "4Gi"
          cpu: "2000m"
        limits:
          memory: "8Gi"
          cpu: "4000m"

  redis:
    master:
      persistence:
        size: 100Gi
      resources:
        requests:
          memory: "2Gi"
          cpu: "1000m"
        limits:
          memory: "4Gi"
          cpu: "2000m"

  monitoring:
    prometheus:
      enabled: true
      retention: "30d"
      storage: "100Gi"
    grafana:
      enabled: true
      persistence:
        enabled: true
        size: "10Gi"

```text

### Configuration Templates

#### Application Configuration

```yaml
```yaml

## config/templates/consciousness-config.yaml.j2

apiVersion: v1
kind: ConfigMap
metadata:
  name: consciousness-config
  namespace: {{ namespace }}
data:
  log-level: "{{ log_level | default('INFO') }}"
  neural-population-size: "{{ neural_population_size | default('1000') }}"
  consciousness-bus-config: |
    host: "0.0.0.0"
    port: 8080
    tls_port: 8443
    max_connections: {{ max_connections | default('1000') }}
    event_queue_size: {{ event_queue_size | default('10000') }}
    heartbeat_interval: {{ heartbeat_interval | default('30') }}
    component_timeout: {{ component_timeout | default('60') }}
    enable_tls: {{ enable_tls | default('true') }}

  neural-darwinism-config: |
    population_size: {{ neural_population_size | default('1000') }}
    mutation_rate: {{ mutation_rate | default('0.1') }}
    selection_pressure: {{ selection_pressure | default('0.3') }}
    evolution_frequency: {{ evolution_frequency | default('300') }}
    gpu_acceleration: {{ gpu_acceleration | default('true') }}

  personal-context-config: |
    max_user_contexts: {{ max_user_contexts | default('10000') }}
    context_cache_size: {{ context_cache_size | default('1000') }}
    skill_assessment_interval: {{ skill_assessment_interval | default('86400') }}

  security-tutor-config: |
    threat_scenario_pool_size: {{ threat_scenario_pool_size | default('500') }}
    adaptive_difficulty: {{ adaptive_difficulty | default('true') }}
    security_assessment_frequency: {{ security_assessment_frequency | default('7200') }}

  monitoring-config: |
    enable_metrics: {{ enable_metrics | default('true') }}
    metrics_port: {{ metrics_port | default('9090') }}
    enable_tracing: {{ enable_tracing | default('true') }}
    log_retention_days: {{ log_retention_days | default('30') }}
```text
metadata:
  name: consciousness-config
  namespace: {{ namespace }}
data:
  log-level: "{{ log_level | default('INFO') }}"
  neural-population-size: "{{ neural_population_size | default('1000') }}"
  consciousness-bus-config: |
    host: "0.0.0.0"
    port: 8080
    tls_port: 8443
    max_connections: {{ max_connections | default('1000') }}
    event_queue_size: {{ event_queue_size | default('10000') }}
    heartbeat_interval: {{ heartbeat_interval | default('30') }}
    component_timeout: {{ component_timeout | default('60') }}
    enable_tls: {{ enable_tls | default('true') }}

  neural-darwinism-config: |
    population_size: {{ neural_population_size | default('1000') }}
    mutation_rate: {{ mutation_rate | default('0.1') }}
    selection_pressure: {{ selection_pressure | default('0.3') }}
    evolution_frequency: {{ evolution_frequency | default('300') }}
    gpu_acceleration: {{ gpu_acceleration | default('true') }}

  personal-context-config: |
    max_user_contexts: {{ max_user_contexts | default('10000') }}
    context_cache_size: {{ context_cache_size | default('1000') }}
    skill_assessment_interval: {{ skill_assessment_interval | default('86400') }}

  security-tutor-config: |
    threat_scenario_pool_size: {{ threat_scenario_pool_size | default('500') }}
    adaptive_difficulty: {{ adaptive_difficulty | default('true') }}
    security_assessment_frequency: {{ security_assessment_frequency | default('7200') }}

  monitoring-config: |
    enable_metrics: {{ enable_metrics | default('true') }}
    metrics_port: {{ metrics_port | default('9090') }}
    enable_tracing: {{ enable_tracing | default('true') }}
    log_retention_days: {{ log_retention_days | default('30') }}

```text

- --

## CI/CD Pipeline

### GitHub Actions Workflow

#### Main Deployment Pipeline

```yaml
### GitHub Actions Workflow

#### Main Deployment Pipeline

```yaml

## .github/workflows/deploy.yml

name: Deploy Consciousness System

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: synapticos/consciousness

jobs:
  test:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4

      - name: Set up Python

        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies

        run: |
          pip install -r requirements.txt
          pip install -r test-requirements.txt

      - name: Run unit tests

        run: |
          python -m pytest tests/unit/ -v --cov=src --cov-report=xml

      - name: Run integration tests

        run: |
          python -m pytest tests/integration/ -v

      - name: Upload coverage reports

        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4

      - name: Run security scan

        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: 'security-scan-results.sarif'

      - name: Run dependency check

        run: |
          pip install safety
          safety check --json --output safety-report.json

  build:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [consciousness-bus, neural-darwinism, personal-context, security-tutor, lm-studio-integration]

    steps:

      - uses: actions/checkout@v4

      - name: Set up Docker Buildx

        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry

        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata

        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.component }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image

        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/${{ matrix.component }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:

      - uses: actions/checkout@v4

      - name: Configure AWS credentials

        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Update kubeconfig

        run: |
          aws eks update-kubeconfig --region us-west-2 --name consciousness-cluster-staging

      - name: Deploy to staging

        run: |
          helm upgrade --install consciousness-system ./helm/consciousness-system \
            - -namespace consciousness-system \
            - -create-namespace \
            - -values ./helm/consciousness-system/values-staging.yaml \
            - -set global.imageTag=${{ github.sha }} \
            - -wait --timeout=600s

      - name: Run smoke tests

        run: |
          python -m pytest tests/smoke/ -v --environment=staging

  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:

      - uses: actions/checkout@v4

      - name: Configure AWS credentials

        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Update kubeconfig

        run: |
          aws eks update-kubeconfig --region us-west-2 --name consciousness-cluster-production

      - name: Deploy to production

        run: |
          helm upgrade --install consciousness-system ./helm/consciousness-system \
            - -namespace consciousness-system \
            - -create-namespace \
            - -values ./helm/consciousness-system/values-production.yaml \
            - -set global.imageTag=${{ github.sha }} \
            - -wait --timeout=600s

      - name: Run production health checks

        run: |
          python -m pytest tests/health/ -v --environment=production

      - name: Notify deployment success

        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "Consciousness System v${{ github.sha }} deployed to production successfully!"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```text
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: synapticos/consciousness

jobs:
  test:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4

      - name: Set up Python

        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies

        run: |
          pip install -r requirements.txt
          pip install -r test-requirements.txt

      - name: Run unit tests

        run: |
          python -m pytest tests/unit/ -v --cov=src --cov-report=xml

      - name: Run integration tests

        run: |
          python -m pytest tests/integration/ -v

      - name: Upload coverage reports

        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4

      - name: Run security scan

        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: 'security-scan-results.sarif'

      - name: Run dependency check

        run: |
          pip install safety
          safety check --json --output safety-report.json

  build:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [consciousness-bus, neural-darwinism, personal-context, security-tutor, lm-studio-integration]

    steps:

      - uses: actions/checkout@v4

      - name: Set up Docker Buildx

        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry

        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata

        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.component }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image

        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./docker/${{ matrix.component }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:

      - uses: actions/checkout@v4

      - name: Configure AWS credentials

        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Update kubeconfig

        run: |
          aws eks update-kubeconfig --region us-west-2 --name consciousness-cluster-staging

      - name: Deploy to staging

        run: |
          helm upgrade --install consciousness-system ./helm/consciousness-system \
            - -namespace consciousness-system \
            - -create-namespace \
            - -values ./helm/consciousness-system/values-staging.yaml \
            - -set global.imageTag=${{ github.sha }} \
            - -wait --timeout=600s

      - name: Run smoke tests

        run: |
          python -m pytest tests/smoke/ -v --environment=staging

  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:

      - uses: actions/checkout@v4

      - name: Configure AWS credentials

        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Update kubeconfig

        run: |
          aws eks update-kubeconfig --region us-west-2 --name consciousness-cluster-production

      - name: Deploy to production

        run: |
          helm upgrade --install consciousness-system ./helm/consciousness-system \
            - -namespace consciousness-system \
            - -create-namespace \
            - -values ./helm/consciousness-system/values-production.yaml \
            - -set global.imageTag=${{ github.sha }} \
            - -wait --timeout=600s

      - name: Run production health checks

        run: |
          python -m pytest tests/health/ -v --environment=production

      - name: Notify deployment success

        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "Consciousness System v${{ github.sha }} deployed to production successfully!"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

```text

### GitLab CI/CD Pipeline

```yaml
```yaml

## .gitlab-ci.yml

stages:

  - test
  - security
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_REGISTRY: registry.gitlab.com
  PROJECT_PATH: synapticos/consciousness-system

test:
  stage: test
  image: python:3.11
  script:

    - pip install -r requirements.txt -r test-requirements.txt
    - python -m pytest tests/ -v --cov=src --cov-report=xml
    - python -m pytest tests/integration/ -v

  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

security-scan:
  stage: security
  image: securecodewarrior/gitlab-sast:latest
  script:

    - sast-scan --format gitlab-sast --output gl-sast-report.json

  artifacts:
    reports:
      sast: gl-sast-report.json

.build-template: &build-template
  stage: build
  image: docker:latest
  services:

    - docker:dind

  before_script:

    - docker login
  - test
  - security
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_REGISTRY: registry.gitlab.com
  PROJECT_PATH: synapticos/consciousness-system

test:
  stage: test
  image: python:3.11
  script:

    - pip install -r requirements.txt -r test-requirements.txt
    - python -m pytest tests/ -v --cov=src --cov-report=xml
    - python -m pytest tests/integration/ -v

  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

security-scan:
  stage: security
  image: securecodewarrior/gitlab-sast:latest
  script:

    - sast-scan --format gitlab-sast --output gl-sast-report.json

  artifacts:
    reports:
      sast: gl-sast-report.json

.build-template: &build-template
  stage: build
  image: docker:latest
  services:

    - docker:dind

  before_script:

    - docker login