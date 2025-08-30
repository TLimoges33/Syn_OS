#!/bin/bash
set -euo pipefail

# Environment Setup Script for Syn_OS
# Sets up production and staging environments with proper configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
ENVIRONMENT="production"
GENERATE_SECRETS=true
SETUP_SSL=false
SETUP_MONITORING=true

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

Set up Syn_OS environment configuration

Options:
    -e, --environment ENV   Environment: staging, production (default: production)
    -s, --setup-ssl        Generate self-signed SSL certificates
    -m, --skip-monitoring  Skip monitoring stack setup
    -n, --no-secrets       Skip generating secrets (use existing)
    -h, --help             Show this help message

Examples:
    $0                           # Setup production environment
    $0 -e staging -s            # Setup staging with SSL
    $0 -n                       # Use existing secrets

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--setup-ssl)
            SETUP_SSL=true
            shift
            ;;
        -m|--skip-monitoring)
            SETUP_MONITORING=false
            shift
            ;;
        -n|--no-secrets)
            GENERATE_SECRETS=false
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

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    exit 1
fi

# Generate secure random string
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "=+/" | cut -c1-64
}

# Generate encryption key
generate_encryption_key() {
    openssl rand -base64 32
}

# Create environment file
create_environment_file() {
    log_info "Creating environment file for $ENVIRONMENT..."
    
    local env_file="$PROJECT_ROOT/.env.$ENVIRONMENT"
    local secrets_needed=$GENERATE_SECRETS
    
    # Check if file exists
    if [[ -f "$env_file" && "$GENERATE_SECRETS" == false ]]; then
        log_info "Using existing environment file: $env_file"
        return 0
    fi
    
    # Generate or preserve secrets
    local postgres_password
    local postgres_replication_password  
    local redis_password
    local jwt_secret
    local encryption_key
    local grafana_password
    
    if [[ -f "$env_file" && "$GENERATE_SECRETS" == false ]]; then
        # Preserve existing secrets
        postgres_password=$(grep "^POSTGRES_PASSWORD=" "$env_file" | cut -d'=' -f2 || echo "")
        postgres_replication_password=$(grep "^POSTGRES_REPLICATION_PASSWORD=" "$env_file" | cut -d'=' -f2 || echo "")
        redis_password=$(grep "^REDIS_PASSWORD=" "$env_file" | cut -d'=' -f2 || echo "")
        jwt_secret=$(grep "^JWT_SECRET_KEY=" "$env_file" | cut -d'=' -f2 || echo "")
        encryption_key=$(grep "^ENCRYPTION_KEY=" "$env_file" | cut -d'=' -f2 || echo "")
        grafana_password=$(grep "^GRAFANA_PASSWORD=" "$env_file" | cut -d'=' -f2 || echo "")
    fi
    
    # Generate missing secrets
    [[ -z "${postgres_password:-}" ]] && postgres_password=$(generate_secret)
    [[ -z "${postgres_replication_password:-}" ]] && postgres_replication_password=$(generate_secret)
    [[ -z "${redis_password:-}" ]] && redis_password=$(generate_secret)
    [[ -z "${jwt_secret:-}" ]] && jwt_secret=$(generate_jwt_secret)
    [[ -z "${encryption_key:-}" ]] && encryption_key=$(generate_encryption_key)
    [[ -z "${grafana_password:-}" ]] && grafana_password=$(generate_secret)
    
    # Create environment file
    cat > "$env_file" << EOF
# Syn_OS $ENVIRONMENT Environment Configuration
# Generated on $(date)

# Environment
ENV=$ENVIRONMENT
NODE_ENV=$ENVIRONMENT
CONSCIOUSNESS_MODE=$ENVIRONMENT

# Container Registry
REGISTRY=${REGISTRY:-ghcr.io/syn-os}
TAG=${TAG:-latest}

# Database Configuration
POSTGRES_DB=syn_os_$ENVIRONMENT
POSTGRES_USER=syn_os
POSTGRES_PASSWORD=$postgres_password
POSTGRES_HOST=postgres-primary
POSTGRES_PORT=5432
POSTGRES_REPLICATION_USER=replicator
POSTGRES_REPLICATION_PASSWORD=$postgres_replication_password

# Redis Configuration
REDIS_PASSWORD=$redis_password
REDIS_HOST=redis-master
REDIS_PORT=6379
REDIS_SENTINEL_HOST=redis-sentinel
REDIS_SENTINEL_PORT=26379

# NATS Configuration
NATS_URL=nats://nats-1:4222,nats://nats-2:4222,nats://nats-3:4222
NATS_CLUSTER_NAME=syn_os_cluster

# Security Configuration
JWT_SECRET_KEY=$jwt_secret
ENCRYPTION_KEY=$encryption_key
BCRYPT_ROUNDS=12
SESSION_TIMEOUT=3600

# Consciousness Configuration
CONSCIOUSNESS_MODEL_PATH=/app/models
CONSCIOUSNESS_LEARNING_RATE=0.001
CONSCIOUSNESS_BATCH_SIZE=32
MAX_DECISION_TIME_MS=100
THREAT_DETECTION_THRESHOLD=0.8

# Security Targets
AUTHENTICATION_TARGET_OPS_PER_SEC=9798
SECURITY_GRADE_TARGET=95
CONSCIOUSNESS_ACCURACY_TARGET=0.95

# Monitoring Configuration
GRAFANA_PASSWORD=$grafana_password
PROMETHEUS_RETENTION=30d
METRICS_INTERVAL=15s

# Logging Configuration
LOG_LEVEL=${LOG_LEVEL:-INFO}
LOG_FORMAT=json
ENABLE_STRUCTURED_LOGGING=true

# Performance Configuration
WORKER_PROCESSES=${WORKER_PROCESSES:-auto}
MAX_REQUESTS_PER_CHILD=1000
KEEPALIVE_TIMEOUT=65

# Feature Flags
ENABLE_CONSCIOUSNESS_ADAPTATION=true
ENABLE_NEURAL_DARWINISM=true
ENABLE_THREAT_PREDICTION=true
ENABLE_REAL_TIME_MONITORING=true

# External Services (configure as needed)
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
# EMAIL_SMTP_HOST=smtp.example.com
# EMAIL_SMTP_PORT=587
# EMAIL_FROM=alerts@syn-os.local

# Development/Debug (only for staging)
EOF

    if [[ "$ENVIRONMENT" == "staging" ]]; then
        cat >> "$env_file" << EOF
DEBUG=true
ENABLE_DEBUG_ENDPOINTS=true
SKIP_AUTH_IN_DEVELOPMENT=false
EOF
    else
        cat >> "$env_file" << EOF
DEBUG=false
ENABLE_DEBUG_ENDPOINTS=false
EOF
    fi
    
    # Secure the environment file
    chmod 600 "$env_file"
    
    log_success "Environment file created: $env_file"
}

# Setup SSL certificates
setup_ssl_certificates() {
    if [[ "$SETUP_SSL" != true ]]; then
        return 0
    fi
    
    log_info "Setting up SSL certificates..."
    
    local ssl_dir="$PROJECT_ROOT/deploy/nginx/ssl"
    mkdir -p "$ssl_dir"
    
    # Generate self-signed certificate if it doesn't exist
    if [[ ! -f "$ssl_dir/server.crt" ]]; then
        log_info "Generating self-signed SSL certificate..."
        
        # Create certificate configuration
        cat > "$ssl_dir/cert.conf" << EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Local
L = Local
O = Syn_OS
CN = syn-os.local

[v3_req]
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = syn-os.local
DNS.2 = localhost
DNS.3 = *.syn-os.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
        
        # Generate private key and certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$ssl_dir/server.key" \
            -out "$ssl_dir/server.crt" \
            -config "$ssl_dir/cert.conf"
        
        # Secure the private key
        chmod 600 "$ssl_dir/server.key"
        chmod 644 "$ssl_dir/server.crt"
        
        # Clean up config file
        rm "$ssl_dir/cert.conf"
        
        log_success "SSL certificate generated"
        log_warning "This is a self-signed certificate. Replace with proper CA-signed certificate for production."
    else
        log_info "SSL certificate already exists"
    fi
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    local dirs=(
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/data"
        "$PROJECT_ROOT/backups"
        "$PROJECT_ROOT/security/scan-results"
        "$PROJECT_ROOT/monitoring/data"
        "$PROJECT_ROOT/deploy/nginx/ssl"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
    
    log_success "Directory structure created"
}

# Setup monitoring
setup_monitoring_stack() {
    if [[ "$SETUP_MONITORING" != true ]]; then
        return 0
    fi
    
    log_info "Setting up monitoring stack..."
    
    # Run the monitoring setup script if it exists
    if [[ -f "$PROJECT_ROOT/scripts/setup-monitoring.sh" ]]; then
        bash "$PROJECT_ROOT/scripts/setup-monitoring.sh"
    else
        log_warning "Monitoring setup script not found. Skipping monitoring setup."
    fi
}

# Validate configuration
validate_configuration() {
    log_info "Validating configuration..."
    
    local env_file="$PROJECT_ROOT/.env.$ENVIRONMENT"
    
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        return 1
    fi
    
    # Source the environment file
    source "$env_file"
    
    # Check required variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET_KEY"
        "ENCRYPTION_KEY"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required variables: ${missing_vars[*]}"
        return 1
    fi
    
    log_success "Configuration validation passed"
}

# Print setup summary
print_summary() {
    log_info "Environment setup completed!"
    echo
    echo "Configuration Summary:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Environment file: .env.$ENVIRONMENT"
    echo "  SSL certificates: $([ "$SETUP_SSL" == true ] && echo "Generated" || echo "Not generated")"
    echo "  Monitoring: $([ "$SETUP_MONITORING" == true ] && echo "Configured" || echo "Skipped")"
    echo
    log_info "Next steps:"
    echo "  1. Review and customize .env.$ENVIRONMENT"
    echo "  2. Build containers: ./scripts/build-containers.sh"
    echo "  3. Deploy: ./scripts/deploy-production.sh -e $ENVIRONMENT"
    echo
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_warning "For production:"
        echo "  - Replace self-signed SSL certificates with CA-signed certificates"
        echo "  - Configure external monitoring and alerting endpoints"
        echo "  - Set up proper backup and disaster recovery procedures"
        echo "  - Review and harden security configuration"
    fi
}

# Main function
main() {
    log_info "Setting up Syn_OS $ENVIRONMENT environment..."
    
    create_directories
    create_environment_file
    setup_ssl_certificates
    setup_monitoring_stack
    validate_configuration
    print_summary
    
    log_success "🎉 Environment setup completed successfully!"
}

# Run main function
main "$@"