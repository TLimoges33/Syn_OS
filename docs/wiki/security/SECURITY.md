# SynOS Wiki Security Documentation
**Last Updated:** October 22, 2025

## 🔒 Secure Directory Structure

The SynOS wiki contains sensitive documentation that requires multi-layered security:

```
docs/wiki/
├── internal/          # 🔴 HIGHLY RESTRICTED - Internal development docs
│   ├── .gitattributes # Git-crypt encryption rules
│   ├── .gpg-id        # GPG key ID for encryption
│   └── *.md           # Encrypted documentation (AI, kernel, security)
│
├── restricted/        # 🟡 LICENSED ACCESS - Licensed developer docs
│   ├── .gitattributes # Git-crypt encryption rules
│   ├── .gpg-id        # GPG key ID for encryption
│   └── *.md           # Encrypted documentation (deployment, testing)
│
└── public/            # 🟢 PUBLIC - General documentation
    └── *.md           # Public documentation
```

## 🛡️ Security Layers

### Layer 1: Git Ignore (Public Repository Protection)
```gitignore
# In root .gitignore
docs/wiki/internal/
docs/wiki/restricted/
```
- ✅ Prevents accidental commits to public repository
- ✅ Forces developers to use private repository

### Layer 2: Unix Permissions (Filesystem Protection)
```bash
# Internal directory (most sensitive)
chown -R root:synos-internal docs/wiki/internal/
chmod 750 docs/wiki/internal/
chmod 640 docs/wiki/internal/*.md

# Restricted directory (licensed access)
chown -R root:synos-licensed docs/wiki/restricted/
chmod 750 docs/wiki/restricted/
chmod 640 docs/wiki/restricted/*.md
```
- ✅ Only `synos-internal` group can read internal docs
- ✅ Only `synos-licensed` group can read restricted docs
- ✅ Root ownership prevents tampering

### Layer 3: Git-Crypt Encryption (Repository Protection)
```bash
# Install git-crypt
sudo apt install git-crypt

# Initialize encryption
cd /home/diablorain/Syn_OS
git-crypt init

# Add GPG key for team members
git-crypt add-gpg-user YOUR_GPG_KEY_ID
```
- ✅ Files encrypted in Git repository
- ✅ Automatic encryption/decryption on commit/checkout
- ✅ Only authorized GPG keys can decrypt

### Layer 4: GPG Encryption (File-Level Protection)
```bash
# Encrypt entire directory (backup)
tar czf - docs/wiki/internal/ | gpg -c > internal-docs.tar.gz.gpg

# Decrypt when needed
gpg -d internal-docs.tar.gz.gpg | tar xzf -
```
- ✅ Additional layer for backups
- ✅ Password-protected archives
- ✅ Can be stored separately

## 🔐 Setup Instructions

### For Repository Administrators

#### 1. Install Git-Crypt
```bash
sudo apt update
sudo apt install git-crypt gnupg
```

#### 2. Generate GPG Key (if needed)
```bash
gpg --full-generate-key
# Choose: RSA and RSA, 4096 bits, no expiration
# Enter: Your name and email
# Set a strong passphrase
```

#### 3. Initialize Git-Crypt in Repository
```bash
cd /home/diablorain/Syn_OS
git-crypt init

# Export your public key for team sharing
gpg --armor --export YOUR_EMAIL > synos-dev-public-key.asc
```

#### 4. Create Encryption Rules
Create `.gitattributes` files in sensitive directories (see below).

#### 5. Add Team Members' GPG Keys
```bash
# Team member shares their public key
gpg --import team-member-public-key.asc

# Add them to git-crypt
git-crypt add-gpg-user team-member@email.com
```

### For Team Members (Developer Access)

#### 1. Generate Your GPG Key
```bash
gpg --full-generate-key
# Share public key with admin: gpg --armor --export YOUR_EMAIL > your-key.asc
```

#### 2. Clone Repository
```bash
git clone git@github.com:TLimoges33/Syn_OS.git
cd Syn_OS
```

#### 3. Unlock Encrypted Files
```bash
# Admin must have added your GPG key first
git-crypt unlock
```

#### 4. Verify Access
```bash
# Check if files are decrypted
file docs/wiki/internal/README.md
# Should show: "ASCII text" not "data" or "GPG encrypted"
```

## 📋 Current Security Status

### Internal Directory (`docs/wiki/internal/`)
**Access Level:** 🔴 HIGHLY RESTRICTED  
**Unix Group:** `synos-internal`  
**Encryption:** Git-crypt + GPG  
**Contents:**
- AI Consciousness Engine (45KB)
- Custom Kernel Development (40KB)
- Security Framework (37KB)
- Kernel Development (16KB)
- Advanced Exploitation (14KB)
- Custom Tool Development (6.6KB)
- And 6 more files...

### Restricted Directory (`docs/wiki/restricted/`)
**Access Level:** 🟡 LICENSED ACCESS  
**Unix Group:** `synos-licensed`  
**Encryption:** Git-crypt + GPG  
**Contents:**
- Docker Guide (3.3KB)
- Kubernetes Deployment (2.9KB)
- Security Tools (4.4KB)
- Build System (2.2KB)
- And 5 more files...

## 🚨 Security Checklist

- [x] Unix permissions set (root:synos-internal, root:synos-licensed)
- [ ] Git-crypt installed and initialized
- [ ] .gitattributes encryption rules created
- [ ] GPG keys generated for team members
- [ ] Team members added to git-crypt
- [x] Directories added to .gitignore (public repo protection)
- [ ] Encrypted backups created
- [ ] Access audit log established

## 🔧 Maintenance

### Adding a New Developer
```bash
# 1. Get their GPG public key
gpg --import developer-key.asc

# 2. Add to git-crypt
git-crypt add-gpg-user developer@email.com

# 3. Add to Unix group (if on local system)
sudo usermod -aG synos-internal developer
```

### Removing a Developer
```bash
# 1. Remove from Unix group
sudo gpasswd -d developer synos-internal

# 2. Re-key git-crypt (requires re-adding all authorized users)
git-crypt init -f
# Re-add all remaining authorized users
```

### Creating Encrypted Backup
```bash
# Full encrypted backup
tar czf - docs/wiki/{internal,restricted}/ | \
  gpg --symmetric --cipher-algo AES256 \
  > synos-wiki-backup-$(date +%Y%m%d).tar.gz.gpg

# Verify backup
gpg -d synos-wiki-backup-*.tar.gz.gpg | tar tzf - | head
```

## 📞 Emergency Access

### Lost GPG Key
1. Contact repository administrator
2. Verify identity through secure channel
3. Generate new GPG key
4. Request re-addition to git-crypt

### Suspected Compromise
1. Immediately rotate all GPG keys
2. Re-encrypt all sensitive files
3. Audit Git history for unauthorized access
4. Review Unix group memberships

## 📚 References

- [Git-Crypt Documentation](https://github.com/AGWA/git-crypt)
- [GPG Handbook](https://www.gnupg.org/gph/en/manual.html)
- [SynOS Security Policy](../../08-security/SECURITY_POLICY.md)

## ⚖️ Legal Notice

The contents of `docs/wiki/internal/` and `docs/wiki/restricted/` are:
- **Proprietary and confidential**
- **Protected by copyright**
- **Subject to NDA agreements**
- **Export controlled**

Unauthorized access, use, or distribution is strictly prohibited and may result in legal action.

---

**For security questions:** security@synos.dev  
**For access requests:** admin@synos.dev
