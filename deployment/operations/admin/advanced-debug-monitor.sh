#!/bin/bash

# Advanced SynOS Development Monitoring Script
# Real-time debugging and environment monitoring

SYNOS_ROOT="/home/diablorain/Syn_OS"
KERNEL_DIR="$SYNOS_ROOT/core/kernel"
BUILD_DIR="$SYNOS_ROOT/build"
LOG_DIR="$SYNOS_ROOT/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔧 SynOS Advanced Development Monitor${NC}"
echo -e "${CYAN}📅 $(date)${NC}"
echo "======================================================"

# Function to log with timestamp
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/development.log"
}

# Function to monitor QEMU output in real-time
monitor_qemu_output() {
    local iso_path="$1"
    local log_file="$LOG_DIR/qemu_output_$(date +%s).log"
    
    echo -e "${YELLOW}🖥️  Starting QEMU with comprehensive monitoring...${NC}"
    log_with_timestamp "Starting QEMU monitoring for $iso_path"
    
    # Start QEMU with extensive debugging
    timeout 60 qemu-system-x86_64 \
        -cdrom "$iso_path" \
        -m 512M \
        -serial file:"$log_file" \
        -d int,cpu_reset,guest_errors \
        -D "$LOG_DIR/qemu_debug.log" \
        -monitor stdio \
        -no-reboot \
        -no-shutdown 2>&1 | tee "$LOG_DIR/qemu_monitor.log"
    
    echo -e "${BLUE}📋 QEMU Output Analysis:${NC}"
    if [ -f "$log_file" ]; then
        echo "Serial output captured in: $log_file"
        echo "Last 20 lines of serial output:"
        tail -20 "$log_file"
    fi
    
    if [ -f "$LOG_DIR/qemu_debug.log" ]; then
        echo -e "${RED}🐛 Debug output captured in: $LOG_DIR/qemu_debug.log${NC}"
        echo "Checking for CPU resets or interrupts:"
        grep -i "reset\|interrupt\|exception" "$LOG_DIR/qemu_debug.log" | tail -10
    fi
}

# Function to analyze kernel for potential issues
analyze_kernel() {
    echo -e "${YELLOW}🔍 Analyzing kernel for potential issues...${NC}"
    
    # Check for infinite loops in source
    echo "Checking for potential infinite loops:"
    grep -n "while.*1\|for.*;;.*" "$KERNEL_DIR/src/"*.c | head -5
    
    # Check for missing bounds checking
    echo "Checking for array access without bounds checking:"
    grep -n "\[.*\].*=" "$KERNEL_DIR/src/"*.c | grep -v "if.*<\|if.*>" | head -5
    
    # Check interrupt handlers
    echo "Analyzing interrupt handlers:"
    grep -n "interrupt.*handler\|IRQ" "$KERNEL_DIR/src/"*.c
    
    # Check for recursive calls
    echo "Checking for potential recursion issues:"
    grep -n "console_process.*console_process\|keyboard.*keyboard" "$KERNEL_DIR/src/"*.c
}

# Function to build with extensive debugging
build_with_debugging() {
    echo -e "${YELLOW}🔨 Building kernel with debugging symbols...${NC}"
    cd "$KERNEL_DIR"
    
    # Add debugging flags to Makefile
    make clean
    CFLAGS="-g -DDEBUG -O0" make 2>&1 | tee "$LOG_DIR/build.log"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Build successful with debugging${NC}"
        
        # Analyze symbols
        echo "Symbol analysis:"
        nm kernel.bin | grep -E "console|keyboard|interrupt" | head -10
        
        # Check binary size
        echo "Binary size analysis:"
        ls -lh kernel.bin
        
        return 0
    else
        echo -e "${RED}❌ Build failed${NC}"
        return 1
    fi
}

# Function to create debugging ISO
create_debug_iso() {
    echo -e "${YELLOW}📀 Creating debugging ISO...${NC}"
    cd "$SYNOS_ROOT"
    
    cp core/kernel/kernel.bin build/kernel.bin
    ./scripts/build-grub-iso.sh 2>&1 | tee "$LOG_DIR/iso_build.log"
    
    if [ -f "build/SynOS-v1.0-grub-20250902.iso" ]; then
        echo -e "${GREEN}✅ Debug ISO created successfully${NC}"
        echo "ISO size: $(du -h build/SynOS-v1.0-grub-20250902.iso)"
        return 0
    else
        echo -e "${RED}❌ ISO creation failed${NC}"
        return 1
    fi
}

# Main execution
echo -e "${BLUE}🔍 Step 1: Kernel Analysis${NC}"
analyze_kernel

echo -e "\n${BLUE}🔨 Step 2: Debug Build${NC}"
if build_with_debugging; then
    echo -e "\n${BLUE}📀 Step 3: Create Debug ISO${NC}"
    if create_debug_iso; then
        echo -e "\n${BLUE}🖥️  Step 4: Monitor QEMU Execution${NC}"
        monitor_qemu_output "build/SynOS-v1.0-grub-20250902.iso"
    fi
fi

echo -e "\n${PURPLE}📋 Development Session Summary${NC}"
echo "======================================================"
echo "Logs available in: $LOG_DIR"
echo "- development.log: General development log"
echo "- build.log: Compilation output" 
echo "- qemu_output_*.log: Serial console output"
echo "- qemu_debug.log: QEMU debugging information"
echo "- qemu_monitor.log: QEMU monitor output"

echo -e "\n${CYAN}💡 Next Steps for ParrotOS/EndeavorOS Hybrid:${NC}"
echo "1. 🐧 Analyze ParrotOS kernel configuration"
echo "2. 🚀 Study EndeavorOS Arch-based optimizations"  
echo "3. 🔧 Integrate best security features from both"
echo "4. 🎓 Maintain educational focus with professional tools"
echo "5. 📦 Create hybrid package management system"
