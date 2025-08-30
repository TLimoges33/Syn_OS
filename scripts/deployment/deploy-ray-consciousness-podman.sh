#!/bin/bash
# Ray Distributed Consciousness Deployment Script (Podman Compatible)
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
echo -e "${BLUE}Deployment & Integration Script (Podman)${NC}"
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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python3 (for Ray)
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed"
        exit 1
    fi
    
    # Check Podman (instead of Docker)
    if ! command -v podman &> /dev/null; then
        print_error "Podman is not installed"
        exit 1
    fi
    
    # Check Podman Compose (instead of Docker Compose)
    if ! command -v podman-compose &> /dev/null; then
        print_error "Podman Compose is not installed"
        exit 1
    fi
    
    # Check Ray installation
    if ! python3 -c "import ray" &> /dev/null; then
        print_warning "Ray not installed, installing..."
        pip3 install ray[default]==2.34.0
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Create required directories
    sudo mkdir -p /var/log/syn_os/ray
    sudo mkdir -p /var/lib/syn_os/ray
    sudo chown -R $USER:$USER /var/log/syn_os /var/lib/syn_os
    
    print_success "Directories created successfully"
}

# Function to deploy with direct Python execution (no containers for now)
deploy_direct() {
    print_status "Deploying Ray consciousness directly (non-containerized)..."
    
    # Start Ray cluster locally
    print_status "Starting local Ray cluster..."
    ray stop || true  # Stop any existing cluster
    ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --disable-usage-stats
    
    # Run the consciousness service
    print_status "Starting Ray consciousness service..."
    cd "$RAY_SERVICE_DIR"
    
    # Start the API service in background
    python3 ray_consciousness_api.py &
    RAY_API_PID=$!
    echo $RAY_API_PID > /tmp/ray_consciousness_api.pid
    
    print_success "Ray consciousness service started"
    print_status "Ray Dashboard: http://localhost:8265"
    print_status "Consciousness API: http://localhost:8001"
    print_status "API PID saved to /tmp/ray_consciousness_api.pid"
}

# Function to stop the deployment
stop_deployment() {
    print_status "Stopping Ray consciousness deployment..."
    
    # Stop API service
    if [ -f /tmp/ray_consciousness_api.pid ]; then
        PID=$(cat /tmp/ray_consciousness_api.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            print_success "Ray consciousness API stopped"
        fi
        rm -f /tmp/ray_consciousness_api.pid
    fi
    
    # Stop Ray cluster
    ray stop
    print_success "Ray cluster stopped"
}

# Function to check deployment status
check_status() {
    print_status "Checking Ray consciousness deployment status..."
    
    # Check Ray cluster
    if ray status 2>/dev/null | grep -q "head"; then
        print_success "Ray cluster is running"
        print_status "Ray Dashboard: http://localhost:8265"
    else
        print_warning "Ray cluster is not running"
    fi
    
    # Check API service
    if [ -f /tmp/ray_consciousness_api.pid ]; then
        PID=$(cat /tmp/ray_consciousness_api.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_success "Ray consciousness API is running (PID: $PID)"
            print_status "API endpoint: http://localhost:8001"
        else
            print_warning "Ray consciousness API is not running"
        fi
    else
        print_warning "Ray consciousness API PID file not found"
    fi
    
    # Test API endpoint
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "API health check passed"
    else
        print_warning "API health check failed"
    fi
}

# Function to run performance test
run_performance_test() {
    print_status "Running Ray consciousness performance test..."
    
    cd "$PROJECT_ROOT"
    
    # Create and run performance test
    cat << 'EOF' > ray_performance_test.py
#!/usr/bin/env python3
import asyncio
import time
import requests
import json
from typing import Dict, List, Any

async def performance_test():
    """Test Ray consciousness performance"""
    print("🔬 Ray Consciousness Performance Test")
    print("=" * 50)
    
    # Test data
    test_data = [
        {"stimulus_id": f"test_{i}", "input": f"consciousness_input_{i}"}
        for i in range(100)
    ]
    
    try:
        # Test consciousness processing endpoint
        print("📊 Testing consciousness processing...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8001/consciousness/process",
            json={"batch_data": test_data},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            processing_time = (time.time() - start_time) * 1000
            
            print(f"✅ Processing completed in {processing_time:.2f}ms")
            print(f"📈 Items processed: {result.get('items_processed', len(test_data))}")
            print(f"🚀 Performance improvement target: 50%")
            
            # Calculate improvement (simulated baseline: 76.3ms per item)
            baseline_total = len(test_data) * 76.3
            improvement = ((baseline_total - processing_time) / baseline_total) * 100
            
            print(f"📊 Estimated improvement: {improvement:.1f}%")
            
            if improvement >= 50:
                print("🎉 PERFORMANCE TARGET ACHIEVED!")
                return True
            else:
                print("⚠️  Performance target not met, but system is functional")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(performance_test())
    exit(0 if success else 1)
EOF

    python3 ray_performance_test.py
    rm -f ray_performance_test.py
}

# Main deployment logic
case "$1" in
    "deploy")
        print_status "Starting Ray Distributed Consciousness deployment..."
        check_prerequisites
        create_directories
        deploy_direct
        sleep 5  # Give services time to start
        check_status
        print_success "Ray consciousness deployment completed!"
        print_status "Run './scripts/deploy-ray-consciousness-podman.sh test' to validate performance"
        ;;
    "stop")
        stop_deployment
        ;;
    "status")
        check_status
        ;;
    "test")
        run_performance_test
        ;;
    "restart")
        stop_deployment
        sleep 2
        deploy_direct
        sleep 5
        check_status
        ;;
    *)
        echo "Usage: $0 {deploy|stop|status|test|restart}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy Ray consciousness system"
        echo "  stop     - Stop Ray consciousness system"
        echo "  status   - Check deployment status"
        echo "  test     - Run performance test"
        echo "  restart  - Restart the system"
        exit 1
        ;;
esac

print_success "Ray consciousness script completed successfully!"
