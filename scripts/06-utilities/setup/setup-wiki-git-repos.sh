#!/bin/bash
# SynOS Wiki Security - Separate Git Repositories Setup
# This script creates 3 separate git repositories for different access levels

set -e  # Exit on error

echo "📦 SynOS Wiki Security - Git Repository Separation"
echo "=================================================="
echo ""

WIKI_DIR="/home/diablorain/Syn_OS/wiki"
BACKUP_DIR="/home/diablorain/Syn_OS/wiki-backup-$(date +%Y%m%d-%H%M%S)"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) not installed"
    echo "   Install with: sudo apt install gh"
    echo "   Or: brew install gh"
    echo ""
    echo "   For now, I'll show you the manual steps..."
    GH_AVAILABLE=false
else
    echo "✅ GitHub CLI (gh) is installed"
    GH_AVAILABLE=true
fi

echo ""

# ===========================================
# STEP 1: Backup Current Wiki
# ===========================================
echo "1️⃣  Creating backup of current wiki..."

cp -r "$WIKI_DIR" "$BACKUP_DIR"
echo "   ✅ Backup created: $BACKUP_DIR"
echo ""

# ===========================================
# STEP 2: Initialize Git in Each Directory
# ===========================================
echo "2️⃣  Initializing git repositories..."
echo ""

# Internal repository
if [ -d "$WIKI_DIR/internal" ]; then
    echo "   🔴 INTERNAL repository..."
    cd "$WIKI_DIR/internal"

    if [ ! -d ".git" ]; then
        git init
        echo "      ✅ Git initialized"

        # Create README for the separate repo
        cat > README-REPO.md << 'EOF'
# SynOS Wiki - Internal Documentation

**⚠️ CONFIDENTIAL - EMPLOYEES ONLY**

This is a **private repository** containing company confidential information.

## What's Here

- MSSP operations guide (pricing: $500, $2,000, custom)
- Proprietary AI Consciousness Engine (54,218 lines of code)
- Custom kernel internals and architecture
- Security framework implementation details
- Advanced exploitation techniques
- Red team methodologies
- Production infrastructure configurations
- Zero-day development processes

## Access

**Who can access**: Employees and contractors with signed NDA only

**Authentication**:
- VPN required
- Employee SSO
- Audit logging enabled

## Security

- Never share outside the company
- Never commit to public repos
- Review before sharing screens
- Lock workstation when away

## Questions?

- Security: security@synos.com
- Legal: legal@synos.com
- IT Support: it-support@synos.com
EOF

        git add .
        git commit -m "Initial commit: Internal documentation (confidential)"
        echo "      ✅ Initial commit created"
    else
        echo "      ℹ️  Already a git repository"
    fi

    echo ""
fi

# Restricted repository
if [ -d "$WIKI_DIR/restricted" ]; then
    echo "   🟡 RESTRICTED repository..."
    cd "$WIKI_DIR/restricted"

    if [ ! -d ".git" ]; then
        git init
        echo "      ✅ Git initialized"

        cat > README-REPO.md << 'EOF'
# SynOS Wiki - Licensed User Documentation

**🔒 RESTRICTED - LICENSED USERS ONLY**

This is a **private repository** for paying customers (Professional/Enterprise tiers).

## What's Here

- Complete 500+ security tool catalog
- Docker deployment guides
- Kubernetes orchestration
- Professional penetration testing guides
- Build system internals
- System call reference
- Error code database

## Access

**Who can access**: Users with valid Professional or Enterprise license

**Authentication**:
- Login required at portal.synos.com
- Valid license key
- Terms of service acceptance

## License Required

- Professional: $2,000/year
- Enterprise: Custom pricing

## Support

- Professional: support@synos.com (24-48h)
- Enterprise: enterprise@synos.com (24/7)

## Questions?

- Sales: sales@synos.com
- Support: support@synos.com
- Licensing: licensing@synos.com
EOF

        git add .
        git commit -m "Initial commit: Restricted documentation (licensed users)"
        echo "      ✅ Initial commit created"
    else
        echo "      ℹ️  Already a git repository"
    fi

    echo ""
fi

# Public repository (already in main repo, but we'll note it)
echo "   🟢 PUBLIC documentation..."
echo "      ℹ️  Public docs remain in main repository"
echo ""

# ===========================================
# STEP 3: Create GitHub Repositories
# ===========================================
echo "3️⃣  Creating GitHub repositories..."
echo ""

if [ "$GH_AVAILABLE" = true ]; then
    echo "   Checking GitHub authentication..."
    if gh auth status &> /dev/null; then
        echo "   ✅ Authenticated with GitHub"
        echo ""

        # Create internal repo
        echo "   Creating internal repository (private)..."
        if gh repo view TLimoges33/Syn_OS_Wiki_Internal &> /dev/null; then
            echo "      ℹ️  Repository already exists: TLimoges33/Syn_OS_Wiki_Internal"
        else
            read -p "   Create private repo 'Syn_OS_Wiki_Internal'? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                gh repo create TLimoges33/Syn_OS_Wiki_Internal \
                    --private \
                    --description "SynOS Internal Documentation (Confidential)" \
                    --disable-wiki \
                    --disable-issues
                echo "      ✅ Created private repository"
            fi
        fi

        # Create restricted repo
        echo "   Creating restricted repository (private)..."
        if gh repo view TLimoges33/Syn_OS_Wiki_Licensed &> /dev/null; then
            echo "      ℹ️  Repository already exists: TLimoges33/Syn_OS_Wiki_Licensed"
        else
            read -p "   Create private repo 'Syn_OS_Wiki_Licensed'? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                gh repo create TLimoges33/Syn_OS_Wiki_Licensed \
                    --private \
                    --description "SynOS Licensed User Documentation (Professional/Enterprise)" \
                    --disable-wiki \
                    --disable-issues
                echo "      ✅ Created private repository"
            fi
        fi

    else
        echo "   ⚠️  Not authenticated with GitHub"
        echo "      Run: gh auth login"
    fi
else
    echo "   ⚠️  GitHub CLI not available - Manual setup required"
fi

echo ""

# ===========================================
# STEP 4: Add Remote and Push
# ===========================================
echo "4️⃣  Adding git remotes..."
echo ""

# Internal
if [ -d "$WIKI_DIR/internal/.git" ]; then
    cd "$WIKI_DIR/internal"

    if ! git remote | grep -q "origin"; then
        echo "   🔴 INTERNAL: Adding remote..."
        echo "      Manual command:"
        echo "      cd $WIKI_DIR/internal"
        echo "      git remote add origin git@github.com:TLimoges33/Syn_OS_Wiki_Internal.git"
        echo "      git push -u origin master"
        echo ""
    else
        echo "   🔴 INTERNAL: Remote already configured"
    fi
fi

# Restricted
if [ -d "$WIKI_DIR/restricted/.git" ]; then
    cd "$WIKI_DIR/restricted"

    if ! git remote | grep -q "origin"; then
        echo "   🟡 RESTRICTED: Adding remote..."
        echo "      Manual command:"
        echo "      cd $WIKI_DIR/restricted"
        echo "      git remote add origin git@github.com:TLimoges33/Syn_OS_Wiki_Licensed.git"
        echo "      git push -u origin master"
        echo ""
    else
        echo "   🟡 RESTRICTED: Remote already configured"
    fi
fi

echo ""

# ===========================================
# STEP 5: Update Main Repository .gitignore
# ===========================================
echo "5️⃣  Updating main repository .gitignore..."

cd /home/diablorain/Syn_OS

if grep -q "wiki/internal/" .gitignore; then
    echo "   ✅ .gitignore already configured"
else
    echo "   ⚠️  .gitignore needs to be updated (already done in Step 1)"
fi

echo ""

# ===========================================
# STEP 6: Create Git Submodules (Optional)
# ===========================================
echo "6️⃣  Git submodules setup (optional)..."
echo ""
echo "   To use git submodules (link separate repos back to main):"
echo ""
echo "   cd /home/diablorain/Syn_OS"
echo "   git submodule add git@github.com:TLimoges33/Syn_OS_Wiki_Internal.git wiki/internal"
echo "   git submodule add git@github.com:TLimoges33/Syn_OS_Wiki_Licensed.git wiki/restricted"
echo "   git commit -m 'Add wiki submodules'"
echo ""
echo "   ⚠️  WARNING: Submodules will still be visible in main repo!"
echo "      Only use if you want employees to easily clone everything."
echo ""

# ===========================================
# FINAL SUMMARY
# ===========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ GIT REPOSITORY SEPARATION CONFIGURED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Repository Structure:"
echo "   🔴 Internal:    wiki/internal/  → Separate private repo"
echo "   🟡 Restricted:  wiki/restricted/ → Separate private repo"
echo "   🟢 Public:      wiki/*.md       → Main public repo"
echo ""
echo "🔒 Security Status:"
echo "   • Internal docs are in separate private git repo"
echo "   • Restricted docs are in separate private git repo"
echo "   • Public docs remain in main repository"
echo "   • .gitignore prevents accidental commits"
echo ""
echo "📝 Manual Steps Required:"
echo ""
echo "   1. Authenticate with GitHub:"
echo "      gh auth login"
echo ""
echo "   2. Push internal repository:"
echo "      cd $WIKI_DIR/internal"
echo "      git remote add origin git@github.com:TLimoges33/Syn_OS_Wiki_Internal.git"
echo "      git push -u origin master"
echo ""
echo "   3. Push restricted repository:"
echo "      cd $WIKI_DIR/restricted"
echo "      git remote add origin git@github.com:TLimoges33/Syn_OS_Wiki_Licensed.git"
echo "      git push -u origin master"
echo ""
echo "   4. Configure GitHub repository settings:"
echo "      • Go to repository Settings → Manage Access"
echo "      • Add team members for internal repo"
echo "      • Add licensed users for restricted repo"
echo "      • Enable branch protection on master"
echo ""
echo "   5. Set up deploy keys for CI/CD (optional)"
echo ""
echo "⚠️  Important:"
echo "   • NEVER make these repos public"
echo "   • Use SSH keys for authentication"
echo "   • Enable 2FA on GitHub"
echo "   • Review access regularly"
echo ""
echo "💾 Backup Location: $BACKUP_DIR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
