#!/bin/bash
# Tunnel control interface

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../.logs/tunnel"

case "$1" in
    status)
        echo "📊 Tunnel Status:"
        if command -v netstat &> /dev/null; then
            netstat -tuln | grep -E "(3000|8080|8443|9000)" || echo "No tunnels active"
        else
            ss -tuln | grep -E "(3000|8080|8443|9000)" || echo "No tunnels active"
        fi
        echo ""
        echo "🔗 Codespace Status:"
        if command -v gh &> /dev/null; then
            gh codespace list 2>/dev/null || echo "No codespaces found"
        else
            echo "GitHub CLI not available"
        fi
        ;;
    logs)
        echo "📋 Recent tunnel logs:"
        if [[ -f "$LOG_DIR/security.log" ]]; then
            tail -20 "$LOG_DIR/security.log"
        else
            echo "No logs available - run tunnel-setup.sh first"
        fi
        ;;
    alerts)
        echo "🚨 Security alerts:"
        if [[ -f "$LOG_DIR/alerts.log" ]]; then
            tail -20 "$LOG_DIR/alerts.log"
        else
            echo "No alerts - monitoring not active"
        fi
        ;;
    stop)
        echo "🛑 Stopping tunnels..."
        pkill -f "tunnel-monitor" 2>/dev/null || true
        pkill -f "security-alerts" 2>/dev/null || true
        echo "Tunnel monitoring stopped"
        ;;
    setup)
        echo "🚀 Setting up tunnel infrastructure..."
        exec "$SCRIPT_DIR/tunnel-setup.sh"
        ;;
    *)
        echo "🛠️ Syn_OS Tunnel Control"
        echo ""
        echo "Usage: $0 {status|logs|alerts|stop|setup}"
        echo ""
        echo "Commands:"
        echo "  status  - Show tunnel and codespace status"
        echo "  logs    - Show recent security logs"
        echo "  alerts  - Show security alerts"
        echo "  stop    - Stop tunnel monitoring"
        echo "  setup   - Run tunnel setup"
        echo ""
        exit 1
        ;;
esac