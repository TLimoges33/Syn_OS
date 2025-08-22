#!/bin/bash

# ============================================================================
# SynapticOS Container Infrastructure Setup Script
# ============================================================================
# Description: Complete setup script for SynapticOS container infrastructure
# Author: SynapticOS Team
# Version: 1.0.0
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if user is in docker group
    if ! groups | grep -q docker; then
        log_warning "User is not in docker group. You may need to run docker commands with sudo."
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    local dirs=(
        "logs/security"
        "logs/nginx"
        "config/nats"
        "config/postgres"
        "config/redis"
        "config/nginx/conf.d"
        "certs/zero_trust"
        "data/backups"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    log_success "Directory structure created"
}

# Generate secure secrets
generate_secrets() {
    log_info "Generating secure secrets..."
    
    # Function to generate random string
    generate_random() {
        openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
    }
    
    # Generate strong passwords
    POSTGRES_PASSWORD=$(generate_random)
    REDIS_PASSWORD=$(generate_random)
    NATS_PASSWORD=$(generate_random)
    JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
    ENCRYPTION_KEY=$(generate_random)
    SIGNING_KEY=$(generate_random)
    CONSCIOUSNESS_KEY=$(generate_random)
    INTERNAL_API_KEY=$(generate_random)
    GRAFANA_PASSWORD=$(generate_random)
    
    log_success "Secure secrets generated"
}

# Create production environment file
create_production_env() {
    log_info "Creating production environment file..."
    
    if [[ -f ".env.production" ]]; then
        log_warning ".env.production already exists. Creating backup..."
        cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Create production environment file with generated secrets
    cat > .env.production << EOF
# SynapticOS Production Environment Configuration
# Generated on $(date)

# Core System
ENV=production
LOG_LEVEL=WARN
DEBUG=false

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=syn_os_prod
POSTGRES_USER=syn_os_prod_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_SSL_MODE=require

# Cache Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_DB=0

# Message Bus Configuration
NATS_URL=nats://nats:4222
NATS_CLUSTER_ID=syn-os-prod-cluster
NATS_CLIENT_ID=syn-os-prod-client
NATS_USERNAME=orchestrator_prod
NATS_PASSWORD=${NATS_PASSWORD}
NATS_MAX_RECONNECT=10

# NATS JetStream Configuration
NATS_JETSTREAM_ENABLED=true
NATS_STREAM_REPLICAS=1
NATS_MAX_MEMORY_STORE=4GB
NATS_MAX_FILE_STORE=50GB

# Service Configuration
HTTP_PORT=8080
ORCHESTRATOR_URL=http://orchestrator:8080
CONSCIOUSNESS_URL=http://consciousness:8081
CONSCIOUSNESS_MODE=production
CONSCIOUSNESS_ENCRYPTION_KEY=${CONSCIOUSNESS_KEY}

# Application Ports
SECURITY_DASHBOARD_PORT=8083
LEARNING_HUB_PORT=8084
SECURITY_TUTOR_PORT=8085
WEB_DASHBOARD_PORT=8086
THREAT_INTEL_PORT=8087

# Security Configuration
JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1
ENCRYPTION_KEY=${ENCRYPTION_KEY}
SIGNING_KEY=${SIGNING_KEY}
INTERNAL_API_KEY=${INTERNAL_API_KEY}

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

# Health Checks
HEALTH_CHECK_INTERVAL=15
HEALTH_CHECK_TIMEOUT=5
HEALTH_CHECK_RETRIES=3

# Production Settings
DEVELOPMENT_MODE=false
SYN_OS_DEV_ENV=false
SECURITY_ENABLED=true

# NATS Advanced Configuration
NATS_CONNECTION_POOL_SIZE=20
NATS_CONNECTION_TIMEOUT=10s
NATS_RECONNECT_WAIT=2s
NATS_MESSAGE_MAX_SIZE=10MB
NATS_MESSAGE_TTL=1h
NATS_ACK_WAIT=10s
NATS_MONITORING_PORT=8222
NATS_SURVEYOR_PORT=7777

# Consciousness System Configuration
NEURAL_POPULATION_SIZE=500
NEURAL_MUTATION_RATE=0.05
NEURAL_SELECTION_PRESSURE=0.9
CONSCIOUSNESS_PROCESSING_THREADS=8
CONSCIOUSNESS_MEMORY_LIMIT=4GB
CONSCIOUSNESS_CACHE_SIZE=10000
LEARNING_RATE=0.001
ADAPTATION_THRESHOLD=0.85
CONTEXT_WINDOW_SIZE=5000
EOF
    
    chmod 600 .env.production
    log_success "Production environment file created with secure permissions"
}

# Create NATS auth configuration
create_nats_config() {
    log_info "Creating NATS authentication configuration..."
    
    cat > config/nats/auth.conf << EOF
# NATS Authentication Configuration
authorization {
    users = [
        {
            user: "orchestrator_prod"
            password: "${NATS_PASSWORD}"
            permissions = {
                publish = ["orchestrator.>", "consciousness.>", "security.>"]
                subscribe = ["orchestrator.>", "consciousness.>", "security.>"]
            }
        }
    ]
}
EOF
    
    chmod 600 config/nats/auth.conf
    log_success "NATS authentication configuration created"
}

# Create Nginx configuration
create_nginx_config() {
    log_info "Creating Nginx configuration..."
    
    cat > config/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    include /etc/nginx/conf.d/*.conf;
}
EOF
    
    cat > config/nginx/conf.d/syn_os.conf << 'EOF'
upstream orchestrator {
    server orchestrator:8080;
}

upstream consciousness {
    server consciousness:8081;
}

upstream security_dashboard {
    server security-dashboard:8083;
}

upstream learning_hub {
    server learning-hub:8084;
}

upstream security_tutor {
    server security-tutor:8085;
}

upstream web_dashboard {
    server web-dashboard:8086;
}

upstream threat_intelligence {
    server threat-intelligence:8087;
}

server {
    listen 80;
    server_name localhost;
    
    # Redirect HTTP to HTTPS in production
    # return 301 https://$server_name$request_uri;
    
    # API Gateway
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://orchestrator/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Consciousness Service
    location /consciousness/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://consciousness/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security Dashboard
    location /security/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://security_dashboard/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Learning Hub
    location /learning/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://learning_hub/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security Tutor
    location /tutor/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://security_tutor/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Web Dashboard (default)
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://web_dashboard/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Threat Intelligence
    location /threats/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://threat_intelligence/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    log_success "Nginx configuration created"
}

# Create PostgreSQL configuration
create_postgres_config() {
    log_info "Creating PostgreSQL configuration..."
    
    cat > config/postgres/postgresql.conf << 'EOF'
# PostgreSQL Production Configuration for SynapticOS

# Connection Settings
listen_addresses = '*'
port = 5432
max_connections = 100
superuser_reserved_connections = 3

# Memory Settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Security Settings
ssl = on
ssl_ciphers = 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384'
ssl_prefer_server_ciphers = on
password_encryption = scram-sha-256

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_size = 10MB
log_min_messages = warning
log_min_error_statement = error
log_min_duration_statement = 1000
log_connections = on
log_disconnections = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Performance
checkpoint_timeout = 5min
checkpoint_completion_target = 0.9
archive_mode = on
archive_command = '/bin/true'
max_wal_size = 1GB
min_wal_size = 80MB
EOF
    
    log_success "PostgreSQL configuration created"
}

# Create Redis configuration
create_redis_config() {
    log_info "Creating Redis configuration..."
    
    cat > config/redis/redis.conf << EOF
# Redis Production Configuration for SynapticOS

# Network
bind 0.0.0.0
port 6379
timeout 300
keepalive 300

# Security
requirepass ${REDIS_PASSWORD}
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG "CONFIG_b835529a8b2e1d3c"

# Memory Management
maxmemory 1gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# Append Only File
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes

# Logging
loglevel notice
logfile /data/redis.log

# Performance
tcp-keepalive 300
tcp-backlog 511
databases 16
EOF
    
    log_success "Redis configuration created"
}

# Generate self-signed certificates for development
generate_dev_certificates() {
    log_info "Generating development SSL certificates..."
    
    if [[ ! -f "certs/syn_os.crt" ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout certs/syn_os.key \
            -out certs/syn_os.crt \
            -subj "/C=US/ST=DevState/L=DevCity/O=SynapticOS/CN=localhost"
        
        chmod 600 certs/syn_os.key
        chmod 644 certs/syn_os.crt
        
        log_success "Development SSL certificates generated"
    else
        log_info "SSL certificates already exist"
    fi
}

# Set proper file permissions
set_permissions() {
    log_info "Setting secure file permissions..."
    
    # Secure environment files
    chmod 600 .env* 2>/dev/null || true
    
    # Secure config files
    chmod 600 config/nats/auth.conf 2>/dev/null || true
    chmod 600 config/redis/redis.conf 2>/dev/null || true
    
    # Secure certificate files
    chmod 600 certs/*.key 2>/dev/null || true
    chmod 644 certs/*.crt 2>/dev/null || true
    
    log_success "File permissions set securely"
}

# Build container images
build_images() {
    local mode=${1:-development}
    
    log_info "Building container images for $mode..."
    
    if [[ "$mode" == "production" ]]; then
        docker-compose -f docker-compose.production.yml build --no-cache
    else
        docker-compose build --no-cache
    fi
    
    log_success "Container images built successfully"
}

# Start services
start_services() {
    local mode=${1:-development}
    
    log_info "Starting SynapticOS services in $mode mode..."
    
    if [[ "$mode" == "production" ]]; then
        docker-compose -f docker-compose.production.yml up -d
    else
        docker-compose up -d
    fi
    
    log_success "Services started successfully"
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    local services=(
        "http://localhost:8080/health:Orchestrator"
        "http://localhost:8081/health:Consciousness"
        "http://localhost:8083/health:Security Dashboard"
        "http://localhost:8084/health:Learning Hub"
        "http://localhost:8085/health:Security Tutor"
        "http://localhost:8086/health:Web Dashboard"
        "http://localhost:8087/health:Threat Intelligence"
    )
    
    log_info "Waiting for services to start..."
    sleep 30
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        if curl -f -s "$url" >/dev/null 2>&1; then
            log_success "$name is healthy"
        else
            log_warning "$name health check failed"
        fi
    done
}

# Display summary
display_summary() {
    local mode=${1:-development}
    
    echo
    log_success "SynapticOS Container Infrastructure Setup Complete!"
    echo
    echo "=============================================================="
    echo "                   SERVICE ENDPOINTS"
    echo "=============================================================="
    echo "Orchestrator API:          http://localhost:8080"
    echo "Consciousness Service:     http://localhost:8081"
    echo "Security Dashboard:        http://localhost:8083"
    echo "Learning Hub:              http://localhost:8084"
    echo "Security Tutor:            http://localhost:8085"
    echo "Web Dashboard:             http://localhost:8086"
    echo "Threat Intelligence:       http://localhost:8087"
    echo "NATS Monitoring:           http://localhost:8222"
    echo "NATS Surveyor:             http://localhost:7777"
    echo
    echo "=============================================================="
    echo "                    IMPORTANT NOTES"
    echo "=============================================================="
    
    if [[ "$mode" == "production" ]]; then
        echo "✓ Production environment configured"
        echo "✓ Secure secrets generated and stored in .env.production"
        echo "✓ Production-grade security settings applied"
        echo "✓ SSL certificates ready (replace with production certs)"
        echo
        echo "⚠️  PRODUCTION CHECKLIST:"
        echo "   - Replace development SSL certificates with production ones"
        echo "   - Review and update firewall rules"
        echo "   - Set up proper backup procedures"
        echo "   - Configure external monitoring"
        echo "   - Review and test disaster recovery procedures"
    else
        echo "✓ Development environment configured"
        echo "✓ Self-signed SSL certificates generated"
        echo "✓ All services running with development settings"
    fi
    
    echo
    echo "Generated credentials are stored in .env.production"
    echo "Keep this file secure and never commit it to version control!"
    echo
    echo "=============================================================="
    echo "                     USEFUL COMMANDS"
    echo "=============================================================="
    if [[ "$mode" == "production" ]]; then
        echo "View logs:                 docker-compose -f docker-compose.production.yml logs -f"
        echo "Stop services:             docker-compose -f docker-compose.production.yml down"
        echo "Restart services:          docker-compose -f docker-compose.production.yml restart"
        echo "View service status:       docker-compose -f docker-compose.production.yml ps"
    else
        echo "View logs:                 docker-compose logs -f"
        echo "Stop services:             docker-compose down"
        echo "Restart services:          docker-compose restart"
        echo "View service status:       docker-compose ps"
    fi
    echo "=============================================================="
}

# Main function
main() {
    local mode=${1:-development}
    
    echo "=============================================================="
    echo "         SynapticOS Container Infrastructure Setup"
    echo "=============================================================="
    echo "Mode: $mode"
    echo "Date: $(date)"
    echo "=============================================================="
    
    check_root
    check_prerequisites
    create_directories
    generate_secrets
    
    if [[ "$mode" == "production" ]]; then
        create_production_env
    fi
    
    create_nats_config
    create_nginx_config
    create_postgres_config
    create_redis_config
    generate_dev_certificates
    set_permissions
    
    read -p "Build and start services now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_images "$mode"
        start_services "$mode"
        health_check
    fi
    
    display_summary "$mode"
}

# Handle command line arguments
case "${1:-development}" in
    "production"|"prod")
        main "production"
        ;;
    "development"|"dev"|"")
        main "development"
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [mode]"
        echo "Modes: development (default), production"
        echo
        echo "Examples:"
        echo "  $0                    # Setup development environment"
        echo "  $0 development        # Setup development environment"
        echo "  $0 production         # Setup production environment"
        exit 0
        ;;
    *)
        log_error "Invalid mode: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
