#!/bin/bash
# VM Test for consciousness mode
timeout 30s qemu-system-x86_64 \
    -cdrom "build/phase4_iso/SynOS-v4.0.0-consciousness.iso" \
    -m 4G \
    -smp 4 \
    -enable-kvm \
    -nographic \
    -serial stdio \
    -netdev user,id=net0,hostfwd=tcp::8080-:8080,hostfwd=tcp::8081-:8081,hostfwd=tcp::8082-:8082 \
    -device e1000,netdev=net0 \
    > "build/phase4.2_testing/vm_boot_consciousness.log" 2>&1
