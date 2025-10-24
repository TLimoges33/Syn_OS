# Installing TensorFlow Lite C Library

**Required for:** SynOS AI Runtime (v1.1+)
**Status:** MANDATORY - No stubs, real library required
**Updated:** October 22, 2025

---

## 🎯 Overview

SynOS v1.1+ requires the **real** TensorFlow Lite C API library, not stubs. This enables:
- ✅ Loading actual .tflite models
- ✅ GPU/NPU/TPU hardware acceleration
- ✅ Production-grade inference performance
- ✅ Industry-standard model compatibility

---

## 📋 Prerequisites

```bash
# Required build tools
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    wget \
    unzip
```

---

## 🚀 Installation Methods

### Option 1: Pre-Built Package (Easiest)

**Debian/Ubuntu:**
```bash
# Add TensorFlow Lite repository (if available)
# Note: Official packages may not be available for all distros
sudo apt install libtensorflowlite-dev

# Verify installation
ls -la /usr/lib/*tensorflowlite*
```

**Status:** ⚠️ Official Debian packages may not exist yet

---

### Option 2: Download Pre-Built Binary (Recommended)

```bash
# Create installation directory
sudo mkdir -p /opt/tensorflow/lib
cd /opt/tensorflow

# Download pre-built TensorFlow Lite (if available from official releases)
# Check: https://github.com/tensorflow/tensorflow/releases

# For now, need to build from source (Option 3)
```

**Status:** ⚠️ Official pre-built binaries not widely available

---

### Option 3: Build from Source (Most Reliable) ⭐

#### Step 1: Install Bazel Build System

```bash
# Install Bazel (TensorFlow's build system)
wget https://github.com/bazelbuild/bazel/releases/download/6.4.0/bazel-6.4.0-installer-linux-x86_64.sh
chmod +x bazel-6.4.0-installer-linux-x86_64.sh
./bazel-6.4.0-installer-linux-x86_64.sh --user

# Add to PATH
export PATH="$PATH:$HOME/bin"
echo 'export PATH="$PATH:$HOME/bin"' >> ~/.bashrc

# Verify
bazel --version
```

#### Step 2: Clone TensorFlow Repository

```bash
# Clone (this is large - ~2GB)
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow

# Checkout stable version (v2.14.0)
git checkout v2.14.0
```

#### Step 3: Configure Build

```bash
# Run configuration
./configure

# When prompted, answer:
# - Python: /usr/bin/python3
# - Optimization flags: -march=native -O3
# - CUDA support: N (unless you have GPU)
# - Other options: accept defaults
```

#### Step 4: Build TensorFlow Lite C Library

```bash
# Build C API library (takes 30-60 minutes)
bazel build -c opt //tensorflow/lite/c:tensorflowlite_c

# Build output location:
ls -lh bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so
```

#### Step 5: Install Library

```bash
# Copy library to system location
sudo cp bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so /usr/local/lib/

# Copy headers
sudo mkdir -p /usr/local/include/tensorflow/lite/c
sudo cp tensorflow/lite/c/*.h /usr/local/include/tensorflow/lite/c/

# Update library cache
sudo ldconfig

# Verify installation
ldconfig -p | grep tensorflowlite
```

#### Step 6: Build GPU Delegate (Optional)

```bash
# For GPU acceleration
bazel build -c opt //tensorflow/lite/delegates/gpu:libtensorflowlite_gpu_delegate.so

# Install
sudo cp bazel-bin/tensorflow/lite/delegates/gpu/libtensorflowlite_gpu_delegate.so /usr/local/lib/
sudo ldconfig
```

---

## ✅ Verification

### Test 1: Check Library Exists

```bash
# Verify library is in system path
ldconfig -p | grep tensorflowlite

# Should output:
# libtensorflowlite_c.so (libc6,x86-64) => /usr/local/lib/libtensorflowlite_c.so
```

### Test 2: Check Headers

```bash
# Verify headers exist
ls -la /usr/local/include/tensorflow/lite/c/

# Should show:
# c_api.h
# c_api_types.h
# common.h
```

### Test 3: Test with nm

```bash
# Check symbols in library
nm -D /usr/local/lib/libtensorflowlite_c.so | grep TfLiteModel

# Should show functions like:
# TfLiteModelCreate
# TfLiteModelDelete
# etc.
```

### Test 4: Compile Test Program

```c
// test_tflite.c
#include <tensorflow/lite/c/c_api.h>
#include <stdio.h>

int main() {
    TfLiteModel* model = TfLiteModelCreateFromFile("model.tflite");
    if (model) {
        printf("TensorFlow Lite C API is working!\n");
        TfLiteModelDelete(model);
        return 0;
    }
    printf("Failed to load model (expected if model.tflite doesn't exist)\n");
    return 1;
}
```

```bash
# Compile
gcc test_tflite.c -o test_tflite -ltensorflowlite_c -I/usr/local/include

# Run (will fail without model.tflite, but that's OK)
./test_tflite
```

### Test 5: Build SynOS AI Runtime

```bash
cd /home/diablorain/Syn_OS
cargo build --package ai-runtime --features tensorflow-lite

# Should compile without errors
# No more stubs!
```

---

## 🐛 Troubleshooting

### Error: "libtensorflowlite_c.so: cannot open shared object file"

**Solution:**
```bash
# Add library path to LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

# Or rebuild library cache
sudo ldconfig
```

### Error: Bazel build fails with "Out of memory"

**Solution:**
```bash
# Limit Bazel memory usage
bazel build --local_ram_resources=4096 -c opt //tensorflow/lite/c:tensorflowlite_c
```

### Error: "fatal error: tensorflow/lite/c/c_api.h: No such file or directory"

**Solution:**
```bash
# Install headers manually
sudo cp -r tensorflow/lite /usr/local/include/tensorflow/
```

---

## 📊 Performance Verification

### Benchmark TFLite vs Pure Rust

```bash
# Once installed, run benchmarks
cd /home/diablorain/Syn_OS
cargo bench --package ai-runtime --features tensorflow-lite

# Expected results:
# TFLite CPU: ~10-50ms for MobileNetV2
# TFLite GPU: ~2-10ms for MobileNetV2
# Pure Rust: ~500-2000ms (50-200x slower)
```

---

## 🎯 Next Steps

Once TensorFlow Lite C library is installed:

1. ✅ Verify with test program
2. ✅ Build SynOS AI Runtime
3. ✅ Download test models (.tflite)
4. ✅ Run inference benchmarks
5. ✅ Test GPU acceleration (if available)

**Then move to:** ONNX Runtime installation (Week 3-4)

---

## 📚 Resources

- [TensorFlow Lite Guide](https://www.tensorflow.org/lite/guide)
- [TensorFlow Lite C API](https://www.tensorflow.org/lite/api_docs/c)
- [Building TensorFlow from Source](https://www.tensorflow.org/install/source)
- [Bazel Build System](https://bazel.build)

---

**Last Updated:** October 22, 2025
**Status:** Required for v1.1 (Week 1-2)
**Estimated Time:** 1-2 hours (with pre-built) or 2-4 hours (build from source)
