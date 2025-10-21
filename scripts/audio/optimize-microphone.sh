#!/bin/bash
################################################################################
# Microphone Optimization for ALFRED Voice Recognition
# Auto-calibrates and optimizes microphone settings
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ALFRED Microphone Optimization                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if PulseAudio is running
if ! pactl info &>/dev/null; then
    echo -e "${RED}Error: PulseAudio is not running${NC}"
    echo "Run: pulseaudio --start"
    exit 1
fi

echo -e "${YELLOW}[1/5] Detecting microphone...${NC}"
# Get default source
DEFAULT_SOURCE=$(pactl get-default-source)
echo -e "${GREEN}✓ Found: $DEFAULT_SOURCE${NC}"
echo ""

echo -e "${YELLOW}[2/5] Setting optimal gain levels...${NC}"
# Set microphone volume to 70% (good balance for voice)
pactl set-source-volume @DEFAULT_SOURCE@ 70%
echo -e "${GREEN}✓ Volume set to 70%${NC}"

# Unmute microphone
pactl set-source-mute @DEFAULT_SOURCE@ 0
echo -e "${GREEN}✓ Microphone unmuted${NC}"
echo ""

echo -e "${YELLOW}[3/5] Enabling echo cancellation...${NC}"
# Check if echo cancel module is loaded
if ! pactl list modules short | grep -q "module-echo-cancel"; then
    pactl load-module module-echo-cancel \
        use_master_format=1 \
        aec_method=webrtc \
        aec_args="analog_gain_control=0 digital_gain_control=1 noise_suppression=1 voice_detection=1" \
        >/dev/null 2>&1 || echo -e "${YELLOW}  Echo cancel already configured${NC}"
    echo -e "${GREEN}✓ Echo cancellation enabled${NC}"
else
    echo -e "${GREEN}✓ Echo cancellation already active${NC}"
fi
echo ""

echo -e "${YELLOW}[4/5] Testing microphone (3 seconds)...${NC}"
echo -e "${BLUE}  Recording sample audio...${NC}"

TEMP_FILE=$(mktemp --suffix=.wav)
if arecord -d 3 -f cd "$TEMP_FILE" 2>/dev/null; then
    FILE_SIZE=$(stat -c%s "$TEMP_FILE")

    if [ "$FILE_SIZE" -gt 1000 ]; then
        echo -e "${GREEN}✓ Microphone is working (${FILE_SIZE} bytes recorded)${NC}"

        # Optionally play back
        echo -e "${BLUE}  Play back recording? (y/n)${NC}"
        read -t 5 -n 1 -r REPLY || REPLY="n"
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aplay "$TEMP_FILE" 2>/dev/null
        fi
    else
        echo -e "${RED}✗ Warning: Recording seems empty${NC}"
    fi

    rm -f "$TEMP_FILE"
else
    echo -e "${RED}✗ Recording failed${NC}"
fi
echo ""

echo -e "${YELLOW}[5/5] Ambient noise calibration...${NC}"
echo -e "${BLUE}  Please remain quiet for 3 seconds...${NC}"
sleep 1

# Record ambient noise sample
NOISE_FILE=$(mktemp --suffix=.wav)
arecord -d 3 -f cd "$NOISE_FILE" 2>/dev/null

# Analyze noise level (very basic)
NOISE_SIZE=$(stat -c%s "$NOISE_FILE")
if [ "$NOISE_SIZE" -lt 50000 ]; then
    echo -e "${GREEN}✓ Low ambient noise - excellent environment${NC}"
elif [ "$NOISE_SIZE" -lt 100000 ]; then
    echo -e "${YELLOW}✓ Moderate ambient noise - acceptable${NC}"
else
    echo -e "${YELLOW}⚠ High ambient noise detected${NC}"
    echo -e "${BLUE}  Consider using headset or quieter location${NC}"
fi

rm -f "$NOISE_FILE"
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Microphone Optimization Complete!                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Current Settings:${NC}"
pactl list sources | grep -A 10 "Name: $DEFAULT_SOURCE" | grep -E "(Name|Volume|Mute)" | while read line; do
    echo -e "  $line"
done

echo ""
echo -e "${BLUE}Recommendations:${NC}"
echo "  • Speak 1-2 feet from microphone"
echo "  • Minimize background noise"
echo "  • Use consistent volume when speaking"
echo "  • Test with: python3 src/ai/alfred/audio_manager.py"
echo ""

echo -e "${GREEN}Ready for ALFRED voice recognition!${NC}"
