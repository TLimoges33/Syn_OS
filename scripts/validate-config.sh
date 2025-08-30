#!/bin/bash
# Syn_OS Configuration Validation Script
# Validates Kubernetes configs, VS Code settings, and other configurations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((VALIDATION_WARNINGS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((VALIDATION_ERRORS++))
}

# Function to validate Kubernetes configuration
validate_kubernetes_config() {
    log_info "Validating Kubernetes configuration..."
    
    local k8s_dir="$PROJECT_ROOT/deploy/kubernetes"
    
    # Check if base directory exists
    if [[ ! -d "$k8s_dir/base" ]]; then
        log_error "Kubernetes base directory not found: $k8s_dir/base"
        return 1
    fi
    
    # Check required base files
    local required_files=(
        "namespace.yaml"
        "core-deployment.yaml"
        "security-deployment.yaml"
        "kustomization.yaml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$k8s_dir/base/$file" ]]; then
            log_error "Required Kubernetes file missing: $k8s_dir/base/$file"
        else
            log_success "Found: $file"
        fi
    done
    
    # Check overlay directories
    local overlay_dir="$k8s_dir/overlays"
    if [[ ! -d "$overlay_dir" ]]; then
        log_error "Kubernetes overlays directory not found: $overlay_dir"
        return 1
    fi
    
    # Check development overlay
    if [[ -f "$overlay_dir/development/kustomization.yaml" ]]; then
        log_success "Development overlay found"
    else
        log_error "Development overlay missing: $overlay_dir/development/kustomization.yaml"
    fi
    
    # Check production overlay
    if [[ -f "$overlay_dir/production/kustomization.yaml" ]]; then
        log_success "Production overlay found"
    else
        log_error "Production overlay missing: $overlay_dir/production/kustomization.yaml"
    fi
    
    # Validate YAML syntax if yamllint is available
    if command -v yamllint &> /dev/null; then
        log_info "Validating YAML syntax..."
        find "$k8s_dir" -name "*.yaml" -o -name "*.yml" | while read -r file; do
            if yamllint "$file" > /dev/null 2>&1; then
                log_success "YAML valid: $(basename "$file")"
            else
                log_error "YAML invalid: $file"
            fi
        done
    else
        log_warning "yamllint not available, skipping YAML syntax validation"
    fi
    
    # Validate with kubectl if available
    if command -v kubectl &> /dev/null; then
        log_info "Validating Kubernetes manifests with kubectl..."
        
        for env in development production; do
            if [[ -d "$overlay_dir/$env" ]]; then
                if kubectl apply --dry-run=client -k "$overlay_dir/$env" &> /dev/null; then
                    log_success "Kubernetes manifests valid for $env"
                else
                    log_error "Kubernetes manifests invalid for $env"
                fi
            fi
        done
    else
        log_warning "kubectl not available, skipping manifest validation"
    fi
    
    log_success "Kubernetes configuration structure is valid"
}

# Function to validate VS Code configuration
validate_vscode_config() {
    log_info "Validating VS Code configuration..."
    
    local vscode_settings="$PROJECT_ROOT/.vscode/settings.json"
    local dev_config="$PROJECT_ROOT/config/development/dev-environment.yaml"
    
    # Check if VS Code settings file exists
    if [[ ! -f "$vscode_settings" ]]; then
        log_error "VS Code settings file not found: $vscode_settings"
        return 1
    fi
    
    # Validate JSON syntax
    if command -v jq &> /dev/null; then
        if jq empty < "$vscode_settings" > /dev/null 2>&1; then
            log_success "VS Code settings JSON is valid"
        else
            log_error "VS Code settings JSON is invalid"
        fi
    else
        log_warning "jq not available, skipping JSON validation"
    fi
    
    # Check for the problematic checkOnSave configuration
    log_info "Checking rust-analyzer checkOnSave configuration..."
    
    if grep -q '"rust-analyzer.checkOnSave.command"' "$vscode_settings"; then
        log_success "checkOnSave.command properly configured in VS Code settings"
    else
        log_warning "checkOnSave.command not found in VS Code settings"
    fi
    
    # Check development environment config
    if [[ -f "$dev_config" ]]; then
        log_info "Checking development environment configuration..."
        
        if grep -A 3 "checkOnSave:" "$dev_config" | grep -q "command:"; then
            log_success "checkOnSave properly configured as object in dev environment"
        else
            log_warning "checkOnSave may not be properly configured in dev environment"
        fi
    else
        log_warning "Development environment config not found: $dev_config"
    fi
    
    # Check for common configuration issues
    log_info "Checking for common VS Code configuration issues..."
    
    # Check for deprecated settings
    local deprecated_settings=(
        "rust-analyzer.checkOnSave"
        "rust-analyzer.cargo.loadOutDirsFromCheck"
    )
    
    for setting in "${deprecated_settings[@]}"; do
        if grep -q "\"$setting\":" "$vscode_settings"; then
            if [[ "$setting" == "rust-analyzer.checkOnSave" ]] && ! grep -q "\"$setting\":" "$vscode_settings" | grep -q "command\|enable"; then
                log_error "Deprecated checkOnSave configuration found (should be object with command/enable)"
            fi
        fi
    done
}

# Function to validate Docker configuration
validate_docker_config() {
    log_info "Validating Docker configuration..."
    
    local docker_files=(
        "docker-compose.yml"
        "Dockerfile.consciousness"
        "Dockerfile.iso-builder"
    )
    
    for file in "${docker_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            log_success "Found Docker file: $file"
        else
            log_warning "Docker file not found: $file"
        fi
    done
    
    # Validate docker-compose syntax if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        if [[ -f "$PROJECT_ROOT/docker-compose.yml" ]]; then
            if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" config > /dev/null 2>&1; then
                log_success "docker-compose.yml is valid"
            else
                log_error "docker-compose.yml is invalid"
            fi
        fi
    else
        log_warning "docker-compose not available, skipping validation"
    fi
}

# Function to validate Helm charts
validate_helm_config() {
    log_info "Validating Helm configuration..."
    
    local helm_dir="$PROJECT_ROOT/deploy/helm"
    
    if [[ ! -d "$helm_dir" ]]; then
        log_warning "Helm directory not found: $helm_dir"
        return 0
    fi
    
    # Check for Helm charts
    find "$helm_dir" -name "Chart.yaml" | while read -r chart; do
        local chart_dir=$(dirname "$chart")
        local chart_name=$(basename "$chart_dir")
        
        log_info "Validating Helm chart: $chart_name"
        
        if command -v helm &> /dev/null; then
            if helm lint "$chart_dir" > /dev/null 2>&1; then
                log_success "Helm chart valid: $chart_name"
            else
                log_error "Helm chart invalid: $chart_name"
            fi
        else
            log_warning "helm not available, skipping chart validation"
        fi
        
        # Check for required files
        local required_helm_files=("values.yaml" "templates")
        for req_file in "${required_helm_files[@]}"; do
            if [[ -e "$chart_dir/$req_file" ]]; then
                log_success "Found $req_file in $chart_name"
            else
                log_warning "Missing $req_file in $chart_name"
            fi
        done
    done
}

# Function to validate Rust configuration
validate_rust_config() {
    log_info "Validating Rust configuration..."
    
    # Check Cargo.toml files
    find "$PROJECT_ROOT" -name "Cargo.toml" -not -path "*/target/*" -not -path "*/venv/*" | while read -r cargo_file; do
        local dir=$(dirname "$cargo_file")
        local rel_path=$(realpath --relative-to="$PROJECT_ROOT" "$cargo_file")
        
        log_info "Checking Cargo.toml: $rel_path"
        
        if cargo check --manifest-path "$cargo_file" > /dev/null 2>&1; then
            log_success "Cargo.toml valid: $rel_path"
        else
            log_warning "Cargo.toml may have issues: $rel_path"
        fi
    done
    
    # Check rust-toolchain.toml
    if [[ -f "$PROJECT_ROOT/rust-toolchain.toml" ]]; then
        log_success "Found rust-toolchain.toml"
    else
        log_warning "rust-toolchain.toml not found"
    fi
}

# Function to validate Python configuration
validate_python_config() {
    log_info "Validating Python configuration..."
    
    # Check pyproject.toml
    if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        log_success "Found pyproject.toml"
    else
        log_warning "pyproject.toml not found"
    fi
    
    # Check requirements files
    local req_files=(
        "requirements.txt"
        "requirements-dev.txt"
        "docker/requirements.txt"
    )
    
    for req_file in "${req_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$req_file" ]]; then
            log_success "Found requirements file: $req_file"
        else
            log_warning "Requirements file not found: $req_file"
        fi
    done
}

# Function to validate security configuration
validate_security_config() {
    log_info "Validating security configuration..."
    
    local security_dir="$PROJECT_ROOT/security"
    
    if [[ ! -d "$security_dir" ]]; then
        log_warning "Security directory not found: $security_dir"
        return 0
    fi
    
    # Check for security audit configuration
    if [[ -f "$security_dir/audit/security_config.json" ]]; then
        log_success "Security audit configuration found"
    else
        log_warning "Security audit configuration not found"
    fi
    
    # Check for certificates
    local cert_dir="$PROJECT_ROOT/certs"
    if [[ -d "$cert_dir" ]]; then
        log_success "Certificates directory found"
    else
        log_warning "Certificates directory not found"
    fi
}

# Function to show validation summary
show_summary() {
    echo
    log_info "=== Validation Summary ==="
    
    if [[ $VALIDATION_ERRORS -eq 0 && $VALIDATION_WARNINGS -eq 0 ]]; then
        log_success "All validations passed! ✅"
    elif [[ $VALIDATION_ERRORS -eq 0 ]]; then
        log_warning "Validation completed with $VALIDATION_WARNINGS warnings ⚠️"
    else
        log_error "Validation failed with $VALIDATION_ERRORS errors and $VALIDATION_WARNINGS warnings ❌"
    fi
    
    echo
    log_info "Summary:"
    echo "  Errors: $VALIDATION_ERRORS"
    echo "  Warnings: $VALIDATION_WARNINGS"
    
    if [[ $VALIDATION_ERRORS -gt 0 ]]; then
        echo
        log_error "Please fix the errors before proceeding with deployment."
        return 1
    fi
    
    return 0
}

# Main execution
main() {
    log_info "Starting Syn_OS configuration validation..."
    echo
    
    validate_kubernetes_config
    echo
    
    validate_vscode_config
    echo
    
    validate_docker_config
    echo
    
    validate_helm_config
    echo
    
    validate_rust_config
    echo
    
    validate_python_config
    echo
    
    validate_security_config
    echo
    
    show_summary
}

# Run main function
main "$@"
