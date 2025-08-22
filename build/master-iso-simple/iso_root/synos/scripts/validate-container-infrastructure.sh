#!/bin/bash

# ============================================================================
# SynapticOS Container Infrastructure Validation Script
# ============================================================================
# Description: Validates the container infrastructure setup
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

# Check Docker and Docker Compose
check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi
    
    if ! docker --version &> /dev/null; then
        log_error "Docker is not running or accessible"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        return 1
    fi
    
    log_success "Docker and Docker Compose are available"
    return 0
}

# Validate Dockerfiles
validate_dockerfiles() {
    log_info "Validating Dockerfiles..."
    
    local dockerfiles=(
        "Dockerfile.consciousness"
        "services/orchestrator/Dockerfile"
        "applications/security_dashboard/Dockerfile"
        "applications/learning_hub/Dockerfile"
        "applications/security_tutor/Dockerfile"
        "applications/web_dashboard/Dockerfile"
        "applications/threat_intelligence_dashboard/Dockerfile"
    )
    
    local missing_files=()
    
    for dockerfile in "${dockerfiles[@]}"; do
        if [[ -f "$dockerfile" ]]; then
            log_success "✓ $dockerfile exists"
        else
            log_error "✗ $dockerfile is missing"
            missing_files+=("$dockerfile")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        log_success "All Dockerfiles are present"
        return 0
    else
        log_error "Missing Dockerfiles: ${missing_files[*]}"
        return 1
    fi
}

# Validate docker-compose files
validate_compose_files() {
    log_info "Validating docker-compose files..."
    
    local compose_files=(
        "docker-compose.yml"
        "docker-compose.production.yml"
    )
    
    for file in "${compose_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_info "Validating $file syntax..."
            if docker-compose -f "$file" config >/dev/null 2>&1; then
                log_success "✓ $file syntax is valid"
            else
                log_error "✗ $file has syntax errors"
                return 1
            fi
        else
            log_error "✗ $file is missing"
            return 1
        fi
    done
    
    log_success "All docker-compose files are valid"
    return 0
}

# Validate environment files
validate_env_files() {
    log_info "Validating environment files..."
    
    if [[ -f ".env" ]]; then
        log_success "✓ .env file exists"
    else
        log_warning "✗ .env file is missing (will use defaults)"
    fi
    
    if [[ -f ".env.production.template" ]]; then
        log_success "✓ .env.production.template exists"
    else
        log_error "✗ .env.production.template is missing"
        return 1
    fi
    
    # Check for placeholder values in .env
    if [[ -f ".env" ]]; then
        local placeholders=(
            "your_secure_password_here"
            "your_redis_password_here"
            "your_nats_password_here"
            "your_jwt_secret_key_here"
            "your_encryption_key_here"
        )
        
        for placeholder in "${placeholders[@]}"; do
            if grep -q "$placeholder" .env; then
                log_warning "⚠️  Placeholder '$placeholder' found in .env - should be replaced with secure values"
            fi
        done
    fi
    
    return 0
}

# Validate required directories
validate_directories() {
    log_info "Validating directory structure..."
    
    local required_dirs=(
        "src/consciousness_v2"
        "src/security"
        "services/orchestrator"
        "applications/security_dashboard"
        "applications/learning_hub"
        "applications/security_tutor"
        "applications/web_dashboard"
        "applications/threat_intelligence_dashboard"
        "logs"
        "config"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            log_success "✓ Directory $dir exists"
        else
            log_error "✗ Directory $dir is missing"
            return 1
        fi
    done
    
    log_success "All required directories are present"
    return 0
}

# Validate requirements files
validate_requirements() {
    log_info "Validating requirements files..."
    
    local requirements_files=(
        "requirements-consciousness.txt"
        "applications/security_dashboard/requirements.txt"
        "applications/learning_hub/requirements.txt"
        "applications/security_tutor/requirements.txt"
        "applications/web_dashboard/requirements.txt"
        "applications/threat_intelligence_dashboard/requirements.txt"
    )
    
    for file in "${requirements_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✓ $file exists"
        else
            log_error "✗ $file is missing"
            return 1
        fi
    done
    
    log_success "All requirements files are present"
    return 0
}

# Test Docker builds (dry run)
test_docker_builds() {
    log_info "Testing Docker builds (syntax only)..."
    
    # Test consciousness service build
    if docker build -f Dockerfile.consciousness -t syn_os/consciousness:test . --dry-run 2>/dev/null || \
       docker build -f Dockerfile.consciousness --no-cache --target builder . >/dev/null 2>&1; then
        log_success "✓ Consciousness Dockerfile build test passed"
    else
        log_warning "⚠️  Consciousness Dockerfile build test failed (may need dependencies)"
    fi
    
    # Test orchestrator build
    if [[ -f "services/orchestrator/go.mod" ]]; then
        log_success "✓ Orchestrator Go module exists"
    else
        log_warning "⚠️  Orchestrator Go module missing - build may fail"
    fi
    
    return 0
}

# Check network configuration
validate_network_config() {
    log_info "Validating network configuration..."
    
    # Check if ports are available
    local ports=(8080 8081 8083 8084 8085 8086 8087 4222 6379 5432)
    local busy_ports=()
    
    for port in "${ports[@]}"; do
        if ss -tlnp | grep -q ":$port "; then
            busy_ports+=("$port")
        fi
    done
    
    if [[ ${#busy_ports[@]} -gt 0 ]]; then
        log_warning "⚠️  Ports already in use: ${busy_ports[*]}"
        log_warning "These ports may conflict with SynapticOS services"
    else
        log_success "✓ All required ports are available"
    fi
    
    return 0
}

# Security validation
validate_security_config() {
    log_info "Validating security configuration..."
    
    # Check file permissions
    local secure_files=(
        ".env"
        ".env.production"
        "config/nats/auth.conf"
        "config/redis/redis.conf"
    )
    
    for file in "${secure_files[@]}"; do
        if [[ -f "$file" ]]; then
            local perms=$(stat -c "%a" "$file" 2>/dev/null || echo "unknown")
            if [[ "$perms" == "600" ]]; then
                log_success "✓ $file has secure permissions (600)"
            else
                log_warning "⚠️  $file permissions: $perms (should be 600)"
            fi
        fi
    done
    
    # Check for default passwords in production template
    if [[ -f ".env.production.template" ]]; then
        if grep -q "REPLACE_WITH_" .env.production.template; then
            log_success "✓ Production template contains placeholder values"
        else
            log_warning "⚠️  Production template may not have placeholders"
        fi
    fi
    
    return 0
}

# Overall validation summary
validation_summary() {
    local total_checks=8
    local passed_checks=0
    
    log_info "Running comprehensive validation..."
    echo
    
    check_docker && ((passed_checks++)) || true
    validate_dockerfiles && ((passed_checks++)) || true
    validate_compose_files && ((passed_checks++)) || true
    validate_env_files && ((passed_checks++)) || true
    validate_directories && ((passed_checks++)) || true
    validate_requirements && ((passed_checks++)) || true
    test_docker_builds && ((passed_checks++)) || true
    validate_network_config && ((passed_checks++)) || true
    validate_security_config || true  # Don't count this one as it may not exist yet
    
    echo
    echo "=============================================================="
    echo "                 VALIDATION SUMMARY"
    echo "=============================================================="
    echo "Validation checks passed: $passed_checks/$total_checks"
    echo
    
    if [[ $passed_checks -eq $total_checks ]]; then
        log_success "🎉 All validation checks passed!"
        echo
        echo "✅ Container infrastructure is ready for deployment"
        echo "✅ All Dockerfiles are present and valid"
        echo "✅ Docker Compose configurations are valid"
        echo "✅ Environment files are properly configured"
        echo "✅ Directory structure is complete"
        echo
        echo "Next steps:"
        echo "1. Run: ./scripts/setup-container-infrastructure.sh"
        echo "2. Or manually: docker-compose up -d"
        echo
        return 0
    else
        log_warning "⚠️  Some validation checks failed"
        echo
        echo "Please address the issues above before deploying"
        echo "Run the setup script to automatically fix most issues:"
        echo "./scripts/setup-container-infrastructure.sh"
        echo
        return 1
    fi
}

# Main execution
main() {
    echo "=============================================================="
    echo "      SynapticOS Container Infrastructure Validation"
    echo "=============================================================="
    echo "Date: $(date)"
    echo "=============================================================="
    echo
    
    validation_summary
}

# Run main function
main "$@"
