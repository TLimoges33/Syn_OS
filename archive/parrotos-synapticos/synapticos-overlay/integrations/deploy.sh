#!/bin/bash
# SynapticsOS Integration Infrastructure Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SynapticsOS Integration Infrastructure${NC}"
echo -e "${BLUE}========================================${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed!${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed!${NC}"
        exit 1
    fi
    
    # Check if running as root for iptables
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}Warning: Not running as root. Network segmentation rules will require sudo.${NC}"
    fi
    
    echo -e "${GREEN}Prerequisites check passed!${NC}"
}

# Create necessary directories
create_directories() {
    echo -e "\n${YELLOW}Creating directory structure...${NC}"
    
    # Data directories
    mkdir -p data/{vault,n8n,knowledge,postgres,prometheus,grafana,loki,audio}
    
    # Log directories
    mkdir -p logs/{api-gateway,services,monitoring}
    
    # Temporary directories
    mkdir -p tmp
    
    # Set permissions
    chmod -R 755 data logs tmp
    
    echo -e "${GREEN}Directories created!${NC}"
}

# Generate secrets
generate_secrets() {
    echo -e "\n${YELLOW}Generating secrets...${NC}"
    
    if [ ! -f docker/.env ]; then
        cp docker/.env.example docker/.env
        
        # Generate random passwords
        VAULT_ROOT_TOKEN=$(openssl rand -hex 32)
        VAULT_TOKEN=$(openssl rand -hex 32)
        KNOWLEDGE_DB_PASSWORD=$(openssl rand -base64 32)
        N8N_PASSWORD=$(openssl rand -base64 32)
        N8N_ENCRYPTION_KEY=$(openssl rand -hex 16)
        GRAFANA_PASSWORD=$(openssl rand -base64 32)
        
        # Update .env file
        sed -i "s/your-vault-root-token-here/$VAULT_ROOT_TOKEN/g" docker/.env
        sed -i "s/your-vault-app-token-here/$VAULT_TOKEN/g" docker/.env
        sed -i "s/secure-password-here/$KNOWLEDGE_DB_PASSWORD/g" docker/.env
        sed -i "s/your-32-char-encryption-key-here/$N8N_ENCRYPTION_KEY/g" docker/.env
        
        echo -e "${GREEN}Secrets generated and saved to docker/.env${NC}"
        echo -e "${YELLOW}Please update the remaining configuration values in docker/.env${NC}"
    else
        echo -e "${YELLOW}docker/.env already exists, skipping secret generation${NC}"
    fi
}

# Initialize Vault
init_vault() {
    echo -e "\n${YELLOW}Initializing Vault...${NC}"
    
    # Start only Vault container
    docker-compose -f docker/docker-compose.yml up -d vault
    
    # Wait for Vault to be ready
    echo -e "Waiting for Vault to start..."
    sleep 10
    
    # Initialize Vault (this would normally be done via API)
    echo -e "${GREEN}Vault container started. Manual initialization required.${NC}"
    echo -e "${YELLOW}Run: docker exec -it synapticos-vault vault operator init${NC}"
}

# Apply network segmentation
apply_network_segmentation() {
    echo -e "\n${YELLOW}Applying network segmentation rules...${NC}"
    
    if [[ $EUID -eq 0 ]]; then
        bash network/iptables-rules.sh
    else
        echo -e "${YELLOW}Skipping network rules (requires root). Run manually with:${NC}"
        echo -e "sudo bash network/iptables-rules.sh"
    fi
}

# Start services
start_services() {
    echo -e "\n${YELLOW}Starting all services...${NC}"
    
    # Start all containers
    docker-compose -f docker/docker-compose.yml up -d
    
    # Wait for services to be ready
    echo -e "Waiting for services to start..."
    sleep 30
    
    # Check service health
    docker-compose -f docker/docker-compose.yml ps
}

# Configure monitoring
configure_monitoring() {
    echo -e "\n${YELLOW}Configuring monitoring dashboards...${NC}"
    
    # This would normally import Grafana dashboards via API
    echo -e "${GREEN}Monitoring stack deployed.${NC}"
    echo -e "Access Grafana at: http://localhost:3000"
    echo -e "Access Prometheus at: http://localhost:9090"
}

# Display status
display_status() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}Deployment Complete!${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo -e "\n${GREEN}Service URLs:${NC}"
    echo -e "API Gateway: https://localhost:8443"
    echo -e "Vault UI: http://localhost:8200"
    echo -e "n8n: http://localhost:5678"
    echo -e "Grafana: http://localhost:3000"
    echo -e "Prometheus: http://localhost:9090"
    echo -e "Loki: http://localhost:3100"
    
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo -e "1. Initialize Vault and unseal it"
    echo -e "2. Configure API keys in Vault"
    echo -e "3. Update service configurations"
    echo -e "4. Import Grafana dashboards"
    echo -e "5. Test service connectivity"
    
    echo -e "\n${YELLOW}Security Notes:${NC}"
    echo -e "- Change all default passwords in docker/.env"
    echo -e "- Enable TLS for all services in production"
    echo -e "- Review and adjust network segmentation rules"
    echo -e "- Configure proper backup strategies"
}

# Main deployment flow
main() {
    check_prerequisites
    create_directories
    generate_secrets
    
    # Ask user if they want to continue
    echo -e "\n${YELLOW}Ready to deploy. Continue? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled.${NC}"
        exit 0
    fi
    
    apply_network_segmentation
    start_services
    configure_monitoring
    display_status
}

# Run main function
main "$@"