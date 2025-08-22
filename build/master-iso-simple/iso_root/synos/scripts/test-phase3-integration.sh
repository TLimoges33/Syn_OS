#!/bin/bash

# NATS Phase 3 Integration Testing Script
# =====================================
# Tests all Phase 3 resilience features including schema validation,
# performance optimization, circuit breakers, and monitoring.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/phase3-integration-test.log"
RESULTS_FILE="$PROJECT_ROOT/logs/phase3-test-results.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
NATS_URL="${NATS_URL:-nats://localhost:4222}"
TEST_DURATION=30
LOAD_TEST_MESSAGES=1000
CIRCUIT_BREAKER_THRESHOLD=5

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Test result tracking
declare -A test_results
total_tests=0
passed_tests=0
failed_tests=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    total_tests=$((total_tests + 1))
    log "${BLUE}Running test: $test_name${NC}"
    
    if eval "$test_command" >> "$LOG_FILE" 2>&1; then
        if [ $? -eq $expected_result ]; then
            log "${GREEN}✓ PASSED: $test_name${NC}"
            test_results["$test_name"]="PASSED"
            passed_tests=$((passed_tests + 1))
            return 0
        else
            log "${RED}✗ FAILED: $test_name (unexpected exit code)${NC}"
            test_results["$test_name"]="FAILED"
            failed_tests=$((failed_tests + 1))
            return 1
        fi
    else
        log "${RED}✗ FAILED: $test_name${NC}"
        test_results["$test_name"]="FAILED"
        failed_tests=$((failed_tests + 1))
        return 1
    fi
}

# Function to check if NATS is running
check_nats_running() {
    log "Checking if NATS server is running..."
    
    if ! command -v nats &> /dev/null; then
        log "${YELLOW}NATS CLI not found, installing...${NC}"
        go install github.com/nats-io/natscli/nats@latest
    fi
    
    if nats server check --server="$NATS_URL" &> /dev/null; then
        log "${GREEN}NATS server is running${NC}"
        return 0
    else
        log "${RED}NATS server is not running or not accessible${NC}"
        return 1
    fi
}

# Function to test schema validation
test_schema_validation() {
    log "Testing NATS message schema validation..."
    
    # Create test script
    cat > /tmp/test_schema_validation.py << 'EOF'
import sys
import json
import asyncio
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.schema_validation import NATSMessageValidator

async def test_schema_validation():
    validator = NATSMessageValidator()
    
    # Test valid consciousness event
    valid_message = {
        "id": "test_001",
        "type": "consciousness.state_change",
        "source": "consciousness_core",
        "timestamp": "2025-08-19T19:20:00Z",
        "data": {
            "consciousness_level": 0.8,
            "emotional_state": {
                "valence": 0.5,
                "arousal": 0.7,
                "confidence": 0.9
            }
        },
        "priority": 5
    }
    
    result = validator.validate_nats_message(
        "consciousness.state_change",
        json.dumps(valid_message).encode()
    )
    
    if not result.is_valid:
        print(f"Valid message failed validation: {result.errors}")
        return False
    
    # Test invalid message
    invalid_message = {
        "id": "test_002",
        "type": "consciousness.state_change",
        "source": "consciousness_core"
        # Missing required fields
    }
    
    result = validator.validate_nats_message(
        "consciousness.state_change",
        json.dumps(invalid_message).encode()
    )
    
    if result.is_valid:
        print("Invalid message passed validation")
        return False
    
    print("Schema validation tests passed")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_schema_validation())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_schema_validation.py
}

# Function to test circuit breaker
test_circuit_breaker() {
    log "Testing circuit breaker functionality..."
    
    cat > /tmp/test_circuit_breaker.py << 'EOF'
import sys
import asyncio
import time
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerState

async def test_circuit_breaker():
    # Create circuit breaker with low threshold for testing
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=2.0,
        expected_exception=Exception
    )
    
    # Test normal operation
    @cb
    async def normal_operation():
        return "success"
    
    result = await normal_operation()
    if result != "success":
        print("Normal operation failed")
        return False
    
    # Test failure handling
    @cb
    async def failing_operation():
        raise Exception("Test failure")
    
    # Trigger failures to open circuit
    for i in range(4):
        try:
            await failing_operation()
        except Exception:
            pass
    
    # Circuit should be open now
    if cb.state != CircuitBreakerState.OPEN:
        print(f"Circuit breaker should be OPEN, but is {cb.state}")
        return False
    
    # Wait for recovery timeout
    await asyncio.sleep(2.5)
    
    # Circuit should be half-open now
    if cb.state != CircuitBreakerState.HALF_OPEN:
        print(f"Circuit breaker should be HALF_OPEN, but is {cb.state}")
        return False
    
    print("Circuit breaker tests passed")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_circuit_breaker())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_circuit_breaker.py
}

# Function to test message persistence
test_message_persistence() {
    log "Testing message persistence functionality..."
    
    cat > /tmp/test_message_persistence.py << 'EOF'
import sys
import asyncio
import json
import tempfile
import os
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.message_persistence import MessagePersistenceManager

async def test_message_persistence():
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        manager = MessagePersistenceManager(db_path)
        await manager.initialize()
        
        # Test message storage
        test_message = {
            "id": "test_persist_001",
            "type": "test.message",
            "source": "test",
            "timestamp": "2025-08-19T19:20:00Z",
            "data": {"test": "data"},
            "priority": 5
        }
        
        message_id = await manager.store_message(
            "test.subject",
            json.dumps(test_message).encode(),
            priority=5
        )
        
        if not message_id:
            print("Failed to store message")
            return False
        
        # Test message retrieval
        messages = await manager.get_pending_messages(limit=10)
        if len(messages) != 1:
            print(f"Expected 1 message, got {len(messages)}")
            return False
        
        # Test message acknowledgment
        await manager.acknowledge_message(message_id)
        
        # Should have no pending messages now
        messages = await manager.get_pending_messages(limit=10)
        if len(messages) != 0:
            print(f"Expected 0 messages after ack, got {len(messages)}")
            return False
        
        await manager.close()
        print("Message persistence tests passed")
        return True
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    result = asyncio.run(test_message_persistence())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_message_persistence.py
}

# Function to test performance monitoring
test_performance_monitoring() {
    log "Testing performance monitoring..."
    
    cat > /tmp/test_performance_monitoring.py << 'EOF'
import sys
import asyncio
import time
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.performance_optimizer import PerformanceMonitor

async def test_performance_monitoring():
    monitor = PerformanceMonitor(window_size=10)
    
    # Start monitoring
    monitor.start_monitoring(interval_seconds=0.1)
    
    # Simulate some activity
    for i in range(20):
        monitor.record_message(latency_ms=10.0 + i)
        if i % 5 == 0:
            monitor.record_error()
        await asyncio.sleep(0.05)
    
    # Get current metrics
    metrics = monitor.get_current_metrics()
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Validate metrics
    if metrics.message_count != 20:
        print(f"Expected 20 messages, got {metrics.message_count}")
        return False
    
    if metrics.error_count != 4:  # Errors at i=0,5,10,15
        print(f"Expected 4 errors, got {metrics.error_count}")
        return False
    
    if metrics.avg_latency_ms <= 0:
        print(f"Expected positive latency, got {metrics.avg_latency_ms}")
        return False
    
    print("Performance monitoring tests passed")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_performance_monitoring())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_performance_monitoring.py
}

# Function to test JetStream configuration
test_jetstream_config() {
    log "Testing JetStream configuration..."
    
    cat > /tmp/test_jetstream_config.py << 'EOF'
import sys
import asyncio
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.jetstream_config import JetStreamConfigManager

async def test_jetstream_config():
    config_manager = JetStreamConfigManager()
    
    # Test stream configuration generation
    consciousness_config = config_manager.get_stream_config('consciousness')
    if not consciousness_config:
        print("Failed to get consciousness stream config")
        return False
    
    if consciousness_config.name != 'CONSCIOUSNESS':
        print(f"Expected stream name CONSCIOUSNESS, got {consciousness_config.name}")
        return False
    
    # Test consumer configuration
    consumer_config = config_manager.get_consumer_config(
        'consciousness', 'consciousness_processor'
    )
    if not consumer_config:
        print("Failed to get consumer config")
        return False
    
    print("JetStream configuration tests passed")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_jetstream_config())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_jetstream_config.py
}

# Function to test monitoring and alerting
test_monitoring_alerting() {
    log "Testing monitoring and alerting system..."
    
    cat > /tmp/test_monitoring_alerting.py << 'EOF'
import sys
import asyncio
import tempfile
import os
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.monitoring import NATSMonitoringSystem

async def test_monitoring_alerting():
    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp_log:
        log_path = tmp_log.name
    
    try:
        monitor = NATSMonitoringSystem(
            nats_url="nats://localhost:4222",
            log_file=log_path
        )
        
        # Test metric recording
        await monitor.record_metric("test.metric", 100.0, {"component": "test"})
        
        # Test alert generation
        await monitor.check_alert_conditions()
        
        # Test health check
        health_status = await monitor.get_health_status()
        if not isinstance(health_status, dict):
            print("Health status should be a dictionary")
            return False
        
        print("Monitoring and alerting tests passed")
        return True
        
    finally:
        # Cleanup
        if os.path.exists(log_path):
            os.unlink(log_path)

if __name__ == "__main__":
    result = asyncio.run(test_monitoring_alerting())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_monitoring_alerting.py
}

# Function to run integration test
test_full_integration() {
    log "Running full Phase 3 integration test..."
    
    cat > /tmp/test_full_integration.py << 'EOF'
import sys
import asyncio
import json
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.schema_validation import NATSMessageValidator
from consciousness_v2.resilience.circuit_breaker import CircuitBreaker
from consciousness_v2.resilience.performance_optimizer import PerformanceMonitor

async def test_full_integration():
    try:
        # Connect to NATS
        nc = await nats.connect("nats://localhost:4222")
        js = nc.jetstream()
        
        # Initialize components
        validator = NATSMessageValidator()
        monitor = PerformanceMonitor()
        monitor.start_monitoring(interval_seconds=0.5)
        
        # Test message flow with validation
        test_message = {
            "id": "integration_test_001",
            "type": "consciousness.state_change",
            "source": "integration_test",
            "timestamp": "2025-08-19T19:20:00Z",
            "data": {
                "consciousness_level": 0.8,
                "emotional_state": {
                    "valence": 0.5,
                    "arousal": 0.7,
                    "confidence": 0.9
                }
            },
            "priority": 5
        }
        
        # Validate message
        validation_result = validator.validate_nats_message(
            "consciousness.state_change",
            json.dumps(test_message).encode()
        )
        
        if not validation_result.is_valid:
            print(f"Message validation failed: {validation_result.errors}")
            return False
        
        # Publish message
        await js.publish("consciousness.state_change", json.dumps(test_message).encode())
        monitor.record_message(latency_ms=5.0)
        
        # Wait a bit for processing
        await asyncio.sleep(1.0)
        
        # Get metrics
        metrics = monitor.get_current_metrics()
        if metrics.message_count == 0:
            print("No messages recorded in monitor")
            return False
        
        # Cleanup
        monitor.stop_monitoring()
        await nc.close()
        
        print("Full integration test passed")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_full_integration())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_full_integration.py
}

# Function to generate test report
generate_test_report() {
    log "Generating test report..."
    
    local success_rate=0
    if [ $total_tests -gt 0 ]; then
        success_rate=$(( (passed_tests * 100) / total_tests ))
    fi
    
    # Create JSON report
    cat > "$RESULTS_FILE" << EOF
{
    "test_suite": "Phase 3 NATS Integration",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "summary": {
        "total_tests": $total_tests,
        "passed_tests": $passed_tests,
        "failed_tests": $failed_tests,
        "success_rate": $success_rate
    },
    "test_results": {
EOF
    
    local first=true
    for test_name in "${!test_results[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$RESULTS_FILE"
        fi
        echo "        \"$test_name\": \"${test_results[$test_name]}\"" >> "$RESULTS_FILE"
    done
    
    cat >> "$RESULTS_FILE" << EOF
    },
    "environment": {
        "nats_url": "$NATS_URL",
        "test_duration": $TEST_DURATION,
        "load_test_messages": $LOAD_TEST_MESSAGES
    }
}
EOF
    
    log "Test report generated: $RESULTS_FILE"
}

# Main execution
main() {
    log "${BLUE}Starting Phase 3 NATS Integration Testing${NC}"
    log "=========================================="
    
    # Check prerequisites
    if ! check_nats_running; then
        log "${RED}NATS server is required for testing. Please start NATS server first.${NC}"
        log "You can start it with: docker-compose up -d nats"
        exit 1
    fi
    
    # Run all tests
    run_test "Schema Validation" "test_schema_validation"
    run_test "Circuit Breaker" "test_circuit_breaker"
    run_test "Message Persistence" "test_message_persistence"
    run_test "Performance Monitoring" "test_performance_monitoring"
    run_test "JetStream Configuration" "test_jetstream_config"
    run_test "Monitoring and Alerting" "test_monitoring_alerting"
    run_test "Full Integration" "test_full_integration"
    
    # Generate report
    generate_test_report
    
    # Summary
    log ""
    log "=========================================="
    log "${BLUE}Phase 3 Integration Test Summary${NC}"
    log "Total Tests: $total_tests"
    log "${GREEN}Passed: $passed_tests${NC}"
    log "${RED}Failed: $failed_tests${NC}"
    
    local success_rate=0
    if [ $total_tests -gt 0 ]; then
        success_rate=$(( (passed_tests * 100) / total_tests ))
    fi
    log "Success Rate: $success_rate%"
    
    if [ $failed_tests -eq 0 ]; then
        log "${GREEN}🎉 All Phase 3 tests passed!${NC}"
        log "${GREEN}Phase 3 NATS resilience features are ready for production.${NC}"
        exit 0
    else
        log "${RED}❌ Some tests failed. Please check the logs for details.${NC}"
        log "Log file: $LOG_FILE"
        log "Results file: $RESULTS_FILE"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    rm -f /tmp/test_*.py
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"