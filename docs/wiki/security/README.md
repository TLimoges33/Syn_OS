# 🔐 Security & Access Control

**Documentation encryption, access control, and security policies**

---

## 📚 Security Documentation

### Main Security Guides

- **[SECURITY.md](SECURITY.md)** - Comprehensive security guide (300+ lines)
  - 4-layer security architecture
  - Administrator setup instructions
  - Team member access procedures
  - Maintenance and emergency protocols
  - Current status of protected documentation

- **[SECURITY-QUICK-REF.md](SECURITY-QUICK-REF.md)** - Quick reference
  - Common commands
  - Troubleshooting guide
  - Access level table
  - Quick setup steps

---

## 🔒 4-Layer Security Architecture

### Layer 1: Unix Permissions
- `root:synos-internal` group (750/640) - Internal docs
- `root:synos-licensed` group (750/640) - Restricted docs
- Filesystem-level access control

### Layer 2: Git-Crypt Encryption
- Automatic encryption on Git commit
- Automatic decryption on authorized checkout
- GPG key-based authorization

### Layer 3: .gitattributes Rules
- Auto-encrypt all file types in sensitive directories
- Transparent encryption/decryption
- Applied to internal/ and restricted/ directories

### Layer 4: .gitignore Protection
- Prevents accidental commit of backup files
- Excludes GPG private keys
- Documented usage patterns

---

## 📁 Protected Directories

### 🔴 Internal (Highly Restricted)
**Location:** `../internal/`  
**Files:** 13 files (~187KB)  
**Access:** Internal employees and contractors (NDA required)  
**Encryption:** Git-crypt + GPG keys  
**Unix Group:** `synos-internal`

**Contains:**
- AI Consciousness Engine implementation
- Custom Kernel internals
- Security Framework architecture
- MSSP operations guide
- Production deployment details
- Advanced exploitation techniques

### 🟡 Restricted (Licensed Users)
**Location:** `../restricted/`  
**Files:** 9 files (~30KB)  
**Access:** Professional and Enterprise license holders  
**Encryption:** Git-crypt + GPG keys  
**Unix Group:** `synos-licensed`

**Contains:**
- Docker deployment guide
- Kubernetes deployment guide
- Complete security tools catalog (500+ tools)
- Build system details
- Testing framework
- Error code reference

---

## 🚀 Quick Start

### For Administrators

**One-command setup:**
```bash
sudo ./scripts/setup-wiki-security.sh
```

This script:
1. Installs git-crypt and GPG
2. Creates Unix groups
3. Sets file permissions
4. Initializes git-crypt
5. Adds your GPG key
6. Verifies setup

### For Team Members

**Request access:**
1. Generate GPG key pair
2. Send public key to administrator
3. Administrator adds your key:
   ```bash
   gpg --import team-member-key.asc
   git-crypt add-gpg-user team-member@email.com
   ```
4. Clone and unlock repository:
   ```bash
   git clone git@github.com:TLimoges33/Syn_OS.git
   cd Syn_OS
   git-crypt unlock
   ```

---

## 🛠️ Maintenance

### Backup Protected Documentation

**Automated backup script:**
```bash
./scripts/wiki-backup.sh
```

Creates encrypted backups:
- `~/synos-backups/synos-wiki-internal-DATE.tar.gz.gpg`
- `~/synos-backups/synos-wiki-restricted-DATE.tar.gz.gpg`
- `~/synos-backups/synos-wiki-all-DATE.tar.gz.gpg`

**Encryption:** AES-256 via GPG symmetric encryption

### Verify Encryption Status

```bash
# Check overall git-crypt status
git-crypt status

# Check specific file
git-crypt status docs/wiki/internal/README.md

# List all encrypted files
git-crypt status -e
```

---

## 🔐 Access Levels

| Directory | Unix Group | Encryption | Access Level |
|-----------|-----------|------------|--------------|
| `docs/wiki/internal/` | `synos-internal` | Git-crypt + GPG | 🔴 HIGHLY RESTRICTED |
| `docs/wiki/restricted/` | `synos-licensed` | Git-crypt + GPG | 🟡 LICENSED |
| `docs/wiki/` (root) | public | None | 🟢 PUBLIC |
| `docs/wiki/public/` | public | None | 🟢 PUBLIC |

---

## 🆘 Troubleshooting

### Files appear as binary/garbage

**Problem:** Files are encrypted (git-crypt locked)  
**Solution:** Run `git-crypt unlock`

### "Permission denied" when accessing files

**Problem:** Not in required Unix group  
**Solution:** Administrator must add you:
```bash
sudo usermod -aG synos-internal username
sudo usermod -aG synos-licensed username
```

### git-crypt not working

**Problem:** Git-crypt not initialized or GPG key not added  
**Solution:** Run setup script or manually:
```bash
git-crypt init
git-crypt add-gpg-user your-email@example.com
```

---

## 📊 Current Protection Status

### Protected Content

**Internal Documentation:**
- 13 files, ~187KB total
- All files encrypted with git-crypt
- Unix permissions: 750/640 (root:synos-internal)
- GPG keys required for access

**Restricted Documentation:**
- 9 files, ~30KB total
- All files encrypted with git-crypt
- Unix permissions: 750/640 (root:synos-licensed)
- Licensed access required

### Encryption Status
✅ Git-crypt initialized  
✅ .gitattributes rules configured  
✅ Unix permissions set  
✅ Backup automation configured  
✅ Documentation complete

---

## 📞 Security Contact

### Report Security Issues
- **Vulnerability Reports:** See [SECURITY.md](https://github.com/TLimoges33/Syn_OS/blob/master/SECURITY.md)
- **Access Issues:** Contact your team lead or IT administrator
- **Documentation Issues:** [GitHub Issues](https://github.com/TLimoges33/Syn_OS/issues)

### Request Access
- **Internal Access:** HR/Management approval required
- **Licensed Access:** Purchase Professional or Enterprise license at https://synos.com/pricing

---

## 📚 Additional Resources

- **[Main Wiki](../README.md)** - Complete documentation index
- **[Recent Updates](../RECENT_UPDATES.md)** - Latest changes and improvements
- **[Technical Docs](../technical/)** - System architecture
- **[Git-Crypt Documentation](https://github.com/AGWA/git-crypt)** - Upstream project

---

**Your documentation is protected with enterprise-grade encryption!** 🔐
