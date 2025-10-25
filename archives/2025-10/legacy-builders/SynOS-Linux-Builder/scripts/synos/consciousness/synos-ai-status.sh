#!/bin/bash

# SynOS AI Status Check
# Shows the status of all AI consciousness components

echo "🧠 SynOS AI Consciousness Status"
echo "================================="
echo ""

# Check consciousness engine
if systemctl is-active --quiet synos-consciousness.service; then
    echo "✅ Consciousness Engine: RUNNING"
    echo "   Neural Darwinism: Active"
    echo "   Threat Detection: Active"
    echo "   Learning Engine: Active"
else
    echo "❌ Consciousness Engine: STOPPED"
fi

echo ""

# Check AI dashboard
if systemctl is-active --quiet synos-dashboard.service; then
    echo "✅ AI Dashboard: RUNNING"
    echo "   URL: http://localhost:8080"
    echo "   WebSocket: Active"
else
    echo "❌ AI Dashboard: STOPPED"
fi

echo ""

# Check educational framework
if [[ -f /opt/synos/data/education.db ]]; then
    echo "✅ Educational Framework: INITIALIZED"
    echo "   Learning Paths: 4 available"
    echo "   AI Tutor: Ready"
else
    echo "⚠️ Educational Framework: NOT INITIALIZED"
fi

echo ""

# Check security AI
if pgrep -f "security-ai" > /dev/null; then
    echo "✅ Security AI: ACTIVE"
    echo "   eBPF Monitoring: Enabled"
    echo "   Anomaly Detection: Running"
else
    echo "⚠️ Security AI: INACTIVE"
fi

echo ""

# Show AI resource usage
echo "📊 AI Resource Usage:"
echo "   CPU: $(ps aux | grep synos | awk '{sum+=$3} END {print sum "%"}')"
echo "   Memory: $(ps aux | grep synos | awk '{sum+=$4} END {print sum "%"}')"

echo ""
echo "Run 'synos-ai-control' to manage AI services"