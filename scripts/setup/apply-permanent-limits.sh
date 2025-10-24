#!/bin/bash
# Apply permanent system limits for SynOS development
# Run with: sudo bash scripts/apply-permanent-limits.sh

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Usage: sudo bash scripts/apply-permanent-limits.sh"
    exit 1
fi

echo "========================================="
echo " Applying Permanent System Limits"
echo "========================================="
echo ""

# Backup existing limits.conf
LIMITS_FILE="/etc/security/limits.conf"
BACKUP_FILE="/etc/security/limits.conf.backup-$(date +%Y%m%d-%H%M%S)"

if [ -f "$LIMITS_FILE" ]; then
    echo "📋 Backing up existing limits.conf to:"
    echo "   $BACKUP_FILE"
    cp "$LIMITS_FILE" "$BACKUP_FILE"
else
    echo "⚠️  No existing limits.conf found - creating new"
fi

# Add SynOS limits
echo ""
echo "📝 Adding SynOS development limits..."

cat >> "$LIMITS_FILE" << 'EOF'

# ========================================
# SynOS Development Environment Limits
# Added: October 23, 2025
# ========================================

# Global defaults (all users)
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768

# User-specific limits (developer account)
diablorain soft nofile 1048576
diablorain hard nofile 1048576
diablorain soft nproc 65536
diablorain hard nproc 65536
diablorain soft stack 8192
diablorain hard stack 16384

# Root limits
root soft nofile 1048576
root hard nofile 1048576

# End of SynOS limits
EOF

echo "✅ Limits added to $LIMITS_FILE"
echo ""

# Show what was added
echo "📄 Added configuration:"
echo "---"
tail -20 "$LIMITS_FILE"
echo "---"
echo ""

# Fix systemd user service limits
echo "🔧 Configuring systemd user service limits..."
SYSTEMD_USER_DIR="/etc/systemd/system/user@.service.d"
SYSTEMD_LIMITS_FILE="$SYSTEMD_USER_DIR/limits.conf"

mkdir -p "$SYSTEMD_USER_DIR"

cat > "$SYSTEMD_LIMITS_FILE" << 'EOF'
[Service]
# SynOS Development Environment
LimitNOFILE=1048576
LimitNPROC=65536
TasksMax=65536
EOF

echo "✅ Systemd user limits configured"
echo ""

# Fix systemd-logind limits
echo "🔧 Configuring systemd-logind..."
LOGIND_CONF="/etc/systemd/logind.conf"

# Check if UserTasksMax is already configured
if grep -q "^UserTasksMax=" "$LOGIND_CONF"; then
    echo "⚠️  UserTasksMax already configured in logind.conf"
else
    # Add or uncomment UserTasksMax
    if grep -q "^#UserTasksMax=" "$LOGIND_CONF"; then
        sed -i 's/^#UserTasksMax=.*/UserTasksMax=65536/' "$LOGIND_CONF"
    else
        echo "" >> "$LOGIND_CONF"
        echo "[Login]" >> "$LOGIND_CONF"
        echo "UserTasksMax=65536" >> "$LOGIND_CONF"
    fi
    echo "✅ UserTasksMax configured in logind.conf"
fi
echo ""

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload
echo "✅ Systemd reloaded"
echo ""

# Summary
echo "========================================="
echo " ✅ Configuration Complete"
echo "========================================="
echo ""
echo "Applied limits:"
echo "  • Open files: 1,048,576 (for diablorain)"
echo "  • Processes: 65,536 (for diablorain)"
echo "  • Systemd tasks: 65,536"
echo ""
echo "⚠️  IMPORTANT: Changes take effect on next login"
echo ""
echo "Next steps:"
echo "  1. Log out and log back in (or reboot)"
echo "  2. Verify with: ulimit -n"
echo "  3. Should show: 1048576"
echo ""
echo "Backup saved to:"
echo "  $BACKUP_FILE"
echo ""
echo "========================================="
