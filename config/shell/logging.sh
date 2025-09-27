#!/bin/bash
# Structured Security Logging Framework
set -euo pipefail

# Logging configuration
LOG_DIR="${PROJECT_ROOT}/security/logs"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FORMAT="${LOG_FORMAT:-json}"

mkdir -p "$LOG_DIR"

# Log levels
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARN"]=2
    ["ERROR"]=3
    ["CRITICAL"]=4
)

# Get current log level value
get_log_level_value() {
    echo "${LOG_LEVELS[${LOG_LEVEL}]}"
}

# Structured logging function
log_structured() {
    local level="$1"
    local message="$2"
    local component="${3:-system}"
    local user="${USER:-$(whoami)}"
    local timestamp=$(date --iso-8601=seconds)
    local level_value="${LOG_LEVELS[$level]}"
    local current_level_value=$(get_log_level_value)
    
    # Only log if level is high enough
    if [[ $level_value -ge $current_level_value ]]; then
        if [[ "$LOG_FORMAT" == "json" ]]; then
            local log_entry=$(jq -n \
                --arg timestamp "$timestamp" \
                --arg level "$level" \
                --arg component "$component" \
                --arg user "$user" \
                --arg message "$message" \
                --arg pid "$$" \
                --arg hostname "$(hostname)" \
                '{timestamp: $timestamp, level: $level, component: $component, user: $user, message: $message, pid: $pid, hostname: $hostname}')
            
            echo "$log_entry" >> "$LOG_DIR/security.log"
        else
            echo "$timestamp [$level] $component: $message (user=$user)" >> "$LOG_DIR/security.log"
        fi
        
        # Also output to console for interactive use
        case $level in
            "DEBUG") echo -e "\033[0;36m[DEBUG]\033[0m $message" ;;
            "INFO") echo -e "\033[0;32m[INFO]\033[0m $message" ;;
            "WARN") echo -e "\033[1;33m[WARN]\033[0m $message" ;;
            "ERROR") echo -e "\033[0;31m[ERROR]\033[0m $message" ;;
            "CRITICAL") echo -e "\033[1;31m[CRITICAL]\033[0m $message" ;;
        esac
    fi
}

# Convenience logging functions
log_debug() { log_structured "DEBUG" "$1" "${2:-system}"; }
log_info() { log_structured "INFO" "$1" "${2:-system}"; }
log_warn() { log_structured "WARN" "$1" "${2:-system}"; }
log_error() { log_structured "ERROR" "$1" "${2:-system}"; }
log_critical() { log_structured "CRITICAL" "$1" "${2:-system}"; }

# Security event logging
log_security_event() {
    local event_type="$1"
    local description="$2"
    local severity="${3:-WARN}"
    
    log_structured "$severity" "SECURITY EVENT: $event_type - $description" "security"
    
    # Also log to dedicated security events file
    local security_log="$LOG_DIR/security-events.log"
    local timestamp=$(date --iso-8601=seconds)
    echo "$timestamp [$severity] $event_type: $description" >> "$security_log"
}

# Export logging functions
export -f log_structured log_debug log_info log_warn log_error log_critical log_security_event
