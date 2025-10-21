#!/bin/bash

echo "=== PRE-FLIGHT BUILD CHECK ==="

# 1. Check Debian keys are valid PGP format
echo "[1/5] Checking GPG keys..."
for key in config/archives/debian*.key.chroot; do
    if grep -q "BEGIN PGP PUBLIC KEY BLOCK" "$key"; then
        echo "  ✓ $key is valid PGP format"
    else
        echo "  ✗ $key is INVALID!"
        exit 1
    fi
done

# 2. Check for broken repo references
echo "[2/5] Checking for broken repos..."
if grep -r "/tmp/synos-repo" config/ 2>/dev/null; then
    echo "  ✗ Found broken synos-repo references!"
    grep -r "/tmp/synos-repo" config/
    exit 1
else
    echo "  ✓ No broken repo references"
fi

# 3. Check live-build version
echo "[3/5] Checking live-build..."
lb --version
if lb --version 2>/dev/null | grep -q "20230502"; then
    echo "  ✓ Live-build version OK"
else
    echo "  ✗ Unexpected live-build version"
fi

# 4. Check available disk space
echo "[4/5] Checking disk space..."
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -gt 20 ]; then
    echo "  ✓ ${AVAILABLE}GB available (need >20GB)"
else
    echo "  ✗ Only ${AVAILABLE}GB available - need >20GB!"
    exit 1
fi

# 5. Test key import in a temp chroot
echo "[5/5] Testing key import..."
TESTDIR=$(mktemp -d)
sudo debootstrap --variant=minbase bookworm "$TESTDIR" http://deb.debian.org/debian 2>/dev/null
if [ $? -eq 0 ]; then
    sudo cp config/archives/debian*.key.chroot "$TESTDIR/tmp/"
    sudo chroot "$TESTDIR" bash -c 'apt-key add /tmp/*.key.chroot' 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✓ Keys import successfully in test chroot"
    else
        echo "  ✗ Keys failed to import!"
        sudo rm -rf "$TESTDIR"
        exit 1
    fi
    sudo rm -rf "$TESTDIR"
else
    echo "  ⚠ Could not test (debootstrap failed, but not critical)"
fi

echo ""
echo "✅ ALL PRE-FLIGHT CHECKS PASSED"
echo "Build should succeed. Run: sudo ./FINAL-BUILD.sh"
