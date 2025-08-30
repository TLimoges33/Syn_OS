#!/bin/bash
# Syn_OS Standardized Error Handling Framework for Bash Scripts
# Provides unified error handling, logging, and recovery patterns

# Error severity levels
declare -r ERROR_SEVERITY_CRITICAL="CRITICAL"
declare -r ERROR_SEVERITY_HIGH="HIGH"
declare -r ERROR_SEVERITY_MEDIUM="MEDIUM"
declare -r ERROR_SEVERITY_LOW="LOW"
declare -r ERROR_SEVERITY_INFO="INFO"

# Error categories
declare -r ERROR_CATEGORY_AUTHENTICATION="AUTHENTICATION"
declare -r ERROR_CATEGORY_AUTHORIZATION="AUTHORIZATION"
declare -r ERROR_CATEGORY_VALIDATION="VALIDATION"
declare -r ERROR_CATEGORY_NETWORK="NETWORK"
declare -r ERROR_CATEGORY_DATABASE="DATABASE"
declare -r ERROR_CATEGORY_FILESYSTEM="FILESYSTEM"
declare -r ERROR_CATEGORY_CONFIGURATION="CONFIGURATION"
declare -r ERROR_CATEGORY_CONSCIOUSNESS="CONSCIOUSNESS"
declare -r ERROR_CATEGORY_INTEGRATION="INTEGRATION"
declare -r ERROR_CATEGORY_SECURITY="SECURITY"
declare -r ERROR_CATEGORY_PERFORMANCE="PERFORMANCE"
declare -r ERROR_CATEGORY_SYSTEM="SYSTEM"

# Colors for output
declare -r RED='\033[0;31m'
declare -r YELLOW='\033[1;33m'
declare -r GREEN='\033[0;32m'
declare -r BLUE='\033[0;34m'
declare -r PURPLE='\033[0;35m'
declare -r NC='\033[0m' # No Color

# Global variables
SCRIPT_NAME="${0##*/}"
SERVICE_NAME="${SERVICE_NAME:-${SCRIPT_NAME%.*}}"
LOG_DIR="/home/diablorain/Syn_OS/logs/errors"
ERROR_LOG_FILE="${LOG_DIR}/${SERVICE_NAME}_errors.log"
CRITICAL_ALERT_FILE="${LOG_DIR}/critical_alerts.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Error statistics (using associative array if bash 4+)
if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
    declare -A ERROR_STATS
fi

# Initialize error handling
init_error_handling() {
    # Set strict error handling
    set -euo pipefail
    
    # Set up trap for script errors
    trap 'handle_script_error ${LINENO} "$BASH_COMMAND"' ERR
    
    # Set up trap for script exit
    trap 'cleanup_error_handling' EXIT
    
    # Initialize log file
    echo "$(timestamp) - [INFO] Error handling initialized for service: $SERVICE_NAME" >> "$ERROR_LOG_FILE"
}

# Get current timestamp in ISO format
timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%S.%3NZ"
}

# Generate error code from category and severity
generate_error_code() {
    local category="$1"
    local severity="$2"
    echo "${category}_${severity}"
}

# Log structured error
log_structured_error() {
    local message="$1"
    local category="$2"
    local severity="$3"
    local context="$4"
    local line_number="${5:-unknown}"
    local command="${6:-unknown}"
    
    local error_code
    error_code=$(generate_error_code "$category" "$severity")
    
    local timestamp
    timestamp=$(timestamp)
    
    # Create structured log entry
    local log_entry
    log_entry=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "service": "$SERVICE_NAME",
  "error_code": "$error_code",
  "message": "$message",
  "category": "$category",
  "severity": "$severity",
  "context": {
    "line_number": "$line_number",
    "command": "$command",
    "script": "$SCRIPT_NAME",
    "pid": "$$",
    $context
  }
}
EOF
    )
    
    # Write to log file
    echo "$log_entry" >> "$ERROR_LOG_FILE"
    
    # Update statistics if supported
    if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
        ((ERROR_STATS["$category"]++)) || ERROR_STATS["$category"]=1
    fi
    
    # Handle critical errors
    if [[ "$severity" == "$ERROR_SEVERITY_CRITICAL" ]]; then
        handle_critical_error "$log_entry"
    fi
    
    # Output to console with appropriate color
    local color
    case "$severity" in
        "$ERROR_SEVERITY_CRITICAL") color="$RED" ;;
        "$ERROR_SEVERITY_HIGH") color="$RED" ;;
        "$ERROR_SEVERITY_MEDIUM") color="$YELLOW" ;;
        "$ERROR_SEVERITY_LOW") color="$BLUE" ;;
        "$ERROR_SEVERITY_INFO") color="$GREEN" ;;
        *) color="$NC" ;;
    esac
    
    echo -e "${color}[$error_code] $message${NC}" >&2
}

# Handle critical errors with alerting
handle_critical_error() {
    local log_entry="$1"
    
    # Write to critical alerts file
    echo "$(timestamp) - CRITICAL ALERT: $log_entry" >> "$CRITICAL_ALERT_FILE"
    
    # Could integrate with alerting systems here
    # For example: send to PagerDuty, Slack, email, etc.
    
    echo -e "${RED}🚨 CRITICAL ERROR DETECTED - Check $CRITICAL_ALERT_FILE for details${NC}" >&2
}

# Handle script errors (called by trap)
handle_script_error() {
    local line_number="$1"
    local command="$2"
    
    log_structured_error \
        "Script error occurred" \
        "$ERROR_CATEGORY_SYSTEM" \
        "$ERROR_SEVERITY_HIGH" \
        "\"exit_code\": \"$?\"" \
        "$line_number" \
        "$command"
    
    echo -e "${RED}❌ Script failed at line $line_number: $command${NC}" >&2
    exit 1
}

# Specific error logging functions
log_authentication_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_AUTHENTICATION" "$ERROR_SEVERITY_HIGH" "$context"
}

log_authorization_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_AUTHORIZATION" "$ERROR_SEVERITY_HIGH" "$context"
}

log_validation_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_VALIDATION" "$ERROR_SEVERITY_MEDIUM" "$context"
}

log_network_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_NETWORK" "$ERROR_SEVERITY_MEDIUM" "$context"
}

log_database_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_DATABASE" "$ERROR_SEVERITY_HIGH" "$context"
}

log_filesystem_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_FILESYSTEM" "$ERROR_SEVERITY_MEDIUM" "$context"
}

log_configuration_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_CONFIGURATION" "$ERROR_SEVERITY_HIGH" "$context"
}

log_consciousness_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_CONSCIOUSNESS" "$ERROR_SEVERITY_CRITICAL" "$context"
}

log_integration_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_INTEGRATION" "$ERROR_SEVERITY_MEDIUM" "$context"
}

log_security_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_SECURITY" "$ERROR_SEVERITY_CRITICAL" "$context"
}

log_performance_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_PERFORMANCE" "$ERROR_SEVERITY_LOW" "$context"
}

log_system_error() {
    local message="$1"
    local context="${2:-}"
    log_structured_error "$message" "$ERROR_CATEGORY_SYSTEM" "$ERROR_SEVERITY_MEDIUM" "$context"
}

# Safe command execution with error handling
safe_execute() {
    local command="$1"
    local error_message="${2:-Command execution failed}"
    local category="${3:-$ERROR_CATEGORY_SYSTEM}"
    local severity="${4:-$ERROR_SEVERITY_MEDIUM}"
    
    if ! eval "$command"; then
        local exit_code=$?
        log_structured_error \
            "$error_message" \
            "$category" \
            "$severity" \
            "\"command\": \"$command\", \"exit_code\": \"$exit_code\""
        return $exit_code
    fi
}

# Validate command availability
require_command() {
    local command="$1"
    local package="${2:-$command}"
    
    if ! command -v "$command" &> /dev/null; then
        log_configuration_error \
            "Required command '$command' not found" \
            "\"package\": \"$package\", \"command\": \"$command\""
        echo -e "${RED}❌ Required command '$command' is not installed. Install package: $package${NC}" >&2
        exit 1
    fi
}

# Validate file exists and is readable
require_file() {
    local file="$1"
    local description="${2:-file}"
    
    if [[ ! -f "$file" ]]; then
        log_filesystem_error \
            "Required $description not found: $file" \
            "\"file\": \"$file\", \"description\": \"$description\""
        echo -e "${RED}❌ Required $description not found: $file${NC}" >&2
        exit 1
    fi
    
    if [[ ! -r "$file" ]]; then
        log_filesystem_error \
            "Required $description not readable: $file" \
            "\"file\": \"$file\", \"description\": \"$description\""
        echo -e "${RED}❌ Required $description not readable: $file${NC}" >&2
        exit 1
    fi
}

# Validate directory exists and is writable
require_directory() {
    local dir="$1"
    local description="${2:-directory}"
    local create_if_missing="${3:-false}"
    
    if [[ ! -d "$dir" ]]; then
        if [[ "$create_if_missing" == "true" ]]; then
            if ! mkdir -p "$dir"; then
                log_filesystem_error \
                    "Failed to create required $description: $dir" \
                    "\"directory\": \"$dir\", \"description\": \"$description\""
                echo -e "${RED}❌ Failed to create required $description: $dir${NC}" >&2
                exit 1
            fi
        else
            log_filesystem_error \
                "Required $description not found: $dir" \
                "\"directory\": \"$dir\", \"description\": \"$description\""
            echo -e "${RED}❌ Required $description not found: $dir${NC}" >&2
            exit 1
        fi
    fi
    
    if [[ ! -w "$dir" ]]; then
        log_filesystem_error \
            "Required $description not writable: $dir" \
            "\"directory\": \"$dir\", \"description\": \"$description\""
        echo -e "${RED}❌ Required $description not writable: $dir${NC}" >&2
        exit 1
    fi
}

# Network connectivity check
check_network_connectivity() {
    local host="${1:-google.com}"
    local port="${2:-80}"
    local timeout="${3:-5}"
    
    if ! timeout "$timeout" bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        log_network_error \
            "Network connectivity check failed" \
            "\"host\": \"$host\", \"port\": \"$port\", \"timeout\": \"$timeout\""
        return 1
    fi
}

# Service availability check
check_service_availability() {
    local service_name="$1"
    local check_command="$2"
    
    if ! eval "$check_command" &>/dev/null; then
        log_system_error \
            "Service availability check failed: $service_name" \
            "\"service\": \"$service_name\", \"check_command\": \"$check_command\""
        return 1
    fi
}

# Get error statistics
get_error_statistics() {
    if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
        echo "Error Statistics for $SERVICE_NAME:"
        for category in "${!ERROR_STATS[@]}"; do
            echo "  $category: ${ERROR_STATS[$category]}"
        done
    else
        echo "Error statistics require Bash 4+ (current: $BASH_VERSION)"
    fi
}

# Cleanup function (called on script exit)
cleanup_error_handling() {
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        echo "$(timestamp) - [INFO] Script exited with code $exit_code" >> "$ERROR_LOG_FILE"
    fi
    
    # Print statistics if available
    if [[ ${BASH_VERSION%%.*} -ge 4 ]] && [[ ${#ERROR_STATS[@]} -gt 0 ]]; then
        {
            echo "$(timestamp) - [INFO] Error statistics:"
            for category in "${!ERROR_STATS[@]}"; do
                echo "  $category: ${ERROR_STATS[$category]}"
            done
        } >> "$ERROR_LOG_FILE"
    fi
}

# Progress indicator with error handling
progress_with_error_handling() {
    local total_steps="$1"
    local current_step="$2"
    local step_description="$3"
    local step_command="$4"
    
    echo -e "${BLUE}[$current_step/$total_steps] $step_description...${NC}"
    
    if ! safe_execute "$step_command" "Step failed: $step_description"; then
        echo -e "${RED}❌ Step $current_step failed: $step_description${NC}" >&2
        return 1
    fi
    
    echo -e "${GREEN}✅ Step $current_step completed: $step_description${NC}"
}

# Example usage function
example_usage() {
    echo "Syn_OS Error Handling Framework - Example Usage"
    echo "=============================================="
    
    # Initialize error handling
    init_error_handling
    
    # Example error logging
    log_system_error "Example system error" "\"component\": \"test\""
    
    # Example safe command execution
    safe_execute "echo 'Safe command executed successfully'"
    
    # Example requirement checks
    require_command "bash" "bash"
    require_directory "$LOG_DIR" "log directory" "true"
    
    # Example network check
    if check_network_connectivity "google.com" 80 5; then
        echo "Network connectivity OK"
    else
        echo "Network connectivity failed"
    fi
    
    # Show statistics
    get_error_statistics
}

# If script is run directly, show example usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    example_usage
fi
