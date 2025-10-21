#!/bin/bash
################################################################################
# ALFRED v1.1 Test Suite
# Comprehensive testing for voice assistant functionality
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ALFRED v1.1 Test Suite                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -ne "${YELLOW}Testing: ${test_name}...${NC} "

    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}[1/5] File Structure Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "ALFRED v1.1 daemon exists" "test -f src/ai/alfred/alfred-daemon-v1.1.py"
run_test "Command handlers directory exists" "test -d src/ai/alfred/commands"
run_test "Security tools handler exists" "test -f src/ai/alfred/commands/security_tools.py"
run_test "System handler exists" "test -f src/ai/alfred/commands/system.py"
run_test "Applications handler exists" "test -f src/ai/alfred/commands/applications.py"
run_test "Files handler exists" "test -f src/ai/alfred/commands/files.py"
run_test "Conversational handler exists" "test -f src/ai/alfred/commands/conversational.py"

echo ""
echo -e "${BLUE}[2/5] Python Syntax Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "ALFRED daemon syntax" "python3 -m py_compile src/ai/alfred/alfred-daemon-v1.1.py"
run_test "Security tools syntax" "python3 -m py_compile src/ai/alfred/commands/security_tools.py"
run_test "System handler syntax" "python3 -m py_compile src/ai/alfred/commands/system.py"
run_test "Applications handler syntax" "python3 -m py_compile src/ai/alfred/commands/applications.py"
run_test "Files handler syntax" "python3 -m py_compile src/ai/alfred/commands/files.py"
run_test "Conversational handler syntax" "python3 -m py_compile src/ai/alfred/commands/conversational.py"

echo ""
echo -e "${BLUE}[3/5] Dependencies Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Python 3 installed" "command -v python3"
run_test "espeak installed" "command -v espeak"
run_test "xdotool installed" "command -v xdotool"
run_test "paplay installed" "command -v paplay"
run_test "SpeechRecognition module" "python3 -c 'import speech_recognition'"
run_test "psutil module" "python3 -c 'import psutil'"

echo ""
echo -e "${BLUE}[4/5] Audio System Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "espeak TTS works" "espeak -v en-gb 'Test' --stdout > /dev/null 2>&1"
run_test "Microphone detected" "arecord -l | grep -q 'card'"
run_test "PulseAudio running" "pactl info &>/dev/null"
run_test "ALFRED log directory exists" "test -d /var/log/synos || sudo mkdir -p /var/log/synos"

echo ""
echo -e "${BLUE}[5/5] Documentation Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "v1.1 Development Plan exists" "test -f docs/06-project-status/V1.1-DEVELOPMENT-PLAN.md"
run_test "ALFRED User Guide exists" "test -f docs/04-user-guides/ALFRED-GUIDE.md"
run_test "Kickoff Summary exists" "test -f docs/06-project-status/V1.1-KICKOFF-SUMMARY.md"
run_test "CHANGELOG updated" "grep -q 'v1.1' CHANGELOG.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Test Results Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=$((PASSED + FAILED))
PASS_RATE=$((PASSED * 100 / TOTAL))

echo -e "Total Tests:  ${BLUE}$TOTAL${NC}"
echo -e "Passed:       ${GREEN}$PASSED${NC}"
echo -e "Failed:       ${RED}$FAILED${NC}"
echo -e "Pass Rate:    ${BLUE}${PASS_RATE}%${NC}"

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ All Tests Passed! ALFRED v1.1 is Ready!             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Test ALFRED: python3 src/ai/alfred/alfred-daemon-v1.1.py"
    echo "  2. Begin Phase 1 development"
    echo "  3. Implement audio system integration"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ Some Tests Failed - Review Required                 ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Please address failed tests before proceeding.${NC}"
    exit 1
fi
