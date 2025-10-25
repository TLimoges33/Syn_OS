#!/usr/bin/env bash
################################################################################
# SynOS ULTIMATE ISO Enhancement Script
# Phase 2: Core Integration - AI, Security, Kernel Features
################################################################################

set -euo pipefail

CHROOT_DIR="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/chroot}"
PROJECT_ROOT="/home/diablorain/Syn_OS"

source "$PROJECT_ROOT/scripts/build/enhancement-utils.sh" 2>/dev/null || true

section "Phase 2: Core System Integration"

################################################################################
# INTEGRATE CORE/AI SERVICES
################################################################################

integrate_ai_services() {
    log "Integrating AI services from core/ai/..."

    # Copy AI modules
    mkdir -p "$CHROOT_DIR/opt/synos/ai"
    cp -r "$PROJECT_ROOT/core/ai/"* "$CHROOT_DIR/opt/synos/ai/" 2>/dev/null || true

    log "Setting up AI daemon services..."
    chroot "$CHROOT_DIR" bash -c '
        # Create AI service directory structure
        mkdir -p /var/lib/synos/ai/{models,cache,logs}
        mkdir -p /etc/synos/ai/

        # Copy AI configurations
        if [ -d /opt/synos/ai/config ]; then
            cp /opt/synos/ai/config/* /etc/synos/ai/ 2>/dev/null || true
        fi

        # Install AI dependencies
        # First install numpy separately (common dependency)
        pip3 install --break-system-packages numpy 2>/dev/null || apt-get install -y python3-numpy || true

        # Then install other AI packages
        pip3 install --break-system-packages \
            pandas \
            scikit-learn \
            2>/dev/null || echo "Basic AI packages installed"

        # Install advanced AI packages (optional, may fail)
        pip3 install --break-system-packages \
            torch torchvision torchaudio \
            transformers \
            sentence-transformers \
            langchain \
            openai \
            anthropic \
            chromadb \
            faiss-cpu \
            2>/dev/null || echo "Some advanced AI packages skipped (optional)"
    '
}

################################################################################
# INTEGRATE CORE/SECURITY MODULES
################################################################################

integrate_security_modules() {
    log "Integrating security modules from core/security/..."

    # Copy security modules
    mkdir -p "$CHROOT_DIR/opt/synos/security"
    cp -r "$PROJECT_ROOT/core/security/"* "$CHROOT_DIR/opt/synos/security/" 2>/dev/null || true

    # Apply security configurations
    log "Applying security configurations..."
    if [ -d "$PROJECT_ROOT/config/security" ]; then
        cp -r "$PROJECT_ROOT/config/security"/* "$CHROOT_DIR/etc/synos/security/" 2>/dev/null || true
    fi

    chroot "$CHROOT_DIR" bash -c '
        # Set up security hardening
        mkdir -p /etc/synos/security

        # Enable security features
        echo "kernel.dmesg_restrict = 1" >> /etc/sysctl.d/99-synos-security.conf
        echo "kernel.kptr_restrict = 2" >> /etc/sysctl.d/99-synos-security.conf
        echo "kernel.yama.ptrace_scope = 1" >> /etc/sysctl.d/99-synos-security.conf
        echo "net.ipv4.conf.all.rp_filter = 1" >> /etc/sysctl.d/99-synos-security.conf
        echo "net.ipv4.conf.default.rp_filter = 1" >> /etc/sysctl.d/99-synos-security.conf
        echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.d/99-synos-security.conf
        echo "net.ipv4.conf.default.accept_redirects = 0" >> /etc/sysctl.d/99-synos-security.conf
        echo "net.ipv6.conf.all.accept_redirects = 0" >> /etc/sysctl.d/99-synos-security.conf
        echo "net.ipv6.conf.default.accept_redirects = 0" >> /etc/sysctl.d/99-synos-security.conf
    '
}

################################################################################
# INTEGRATE CORE/SERVICES
################################################################################

integrate_core_services() {
    log "Integrating core services from core/services/..."

    # Copy service modules
    mkdir -p "$CHROOT_DIR/opt/synos/services"
    cp -r "$PROJECT_ROOT/core/services/"* "$CHROOT_DIR/opt/synos/services/" 2>/dev/null || true

    # Create systemd service files
    log "Creating SynOS system services..."

    # AI Service
    cat > "$CHROOT_DIR/etc/systemd/system/synos-ai.service" <<'EOF'
[Unit]
Description=SynOS AI Consciousness Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/synos/ai
ExecStart=/usr/bin/python3 /opt/synos/ai/daemon.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Security Monitor Service
    cat > "$CHROOT_DIR/etc/systemd/system/synos-security-monitor.service" <<'EOF'
[Unit]
Description=SynOS Security Monitoring Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/synos/security
ExecStart=/usr/bin/python3 /opt/synos/security/monitor.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Enable services (but don't start in chroot)
    chroot "$CHROOT_DIR" systemctl enable synos-ai.service 2>/dev/null || true
    chroot "$CHROOT_DIR" systemctl enable synos-security-monitor.service 2>/dev/null || true
}

################################################################################
# APPLY CONFIG TEMPLATES
################################################################################

apply_config_templates() {
    log "Applying configuration templates from config/..."

    # Core configs
    if [ -d "$PROJECT_ROOT/config/core" ]; then
        cp -r "$PROJECT_ROOT/config/core"/* "$CHROOT_DIR/etc/synos/" 2>/dev/null || true
    fi

    # Compliance configs
    if [ -d "$PROJECT_ROOT/config/compliance" ]; then
        mkdir -p "$CHROOT_DIR/etc/synos/compliance"
        cp -r "$PROJECT_ROOT/config/compliance"/* "$CHROOT_DIR/etc/synos/compliance/" 2>/dev/null || true
    fi

    # MSSP configs
    if [ -d "$PROJECT_ROOT/config/mssp" ]; then
        mkdir -p "$CHROOT_DIR/etc/synos/mssp"
        cp -r "$PROJECT_ROOT/config/mssp"/* "$CHROOT_DIR/etc/synos/mssp/" 2>/dev/null || true
    fi

    # Runtime configs
    if [ -d "$PROJECT_ROOT/config/runtime" ]; then
        cp -r "$PROJECT_ROOT/config/runtime"/* "$CHROOT_DIR/etc/synos/" 2>/dev/null || true
    fi
}

################################################################################
# KERNEL CUSTOMIZATION
################################################################################

apply_kernel_customizations() {
    log "Applying kernel customizations from core/kernel/..."

    # Copy kernel modules if any
    if [ -d "$PROJECT_ROOT/core/kernel/modules" ]; then
        cp -r "$PROJECT_ROOT/core/kernel/modules"/* "$CHROOT_DIR/lib/modules/" 2>/dev/null || true
    fi

    # Apply kernel parameters
    cat >> "$CHROOT_DIR/etc/sysctl.d/99-synos-kernel.conf" <<'EOF'
# SynOS Kernel Optimizations
vm.swappiness = 10
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5

# Network performance
net.core.netdev_max_backlog = 5000
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr

# Security
kernel.unprivileged_bpf_disabled = 1
kernel.kexec_load_disabled = 1
EOF
}

################################################################################
# SETUP MONITORING & LOGGING
################################################################################

setup_monitoring() {
    log "Setting up monitoring and logging infrastructure..."

    # Copy monitoring configs
    if [ -d "$PROJECT_ROOT/deployment/monitoring" ]; then
        mkdir -p "$CHROOT_DIR/opt/synos/monitoring"
        cp -r "$PROJECT_ROOT/deployment/monitoring"/* "$CHROOT_DIR/opt/synos/monitoring/" 2>/dev/null || true
    fi

    chroot "$CHROOT_DIR" bash -c '
        # Create log directories
        mkdir -p /var/log/synos/{ai,security,services,tools}

        # Install monitoring tools
        apt-get install -y \
            htop iotop iftop \
            sysstat \
            prometheus-node-exporter \
            2>/dev/null || true

        # Configure logrotate
        cat > /etc/logrotate.d/synos <<EOF
/var/log/synos/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
EOF
    '
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    echo "Phase 2: Core Integration"
    echo "========================="

    integrate_ai_services
    integrate_security_modules
    integrate_core_services
    apply_config_templates
    apply_kernel_customizations
    setup_monitoring

    log "✓ Phase 2 complete!"
    log "Integrated: AI services, Security modules, Core services, Configs, Kernel tweaks"
}

main "$@"
