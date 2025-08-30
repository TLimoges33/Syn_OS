#!/bin/bash
set -euo pipefail

# Production Configuration Management Script for Syn_OS
# Manages configuration, secrets, and environment variables across deployments

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
ENVIRONMENT="production"
ACTION="sync"
CONFIG_SOURCE="local"
BACKUP_CONFIGS=true
VALIDATE_CONFIGS=true

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

Manage Syn_OS production configuration and secrets

Options:
    -e, --environment ENV   Environment: staging, production (default: production)
    -a, --action ACTION     Action: sync, backup, restore, validate (default: sync)
    -s, --source SOURCE     Config source: local, vault, consul (default: local)
    -b, --no-backup        Skip configuration backup
    -v, --skip-validation  Skip configuration validation
    -h, --help             Show this help message

Actions:
    sync        Synchronize configuration across all services
    backup      Create backup of current configuration
    restore     Restore configuration from backup
    validate    Validate all configuration files
    rotate      Rotate secrets and update configuration

Examples:
    $0                          # Sync production configuration
    $0 -a backup               # Backup current configuration
    $0 -a restore -e staging   # Restore staging configuration
    $0 -a rotate               # Rotate all secrets

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -s|--source)
            CONFIG_SOURCE="$2"
            shift 2
            ;;
        -b|--no-backup)
            BACKUP_CONFIGS=false
            shift
            ;;
        -v|--skip-validation)
            VALIDATE_CONFIGS=false
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
    log_info "Checking configuration management prerequisites..."
    
    local missing_tools=()
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v openssl >/dev/null 2>&1 || missing_tools+=("openssl")
    command -v jq >/dev/null 2>&1 || missing_tools+=("jq")
    
    if [[ "$CONFIG_SOURCE" == "vault" ]]; then
        command -v vault >/dev/null 2>&1 || missing_tools+=("vault")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Configuration validation schemas
create_validation_schemas() {
    log_info "Creating configuration validation schemas..."
    
    mkdir -p "$PROJECT_ROOT/config/schemas"
    
    # Environment variable schema
    cat > "$PROJECT_ROOT/config/schemas/environment.json" << 'EOF'
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Syn_OS Environment Configuration",
    "type": "object",
    "required": [
        "ENV",
        "POSTGRES_PASSWORD",
        "REDIS_PASSWORD",
        "JWT_SECRET_KEY",
        "ENCRYPTION_KEY"
    ],
    "properties": {
        "ENV": {
            "type": "string",
            "enum": ["development", "staging", "production"]
        },
        "POSTGRES_PASSWORD": {
            "type": "string",
            "minLength": 16,
            "pattern": "^[A-Za-z0-9+/=]+$"
        },
        "REDIS_PASSWORD": {
            "type": "string",
            "minLength": 16,
            "pattern": "^[A-Za-z0-9+/=]+$"
        },
        "JWT_SECRET_KEY": {
            "type": "string",
            "minLength": 32,
            "pattern": "^[A-Za-z0-9+/=]+$"
        },
        "ENCRYPTION_KEY": {
            "type": "string",
            "minLength": 24,
            "pattern": "^[A-Za-z0-9+/=]+$"
        },
        "CONSCIOUSNESS_MODE": {
            "type": "string",
            "enum": ["development", "production"]
        },
        "DEBUG": {
            "type": "string",
            "enum": ["true", "false"]
        }
    },
    "additionalProperties": true
}
EOF

    # Docker Compose configuration schema
    cat > "$PROJECT_ROOT/config/schemas/docker-compose.json" << 'EOF'
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Docker Compose Configuration",
    "type": "object",
    "required": ["version", "services"],
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^3\\.[0-9]+$"
        },
        "services": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "image": {"type": "string"},
                        "environment": {
                            "oneOf": [
                                {"type": "array"},
                                {"type": "object"}
                            ]
                        },
                        "ports": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "volumes": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}
EOF

    log_success "Validation schemas created"
}

# Configuration template system
create_config_templates() {
    log_info "Creating configuration templates..."
    
    mkdir -p "$PROJECT_ROOT/config/templates"
    
    # Environment template
    cat > "$PROJECT_ROOT/config/templates/environment.template" << 'EOF'
# Syn_OS {{ENVIRONMENT}} Environment Configuration
# Generated on {{TIMESTAMP}}

# Environment
ENV={{ENVIRONMENT}}
NODE_ENV={{ENVIRONMENT}}
CONSCIOUSNESS_MODE={{ENVIRONMENT}}

# Container Registry
REGISTRY={{REGISTRY}}
TAG={{TAG}}

# Database Configuration
POSTGRES_DB=syn_os_{{ENVIRONMENT}}
POSTGRES_USER=syn_os
POSTGRES_PASSWORD={{POSTGRES_PASSWORD}}
POSTGRES_HOST={{POSTGRES_HOST}}
POSTGRES_PORT=5432
POSTGRES_REPLICATION_USER=replicator
POSTGRES_REPLICATION_PASSWORD={{POSTGRES_REPLICATION_PASSWORD}}

# Redis Configuration
REDIS_PASSWORD={{REDIS_PASSWORD}}
REDIS_HOST={{REDIS_HOST}}
REDIS_PORT=6379
REDIS_SENTINEL_HOST={{REDIS_SENTINEL_HOST}}
REDIS_SENTINEL_PORT=26379

# NATS Configuration
NATS_URL={{NATS_URL}}
NATS_CLUSTER_NAME=syn_os_cluster

# Security Configuration
JWT_SECRET_KEY={{JWT_SECRET_KEY}}
ENCRYPTION_KEY={{ENCRYPTION_KEY}}
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
GRAFANA_PASSWORD={{GRAFANA_PASSWORD}}
PROMETHEUS_RETENTION=30d
METRICS_INTERVAL=15s

# Logging Configuration
LOG_LEVEL={{LOG_LEVEL}}
LOG_FORMAT=json
ENABLE_STRUCTURED_LOGGING=true

# Performance Configuration
WORKER_PROCESSES={{WORKER_PROCESSES}}
MAX_REQUESTS_PER_CHILD=1000
KEEPALIVE_TIMEOUT=65

# Feature Flags
ENABLE_CONSCIOUSNESS_ADAPTATION=true
ENABLE_NEURAL_DARWINISM=true
ENABLE_THREAT_PREDICTION=true
ENABLE_REAL_TIME_MONITORING=true

# High Availability
HAPROXY_STATS_PASSWORD={{HAPROXY_STATS_PASSWORD}}
KEEPALIVED_PASSWORD={{KEEPALIVED_PASSWORD}}

# External Services
{{#SLACK_WEBHOOK_URL}}
SLACK_WEBHOOK_URL={{SLACK_WEBHOOK_URL}}
{{/SLACK_WEBHOOK_URL}}
{{#EMAIL_SMTP_HOST}}
EMAIL_SMTP_HOST={{EMAIL_SMTP_HOST}}
EMAIL_SMTP_PORT={{EMAIL_SMTP_PORT}}
EMAIL_FROM={{EMAIL_FROM}}
{{/EMAIL_SMTP_HOST}}

# Development/Debug
{{#DEBUG}}
DEBUG={{DEBUG}}
ENABLE_DEBUG_ENDPOINTS={{ENABLE_DEBUG_ENDPOINTS}}
{{/DEBUG}}
EOF

    # Docker Compose override template
    cat > "$PROJECT_ROOT/config/templates/docker-compose.override.template" << 'EOF'
# Docker Compose Override for {{ENVIRONMENT}}
version: '3.8'

services:
  orchestrator-1:
    environment:
      - LOG_LEVEL={{LOG_LEVEL}}
      - DEBUG={{DEBUG}}
    {{#DEVELOPMENT}}
    ports:
      - "8080:8080"
    {{/DEVELOPMENT}}

  consciousness-1:
    environment:
      - LOG_LEVEL={{LOG_LEVEL}}
      - CONSCIOUSNESS_MODE={{CONSCIOUSNESS_MODE}}
    {{#DEVELOPMENT}}
    ports:
      - "8081:8081"
    {{/DEVELOPMENT}}

  security-dashboard-1:
    environment:
      - LOG_LEVEL={{LOG_LEVEL}}
    {{#DEVELOPMENT}}
    ports:
      - "8083:8083"
    {{/DEVELOPMENT}}

{{#PRODUCTION}}
  prometheus:
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time={{PROMETHEUS_RETENTION}}'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'

  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD={{GRAFANA_PASSWORD}}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_ANALYTICS_REPORTING_ENABLED=false
{{/PRODUCTION}}
EOF

    log_success "Configuration templates created"
}

# Configuration generation engine
generate_configuration() {
    local template_file="$1"
    local output_file="$2"
    local config_vars="$3"
    
    log_info "Generating configuration from template: $(basename "$template_file")"
    
    # Simple template engine using envsubst
    local temp_file=$(mktemp)
    
    # Load configuration variables
    source "$config_vars"
    
    # Generate timestamp
    export TIMESTAMP=$(date -Iseconds)
    
    # Process template
    envsubst < "$template_file" > "$temp_file"
    
    # Handle conditional blocks (simple implementation)
    if [[ "$ENVIRONMENT" == "production" ]]; then
        sed -i '/{{#PRODUCTION}}/,/{{\/PRODUCTION}}/s/{{#PRODUCTION}}\|{{\/PRODUCTION}}//g' "$temp_file"
        sed -i '/{{#DEVELOPMENT}}/,/{{\/DEVELOPMENT}}/d' "$temp_file"
    else
        sed -i '/{{#DEVELOPMENT}}/,/{{\/DEVELOPMENT}}/s/{{#DEVELOPMENT}}\|{{\/DEVELOPMENT}}//g' "$temp_file"
        sed -i '/{{#PRODUCTION}}/,/{{\/PRODUCTION}}/d' "$temp_file"
    fi
    
    # Remove empty conditional blocks
    sed -i '/{{#.*}}/d; /{{\/.*}}/d' "$temp_file"
    
    # Move to final location
    mv "$temp_file" "$output_file"
    
    log_success "Configuration generated: $output_file"
}

# Validate configuration files
validate_configuration() {
    if [[ "$VALIDATE_CONFIGS" != true ]]; then
        return 0
    fi
    
    log_info "Validating configuration files..."
    
    local validation_errors=()
    
    # Validate environment file
    local env_file=".env.$ENVIRONMENT"
    if [[ -f "$env_file" ]]; then
        # Convert env file to JSON for validation
        local env_json=$(mktemp)
        cat "$env_file" | grep -E '^[A-Z_]+=.*' | sed 's/^\([^=]*\)=\(.*\)$/"\1": "\2",/' | sed '$ s/,$//' | sed '1s/^/{/' | sed '$ s/$/}/' > "$env_json"
        
        if jq -e . "$env_json" >/dev/null 2>&1; then
            if jsonschema -i "$env_json" "$PROJECT_ROOT/config/schemas/environment.json" >/dev/null 2>&1; then
                log_success "✓ Environment configuration is valid"
            else
                validation_errors+=("Environment configuration validation failed")
            fi
        else
            validation_errors+=("Environment file is not valid JSON-convertible")
        fi
        
        rm -f "$env_json"
    else
        validation_errors+=("Environment file $env_file not found")
    fi
    
    # Validate Docker Compose files
    for compose_file in docker-compose.yml deploy/docker-compose.*.yml; do
        if [[ -f "$compose_file" ]]; then
            if docker-compose -f "$compose_file" config >/dev/null 2>&1; then
                log_success "✓ $(basename "$compose_file") is valid"
            else
                validation_errors+=("$(basename "$compose_file") validation failed")
            fi
        fi
    done
    
    # Validate Prometheus configuration
    if [[ -f "deploy/monitoring/prometheus.yml" ]]; then
        if docker run --rm -v "$PWD/deploy/monitoring:/etc/prometheus" prom/prometheus:latest promtool check config /etc/prometheus/prometheus.yml >/dev/null 2>&1; then
            log_success "✓ Prometheus configuration is valid"
        else
            validation_errors+=("Prometheus configuration validation failed")
        fi
    fi
    
    # Validate HAProxy configuration
    if [[ -f "deploy/haproxy/haproxy.cfg" ]]; then
        if docker run --rm -v "$PWD/deploy/haproxy:/usr/local/etc/haproxy" haproxy:2.8-alpine haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg >/dev/null 2>&1; then
            log_success "✓ HAProxy configuration is valid"
        else
            validation_errors+=("HAProxy configuration validation failed")
        fi
    fi
    
    # Report validation results
    if [[ ${#validation_errors[@]} -eq 0 ]]; then
        log_success "All configuration files are valid"
        return 0
    else
        log_error "Configuration validation errors found:"
        for error in "${validation_errors[@]}"; do
            echo "  - $error"
        done
        return 1
    fi
}

# Backup configuration
backup_configuration() {
    if [[ "$BACKUP_CONFIGS" != true && "$ACTION" != "backup" ]]; then
        return 0
    fi
    
    log_info "Creating configuration backup..."
    
    local backup_dir="$PROJECT_ROOT/backups/config/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup environment files
    cp .env.* "$backup_dir/" 2>/dev/null || true
    
    # Backup configuration files
    cp -r deploy/ "$backup_dir/" 2>/dev/null || true
    cp -r config/ "$backup_dir/" 2>/dev/null || true
    
    # Backup Docker Compose files
    cp docker-compose*.yml "$backup_dir/" 2>/dev/null || true
    
    # Create backup manifest
    cat > "$backup_dir/manifest.json" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "environment": "$ENVIRONMENT",
    "backup_type": "configuration",
    "files_included": [
        "environment_files",
        "deploy_configs",
        "docker_compose_files",
        "monitoring_configs",
        "security_configs"
    ]
}
EOF

    # Compress backup
    tar -czf "$backup_dir.tar.gz" -C "$(dirname "$backup_dir")" "$(basename "$backup_dir")"
    rm -rf "$backup_dir"
    
    log_success "Configuration backup created: $backup_dir.tar.gz"
}

# Restore configuration
restore_configuration() {
    if [[ "$ACTION" != "restore" ]]; then
        return 0
    fi
    
    log_info "Restoring configuration from backup..."
    
    # Find latest backup if no specific backup specified
    local backup_file
    if [[ -z "${BACKUP_FILE:-}" ]]; then
        backup_file=$(find "$PROJECT_ROOT/backups/config/" -name "*.tar.gz" -type f | sort -r | head -1)
        if [[ -z "$backup_file" ]]; then
            log_error "No backup files found"
            exit 1
        fi
        log_info "Using latest backup: $(basename "$backup_file")"
    else
        backup_file="$BACKUP_FILE"
    fi
    
    # Create temporary extraction directory
    local temp_dir=$(mktemp -d)
    
    # Extract backup
    tar -xzf "$backup_file" -C "$temp_dir"
    local extracted_dir=$(find "$temp_dir" -maxdepth 1 -type d | tail -1)
    
    # Restore files
    cp "$extracted_dir"/.env.* . 2>/dev/null || true
    cp -r "$extracted_dir"/deploy/* deploy/ 2>/dev/null || true
    cp -r "$extracted_dir"/config/* config/ 2>/dev/null || true
    cp "$extracted_dir"/docker-compose*.yml . 2>/dev/null || true
    
    # Cleanup
    rm -rf "$temp_dir"
    
    log_success "Configuration restored from backup"
}

# Sync configuration across services
sync_configuration() {
    if [[ "$ACTION" != "sync" ]]; then
        return 0
    fi
    
    log_info "Synchronizing configuration across services..."
    
    # Load current environment
    local env_file=".env.$ENVIRONMENT"
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file $env_file not found"
        exit 1
    fi
    
    source "$env_file"
    
    # Generate configuration from templates
    if [[ -f "$PROJECT_ROOT/config/templates/environment.template" ]]; then
        generate_configuration \
            "$PROJECT_ROOT/config/templates/environment.template" \
            "$PROJECT_ROOT/.env.$ENVIRONMENT.generated" \
            "$env_file"
    fi
    
    # Sync with Consul if available
    if [[ "$CONFIG_SOURCE" == "consul" ]] && command -v consul >/dev/null; then
        log_info "Syncing configuration with Consul..."
        
        # Upload environment variables to Consul KV
        while IFS='=' read -r key value; do
            if [[ "$key" =~ ^[A-Z_]+ ]]; then
                consul kv put "syn-os/$ENVIRONMENT/config/$key" "$value" >/dev/null
            fi
        done < "$env_file"
        
        log_success "Configuration synced with Consul"
    fi
    
    # Sync with Vault if available
    if [[ "$CONFIG_SOURCE" == "vault" ]] && command -v vault >/dev/null; then
        log_info "Syncing secrets with Vault..."
        
        # Store secrets in Vault
        vault kv put secret/syn-os/$ENVIRONMENT \
            postgres_password="$POSTGRES_PASSWORD" \
            redis_password="$REDIS_PASSWORD" \
            jwt_secret_key="$JWT_SECRET_KEY" \
            encryption_key="$ENCRYPTION_KEY" \
            >/dev/null
        
        log_success "Secrets synced with Vault"
    fi
    
    # Update Docker services with new configuration
    if docker-compose ps | grep -q "syn_os"; then
        log_info "Reloading services with updated configuration..."
        docker-compose -f docker-compose.yml -f "deploy/docker-compose.$ENVIRONMENT.yml" up -d --force-recreate
        log_success "Services reloaded with updated configuration"
    fi
}

# Rotate secrets
rotate_secrets() {
    if [[ "$ACTION" != "rotate" ]]; then
        return 0
    fi
    
    log_info "Rotating secrets for $ENVIRONMENT environment..."
    
    # Create backup before rotation
    backup_configuration
    
    # Generate new secrets
    local new_postgres_pass=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    local new_redis_pass=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    local new_jwt_secret=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
    local new_encryption_key=$(openssl rand -base64 32)
    local new_grafana_pass=$(openssl rand -base64 16)
    local new_haproxy_pass=$(openssl rand -base64 16)
    local new_keepalived_pass=$(openssl rand -base64 16)
    
    # Update environment file
    local env_file=".env.$ENVIRONMENT"
    local temp_file=$(mktemp)
    
    # Replace secrets in environment file
    sed "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$new_postgres_pass/" "$env_file" |
    sed "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$new_redis_pass/" |
    sed "s/^JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$new_jwt_secret/" |
    sed "s/^ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$new_encryption_key/" |
    sed "s/^GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=$new_grafana_pass/" |
    sed "s/^HAPROXY_STATS_PASSWORD=.*/HAPROXY_STATS_PASSWORD=$new_haproxy_pass/" |
    sed "s/^KEEPALIVED_PASSWORD=.*/KEEPALIVED_PASSWORD=$new_keepalived_pass/" > "$temp_file"
    
    mv "$temp_file" "$env_file"
    
    # Update Docker secrets
    if command -v docker >/dev/null; then
        log_info "Updating Docker secrets..."
        
        # Remove old secrets
        docker secret rm "syn_os_postgres_password_$ENVIRONMENT" 2>/dev/null || true
        docker secret rm "syn_os_redis_password_$ENVIRONMENT" 2>/dev/null || true
        docker secret rm "syn_os_jwt_secret_$ENVIRONMENT" 2>/dev/null || true
        docker secret rm "syn_os_encryption_key_$ENVIRONMENT" 2>/dev/null || true
        
        # Create new secrets
        echo "$new_postgres_pass" | docker secret create "syn_os_postgres_password_$ENVIRONMENT" -
        echo "$new_redis_pass" | docker secret create "syn_os_redis_password_$ENVIRONMENT" -
        echo "$new_jwt_secret" | docker secret create "syn_os_jwt_secret_$ENVIRONMENT" -
        echo "$new_encryption_key" | docker secret create "syn_os_encryption_key_$ENVIRONMENT" -
    fi
    
    log_success "Secrets rotated successfully"
    log_warning "Services need to be restarted to use new secrets"
}

# Configuration drift detection
detect_configuration_drift() {
    log_info "Detecting configuration drift..."
    
    local drift_detected=false
    local drift_report="$PROJECT_ROOT/config/drift-report-$(date +%Y%m%d_%H%M%S).json"
    
    echo '{"drift_analysis": {' > "$drift_report"
    echo '"timestamp": "'$(date -Iseconds)'",' >> "$drift_report"
    echo '"environment": "'$ENVIRONMENT'",' >> "$drift_report"
    echo '"checks": [' >> "$drift_report"
    
    # Check environment file against template
    if [[ -f "$PROJECT_ROOT/config/templates/environment.template" ]]; then
        local expected_vars=$(grep -o '{{[A-Z_]*}}' "$PROJECT_ROOT/config/templates/environment.template" | sed 's/[{}]//g' | sort -u)
        local actual_vars=$(grep -o '^[A-Z_]*=' ".env.$ENVIRONMENT" | sed 's/=$//' | sort)
        
        local missing_vars=$(comm -23 <(echo "$expected_vars") <(echo "$actual_vars"))
        local extra_vars=$(comm -13 <(echo "$expected_vars") <(echo "$actual_vars"))
        
        if [[ -n "$missing_vars" || -n "$extra_vars" ]]; then
            drift_detected=true
            echo '{"check": "environment_variables", "status": "drift", "missing": "'$missing_vars'", "extra": "'$extra_vars'"},' >> "$drift_report"
        else
            echo '{"check": "environment_variables", "status": "ok"},' >> "$drift_report"
        fi
    fi
    
    # Check Docker Compose configuration
    local expected_services="orchestrator consciousness security-dashboard postgres redis nats"
    local actual_services=$(docker-compose -f docker-compose.yml -f "deploy/docker-compose.$ENVIRONMENT.yml" config --services | tr '\n' ' ')
    
    for service in $expected_services; do
        if [[ "$actual_services" != *"$service"* ]]; then
            drift_detected=true
            echo '{"check": "docker_services", "status": "drift", "missing_service": "'$service'"},' >> "$drift_report"
        fi
    done
    
    # Finalize report
    sed -i '$ s/,$//' "$drift_report"
    echo ']},' >> "$drift_report"
    echo '"drift_detected": '$drift_detected >> "$drift_report"
    echo '}' >> "$drift_report"
    
    if [[ "$drift_detected" == true ]]; then
        log_warning "Configuration drift detected. Report: $drift_report"
        return 1
    else
        log_success "No configuration drift detected"
        rm -f "$drift_report"
        return 0
    fi
}

# Main action dispatcher
main() {
    log_info "Starting Syn_OS configuration management..."
    
    check_prerequisites
    create_validation_schemas
    create_config_templates
    
    case "$ACTION" in
        sync)
            backup_configuration
            sync_configuration
            validate_configuration
            detect_configuration_drift
            ;;
        backup)
            backup_configuration
            ;;
        restore)
            restore_configuration
            validate_configuration
            ;;
        validate)
            validate_configuration
            detect_configuration_drift
            ;;
        rotate)
            rotate_secrets
            sync_configuration
            validate_configuration
            ;;
        *)
            log_error "Unknown action: $ACTION"
            usage
            exit 1
            ;;
    esac
    
    log_success "🔧 Configuration management completed successfully!"
}

# Run main function
main "$@"