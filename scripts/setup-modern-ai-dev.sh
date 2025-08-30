#!/bin/bash
set -euo pipefail

# Modern AI Development Environment Setup for Syn_OS
# Optimized for Claude Code, GitHub Copilot, and modern development practices

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Setting up Modern AI Development Environment for Syn_OS"
echo "=========================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in correct directory
if [[ ! -f "$PROJECT_ROOT/CLAUDE.md" ]]; then
    log_error "Please run this script from the Syn_OS project root"
    exit 1
fi

cd "$PROJECT_ROOT"

log_info "Current directory: $(pwd)"

# 1. Environment Validation
log_info "Validating development environment..."

# Check required tools
REQUIRED_TOOLS=("git" "docker" "podman" "rustc" "cargo" "python3" "go" "code" "gh")
MISSING_TOOLS=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS+=("$tool")
    else
        log_success "$tool is available"
    fi
done

if [[ ${#MISSING_TOOLS[@]} -gt 0 ]]; then
    log_error "Missing required tools: ${MISSING_TOOLS[*]}"
    log_info "Please install missing tools and run again"
    exit 1
fi

# 2. Setup Environment Files
log_info "Setting up environment configuration..."

if [[ ! -f ".env" ]]; then
    log_info "Creating .env from template..."
    cp .env.example .env
    
    # Generate secure random passwords
    POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    REDIS_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    NATS_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
    ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    INTERNAL_API_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    # Update .env with generated passwords
    sed -i "s/your_secure_password_here/$POSTGRES_PASS/g" .env
    sed -i "s/your_redis_password_here/$REDIS_PASS/g" .env
    sed -i "s/your_nats_password_here/$NATS_PASS/g" .env
    sed -i "s/your_jwt_secret_key_here_minimum_32_characters/$JWT_SECRET/g" .env
    sed -i "s/your_encryption_key_here_32_characters/$ENCRYPTION_KEY/g" .env
    sed -i "s/your_internal_api_key_here/$INTERNAL_API_KEY/g" .env
    
    log_success "Environment file created with secure random passwords"
else
    log_info ".env file already exists"
fi

# 3. VS Code Configuration Optimization
log_info "Optimizing VS Code configuration..."

# Create .vscode directory if it doesn't exist
mkdir -p .vscode

# Enhanced settings for AI development
cat > .vscode/settings.json << 'EOF'
{
    // Rust Configuration - Enhanced for kernel development
    "rust-analyzer.cargo.features": ["all"],
    "rust-analyzer.check.command": "clippy",
    "rust-analyzer.cargo.loadOutDirsFromCheck": true,
    "rust-analyzer.procMacro.enable": true,
    "rust-analyzer.experimental.procAttrMacros": true,
    "rust-analyzer.inlayHints.enable": true,
    "rust-analyzer.completion.addCallArgumentSnippets": true,
    "rust-analyzer.cargo.allFeatures": true,
    "rust-analyzer.checkOnSave.command": "clippy",
    "rust-analyzer.checkOnSave.extraArgs": ["--all-targets", "--all-features"],
    
    // Python Configuration - Enhanced for AI/ML development
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.banditEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.typeCheckingMode": "strict",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.autoTestDiscoverOnSaveEnabled": true,
    
    // Go Configuration
    "go.formatTool": "goimports",
    "go.lintTool": "golangci-lint",
    "go.testFlags": ["-v", "-race"],
    "go.buildFlags": ["-race"],
    "go.vetFlags": ["-all"],
    
    // C/C++ Configuration for low-level development
    "C_Cpp.clang_format_style": "Google",
    "C_Cpp.intelliSenseEngine": "default",
    "C_Cpp.errorSquiggles": "enabled",
    "C_Cpp.codeAnalysis.clangTidy.enabled": true,
    
    // AI Development Enhancements
    "github.copilot.enable": {
        "*": true,
        "yaml": true,
        "plaintext": true,
        "markdown": true,
        "rust": true,
        "python": true,
        "go": true,
        "c": true,
        "cpp": true
    },
    "github.copilot.advanced.debug.overrideEngine": "codegen",
    "github.copilot.advanced.debug.useNodejs": true,
    
    // Editor Enhancements
    "editor.formatOnSave": true,
    "editor.formatOnPaste": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": "always",
        "source.organizeImports": "always",
        "source.sortMembers": "always"
    },
    "editor.rulers": [80, 100, 120],
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.trimAutoWhitespace": true,
    "editor.linkedEditing": true,
    "editor.bracketPairColorization.enabled": true,
    "editor.guides.bracketPairs": "active",
    "editor.inlineSuggest.enabled": true,
    "editor.suggestSelection": "first",
    "editor.wordBasedSuggestions": "off",
    
    // File Associations - Enhanced
    "files.associations": {
        "*.toml": "toml",
        "*.rs": "rust",
        "*.asm": "asm",
        "*.s": "asm",
        "Dockerfile*": "dockerfile",
        "*.yml": "yaml",
        "*.yaml": "yaml",
        "*.json": "jsonc",
        "*.md": "markdown",
        "CLAUDE.md": "markdown"
    },
    
    // Performance Optimizations
    "files.exclude": {
        "**/target": true,
        "**/.venv": true,
        "**/venv": true,
        "**/node_modules": true,
        "**/.git/objects": true,
        "**/.git/subtree-cache": true,
        "**/*.tmp": true,
        "**/*.log": true,
        "**/dist": true,
        "**/build": true
    },
    
    "files.watcherExclude": {
        "**/target/**": true,
        "**/.venv/**": true,
        "**/venv/**": true,
        "**/node_modules/**": true,
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/dist/**": true,
        "**/build/**": true
    },
    
    "search.exclude": {
        "**/target": true,
        "**/.venv": true,
        "**/venv": true,
        "**/node_modules": true,
        "**/Cargo.lock": true,
        "**/dist": true,
        "**/build": true
    },
    
    // Git Configuration
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    "git.autofetch": true,
    "git.defaultCloneDirectory": "../",
    "git.showPushSuccessNotification": true,
    "git.suggestSmartCommit": false,
    
    // Terminal Configuration
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.profiles.linux": {
        "bash": {
            "path": "/bin/bash",
            "args": ["--login"]
        }
    },
    "terminal.integrated.copyOnSelection": true,
    "terminal.integrated.cursorBlinking": true,
    "terminal.integrated.fontSize": 14,
    "terminal.integrated.scrollback": 10000,
    "terminal.integrated.enableVisualBell": false,
    "terminal.integrated.allowChords": false,
    
    // Security and Privacy
    "security.workspace.trust.enabled": false,
    "telemetry.telemetryLevel": "off",
    "workbench.enableExperiments": false,
    "extensions.autoUpdate": false,
    
    // Workspace Enhancements
    "workbench.editor.enablePreview": false,
    "workbench.startupEditor": "readme",
    "workbench.tree.indent": 20,
    "workbench.colorTheme": "Default Dark+",
    "workbench.iconTheme": "vs-seti",
    
    // Explorer Configuration
    "explorer.confirmDelete": false,
    "explorer.confirmDragAndDrop": false,
    "explorer.compactFolders": false,
    "explorer.sortOrder": "type",
    
    // Debug Configuration
    "debug.allowBreakpointsEverywhere": true,
    "debug.console.fontSize": 14,
    "debug.inlineValues": "auto",
    "debug.showBreakpointsInOverviewRuler": true,
    
    // Problems and Diagnostics
    "problems.showCurrentInStatus": true,
    "problems.sortOrder": "severity",
    
    // Markdown Configuration
    "markdown.preview.fontSize": 14,
    "markdown.preview.lineHeight": 1.6,
    "markdown.preview.scrollPreviewWithEditor": true,
    "markdown.preview.markEditorSelection": true,
    
    // Language-specific settings
    "[rust]": {
        "editor.defaultFormatter": "rust-lang.rust-analyzer",
        "editor.formatOnSave": true,
        "editor.semanticHighlighting.enabled": true
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "always"
        }
    },
    "[go]": {
        "editor.defaultFormatter": "golang.go",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "always"
        }
    },
    "[json]": {
        "editor.defaultFormatter": "vscode.json-language-features"
    },
    "[yaml]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[markdown]": {
        "editor.defaultFormatter": "yzhang.markdown-all-in-one",
        "editor.wordWrap": "on"
    }
}
EOF

log_success "VS Code settings optimized for AI development"

# 4. Enhanced Launch Configuration for Debugging
cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Rust Kernel",
            "type": "lldb",
            "request": "launch",
            "program": "${workspaceFolder}/target/x86_64-syn_os/debug/syn_os_kernel",
            "args": [],
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "lldb",
            "preLaunchTask": "cargo build kernel"
        },
        {
            "name": "Debug Security Module",
            "type": "lldb",
            "request": "launch",
            "program": "${workspaceFolder}/target/debug/security_module",
            "args": [],
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "lldb",
            "preLaunchTask": "cargo build security"
        },
        {
            "name": "Debug Python Security Tests",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/tests/test_security.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Debug Go Orchestrator",
            "type": "go",
            "request": "launch",
            "mode": "debug",
            "program": "${workspaceFolder}/services/orchestrator/main.go",
            "env": {
                "ENV": "development"
            },
            "args": []
        }
    ]
}
EOF

log_success "Debug configurations created"

# 5. Enhanced Task Configuration
cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "cargo build kernel",
            "type": "cargo",
            "command": "build",
            "args": [
                "--manifest-path=src/kernel/Cargo.toml",
                "--target=x86_64-syn_os"
            ],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": [
                "$rustc"
            ]
        },
        {
            "label": "cargo build security",
            "type": "cargo", 
            "command": "build",
            "args": [
                "--manifest-path=src/security/Cargo.toml"
            ],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": [
                "$rustc"
            ]
        },
        {
            "label": "run security audit",
            "type": "shell",
            "command": "python3",
            "args": [
                "scripts/a_plus_security_audit.py"
            ],
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "run comprehensive tests",
            "type": "shell",
            "command": "make",
            "args": ["test"],
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "start development containers",
            "type": "shell",
            "command": "docker-compose",
            "args": ["-f", "docker-compose.yml", "up", "-d"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "stop development containers", 
            "type": "shell",
            "command": "docker-compose",
            "args": ["-f", "docker-compose.yml", "down"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "validate environment",
            "type": "shell",
            "command": "./scripts/validate-environment.sh",
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "build ISO image",
            "type": "shell",
            "command": "./scripts/build-simple-kernel-iso.sh",
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        }
    ]
}
EOF

log_success "Enhanced task configurations created"

# 6. Python Virtual Environment Setup
log_info "Setting up Python virtual environment..."

if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    log_success "Python virtual environment created"
else
    log_info "Python virtual environment already exists"
fi

# Activate virtual environment and install/upgrade dependencies
source venv/bin/activate

# Upgrade pip and install wheel
python -m pip install --upgrade pip wheel setuptools

# Install core dependencies
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    log_success "Core Python dependencies installed"
fi

# Install development and security dependencies
pip install --upgrade \
    black \
    pylint \
    mypy \
    bandit \
    pytest \
    pytest-cov \
    pytest-asyncio \
    safety \
    pip-audit

log_success "Python development tools installed"

# 7. Rust Development Environment
log_info "Setting up Rust development environment..."

# Install additional Rust components if not already installed
rustup component add clippy rustfmt llvm-tools-preview --toolchain nightly

# Install cargo tools for development
cargo install --locked \
    cargo-audit \
    cargo-deny \
    cargo-outdated \
    cargo-tarpaulin \
    cargo-watch \
    bindgen

log_success "Rust development tools installed"

# 8. Git Configuration Optimization
log_info "Optimizing Git configuration..."

# Create enhanced gitignore
cat >> .gitignore << 'EOF'

# AI Development artifacts
.ai_temp/
.claude_temp/
.copilot_cache/

# IDE specific
.vscode/settings.json.backup
.idea/
*.swp
*.swo

# OS specific
.DS_Store
Thumbs.db

# Development tools
.mypy_cache/
.pytest_cache/
__pycache__/
*.pyc
*.pyo

# Environment files
.env.local
.env.development
.env.production

# Build artifacts
target/
dist/
build/
*.o
*.a
*.so
*.dylib

# Logs and temporary files
*.log
*.tmp
*.temp

# Security sensitive
private_keys/
certificates/
secrets/
EOF

# Setup git hooks directory
mkdir -p .githooks

# Pre-commit hook for security checks
cat > .githooks/pre-commit << 'EOF'
#!/bin/bash
set -e

echo "Running pre-commit security checks..."

# Run security audit if Python files changed
if git diff --cached --name-only | grep -q '\.py$'; then
    echo "Python files detected, running security audit..."
    python scripts/a_plus_security_audit.py --quick || {
        echo "Security audit failed! Please fix issues before committing."
        exit 1
    }
fi

# Run Rust security audit if Rust files changed
if git diff --cached --name-only | grep -q '\.rs$'; then
    echo "Rust files detected, running cargo audit..."
    cargo audit || {
        echo "Rust security audit failed! Please fix issues before committing."
        exit 1
    }
fi

# Format code
if git diff --cached --name-only | grep -q '\.py$'; then
    echo "Formatting Python files..."
    black --check $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$') || {
        echo "Python formatting required. Run 'black .' and commit again."
        exit 1
    }
fi

if git diff --cached --name-only | grep -q '\.rs$'; then
    echo "Formatting Rust files..."
    cargo fmt --all -- --check || {
        echo "Rust formatting required. Run 'cargo fmt --all' and commit again."
        exit 1
    }
fi

echo "Pre-commit checks passed!"
EOF

chmod +x .githooks/pre-commit

# Configure git to use our hooks
git config core.hooksPath .githooks

log_success "Git configuration optimized with security hooks"

# 9. Container Infrastructure Setup
log_info "Starting development infrastructure..."

# Check if containers are running
if ! docker ps | grep -q "syn_os_"; then
    log_info "Starting development containers..."
    docker-compose -f docker-compose.yml up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Verify services
    if docker ps | grep -q "syn_os_postgres.*Up"; then
        log_success "PostgreSQL is running"
    else
        log_warning "PostgreSQL may not be running properly"
    fi
    
    if docker ps | grep -q "syn_os_redis.*Up"; then
        log_success "Redis is running"
    else
        log_warning "Redis may not be running properly"
    fi
    
    if docker ps | grep -q "syn_os_nats.*Up"; then
        log_success "NATS is running"
    else
        log_warning "NATS may not be running properly"
    fi
else
    log_success "Development containers already running"
fi

# 10. Build and Test
log_info "Running initial build and tests..."

# Build Rust components
log_info "Building Rust workspace..."
cargo build --workspace

# Run quick tests
log_info "Running quick tests..."
make test || log_warning "Some tests failed - check output above"

# 11. Final Validation
log_info "Running environment validation..."
./scripts/validate-environment.sh || log_warning "Environment validation had issues"

echo ""
echo "=========================================================="
log_success "Modern AI Development Environment Setup Complete!"
echo "=========================================================="
echo ""
echo "🎯 Next Steps:"
echo "  1. Open VS Code in this directory: code ."
echo "  2. Install recommended extensions when prompted"
echo "  3. Activate Python virtual environment: source venv/bin/activate"
echo "  4. Run security audit: python scripts/a_plus_security_audit.py"
echo "  5. Check CLAUDE.md for development workflows"
echo ""
echo "🔧 Available Commands:"
echo "  • make build        - Build all components"
echo "  • make test         - Run comprehensive tests"
echo "  • make dev          - Start development containers"
echo "  • cargo build       - Build Rust workspace"
echo "  • ./scripts/*       - Various utility scripts"
echo ""
echo "🤖 AI Development Features:"
echo "  • GitHub Copilot enabled for all languages"
echo "  • Claude Code integration optimized"
echo "  • Intelligent code suggestions and completions"
echo "  • Automated security scanning in git hooks"
echo "  • Enhanced debugging configurations"
echo ""
echo "📊 Monitoring:"
echo "  • Security alerts: logs/security/security_alerts.log"
echo "  • System logs: logs/ directory"
echo "  • Container logs: docker-compose logs -f"
echo ""

deactivate 2>/dev/null || true

log_success "Setup completed successfully! Happy coding! 🚀"