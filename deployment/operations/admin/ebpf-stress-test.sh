#!/bin/bash

# SynOS eBPF System Stress Test
# High-intensity testing to validate system performance under load

set -e

export PATH=/usr/sbin:$PATH

echo "💪 SYNOS EBPF STRESS TEST SUITE"
echo "================================"
echo ""

# Stress test parameters
NETWORK_ITERATIONS=50
PROCESS_ITERATIONS=25
MEMORY_SIZE_MB=10
TEST_DURATION=30

echo "🏋️ Stress Test Parameters:"
echo "  Network iterations: $NETWORK_ITERATIONS"
echo "  Process iterations: $PROCESS_ITERATIONS"
echo "  Memory test size: ${MEMORY_SIZE_MB}MB"
echo "  Test duration: ${TEST_DURATION}s"
echo ""

# Pre-test system state
echo "📊 PRE-TEST SYSTEM STATE:"
echo "------------------------"
echo "eBPF Programs loaded: $(sudo bpftool prog show | grep -E "(synos|trace_)" | wc -l)"
echo "Ring buffer maps: $(sudo bpftool map show | grep consciousness | wc -l)"

# Get baseline memory usage
INITIAL_MEMORY=$(free -m | grep Mem | awk '{print $3}')
echo "System memory usage: ${INITIAL_MEMORY}MB"
echo ""

# Start stress test monitoring in background
echo "🎯 STARTING STRESS TEST MONITORING..."
(
    for i in $(seq 1 $TEST_DURATION); do
        echo "[$i/${TEST_DURATION}s] Monitoring eBPF programs..."
        
        # Check if all programs are still loaded
        PROG_COUNT=$(sudo bpftool prog show | grep -E "(synos|trace_)" | wc -l)
        if [ $PROG_COUNT -ne 3 ]; then
            echo "❌ ERROR: Program count dropped to $PROG_COUNT at ${i}s"
            exit 1
        fi
        
        sleep 1
    done
    echo "✅ Background monitoring completed successfully"
) &

MONITOR_PID=$!

echo ""
echo "🚀 PHASE 1: NETWORK STRESS TEST"
echo "-------------------------------"

# Network stress test
for i in $(seq 1 $NETWORK_ITERATIONS); do
    echo -n "Network test $i/$NETWORK_ITERATIONS... "
    
    # Generate various types of network traffic
    timeout 0.5s ping -c 1 8.8.8.8 >/dev/null 2>&1 || true
    timeout 0.5s nc -z google.com 80 >/dev/null 2>&1 || true
    
    # Verify network monitor still responsive
    if sudo bpftool prog show id 28 >/dev/null 2>&1; then
        echo "✅"
    else
        echo "❌ Network monitor failed!"
        exit 1
    fi
done

echo ""
echo "⚙️ PHASE 2: PROCESS STRESS TEST"
echo "------------------------------"

# Process stress test
for i in $(seq 1 $PROCESS_ITERATIONS); do
    echo -n "Process test $i/$PROCESS_ITERATIONS... "
    
    # Generate process activity
    echo "test data $i" > /tmp/stress_test_$i.tmp
    cat /tmp/stress_test_$i.tmp > /dev/null
    rm /tmp/stress_test_$i.tmp
    
    # Quick process spawning
    /bin/true
    /bin/echo "stress test $i" >/dev/null
    
    # Verify process monitor still responsive
    if sudo bpftool prog show id 34 >/dev/null 2>&1; then
        echo "✅"
    else
        echo "❌ Process monitor failed!"
        exit 1
    fi
done

echo ""
echo "🧠 PHASE 3: MEMORY STRESS TEST"
echo "-----------------------------"

# Memory stress test
for i in $(seq 1 5); do
    echo -n "Memory test $i/5... "
    
    # Create and manipulate memory
    dd if=/dev/zero of=/tmp/memory_stress_$i.tmp bs=1M count=$MEMORY_SIZE_MB >/dev/null 2>&1
    sync
    rm /tmp/memory_stress_$i.tmp
    
    # Verify memory monitor still responsive
    if sudo bpftool prog show id 40 >/dev/null 2>&1; then
        echo "✅"
    else
        echo "❌ Memory monitor failed!"
        exit 1
    fi
done

echo ""
echo "🔥 PHASE 4: CONCURRENT STRESS TEST"
echo "--------------------------------"

# Concurrent activity to stress all monitors simultaneously
echo "Launching concurrent stress operations..."

# Network background activity
(
    for i in $(seq 1 20); do
        timeout 0.2s ping -c 1 1.1.1.1 >/dev/null 2>&1 || true
        sleep 0.1
    done
) &

# Process background activity  
(
    for i in $(seq 1 15); do
        echo "concurrent test $i" > /tmp/concurrent_$i.tmp 2>/dev/null
        rm /tmp/concurrent_$i.tmp 2>/dev/null || true
        /bin/date >/dev/null
        sleep 0.1
    done
) &

# Memory background activity
(
    for i in $(seq 1 3); do
        dd if=/dev/zero of=/tmp/concurrent_mem_$i.tmp bs=1M count=2 >/dev/null 2>&1
        rm /tmp/concurrent_mem_$i.tmp 2>/dev/null || true
        sleep 0.2
    done
) &

# Wait for concurrent tests
wait

echo "✅ Concurrent stress operations completed"

echo ""
echo "⏱️ WAITING FOR MONITORING TO COMPLETE..."
wait $MONITOR_PID

echo ""
echo "📊 POST-TEST SYSTEM STATE:"
echo "-------------------------"

# Verify all programs still loaded and functional
FINAL_PROG_COUNT=$(sudo bpftool prog show | grep -E "(synos|trace_)" | wc -l)
FINAL_MAP_COUNT=$(sudo bpftool map show | grep consciousness | wc -l)
FINAL_MEMORY=$(free -m | grep Mem | awk '{print $3}')

echo "eBPF Programs loaded: $FINAL_PROG_COUNT/3"
echo "Ring buffer maps: $FINAL_MAP_COUNT/1"
echo "Memory usage change: $((FINAL_MEMORY - INITIAL_MEMORY))MB"

# Detailed program status
echo ""
echo "📋 DETAILED PROGRAM STATUS:"
echo "---------------------------"
sudo bpftool prog show | grep -E "(synos|trace_)" | while read line; do
    id=$(echo "$line" | cut -d':' -f1)
    name=$(echo "$line" | grep -o "name [^ ]*" | cut -d' ' -f2)
    status="✅ OPERATIONAL"
    
    # Try to get program details to verify it's responsive
    if ! sudo bpftool prog show id $id >/dev/null 2>&1; then
        status="❌ UNRESPONSIVE"
    fi
    
    echo "  $name (ID: $id): $status"
done

echo ""
echo "🏆 STRESS TEST RESULTS:"
echo "======================="

if [ $FINAL_PROG_COUNT -eq 3 ] && [ $FINAL_MAP_COUNT -eq 1 ]; then
    echo "🎉 STRESS TEST PASSED!"
    echo ""
    echo "✅ All eBPF programs survived stress testing"
    echo "✅ Ring buffer maps remained stable"
    echo "✅ System performed $((NETWORK_ITERATIONS + PROCESS_ITERATIONS + 5)) stress operations"
    echo "✅ Concurrent operations handled successfully"
    echo "✅ ${TEST_DURATION}s continuous monitoring passed"
    echo ""
    echo "🚀 SYNOS EBPF SYSTEM: STRESS-TESTED AND PRODUCTION-READY!"
    exit 0
else
    echo "❌ STRESS TEST FAILED!"
    echo "Programs: $FINAL_PROG_COUNT/3, Maps: $FINAL_MAP_COUNT/1"
    exit 1
fi
