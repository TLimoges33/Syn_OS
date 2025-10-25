#!/usr/bin/env bash
################################################################################
# SynOS Final Cleanup - Remove PyTorch CUDA remnants
################################################################################

CHROOT_DIR="/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot"

echo "Removing PyTorch CUDA libraries..."
echo "Before: $(du -sh $CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch | cut -f1)"

# Remove CUDA-specific PyTorch libraries
rm -f "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch/lib/libtorch_cuda.so" 2>/dev/null
rm -f "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch/lib/libtorch_cuda_linalg.so" 2>/dev/null
rm -f "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch/lib/libtorch_cuda_cpp.so" 2>/dev/null
rm -rf "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch/lib/libnvrtc"* 2>/dev/null
rm -rf "$CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch/lib/libcudart"* 2>/dev/null

echo "After: $(du -sh $CHROOT_DIR/usr/local/lib/python3.11/dist-packages/torch | cut -f1)"
echo "Chroot size: $(du -sh $CHROOT_DIR | cut -f1)"
