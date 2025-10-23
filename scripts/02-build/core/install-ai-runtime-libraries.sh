#!/bin/bash

################################################################################
# SynOS AI Runtime Library Installation Script
#
# Installs TensorFlow Lite, ONNX Runtime, and PyTorch libraries
# for the AI runtime FFI bindings to work properly
#
# Author: SynOS Build Team
# Date: October 22, 2025
# Version: 1.0.0
################################################################################

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
readonly CHROOT_DIR="${1:-}"
readonly LOG_FILE="${2:-/tmp/ai-runtime-install.log}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} ✓ $1" | tee -a "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} ⚠ $1" | tee -a "$LOG_FILE"; }
log_error() { echo -e "${RED}[ERROR]${NC} ✗ $1" | tee -a "$LOG_FILE"; }

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    SynOS AI Runtime Library Installer                     ║"
    echo "║                                                                            ║"
    echo "║  Installing TensorFlow Lite, ONNX Runtime, and PyTorch libraries          ║"
    echo "║  for production-grade AI inference capabilities                            ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_chroot() {
    if [[ -z "$CHROOT_DIR" ]]; then
        log_error "Usage: $0 <chroot_directory> [log_file]"
        log_error "Example: $0 /tmp/synos-build/chroot"
        exit 1
    fi

    if [[ ! -d "$CHROOT_DIR" ]]; then
        log_error "Chroot directory does not exist: $CHROOT_DIR"
        exit 1
    fi

    log_success "Chroot directory verified: $CHROOT_DIR"
}

install_tensorflow_lite() {
    log_info "Installing TensorFlow Lite C library..."

    # Method 1: Try package manager first
    if chroot "$CHROOT_DIR" bash -c "apt update && apt install -y libtensorflowlite-dev" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "TensorFlow Lite installed via package manager"
        return 0
    fi

    log_warning "Package manager installation failed, trying manual installation..."

    # Method 2: Download pre-built binaries
    local tflite_version="2.14.0"
    local tflite_url="https://storage.googleapis.com/tensorflow/libtensorflow/libtensorflow-cpu-linux-x86_64-2.14.0.tar.gz"

    log_info "Downloading TensorFlow Lite ${tflite_version}..."

    if chroot "$CHROOT_DIR" bash -c "
        cd /tmp &&
        wget -q '$tflite_url' -O tflite.tar.gz &&
        tar -xzf tflite.tar.gz &&
        cp lib/libtensorflow.so.2 /usr/local/lib/libtensorflowlite_c.so &&
        cp -r include/tensorflow /usr/local/include/ &&
        ldconfig &&
        rm -rf tflite.tar.gz lib include
    " 2>&1 | tee -a "$LOG_FILE"; then
        log_success "TensorFlow Lite installed manually"
        return 0
    fi

    log_error "TensorFlow Lite installation failed"
    return 1
}

install_onnx_runtime() {
    log_info "Installing ONNX Runtime..."

    # Download pre-built binaries
    local onnx_version="1.16.0"
    local onnx_url="https://github.com/microsoft/onnxruntime/releases/download/v${onnx_version}/onnxruntime-linux-x64-${onnx_version}.tgz"

    log_info "Downloading ONNX Runtime ${onnx_version}..."

    if chroot "$CHROOT_DIR" bash -c "
        cd /tmp &&
        wget -q '$onnx_url' -O onnxruntime.tgz &&
        tar -xzf onnxruntime.tgz &&
        cd onnxruntime-linux-x64-${onnx_version} &&
        cp lib/libonnxruntime.so* /usr/local/lib/ &&
        cp -r include/* /usr/local/include/ &&
        ldconfig &&
        cd / && rm -rf /tmp/onnxruntime*
    " 2>&1 | tee -a "$LOG_FILE"; then
        log_success "ONNX Runtime installed"
        return 0
    fi

    log_error "ONNX Runtime installation failed"
    return 1
}

install_pytorch() {
    log_info "Installing PyTorch LibTorch..."

    # Download LibTorch
    local torch_version="2.1.0"
    local torch_url="https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-${torch_version}%2Bcpu.zip"

    log_info "Downloading LibTorch ${torch_version}..."

    if chroot "$CHROOT_DIR" bash -c "
        apt install -y unzip &&
        cd /tmp &&
        wget -q '$torch_url' -O libtorch.zip &&
        unzip -q libtorch.zip &&
        cp -r libtorch/lib/* /usr/local/lib/ &&
        cp -r libtorch/include/* /usr/local/include/ &&
        ldconfig &&
        rm -rf libtorch.zip libtorch
    " 2>&1 | tee -a "$LOG_FILE"; then
        log_success "PyTorch LibTorch installed"
        return 0
    fi

    log_error "PyTorch LibTorch installation failed"
    return 1
}

verify_installations() {
    log_info "Verifying AI runtime library installations..."

    local verification_failed=false

    # Check TensorFlow Lite
    if chroot "$CHROOT_DIR" bash -c "ldconfig -p | grep -q tensorflowlite_c"; then
        log_success "TensorFlow Lite library verified"
    else
        log_error "TensorFlow Lite library not found"
        verification_failed=true
    fi

    # Check ONNX Runtime
    if chroot "$CHROOT_DIR" bash -c "ldconfig -p | grep -q onnxruntime"; then
        log_success "ONNX Runtime library verified"
    else
        log_error "ONNX Runtime library not found"
        verification_failed=true
    fi

    # Check PyTorch
    if chroot "$CHROOT_DIR" bash -c "ldconfig -p | grep -q torch"; then
        log_success "PyTorch LibTorch library verified"
    else
        log_error "PyTorch LibTorch library not found"
        verification_failed=true
    fi

    if [[ "$verification_failed" == "true" ]]; then
        log_error "Some AI runtime libraries failed verification"
        return 1
    fi

    log_success "All AI runtime libraries verified successfully"
    return 0
}

create_ai_runtime_config() {
    log_info "Creating AI runtime configuration..."

    # Create configuration file for AI runtime
    cat > "$CHROOT_DIR/etc/synos/ai-runtime.conf" << 'EOF'
# SynOS AI Runtime Configuration
# Generated automatically during ISO build

[tensorflow_lite]
enabled = true
library_path = /usr/local/lib/libtensorflowlite_c.so
gpu_acceleration = auto
num_threads = auto

[onnx_runtime]
enabled = true
library_path = /usr/local/lib/libonnxruntime.so
execution_providers = CPU,CUDA
optimization_level = all

[pytorch]
enabled = true
library_path = /usr/local/lib/libtorch.so
device = auto
num_threads = auto

[general]
model_cache_dir = /var/cache/synos/ai-models
max_cache_size_mb = 1024
enable_model_encryption = true
log_level = info
EOF

    # Create cache directory
    mkdir -p "$CHROOT_DIR/var/cache/synos/ai-models"
    chmod 755 "$CHROOT_DIR/var/cache/synos/ai-models"

    log_success "AI runtime configuration created"
}

main() {
    print_banner
    check_chroot

    # Create necessary directories
    mkdir -p "$CHROOT_DIR/etc/synos"
    mkdir -p "$CHROOT_DIR/usr/local/lib"
    mkdir -p "$CHROOT_DIR/usr/local/include"

    # Install libraries
    local install_failed=false

    if ! install_tensorflow_lite; then
        log_warning "TensorFlow Lite installation failed - AI runtime will use fallback"
        install_failed=true
    fi

    if ! install_onnx_runtime; then
        log_warning "ONNX Runtime installation failed - AI runtime will use fallback"
        install_failed=true
    fi

    if ! install_pytorch; then
        log_warning "PyTorch installation failed - AI runtime will use fallback"
        install_failed=true
    fi

    # Create configuration
    create_ai_runtime_config

    # Verify installations
    if ! verify_installations && [[ "$install_failed" == "true" ]]; then
        log_warning "Some AI libraries failed to install - system will work with reduced AI capabilities"
        log_info "The AI runtime FFI bindings will gracefully degrade to simulation mode"
    fi

    log_success "AI runtime library installation complete"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "  1. Build SynOS with AI runtime features enabled"
    echo "  2. Test AI inference capabilities"
    echo "  3. Verify model loading and execution"
    echo ""
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
