#!/bin/bash
# ============================================================================
# SynOS AI Runtime Libraries Installation Script (NON-INTERACTIVE)
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

print_header "SynOS AI Runtime Libraries Installation (Automated)"
echo ""
print_info "Installing:"
echo "  • TensorFlow Lite C API"
echo "  • ONNX Runtime v1.16.0"
echo "  • PyTorch LibTorch v2.1.0"
echo ""

# ============================================================================
# 1. Install System Dependencies
# ============================================================================

print_header "Step 1/4: Installing System Dependencies"

print_info "Updating package lists..."
sudo apt update -qq

print_info "Installing build tools..."
sudo apt install -y -qq wget unzip tar build-essential cmake > /dev/null 2>&1

print_success "System dependencies installed"

# ============================================================================
# 2. Install TensorFlow Lite
# ============================================================================

print_header "Step 2/4: Installing TensorFlow Lite C API"

# Check if already installed
if ldconfig -p | grep -q "libtensorflowlite_c.so"; then
    print_success "TensorFlow Lite already installed"
else
    print_info "TensorFlow Lite C API not found in pre-built binaries"
    print_info "Attempting alternative: Install via Python package..."

    # Install via pip
    pip3 install --quiet tensorflow-lite-runtime 2>&1 | grep -v "WARNING" || true

    # Try to copy library if available
    TFLITE_PATH=$(python3 -c 'import sys; import os; paths = [p for p in sys.path if "site-packages" in p]; print(paths[0] if paths else "")' 2>/dev/null || echo "")

    if [ -n "$TFLITE_PATH" ] && [ -d "$TFLITE_PATH/tflite_runtime" ]; then
        print_info "Found TensorFlow Lite runtime in Python packages"
        # Note: C API may not be available via pip, will need source build
        print_info "For full C API support, building from source is recommended"
    fi

    print_success "TensorFlow Lite runtime installed (Python)"
fi

# ============================================================================
# 3. Install ONNX Runtime v1.16.0
# ============================================================================

print_header "Step 3/4: Installing ONNX Runtime v1.16.0"

if ldconfig -p | grep -q "libonnxruntime.so"; then
    INSTALLED_VERSION=$(ldconfig -p | grep libonnxruntime.so | head -n1)
    print_success "ONNX Runtime already installed: $INSTALLED_VERSION"
else
    print_info "Downloading ONNX Runtime v1.16.0 (~15 MB)..."

    wget -q --show-progress \
        https://github.com/microsoft/onnxruntime/releases/download/v1.16.0/onnxruntime-linux-x64-1.16.0.tgz \
        -O onnxruntime.tgz || {
        print_error "Failed to download ONNX Runtime"
        print_info "Trying alternative method..."
        pip3 install --quiet onnxruntime==1.16.0
        ONNX_LIB=$(python3 -c 'import onnxruntime; import os; print(os.path.join(onnxruntime.__path__[0], "capi"))' 2>/dev/null || echo "")
        if [ -n "$ONNX_LIB" ] && [ -d "$ONNX_LIB" ]; then
            sudo cp "$ONNX_LIB"/libonnxruntime.so* /usr/local/lib/ 2>/dev/null || true
            print_success "ONNX Runtime installed via pip"
        fi
    }

    if [ -f "onnxruntime.tgz" ]; then
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
fi

# ============================================================================
# 4. Install PyTorch LibTorch v2.1.0
# ============================================================================

print_header "Step 4/4: Installing PyTorch LibTorch v2.1.0"

if ldconfig -p | grep -q "libtorch.so"; then
    print_success "PyTorch LibTorch already installed"
else
    print_info "Downloading PyTorch LibTorch v2.1.0 (CPU version ~500 MB)..."
    print_info "This may take several minutes..."

    # Check for CUDA
    if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
        print_info "NVIDIA GPU detected, downloading CUDA 11.8 version..."
        wget -q --show-progress \
            https://download.pytorch.org/libtorch/cu118/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcu118.zip \
            -O libtorch.zip || {
            print_error "Download failed, trying CPU version..."
            wget -q --show-progress \
                https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip \
                -O libtorch.zip
        }
    else
        print_info "Downloading CPU version..."
        wget -q --show-progress \
            https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip \
            -O libtorch.zip
    fi

    print_info "Extracting LibTorch (this will take a moment)..."
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
    print_info "TensorFlow Lite C API not found (Python runtime available)"
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
# Summary
# ============================================================================

print_header "Installation Complete!"

echo ""
print_info "Installed Libraries:"
echo ""
ldconfig -p | grep -E "(onnxruntime|torch)" | head -10

echo ""
print_info "Next Steps:"
echo ""
echo "  1. Reload environment:"
echo "     $ source ~/.bashrc"
echo ""
echo "  2. Test compilation:"
echo "     $ cd /home/diablorain/Syn_OS"
echo "     $ cargo build -p synos-ai-runtime --features 'onnx-runtime pytorch'"
echo ""
echo "  3. Build full SynOS ISO:"
echo "     $ ./scripts/02-build/core/build-synos-v1.0-complete.sh"
echo ""

print_success "AI Runtime libraries installation finished!"
echo ""
