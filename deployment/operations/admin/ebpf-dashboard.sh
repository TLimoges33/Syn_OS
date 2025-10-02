#!/bin/bash

# SynOS eBPF Enhanced Security Monitoring Dashboard
# Real-time monitoring and control interface

set -e

export PATH=/usr/sbin:$PATH

echo "=========================================="
echo "   SynOS eBPF Security Monitoring        "
echo "   Enhanced Real-Time Dashboard          "
echo "=========================================="
echo ""

# Check if eBPF programs are loaded
echo "📊 eBPF Program Status:"
echo "----------------------------------------"

NETWORK_PROG=$(sudo bpftool prog show | grep "synos_network_monitor" || echo "")
PROCESS_PROG=$(sudo bpftool prog show | grep "trace_process_basic" || echo "")
MEMORY_PROG=$(sudo bpftool prog show | grep "trace_memory_basic" || echo "")

if [ -n "$NETWORK_PROG" ]; then
    echo "✅ Network Monitor: LOADED"
    echo "   $NETWORK_PROG"
else
    echo "❌ Network Monitor: NOT LOADED"
fi

if [ -n "$PROCESS_PROG" ]; then
    echo "✅ Process Monitor: LOADED"
    echo "   $PROCESS_PROG"
else
    echo "❌ Process Monitor: NOT LOADED"
fi

if [ -n "$MEMORY_PROG" ]; then
    echo "✅ Memory Monitor: LOADED"
    echo "   $MEMORY_PROG"
else
    echo "❌ Memory Monitor: NOT LOADED"
fi

echo ""

# Check eBPF maps
echo "🗄️  eBPF Maps Status:"
echo "----------------------------------------"
MAPS=$(sudo bpftool map show | grep -E "(consciousness|synos)" || echo "")
if [ -n "$MAPS" ]; then
    echo "✅ Consciousness Maps Active:"
    echo "$MAPS"
else
    echo "❌ No SynOS eBPF maps found"
fi

echo ""

# Check network interfaces with XDP
echo "🌐 Network Interface Status:"
echo "----------------------------------------"
for iface in $(ip link show | grep -E '^[0-9]+:' | cut -d':' -f2 | tr -d ' ' | grep -v lo); do
    XDP_STATUS=$(ip link show $iface | grep -o "xdp.*" || echo "none")
    if [ "$XDP_STATUS" != "none" ]; then
        echo "✅ $iface: XDP attached ($XDP_STATUS)"
    else
        echo "⚠️  $iface: No XDP program"
    fi
done

echo ""

# System resource usage
echo "⚡ System Resources:"
echo "----------------------------------------"
MEMORY_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "Memory: $MEMORY_USAGE"
echo "CPU: ${CPU_USAGE}%"

echo ""

# eBPF program details
echo "🔍 eBPF Program Details:"
echo "----------------------------------------"
if [ -n "$NETWORK_PROG" ]; then
    PROG_ID=$(echo "$NETWORK_PROG" | cut -d':' -f1)
    echo "Network Monitor (ID: $PROG_ID):"
    sudo bpftool prog show id $PROG_ID --pretty 2>/dev/null | head -10 || echo "  Details unavailable"
    echo ""
fi

# Show recent kernel log messages related to eBPF
echo "📋 Recent eBPF Kernel Messages:"
echo "----------------------------------------"
RECENT_LOGS=$(dmesg | grep -i "bpf\|xdp" | tail -5 || echo "No recent eBPF messages")
if [ "$RECENT_LOGS" != "No recent eBPF messages" ]; then
    echo "$RECENT_LOGS"
else
    echo "No recent eBPF kernel messages"
fi

echo ""

# Consciousness Integration Status
echo "🧠 Consciousness Integration:"
echo "----------------------------------------"
if pgrep -f "syn.*consciousness" > /dev/null; then
    echo "✅ Consciousness System: RUNNING"
else
    echo "⚠️  Consciousness System: NOT DETECTED"
fi

# Check if security framework is built
if [ -f "/home/diablorain/Syn_OS/target/debug/libsyn_security.rlib" ] || [ -f "/home/diablorain/Syn_OS/target/debug/deps/libsyn_security-*.rlib" ] || [ -d "/home/diablorain/Syn_OS/target/debug/deps" ]; then
    if ls /home/diablorain/Syn_OS/target/debug/deps/libsyn_security-*.rlib 1> /dev/null 2>&1; then
        echo "✅ Security Framework: COMPILED"
    else
        echo "⚠️  Security Framework: NEEDS COMPILATION"
    fi
else
    echo "⚠️  Security Framework: NEEDS COMPILATION"
fi

echo ""

# Performance metrics
echo "📈 Performance Metrics:"
echo "----------------------------------------"
if [ -n "$NETWORK_PROG" ]; then
    PROG_ID=$(echo "$NETWORK_PROG" | cut -d':' -f1)
    # Get program statistics
    PROG_STATS=$(sudo bpftool prog show id $PROG_ID 2>/dev/null | grep -E "(xlated|jited)" || echo "")
    if [ -n "$PROG_STATS" ]; then
        echo "Network Monitor:"
        echo "  $PROG_STATS"
    fi
fi

echo ""

# Interactive menu
echo "🎛️  Control Menu:"
echo "----------------------------------------"
echo "1) Reload eBPF Programs"
echo "2) Attach Network Monitor to Interface"
echo "3) View Live eBPF Events (if available)"
echo "4) Build Security Framework"
echo "5) Run Security Tests"
echo "6) Show Detailed Program Info"
echo "7) Exit"
echo ""

read -p "Select option (1-7): " choice

case $choice in
    1)
        echo "Reloading eBPF programs..."
        cd /home/diablorain/Syn_OS/core/kernel/ebpf
        sudo ./load_programs.sh
        ;;
    2)
        echo "Available interfaces:"
        ip link show | grep -E '^[0-9]+:' | grep -v lo
        read -p "Enter interface name: " iface
        if [ -n "$iface" ]; then
            echo "Attaching XDP program to $iface..."
            sudo ip link set dev $iface xdp obj /home/diablorain/Syn_OS/core/kernel/ebpf/build/network/network_monitor.o sec xdp 2>/dev/null || echo "Failed to attach XDP program"
        fi
        ;;
    3)
        echo "Live event monitoring not yet implemented"
        echo "Future implementation will show real-time eBPF events"
        ;;
    4)
        echo "Building Security Framework..."
        cd /home/diablorain/Syn_OS/core/security
        cargo build --all-features
        ;;
    5)
        echo "Running Security Tests..."
        cd /home/diablorain/Syn_OS/core/security
        cargo test --all-features
        ;;
    6)
        if [ -n "$NETWORK_PROG" ]; then
            PROG_ID=$(echo "$NETWORK_PROG" | cut -d':' -f1)
            echo "Detailed Network Monitor Info:"
            sudo bpftool prog show id $PROG_ID --pretty
        else
            echo "No eBPF programs loaded"
        fi
        ;;
    7)
        echo "Exiting dashboard..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        ;;
esac

echo ""
echo "Dashboard updated. Run this script again to refresh status."
