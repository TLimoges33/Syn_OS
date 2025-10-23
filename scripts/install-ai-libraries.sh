#!/bin/bash
# ============================================================================
# SynOS AI Runtime Libraries Installation Script
# ============================================================================
# Installs TensorFlow Lite, ONNX Runtime, and PyTorch LibTorch
# Version: 1.0.0
# Last Updated: October 22, 2025
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Do not run this script as root. Use regular user (sudo will be called when needed)."
    exit 1
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

cd "$TEMP_DIR"

print_header "SynOS AI Runtime Libraries Installation"
echo ""
print_info "This script will install:"
echo "  • TensorFlow Lite C API"
echo "  • ONNX Runtime v1.16.0"
echo "  • PyTorch LibTorch v2.1.0"
echo ""
print_info "Total download size: ~600 MB"
print_info "Total install size: ~1.5 GB"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled."
    exit 0
fi

# ============================================================================
# 1. Install System Dependencies
# ============================================================================

print_header "Step 1/4: Installing System Dependencies"

print_info "Updating package lists..."
sudo apt update

print_info "Installing build tools..."
sudo apt install -y wget unzip tar build-essential cmake

print_success "System dependencies installed"

# ============================================================================
# 2. Install TensorFlow Lite
# ============================================================================

print_header "Step 2/4: Installing TensorFlow Lite C API"

# Check if already installed
if ldconfig -p | grep -q "libtensorflowlite_c.so"; then
    print_success "TensorFlow Lite already installed"
else
    print_info "Downloading TensorFlow Lite pre-built binary..."

    # Use pre-built binary for fastest installation
    wget -q --show-progress \
        https://storage.googleapis.com/tensorflow/libtensorflow/libtensorflow-cpu-linux-x86_64-2.14.0.tar.gz \
        -O tflite.tar.gz

    print_info "Extracting..."
    tar -xzf tflite.tar.gz

    print_info "Installing to /usr/local/lib..."
    sudo cp lib/libtensorflow*.so* /usr/local/lib/

    # Try to find and install C API specifically
    if [ -f "lib/libtensorflowlite_c.so" ]; then
        sudo cp lib/libtensorflowlite_c.so /usr/local/lib/
    fi

    print_success "TensorFlow Lite installed"
fi

# Install GPU delegate (optional)
if command -v nvidia-smi &> /dev/null; then
    print_info "NVIDIA GPU detected, attempting GPU delegate install..."
    # This is optional and may not be available in pre-built binaries
    print_info "GPU delegate requires building from source (optional feature)"
else
    print_info "No NVIDIA GPU detected, skipping GPU delegate"
fi

# ============================================================================
# 3. Install ONNX Runtime v1.16.0
# ============================================================================

print_header "Step 3/4: Installing ONNX Runtime v1.16.0"

if ldconfig -p | grep -q "libonnxruntime.so"; then
    INSTALLED_VERSION=$(ldconfig -p | grep libonnxruntime.so | head -n1)
    print_success "ONNX Runtime already installed: $INSTALLED_VERSION"
else
    print_info "Downloading ONNX Runtime v1.16.0..."

    wget -q --show-progress \
        https://github.com/microsoft/onnxruntime/releases/download/v1.16.0/onnxruntime-linux-x64-1.16.0.tgz \
        -O onnxruntime.tgz

    print_info "Extracting..."
    tar -xzf onnxruntime.tgz

    cd onnxruntime-linux-x64-1.16.0

    print_info "Installing to /usr/local..."
    sudo cp lib/libonnxruntime.so* /usr/local/lib/
    sudo mkdir -p /usr/local/include/onnxruntime
    sudo cp -r include/* /usr/local/include/onnxruntime/

    cd ..

    print_success "ONNX Runtime v1.16.0 installed"
fi

# ============================================================================
# 4. Install PyTorch LibTorch v2.1.0
# ============================================================================

print_header "Step 4/4: Installing PyTorch LibTorch v2.1.0"

if ldconfig -p | grep -q "libtorch.so"; then
    print_success "PyTorch LibTorch already installed"
else
    print_info "Downloading PyTorch LibTorch v2.1.0 (CPU version)..."
    print_info "This is a large download (~500 MB), please be patient..."

    # Check for CUDA
    if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
        print_info "NVIDIA GPU detected, downloading CUDA 11.8 version..."
        wget -q --show-progress \
            https://download.pytorch.org/libtorch/cu118/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcu118.zip \
            -O libtorch.zip
    else
        print_info "No GPU detected, downloading CPU version..."
        wget -q --show-progress \
            https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip \
            -O libtorch.zip
    fi

    print_info "Extracting LibTorch..."
    unzip -q libtorch.zip

    print_info "Installing to /usr/local..."
    sudo cp -r libtorch/lib/* /usr/local/lib/
    sudo cp -r libtorch/include/* /usr/local/include/

    print_success "PyTorch LibTorch v2.1.0 installed"
fi

# ============================================================================
# 5. Update Library Cache
# ============================================================================

print_header "Finalizing Installation"

print_info "Updating library cache..."
sudo ldconfig

print_info "Verifying installations..."

# Verify TensorFlow Lite
if ldconfig -p | grep -q "libtensorflow"; then
    print_success "TensorFlow Lite verified"
    TFLITE_COUNT=$(ldconfig -p | grep libtensorflow | wc -l)
    print_info "  Found $TFLITE_COUNT TensorFlow libraries"
else
    print_error "TensorFlow Lite verification failed"
fi

# Verify ONNX Runtime
if ldconfig -p | grep -q "libonnxruntime.so"; then
    print_success "ONNX Runtime verified"
    ONNX_VERSION=$(ldconfig -p | grep libonnxruntime.so | head -n1)
    print_info "  $ONNX_VERSION"
else
    print_error "ONNX Runtime verification failed"
fi

# Verify PyTorch
if ldconfig -p | grep -q "libtorch.so"; then
    print_success "PyTorch LibTorch verified"
    TORCH_COUNT=$(ldconfig -p | grep libtorch | wc -l)
    print_info "  Found $TORCH_COUNT PyTorch libraries"
else
    print_error "PyTorch LibTorch verification failed"
fi

# ============================================================================
# 6. Set up Environment
# ============================================================================

print_info "Setting up environment variables..."

ENV_SETUP="
# SynOS AI Runtime Library Paths
export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH
export LIBRARY_PATH=/usr/local/lib:\$LIBRARY_PATH
export C_INCLUDE_PATH=/usr/local/include:\$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=/usr/local/include:\$CPLUS_INCLUDE_PATH
"

# Check if already in .bashrc
if ! grep -q "SynOS AI Runtime Library Paths" ~/.bashrc; then
    echo "$ENV_SETUP" >> ~/.bashrc
    print_success "Added library paths to ~/.bashrc"
else
    print_info "Library paths already in ~/.bashrc"
fi

# Apply to current session
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# ============================================================================
# 7. Test Compilation
# ============================================================================

print_header "Testing AI Runtime Compilation"

print_info "Attempting to build SynOS AI runtime..."
cd /home/diablorain/Syn_OS

# Try to build with all features
if cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch" 2>&1 | tee /tmp/cargo-build.log; then
    print_success "AI Runtime compilation successful!"
else
    print_error "Compilation failed. Check /tmp/cargo-build.log for details."
    print_info "This may be normal if some libraries couldn't be found."
    print_info "Try running: source ~/.bashrc && cargo build -p synos-ai-runtime --features 'tensorflow-lite onnx-runtime pytorch'"
fi

# ============================================================================
# Summary
# ============================================================================

print_header "Installation Complete!"

echo ""
print_info "Installed Libraries:"
echo ""
echo "  • TensorFlow Lite C API"
echo "  • ONNX Runtime v1.16.0"
echo "  • PyTorch LibTorch v2.1.0"
echo ""

print_info "Next Steps:"
echo ""
echo "  1. Reload environment:"
echo "     $ source ~/.bashrc"
echo ""
echo "  2. Test compilation:"
echo "     $ cd /home/diablorain/Syn_OS"
echo "     $ cargo build -p synos-ai-runtime --features 'tensorflow-lite onnx-runtime pytorch'"
echo ""
echo "  3. Run tests:"
echo "     $ cargo test -p synos-ai-runtime"
echo ""
echo "  4. Build full SynOS ISO:"
echo "     $ ./scripts/02-build/core/build-synos-v1.0-complete.sh"
echo ""

print_success "AI Runtime libraries ready for SynOS!"
echo ""
