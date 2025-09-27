#!/bin/bash
# Security Benchmarks Validation
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
BENCHMARK_RESULTS="${PROJECT_ROOT}/security/benchmarks.json"

mkdir -p "$(dirname "$BENCHMARK_RESULTS")"

echo "🔍 Running security benchmarks validation..."

# Initialize results
cat > "$BENCHMARK_RESULTS" <<EOF
{
  "timestamp": "$(date --iso-8601=seconds)",
  "benchmarks": {},
  "overall_score": 0,
  "status": "running"
}
EOF

# Benchmark functions
check_file_permissions() {
    local score=0
    local total=0
    
    echo "🔐 Checking file permissions..."
    
    # Check sensitive files have correct permissions
    local sensitive_files=(
        "config/rbac.sh:755"
        "security/keys:700"
        ".cargo/config-security.toml:644"
    )
    
    for file_perm in "${sensitive_files[@]}"; do
        local file="${file_perm%:*}"
        local expected="${file_perm#*:}"
        ((total++))
        
        if [[ -e "$file" ]]; then
            local actual=$(stat -c "%a" "$file" 2>/dev/null || echo "000")
            if [[ "$actual" == "$expected" ]]; then
                ((score++))
                echo "   ✅ $file: $actual (expected: $expected)"
            else
                echo "   ❌ $file: $actual (expected: $expected)"
            fi
        else
            echo "   ⚠️ $file: not found"
        fi
    done
    
    local perm_score=$((score * 100 / total))
    echo "   Score: $perm_score% ($score/$total)"
    
    # Update results
    jq ".benchmarks.file_permissions = {"score": $perm_score, "details": "$score/$total files correct"}" "$BENCHMARK_RESULTS" > "$BENCHMARK_RESULTS.tmp"
    mv "$BENCHMARK_RESULTS.tmp" "$BENCHMARK_RESULTS"
}

check_security_tools() {
    local score=0
    local total=0
    
    echo "🛠️ Checking security tools..."
    
    local tools=("cargo-audit" "cargo-deny" "openssl" "gpg")
    
    for tool in "${tools[@]}"; do
        ((total++))
        if command -v "$tool" >/dev/null 2>&1; then
            ((score++))
            echo "   ✅ $tool: available"
        else
            echo "   ❌ $tool: not found"
        fi
    done
    
    local tools_score=$((score * 100 / total))
    echo "   Score: $tools_score% ($score/$total)"
    
    jq ".benchmarks.security_tools = {"score": $tools_score, "details": "$score/$total tools available"}" "$BENCHMARK_RESULTS" > "$BENCHMARK_RESULTS.tmp"
    mv "$BENCHMARK_RESULTS.tmp" "$BENCHMARK_RESULTS"
}

check_configuration_security() {
    local score=0
    local total=0
    
    echo "⚙️ Checking configuration security..."
    
    # Check for security configurations
    local configs=(
        "config/environment-secure.sh"
        ".cargo/config-security.toml"
        "scripts/security-automation/validate-security.sh"
    )
    
    for config in "${configs[@]}"; do
        ((total++))
        if [[ -f "$config" ]]; then
            ((score++))
            echo "   ✅ $config: exists"
        else
            echo "   ❌ $config: missing"
        fi
    done
    
    local config_score=$((score * 100 / total))
    echo "   Score: $config_score% ($score/$total)"
    
    jq ".benchmarks.configuration_security = {"score": $config_score, "details": "$score/$total configs present"}" "$BENCHMARK_RESULTS" > "$BENCHMARK_RESULTS.tmp"
    mv "$BENCHMARK_RESULTS.tmp" "$BENCHMARK_RESULTS"
}

# Run all benchmarks
run_all_benchmarks() {
    check_file_permissions
    check_security_tools
    check_configuration_security
    
    # Calculate overall score
    local overall_score=$(jq '.benchmarks | to_entries | map(.value.score) | add / length' "$BENCHMARK_RESULTS")
    
    # Update final results
    jq ".overall_score = $overall_score | .status = "complete"" "$BENCHMARK_RESULTS" > "$BENCHMARK_RESULTS.tmp"
    mv "$BENCHMARK_RESULTS.tmp" "$BENCHMARK_RESULTS"
    
    echo ""
    echo "📊 Security Benchmarks Complete"
    echo "   Overall Score: ${overall_score}%"
    echo "   Report: $BENCHMARK_RESULTS"
    
    if (( $(echo "$overall_score >= 80" | bc -l) )); then
        echo "✅ Security benchmarks PASSED"
        return 0
    else
        echo "❌ Security benchmarks FAILED"
        return 1
    fi
}

run_all_benchmarks
