#!/bin/bash
# Enhanced QEMU debugging script with serial logging
# Captures kernel panic information and debug output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
KERNEL_DIR="$PROJECT_ROOT/src/kernel"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 SynOS Enhanced QEMU Debug Runner${NC}"
echo -e "${BLUE}======================================${NC}"

# Create logs directory
mkdir -p "$LOG_DIR"

# Generate timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SERIAL_LOG="$LOG_DIR/serial_debug_$TIMESTAMP.log"
KERNEL_LOG="$LOG_DIR/kernel_panic_$TIMESTAMP.log"

echo -e "${GREEN}📁 Log files:${NC}"
echo -e "   Serial Output: $SERIAL_LOG"
echo -e "   Kernel Panics: $KERNEL_LOG"
echo ""

# Build kernel first
echo -e "${YELLOW}🔨 Building kernel with debug logging...${NC}"
cd "$KERNEL_DIR"
if ! cargo bootimage --target ./x86_64-syn_os.json; then
    echo -e "${RED}❌ Kernel bootimage build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Kernel bootimage build successful${NC}"
echo ""

# Find the kernel bootimage (it's built at workspace root level)
cd "$PROJECT_ROOT"
KERNEL_BINARY="target/x86_64-syn_os/debug/bootimage-kernel.bin"
if [ ! -f "$KERNEL_BINARY" ]; then
    echo -e "${RED}❌ Could not find kernel bootimage at $KERNEL_BINARY${NC}"
    exit 1
fi

echo -e "${GREEN}🎯 Kernel binary: $KERNEL_BINARY${NC}"
echo ""

# Start QEMU with enhanced logging
echo -e "${YELLOW}🚀 Starting QEMU with enhanced debugging...${NC}"
echo -e "${BLUE}   - Serial output logging to: $SERIAL_LOG${NC}"
echo -e "${BLUE}   - Press Ctrl+C to stop QEMU${NC}"
echo -e "${BLUE}   - Use 'tail -f $SERIAL_LOG' in another terminal for live output${NC}"
echo ""

# Create background process to monitor for panics
monitor_panics() {
    tail -f "$SERIAL_LOG" 2>/dev/null | while read line; do
        if echo "$line" | grep -q "KERNEL PANIC\|panic\|ERROR"; then
            echo "$line" >> "$KERNEL_LOG"
            echo -e "${RED}🚨 PANIC/ERROR detected: $line${NC}" >&2
        fi
    done
}

# Start panic monitoring in background
touch "$SERIAL_LOG"
monitor_panics &
MONITOR_PID=$!

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping QEMU and cleaning up...${NC}"
    if [ ! -z "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null || true
    fi
    
    # Check if we captured any panics
    if [ -f "$KERNEL_LOG" ] && [ -s "$KERNEL_LOG" ]; then
        echo -e "${RED}🚨 Kernel panics/errors were detected!${NC}"
        echo -e "${YELLOW}📋 Panic log contents:${NC}"
        echo "----------------------------------------"
        cat "$KERNEL_LOG"
        echo "----------------------------------------"
    else
        echo -e "${GREEN}✅ No kernel panics detected${NC}"
        rm -f "$KERNEL_LOG"
    fi
    
    echo -e "${BLUE}📝 Full serial output saved to: $SERIAL_LOG${NC}"
}

trap cleanup EXIT

# Run QEMU with comprehensive options
qemu-system-x86_64 \
    -drive format=raw,file="$KERNEL_BINARY" \
    -no-reboot \
    -no-shutdown \
    -serial file:"$SERIAL_LOG" \
    -display none \
    -m 128M \
    -cpu qemu64 \
    -smp 1 \
    -monitor stdio \
    -d guest_errors,unimp \
    -D "$LOG_DIR/qemu_debug_$TIMESTAMP.log" \
    "$@"

echo -e "${GREEN}✅ QEMU session completed${NC}"
