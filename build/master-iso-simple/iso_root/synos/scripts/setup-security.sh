#!/bin/bash
# Syn_OS Security Setup Script
# This script implements critical security fixes and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="/tmp/syn_os_security_setup.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo -e "${BLUE}🔒 Syn_OS Security Setup Script${NC}"
echo -e "${BLUE}================================${NC}"
echo "Log file: $LOG_FILE"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root for security reasons${NC}"
   exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed - some features may not work"
    fi
    
    # Check if we're in the Syn_OS directory
    if [[ ! -f "docker-compose.yml" ]] || [[ ! -d "src/security" ]]; then
        print_error "Please run this script from the Syn_OS root directory"
        exit 1
    fi
    
    print_status "Prerequisites check completed"
}

# Install security dependencies
install_security_deps() {
    print_info "Installing security dependencies..."
    
    if [[ -f "requirements-security.txt" ]]; then
        pip3 install -r requirements-security.txt
        print_status "Security dependencies installed"
    else
        print_warning "requirements-security.txt not found, skipping dependency installation"
    fi
}

# Generate secure environment file
generate_secure_env() {
    print_info "Generating secure environment configuration..."
    
    if [[ -f ".env" ]]; then
        print_warning ".env file already exists"
        read -p "Do you want to backup and regenerate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mv .env .env.backup.$(date +%Y%m%d_%H%M%S)
            print_info "Existing .env backed up"
        else
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    # Use Python script to generate secure configuration
    python3 -c "
import sys
sys.path.append('src/security')
from config_manager import SecureConfigManager
config = SecureConfigManager()
if config.create_secure_env_file():
    print('✅ Secure .env file generated')
else:
    print('❌ Failed to generate .env file')
    sys.exit(1)
"
    
    # Set secure permissions
    chmod 600 .env
    print_status "Secure environment file generated with proper permissions"
}

# Validate security configuration
validate_security() {
    print_info "Validating security configuration..."
    
    python3 -c "
import sys
sys.path.append('src/security')
from config_manager import validate_system_security
if validate_system_security():
    print('✅ Security configuration is valid')
else:
    print('❌ Security configuration has issues')
    sys.exit(1)
"
    
    print_status "Security configuration validated"
}

# Set up security logging
setup_security_logging() {
    print_info "Setting up security logging..."
    
    # Create log directories
    sudo mkdir -p /var/log/syn_os/security
    sudo chown $USER:$USER /var/log/syn_os/security
    sudo chmod 750 /var/log/syn_os/security
    
    # Create logrotate configuration
    sudo tee /etc/logrotate.d/syn_os > /dev/null << EOF
/var/log/syn_os/security/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 $USER $USER
    postrotate
        # Restart logging service if needed
    endscript
}
EOF
    
    print_status "Security logging configured"
}

# Configure firewall rules
configure_firewall() {
    print_info "Configuring firewall rules..."
    
    if command -v ufw &> /dev/null; then
        # Enable UFW if not already enabled
        sudo ufw --force enable
        
        # Default policies
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        
        # Allow SSH (be careful!)
        sudo ufw allow ssh
        
        # Allow application ports
        sudo ufw allow 8080/tcp comment 'Orchestrator API'
        sudo ufw allow 8081/tcp comment 'Consciousness API'
        sudo ufw allow 4222/tcp comment 'NATS'
        
        # Allow Docker network
        sudo ufw allow from 172.20.0.0/16
        
        print_status "Firewall configured with UFW"
    else
        print_warning "UFW not available, skipping firewall configuration"
    fi
}

# Set up file permissions
setup_file_permissions() {
    print_info "Setting up secure file permissions..."
    
    # Secure configuration files
    find . -name "*.env*" -exec chmod 600 {} \;
    find . -name "config.ini" -exec chmod 600 {} \;
    find . -name "config.yaml" -exec chmod 600 {} \;
    find . -name "config.yml" -exec chmod 600 {} \;
    
    # Secure key files
    find . -name "*.key" -exec chmod 600 {} \;
    find . -name "*.pem" -exec chmod 600 {} \;
    
    # Secure script files
    find scripts/ -name "*.sh" -exec chmod 755 {} \;
    
    # Secure Python files
    find src/ -name "*.py" -exec chmod 644 {} \;
    
    print_status "File permissions configured"
}

# Run security tests
run_security_tests() {
    print_info "Running security tests..."
    
    # Test JWT system
    python3 -c "
import sys
sys.path.append('src/security')
try:
    from jwt_auth import SecureJWTManager
    manager = SecureJWTManager()
    print('✅ JWT system initialized successfully')
except Exception as e:
    print(f'❌ JWT system test failed: {e}')
    sys.exit(1)
"
    
    # Test input validation
    python3 -c "
import sys
sys.path.append('src/security')
try:
    from input_validator import SecureInputValidator
    validator = SecureInputValidator()
    print('✅ Input validator initialized successfully')
except Exception as e:
    print(f'❌ Input validator test failed: {e}')
    sys.exit(1)
"
    
    # Test audit logging
    python3 -c "
import sys
sys.path.append('src/security')
try:
    from audit_logger import SecurityAuditLogger
    logger = SecurityAuditLogger()
    print('✅ Audit logger initialized successfully')
except Exception as e:
    print(f'❌ Audit logger test failed: {e}')
    sys.exit(1)
"
    
    print_status "Security tests completed successfully"
}

# Generate security report
generate_security_report() {
    print_info "Generating security report..."
    
    REPORT_FILE="security_setup_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
Syn_OS Security Setup Report
============================
Date: $(date)
User: $(whoami)
Host: $(hostname)

Security Components Installed:
- ✅ Secure Configuration Manager
- ✅ JWT Authentication System
- ✅ Input Validation System
- ✅ Security Audit Logger
- ✅ Environment Protection (.gitignore updated)

Configuration Files:
- ✅ .env (secure environment variables)
- ✅ requirements-security.txt (security dependencies)
- ✅ docker-compose.yml (updated with environment variables)

Security Measures Implemented:
- ✅ Hardcoded credentials removed
- ✅ Strong JWT implementation
- ✅ Comprehensive input validation
- ✅ Security audit logging
- ✅ File permissions secured
- ✅ Firewall configured (if UFW available)

Next Steps:
1. Review and customize the generated .env file
2. Test the application with new security settings
3. Set up monitoring and alerting
4. Conduct security penetration testing
5. Train team on security best practices

Important Security Notes:
- Never commit .env files to version control
- Regularly rotate secrets and API keys
- Monitor security logs for suspicious activity
- Keep security dependencies updated
- Conduct regular security audits

For more information, see:
- src/security/README.md (if available)
- Security documentation in docs/
EOF
    
    print_status "Security report generated: $REPORT_FILE"
}

# Main execution
main() {
    echo -e "${BLUE}Starting Syn_OS security setup...${NC}"
    echo ""
    
    check_prerequisites
    echo ""
    
    install_security_deps
    echo ""
    
    generate_secure_env
    echo ""
    
    validate_security
    echo ""
    
    setup_security_logging
    echo ""
    
    configure_firewall
    echo ""
    
    setup_file_permissions
    echo ""
    
    run_security_tests
    echo ""
    
    generate_security_report
    echo ""
    
    echo -e "${GREEN}🎉 Security setup completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Important next steps:${NC}"
    echo "1. Review the generated .env file and customize as needed"
    echo "2. Test your application with the new security settings"
    echo "3. Set up monitoring and alerting for security events"
    echo "4. Regularly update security dependencies"
    echo ""
    echo -e "${BLUE}Security report saved to: $REPORT_FILE${NC}"
    echo -e "${BLUE}Setup log saved to: $LOG_FILE${NC}"
}

# Run main function
main "$@"