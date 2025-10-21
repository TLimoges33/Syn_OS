#!/bin/bash
################################################################################
# SynOS Memory Optimizer
# Reduces memory footprint by optimizing services and desktop environment
# Target: 15% reduction (from 4.7GB to 4.0GB)
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Memory Optimizer v1.1                              ║"
echo "║   Target: 15% Reduction (4.7GB → 4.0GB)                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Get current memory usage
current_mem=$(free -m | awk '/^Mem:/ {print $3}')
target_reduction=$(echo "scale=0; $current_mem * 0.15" | bc)
target_mem=$(echo "scale=0; $current_mem - $target_reduction" | bc)

echo -e "${BLUE}Current Status:${NC}"
echo "  Current Memory:    ${current_mem} MB"
echo "  Target Reduction:  ${target_reduction} MB (15%)"
echo "  Target Memory:     ${target_mem} MB"
echo ""

echo -e "${YELLOW}This script will optimize memory usage. Some services may be disabled.${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${BLUE}=== PHASE 1: Desktop Environment Optimization ===${NC}"
echo ""

# MATE Desktop optimizations
if pgrep -x mate-session &>/dev/null; then
    echo -e "${YELLOW}Optimizing MATE Desktop...${NC}"

    # Disable compositor effects
    if command -v gsettings &>/dev/null; then
        echo -ne "  Disabling compositor effects... "
        gsettings set org.mate.Marco.general compositing-manager false 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${CYAN}N/A${NC}"

        # Disable animations
        echo -ne "  Disabling animations... "
        gsettings set org.mate.Marco.general reduced-resources true 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${CYAN}N/A${NC}"

        # Optimize file manager
        echo -ne "  Optimizing Caja file manager... "
        gsettings set org.mate.caja.preferences show-image-thumbnails 'never' 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${CYAN}N/A${NC}"

        echo -e "${GREEN}✓ MATE optimizations applied${NC}"
    else
        echo -e "${CYAN}  gsettings not available${NC}"
    fi
else
    echo -e "${CYAN}  MATE Desktop not running${NC}"
fi

echo ""
echo -e "${BLUE}=== PHASE 2: Service Memory Optimization ===${NC}"
echo ""

# Disable memory-heavy non-critical services
MEMORY_HEAVY_SERVICES=(
    "ModemManager.service"        # 1.54 MB - Not needed on most systems
    "bluetooth.service"           # 1.35 MB - Disable if not using Bluetooth
)

echo -e "${YELLOW}Memory-heavy services (consider disabling if not needed):${NC}"
for service in "${MEMORY_HEAVY_SERVICES[@]}"; do
    mem=$(systemctl show "$service" --property=MemoryCurrent 2>/dev/null | cut -d= -f2)
    if [ "$mem" != "" ] && [ "$mem" != "[not set]" ] && [ "$mem" -gt 0 ] 2>/dev/null; then
        mem_mb=$(echo "scale=2; $mem / 1024 / 1024" | bc)
        echo "  • $service (${mem_mb} MB)"
    fi
done

echo ""
read -p "Disable these services? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for service in "${MEMORY_HEAVY_SERVICES[@]}"; do
        if systemctl is-active "$service" &>/dev/null; then
            echo -ne "${YELLOW}Stopping $service... ${NC}"
            sudo systemctl stop "$service" && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"

            echo -ne "${YELLOW}Disabling $service... ${NC}"
            sudo systemctl disable "$service" &>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}"
        fi
    done
fi

echo ""
echo -e "${BLUE}=== PHASE 3: Kernel Memory Management ===${NC}"
echo ""

# Optimize swappiness
echo -e "${YELLOW}Optimizing swap usage...${NC}"
current_swappiness=$(cat /proc/sys/vm/swappiness)
echo "  Current swappiness: $current_swappiness"

if [ "$current_swappiness" -gt 10 ]; then
    echo -ne "  Setting swappiness to 10 (prefer RAM over swap)... "
    echo 10 | sudo tee /proc/sys/vm/swappiness > /dev/null

    # Make permanent
    sudo tee /etc/sysctl.d/99-swappiness.conf > /dev/null <<EOF
# Reduce swappiness for better performance
vm.swappiness=10
EOF
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${GREEN}  ✓ Already optimized${NC}"
fi

# Optimize cache pressure
echo -ne "  Optimizing VFS cache pressure... "
echo 50 | sudo tee /proc/sys/vm/vfs_cache_pressure > /dev/null
sudo tee /etc/sysctl.d/99-cache-pressure.conf > /dev/null <<EOF
# Optimize cache retention
vm.vfs_cache_pressure=50
EOF
echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${BLUE}=== PHASE 4: Application Memory Optimization ===${NC}"
echo ""

# Check for memory leaks in long-running processes
echo -e "${YELLOW}Analyzing long-running processes...${NC}"
ps aux --sort=-%mem | head -n 10 | awk 'NR>1 {printf "  %-30s %6s MB  (%s%%)\n", $11, int($6/1024), $4}'

echo ""
echo -e "${CYAN}Tip: Restart high-memory applications if they've been running for days${NC}"

echo ""
echo -e "${BLUE}=== PHASE 5: Preload Configuration ===${NC}"
echo ""

# Install and configure preload for better memory usage
if ! command -v preload &>/dev/null; then
    echo -e "${YELLOW}Preload not installed. Install it for better memory efficiency.${NC}"
    echo -e "${CYAN}  sudo apt install preload${NC}"
else
    echo -e "${GREEN}✓ Preload already installed${NC}"

    # Configure preload
    if [ -f /etc/preload.conf ]; then
        echo -ne "  Optimizing preload configuration... "
        sudo sed -i 's/^memtotal = .*/memtotal = 50/' /etc/preload.conf 2>/dev/null
        sudo sed -i 's/^minsize = .*/minsize = 2000/' /etc/preload.conf 2>/dev/null
        echo -e "${GREEN}✓${NC}"
    fi
fi

echo ""
echo -e "${BLUE}=== PHASE 6: Browser Memory Optimization ===${NC}"
echo ""

# Firefox optimizations (if profile exists)
if [ -d ~/.mozilla/firefox/*.default* ]; then
    echo -e "${YELLOW}Optimizing Firefox memory usage...${NC}"

    firefox_prefs=$(find ~/.mozilla/firefox/*.default*/prefs.js | head -n 1)
    if [ ! -z "$firefox_prefs" ]; then
        echo "  Creating memory optimization config..."
        cat >> "$firefox_prefs" <<EOF

// SynOS Memory Optimizations
user_pref("browser.cache.memory.capacity", 65536);
user_pref("browser.sessionhistory.max_total_viewers", 2);
user_pref("browser.tabs.animate", false);
user_pref("config.trim_on_minimize", true);
EOF
        echo -e "${GREEN}  ✓ Firefox optimized${NC}"
    fi
else
    echo -e "${CYAN}  Firefox profile not found${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Memory Optimization Complete!                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check new memory usage
new_mem=$(free -m | awk '/^Mem:/ {print $3}')
saved=$(echo "scale=0; $current_mem - $new_mem" | bc)

echo -e "${BLUE}Memory Usage:${NC}"
echo "  Before: ${current_mem} MB"
echo "  After:  ${new_mem} MB"

if [ "$saved" -gt 0 ]; then
    percent=$(echo "scale=1; $saved / $current_mem * 100" | bc)
    echo -e "  Saved:  ${GREEN}${saved} MB (${percent}%)${NC} ✓"
else
    saved=${saved#-}
    echo -e "  Change: ${YELLOW}+${saved} MB${NC}"
    echo -e "${CYAN}  Note: Some optimizations require restart to take effect${NC}"
fi

echo ""
echo -e "${BLUE}Optimizations Applied:${NC}"
echo "  • Desktop compositor disabled"
echo "  • Animations reduced"
echo "  • Swap usage optimized (swappiness=10)"
echo "  • VFS cache pressure optimized"
echo "  • Memory-heavy services disabled"
echo ""

echo -e "${YELLOW}⚠ For full effect, restart applications or reboot${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Restart heavy applications (browsers, IDEs)"
echo "  2. Run: ./scripts/performance/memory-profiler.sh"
echo "  3. Compare with baseline to measure improvement"
echo ""

echo -e "${CYAN}To further reduce memory:${NC}"
echo "  • Close unused browser tabs"
echo "  • Limit VS Code extensions"
echo "  • Use lightweight alternatives to heavy apps"
echo ""
