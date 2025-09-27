#!/bin/bash
# Intrusion Detection System
set -euo pipefail

# Load logging framework
source "${PROJECT_ROOT}/config/logging.sh"

IDS_CONFIG="${PROJECT_ROOT}/config/ids.conf"
IDS_STATE="${PROJECT_ROOT}/security/ids-state.json"

mkdir -p "$(dirname "$IDS_STATE")"

# Initialize IDS state
init_ids() {
    cat > "$IDS_STATE" <<EOF
{
  "startup_time": "$(date --iso-8601=seconds)",
  "file_hashes": {},
  "process_baseline": {},
  "network_baseline": {},
  "alerts": []
}
EOF
    
    log_info "IDS initialized" "intrusion-detection"
}

# File integrity monitoring
check_file_integrity() {
    log_debug "Starting file integrity check" "file-integrity"
    
    local critical_files=(
        "scripts/security-automation/validate-security.sh"
        "config/environment-secure.sh"
        ".cargo/config-security.toml"
        "src/kernel/src/main.rs"
    )
    
    local changes_detected=false
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            local current_hash=$(sha256sum "$file" | cut -d' ' -f1)
            local stored_hash=$(jq -r ".file_hashes["$file"] // """ "$IDS_STATE")
            
            if [[ -z "$stored_hash" ]]; then
                # First time seeing this file
                jq ".file_hashes["$file"] = "$current_hash"" "$IDS_STATE" > "$IDS_STATE.tmp"
                mv "$IDS_STATE.tmp" "$IDS_STATE"
                log_debug "Baseline established for: $file" "file-integrity"
            elif [[ "$current_hash" != "$stored_hash" ]]; then
                # File has been modified
                log_security_event "FILE_MODIFIED" "Critical file modified: $file" "WARN"
                changes_detected=true
                
                # Update hash
                jq ".file_hashes["$file"] = "$current_hash"" "$IDS_STATE" > "$IDS_STATE.tmp"
                mv "$IDS_STATE.tmp" "$IDS_STATE"
            fi
        else
            log_security_event "FILE_MISSING" "Critical file missing: $file" "ERROR"
            changes_detected=true
        fi
    done
    
    if [[ "$changes_detected" == "true" ]]; then
        log_warn "File integrity violations detected" "file-integrity"
    else
        log_debug "File integrity check passed" "file-integrity"
    fi
}

# Process monitoring
check_suspicious_processes() {
    log_debug "Checking for suspicious processes" "process-monitor"
    
    # Look for suspicious process patterns
    local suspicious_patterns=(
        "nc.*-l"          # Netcat listeners
        "python.*-c"      # Python one-liners
        "curl.*sh"        # Curl pipe to shell
        "wget.*sh"        # Wget pipe to shell
        "base64.*-d"      # Base64 decoding
    )
    
    for pattern in "${suspicious_patterns[@]}"; do
        local matches=$(pgrep -f "$pattern" || true)
        if [[ -n "$matches" ]]; then
            log_security_event "SUSPICIOUS_PROCESS" "Detected suspicious process pattern: $pattern" "WARN"
        fi
    done
}

# Network monitoring (basic)
check_network_activity() {
    log_debug "Checking network activity" "network-monitor"
    
    # Check for unusual listening ports
    local listening_ports=$(netstat -tuln | grep LISTEN | awk '{print $4}' | cut -d: -f2 | sort -n)
    local expected_ports=("22" "80" "443" "8080")  # Add expected ports
    
    while IFS= read -r port; do
        local is_expected=false
        for expected in "${expected_ports[@]}"; do
            if [[ "$port" == "$expected" ]]; then
                is_expected=true
                break
            fi
        done
        
        if [[ "$is_expected" == "false" ]] && [[ "$port" -gt 1024 ]]; then
            log_security_event "UNUSUAL_PORT" "Unusual listening port detected: $port" "INFO"
        fi
    done <<< "$listening_ports"
}

# Main IDS scan function
run_ids_scan() {
    log_info "Starting intrusion detection scan" "intrusion-detection"
    
    # Initialize if first run
    if [[ ! -f "$IDS_STATE" ]]; then
        init_ids
    fi
    
    check_file_integrity
    check_suspicious_processes
    check_network_activity
    
    # Update scan timestamp
    jq ".last_scan = "$(date --iso-8601=seconds)"" "$IDS_STATE" > "$IDS_STATE.tmp"
    mv "$IDS_STATE.tmp" "$IDS_STATE"
    
    log_info "Intrusion detection scan complete" "intrusion-detection"
}

# Run IDS scan
run_ids_scan
