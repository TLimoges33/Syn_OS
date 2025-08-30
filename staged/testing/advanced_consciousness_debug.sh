#!/bin/bash

# Advanced Consciousness Kernel Debug Script
# Phase 4.1 Innovation: Real-time boot diagnostics

echo "🧠 Advanced Consciousness Kernel Diagnostics"
echo "============================================="

KERNEL_PATH="/home/diablorain/Syn_OS/target/x86_64-unknown-none/release/bootimage-kernel.bin"
LOG_DIR="/home/diablorain/Syn_OS/testing/debug-logs"

mkdir -p "$LOG_DIR"

echo "📋 Starting comprehensive kernel diagnostics..."

# Test 1: Memory dump analysis
echo "🔍 Test 1: Memory state analysis"
timeout 5s qemu-system-x86_64 \
    -drive format=raw,file="$KERNEL_PATH" \
    -monitor stdio \
    -nographic \
    -no-reboot \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
    << EOF > "$LOG_DIR/memory_analysis.log" 2>&1
info registers
info memory
info tlb
info mem
x/32i 0xffffffff80000000
x/32i 0x100000
x/16x 0xb8000
quit
EOF

echo "📄 Memory analysis saved to: $LOG_DIR/memory_analysis.log"

# Test 2: CPU state monitoring
echo "🖥️  Test 2: CPU state monitoring"
timeout 5s qemu-system-x86_64 \
    -drive format=raw,file="$KERNEL_PATH" \
    -monitor stdio \
    -nographic \
    -no-reboot \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
    << EOF > "$LOG_DIR/cpu_state.log" 2>&1
info cpus
info registers
info pic
info irq
quit
EOF

echo "📄 CPU state saved to: $LOG_DIR/cpu_state.log"

# Test 3: Boot sequence analysis with GDB-style debugging
echo "🔧 Test 3: Boot sequence analysis"
timeout 10s qemu-system-x86_64 \
    -drive format=raw,file="$KERNEL_PATH" \
    -s \
    -S \
    -nographic \
    -no-reboot \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04 &

QEMU_PID=$!

# Give QEMU time to start
sleep 2

# Connect with GDB for analysis
timeout 8s gdb -batch \
    -ex "target remote localhost:1234" \
    -ex "info registers" \
    -ex "x/10i \$pc" \
    -ex "x/32x 0x7c00" \
    -ex "x/32x 0x100000" \
    -ex "continue" \
    -ex "quit" \
    > "$LOG_DIR/gdb_analysis.log" 2>&1

# Kill QEMU if still running
kill $QEMU_PID 2>/dev/null

echo "📄 GDB analysis saved to: $LOG_DIR/gdb_analysis.log"

# Test 4: Simple execution test with detailed logging
echo "🚀 Test 4: Execution test with logging"
timeout 5s qemu-system-x86_64 \
    -drive format=raw,file="$KERNEL_PATH" \
    -serial file:"$LOG_DIR/serial_output.log" \
    -nographic \
    -no-reboot \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
    -d cpu,exec,int,mmu \
    -D "$LOG_DIR/qemu_execution.log"

echo "📄 Serial output saved to: $LOG_DIR/serial_output.log"
echo "📄 QEMU execution log saved to: $LOG_DIR/qemu_execution.log"

# Analysis summary
echo ""
echo "📊 Diagnostic Analysis Summary"
echo "=============================="

echo "📁 Log files created:"
ls -la "$LOG_DIR"

echo ""
echo "🔍 Quick analysis:"

# Check if we have any serial output
if [ -s "$LOG_DIR/serial_output.log" ]; then
    echo "✅ Serial output detected:"
    head -n 5 "$LOG_DIR/serial_output.log"
else
    echo "❌ No serial output detected"
fi

# Check CPU state
if grep -q "EAX" "$LOG_DIR/cpu_state.log" 2>/dev/null; then
    echo "✅ CPU state captured"
else
    echo "❌ CPU state not captured"
fi

# Check for execution traces
if [ -s "$LOG_DIR/qemu_execution.log" ]; then
    echo "✅ Execution traces available"
    echo "📈 Execution log size: $(wc -l < "$LOG_DIR/qemu_execution.log") lines"
else
    echo "❌ No execution traces"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Review logs in $LOG_DIR"
echo "2. Analyze memory layout issues"
echo "3. Check bootloader handoff problems"
echo "4. Investigate consciousness initialization failures"
