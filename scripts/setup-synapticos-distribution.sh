#!/bin/bash
# SynapticOS Linux Distribution Setup Script
# Creates the foundation for consciousness-aware Linux distribution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 SynapticOS Distribution Setup${NC}"
echo "Building consciousness-aware Linux distribution foundation..."
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   exit 1
fi

# Create system directories
echo -e "${YELLOW}📁 Creating system directories...${NC}"
sudo mkdir -p /opt/synapticos/{bin,lib,share,services}
sudo mkdir -p /var/lib/synapticos/{consciousness,education,security}
sudo mkdir -p /var/log/synapticos
sudo mkdir -p /etc/synapticos

# Create service user
echo -e "${YELLOW}👤 Creating synapticos service user...${NC}"
if ! id "synapticos" &>/dev/null; then
    sudo useradd -r -s /bin/false -d /var/lib/synapticos synapticos
    echo -e "${GREEN}✅ Created synapticos user${NC}"
else
    echo -e "${GREEN}✅ synapticos user already exists${NC}"
fi

# Set proper permissions
echo -e "${YELLOW}🔒 Setting permissions...${NC}"
sudo chown -R synapticos:synapticos /var/lib/synapticos
sudo chown -R synapticos:synapticos /var/log/synapticos
sudo chmod 755 /opt/synapticos
sudo chmod 755 /etc/synapticos

# Install Python dependencies for consciousness services
echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
pip3 install --user aiohttp aiofiles asyncio-nats-client fastapi uvicorn sqlalchemy psycopg2-binary redis

# Copy consciousness services
echo -e "${YELLOW}🧠 Installing consciousness services...${NC}"
sudo cp -r services/consciousness-ai-bridge /opt/synapticos/services/
sudo cp -r services/educational-platform /opt/synapticos/services/

# Install systemd services
echo -e "${YELLOW}⚙️ Installing systemd services...${NC}"
sudo cp services/consciousness-ai-bridge/consciousness-ai-bridge.service /etc/systemd/system/
sudo cp services/educational-platform/educational-platform.service /etc/systemd/system/

# Copy environment files
echo -e "${YELLOW}🔧 Installing configuration files...${NC}"
sudo cp services/consciousness-ai-bridge/consciousness-ai-bridge.env /etc/synapticos/
sudo cp services/educational-platform/educational-platform.env /etc/synapticos/

# Secure environment files
sudo chmod 600 /etc/synapticos/*.env
sudo chown root:synapticos /etc/synapticos/*.env

# Reload systemd
echo -e "${YELLOW}🔄 Reloading systemd...${NC}"
sudo systemctl daemon-reload

# Enable services (but don't start yet)
echo -e "${YELLOW}🚀 Enabling services...${NC}"
sudo systemctl enable consciousness-ai-bridge.service
sudo systemctl enable educational-platform.service

# Create desktop entries for applications
echo -e "${YELLOW}🖥️ Creating desktop entries...${NC}"
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/synapticos-consciousness-monitor.desktop << EOF
[Desktop Entry]
Name=SynapticOS Consciousness Monitor
Comment=Monitor consciousness level and AI integration
Exec=python3 /opt/synapticos/services/consciousness-ai-bridge/monitor.py
Icon=applications-system
Terminal=false
Type=Application
Categories=System;Monitor;
EOF

cat > ~/.local/share/applications/synapticos-learning-hub.desktop << EOF
[Desktop Entry]
Name=SynapticOS Learning Hub
Comment=Educational platform integration and progress tracking
Exec=python3 /opt/synapticos/services/educational-platform/gui.py
Icon=applications-education
Terminal=false
Type=Application
Categories=Education;Development;
EOF

# Install Docker and Docker Compose if not present
echo -e "${YELLOW}🐳 Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Create development environment setup
echo -e "${YELLOW}💻 Setting up development environment...${NC}"
cat > /tmp/synapticos-dev-setup.sh << 'EOF'
#!/bin/bash
# SynapticOS Development Environment

export SYNAPTICOS_HOME="/opt/synapticos"
export SYNAPTICOS_CONFIG="/etc/synapticos"
export SYNAPTICOS_DATA="/var/lib/synapticos"
export SYNAPTICOS_LOGS="/var/log/synapticos"

# Add to PATH
export PATH="$SYNAPTICOS_HOME/bin:$PATH"

# Python path
export PYTHONPATH="$SYNAPTICOS_HOME/lib:$PYTHONPATH"

# Consciousness development functions
consciousness_status() {
    systemctl status consciousness-ai-bridge
}

consciousness_logs() {
    journalctl -u consciousness-ai-bridge -f
}

education_status() {
    systemctl status educational-platform
}

education_logs() {
    journalctl -u educational-platform -f
}

synapticos_start() {
    echo "Starting SynapticOS services..."
    sudo systemctl start consciousness-ai-bridge
    sudo systemctl start educational-platform
    docker-compose up -d
}

synapticos_stop() {
    echo "Stopping SynapticOS services..."
    sudo systemctl stop consciousness-ai-bridge
    sudo systemctl stop educational-platform
    docker-compose down
}

synapticos_status() {
    echo "=== SynapticOS Service Status ==="
    echo "Consciousness AI Bridge:"
    systemctl is-active consciousness-ai-bridge
    echo "Educational Platform:"
    systemctl is-active educational-platform
    echo "Docker Services:"
    docker-compose ps
}

echo "SynapticOS development environment loaded!"
echo "Available commands:"
echo "  synapticos_start    - Start all services"
echo "  synapticos_stop     - Stop all services"
echo "  synapticos_status   - Check service status"
echo "  consciousness_status - Check consciousness service"
echo "  education_status    - Check education service"
EOF

sudo mv /tmp/synapticos-dev-setup.sh /opt/synapticos/bin/synapticos-env
sudo chmod +x /opt/synapticos/bin/synapticos-env

# Add to bashrc
if ! grep -q "synapticos-env" ~/.bashrc; then
    echo "source /opt/synapticos/bin/synapticos-env" >> ~/.bashrc
fi

# Create quick start script
cat > /opt/synapticos/bin/synapticos-quickstart << 'EOF'
#!/bin/bash
# SynapticOS Quick Start

echo "🧠 SynapticOS Quick Start"
echo "========================="
echo

echo "1. Starting consciousness services..."
sudo systemctl start consciousness-ai-bridge
sleep 2

echo "2. Starting educational platform..."
sudo systemctl start educational-platform
sleep 2

echo "3. Starting supporting services..."
docker-compose up -d
sleep 5

echo "4. Checking service status..."
if systemctl is-active --quiet consciousness-ai-bridge; then
    echo "✅ Consciousness AI Bridge: Active"
else
    echo "❌ Consciousness AI Bridge: Failed"
fi

if systemctl is-active --quiet educational-platform; then
    echo "✅ Educational Platform: Active"
else
    echo "❌ Educational Platform: Failed"
fi

echo
echo "🎉 SynapticOS is ready!"
echo "Access the web dashboard at: http://localhost:8086"
echo "Consciousness monitor: http://localhost:8082"
echo "Educational hub: http://localhost:8084"
echo
echo "Use 'synapticos_status' to check services anytime"
EOF

sudo chmod +x /opt/synapticos/bin/synapticos-quickstart

# Create uninstall script
cat > /opt/synapticos/bin/synapticos-uninstall << 'EOF'
#!/bin/bash
# SynapticOS Uninstall

echo "🗑️ SynapticOS Uninstall"
echo "======================"
echo "This will remove all SynapticOS components."
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping services..."
    sudo systemctl stop consciousness-ai-bridge educational-platform
    sudo systemctl disable consciousness-ai-bridge educational-platform
    
    echo "Removing systemd services..."
    sudo rm -f /etc/systemd/system/consciousness-ai-bridge.service
    sudo rm -f /etc/systemd/system/educational-platform.service
    sudo systemctl daemon-reload
    
    echo "Removing files..."
    sudo rm -rf /opt/synapticos
    sudo rm -rf /var/lib/synapticos
    sudo rm -rf /var/log/synapticos
    sudo rm -rf /etc/synapticos
    
    echo "Removing user..."
    sudo userdel synapticos
    
    echo "Removing desktop entries..."
    rm -f ~/.local/share/applications/synapticos-*.desktop
    
    echo "✅ SynapticOS uninstalled"
else
    echo "Uninstall cancelled"
fi
EOF

sudo chmod +x /opt/synapticos/bin/synapticos-uninstall

echo
echo -e "${GREEN}🎉 SynapticOS distribution setup complete!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit API keys in /etc/synapticos/*.env files"
echo "2. Run: source ~/.bashrc"
echo "3. Run: synapticos-quickstart"
echo "4. Access web dashboard at http://localhost:8086"
echo
echo -e "${BLUE}Available commands:${NC}"
echo "  synapticos-quickstart  - Start SynapticOS"
echo "  synapticos_status      - Check service status"
echo "  synapticos_start       - Start services"
echo "  synapticos_stop        - Stop services"
echo "  synapticos-uninstall   - Remove SynapticOS"
echo
echo -e "${YELLOW}⚠️ Remember to:${NC}"
echo "  - Configure API keys in /etc/synapticos/"
echo "  - Set up your educational platform accounts"
echo "  - Review security settings"
echo
