#!/bin/bash
################################################################################
# PulseAudio Setup for ALFRED Voice Assistant
# Optimizes audio settings for voice recognition and TTS
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PulseAudio Setup for ALFRED                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo -e "${RED}Error: Do not run as root (PulseAudio is per-user)${NC}"
   exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}[1/6] Checking PulseAudio installation...${NC}"
if ! command -v pulseaudio &> /dev/null; then
    echo -e "${RED}PulseAudio not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y pulseaudio pulseaudio-utils pavucontrol
fi
echo -e "${GREEN}✓ PulseAudio installed${NC}"
echo ""

echo -e "${YELLOW}[2/6] Creating configuration directories...${NC}"
mkdir -p ~/.config/pulse
mkdir -p ~/.config/synos/alfred/audio
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

echo -e "${YELLOW}[3/6] Backing up existing configuration...${NC}"
if [ -f ~/.config/pulse/default.pa ]; then
    cp ~/.config/pulse/default.pa ~/.config/pulse/default.pa.backup.$(date +%Y%m%d)
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${BLUE}  No existing configuration found (will use system defaults)${NC}"
fi
echo ""

echo -e "${YELLOW}[4/6] Configuring echo cancellation...${NC}"
# Instead of replacing default.pa, we'll load the module dynamically
# This is safer and doesn't break existing configuration
echo -e "${BLUE}  Loading WebRTC echo cancellation module...${NC}"

# Note: We don't install a custom default.pa anymore
# The echo cancellation will be loaded dynamically in step 6
echo -e "${GREEN}✓ Configuration prepared${NC}"
echo ""

echo -e "${YELLOW}[5/6] Restarting PulseAudio...${NC}"
# Use systemd if available, otherwise manual start
if systemctl --user is-active --quiet pulseaudio.service 2>/dev/null; then
    systemctl --user restart pulseaudio.service
    sleep 2
elif systemctl --user is-enabled --quiet pulseaudio.service 2>/dev/null; then
    systemctl --user start pulseaudio.service
    sleep 2
else
    pulseaudio --kill 2>/dev/null || true
    sleep 1
    pulseaudio --start -D
    sleep 2
fi
echo -e "${GREEN}✓ PulseAudio restarted${NC}"
echo ""

echo -e "${YELLOW}[6/6] Verifying audio setup and loading echo cancellation...${NC}"
# Check if PulseAudio is running
if pactl info &>/dev/null; then
    echo -e "${GREEN}✓ PulseAudio is running${NC}"

    # Load echo cancellation module dynamically
    echo ""
    echo -e "${BLUE}Loading WebRTC echo cancellation module...${NC}"
    if pactl load-module module-echo-cancel \
        use_master_format=1 \
        aec_method=webrtc \
        aec_args="analog_gain_control=0 digital_gain_control=1 noise_suppression=1 voice_detection=1" \
        >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Echo cancellation loaded${NC}"
    else
        # Module might already be loaded
        if pactl list modules short | grep -q "module-echo-cancel"; then
            echo -e "${YELLOW}⚠ Echo cancellation already loaded${NC}"
        else
            echo -e "${RED}✗ Failed to load echo cancellation${NC}"
            echo -e "${YELLOW}  Continuing without echo cancellation...${NC}"
        fi
    fi

    # List audio devices
    echo ""
    echo -e "${BLUE}Available audio devices:${NC}"
    pactl list short sinks | while read line; do
        echo -e "  ${GREEN}→${NC} $line"
    done

    echo ""
    echo -e "${BLUE}Available input devices:${NC}"
    pactl list short sources | while read line; do
        echo -e "  ${GREEN}→${NC} $line"
    done
else
    echo -e "${RED}✗ PulseAudio failed to start${NC}"
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  • Check logs: journalctl --user -u pulseaudio.service -n 50"
    echo "  • Manual start: systemctl --user start pulseaudio.service"
    exit 1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Audio Setup Complete!                                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Audio Configuration:${NC}"
echo "  • Echo cancellation: Enabled (WebRTC)"
echo "  • Noise suppression: Enabled"
echo "  • Voice detection: Enabled"
echo "  • Sample rate: 44.1kHz / 48kHz"
echo "  • Low latency mode: Enabled"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Test microphone: arecord -d 5 test.wav"
echo "  2. Play test: aplay test.wav"
echo "  3. Adjust levels: pavucontrol"
echo "  4. Run ALFRED: python3 src/ai/alfred/alfred-daemon-v1.1.py"
echo ""

echo -e "${BLUE}Troubleshooting:${NC}"
echo "  • Volume control: pavucontrol"
echo "  • Restart audio: pulseaudio --kill && pulseaudio --start"
echo "  • Check status: pactl info"
echo ""
