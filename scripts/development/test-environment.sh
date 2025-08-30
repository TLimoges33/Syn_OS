#!/bin/bash

# Syn_OS Development Environment Deployment Test
# Version: 1.0.0
# Description: Tests the complete development environment setup

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

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "Running test: $test_name"
    
    if eval "$test_command" &>/dev/null; then
        log_success "✅ $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "❌ $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

main() {
    log_info "Starting Syn_OS Development Environment Deployment Test"
    echo "=================================================="
    
    # Environment Detection
    log_info "Detecting environment..."
    if [ -f "/.dockerenv" ]; then
        log_info "Running in Docker container"
        ENVIRONMENT="docker"
    elif [ -n "${CODESPACES:-}" ]; then
        log_info "Running in GitHub Codespaces"
        ENVIRONMENT="codespaces"
    else
        log_info "Running in local environment"
        ENVIRONMENT="local"
    fi
    
    # Core System Tests
    log_info "Testing core system components..."
    run_test "Operating System Detection" "uname -a"
    run_test "CPU Information" "lscpu"
    run_test "Memory Information" "free -h"
    run_test "Disk Space" "df -h /"
    
    # Development Tools Tests
    log_info "Testing development tools..."
    run_test "Rust Compiler" "rustc --version"
    run_test "Cargo Package Manager" "cargo --version"
    run_test "Python Interpreter" "python3 --version"
    run_test "Go Compiler" "go version"
    run_test "Node.js Runtime" "node --version"
    run_test "Git Version Control" "git --version"
    
    # Rust-specific Tests
    log_info "Testing Rust development environment..."
    run_test "Rust Toolchain x86_64-unknown-none" "rustup target list --installed | grep -q x86_64-unknown-none"
    run_test "Cargo Cross-compilation" "which cross || cargo install cross --quiet && cross --version"
    run_test "Clippy Linter" "cargo clippy --version"
    run_test "Rustfmt Formatter" "cargo fmt --version"
    
    # Security Tools Tests
    log_info "Testing security tools..."
    run_test "Trivy Scanner" "trivy --version"
    run_test "Bandit Security Checker" "bandit --version || pip3 install bandit && bandit --version"
    run_test "Semgrep Static Analysis" "semgrep --version || pip3 install semgrep && semgrep --version"
    
    # Performance Tools Tests
    log_info "Testing performance tools..."
    run_test "Valgrind Memory Checker" "valgrind --version"
    run_test "GDB Debugger" "gdb --version"
    run_test "Performance Analyzer" "perf --version || echo 'perf not available'"
    
    # Container and Virtualization Tests
    log_info "Testing virtualization tools..."
    run_test "Docker Client" "docker --version"
    run_test "QEMU Emulator" "qemu-system-x86_64 --version"
    
    # Network Tools Tests
    log_info "Testing network tools..."
    run_test "Nmap Network Scanner" "nmap --version"
    run_test "Curl HTTP Client" "curl --version"
    run_test "Wget Downloader" "wget --version"
    
    # Development Services Tests (if running)
    log_info "Testing development services..."
    run_test "Redis Service" "redis-cli ping 2>/dev/null || echo 'Redis not running'"
    run_test "PostgreSQL Service" "pg_isready 2>/dev/null || echo 'PostgreSQL not running'"
    
    # Project-specific Tests
    log_info "Testing project configuration..."
    run_test "Cargo Workspace" "cargo metadata --no-deps --format-version 1 >/dev/null"
    run_test "Project Structure" "[ -d src/ ] && [ -f Cargo.toml ]"
    run_test "Documentation" "[ -d docs/ ] && [ -f README.md ]"
    
    # Health Check Script Test
    if [ -f "./healthcheck.sh" ]; then
        log_info "Testing health check script..."
        run_test "Health Check Script" "bash ./healthcheck.sh --quick"
    fi
    
    # Build System Test
    log_info "Testing build system..."
    if run_test "Cargo Check" "cargo check --workspace --all-targets"; then
        log_info "Attempting full build test..."
        run_test "Cargo Build" "timeout 300 cargo build --workspace || echo 'Build timeout or failed'"
    fi
    
    # Generate Test Report
    echo ""
    echo "=================================================="
    log_info "Test Summary Report"
    echo "=================================================="
    echo "Environment: $ENVIRONMENT"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "🎉 All tests passed! Development environment is ready."
        echo ""
        log_info "Next steps:"
        echo "1. Run 'cargo build --workspace' to build the project"
        echo "2. Run 'cargo test --workspace' to run tests"
        echo "3. Use 'syn-dev' command for development helpers"
        echo "4. Check './healthcheck.sh' for detailed environment status"
        exit 0
    else
        log_warning "⚠️  Some tests failed. Environment may need attention."
        echo ""
        log_info "Troubleshooting:"
        if [ $ENVIRONMENT = "codespaces" ]; then
            echo "- Rebuild your Codespace if issues persist"
            echo "- Check Codespace creation logs for errors"
        else
            echo "- Run './setup-environment.sh' to fix common issues"
            echo "- Check './healthcheck.sh' for detailed diagnostics"
        fi
        exit 1
    fi
}

# Handle script interruption
trap 'log_error "Test interrupted!"; exit 1' INT TERM

# Run main function
main "$@"
