# SynOS Wiki Security - Quick Reference

## 🔐 Security Setup (One-Time)

```bash
# Run the automated setup script
sudo ./scripts/setup-wiki-security.sh
```

This will:

-   ✅ Install git-crypt and GPG
-   ✅ Create Unix groups (synos-internal, synos-licensed)
-   ✅ Set proper file permissions
-   ✅ Initialize git-crypt encryption
-   ✅ Add your GPG key

## 👥 Adding Team Members

```bash
# 1. Team member generates GPG key
gpg --full-generate-key

# 2. Team member exports public key
gpg --armor --export their@email.com > team-member-key.asc

# 3. Admin imports and adds to git-crypt
gpg --import team-member-key.asc
git-crypt add-gpg-user their@email.com

# 4. Admin adds to Unix groups (if on local system)
sudo usermod -aG synos-internal team-member
sudo usermod -aG synos-licensed team-member
```

## 🔓 Accessing Encrypted Files

```bash
# Team member clones repository
git clone git@github.com:TLimoges33/Syn_OS.git
cd Syn_OS

# Unlock encrypted files (requires GPG key added by admin)
git-crypt unlock

# Verify decryption
file docs/wiki/internal/README.md
# Should show: "ASCII text" (not "data")
```

## 💾 Creating Backups

```bash
# Create encrypted backup
./scripts/wiki-backup.sh

# Backups saved to: ~/synos-backups/
```

## 🔓 Restoring from Backup

```bash
# Decrypt and extract
gpg -d ~/synos-backups/synos-wiki-all-20251022-*.tar.gz.gpg | tar xzf -
```

## ✅ Verifying Encryption Status

```bash
# Check which files are encrypted
git-crypt status

# Check specific file
git-crypt status docs/wiki/internal/README.md
```

## 🚨 Emergency: Lock Files

```bash
# Lock all encrypted files (requires re-unlock with GPG key)
git-crypt lock
```

## 📊 Current Access Levels

| Directory               | Unix Group       | Encryption | Access Level         |
| ----------------------- | ---------------- | ---------- | -------------------- |
| `docs/wiki/internal/`   | `synos-internal` | git-crypt  | 🔴 HIGHLY RESTRICTED |
| `docs/wiki/restricted/` | `synos-licensed` | git-crypt  | 🟡 LICENSED          |
| `docs/wiki/public/`     | world-readable   | none       | 🟢 PUBLIC            |

## 🛠️ Troubleshooting

### "binary data" when viewing files

**Problem:** Files show as binary instead of text  
**Solution:** Run `git-crypt unlock` to decrypt files

### Permission denied

**Problem:** Cannot access internal/ or restricted/  
**Solution:** Add user to appropriate Unix group:

```bash
sudo usermod -aG synos-internal $USER
# Log out and log back in for group to take effect
```

### git-crypt not working

**Problem:** Files not encrypting  
**Solution:** Check .gitattributes exists in directory:

```bash
ls -la docs/wiki/internal/.gitattributes
ls -la docs/wiki/restricted/.gitattributes
```

## 📚 Full Documentation

For complete details, see: [docs/wiki/SECURITY.md](SECURITY.md)

## 🔗 Quick Links

-   [Setup Script](../../scripts/setup-wiki-security.sh)
-   [Backup Script](../../scripts/wiki-backup.sh)
-   [Git-Crypt Documentation](https://github.com/AGWA/git-crypt)
-   [GPG Quick Start](https://www.gnupg.org/gph/en/manual/c14.html)
