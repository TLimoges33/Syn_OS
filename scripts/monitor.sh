#!/bin/bash
# SynapticOS System Health Monitor
# Real-time monitoring of Neural Darwinism system performance

echo "🧠 SynapticOS Neural Darwinism System Monitor"
echo "=============================================="
echo

# Container Status
echo "📦 Container Status:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# Resource Usage
echo "💻 Resource Usage:"
podman stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

# Neural Darwinism Activity
echo "🧬 Neural Darwinism Activity (Last 5 minutes):"
podman logs --since="5m" synapticos_consciousness_bridge | grep -E "(Generation|Consciousness|Evolution)" | tail -10
echo

# Web Interface Tests
echo "🌐 Web Interface Health:"
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Consciousness Dashboard (8000): Running"
else
    echo "❌ Consciousness Dashboard (8000): Not accessible"
fi

if curl -s http://localhost:8001 > /dev/null; then
    echo "✅ Education GUI (8001): Running"
else
    echo "❌ Education GUI (8001): Not accessible"
fi

# Log file sizes
echo
echo "📄 Log File Status:"
if [ -d "./logs" ]; then
    ls -lh ./logs/ 2>/dev/null || echo "No log files found"
else
    echo "Logs directory not found"
fi

# Disk usage
echo
echo "💾 Disk Usage:"
df -h | grep -E "(Filesystem|/home|/var)"

echo
echo "Monitor completed at: $(date)"
echo "Refresh with: ./scripts/monitor.sh"
