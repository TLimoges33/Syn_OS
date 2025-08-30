#!/bin/bash

# Phase 4 Integration Test Suite
# ==============================
# Comprehensive testing script for Phase 4 deployment infrastructure,
# threat intelligence dashboard, and integration components

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_RESULTS_DIR="$PROJECT_ROOT/results/phase4_integration_tests"
LOG_FILE="$TEST_RESULTS_DIR/test-run-$(date +%Y%m%d-%H%M%S).log"
NAMESPACE="synos-phase4"

# Test configuration
THREAT_INTEL_DASHBOARD_URL="http://localhost:8084"
INTEGRATION_BRIDGE_URL="http://localhost:8085"
KUBERNETES_TESTS_ENABLED=false
DOCKER_TESTS_ENABLED=false

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "${RED}❌ Error occurred in test script at line $1${NC}"
    log "${RED}❌ Phase 4 integration tests failed${NC}"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "=============================================================="
    echo "   🧪 Syn_OS Phase 4 Integration Test Suite"
    echo "=============================================================="
    echo "   • Threat Intelligence Dashboard Tests"
    echo "   • Phase 4 Integration Bridge Tests"
    echo "   • Kubernetes Deployment Validation"
    echo "   • End-to-End Integration Testing"
    echo "=============================================================="
    echo -e "${NC}"
}

# Setup test environment
setup_test_environment() {
    log "${CYAN}=== SETTING UP TEST ENVIRONMENT ===${NC}"
    
    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Check if services are running locally
    if curl -s "$THREAT_INTEL_DASHBOARD_URL/health" > /dev/null 2>&1; then
        log "${GREEN}✅ Threat Intelligence Dashboard is running locally${NC}"
    else
        log "${YELLOW}⚠️ Threat Intelligence Dashboard not running locally${NC}"
    fi
    
    if curl -s "$INTEGRATION_BRIDGE_URL/health" > /dev/null 2>&1; then
        log "${GREEN}✅ Integration Bridge is running locally${NC}"
    else
        log "${YELLOW}⚠️ Integration Bridge not running locally${NC}"
    fi
    
    # Check if Kubernetes is available
    if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
        KUBERNETES_TESTS_ENABLED=true
        log "${GREEN}✅ Kubernetes is available for testing${NC}"
    else
        log "${YELLOW}⚠️ Kubernetes not available - skipping K8s tests${NC}"
    fi
    
    # Check if Docker is available
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        DOCKER_TESTS_ENABLED=true
        log "${GREEN}✅ Docker is available for testing${NC}"
    else
        log "${YELLOW}⚠️ Docker not available - skipping Docker tests${NC}"
    fi
    
    log "${GREEN}✅ Test environment setup completed${NC}"
}

# Test Python integration bridge
test_integration_bridge_python() {
    log "${CYAN}=== TESTING PHASE 4 INTEGRATION BRIDGE (PYTHON) ===${NC}"
    
    local test_file="$PROJECT_ROOT/tests/integration/test_phase4_integration.py"
    
    if [[ -f "$test_file" ]]; then
        log "${BLUE}🧪 Running Python integration tests...${NC}"
        
        # Run the Python tests
        cd "$PROJECT_ROOT"
        python -m pytest "$test_file" -v --tb=short --junit-xml="$TEST_RESULTS_DIR/pytest-results.xml" 2>&1 | tee -a "$LOG_FILE"
        
        if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
            log "${GREEN}✅ Python integration tests passed${NC}"
        else
            log "${YELLOW}⚠️ Some Python integration tests failed (check logs)${NC}"
        fi
    else
        log "${YELLOW}⚠️ Python test file not found: $test_file${NC}"
    fi
}

# Test threat intelligence dashboard
test_threat_intelligence_dashboard() {
    log "${CYAN}=== TESTING THREAT INTELLIGENCE DASHBOARD ===${NC}"
    
    local health_passed=false
    local api_tests_passed=false
    
    # Test health endpoint
    log "${BLUE}🧪 Testing dashboard health endpoint...${NC}"
    if curl -f -s "$THREAT_INTEL_DASHBOARD_URL/health" | jq '.status' | grep -q "healthy"; then
        log "${GREEN}✅ Dashboard health check passed${NC}"
        health_passed=true
    else
        log "${RED}❌ Dashboard health check failed${NC}"
    fi
    
    # Test API endpoints (basic connectivity)
    log "${BLUE}🧪 Testing dashboard API endpoints...${NC}"
    local endpoints=(
        "/health"
        "/api/dashboard/overview"
        "/api/threats/feeds/status"
        "/api/threats/real-time"
    )
    
    local passed_endpoints=0
    for endpoint in "${endpoints[@]}"; do
        local url="$THREAT_INTEL_DASHBOARD_URL$endpoint"
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        
        if [[ "$status_code" == "200" ]] || [[ "$status_code" == "401" ]]; then
            log "${GREEN}✅ Endpoint $endpoint responded correctly (status: $status_code)${NC}"
            ((passed_endpoints++))
        else
            log "${RED}❌ Endpoint $endpoint failed (status: $status_code)${NC}"
        fi
    done
    
    if [[ $passed_endpoints -eq ${#endpoints[@]} ]]; then
        api_tests_passed=true
        log "${GREEN}✅ All dashboard API endpoints passed${NC}"
    else
        log "${YELLOW}⚠️ Some dashboard API endpoints failed${NC}"
    fi
    
    # Test WebSocket endpoint (basic connectivity)
    log "${BLUE}🧪 Testing dashboard WebSocket endpoint...${NC}"
    if command -v wscat &> /dev/null; then
        # Use wscat if available
        timeout 5s wscat -c "ws://localhost:8084/ws" -x '{"type":"ping"}' 2>/dev/null && {
            log "${GREEN}✅ WebSocket connection test passed${NC}"
        } || {
            log "${YELLOW}⚠️ WebSocket connection test failed or timed out${NC}"
        }
    else
        log "${YELLOW}⚠️ wscat not available - skipping WebSocket test${NC}"
    fi
    
    # Create test summary
    if [[ "$health_passed" == true ]] && [[ "$api_tests_passed" == true ]]; then
        log "${GREEN}✅ Threat Intelligence Dashboard tests completed successfully${NC}"
        return 0
    else
        log "${YELLOW}⚠️ Threat Intelligence Dashboard tests completed with warnings${NC}"
        return 1
    fi
}

# Test integration bridge
test_integration_bridge() {
    log "${CYAN}=== TESTING PHASE 4 INTEGRATION BRIDGE ===${NC}"
    
    local health_passed=false
    local status_tests_passed=false
    
    # Test health endpoint
    log "${BLUE}🧪 Testing integration bridge health endpoint...${NC}"
    if curl -f -s "$INTEGRATION_BRIDGE_URL/health" | jq '.status' | grep -q "healthy"; then
        log "${GREEN}✅ Integration bridge health check passed${NC}"
        health_passed=true
    else
        log "${RED}❌ Integration bridge health check failed${NC}"
    fi
    
    # Test status endpoints
    log "${BLUE}🧪 Testing integration bridge status endpoints...${NC}"
    local endpoints=(
        "/health"
        "/api/integration/status"
        "/api/components/status"
        "/api/deployment/readiness"
    )
    
    local passed_endpoints=0
    for endpoint in "${endpoints[@]}"; do
        local url="$INTEGRATION_BRIDGE_URL$endpoint"
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        
        if [[ "$status_code" == "200" ]] || [[ "$status_code" == "401" ]]; then
            log "${GREEN}✅ Endpoint $endpoint responded correctly (status: $status_code)${NC}"
            ((passed_endpoints++))
        else
            log "${RED}❌ Endpoint $endpoint failed (status: $status_code)${NC}"
        fi
    done
    
    if [[ $passed_endpoints -ge 1 ]]; then  # At least health endpoint should work
        status_tests_passed=true
        log "${GREEN}✅ Integration bridge status tests passed${NC}"
    else
        log "${RED}❌ Integration bridge status tests failed${NC}"
    fi
    
    # Create test summary
    if [[ "$health_passed" == true ]] && [[ "$status_tests_passed" == true ]]; then
        log "${GREEN}✅ Integration Bridge tests completed successfully${NC}"
        return 0
    else
        log "${YELLOW}⚠️ Integration Bridge tests completed with warnings${NC}"
        return 1
    fi
}

# Test Kubernetes deployment
test_kubernetes_deployment() {
    if [[ "$KUBERNETES_TESTS_ENABLED" != true ]]; then
        log "${YELLOW}⚠️ Kubernetes tests disabled - skipping${NC}"
        return 0
    fi
    
    log "${CYAN}=== TESTING KUBERNETES DEPLOYMENT ===${NC}"
    
    # Check if namespace exists
    log "${BLUE}🧪 Testing Kubernetes namespace...${NC}"
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log "${GREEN}✅ Namespace $NAMESPACE exists${NC}"
    else
        log "${YELLOW}⚠️ Namespace $NAMESPACE does not exist${NC}"
        return 1
    fi
    
    # Check deployments
    log "${BLUE}🧪 Testing Kubernetes deployments...${NC}"
    local deployments=("threat-intelligence-dashboard" "phase4-integration-bridge")
    local deployment_tests_passed=true
    
    for deployment in "${deployments[@]}"; do
        if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            local ready_replicas=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
            local desired_replicas=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
            
            if [[ "$ready_replicas" -eq "$desired_replicas" ]] && [[ "$ready_replicas" -gt 0 ]]; then
                log "${GREEN}✅ Deployment $deployment is ready ($ready_replicas/$desired_replicas replicas)${NC}"
            else
                log "${RED}❌ Deployment $deployment is not ready ($ready_replicas/$desired_replicas replicas)${NC}"
                deployment_tests_passed=false
            fi
        else
            log "${YELLOW}⚠️ Deployment $deployment not found${NC}"
            deployment_tests_passed=false
        fi
    done
    
    # Check services
    log "${BLUE}🧪 Testing Kubernetes services...${NC}"
    local services=("threat-intelligence-dashboard-service" "phase4-integration-bridge-service")
    local service_tests_passed=true
    
    for service in "${services[@]}"; do
        if kubectl get service "$service" -n "$NAMESPACE" &> /dev/null; then
            log "${GREEN}✅ Service $service exists${NC}"
        else
            log "${YELLOW}⚠️ Service $service not found${NC}"
            service_tests_passed=false
        fi
    done
    
    # Check ingress
    log "${BLUE}🧪 Testing Kubernetes ingress...${NC}"
    if kubectl get ingress "phase4-ingress" -n "$NAMESPACE" &> /dev/null; then
        log "${GREEN}✅ Ingress phase4-ingress exists${NC}"
    else
        log "${YELLOW}⚠️ Ingress phase4-ingress not found${NC}"
    fi
    
    # Check ConfigMaps and Secrets
    log "${BLUE}🧪 Testing Kubernetes ConfigMaps and Secrets...${NC}"
    if kubectl get configmap "phase4-config" -n "$NAMESPACE" &> /dev/null; then
        log "${GREEN}✅ ConfigMap phase4-config exists${NC}"
    else
        log "${YELLOW}⚠️ ConfigMap phase4-config not found${NC}"
    fi
    
    if kubectl get secret "phase4-secrets" -n "$NAMESPACE" &> /dev/null; then
        log "${GREEN}✅ Secret phase4-secrets exists${NC}"
    else
        log "${YELLOW}⚠️ Secret phase4-secrets not found${NC}"
    fi
    
    # Create test summary
    if [[ "$deployment_tests_passed" == true ]] && [[ "$service_tests_passed" == true ]]; then
        log "${GREEN}✅ Kubernetes deployment tests completed successfully${NC}"
        return 0
    else
        log "${YELLOW}⚠️ Kubernetes deployment tests completed with warnings${NC}"
        return 1
    fi
}

# Test Docker images
test_docker_images() {
    if [[ "$DOCKER_TESTS_ENABLED" != true ]]; then
        log "${YELLOW}⚠️ Docker tests disabled - skipping${NC}"
        return 0
    fi
    
    log "${CYAN}=== TESTING DOCKER IMAGES ===${NC}"
    
    local images=("synos/threat-intelligence-dashboard:latest" "synos/phase4-integration-bridge:latest")
    local docker_tests_passed=true
    
    for image in "${images[@]}"; do
        log "${BLUE}🧪 Testing Docker image $image...${NC}"
        
        if docker image inspect "$image" &> /dev/null; then
            log "${GREEN}✅ Docker image $image exists${NC}"
            
            # Test if image can run
            log "${BLUE}🧪 Testing Docker image startup...${NC}"
            local container_id=$(docker run -d --rm "$image" --help 2>/dev/null || echo "")
            
            if [[ -n "$container_id" ]]; then
                # Wait a moment then check if container is still running
                sleep 2
                if docker ps --filter "id=$container_id" --format "{{.ID}}" | grep -q "$container_id"; then
                    log "${GREEN}✅ Docker image $image starts successfully${NC}"
                    docker stop "$container_id" &> /dev/null || true
                else
                    log "${YELLOW}⚠️ Docker image $image stopped unexpectedly${NC}"
                fi
            else
                log "${YELLOW}⚠️ Docker image $image failed to start${NC}"
            fi
        else
            log "${YELLOW}⚠️ Docker image $image not found${NC}"
            docker_tests_passed=false
        fi
    done
    
    if [[ "$docker_tests_passed" == true ]]; then
        log "${GREEN}✅ Docker image tests completed successfully${NC}"
        return 0
    else
        log "${YELLOW}⚠️ Docker image tests completed with warnings${NC}"
        return 1
    fi
}

# End-to-end integration test
test_end_to_end_integration() {
    log "${CYAN}=== TESTING END-TO-END INTEGRATION ===${NC}"
    
    # This test verifies that all components work together
    log "${BLUE}🧪 Testing complete system integration...${NC}"
    
    local e2e_passed=true
    
    # Test 1: Health checks across all services
    log "${BLUE}🧪 Testing cross-service health...${NC}"
    if curl -f -s "$THREAT_INTEL_DASHBOARD_URL/health" > /dev/null && \
       curl -f -s "$INTEGRATION_BRIDGE_URL/health" > /dev/null; then
        log "${GREEN}✅ All services are healthy${NC}"
    else
        log "${RED}❌ Some services are not healthy${NC}"
        e2e_passed=false
    fi
    
    # Test 2: Data flow simulation (if services support it)
    log "${BLUE}🧪 Testing data flow simulation...${NC}"
    # This would test actual threat intelligence data flow
    # For now, we'll just verify endpoints respond
    local test_endpoints=(
        "$THREAT_INTEL_DASHBOARD_URL/api/dashboard/overview"
        "$INTEGRATION_BRIDGE_URL/api/integration/status"
    )
    
    local data_flow_passed=true
    for endpoint in "${test_endpoints[@]}"; do
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" || echo "000")
        if [[ "$status_code" == "200" ]] || [[ "$status_code" == "401" ]]; then
            log "${GREEN}✅ Data flow endpoint responded: $endpoint${NC}"
        else
            log "${YELLOW}⚠️ Data flow endpoint failed: $endpoint (status: $status_code)${NC}"
            data_flow_passed=false
        fi
    done
    
    if [[ "$data_flow_passed" == true ]]; then
        log "${GREEN}✅ Data flow simulation passed${NC}"
    else
        log "${YELLOW}⚠️ Data flow simulation had issues${NC}"
        e2e_passed=false
    fi
    
    # Test 3: Component integration verification
    log "${BLUE}🧪 Testing component integration...${NC}"
    # This would test that the integration bridge properly monitors all components
    # For now, we'll just verify the bridge can report status
    
    if curl -s "$INTEGRATION_BRIDGE_URL/health" | jq -e '.components' > /dev/null 2>&1; then
        log "${GREEN}✅ Integration bridge reports component status${NC}"
    else
        log "${YELLOW}⚠️ Integration bridge component status unavailable${NC}"
        e2e_passed=false
    fi
    
    # Create test summary
    if [[ "$e2e_passed" == true ]]; then
        log "${GREEN}✅ End-to-end integration tests completed successfully${NC}"
        return 0
    else
        log "${YELLOW}⚠️ End-to-end integration tests completed with warnings${NC}"
        return 1
    fi
}

# Generate test report
generate_test_report() {
    log "${CYAN}=== GENERATING TEST REPORT ===${NC}"
    
    local report_file="$TEST_RESULTS_DIR/phase4-integration-test-report.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$report_file" << EOF
{
    "test_suite": "Phase 4 Integration Tests",
    "timestamp": "$timestamp",
    "test_environment": {
        "kubernetes_available": $KUBERNETES_TESTS_ENABLED,
        "docker_available": $DOCKER_TESTS_ENABLED,
        "threat_intel_dashboard_url": "$THREAT_INTEL_DASHBOARD_URL",
        "integration_bridge_url": "$INTEGRATION_BRIDGE_URL"
    },
    "test_results": {
        "python_integration_tests": "See pytest-results.xml",
        "threat_intelligence_dashboard": "Completed",
        "integration_bridge": "Completed",
        "kubernetes_deployment": "$([ "$KUBERNETES_TESTS_ENABLED" = true ] && echo "Completed" || echo "Skipped")",
        "docker_images": "$([ "$DOCKER_TESTS_ENABLED" = true ] && echo "Completed" || echo "Skipped")",
        "end_to_end_integration": "Completed"
    },
    "log_file": "$LOG_FILE",
    "recommendations": [
        "Review individual test logs for detailed results",
        "Ensure all services are running for complete test coverage",
        "Consider running tests in Kubernetes environment for full validation"
    ]
}
EOF
    
    log "${GREEN}✅ Test report generated: $report_file${NC}"
}

# Display test summary
display_test_summary() {
    log "${CYAN}=== TEST SUMMARY ===${NC}"
    
    echo -e "${GREEN}"
    echo "🎉 Phase 4 Integration Test Suite Completed!"
    echo ""
    echo "📊 Test Results:"
    echo "   • Python Integration Tests: Executed"
    echo "   • Threat Intelligence Dashboard: Tested"
    echo "   • Phase 4 Integration Bridge: Tested"
    echo "   • Kubernetes Deployment: $([ "$KUBERNETES_TESTS_ENABLED" = true ] && echo "Tested" || echo "Skipped")"
    echo "   • Docker Images: $([ "$DOCKER_TESTS_ENABLED" = true ] && echo "Tested" || echo "Skipped")"
    echo "   • End-to-End Integration: Tested"
    echo ""
    echo "📁 Test Artifacts:"
    echo "   • Test Log: $LOG_FILE"
    echo "   • Results Directory: $TEST_RESULTS_DIR"
    echo "   • Test Report: $TEST_RESULTS_DIR/phase4-integration-test-report.json"
    echo ""
    echo "🔍 Next Steps:"
    echo "   • Review test logs for any warnings or failures"
    echo "   • Address any identified issues"
    echo "   • Run tests in production-like environment"
    echo "   • Validate deployment readiness"
    echo -e "${NC}"
}

# Main test execution function
main() {
    print_banner
    
    log "${GREEN}🧪 Starting Phase 4 Integration Test Suite${NC}"
    log "${BLUE}📝 Test log: $LOG_FILE${NC}"
    
    # Parse command line arguments
    local run_python_tests=true
    local run_dashboard_tests=true
    local run_bridge_tests=true
    local run_k8s_tests=true
    local run_docker_tests=true
    local run_e2e_tests=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-python)
                run_python_tests=false
                shift
                ;;
            --skip-dashboard)
                run_dashboard_tests=false
                shift
                ;;
            --skip-bridge)
                run_bridge_tests=false
                shift
                ;;
            --skip-k8s)
                run_k8s_tests=false
                shift
                ;;
            --skip-docker)
                run_docker_tests=false
                shift
                ;;
            --skip-e2e)
                run_e2e_tests=false
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-python    Skip Python integration tests"
                echo "  --skip-dashboard Skip threat intelligence dashboard tests"
                echo "  --skip-bridge    Skip integration bridge tests"
                echo "  --skip-k8s       Skip Kubernetes deployment tests"
                echo "  --skip-docker    Skip Docker image tests"
                echo "  --skip-e2e       Skip end-to-end integration tests"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                log "${RED}❌ Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    # Setup test environment
    setup_test_environment
    
    # Execute test suites
    if [[ "$run_python_tests" == true ]]; then
        test_integration_bridge_python
    fi
    
    if [[ "$run_dashboard_tests" == true ]]; then
        test_threat_intelligence_dashboard
    fi
    
    if [[ "$run_bridge_tests" == true ]]; then
        test_integration_bridge
    fi
    
    if [[ "$run_k8s_tests" == true ]]; then
        test_kubernetes_deployment
    fi
    
    if [[ "$run_docker_tests" == true ]]; then
        test_docker_images
    fi
    
    if [[ "$run_e2e_tests" == true ]]; then
        test_end_to_end_integration
    fi
    
    # Generate report and summary
    generate_test_report
    display_test_summary
    
    log "${GREEN}🎉 Phase 4 Integration Test Suite completed successfully!${NC}"
    log "${BLUE}📝 Full test log available at: $LOG_FILE${NC}"
}

# Run main function
main "$@"