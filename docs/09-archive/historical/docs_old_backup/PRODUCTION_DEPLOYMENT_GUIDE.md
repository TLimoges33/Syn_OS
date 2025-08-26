# Syn_OS Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Syn_OS consciousness-aware infrastructure platform in
production environments. The system combines AI consciousness with service orchestration to create an adaptive,
intelligent infrastructure platform.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Syn_OS Production Architecture                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Web Dashboard │    │  Security Tutor │    │  CLI Tools   │ │
│  │   (Port 8083)   │    │   (Port 8082)   │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Service Orchestrator                        │ │
│  │                   (Port 8080)                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Service   │  │   Health    │  │    Consciousness    │ │ │
│  │  │  Registry   │  │   Monitor   │  │      Bridge         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  NATS JetStream │    │   PostgreSQL    │    │    Redis     │ │
│  │   (Port 4222)   │    │   (Port 5432)   │    │ (Port 6379)  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Consciousness System v2                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Kernel    │  │  Cognitive  │  │    Persistence      │ │ │
│  │  │   Hooks     │  │  Framework  │  │     Manager         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```text

│  │   (Port 8083)   │    │   (Port 8082)   │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Service Orchestrator                        │ │
│  │                   (Port 8080)                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Service   │  │   Health    │  │    Consciousness    │ │ │
│  │  │  Registry   │  │   Monitor   │  │      Bridge         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  NATS JetStream │    │   PostgreSQL    │    │    Redis     │ │
│  │   (Port 4222)   │    │   (Port 5432)   │    │ (Port 6379)  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Consciousness System v2                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Kernel    │  │  Cognitive  │  │    Persistence      │ │ │
│  │  │   Hooks     │  │  Framework  │  │     Manager         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

```text
│  │   (Port 8083)   │    │   (Port 8082)   │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Service Orchestrator                        │ │
│  │                   (Port 8080)                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Service   │  │   Health    │  │    Consciousness    │ │ │
│  │  │  Registry   │  │   Monitor   │  │      Bridge         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  NATS JetStream │    │   PostgreSQL    │    │    Redis     │ │
│  │   (Port 4222)   │    │   (Port 5432)   │    │ (Port 6379)  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Consciousness System v2                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Kernel    │  │  Cognitive  │  │    Persistence      │ │ │
│  │  │   Hooks     │  │  Framework  │  │     Manager         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

```text
│  │                   (Port 8080)                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Service   │  │   Health    │  │    Consciousness    │ │ │
│  │  │  Registry   │  │   Monitor   │  │      Bridge         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                       │                      │       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  NATS JetStream │    │   PostgreSQL    │    │    Redis     │ │
│  │   (Port 4222)   │    │   (Port 5432)   │    │ (Port 6379)  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Consciousness System v2                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Kernel    │  │  Cognitive  │  │    Persistence      │ │ │
│  │  │   Hooks     │  │  Framework  │  │     Manager         │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

```text

## Prerequisites

### System Requirements

- **Operating System**: ParrotOS 5.3+ (recommended) or Ubuntu 20.04+
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for initial setup

### Software Dependencies

- Docker 24.0+
- Docker Compose 2.20+
- Go 1.21+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- NATS Server 2.10+

## Quick Start Deployment

### Option 1: Automated ParrotOS Deployment

For ParrotOS systems, use the automated deployment script:

```bash
- **Operating System**: ParrotOS 5.3+ (recommended) or Ubuntu 20.04+
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for initial setup

### Software Dependencies

- Docker 24.0+
- Docker Compose 2.20+
- Go 1.21+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- NATS Server 2.10+

## Quick Start Deployment

### Option 1: Automated ParrotOS Deployment

For ParrotOS systems, use the automated deployment script:

```bash

- **Operating System**: ParrotOS 5.3+ (recommended) or Ubuntu 20.04+
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for initial setup

### Software Dependencies

- Docker 24.0+
- Docker Compose 2.20+
- Go 1.21+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- NATS Server 2.10+

## Quick Start Deployment

### Option 1: Automated ParrotOS Deployment

For ParrotOS systems, use the automated deployment script:

```bash
- **Network**: Stable internet connection for initial setup

### Software Dependencies

- Docker 24.0+
- Docker Compose 2.20+
- Go 1.21+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- NATS Server 2.10+

## Quick Start Deployment

### Option 1: Automated ParrotOS Deployment

For ParrotOS systems, use the automated deployment script:

```bash

## Clone the repository

git clone https://github.com/your-org/syn-os.git
cd syn-os

## Run the automated deployment script

sudo ./parrotos-synapticos/deploy_syn_os.sh

## Follow the interactive prompts for configuration

```text

## Run the automated deployment script

sudo ./parrotos-synapticos/deploy_syn_os.sh

## Follow the interactive prompts for configuration

```text

## Run the automated deployment script

sudo ./parrotos-synapticos/deploy_syn_os.sh

## Follow the interactive prompts for configuration

```text
## Follow the interactive prompts for configuration

```text

### Option 2: Docker Compose Deployment

For other Linux distributions:

```bash

```bash
```bash

```bash

## Clone and setup

git clone https://github.com/your-org/syn-os.git
cd syn-os

## Copy and configure environment

cp .env.example .env

## Edit .env with your configuration

## Deploy with Docker Compose

make deploy-production

## Verify deployment

make health-check
```text

## Copy and configure environment

cp .env.example .env

## Edit .env with your configuration

## Deploy with Docker Compose

make deploy-production

## Verify deployment

make health-check

```text

## Copy and configure environment

cp .env.example .env

## Edit .env with your configuration

## Deploy with Docker Compose

make deploy-production

## Verify deployment

make health-check

```text
## Edit .env with your configuration

## Deploy with Docker Compose

make deploy-production

## Verify deployment

make health-check

```text

### Option 3: Manual Installation

For custom deployments or development:

```bash

```bash
```bash

```bash

## Install dependencies

make install-deps

## Build all components

make build-all

## Initialize databases

make init-db

## Start services

make start-all
```text
## Build all components

make build-all

## Initialize databases

make init-db

## Start services

make start-all

```text

## Build all components

make build-all

## Initialize databases

make init-db

## Start services

make start-all

```text
## Initialize databases

make init-db

## Start services

make start-all

```text

## Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash

Create a `.env` file with the following configuration:

```bash
Create a `.env` file with the following configuration:

```bash
```bash

## Database Configuration

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=syn_os_prod
POSTGRES_USER=syn_os_user
POSTGRES_PASSWORD=your_secure_password

## Redis Configuration

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

## NATS Configuration

NATS_URL=nats://localhost:4222
NATS_CLUSTER_ID=syn-os-cluster
NATS_CLIENT_ID=syn-os-client

## Service Orchestrator

ORCHESTRATOR_PORT=8080
ORCHESTRATOR_LOG_LEVEL=info
ORCHESTRATOR_JWT_SECRET=your_jwt_secret_key

## Consciousness System

CONSCIOUSNESS_LOG_LEVEL=info
CONSCIOUSNESS_PERSISTENCE_PATH=/var/lib/syn-os/consciousness
CONSCIOUSNESS_MODEL_PATH=/var/lib/syn-os/models

## Security Configuration

JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=24h
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

## Monitoring

PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000

## SSL/TLS Configuration

SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/syn-os.crt
SSL_KEY_PATH=/etc/ssl/private/syn-os.key
```text

POSTGRES_DB=syn_os_prod
POSTGRES_USER=syn_os_user
POSTGRES_PASSWORD=your_secure_password

## Redis Configuration

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

## NATS Configuration

NATS_URL=nats://localhost:4222
NATS_CLUSTER_ID=syn-os-cluster
NATS_CLIENT_ID=syn-os-client

## Service Orchestrator

ORCHESTRATOR_PORT=8080
ORCHESTRATOR_LOG_LEVEL=info
ORCHESTRATOR_JWT_SECRET=your_jwt_secret_key

## Consciousness System

CONSCIOUSNESS_LOG_LEVEL=info
CONSCIOUSNESS_PERSISTENCE_PATH=/var/lib/syn-os/consciousness
CONSCIOUSNESS_MODEL_PATH=/var/lib/syn-os/models

## Security Configuration

JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=24h
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

## Monitoring

PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000

## SSL/TLS Configuration

SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/syn-os.crt
SSL_KEY_PATH=/etc/ssl/private/syn-os.key

```text
POSTGRES_DB=syn_os_prod
POSTGRES_USER=syn_os_user
POSTGRES_PASSWORD=your_secure_password

## Redis Configuration

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

## NATS Configuration

NATS_URL=nats://localhost:4222
NATS_CLUSTER_ID=syn-os-cluster
NATS_CLIENT_ID=syn-os-client

## Service Orchestrator

ORCHESTRATOR_PORT=8080
ORCHESTRATOR_LOG_LEVEL=info
ORCHESTRATOR_JWT_SECRET=your_jwt_secret_key

## Consciousness System

CONSCIOUSNESS_LOG_LEVEL=info
CONSCIOUSNESS_PERSISTENCE_PATH=/var/lib/syn-os/consciousness
CONSCIOUSNESS_MODEL_PATH=/var/lib/syn-os/models

## Security Configuration

JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=24h
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

## Monitoring

PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000

## SSL/TLS Configuration

SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/syn-os.crt
SSL_KEY_PATH=/etc/ssl/private/syn-os.key

```text

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

## NATS Configuration

NATS_URL=nats://localhost:4222
NATS_CLUSTER_ID=syn-os-cluster
NATS_CLIENT_ID=syn-os-client

## Service Orchestrator

ORCHESTRATOR_PORT=8080
ORCHESTRATOR_LOG_LEVEL=info
ORCHESTRATOR_JWT_SECRET=your_jwt_secret_key

## Consciousness System

CONSCIOUSNESS_LOG_LEVEL=info
CONSCIOUSNESS_PERSISTENCE_PATH=/var/lib/syn-os/consciousness
CONSCIOUSNESS_MODEL_PATH=/var/lib/syn-os/models

## Security Configuration

JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=24h
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

## Monitoring

PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000

## SSL/TLS Configuration

SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/syn-os.crt
SSL_KEY_PATH=/etc/ssl/private/syn-os.key

```text

### Service Configuration

#### PostgreSQL Setup

```sql
```sql

```sql
```sql

- - Create database and user

CREATE DATABASE syn_os_prod;
CREATE USER syn_os_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE syn_os_prod TO syn_os_user;

- - Enable required extensions

\c syn_os_prod;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```text
GRANT ALL PRIVILEGES ON DATABASE syn_os_prod TO syn_os_user;

- - Enable required extensions

\c syn_os_prod;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

```text

- - Enable required extensions

\c syn_os_prod;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

```text
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

```text

#### NATS JetStream Configuration

```bash

```bash
```bash

```bash

## Create NATS configuration file

cat > /etc/nats/nats-server.conf << EOF
port: 4222
http_port: 8222

jetstream {
    store_dir: "/var/lib/nats/jetstream"
    max_memory_store: 1GB
    max_file_store: 10GB
}

accounts {
    SYN_OS: {
        jetstream: enabled
        users: [
            {user: "syn_os_user", password: "your_nats_password"}
        ]
    }
}
EOF
```text

http_port: 8222

jetstream {
    store_dir: "/var/lib/nats/jetstream"
    max_memory_store: 1GB
    max_file_store: 10GB
}

accounts {
    SYN_OS: {
        jetstream: enabled
        users: [
            {user: "syn_os_user", password: "your_nats_password"}
        ]
    }
}
EOF

```text
http_port: 8222

jetstream {
    store_dir: "/var/lib/nats/jetstream"
    max_memory_store: 1GB
    max_file_store: 10GB
}

accounts {
    SYN_OS: {
        jetstream: enabled
        users: [
            {user: "syn_os_user", password: "your_nats_password"}
        ]
    }
}
EOF

```text
    max_file_store: 10GB
}

accounts {
    SYN_OS: {
        jetstream: enabled
        users: [
            {user: "syn_os_user", password: "your_nats_password"}
        ]
    }
}
EOF

```text

## Security Configuration

### SSL/TLS Setup

Generate SSL certificates for production:

```bash

Generate SSL certificates for production:

```bash
Generate SSL certificates for production:

```bash
```bash

## Generate self-signed certificates (for testing)

openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/syn-os.key \

    - out /etc/ssl/certs/syn-os.crt -days 365 -nodes \
    - subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

## Set proper permissions

chmod 600 /etc/ssl/private/syn-os.key
chmod 644 /etc/ssl/certs/syn-os.crt
```text
    - out /etc/ssl/certs/syn-os.crt -days 365 -nodes \
    - subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

## Set proper permissions

chmod 600 /etc/ssl/private/syn-os.key
chmod 644 /etc/ssl/certs/syn-os.crt

```text

    - subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

## Set proper permissions

chmod 600 /etc/ssl/private/syn-os.key
chmod 644 /etc/ssl/certs/syn-os.crt

```text
chmod 600 /etc/ssl/private/syn-os.key
chmod 644 /etc/ssl/certs/syn-os.crt

```text

### Firewall Configuration

Configure firewall rules for production:

```bash

```bash
```bash

```bash

## Allow SSH

ufw allow 22/tcp

## Allow HTTP/HTTPS

ufw allow 80/tcp
ufw allow 443/tcp

## Allow application ports (adjust as needed)

ufw allow 8080/tcp  # Service Orchestrator
ufw allow 8082/tcp  # Security Tutor
ufw allow 8083/tcp  # Web Dashboard

## Allow database access (restrict to application servers)

ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
ufw allow from 10.0.0.0/8 to any port 6379  # Redis
ufw allow from 10.0.0.0/8 to any port 4222  # NATS

## Enable firewall

ufw --force enable
```text
## Allow HTTP/HTTPS

ufw allow 80/tcp
ufw allow 443/tcp

## Allow application ports (adjust as needed)

ufw allow 8080/tcp  # Service Orchestrator
ufw allow 8082/tcp  # Security Tutor
ufw allow 8083/tcp  # Web Dashboard

## Allow database access (restrict to application servers)

ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
ufw allow from 10.0.0.0/8 to any port 6379  # Redis
ufw allow from 10.0.0.0/8 to any port 4222  # NATS

## Enable firewall

ufw --force enable

```text

## Allow HTTP/HTTPS

ufw allow 80/tcp
ufw allow 443/tcp

## Allow application ports (adjust as needed)

ufw allow 8080/tcp  # Service Orchestrator
ufw allow 8082/tcp  # Security Tutor
ufw allow 8083/tcp  # Web Dashboard

## Allow database access (restrict to application servers)

ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
ufw allow from 10.0.0.0/8 to any port 6379  # Redis
ufw allow from 10.0.0.0/8 to any port 4222  # NATS

## Enable firewall

ufw --force enable

```text

## Allow application ports (adjust as needed)

ufw allow 8080/tcp  # Service Orchestrator
ufw allow 8082/tcp  # Security Tutor
ufw allow 8083/tcp  # Web Dashboard

## Allow database access (restrict to application servers)

ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
ufw allow from 10.0.0.0/8 to any port 6379  # Redis
ufw allow from 10.0.0.0/8 to any port 4222  # NATS

## Enable firewall

ufw --force enable

```text

### Authentication Setup

Configure JWT authentication:

```bash

```bash
```bash

```bash

## Generate secure JWT secret

JWT_SECRET=$(openssl rand -base64 64)
echo "JWT_SECRET=$JWT_SECRET" >> .env

## Create admin user

python tools/cli/syn_os_cli.py user create-admin \

    - -username admin \
    - -email admin@your-domain.com \
    - -password your_admin_password

```text

## Create admin user

python tools/cli/syn_os_cli.py user create-admin \

    - -username admin \
    - -email admin@your-domain.com \
    - -password your_admin_password

```text

## Create admin user

python tools/cli/syn_os_cli.py user create-admin \

    - -username admin \
    - -email admin@your-domain.com \
    - -password your_admin_password

```text
    - -username admin \
    - -email admin@your-domain.com \
    - -password your_admin_password

```text

## Monitoring and Logging

### Prometheus Configuration

```yaml

```yaml
```yaml

```yaml

## prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:

  - job_name: 'syn-os-orchestrator'

    static_configs:

      - targets: ['localhost:8080']

    metrics_path: '/metrics'

  - job_name: 'syn-os-consciousness'

    static_configs:

      - targets: ['localhost:8081']

    metrics_path: '/metrics'

  - job_name: 'nats'

    static_configs:

      - targets: ['localhost:8222']

    metrics_path: '/varz'
```text

scrape_configs:

  - job_name: 'syn-os-orchestrator'

    static_configs:

      - targets: ['localhost:8080']

    metrics_path: '/metrics'

  - job_name: 'syn-os-consciousness'

    static_configs:

      - targets: ['localhost:8081']

    metrics_path: '/metrics'

  - job_name: 'nats'

    static_configs:

      - targets: ['localhost:8222']

    metrics_path: '/varz'

```text

scrape_configs:

  - job_name: 'syn-os-orchestrator'

    static_configs:

      - targets: ['localhost:8080']

    metrics_path: '/metrics'

  - job_name: 'syn-os-consciousness'

    static_configs:

      - targets: ['localhost:8081']

    metrics_path: '/metrics'

  - job_name: 'nats'

    static_configs:

      - targets: ['localhost:8222']

    metrics_path: '/varz'

```text
    static_configs:

      - targets: ['localhost:8080']

    metrics_path: '/metrics'

  - job_name: 'syn-os-consciousness'

    static_configs:

      - targets: ['localhost:8081']

    metrics_path: '/metrics'

  - job_name: 'nats'

    static_configs:

      - targets: ['localhost:8222']

    metrics_path: '/varz'

```text

### Log Aggregation

Configure centralized logging:

```bash

```bash
```bash

```bash

## Install and configure rsyslog

apt-get install rsyslog

## Configure log rotation

cat > /etc/logrotate.d/syn-os << EOF
/var/log/syn-os/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 syn-os syn-os
}
EOF
```text
## Configure log rotation

cat > /etc/logrotate.d/syn-os << EOF
/var/log/syn-os/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 syn-os syn-os
}
EOF

```text

## Configure log rotation

cat > /etc/logrotate.d/syn-os << EOF
/var/log/syn-os/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 syn-os syn-os
}
EOF

```text
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 syn-os syn-os
}
EOF

```text

## Performance Tuning

### PostgreSQL Optimization

```sql
```sql

```sql
```sql

- - postgresql.conf optimizations

ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

- - Reload configuration

SELECT pg_reload_conf();
```text

ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

- - Reload configuration

SELECT pg_reload_conf();

```text
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

- - Reload configuration

SELECT pg_reload_conf();

```text
- - Reload configuration

SELECT pg_reload_conf();

```text

### Redis Optimization

```bash

```bash
```bash

```bash

## redis.conf optimizations

echo "maxmemory 2gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
echo "save 900 1" >> /etc/redis/redis.conf
echo "save 300 10" >> /etc/redis/redis.conf
echo "save 60 10000" >> /etc/redis/redis.conf
```text

echo "save 900 1" >> /etc/redis/redis.conf
echo "save 300 10" >> /etc/redis/redis.conf
echo "save 60 10000" >> /etc/redis/redis.conf

```text
echo "save 900 1" >> /etc/redis/redis.conf
echo "save 300 10" >> /etc/redis/redis.conf
echo "save 60 10000" >> /etc/redis/redis.conf

```text
```text

### System Optimization

```bash

```bash
```bash

```bash

## Increase file descriptor limits

echo "syn-os soft nofile 65536" >> /etc/security/limits.conf
echo "syn-os hard nofile 65536" >> /etc/security/limits.conf

## Optimize network settings

echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p
```text

## Optimize network settings

echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p

```text

## Optimize network settings

echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p

```text
sysctl -p

```text

## Backup and Recovery

### Database Backup

```bash
```bash

```bash

```bash
#!/bin/bash
## backup_database.sh

BACKUP_DIR="/var/backups/syn-os"
DATE=$(date +%Y%m%d_%H%M%S)

## Create backup directory

mkdir -p $BACKUP_DIR

## Backup PostgreSQL

pg_dump -h localhost -U syn_os_user syn_os_prod | \
    gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

## Backup Redis

redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

## Backup consciousness data

tar -czf $BACKUP_DIR/consciousness_$DATE.tar.gz \
    /var/lib/syn-os/consciousness

## Clean old backups (keep 30 days)

find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```text

## Create backup directory

mkdir -p $BACKUP_DIR

## Backup PostgreSQL

pg_dump -h localhost -U syn_os_user syn_os_prod | \
    gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

## Backup Redis

redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

## Backup consciousness data

tar -czf $BACKUP_DIR/consciousness_$DATE.tar.gz \
    /var/lib/syn-os/consciousness

## Clean old backups (keep 30 days)

find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

```text

## Create backup directory

mkdir -p $BACKUP_DIR

## Backup PostgreSQL

pg_dump -h localhost -U syn_os_user syn_os_prod | \
    gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

## Backup Redis

redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

## Backup consciousness data

tar -czf $BACKUP_DIR/consciousness_$DATE.tar.gz \
    /var/lib/syn-os/consciousness

## Clean old backups (keep 30 days)

find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

```text
## Backup PostgreSQL

pg_dump -h localhost -U syn_os_user syn_os_prod | \
    gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

## Backup Redis

redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

## Backup consciousness data

tar -czf $BACKUP_DIR/consciousness_$DATE.tar.gz \
    /var/lib/syn-os/consciousness

## Clean old backups (keep 30 days)

find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

```text

### Automated Backup Schedule

```bash

```bash
```bash

```bash

## Add to crontab

crontab -e

## Add this line for daily backups at 2 AM

0 2 * * * /usr/local/bin/backup_database.sh
```text
## Add this line for daily backups at 2 AM

0 2 * * * /usr/local/bin/backup_database.sh

```text

## Add this line for daily backups at 2 AM

0 2 * * * /usr/local/bin/backup_database.sh

```text
```text

## Health Checks and Monitoring

### Service Health Endpoints

- **Service Orchestrator**: `http://localhost:8080/health`
- **Consciousness System**: `http://localhost:8081/health`
- **Web Dashboard**: `http://localhost:8083/health`
- **Security Tutor**: `http://localhost:8082/health`

### Monitoring Script

```bash
- **Service Orchestrator**: `http://localhost:8080/health`
- **Consciousness System**: `http://localhost:8081/health`
- **Web Dashboard**: `http://localhost:8083/health`
- **Security Tutor**: `http://localhost:8082/health`

### Monitoring Script

```bash

- **Service Orchestrator**: `http://localhost:8080/health`
- **Consciousness System**: `http://localhost:8081/health`
- **Web Dashboard**: `http://localhost:8083/health`
- **Security Tutor**: `http://localhost:8082/health`

### Monitoring Script

```bash

### Monitoring Script

```bash
#!/bin/bash
## health_check.sh

SERVICES=(
    "orchestrator:8080"
    "consciousness:8081"
    "dashboard:8083"
    "tutor:8082"
)

for service in "${SERVICES[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)

    if curl -f -s http://localhost:$port/health > /dev/null; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is unhealthy"
        # Add alerting logic here
    fi
done
```text

    "consciousness:8081"
    "dashboard:8083"
    "tutor:8082"
)

for service in "${SERVICES[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)

    if curl -f -s http://localhost:$port/health > /dev/null; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is unhealthy"
        # Add alerting logic here
    fi
done

```text
    "consciousness:8081"
    "dashboard:8083"
    "tutor:8082"
)

for service in "${SERVICES[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)

    if curl -f -s http://localhost:$port/health > /dev/null; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is unhealthy"
        # Add alerting logic here
    fi
done

```text
for service in "${SERVICES[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)

    if curl -f -s http://localhost:$port/health > /dev/null; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is unhealthy"
        # Add alerting logic here
    fi
done

```text

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
#### Service Won't Start

```bash

#### Service Won't Start

```bash
```bash

## Check logs

journalctl -u syn-os-orchestrator -f
tail -f /var/log/syn-os/consciousness.log

## Check port availability

netstat -tlnp | grep :8080

## Check database connectivity

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT 1;"
```text

## Check port availability

netstat -tlnp | grep :8080

## Check database connectivity

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT 1;"

```text

## Check port availability

netstat -tlnp | grep :8080

## Check database connectivity

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT 1;"

```text
## Check database connectivity

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT 1;"

```text

#### High Memory Usage

```bash

```bash
```bash

```bash

## Check memory usage by service

ps aux | grep -E "(orchestrator|consciousness)" | sort -k4 -nr

## Check system memory

free -h
cat /proc/meminfo
```text
## Check system memory

free -h
cat /proc/meminfo

```text

## Check system memory

free -h
cat /proc/meminfo

```text

```text

#### Database Connection Issues

```bash

```bash
```bash

```bash

## Check PostgreSQL status

systemctl status postgresql

## Check connections

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT count(*) FROM pg_stat_activity;"

## Check locks

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT * FROM pg_locks WHERE NOT granted;"
```text
## Check connections

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT count(*) FROM pg_stat_activity;"

## Check locks

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT * FROM pg_locks WHERE NOT granted;"

```text

## Check connections

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT count(*) FROM pg_stat_activity;"

## Check locks

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT * FROM pg_locks WHERE NOT granted;"

```text
## Check locks

psql -h localhost -U syn_os_user -d syn_os_prod -c "SELECT * FROM pg_locks WHERE NOT granted;"

```text

### Log Locations

- **Service Orchestrator**: `/var/log/syn-os/orchestrator.log`
- **Consciousness System**: `/var/log/syn-os/consciousness.log`
- **Web Dashboard**: `/var/log/syn-os/dashboard.log`
- **Security Tutor**: `/var/log/syn-os/tutor.log`
- **System Logs**: `/var/log/syslog`

## Scaling and High Availability

### Horizontal Scaling

For high-traffic deployments, consider:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Orchestrator Instances**: Scale the Go service
3. **Database Clustering**: PostgreSQL streaming replication
4. **Redis Clustering**: Redis Cluster mode
5. **NATS Clustering**: Multi-node NATS setup

### Example Load Balancer Configuration

```nginx
- **Web Dashboard**: `/var/log/syn-os/dashboard.log`
- **Security Tutor**: `/var/log/syn-os/tutor.log`
- **System Logs**: `/var/log/syslog`

## Scaling and High Availability

### Horizontal Scaling

For high-traffic deployments, consider:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Orchestrator Instances**: Scale the Go service
3. **Database Clustering**: PostgreSQL streaming replication
4. **Redis Clustering**: Redis Cluster mode
5. **NATS Clustering**: Multi-node NATS setup

### Example Load Balancer Configuration

```nginx

- **Web Dashboard**: `/var/log/syn-os/dashboard.log`
- **Security Tutor**: `/var/log/syn-os/tutor.log`
- **System Logs**: `/var/log/syslog`

## Scaling and High Availability

### Horizontal Scaling

For high-traffic deployments, consider:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Orchestrator Instances**: Scale the Go service
3. **Database Clustering**: PostgreSQL streaming replication
4. **Redis Clustering**: Redis Cluster mode
5. **NATS Clustering**: Multi-node NATS setup

### Example Load Balancer Configuration

```nginx
## Scaling and High Availability

### Horizontal Scaling

For high-traffic deployments, consider:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Orchestrator Instances**: Scale the Go service
3. **Database Clustering**: PostgreSQL streaming replication
4. **Redis Clustering**: Redis Cluster mode
5. **NATS Clustering**: Multi-node NATS setup

### Example Load Balancer Configuration

```nginx

## /etc/nginx/sites-available/syn-os

upstream syn_os_orchestrator {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://syn_os_orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```text

    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://syn_os_orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

```text
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://syn_os_orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

```text
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://syn_os_orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

```text

## Security Best Practices

1. **Regular Updates**: Keep all components updated
2. **Access Control**: Use strong authentication and authorization
3. **Network Security**: Implement proper firewall rules
4. **Data Encryption**: Encrypt data at rest and in transit
5. **Audit Logging**: Enable comprehensive audit trails
6. **Vulnerability Scanning**: Regular security assessments
7. **Backup Security**: Encrypt and secure backups

## Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Check service health and logs
- **Weekly**: Review performance metrics and alerts
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system backup and disaster recovery testing

### Getting Help

- **Documentation**: Check the `/docs` directory
- **Logs**: Review service logs for error details
- **CLI Tools**: Use `syn_os_cli.py` for diagnostics
- **Community**: Join the Syn_OS community forums
- **Support**: Contact professional support services

## Conclusion

This deployment guide provides a comprehensive foundation for running Syn_OS in production. The consciousness-aware
infrastructure platform represents a new paradigm in intelligent systems management, where AI consciousness actively
participates in service orchestration and decision-making.

For additional support and advanced configuration options, refer to the detailed API documentation and architecture guides in the `/docs` directory.

1. **Network Security**: Implement proper firewall rules
2. **Data Encryption**: Encrypt data at rest and in transit
3. **Audit Logging**: Enable comprehensive audit trails
4. **Vulnerability Scanning**: Regular security assessments
5. **Backup Security**: Encrypt and secure backups

## Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Check service health and logs
- **Weekly**: Review performance metrics and alerts
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system backup and disaster recovery testing

### Getting Help

- **Documentation**: Check the `/docs` directory
- **Logs**: Review service logs for error details
- **CLI Tools**: Use `syn_os_cli.py` for diagnostics
- **Community**: Join the Syn_OS community forums
- **Support**: Contact professional support services

## Conclusion

This deployment guide provides a comprehensive foundation for running Syn_OS in production. The consciousness-aware
infrastructure platform represents a new paradigm in intelligent systems management, where AI consciousness actively
participates in service orchestration and decision-making.

For additional support and advanced configuration options, refer to the detailed API documentation and architecture guides in the `/docs` directory.
1. **Network Security**: Implement proper firewall rules
2. **Data Encryption**: Encrypt data at rest and in transit
3. **Audit Logging**: Enable comprehensive audit trails
4. **Vulnerability Scanning**: Regular security assessments
5. **Backup Security**: Encrypt and secure backups

## Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Check service health and logs
- **Weekly**: Review performance metrics and alerts
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system backup and disaster recovery testing

### Getting Help

- **Documentation**: Check the `/docs` directory
- **Logs**: Review service logs for error details
- **CLI Tools**: Use `syn_os_cli.py` for diagnostics
- **Community**: Join the Syn_OS community forums
- **Support**: Contact professional support services

## Conclusion

This deployment guide provides a comprehensive foundation for running Syn_OS in production. The consciousness-aware
infrastructure platform represents a new paradigm in intelligent systems management, where AI consciousness actively
participates in service orchestration and decision-making.

For additional support and advanced configuration options, refer to the detailed API documentation and architecture guides in the `/docs` directory.

1. **Network Security**: Implement proper firewall rules
2. **Data Encryption**: Encrypt data at rest and in transit
3. **Audit Logging**: Enable comprehensive audit trails
4. **Vulnerability Scanning**: Regular security assessments
5. **Backup Security**: Encrypt and secure backups

## Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Check service health and logs
- **Weekly**: Review performance metrics and alerts
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system backup and disaster recovery testing

### Getting Help

- **Documentation**: Check the `/docs` directory
- **Logs**: Review service logs for error details
- **CLI Tools**: Use `syn_os_cli.py` for diagnostics
- **Community**: Join the Syn_OS community forums
- **Support**: Contact professional support services

## Conclusion

This deployment guide provides a comprehensive foundation for running Syn_OS in production. The consciousness-aware
infrastructure platform represents a new paradigm in intelligent systems management, where AI consciousness actively
participates in service orchestration and decision-making.

For additional support and advanced configuration options, refer to the detailed API documentation and architecture guides in the `/docs` directory.