# SynOS Quick Reference - Code Organization

**Last Updated:** October 23, 2025

## 📂 Where Does Code Go?

### ✅ Production Code → `src/<category>/`

Add to workspace in `Cargo.toml` immediately.

**Categories:**

-   `src/userspace/` - User applications
-   `src/ai/` - AI/ML components
-   `src/services/` - System daemons
-   `src/security/` - Security modules
-   `src/<feature>/` - Feature modules

### 🔬 Prototype Code → `src/experimental/`

NOT in workspace. Move fast, break things.

### 🔬 Research Code → `src/distributed/` or `src/ai/advanced/`

NOT in workspace. Cutting-edge, may not compile.

---

## 🔍 How to Find Code

| Looking For...     | Check Directory                         |
| ------------------ | --------------------------------------- |
| Kernel code        | `src/kernel/`                           |
| Shell/CLI          | `src/userspace/shell/`                  |
| AI inference       | `src/ai/runtime/`                       |
| AI scheduling      | `src/ai/engine/`                        |
| System services    | `src/services/`                         |
| Security analytics | `src/analytics/`                        |
| Threat detection   | `src/threat-hunting/`                   |
| Compliance checks  | `src/compliance-runner/`                |
| Cloud security     | `src/cloud-security/`                   |
| Training games     | `src/vm-wargames/`, `src/ctf-platform/` |
| Gamification       | `src/gamification/`                     |
| Mobile apps        | `src/mobile-bridge/`                    |

---

## 🛠️ Common Commands

### Build Everything

```bash
cargo build --workspace --release
```

### Build Kernel

```bash
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none --release
```

### Build Single Package

```bash
cargo build -p <package-name>
```

### Build ISO

```bash
./scripts/unified-iso-builder.sh
```

---

## 📚 Documentation

| Topic               | File                                        |
| ------------------- | ------------------------------------------- |
| Full architecture   | `src/ARCHITECTURE.md`                       |
| This reorganization | `docs/REORGANIZATION_SUMMARY_2025-10-23.md` |
| Distributed systems | `src/distributed/README.md`                 |
| Experimental code   | `src/experimental/README.md`                |
| Business metrics    | `src/executive-dashboard/README.md`         |

---

## 🚦 Code Maturity

-   🟢 **Production** - In workspace, tested, documented
-   🟡 **Experimental** - Compiles, not integrated, documented
-   🔴 **Research** - May not compile, cutting-edge

---

## ✅ Current Status (Oct 23, 2025)

-   **Production Packages:** 50+
-   **Build Status:** ✅ All passing (9m 31s)
-   **Experimental Areas:** 3 (documented)
-   **Research Areas:** 2 (documented)
-   **ISO Build Status:** ✅ Ready

---

**Quick Help:** See `src/ARCHITECTURE.md` for complete details
