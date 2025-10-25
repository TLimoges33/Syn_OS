#!/bin/bash

# Automated GitHub Repository Forking Script
# Requires: gh CLI tool and proper authentication

set -euo pipefail

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Install with: sudo apt install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Run: gh auth login"
    exit 1
fi

echo "🚀 Starting automated repository forking..."

# Tier 1: Critical repositories
declare -a tier1_repos=(
    "torvalds/linux"
    "rust-lang/rust"
    "cilium/ebpf"
    "libbpf/libbpf"
    "phil-opp/blog_os"
    "systemd/systemd"
)

# Tier 2: Penetration testing tools
declare -a tier2_repos=(
    "rapid7/metasploit-framework"
    "sqlmapproject/sqlmap"
    "nmap/nmap"
    "projectdiscovery/nuclei"
    "bettercap/bettercap"
    "lanmaster53/recon-ng"
    "zaproxy/zaproxy"
    "BloodHoundAD/BloodHound"
)

# Tier 3: Bug bounty and advanced tools
declare -a tier3_repos=(
    "projectdiscovery/subfinder"
    "OWASP/Amass"
    "ffuf/ffuf"
    "hashcat/hashcat"
    "volatilityfoundation/volatility3"
    "radareorg/radare2"
    "sleuthkit/sleuthkit"
    "prometheus/prometheus"
    "grafana/grafana"
)

fork_repository() {
    local repo=$1
    local tier=$2

    echo "📁 Forking $repo (Tier $tier)..."

    if gh repo fork "$repo" --org SynOS-Security --clone=false; then
        echo "✅ Successfully forked $repo"

        # Add to local tracking
        echo "$repo,Tier$tier,$(date)" >> forked_repositories.csv
    else
        echo "❌ Failed to fork $repo"
        echo "$repo,Tier$tier,FAILED,$(date)" >> failed_forks.csv
    fi

    # Rate limiting - wait 2 seconds between forks
    sleep 2
}

# Initialize tracking files
echo "Repository,Tier,Date" > forked_repositories.csv
echo "Repository,Tier,Status,Date" > failed_forks.csv

# Fork Tier 1 repositories (most critical)
echo "🎯 Forking Tier 1 repositories (Critical)..."
for repo in "${tier1_repos[@]}"; do
    fork_repository "$repo" "1"
done

# Fork Tier 2 repositories
echo "🛡️ Forking Tier 2 repositories (Penetration Testing)..."
for repo in "${tier2_repos[@]}"; do
    fork_repository "$repo" "2"
done

# Fork Tier 3 repositories
echo "🔍 Forking Tier 3 repositories (Bug Bounty & Advanced)..."
for repo in "${tier3_repos[@]}"; do
    fork_repository "$repo" "3"
done

echo ""
echo "📊 Fork Summary:"
echo "✅ Successfully forked: $(wc -l < forked_repositories.csv) repositories"
if [[ -f failed_forks.csv ]] && [[ $(wc -l < failed_forks.csv) -gt 1 ]]; then
    echo "❌ Failed forks: $(( $(wc -l < failed_forks.csv) - 1 )) repositories"
    echo "Check failed_forks.csv for details"
fi

echo ""
echo "🎉 GitHub integration setup complete!"
echo "Next steps:"
echo "1. Configure local clones: ./setup-local-repos.sh"
echo "2. Set up CI/CD pipeline: ./setup-ci-cd.sh"
echo "3. Begin integration development"
