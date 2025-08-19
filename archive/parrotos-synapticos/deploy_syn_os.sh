#!/bin/bash
"""
Syn_OS ParrotOS Deployment Script

This script deploys the complete Syn_OS consciousness-aware infrastructure
on ParrotOS, including all services, dependencies, and security configurations.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SYN_OS_HOME="/opt/syn_os"
SYN_OS_USER="syn_os"
SYN_OS_GROUP="syn_os"
DOCKER_COMPOSE_VERSION="2.21.0"
GO_VERSION="1.21.5"
NODE_VERSION="18.18.0"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Check ParrotOS version
check_parrot_os() {
    if ! grep -q "Parrot" /etc/os-release; then
        error "This script is designed for ParrotOS. Current OS not supported."
    fi
    
    local version=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2)
    log "Detected ParrotOS version: $version"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    apt update && apt upgrade -y
    
    # Install essential packages
    apt install -y \
        curl \
        wget \
        git \
        build-essential \
        python3 \
        python3-pip \
        python3-venv \
        sqlite3 \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        certbot \
        python3-certbot-nginx \
        ufw \
        fail2ban \
        htop \
        jq \
        unzip
}

# Install Docker and Docker Compose
install_docker() {
    log "Installing Docker..."
    
    # Remove old Docker versions
    apt remove -y docker docker-engine docker.io containerd runc || true
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Install Docker Compose
    log "Installing Docker Compose v${DOCKER_COMPOSE_VERSION}..."
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Add syn_os user to docker group
    usermod -aG docker $SYN_OS_USER || true
}

# Install Go
install_go() {
    log "Installing Go v${GO_VERSION}..."
    
    # Remove existing Go installation
    rm -rf /usr/local/go
    
    # Download and install Go
    wget "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz"
    tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
    rm "go${GO_VERSION}.linux-amd64.tar.gz"
    
    # Add Go to PATH
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile
    echo 'export GOPATH=/opt/go' >> /etc/profile
    mkdir -p /opt/go
    chown -R $SYN_OS_USER:$SYN_OS_GROUP /opt/go
}

# Install Node.js
install_nodejs() {
    log "Installing Node.js v${NODE_VERSION}..."
    
    # Install Node.js using NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    
    # Install global packages
    npm install -g pm2 yarn
}

# Install NATS Server
install_nats() {
    log "Installing NATS Server..."
    
    # Download and install NATS Server
    wget https://github.com/nats-io/nats-server/releases/latest/download/nats-server-v2.10.4-linux-amd64.zip
    unzip nats-server-v2.10.4-linux-amd64.zip
    mv nats-server-v2.10.4-linux-amd64/nats-server /usr/local/bin/
    chmod +x /usr/local/bin/nats-server
    rm -rf nats-server-v2.10.4-linux-amd64*
    
    # Create NATS configuration
    mkdir -p /etc/nats
    cat > /etc/nats/nats-server.conf << 'EOF'
# NATS Server Configuration for Syn_OS
port: 4222
http_port: 8222

# JetStream Configuration
jetstream {
    store_dir: "/var/lib/nats"
    max_memory_store: 1GB
    max_file_store: 10GB
}

# Logging
log_file: "/var/log/nats/nats-server.log"
logtime: true
debug: false
trace: false

# Security
authorization {
    users = [
        {user: "syn_os", password: "syn_os_secure_password_2024"}
    ]
}
EOF
    
    # Create NATS directories
    mkdir -p /var/lib/nats /var/log/nats
    chown -R $SYN_OS_USER:$SYN_OS_GROUP /var/lib/nats /var/log/nats
    
    # Create systemd service
    cat > /etc/systemd/system/nats.service << 'EOF'
[Unit]
Description=NATS Server
After=network.target

[Service]
Type=simple
User=syn_os
Group=syn_os
ExecStart=/usr/local/bin/nats-server -c /etc/nats/nats-server.conf
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable nats
}

# Create syn_os user and directories
setup_user_and_directories() {
    log "Setting up syn_os user and directories..."
    
    # Create syn_os user if it doesn't exist
    if ! id "$SYN_OS_USER" &>/dev/null; then
        useradd -r -m -s /bin/bash -d /home/$SYN_OS_USER $SYN_OS_USER
        usermod -aG sudo $SYN_OS_USER
    fi
    
    # Create main directories
    mkdir -p $SYN_OS_HOME/{services,applications,data,logs,config,scripts}
    mkdir -p /var/log/syn_os
    mkdir -p /etc/syn_os
    
    # Set ownership
    chown -R $SYN_OS_USER:$SYN_OS_GROUP $SYN_OS_HOME
    chown -R $SYN_OS_USER:$SYN_OS_GROUP /var/log/syn_os
    chown -R $SYN_OS_USER:$SYN_OS_GROUP /etc/syn_os
}

# Deploy Syn_OS code
deploy_syn_os_code() {
    log "Deploying Syn_OS code..."
    
    # Copy source code to deployment directory
    if [ -d "/tmp/syn_os_source" ]; then
        cp -r /tmp/syn_os_source/* $SYN_OS_HOME/
    else
        # Clone from repository (if available)
        warn "Source code not found in /tmp/syn_os_source"
        warn "Please manually copy the Syn_OS source code to $SYN_OS_HOME"
    fi
    
    # Set permissions
    chown -R $SYN_OS_USER:$SYN_OS_GROUP $SYN_OS_HOME
    chmod +x $SYN_OS_HOME/scripts/*.sh || true
    chmod +x $SYN_OS_HOME/tools/cli/*.py || true
}

# Configure PostgreSQL
configure_postgresql() {
    log "Configuring PostgreSQL..."
    
    # Start PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql << 'EOF'
CREATE DATABASE syn_os;
CREATE USER syn_os_user WITH ENCRYPTED PASSWORD 'syn_os_db_password_2024';
GRANT ALL PRIVILEGES ON DATABASE syn_os TO syn_os_user;
ALTER USER syn_os_user CREATEDB;
\q
EOF
    
    # Configure PostgreSQL for network access
    local pg_version=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    local pg_config_dir="/etc/postgresql/$pg_version/main"
    
    # Update postgresql.conf
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" "$pg_config_dir/postgresql.conf"
    
    # Update pg_hba.conf
    echo "local   syn_os          syn_os_user                     md5" >> "$pg_config_dir/pg_hba.conf"
    echo "host    syn_os          syn_os_user     127.0.0.1/32    md5" >> "$pg_config_dir/pg_hba.conf"
    
    # Restart PostgreSQL
    systemctl restart postgresql
}

# Configure Redis
configure_redis() {
    log "Configuring Redis..."
    
    # Configure Redis
    sed -i 's/^# requirepass foobared/requirepass syn_os_redis_password_2024/' /etc/redis/redis.conf
    sed -i 's/^bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
    
    # Start and enable Redis
    systemctl start redis-server
    systemctl enable redis-server
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Create Nginx configuration for Syn_OS
    cat > /etc/nginx/sites-available/syn_os << 'EOF'
# Syn_OS Nginx Configuration
upstream orchestrator {
    server 127.0.0.1:8080;
}

upstream consciousness {
    server 127.0.0.1:8081;
}

upstream security_tutor {
    server 127.0.0.1:8082;
}

upstream web_dashboard {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Main dashboard
    location / {
        proxy_pass http://web_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Orchestrator API
    location /api/orchestrator/ {
        proxy_pass http://orchestrator/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Consciousness API
    location /api/consciousness/ {
        proxy_pass http://consciousness/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Security Tutor
    location /security-tutor/ {
        proxy_pass http://security_tutor/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /opt/syn_os/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/syn_os /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t
    systemctl start nginx
    systemctl enable nginx
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Reset UFW
    ufw --force reset
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow NATS (internal only)
    ufw allow from 127.0.0.1 to any port 4222
    ufw allow from 127.0.0.1 to any port 8222
    
    # Allow PostgreSQL (internal only)
    ufw allow from 127.0.0.1 to any port 5432
    
    # Allow Redis (internal only)
    ufw allow from 127.0.0.1 to any port 6379
    
    # Enable UFW
    ufw --force enable
}

# Configure fail2ban
configure_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create custom jail for Syn_OS
    cat > /etc/fail2ban/jail.d/syn_os.conf << 'EOF'
[syn_os_orchestrator]
enabled = true
port = 8080
filter = syn_os_orchestrator
logpath = /var/log/syn_os/orchestrator.log
maxretry = 5
bantime = 3600

[syn_os_consciousness]
enabled = true
port = 8081
filter = syn_os_consciousness
logpath = /var/log/syn_os/consciousness.log
maxretry = 5
bantime = 3600

[syn_os_security_tutor]
enabled = true
port = 8082
filter = syn_os_security_tutor
logpath = /var/log/syn_os/security_tutor.log
maxretry = 5
bantime = 3600
EOF
    
    # Create filters
    cat > /etc/fail2ban/filter.d/syn_os_orchestrator.conf << 'EOF'
[Definition]
failregex = ^.*\[ERROR\].*Authentication failed.*<HOST>.*$
            ^.*\[ERROR\].*Unauthorized access.*<HOST>.*$
ignoreregex =
EOF
    
    cat > /etc/fail2ban/filter.d/syn_os_consciousness.conf << 'EOF'
[Definition]
failregex = ^.*\[ERROR\].*Authentication failed.*<HOST>.*$
            ^.*\[ERROR\].*Unauthorized access.*<HOST>.*$
ignoreregex =
EOF
    
    cat > /etc/fail2ban/filter.d/syn_os_security_tutor.conf << 'EOF'
[Definition]
failregex = ^.*\[ERROR\].*Authentication failed.*<HOST>.*$
            ^.*\[ERROR\].*Unauthorized access.*<HOST>.*$
ignoreregex =
EOF
    
    # Start and enable fail2ban
    systemctl start fail2ban
    systemctl enable fail2ban
}

# Create systemd services
create_systemd_services() {
    log "Creating systemd services..."
    
    # Orchestrator service
    cat > /etc/systemd/system/syn_os_orchestrator.service << 'EOF'
[Unit]
Description=Syn_OS Service Orchestrator
After=network.target postgresql.service redis.service nats.service
Requires=postgresql.service redis.service nats.service

[Service]
Type=simple
User=syn_os
Group=syn_os
WorkingDirectory=/opt/syn_os/services/orchestrator
ExecStart=/opt/syn_os/services/orchestrator/bin/orchestrator
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment=ENV=production
Environment=NATS_URL=nats://syn_os:syn_os_secure_password_2024@localhost:4222
Environment=POSTGRES_HOST=localhost
Environment=POSTGRES_PORT=5432
Environment=POSTGRES_DB=syn_os
Environment=POSTGRES_USER=syn_os_user
Environment=POSTGRES_PASSWORD=syn_os_db_password_2024
Environment=REDIS_HOST=localhost
Environment=REDIS_PORT=6379
Environment=REDIS_PASSWORD=syn_os_redis_password_2024
Environment=HTTP_PORT=8080
Environment=LOG_LEVEL=info

[Install]
WantedBy=multi-user.target
EOF
    
    # Consciousness service
    cat > /etc/systemd/system/syn_os_consciousness.service << 'EOF'
[Unit]
Description=Syn_OS Consciousness System
After=network.target nats.service syn_os_orchestrator.service
Requires=nats.service

[Service]
Type=simple
User=syn_os
Group=syn_os
WorkingDirectory=/opt/syn_os/src/consciousness_v2
ExecStart=/usr/bin/python3 -m main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment=NATS_URL=nats://syn_os:syn_os_secure_password_2024@localhost:4222
Environment=ORCHESTRATOR_URL=http://localhost:8080
Environment=LOG_LEVEL=INFO
Environment=CONSCIOUSNESS_MODE=production

[Install]
WantedBy=multi-user.target
EOF
    
    # Security Tutor service
    cat > /etc/systemd/system/syn_os_security_tutor.service << 'EOF'
[Unit]
Description=Syn_OS Security Tutor
After=network.target syn_os_consciousness.service
Requires=syn_os_consciousness.service

[Service]
Type=simple
User=syn_os
Group=syn_os
WorkingDirectory=/opt/syn_os/applications/security_tutor
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment=NATS_URL=nats://syn_os:syn_os_secure_password_2024@localhost:4222
Environment=ORCHESTRATOR_URL=http://localhost:8080
Environment=SECURITY_TUTOR_PORT=8082

[Install]
WantedBy=multi-user.target
EOF
    
    # Web Dashboard service
    cat > /etc/systemd/system/syn_os_dashboard.service << 'EOF'
[Unit]
Description=Syn_OS Web Dashboard
After=network.target syn_os_orchestrator.service syn_os_consciousness.service
Requires=syn_os_orchestrator.service syn_os_consciousness.service

[Service]
Type=simple
User=syn_os
Group=syn_os
WorkingDirectory=/opt/syn_os/applications/web_dashboard
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment=NATS_URL=nats://syn_os:syn_os_secure_password_2024@localhost:4222
Environment=ORCHESTRATOR_URL=http://localhost:8080
Environment=CONSCIOUSNESS_URL=http://localhost:8081
Environment=SECURITY_TUTOR_URL=http://localhost:8082
Environment=DASHBOARD_PORT=3000

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
}

# Install Python dependencies
install_python_dependencies() {
    log "Installing Python dependencies..."
    
    # Create virtual environment
    sudo -u $SYN_OS_USER python3 -m venv $SYN_OS_HOME/venv
    
    # Install dependencies
    sudo -u $SYN_OS_USER $SYN_OS_HOME/venv/bin/pip install --upgrade pip
    
    # Install from requirements files
    if [ -f "$SYN_OS_HOME/requirements.txt" ]; then
        sudo -u $SYN_OS_USER $SYN_OS_HOME/venv/bin/pip install -r $SYN_OS_HOME/requirements.txt
    fi
    
    if [ -f "$SYN_OS_HOME/requirements-nats.txt" ]; then
        sudo -u $SYN_OS_USER $SYN_OS_HOME/venv/bin/pip install -r $SYN_OS_HOME/requirements-nats.txt
    fi
    
    # Install additional dependencies
    sudo -u $SYN_OS_USER $SYN_OS_HOME/venv/bin/pip install \
        aiohttp \
        aiohttp-cors \
        aiosqlite \
        click \
        jinja2 \
        requests \
        tabulate \
        rich \
        nats-py \
        asyncio
}

# Build Go services
build_go_services() {
    log "Building Go services..."
    
    # Set Go environment
    export PATH=$PATH:/usr/local/go/bin
    export GOPATH=/opt/go
    
    # Build orchestrator
    if [ -d "$SYN_OS_HOME/services/orchestrator" ]; then
        cd $SYN_OS_HOME/services/orchestrator
        sudo -u $SYN_OS_USER -E go mod download
        sudo -u $SYN_OS_USER -E go build -o bin/orchestrator ./cmd/orchestrator
        chmod +x bin/orchestrator
    fi
}

# Create configuration files
create_configuration() {
    log "Creating configuration files..."
    
    # Main configuration
    cat > /etc/syn_os/syn_os.conf << 'EOF'
# Syn_OS Main Configuration
[database]
host = localhost
port = 5432
name = syn_os
user = syn_os_user
password = syn_os_db_password_2024

[redis]
host = localhost
port = 6379
password = syn_os_redis_password_2024

[nats]
url = nats://syn_os:syn_os_secure_password_2024@localhost:4222

[services]
orchestrator_port = 8080
consciousness_port = 8081
security_tutor_port = 8082
dashboard_port = 3000

[security]
jwt_secret = syn_os_jwt_secret_key_2024_very_secure
enable_auth = true
session_timeout = 3600

[logging]
level = info
directory = /var/log/syn_os
EOF
    
    # Set permissions
    chown $SYN_OS_USER:$SYN_OS_GROUP /etc/syn_os/syn_os.conf
    chmod 600 /etc/syn_os/syn_os.conf
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat > $SYN_OS_HOME/scripts/start_syn_os.sh << 'EOF'
#!/bin/bash
# Syn_OS Startup Script

echo "Starting Syn_OS services..."

# Start core services
sudo systemctl start nats
sudo systemctl start postgresql
sudo systemctl start redis-server

# Wait for core services
sleep 5

# Start Syn_OS services
sudo systemctl start syn_os_orchestrator
sleep 3
sudo systemctl start syn_os_consciousness
sleep 3
sudo systemctl start syn_os_security_tutor
sleep 3
sudo systemctl start syn_os_dashboard

# Start web server
sudo systemctl start nginx

echo "Syn_OS services started successfully!"
echo "Access the dashboard at: http://localhost"
EOF
    
    chmod +x $SYN_OS_HOME/scripts/start_syn_os.sh
    chown $SYN_OS_USER:$SYN_OS_GROUP $SYN_OS_HOME/scripts/start_syn_os.sh
}

# Create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > $SYN_OS_HOME/scripts/monitor_syn_os.sh << 'EOF'
#!/bin/bash
# Syn_OS Monitoring Script

echo "=== Syn_OS System Status ==="
echo

# Check service status
services=("nats" "postgresql" "redis-server" "syn_os_orchestrator" "syn_os_consciousness" "syn_os_security_tutor" "syn_os_dashboard" "nginx")

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Stopped"
    fi
done

echo
echo "=== Resource Usage ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"

echo
echo "=== Network Ports ==="
netstat -tlnp | grep -E ':(4222|5432|6379|8080|8081|8082|3000|80|443) '

echo
echo "=== Recent Logs ==="
echo "Orchestrator:"
tail -n 3 /var/log/syn_os/orchestrator.log 2>/dev/null || echo "No logs found"
echo
echo "Consciousness:"
tail -n 3 /var/log/syn_os/consciousness.log 2>/dev/null || echo "No logs found"
EOF
    
    chmod +x $SYN_OS_HOME/scripts/monitor_syn_os.sh
    chown $SYN_OS_USER:$SYN_OS_GROUP $SYN_OS_HOME/scripts/monitor_syn_os.sh
}

# Main deployment function
main() {
    log "Starting Syn_OS deployment on ParrotOS..."
    
    check_root
    check_parrot_os
    
    # System setup
    update_system
    install_docker
    install_go
    install_nodejs
    install_nats
    
    # User and directory setup
    setup_user_and_directories
    deploy_syn_os_code
    
    # Database setup
    configure_postgresql
    configure_redis
    
    # Web server setup
    configure_nginx
    
    # Security setup
    configure_firewall
    configure_fail2ban
    
    # Service setup
    create_systemd_services
    install_python_dependencies
    build_go_services
    
    # Configuration
    create_configuration
    create_startup_script
    create_monitoring_script
    
    log "Syn_OS deployment completed successfully!"
    info "Next steps:"
    info "1. Copy your Syn_OS source code to $SYN_OS_HOME"
    info "2. Run: $SYN_OS_HOME/scripts/start_syn_os.sh"
    info "3. Access the dashboard at: http://your-server-ip"
    info "4. Monitor with: $SYN_OS_HOME/scripts/monitor_syn_os.sh"
    
    warn "Remember to:"
    warn "- Change default passwords in /etc/syn_os/syn_os.conf"
    warn "- Configure SSL certificates with certbot"
    warn "- Review firewall rules for your environment"
    warn "- Set up regular backups"
}

# Run main function
main "$@"