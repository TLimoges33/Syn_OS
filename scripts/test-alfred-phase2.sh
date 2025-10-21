#!/bin/bash
################################################################################
# ALFRED Phase 2 Testing Suite
# Comprehensive testing of voice commands and audio integration
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   ALFRED Phase 2 Testing Suite v1.1                       ║"
echo "║   Voice Commands & Audio Integration Testing              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Test result function
test_result() {
    local name="$1"
    local result="$2"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    if [ "$result" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# 1. Pre-flight checks
echo -e "${CYAN}[1/7] Pre-flight Checks${NC}"
echo ""

# Check if ALFRED directory exists
if [ -d "$PROJECT_ROOT/src/ai/alfred" ]; then
    test_result "ALFRED directory exists" "pass"
else
    test_result "ALFRED directory exists" "fail"
fi

# Check if venv exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    test_result "Python virtual environment exists" "pass"
else
    test_result "Python virtual environment exists" "fail"
    echo -e "${YELLOW}  Run: ./scripts/install-alfred.sh${NC}"
fi

# Check PulseAudio
if pgrep -x "pulseaudio" > /dev/null; then
    test_result "PulseAudio running" "pass"
else
    test_result "PulseAudio running" "fail"
fi

# Check echo cancellation
if pactl list modules short | grep -q "echo-cancel"; then
    test_result "Echo cancellation module loaded" "pass"
else
    test_result "Echo cancellation module loaded" "fail"
fi

echo ""

# 2. Audio System Tests
echo -e "${CYAN}[2/7] Audio System Tests${NC}"
echo ""

# Check default source
DEFAULT_SOURCE=$(pactl info | grep "Default Source" | cut -d: -f2 | xargs)
if [ ! -z "$DEFAULT_SOURCE" ]; then
    test_result "Default audio source configured: $DEFAULT_SOURCE" "pass"
else
    test_result "Default audio source configured" "fail"
fi

# Check microphone volume
MIC_VOLUME=$(pactl list sources | grep -A 10 "$DEFAULT_SOURCE" | grep "Volume:" | head -1 | grep -oP '\d+%' | head -1)
if [ ! -z "$MIC_VOLUME" ]; then
    test_result "Microphone volume: $MIC_VOLUME" "pass"
else
    test_result "Microphone volume readable" "fail"
fi

# List available audio devices
echo ""
echo -e "${BLUE}Available Audio Devices:${NC}"
pactl list sources short | awk '{print "  • " $2}'

echo ""

# 3. Python Dependencies
echo -e "${CYAN}[3/7] Python Dependencies${NC}"
echo ""

if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"

    # Check key packages
    python3 -c "import speech_recognition" 2>/dev/null && test_result "speech_recognition installed" "pass" || test_result "speech_recognition installed" "fail"
    python3 -c "import pyaudio" 2>/dev/null && test_result "pyaudio installed" "pass" || test_result "pyaudio installed" "fail"
    python3 -c "import pyttsx3" 2>/dev/null && test_result "pyttsx3 installed" "pass" || test_result "pyttsx3 installed" "fail"
else
    echo -e "${YELLOW}  Virtual environment not found${NC}"
fi

echo ""

# 4. ALFRED Module Tests
echo -e "${CYAN}[4/7] ALFRED Module Tests${NC}"
echo ""

# Check if ALFRED files exist
ALFRED_FILES=(
    "src/ai/alfred/alfred-daemon-v1.1.py"
    "src/ai/alfred/audio_manager.py"
    "src/ai/alfred/handlers/system_handler.py"
    "src/ai/alfred/handlers/security_handler.py"
    "src/ai/alfred/handlers/file_handler.py"
    "src/ai/alfred/handlers/conversation_handler.py"
    "src/ai/alfred/handlers/application_handler.py"
)

for file in "${ALFRED_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        test_result "$(basename "$file") exists" "pass"
    else
        test_result "$(basename "$file") exists" "fail"
    fi
done

echo ""

# 5. Import Tests
echo -e "${CYAN}[5/7] Python Import Tests${NC}"
echo ""

if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    cd "$PROJECT_ROOT"

    # Test AudioManager import
    python3 -c "from src.ai.alfred.audio_manager import AudioManager; print('AudioManager imported successfully')" 2>/dev/null && \
        test_result "AudioManager import" "pass" || test_result "AudioManager import" "fail"

    # Test handler imports
    python3 -c "from src.ai.alfred.handlers.system_handler import SystemHandler" 2>/dev/null && \
        test_result "SystemHandler import" "pass" || test_result "SystemHandler import" "fail"

    python3 -c "from src.ai.alfred.handlers.security_handler import SecurityHandler" 2>/dev/null && \
        test_result "SecurityHandler import" "pass" || test_result "SecurityHandler import" "fail"
fi

echo ""

# 6. Configuration Tests
echo -e "${CYAN}[6/7] Configuration Tests${NC}"
echo ""

# Check PulseAudio config
if [ -f "$HOME/.config/pulse/default.pa" ]; then
    if grep -q "module-echo-cancel" "$HOME/.config/pulse/default.pa"; then
        test_result "PulseAudio echo cancel in config" "pass"
    else
        test_result "PulseAudio echo cancel in config" "fail"
    fi
else
    test_result "PulseAudio config exists" "fail"
fi

# Check systemd service (if installed)
if systemctl --user list-unit-files | grep -q "alfred.service"; then
    test_result "ALFRED systemd service exists" "pass"
else
    test_result "ALFRED systemd service exists" "fail"
    echo -e "${YELLOW}  (Not required for manual testing)${NC}"
fi

echo ""

# 7. Summary
echo -e "${CYAN}[7/7] Test Summary${NC}"
echo ""
echo "═══════════════════════════════════════"
echo "  Tests Passed:  $TESTS_PASSED / $TESTS_TOTAL"
echo "  Tests Failed:  $TESTS_FAILED / $TESTS_TOTAL"
echo "═══════════════════════════════════════"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! ALFRED is ready for live testing.${NC}"
    echo ""
    echo -e "${CYAN}To start ALFRED:${NC}"
    echo "  cd $PROJECT_ROOT"
    echo "  source venv/bin/activate"
    echo "  python3 src/ai/alfred/alfred-daemon-v1.1.py"
else
    echo -e "${YELLOW}⚠ Some tests failed. Review failures above.${NC}"
    echo ""
    if [ $TESTS_PASSED -gt $((TESTS_TOTAL / 2)) ]; then
        echo -e "${CYAN}Most tests passed. You can still try ALFRED:${NC}"
        echo "  cd $PROJECT_ROOT"
        echo "  source venv/bin/activate"
        echo "  python3 src/ai/alfred/alfred-daemon-v1.1.py"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Manual Testing Checklist:${NC}"
echo ""
echo "Once ALFRED is running, test these commands:"
echo ""
echo "  1. System Commands:"
echo "     • \"Alfred, system health check\""
echo "     • \"Alfred, what's my IP address?\""
echo "     • \"Alfred, show disk usage\""
echo ""
echo "  2. Security Tools:"
echo "     • \"Alfred, scan localhost with nmap\""
echo "     • \"Alfred, launch wireshark\""
echo "     • \"Alfred, start burp suite\""
echo ""
echo "  3. File Operations:"
echo "     • \"Alfred, find file test.txt\""
echo "     • \"Alfred, open home directory\""
echo ""
echo "  4. Conversational:"
echo "     • \"Alfred, what time is it?\""
echo "     • \"Alfred, hello\""
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Exit code based on test results
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
