#!/bin/bash
# Syn_OS Development Environment Entrypoint
# Initializes consciousness-aware cybersecurity education kernel development environment

set -e

echo "🧠 Starting Syn_OS Consciousness-Aware Development Environment"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Initialize development environment
initialize_dev_environment() {
    print_info "Initializing development environment..."
    
    # Create necessary directories
    mkdir -p /workspace/syn_os/logs
    mkdir -p /workspace/syn_os/target
    mkdir -p /workspace/syn_os/iso
    mkdir -p /home/synaptic-dev/consciousness-logs
    
    # Set proper permissions
    chown -R synaptic-dev:synaptic-dev /workspace/syn_os/logs
    chown -R synaptic-dev:synaptic-dev /home/synaptic-dev/consciousness-logs
    
    print_status "Development directories initialized"
}

# Check Rust installation and components
check_rust_environment() {
    print_info "Checking Rust development environment..."
    
    if ! command -v rustc &> /dev/null; then
        print_error "Rust compiler not found!"
        exit 1
    fi
    
    if ! command -v cargo &> /dev/null; then
        print_error "Cargo not found!"
        exit 1
    fi
    
    # Check required targets
    if ! rustup target list --installed | grep -q "x86_64-unknown-none"; then
        print_warning "Installing x86_64-unknown-none target..."
        rustup target add x86_64-unknown-none
    fi
    
    # Check required components
    if ! rustup component list --installed | grep -q "rust-src"; then
        print_warning "Installing rust-src component..."
        rustup component add rust-src
    fi
    
    print_status "Rust environment ready"
    print_info "Rust version: $(rustc --version)"
    print_info "Cargo version: $(cargo --version)"
}

# Check QEMU installation
check_qemu_environment() {
    print_info "Checking QEMU environment..."
    
    if ! command -v qemu-system-x86_64 &> /dev/null; then
        print_error "QEMU x86_64 not found!"
        exit 1
    fi
    
    print_status "QEMU environment ready"
    print_info "QEMU version: $(qemu-system-x86_64 --version | head -1)"
}

# Check build tools
check_build_tools() {
    print_info "Checking build tools..."
    
    local tools=("nasm" "grub-mkrescue" "xorriso" "gcc" "ld")
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool not found!"
            exit 1
        fi
    done
    
    print_status "Build tools ready"
}

# Start consciousness monitoring service
start_consciousness_monitor() {
    print_info "Starting consciousness monitoring service..."
    
    if [ -f "/home/synaptic-dev/consciousness-monitor.py" ]; then
        python3 /home/synaptic-dev/consciousness-monitor.py &
        CONSCIOUSNESS_PID=$!
        echo $CONSCIOUSNESS_PID > /tmp/consciousness-monitor.pid
        print_status "Consciousness monitor started (PID: $CONSCIOUSNESS_PID)"
    else
        print_warning "Consciousness monitor script not found"
    fi
}

# Initialize educational sandbox
start_educational_sandbox() {
    print_info "Initializing educational sandbox..."
    
    if [ -f "/home/synaptic-dev/educational-sandbox.sh" ]; then
        /home/synaptic-dev/educational-sandbox.sh &
        SANDBOX_PID=$!
        echo $SANDBOX_PID > /tmp/educational-sandbox.pid
        print_status "Educational sandbox started (PID: $SANDBOX_PID)"
    else
        print_warning "Educational sandbox script not found"
    fi
}

# Start development server
start_development_server() {
    print_info "Starting development server..."
    
    # Start code-server if available
    if command -v code-server &> /dev/null; then
        code-server --bind-addr=0.0.0.0:9000 --auth=none /workspace/syn_os &
        CODE_SERVER_PID=$!
        echo $CODE_SERVER_PID > /tmp/code-server.pid
        print_status "Code server started on port 9000 (PID: $CODE_SERVER_PID)"
    fi
    
    # Start simple HTTP server for logs and documentation
    cd /workspace/syn_os/logs && python3 -m http.server 8080 &
    HTTP_SERVER_PID=$!
    echo $HTTP_SERVER_PID > /tmp/http-server.pid
    print_status "HTTP server started on port 8080 (PID: $HTTP_SERVER_PID)"
}

# Display environment information
display_environment_info() {
    echo ""
    echo -e "${PURPLE}🧠 Syn_OS Development Environment Ready${NC}"
    echo "=========================================="
    echo ""
    echo -e "${GREEN}📂 Workspace:${NC} /workspace/syn_os"
    echo -e "${GREEN}🏠 Home:${NC} /home/synaptic-dev"
    echo -e "${GREEN}🧠 Consciousness Logs:${NC} /home/synaptic-dev/consciousness-logs"
    echo ""
    echo -e "${BLUE}🔧 Available Services:${NC}"
    echo "  • Code Server: http://localhost:9000"
    echo "  • HTTP Server: http://localhost:8080"
    echo "  • Consciousness Monitor: Background service"
    echo "  • Educational Sandbox: Background service"
    echo ""
    echo -e "${YELLOW}🚀 Quick Commands:${NC}"
    echo "  • cargo build --release --target x86_64-unknown-none  # Build kernel"
    echo "  • ./simple_qemu_test.sh                              # Test in QEMU"
    echo "  • ./build_and_test.sh                                # Full build & test"
    echo "  • python3 consciousness-monitor.py                   # Manual consciousness monitor"
    echo ""
    echo -e "${GREEN}🎓 Educational Features:${NC}"
    echo "  • Consciousness-aware learning adaptation"
    echo "  • Neural darwinism security simulation"
    echo "  • Safe exploit demonstration environment"
    echo "  • Real-time learning analytics"
    echo ""
}

# Cleanup function for graceful shutdown
cleanup() {
    print_info "Shutting down services..."
    
    # Kill background processes
    if [ -f /tmp/consciousness-monitor.pid ]; then
        kill $(cat /tmp/consciousness-monitor.pid) 2>/dev/null || true
        rm -f /tmp/consciousness-monitor.pid
    fi
    
    if [ -f /tmp/educational-sandbox.pid ]; then
        kill $(cat /tmp/educational-sandbox.pid) 2>/dev/null || true
        rm -f /tmp/educational-sandbox.pid
    fi
    
    if [ -f /tmp/code-server.pid ]; then
        kill $(cat /tmp/code-server.pid) 2>/dev/null || true
        rm -f /tmp/code-server.pid
    fi
    
    if [ -f /tmp/http-server.pid ]; then
        kill $(cat /tmp/http-server.pid) 2>/dev/null || true
        rm -f /tmp/http-server.pid
    fi
    
    print_status "Development environment shutdown complete"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main initialization sequence
main() {
    initialize_dev_environment
    check_rust_environment
    check_qemu_environment
    check_build_tools
    start_consciousness_monitor
    start_educational_sandbox
    start_development_server
    display_environment_info
    
    # If no arguments provided, start interactive shell
    if [ $# -eq 0 ]; then
        print_info "Starting interactive development shell..."
        exec /bin/bash
    else
        # Execute provided command
        print_info "Executing: $*"
        exec "$@"
    fi
}

# Run main function with all arguments
main "$@"