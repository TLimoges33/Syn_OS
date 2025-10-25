#!/bin/bash
#
# TensorFlow Lite C Library Installation Script
#
# Week 1 Day 2-3: Zero-Stubs Roadmap
# Date: October 22, 2025
#
# STATUS: Library successfully built! Ready to install.
#
# BUILD COMPLETED: ✅
# - Library location: /tmp/tensorflow/bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so
# - Library size: 4.2 MB
# - Build time: ~20 minutes
# - Exit code: 0 (SUCCESS)
#
# NEXT STEP: Run this script with sudo to install the library system-wide
#

set -e  # Exit on error

echo "========================================="
echo "TensorFlow Lite C Library Installation"
echo "========================================="
echo ""
echo "This script will:"
echo "  1. Copy libtensorflowlite_c.so to /usr/local/lib/"
echo "  2. Copy TFLite C API headers to /usr/local/include/"
echo "  3. Update library cache with ldconfig"
echo ""

# Check if library exists
if [ ! -f "/tmp/tensorflow/bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so" ]; then
    echo "ERROR: TensorFlow Lite library not found!"
    echo "Expected location: /tmp/tensorflow/bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so"
    exit 1
fi

echo "Step 1: Copying library to /usr/local/lib..."
sudo cp /tmp/tensorflow/bazel-bin/tensorflow/lite/c/libtensorflowlite_c.so /usr/local/lib/
echo "✅ Library copied"
echo ""

echo "Step 2: Creating header directory..."
sudo mkdir -p /usr/local/include/tensorflow/lite/c
echo "✅ Directory created"
echo ""

echo "Step 3: Copying header files..."
sudo cp /tmp/tensorflow/tensorflow/lite/c/*.h /usr/local/include/tensorflow/lite/c/
echo "✅ Headers copied"
echo ""

echo "Step 4: Updating library cache..."
sudo ldconfig
echo "✅ Library cache updated"
echo ""

echo "========================================="
echo "VERIFICATION"
echo "========================================="
echo ""

# Verify library is in cache
echo "Checking library cache:"
ldconfig -p | grep tensorflowlite || echo "WARNING: Library not found in cache!"
echo ""

# Check library size
echo "Library details:"
ls -lh /usr/local/lib/libtensorflowlite_c.so
echo ""

# Check headers
echo "Header files installed:"
ls -1 /usr/local/include/tensorflow/lite/c/
echo ""

# Check symbols
echo "Verifying C API symbols:"
nm -D /usr/local/lib/libtensorflowlite_c.so | grep TfLiteModel | head -5
echo ""

echo "========================================="
echo "INSTALLATION COMPLETE! ✅"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Test compilation:"
echo "     cd /home/diablorain/Syn_OS"
echo "     cargo build -p synos-ai-runtime --features tensorflow-lite"
echo ""
echo "  2. Download test model:"
echo "     wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/mobilenet_v2_1.0_224.tflite"
echo ""
echo "  3. Run inference test:"
echo "     cargo run --example tflite_inference -- mobilenet_v2_1.0_224.tflite test_image.jpg"
echo ""
echo "Week 1 Day 2-3: COMPLETE ✅"
echo "Week 1 Day 4-7: Ready to begin testing!"
echo ""
