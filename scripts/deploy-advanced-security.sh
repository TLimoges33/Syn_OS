#!/bin/bash
"""
Advanced Security Orchestrator Deployment Script
Deploys consciousness-controlled security operations with multi-tool integration.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/venv"
LOG_FILE="$PROJECT_ROOT/logs/deployment.log"

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Banner
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🧠 ADVANCED SECURITY ORCHESTRATOR DEPLOYMENT                             ║
║    Consciousness-Controlled Security Operations                              ║
║                                                                              ║
║    Phase 3: Advanced Security Tool Integration                               ║
║    - Nmap Network Discovery with AI Decision-Making                         ║
║    - Metasploit Exploitation Framework Automation                           ║
║    - Wireshark Traffic Analysis with Pattern Recognition                     ║
║    - Burp Suite Web Security Testing                                        ║
║    - OWASP ZAP Automated Scanning                                           ║
║    - Advanced Threat Intelligence System                                    ║
║    - Behavioral Analysis and Anomaly Detection                              ║
║    - Predictive Threat Modeling                                             ║
║    - Automated Incident Response                                            ║
║    - Self-Healing Security Mechanisms                                       ║
║    - Adaptive Defense Strategies                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log "🚀 Starting Advanced Security Orchestrator Deployment"

# Check if running as root for security tool installation
if [[ $EUID -eq 0 ]]; then
    warning "Running as root. This is required for security tool installation."
else
    info "Running as non-root user. Some security tools may require sudo privileges."
fi

# Step 1: System Requirements Check
log "📋 Step 1: Checking System Requirements"

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    info "✅ Linux system detected"
    DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    VERSION=$(lsb_release -sr 2>/dev/null || echo "Unknown")
    info "Distribution: $DISTRO $VERSION"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    info "✅ macOS system detected"
    DISTRO="macOS"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    info "✅ Windows system detected"
    DISTRO="Windows"
else
    warning "Unknown operating system: $OSTYPE"
    DISTRO="Unknown"
fi

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    info "✅ Python 3 found: $PYTHON_VERSION"
    
    # Check if version is 3.8+
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        info "✅ Python version is compatible (3.8+)"
    else
        error "❌ Python 3.8+ required, found $PYTHON_VERSION"
    fi
else
    error "❌ Python 3 not found. Please install Python 3.8+"
fi

# Check available memory
if command -v free &> /dev/null; then
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -ge 4 ]]; then
        info "✅ Sufficient memory: ${MEMORY_GB}GB"
    else
        warning "⚠️  Low memory: ${MEMORY_GB}GB (4GB+ recommended)"
    fi
fi

# Check disk space
if command -v df &> /dev/null; then
    DISK_SPACE=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $DISK_SPACE -ge 10 ]]; then
        info "✅ Sufficient disk space: ${DISK_SPACE}GB available"
    else
        warning "⚠️  Low disk space: ${DISK_SPACE}GB (10GB+ recommended)"
    fi
fi

# Step 2: Security Tools Installation
log "🔧 Step 2: Installing Security Tools"

install_security_tools() {
    case "$DISTRO" in
        "Ubuntu"|"Debian")
            info "Installing security tools for Debian/Ubuntu..."
            
            # Update package list
            sudo apt-get update -qq
            
            # Install basic security tools
            sudo apt-get install -y \
                nmap \
                wireshark-common \
                tshark \
                tcpdump \
                netcat \
                curl \
                wget \
                git \
                build-essential \
                python3-dev \
                python3-pip \
                python3-venv
            
            # Install additional security tools if available
            if apt-cache show zaproxy &> /dev/null; then
                sudo apt-get install -y zaproxy
                info "✅ OWASP ZAP installed"
            else
                warning "⚠️  OWASP ZAP not available in repositories"
            fi
            
            # Check for Metasploit
            if command -v msfconsole &> /dev/null; then
                info "✅ Metasploit already installed"
            else
                info "📦 Metasploit not found. Install manually if needed."
            fi
            
            # Check for Burp Suite
            if command -v burpsuite &> /dev/null; then
                info "✅ Burp Suite Community Edition found"
            else
                info "📦 Burp Suite not found. Install manually if needed."
            fi
            ;;
            
        "CentOS"|"RHEL"|"Fedora")
            info "Installing security tools for Red Hat/CentOS/Fedora..."
            
            # Use dnf or yum
            if command -v dnf &> /dev/null; then
                PKG_MGR="dnf"
            else
                PKG_MGR="yum"
            fi
            
            sudo $PKG_MGR update -y
            sudo $PKG_MGR install -y \
                nmap \
                wireshark \
                tcpdump \
                nc \
                curl \
                wget \
                git \
                gcc \
                python3-devel \
                python3-pip
            ;;
            
        "Arch")
            info "Installing security tools for Arch Linux..."
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm \
                nmap \
                wireshark-cli \
                tcpdump \
                netcat \
                curl \
                wget \
                git \
                base-devel \
                python \
                python-pip
            ;;
            
        "macOS")
            info "Installing security tools for macOS..."
            
            # Check for Homebrew
            if ! command -v brew &> /dev/null; then
                info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            # Install tools via Homebrew
            brew update
            brew install \
                nmap \
                wireshark \
                tcpdump \
                netcat \
                curl \
                wget \
                git \
                python@3.11
            ;;
            
        *)
            warning "⚠️  Unknown distribution. Please install security tools manually:"
            echo "  - nmap"
            echo "  - wireshark/tshark"
            echo "  - tcpdump"
            echo "  - python3 (3.8+)"
            echo "  - python3-pip"
            ;;
    esac
}

# Install security tools
install_security_tools

# Verify tool installations
log "🔍 Verifying Security Tool Installations"

check_tool() {
    local tool=$1
    local package=$2
    
    if command -v "$tool" &> /dev/null; then
        local version=$($tool --version 2>&1 | head -n1 || echo "Version unknown")
        info "✅ $package: $version"
        return 0
    else
        warning "⚠️  $package not found"
        return 1
    fi
}

# Check core tools
check_tool "nmap" "Nmap"
check_tool "tshark" "Wireshark/TShark"
check_tool "tcpdump" "TCPDump"
check_tool "python3" "Python 3"
check_tool "pip3" "Python Pip"

# Check optional tools
check_tool "msfconsole" "Metasploit Framework" || true
check_tool "burpsuite" "Burp Suite" || true
check_tool "zaproxy" "OWASP ZAP" || true

# Step 3: Python Environment Setup
log "🐍 Step 3: Setting up Python Environment"

# Create virtual environment if it doesn't exist
if [[ ! -d "$VENV_PATH" ]]; then
    info "Creating Python virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"
info "✅ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
log "📦 Installing Python Dependencies"

# Create requirements file for advanced security
cat > "$PROJECT_ROOT/requirements-advanced-security.txt" << EOF
# Advanced Security Orchestrator Dependencies
asyncio-mqtt>=0.11.1
aiohttp>=3.8.0
aiofiles>=0.8.0
cryptography>=3.4.8
psutil>=5.8.0
python-nmap>=0.7.1
scapy>=2.4.5
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
xmltodict>=0.13.0
pyyaml>=6.0
jinja2>=3.1.0
click>=8.1.0
rich>=12.0.0
tabulate>=0.9.0
colorama>=0.4.4
tqdm>=4.64.0
numpy>=1.21.0
pandas>=1.5.0
scikit-learn>=1.1.0
matplotlib>=3.5.0
seaborn>=0.11.0

# Testing dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0

# Development dependencies
black>=22.0.0
flake8>=5.0.0
mypy>=0.991
pre-commit>=2.20.0
EOF

# Install dependencies
pip install -r "$PROJECT_ROOT/requirements-advanced-security.txt"
info "✅ Python dependencies installed"

# Step 4: Configuration Setup
log "⚙️  Step 4: Setting up Configuration"

# Create configuration directory
mkdir -p "$PROJECT_ROOT/config/security"

# Create advanced security configuration
cat > "$PROJECT_ROOT/config/security/advanced_security_config.yaml" << EOF
# Advanced Security Orchestrator Configuration

# Consciousness Settings
consciousness:
  default_level: 0.5
  autonomous_mode: true
  learning_enabled: true
  predictive_defense: true
  self_healing: true

# Security Tools Configuration
tools:
  nmap:
    path: "/usr/bin/nmap"
    enabled: true
    default_options: ["-sS", "-O", "-sV", "--open"]
    max_scan_time: 300
    
  metasploit:
    path: "/usr/bin/msfconsole"
    enabled: false  # Requires manual installation
    database_enabled: false
    
  wireshark:
    path: "/usr/bin/tshark"
    enabled: true
    capture_duration: 60
    max_capture_size: "100MB"
    
  burpsuite:
    path: "/usr/bin/burpsuite"
    enabled: false  # Requires manual installation
    proxy_port: 8080
    
  zap:
    path: "/usr/bin/zaproxy"
    enabled: true
    proxy_port: 8081
    api_enabled: true

# Threat Intelligence Configuration
threat_intelligence:
  feeds:
    misp:
      enabled: false
      url: "https://misp.local"
      api_key: ""
    
    otx:
      enabled: false
      url: "https://otx.alienvault.com"
      api_key: ""
    
    virustotal:
      enabled: false
      url: "https://www.virustotal.com/api/v3"
      api_key: ""

# Security Distributions Integration
distributions:
  tails:
    enabled: false
    vm_path: ""
    
  parrot:
    enabled: false
    vm_path: ""
    
  kali:
    enabled: false
    vm_path: ""
    
  blackarch:
    enabled: false
    vm_path: ""

# Logging Configuration
logging:
  level: "INFO"
  file: "logs/advanced_security.log"
  max_size: "100MB"
  backup_count: 5
  
# Network Configuration
network:
  default_interface: "auto"
  scan_timeout: 300
  max_concurrent_scans: 5
  
# Performance Settings
performance:
  max_memory_usage: "2GB"
  max_cpu_usage: 80
  scan_throttling: true
EOF

info "✅ Configuration files created"

# Step 5: Security Permissions Setup
log "🔐 Step 5: Setting up Security Permissions"

# Create security group if it doesn't exist
if ! getent group security &> /dev/null; then
    sudo groupadd security
    info "✅ Security group created"
fi

# Add current user to security group
sudo usermod -a -G security "$USER"
info "✅ User added to security group"

# Set up capabilities for network tools (if supported)
if command -v setcap &> /dev/null; then
    # Allow nmap to run without root for SYN scans
    if [[ -f "/usr/bin/nmap" ]]; then
        sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap || true
        info "✅ Network capabilities set for nmap"
    fi
    
    # Allow tshark to capture packets without root
    if [[ -f "/usr/bin/tshark" ]]; then
        sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tshark || true
        info "✅ Network capabilities set for tshark"
    fi
fi

# Step 6: Service Setup
log "🚀 Step 6: Setting up Services"

# Create systemd service file for advanced security orchestrator
sudo tee /etc/systemd/system/advanced-security-orchestrator.service > /dev/null << EOF
[Unit]
Description=Advanced Security Orchestrator
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=security
WorkingDirectory=$PROJECT_ROOT
Environment=PATH=$VENV_PATH/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$VENV_PATH/bin/python -m src.security.advanced_security_orchestrator
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_ROOT/logs $PROJECT_ROOT/data

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable advanced-security-orchestrator.service
info "✅ Systemd service created and enabled"

# Step 7: Testing and Validation
log "🧪 Step 7: Testing Installation"

# Run basic tests
cd "$PROJECT_ROOT"

# Test Python imports
python3 -c "
import sys
sys.path.append('.')
try:
    from src.security.advanced_security_orchestrator import AdvancedSecurityOrchestrator
    print('✅ Advanced Security Orchestrator import successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

# Test tool availability
python3 -c "
import subprocess
import sys

tools = {
    'nmap': ['nmap', '--version'],
    'tshark': ['tshark', '--version'],
    'python3': ['python3', '--version']
}

for tool, cmd in tools.items():
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f'✅ {tool}: Available')
        else:
            print(f'⚠️  {tool}: Error - {result.stderr.strip()}')
    except Exception as e:
        print(f'❌ {tool}: Not available - {e}')
"

# Step 8: Documentation and Usage
log "📚 Step 8: Creating Documentation"

# Create usage documentation
cat > "$PROJECT_ROOT/ADVANCED_SECURITY_USAGE.md" << 'EOF'
# Advanced Security Orchestrator Usage Guide

## 🧠 Consciousness-Controlled Security Operations

The Advanced Security Orchestrator provides autonomous, AI-driven security operations with multi-tool integration.

### Quick Start

1. **Activate the environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run autonomous threat hunting:**
   ```python
   from src.security.advanced_security_orchestrator import AdvancedSecurityOrchestrator
   import asyncio
   
   async def main():
       orchestrator = AdvancedSecurityOrchestrator()
       await orchestrator.initialize_advanced_systems()
       
       # Perform autonomous threat hunting
       result = await orchestrator.autonomous_threat_hunting("192.168.1.0/24")
       print(f"Threat hunting completed: {result['operation_id']}")
   
   asyncio.run(main())
   ```

3. **Start the service:**
   ```bash
   sudo systemctl start advanced-security-orchestrator
   ```

### Features

- **🔍 Autonomous Threat Hunting**: AI-driven network reconnaissance and threat detection
- **🛡️ Multi-Tool Integration**: Nmap, Metasploit, Wireshark, Burp Suite, OWASP ZAP
- **🧠 Consciousness Control**: Adaptive decision-making based on threat levels
- **📊 Predictive Modeling**: Machine learning-based threat prediction
- **🔄 Self-Healing**: Automatic adaptation to new threats
- **⚡ Real-Time Response**: Immediate incident response and containment

### Security Tools Supported

1. **Nmap**: Network discovery and port scanning
2. **Metasploit**: Exploitation framework (requires separate installation)
3. **Wireshark/TShark**: Network traffic analysis with AI pattern recognition
4. **Burp Suite**: Web application security testing (requires separate installation)
5. **OWASP ZAP**: Automated web application scanning

### Configuration

Edit `config/security/advanced_security_config.yaml` to customize:

- Consciousness levels and autonomous behavior
- Tool paths and options
- Threat intelligence feeds
- Network and performance settings

### Monitoring

- **Logs**: `logs/advanced_security.log`
- **Service Status**: `sudo systemctl status advanced-security-orchestrator`
- **Real-time Monitoring**: Built-in consciousness monitoring dashboard

### Security Considerations

- Run with appropriate permissions (security group membership)
- Network capabilities are set for packet capture tools
- All operations are logged for audit purposes
- Consciousness level controls autonomous actions

### Troubleshooting

1. **Permission Issues**: Ensure user is in security group
2. **Tool Not Found**: Check tool installation and paths in config
3. **Network Access**: Verify network interfaces and permissions
4. **Memory Issues**: Adjust performance settings in configuration

For detailed documentation, see the project wiki.
EOF

info "✅ Usage documentation created"

# Step 9: Final Setup and Cleanup
log "🏁 Step 9: Final Setup"

# Set proper permissions
chmod +x "$PROJECT_ROOT/scripts/"*.sh
chmod 600 "$PROJECT_ROOT/config/security/"*.yaml

# Create data directories
mkdir -p "$PROJECT_ROOT/data/threat_intelligence"
mkdir -p "$PROJECT_ROOT/data/scan_results"
mkdir -p "$PROJECT_ROOT/data/behavioral_baselines"

# Set ownership
sudo chown -R "$USER:security" "$PROJECT_ROOT/data"
sudo chown -R "$USER:security" "$PROJECT_ROOT/logs"

info "✅ Permissions and directories configured"

# Deactivate virtual environment
deactivate

# Final summary
log "🎉 Advanced Security Orchestrator Deployment Complete!"

echo -e "${GREEN}"
cat << "EOF"

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🎯 DEPLOYMENT SUCCESSFUL!                                                 ║
║                                                                              ║
║    The Advanced Security Orchestrator is now ready for operation.           ║
║                                                                              ║
║    Next Steps:                                                               ║
║    1. Review configuration: config/security/advanced_security_config.yaml   ║
║    2. Read usage guide: ADVANCED_SECURITY_USAGE.md                          ║
║    3. Start the service: sudo systemctl start advanced-security-orchestrator║
║    4. Run tests: python test_advanced_security_orchestrator.py              ║
║                                                                              ║
║    🧠 Consciousness-controlled security operations are now active!          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

# Display system information
info "System Information:"
echo "  - Project Root: $PROJECT_ROOT"
echo "  - Virtual Environment: $VENV_PATH"
echo "  - Configuration: $PROJECT_ROOT/config/security/"
echo "  - Logs: $PROJECT_ROOT/logs/"
echo "  - Service: advanced-security-orchestrator.service"

# Display next steps
info "Next Steps:"
echo "  1. Activate environment: source $VENV_PATH/bin/activate"
echo "  2. Run tests: python test_advanced_security_orchestrator.py"
echo "  3. Start service: sudo systemctl start advanced-security-orchestrator"
echo "  4. Check status: sudo systemctl status advanced-security-orchestrator"

log "🚀 Advanced Security Orchestrator deployment completed successfully!"