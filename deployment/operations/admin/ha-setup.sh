#!/bin/bash
set -euo pipefail

# High Availability Setup Script for Syn_OS
# Configures and deploys high-availability cluster with load balancing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
DEPLOYMENT_TYPE="docker"
ENVIRONMENT="production"
SETUP_HA=true
SETUP_MONITORING=true
VERIFY_CLUSTER=true

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

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Set up Syn_OS high availability cluster with load balancing

Options:
    -t, --type TYPE         Deployment type: docker, kubernetes (default: docker)
    -e, --environment ENV   Environment: staging, production (default: production)
    -m, --skip-monitoring   Skip monitoring setup
    -v, --skip-verify       Skip cluster verification
    -h, --help              Show this help message

Examples:
    $0                      # Setup HA cluster with Docker
    $0 -t kubernetes       # Setup HA cluster with Kubernetes
    $0 -e staging          # Setup staging HA cluster

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -m|--skip-monitoring)
            SETUP_MONITORING=false
            shift
            ;;
        -v|--skip-verify)
            VERIFY_CLUSTER=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    log_info "Checking HA setup prerequisites..."
    
    local missing_tools=()
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
        command -v helm >/dev/null 2>&1 || missing_tools+=("helm")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create HAProxy configuration
setup_haproxy_config() {
    log_info "Setting up HAProxy configuration..."
    
    # Create HAProxy errors directory
    mkdir -p "$PROJECT_ROOT/deploy/haproxy/errors"
    
    # Create custom error pages
    cat > "$PROJECT_ROOT/deploy/haproxy/errors/400.http" << 'EOF'
HTTP/1.1 400 Bad Request
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>400 Bad Request - Syn_OS</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 50px; }
        .error { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .code { color: #e74c3c; font-size: 48px; font-weight: bold; }
        .message { color: #2c3e50; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="error">
        <div class="code">400</div>
        <div class="message">Bad Request</div>
        <p>The request could not be understood by the server due to malformed syntax.</p>
    </div>
</body>
</html>
EOF

    cat > "$PROJECT_ROOT/deploy/haproxy/errors/503.http" << 'EOF'
HTTP/1.1 503 Service Unavailable
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>503 Service Unavailable - Syn_OS</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 50px; }
        .error { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .code { color: #e74c3c; font-size: 48px; font-weight: bold; }
        .message { color: #2c3e50; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="error">
        <div class="code">503</div>
        <div class="message">Service Unavailable</div>
        <p>The Syn_OS service is temporarily unavailable. Please try again in a few moments.</p>
    </div>
</body>
</html>
EOF

    log_success "HAProxy configuration created"
}

# Setup Keepalived configuration
setup_keepalived_config() {
    log_info "Setting up Keepalived configuration..."
    
    mkdir -p "$PROJECT_ROOT/deploy/keepalived"
    
    # Keepalived configuration for node 1 (master)
    cat > "$PROJECT_ROOT/deploy/keepalived/keepalived-1.conf" << 'EOF'
vrrp_script chk_haproxy {
    script "/bin/check_haproxy"
    interval 2
    weight 2
    fall 3
    rise 2
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 110
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass syn_os_ha
    }
    virtual_ipaddress {
        172.21.100.100
    }
    track_script {
        chk_haproxy
    }
}
EOF

    # Keepalived configuration for node 2 (backup)
    cat > "$PROJECT_ROOT/deploy/keepalived/keepalived-2.conf" << 'EOF'
vrrp_script chk_haproxy {
    script "/bin/check_haproxy"
    interval 2
    weight 2
    fall 3
    rise 2
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass syn_os_ha
    }
    virtual_ipaddress {
        172.21.100.100
    }
    track_script {
        chk_haproxy
    }
}
EOF

    # HAProxy health check script
    cat > "$PROJECT_ROOT/deploy/keepalived/check_haproxy" << 'EOF'
#!/bin/bash
# HAProxy health check script for Keepalived

# Check if HAProxy process is running
if ! pgrep haproxy > /dev/null; then
    exit 1
fi

# Check if HAProxy stats are responding
if ! curl -s http://localhost:8404/stats > /dev/null; then
    exit 1
fi

exit 0
EOF

    chmod +x "$PROJECT_ROOT/deploy/keepalived/check_haproxy"
    
    log_success "Keepalived configuration created"
}

# Setup Consul configuration
setup_consul_config() {
    log_info "Setting up Consul configuration..."
    
    mkdir -p "$PROJECT_ROOT/deploy/consul"
    
    # Consul configuration for service discovery
    cat > "$PROJECT_ROOT/deploy/consul/consul-1.json" << 'EOF'
{
    "datacenter": "syn-os-dc",
    "data_dir": "/consul/data",
    "log_level": "INFO",
    "node_name": "consul-1",
    "bind_addr": "0.0.0.0",
    "client_addr": "0.0.0.0",
    "retry_join": ["consul-2", "consul-3"],
    "server": true,
    "bootstrap_expect": 3,
    "ui_config": {
        "enabled": true
    },
    "connect": {
        "enabled": true
    },
    "ports": {
        "grpc": 8502
    },
    "services": [
        {
            "name": "syn-os-orchestrator",
            "port": 8080,
            "check": {
                "http": "http://localhost:8080/health",
                "interval": "10s"
            }
        },
        {
            "name": "syn-os-consciousness",
            "port": 8081,
            "check": {
                "http": "http://localhost:8081/health",
                "interval": "10s"
            }
        },
        {
            "name": "syn-os-security",
            "port": 8083,
            "check": {
                "http": "http://localhost:8083/health",
                "interval": "10s"
            }
        }
    ]
}
EOF

    # Copy for other nodes with different node names
    sed 's/consul-1/consul-2/g' "$PROJECT_ROOT/deploy/consul/consul-1.json" > "$PROJECT_ROOT/deploy/consul/consul-2.json"
    sed 's/consul-1/consul-3/g' "$PROJECT_ROOT/deploy/consul/consul-1.json" > "$PROJECT_ROOT/deploy/consul/consul-3.json"
    
    log_success "Consul configuration created"
}

# Setup Filebeat configuration
setup_filebeat_config() {
    log_info "Setting up Filebeat configuration..."
    
    mkdir -p "$PROJECT_ROOT/deploy/filebeat"
    
    cat > "$PROJECT_ROOT/deploy/filebeat/filebeat.yml" << 'EOF'
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"
      - decode_json_fields:
          fields: ["message"]
          target: ""
          overwrite_keys: true

  - type: log
    paths:
      - /var/log/syn_os/*.log
    fields:
      service: syn_os
      environment: ${ENVIRONMENT}
    multiline.pattern: '^\d{4}-\d{2}-\d{2}'
    multiline.negate: true
    multiline.match: after

output.elasticsearch:
  hosts: ["elasticsearch-1:9200", "elasticsearch-2:9200", "elasticsearch-3:9200"]
  index: "syn-os-logs-%{+yyyy.MM.dd}"

setup.template.name: "syn-os"
setup.template.pattern: "syn-os-*"
setup.template.settings:
  index.number_of_shards: 3
  index.number_of_replicas: 1

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~
EOF

    log_success "Filebeat configuration created"
}

# Deploy Docker HA cluster
deploy_docker_ha() {
    log_info "Deploying Docker HA cluster..."
    
    cd "$PROJECT_ROOT"
    
    # Load environment
    if [[ -f ".env.$ENVIRONMENT" ]]; then
        source ".env.$ENVIRONMENT"
    else
        log_error "Environment file .env.$ENVIRONMENT not found"
        exit 1
    fi
    
    # Generate HAProxy stats password if not set
    if [[ -z "${HAPROXY_STATS_PASSWORD:-}" ]]; then
        export HAPROXY_STATS_PASSWORD=$(openssl rand -base64 16)
        echo "HAPROXY_STATS_PASSWORD=$HAPROXY_STATS_PASSWORD" >> ".env.$ENVIRONMENT"
        log_info "Generated HAProxy stats password"
    fi
    
    # Generate Keepalived password if not set
    if [[ -z "${KEEPALIVED_PASSWORD:-}" ]]; then
        export KEEPALIVED_PASSWORD=$(openssl rand -base64 16)
        echo "KEEPALIVED_PASSWORD=$KEEPALIVED_PASSWORD" >> ".env.$ENVIRONMENT"
        log_info "Generated Keepalived password"
    fi
    
    # Deploy base production stack first
    log_info "Starting base production services..."
    docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml up -d
    
    # Wait for base services to be ready
    log_info "Waiting for base services to be ready..."
    sleep 30
    
    # Deploy HA extensions
    log_info "Starting HA extensions..."
    docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml -f deploy/docker-compose.ha.yml up -d
    
    log_success "Docker HA cluster deployed"
}

# Deploy Kubernetes HA cluster
deploy_kubernetes_ha() {
    log_info "Deploying Kubernetes HA cluster..."
    
    # Update Helm values for HA
    cat > "$PROJECT_ROOT/deploy/helm/syn-os/values-ha.yaml" << EOF
replicaCount: 3

orchestrator:
  replicaCount: 3
  resources:
    limits:
      memory: 1Gi
      cpu: 500m
    requests:
      memory: 512Mi
      cpu: 250m

consciousness:
  replicaCount: 3
  resources:
    limits:
      memory: 4Gi
      cpu: 2
    requests:
      memory: 2Gi
      cpu: 1

security:
  replicaCount: 3
  resources:
    limits:
      memory: 512Mi
      cpu: 300m
    requests:
      memory: 256Mi
      cpu: 150m

postgresql:
  primary:
    persistence:
      enabled: true
      size: 20Gi
  readReplicas:
    replicaCount: 2
    persistence:
      enabled: true
      size: 20Gi

redis:
  replica:
    replicaCount: 2
  sentinel:
    enabled: true

nats:
  nats:
    jetstream:
      enabled: true
  cluster:
    enabled: true
    replicas: 3

monitoring:
  prometheus:
    server:
      replicaCount: 2
      persistentVolume:
        size: 50Gi
  grafana:
    replicas: 2

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: syn-os.$ENVIRONMENT.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: syn-os-tls
      hosts:
        - syn-os.$ENVIRONMENT.local

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

podDisruptionBudget:
  enabled: true
  minAvailable: 1

networkPolicy:
  enabled: true

serviceMonitor:
  enabled: true
EOF

    # Deploy with Helm
    helm upgrade --install "syn-os-$ENVIRONMENT" ./deploy/helm/syn-os \
        --namespace "syn-os-$ENVIRONMENT" \
        --create-namespace \
        --values ./deploy/helm/syn-os/values.yaml \
        --values ./deploy/helm/syn-os/values-ha.yaml \
        --set global.environment="$ENVIRONMENT" \
        --wait \
        --timeout=600s
    
    log_success "Kubernetes HA cluster deployed"
}

# Setup monitoring for HA cluster
setup_ha_monitoring() {
    if [[ "$SETUP_MONITORING" != true ]]; then
        return 0
    fi
    
    log_info "Setting up HA cluster monitoring..."
    
    # Create additional monitoring rules for HA
    cat > "$PROJECT_ROOT/deploy/monitoring/ha_rules.yml" << 'EOF'
groups:
  - name: syn_os_ha_alerts
    rules:
      # HAProxy alerts
      - alert: HAProxyDown
        expr: up{job="haproxy"} == 0
        for: 30s
        labels:
          severity: critical
          service: load_balancer
        annotations:
          summary: "HAProxy instance is down"
          description: "HAProxy {{ $labels.instance }} has been down for more than 30 seconds"

      - alert: HAProxyHighLatency
        expr: haproxy_backend_response_time_average_seconds > 1
        for: 2m
        labels:
          severity: warning
          service: load_balancer
        annotations:
          summary: "HAProxy high backend latency"
          description: "HAProxy backend {{ $labels.backend }} latency is {{ $value }}s"

      - alert: HAProxyBackendDown
        expr: haproxy_backend_up == 0
        for: 1m
        labels:
          severity: critical
          service: load_balancer
        annotations:
          summary: "HAProxy backend is down"
          description: "HAProxy backend {{ $labels.backend }} is down"

      # Consul alerts
      - alert: ConsulClusterUnhealthy
        expr: consul_health_service_status{status!="passing"} > 0
        for: 2m
        labels:
          severity: warning
          service: service_discovery
        annotations:
          summary: "Consul cluster has unhealthy services"
          description: "Consul service {{ $labels.service_name }} is not healthy"

      # Elasticsearch alerts
      - alert: ElasticsearchClusterHealth
        expr: elasticsearch_cluster_health_status{color="red"} == 1
        for: 5m
        labels:
          severity: critical
          service: logging
        annotations:
          summary: "Elasticsearch cluster health is red"
          description: "Elasticsearch cluster health is red for more than 5 minutes"
EOF

    # Add HA monitoring to Prometheus config
    cat >> "$PROJECT_ROOT/deploy/monitoring/prometheus.yml" << 'EOF'

  # HAProxy monitoring
  - job_name: 'haproxy'
    static_configs:
      - targets: 
        - 'haproxy-1:8404'
        - 'haproxy-2:8404'
    metrics_path: '/stats'
    params:
      stats: ['']

  # Consul monitoring
  - job_name: 'consul'
    static_configs:
      - targets:
        - 'consul-1:8500'
        - 'consul-2:8500'
        - 'consul-3:8500'
    metrics_path: '/v1/agent/metrics'
    params:
      format: ['prometheus']

  # Elasticsearch monitoring
  - job_name: 'elasticsearch'
    static_configs:
      - targets:
        - 'elasticsearch-1:9200'
        - 'elasticsearch-2:9200'
        - 'elasticsearch-3:9200'
    metrics_path: '/_prometheus/metrics'
EOF

    log_success "HA cluster monitoring configured"
}

# Verify cluster health
verify_cluster_health() {
    if [[ "$VERIFY_CLUSTER" != true ]]; then
        return 0
    fi
    
    log_info "Verifying HA cluster health..."
    
    # Wait for services to be ready
    log_info "Waiting for HA cluster to stabilize..."
    sleep 60
    
    local health_checks=(
        "http://localhost/health:Main load balancer"
        "http://localhost:8080/health:Backup load balancer"
        "http://localhost:8500/v1/status/leader:Consul leader"
        "http://localhost:9200/_cluster/health:Elasticsearch cluster"
    )
    
    local failed_checks=()
    
    for check in "${health_checks[@]}"; do
        IFS=':' read -r url description <<< "$check"
        
        if curl -f -s "$url" >/dev/null 2>&1; then
            log_success "✓ $description is healthy"
        else
            log_warning "✗ $description is not responding"
            failed_checks+=("$description")
        fi
    done
    
    # Check service discovery
    if command -v curl >/dev/null && curl -s http://localhost:8500/v1/catalog/services | grep -q syn-os; then
        log_success "✓ Service discovery is working"
    else
        log_warning "✗ Service discovery may not be working"
        failed_checks+=("Service discovery")
    fi
    
    # Check load balancing
    log_info "Testing load balancing..."
    local responses=0
    for i in {1..5}; do
        if curl -f -s http://localhost/health >/dev/null; then
            ((responses++))
        fi
        sleep 1
    done
    
    if [[ $responses -ge 4 ]]; then
        log_success "✓ Load balancing is working ($responses/5 successful)"
    else
        log_warning "✗ Load balancing may not be working ($responses/5 successful)"
        failed_checks+=("Load balancing")
    fi
    
    # Summary
    if [[ ${#failed_checks[@]} -eq 0 ]]; then
        log_success "🎉 HA cluster health verification passed!"
    else
        log_warning "⚠ Some health checks failed: ${failed_checks[*]}"
        log_info "Check the logs for more details: docker-compose logs"
    fi
}

# Print cluster information
print_cluster_info() {
    log_info "HA Cluster Information:"
    echo
    echo "🌐 Load Balancer Endpoints:"
    echo "  Primary:   http://localhost (ports 80/443)"
    echo "  Secondary: http://localhost:8080 (ports 8080/8443)"
    echo "  HAProxy Stats: http://localhost:8404/stats"
    echo
    echo "🔧 Management Interfaces:"
    echo "  Consul UI:        http://localhost:8500"
    echo "  Elasticsearch:    http://localhost:9200"
    echo "  Prometheus:       http://localhost:9090"
    echo "  Grafana:          http://localhost:3001"
    echo
    echo "📊 Service Status:"
    echo "  Orchestrator:     3 replicas (ports 8080)"
    echo "  Consciousness:    3 replicas (ports 8081)"
    echo "  Security:         3 replicas (ports 8083)"
    echo "  PostgreSQL:       1 primary + 2 replicas"
    echo "  Redis:            1 master + 2 replicas"
    echo "  NATS:             3-node cluster"
    echo "  Elasticsearch:    3-node cluster"
    echo
    echo "🔍 Monitoring:"
    echo "  HAProxy metrics, Consul health, and service discovery"
    echo "  Centralized logging with Elasticsearch and Filebeat"
    echo "  Enhanced alerting for HA-specific scenarios"
}

# Main function
main() {
    log_info "Setting up Syn_OS High Availability cluster..."
    
    check_prerequisites
    setup_haproxy_config
    setup_keepalived_config
    setup_consul_config
    setup_filebeat_config
    
    case "$DEPLOYMENT_TYPE" in
        docker)
            deploy_docker_ha
            ;;
        kubernetes)
            deploy_kubernetes_ha
            ;;
    esac
    
    setup_ha_monitoring
    verify_cluster_health
    print_cluster_info
    
    log_success "🚀 High Availability cluster setup completed!"
}

# Run main function
main "$@"