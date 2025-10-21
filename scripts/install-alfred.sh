#!/bin/bash
################################################################################
# ALFRED v1.1 Installation Script
# Sets up ALFRED with proper dependencies in a virtual environment
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ALFRED v1.1 Installation                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Install system dependencies
echo -e "${YELLOW}[1/4] Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3-full \
    python3-pip \
    python3-venv \
    espeak \
    espeak-data \
    pulseaudio \
    pulseaudio-utils \
    xdotool \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils

echo -e "${GREEN}✓ System dependencies installed${NC}"
echo ""

# Create virtual environment (optional, but recommended)
echo -e "${YELLOW}[2/4] Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv --system-site-packages
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate and install Python packages
source venv/bin/activate

echo ""
echo -e "${YELLOW}[3/4] Installing Python packages...${NC}"
pip install --upgrade pip
pip install \
    SpeechRecognition \
    pyaudio \
    psutil

echo -e "${GREEN}✓ Python packages installed${NC}"
echo ""

# Set up directories and permissions
echo -e "${YELLOW}[4/4] Setting up directories and permissions...${NC}"
sudo mkdir -p /var/log/synos
sudo chown "$USER":"$USER" /var/log/synos
mkdir -p ~/.config/synos/alfred

# Create systemd service
if [ ! -f "/etc/systemd/system/alfred.service" ]; then
    sudo tee /etc/systemd/system/alfred.service > /dev/null <<EOF
[Unit]
Description=ALFRED Voice Assistant v1.1
After=pulseaudio.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/venv/bin/python3 $PROJECT_ROOT/src/ai/alfred/alfred-daemon-v1.1.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF
    echo -e "${GREEN}✓ Systemd service created${NC}"
else
    echo -e "${GREEN}✓ Systemd service already exists${NC}"
fi

echo -e "${GREEN}✓ Setup complete${NC}"
echo ""

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Installation Complete!                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}ALFRED v1.1 is now installed!${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo ""
echo -e "  ${YELLOW}Run ALFRED now:${NC}"
echo -e "    source venv/bin/activate"
echo -e "    python3 src/ai/alfred/alfred-daemon-v1.1.py"
echo ""
echo -e "  ${YELLOW}Enable ALFRED service (auto-start on boot):${NC}"
echo -e "    sudo systemctl enable alfred"
echo -e "    sudo systemctl start alfred"
echo ""
echo -e "  ${YELLOW}Check ALFRED status:${NC}"
echo -e "    sudo systemctl status alfred"
echo ""
echo -e "  ${YELLOW}View logs:${NC}"
echo -e "    tail -f /var/log/synos/alfred.log"
echo ""

echo -e "${BLUE}\"At your service, sir!\" - ALFRED${NC}"
echo ""
