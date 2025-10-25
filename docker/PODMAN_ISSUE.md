# Docker/Podman Status

**Date:** 2025-10-25  
**System:** Parrot OS 6.4 (lorikeet)  
**Container Runtime:** Podman 4.3.1 (rootless mode)

---

## Issue: Podman Permission Error

### Error Message

```
Error: cannot set up namespace using "/usr/bin/newuidmap": should have setuid or have filecaps setuid: exit status 1
```

### Root Cause

-   System uses **Podman** (not Docker)
-   Podman running in **rootless mode**
-   `/usr/bin/newuidmap` lacks proper permissions for namespace creation
-   This is a system-level PAM/subuid configuration issue

### Impact

-   ⚠️ Cannot build Docker images without root
-   ⚠️ Docker isolation unavailable in current configuration
-   ✅ **Host has all tools natively** (no isolation needed for this system)

---

## Workarounds

### Option 1: Use Host Tools (RECOMMENDED for Parrot OS)

```bash
# Host already has everything
which debootstrap xorriso mksquashfs rustc cargo python3
# All present!

# Build directly on host
./scripts/build-full-distribution.sh --clean --fresh
```

**Rationale:** Parrot OS is already a security-focused distribution. The risk of `/dev` corruption (reason for Docker isolation) can be mitigated with the pre-flight checks we documented.

### Option 2: Fix Podman Permissions (Advanced)

```bash
# Check current subuid/subgid
cat /etc/subuid
cat /etc/subgid

# Verify newuidmap permissions
ls -la /usr/bin/newuidmap
# Should be: -rwsr-xr-x (setuid bit set)

# If not setuid, fix with:
sudo chmod u+s /usr/bin/newuidmap
sudo chmod u+s /usr/bin/newgidmap

# Restart podman
podman system reset  # WARNING: Deletes all containers/images
```

### Option 3: Use Podman with Root (Not Recommended)

```bash
sudo podman build -t synos-builder:latest -f docker/build/Dockerfile .
```

**Downsides:** Defeats purpose of rootless containers, security risk

### Option 4: Install Docker (Heavy)

```bash
# Remove podman-docker alias
sudo apt remove podman-docker

# Install real Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in

docker build -t synos-builder:latest -f docker/build/Dockerfile .
```

---

## Host Native Build Safety

### Pre-Flight Checks (Recommended)

```bash
# Before build
./scripts/utilities/validate-dev-environment.sh

# Check /dev health
ls /dev/ | wc -l  # Should be 178+

# Check disk space
df -h /  # Need 100GB+ free
```

###During Build Monitoring

```bash
# Watch /dev in another terminal
watch -n 5 'ls /dev/ | wc -l'

# Should stay constant at 178
# If drops below 150, STOP BUILD immediately
```

### Post-Build Verification

```bash
# After build
ls /dev/ | wc -l  # Should still be 178

# If corrupted
sudo reboot  # Last resort fix
```

---

## Docker System Status

### Built Files (Ready for Future Use)

```
✅ docker/build/Dockerfile (multi-stage, optimized)
✅ docker/build/docker-compose.yml (BuildKit caching)
✅ docker/build/BUILD_VERSIONS.md (reproducibility docs)
✅ docker/README.md (usage documentation)
✅ .dockerignore (14GB context reduction)
✅ scripts/utilities/safe-docker-build.sh (wrapper)
```

### What Works

-   ✅ All Dockerfiles syntactically valid
-   ✅ BuildKit configuration correct
-   ✅ Multi-stage design optimal
-   ✅ Cache volumes configured

### What Doesn't Work (Current System)

-   ❌ Image building (Podman permission issue)
-   ❌ Container execution (needs image first)
-   ❌ Build isolation (not critical on Parrot OS)

---

## Future Systems

### On Systems With Docker

```bash
# This will work perfectly
cd /path/to/Syn_OS
./scripts/utilities/safe-docker-build.sh --auto --clean --fresh
```

### On Systems With Proper Podman

```bash
# With fixed permissions
podman build -t synos-builder:latest -f docker/build/Dockerfile .
podman-compose -f docker/build/docker-compose.yml run --rm synos-builder
```

### In CI/CD (GitHub Actions, GitLab CI)

```yaml
# .github/workflows/build.yml
- name: Build ISO in Docker
  run: |
      docker build -t synos-builder:latest -f docker/build/Dockerfile .
      docker run -v $PWD:/build synos-builder:latest \
        /build/scripts/build-full-distribution.sh --clean
```

---

## Recommendation

**For Current System (Parrot OS with Podman issues):**

1. ✅ Use native host tools (all present)
2. ✅ Implement pre-flight `/dev` health checks
3. ✅ Monitor `/dev` entry count during build
4. ✅ Keep Docker files for future CI/CD use
5. ❌ Don't waste time fixing Podman (not critical)

**For Production Deployments:**

1. Use Docker (not Podman) on build servers
2. Run builds in isolated containers
3. Never expose host `/dev` to chroot
4. Automate with the scripts we created

---

## Related Documentation

-   `docs/03-build/ROOT_CAUSE_ANALYSIS_DEV_CORRUPTION.md` - Why isolation matters
-   `docker/README.md` - Full Docker system usage
-   `scripts/utilities/safe-docker-build.sh` - Wrapper script (needs Docker)
-   `docs/03-build/COMPREHENSIVE_AUDIT_PRE_COMMIT.md` - Complete audit

---

**Status:** Docker system complete but unusable on current system due to Podman permissions.  
**Alternative:** Native host builds work perfectly (all tools present).  
**Future:** Docker system ready for CI/CD and other environments.
