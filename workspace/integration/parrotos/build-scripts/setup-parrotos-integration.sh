#!/bin/bash

# SynapticOS ParrotOS Integration Script
# Downloads and prepares ParrotOS base for consciousness integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                SYNAPTICOS PARROTOS INTEGRATION              ║${NC}"
echo -e "${PURPLE}║         Building Consciousness-Enhanced Linux Distribution   ║${NC}"
echo -e "${PURPLE}║                                                              ║${NC}"
echo -e "${PURPLE}║  🧠 Consciousness Integration  🔒 ParrotOS Security         ║${NC}"
echo -e "${PURPLE}║  🎓 Educational Framework     ⚡ Real OS Distribution       ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INTEGRATION_DIR="${PROJECT_ROOT}/parrotos-integration"
BASE_DIR="${INTEGRATION_DIR}/base"
OVERLAY_DIR="${INTEGRATION_DIR}/overlay"
BUILD_DIR="${INTEGRATION_DIR}/build-scripts"

# Configuration
PARROTOS_VERSION="6.4"
PARROTOS_EDITION="Security"
PARROTOS_ARCH="amd64"
PARROTOS_ISO_NAME="Parrot-security-${PARROTOS_VERSION}_${PARROTOS_ARCH}.iso"
PARROTOS_DOWNLOAD_URL="https://mirrors.parrotsec.org/parrot/iso/${PARROTOS_VERSION}/${PARROTOS_ISO_NAME}"
PARROTOS_ISO="${BASE_DIR}/${PARROTOS_ISO_NAME}"

echo -e "${BLUE}[INFO]${NC} SynapticOS ParrotOS Integration Setup"
echo -e "${BLUE}[INFO]${NC} Base: ParrotOS ${PARROTOS_VERSION} ${PARROTOS_EDITION} Edition"
echo -e "${BLUE}[INFO]${NC} Target: SynapticOS with Consciousness Integration"
echo -e "${BLUE}[INFO]${NC} Expected ISO size: ~5.4GB"

# Create necessary directories
mkdir -p "$BASE_DIR" "$OVERLAY_DIR"

# Step 1: Download ParrotOS if not already present
echo -e "${CYAN}[1/6]${NC} Checking ParrotOS base system"
if [ ! -f "$PARROTOS_ISO" ]; then
    log_info "Downloading ParrotOS 6.4..."
    # Try multiple mirrors with SSL verification disabled for CI/automation
        DOWNLOAD_URLS=(
            "https://mirrors.parrotsec.org/parrot/iso/6.4/Parrot-security-6.4_amd64.iso"
            "https://archive.parrotsec.org/parrot/iso/6.4/Parrot-security-6.4_amd64.iso"
            "https://deb.parrot.sh/parrot/iso/6.4/Parrot-security-6.4_amd64.iso"
        )
        
        DOWNLOAD_SUCCESS=false
        for url in "${DOWNLOAD_URLS[@]}"; do
            log_info "Trying download from: $url"
            if wget --no-check-certificate --progress=bar:force:noscroll -O "$PARROTOS_ISO" "$url" 2>&1; then
                if [ -f "$PARROTOS_ISO" ] && [ $(stat -f%z "$PARROTOS_ISO" 2>/dev/null || stat -c%s "$PARROTOS_ISO" 2>/dev/null || echo 0) -gt 1000000000 ]; then
                    log_success "ParrotOS ISO downloaded successfully"
                    DOWNLOAD_SUCCESS=true
                    break
                else
                    log_warning "Download appeared successful but file is too small, trying next mirror..."
                    rm -f "$PARROTOS_ISO"
                fi
            else
                log_warning "Download failed from $url, trying next mirror..."
                rm -f "$PARROTOS_ISO"
            fi
        done
        
        if [ "$DOWNLOAD_SUCCESS" = false ]; then
            log_error "Failed to download ParrotOS from all mirrors"
            log_info "Please manually download Parrot-security-6.4_amd64.iso to: $PARROTOS_ISO"
            exit 1
        fi
    else
        log_success "ParrotOS ISO already exists: $PARROTOS_ISO"
    fi

# Step 2: Extract ISO contents
echo -e "${CYAN}[2/6]${NC} Extracting ParrotOS filesystem"
ISO_MOUNT="${BASE_DIR}/iso_mount"
ISO_EXTRACT="${BASE_DIR}/iso_contents"

mkdir -p "${ISO_MOUNT}" "${ISO_EXTRACT}"

# Mount ISO and extract contents
sudo mount -o loop "${PARROTOS_ISO}" "${ISO_MOUNT}"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[MOUNTED]${NC} ParrotOS ISO mounted at ${ISO_MOUNT}"
    
    # Copy all contents
    sudo cp -r "${ISO_MOUNT}"/* "${ISO_EXTRACT}/" 2>/dev/null || true
    sudo cp -r "${ISO_MOUNT}"/.[^.]* "${ISO_EXTRACT}/" 2>/dev/null || true
    
    # Unmount
    sudo umount "${ISO_MOUNT}"
    echo -e "${GREEN}[EXTRACTED]${NC} ParrotOS contents extracted to ${ISO_EXTRACT}"
else
    echo -e "${RED}[ERROR]${NC} Failed to mount ParrotOS ISO"
    exit 1
fi

# Step 3: Create SynapticOS overlay structure
echo -e "${CYAN}[3/6]${NC} Creating SynapticOS overlay structure"
mkdir -p "${OVERLAY_DIR}"/{services,kernel-mods,systemd-services,desktop-integration,package-configs,consciousness-configs}

# Copy our existing services to overlay
echo -e "${YELLOW}[COPY]${NC} Copying consciousness services to overlay..."
cp -r "${PROJECT_ROOT}/services" "${OVERLAY_DIR}/"

# Create systemd service files
echo -e "${CYAN}[4/6]${NC} Creating systemd service configurations"
cat > "${OVERLAY_DIR}/systemd-services/synapticos-consciousness-bridge.service" << 'EOF'
[Unit]
Description=SynapticOS Consciousness AI Bridge
After=network.target
Wants=postgresql.service redis.service

[Service]
Type=simple
User=synapticos
Group=synapticos
WorkingDirectory=/opt/synapticos/services/consciousness-ai-bridge
ExecStart=/usr/bin/python3 consciousness_bridge.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/synapticos/services/consciousness-ai-bridge

[Install]
WantedBy=multi-user.target
EOF

cat > "${OVERLAY_DIR}/systemd-services/synapticos-educational-platform.service" << 'EOF'
[Unit]
Description=SynapticOS Educational Platform
After=network.target synapticos-consciousness-bridge.service
Requires=synapticos-consciousness-bridge.service

[Service]
Type=simple
User=synapticos
Group=synapticos
WorkingDirectory=/opt/synapticos/services/educational-platform
ExecStart=/usr/bin/python3 educational_platform.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/synapticos/services/educational-platform

[Install]
WantedBy=multi-user.target
EOF

cat > "${OVERLAY_DIR}/systemd-services/synapticos-ctf-platform.service" << 'EOF'
[Unit]
Description=SynapticOS CTF Platform
After=network.target synapticos-consciousness-bridge.service
Requires=synapticos-consciousness-bridge.service

[Service]
Type=simple
User=synapticos
Group=synapticos
WorkingDirectory=/opt/synapticos/services/ctf-platform
ExecStart=/usr/bin/python3 ctf_platform.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/synapticos/services/ctf-platform

[Install]
WantedBy=multi-user.target
EOF

cat > "${OVERLAY_DIR}/systemd-services/synapticos-news-intelligence.service" << 'EOF'
[Unit]
Description=SynapticOS News Intelligence Platform
After=network.target synapticos-consciousness-bridge.service
Requires=synapticos-consciousness-bridge.service

[Service]
Type=simple
User=synapticos
Group=synapticos
WorkingDirectory=/opt/synapticos/services/news-intelligence
ExecStart=/usr/bin/python3 news_intelligence.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/synapticos/services/news-intelligence

[Install]
WantedBy=multi-user.target
EOF

cat > "${OVERLAY_DIR}/systemd-services/synapticos-context-engine.service" << 'EOF'
[Unit]
Description=SynapticOS Advanced Context Engine
After=network.target synapticos-consciousness-bridge.service
Requires=synapticos-consciousness-bridge.service

[Service]
Type=simple
User=synapticos
Group=synapticos
WorkingDirectory=/opt/synapticos/services/context-engine
ExecStart=/usr/bin/python3 context_engine.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/synapticos/services/context-engine

[Install]
WantedBy=multi-user.target
EOF

# Create target for all SynapticOS services
cat > "${OVERLAY_DIR}/systemd-services/synapticos-stack.target" << 'EOF'
[Unit]
Description=SynapticOS Consciousness Stack
Requires=synapticos-consciousness-bridge.service
Wants=synapticos-educational-platform.service synapticos-ctf-platform.service synapticos-news-intelligence.service synapticos-context-engine.service
After=network.target

[Install]
WantedBy=multi-user.target
EOF

# Step 5: Create desktop integration files
echo -e "${CYAN}[5/6]${NC} Creating desktop integration"
mkdir -p "${OVERLAY_DIR}/desktop-integration/applications"
mkdir -p "${OVERLAY_DIR}/desktop-integration/autostart"

cat > "${OVERLAY_DIR}/desktop-integration/applications/synapticos-dashboard.desktop" << 'EOF'
[Desktop Entry]
Name=SynapticOS Consciousness Dashboard
Comment=Monitor and control SynapticOS consciousness services
Exec=/usr/bin/chromium-browser http://localhost:8000
Icon=/opt/synapticos/icons/consciousness-dashboard.png
Terminal=false
Type=Application
Categories=Education;Security;Development;
StartupNotify=true
EOF

cat > "${OVERLAY_DIR}/desktop-integration/applications/synapticos-education.desktop" << 'EOF'
[Desktop Entry]
Name=SynapticOS Educational Platform
Comment=AI-powered cybersecurity education with consciousness integration
Exec=/usr/bin/chromium-browser http://localhost:8001
Icon=/opt/synapticos/icons/education-platform.png
Terminal=false
Type=Application
Categories=Education;Security;Development;
StartupNotify=true
EOF

cat > "${OVERLAY_DIR}/desktop-integration/applications/synapticos-ctf.desktop" << 'EOF'
[Desktop Entry]
Name=SynapticOS CTF Platform
Comment=Dynamic cybersecurity challenges with AI consciousness
Exec=/usr/bin/chromium-browser http://localhost:8086
Icon=/opt/synapticos/icons/ctf-platform.png
Terminal=false
Type=Application
Categories=Education;Security;Development;Game;
StartupNotify=true
EOF

# Step 6: Create package configuration
echo -e "${CYAN}[6/6]${NC} Creating package configurations"
cat > "${OVERLAY_DIR}/package-configs/synapticos-packages.list" << 'EOF'
# SynapticOS Additional Packages
python3-fastapi
python3-uvicorn
python3-aiohttp
python3-docker
python3-feedparser
python3-beautifulsoup4
python3-spacy
python3-sklearn
python3-networkx
python3-numpy
python3-pydantic
python3-yaml
redis-server
postgresql-client
chromium-browser

# Development tools for consciousness integration
python3-dev
python3-pip
git
curl
wget
build-essential
EOF

# Create installation summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   SYNAPTICOS PARROTOS INTEGRATION COMPLETE                     ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo
echo -e "${BLUE}📂 Base System:${NC} ${BASE_DIR}/${PARROTOS_ISO}"
echo -e "${BLUE}📂 Extracted:${NC} ${BASE_DIR}/iso_contents"
echo -e "${BLUE}📂 Overlay:${NC} ${OVERLAY_DIR}"
echo -e "${BLUE}🔧 Services:${NC} 5 consciousness services configured"
echo -e "${BLUE}🖥️  Desktop:${NC} 3 desktop applications created"
echo -e "${BLUE}📦 Packages:${NC} Additional package list prepared"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Run: ${CYAN}./build-synapticos-iso.sh${NC} (when available)"
echo -e "  2. Test consciousness integration in VM"
echo -e "  3. Validate educational platform integration"
echo -e "  4. Create final distribution ISO"
echo
echo -e "${GREEN}🎯 Ready for SynapticOS distribution building!${NC}"
