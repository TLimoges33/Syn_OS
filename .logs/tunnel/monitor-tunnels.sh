#!/bin/bash
# Tunnel monitoring script

MONITOR_LOG="$LOG_DIR/monitor.log"

while true; do
    timestamp=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    
    # Check tunnel health
    echo "[$timestamp] Checking tunnel health..." >> "$MONITOR_LOG"
    
    # Monitor network connections
    netstat -tuln | grep -E "(3000|8080|8443|9000)" >> "$MONITOR_LOG" 2>/dev/null || true
    
    # Check for suspicious activity
    ss -tuln | grep -E "(3000|8080|8443|9000)" | while read line; do
        echo "[$timestamp] CONN: $line" >> "$MONITOR_LOG"
    done
    
    # Resource monitoring
    echo "[$timestamp] Memory: $(free -h | grep '^Mem:' | awk '{print $3"/"$2}')" >> "$MONITOR_LOG"
    
    sleep 30
done
