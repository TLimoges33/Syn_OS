#!/bin/bash
# Role-Based Access Control System
set -euo pipefail

# Define roles and permissions
declare -A ROLES=(
    ["developer"]="build test audit"
    ["security"]="audit scan verify"
    ["release"]="build test audit sign release"
    ["admin"]="build test audit scan verify sign release configure"
)

# Get current user role
get_user_role() {
    local user="$1"
    
    # Check role assignments (would integrate with LDAP/AD in production)
    case "$user" in
        "build-"*) echo "developer" ;;
        "sec-"*) echo "security" ;;
        "rel-"*) echo "release" ;;
        "admin-"*) echo "admin" ;;
        *) echo "developer" ;;  # Default role
    esac
}

# Check if user has permission for operation
check_permission() {
    local operation="$1"
    local user="${USER:-$(whoami)}"
    local role=$(get_user_role "$user")
    
    if [[ "${ROLES[$role]}" == *"$operation"* ]]; then
        echo "✅ Permission granted: $user ($role) -> $operation"
        return 0
    else
        echo "❌ Permission denied: $user ($role) cannot perform $operation"
        return 1
    fi
}

# Audit log function
audit_log() {
    local operation="$1"
    local user="${USER:-$(whoami)}"
    local timestamp=$(date --iso-8601=seconds)
    local result="${2:-SUCCESS}"
    
    echo "$timestamp $user $operation $result" >> "${PROJECT_ROOT}/security/audit.log"
}

# Permission wrapper function
with_permission() {
    local operation="$1"
    shift
    
    if check_permission "$operation"; then
        audit_log "$operation" "GRANTED"
        "$@"
    else
        audit_log "$operation" "DENIED"
        exit 1
    fi
}

# Export functions for use in other scripts
export -f check_permission audit_log with_permission
