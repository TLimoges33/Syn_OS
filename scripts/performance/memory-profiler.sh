#!/bin/bash
################################################################################
# SynOS Memory Profiler
# Analyzes system memory usage at boot and runtime
# Target: Reduce memory footprint by 15% for v1.1
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/../../build/logs/performance"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PROFILE_FILE="$OUTPUT_DIR/memory-profile-$TIMESTAMP.txt"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Memory Profiler v1.1                               ║"
echo "║   Target: 15% Reduction from v1.0 Baseline                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Start profiling
{
    echo "SynOS Memory Profile - $(date)"
    echo "========================================"
    echo ""

    # System information
    echo "=== SYSTEM INFORMATION ==="
    echo "Hostname: $(hostname)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p)"
    echo ""

    # Total memory
    echo "=== TOTAL MEMORY ==="
    total_mem=$(free -h | awk '/^Mem:/ {print $2}')
    used_mem=$(free -h | awk '/^Mem:/ {print $3}')
    free_mem=$(free -h | awk '/^Mem:/ {print $4}')
    available_mem=$(free -h | awk '/^Mem:/ {print $7}')

    echo "Total:     $total_mem"
    echo "Used:      $used_mem"
    echo "Free:      $free_mem"
    echo "Available: $available_mem"
    echo ""

    # Memory usage percentage
    mem_percent=$(free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100}')
    echo "Memory Usage: ${mem_percent}%"
    echo ""

    # Detailed memory breakdown
    echo "=== DETAILED MEMORY (MB) ==="
    free -m
    echo ""

    # Top 20 memory consumers
    echo "=== TOP 20 MEMORY CONSUMERS ==="
    echo "PID       USER      RSS(MB)  %MEM  COMMAND"
    echo "-----------------------------------------------"
    ps aux --sort=-%mem | head -n 21 | tail -n 20 | awk '{printf "%-9s %-9s %-8s %-5s %s\n", $2, $1, int($6/1024), $4, $11}'
    echo ""

    # Memory by user
    echo "=== MEMORY BY USER ==="
    ps aux | awk 'NR>1 {user[$1]+=$6} END {for (u in user) printf "%-15s %10.2f MB\n", u, user[u]/1024}' | sort -k2 -rn
    echo ""

    # Systemd services memory
    echo "=== TOP 15 SYSTEMD SERVICES (Memory) ==="
    systemctl list-units --type=service --state=running --no-pager | \
        awk '{print $1}' | grep '.service$' | \
        head -n 15 | \
        while read service; do
            mem=$(systemctl show "$service" --property=MemoryCurrent 2>/dev/null | cut -d= -f2)
            if [ "$mem" != "" ] && [ "$mem" != "[not set]" ] && [ "$mem" -gt 0 ] 2>/dev/null; then
                mem_mb=$(echo "scale=2; $mem / 1024 / 1024" | bc)
                printf "%-40s %10.2f MB\n" "$service" "$mem_mb"
            fi
        done | sort -k2 -rn | head -n 15
    echo ""

    # Desktop environment
    echo "=== DESKTOP ENVIRONMENT ==="
    if pgrep -x mate-session &>/dev/null; then
        mate_mem=$(ps aux | grep -E 'mate-|caja|pluma' | grep -v grep | awk '{sum+=$6} END {printf "%.2f", sum/1024}')
        echo "MATE Desktop: ${mate_mem} MB"
    fi

    if pgrep -x Xorg &>/dev/null || pgrep -x X &>/dev/null; then
        x_mem=$(ps aux | grep -E 'Xorg|X ' | grep -v grep | head -1 | awk '{printf "%.2f", $6/1024}')
        echo "X Server: ${x_mem} MB"
    fi
    echo ""

    # Rust services (SynOS specific)
    echo "=== SYNOS RUST SERVICES ==="
    rust_total=0
    for proc in $(pgrep -f 'synos|alfred|consciousness'); do
        if ps -p "$proc" &>/dev/null; then
            cmd=$(ps -p "$proc" -o comm= 2>/dev/null || echo "unknown")
            mem=$(ps -p "$proc" -o rss= 2>/dev/null || echo "0")
            mem_mb=$(echo "scale=2; $mem / 1024" | bc)
            rust_total=$(echo "$rust_total + $mem_mb" | bc)
            printf "%-30s %10.2f MB\n" "$cmd" "$mem_mb"
        fi
    done
    echo "-----------------------------------------------"
    printf "%-30s %10.2f MB\n" "Total Rust Services:" "$rust_total"
    echo ""

    # Python processes (ALFRED)
    echo "=== PYTHON PROCESSES (ALFRED) ==="
    python_total=0
    ps aux | grep python | grep -v grep | while read line; do
        pid=$(echo "$line" | awk '{print $2}')
        mem=$(echo "$line" | awk '{print $6}')
        mem_mb=$(echo "scale=2; $mem / 1024" | bc)
        cmd=$(echo "$line" | awk '{print $11}')
        python_total=$(echo "$python_total + $mem_mb" | bc)
        printf "%-30s %10.2f MB\n" "$(basename "$cmd")" "$mem_mb"
    done
    echo ""

    # Swap usage
    echo "=== SWAP USAGE ==="
    swap_total=$(free -h | awk '/^Swap:/ {print $2}')
    swap_used=$(free -h | awk '/^Swap:/ {print $3}')
    swap_free=$(free -h | awk '/^Swap:/ {print $4}')
    echo "Total: $swap_total"
    echo "Used:  $swap_used"
    echo "Free:  $swap_free"
    echo ""

    # Memory optimization recommendations
    echo "=== OPTIMIZATION RECOMMENDATIONS ==="

    # Check high memory services
    high_mem_services=$(systemctl list-units --type=service --state=running --no-pager | \
        awk '{print $1}' | grep '.service$' | head -n 20 | \
        while read service; do
            mem=$(systemctl show "$service" --property=MemoryCurrent 2>/dev/null | cut -d= -f2)
            if [ "$mem" != "" ] && [ "$mem" != "[not set]" ] && [ "$mem" -gt 104857600 ] 2>/dev/null; then
                echo "$service"
            fi
        done)

    if [ ! -z "$high_mem_services" ]; then
        echo "⚠ High memory services detected (>100MB):"
        echo "$high_mem_services" | while read svc; do
            echo "  • $svc - Consider optimization or lazy loading"
        done
    else
        echo "✓ No excessively high memory services detected"
    fi
    echo ""

    # Cache and buffers
    cached=$(free -m | awk '/^Mem:/ {print $6}')
    if [ "$cached" -gt 500 ]; then
        echo "✓ Good cache usage: ${cached}MB"
    else
        echo "⚠ Low cache: ${cached}MB - May affect performance"
    fi
    echo ""

    # Desktop environment optimization
    if pgrep -x mate-session &>/dev/null; then
        echo "MATE Desktop optimizations:"
        echo "  • Consider disabling unused applets"
        echo "  • Reduce compositor effects"
        echo "  • Disable desktop animations"
    fi
    echo ""

    # Profile complete
    echo "========================================"
    echo "Profile saved to: $PROFILE_FILE"
    echo "========================================"

} | tee "$PROFILE_FILE"

echo ""
echo -e "${GREEN}Memory profiling complete!${NC}"
echo ""

# Calculate target reduction
current_mem=$(free -m | awk '/^Mem:/ {print $3}')
target_reduction=$(echo "scale=0; $current_mem * 0.15" | bc)
target_mem=$(echo "scale=0; $current_mem - $target_reduction" | bc)

echo -e "${BLUE}=== MEMORY REDUCTION TARGET ===${NC}"
echo -e "Current Usage:    ${YELLOW}${current_mem} MB${NC}"
echo -e "Target Reduction: ${CYAN}${target_reduction} MB (15%)${NC}"
echo -e "Target Usage:     ${GREEN}${target_mem} MB${NC}"
echo ""

# Compare with baseline if exists
BASELINE_FILE="$OUTPUT_DIR/memory-baseline.txt"
if [ -f "$BASELINE_FILE" ]; then
    baseline_mem=$(grep "Current Usage:" "$BASELINE_FILE" | awk '{print $3}')
    if [ ! -z "$baseline_mem" ]; then
        diff=$(echo "scale=0; $baseline_mem - $current_mem" | bc)
        percent=$(echo "scale=1; ($baseline_mem - $current_mem) / $baseline_mem * 100" | bc)

        echo -e "${BLUE}=== COMPARISON WITH BASELINE ===${NC}"
        echo -e "Baseline:  ${baseline_mem} MB"
        echo -e "Current:   ${current_mem} MB"

        if [ $(echo "$diff > 0" | bc) -eq 1 ]; then
            echo -e "Change:    ${GREEN}-${diff} MB (${percent}% improvement)${NC} ✓"
        else
            diff=${diff#-}
            percent=${percent#-}
            echo -e "Change:    ${RED}+${diff} MB (${percent}% increase)${NC} ✗"
        fi
    fi
else
    echo -e "${YELLOW}No baseline found. Creating baseline...${NC}"
    cp "$PROFILE_FILE" "$BASELINE_FILE"
    echo "Current Usage:    ${current_mem} MB" >> "$BASELINE_FILE"
    echo -e "${GREEN}✓ Baseline created${NC}"
fi

echo ""
echo -e "${BLUE}Profile Location:${NC}"
echo "  $PROFILE_FILE"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review top memory consumers"
echo "  2. Identify optimization targets"
echo "  3. Implement lazy loading for heavy services"
echo "  4. Re-run profiler to measure improvements"
echo ""
echo -e "${CYAN}Run again after optimization:${NC}"
echo "  ./scripts/performance/memory-profiler.sh"
echo ""
