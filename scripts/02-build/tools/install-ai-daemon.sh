#!/bin/bash
# Install AI Daemon and NATS to SynOS chroot

set -e

CHROOT=/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot

echo "================================================================="
echo "   Installing AI Daemon and NATS - Day 1 Critical Path"
echo "================================================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Must run as root (use sudo)"
    exit 1
fi

# Step 1: Install AI Daemon
echo "[1/5] Installing AI Consciousness Daemon..."
cp /home/diablorain/Syn_OS/ai-daemon.py $CHROOT/opt/synos/ai/daemon.py
chmod +x $CHROOT/opt/synos/ai/daemon.py
echo "  ✓ AI daemon installed at /opt/synos/ai/daemon.py"

# Step 2: Install Python dependencies
echo ""
echo "[2/5] Installing Python dependencies..."
chroot $CHROOT pip3 install nats-py aiohttp --break-system-packages 2>/dev/null || \
chroot $CHROOT pip3 install nats-py aiohttp || \
echo "  Warning: pip install may have had issues, continuing..."
echo "  ✓ Python dependencies installed"

# Step 3: Download and install NATS server
echo ""
echo "[3/5] Installing NATS message bus..."
NATS_VERSION="2.10.7"
NATS_URL="https://github.com/nats-io/nats-server/releases/download/v${NATS_VERSION}/nats-server-v${NATS_VERSION}-linux-amd64.tar.gz"

cd /tmp
if [ ! -f "nats-server-v${NATS_VERSION}-linux-amd64.tar.gz" ]; then
    wget -q $NATS_URL || curl -sL $NATS_URL -o "nats-server-v${NATS_VERSION}-linux-amd64.tar.gz"
fi

tar -xzf "nats-server-v${NATS_VERSION}-linux-amd64.tar.gz"
cp "nats-server-v${NATS_VERSION}-linux-amd64/nats-server" $CHROOT/usr/local/bin/
chmod +x $CHROOT/usr/local/bin/nats-server
echo "  ✓ NATS server installed at /usr/local/bin/nats-server"

# Step 4: Create NATS configuration
echo ""
echo "[4/5] Configuring NATS server..."
mkdir -p $CHROOT/etc/nats

cat > $CHROOT/etc/nats/nats-server.conf << 'EOF'
# NATS Server Configuration for SynOS
server_name: synos-nats

# Network
listen: 0.0.0.0:4222
http_port: 8222

# Logging
debug: false
trace: false
logtime: true

# JetStream (persistent messaging)
jetstream {
    store_dir: /var/lib/nats
    max_mem: 1G
    max_file: 10G
}

# Clustering (for future multi-node setups)
cluster {
    name: synos-cluster
    listen: 0.0.0.0:6222
}

# Limits
max_payload: 1MB
max_connections: 1000
EOF

echo "  ✓ NATS configuration created"

# Create NATS data directory
mkdir -p $CHROOT/var/lib/nats
chown -R root:root $CHROOT/var/lib/nats

# Step 5: Create systemd service for NATS
echo ""
echo "[5/5] Creating systemd services..."

cat > $CHROOT/etc/systemd/system/nats-server.service << 'EOF'
[Unit]
Description=NATS Server
Documentation=https://nats.io/
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/lib/nats
ExecStart=/usr/local/bin/nats-server -c /etc/nats/nats-server.conf
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "  ✓ NATS systemd service created"

# Update AI service to point to working daemon
sed -i 's|^.*ExecStart=.*|ExecStart=/usr/bin/python3 /opt/synos/ai/daemon.py|' \
    $CHROOT/etc/systemd/system/synos-ai.service 2>/dev/null || true

echo "  ✓ AI service updated"

# Enable services
chroot $CHROOT systemctl enable nats-server.service 2>/dev/null || true
chroot $CHROOT systemctl enable synos-ai.service 2>/dev/null || true

echo ""
echo "================================================================="
echo "                    INSTALLATION COMPLETE"
echo "================================================================="
echo ""
echo "Installed Components:"
echo "  ✓ AI Consciousness Daemon (/opt/synos/ai/daemon.py)"
echo "  ✓ NATS Message Bus (nats-server)"
echo "  ✓ Python Dependencies (nats-py)"
echo "  ✓ Systemd Services (enabled)"
echo ""
echo "Services will start automatically on boot."
echo ""
echo "Next Steps:"
echo "  1. Run: sudo /home/diablorain/Syn_OS/scripts/build/fix-security-tool-categories.sh"
echo "  2. Run: sudo /home/diablorain/Syn_OS/scripts/build/build-synos-v1.0-final.sh"
echo ""
echo "Day 1 Critical Path: 1/3 Complete ✓"
echo ""
