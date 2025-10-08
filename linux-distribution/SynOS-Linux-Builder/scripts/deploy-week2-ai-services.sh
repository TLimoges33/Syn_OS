#!/bin/bash

# SynOS Week 2 AI Services Deployment Script
# Deploys all AI consciousness framework components to the filesystem

set -e

FILESYSTEM_ROOT="/home/diablorain/Syn_OS/SynOS-Linux-Builder/filesystem-extract"
PACKAGES_DIR="/home/diablorain/Syn_OS/SynOS-Packages"
SCRIPT_DIR="$(dirname "$0")"

echo "🚀 Deploying SynOS Week 2 AI Services to Filesystem..."

# Check if filesystem exists
if [ ! -d "$FILESYSTEM_ROOT" ]; then
    echo "❌ Filesystem not found at $FILESYSTEM_ROOT"
    exit 1
fi

echo "📁 Target filesystem: $FILESYSTEM_ROOT"

echo "🧠 Phase 1: Deploying AI Consciousness Daemon..."

# Create system directories
mkdir -p "$FILESYSTEM_ROOT/usr/lib/synos"
mkdir -p "$FILESYSTEM_ROOT/etc/synos"
mkdir -p "$FILESYSTEM_ROOT/var/lib/synos"
mkdir -p "$FILESYSTEM_ROOT/var/log"
mkdir -p "$FILESYSTEM_ROOT/usr/share/synos"

# Deploy AI daemon
cp "$PACKAGES_DIR/synos-ai-daemon/src/synos_ai_daemon.py" "$FILESYSTEM_ROOT/usr/lib/synos/"
chmod +x "$FILESYSTEM_ROOT/usr/lib/synos/synos_ai_daemon.py"

# Deploy daemon configuration
cp "$PACKAGES_DIR/synos-ai-daemon/config/ai-daemon.yml" "$FILESYSTEM_ROOT/etc/synos/"

# Deploy systemd service
mkdir -p "$FILESYSTEM_ROOT/etc/systemd/system"
cp "$PACKAGES_DIR/synos-ai-daemon/debian/synos-ai-daemon.service" "$FILESYSTEM_ROOT/etc/systemd/system/"

echo "🔗 Phase 2: Deploying NATS Message Bus Integration..."

# Deploy NATS integration
cp "$PACKAGES_DIR/synos-neural-darwinism/src/nats_integration.py" "$FILESYSTEM_ROOT/usr/lib/synos/"

# Create NATS configuration
mkdir -p "$FILESYSTEM_ROOT/etc/nats"
cat > "$FILESYSTEM_ROOT/etc/nats/nats-server.conf" << 'EOF'
# SynOS NATS Server Configuration
# High-performance messaging for AI consciousness framework

port: 4222
http_port: 8222

# Authentication (for production)
# authorization {
#   user: "synos"
#   password: "$2a$11$T0qiAUC7QgZRG7FBG5LdCe.8w5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Zu"
# }

# Clustering for high availability
cluster {
  name: "synos-cluster"
  listen: 0.0.0.0:6222
  routes = [
    nats-route://127.0.0.1:6222
  ]
}

# Monitoring
monitor_port: 8222

# Logging
log_file: "/var/log/nats-server.log"
debug: false
trace: false
logtime: true

# Limits
max_connections: 1000
max_control_line: 4096
max_payload: 1048576
max_pending: 67108864
max_subscriptions: 0

# Performance tuning
write_deadline: "2s"
max_closed_clients: 500

# JetStream for persistence (if needed)
jetstream {
  store_dir: "/var/lib/nats"
  max_memory_store: 256MB
  max_file_store: 2GB
}
EOF

# Create NATS systemd service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/nats-server.service" << 'EOF'
[Unit]
Description=NATS Server
Documentation=https://docs.nats.io/
After=network.target
Wants=network.target

[Service]
Type=simple
User=nats
Group=nats
ExecStart=/usr/bin/nats-server -c /etc/nats/nats-server.conf
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/nats /var/log
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Resource limits
LimitNOFILE=65536
MemoryAccounting=true
MemoryMax=256M

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 Phase 3: Deploying AI Dashboard Web Interface..."

# Deploy dashboard application
mkdir -p "$FILESYSTEM_ROOT/usr/lib/synos/dashboard"
mkdir -p "$FILESYSTEM_ROOT/usr/share/synos/dashboard/templates"
mkdir -p "$FILESYSTEM_ROOT/usr/share/synos/dashboard/static"

cp "$PACKAGES_DIR/synos-ai-dashboard/src/dashboard.py" "$FILESYSTEM_ROOT/usr/lib/synos/dashboard/"
chmod +x "$FILESYSTEM_ROOT/usr/lib/synos/dashboard/dashboard.py"

# Create dashboard HTML template
cat > "$FILESYSTEM_ROOT/usr/share/synos/dashboard/templates/dashboard.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SynOS AI Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #e0e0e0;
            font-family: 'Liberation Sans', sans-serif;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #00ffff;
            font-size: 2.5rem;
            margin: 0;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #00ffff44;
            border-radius: 10px;
            padding: 20px;
        }
        .status-card h3 {
            color: #00ffff;
            margin-top: 0;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }
        .metric-value {
            font-weight: bold;
            color: #ffffff;
        }
        .chart-container {
            background: rgba(26, 26, 46, 0.8);
            border: 1px solid #00ffff44;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 SynOS AI Consciousness Dashboard</h1>
        <p>Neural Darwinism • Real-time AI Monitoring • System Integration</p>
    </div>

    <div class="status-grid">
        <div class="status-card">
            <h3>🧠 Consciousness State</h3>
            <div class="metric">
                <span>Awareness Level:</span>
                <span class="metric-value" id="awareness-level">--</span>
            </div>
            <div class="metric">
                <span>Neural Activity:</span>
                <span class="metric-value" id="neural-activity">--</span>
            </div>
        </div>
    </div>

    <script>
        console.log('SynOS AI Dashboard loaded');
    </script>
</body>
</html>
EOF

# Create dashboard systemd service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-dashboard.service" << 'EOF'
[Unit]
Description=SynOS AI Dashboard Web Interface
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service nats-server.service
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/usr/lib/synos/dashboard
ExecStart=/usr/bin/python3 /usr/lib/synos/dashboard/dashboard.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log /tmp
PrivateTmp=true

# Resource limits
MemoryAccounting=true
MemoryMax=128M

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

echo "💻 Phase 4: Deploying CLI Tools..."

# Deploy synctl command
mkdir -p "$FILESYSTEM_ROOT/usr/bin"
cp "$PACKAGES_DIR/synos-cli-tools/src/synctl" "$FILESYSTEM_ROOT/usr/bin/"
chmod +x "$FILESYSTEM_ROOT/usr/bin/synctl"

# Create bash completion for synctl
mkdir -p "$FILESYSTEM_ROOT/etc/bash_completion.d"
cat > "$FILESYSTEM_ROOT/etc/bash_completion.d/synctl" << 'EOF'
# SynOS synctl bash completion

_synctl_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="status monitor neural learning security config services logs"

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "--help" -- ${cur}) )
        return 0
    fi

    case "${prev}" in
        synctl)
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        services)
            COMPREPLY=( $(compgen -W "start stop restart status" -- ${cur}) )
            return 0
            ;;
        config)
            COMPREPLY=( $(compgen -W "--show --edit --validate" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
}

complete -F _synctl_completions synctl
EOF

echo "🤖 Phase 5: Deploying TensorFlow Lite Integration..."

# Deploy TensorFlow Lite integration
cp "$PACKAGES_DIR/synos-tensorflow-lite/src/tf_lite_integration.py" "$FILESYSTEM_ROOT/usr/lib/synos/"

# Create model directories
mkdir -p "$FILESYSTEM_ROOT/usr/share/synos/models"
mkdir -p "$FILESYSTEM_ROOT/etc/synos"

# Create model hash configuration file
cat > "$FILESYSTEM_ROOT/etc/synos/model-hashes.json" << 'EOF'
{
  "consciousness_patterns.tflite": "placeholder_hash_for_consciousness_model",
  "threat_classifier.tflite": "placeholder_hash_for_threat_model"
}
EOF

echo "👥 Phase 6: Creating System Users and Groups..."

# Create synos-ai user for daemon
cat >> "$FILESYSTEM_ROOT/etc/passwd" << 'EOF'
synos-ai:x:999:999:SynOS AI Daemon:/var/lib/synos:/usr/sbin/nologin
EOF

cat >> "$FILESYSTEM_ROOT/etc/group" << 'EOF'
synos-ai:x:999:
EOF

# Create nats user for NATS server
cat >> "$FILESYSTEM_ROOT/etc/passwd" << 'EOF'
nats:x:998:998:NATS Server:/var/lib/nats:/usr/sbin/nologin
EOF

cat >> "$FILESYSTEM_ROOT/etc/group" << 'EOF'
nats:x:998:
EOF

# Set up directories and permissions
mkdir -p "$FILESYSTEM_ROOT/var/lib/synos"
mkdir -p "$FILESYSTEM_ROOT/var/lib/nats"
mkdir -p "$FILESYSTEM_ROOT/var/log"

# Note: Actual chown operations would be done during live system boot

echo "⚙️  Phase 7: Configuring AI Services Integration..."

# Create AI services configuration directory
mkdir -p "$FILESYSTEM_ROOT/etc/synos/services.d"

# Create service orchestration configuration
cat > "$FILESYSTEM_ROOT/etc/synos/services.d/ai-orchestration.conf" << 'EOF'
# SynOS AI Services Orchestration Configuration

[services]
# Core AI services in startup order
core_services = [
    "nats-server",
    "synos-ai-daemon",
    "synos-dashboard"
]

# Optional AI enhancement services
enhancement_services = [
    "synos-security-orchestrator",
    "synos-ml-inference"
]

[monitoring]
# Health check intervals (seconds)
health_check_interval = 30

# Service restart policies
restart_policy = "always"
restart_delay = 10

# Resource monitoring
monitor_memory = true
monitor_cpu = true
memory_threshold = 80  # percent
cpu_threshold = 70     # percent

[consciousness]
# Consciousness framework settings
enable_consciousness = true
consciousness_update_interval = 1.0
neural_darwinism_enabled = true
learning_engine_enabled = true

# Integration with system services
integrate_with_systemd = true
integrate_with_dbus = true
integrate_with_networkmanager = true
EOF

# Create systemd target for SynOS AI services
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-ai.target" << 'EOF'
[Unit]
Description=SynOS AI Consciousness Framework
Documentation=https://github.com/FranklineMisango/Syn_OS
After=multi-user.target
Wants=multi-user.target

[Install]
WantedBy=multi-user.target
EOF

# Create AI services dependency file
mkdir -p "$FILESYSTEM_ROOT/etc/systemd/system/synos-ai.target.wants"
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-ai.target.wants/.gitkeep" << 'EOF'
# This directory contains symlinks to AI services that should start with the AI framework
EOF

echo "🔧 Phase 8: Setting up Desktop Integration..."

# Update the existing AI Control Center desktop file
cat > "$FILESYSTEM_ROOT/usr/share/applications/synos-ai-control-enhanced.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS AI Control Center
GenericName=AI Consciousness Management
Comment=Comprehensive SynOS AI consciousness framework control panel
Icon=synos
Exec=synos-ai-control
Terminal=false
Categories=System;Settings;
Keywords=AI;consciousness;neural;darwinism;tensorflow;
StartupNotify=true
EOF

# Create desktop shortcut for dashboard
cat > "$FILESYSTEM_ROOT/usr/share/applications/synos-dashboard.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS AI Dashboard
GenericName=AI Monitoring Dashboard
Comment=Real-time SynOS AI consciousness monitoring web interface
Icon=synos
Exec=x-www-browser http://localhost:8080
Terminal=false
Categories=System;Monitor;
Keywords=AI;dashboard;monitoring;consciousness;
StartupNotify=true
EOF

# Create menu entry for synctl terminal
cat > "$FILESYSTEM_ROOT/usr/share/applications/synos-terminal.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS AI Terminal
GenericName=AI Command Terminal
Comment=Command-line interface for SynOS AI consciousness framework
Icon=utilities-terminal
Exec=mate-terminal -e "synctl monitor"
Terminal=false
Categories=System;TerminalEmulator;
Keywords=AI;terminal;synctl;consciousness;
StartupNotify=true
EOF

echo "🚀 Phase 9: Creating Startup Scripts..."

# Create AI services initialization script
mkdir -p "$FILESYSTEM_ROOT/usr/lib/synos/scripts"
cat > "$FILESYSTEM_ROOT/usr/lib/synos/scripts/initialize-ai-services.sh" << 'EOF'
#!/bin/bash

# SynOS AI Services Initialization Script
# Ensures proper startup of AI consciousness framework

LOG_FILE="/var/log/synos-ai-init.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [AI-INIT] $1" >> "$LOG_FILE"
    echo "$1"
}

log "Starting SynOS AI services initialization..."

# Create required directories
mkdir -p /var/lib/synos /var/lib/nats /var/log
chown synos-ai:synos-ai /var/lib/synos
chown nats:nats /var/lib/nats

# Set proper permissions
chmod 755 /usr/lib/synos/*.py
chmod 755 /usr/bin/synctl
chmod 644 /etc/synos/*.yml
chmod 644 /etc/synos/*.json
chmod 644 /etc/systemd/system/synos-*.service

# Enable AI services
systemctl daemon-reload
systemctl enable nats-server.service
systemctl enable synos-ai-daemon.service
systemctl enable synos-dashboard.service

# Start services in order
log "Starting NATS message bus..."
systemctl start nats-server.service

sleep 3

log "Starting SynOS AI daemon..."
systemctl start synos-ai-daemon.service

sleep 2

log "Starting SynOS dashboard..."
systemctl start synos-dashboard.service

log "SynOS AI services initialization complete"

# Display status
synctl status
EOF

chmod +x "$FILESYSTEM_ROOT/usr/lib/synos/scripts/initialize-ai-services.sh"

# Create systemd service for initialization
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-ai-init.service" << 'EOF'
[Unit]
Description=SynOS AI Services Initialization
After=network.target
Before=synos-ai.target
DefaultDependencies=no

[Service]
Type=oneshot
ExecStart=/usr/lib/synos/scripts/initialize-ai-services.sh
RemainAfterExit=yes
TimeoutSec=60

[Install]
WantedBy=multi-user.target
EOF

echo "🎯 Phase 10: Final Integration and Verification..."

# Create system integration verification script
cat > "$FILESYSTEM_ROOT/usr/bin/synos-verify-ai" << 'EOF'
#!/bin/bash

# SynOS AI Framework Verification Tool

echo "🧠 SynOS AI Framework Verification"
echo "=================================="

# Check core files
echo "📁 Checking core files..."
FILES=(
    "/usr/lib/synos/synos_ai_daemon.py"
    "/usr/lib/synos/nats_integration.py"
    "/usr/lib/synos/tf_lite_integration.py"
    "/usr/bin/synctl"
    "/etc/synos/ai-daemon.yml"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
    fi
done

# Check services
echo "⚙️ Checking systemd services..."
SERVICES=(
    "nats-server.service"
    "synos-ai-daemon.service"
    "synos-dashboard.service"
)

for service in "${SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "$service"; then
        echo "  ✓ $service"
    else
        echo "  ✗ $service (NOT FOUND)"
    fi
done

# Check users
echo "👥 Checking system users..."
USERS=("synos-ai" "nats")

for user in "${USERS[@]}"; do
    if id "$user" &>/dev/null; then
        echo "  ✓ User $user exists"
    else
        echo "  ✗ User $user missing"
    fi
done

# Check directories
echo "📂 Checking directories..."
DIRS=(
    "/var/lib/synos"
    "/var/lib/nats"
    "/etc/synos"
    "/usr/share/synos"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir (MISSING)"
    fi
done

echo ""
echo "🎯 Verification complete. Run 'synctl status' after boot to check AI framework status."
EOF

chmod +x "$FILESYSTEM_ROOT/usr/bin/synos-verify-ai"

# Set file permissions for all deployed files
find "$FILESYSTEM_ROOT/usr/lib/synos" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
find "$FILESYSTEM_ROOT/etc/synos" -name "*.yml" -exec chmod 644 {} \; 2>/dev/null || true
find "$FILESYSTEM_ROOT/etc/systemd/system" -name "synos-*.service" -exec chmod 644 {} \; 2>/dev/null || true

echo "✅ SynOS Week 2 AI Services Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 AI Consciousness Daemon: Deployed with systemd service"
echo "🔗 NATS Message Bus: Configured for AI service communication"
echo "🌐 AI Dashboard: Web interface ready on port 8080"
echo "💻 CLI Tools: synctl command available system-wide"
echo "🤖 TensorFlow Lite: On-device inference framework integrated"
echo "👥 System Users: AI service users created"
echo "⚙️  Services: Systemd services configured and enabled"
echo "🎯 Integration: Desktop and startup integration complete"
echo ""
echo "🚀 Next Steps:"
echo "  1. Boot the SynOS system"
echo "  2. Run: sudo /usr/lib/synos/scripts/initialize-ai-services.sh"
echo "  3. Test with: synctl status"
echo "  4. Open dashboard at: http://localhost:8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"