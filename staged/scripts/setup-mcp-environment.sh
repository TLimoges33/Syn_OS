#!/bin/bash

# Syn OS MCP Environment Setup Script
# Secure API key configuration with validation

echo -e "\033[32m🔐 SYN OS MCP ENVIRONMENT SETUP\033[0m"
echo -e "\033[33m⚠️  SECURITY CRITICAL: API Key Configuration\033[0m"
echo ""

ENV_FILE="$HOME/.env.mcp"
BACKUP_FILE="$HOME/.env.mcp.backup-$(date +%Y%m%d-%H%M%S)"

# Create backup if exists
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo -e "\033[33m📁 Backed up existing environment to: $BACKUP_FILE\033[0m"
fi

echo -e "\033[36mConfiguring API Keys for Syn OS MCP Integration:\033[0m"
echo ""

# Function to securely prompt for API keys
secure_prompt() {
    local var_name=$1
    local description=$2
    local is_secret=${3:-true}
    
    echo -e "\033[32m$description\033[0m"
    if [ "$is_secret" = true ]; then
        read -s -p "Enter $var_name (hidden): " value
        echo ""
    else
        read -p "Enter $var_name: " value
    fi
    
    # Update or add to env file
    if grep -q "^$var_name=" "$ENV_FILE" 2>/dev/null; then
        sed -i "s|^$var_name=.*|$var_name=$value|" "$ENV_FILE"
    else
        echo "$var_name=$value" >> "$ENV_FILE"
    fi
    
    echo -e "\033[32m✅ $var_name configured\033[0m"
    echo ""
}

# GitHub Token (Critical for repository access)
echo -e "\033[31m🔴 CRITICAL: GitHub Personal Access Token\033[0m"
echo "Required for: Repository access, issue management, code analysis"
echo "Generate at: https://github.com/settings/personal-access-tokens"
secure_prompt "GITHUB_PERSONAL_ACCESS_TOKEN" "GitHub PAT with repo permissions"

# AWS Credentials (for knowledge base)
echo -e "\033[33m🟡 MEDIUM: AWS Credentials\033[0m"
echo "Required for: AWS Knowledge Base access, documentation"
secure_prompt "AWS_REGION" "AWS Region (e.g., us-east-1)" false
secure_prompt "AWS_ACCESS_KEY_ID" "AWS Access Key ID" false
secure_prompt "AWS_SECRET_ACCESS_KEY" "AWS Secret Access Key"

# Search APIs
echo -e "\033[32m🟢 LOW: Search API Keys\033[0m"
echo "Required for: Enhanced search capabilities"
secure_prompt "BRAVE_API_KEY" "Brave Search API Key (optional)" false
secure_prompt "EXA_API_KEY" "Exa Search API Key (optional)" false

# Collaboration Tools
echo -e "\033[33m🟡 MEDIUM: Collaboration APIs\033[0m"
echo "Required for: Team communication, knowledge management"
secure_prompt "SLACK_BOT_TOKEN" "Slack Bot Token (optional)"
secure_prompt "NOTION_API_KEY" "Notion Integration Token (optional)"

# Google Services
echo -e "\033[33m🟡 MEDIUM: Google Services\033[0m"
echo "Required for: Drive access, Maps integration"
secure_prompt "GOOGLE_MAPS_API_KEY" "Google Maps API Key (optional)"

# New Development Services - Syn OS Specific
echo -e "\033[32m🟢 DEVELOPMENT: Syn OS Development APIs\033[0m"
echo "Required for: Database, containers, NATS messaging, Rust development"
secure_prompt "DATABASE_URL" "PostgreSQL Database URL (e.g., postgresql://user:pass@localhost:5432/synos_dev)" false
secure_prompt "DOCKER_HOST" "Docker Host (e.g., unix:///var/run/docker.sock)" false
secure_prompt "NATS_URL" "NATS Server URL (e.g., nats://localhost:4222)" false
secure_prompt "CARGO_HOME" "Cargo Home Path (e.g., /usr/local/cargo)" false
secure_prompt "TRIVY_DB_PATH" "Trivy Database Path (e.g., /tmp/trivy)" false
secure_prompt "PROMETHEUS_URL" "Prometheus URL (e.g., http://localhost:9090)" false

# High-Risk Services (Optional but with warnings)
echo -e "\033[31m🔴 HIGH RISK: Financial & Infrastructure APIs\033[0m"
echo -e "\033[33m⚠️  WARNING: Only configure if absolutely necessary\033[0m"
read -p "Configure Stripe API? (y/N): " configure_stripe
if [[ $configure_stripe =~ ^[Yy]$ ]]; then
    secure_prompt "STRIPE_SECRET_KEY" "Stripe Secret Key (TEST KEY ONLY)"
fi

read -p "Configure Kubernetes access? (y/N): " configure_k8s
if [[ $configure_k8s =~ ^[Yy]$ ]]; then
    secure_prompt "KUBECONFIG" "Kubernetes Config Path" false
fi

# Set secure permissions on env file
chmod 600 "$ENV_FILE"
echo -e "\033[32m🔒 Set secure permissions (600) on environment file\033[0m"

# Add to shell profile
SHELL_PROFILE=""
if [ -f ~/.bashrc ]; then
    SHELL_PROFILE=~/.bashrc
elif [ -f ~/.zshrc ]; then
    SHELL_PROFILE=~/.zshrc
fi

if [ ! -z "$SHELL_PROFILE" ]; then
    if ! grep -q "env.mcp" "$SHELL_PROFILE"; then
        echo "" >> "$SHELL_PROFILE"
        echo "# Syn OS MCP Environment Variables" >> "$SHELL_PROFILE"
        echo 'if [ -f ~/.env.mcp ]; then' >> "$SHELL_PROFILE"
        echo '    export $(cat ~/.env.mcp | grep -v "^#" | xargs)' >> "$SHELL_PROFILE"
        echo 'fi' >> "$SHELL_PROFILE"
        echo -e "\033[32m📝 Added MCP environment loading to $SHELL_PROFILE\033[0m"
    fi
fi

echo ""
echo -e "\033[32m✅ MCP Environment Configuration Complete!\033[0m"
echo ""
echo -e "\033[33m🔄 Next Steps:\033[0m"
echo -e "   1. Restart your terminal (or run: source $SHELL_PROFILE)"
echo -e "   2. Restart Claude Desktop"
echo -e "   3. Look for MCP indicator in Claude Desktop"
echo -e "   4. Test MCP tools with simple commands"
echo ""
echo -e "\033[31m🛡️  Security Reminders:\033[0m"
echo -e "   • Never commit .env.mcp to version control"
echo -e "   • Regularly rotate API keys"
echo -e "   • Monitor API usage for anomalies"
echo -e "   • Use test/sandbox keys when possible"
echo ""

# Make script executable
chmod +x "$0"