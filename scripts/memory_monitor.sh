#!/bin/bash
# Memory Monitoring Script for Phase 3.4 Implementation
# Continuously monitors memory usage and prevents OOM conditions

LOGFILE="/tmp/memory_monitor.log"
THRESHOLD_MB=200  # Alert when free memory drops below 200MB

log_memory_status() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Memory Status:" >> "$LOGFILE"
    free -h >> "$LOGFILE"
    echo "---" >> "$LOGFILE"
}

check_memory_critical() {
    FREE_MB=$(free -m | awk 'NR==2{print $7}')
    if [ "$FREE_MB" -lt "$THRESHOLD_MB" ]; then
        echo "⚠️  CRITICAL: Available memory below ${THRESHOLD_MB}MB (${FREE_MB}MB available)"
        echo "Consider pausing installation and checking for memory leaks"
        return 1
    fi
    return 0
}

monitor_continuous() {
    echo "Starting continuous memory monitoring..."
    echo "Log file: $LOGFILE"
    echo "Critical threshold: ${THRESHOLD_MB}MB available memory"
    echo "Press Ctrl+C to stop"
    
    while true; do
        clear
        echo "=== MEMORY MONITOR - Phase 3.4 Installation ==="
        echo "$(date '+%Y-%m-%d %H:%M:%S')"
        echo
        free -h
        echo
        echo "Swap usage:"
        swapon -s 2>/dev/null || echo "No swap configured"
        echo
        
        if ! check_memory_critical; then
            echo "🔴 MEMORY CRITICAL - Consider stopping installation"
        else
            echo "✅ Memory levels safe"
        fi
        
        log_memory_status
        sleep 5
    done
}

case "${1:-monitor}" in
    "check")
        check_memory_critical
        ;;
    "log")
        log_memory_status
        echo "Memory status logged to $LOGFILE"
        ;;
    "monitor")
        monitor_continuous
        ;;
    *)
        echo "Usage: $0 [check|log|monitor]"
        echo "  check   - One-time memory check"
        echo "  log     - Log current memory status"
        echo "  monitor - Continuous monitoring (default)"
        ;;
esac