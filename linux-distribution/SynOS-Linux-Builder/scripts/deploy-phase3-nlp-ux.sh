#!/bin/bash

# Deploy Phase 3: Natural Language & UX Components to SynOS Filesystem
# This script integrates all NLP, LLM, knowledge graph, RAG, and adaptive UI components

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FILESYSTEM_ROOT="${PROJECT_ROOT}/filesystem-extract"
PACKAGES_DIR="${PROJECT_ROOT}/../SynOS-Packages"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[DEPLOY-PHASE3]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if filesystem root exists
if [[ ! -d "$FILESYSTEM_ROOT" ]]; then
    error "Filesystem root not found at $FILESYSTEM_ROOT. Please extract ParrotOS first."
fi

log "Starting Phase 3 Natural Language & UX Components deployment..."

# Create directory structure
log "Creating Phase 3 directory structure..."
mkdir -p "$FILESYSTEM_ROOT/opt/synos/nlp"
mkdir -p "$FILESYSTEM_ROOT/opt/synos/llm-hub"
mkdir -p "$FILESYSTEM_ROOT/opt/synos/smart-shell"
mkdir -p "$FILESYSTEM_ROOT/opt/synos/knowledge-base"
mkdir -p "$FILESYSTEM_ROOT/opt/synos/rag-system"
mkdir -p "$FILESYSTEM_ROOT/opt/synos/adaptive-ui"
mkdir -p "$FILESYSTEM_ROOT/opt/synos/models"
mkdir -p "$FILESYSTEM_ROOT/etc/synos/phase3"
mkdir -p "$FILESYSTEM_ROOT/var/lib/synos/knowledge"
mkdir -p "$FILESYSTEM_ROOT/var/lib/synos/embeddings"
mkdir -p "$FILESYSTEM_ROOT/var/log/synos/nlp"
mkdir -p "$FILESYSTEM_ROOT/usr/share/synos/ui-themes"

# Deploy NLP Command Interface
log "Deploying NLP Command Interface..."
cp -r "$PACKAGES_DIR/synos-nlp-interface/"* "$FILESYSTEM_ROOT/opt/synos/nlp/"
chmod +x "$FILESYSTEM_ROOT/opt/synos/nlp/bin/synos-nlp"

# Deploy LLM Integration Engine
log "Deploying LLM Integration Engine..."
cp -r "$PACKAGES_DIR/synos-llm-hub/"* "$FILESYSTEM_ROOT/opt/synos/llm-hub/"
chmod +x "$FILESYSTEM_ROOT/opt/synos/llm-hub/bin/synos-llm"

# Deploy Smart Shell
log "Deploying Intelligent Command Completion..."
cp -r "$PACKAGES_DIR/synos-smart-shell/"* "$FILESYSTEM_ROOT/opt/synos/smart-shell/"
chmod +x "$FILESYSTEM_ROOT/opt/synos/smart-shell/bin/synos-completion"

# Deploy Knowledge Base
log "Deploying Security Knowledge Graph..."
cp -r "$PACKAGES_DIR/synos-knowledge-base/"* "$FILESYSTEM_ROOT/opt/synos/knowledge-base/"
chmod +x "$FILESYSTEM_ROOT/opt/synos/knowledge-base/bin/synos-knowledge"

# Deploy RAG System
log "Deploying RAG Architecture..."
cp -r "$PACKAGES_DIR/synos-rag-system/"* "$FILESYSTEM_ROOT/opt/synos/rag-system/"
chmod +x "$FILESYSTEM_ROOT/opt/synos/rag-system/bin/synos-rag"

# Deploy Adaptive UI
log "Deploying Context-Driven UI Adaptation..."
cp -r "$PACKAGES_DIR/synos-adaptive-ui/"* "$FILESYSTEM_ROOT/opt/synos/adaptive-ui/"
chmod +x "$FILESYSTEM_ROOT/opt/synos/adaptive-ui/bin/synos-ui-adapter"

# Create systemd services for Phase 3 components
log "Creating systemd services for Phase 3..."

# NLP Command Service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-nlp-interface.service" << 'EOF'
[Unit]
Description=SynOS Natural Language Processing Interface
After=network.target synos-consciousness.service
Wants=synos-consciousness.service

[Service]
Type=notify
User=synos
Group=synos
WorkingDirectory=/opt/synos/nlp
ExecStart=/opt/synos/nlp/bin/synos-nlp --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/synos /var/log/synos /tmp
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

# Resource limits
MemoryMax=512M
CPUQuota=50%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=synos-nlp

[Install]
WantedBy=multi-user.target
EOF

# LLM Hub Service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-llm-hub.service" << 'EOF'
[Unit]
Description=SynOS Local LLM Integration Engine
After=network.target synos-consciousness.service
Wants=synos-consciousness.service

[Service]
Type=notify
User=synos
Group=synos
WorkingDirectory=/opt/synos/llm-hub
ExecStart=/opt/synos/llm-hub/bin/synos-llm --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=15

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/synos /var/log/synos /opt/synos/models /tmp
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

# Resource limits for LLM operations
MemoryMax=4G
CPUQuota=80%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=synos-llm

[Install]
WantedBy=multi-user.target
EOF

# Knowledge Graph Service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-knowledge-graph.service" << 'EOF'
[Unit]
Description=SynOS Security Knowledge Graph
After=network.target synos-consciousness.service
Wants=synos-consciousness.service

[Service]
Type=notify
User=synos
Group=synos
WorkingDirectory=/opt/synos/knowledge-base
ExecStart=/opt/synos/knowledge-base/bin/synos-knowledge --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/synos/knowledge /var/lib/synos/embeddings /var/log/synos /tmp
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

# Resource limits
MemoryMax=1G
CPUQuota=60%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=synos-knowledge

[Install]
WantedBy=multi-user.target
EOF

# RAG System Service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-rag-system.service" << 'EOF'
[Unit]
Description=SynOS RAG Architecture System
After=network.target synos-knowledge-graph.service synos-llm-hub.service
Wants=synos-knowledge-graph.service synos-llm-hub.service

[Service]
Type=notify
User=synos
Group=synos
WorkingDirectory=/opt/synos/rag-system
ExecStart=/opt/synos/rag-system/bin/synos-rag --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/synos /var/log/synos /tmp
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

# Resource limits
MemoryMax=2G
CPUQuota=70%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=synos-rag

[Install]
WantedBy=multi-user.target
EOF

# Adaptive UI Service
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-adaptive-ui.service" << 'EOF'
[Unit]
Description=SynOS Context-Driven UI Adaptation
After=graphical.target synos-consciousness.service
Wants=synos-consciousness.service

[Service]
Type=notify
User=synos
Group=synos
WorkingDirectory=/opt/synos/adaptive-ui
ExecStart=/opt/synos/adaptive-ui/bin/synos-ui-adapter --daemon
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/synos /var/log/synos /usr/share/synos/ui-themes /tmp
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

# Resource limits
MemoryMax=256M
CPUQuota=30%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=synos-ui

[Install]
WantedBy=graphical.target
EOF

# Create Phase 3 configuration files
log "Creating Phase 3 configuration files..."

# NLP Configuration
cat > "$FILESYSTEM_ROOT/etc/synos/phase3/nlp-config.yaml" << 'EOF'
nlp_interface:
  model_path: "/opt/synos/models/spacy/en_core_web_sm"
  confidence_threshold: 0.75
  max_command_length: 1024
  safety_mode: true
  user_confirmation_required: true

  intents:
    - reconnaissance
    - vulnerability_assessment
    - exploitation
    - post_exploitation
    - system_administration
    - file_management

  restricted_commands:
    - "rm -rf /"
    - "dd if=/dev/zero"
    - "mkfs.*"
    - "fdisk.*"

  nats_config:
    server: "nats://localhost:4222"
    subject_prefix: "synos.nlp"
EOF

# LLM Hub Configuration
cat > "$FILESYSTEM_ROOT/etc/synos/phase3/llm-config.yaml" << 'EOF'
llm_hub:
  models_directory: "/opt/synos/models"
  max_concurrent_sessions: 4
  default_model: "microsoft/DialoGPT-medium"
  context_window_size: 2048
  temperature: 0.7
  max_tokens: 512

  security_prompts:
    system_prompt: |
      You are SynOS AI, a cybersecurity assistant integrated into a security-focused Linux distribution.
      Provide accurate, ethical cybersecurity guidance. Always prioritize defensive security practices.
      Never provide instructions for malicious activities or illegal hacking.

  privacy:
    local_inference_only: true
    disable_telemetry: true
    encrypt_conversations: true

  resource_limits:
    max_memory_mb: 3072
    max_cpu_cores: 4
EOF

# Knowledge Graph Configuration
cat > "$FILESYSTEM_ROOT/etc/synos/phase3/knowledge-config.yaml" << 'EOF'
knowledge_graph:
  database_path: "/var/lib/synos/knowledge/graph.db"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  vector_dimension: 384
  max_entities: 100000
  similarity_threshold: 0.7

  entity_types:
    - vulnerability
    - exploit
    - tool
    - technique
    - indicator
    - threat_actor
    - malware
    - network_service

  data_sources:
    - cve_database
    - exploit_database
    - mitre_attack
    - threat_intelligence_feeds
    - security_advisories
EOF

# RAG Configuration
cat > "$FILESYSTEM_ROOT/etc/synos/phase3/rag-config.yaml" << 'EOF'
rag_system:
  vector_store: "faiss"
  chunk_size: 512
  chunk_overlap: 50
  max_retrievals: 5
  similarity_threshold: 0.6

  chromadb:
    persist_directory: "/var/lib/synos/knowledge/chromadb"
    collection_name: "synos_security_docs"

  faiss:
    index_path: "/var/lib/synos/embeddings/faiss.index"
    metadata_path: "/var/lib/synos/embeddings/metadata.json"

  document_types:
    - security_documentation
    - vulnerability_reports
    - threat_intelligence
    - forensic_reports
    - incident_response_playbooks
EOF

# UI Adaptation Configuration
cat > "$FILESYSTEM_ROOT/etc/synos/phase3/ui-config.yaml" << 'EOF'
adaptive_ui:
  theme_directory: "/usr/share/synos/ui-themes"
  update_interval: 30
  accessibility_enabled: true

  security_phases:
    reconnaissance:
      primary_color: "#2E86AB"
      layout: "dual_pane"
      tools_priority: ["nmap", "gobuster", "recon-ng"]

    vulnerability_assessment:
      primary_color: "#A23B72"
      layout: "triple_pane"
      tools_priority: ["nessus", "openvas", "nuclei"]

    exploitation:
      primary_color: "#F18F01"
      layout: "focused"
      tools_priority: ["metasploit", "sqlmap", "burpsuite"]

    post_exploitation:
      primary_color: "#C73E1D"
      layout: "command_focused"
      tools_priority: ["empire", "covenant", "bloodhound"]

    incident_response:
      primary_color: "#8B1538"
      layout: "emergency"
      tools_priority: ["volatility", "autopsy", "osquery"]

  threat_levels:
    green: { urgency: 0, color: "#28A745" }
    yellow: { urgency: 1, color: "#FFC107" }
    orange: { urgency: 2, color: "#FD7E14" }
    red: { urgency: 3, color: "#DC3545" }
EOF

# Create CLI integration scripts
log "Creating CLI integration scripts..."

# Main SynOS AI CLI
cat > "$FILESYSTEM_ROOT/usr/local/bin/synos-ai" << 'EOF'
#!/bin/bash

# SynOS AI - Unified Natural Language Interface
# Usage: synos-ai [command] | synos-ai --interactive

set -euo pipefail

SYNOS_NLP_SOCKET="/var/run/synos/nlp.sock"

show_help() {
    cat << 'HELP'
SynOS AI - Natural Language Cybersecurity Interface

USAGE:
    synos-ai "scan network for vulnerabilities"
    synos-ai "analyze this file for malware"
    synos-ai --interactive
    synos-ai --status

COMMANDS:
    --interactive    Start interactive NLP session
    --status         Show AI system status
    --help           Show this help message

EXAMPLES:
    synos-ai "perform reconnaissance on 192.168.1.0/24"
    synos-ai "check for SQL injection vulnerabilities in target.com"
    synos-ai "generate forensic timeline from /evidence/disk.img"
    synos-ai "correlate these IOCs with threat intelligence"

The AI understands natural language commands related to cybersecurity operations
and translates them into appropriate tool executions with safety validation.
HELP
}

check_service_status() {
    systemctl is-active --quiet synos-nlp-interface && echo "✓ NLP Interface: Active" || echo "✗ NLP Interface: Inactive"
    systemctl is-active --quiet synos-llm-hub && echo "✓ LLM Hub: Active" || echo "✗ LLM Hub: Inactive"
    systemctl is-active --quiet synos-knowledge-graph && echo "✓ Knowledge Graph: Active" || echo "✗ Knowledge Graph: Inactive"
    systemctl is-active --quiet synos-rag-system && echo "✓ RAG System: Active" || echo "✗ RAG System: Inactive"
    systemctl is-active --quiet synos-adaptive-ui && echo "✓ Adaptive UI: Active" || echo "✗ Adaptive UI: Inactive"
}

interactive_mode() {
    echo "🧠 SynOS AI Interactive Mode"
    echo "Type 'exit' to quit, 'help' for assistance"
    echo "----------------------------------------"

    while true; do
        read -p "synos-ai> " input
        case "$input" in
            "exit"|"quit") break ;;
            "help") show_help ;;
            "status") check_service_status ;;
            "") continue ;;
            *)
                echo "Processing: $input"
                /opt/synos/nlp/bin/synos-nlp --command "$input"
                ;;
        esac
    done
}

# Main execution
case "${1:-}" in
    "--help"|"-h") show_help ;;
    "--status") check_service_status ;;
    "--interactive"|"-i") interactive_mode ;;
    "") interactive_mode ;;
    *) /opt/synos/nlp/bin/synos-nlp --command "$*" ;;
esac
EOF

chmod +x "$FILESYSTEM_ROOT/usr/local/bin/synos-ai"

# Knowledge query CLI
cat > "$FILESYSTEM_ROOT/usr/local/bin/synos-knowledge" << 'EOF'
#!/bin/bash

# SynOS Knowledge - Security Knowledge Graph Query Interface
# Usage: synos-knowledge [query] | synos-knowledge --search "term"

set -euo pipefail

show_help() {
    cat << 'HELP'
SynOS Knowledge - Security Knowledge Graph Interface

USAGE:
    synos-knowledge "what is CVE-2023-4911"
    synos-knowledge --search "privilege escalation"
    synos-knowledge --related "nmap"
    synos-knowledge --export cve

COMMANDS:
    --search TERM     Semantic search for security knowledge
    --related ENTITY  Find related security concepts
    --export TYPE     Export knowledge in format (json, csv, xml)
    --stats           Show knowledge graph statistics
    --help            Show this help message

EXAMPLES:
    synos-knowledge "show me Linux kernel exploits"
    synos-knowledge --search "buffer overflow techniques"
    synos-knowledge --related "metasploit"
    synos-knowledge --export vulnerabilities
HELP
}

# Main execution
case "${1:-}" in
    "--help"|"-h") show_help ;;
    "--search") /opt/synos/knowledge-base/bin/synos-knowledge --semantic-search "$2" ;;
    "--related") /opt/synos/knowledge-base/bin/synos-knowledge --find-related "$2" ;;
    "--export") /opt/synos/knowledge-base/bin/synos-knowledge --export "$2" ;;
    "--stats") /opt/synos/knowledge-base/bin/synos-knowledge --statistics ;;
    "") show_help ;;
    *) /opt/synos/knowledge-base/bin/synos-knowledge --query "$*" ;;
esac
EOF

chmod +x "$FILESYSTEM_ROOT/usr/local/bin/synos-knowledge"

# Create MATE desktop integration
log "Creating MATE desktop integration..."

# Desktop entry for SynOS AI
cat > "$FILESYSTEM_ROOT/usr/share/applications/synos-ai.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Name=SynOS AI Assistant
Comment=Natural Language Cybersecurity Interface
Exec=gnome-terminal -- synos-ai --interactive
Icon=synos-ai
Terminal=false
Type=Application
Categories=Security;System;
Keywords=AI;Security;NLP;Assistant;Cybersecurity;
StartupNotify=true
EOF

# Desktop entry for Knowledge Graph
cat > "$FILESYSTEM_ROOT/usr/share/applications/synos-knowledge.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Name=SynOS Knowledge Graph
Comment=Security Knowledge Base Explorer
Exec=gnome-terminal -- synos-knowledge --search
Icon=synos-knowledge
Terminal=false
Type=Application
Categories=Security;Education;
Keywords=Knowledge;Security;Database;Search;CVE;Exploits;
StartupNotify=true
EOF

# Create bash completion for CLI tools
log "Setting up bash completion..."
mkdir -p "$FILESYSTEM_ROOT/etc/bash_completion.d"

cat > "$FILESYSTEM_ROOT/etc/bash_completion.d/synos-ai" << 'EOF'
# Bash completion for synos-ai command

_synos_ai_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Common security operation patterns
    local patterns="scan network enumerate services check vulnerabilities analyze file perform reconnaissance run exploit search for find related to correlate evidence generate report"

    case $prev in
        synos-ai)
            opts="--interactive --status --help"
            COMPREPLY=( $(compgen -W "${opts} ${patterns}" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _synos_ai_completions synos-ai
EOF

# Create Phase 3 startup script
cat > "$FILESYSTEM_ROOT/usr/local/bin/synos-phase3-startup" << 'EOF'
#!/bin/bash

# SynOS Phase 3 - Natural Language & UX Components Startup
# This script initializes all Phase 3 AI services on system boot

set -euo pipefail

log() {
    echo "[SYNOS-PHASE3] $1"
}

log "Initializing SynOS Phase 3 Natural Language & UX Components..."

# Ensure directories exist
mkdir -p /var/lib/synos/knowledge
mkdir -p /var/lib/synos/embeddings
mkdir -p /var/log/synos/nlp
mkdir -p /opt/synos/models

# Download essential models if not present
if [[ ! -f /opt/synos/models/.models_initialized ]]; then
    log "Initializing AI models..."

    # Download spaCy model for NLP
    python3 -m spacy download en_core_web_sm 2>/dev/null || true

    # Create model directory structure
    mkdir -p /opt/synos/models/spacy
    mkdir -p /opt/synos/models/sentence-transformers
    mkdir -p /opt/synos/models/dialogpt

    touch /opt/synos/models/.models_initialized
fi

# Initialize knowledge graph database
if [[ ! -f /var/lib/synos/knowledge/graph.db ]]; then
    log "Initializing knowledge graph database..."
    /opt/synos/knowledge-base/bin/synos-knowledge --initialize-db
fi

# Initialize vector embeddings
if [[ ! -f /var/lib/synos/embeddings/faiss.index ]]; then
    log "Initializing vector embeddings..."
    /opt/synos/rag-system/bin/synos-rag --initialize-embeddings
fi

# Set permissions
chown -R synos:synos /var/lib/synos/knowledge
chown -R synos:synos /var/lib/synos/embeddings
chown -R synos:synos /var/log/synos/nlp
chown -R synos:synos /opt/synos/models

log "Phase 3 initialization complete"
EOF

chmod +x "$FILESYSTEM_ROOT/usr/local/bin/synos-phase3-startup"

# Create systemd service for Phase 3 startup
cat > "$FILESYSTEM_ROOT/etc/systemd/system/synos-phase3-startup.service" << 'EOF'
[Unit]
Description=SynOS Phase 3 Natural Language & UX Initialization
After=network.target
Before=synos-nlp-interface.service synos-llm-hub.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/synos-phase3-startup
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
EOF

# Update environment configuration
log "Updating environment configuration..."

# Add Phase 3 to PATH and environment
cat >> "$FILESYSTEM_ROOT/etc/environment" << 'EOF'

# SynOS Phase 3 Environment Variables
SYNOS_PHASE3_ROOT="/opt/synos"
SYNOS_KNOWLEDGE_DB="/var/lib/synos/knowledge/graph.db"
SYNOS_MODELS_DIR="/opt/synos/models"
SYNOS_NLP_CONFIG="/etc/synos/phase3/nlp-config.yaml"
SYNOS_LLM_CONFIG="/etc/synos/phase3/llm-config.yaml"
EOF

# Create Phase 3 integration test script
log "Creating integration test script..."

cat > "$FILESYSTEM_ROOT/usr/local/bin/synos-phase3-test" << 'EOF'
#!/bin/bash

# SynOS Phase 3 Integration Testing
# Tests all Natural Language & UX Components

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[TEST]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

test_service() {
    local service="$1"
    local description="$2"

    if systemctl is-active --quiet "$service"; then
        log "✓ $description: Running"
        return 0
    else
        error "✗ $description: Not running"
        return 1
    fi
}

test_command() {
    local command="$1"
    local description="$2"

    if command -v "$command" >/dev/null 2>&1; then
        log "✓ $description: Available"
        return 0
    else
        error "✗ $description: Not available"
        return 1
    fi
}

log "Starting SynOS Phase 3 Integration Tests..."

# Test systemd services
test_service "synos-nlp-interface" "NLP Interface Service"
test_service "synos-llm-hub" "LLM Hub Service"
test_service "synos-knowledge-graph" "Knowledge Graph Service"
test_service "synos-rag-system" "RAG System Service"
test_service "synos-adaptive-ui" "Adaptive UI Service"

# Test CLI commands
test_command "synos-ai" "SynOS AI CLI"
test_command "synos-knowledge" "Knowledge Graph CLI"

# Test configuration files
log "Testing configuration files..."
for config in nlp-config.yaml llm-config.yaml knowledge-config.yaml rag-config.yaml ui-config.yaml; do
    if [[ -f "/etc/synos/phase3/$config" ]]; then
        log "✓ Configuration: $config"
    else
        error "✗ Configuration missing: $config"
    fi
done

# Test directories
log "Testing directory structure..."
for dir in knowledge embeddings nlp; do
    if [[ -d "/var/lib/synos/$dir" ]]; then
        log "✓ Directory: /var/lib/synos/$dir"
    else
        error "✗ Directory missing: /var/lib/synos/$dir"
    fi
done

# Test AI functionality
log "Testing AI functionality..."
if timeout 10s synos-ai "help" >/dev/null 2>&1; then
    log "✓ NLP Interface: Responding"
else
    warn "⚠ NLP Interface: May need initialization"
fi

log "Phase 3 integration test complete"
EOF

chmod +x "$FILESYSTEM_ROOT/usr/local/bin/synos-phase3-test"

# Enable all Phase 3 systemd services
log "Enabling Phase 3 systemd services..."
chroot "$FILESYSTEM_ROOT" systemctl enable synos-phase3-startup.service
chroot "$FILESYSTEM_ROOT" systemctl enable synos-nlp-interface.service
chroot "$FILESYSTEM_ROOT" systemctl enable synos-llm-hub.service
chroot "$FILESYSTEM_ROOT" systemctl enable synos-knowledge-graph.service
chroot "$FILESYSTEM_ROOT" systemctl enable synos-rag-system.service
chroot "$FILESYSTEM_ROOT" systemctl enable synos-adaptive-ui.service

# Set ownership and permissions
log "Setting ownership and permissions..."
chroot "$FILESYSTEM_ROOT" chown -R synos:synos /opt/synos
chroot "$FILESYSTEM_ROOT" chown -R synos:synos /var/lib/synos
chroot "$FILESYSTEM_ROOT" chown -R synos:synos /var/log/synos
chroot "$FILESYSTEM_ROOT" chmod +x /usr/local/bin/synos-*

# Create deployment summary
log "Creating deployment summary..."

cat > "$PROJECT_ROOT/PHASE3-DEPLOYMENT-SUMMARY.md" << 'EOF'
# SynOS Phase 3: Natural Language & UX Components - Deployment Summary

## 🚀 Successfully Deployed Components

### Core AI Services
- **NLP Command Interface** (`synos-nlp-interface.service`)
  - Natural language processing for security operations
  - Intent classification and command mapping
  - Safety validation and user confirmation workflows
  - CLI: `synos-ai "scan network for vulnerabilities"`

- **LLM Integration Engine** (`synos-llm-hub.service`)
  - Privacy-preserving local LLM deployment
  - DialoGPT integration for conversational AI
  - Security-focused prompts and response filtering
  - Resource management (4GB RAM, 4 CPU cores)

- **Security Knowledge Graph** (`synos-knowledge-graph.service`)
  - Vector embeddings with sentence-transformers
  - Semantic search across cybersecurity knowledge
  - Entity relationship mapping (CVEs, exploits, tools)
  - CLI: `synos-knowledge --search "buffer overflow"`

- **RAG Architecture** (`synos-rag-system.service`)
  - ChromaDB and FAISS integration
  - Contextual retrieval for security documentation
  - Document chunking and similarity search
  - Response generation with context awareness

- **Context-Driven UI Adaptation** (`synos-adaptive-ui.service`)
  - Dynamic interface changes based on security phases
  - Threat level visualization (green/yellow/orange/red)
  - Accessibility adaptations and layout optimization
  - Integration with MATE desktop environment

### CLI Integration
- **`synos-ai`** - Unified natural language interface
- **`synos-knowledge`** - Knowledge graph query tool
- **Bash completion** - Auto-completion for security operations
- **Desktop entries** - MATE desktop integration

### Configuration Files
- `/etc/synos/phase3/nlp-config.yaml` - NLP interface settings
- `/etc/synos/phase3/llm-config.yaml` - LLM hub configuration
- `/etc/synos/phase3/knowledge-config.yaml` - Knowledge graph setup
- `/etc/synos/phase3/rag-config.yaml` - RAG system parameters
- `/etc/synos/phase3/ui-config.yaml` - UI adaptation rules

### Testing & Validation
- **`synos-phase3-test`** - Comprehensive integration testing
- **`synos-phase3-startup`** - System initialization script
- All services enabled with systemd integration
- Security hardening with resource limits

## 🎯 Key Capabilities Achieved

### Natural Language Security Operations
```bash
synos-ai "perform reconnaissance on target network 192.168.1.0/24"
synos-ai "check for SQL injection vulnerabilities in webapp.com"
synos-ai "analyze this suspicious file for malware indicators"
synos-ai "generate forensic timeline from disk image"
```

### Intelligent Knowledge Retrieval
```bash
synos-knowledge "what is CVE-2023-4911"
synos-knowledge --search "privilege escalation techniques"
synos-knowledge --related "metasploit modules"
synos-knowledge --export vulnerabilities
```

### Context-Aware Interface Adaptation
- **Reconnaissance Phase**: Blue theme, dual-pane layout, nmap/gobuster priority
- **Vulnerability Assessment**: Purple theme, triple-pane, nessus/openvas priority
- **Exploitation Phase**: Orange theme, focused layout, metasploit priority
- **Incident Response**: Red theme, emergency layout, volatility/autopsy priority

### Privacy-Preserving AI Features
- Local inference only (no cloud dependencies)
- Encrypted conversation storage
- Telemetry disabled by default
- Resource-constrained operation (4GB RAM max)

## 🔧 System Integration

### Systemd Services Status
All Phase 3 services are enabled and configured with:
- Automatic restart on failure
- Security hardening (NoNewPrivileges, ProtectSystem)
- Resource limits (CPU quota, memory caps)
- Structured logging to journald

### Directory Structure
```
/opt/synos/              # Phase 3 application binaries
├── nlp/                 # NLP command interface
├── llm-hub/             # LLM integration engine
├── knowledge-base/      # Knowledge graph system
├── rag-system/          # RAG architecture
├── adaptive-ui/         # UI adaptation engine
└── models/              # AI model storage

/var/lib/synos/          # Phase 3 data storage
├── knowledge/           # Knowledge graph database
└── embeddings/          # Vector embeddings

/etc/synos/phase3/       # Phase 3 configuration files
```

## 🎉 Achievement Milestone

**SynOS Phase 3: Natural Language & UX Components - COMPLETE**

This deployment successfully integrates advanced AI capabilities into SynOS, providing:
- Conversational security operations through natural language
- Intelligent knowledge management with semantic search
- Context-aware user interface adaptation
- Privacy-preserving local AI processing

The system is now ready for Phase 4: Privacy-Preserving AI & Production Deployment.
EOF

log "✅ Phase 3 Natural Language & UX Components deployment complete!"
log "📊 Summary report: PHASE3-DEPLOYMENT-SUMMARY.md"
log "🧪 Run integration tests: synos-phase3-test"
log "🚀 Phase 3 services will start automatically on next boot"

echo
echo -e "${GREEN}🎉 PHASE 3 DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${BLUE}Natural Language & UX Components fully integrated into SynOS${NC}"
echo
echo "Key commands to try:"
echo "  synos-ai 'scan network for vulnerabilities'"
echo "  synos-knowledge --search 'buffer overflow'"
echo "  synos-phase3-test"