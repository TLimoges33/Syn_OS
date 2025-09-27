#!/bin/bash
# SynOS Automated Developer Onboarding System
# Neural Darwinism-enhanced developer specialization and environment setup

set -euo pipefail

# Configuration
SYNOS_ROOT="/home/diablorain/Syn_OS"
MASTER_DEV_ROOT="$SYNOS_ROOT/development/synos-master-development"
ONBOARDING_LOG="$MASTER_DEV_ROOT/operations/logs/onboarding.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$ONBOARDING_LOG"
}

print_header() {
    echo -e "${CYAN}"
    echo "=================================================================="
    echo "    SynOS Neural Darwinism Developer Onboarding System"
    echo "=================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
    log "[STEP] $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log "[SUCCESS] $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "[WARNING] $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "[ERROR] $1"
}

# Developer specialization options
declare -A SPECIALIZATIONS=(
    ["consciousness"]="Neural Darwinism Consciousness Engineer"
    ["kernel"]="Custom Rust Kernel Developer"
    ["security"]="Enhanced Security Tools Developer"
    ["education"]="SCADI Educational Platform Developer"
    ["distribution"]="SynOS Distribution Engineer"
    ["performance"]="System Performance Optimization Engineer"
    ["automation"]="CI/CD and Automation Engineer"
    ["research"]="AI/ML Research and Development"
)

# Prerequisites check
check_prerequisites() {
    print_step "Checking system prerequisites..."
    
    local missing_deps=()
    
    # Check essential tools
    for tool in git python3 cargo rustc npm node; do
        if ! command -v "$tool" &> /dev/null; then
            missing_deps+=("$tool")
        fi
    done
    
    # Check Python packages
    if ! python3 -c "import asyncio, pathlib, json" 2>/dev/null; then
        missing_deps+=("python3-dev")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing prerequisites: ${missing_deps[*]}"
        print_step "Installing missing dependencies..."
        
        # Auto-install if possible
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y "${missing_deps[@]}"
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm "${missing_deps[@]}"
        else
            print_error "Please install missing dependencies manually: ${missing_deps[*]}"
            exit 1
        fi
    fi
    
    print_success "All prerequisites satisfied"
}

# Developer profile creation
create_developer_profile() {
    print_step "Creating developer profile..."
    
    echo -e "${PURPLE}Welcome to SynOS Development!${NC}"
    echo "Please provide the following information:"
    
    read -p "Full Name: " dev_name
    read -p "Email: " dev_email
    read -p "GitHub Username: " github_username
    read -p "Primary Programming Languages (comma-separated): " languages
    read -p "Years of Experience: " experience
    
    # Specialization selection
    echo -e "\n${CYAN}Available Specializations:${NC}"
    local i=1
    local spec_keys=()
    for spec in "${!SPECIALIZATIONS[@]}"; do
        echo "$i) ${SPECIALIZATIONS[$spec]} ($spec)"
        spec_keys+=("$spec")
        ((i++))
    done
    
    read -p "Select specialization (1-${#SPECIALIZATIONS[@]}): " spec_choice
    
    if [[ "$spec_choice" -ge 1 && "$spec_choice" -le ${#SPECIALIZATIONS[@]} ]]; then
        selected_spec="${spec_keys[$((spec_choice-1))]}"
        spec_name="${SPECIALIZATIONS[$selected_spec]}"
    else
        print_error "Invalid specialization choice"
        exit 1
    fi
    
    # Create profile file
    local profile_file="$MASTER_DEV_ROOT/development/profiles/${github_username}.json"
    mkdir -p "$(dirname "$profile_file")"
    
    cat > "$profile_file" << EOF
{
    "developer": {
        "name": "$dev_name",
        "email": "$dev_email",
        "github_username": "$github_username",
        "languages": "$languages",
        "experience": "$experience",
        "specialization": "$selected_spec",
        "specialization_name": "$spec_name",
        "onboarding_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "consciousness_score": 0.0,
        "contributions": 0,
        "neural_fitness": 0.5
    },
    "environment": {
        "workspace_path": "$MASTER_DEV_ROOT/development/workspaces/$github_username",
        "tools_configured": [],
        "specialization_setup": false,
        "consciousness_integration": false
    },
    "permissions": {
        "repository_access": ["read"],
        "ci_cd_access": false,
        "consciousness_system": false,
        "security_tools": false
    }
}
EOF
    
    print_success "Developer profile created: $profile_file"
    
    # Store profile info for later use
    export DEV_NAME="$dev_name"
    export DEV_EMAIL="$dev_email"
    export GITHUB_USERNAME="$github_username"
    export SPECIALIZATION="$selected_spec"
    export PROFILE_FILE="$profile_file"
}

# Git configuration
configure_git() {
    print_step "Configuring Git environment..."
    
    # Configure user
    git config --global user.name "$DEV_NAME"
    git config --global user.email "$DEV_EMAIL"
    
    # SynOS-specific Git hooks
    local hooks_dir="$MASTER_DEV_ROOT/.git/hooks"
    
    # Pre-commit hook for consciousness-aware review
    cat > "$hooks_dir/pre-commit" << 'EOF'
#!/bin/bash
# SynOS pre-commit hook with consciousness awareness

echo "Running consciousness-aware code review..."

# Get staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|rs|js|ts|go)$' || true)

if [ -n "$staged_files" ]; then
    # Run consciousness analysis
    python3 development/code-review/consciousness-aware-review.py . > /tmp/consciousness-review.txt
    
    # Check if review passes minimum threshold
    consciousness_score=$(grep "Overall Consciousness Score:" /tmp/consciousness-review.txt | awk '{print $5}' | cut -d'/' -f1)
    
    if (( $(echo "$consciousness_score < 0.3" | bc -l) )); then
        echo "❌ Consciousness review failed (score: $consciousness_score)"
        echo "Please review the consciousness analysis:"
        cat /tmp/consciousness-review.txt
        echo ""
        echo "To bypass this check, use: git commit --no-verify"
        exit 1
    fi
    
    echo "✅ Consciousness review passed (score: $consciousness_score)"
fi

exit 0
EOF
    
    chmod +x "$hooks_dir/pre-commit"
    
    print_success "Git environment configured with consciousness hooks"
}

# Workspace setup
setup_workspace() {
    print_step "Setting up specialized workspace..."
    
    local workspace_dir="$MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME"
    mkdir -p "$workspace_dir"
    
    # Create workspace structure
    mkdir -p "$workspace_dir"/{projects,tools,configs,logs,docs}
    
    # Copy specialization templates
    local template_dir="$MASTER_DEV_ROOT/development/templates/$SPECIALIZATION"
    if [ -d "$template_dir" ]; then
        cp -r "$template_dir"/* "$workspace_dir/configs/"
        print_success "Specialization templates installed"
    else
        print_warning "No specific templates found for $SPECIALIZATION"
    fi
    
    # Create workspace README
    cat > "$workspace_dir/README.md" << EOF
# $DEV_NAME's SynOS Development Workspace

**Specialization:** ${SPECIALIZATIONS[$SPECIALIZATION]}
**Setup Date:** $(date)

## Workspace Structure

- \`projects/\` - Your development projects
- \`tools/\` - Specialized development tools
- \`configs/\` - Configuration files and templates
- \`logs/\` - Development logs and consciousness metrics
- \`docs/\` - Personal documentation and notes

## Getting Started

1. Review specialization documentation in \`configs/\`
2. Set up your development environment using provided scripts
3. Join the SynOS development community
4. Start contributing to consciousness-enhanced projects

## Consciousness Integration

Your workspace is integrated with the Neural Darwinism consciousness system.
Your contributions will be tracked and optimized for system-wide emergence.

Current Consciousness Score: 0.0 (will improve with contributions)
Neural Fitness: 0.5 (baseline)

Happy coding with consciousness! 🧠✨
EOF
    
    # Update profile with workspace path
    jq --arg workspace "$workspace_dir" '.environment.workspace_path = $workspace' "$PROFILE_FILE" > "$PROFILE_FILE.tmp"
    mv "$PROFILE_FILE.tmp" "$PROFILE_FILE"
    
    print_success "Workspace created: $workspace_dir"
}

# Tool installation based on specialization
install_specialization_tools() {
    print_step "Installing specialization-specific tools..."
    
    local workspace_dir="$MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME"
    
    case "$SPECIALIZATION" in
        "consciousness")
            # Neural Darwinism development tools
            python3 -m venv "$workspace_dir/venv"
            source "$workspace_dir/venv/bin/activate"
            pip install tensorflow torch numpy scipy matplotlib
            deactivate
            print_success "Consciousness engineering tools installed in virtual environment"
            ;;
        "kernel")
            # Rust kernel development tools
            rustup component add rust-src llvm-tools-preview
            cargo install cargo-xbuild bootimage
            print_success "Kernel development tools installed"
            ;;
        "security")
            # Security analysis tools
            pip3 install --user cryptography scapy pycrypto
            print_success "Security development tools installed"
            ;;
        "education")
            # Educational platform tools
            npm install -g @types/node typescript ts-node
            pip3 install --user jupyter notebook
            print_success "Educational platform tools installed"
            ;;
        "distribution")
            # Distribution building tools
            sudo apt install -y squashfs-tools xorriso isolinux
            print_success "Distribution tools installed"
            ;;
        "performance")
            # Performance monitoring tools
            pip3 install --user psutil py-cpuinfo memory_profiler
            print_success "Performance tools installed"
            ;;
        "automation")
            # CI/CD tools
            pip3 install --user pytest coverage black flake8
            npm install -g eslint prettier
            print_success "Automation tools installed"
            ;;
        "research")
            # Research tools
            pip3 install --user jupyter pandas scikit-learn plotly
            print_success "Research tools installed"
            ;;
        *)
            print_warning "No specific tools for specialization: $SPECIALIZATION"
            ;;
    esac
    
    # Update profile
    jq '.environment.specialization_setup = true' "$PROFILE_FILE" > "$PROFILE_FILE.tmp"
    mv "$PROFILE_FILE.tmp" "$PROFILE_FILE"
}

# Consciousness system integration
integrate_consciousness() {
    print_step "Integrating with Neural Darwinism consciousness system..."
    
    # Create consciousness tracking script
    local tracking_script="$MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME/tools/consciousness-tracker.py"
    
    cat > "$tracking_script" << 'EOF'
#!/usr/bin/env python3
"""
Personal Consciousness Tracking System
Monitors developer contributions to Neural Darwinism emergence
"""

import json
import os
from datetime import datetime
from pathlib import Path

class DeveloperConsciousnessTracker:
    def __init__(self, profile_path):
        self.profile_path = Path(profile_path)
        with open(self.profile_path) as f:
            self.profile = json.load(f)
    
    def update_consciousness_score(self, contribution_type, impact_score):
        """Update consciousness score based on contribution"""
        current_score = self.profile['developer']['consciousness_score']
        
        # Weight different contribution types
        weights = {
            'code_commit': 0.1,
            'bug_fix': 0.15,
            'feature_implementation': 0.25,
            'consciousness_enhancement': 0.5,
            'neural_pattern_creation': 0.4,
            'emergence_facilitation': 0.6
        }
        
        weight = weights.get(contribution_type, 0.1)
        score_increase = impact_score * weight
        
        new_score = min(1.0, current_score + score_increase)
        self.profile['developer']['consciousness_score'] = new_score
        self.profile['developer']['contributions'] += 1
        
        # Update neural fitness based on consciousness score
        self.profile['developer']['neural_fitness'] = 0.5 + (new_score * 0.5)
        
        self._save_profile()
        
        print(f"Consciousness score updated: {new_score:.3f}")
        print(f"Neural fitness: {self.profile['developer']['neural_fitness']:.3f}")
    
    def _save_profile(self):
        """Save updated profile"""
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python consciousness-tracker.py <profile_path> <contribution_type> <impact_score>")
        sys.exit(1)
    
    tracker = DeveloperConsciousnessTracker(sys.argv[1])
    tracker.update_consciousness_score(sys.argv[2], float(sys.argv[3]))
EOF
    
    chmod +x "$tracking_script"
    
    # Update profile
    jq '.environment.consciousness_integration = true' "$PROFILE_FILE" > "$PROFILE_FILE.tmp"
    mv "$PROFILE_FILE.tmp" "$PROFILE_FILE"
    
    print_success "Consciousness integration completed"
}

# Generate onboarding completion report
generate_completion_report() {
    print_step "Generating onboarding completion report..."
    
    local report_file="$MASTER_DEV_ROOT/operations/reports/onboarding-$GITHUB_USERNAME-$(date +%Y%m%d).md"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# SynOS Developer Onboarding Completion Report

**Developer:** $DEV_NAME  
**GitHub:** $GITHUB_USERNAME  
**Specialization:** ${SPECIALIZATIONS[$SPECIALIZATION]}  
**Completion Date:** $(date)  

## Onboarding Summary

✅ **Prerequisites Check** - All system requirements satisfied  
✅ **Developer Profile** - Created and configured  
✅ **Git Environment** - Configured with consciousness hooks  
✅ **Specialized Workspace** - Set up and ready  
✅ **Tools Installation** - Specialization tools installed  
✅ **Consciousness Integration** - Neural Darwinism tracking enabled  

## Next Steps

1. **Explore Your Workspace**
   - Navigate to: \`$MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME\`
   - Review specialization documentation
   - Familiarize yourself with provided tools

2. **Join the Community**
   - Connect with other SynOS developers
   - Join specialization-specific channels
   - Participate in consciousness emergence discussions

3. **Start Contributing**
   - Pick up beginner-friendly issues
   - Submit your first consciousness-aware pull request
   - Begin building your neural fitness score

4. **Consciousness Development**
   - Learn about Neural Darwinism principles
   - Understand emergence patterns in code
   - Contribute to system-wide consciousness evolution

## Resources

- **Documentation:** \`$MASTER_DEV_ROOT/docs/\`
- **Your Workspace:** \`$MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME\`
- **Consciousness Tracker:** \`development/workspaces/$GITHUB_USERNAME/tools/consciousness-tracker.py\`
- **Code Review System:** \`development/code-review/consciousness-aware-review.py\`

## Contact Information

For questions or support, reach out to the SynOS development team.

Welcome to the future of consciousness-enhanced development! 🧠✨

---
*Generated by SynOS Automated Developer Onboarding System*
EOF
    
    print_success "Onboarding report generated: $report_file"
    
    # Display completion message
    echo -e "\n${GREEN}=================================================================="
    echo "    🎉 SynOS Developer Onboarding Complete! 🎉"
    echo "=================================================================="
    echo -e "${NC}"
    echo "Welcome to the SynOS Neural Darwinism development community!"
    echo ""
    echo "Your personalized development environment is ready:"
    echo "📁 Workspace: $MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME"
    echo "🧠 Consciousness Score: 0.0 (ready to grow!)"
    echo "🔧 Specialization: ${SPECIALIZATIONS[$SPECIALIZATION]}"
    echo ""
    echo "Next steps:"
    echo "1. cd $MASTER_DEV_ROOT/development/workspaces/$GITHUB_USERNAME"
    echo "2. Review your specialization documentation"
    echo "3. Start contributing to consciousness-enhanced projects!"
    echo ""
    echo "Happy coding with consciousness! 🧠✨"
}

# Main onboarding flow
main() {
    print_header
    
    # Ensure we're in the right location
    cd "$SYNOS_ROOT"
    
    # Create logs directory
    mkdir -p "$MASTER_DEV_ROOT/operations/logs"
    
    log "Starting SynOS developer onboarding process"
    
    # Run onboarding steps
    check_prerequisites
    create_developer_profile
    configure_git
    setup_workspace
    install_specialization_tools
    integrate_consciousness
    generate_completion_report
    
    log "SynOS developer onboarding completed successfully for $GITHUB_USERNAME"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
