#!/bin/bash
# Tunnel control interface

case "$1" in
    status)
        echo "📊 Tunnel Status:"
        netstat -tuln | grep -E "(3000|8080|8443|9000)" || echo "No tunnels active"
        ;;
    logs)
        echo "📋 Recent tunnel logs:"
        tail -20 .logs/tunnel/security.log 2>/dev/null || echo "No logs available"
        ;;
    alerts)
        echo "🚨 Security alerts:"
        tail -20 .logs/tunnel/alerts.log 2>/dev/null || echo "No alerts"
        ;;
    stop)
        echo "🛑 Stopping tunnels..."
        pkill -f "tunnel-monitor" || true
        echo "Tunnels stopped"
        ;;
    *)
        echo "Usage: $0 {status|logs|alerts|stop}"
        exit 1
        ;;
esac
