#!/bin/bash
# Syn OS eBPF Program Loader
# Loads essential eBPF monitoring programs for kernel operations

echo "Loading Syn OS eBPF monitoring programs..."

# Load memory monitor
echo "Loading memory monitor..."
clang -O2 -target bpf -c memory/memory_monitor_simple.c -o memory_monitor.o
bpftool prog load memory_monitor.o /sys/fs/bpf/memory_monitor

# Load process monitor  
echo "Loading process monitor..."
clang -O2 -target bpf -c process/process_monitor_simple.c -o process_monitor.o
bpftool prog load process_monitor.o /sys/fs/bpf/process_monitor

# Load network monitor
echo "Loading network monitor..."
clang -O2 -target bpf -c network/network_monitor.c -o network_monitor.o
bpftool prog load network_monitor.o /sys/fs/bpf/network_monitor

echo "eBPF programs loaded successfully"
