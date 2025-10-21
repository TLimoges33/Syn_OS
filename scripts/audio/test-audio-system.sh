#!/bin/bash
################################################################################
# ALFRED Audio System Test Suite
# Comprehensive audio testing for voice recognition
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ALFRED Audio System Test Suite                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${YELLOW}Testing: $test_name${NC}"

    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${BLUE}[1/7] Checking PulseAudio Installation${NC}"
echo "------------------------------------------------------"
run_test "PulseAudio server" "pactl info"
run_test "PulseAudio utilities" "which pactl pacmd paplay parecord"
echo ""

echo -e "${BLUE}[2/7] Checking Audio Devices${NC}"
echo "------------------------------------------------------"
run_test "Audio output devices" "pactl list sinks short | grep -q ."
run_test "Audio input devices" "pactl list sources short | grep -q ."

# List devices
echo -e "${YELLOW}Available output devices:${NC}"
pactl list sinks short | while read -r line; do
    echo "  • $line"
done

echo -e "${YELLOW}Available input devices:${NC}"
pactl list sources short | while read -r line; do
    echo "  • $line"
done
echo ""

echo -e "${BLUE}[3/7] Testing Echo Cancellation${NC}"
echo "------------------------------------------------------"
if pactl list modules short | grep -q "module-echo-cancel"; then
    echo -e "${GREEN}✓ Echo cancellation module loaded${NC}"
    ((TESTS_PASSED++))

    # Show echo cancel settings
    pactl list modules | grep -A 20 "module-echo-cancel" | head -n 20
else
    echo -e "${YELLOW}⚠ Echo cancellation not loaded${NC}"
    echo "  Run: scripts/audio/setup-pulseaudio.sh"
    ((TESTS_FAILED++))
fi
echo ""

echo -e "${BLUE}[4/7] Testing Python Audio Libraries${NC}"
echo "------------------------------------------------------"
run_test "pyaudio import" "python3 -c 'import pyaudio'"
run_test "speech_recognition import" "python3 -c 'import speech_recognition'"

# Test AudioManager if available
if [ -f "$PROJECT_ROOT/src/ai/alfred/audio_manager.py" ]; then
    run_test "AudioManager import" "cd '$PROJECT_ROOT/src/ai/alfred' && python3 -c 'from audio_manager import AudioManager'"
fi
echo ""

echo -e "${BLUE}[5/7] Testing Microphone Recording${NC}"
echo "------------------------------------------------------"
echo -e "${YELLOW}Recording 3 seconds of audio...${NC}"
TEMP_FILE=$(mktemp --suffix=.wav)

if timeout 5 arecord -d 3 -f cd "$TEMP_FILE" 2>/dev/null; then
    FILE_SIZE=$(stat -c%s "$TEMP_FILE")

    if [ "$FILE_SIZE" -gt 10000 ]; then
        echo -e "${GREEN}✓ Recording successful (${FILE_SIZE} bytes)${NC}"
        ((TESTS_PASSED++))

        echo -e "${YELLOW}Playback test (y/n)?${NC}"
        read -t 5 -n 1 -r REPLY || REPLY="n"
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aplay "$TEMP_FILE" 2>/dev/null
        fi
    else
        echo -e "${RED}✗ Recording file too small${NC}"
        ((TESTS_FAILED++))
    fi

    rm -f "$TEMP_FILE"
else
    echo -e "${RED}✗ Recording failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

echo -e "${BLUE}[6/7] Testing Text-to-Speech${NC}"
echo "------------------------------------------------------"
run_test "espeak installed" "which espeak"

if which espeak &>/dev/null; then
    echo -e "${YELLOW}Testing British accent voice...${NC}"
    if espeak -v en-gb+m3 "Audio test successful" 2>/dev/null; then
        echo -e "${GREEN}✓ TTS working${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ TTS failed${NC}"
        ((TESTS_FAILED++))
    fi
fi
echo ""

echo -e "${BLUE}[7/7] Testing AudioManager${NC}"
echo "------------------------------------------------------"
if [ -f "$PROJECT_ROOT/src/ai/alfred/audio_manager.py" ]; then
    echo -e "${YELLOW}Running AudioManager test...${NC}"

    cd "$PROJECT_ROOT/src/ai/alfred"
    if python3 -c "from audio_manager import AudioManager; am = AudioManager(); print(am.get_status_report())" 2>/dev/null; then
        echo -e "${GREEN}✓ AudioManager functional${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ AudioManager test failed${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${YELLOW}⚠ AudioManager not found${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Summary
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Test Summary                                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "Total Tests:  $TOTAL"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! ALFRED is ready for voice recognition.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Run: ./scripts/audio/optimize-microphone.sh"
    echo "  2. Test: python3 src/ai/alfred/alfred-daemon-v1.1.py"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed. Please check the output above.${NC}"
    echo ""
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "  • Run: ./scripts/audio/setup-pulseaudio.sh"
    echo "  • Check: pactl list sources"
    echo "  • Verify microphone is not muted: pactl list sources | grep -i mute"
    echo ""
    exit 1
fi
