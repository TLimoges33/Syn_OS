#!/bin/bash
set -euo pipefail

# Production Monitoring Setup Script for Syn_OS
# Sets up comprehensive monitoring stack with Prometheus, Grafana, Loki, and Alertmanager

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking monitoring prerequisites..."
    
    local missing_tools=()
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    command -v curl >/dev/null 2>&1 || missing_tools+=("curl")
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create monitoring directories
setup_directories() {
    log_info "Setting up monitoring directories..."
    
    local dirs=(
        "$PROJECT_ROOT/deploy/monitoring/grafana/dashboards"
        "$PROJECT_ROOT/deploy/monitoring/grafana/provisioning/dashboards"
        "$PROJECT_ROOT/deploy/monitoring/grafana/provisioning/datasources"
        "$PROJECT_ROOT/deploy/monitoring/alertmanager"
        "$PROJECT_ROOT/deploy/logging"
        "$PROJECT_ROOT/monitoring/data/prometheus"
        "$PROJECT_ROOT/monitoring/data/grafana"
        "$PROJECT_ROOT/monitoring/data/loki"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    log_success "Monitoring directories created"
}

# Create Grafana configuration
setup_grafana_config() {
    log_info "Setting up Grafana configuration..."
    
    # Datasource configuration
    cat > "$PROJECT_ROOT/deploy/monitoring/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
EOF

    # Dashboard provisioning
    cat > "$PROJECT_ROOT/deploy/monitoring/grafana/provisioning/dashboards/dashboard.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'Syn_OS Dashboards'
    orgId: 1
    folder: 'Syn_OS'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    log_success "Grafana configuration created"
}

# Create Grafana dashboards
create_grafana_dashboards() {
    log_info "Creating Grafana dashboards..."
    
    # Consciousness monitoring dashboard
    cat > "$PROJECT_ROOT/deploy/monitoring/grafana/dashboards/consciousness-monitoring.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Syn_OS Consciousness Monitoring",
    "tags": ["syn_os", "consciousness"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Consciousness Level",
        "type": "stat",
        "targets": [
          {
            "expr": "consciousness_level",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 1,
            "unit": "percentunit"
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Neural Activity",
        "type": "stat",
        "targets": [
          {
            "expr": "neural_activity_level",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 1,
            "unit": "percentunit"
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Decision Processing Time",
        "type": "graph",
        "targets": [
          {
            "expr": "consciousness_decision_time_seconds",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Decisions Per Second",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(consciousness_decisions_total[5m])",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "Threat Analysis",
        "type": "graph",
        "targets": [
          {
            "expr": "consciousness_threat_level",
            "legendFormat": "Threat Level"
          },
          {
            "expr": "consciousness_threat_confidence",
            "legendFormat": "Confidence"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
EOF

    # Security monitoring dashboard
    cat > "$PROJECT_ROOT/deploy/monitoring/grafana/dashboards/security-monitoring.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Syn_OS Security Monitoring",
    "tags": ["syn_os", "security"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Authentication Performance",
        "type": "stat",
        "targets": [
          {
            "expr": "authentication_operations_per_second",
            "legendFormat": "Ops/Sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ops",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 5000},
                {"color": "green", "value": 9000}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Security Grade",
        "type": "stat",
        "targets": [
          {
            "expr": "security_audit_score",
            "legendFormat": "Score"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 100,
            "unit": "percent"
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Active Threats",
        "type": "graph",
        "targets": [
          {
            "expr": "security_active_threats",
            "legendFormat": "{{threat_type}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "Authentication Failures",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(authentication_failures_total[5m])",
            "legendFormat": "Failures/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "10s"
  }
}
EOF

    log_success "Grafana dashboards created"
}

# Create Alertmanager configuration
setup_alertmanager() {
    log_info "Setting up Alertmanager configuration..."
    
    cat > "$PROJECT_ROOT/deploy/monitoring/alertmanager/alertmanager.yml" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@syn-os.local'

route:
  group_by: ['alertname', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'

- name: 'critical-alerts'
  email_configs:
  - to: 'admin@syn-os.local'
    subject: '[CRITICAL] Syn_OS Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Severity: {{ .Labels.severity }}
      Service: {{ .Labels.service }}
      {{ end }}
  slack_configs:
  - api_url: '${SLACK_WEBHOOK_URL}'
    channel: '#syn-os-critical'
    title: 'Syn_OS Critical Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: 'warning-alerts'
  email_configs:
  - to: 'team@syn-os.local'
    subject: '[WARNING] Syn_OS Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Severity: {{ .Labels.severity }}
      Service: {{ .Labels.service }}
      {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'service']
EOF

    log_success "Alertmanager configuration created"
}

# Create Loki configuration
setup_loki() {
    log_info "Setting up Loki configuration..."
    
    cat > "$PROJECT_ROOT/deploy/logging/loki-config.yaml" << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 1h
  max_chunk_age: 1h
  chunk_target_size: 1048576
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /tmp/loki/boltdb-shipper-active
    cache_location: /tmp/loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /tmp/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s

ruler:
  storage:
    type: local
    local:
      directory: /tmp/loki/rules
  rule_path: /tmp/loki/rules-temp
  alertmanager_url: http://alertmanager:9093
  ring:
    kvstore:
      store: inmemory
  enable_api: true
EOF

    # Promtail configuration
    cat > "$PROJECT_ROOT/deploy/logging/promtail-config.yml" << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

  - job_name: syn_os_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: syn_os
          __path__: /var/log/syn_os/*.log

  - job_name: nginx_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/*.log

  - job_name: security_logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: security
          __path__: /var/log/security/*.log
EOF

    log_success "Loki configuration created"
}

# Create monitoring Docker Compose
create_monitoring_compose() {
    log_info "Creating monitoring Docker Compose configuration..."
    
    cat > "$PROJECT_ROOT/deploy/docker-compose.monitoring.yml" << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: syn_os_prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    ports:
      - "9090:9090"
    volumes:
      - ./deploy/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./deploy/monitoring/syn_os_rules.yml:/etc/prometheus/syn_os_rules.yml
      - prometheus_data:/prometheus
    networks:
      - monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3

  alertmanager:
    image: prom/alertmanager:latest
    container_name: syn_os_alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    ports:
      - "9093:9093"
    volumes:
      - ./deploy/monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: syn_os_grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./deploy/monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./deploy/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - monitoring
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "wget --quiet --tries=1 --spider http://localhost:3000/api/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  loki:
    image: grafana/loki:latest
    container_name: syn_os_loki
    command: -config.file=/etc/loki/local-config.yaml
    ports:
      - "3100:3100"
    volumes:
      - ./deploy/logging/loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/tmp/loki
    networks:
      - monitoring
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    container_name: syn_os_promtail
    command: -config.file=/etc/promtail/config.yml
    volumes:
      - ./deploy/logging/promtail-config.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    networks:
      - monitoring
    restart: unless-stopped

  # Exporters
  node-exporter:
    image: prom/node-exporter:latest
    container_name: syn_os_node_exporter
    command:
      - '--path.rootfs=/host'
    ports:
      - "9100:9100"
    volumes:
      - '/:/host:ro,rslave'
    networks:
      - monitoring
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: syn_os_cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    networks:
      - monitoring
    restart: unless-stopped

  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: syn_os_blackbox_exporter
    ports:
      - "9115:9115"
    volumes:
      - ./deploy/monitoring/blackbox.yml:/etc/blackbox_exporter/config.yml
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data:
  alertmanager_data:
  grafana_data:
  loki_data:

networks:
  monitoring:
    driver: bridge
  default:
    external:
      name: syn_os_production
EOF

    log_success "Monitoring Docker Compose created"
}

# Create blackbox exporter configuration
setup_blackbox_exporter() {
    log_info "Setting up Blackbox Exporter configuration..."
    
    cat > "$PROJECT_ROOT/deploy/monitoring/blackbox.yml" << 'EOF'
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []
      method: GET
      follow_redirects: true
      fail_if_ssl: false
      fail_if_not_ssl: false
      tls_config:
        insecure_skip_verify: true

  http_post_2xx:
    prober: http
    timeout: 5s
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: '{"test": true}'

  tcp_connect:
    prober: tcp
    timeout: 5s

  icmp:
    prober: icmp
    timeout: 5s
EOF

    log_success "Blackbox Exporter configuration created"
}

# Start monitoring stack
start_monitoring() {
    log_info "Starting monitoring stack..."
    
    cd "$PROJECT_ROOT"
    
    # Start monitoring services
    docker-compose -f deploy/docker-compose.monitoring.yml up -d
    
    # Wait for services to be ready
    log_info "Waiting for monitoring services to be ready..."
    sleep 30
    
    # Check service health
    local services=("prometheus" "grafana" "alertmanager" "loki")
    for service in "${services[@]}"; do
        if docker ps --filter "name=syn_os_$service" --filter "status=running" | grep -q "syn_os_$service"; then
            log_success "$service is running"
        else
            log_error "$service failed to start"
            docker logs "syn_os_$service" --tail=20
            exit 1
        fi
    done
    
    log_success "Monitoring stack started successfully"
}

# Print access information
print_access_info() {
    log_info "Monitoring stack access information:"
    echo
    echo "📊 Grafana:       http://localhost:3001 (admin/admin)"
    echo "🔍 Prometheus:    http://localhost:9090"
    echo "🚨 Alertmanager:  http://localhost:9093"
    echo "📋 Loki:         http://localhost:3100"
    echo
    echo "🎯 Default Dashboards:"
    echo "  - Syn_OS Consciousness Monitoring"
    echo "  - Syn_OS Security Monitoring"
    echo "  - Node Exporter Full"
    echo "  - Docker Container Monitoring"
    echo
    log_warning "Remember to change default Grafana password!"
}

# Main function
main() {
    log_info "Setting up Syn_OS monitoring stack..."
    
    check_prerequisites
    setup_directories
    setup_grafana_config
    create_grafana_dashboards
    setup_alertmanager
    setup_loki
    setup_blackbox_exporter
    create_monitoring_compose
    start_monitoring
    print_access_info
    
    log_success "🎉 Monitoring stack setup completed!"
}

# Run main function
main "$@"