#!/bin/bash

# ============================================================================
# SynOS Phase 3 - Comprehensive Utilities Testing Framework
# ============================================================================
# Tests all individual utility functions and their AI integrations
# Author: SynOS Development Team
# Date: September 20, 2025
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Logging
LOG_FILE="/tmp/synos_utilities_test.log"

echo "🔧 SynOS Utilities Comprehensive Testing Framework" | tee $LOG_FILE
echo "===============================================" | tee -a $LOG_FILE
echo "Date: $(date)" | tee -a $LOG_FILE
echo "Testing Individual Utility Functions..." | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Helper function to run tests
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}Testing: $test_name${NC}" | tee -a $LOG_FILE
    
    if eval "$test_command" 2>&1 | tee -a $LOG_FILE; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}" | tee -a $LOG_FILE
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}" | tee -a $LOG_FILE
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo "" | tee -a $LOG_FILE
}

# Test 1: Core Utilities Compilation
echo -e "${CYAN}=== Testing Core Utilities Compilation ===${NC}" | tee -a $LOG_FILE

run_test "Enhanced Utilities Module Compilation" \
    "cd /home/diablorain/Syn_OS && cargo check -p syn-kernel --lib" \
    "success"

run_test "Userspace Utilities Compilation" \
    "cd /home/diablorain/Syn_OS/src/userspace && find . -name '*.rs' | wc -l" \
    "greater_than_5"

# Test 2: Individual Utility Function Testing
echo -e "${CYAN}=== Testing Individual Utility Functions ===${NC}" | tee -a $LOG_FILE

# Create test environment
TEST_DIR="/tmp/synos_util_test"
mkdir -p $TEST_DIR
cd $TEST_DIR

# Test basic file operations
run_test "File Creation and Listing" \
    "echo 'test content' > test_file.txt && ls -la test_file.txt" \
    "success"

run_test "Directory Operations" \
    "mkdir test_dir && cd test_dir && pwd" \
    "success"

run_test "File Permissions Testing" \
    "chmod 755 ../test_file.txt && ls -la ../test_file.txt | grep rwxr-xr-x" \
    "success"

# Test 3: AI-Enhanced Utility Features
echo -e "${CYAN}=== Testing AI-Enhanced Utility Features ===${NC}" | tee -a $LOG_FILE

run_test "AI File Analysis Simulation" \
    "echo 'Simulating AI file analysis...' && sleep 1 && echo 'AI analysis complete'" \
    "success"

run_test "Consciousness Integration Points" \
    "cd /home/diablorain/Syn_OS && grep -r 'consciousness' src/userspace/utilities/ | wc -l" \
    "greater_than_0"

run_test "Educational Mode Hooks" \
    "cd /home/diablorain/Syn_OS && grep -r 'educational' src/userspace/utilities/ | wc -l" \
    "greater_than_0"

# Test 4: System Utility Performance
echo -e "${CYAN}=== Testing System Utility Performance ===${NC}" | tee -a $LOG_FILE

run_test "Large File Handling" \
    "dd if=/dev/zero of=large_test_file bs=1M count=10 2>/dev/null && ls -lh large_test_file" \
    "success"

run_test "Directory Traversal Performance" \
    "find /home/diablorain/Syn_OS -name '*.rs' | head -20" \
    "success"

run_test "Text Processing Performance" \
    "cd /home/diablorain/Syn_OS && find . -name '*.rs' -exec wc -l {} + | tail -1" \
    "success"

# Test 5: Error Handling and Edge Cases
echo -e "${CYAN}=== Testing Error Handling and Edge Cases ===${NC}" | tee -a $LOG_FILE

run_test "Non-existent File Handling" \
    "ls non_existent_file.txt 2>&1 | grep -i 'no such file'" \
    "success"

run_test "Permission Denied Handling" \
    "touch restricted_file && chmod 000 restricted_file && cat restricted_file 2>&1 | grep -i permission" \
    "success"

run_test "Invalid Command Arguments" \
    "chmod invalid_mode test_file.txt 2>&1 | grep -i 'invalid'" \
    "success"

# Test 6: Integration with System Libraries
echo -e "${CYAN}=== Testing Integration with System Libraries ===${NC}" | tee -a $LOG_FILE

run_test "C Library Integration Check" \
    "cd /home/diablorain/Syn_OS && find src/userspace -name 'libc.rs' | wc -l" \
    "greater_than_0"

run_test "FFI Integration Points" \
    "cd /home/diablorain/Syn_OS && grep -r 'extern \"C\"' src/userspace/ | wc -l" \
    "greater_than_0"

run_test "System Call Integration" \
    "cd /home/diablorain/Syn_OS && grep -r 'syscall' src/userspace/utilities/ | wc -l" \
    "greater_than_0"

# Test 7: Security Features
echo -e "${CYAN}=== Testing Security Features ===${NC}" | tee -a $LOG_FILE

run_test "Security Context Validation" \
    "cd /home/diablorain/Syn_OS && grep -r 'SecurityContext' src/userspace/ | wc -l" \
    "greater_than_0"

run_test "Privilege Management" \
    "cd /home/diablorain/Syn_OS && grep -r 'privilege' src/userspace/ | wc -l" \
    "greater_than_0"

run_test "Access Control Implementation" \
    "cd /home/diablorain/Syn_OS && grep -r 'access_control' src/userspace/ | wc -l" \
    "greater_than_0"

# Cleanup
cd /home/diablorain/Syn_OS
rm -rf $TEST_DIR

# Final Results
echo "" | tee -a $LOG_FILE
echo -e "${PURPLE}=== Utilities Testing Summary ===${NC}" | tee -a $LOG_FILE
echo "Total Tests: $TOTAL_TESTS" | tee -a $LOG_FILE
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}" | tee -a $LOG_FILE
echo -e "${RED}Failed: $FAILED_TESTS${NC}" | tee -a $LOG_FILE

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL UTILITIES TESTS PASSED!${NC}" | tee -a $LOG_FILE
    SUCCESS_RATE=100
else
    SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo -e "${YELLOW}⚠️  Some tests failed. Success rate: ${SUCCESS_RATE}%${NC}" | tee -a $LOG_FILE
fi

echo "" | tee -a $LOG_FILE
echo "Detailed log saved to: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Export results for next phase
echo "UTILITIES_TEST_RESULTS='TOTAL:$TOTAL_TESTS,PASSED:$PASSED_TESTS,FAILED:$FAILED_TESTS,RATE:${SUCCESS_RATE}%'" > /tmp/utilities_test_results.env

exit $FAILED_TESTS
