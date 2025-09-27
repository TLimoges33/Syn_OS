#!/bin/bash

# SynOS Comprehensive Test Suite
# Tests all optimization improvements and system functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$TEST_DIR")"
FAILED_TESTS=()

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_info "Running test: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log_success "$test_name"
        return 0
    else
        log_error "$test_name"
        FAILED_TESTS+=("$test_name")
        return 1
    fi
}

# Test 1: Archive consolidation verification
test_archive_consolidation() {
    log_info "Testing archive consolidation..."
    
    # Check that legacy archive structure exists
    run_test "Legacy archive structure exists" "test -d '$ROOT_DIR/archive/legacy-v0.x'"
    
    # Check that old scattered archives are gone
    run_test "Old scattered archives removed" "! test -d '$ROOT_DIR/archive/services_archived_20250830'"
    run_test "Redundant src archive removed" "! test -d '$ROOT_DIR/archive/src_archived_redundant'"
}

# Test 2: Duplicate code elimination verification
test_duplicate_elimination() {
    log_info "Testing duplicate code elimination..."
    
    # Check that duplicate src directories are removed
    run_test "Consciousness bridge duplicate removed" "! test -d '$ROOT_DIR/services/consciousness/bridge/src'"
    run_test "Consciousness dashboard duplicate removed" "! test -d '$ROOT_DIR/services/consciousness/dashboard/src'"
    run_test "Education platform duplicate removed" "! test -d '$ROOT_DIR/services/education/platform/src'"
    
    # Check that main services still exist
    run_test "Main consciousness service exists" "test -f '$ROOT_DIR/services/consciousness/core/unified_consciousness_service.py'"
    run_test "Main education service exists" "test -f '$ROOT_DIR/services/education/core/educational_platform_service.py' || test -f '$ROOT_DIR/services/education/platform/educational_platform_service.py'"
}

# Test 3: Build artifacts cleanup verification
test_build_cleanup() {
    log_info "Testing build artifacts cleanup..."
    
    # Check .gitignore enhancements
    run_test "Enhanced .gitignore exists" "grep -q 'target/' '$ROOT_DIR/.gitignore'"
    run_test "Gitignore includes build artifacts" "grep -q 'build/simple-kernel-iso/' '$ROOT_DIR/.gitignore'"
    
    # Check that target directories are cleaned
    run_test "No target directories in services" "! find '$ROOT_DIR/services' -name 'target' -type d | grep -q ."
}

# Test 4: Rust workspace consolidation verification
test_rust_workspace() {
    log_info "Testing Rust workspace consolidation..."
    
    # Change to root directory for cargo commands
    cd "$ROOT_DIR"
    
    # Test workspace configuration
    run_test "Workspace members defined" "grep -A 5 'members' '$ROOT_DIR/Cargo.toml' | grep -q 'src/kernel'"
    run_test "Workspace dependencies defined" "grep -q 'workspace.dependencies' '$ROOT_DIR/Cargo.toml'"
    
    # Test workspace compilation
    run_test "Workspace check passes" "cargo check --workspace --quiet"
    
    # Test individual crates use workspace dependencies
    run_test "Kernel uses workspace deps" "grep -q 'workspace = true' src/kernel/Cargo.toml"
    run_test "Security uses workspace deps" "grep -q 'workspace = true' src/security/Cargo.toml"
}

# Test 5: Container optimization verification
test_container_optimization() {
    log_info "Testing container optimization..."
    
    # Check environment-specific configurations
    run_test "Development docker-compose exists" "test -f '$ROOT_DIR/deploy/environments/development/docker-compose.yml'"
    run_test "Production docker-compose exists" "test -f '$ROOT_DIR/deploy/environments/production/docker-compose.yml'"
    run_test "Staging docker-compose exists" "test -f '$ROOT_DIR/deploy/environments/staging/docker-compose.yml'"
    
    # Check deployment script
    run_test "Deployment script exists" "test -x '$ROOT_DIR/deploy/deploy.sh'"
    
    # Check environment templates
    run_test "Development env template exists" "test -f '$ROOT_DIR/deploy/environments/development/.env.template'"
    run_test "Production env template exists" "test -f '$ROOT_DIR/deploy/environments/production/.env.template'"
}

# Test 6: Performance monitoring verification
test_performance_monitoring() {
    log_info "Testing performance monitoring..."
    
    # Check monitoring system exists
    run_test "Performance monitor exists" "test -f '$ROOT_DIR/monitoring/performance_monitor.py'"
    run_test "Metrics server exists" "test -f '$ROOT_DIR/monitoring/metrics_server.py'"
    run_test "Monitoring Dockerfile exists" "test -f '$ROOT_DIR/monitoring/Dockerfile'"
    
    # Test Python syntax
    run_test "Performance monitor syntax" "python -m py_compile '$ROOT_DIR/monitoring/performance_monitor.py'"
    run_test "Metrics server syntax" "python -m py_compile '$ROOT_DIR/monitoring/metrics_server.py'"
}

# Test 7: Documentation verification
test_documentation() {
    log_info "Testing documentation..."
    
    # Check that key documentation exists
    run_test "Codebase audit recommendations exist" "test -f '$ROOT_DIR/CODEBASE_AUDIT_RECOMMENDATIONS.md'"
    run_test "Monitoring documentation exists" "test -f '$ROOT_DIR/monitoring/README.md'"
    
    # Check documentation structure
    run_test "Documentation follows structure" "grep -q '# SynOS' '$ROOT_DIR/monitoring/README.md'"
}

# Test 8: Security improvements verification
test_security_improvements() {
    log_info "Testing security improvements..."
    
    # Check for proper environment variable templates
    run_test "Development env has security vars" "grep -q 'JWT_SECRET_KEY' '$ROOT_DIR/deploy/environments/development/.env.template'"
    run_test "Production env has security vars" "grep -q 'ENCRYPTION_KEY' '$ROOT_DIR/deploy/environments/production/.env.template'"
    
    # Check that no secrets are committed (basic check)
    run_test "No .env files committed" "! find '$ROOT_DIR' -name '.env' -not -path '*/archive/*' | grep -q ."
}

# Test 9: Repository structure verification
test_repository_structure() {
    log_info "Testing repository structure..."
    
    # Check that key directories exist
    run_test "Source directory structure" "test -d '$ROOT_DIR/src/kernel' && test -d '$ROOT_DIR/src/consciousness'"
    run_test "Services directory structure" "test -d '$ROOT_DIR/services/consciousness' && test -d '$ROOT_DIR/services/education'"
    run_test "Deploy directory structure" "test -d '$ROOT_DIR/deploy/environments'"
    run_test "Monitoring directory structure" "test -d '$ROOT_DIR/monitoring'"
}

# Test 10: Performance metrics validation
test_performance_metrics() {
    log_info "Testing performance metrics..."
    
    # Calculate approximate repository size improvement
    if command -v du >/dev/null 2>&1; then
        TOTAL_SIZE=$(du -sh "$ROOT_DIR" 2>/dev/null | cut -f1 || echo "unknown")
        ARCHIVE_SIZE=$(du -sh "$ROOT_DIR/archive" 2>/dev/null | cut -f1 || echo "0")
        log_info "Current repository size: $TOTAL_SIZE (archive: $ARCHIVE_SIZE)"
    fi
    
    # Count Rust files
    RUST_FILES=$(find "$ROOT_DIR/src" -name "*.rs" 2>/dev/null | wc -l)
    run_test "Rust files count reasonable" "test $RUST_FILES -gt 200"
    
    # Count Python files
    PYTHON_FILES=$(find "$ROOT_DIR/services" -name "*.py" 2>/dev/null | wc -l)
    run_test "Python files exist" "test $PYTHON_FILES -gt 10"
}

# Main test runner
main() {
    log_info "Starting SynOS Comprehensive Test Suite"
    log_info "Testing optimization improvements and system functionality"
    echo ""
    
    # Run all test suites
    test_archive_consolidation
    test_duplicate_elimination
    test_build_cleanup
    test_rust_workspace
    test_container_optimization
    test_performance_monitoring
    test_documentation
    test_security_improvements
    test_repository_structure
    test_performance_metrics
    
    echo ""
    log_info "Test Summary"
    echo "============"
    
    if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
        log_success "All tests passed! 🎉"
        log_info "SynOS optimization implementation is successful"
        return 0
    else
        log_error "Some tests failed:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
        log_warning "Please review failed tests and fix issues"
        return 1
    fi
}

# Run main function
main "$@"
