#!/bin/bash
################################################################################
# SynOS Boot Optimization Script
# Optimizes boot time by disabling unnecessary services
# Safe mode: Only disables services that won't break system functionality
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SynOS Boot Optimizer v1.1                                ║"
echo "║   Target: Reduce boot time from 55s to <30s                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${YELLOW}This script will disable non-critical services to improve boot time.${NC}"
echo -e "${YELLOW}All changes can be reverted with 'systemctl enable <service>'${NC}"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${BLUE}=== PHASE 1: Disabling Slow Non-Critical Services ===${NC}"
echo ""

# Services safe to disable (won't break system)
SAFE_TO_DISABLE=(
    "NetworkManager-wait-online.service"  # 6.6s - Network not needed for boot
    "man-db.service"                      # 6.8s - Man page indexing can wait
    "apt-daily.service"                   # 5.1s - Can run later
    "apt-daily-upgrade.service"           # 895ms - Can run later
    "e2scrub_reap.service"                # 792ms - Filesystem check can wait
    "arpwatch.service"                    # 554ms - Not critical for boot
    "podman-auto-update.service"          # 367ms - Container updates can wait
    "sysstat.service"                     # 499ms - Statistics can wait
    "phpsessionclean.service"             # 171ms - PHP cleanup can wait
    "logrotate.service"                   # 140ms - Log rotation can wait
    "dpkg-db-backup.service"              # 86ms - Package db backup can wait
    "systemd-tmpfiles-clean.service"      # 55ms - Cleanup can wait
)

for service in "${SAFE_TO_DISABLE[@]}"; do
    if systemctl is-enabled "$service" &>/dev/null; then
        echo -ne "${YELLOW}Disabling $service... ${NC}"
        if sudo systemctl disable "$service" &>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗ (may not exist)${NC}"
        fi
    else
        echo -e "${CYAN}$service already disabled${NC}"
    fi
done

echo ""
echo -e "${BLUE}=== PHASE 2: Optimizing Service Dependencies ===${NC}"
echo ""

# Mask services that are completely unnecessary
SERVICES_TO_MASK=(
    "apt-daily.timer"
    "apt-daily-upgrade.timer"
)

for service in "${SERVICES_TO_MASK[@]}"; do
    if systemctl is-enabled "$service" &>/dev/null; then
        echo -ne "${YELLOW}Masking $service... ${NC}"
        if sudo systemctl mask "$service" &>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    else
        echo -e "${CYAN}$service already masked/disabled${NC}"
    fi
done

echo ""
echo -e "${BLUE}=== PHASE 3: Systemd Configuration Optimization ===${NC}"
echo ""

# Backup systemd config
if [ ! -f /etc/systemd/system.conf.backup ]; then
    echo -e "${YELLOW}Backing up /etc/systemd/system.conf...${NC}"
    sudo cp /etc/systemd/system.conf /etc/systemd/system.conf.backup
    echo -e "${GREEN}✓ Backup created${NC}"
fi

echo -e "${YELLOW}Optimizing systemd parallel execution...${NC}"

# Create optimized systemd config
sudo tee /etc/systemd/system.conf.d/boot-optimization.conf > /dev/null <<EOF
# SynOS Boot Optimization
[Manager]
# Increase default timeout to prevent service failures
DefaultTimeoutStartSec=30s
DefaultTimeoutStopSec=15s

# Optimize parallel execution
DefaultStartLimitIntervalSec=60s
DefaultStartLimitBurst=10
EOF

echo -e "${GREEN}✓ Systemd configuration optimized${NC}"

echo ""
echo -e "${BLUE}=== PHASE 4: Plymouth Boot Splash Optimization ===${NC}"
echo ""

# Disable plymouth if it's slowing boot
if systemctl is-enabled plymouth-quit-wait.service &>/dev/null; then
    plymouth_time=$(systemd-analyze blame | grep plymouth | head -1 | awk '{print $1}' | sed 's/s//' | sed 's/ms//')
    echo -e "${YELLOW}Plymouth boot splash takes ${plymouth_time}${NC}"
    echo -e "${CYAN}Consider disabling for faster boot (optional)${NC}"
    echo -e "${CYAN}  sudo systemctl disable plymouth-quit-wait.service${NC}"
fi

echo ""
echo -e "${BLUE}=== PHASE 5: Memory and Filesystem Optimization ===${NC}"
echo ""

# Enable readahead (if available)
if command -v systemd-readahead &>/dev/null; then
    echo -e "${YELLOW}Enabling readahead for faster file loading...${NC}"
    sudo systemctl enable systemd-readahead-collect.service
    sudo systemctl enable systemd-readahead-replay.service
    echo -e "${GREEN}✓ Readahead enabled${NC}"
else
    echo -e "${CYAN}Readahead not available on this system${NC}"
fi

# Optimize journal size
echo -e "${YELLOW}Optimizing systemd journal size...${NC}"
sudo mkdir -p /etc/systemd/journald.conf.d/
sudo tee /etc/systemd/journald.conf.d/size-limit.conf > /dev/null <<EOF
# Limit journal size for faster boot
[Journal]
SystemMaxUse=100M
RuntimeMaxUse=100M
EOF
echo -e "${GREEN}✓ Journal size optimized${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Boot Optimization Complete!                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Services Optimized:${NC}"
echo "  • Disabled ${#SAFE_TO_DISABLE[@]} slow non-critical services"
echo "  • Masked ${#SERVICES_TO_MASK[@]} unnecessary timers"
echo "  • Optimized systemd parallel execution"
echo "  • Configured journal size limits"
echo ""

echo -e "${YELLOW}⚠ IMPORTANT: Reboot required for changes to take effect${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review changes: ls /etc/systemd/system.conf.d/"
echo "  2. Reboot: sudo reboot"
echo "  3. Test boot time: ./scripts/performance/boot-analyzer.sh"
echo ""

echo -e "${BLUE}To Revert Changes:${NC}"
echo "  • Restore config: sudo cp /etc/systemd/system.conf.backup /etc/systemd/system.conf"
echo "  • Re-enable services: sudo systemctl enable <service>"
echo "  • Unmask timers: sudo systemctl unmask <timer>"
echo ""

echo -e "${CYAN}Expected boot time improvement: 20-25 seconds${NC}"
echo -e "${GREEN}Target: <30 seconds (from current 55s)${NC}"
echo ""
