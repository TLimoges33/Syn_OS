#!/bin/bash
################################################################################
# SynOS Boot Performance Analyzer
# Analyzes boot time and identifies optimization opportunities
# Target: <30 seconds boot time for v1.1
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
BOOT_FILE="$OUTPUT_DIR/boot-analysis-$TIMESTAMP.txt"

mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Boot Performance Analyzer v1.1                     ║"
echo "║   Target: <30 seconds boot time                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

{
    echo "SynOS Boot Performance Analysis - $(date)"
    echo "========================================"
    echo ""

    # System info
    echo "=== SYSTEM INFORMATION ==="
    echo "Hostname: $(hostname)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p)"
    echo "Boot time: $(who -b | awk '{print $3, $4}')"
    echo ""

    # Overall boot time
    echo "=== OVERALL BOOT TIME ==="
    boot_time=$(systemd-analyze 2>/dev/null || echo "systemd-analyze not available")
    echo "$boot_time"
    echo ""

    # Critical chain
    echo "=== CRITICAL PATH (Slowest Chain) ==="
    systemd-analyze critical-chain 2>/dev/null | head -n 20 || echo "Not available"
    echo ""

    # Slowest services
    echo "=== TOP 20 SLOWEST SERVICES ==="
    echo "TIME      SERVICE"
    echo "---------------------------------------"
    systemd-analyze blame 2>/dev/null | head -n 20 || echo "Not available"
    echo ""

    # Services taking >1 second
    echo "=== SERVICES TAKING >1 SECOND ==="
    slow_services=$(systemd-analyze blame 2>/dev/null | awk '$1 ~ /s$/ {time=$1; sub(/s/, "", time); if (time+0 >= 1.0) print}' | wc -l)
    echo "Count: $slow_services services"
    systemd-analyze blame 2>/dev/null | awk '$1 ~ /s$/ {time=$1; sub(/s/, "", time); if (time+0 >= 1.0) print}' | head -n 15
    echo ""

    # Services taking >5 seconds (critical)
    echo "=== CRITICAL: SERVICES TAKING >5 SECONDS ==="
    critical_count=$(systemd-analyze blame 2>/dev/null | awk '$1 ~ /s$/ {time=$1; sub(/s/, "", time); if (time+0 >= 5.0) print}' | wc -l)
    if [ "$critical_count" -gt 0 ]; then
        echo "⚠ Found $critical_count critical slow services:"
        systemd-analyze blame 2>/dev/null | awk '$1 ~ /s$/ {time=$1; sub(/s/, "", time); if (time+0 >= 5.0) print}'
    else
        echo "✓ No services taking more than 5 seconds"
    fi
    echo ""

    # Parallel service execution
    echo "=== SERVICE PARALLELIZATION ==="
    total_services=$(systemctl list-units --type=service --all --no-pager | grep -c '\.service')
    active_services=$(systemctl list-units --type=service --state=running --no-pager | grep -c '\.service')
    failed_services=$(systemctl list-units --type=service --state=failed --no-pager | grep -c '\.service' || echo "0")

    echo "Total services:  $total_services"
    echo "Active services: $active_services"
    echo "Failed services: $failed_services"
    echo ""

    # Failed services detail
    if [ "$failed_services" -gt 0 ]; then
        echo "=== FAILED SERVICES (May delay boot) ==="
        systemctl list-units --type=service --state=failed --no-pager | grep '\.service'
        echo ""
    fi

    # Kernel boot time
    echo "=== KERNEL & FIRMWARE ==="
    systemd-analyze 2>/dev/null | grep -E 'firmware|loader|kernel' || echo "Not available"
    echo ""

    # User space vs kernel space
    echo "=== BOOT PHASE BREAKDOWN ==="
    systemd-analyze time 2>/dev/null || echo "Not available"
    echo ""

    # Service dependencies
    echo "=== DEPENDENCY ANALYSIS ==="
    echo "Services with most dependencies (may cause delays):"
    for service in graphical.target multi-user.target network.target; do
        deps=$(systemctl list-dependencies --no-pager "$service" 2>/dev/null | wc -l)
        echo "  $service: $deps dependencies"
    done
    echo ""

    # Desktop environment startup
    echo "=== DESKTOP ENVIRONMENT STARTUP ==="
    if pgrep -x mate-session &>/dev/null; then
        echo "Desktop: MATE"
        # Try to get display manager startup time
        dm_time=$(systemd-analyze blame 2>/dev/null | grep -E 'lightdm|gdm|sddm|display-manager' | head -1)
        if [ ! -z "$dm_time" ]; then
            echo "Display Manager: $dm_time"
        fi
    fi
    echo ""

    # Optimization recommendations
    echo "=== OPTIMIZATION RECOMMENDATIONS ==="

    # Check if boot time is over target
    boot_seconds=$(systemd-analyze 2>/dev/null | grep "Startup finished" | grep -oP '\d+\.\d+s' | tail -1 | sed 's/s//')
    if [ ! -z "$boot_seconds" ]; then
        boot_seconds_int=$(echo "$boot_seconds" | cut -d. -f1)
        if [ "$boot_seconds_int" -gt 30 ]; then
            echo "⚠ Boot time (${boot_seconds}s) exceeds target (30s)"
            echo ""
            echo "Recommended actions:"
            echo "  1. Disable unnecessary services:"

            # Suggest services to disable
            systemd-analyze blame 2>/dev/null | head -n 10 | while read line; do
                service=$(echo "$line" | awk '{print $2}')
                time=$(echo "$line" | awk '{print $1}')
                echo "     • $service ($time) - Check if needed"
            done
            echo ""
            echo "  2. Enable parallel service startup in /etc/systemd/system.conf"
            echo "  3. Optimize critical path services"
            echo "  4. Consider using preload for commonly used files"
        else
            echo "✓ Boot time (${boot_seconds}s) meets target (<30s)"
        fi
    fi
    echo ""

    # Check for slow network wait
    network_wait=$(systemd-analyze blame 2>/dev/null | grep 'network.*wait\|NetworkManager-wait' | head -1)
    if [ ! -z "$network_wait" ]; then
        echo "⚠ Network wait detected: $network_wait"
        echo "  Consider: systemctl disable NetworkManager-wait-online.service"
        echo ""
    fi

    # Check for plymouth (boot splash)
    plymouth_time=$(systemd-analyze blame 2>/dev/null | grep plymouth | head -1)
    if [ ! -z "$plymouth_time" ]; then
        time_val=$(echo "$plymouth_time" | awk '{print $1}' | sed 's/s//' | sed 's/ms//')
        if [ $(echo "$time_val > 2000" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
            echo "⚠ Plymouth boot splash is slow: $plymouth_time"
            echo "  Consider: Optimizing animation or disabling"
            echo ""
        fi
    fi

    echo "========================================"
    echo "Analysis saved to: $BOOT_FILE"
    echo "========================================"

} | tee "$BOOT_FILE"

echo ""
echo -e "${GREEN}Boot analysis complete!${NC}"
echo ""

# Extract and display key metrics
echo -e "${BLUE}=== KEY METRICS ===${NC}"

boot_total=$(systemd-analyze 2>/dev/null | grep "Startup finished" | grep -oP '\d+\.\d+s' | tail -1)
if [ ! -z "$boot_total" ]; then
    echo -e "Total Boot Time:  ${YELLOW}${boot_total}${NC}"

    boot_seconds=$(echo "$boot_total" | sed 's/s//')
    target=30

    if [ $(echo "$boot_seconds < $target" | bc -l) -eq 1 ]; then
        echo -e "Status:           ${GREEN}✓ MEETS TARGET (<${target}s)${NC}"
    else
        diff=$(echo "scale=1; $boot_seconds - $target" | bc -l)
        echo -e "Status:           ${RED}✗ EXCEEDS TARGET by ${diff}s${NC}"
    fi
else
    echo -e "${YELLOW}Boot time data not available${NC}"
fi

echo ""

# Count slow services
slow_count=$(systemd-analyze blame 2>/dev/null | awk '$1 ~ /s$/ {time=$1; sub(/s/, "", time); if (time+0 >= 1.0) print}' | wc -l)
echo -e "Slow Services (>1s):  ${YELLOW}${slow_count}${NC}"

critical_count=$(systemd-analyze blame 2>/dev/null | awk '$1 ~ /s$/ {time=$1; sub(/s/, "", time); if (time+0 >= 5.0) print}' | wc -l)
if [ "$critical_count" -gt 0 ]; then
    echo -e "Critical Slow (>5s):  ${RED}${critical_count}${NC} ⚠"
else
    echo -e "Critical Slow (>5s):  ${GREEN}0${NC} ✓"
fi

echo ""
echo -e "${BLUE}Analysis Location:${NC}"
echo "  $BOOT_FILE"
echo ""

# Compare with baseline if exists
BASELINE_FILE="$OUTPUT_DIR/boot-baseline.txt"
if [ -f "$BASELINE_FILE" ]; then
    baseline_time=$(grep "Total Boot Time:" "$BASELINE_FILE" | awk '{print $4}' | sed 's/s//')
    if [ ! -z "$baseline_time" ] && [ ! -z "$boot_total" ]; then
        current_time=$(echo "$boot_total" | sed 's/s//')
        diff=$(echo "scale=2; $baseline_time - $current_time" | bc -l)
        percent=$(echo "scale=1; ($baseline_time - $current_time) / $baseline_time * 100" | bc -l)

        echo -e "${BLUE}=== COMPARISON WITH BASELINE ===${NC}"
        echo -e "Baseline:  ${baseline_time}s"
        echo -e "Current:   ${current_time}s"

        if [ $(echo "$diff > 0" | bc -l) -eq 1 ]; then
            echo -e "Change:    ${GREEN}-${diff}s (${percent}% faster)${NC} ✓"
        else
            diff=${diff#-}
            percent=${percent#-}
            echo -e "Change:    ${RED}+${diff}s (${percent}% slower)${NC} ✗"
        fi
        echo ""
    fi
else
    echo -e "${YELLOW}No baseline found. Creating baseline...${NC}"
    cp "$BOOT_FILE" "$BASELINE_FILE"
    if [ ! -z "$boot_total" ]; then
        echo "Total Boot Time:  $boot_total" >> "$BASELINE_FILE"
    fi
    echo -e "${GREEN}✓ Baseline created${NC}"
    echo ""
fi

echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review slowest services in the report"
echo "  2. Disable unnecessary services"
echo "  3. Enable parallel startup"
echo "  4. Reboot and re-run analysis"
echo ""
echo -e "${CYAN}Useful commands:${NC}"
echo "  • systemctl disable <service>  - Disable service"
echo "  • systemctl mask <service>     - Prevent service from starting"
echo "  • systemd-analyze plot > boot.svg  - Visual timeline"
echo ""
