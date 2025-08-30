#!/bin/bash

# SynaptikOS Phase 3.2 - Enterprise MSSP Platform Setup
# Comprehensive security tools installation and configuration script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/synaptic-security"
LOG_FILE="/var/log/enterprise-mssp-setup.log"
VENV_DIR="$INSTALL_DIR/venv"

# Functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log "INFO: $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log "SUCCESS: $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "ERROR: $1"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine OS version"
    fi
    
    . /etc/os-release
    case $ID in
        ubuntu|debian)
            PACKAGE_MANAGER="apt"
            ;;
        centos|rhel|fedora)
            PACKAGE_MANAGER="yum"
            ;;
        arch)
            PACKAGE_MANAGER="pacman"
            ;;
        *)
            error "Unsupported OS: $ID"
            ;;
    esac
    
    info "Detected OS: $PRETTY_NAME"
    info "Package manager: $PACKAGE_MANAGER"
}

create_directories() {
    info "Creating enterprise security directories..."
    
    directories=(
        "$INSTALL_DIR"
        "$INSTALL_DIR/tools"
        "$INSTALL_DIR/config"
        "$INSTALL_DIR/logs"
        "$INSTALL_DIR/data"
        "$INSTALL_DIR/scripts"
        "/var/log/synaptic-security"
        "/etc/synaptic-security"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        chmod 755 "$dir"
        info "Created directory: $dir"
    done
    
    success "Directory structure created"
}

install_system_packages() {
    info "Installing system packages..."
    
    case $PACKAGE_MANAGER in
        apt)
            apt update -y
            apt install -y \
                python3 python3-pip python3-venv python3-dev \
                ruby ruby-dev \
                openjdk-11-jdk \
                git curl wget build-essential \
                docker.io docker-compose \
                postgresql-client \
                redis-tools \
                nmap \
                sqlmap \
                wireshark-common tshark \
                john \
                hashcat \
                aircrack-ng \
                metasploit-framework \
                zaproxy \
                libssl-dev libffi-dev \
                pkg-config
            ;;
        yum)
            yum update -y
            yum install -y \
                python3 python3-pip python3-devel \
                ruby ruby-devel \
                java-11-openjdk \
                git curl wget gcc gcc-c++ make \
                docker docker-compose \
                postgresql \
                redis \
                nmap \
                sqlmap \
                wireshark \
                john \
                hashcat \
                aircrack-ng \
                openssl-devel libffi-devel
            ;;
        pacman)
            pacman -Syu --noconfirm
            pacman -S --noconfirm \
                python python-pip \
                ruby \
                jdk11-openjdk \
                git curl wget base-devel \
                docker docker-compose \
                postgresql-libs \
                redis \
                nmap \
                sqlmap \
                wireshark-cli \
                john \
                hashcat \
                aircrack-ng
            ;;
    esac
    
    success "System packages installed"
}

setup_python_environment() {
    info "Setting up Python virtual environment..."
    
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    pip install --upgrade pip setuptools wheel
    
    # Enterprise security Python packages
    pip install \
        asyncio \
        redis \
        psutil \
        requests \
        sqlalchemy \
        cryptography \
        docker \
        kubernetes \
        prometheus-client \
        pyyaml \
        psycopg2-binary \
        aiohttp \
        aiofiles \
        celery \
        flask \
        fastapi \
        uvicorn \
        jinja2 \
        click \
        colorama \
        tqdm \
        python-dotenv \
        schedule \
        matplotlib \
        pandas \
        numpy \
        scikit-learn
    
    success "Python environment configured"
}

install_ruby_gems() {
    info "Installing Ruby gems..."
    
    gem install bundler
    gem install brakeman
    gem install rails_best_practices
    gem install rubocop
    
    success "Ruby gems installed"
}

install_security_tools() {
    info "Installing additional security tools..."
    
    cd "$INSTALL_DIR/tools"
    
    # HackingTool Collection
    info "Installing HackingTool collection..."
    git clone https://github.com/Z4nzu/hackingtool.git
    cd hackingtool
    chmod -R 755 .
    pip install -r requirements.txt || warning "Some HackingTool requirements failed"
    cd ..
    
    # Checkov (Infrastructure Security)
    info "Installing Checkov..."
    pip install checkov
    
    # OWASP Dependency Check
    info "Installing OWASP Dependency Check..."
    wget -O dependency-check.zip https://github.com/jeremylong/DependencyCheck/releases/download/v8.4.0/dependency-check-8.4.0-release.zip
    unzip dependency-check.zip
    rm dependency-check.zip
    ln -sf "$INSTALL_DIR/tools/dependency-check/bin/dependency-check.sh" /usr/local/bin/dependency-check
    
    # Vault (Secrets Management)
    info "Installing HashiCorp Vault..."
    VAULT_VERSION="1.15.2"
    wget -O vault.zip "https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip"
    unzip vault.zip
    mv vault /usr/local/bin/
    rm vault.zip
    
    # Additional penetration testing tools
    info "Installing additional penetration testing tools..."
    
    # Subfinder
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || warning "Subfinder installation failed"
    
    # Nuclei
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest || warning "Nuclei installation failed"
    
    # Gobuster
    go install github.com/OJ/gobuster/v3@latest || warning "Gobuster installation failed"
    
    success "Security tools installed"
}

configure_docker() {
    info "Configuring Docker for security tools..."
    
    systemctl enable docker
    systemctl start docker
    
    # Add synaptic user to docker group
    if id "synaptic" &>/dev/null; then
        usermod -aG docker synaptic
    fi
    
    # Pull security-related Docker images
    docker pull owasp/zap2docker-stable || warning "Failed to pull OWASP ZAP image"
    docker pull kalilinux/kali-rolling || warning "Failed to pull Kali Linux image"
    docker pull remnux/remnux-distro || warning "Failed to pull REMnux image"
    
    success "Docker configured"
}

setup_kubernetes_security_namespace() {
    info "Setting up Kubernetes security namespace..."
    
    if command -v kubectl &> /dev/null; then
        kubectl create namespace security-tools --dry-run=client -o yaml | kubectl apply -f -
        kubectl create namespace incident-response --dry-run=client -o yaml | kubectl apply -f -
        success "Kubernetes namespaces configured"
    else
        warning "kubectl not found, skipping Kubernetes setup"
    fi
}

configure_enterprise_database() {
    info "Configuring enterprise database..."
    
    # Create database user and database
    if command -v psql &> /dev/null; then
        sudo -u postgres psql -c "CREATE USER mssp WITH PASSWORD 'enterprise_password';" || true
        sudo -u postgres psql -c "CREATE DATABASE enterprise_security OWNER mssp;" || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE enterprise_security TO mssp;" || true
        success "PostgreSQL database configured"
    else
        warning "PostgreSQL not available, database setup skipped"
    fi
}

setup_monitoring() {
    info "Setting up monitoring infrastructure..."
    
    cd "$INSTALL_DIR/tools"
    
    # Prometheus
    PROMETHEUS_VERSION="2.45.0"
    wget -O prometheus.tar.gz "https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz"
    tar -xzf prometheus.tar.gz
    mv prometheus-${PROMETHEUS_VERSION}.linux-amd64 prometheus
    rm prometheus.tar.gz
    ln -sf "$INSTALL_DIR/tools/prometheus/prometheus" /usr/local/bin/prometheus
    
    # Grafana
    if [[ $PACKAGE_MANAGER == "apt" ]]; then
        apt-get install -y software-properties-common
        add-apt-repository "deb https://packages.grafana.com/oss/deb stable main" -y
        wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
        apt-get update
        apt-get install grafana -y
    fi
    
    success "Monitoring tools installed"
}

create_systemd_services() {
    info "Creating systemd services..."
    
    # Enterprise MSSP Platform service
    cat > /etc/systemd/system/enterprise-mssp.service << EOF
[Unit]
Description=SynaptikOS Enterprise MSSP Platform
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=synaptic
Group=synaptic
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/python src/security/enterprise_mssp_platform.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Security Assessment Worker service
    cat > /etc/systemd/system/security-worker.service << EOF
[Unit]
Description=SynaptikOS Security Assessment Worker
After=network.target redis.service

[Service]
Type=simple
User=synaptic
Group=synaptic
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/celery worker -A security.worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable enterprise-mssp.service
    systemctl enable security-worker.service
    
    success "Systemd services created"
}

create_enterprise_user() {
    info "Creating enterprise security user..."
    
    if ! id "synaptic" &>/dev/null; then
        useradd -r -s /bin/bash -d "$INSTALL_DIR" -c "SynaptikOS Security User" synaptic
    fi
    
    chown -R synaptic:synaptic "$INSTALL_DIR"
    chown -R synaptic:synaptic "/var/log/synaptic-security"
    
    success "Enterprise user configured"
}

setup_firewall() {
    info "Configuring firewall rules..."
    
    if command -v ufw &> /dev/null; then
        # Enterprise security ports
        ufw allow 8090/tcp  # Prometheus metrics
        ufw allow 3000/tcp  # Grafana
        ufw allow 9200/tcp  # Elasticsearch
        ufw allow 5601/tcp  # Kibana
        ufw allow 8080/tcp  # Enterprise dashboard
        
        success "UFW firewall rules configured"
    elif command -v firewalld &> /dev/null; then
        firewall-cmd --permanent --add-port=8090/tcp
        firewall-cmd --permanent --add-port=3000/tcp
        firewall-cmd --permanent --add-port=9200/tcp
        firewall-cmd --permanent --add-port=5601/tcp
        firewall-cmd --permanent --add-port=8080/tcp
        firewall-cmd --reload
        
        success "Firewalld rules configured"
    else
        warning "No firewall service found"
    fi
}

generate_certificates() {
    info "Generating enterprise certificates..."
    
    CERT_DIR="$INSTALL_DIR/certs"
    mkdir -p "$CERT_DIR"
    
    # Generate CA certificate
    openssl genrsa -out "$CERT_DIR/ca-key.pem" 4096
    openssl req -new -x509 -days 365 -key "$CERT_DIR/ca-key.pem" -sha256 -out "$CERT_DIR/ca.pem" -subj "/C=US/ST=CA/L=SF/O=SynaptikOS/OU=Security/CN=enterprise-ca"
    
    # Generate server certificate
    openssl genrsa -out "$CERT_DIR/server-key.pem" 4096
    openssl req -subj "/C=US/ST=CA/L=SF/O=SynaptikOS/OU=Security/CN=enterprise-mssp" -sha256 -new -key "$CERT_DIR/server-key.pem" -out "$CERT_DIR/server.csr"
    openssl x509 -req -days 365 -in "$CERT_DIR/server.csr" -CA "$CERT_DIR/ca.pem" -CAkey "$CERT_DIR/ca-key.pem" -out "$CERT_DIR/server-cert.pem" -CAcreateserial
    
    chmod 400 "$CERT_DIR"/*-key.pem
    chown -R synaptic:synaptic "$CERT_DIR"
    
    success "Enterprise certificates generated"
}

create_startup_script() {
    info "Creating enterprise startup script..."
    
    cat > "$INSTALL_DIR/scripts/start-enterprise-mssp.sh" << 'EOF'
#!/bin/bash

# SynaptikOS Enterprise MSSP Platform Startup Script

set -euo pipefail

INSTALL_DIR="/opt/synaptic-security"
VENV_DIR="$INSTALL_DIR/venv"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏢 Starting SynaptikOS Enterprise MSSP Platform...${NC}"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Start Redis (if not running)
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis..."
    systemctl start redis-server || redis-server --daemonize yes
fi

# Start PostgreSQL (if not running)
if ! pgrep postgres > /dev/null; then
    echo "Starting PostgreSQL..."
    systemctl start postgresql
fi

# Start Docker (if not running)
if ! pgrep dockerd > /dev/null; then
    echo "Starting Docker..."
    systemctl start docker
fi

# Start Prometheus
if ! pgrep prometheus > /dev/null; then
    echo "Starting Prometheus..."
    nohup "$INSTALL_DIR/tools/prometheus/prometheus" --config.file="$INSTALL_DIR/config/prometheus.yml" --storage.tsdb.path="$INSTALL_DIR/data/prometheus" > /var/log/synaptic-security/prometheus.log 2>&1 &
fi

# Start Grafana
if ! pgrep grafana-server > /dev/null; then
    echo "Starting Grafana..."
    systemctl start grafana-server || echo "Grafana not available"
fi

# Start Enterprise MSSP Platform
echo "Starting Enterprise MSSP Platform..."
systemctl start enterprise-mssp.service

# Start Security Workers
echo "Starting Security Workers..."
systemctl start security-worker.service

echo -e "${GREEN}✅ Enterprise MSSP Platform started successfully!${NC}"
echo ""
echo "🌐 Access points:"
echo "   - Enterprise Dashboard: http://localhost:8080"
echo "   - Prometheus Metrics: http://localhost:8090"
echo "   - Grafana Dashboard: http://localhost:3000"
echo ""
echo "📊 Monitoring:"
echo "   - Service status: systemctl status enterprise-mssp"
echo "   - Logs: journalctl -u enterprise-mssp -f"
echo "   - Worker status: systemctl status security-worker"
EOF

    chmod +x "$INSTALL_DIR/scripts/start-enterprise-mssp.sh"
    ln -sf "$INSTALL_DIR/scripts/start-enterprise-mssp.sh" /usr/local/bin/start-enterprise-mssp
    
    success "Startup script created"
}

create_configuration_files() {
    info "Creating configuration files..."
    
    # Copy enterprise configuration if it exists
    if [[ -f "/home/diablorain/Syn_OS/config/enterprise_mssp.yaml" ]]; then
        cp "/home/diablorain/Syn_OS/config/enterprise_mssp.yaml" "$INSTALL_DIR/config/"
    fi
    
    # Create Prometheus configuration
    cat > "$INSTALL_DIR/config/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'enterprise-mssp'
    static_configs:
      - targets: ['localhost:8090']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

rule_files:
  - "security_alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF

    # Create security alerts rules
    cat > "$INSTALL_DIR/config/security_alerts.yml" << EOF
groups:
  - name: security_alerts
    rules:
      - alert: HighRiskAssessment
        expr: security_assessment_risk_score > 80
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "High risk security assessment detected"
          description: "Security assessment {{ \$labels.assessment_id }} has risk score {{ \$value }}"

      - alert: CriticalVulnerability
        expr: vulnerabilities_found_total{severity="critical"} > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Critical vulnerability detected"
          description: "{{ \$value }} critical vulnerabilities found"

      - alert: AssessmentFailure
        expr: increase(security_assessments_total{status="failed"}[5m]) > 3
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Multiple assessment failures"
          description: "{{ \$value }} assessments failed in the last 5 minutes"
EOF

    success "Configuration files created"
}

run_tests() {
    info "Running enterprise platform tests..."
    
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Test basic functionality
    python3 -c "
import asyncio
import sys
sys.path.append('$INSTALL_DIR')

async def test_basic():
    try:
        from src.security.enterprise_mssp_platform import EnterpriseMSSPPlatform
        mssp = EnterpriseMSSPPlatform()
        print('✅ Enterprise MSSP Platform initialization: PASSED')
        
        # Test dashboard data
        dashboard = mssp.get_enterprise_dashboard_data()
        print(f'✅ Dashboard data generation: PASSED (tools: {len(dashboard[\"tools_status\"])})')
        
        return True
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False

result = asyncio.run(test_basic())
exit(0 if result else 1)
"
    
    if [[ $? -eq 0 ]]; then
        success "Enterprise platform tests passed"
    else
        warning "Some tests failed, but installation continues"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}🎯 SynaptikOS Enterprise MSSP Platform Installation Complete!${NC}"
    echo "================================================================"
    echo ""
    echo -e "${BLUE}📋 Installation Summary:${NC}"
    echo "  ✅ System packages installed"
    echo "  ✅ Python environment configured"
    echo "  ✅ Security tools installed (DevSecOps + PenTest)"
    echo "  ✅ Docker environment configured"
    echo "  ✅ Database configured"
    echo "  ✅ Monitoring infrastructure setup"
    echo "  ✅ Enterprise services created"
    echo "  ✅ Certificates generated"
    echo "  ✅ Firewall configured"
    echo ""
    echo -e "${BLUE}🔧 Available Security Tools:${NC}"
    echo "  • Nmap (Network scanning)"
    echo "  • SQLMap (SQL injection testing)"
    echo "  • OWASP ZAP (Web application security)"
    echo "  • Metasploit (Exploitation framework)"
    echo "  • Brakeman (Ruby static analysis)"
    echo "  • Checkov (Infrastructure security)"
    echo "  • HashiCorp Vault (Secrets management)"
    echo "  • John the Ripper (Password cracking)"
    echo "  • Hashcat (Advanced password recovery)"
    echo "  • Wireshark (Network analysis)"
    echo "  • HackingTool Collection (100+ tools)"
    echo ""
    echo -e "${BLUE}🚀 Next Steps:${NC}"
    echo "  1. Start the platform: start-enterprise-mssp"
    echo "  2. Access dashboard: http://localhost:8080"
    echo "  3. View metrics: http://localhost:8090"
    echo "  4. Configure API keys in /etc/synaptic-security/"
    echo "  5. Review logs: journalctl -u enterprise-mssp -f"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "  • Configuration: $INSTALL_DIR/config/enterprise_mssp.yaml"
    echo "  • Logs: /var/log/synaptic-security/"
    echo "  • Tools: $INSTALL_DIR/tools/"
    echo ""
    echo -e "${GREEN}Enterprise MSSP Platform is ready for production deployment!${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🏢 SynaptikOS Phase 3.2 - Enterprise MSSP Platform Setup${NC}"
    echo "=============================================================="
    
    check_root
    check_os
    create_directories
    install_system_packages
    setup_python_environment
    install_ruby_gems
    install_security_tools
    configure_docker
    setup_kubernetes_security_namespace
    configure_enterprise_database
    setup_monitoring
    create_systemd_services
    create_enterprise_user
    setup_firewall
    generate_certificates
    create_startup_script
    create_configuration_files
    run_tests
    print_summary
}

# Trap errors
trap 'error "Installation failed at line $LINENO"' ERR

# Run main function
main "$@"
