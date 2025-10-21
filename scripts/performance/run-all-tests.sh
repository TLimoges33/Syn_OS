#!/bin/bash
################################################################################
# SynOS Performance Test Suite
# Comprehensive performance testing and benchmarking
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Performance Test Suite v1.1                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Run all performance tests
echo -e "${BLUE}Running all performance tests...${NC}"
echo ""

# 1. Memory Profiler
echo -e "${CYAN}[1/3] Memory Profiling...${NC}"
if [ -f "$SCRIPT_DIR/memory-profiler.sh" ]; then
    "$SCRIPT_DIR/memory-profiler.sh"
else
    echo -e "${RED}✗ Memory profiler not found${NC}"
fi

echo ""
echo -e "${YELLOW}Press Enter to continue to boot analysis...${NC}"
read

# 2. Boot Analyzer
echo -e "${CYAN}[2/3] Boot Performance Analysis...${NC}"
if [ -f "$SCRIPT_DIR/boot-analyzer.sh" ]; then
    "$SCRIPT_DIR/boot-analyzer.sh"
else
    echo -e "${RED}✗ Boot analyzer not found${NC}"
fi

echo ""
echo -e "${YELLOW}Press Enter to continue to system benchmarks...${NC}"
read

# 3. System Benchmarks
echo -e "${CYAN}[3/3] System Benchmarks...${NC}"
echo ""

# CPU Performance
echo -e "${BLUE}CPU Performance:${NC}"
echo -ne "  Running CPU benchmark... "
if command -v sysbench &>/dev/null; then
    cpu_score=$(sysbench cpu --cpu-max-prime=20000 --threads=1 run 2>/dev/null | grep "events per second" | awk '{print $4}')
    echo -e "${GREEN}${cpu_score} events/sec${NC}"
else
    echo -e "${YELLOW}sysbench not installed${NC}"
fi

# Disk I/O
echo -e "${BLUE}Disk I/O Performance:${NC}"
echo -ne "  Testing read speed... "
if command -v dd &>/dev/null; then
    read_speed=$(dd if=/dev/zero of=/tmp/test bs=1M count=100 2>&1 | grep copied | awk '{print $(NF-1), $NF}')
    echo -e "${GREEN}${read_speed}${NC}"
    rm -f /tmp/test
else
    echo -e "${YELLOW}dd not available${NC}"
fi

# Network latency (if online)
echo -e "${BLUE}Network Performance:${NC}"
echo -ne "  Testing DNS resolution... "
if command -v host &>/dev/null; then
    dns_time=$(time (host google.com > /dev/null 2>&1) 2>&1 | grep real | awk '{print $2}')
    echo -e "${GREEN}${dns_time}${NC}"
else
    echo -e "${YELLOW}host command not available${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Performance Testing Complete!                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Summary
echo -e "${BLUE}=== PERFORMANCE SUMMARY ===${NC}"
echo ""

# Memory
current_mem=$(free -h | awk '/^Mem:/ {print $3}')
mem_percent=$(free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100}')
echo -e "Memory Usage:  ${YELLOW}${current_mem} (${mem_percent}%)${NC}"

# Boot time
if command -v systemd-analyze &>/dev/null; then
    boot_time=$(systemd-analyze 2>/dev/null | grep "Startup finished" | grep -oP '\d+\.\d+s' | tail -1)
    if [ ! -z "$boot_time" ]; then
        echo -e "Boot Time:     ${YELLOW}${boot_time}${NC}"
    fi
fi

# Uptime
uptime_str=$(uptime -p)
echo -e "System Uptime: ${CYAN}${uptime_str}${NC}"

echo ""
echo -e "${BLUE}Performance Targets (v1.1):${NC}"
echo "  • Memory: <4.0 GB (15% reduction)"
echo "  • Boot Time: <30 seconds"
echo "  • CPU: Minimal idle usage (<5%)"
echo ""

echo -e "${BLUE}Reports Location:${NC}"
echo "  build/logs/performance/"
echo ""

echo -e "${CYAN}To optimize performance:${NC}"
echo "  • Memory: ./scripts/performance/optimize-memory.sh"
echo "  • Boot:   ./scripts/performance/optimize-boot.sh"
echo ""
