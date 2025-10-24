#!/usr/bin/env bash
################################################################################
# SynOS Build Environment Verification
# 
# Comprehensive pre-build verification to catch issues before building.
# Consolidates multiple verification scripts into one unified tool.
#
# Usage:
#   ./scripts/testing/verify-build.sh [OPTIONS]
#
# Options:
#   --fix             Attempt to fix issues automatically
#   --verbose         Show detailed information
#   --minimal         Check only essential requirements
#   --full            Full verification (default)
#   --json FILE       Output results as JSON
#   --no-color        Disable colored output
#   --help            Show this help message
#
# Verification Levels:
#   minimal - Essential checks only (rust, disk space)
#   full    - All checks including optional tools
#
# Exit Codes:
#   0 - All checks passed
#   1 - Critical checks failed
#   2 - Warning (non-critical issues)
#
################################################################################

set -euo pipefail

# Determine project root first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source shared library
source "${SCRIPT_DIR}/../lib/build-common.sh"

################################################################################
# Configuration
################################################################################

FIX_ISSUES=false
VERBOSE=false
VERIFICATION_LEVEL="full"
JSON_OUTPUT=""
USE_COLOR=true

# Verification results
declare -A CHECK_RESULTS
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

################################################################################
# Argument Parsing
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_ISSUES=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --minimal)
            VERIFICATION_LEVEL="minimal"
            shift
            ;;
        --full)
            VERIFICATION_LEVEL="full"
            shift
            ;;
        --json)
            JSON_OUTPUT="$2"
            shift 2
            ;;
        --no-color)
            USE_COLOR=false
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

################################################################################
# Verification Functions
################################################################################

check_rust_toolchain() {
    section "Rust Toolchain"
    
    # Check rustc
    if command -v rustc &>/dev/null; then
        local rust_version
        rust_version=$(rustc --version)
        CHECK_RESULTS["rustc"]="PASS"
        success "rustc: $rust_version"
    else
        CHECK_RESULTS["rustc"]="FAIL"
        error "rustc not found"
        
        if [[ "$FIX_ISSUES" == true ]]; then
            info "Installing Rust..."
            curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
            source "$HOME/.cargo/env"
        else
            info "Fix: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        fi
        return 1
    fi
    
    # Check cargo
    if command -v cargo &>/dev/null; then
        local cargo_version
        cargo_version=$(cargo --version)
        CHECK_RESULTS["cargo"]="PASS"
        success "cargo: $cargo_version"
    else
        CHECK_RESULTS["cargo"]="FAIL"
        error "cargo not found"
        return 1
    fi
    
    # Check for kernel target
    if rustup target list --installed | grep -q "x86_64-unknown-none"; then
        CHECK_RESULTS["kernel_target"]="PASS"
        success "Kernel target (x86_64-unknown-none) installed"
    else
        CHECK_RESULTS["kernel_target"]="FAIL"
        error "Kernel target not installed"
        
        if [[ "$FIX_ISSUES" == true ]]; then
            info "Installing kernel target..."
            rustup target add x86_64-unknown-none
            CHECK_RESULTS["kernel_target"]="PASS"
        else
            info "Fix: rustup target add x86_64-unknown-none"
        fi
        return 1
    fi
    
    return 0
}

check_build_tools() {
    section "Build Tools"
    
    local required_tools=("make" "git" "gcc")
    local optional_tools=("grub-mkrescue" "xorriso" "genisoimage")
    
    # Check required tools
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" &>/dev/null; then
            CHECK_RESULTS["tool_$tool"]="PASS"
            if [[ "$VERBOSE" == true ]]; then
                local version
                version=$("$tool" --version 2>/dev/null | head -1 || echo "installed")
                success "$tool: $version"
            else
                success "$tool: installed"
            fi
        else
            CHECK_RESULTS["tool_$tool"]="FAIL"
            error "$tool not found"
            
            if [[ "$FIX_ISSUES" == true ]]; then
                info "Installing $tool..."
                sudo apt-get install -y "$tool" 2>/dev/null || true
            else
                info "Fix: sudo apt install $tool"
            fi
        fi
    done
    
    # Check optional tools (warnings only)
    if [[ "$VERIFICATION_LEVEL" == "full" ]]; then
        for tool in "${optional_tools[@]}"; do
            if command -v "$tool" &>/dev/null; then
                CHECK_RESULTS["tool_$tool"]="PASS"
                success "$tool: installed"
            else
                CHECK_RESULTS["tool_$tool"]="WARN"
                warning "$tool not found (optional)"
                info "Install with: sudo apt install $(echo "$tool" | sed 's/-mkrescue//')"
            fi
        done
    fi
    
    return 0
}

check_disk_space() {
    section "Disk Space"
    
    local build_dir="${PROJECT_ROOT}/build"
    mkdir -p "$build_dir"
    
    local available_kb
    available_kb=$(df "$build_dir" | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    
    info "Build directory: $build_dir"
    info "Available space: ${available_gb}GB"
    
    # Minimum requirements
    local min_gb=5
    
    if [[ $available_gb -ge $min_gb ]]; then
        CHECK_RESULTS["disk_space"]="PASS"
        success "Sufficient disk space (${available_gb}GB >= ${min_gb}GB)"
    else
        CHECK_RESULTS["disk_space"]="FAIL"
        error "Insufficient disk space (${available_gb}GB < ${min_gb}GB)"
        
        if [[ "$FIX_ISSUES" == true ]]; then
            info "Cleaning old builds..."
            rm -rf "$build_dir"/workspace-* 2>/dev/null || true
            rm -f "$build_dir"/*.iso.old 2>/dev/null || true
        else
            info "Fix: Clean old builds or free up disk space"
        fi
        return 1
    fi
    
    # Check for build artifacts
    if [[ "$VERBOSE" == true ]]; then
        local build_size
        build_size=$(du -sh "$build_dir" 2>/dev/null | cut -f1 || echo "0")
        info "Current build cache: $build_size"
    fi
    
    return 0
}

check_git_status() {
    section "Git Repository"
    
    if [[ ! -d "${PROJECT_ROOT}/.git" ]]; then
        CHECK_RESULTS["git_repo"]="WARN"
        warning "Not a git repository"
        return 0
    fi
    
    CHECK_RESULTS["git_repo"]="PASS"
    success "Git repository detected"
    
    if [[ "$VERIFICATION_LEVEL" == "full" ]]; then
        # Check for uncommitted changes
        if git diff --quiet && git diff --cached --quiet; then
            CHECK_RESULTS["git_clean"]="PASS"
            success "Working directory clean"
        else
            CHECK_RESULTS["git_clean"]="WARN"
            warning "Uncommitted changes present"
            
            if [[ "$VERBOSE" == true ]]; then
                info "Modified files:"
                git status --short | head -10 | while IFS= read -r line; do
                    echo "  $line"
                done
            fi
        fi
        
        # Check current branch
        local branch
        branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        info "Current branch: $branch"
    fi
    
    return 0
}

check_dependencies() {
    section "Cargo Dependencies"
    
    if [[ ! -f "${PROJECT_ROOT}/Cargo.toml" ]]; then
        CHECK_RESULTS["cargo_deps"]="WARN"
        warning "No Cargo.toml found in project root"
        return 0
    fi
    
    # Check if Cargo.lock exists
    if [[ -f "${PROJECT_ROOT}/Cargo.lock" ]]; then
        CHECK_RESULTS["cargo_lock"]="PASS"
        success "Cargo.lock present"
    else
        CHECK_RESULTS["cargo_lock"]="WARN"
        warning "Cargo.lock missing (will be created on build)"
    fi
    
    # Try to resolve dependencies (doesn't build, just checks)
    if [[ "$VERIFICATION_LEVEL" == "full" ]]; then
        info "Checking dependency resolution..."
        if cargo metadata --format-version 1 >/dev/null 2>&1; then
            CHECK_RESULTS["cargo_deps"]="PASS"
            success "Dependencies resolve successfully"
        else
            CHECK_RESULTS["cargo_deps"]="FAIL"
            error "Dependency resolution failed"
            info "Try: cargo update"
            return 1
        fi
    else
        CHECK_RESULTS["cargo_deps"]="PASS"
    fi
    
    return 0
}

check_kernel_source() {
    section "Kernel Source"
    
    local kernel_toml="${PROJECT_ROOT}/src/kernel/Cargo.toml"
    
    if [[ -f "$kernel_toml" ]]; then
        CHECK_RESULTS["kernel_source"]="PASS"
        success "Kernel source found"
        
        if [[ "$VERBOSE" == true ]]; then
            local kernel_name
            kernel_name=$(grep "^name" "$kernel_toml" | head -1 | cut -d'"' -f2)
            local kernel_version
            kernel_version=$(grep "^version" "$kernel_toml" | head -1 | cut -d'"' -f2)
            info "Kernel: $kernel_name v$kernel_version"
        fi
    else
        CHECK_RESULTS["kernel_source"]="FAIL"
        error "Kernel source not found at: $kernel_toml"
        return 1
    fi
    
    return 0
}

check_memory() {
    section "System Memory"
    
    local total_mem_kb
    total_mem_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local total_mem_gb=$((total_mem_kb / 1024 / 1024))
    
    local available_mem_kb
    available_mem_kb=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    local available_mem_gb=$((available_mem_kb / 1024 / 1024))
    
    info "Total memory: ${total_mem_gb}GB"
    info "Available memory: ${available_mem_gb}GB"
    
    # Minimum 2GB recommended
    if [[ $available_mem_gb -ge 2 ]]; then
        CHECK_RESULTS["memory"]="PASS"
        success "Sufficient memory available"
    else
        CHECK_RESULTS["memory"]="WARN"
        warning "Low memory (${available_mem_gb}GB available, 2GB recommended)"
        info "Consider closing other applications"
    fi
    
    return 0
}

check_environment_vars() {
    section "Environment Variables"
    
    # Check common environment variables
    local env_vars=("HOME" "USER" "PATH" "SHELL")
    local all_ok=true
    
    for var in "${env_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            if [[ "$VERBOSE" == true ]]; then
                success "$var is set"
            fi
        else
            warning "$var is not set"
            all_ok=false
        fi
    done
    
    if [[ "$all_ok" == true ]]; then
        CHECK_RESULTS["environment"]="PASS"
        success "Environment variables OK"
    else
        CHECK_RESULTS["environment"]="WARN"
        warning "Some environment variables missing"
    fi
    
    # Check Rust environment
    if [[ -f "$HOME/.cargo/env" ]]; then
        if [[ "$VERBOSE" == true ]]; then
            success "Rust environment file present"
        fi
    fi
    
    return 0
}

check_permissions() {
    section "Permissions"
    
    # Check if running as root (should not be)
    if [[ $EUID -eq 0 ]]; then
        CHECK_RESULTS["not_root"]="FAIL"
        error "Running as root (not recommended)"
        info "Run as normal user instead"
        return 1
    else
        CHECK_RESULTS["not_root"]="PASS"
        success "Not running as root"
    fi
    
    # Check write permissions on build directory
    local build_dir="${PROJECT_ROOT}/build"
    mkdir -p "$build_dir" 2>/dev/null || true
    
    if [[ -w "$build_dir" ]]; then
        CHECK_RESULTS["build_writable"]="PASS"
        success "Build directory writable"
    else
        CHECK_RESULTS["build_writable"]="FAIL"
        error "Build directory not writable: $build_dir"
        return 1
    fi
    
    return 0
}

generate_json_report() {
    if [[ -z "$JSON_OUTPUT" ]]; then
        return 0
    fi
    
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$JSON_OUTPUT" <<EOF
{
  "verification": {
    "timestamp": "$timestamp",
    "level": "$VERIFICATION_LEVEL",
    "project_root": "$PROJECT_ROOT"
  },
  "checks": {
EOF
    
    local first=true
    for check_name in "${!CHECK_RESULTS[@]}"; do
        if [[ "$first" == true ]]; then
            first=false
        else
            echo "," >> "$JSON_OUTPUT"
        fi
        echo -n "    \"$check_name\": \"${CHECK_RESULTS[$check_name]}\"" >> "$JSON_OUTPUT"
    done
    
    cat >> "$JSON_OUTPUT" <<EOF

  },
  "summary": {
    "passed": $CHECKS_PASSED,
    "failed": $CHECKS_FAILED,
    "warnings": $CHECKS_WARNING
  }
}
EOF
    
    success "JSON report: $JSON_OUTPUT"
}

################################################################################
# Main Verification Flow
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS Build Environment Verification"
    
    info "Verification Level: $VERIFICATION_LEVEL"
    info "Auto-fix: $FIX_ISSUES"
    echo ""
    
    # Run checks
    check_permissions || true
    check_rust_toolchain || true
    check_build_tools || true
    check_disk_space || true
    check_memory || true
    check_kernel_source || true
    check_dependencies || true
    check_git_status || true
    check_environment_vars || true
    
    # Count results
    set +e  # Temporarily disable exit on error for counting
    if [[ ${#CHECK_RESULTS[@]} -gt 0 ]]; then
        for result in "${CHECK_RESULTS[@]}"; do
            case "$result" in
                PASS) ((CHECKS_PASSED++)) ;;
                FAIL) ((CHECKS_FAILED++)) ;;
                WARN) ((CHECKS_WARNING++)) ;;
            esac
        done
    fi
    set -e  # Re-enable exit on error
    
    # Generate JSON if requested
    generate_json_report
    
    # Summary
    local end_time
    end_time=$(date +%s)
    
    echo ""
    section "Verification Summary"
    
    success "Passed: $CHECKS_PASSED"
    if [[ $CHECKS_FAILED -gt 0 ]]; then
        error "Failed: $CHECKS_FAILED"
    else
        info "Failed: $CHECKS_FAILED"
    fi
    if [[ $CHECKS_WARNING -gt 0 ]]; then
        warning "Warnings: $CHECKS_WARNING"
    else
        info "Warnings: $CHECKS_WARNING"
    fi
    
    info "Verification time: $(elapsed_time "$start_time" "$end_time")"
    
    # Exit code
    echo ""
    if [[ $CHECKS_FAILED -gt 0 ]]; then
        error "Build environment has critical issues"
        if [[ "$FIX_ISSUES" == false ]]; then
            info "Try: $0 --fix"
        fi
        return 1
    elif [[ $CHECKS_WARNING -gt 0 ]]; then
        warning "Build environment has warnings (non-critical)"
        return 2
    else
        success "Build environment ready!"
        return 0
    fi
}

################################################################################
# Execute
################################################################################

main "$@"
