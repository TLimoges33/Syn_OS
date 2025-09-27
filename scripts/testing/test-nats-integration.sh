#!/bin/bash

# =========================================================
# Syn_OS NATS Integration Testing Script
# =========================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NATS_VERSION="2.10.5"
NATS_PORT=4222
NATS_MONITOR_PORT=8222
NATS_CONTAINER="synos-nats-test"
TEST_TIMEOUT=30

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

print_status() {
    local status=$1
    local message=$2

    case $status in
        "success")
            echo -e "${GREEN}✓${NC} $message"
            ((TESTS_PASSED++))
            ;;
        "error")
            echo -e "${RED}✗${NC} $message"
            ((TESTS_FAILED++))
            ;;
        "info")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
        "warning")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
    esac
}

cleanup() {
    print_status "info" "Cleaning up..."
    docker stop $NATS_CONTAINER 2>/dev/null || true
    docker rm $NATS_CONTAINER 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

echo "========================================="
echo "    NATS Integration Test Suite"
echo "========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    print_status "error" "Docker is not installed"
    exit 1
fi

# Start NATS server
print_status "info" "Starting NATS server..."
docker run -d \
    --name $NATS_CONTAINER \
    -p $NATS_PORT:4222 \
    -p $NATS_MONITOR_PORT:8222 \
    nats:$NATS_VERSION \
    -js \
    -m 8222 \
    --store_dir /tmp/nats-storage \
    --max_payload 10MB

# Wait for NATS to be ready
print_status "info" "Waiting for NATS to be ready..."
sleep 3

# Check NATS health
if curl -s http://localhost:$NATS_MONITOR_PORT/healthz | grep -q "ok"; then
    print_status "success" "NATS server is healthy"
else
    print_status "error" "NATS server health check failed"
    exit 1
fi

# Test Python NATS client
print_status "info" "Testing Python NATS client..."
python3 - <<EOF
import asyncio
import sys

try:
    import nats
    from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
    print("✓ NATS Python client imported successfully")
except ImportError as e:
    print(f"✗ Failed to import NATS client: {e}")
    print("  Install with: pip3 install nats-py")
    sys.exit(1)

async def test_nats_connection():
    try:
        # Connect to NATS
        nc = await nats.connect("nats://localhost:$NATS_PORT")
        print("✓ Connected to NATS server")

        # Create JetStream context
        js = nc.jetstream()
        print("✓ JetStream context created")

        # Add a stream
        await js.add_stream(
            name="TEST-STREAM",
            subjects=["test.>"],
            retention="limits",
            max_msgs=10000,
            max_bytes=1048576,
            max_age=86400
        )
        print("✓ Test stream created")

        # Publish a test message
        ack = await js.publish("test.message", b"Hello Syn_OS!")
        print(f"✓ Published test message (seq: {ack.seq})")

        # Subscribe and receive
        received = []

        async def message_handler(msg):
            received.append(msg)
            await msg.ack()

        sub = await js.subscribe("test.>", cb=message_handler)

        # Wait briefly for message
        await asyncio.sleep(0.5)

        if received:
            print(f"✓ Received message: {received[0].data.decode()}")
        else:
            print("✗ No message received")

        await nc.close()
        print("✓ Connection closed cleanly")
        return True

    except Exception as e:
        print(f"✗ NATS test failed: {e}")
        return False

# Run the test
result = asyncio.run(test_nats_connection())
sys.exit(0 if result else 1)
EOF

if [ $? -eq 0 ]; then
    print_status "success" "Python NATS integration test passed"
else
    print_status "error" "Python NATS integration test failed"
fi

# Test NATS CLI if available
if command -v nats &> /dev/null; then
    print_status "info" "Testing NATS CLI..."

    # Test server info
    if nats server info -s localhost:$NATS_PORT &>/dev/null; then
        print_status "success" "NATS CLI can connect to server"
    else
        print_status "error" "NATS CLI connection failed"
    fi
else
    print_status "warning" "NATS CLI not installed (optional)"
fi

# Test JetStream functionality
print_status "info" "Testing JetStream functionality..."
python3 - <<EOF
import asyncio
import json
import sys

try:
    import nats
except ImportError:
    sys.exit(1)

async def test_jetstream():
    try:
        nc = await nats.connect("nats://localhost:$NATS_PORT")
        js = nc.jetstream()

        # Test consciousness event stream
        await js.add_stream(
            name="CONSCIOUSNESS-EVENTS",
            subjects=["consciousness.>", "events.>"],
            retention="limits",
            max_msgs=100000,
            duplicate_window=60
        )
        print("✓ Consciousness event stream created")

        # Test security alert stream
        await js.add_stream(
            name="SECURITY-ALERTS",
            subjects=["security.alerts.>"],
            retention="workqueue",
            max_msgs=1000
        )
        print("✓ Security alert stream created")

        # Test service coordination stream
        await js.add_stream(
            name="SERVICE-COORDINATION",
            subjects=["service.>"],
            retention="limits",
            max_msgs=50000
        )
        print("✓ Service coordination stream created")

        # Publish test events
        events = [
            ("consciousness.startup", json.dumps({"event": "system_boot", "timestamp": "now"})),
            ("security.alerts.info", json.dumps({"level": "info", "message": "test"})),
            ("service.health", json.dumps({"service": "test", "status": "healthy"}))
        ]

        for subject, payload in events:
            await js.publish(subject, payload.encode())

        print("✓ Test events published")

        # Get stream info
        info = await js.stream_info("CONSCIOUSNESS-EVENTS")
        print(f"✓ Stream info retrieved: {info.config.name}")

        await nc.close()
        return True

    except Exception as e:
        print(f"✗ JetStream test failed: {e}")
        return False

result = asyncio.run(test_jetstream())
sys.exit(0 if result else 1)
EOF

if [ $? -eq 0 ]; then
    print_status "success" "JetStream functionality test passed"
else
    print_status "error" "JetStream functionality test failed"
fi

# Test message patterns for Syn_OS
print_status "info" "Testing Syn_OS message patterns..."
python3 - <<EOF
import asyncio
import json
import sys
import time

try:
    import nats
except ImportError:
    sys.exit(1)

async def test_synos_patterns():
    try:
        nc = await nats.connect("nats://localhost:$NATS_PORT")
        js = nc.jetstream()

        test_passed = True

        # Test request-reply pattern
        async def responder(msg):
            await msg.respond(b"acknowledged")

        await nc.subscribe("system.ping", cb=responder)

        try:
            response = await nc.request("system.ping", b"ping", timeout=1)
            if response.data == b"acknowledged":
                print("✓ Request-reply pattern working")
            else:
                print("✗ Request-reply pattern failed")
                test_passed = False
        except:
            print("✗ Request-reply timeout")
            test_passed = False

        # Test publish-subscribe pattern
        messages_received = []

        async def subscriber(msg):
            messages_received.append(msg)

        sub = await nc.subscribe("broadcast.>", cb=subscriber)

        await nc.publish("broadcast.test", b"broadcast message")
        await asyncio.sleep(0.5)

        if messages_received:
            print("✓ Publish-subscribe pattern working")
        else:
            print("✗ Publish-subscribe pattern failed")
            test_passed = False

        # Test queue groups for load balancing
        queue_count = [0, 0]

        async def queue_handler1(msg):
            queue_count[0] += 1

        async def queue_handler2(msg):
            queue_count[1] += 1

        await nc.subscribe("work.queue", "workers", queue_handler1)
        await nc.subscribe("work.queue", "workers", queue_handler2)

        for i in range(10):
            await nc.publish("work.queue", f"work-{i}".encode())

        await asyncio.sleep(0.5)

        if sum(queue_count) == 10:
            print(f"✓ Queue groups working (distribution: {queue_count})")
        else:
            print(f"✗ Queue groups failed (received: {sum(queue_count)}/10)")
            test_passed = False

        await nc.close()
        return test_passed

    except Exception as e:
        print(f"✗ Pattern test failed: {e}")
        return False

result = asyncio.run(test_synos_patterns())
sys.exit(0 if result else 1)
EOF

if [ $? -eq 0 ]; then
    print_status "success" "Syn_OS message patterns test passed"
else
    print_status "error" "Syn_OS message patterns test failed"
fi

echo ""
echo "========================================="
echo "          Test Summary"
echo "========================================="

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! ($TESTS_PASSED/$TOTAL_TESTS)${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    echo -e "  Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "  Failed: ${RED}$TESTS_FAILED${NC}"
    exit 1
fi