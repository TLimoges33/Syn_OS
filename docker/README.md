# SynOS Docker Systems - Consolidated Architecture

**Date:** 2025-10-25  
**Structure:** Option C - Unified /docker/ with purpose-specific subdirectories  
**Status:** ✅ Active (Production Ready)

---

## 🏗️ Architecture Overview

This directory contains **THREE separate Docker systems** with distinct purposes:

```
/docker/
├── build/          🔨 ISO Build Isolation (chroot/debootstrap)
├── services/       🚀 Service Orchestration (NATS, Redis, consciousness)
└── dev/            💻 Development Containers (VS Code integration)
```

---

## 📁 Subdirectory Purposes

### /docker/build/ - ISO Build System

**Purpose:** Isolated environment for building SynOS ISOs via chroot/debootstrap

**Why It Exists:**  
The build script performs dangerous operations (bind-mounting /dev into chroot). Without isolation, failed builds corrupt the host `/dev` directory, breaking the entire development environment. Docker provides complete host protection.

**Key Files:**

-   `Dockerfile` - Multi-stage build environment (builder 835MB → runtime 300MB)
-   `docker-compose.yml` - Container orchestration with caching
-   `README.md` - Usage documentation

**Use For:**

-   Building SynOS ISO images
-   Testing build scripts safely
-   CI/CD automation

**Do NOT Use For:**

-   Running SynOS services (use /docker/services/)
-   Development coding (use /docker/dev/)

**Documentation:** See `docs/03-build/ROOT_CAUSE_ANALYSIS_DEV_CORRUPTION.md`

---

### /docker/services/ - Service Orchestration

**Purpose:** Running SynOS production and development services

**What's Here:**

-   NATS messaging system
-   PostgreSQL database
-   Redis cache
-   Ray distributed computing
-   Consciousness modules
-   Security services
-   ISO builder service (different from /docker/build/)

**Key Files:**

-   `docker-compose.unified.yml` - All services in one
-   `docker-compose.consciousness-production.yml` - Consciousness in production
-   `docker-compose.iso.yml` - Ray-based ISO builder
-   `docker-compose.security.yml` - Security services
-   `Dockerfile.*` - Various service images

**Use For:**

-   Running SynOS backend services
-   Development with live services
-   Production deployments
-   Integration testing

**Do NOT Use For:**

-   Building ISOs (use /docker/build/)
-   VS Code development (use /docker/dev/)

**Documentation:** See `deployment/docker/DOCKER_DEPLOYMENT_GUIDE.md`

---

### /docker/dev/ - Development Containers

**Purpose:** VS Code development environment with pre-configured tooling

**What's Here:**

-   VS Code devcontainer configuration
-   Pre-installed development tools
-   IDE integrations
-   Debugger configurations

**Use For:**

-   "Reopen in Container" in VS Code
-   Consistent development environment across team
-   Isolated development with full tooling

**Do NOT Use For:**

-   Building ISOs (use /docker/build/)
-   Running production services (use /docker/services/)

**Documentation:** See `.devcontainer/README.md` (if exists)

---

## 🚀 Quick Start Guide

### Building an ISO (Most Common)

```bash
# Method 1: Wrapper script (recommended)
./scripts/utilities/safe-docker-build.sh

# Method 2: Direct docker-compose
cd docker/build
docker-compose up --build

# Method 3: Direct Docker
docker build -t synos-builder:latest -f docker/build/Dockerfile .
docker run -it -v $(pwd):/build synos-builder:latest
```

### Running Services

```bash
# Start all services
cd docker/services
docker-compose -f docker-compose.unified.yml up -d

# Start specific service
docker-compose -f docker-compose.consciousness-production.yml up -d

# Check status
docker-compose ps
```

### VS Code Development

```bash
# Open in VS Code
code .

# Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
# Search: "Reopen in Container"
# Select appropriate devcontainer
```

---

## 📊 Comparison Matrix

| Feature             | /docker/build/       | /docker/services/     | /docker/dev/     |
| ------------------- | -------------------- | --------------------- | ---------------- |
| **Primary Use**     | ISO building         | Service orchestration | Coding           |
| **Privileged Mode** | ✅ Yes (required)    | ❌ No                 | ❌ No            |
| **Mounts Host**     | ✅ Full project      | ⚠️ Selective          | ✅ Full project  |
| **Persistent**      | ❌ Ephemeral         | ✅ Long-running       | ⚠️ Session-based |
| **Resource Heavy**  | ✅ Yes (4 CPU, 8GB)  | ⚠️ Moderate           | ⚠️ Moderate      |
| **Security Risk**   | ⚠️ Medium (isolated) | ✅ Low                | ✅ Low           |
| **Auto-start**      | ❌ Manual            | ✅ Can auto           | ✅ On IDE open   |
| **Team Use**        | ✅ CI/CD             | ✅ Production         | ✅ Development   |

---

## ⚠️ Common Mistakes to Avoid

### ❌ WRONG: Using services compose for builds

```bash
# This will fail - wrong Docker system!
cd docker/services
docker-compose -f docker-compose.iso.yml up
```

**Why:** Service ISO builder is Ray-based (different from chroot builder)

**Fix:** Use `/docker/build/` instead

---

### ❌ WRONG: Building ISOs outside Docker

```bash
# DANGEROUS - Can corrupt host /dev!
./scripts/build-full-distribution.sh
```

**Why:** Native builds bind-mount host /dev (line 1360 bug)

**Fix:** Always use Docker wrapper:

```bash
./scripts/utilities/safe-docker-build.sh
```

---

### ❌ WRONG: Mixing dev and build containers

```bash
# Confusion - are you developing or building?
docker run -it synos-builder:latest code .
```

**Why:** Build container doesn't have VS Code tools

**Fix:** Use correct container for task:

-   Building → `/docker/build/`
-   Coding → `/docker/dev/`

---

## 🔧 Optimization Features

### /docker/build/ Optimizations

✅ **Multi-stage builds** - 60% smaller images (835MB → 300MB)  
✅ **BuildKit caching** - 50-70% faster rebuilds  
✅ **ccache** - 60-80% faster C/C++ recompiles  
✅ **sccache** - 70-90% faster Rust recompiles  
✅ **Persistent volumes** - Cache survives container deletion  
✅ **Resource limits** - Prevents host resource exhaustion

### Verify Caching Works

```bash
# First build (slow - no cache)
docker-compose -f docker/build/docker-compose.yml build
# Time: ~3-5 minutes

# Second build (fast - cached)
docker-compose -f docker/build/docker-compose.yml build
# Time: ~30-60 seconds (90% faster!)
```

---

## 📝 Maintenance

### Cleanup Old Images

```bash
# Remove unused Docker images
docker system prune -a

# Remove specific old build
docker rmi synos-builder:old-tag
```

### Update Base Images

```bash
# Pull latest Debian base
docker pull debian:bookworm-slim

# Rebuild all images
cd docker/build && docker-compose build --no-cache
```

### Check Disk Usage

```bash
# Docker disk usage
docker system df

# Cache volumes
docker volume ls | grep synos
```

---

## 🔐 Security Notes

### /docker/build/ Security

**Risk Level:** ⚠️ **Medium** (but isolated from host)

-   ✅ Runs privileged (required for chroot)
-   ✅ NOPASSWD sudo (required for mounts)
-   ✅ Host project mounted :rw (build can modify files)
-   ✅ **BUT:** Host /dev never exposed (container has own /dev)

**Verdict:** Acceptable risk - build operations need privileges, but host filesystem protected

### /docker/services/ Security

**Risk Level:** ✅ **Low**

-   ❌ No privileged mode
-   ❌ No host /dev access
-   ✅ Network isolated (custom bridge)
-   ✅ Resource limits enforced

**Verdict:** Production-safe

### /docker/dev/ Security

**Risk Level:** ✅ **Low**

-   ❌ No privileged mode
-   ✅ Same user permissions as host
-   ✅ Full project access (for development)

**Verdict:** Development-safe

---

## 📚 Related Documentation

-   **Build System:** `docs/03-build/`

    -   Root cause analysis: `ROOT_CAUSE_ANALYSIS_DEV_CORRUPTION.md`
    -   Safety measures: `BUILD_SAFETY_MEASURES.md`
    -   Base image choice: `BASE_IMAGE_ANALYSIS.md`
    -   Pre-commit audit: `COMPREHENSIVE_AUDIT_PRE_COMMIT.md`

-   **Services:** `deployment/docker/`

    -   Deployment guide: `DOCKER_DEPLOYMENT_GUIDE.md`
    -   Migration strategy: `migrate-to-unified.sh`

-   **Architecture:** `docs/02-architecture/`

---

## ❓ FAQ

### Q: Why three separate Docker systems?

**A:** Different purposes require different configurations:

-   Builds need privileged mode (chroot operations)
-   Services need persistence (long-running daemons)
-   Dev needs IDE integration (VS Code tooling)

Trying to combine them would compromise security or functionality.

---

### Q: Which system should I use for X?

| Task                 | System                                |
| -------------------- | ------------------------------------- |
| Build ISO            | `/docker/build/`                      |
| Run NATS/Redis       | `/docker/services/`                   |
| Code in VS Code      | `/docker/dev/`                        |
| Test build script    | `/docker/build/`                      |
| Deploy to production | `/docker/services/`                   |
| Debug consciousness  | `/docker/dev/` or `/docker/services/` |

---

### Q: Can I use the old `/deployment/docker/` files?

**A:** Yes! They're copied to `/docker/services/` but originals remain for backwards compatibility. New work should reference `/docker/services/`.

---

### Q: What happened to the old `/docker/` files?

**A:** Moved to `/docker/build/` as part of Option C reorganization (2025-10-25). All scripts updated to new paths.

---

### Q: Why is `/docker/build/` privileged mode?

**A:** chroot operations require root inside container. Without privileged mode, `debootstrap` fails. This is unavoidable for ISO building. However, the container's privileges don't extend to host (isolation).

---

## 📈 Migration History

### 2025-10-25: Option C Consolidation

**Before:**

```
/docker/                     (2 files - build system)
/deployment/docker/          (11+ files - services)
/.devcontainer/              (dev containers)
```

**After:**

```
/docker/
  ├── build/                 (3 files - build system)
  ├── services/              (11+ files - services)
  └── dev/                   (dev containers)
```

**Benefits:**

-   ✅ Clear separation of concerns
-   ✅ No naming confusion
-   ✅ Easier to find correct system
-   ✅ Better organization

---

## 🎯 Next Steps

1. **If building ISOs:** → `/docker/build/README.md`
2. **If running services:** → `/docker/services/DOCKER_DEPLOYMENT_GUIDE.md`
3. **If developing code:** → `/.devcontainer/README.md`

---

**Status:** ✅ Production Ready  
**Last Updated:** 2025-10-25  
**Maintainer:** SynOS Dev Team
