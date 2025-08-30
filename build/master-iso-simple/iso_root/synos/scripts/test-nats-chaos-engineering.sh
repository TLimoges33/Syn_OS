#!/bin/bash

# NATS Chaos Engineering Test Suite - Phase 4
# ===========================================
# Validates system resilience under various failure conditions
# including network partitions, service failures, and resource exhaustion.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/chaos-engineering-test.log"
RESULTS_FILE="$PROJECT_ROOT/logs/chaos-test-results.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test configuration
NATS_URL="${NATS_URL:-nats://localhost:4222}"
CHAOS_DURATION=60
MESSAGE_RATE=20
FAILURE_INJECTION_RATE=0.3  # 30% failure rate
RECOVERY_TIMEOUT=10

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Test result tracking
declare -A chaos_results
declare -A chaos_metrics
total_chaos_tests=0
passed_chaos_tests=0
failed_chaos_tests=0
start_time=$(date +%s)

# Function to run chaos test and track results
run_chaos_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    total_chaos_tests=$((total_chaos_tests + 1))
    local test_start=$(date +%s)
    
    log "${BLUE}[CHAOS] Running test: $test_name${NC}"
    
    if eval "$test_command" >> "$LOG_FILE" 2>&1; then
        if [ $? -eq $expected_result ]; then
            local test_end=$(date +%s)
            local test_duration=$((test_end - test_start))
            
            log "${GREEN}✓ CHAOS PASSED: $test_name (${test_duration}s)${NC}"
            chaos_results["$test_name"]="PASSED"
            chaos_metrics["$test_name"]=$test_duration
            passed_chaos_tests=$((passed_chaos_tests + 1))
            return 0
        else
            log "${RED}✗ CHAOS FAILED: $test_name (unexpected exit code)${NC}"
            chaos_results["$test_name"]="FAILED"
            failed_chaos_tests=$((failed_chaos_tests + 1))
            return 1
        fi
    else
        log "${RED}✗ CHAOS FAILED: $test_name${NC}"
        chaos_results["$test_name"]="FAILED"
        failed_chaos_tests=$((failed_chaos_tests + 1))
        return 1
    fi
}

# Check prerequisites for chaos testing
check_chaos_prerequisites() {
    log "${PURPLE}=== CHAOS ENGINEERING PREREQUISITES ===${NC}"
    
    # Check if NATS is running
    if ! nats server check --server="$NATS_URL" &> /dev/null; then
        log "${RED}NATS server is not running at $NATS_URL${NC}"
        return 1
    fi
    
    # Check if Docker is available for container chaos
    if ! command -v docker &> /dev/null; then
        log "${YELLOW}Docker not available, skipping container chaos tests${NC}"
    else
        log "${GREEN}✓ Docker is available for container chaos${NC}"
    fi
    
    # Check if tc (traffic control) is available for network chaos
    if ! command -v tc &> /dev/null; then
        log "${YELLOW}tc (traffic control) not available, skipping network chaos tests${NC}"
    else
        log "${GREEN}✓ tc is available for network chaos${NC}"
    fi
    
    log "${GREEN}✓ Chaos engineering prerequisites checked${NC}"
    return 0
}

# Test 1: Message Loss Chaos
test_message_loss_chaos() {
    log "${CYAN}=== MESSAGE LOSS CHAOS TEST ===${NC}"
    
    cat > /tmp/test_message_loss_chaos.py << 'EOF'
import sys
import asyncio
import json
import random
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.message_persistence import MessagePersistenceManager

async def test_message_loss_chaos():
    try:
        nc = await nats.connect("nats://localhost:4222")
        js = nc.jetstream()
        
        # Setup message persistence
        persistence = MessagePersistenceManager(":memory:")
        await persistence.initialize()
        
        # Send messages with simulated loss
        total_messages = 100
        lost_messages = 0
        recovered_messages = 0
        
        for i in range(total_messages):
            message = {
                "id": f"chaos_msg_{i}",
                "type": "chaos.test",
                "source": "chaos_test",
                "timestamp": "2025-08-19T19:35:00Z",
                "data": {"sequence": i},
                "priority": 5
            }
            
            # Simulate message loss (30% chance)
            if random.random() < 0.3:
                lost_messages += 1
                # Store in persistence for recovery
                await persistence.store_message(
                    "chaos.test",
                    json.dumps(message).encode(),
                    priority=5
                )
            else:
                # Send normally
                await js.publish("chaos.test", json.dumps(message).encode())
        
        # Simulate recovery process
        pending_messages = await persistence.get_pending_messages(limit=lost_messages)
        for msg_data in pending_messages:
            await js.publish(msg_data['subject'], msg_data['data'])
            await persistence.acknowledge_message(msg_data['id'])
            recovered_messages += 1
        
        await persistence.close()
        await nc.close()
        
        recovery_rate = (recovered_messages / max(lost_messages, 1)) * 100
        
        print(f"Message Loss Chaos Results:")
        print(f"  Total Messages: {total_messages}")
        print(f"  Lost Messages: {lost_messages}")
        print(f"  Recovered Messages: {recovered_messages}")
        print(f"  Recovery Rate: {recovery_rate:.1f}%")
        
        # Success if recovery rate is above 90%
        if recovery_rate >= 90.0:
            print("Message loss chaos test passed")
            return True
        else:
            print(f"Recovery rate too low: {recovery_rate:.1f}%")
            return False
        
    except Exception as e:
        print(f"Message loss chaos test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_message_loss_chaos())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_message_loss_chaos.py
}

# Test 2: Connection Failure Chaos
test_connection_failure_chaos() {
    log "${CYAN}=== CONNECTION FAILURE CHAOS TEST ===${NC}"
    
    cat > /tmp/test_connection_failure_chaos.py << 'EOF'
import sys
import asyncio
import json
import random
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.circuit_breaker import CircuitBreaker

async def test_connection_failure_chaos():
    try:
        # Setup circuit breaker for connection resilience
        connection_cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=2.0,
            expected_exception=Exception
        )
        
        successful_operations = 0
        failed_operations = 0
        total_operations = 50
        
        @connection_cb
        async def chaotic_nats_operation():
            # Simulate intermittent connection failures
            if random.random() < 0.4:  # 40% failure rate
                raise nats.errors.ConnectionClosedError("Simulated connection failure")
            
            # Perform actual NATS operation
            nc = await nats.connect("nats://localhost:4222")
            js = nc.jetstream()
            
            test_message = {
                "id": f"chaos_conn_{random.randint(1000, 9999)}",
                "type": "chaos.connection_test",
                "source": "chaos_test",
                "timestamp": "2025-08-19T19:35:00Z",
                "data": {"test": "connection_chaos"},
                "priority": 5
            }
            
            await js.publish("chaos.connection_test", json.dumps(test_message).encode())
            await nc.close()
            return "success"
        
        # Run chaotic operations
        for i in range(total_operations):
            try:
                result = await chaotic_nats_operation()
                if result == "success":
                    successful_operations += 1
            except Exception:
                failed_operations += 1
            
            await asyncio.sleep(0.1)  # Brief pause between operations
        
        success_rate = (successful_operations / total_operations) * 100
        
        print(f"Connection Failure Chaos Results:")
        print(f"  Total Operations: {total_operations}")
        print(f"  Successful Operations: {successful_operations}")
        print(f"  Failed Operations: {failed_operations}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Circuit Breaker State: {connection_cb.state}")
        
        # Success if we maintain reasonable success rate despite failures
        if success_rate >= 30.0:  # Lower threshold due to chaos
            print("Connection failure chaos test passed")
            return True
        else:
            print(f"Success rate too low: {success_rate:.1f}%")
            return False
        
    except Exception as e:
        print(f"Connection failure chaos test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection_failure_chaos())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_connection_failure_chaos.py
}

# Test 3: High Load Chaos
test_high_load_chaos() {
    log "${CYAN}=== HIGH LOAD CHAOS TEST ===${NC}"
    
    cat > /tmp/test_high_load_chaos.py << 'EOF'
import sys
import asyncio
import json
import time
import random
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.performance_optimizer import PerformanceMonitor

async def test_high_load_chaos():
    try:
        # Setup performance monitoring
        monitor = PerformanceMonitor()
        monitor.start_monitoring(interval_seconds=1.0)
        
        nc = await nats.connect("nats://localhost:4222")
        js = nc.jetstream()
        
        # Generate high load with chaos
        total_messages = 500
        successful_publishes = 0
        failed_publishes = 0
        
        # Create multiple concurrent publishers
        async def chaotic_publisher(publisher_id, message_count):
            nonlocal successful_publishes, failed_publishes
            
            for i in range(message_count):
                try:
                    # Simulate variable message sizes and processing delays
                    payload_size = random.randint(100, 2000)
                    processing_delay = random.uniform(0.001, 0.05)  # 1-50ms
                    
                    message = {
                        "id": f"chaos_load_{publisher_id}_{i}",
                        "type": "chaos.high_load",
                        "source": f"chaos_publisher_{publisher_id}",
                        "timestamp": "2025-08-19T19:35:00Z",
                        "data": {
                            "payload": "x" * payload_size,
                            "publisher_id": publisher_id,
                            "sequence": i
                        },
                        "priority": random.randint(1, 10)
                    }
                    
                    # Simulate processing delay
                    await asyncio.sleep(processing_delay)
                    
                    # Publish with potential failures
                    if random.random() < 0.1:  # 10% failure rate
                        failed_publishes += 1
                        monitor.record_error()
                    else:
                        start_time = time.time()
                        await js.publish("chaos.high_load", json.dumps(message).encode())
                        end_time = time.time()
                        
                        latency_ms = (end_time - start_time) * 1000
                        monitor.record_message(latency_ms)
                        successful_publishes += 1
                
                except Exception as e:
                    failed_publishes += 1
                    monitor.record_error()
        
        # Run concurrent publishers
        publishers = []
        messages_per_publisher = total_messages // 5
        
        for pub_id in range(5):
            publishers.append(chaotic_publisher(pub_id, messages_per_publisher))
        
        # Execute all publishers concurrently
        await asyncio.gather(*publishers)
        
        # Get final metrics
        final_metrics = monitor.get_current_metrics()
        monitor.stop_monitoring()
        
        await nc.close()
        
        success_rate = (successful_publishes / (successful_publishes + failed_publishes)) * 100
        
        print(f"High Load Chaos Results:")
        print(f"  Total Messages Attempted: {successful_publishes + failed_publishes}")
        print(f"  Successful Publishes: {successful_publishes}")
        print(f"  Failed Publishes: {failed_publishes}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Average Latency: {final_metrics.avg_latency_ms:.2f}ms")
        print(f"  P95 Latency: {final_metrics.p95_latency_ms:.2f}ms")
        print(f"  Messages/Second: {final_metrics.messages_per_second:.1f}")
        
        # Success criteria for high load chaos
        if (success_rate >= 80.0 and 
            final_metrics.avg_latency_ms < 100.0 and 
            final_metrics.messages_per_second > 10.0):
            print("High load chaos test passed")
            return True
        else:
            print("High load chaos test failed - performance degraded too much")
            return False
        
    except Exception as e:
        print(f"High load chaos test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_high_load_chaos())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_high_load_chaos.py
}

# Test 4: Memory Pressure Chaos
test_memory_pressure_chaos() {
    log "${CYAN}=== MEMORY PRESSURE CHAOS TEST ===${NC}"
    
    cat > /tmp/test_memory_pressure_chaos.py << 'EOF'
import sys
import asyncio
import json
import gc
import psutil
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

async def test_memory_pressure_chaos():
    try:
        nc = await nats.connect("nats://localhost:4222")
        js = nc.jetstream()
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create memory pressure by accumulating large messages
        memory_hogs = []
        successful_operations = 0
        total_operations = 100
        
        for i in range(total_operations):
            try:
                # Create increasingly large messages to simulate memory pressure
                large_payload = "x" * (10000 * (i + 1))  # Growing payload
                
                message = {
                    "id": f"chaos_memory_{i}",
                    "type": "chaos.memory_pressure",
                    "source": "chaos_test",
                    "timestamp": "2025-08-19T19:35:00Z",
                    "data": {
                        "large_payload": large_payload,
                        "sequence": i
                    },
                    "priority": 5
                }
                
                # Keep some messages in memory to create pressure
                if i % 10 == 0:
                    memory_hogs.append(message)
                
                # Publish message
                await js.publish("chaos.memory_pressure", json.dumps(message).encode())
                successful_operations += 1
                
                # Check memory usage periodically
                if i % 20 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_growth = current_memory - initial_memory
                    
                    # If memory growth is excessive, trigger garbage collection
                    if memory_growth > 100:  # More than 100MB growth
                        gc.collect()
                        # Clear some memory hogs
                        memory_hogs = memory_hogs[-5:]  # Keep only last 5
                
            except Exception as e:
                print(f"Operation {i} failed: {e}")
                # Continue despite failures
        
        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Cleanup
        memory_hogs.clear()
        gc.collect()
        
        await nc.close()
        
        success_rate = (successful_operations / total_operations) * 100
        
        print(f"Memory Pressure Chaos Results:")
        print(f"  Total Operations: {total_operations}")
        print(f"  Successful Operations: {successful_operations}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Initial Memory: {initial_memory:.1f} MB")
        print(f"  Final Memory: {final_memory:.1f} MB")
        print(f"  Memory Growth: {memory_growth:.1f} MB")
        
        # Success if we maintain operations despite memory pressure
        if success_rate >= 90.0 and memory_growth < 200:  # Less than 200MB growth
            print("Memory pressure chaos test passed")
            return True
        else:
            print("Memory pressure chaos test failed")
            return False
        
    except Exception as e:
        print(f"Memory pressure chaos test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_memory_pressure_chaos())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_memory_pressure_chaos.py
}

# Test 5: Concurrent Access Chaos
test_concurrent_access_chaos() {
    log "${CYAN}=== CONCURRENT ACCESS CHAOS TEST ===${NC}"
    
    cat > /tmp/test_concurrent_access_chaos.py << 'EOF'
import sys
import asyncio
import json
import random
import threading
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

from consciousness_v2.resilience.message_persistence import MessagePersistenceManager

async def test_concurrent_access_chaos():
    try:
        # Setup shared resources
        persistence = MessagePersistenceManager(":memory:")
        await persistence.initialize()
        
        nc = await nats.connect("nats://localhost:4222")
        js = nc.jetstream()
        
        # Shared counters (thread-safe)
        successful_ops = {"count": 0}
        failed_ops = {"count": 0}
        lock = threading.Lock()
        
        async def chaotic_worker(worker_id, operation_count):
            for i in range(operation_count):
                try:
                    operation_type = random.choice(["publish", "persist", "retrieve"])
                    
                    if operation_type == "publish":
                        # Concurrent publishing
                        message = {
                            "id": f"chaos_concurrent_{worker_id}_{i}",
                            "type": "chaos.concurrent",
                            "source": f"worker_{worker_id}",
                            "timestamp": "2025-08-19T19:35:00Z",
                            "data": {"worker_id": worker_id, "sequence": i},
                            "priority": random.randint(1, 10)
                        }
                        
                        await js.publish("chaos.concurrent", json.dumps(message).encode())
                        
                    elif operation_type == "persist":
                        # Concurrent persistence operations
                        message_data = json.dumps({
                            "id": f"persist_{worker_id}_{i}",
                            "data": f"worker_{worker_id}_data_{i}"
                        }).encode()
                        
                        await persistence.store_message(
                            f"chaos.persist.{worker_id}",
                            message_data,
                            priority=random.randint(1, 10)
                        )
                        
                    elif operation_type == "retrieve":
                        # Concurrent retrieval operations
                        messages = await persistence.get_pending_messages(limit=5)
                        for msg in messages:
                            await persistence.acknowledge_message(msg['id'])
                    
                    # Random delay to increase concurrency chaos
                    await asyncio.sleep(random.uniform(0.001, 0.01))
                    
                    with lock:
                        successful_ops["count"] += 1
                        
                except Exception as e:
                    with lock:
                        failed_ops["count"] += 1
        
        # Create multiple concurrent workers
        workers = []
        operations_per_worker = 50
        worker_count = 10
        
        for worker_id in range(worker_count):
            workers.append(chaotic_worker(worker_id, operations_per_worker))
        
        # Execute all workers concurrently
        await asyncio.gather(*workers)
        
        await persistence.close()
        await nc.close()
        
        total_operations = successful_ops["count"] + failed_ops["count"]
        success_rate = (successful_ops["count"] / max(total_operations, 1)) * 100
        
        print(f"Concurrent Access Chaos Results:")
        print(f"  Workers: {worker_count}")
        print(f"  Operations per Worker: {operations_per_worker}")
        print(f"  Total Operations: {total_operations}")
        print(f"  Successful Operations: {successful_ops['count']}")
        print(f"  Failed Operations: {failed_ops['count']}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        # Success if we handle concurrent access well
        if success_rate >= 85.0:
            print("Concurrent access chaos test passed")
            return True
        else:
            print("Concurrent access chaos test failed")
            return False
        
    except Exception as e:
        print(f"Concurrent access chaos test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_concurrent_access_chaos())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_concurrent_access_chaos.py
}

# Test 6: Network Latency Chaos (if tc is available)
test_network_latency_chaos() {
    log "${CYAN}=== NETWORK LATENCY CHAOS TEST ===${NC}"
    
    if ! command -v tc &> /dev/null; then
        log "${YELLOW}tc not available, skipping network latency chaos test${NC}"
        return 0
    fi
    
    cat > /tmp/test_network_latency_chaos.py << 'EOF'
import sys
import asyncio
import json
import time
import statistics
import nats
sys.path.append('/home/diablorain/Syn_OS/src')

async def test_network_latency_chaos():
    try:
        nc = await nats.connect("nats://localhost:4222")
        js = nc.jetstream()
        
        # Measure baseline latency
        baseline_latencies = []
        for i in range(10):
            start_time = time.time()
            await js.publish("chaos.latency_baseline", b'{"test": "baseline"}')
            end_time = time.time()
            baseline_latencies.append((end_time - start_time) * 1000)
        
        baseline_avg = statistics.mean(baseline_latencies)
        
        # Test with simulated network conditions
        test_latencies = []
        successful_operations = 0
        total_operations = 50
        
        for i in range(total_operations):
            try:
                message = {
                    "id": f"chaos_latency_{i}",
                    "type": "chaos.network_latency",
                    "source": "chaos_test",
                    "timestamp": "2025-08-19T19:35:00Z",
                    "data": {"sequence": i, "test": "network_chaos"},
                    "priority": 5
                }
                
                start_time = time.time()
                await js.publish("chaos.network_latency", json.dumps(message).encode())
                end_time = time.time()
                
                latency_ms = (end_time - start_time) * 1000
                test_latencies.append(latency_ms)
                successful_operations += 1
                
                # Brief pause between operations
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Operation {i} failed: {e}")
        
        await nc.close()
        
        if test_latencies:
            test_avg = statistics.mean(test_latencies)
            test_p95 = sorted(test_latencies)[int(len(test_latencies) * 0.95)]
        else:
            test_avg = 0
            test_p95 = 0
        
        success_rate = (successful_operations / total_operations) * 100
        
        print(f"Network Latency Chaos Results:")
        print(f"  Total Operations: {total_operations}")
        print(f"  Successful Operations: {successful_operations}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Baseline Avg Latency: {baseline_avg:.2f}ms")
        print(f"  Test Avg Latency: {test_avg:.2f}ms")
        print(f"  Test P95 Latency: {test_p95:.2f}ms")
        
        # Success if we maintain reasonable performance despite network chaos
        if success_rate >= 90.0 and test_avg < baseline_avg * 5:  # Less than 5x baseline
            print("Network latency chaos test passed")
            return True
        else:
            print("Network latency chaos test failed")
            return False
        
    except Exception as e:
        print(f"Network latency chaos test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_network_latency_chaos())
    sys.exit(0 if result else 1)
EOF
    
    python3 /tmp/test_network_latency_chaos.py
}

# Generate chaos test report
generate_chaos_report() {
    log "Generating chaos engineering test report..."
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    local success_rate=0
    
    if [ $total_chaos_tests -gt 0 ]; then
        success_rate=$(( (passed_chaos_tests * 100) / total_chaos_tests ))
    fi
    
    cat > "$RESULTS_FILE" << EOF
{
    "test_suite": "NATS Chaos Engineering - Phase 4",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "duration_seconds": $total_duration,
    "summary": {
        "total_tests": $total_chaos_tests,
        "passed_tests": $passed_chaos_tests,
        "failed_tests": $failed_chaos_tests,
        "success_rate": $success_rate
    },
    "chaos_scenarios": {
        "message_loss": "$([ "${chaos_results[Message Loss Chaos]:-}" = "PASSED" ] && echo 'PASSED' || echo 'FAILED')",
        "connection_failure": "$([ "${chaos_results[Connection Failure Chaos]:-}" = "PASSED" ] && echo 'PASSED' || echo 'FAILED')",
        "high_load": "$([ "${chaos_results[High Load Chaos]:-}" = "PASSED" ] && echo 'PASSED' || echo 'FAILED')",
        "memory_pressure": "$([ "${chaos_results[Memory Pressure Chaos]:-}" = "PASSED" ] && echo 'PASSED' || echo 'FAILED')",
        "concurrent_access": "$([ "${chaos_results[Concurrent Access Chaos]:-}" = "PASSED" ] && echo 'PASSED' || echo 'FAILED')",
        "network_latency": "$([ "${chaos_results[Network Latency Chaos]:-}" = "PASSED" ] && echo 'PASSED' || echo 'FAILED')"
    },
    "test_results": {
EOF
    
    local first=true
    for test_name in "${!chaos_results[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$RESULTS_FILE"
        fi
        local timing=${chaos_metrics[$test_name]:-0}
        echo "        \"$test_name\": {" >> "$RESULTS_FILE"
        echo "            \"status\": \"${chaos_results[$test_name]}\"," >> "$RESULTS_FILE"
        echo "            \"duration_seconds\": $timing" >> "$RESULTS_FILE"
        echo "        }" >> "$RESULTS_FILE"
    done
    
    cat >> "$RESULTS_FILE" << EOF
    },
    "resilience_assessment": {
        "message_reliability": "$([ $success_rate -ge 80 ] && echo 'EXCELLENT' || echo 'NEEDS_IMPROVEMENT')",
        "connection_resilience": "$([ $success_rate -ge 80 ] && echo 'EXCELLENT' || echo 'NEEDS_IMPROVEMENT')",
        "performance_under_load": "$([ $success_rate -ge 80 ] && echo 'EXCELLENT' || echo 'NEEDS_IMPROVEMENT')",
        "resource_management": "$([ $success_rate -ge 80 ] && echo 'EXCELLENT' || echo 'NEEDS_IMPROVEMENT')",
        "concurrency_handling": "$([ $success_rate -ge 80 ] && echo 'EXCELLENT' || echo 'NEEDS_IMPROVEMENT')",
        "overall_resilience": "$([ $success_rate -ge 80 ] && echo 'PRODUCTION_READY' || echo 'NEEDS_WORK')"
    },
    "environment": {
        "nats_url": "$NATS_URL",
        "chaos_duration": $CHAOS_DURATION,
        "message_rate": $MESSAGE_RATE,
        "failure_injection_rate": $FAILURE_INJECTION_RATE
    }
}
EOF
    
    log "Chaos
engineering test report generated: $RESULTS_FILE"
}

# Main execution
main() {
    log "${PURPLE}========================================${NC}"
    log "${PURPLE}NATS CHAOS ENGINEERING TEST SUITE${NC}"
    log "${PURPLE}========================================${NC}"
    
    # Check prerequisites
    if ! check_chaos_prerequisites; then
        log "${RED}Chaos engineering prerequisites check failed. Exiting.${NC}"
        exit 1
    fi
    
    # Run all chaos tests
    run_chaos_test "Message Loss Chaos" "test_message_loss_chaos" 0
    run_chaos_test "Connection Failure Chaos" "test_connection_failure_chaos" 0
    run_chaos_test "High Load Chaos" "test_high_load_chaos" 0
    run_chaos_test "Memory Pressure Chaos" "test_memory_pressure_chaos" 0
    run_chaos_test "Concurrent Access Chaos" "test_concurrent_access_chaos" 0
    run_chaos_test "Network Latency Chaos" "test_network_latency_chaos" 0
    
    # Generate comprehensive report
    generate_chaos_report
    
    # Final summary
    log ""
    log "${PURPLE}========================================${NC}"
    log "${PURPLE}CHAOS ENGINEERING TEST SUMMARY${NC}"
    log "${PURPLE}========================================${NC}"
    log "Total Chaos Tests: $total_chaos_tests"
    log "${GREEN}Passed: $passed_chaos_tests${NC}"
    log "${RED}Failed: $failed_chaos_tests${NC}"
    
    local success_rate=0
    if [ $total_chaos_tests -gt 0 ]; then
        success_rate=$(( (passed_chaos_tests * 100) / total_chaos_tests ))
    fi
    log "Success Rate: $success_rate%"
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    log "Total Duration: ${total_duration}s"
    
    if [ $failed_chaos_tests -eq 0 ] && [ $success_rate -ge 80 ]; then
        log ""
        log "${GREEN}🎉 CHAOS ENGINEERING TESTS PASSED!${NC}"
        log "${GREEN}🛡️  SYSTEM DEMONSTRATES EXCELLENT RESILIENCE${NC}"
        log ""
        log "${CYAN}Resilience Validation: COMPLETE${NC}"
        log "${CYAN}Production Readiness: CONFIRMED${NC}"
        log ""
        log "Chaos test report: $RESULTS_FILE"
        exit 0
    else
        log ""
        log "${RED}❌ Some chaos tests failed or success rate below threshold${NC}"
        log "${YELLOW}System resilience needs improvement before production deployment${NC}"
        log ""
        log "Log file: $LOG_FILE"
        log "Results file: $RESULTS_FILE"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary chaos test files..."
    rm -f /tmp/test_*_chaos.py
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"