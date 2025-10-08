#!/bin/bash
# Package SynOS AI Services as Debian packages
# This script creates .deb packages for the 4 compiled AI services

# Removed set -e to allow script to continue on errors

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGES_DIR="$PROJECT_ROOT/linux-distribution/SynOS-Packages"
BUILD_DIR="$PROJECT_ROOT/target/release"
VERSION="1.0.0"
ARCH="amd64"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SynOS AI Services Packaging Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Services to package
SERVICES=(
    "synos-ai-daemon:SynOS AI Daemon - Core AI Consciousness and Orchestration Engine"
    "synos-consciousness-daemon:SynOS Consciousness Daemon - Neural Darwinism AI Engine"
    "synos-security-orchestrator:SynOS Security Orchestrator - AI-Powered Security Tool Management"
    "synos-hardware-accel:SynOS Hardware Accelerator - GPU/NPU/TPU Management for AI"
    "synos-llm-engine:SynOS LLM Engine - Local Language Model Inference API"
)

# Function to create package structure
create_package() {
    local service_name=$1
    local description=$2
    local pkg_dir="$PACKAGES_DIR/${service_name}_${VERSION}_${ARCH}"

    echo -e "${BLUE}Creating package: ${service_name}${NC}"

    # Clean old package dir
    rm -rf "$pkg_dir"

    # Create directory structure
    mkdir -p "$pkg_dir/DEBIAN"
    mkdir -p "$pkg_dir/usr/bin"
    mkdir -p "$pkg_dir/lib/systemd/system"
    mkdir -p "$pkg_dir/etc/synos"
    mkdir -p "$pkg_dir/var/log/synos"

    # Copy binary
    if [ ! -f "$BUILD_DIR/$service_name" ]; then
        echo -e "${RED}ERROR: Binary not found: $BUILD_DIR/$service_name${NC}"
        return 1
    fi

    cp "$BUILD_DIR/$service_name" "$pkg_dir/usr/bin/"
    chmod 755 "$pkg_dir/usr/bin/$service_name"

    # Create control file
    cat > "$pkg_dir/DEBIAN/control" <<EOF
Package: $service_name
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: SynOS Team <dev@synos.io>
Description: $description
 Part of the SynOS AI-powered operating system.
 This service provides critical AI functionality for the system.
Depends: libc6 (>= 2.31), libssl3 (>= 3.0.0)
EOF

    # Create systemd service file
    cat > "$pkg_dir/lib/systemd/system/${service_name}.service" <<EOF
[Unit]
Description=$description
After=network.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/$service_name
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$service_name

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/synos

[Install]
WantedBy=multi-user.target
EOF

    # Create postinst script
    cat > "$pkg_dir/DEBIAN/postinst" <<EOF
#!/bin/bash
set -e

# Create log directory
mkdir -p /var/log/synos
chmod 755 /var/log/synos

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable $service_name.service

echo "Service $service_name installed successfully"
echo "Start with: sudo systemctl start $service_name"

exit 0
EOF
    chmod 755 "$pkg_dir/DEBIAN/postinst"

    # Create prerm script
    cat > "$pkg_dir/DEBIAN/prerm" <<EOF
#!/bin/bash
set -e

# Stop and disable service
systemctl stop $service_name.service 2>/dev/null || true
systemctl disable $service_name.service 2>/dev/null || true

exit 0
EOF
    chmod 755 "$pkg_dir/DEBIAN/prerm"

    # Build the package
    echo -e "${BLUE}Building package...${NC}"
    (cd "$PACKAGES_DIR" && dpkg-deb --build "$(basename "$pkg_dir")")

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Package created: ${service_name}_${VERSION}_${ARCH}.deb${NC}"

        # Get package size
        local pkg_file="${service_name}_${VERSION}_${ARCH}.deb"
        if [ -f "$PACKAGES_DIR/$pkg_file" ]; then
            local size
            size=$(du -h "$PACKAGES_DIR/$pkg_file" | cut -f1)
            echo -e "${GREEN}  Size: $size${NC}"
        fi

        # Clean up build dir
        rm -rf "$pkg_dir"

        return 0
    else
        echo -e "${RED}✗ Failed to create package: $service_name${NC}"
        return 1
    fi
}

# Main packaging loop
SUCCESS_COUNT=0
FAIL_COUNT=0

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name description <<< "$service_info"
    echo ""

    if create_package "$service_name" "$description"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
done

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Packaging Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successfully packaged: $SUCCESS_COUNT${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}Failed: $FAIL_COUNT${NC}"
fi
echo ""

# List created packages
echo -e "${BLUE}Created packages:${NC}"
ls -lh "$PACKAGES_DIR"/*.deb 2>/dev/null || echo "No packages found"

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
echo "To install a package:"
echo "  sudo dpkg -i $PACKAGES_DIR/<package-name>.deb"
echo ""
echo "To install all packages:"
echo "  sudo dpkg -i $PACKAGES_DIR/*.deb"

exit 0
