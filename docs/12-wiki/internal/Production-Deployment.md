# 🚀 Production Deployment Guide

**For**: DevOps Engineers, System Administrators  
**Complexity**: Advanced  
**Scope**: Enterprise production deployment

Deploy SynOS to production environments with high availability and security.

---

## Pre-Deployment Checklist

- [ ] Hardware requirements met (16GB RAM, 8 cores, 500GB storage)
- [ ] Network configured (static IP, DNS, firewall rules)
- [ ] SSL certificates obtained
- [ ] Backup strategy defined
- [ ] Monitoring tools ready
- [ ] Security policies configured
- [ ] Disaster recovery plan documented

---

## Deployment Architecture

### Single Server (Small)

```
┌─────────────────────┐
│    SynOS Server     │
│  - Application      │
│  - Database         │
│  - Web Server       │
└─────────────────────┘
```

**Use Case**: Testing, small teams (<50 users)

### High Availability (Enterprise)

```
          ┌──────────────┐
          │  Load Bal... │
          └──────┬───────┘
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌────▼────┐
   │ SynOS 1 │      │ SynOS 2 │
   └────┬────┘      └────┬────┘
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ PostgreSQL HA   │
        │  (Primary +     │
        │   Standby)      │
        └─────────────────┘
```

**Use Case**: Enterprise (>100 users), 99.9% uptime

---

## Installation

### Method 1: ISO Installation

```bash
# 1. Download ISO
wget https://download.synos.dev/synos-latest.iso

# 2. Verify checksum
sha256sum synos-latest.iso

# 3. Write to USB
dd if=synos-latest.iso of=/dev/sdX bs=4M status=progress

# 4. Boot from USB and follow installer
```

### Method 2: Network Install

```bash
# Bootstrap installation
curl -fsSL https://get.synos.dev | sudo bash

# Configure
sudo synos-setup configure \
  --hostname prod-synos-01 \
  --ip 10.0.1.100/24 \
  --gateway 10.0.1.1 \
  --dns 8.8.8.8

# Install packages
sudo synpkg install synos-server-full
```

---

## Configuration

### System Configuration

```yaml
# /etc/synos/system.yml
system:
  hostname: prod-synos-01
  domain: synos.company.com
  timezone: America/New_York
  
network:
  interface: eth0
  ip: 10.0.1.100
  netmask: 255.255.255.0
  gateway: 10.0.1.1
  dns:
    - 8.8.8.8
    - 8.8.4.4

security:
  firewall: enabled
  selinux: enforcing
  fail2ban: enabled
```

### Database Configuration

```bash
# PostgreSQL setup
sudo -u postgres psql

CREATE DATABASE synos_prod;
CREATE USER synos WITH ENCRYPTED PASSWORD 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE synos_prod TO synos;

# Tune PostgreSQL
sudo nano /etc/postgresql/14/main/postgresql.conf

# Recommended settings for production
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10485kB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### Web Server (Nginx)

```nginx
# /etc/nginx/sites-available/synos
upstream synos_app {
    server 127.0.0.1:8000;
    keepalive 64;
}

server {
    listen 80;
    server_name synos.company.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name synos.company.com;
    
    ssl_certificate /etc/ssl/certs/synos.crt;
    ssl_certificate_key /etc/ssl/private/synos.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://synos_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/synos/static/;
        expires 30d;
    }
}
```

---

## High Availability Setup

### Load Balancer (HAProxy)

```bash
# /etc/haproxy/haproxy.cfg
global
    log /dev/log local0
    maxconn 4096
    
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    
frontend synos_frontend
    bind *:443 ssl crt /etc/ssl/certs/synos.pem
    default_backend synos_backend
    
backend synos_backend
    balance roundrobin
    option httpchk GET /health
    server synos1 10.0.1.101:443 check ssl verify none
    server synos2 10.0.1.102:443 check ssl verify none
```

### Database Replication

```bash
# Primary server
# /etc/postgresql/14/main/postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB

# Create replication user
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'PASSWORD';

# Standby server
# Create recovery.conf
primary_conninfo = 'host=10.0.1.100 port=5432 user=replicator password=PASSWORD'
```

---

## Monitoring

### System Monitoring

```bash
# Install monitoring stack
sudo synpkg install prometheus grafana

# Prometheus config
# /etc/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'synos'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### Application Monitoring

```python
# Enable application metrics
from synos.monitoring import enable_metrics

enable_metrics(
    prometheus_port=9090,
    grafana_dashboard=True
)
```

### Alerting

```yaml
# /etc/prometheus/alerts.yml
groups:
  - name: synos_alerts
    rules:
      - alert: HighCPU
        expr: cpu_usage > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage detected
      
      - alert: LowDiskSpace
        expr: disk_free < 10
        for: 10m
        labels:
          severity: critical
```

---

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# /opt/synos/scripts/backup.sh

BACKUP_DIR="/backups/synos"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump synos_prod | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Configuration backup
tar czf "$BACKUP_DIR/config_$DATE.tar.gz" /etc/synos

# Data backup
tar czf "$BACKUP_DIR/data_$DATE.tar.gz" /var/lib/synos

# Rotate old backups (keep 30 days)
find "$BACKUP_DIR" -mtime +30 -delete

# Upload to S3
aws s3 sync "$BACKUP_DIR" s3://company-backups/synos/
```

### Cron Schedule

```bash
# /etc/cron.d/synos-backup
0 2 * * * root /opt/synos/scripts/backup.sh
```

### Recovery

```bash
# Restore database
gunzip < db_20251004_020000.sql.gz | psql synos_prod

# Restore configuration
tar xzf config_20251004_020000.tar.gz -C /

# Restart services
sudo systemctl restart synos
```

---

## Security Hardening

```bash
# Firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# SSH hardening
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

# Enable fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# System updates
sudo apt update && sudo apt upgrade -y
sudo apt install unattended-upgrades
```

---

## Performance Tuning

```bash
# Kernel parameters
sudo nano /etc/sysctl.conf

# Network tuning
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 8192

# File descriptors
fs.file-max = 2097152

# Apply changes
sudo sysctl -p
```

---

## Troubleshooting

**Service won't start**:
```bash
sudo journalctl -u synos -n 50
sudo systemctl status synos
```

**High load**:
```bash
top
htop
iotop
```

**Database issues**:
```bash
sudo -u postgres psql synos_prod
SELECT * FROM pg_stat_activity;
```

---

**Last Updated**: October 4, 2025  
**Support**: support@synos.dev
