#!/bin/bash
# Syn_OS Log Management and Rotation System
# Provides centralized log management, rotation, and retention policies

# Configuration
LOG_BASE_DIR="/home/diablorain/Syn_OS/logs"
LOG_ROTATE_CONFIG="/etc/logrotate.d/synos"
LOG_RETENTION_DAYS=30
SECURITY_LOG_RETENTION_DAYS=90
CRITICAL_LOG_RETENTION_DAYS=365

# Log directories
LOG_DIRS=(
    "$LOG_BASE_DIR/errors"
    "$LOG_BASE_DIR/security"
    "$LOG_BASE_DIR/system"
    "$LOG_BASE_DIR/performance"
    "$LOG_BASE_DIR/consciousness"
    "$LOG_BASE_DIR/integration"
    "$LOG_BASE_DIR/audit"
)

# Source error handling
if [[ -f "/home/diablorain/Syn_OS/src/common/error_handling.sh" ]]; then
    source "/home/diablorain/Syn_OS/src/common/error_handling.sh"
    SERVICE_NAME="log_management"
    init_error_handling
fi

# Setup log directories
setup_log_directories() {
    echo "Setting up log directories..."
    
    for dir in "${LOG_DIRS[@]}"; do
        if ! require_directory "$dir" "log directory" "true"; then
            log_filesystem_error "Failed to create log directory: $dir"
            return 1
        fi
        
        # Set proper permissions
        chmod 755 "$dir"
        
        # Create .gitkeep file to ensure directory exists in git
        touch "$dir/.gitkeep"
    done
    
    echo "✅ Log directories setup completed"
}

# Create logrotate configuration
create_logrotate_config() {
    echo "Creating logrotate configuration..."
    
    cat > "$LOG_ROTATE_CONFIG" << 'EOF'
# Syn_OS Log Rotation Configuration
# Handles log rotation for all Syn_OS components

# General application logs
/home/diablorain/Syn_OS/logs/system/*.log {
    daily
    rotate 30
    compress
    compresscmd /bin/gzip
    uncompresscmd /bin/gunzip
    compressext .gz
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        # Send signal to applications to reopen log files if needed
        /bin/systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}

# Error logs (higher retention)
/home/diablorain/Syn_OS/logs/errors/*.log {
    daily
    rotate 45
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    copytruncate
}

# Security logs (longest retention)
/home/diablorain/Syn_OS/logs/security/*.log {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    create 600 root root
    copytruncate
    postrotate
        # Send security log rotation notification
        echo "Security logs rotated at $(date)" >> /home/diablorain/Syn_OS/logs/audit/log_rotation.log
    endscript
}

# Critical alerts (permanent retention)
/home/diablorain/Syn_OS/logs/errors/critical_alerts.log {
    weekly
    rotate 52
    compress
    delaycompress
    missingok
    notifempty
    create 600 root root
    copytruncate
    # Never delete critical alerts
    maxage 0
}

# Performance logs
/home/diablorain/Syn_OS/logs/performance/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    copytruncate
}

# Consciousness logs
/home/diablorain/Syn_OS/logs/consciousness/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    copytruncate
}

# Integration logs
/home/diablorain/Syn_OS/logs/integration/*.log {
    daily
    rotate 21
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    copytruncate
}
EOF

    if [[ $? -eq 0 ]]; then
        echo "✅ Logrotate configuration created"
        
        # Test the configuration
        if logrotate -d "$LOG_ROTATE_CONFIG" &>/dev/null; then
            echo "✅ Logrotate configuration validated"
        else
            log_configuration_error "Logrotate configuration validation failed"
            return 1
        fi
    else
        log_configuration_error "Failed to create logrotate configuration"
        return 1
    fi
}

# Create rsyslog configuration for Syn_OS
create_rsyslog_config() {
    echo "Creating rsyslog configuration..."
    
    local rsyslog_config="/etc/rsyslog.d/50-synos.conf"
    
    cat > "$rsyslog_config" << 'EOF'
# Syn_OS rsyslog configuration
# Routes logs from Syn_OS components to appropriate log files

# Create templates for structured logging
$template SynOSErrorFormat,"%timestamp% %hostname% %syslogtag% %msg%\n"
$template SynOSSecurityFormat,"%timestamp% %hostname% [SECURITY] %syslogtag% %msg%\n"
$template SynOSConsciousnessFormat,"%timestamp% %hostname% [CONSCIOUSNESS] %syslogtag% %msg%\n"

# Route logs by facility and priority
# Security logs (local0)
local0.*                        /home/diablorain/Syn_OS/logs/security/security.log;SynOSSecurityFormat
& stop

# Consciousness logs (local1)
local1.*                        /home/diablorain/Syn_OS/logs/consciousness/consciousness.log;SynOSConsciousnessFormat
& stop

# Error logs (local2)
local2.*                        /home/diablorain/Syn_OS/logs/errors/system_errors.log;SynOSErrorFormat
& stop

# Performance logs (local3)
local3.*                        /home/diablorain/Syn_OS/logs/performance/performance.log;SynOSErrorFormat
& stop

# Integration logs (local4)
local4.*                        /home/diablorain/Syn_OS/logs/integration/integration.log;SynOSErrorFormat
& stop

# General system logs (local5)
local5.*                        /home/diablorain/Syn_OS/logs/system/system.log;SynOSErrorFormat
& stop
EOF

    if [[ $? -eq 0 ]]; then
        echo "✅ Rsyslog configuration created"
        
        # Restart rsyslog to apply changes
        if systemctl restart rsyslog &>/dev/null; then
            echo "✅ Rsyslog restarted successfully"
        else
            log_system_error "Failed to restart rsyslog service"
        fi
    else
        log_configuration_error "Failed to create rsyslog configuration"
        return 1
    fi
}

# Create log monitoring script
create_log_monitoring() {
    echo "Creating log monitoring script..."
    
    local monitor_script="/usr/local/bin/synos-log-monitor"
    
    cat > "$monitor_script" << 'EOF'
#!/bin/bash
# Syn_OS Log Monitoring Script
# Monitors log files for critical events and sends alerts

LOG_BASE_DIR="/home/diablorain/Syn_OS/logs"
ALERT_THRESHOLD=100  # Alert if more than 100 errors in 5 minutes
CHECK_INTERVAL=300   # Check every 5 minutes

# Check for critical errors
check_critical_errors() {
    local critical_count
    critical_count=$(find "$LOG_BASE_DIR/errors" -name "*.log" -mmin -5 -exec grep -l "CRITICAL" {} \; | wc -l)
    
    if [[ $critical_count -gt 0 ]]; then
        echo "ALERT: $critical_count critical errors detected in the last 5 minutes" | \
            logger -p local0.alert -t synos-monitor
    fi
}

# Check for high error rates
check_error_rates() {
    local error_count
    error_count=$(find "$LOG_BASE_DIR/errors" -name "*.log" -mmin -5 -exec grep -c "ERROR" {} \; | \
                  awk '{sum += $1} END {print sum}')
    
    if [[ ${error_count:-0} -gt $ALERT_THRESHOLD ]]; then
        echo "ALERT: High error rate detected - $error_count errors in 5 minutes" | \
            logger -p local0.alert -t synos-monitor
    fi
}

# Check disk usage for log directories
check_log_disk_usage() {
    local usage
    usage=$(df "$LOG_BASE_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ $usage -gt 80 ]]; then
        echo "WARNING: Log directory disk usage is at ${usage}%" | \
            logger -p local0.warning -t synos-monitor
    fi
}

# Main monitoring loop
while true; do
    check_critical_errors
    check_error_rates
    check_log_disk_usage
    sleep $CHECK_INTERVAL
done
EOF

    chmod +x "$monitor_script"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Log monitoring script created"
    else
        log_configuration_error "Failed to create log monitoring script"
        return 1
    fi
}

# Create systemd service for log monitoring
create_log_monitoring_service() {
    echo "Creating log monitoring systemd service..."
    
    local service_file="/etc/systemd/system/synos-log-monitor.service"
    
    cat > "$service_file" << 'EOF'
[Unit]
Description=Syn_OS Log Monitoring Service
After=network.target rsyslog.service
Wants=rsyslog.service

[Service]
Type=simple
ExecStart=/usr/local/bin/synos-log-monitor
Restart=always
RestartSec=10
User=root
Group=root

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/diablorain/Syn_OS/logs

[Install]
WantedBy=multi-user.target
EOF

    if [[ $? -eq 0 ]]; then
        echo "✅ Log monitoring service created"
        
        # Enable and start the service
        systemctl daemon-reload
        systemctl enable synos-log-monitor.service
        
        if systemctl start synos-log-monitor.service; then
            echo "✅ Log monitoring service started"
        else
            log_system_error "Failed to start log monitoring service"
        fi
    else
        log_configuration_error "Failed to create log monitoring service"
        return 1
    fi
}

# Cleanup old logs
cleanup_old_logs() {
    echo "Cleaning up old logs..."
    
    # Clean general logs older than retention period
    find "$LOG_BASE_DIR/system" -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null
    find "$LOG_BASE_DIR/performance" -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null
    find "$LOG_BASE_DIR/integration" -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null
    find "$LOG_BASE_DIR/consciousness" -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null
    
    # Clean security logs (longer retention)
    find "$LOG_BASE_DIR/security" -name "*.log.*" -mtime +$SECURITY_LOG_RETENTION_DAYS -delete 2>/dev/null
    
    # Clean error logs but keep critical alerts longer
    find "$LOG_BASE_DIR/errors" -name "*.log.*" -not -name "*critical*" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null
    
    echo "✅ Old logs cleaned up"
}

# Generate log management report
generate_log_report() {
    echo "Generating log management report..."
    
    local report_file="$LOG_BASE_DIR/audit/log_management_report_$(date +%Y%m%d_%H%M%S).log"
    
    {
        echo "Syn_OS Log Management Report"
        echo "Generated: $(date)"
        echo "=================================="
        echo
        
        echo "Log Directory Sizes:"
        for dir in "${LOG_DIRS[@]}"; do
            if [[ -d "$dir" ]]; then
                size=$(du -sh "$dir" 2>/dev/null | cut -f1)
                echo "  $dir: $size"
            fi
        done
        echo
        
        echo "Recent Error Summary (last 24 hours):"
        error_count=$(find "$LOG_BASE_DIR/errors" -name "*.log" -mtime -1 -exec grep -c "ERROR" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
        critical_count=$(find "$LOG_BASE_DIR/errors" -name "*.log" -mtime -1 -exec grep -c "CRITICAL" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
        
        echo "  Total Errors: $error_count"
        echo "  Critical Errors: $critical_count"
        echo
        
        echo "Disk Usage:"
        df -h "$LOG_BASE_DIR"
        echo
        
        echo "Logrotate Status:"
        logrotate -d "$LOG_ROTATE_CONFIG" 2>&1 | head -10
        
    } > "$report_file"
    
    echo "✅ Log management report generated: $report_file"
}

# Main function
main() {
    echo "🔧 Syn_OS Log Management Setup"
    echo "================================"
    
    # Check if running as root for system configurations
    if [[ $EUID -ne 0 ]] && [[ "$1" != "--user-only" ]]; then
        echo "⚠️  Running in user mode - some features require root privileges"
        echo "   Run with --user-only to skip system configurations"
        echo "   Run as root for full setup"
    fi
    
    # Setup log directories (always possible)
    setup_log_directories
    
    # System configurations (require root)
    if [[ $EUID -eq 0 ]] && [[ "$1" != "--user-only" ]]; then
        create_logrotate_config
        create_rsyslog_config
        create_log_monitoring
        create_log_monitoring_service
    fi
    
    # User-level operations
    cleanup_old_logs
    generate_log_report
    
    echo
    echo "✅ Log management setup completed"
    echo "📋 Next steps:"
    echo "   - Monitor logs with: journalctl -f -u synos-log-monitor"
    echo "   - View log report: cat $LOG_BASE_DIR/audit/log_management_report_*.log"
    echo "   - Test log rotation: logrotate -f $LOG_ROTATE_CONFIG"
}

# Run main function with arguments
main "$@"
