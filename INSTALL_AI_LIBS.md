# Quick Start: Install AI Runtime Libraries

**For SynOS Developers** | Takes 20 minutes | Requires sudo access

---

## What This Does

Installs the AI inference libraries needed for SynOS AI features:

- ✅ **TensorFlow Lite** - Already installed
- 🔴 **ONNX Runtime v1.16.0** - Needs installation
- ⚠️ **PyTorch LibTorch** - Needs upgrade (v1.13 → v2.1)

---

## Quick Install (Recommended)

### Option 1: Interactive Script (Easiest)

```bash
# Run the installer
./scripts/install-ai-libraries.sh

# It will download and install everything
# Just answer 'y' when prompted
```

### Option 2: Manual Install (More Control)

#### Step 1: Install ONNX Runtime (Required - 5 minutes)

```bash
# Download
cd /tmp
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.0/onnxruntime-linux-x64-1.16.0.tgz
tar -xzf onnxruntime-linux-x64-1.16.0.tgz
cd onnxruntime-linux-x64-1.16.0

# Install
sudo cp lib/libonnxruntime.so* /usr/local/lib/
sudo mkdir -p /usr/local/include/onnxruntime
sudo cp -r include/* /usr/local/include/onnxruntime/
sudo ldconfig
```

#### Step 2: Upgrade PyTorch (Optional - 15 minutes)

```bash
# Download PyTorch 2.1.0
cd /tmp
wget https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip
unzip libtorch-cxx11-abi-shared-with-deps-2.1.0+cpu.zip

# Install
sudo cp -r libtorch/lib/* /usr/local/lib/
sudo cp -r libtorch/include/* /usr/local/include/
sudo ldconfig
```

---

## Verify Installation

```bash
# Check what's installed
ldconfig -p | grep -E "(onnxruntime|torch|tensorflow)"

# Test build
cd /home/diablorain/Syn_OS
cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch"

# Should see: "Finished dev [unoptimized + debuginfo]" ✅
```

---

## Troubleshooting

### "library not found" error

```bash
# Update library cache
sudo ldconfig

# Add to your shell profile
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Still not working?

See detailed guide: [docs/03-build/AI_RUNTIME_LIBRARIES_INSTALL.md](docs/03-build/AI_RUNTIME_LIBRARIES_INSTALL.md)

---

## What You Get

After installation, you can:

- ✅ Build SynOS with full AI features
- ✅ Run AI inference on .tflite, .onnx, and .pt models
- ✅ Use GPU acceleration (if you have NVIDIA GPU)
- ✅ Deploy AI-enhanced security tools

---

## Next Steps

1. **Install libraries** (above)
2. **Test build:** `cargo build -p synos-ai-runtime --features "tensorflow-lite onnx-runtime pytorch"`
3. **Build SynOS ISO:** `./scripts/02-build/core/build-synos-v1.0-complete.sh`
4. **Deploy:** Your AI-enhanced security OS is ready!

---

**Need help?** Check [AI_RUNTIME_STATUS.md](docs/06-project-status/AI_RUNTIME_STATUS.md) for detailed status.
