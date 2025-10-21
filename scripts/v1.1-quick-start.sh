#!/bin/bash
################################################################################
# SynOS v1.1 "Voice of the Phoenix" - Development Quick Start
# Rapid setup for v1.1 development environment
################################################################################

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SynOS v1.1 'Voice of the Phoenix' - Quick Start       ║${NC}"
echo -e "${BLUE}║   Release Target: November 15, 2025                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}[1/7] Checking Python dependencies...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

pip3 install --user SpeechRecognition pyaudio psutil 2>/dev/null || true
echo -e "${GREEN}✓ Python dependencies ready${NC}"

echo ""
echo -e "${YELLOW}[2/7] Checking audio system...${NC}"
if ! command -v espeak &> /dev/null; then
    echo -e "${YELLOW}Installing espeak for TTS...${NC}"
    sudo apt-get update && sudo apt-get install -y espeak espeak-data
fi

if ! command -v paplay &> /dev/null; then
    echo -e "${YELLOW}Installing PulseAudio...${NC}"
    sudo apt-get install -y pulseaudio pulseaudio-utils
fi

if ! command -v xdotool &> /dev/null; then
    echo -e "${YELLOW}Installing xdotool for transcription...${NC}"
    sudo apt-get install -y xdotool
fi
echo -e "${GREEN}✓ Audio system ready${NC}"

echo ""
echo -e "${YELLOW}[3/7] Setting up ALFRED directories...${NC}"
sudo mkdir -p /var/log/synos
sudo chown "$USER":"$USER" /var/log/synos
mkdir -p ~/.config/synos/alfred
echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo -e "${YELLOW}[4/7] Checking Rust toolchain...${NC}"
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}Warning: Rust toolchain not found${NC}"
    echo -e "${YELLOW}Install with: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh${NC}"
else
    echo -e "${GREEN}✓ Rust toolchain found: $(rustc --version)${NC}"
fi

echo ""
echo -e "${YELLOW}[5/7] Testing ALFRED v1.1...${NC}"
if [ -f "$PROJECT_ROOT/src/ai/alfred/alfred-daemon-v1.1.py" ]; then
    echo -e "${GREEN}✓ ALFRED v1.1 daemon found${NC}"
    echo -e "${BLUE}  Location: src/ai/alfred/alfred-daemon-v1.1.py${NC}"
else
    echo -e "${RED}✗ ALFRED v1.1 daemon not found${NC}"
fi

if [ -d "$PROJECT_ROOT/src/ai/alfred/commands" ]; then
    cmd_count=$(ls -1 "$PROJECT_ROOT/src/ai/alfred/commands"/*.py 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ Command handlers found: $cmd_count modules${NC}"
else
    echo -e "${RED}✗ Command handlers not found${NC}"
fi

echo ""
echo -e "${YELLOW}[6/7] Checking microphone...${NC}"
if command -v arecord &> /dev/null; then
    echo -e "${BLUE}  Available recording devices:${NC}"
    arecord -l 2>/dev/null | grep "card" || echo "  None found"
else
    echo -e "${YELLOW}  Install alsa-utils to test: sudo apt install alsa-utils${NC}"
fi

echo ""
echo -e "${YELLOW}[7/7] Version information...${NC}"
echo -e "${BLUE}  Workspace version:${NC} $(grep '^version' Cargo.toml | head -1 | cut -d'"' -f2)"
echo -e "${BLUE}  ALFRED version:${NC} 1.1.0"
echo -e "${BLUE}  Target release:${NC} November 15, 2025"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Setup Complete! Ready for v1.1 Development            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Quick Commands:${NC}"
echo ""
echo -e "  ${YELLOW}Test ALFRED v1.1:${NC}"
echo -e "    python3 src/ai/alfred/alfred-daemon-v1.1.py"
echo ""
echo -e "  ${YELLOW}Build kernel:${NC}"
echo -e "    cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none"
echo ""
echo -e "  ${YELLOW}Build security core:${NC}"
echo -e "    cargo build --manifest-path=core/security/Cargo.toml"
echo ""
echo -e "  ${YELLOW}View development plan:${NC}"
echo -e "    cat docs/06-project-status/V1.1-DEVELOPMENT-PLAN.md"
echo ""
echo -e "  ${YELLOW}View ALFRED guide:${NC}"
echo -e "    cat docs/04-user-guides/ALFRED-GUIDE.md"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "  1. Review v1.1 Development Plan: ${YELLOW}docs/06-project-status/V1.1-DEVELOPMENT-PLAN.md${NC}"
echo -e "  2. Test ALFRED voice commands"
echo -e "  3. Review TODO.md for task assignments"
echo -e "  4. Start implementing Phase 1 features"
echo ""

echo -e "${GREEN}Happy coding! 🚀${NC}"
echo -e "${BLUE}\"At your service, sir.\" - ALFRED${NC}"
echo ""
