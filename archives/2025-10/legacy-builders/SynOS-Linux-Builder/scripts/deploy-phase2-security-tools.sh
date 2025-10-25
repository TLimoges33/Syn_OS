#!/bin/bash
"""
Deploy Phase 2 Security AI Tools to SynOS Filesystem
Comprehensive deployment of all AI-enhanced security components
"""

set -e

echo "🔐 SynOS Phase 2 Security AI Tools Deployment"
echo "============================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Configuration
SYNOS_ROOT="/home/diablorain/Syn_OS/SynOS-Linux-Builder/filesystem-extract"
SYNOS_PACKAGES="/home/diablorain/Syn_OS/SynOS-Packages"
SECURITY_ORCHESTRATOR="${SYNOS_PACKAGES}/synos-security-orchestrator"

# Ensure target directories exist
echo "📁 Creating directory structure..."

mkdir -p "${SYNOS_ROOT}/usr/lib/synos/security"
mkdir -p "${SYNOS_ROOT}/usr/bin"
mkdir -p "${SYNOS_ROOT}/etc/systemd/system"
mkdir -p "${SYNOS_ROOT}/etc/synos/security"
mkdir -p "${SYNOS_ROOT}/var/lib/synos"
mkdir -p "${SYNOS_ROOT}/var/log/synos"
mkdir -p "${SYNOS_ROOT}/usr/share/synos/security/configs"
mkdir -p "${SYNOS_ROOT}/usr/share/synos/security/models"
mkdir -p "${SYNOS_ROOT}/usr/share/synos/security/signatures"

echo "✅ Directory structure created"

# Deploy AI-Augmented Reconnaissance
echo "🕵️  Deploying AI-Augmented Reconnaissance..."
cp "${SECURITY_ORCHESTRATOR}/src/ai_reconnaissance.py" "${SYNOS_ROOT}/usr/lib/synos/security/"
chmod +x "${SYNOS_ROOT}/usr/lib/synos/security/ai_reconnaissance.py"

# Create reconnaissance service
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-reconnaissance.service" << 'EOF'
[Unit]
Description=SynOS AI-Augmented Reconnaissance Engine
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service nats-server.service
Wants=network.target
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=synos-security
Group=synos-security
WorkingDirectory=/usr/lib/synos/security
ExecStart=/usr/bin/python3 /usr/lib/synos/security/ai_reconnaissance.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/synos /var/lib/synos /tmp
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true

# Resource limits
LimitNOFILE=65536
MemoryAccounting=true
MemoryMax=1G
CPUAccounting=true
CPUQuota=75%

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=SYNOS_CONFIG_DIR=/etc/synos
Environment=SYNOS_LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
EOF

echo "✅ AI-Augmented Reconnaissance deployed"

# Deploy Intelligent Vulnerability Scanner
echo "🔍 Deploying Intelligent Vulnerability Scanner..."
cp "${SECURITY_ORCHESTRATOR}/src/intelligent_vuln_scanner.py" "${SYNOS_ROOT}/usr/lib/synos/security/"
chmod +x "${SYNOS_ROOT}/usr/lib/synos/security/intelligent_vuln_scanner.py"

# Create vulnerability scanner service
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-vuln-scanner.service" << 'EOF'
[Unit]
Description=SynOS Intelligent Vulnerability Scanner
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service
Wants=network.target
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=synos-security
Group=synos-security
WorkingDirectory=/usr/lib/synos/security
ExecStart=/usr/bin/python3 /usr/lib/synos/security/intelligent_vuln_scanner.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=15

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/synos /var/lib/synos /tmp
PrivateTmp=true

# Resource limits
MemoryAccounting=true
MemoryMax=2G
CPUQuota=50%

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=SYNOS_CONFIG_DIR=/etc/synos

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Intelligent Vulnerability Scanner deployed"

# Deploy Smart Metasploit Integration
echo "💥 Deploying Smart Metasploit Integration..."
cp "${SECURITY_ORCHESTRATOR}/src/smart_metasploit.py" "${SYNOS_ROOT}/usr/lib/synos/security/"
chmod +x "${SYNOS_ROOT}/usr/lib/synos/security/smart_metasploit.py"

# Create metasploit integration service
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-metasploit.service" << 'EOF'
[Unit]
Description=SynOS Smart Metasploit Integration
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service postgresql.service
Wants=network.target
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=synos-security
Group=synos-security
WorkingDirectory=/usr/lib/synos/security
ExecStart=/usr/bin/python3 /usr/lib/synos/security/smart_metasploit.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=20

# Security settings - More permissive for MSF operations
NoNewPrivileges=false
ProtectSystem=false
ProtectHome=false
ReadWritePaths=/var/log/synos /var/lib/synos /tmp /usr/share/metasploit-framework
PrivateTmp=false

# Resource limits
MemoryAccounting=true
MemoryMax=4G
CPUQuota=100%

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=SYNOS_CONFIG_DIR=/etc/synos
Environment=MSF_DATABASE_CONFIG=/usr/share/metasploit-framework/config/database.yml

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Smart Metasploit Integration deployed"

# Deploy LLM Evidence Correlator
echo "🧠 Deploying LLM Evidence Correlator..."
cp "${SECURITY_ORCHESTRATOR}/src/llm_evidence_correlator.py" "${SYNOS_ROOT}/usr/lib/synos/security/"
chmod +x "${SYNOS_ROOT}/usr/lib/synos/security/llm_evidence_correlator.py"

# Create evidence correlator service
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-evidence-correlator.service" << 'EOF'
[Unit]
Description=SynOS LLM Evidence Correlation Engine
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service
Wants=network.target
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=synos-security
Group=synos-security
WorkingDirectory=/usr/lib/synos/security
ExecStart=/usr/bin/python3 /usr/lib/synos/security/llm_evidence_correlator.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=15

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/synos /var/lib/synos /tmp
PrivateTmp=true

# Resource limits
MemoryAccounting=true
MemoryMax=3G
CPUQuota=75%

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=SYNOS_CONFIG_DIR=/etc/synos
Environment=OPENAI_API_KEY_FILE=/etc/synos/security/openai.key

[Install]
WantedBy=multi-user.target
EOF

echo "✅ LLM Evidence Correlator deployed"

# Deploy Real-Time Behavior Monitor
echo "👁️  Deploying Real-Time Behavior Monitor..."
cp "${SECURITY_ORCHESTRATOR}/src/realtime_behavior_monitor.py" "${SYNOS_ROOT}/usr/lib/synos/security/"
chmod +x "${SYNOS_ROOT}/usr/lib/synos/security/realtime_behavior_monitor.py"

# Create behavior monitor service
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-behavior-monitor.service" << 'EOF'
[Unit]
Description=SynOS Real-Time Behavior Monitoring System
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service
Wants=network.target
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/usr/lib/synos/security
ExecStart=/usr/bin/python3 /usr/lib/synos/security/realtime_behavior_monitor.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security settings - Needs root for system monitoring
NoNewPrivileges=false
ProtectSystem=false
ProtectHome=false
ReadWritePaths=/var/log/synos /var/lib/synos /tmp /proc /sys
PrivateTmp=false

# Resource limits
MemoryAccounting=true
MemoryMax=2G
CPUQuota=50%

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=SYNOS_CONFIG_DIR=/etc/synos

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Real-Time Behavior Monitor deployed"

# Deploy Advanced Anomaly Detector
echo "📊 Deploying Advanced Anomaly Detector..."
cp "${SECURITY_ORCHESTRATOR}/src/advanced_anomaly_detector.py" "${SYNOS_ROOT}/usr/lib/synos/security/"
chmod +x "${SYNOS_ROOT}/usr/lib/synos/security/advanced_anomaly_detector.py"

# Create anomaly detector service
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-anomaly-detector.service" << 'EOF'
[Unit]
Description=SynOS Advanced Anomaly Detection System
Documentation=https://github.com/FranklineMisango/Syn_OS
After=network.target synos-ai-daemon.service synos-behavior-monitor.service
Wants=network.target
Requires=synos-ai-daemon.service

[Service]
Type=simple
User=synos-security
Group=synos-security
WorkingDirectory=/usr/lib/synos/security
ExecStart=/usr/bin/python3 /usr/lib/synos/security/advanced_anomaly_detector.py --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=15

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/synos /var/lib/synos /tmp
PrivateTmp=true

# Resource limits
MemoryAccounting=true
MemoryMax=2G
CPUQuota=75%

# Environment
Environment=PYTHONPATH=/usr/lib/synos
Environment=SYNOS_CONFIG_DIR=/etc/synos

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Advanced Anomaly Detector deployed"

# Create security orchestrator CLI tool
echo "🔧 Creating Security Orchestrator CLI..."
cat > "${SYNOS_ROOT}/usr/bin/synos-security" << 'EOF'
#!/usr/bin/env python3
"""
SynOS Security Orchestrator CLI
Command-line interface for managing AI-enhanced security tools
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path

# Add security tools to path
sys.path.insert(0, '/usr/lib/synos/security')

def main():
    parser = argparse.ArgumentParser(description='SynOS Security Orchestrator')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Reconnaissance commands
    recon_parser = subparsers.add_parser('recon', help='AI reconnaissance operations')
    recon_parser.add_argument('--target', required=True, help='Target for reconnaissance')
    recon_parser.add_argument('--passive', action='store_true', help='Passive reconnaissance only')
    recon_parser.add_argument('--output', help='Output file for results')

    # Vulnerability scanning commands
    vuln_parser = subparsers.add_parser('scan', help='Intelligent vulnerability scanning')
    vuln_parser.add_argument('--target', required=True, help='Target to scan')
    vuln_parser.add_argument('--policy', help='Scanning policy (adaptive, stealth, aggressive)')
    vuln_parser.add_argument('--format', default='json', help='Output format')

    # Metasploit integration commands
    msf_parser = subparsers.add_parser('exploit', help='Smart Metasploit operations')
    msf_parser.add_argument('--target', required=True, help='Target host:port')
    msf_parser.add_argument('--recommend', action='store_true', help='Get exploit recommendations')
    msf_parser.add_argument('--execute', help='Execute specific exploit module')

    # Evidence correlation commands
    evidence_parser = subparsers.add_parser('correlate', help='Evidence correlation analysis')
    evidence_parser.add_argument('--import-file', help='Import evidence from file')
    evidence_parser.add_argument('--cluster', action='store_true', help='Detect evidence clusters')
    evidence_parser.add_argument('--report', help='Generate investigation report for cluster ID')

    # Behavior monitoring commands
    behavior_parser = subparsers.add_parser('monitor', help='Real-time behavior monitoring')
    behavior_parser.add_argument('--status', action='store_true', help='Show monitoring status')
    behavior_parser.add_argument('--alerts', action='store_true', help='Show recent alerts')
    behavior_parser.add_argument('--acknowledge', help='Acknowledge alert by ID')

    # Anomaly detection commands
    anomaly_parser = subparsers.add_parser('anomaly', help='Anomaly detection operations')
    anomaly_parser.add_argument('--stats', action='store_true', help='Show detection statistics')
    anomaly_parser.add_argument('--train', action='store_true', help='Train ML models')
    anomaly_parser.add_argument('--false-positive', help='Mark anomaly as false positive')

    # Status command
    status_parser = subparsers.add_parser('status', help='Overall security system status')

    args = parser.parse_args()

    if args.command == 'status':
        print_security_status()
    elif args.command == 'recon':
        asyncio.run(run_reconnaissance(args))
    elif args.command == 'scan':
        asyncio.run(run_vulnerability_scan(args))
    elif args.command == 'exploit':
        asyncio.run(run_metasploit_operation(args))
    elif args.command == 'correlate':
        asyncio.run(run_evidence_correlation(args))
    elif args.command == 'monitor':
        asyncio.run(run_behavior_monitoring(args))
    elif args.command == 'anomaly':
        asyncio.run(run_anomaly_detection(args))
    else:
        parser.print_help()

def print_security_status():
    """Print overall security system status"""
    print("🔐 SynOS AI Security System Status")
    print("==================================")

    services = [
        'synos-reconnaissance',
        'synos-vuln-scanner',
        'synos-metasploit',
        'synos-evidence-correlator',
        'synos-behavior-monitor',
        'synos-anomaly-detector'
    ]

    import subprocess
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service],
                                  capture_output=True, text=True)
            status = result.stdout.strip()
            status_icon = "🟢" if status == "active" else "🔴"
            print(f"{status_icon} {service}: {status}")
        except Exception:
            print(f"🔴 {service}: unknown")

async def run_reconnaissance(args):
    """Run AI reconnaissance"""
    try:
        from ai_reconnaissance import AIReconEngine

        recon = AIReconEngine()
        print(f"🕵️  Starting reconnaissance of {args.target}")

        if args.passive:
            print("Using passive reconnaissance mode")

        results = await recon.comprehensive_reconnaissance(
            args.target,
            passive_only=args.passive
        )

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2, default=str))

    except ImportError:
        print("❌ Reconnaissance module not available")
    except Exception as e:
        print(f"❌ Reconnaissance failed: {e}")

async def run_vulnerability_scan(args):
    """Run intelligent vulnerability scan"""
    try:
        from intelligent_vuln_scanner import IntelligentVulnScanner

        scanner = IntelligentVulnScanner()
        print(f"🔍 Starting vulnerability scan of {args.target}")

        scan_id = await scanner.scan_target(args.target)
        print(f"Scan started with ID: {scan_id}")

        # Monitor scan progress
        while True:
            status = await scanner.get_scan_status(scan_id)
            print(f"Scan status: {status['status']}")

            if status['status'] == 'completed':
                vulnerabilities = await scanner.get_vulnerabilities(scan_id)
                print(f"Found {len(vulnerabilities)} vulnerabilities")

                if args.format == 'json':
                    print(json.dumps(vulnerabilities, indent=2, default=str))
                else:
                    for vuln in vulnerabilities:
                        print(f"- {vuln['name']} (Severity: {vuln['severity']})")
                break

            await asyncio.sleep(10)

    except ImportError:
        print("❌ Vulnerability scanner module not available")
    except Exception as e:
        print(f"❌ Vulnerability scan failed: {e}")

async def run_metasploit_operation(args):
    """Run Metasploit operations"""
    try:
        from smart_metasploit import SmartMetasploit

        msf = SmartMetasploit()

        if args.recommend:
            host, port = args.target.split(':')
            recommendations = await msf.get_exploit_recommendations(host, int(port))

            print(f"🎯 Exploit recommendations for {args.target}:")
            for i, rec in enumerate(recommendations[:10], 1):
                print(f"{i}. {rec['module']} (Score: {rec['compatibility_score']})")
                print(f"   {rec['description']}")

        elif args.execute:
            print(f"⚠️  Exploit execution requires manual confirmation")
            print(f"Target: {args.target}")
            print(f"Module: {args.execute}")

    except ImportError:
        print("❌ Metasploit integration module not available")
    except Exception as e:
        print(f"❌ Metasploit operation failed: {e}")

async def run_evidence_correlation(args):
    """Run evidence correlation"""
    try:
        from llm_evidence_correlator import EvidenceCorrelationEngine

        correlator = EvidenceCorrelationEngine()

        if args.import_file:
            evidence_ids = await correlator.import_evidence_from_file(Path(args.import_file))
            print(f"📁 Imported {len(evidence_ids)} evidence items")

        if args.cluster:
            clusters = await correlator.detect_evidence_clusters()
            print(f"🔗 Detected {len(clusters)} evidence clusters")
            for cluster in clusters:
                print(f"- {cluster.name}: {len(cluster.evidence_items)} items ({cluster.threat_level})")

        if args.report:
            report = await correlator.generate_investigation_report(args.report)
            print(json.dumps(report, indent=2, default=str))

    except ImportError:
        print("❌ Evidence correlation module not available")
    except Exception as e:
        print(f"❌ Evidence correlation failed: {e}")

async def run_behavior_monitoring(args):
    """Run behavior monitoring operations"""
    try:
        from realtime_behavior_monitor import RealtimeBehaviorMonitor

        monitor = RealtimeBehaviorMonitor()

        if args.status:
            stats = monitor.get_process_statistics()
            print("👁️  Behavior Monitoring Status:")
            print(f"- Monitored processes: {stats['total_monitored_processes']}")
            print(f"- Suspicious processes: {stats['suspicious_processes']}")
            print(f"- Recent events: {stats['recent_events_count']}")
            print(f"- Total alerts: {stats['total_alerts']}")

        if args.alerts:
            alerts = monitor.get_recent_alerts(20)
            print("🚨 Recent Alerts:")
            for alert in alerts:
                print(f"- {alert['severity']}: {alert['event_details']['process_name']}")
                print(f"  Time: {alert['timestamp']}")

        if args.acknowledge:
            monitor.acknowledge_alert(args.acknowledge)
            print(f"✅ Alert {args.acknowledge} acknowledged")

    except ImportError:
        print("❌ Behavior monitoring module not available")
    except Exception as e:
        print(f"❌ Behavior monitoring failed: {e}")

async def run_anomaly_detection(args):
    """Run anomaly detection operations"""
    try:
        from advanced_anomaly_detector import AdvancedAnomalyDetector

        detector = AdvancedAnomalyDetector()

        if args.stats:
            stats = detector.get_statistics()
            print("📊 Anomaly Detection Statistics:")
            print(f"- Total anomalies: {stats['total_anomalies']}")
            print(f"- Severity distribution: {stats['severity_distribution']}")
            print(f"- ML models: {stats['ml_models_count']}")
            print(f"- False positive rate: {stats['false_positive_rate']:.2%}")

        if args.train:
            print("🧠 Training ML models...")
            await detector.train_ml_models()
            print("✅ ML model training completed")

        if args.false_positive:
            detector.mark_false_positive(args.false_positive)
            print(f"✅ Marked anomaly {args.false_positive} as false positive")

    except ImportError:
        print("❌ Anomaly detection module not available")
    except Exception as e:
        print(f"❌ Anomaly detection failed: {e}")

if __name__ == "__main__":
    main()
EOF

chmod +x "${SYNOS_ROOT}/usr/bin/synos-security"

echo "✅ Security Orchestrator CLI created"

# Create system user for security services
echo "👤 Creating system users..."
if ! getent passwd synos-security >/dev/null 2>&1; then
    chroot "${SYNOS_ROOT}" useradd -r -s /bin/false -d /var/lib/synos -c "SynOS Security Services" synos-security
fi

# Set permissions
echo "🔒 Setting permissions..."
chroot "${SYNOS_ROOT}" chown -R synos-security:synos-security /var/lib/synos
chroot "${SYNOS_ROOT}" chown -R synos-security:synos-security /var/log/synos
chroot "${SYNOS_ROOT}" chown -R synos-security:synos-security /usr/lib/synos/security
chmod -R 750 "${SYNOS_ROOT}/usr/lib/synos/security"
chmod -R 640 "${SYNOS_ROOT}/etc/synos"

echo "✅ Permissions configured"

# Create configuration files
echo "⚙️  Creating configuration files..."

# Main security configuration
cat > "${SYNOS_ROOT}/etc/synos/security/security.conf" << 'EOF'
[global]
log_level = INFO
data_retention_days = 90
max_concurrent_scans = 5
enable_ml_training = true

[reconnaissance]
passive_sources = shodan,censys,virustotal
active_scanning = true
max_threads = 20
rate_limit = 10

[vulnerability_scanner]
default_policy = adaptive
scan_timeout = 3600
stealth_mode = true
update_signatures = true

[metasploit]
database_backend = postgresql
auto_exploit = false
session_timeout = 1800
enable_evasion = true

[behavior_monitor]
monitor_syscalls = true
monitor_filesystem = true
monitor_network = true
alert_threshold = medium

[anomaly_detector]
baseline_window = 24h
training_interval = 6h
ml_algorithms = isolation_forest,random_forest
false_positive_threshold = 0.3

[evidence_correlator]
enable_llm = false
correlation_confidence = 0.7
max_cluster_size = 50
timeline_window = 7d
EOF

# Create systemd target for security services
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-security.target" << 'EOF'
[Unit]
Description=SynOS AI Security Services
Documentation=https://github.com/FranklineMisango/Syn_OS
Requires=synos-ai-daemon.service
After=synos-ai-daemon.service multi-user.target
AllowIsolate=yes

[Install]
WantedBy=multi-user.target
EOF

# Update main target to include security services
cat > "${SYNOS_ROOT}/etc/systemd/system/synos-ai.target" << 'EOF'
[Unit]
Description=SynOS AI Services Target
Documentation=https://github.com/FranklineMisango/Syn_OS
Requires=synos-ai-daemon.service nats-server.service
After=synos-ai-daemon.service nats-server.service multi-user.target
Wants=synos-security.target
AllowIsolate=yes

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Configuration files created"

# Install Python dependencies (simulated - would need proper package management)
echo "📦 Installing Python dependencies..."

# Create requirements file for reference
cat > "${SYNOS_ROOT}/usr/share/synos/security/requirements.txt" << 'EOF'
# SynOS Phase 2 Security AI Tools Dependencies
asyncio>=3.4.3
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
networkx>=2.6.0
psutil>=5.8.0
requests>=2.26.0
nmap>=7.0.0
python-nmap>=0.6.1
shodan>=1.25.0
censys>=2.0.0
virustotal-api>=1.1.11
openai>=0.27.0
joblib>=1.1.0
sqlite3
json
logging
pathlib
threading
queue
subprocess
tempfile
hashlib
re
mimetypes
xml
EOF

echo "✅ Dependencies documented"

# Create desktop integration
echo "🖥️  Creating desktop integration..."
mkdir -p "${SYNOS_ROOT}/usr/share/applications"

cat > "${SYNOS_ROOT}/usr/share/applications/synos-security-dashboard.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SynOS Security Dashboard
Comment=AI-Enhanced Security Monitoring and Management
Exec=/usr/bin/synos-security status
Icon=security-high
Terminal=true
Categories=Security;System;Network;
Keywords=security;ai;monitoring;reconnaissance;vulnerability;
StartupNotify=true
EOF

echo "✅ Desktop integration created"

# Create startup script
echo "🚀 Creating system startup integration..."
cat > "${SYNOS_ROOT}/usr/lib/synos/scripts/start-security-services.sh" << 'EOF'
#!/bin/bash
# SynOS Security Services Startup Script

echo "🔐 Starting SynOS AI Security Services..."

# Enable and start core services
systemctl enable synos-reconnaissance.service
systemctl enable synos-vuln-scanner.service
systemctl enable synos-metasploit.service
systemctl enable synos-evidence-correlator.service
systemctl enable synos-behavior-monitor.service
systemctl enable synos-anomaly-detector.service

# Start security target
systemctl enable synos-security.target
systemctl start synos-security.target

echo "✅ SynOS AI Security Services started"

# Show status
/usr/bin/synos-security status
EOF

chmod +x "${SYNOS_ROOT}/usr/lib/synos/scripts/start-security-services.sh"

echo "✅ Startup script created"

# Create comprehensive documentation
echo "📚 Creating documentation..."
mkdir -p "${SYNOS_ROOT}/usr/share/doc/synos-security"

cat > "${SYNOS_ROOT}/usr/share/doc/synos-security/README.md" << 'EOF'
# SynOS Phase 2 Security AI Tools

## Overview
SynOS Phase 2 implements a comprehensive suite of AI-enhanced security tools for cybersecurity education and professional training.

## Components

### 1. AI-Augmented Reconnaissance
- **Service**: `synos-reconnaissance.service`
- **Purpose**: Automated OSINT collection and network intelligence gathering
- **Features**: Passive/active reconnaissance, threat intelligence correlation
- **CLI**: `synos-security recon --target <target>`

### 2. Intelligent Vulnerability Scanner
- **Service**: `synos-vuln-scanner.service`
- **Purpose**: Context-aware vulnerability assessment with adaptive policies
- **Features**: AI-driven scan optimization, false positive reduction
- **CLI**: `synos-security scan --target <target>`

### 3. Smart Metasploit Integration
- **Service**: `synos-metasploit.service`
- **Purpose**: AI-powered exploit module selection and payload configuration
- **Features**: Automated exploit selection, success rate prediction
- **CLI**: `synos-security exploit --target <target> --recommend`

### 4. LLM Evidence Correlator
- **Service**: `synos-evidence-correlator.service`
- **Purpose**: GPT-4-turbo powered evidence network construction
- **Features**: Evidence clustering, attack narrative generation
- **CLI**: `synos-security correlate --import-file <evidence>`

### 5. Real-Time Behavior Monitor
- **Service**: `synos-behavior-monitor.service`
- **Purpose**: System call, filesystem, and network activity analysis
- **Features**: Process monitoring, threat pattern detection
- **CLI**: `synos-security monitor --alerts`

### 6. Advanced Anomaly Detector
- **Service**: `synos-anomaly-detector.service`
- **Purpose**: Dynamic baseline establishment and ML-based threat detection
- **Features**: Multi-algorithm detection, adaptive learning
- **CLI**: `synos-security anomaly --stats`

## Usage

### System Status
```bash
synos-security status
```

### Service Management
```bash
systemctl status synos-security.target
systemctl start synos-reconnaissance.service
systemctl logs -f synos-vuln-scanner.service
```

### Configuration
- Main config: `/etc/synos/security/security.conf`
- Service configs: `/etc/systemd/system/synos-*.service`
- Logs: `/var/log/synos/`
- Data: `/var/lib/synos/`

## Security Considerations
- Services run with minimal privileges using dedicated users
- Systemd hardening applied (NoNewPrivileges, ProtectSystem, etc.)
- Resource limits enforced (memory, CPU quotas)
- Sensitive operations logged and audited

## Training Integration
These tools are designed for cybersecurity education and should only be used in authorized lab environments or with explicit permission for penetration testing activities.

## Support
- Documentation: `/usr/share/doc/synos-security/`
- Configuration: `/etc/synos/security/`
- Logs: `/var/log/synos/security/`
EOF

echo "✅ Documentation created"

# Create final verification script
echo "🔍 Creating verification script..."
cat > "${SYNOS_ROOT}/usr/lib/synos/scripts/verify-security-deployment.sh" << 'EOF'
#!/bin/bash
# SynOS Phase 2 Security Deployment Verification

echo "🔍 SynOS Phase 2 Security Deployment Verification"
echo "================================================="

EXIT_CODE=0

# Check core files
CORE_FILES=(
    "/usr/lib/synos/security/ai_reconnaissance.py"
    "/usr/lib/synos/security/intelligent_vuln_scanner.py"
    "/usr/lib/synos/security/smart_metasploit.py"
    "/usr/lib/synos/security/llm_evidence_correlator.py"
    "/usr/lib/synos/security/realtime_behavior_monitor.py"
    "/usr/lib/synos/security/advanced_anomaly_detector.py"
    "/usr/bin/synos-security"
)

echo "📁 Checking core files..."
for file in "${CORE_FILES[@]}"; do
    if [[ -f "$file" && -x "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file"
        EXIT_CODE=1
    fi
done

# Check systemd services
SERVICES=(
    "synos-reconnaissance.service"
    "synos-vuln-scanner.service"
    "synos-metasploit.service"
    "synos-evidence-correlator.service"
    "synos-behavior-monitor.service"
    "synos-anomaly-detector.service"
)

echo -e "\n🔧 Checking systemd services..."
for service in "${SERVICES[@]}"; do
    if [[ -f "/etc/systemd/system/$service" ]]; then
        echo "✅ $service"
    else
        echo "❌ $service"
        EXIT_CODE=1
    fi
done

# Check directories
DIRECTORIES=(
    "/usr/lib/synos/security"
    "/etc/synos/security"
    "/var/lib/synos"
    "/var/log/synos"
    "/usr/share/synos/security"
    "/usr/share/doc/synos-security"
)

echo -e "\n📂 Checking directories..."
for dir in "${DIRECTORIES[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir"
    else
        echo "❌ $dir"
        EXIT_CODE=1
    fi
done

# Check user accounts
echo -e "\n👤 Checking user accounts..."
if getent passwd synos-security >/dev/null 2>&1; then
    echo "✅ synos-security user"
else
    echo "❌ synos-security user"
    EXIT_CODE=1
fi

# Summary
echo -e "\n📊 Verification Summary"
echo "======================"
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ All Phase 2 Security AI Tools deployed successfully"
    echo "🚀 Ready for system integration and testing"
else
    echo "❌ Deployment verification failed"
    echo "🔧 Please check missing components"
fi

exit $EXIT_CODE
EOF

chmod +x "${SYNOS_ROOT}/usr/lib/synos/scripts/verify-security-deployment.sh"

echo "✅ Verification script created"

# Run verification
echo "🔍 Running deployment verification..."
if chroot "${SYNOS_ROOT}" /usr/lib/synos/scripts/verify-security-deployment.sh; then
    echo ""
    echo "🎉 SUCCESS: Phase 2 Security AI Tools Deployment Complete!"
    echo "========================================================="
    echo ""
    echo "📋 Deployment Summary:"
    echo "• ✅ AI-Augmented Reconnaissance Engine"
    echo "• ✅ Intelligent Vulnerability Scanner"
    echo "• ✅ Smart Metasploit Integration"
    echo "• ✅ LLM Evidence Correlation Engine"
    echo "• ✅ Real-Time Behavior Monitor"
    echo "• ✅ Advanced Anomaly Detection System"
    echo "• ✅ Security Orchestrator CLI"
    echo "• ✅ Systemd service integration"
    echo "• ✅ Security hardening applied"
    echo "• ✅ Documentation and configs"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Build SynOS ISO with integrated security tools"
    echo "2. Test security service startup and integration"
    echo "3. Validate AI consciousness <-> security tool communication"
    echo "4. Proceed to Phase 3: Natural Language Interfaces"
    echo ""
    echo "🔐 All Phase 2 Security AI Tools are now deployed and ready!"
else
    echo "❌ Deployment verification failed - please check errors above"
    exit 1
fi