# AI Runtime Libraries Installation Guide

**Last Updated:** October 22, 2025
**Status:** Required for SynOS v1.0 - v2.0 AI features

---

## Overview

SynOS AI runtime requires three production AI inference libraries:

1. **TensorFlow Lite C API** (libtensorflowlite_c.so) - Lightweight inference
2. **ONNX Runtime v1.16.0** (libonnxruntime.so) - Cross-platform models
3. **PyTorch LibTorch v2.1.0** (libtorch.so) - PyTorch inference

All three are **REQUIRED** for full AI consciousness features.

---

## Quick Install (Debian/Ubuntu)

```bash
# Run this script for automated installation
sudo /home/diablorain/Syn_OS/scripts/install-ai-libraries.sh
```

---

## Manual Installation

### 1. TensorFlow Lite C API

#### Option A: Package Manager (Recommended for Debian/Ubuntu)

```bash
# Add TensorFlow repository
wget -O - https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | sudo apt-key add -
sudo add-apt-repository "deb https://apt.repos.intel.com/oneapi all main"

# Install TensorFlow Lite
sudo apt update
sudo apt install -y libtensorflowlite-dev
```

#### Option B: Build from Source

```bash
# Clone TensorFlow
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow

# Build TensorFlow Lite C library
./configure
bazel build //tensorflow/lite/c:tensorflowlite_c

# Install
sudo cp bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so /usr/local/lib/
sudo ldconfig
```

#### Option C: Pre-built Binary (Fastest)

```bash
# Download pre-built library (Linux x86_64)
wget https://storage.googleapis.com/tensorflow/libtensorflow/libtensorflow-cpu-linux-x86_64-2.14.0.tar.gz
tar -xzf libtensorflow-cpu-linux-x86_64-2.14.0.tar.gz
sudo cp lib/libtensorflowlite_c.so /usr/local/lib/
sudo ldconfig
```

#### GPU Delegate (Optional - for GPU acceleration)

```bash
# Install GPU delegate
sudo apt install -y libtensorflowlite-gpu-delegate-dev

# Or build from source
bazel build //tensorflow/lite/delegates/gpu:libtensorflowlite_gpu_delegate.so
sudo cp bazel-bin/tensorflow/lite/delegates/gpu/libtensorflowlite_gpu_delegate.so /usr/local/lib/
```

---

### 2. ONNX Runtime v1.16.0

#### Option A: Python Package (Easiest)

```bash
# Install via pip and copy library
pip install onnxruntime==1.16.0

# Find library location
ONNX_LIB=$(python3 -c 'import onnxruntime; import os; print(os.path.join(onnxruntime.__path__[0], "capi"))')

# Copy to system library path
sudo cp $ONNX_LIB/libonnxruntime.so* /usr/local/lib/
sudo ldconfig
```

#### Option B: Official Release (Recommended for Production)

```bash
# Download official release
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.0/onnxruntime-linux-x64-1.16.0.tgz

# Extract and install
tar -xzf onnxruntime-linux-x64-1.16.0.tgz
cd onnxruntime-linux-x64-1.16.0

sudo cp lib/libonnxruntime.so* /usr/local/lib/
sudo cp -r include/onnxruntime /usr/local/include/
sudo ldconfig
```

#### Option C: Build from Source

```bash
# Clone ONNX Runtime
git clone --recursive https://github.com/microsoft/onnxruntime.git
cd onnxruntime
git checkout v1.16.0

# Build
./build.sh --config Release --build_shared_lib --parallel

# Install
sudo cp build/Linux/Release/libonnxruntime.so* /usr/local/lib/
sudo ldconfig
```

---

### 3. PyTorch LibTorch v2.1.0

#### Option A: Pre-built Binary (Recommended)

```bash
# Download LibTorch (CPU version)
wget https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip

# Extract
unzip libtorch-cxx11-abi-shared-with-deps-2.1.0+cpu.zip

# Install
sudo cp -r libtorch/lib/* /usr/local/lib/
sudo cp -r libtorch/include/* /usr/local/include/
sudo ldconfig
```

#### Option B: CUDA Version (for GPU support)

```bash
# Download LibTorch (CUDA 11.8)
wget https://download.pytorch.org/libtorch/cu118/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcu118.zip

# Extract and install
unzip libtorch-cxx11-abi-shared-with-deps-2.1.0+cu118.zip
sudo cp -r libtorch/lib/* /usr/local/lib/
sudo cp -r libtorch/include/* /usr/local/include/
sudo ldconfig
```

#### Option C: Build from Source

```bash
# Clone PyTorch
git clone --recursive https://github.com/pytorch/pytorch.git
cd pytorch
git checkout v2.1.0

# Build
python setup.py install

# Export C++ library
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON ..
make -j$(nproc)

# Install
sudo make install
sudo ldconfig
```

---

## Verification

### Check Installed Libraries

```bash
# TensorFlow Lite
ldconfig -p | grep tensorflowlite_c

# ONNX Runtime
ldconfig -p | grep onnxruntime

# PyTorch
ldconfig -p | grep torch
```

### Test Compilation

```bash
cd /home/diablorain/Syn_OS

# Build AI runtime with all features
cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch"

# Should compile without errors if libraries are installed correctly
```

---

## Troubleshooting

### Library Not Found

If you see "library not found" errors:

```bash
# Update library cache
sudo ldconfig

# Check LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH

# Add to library path if needed
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Make permanent (add to ~/.bashrc)
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
```

### Cargo Build Errors

If cargo build fails:

```bash
# Check which library is missing
cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch" 2>&1 | grep "cannot find"

# Install missing library following instructions above

# Clean and rebuild
cargo clean
cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch"
```

### Version Conflicts

```bash
# Check installed versions
ls -la /usr/local/lib/libonnxruntime.so*
ls -la /usr/local/lib/libtorch.so*
ls -la /usr/local/lib/libtensorflowlite_c.so*

# Remove old versions if needed
sudo rm /usr/local/lib/libonnxruntime.so*
sudo rm /usr/local/lib/libtorch*.so*

# Reinstall correct version
```

---

## Library Locations

SynOS build script searches these paths in order:

1. `/usr/local/lib/` - Manual installs
2. `/usr/lib/` - System packages
3. `/usr/lib/x86_64-linux-gnu/` - Debian/Ubuntu packages
4. `/opt/tensorflow/lib/` - Custom TensorFlow install
5. `/opt/onnxruntime/lib/` - Custom ONNX install
6. `/opt/libtorch/lib/` - Custom PyTorch install

---

## Performance Considerations

### CPU Optimization

All libraries support CPU optimizations:

- **AVX2**: Modern Intel/AMD processors
- **SSE4**: Older processors
- **NEON**: ARM processors

These are auto-detected and enabled.

### GPU Acceleration

For GPU support, install CUDA versions:

```bash
# NVIDIA CUDA 11.8 (recommended)
sudo apt install nvidia-cuda-toolkit-11-8

# Verify
nvidia-smi
nvcc --version
```

Then use GPU-enabled libraries (see installation options above).

---

## File Sizes (Approximate)

- **TensorFlow Lite**: ~3 MB
- **ONNX Runtime**: ~15 MB
- **PyTorch LibTorch**: ~500 MB (CPU), ~2 GB (CUDA)

**Total disk space needed**: ~1-3 GB

---

## Next Steps

After installation:

1. ✅ Verify libraries with `ldconfig -p`
2. ✅ Test build: `cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch"`
3. ✅ Run tests: `cargo test -p synos-ai-runtime`
4. ✅ Build SynOS ISO with AI features enabled

---

## References

- [TensorFlow Lite C API](https://www.tensorflow.org/lite/guide/inference)
- [ONNX Runtime Releases](https://github.com/microsoft/onnxruntime/releases)
- [PyTorch LibTorch](https://pytorch.org/cppdocs/installing.html)
- [SynOS Build System](../03-build/BUILD_GUIDE.md)

---

**Status:** Ready for automated installation script creation
