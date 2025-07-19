#!/bin/bash
# Security alert system for tunnels

ALERT_LOG="$LOG_DIR/alerts.log"

while true; do
    timestamp=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    
    # Check for failed authentication attempts
    if grep -q "authentication_failure" "$LOG_DIR/security.log" 2>/dev/null; then
        echo "[$timestamp] ALERT: Authentication failures detected" >> "$ALERT_LOG"
    fi
    
    # Check for rate limit violations
    netstat -tuln | grep -E "(3000|8080|8443|9000)" | wc -l > /tmp/conn_count
    if [[ $(cat /tmp/conn_count) -gt 100 ]]; then
        echo "[$timestamp] ALERT: High connection count detected" >> "$ALERT_LOG"
    fi
    
    # Check for unauthorized access patterns
    if ss -tuln | grep -E "(3000|8080|8443|9000)" | grep -v "127.0.0.1\|::1" > /tmp/external_conns; then
        if [[ -s /tmp/external_conns ]]; then
            echo "[$timestamp] ALERT: External connections detected" >> "$ALERT_LOG"
            cat /tmp/external_conns >> "$ALERT_LOG"
        fi
    fi
    
    sleep 60
done
