#!/bin/bash
# Comprehensive Error Handling System
set -euo pipefail

# Error handling configuration
ERROR_LOG="${PROJECT_ROOT}/security/errors.log"
ALERT_THRESHOLD=5  # Alert after 5 errors
ERROR_COUNT=0

# Create error log if it doesn't exist
mkdir -p "$(dirname "$ERROR_LOG")"
touch "$ERROR_LOG"

# Enhanced error handler
handle_error() {
    local exit_code=$?
    local line_number=$1
    local bash_lineno=$2
    local last_command="$3"
    local funcstack=("${BASH_FUNCNAME[@]}")
    
    # Increment error count
    ((ERROR_COUNT++))
    
    # Collect error context
    local timestamp=$(date --iso-8601=seconds)
    local user="${USER:-$(whoami)}"
    local pwd="$(pwd)"
    local script="${BASH_SOURCE[1]}"
    
    # Log error details
    cat >> "$ERROR_LOG" <<EOF
===== ERROR REPORT =====
Timestamp: $timestamp
User: $user
Script: $script
Directory: $pwd
Line: $line_number
Bash Line: $bash_lineno  
Exit Code: $exit_code
Command: $last_command
Function Stack: ${funcstack[*]}
Environment: $(uname -a)
========================
EOF

    # Display error
    echo "🚨 ERROR DETECTED:"
    echo "   Script: $(basename "$script"):$line_number"
    echo "   Command: $last_command"
    echo "   Exit Code: $exit_code"
    echo "   Logged to: $ERROR_LOG"
    
    # Security: Check for suspicious errors
    if [[ "$last_command" == *"rm -rf"* ]] || [[ "$last_command" == *"sudo"* ]]; then
        echo "⚠️  SECURITY: Potentially dangerous command failed"
        audit_log "DANGEROUS_COMMAND_FAILED" "ALERT"
    fi
    
    # Alert on error threshold
    if [[ $ERROR_COUNT -ge $ALERT_THRESHOLD ]]; then
        echo "🚨 ALERT: Error threshold reached ($ERROR_COUNT errors)"
        # Would send alert to monitoring system
    fi
    
    exit $exit_code
}

# Set up error trapping
trap 'handle_error $LINENO $BASH_LINENO "$BASH_COMMAND"' ERR

# Safe execution wrapper
safe_execute() {
    local description="$1"
    shift
    
    echo "🔄 Executing: $description"
    if "$@"; then
        echo "✅ Success: $description"
        return 0
    else
        local exit_code=$?
        echo "❌ Failed: $description (exit code: $exit_code)"
        return $exit_code
    fi
}

# Validation functions
validate_file_exists() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file not found: $file"
        return 1
    fi
}

validate_directory_writable() {
    local dir="$1"
    if [[ ! -w "$dir" ]]; then
        echo "❌ Directory not writable: $dir"
        return 1
    fi
}

# Export functions
export -f handle_error safe_execute validate_file_exists validate_directory_writable
