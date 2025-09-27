#!/bin/bash

# SynOS eBPF Real-Time System Monitor
# Live display of eBPF system status and performance

export PATH=/usr/sbin:$PATH

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}🚀 SYNOS EBPF REAL-TIME SYSTEM MONITOR${NC}"
echo -e "${BLUE}=====================================Β${NC}"
echo ""

# Monitor loop
ITERATION=0
while true; do
    ITERATION=$((ITERATION + 1))
    
    # Clear screen and show header
    if [ $((ITERATION % 10)) -eq 1 ]; then
        clear
        echo -e "${BLUE}🚀 SYNOS EBPF REAL-TIME SYSTEM MONITOR${NC}"
        echo -e "${BLUE}=======================================${NC}"
        echo ""
    fi
    
    echo -e "${CYAN}📊 Monitoring Iteration: $ITERATION${NC} | $(date)"
    echo "----------------------------------------"
    
    # Check eBPF programs
    NETWORK_STATUS=$(sudo bpftool prog show | grep synos_network_monitor >/dev/null 2>&1 && echo -e "${GREEN}✅ ACTIVE${NC}" || echo -e "${RED}❌ DOWN${NC}")
    PROCESS_STATUS=$(sudo bpftool prog show | grep trace_process_basic >/dev/null 2>&1 && echo -e "${GREEN}✅ ACTIVE${NC}" || echo -e "${RED}❌ DOWN${NC}")
    MEMORY_STATUS=$(sudo bpftool prog show | grep trace_memory_basic >/dev/null 2>&1 && echo -e "${GREEN}✅ ACTIVE${NC}" || echo -e "${RED}❌ DOWN${NC}")
    
    echo -e "Network Monitor: $NETWORK_STATUS"
    echo -e "Process Monitor: $PROCESS_STATUS"
    echo -e "Memory Monitor:  $MEMORY_STATUS"
    
    # Check maps
    RINGBUF_STATUS=$(sudo bpftool map show | grep consciousness_e >/dev/null 2>&1 && echo -e "${GREEN}✅ ACTIVE${NC}" || echo -e "${RED}❌ DOWN${NC}")
    echo -e "Ring Buffer:     $RINGBUF_STATUS"
    
    # Performance metrics
    if sudo bpftool prog show id 28 >/dev/null 2>&1; then
        NETWORK_SIZE=$(sudo bpftool prog show id 28 | grep -o "xlated [0-9]*B" | grep -o "[0-9]*")
        NETWORK_JIT=$(sudo bpftool prog show id 28 | grep -o "jited [0-9]*B" | grep -o "[0-9]*")
        echo -e "${PURPLE}Network Program: ${NETWORK_SIZE}B xlated, ${NETWORK_JIT}B jited${NC}"
    fi
    
    # System resources
    MEMORY_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | tr -d ' ')
    echo -e "${YELLOW}System: CPU ${CPU_USAGE}%, Memory ${MEMORY_USAGE}${NC}"
    
    # Generate some test activity
    if [ $((ITERATION % 5)) -eq 0 ]; then
        echo -e "${CYAN}🔄 Generating test activity...${NC}"
        timeout 0.5s ping -c 1 8.8.8.8 >/dev/null 2>&1 || true
        echo "test activity $ITERATION" > /tmp/monitor_test_$ITERATION.tmp 2>/dev/null
        rm /tmp/monitor_test_$ITERATION.tmp 2>/dev/null || true
    fi
    
    echo ""
    echo -e "${BLUE}Press Ctrl+C to exit monitoring${NC}"
    echo ""
    
    sleep 2
done
