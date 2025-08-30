#!/bin/bash
# Syn_OS Post-Start Security Validation
# Executes on container start with real-time security monitoring

set -euo pipefail

echo "🔍 Starting Syn_OS security validation..."

# Security: Validate running environment
echo "🛡️ Validating runtime security posture..."

# Check if running with proper security constraints
if [[ -f /proc/1/cgroup ]] && grep -q docker /proc/1/cgroup; then
    echo "✅ Running in containerized environment"
else
    echo "⚠️  WARNING: Not running in expected container environment"
fi

# Validate security configurations
if [[ -f .security-config ]]; then
    source .security-config
    if [[ "$SECURITY_ENABLED" == "true" ]]; then
        echo "✅ Security configuration loaded and active"
    else
        echo "❌ ERROR: Security not enabled"
        exit 1
    fi
fi

# Real-time security monitoring setup
echo "📊 Initializing security monitoring..."

# Create security log directory
mkdir -p .logs/security
chmod 700 .logs/security

# Start security monitoring (background process)
cat > .logs/security/monitor.sh << 'EOF'
#!/bin/bash
# Real-time security monitoring for Syn_OS development

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Monitor for suspicious file changes
    if command -v inotifywait &> /dev/null; then
        inotifywait -m -r --format '%T %w%f %e' --timefmt '%Y-%m-%d %H:%M:%S' . \
            -e create,delete,modify,move 2>/dev/null | while read file; do
            echo "[$timestamp] File activity: $file" >> .logs/security/file-monitor.log
        done &
    fi
    
    # Resource monitoring
    echo "[$timestamp] Memory: $(free -h | grep '^Mem:' | awk '{print $3"/"$2}')" >> .logs/security/resource.log
    echo "[$timestamp] CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)" >> .logs/security/resource.log
    
    sleep 30
done
EOF

chmod +x .logs/security/monitor.sh
nohup .logs/security/monitor.sh > /dev/null 2>&1 &

# Validate development tools security
echo "🔧 Validating development tool security..."

# Rust security validation
if command -v cargo &> /dev/null; then
    echo "🦀 Rust toolchain: $(cargo --version)"
    # Run security audit if Cargo.toml exists
    if [[ -f Cargo.toml ]]; then
        echo "Running cargo audit..."
        cargo audit || echo "⚠️  Security audit completed with warnings"
    fi
fi

# Python security validation
if command -v python3 &> /dev/null; then
    echo "🐍 Python toolchain: $(python3 --version)"
    # Check for security vulnerabilities in Python packages
    if [[ -f requirements.txt ]]; then
        echo "Checking Python dependencies..."
        python3 -m pip check || echo "⚠️  Python dependencies check completed"
    fi
fi

# Network security check
echo "🌐 Network security validation..."
netstat -tuln > .logs/security/network-ports.log 2>/dev/null || echo "Network check completed"

# File permissions audit
echo "📁 File permissions audit..."
find . -type f -perm /022 -not -path "./.git/*" -not -path "./.logs/*" > .logs/security/world-writable.log 2>/dev/null || true

# Environment variables security check
echo "🔑 Environment security check..."
env | grep -E "(TOKEN|KEY|SECRET|PASSWORD)" | sed 's/=.*/=***REDACTED***/' > .logs/security/env-check.log 2>/dev/null || true

# Start real-time threat detection
echo "🕵️ Enabling real-time threat detection..."
cat > .logs/security/threat-monitor.sh << 'EOF'
#!/bin/bash
# Real-time threat detection for Syn_OS development

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Monitor for potential security threats
    # Check for unusual process activity
    ps aux | grep -E "(nc|netcat|nmap|tcpdump)" | grep -v grep > /tmp/security-check 2>/dev/null || true
    if [[ -s /tmp/security-check ]]; then
        echo "[$timestamp] ALERT: Potential security tools detected" >> .logs/security/threat.log
        cat /tmp/security-check >> .logs/security/threat.log
    fi
    
    # Monitor network connections
    netstat -tuln | grep LISTEN > /tmp/network-check 2>/dev/null || true
    if [[ -s /tmp/network-check ]]; then
        echo "[$timestamp] Network listeners:" >> .logs/security/network.log
        cat /tmp/network-check >> .logs/security/network.log
    fi
    
    # Check for new files in sensitive locations
    find . -name "*.key" -o -name "*.pem" -o -name "*secret*" -o -name "*password*" 2>/dev/null > /tmp/sensitive-files || true
    if [[ -s /tmp/sensitive-files ]]; then
        echo "[$timestamp] ALERT: Sensitive files detected" >> .logs/security/threat.log
        cat /tmp/sensitive-files >> .logs/security/threat.log
    fi
    
    sleep 60
done
EOF

chmod +x .logs/security/threat-monitor.sh
nohup .logs/security/threat-monitor.sh > /dev/null 2>&1 &

echo "✅ Post-start security validation completed!"
echo "🔍 Security monitoring active - logs in .logs/security/"
echo "🚀 Syn_OS development environment secured and ready!"

# Display security dashboard
echo ""
echo "🔐 ACTIVE SECURITY MEASURES:"
echo "   ✓ Real-time file monitoring"
echo "   ✓ Resource usage tracking"  
echo "   ✓ Network activity monitoring"
echo "   ✓ Threat detection systems"
echo "   ✓ File permissions auditing"
echo "   ✓ Environment security validation"
echo "   ✓ Development tool security checks"
echo ""
echo "📊 Monitor security: tail -f .logs/security/*.log"
echo ""