#!/bin/bash
# SynOS Development Environment Health Check
# Run this daily to monitor system resources and environment health

set -euo pipefail

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  SynOS Dev Environment Health Check${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Timestamp: $(date)"
echo -e "Host: $(hostname)"
echo ""

# Memory Check
echo -e "${GREEN}📊 Memory Status${NC}"
TOTAL_MEM=$(free -h | grep Mem | awk '{print $2}')
USED_MEM=$(free -h | grep Mem | awk '{print $3}')
FREE_MEM=$(free -h | grep Mem | awk '{print $4}')
MEM_PERCENT=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
echo "  Total: $TOTAL_MEM | Used: $USED_MEM | Free: $FREE_MEM | Usage: ${MEM_PERCENT}%"

if [ "$MEM_PERCENT" -gt 85 ]; then
    echo -e "  ${RED}⚠ HIGH MEMORY USAGE${NC}"
fi
echo ""

# Disk Space Check
echo -e "${GREEN}💾 Disk Space${NC}"
df -h /home | tail -1 | awk '{printf "  /home: %s used of %s (%s)\n", $3, $2, $5}'
df -h /tmp | tail -1 | awk '{printf "  /tmp:  %s used of %s (%s)\n", $3, $2, $5}'
DISK_PERCENT=$(df /home | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_PERCENT" -gt 80 ]; then
    echo -e "  ${RED}⚠ LOW DISK SPACE${NC}"
fi
echo ""

# File Descriptors
echo -e "${GREEN}📁 File Descriptors${NC}"
FD_OPEN=$(lsof -u $(whoami) 2>/dev/null | wc -l)
FD_LIMIT=$(ulimit -n)
FD_PERCENT=$((FD_OPEN * 100 / FD_LIMIT))
echo "  Open: $FD_OPEN / $FD_LIMIT ($FD_PERCENT%)"
if [ "$FD_PERCENT" -gt 80 ]; then
    echo -e "  ${RED}⚠ HIGH FILE DESCRIPTOR USAGE${NC}"
fi
echo ""

# Process Count
echo -e "${GREEN}⚙️  Processes${NC}"
PROC_COUNT=$(ps -u $(whoami) --no-headers | wc -l)
PROC_LIMIT=$(ulimit -u)
echo "  User processes: $PROC_COUNT / $PROC_LIMIT"
echo ""

# VS Code Processes
echo -e "${GREEN}🖥️  VS Code Status${NC}"
VSCODE_COUNT=$(ps aux | grep -E '[c]ode|[e]lectron' | wc -l)
echo "  VS Code processes: $VSCODE_COUNT"
if [ "$VSCODE_COUNT" -gt 30 ]; then
    echo -e "  ${YELLOW}⚠ Many VS Code processes (consider restart)${NC}"
fi
echo ""

# Rust-Analyzer
echo -e "${GREEN}🦀 Rust Analyzer${NC}"
if pgrep -f rust-analyzer > /dev/null; then
    RA_MEM=$(ps aux | grep '[r]ust-analyzer' | awk '{sum+=$6} END {printf "%.1f", sum/1024}')
    RA_CPU=$(ps aux | grep '[r]ust-analyzer' | awk '{sum+=$3} END {printf "%.1f", sum}')
    echo "  Status: Running"
    echo "  Memory: ${RA_MEM}MB | CPU: ${RA_CPU}%"

    # Check if memory is excessive
    if (( $(echo "$RA_MEM > 3500" | bc -l) )); then
        echo -e "  ${YELLOW}⚠ High memory usage - consider restart${NC}"
        echo -e "  ${BLUE}  Run: pkill rust-analyzer${NC}"
    fi
else
    echo "  Status: Not running"
fi
echo ""

# Build Cache Size
echo -e "${GREEN}🗄️  Build Cache${NC}"
if [ -d "target" ]; then
    TARGET_SIZE=$(du -sh target 2>/dev/null | cut -f1)
    echo "  target/ size: $TARGET_SIZE"
    echo -e "  ${BLUE}  Run 'cargo clean' to free space${NC}"
else
    echo "  target/ not found"
fi
echo ""

# Terminal PTYs
echo -e "${GREEN}🖥️  Terminal PTYs${NC}"
PTY_COUNT=$(ls /dev/pts/ 2>/dev/null | wc -l)
echo "  Active PTYs: $PTY_COUNT"
echo ""

# Device Health
echo -e "${GREEN}🔧 Critical Devices${NC}"
ls -la /dev/null /dev/ptmx 2>&1 | awk '{if(NR>1) printf "  %s %s %s\n", $1, $5$6, $NF}'

# Check if devices are correct
if [ -c /dev/null ] && [ -c /dev/ptmx ]; then
    echo -e "  ${GREEN}✓ Devices OK${NC}"
else
    echo -e "  ${RED}✗ Device issues detected${NC}"
fi
echo ""

# Mount Points
echo -e "${GREEN}📌 Critical Mounts${NC}"
if mount | grep -q '/dev/pts'; then
    echo -e "  ${GREEN}✓ /dev/pts mounted${NC}"
else
    echo -e "  ${RED}✗ /dev/pts NOT mounted${NC}"
fi
echo ""

# Resource Limits
echo -e "${GREEN}🔒 Resource Limits${NC}"
echo "  Open files limit: $(ulimit -n)"
echo "  Process limit: $(ulimit -u)"
echo "  Stack size: $(ulimit -s) KB"
echo ""

# Git Status
echo -e "${GREEN}📦 Git Status${NC}"
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    MODIFIED=$(git status --porcelain 2>/dev/null | wc -l)
    echo "  Branch: $BRANCH"
    echo "  Modified files: $MODIFIED"
else
    echo "  Not a git repository"
fi
echo ""

# Zombie Processes
echo -e "${GREEN}👻 Zombie Processes${NC}"
ZOMBIE_COUNT=$(ps aux | awk '$8=="Z"' | wc -l)
if [ "$ZOMBIE_COUNT" -gt 0 ]; then
    echo -e "  ${YELLOW}⚠ Found $ZOMBIE_COUNT zombie processes${NC}"
    ps aux | awk '$8=="Z"' | head -5
else
    echo -e "  ${GREEN}✓ No zombie processes${NC}"
fi
echo ""

# System Load
echo -e "${GREEN}⚡ System Load${NC}"
LOAD=$(uptime | awk -F'load average:' '{print $2}')
echo "  Load average:$LOAD"
echo ""

# Summary
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Health Check Summary${NC}"
echo -e "${BLUE}=========================================${NC}"

WARNINGS=0

if [ "$MEM_PERCENT" -gt 85 ]; then
    echo -e "${YELLOW}⚠ High memory usage ($MEM_PERCENT%)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ "$DISK_PERCENT" -gt 80 ]; then
    echo -e "${YELLOW}⚠ Low disk space ($DISK_PERCENT%)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ "$FD_PERCENT" -gt 80 ]; then
    echo -e "${YELLOW}⚠ High file descriptor usage ($FD_PERCENT%)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ "$VSCODE_COUNT" -gt 30 ]; then
    echo -e "${YELLOW}⚠ Many VS Code processes ($VSCODE_COUNT)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ "$ZOMBIE_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Zombie processes found ($ZOMBIE_COUNT)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}✓ All systems healthy${NC}"
else
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
fi

echo ""
echo -e "${BLUE}Run daily: ./scripts/check-dev-health.sh${NC}"
echo -e "${BLUE}=========================================${NC}"
