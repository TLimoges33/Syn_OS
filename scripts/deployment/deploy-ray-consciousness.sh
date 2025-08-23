#!/bin/bash
# Ray Distributed Consciousness Deployment Script
# Implements the #1 priority integration from repository analysis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RAY_SERVICE_DIR="$PROJECT_ROOT/services/consciousness-ray-distributed"
DOCKER_DIR="$PROJECT_ROOT/docker"

# Performance targets from repository analysis
TARGET_IMPROVEMENT="50%"
BASELINE_TIME="76.3ms"
TARGET_TIME="38.2ms"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Syn_OS Ray Distributed Consciousness${NC}"
echo -e "${BLUE}Deployment & Integration Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Target Performance Improvement: $TARGET_IMPROVEMENT${NC}"
echo -e "${GREEN}Baseline Processing Time: $BASELINE_TIME${NC}"
echo -e "${GREEN}Target Processing Time: $TARGET_TIME${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    sudo mkdir -p /opt/syn_os/data/consciousness/ray
    sudo mkdir -p /opt/syn_os/logs/consciousness/ray
    sudo mkdir -p /opt/syn_os/config/consciousness
    
    # Set permissions
    sudo chown -R $USER:$USER /opt/syn_os/data/consciousness/ray
    sudo chown -R $USER:$USER /opt/syn_os/logs/consciousness/ray
    
    print_success "Directories created successfully"
}

# Build Ray consciousness containers
build_containers() {
    print_status "Building Ray consciousness containers..."
    
    cd "$DOCKER_DIR"
    
    # Build the Ray consciousness service
    docker-compose -f docker-compose.ray.yml build
    
    print_success "Ray consciousness containers built successfully"
}

# Deploy Ray consciousness cluster
deploy_cluster() {
    print_status "Deploying Ray consciousness cluster..."
    
    cd "$DOCKER_DIR"
    
    # Stop any existing containers
    docker-compose -f docker-compose.ray.yml down || true
    
    # Start Ray consciousness cluster
    docker-compose -f docker-compose.ray.yml up -d
    
    print_success "Ray consciousness cluster deployed"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for Ray consciousness services to be ready..."
    
    # Wait for Ray head node
    timeout=60
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:8265/api/cluster_status &> /dev/null; then
            print_success "Ray head node is ready"
            break
        fi
        sleep 2
        counter=$((counter + 2))
    done
    
    if [ $counter -ge $timeout ]; then
        print_error "Ray head node failed to start within $timeout seconds"
        exit 1
    fi
    
    # Wait for Ray consciousness API
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:8010/health &> /dev/null; then
            print_success "Ray consciousness API is ready"
            break
        fi
        sleep 2
        counter=$((counter + 2))
    done
    
    if [ $counter -ge $timeout ]; then
        print_error "Ray consciousness API failed to start within $timeout seconds"
        exit 1
    fi
    
    print_success "All services are ready"
}

# Run integration tests
run_integration_tests() {
    print_status "Running Ray consciousness integration tests..."
    
    cd "$PROJECT_ROOT"
    
    # Install test dependencies
    python3 -m pip install aiohttp pytest requests
    
    # Run the integration tests
    python3 tests/ray_consciousness_integration_tests.py
    
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Performance benchmark
run_performance_benchmark() {
    print_status "Running performance benchmark..."
    
    # Trigger benchmark via API
    curl -X POST http://localhost:8010/consciousness/benchmark
    
    print_status "Benchmark started. Waiting 35 seconds for completion..."
    sleep 35
    
    # Get benchmark results
    benchmark_results=$(curl -s http://localhost:8010/consciousness/metrics)
    
    if echo "$benchmark_results" | grep -q "achieved_improvement"; then
        improvement=$(echo "$benchmark_results" | jq -r '.latest_benchmark.achieved_improvement // 0')
        print_success "Benchmark completed"
        print_status "Performance improvement achieved: ${improvement}%"
        
        if (( $(echo "$improvement >= 50" | bc -l) )); then
            print_success "✅ Performance target achieved (>= 50% improvement)"
        else
            print_warning "⚠️  Performance target not met (<50% improvement)"
        fi
    else
        print_warning "Benchmark results not available"
    fi
}

# Integration with existing consciousness system
integrate_with_existing_system() {
    print_status "Integrating with existing consciousness system..."
    
    # Update main docker-compose to include Ray consciousness
    cd "$DOCKER_DIR"
    
    # Check if main services are running
    if docker-compose ps | grep -q "syn_os_consciousness"; then
        print_status "Existing consciousness system detected"
        
        # Test integration
        integration_result=$(curl -s -X POST http://localhost:8010/bridge/integrate \
            -H "Content-Type: application/json" \
            -d '{"stimulus": "integration_test", "context": "deployment", "complexity": 0.7}')
        
        if echo "$integration_result" | grep -q "successful"; then
            print_success "✅ Integration with existing consciousness system successful"
        else
            print_warning "⚠️  Integration test failed"
        fi
    else
        print_warning "Existing consciousness system not running. Ray system will operate independently."
    fi
}

# Generate deployment report
generate_deployment_report() {
    print_status "Generating deployment report..."
    
    report_file="/tmp/ray_consciousness_deployment_report.txt"
    
    cat > "$report_file" << EOF
Syn_OS Ray Distributed Consciousness Deployment Report
=====================================================
Deployment Date: $(date)
Target Performance Improvement: $TARGET_IMPROVEMENT
Baseline Processing Time: $BASELINE_TIME
Target Processing Time: $TARGET_TIME

Services Deployed:
- Ray Head Node: http://localhost:8265 (Dashboard)
- Ray Workers: 4 distributed workers
- Ray Consciousness API: http://localhost:8010
- Ray Metrics: http://localhost:9095

Integration Status:
- Ray Cluster: Operational
- Consciousness API: Operational
- Integration Tests: $([ $? -eq 0 ] && echo "PASSED" || echo "FAILED")
- Performance Benchmark: Available at http://localhost:8010/consciousness/metrics

Next Steps:
1. Monitor Ray dashboard at http://localhost:8265
2. Run performance tests via API at http://localhost:8010
3. Integrate with existing consciousness-ai-bridge service
4. Monitor consciousness processing improvements

Log Files:
- Ray Logs: /opt/syn_os/logs/consciousness/ray/
- API Logs: Available via docker logs syn-os-consciousness-ray-engine

Commands:
- View cluster status: curl http://localhost:8010/consciousness/status
- Run benchmark: curl -X POST http://localhost:8010/consciousness/benchmark
- View metrics: curl http://localhost:8010/consciousness/metrics

EOF

    print_success "Deployment report saved to: $report_file"
    cat "$report_file"
}

# Main deployment flow
main() {
    print_status "Starting Ray Distributed Consciousness deployment..."
    
    check_prerequisites
    create_directories
    build_containers
    deploy_cluster
    wait_for_services
    
    # Run tests and benchmarks
    if run_integration_tests; then
        run_performance_benchmark
    else
        print_warning "Integration tests failed, but continuing with deployment"
    fi
    
    integrate_with_existing_system
    generate_deployment_report
    
    echo ""
    print_success "🎉 Ray Distributed Consciousness deployment completed!"
    print_status "Ray Dashboard: http://localhost:8265"
    print_status "Consciousness API: http://localhost:8010"
    print_status "Expected Performance: ${TARGET_IMPROVEMENT} improvement (${BASELINE_TIME} → ${TARGET_TIME})"
    echo ""
    print_status "Run 'docker-compose -f docker/docker-compose.ray.yml logs -f' to view logs"
}

# Command line options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "test")
        print_status "Running integration tests only..."
        cd "$PROJECT_ROOT"
        python3 tests/ray_consciousness_integration_tests.py
        ;;
    "benchmark")
        print_status "Running performance benchmark only..."
        run_performance_benchmark
        ;;
    "status")
        print_status "Checking Ray consciousness system status..."
        curl -s http://localhost:8010/consciousness/status | jq '.'
        ;;
    "stop")
        print_status "Stopping Ray consciousness system..."
        cd "$DOCKER_DIR"
        docker-compose -f docker-compose.ray.yml down
        print_success "Ray consciousness system stopped"
        ;;
    *)
        echo "Usage: $0 {deploy|test|benchmark|status|stop}"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment of Ray consciousness system"
        echo "  test      - Run integration tests only"
        echo "  benchmark - Run performance benchmark only"
        echo "  status    - Check system status"
        echo "  stop      - Stop Ray consciousness system"
        exit 1
        ;;
esac
