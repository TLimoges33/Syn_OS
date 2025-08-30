# 🚀 Syn_OS Codespace Onboarding Checklist

Welcome to Syn_OS! This checklist will help you get started in a secure, high-performance Codespace environment.

---

## 1. Create Your Codespace
```
gh codespace create --repo TLimoges33/Syn_OS
# Recommended: 16 cores, 64 GB RAM, 128 GB storage
```

## 2. Wait for Auto-Setup (3-8 minutes)
- All tools, extensions, and permissions are configured automatically.

## 3. Initialize Your Environment
```
source ~/.bashrc
validate-env
```
- Ensures all tools (Rust, Python, Go, Node, security tools) are available.

## 4. Quick Test
```
new-rust-project test-project
cd test-project
cargo check
```
- Verifies Rust toolchain and workspace setup.

## 5. Development Workflow
- Use `rw` for Rust watch mode.
- Run `security-scan` for a full security audit.
- Use aliases: `rs` (run), `rb` (build), `rt` (test), `rc` (quick check), `audit` (security scan), `gs` (git status).

## 6. Troubleshooting
If any command fails:
```
bash .devcontainer/codespace-setup.sh
source ~/.bashrc
validate-env
```

## 7. Documentation
- See `docs/02-user-guides/quick-start.md` and `README.md` for full guides.
- Linked docs cover architecture, deployment, and security.

---

**You are now ready for advanced OS development in Syn_OS!**
