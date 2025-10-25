#!/bin/bash
#
# SynOS - NUCLEAR OPTION: Install EVERYTHING
# No excuses. Build from source if needed.
# ParrotOS + Kali + BlackArch + Google Tools + Everything
#

set -e

CHROOT_PATH="${1:-/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot}"

if [ ! -d "$CHROOT_PATH" ]; then
    echo "❌ Chroot not found: $CHROOT_PATH"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NUCLEAR INSTALLATION: EVERYTHING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Target: $CHROOT_PATH"
echo "Strategy: Install from repos, build from source, whatever it takes"
echo ""

# ============================================================================
# PHASE 1: FIX SYSTEMD & DEPENDENCIES (Required for everything)
# ============================================================================

echo "[1/10] Fixing systemd and core dependencies..."

chroot "$CHROOT_PATH" /bin/bash -c "
    # Create machine-id (required for systemd)
    if [ ! -f /etc/machine-id ]; then
        dbus-uuidgen > /etc/machine-id || echo 'dummy-machine-id-for-chroot' > /etc/machine-id
    fi

    # Fix systemd
    export DEBIAN_FRONTEND=noninteractive
    dpkg --configure -a 2>/dev/null || true
    apt-get install -f -y 2>/dev/null || true
"

echo "✓ Core dependencies prepared"

# ============================================================================
# PHASE 2: ADD ALL REPOS (ParrotOS, Kali, BlackArch via AUR helper)
# ============================================================================

echo ""
echo "[2/10] Adding ALL security distribution repositories..."

# Kali repos (already added, but ensure complete)
chroot "$CHROOT_PATH" /bin/bash -c "
    # Ensure all Kali components
    if ! grep -q 'deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware' /etc/apt/sources.list.d/kali.list 2>/dev/null; then
        echo 'deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware' > /etc/apt/sources.list.d/kali.list
    fi
"

# ParrotOS repos (Security edition)
chroot "$CHROOT_PATH" /bin/bash -c "
    # Add ParrotOS Security repository
    if [ ! -f /etc/apt/sources.list.d/parrot.list ]; then
        echo 'deb https://deb.parrot.sh/parrot/ parrot main contrib non-free non-free-firmware' > /etc/apt/sources.list.d/parrot.list

        # Import ParrotOS GPG key
        wget -qO - https://deb.parrot.sh/parrot/misc/parrotsec.gpg | apt-key add - 2>/dev/null || true

        # Alternative: Download key file
        mkdir -p /etc/apt/trusted.gpg.d/
        wget -q https://deb.parrot.sh/parrot/misc/parrotsec.gpg -O /etc/apt/trusted.gpg.d/parrot.gpg 2>/dev/null || true
    fi
"

# BlackArch - We'll install tools directly from GitHub mirrors
echo "✓ Kali repos configured"
echo "✓ ParrotOS repos configured"
echo "✓ BlackArch tools will be installed from source"

# ============================================================================
# PHASE 3: UPDATE PACKAGE LISTS
# ============================================================================

echo ""
echo "[3/10] Updating package lists from all sources..."

chroot "$CHROOT_PATH" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive
    apt-get update 2>&1 | grep -E '(Hit|Get|Fetched|Reading)' || true
"

echo "✓ Package lists updated"

# ============================================================================
# PHASE 4: INSTALL BUILD DEPENDENCIES (for compiling from source)
# ============================================================================

echo ""
echo "[4/10] Installing build tools and dependencies..."

chroot "$CHROOT_PATH" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive

    # Essential build tools
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        curl \
        ca-certificates \
        pkg-config \
        autoconf \
        automake \
        libtool \
        make \
        gcc \
        g++ \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        ruby-dev \
        golang-go \
        cargo \
        rustc \
        2>&1 | grep -v 'WARNING' || true
"

echo "✓ Build tools installed"

# ============================================================================
# PHASE 5: WIRESHARK (Build from source if needed)
# ============================================================================

echo ""
echo "[5/10] Installing Wireshark (NUCLEAR MODE)..."

chroot "$CHROOT_PATH" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive

    # Try repository installation first
    echo '→ Attempting repository installation...'
    apt-get install -y wireshark tshark 2>&1 | tail -20 || {
        echo '→ Repository failed, building from source...'

        # Install Wireshark dependencies
        apt-get install -y \
            libglib2.0-dev \
            libpcap-dev \
            qtbase5-dev \
            qttools5-dev \
            qtmultimedia5-dev \
            libqt5svg5-dev \
            ninja-build \
            2>&1 | grep -v 'WARNING' || true

        # Build Wireshark from source
        cd /tmp
        wget -q https://www.wireshark.org/download/src/wireshark-4.2.0.tar.xz || \
        git clone --depth 1 https://github.com/wireshark/wireshark.git

        if [ -f wireshark-4.2.0.tar.xz ]; then
            tar xf wireshark-4.2.0.tar.xz
            cd wireshark-4.2.0
        else
            cd wireshark
        fi

        mkdir -p build && cd build
        cmake -G Ninja ..
        ninja
        ninja install
        ldconfig

        cd /tmp
        rm -rf wireshark*

        echo '✓ Wireshark built from source'
    }

    # Verify installation
    if which wireshark >/dev/null 2>&1 || which tshark >/dev/null 2>&1; then
        echo '✓ Wireshark installation verified'
    else
        echo '⚠ Wireshark not available, continuing...'
    fi
"

# ============================================================================
# PHASE 6: METASPLOIT (Build from source)
# ============================================================================

echo ""
echo "[6/10] Installing Metasploit Framework (NUCLEAR MODE)..."

chroot "$CHROOT_PATH" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive

    # Try repository first
    echo '→ Attempting repository installation...'
    apt-get install -y metasploit-framework 2>&1 | tail -20 || {
        echo '→ Repository failed, building from source...'

        # Install Metasploit dependencies
        apt-get install -y \
            ruby \
            ruby-dev \
            libpq-dev \
            postgresql \
            postgresql-client \
            build-essential \
            libpcap-dev \
            libsqlite3-dev \
            libreadline-dev \
            libssl-dev \
            libpq-dev \
            2>&1 | grep -v 'WARNING' || true

        # Clone Metasploit
        cd /opt
        if [ ! -d metasploit-framework ]; then
            git clone --depth 1 https://github.com/rapid7/metasploit-framework.git
        fi

        cd metasploit-framework

        # Install Ruby gems
        gem install bundler:2.4.22
        bundle install

        # Create symlinks
        ln -sf /opt/metasploit-framework/msfconsole /usr/local/bin/msfconsole
        ln -sf /opt/metasploit-framework/msfvenom /usr/local/bin/msfvenom
        ln -sf /opt/metasploit-framework/msfd /usr/local/bin/msfd
        ln -sf /opt/metasploit-framework/msfrpc /usr/local/bin/msfrpc
        ln -sf /opt/metasploit-framework/msfdb /usr/local/bin/msfdb

        echo '✓ Metasploit built from source'
    }

    # Verify installation
    if which msfconsole >/dev/null 2>&1; then
        echo '✓ Metasploit installation verified'
    else
        echo '⚠ Metasploit not available, continuing...'
    fi
"

# ============================================================================
# PHASE 7: PARROT OS METAPACKAGES
# ============================================================================

echo ""
echo "[7/10] Installing ParrotOS metapackages..."

chroot "$CHROOT_PATH" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive

    # Try to install ParrotOS metapackages
    echo '→ Installing Parrot Security tools...'

    # Core Parrot tools
    for pkg in \
        parrot-tools-cloud \
        parrot-tools-crypto \
        parrot-tools-exploit \
        parrot-tools-forensics \
        parrot-tools-mobile \
        parrot-tools-password \
        parrot-tools-postexploit \
        parrot-tools-sniff \
        parrot-tools-web \
        parrot-tools-wifi \
        anonsurf \
        wifiphisher \
        beef-xss \
        ettercap-graphical \
        bettercap
    do
        echo \"  → Installing \$pkg...\"
        apt-get install -y \$pkg 2>&1 | tail -5 || echo \"  ⚠ \$pkg not available\"
    done
"

echo "✓ ParrotOS tools installation attempted"

# ============================================================================
# PHASE 8: KALI METAPACKAGES (EVERYTHING)
# ============================================================================

echo ""
echo "[8/10] Installing Kali Linux metapackages (THE FULL ARSENAL)..."

chroot "$CHROOT_PATH" /bin/bash -c "
    export DEBIAN_FRONTEND=noninteractive

    echo '→ Installing Kali metapackages...'

    # Kali metapackages (install ALL categories)
    for pkg in \
        kali-tools-information-gathering \
        kali-tools-vulnerability \
        kali-tools-web \
        kali-tools-passwords \
        kali-tools-wireless \
        kali-tools-reverse-engineering \
        kali-tools-exploitation \
        kali-tools-social-engineering \
        kali-tools-sniffing-spoofing \
        kali-tools-post-exploitation \
        kali-tools-forensics \
        kali-tools-reporting \
        kali-linux-core
    do
        echo \"  → Installing \$pkg...\"
        apt-get install -y \$pkg 2>&1 | tail -5 || echo \"  ⚠ \$pkg not available\"
    done
"

echo "✓ Kali tools installation attempted"

# ============================================================================
# PHASE 9: BLACKARCH TOOLS (From GitHub mirrors)
# ============================================================================

echo ""
echo "[9/10] Installing BlackArch tools from source..."

chroot "$CHROOT_PATH" /bin/bash -c "
    # Create BlackArch tools directory
    mkdir -p /opt/blackarch
    cd /opt/blackarch

    # Clone popular BlackArch tools not in other repos
    echo '→ Installing BlackArch exclusives...'

    # List of unique BlackArch tools
    declare -a BLACKARCH_TOOLS=(
        'https://github.com/injectexp/firebird::firebird'
        'https://github.com/1N3/Sn1per::sn1per'
        'https://github.com/s0md3v/XSStrike::xsstrike'
        'https://github.com/sqlmapproject/sqlmap::sqlmap'
    )

    for entry in \"\${BLACKARCH_TOOLS[@]}\"; do
        url=\$(echo \$entry | cut -d: -f1,2,3)
        name=\$(echo \$entry | cut -d: -f4)

        if [ ! -d \"\$name\" ]; then
            echo \"  → Cloning \$name...\"
            git clone --depth 1 \$url \$name 2>&1 | tail -3 || true
        fi
    done
"

echo "✓ BlackArch tools installed"

# ============================================================================
# PHASE 10: GOOGLE PROJECT ZERO & SECURITY TOOLS
# ============================================================================

echo ""
echo "[10/10] Installing Google security tools..."

chroot "$CHROOT_PATH" /bin/bash -c "
    mkdir -p /opt/google-tools
    cd /opt/google-tools

    echo '→ Installing Google Project Zero tools...'

    # Google tools
    declare -a GOOGLE_TOOLS=(
        'https://github.com/google/sanitizers::sanitizers'
        'https://github.com/google/oss-fuzz::oss-fuzz'
        'https://github.com/google/syzkaller::syzkaller'
        'https://github.com/google/honggfuzz::honggfuzz'
        'https://github.com/google/tsunami-security-scanner::tsunami'
        'https://github.com/googleprojectzero/fuzzilli::fuzzilli'
        'https://github.com/google/gvisor::gvisor'
        'https://github.com/google/clusterfuzz::clusterfuzz'
    )

    for entry in \"\${GOOGLE_TOOLS[@]}\"; do
        url=\$(echo \$entry | cut -d: -f1,2,3)
        name=\$(echo \$entry | cut -d: -f4)

        if [ ! -d \"\$name\" ]; then
            echo \"  → Cloning \$name...\"
            git clone --depth 1 \$url \$name 2>&1 | tail -3 || true
        fi
    done

    # Build honggfuzz (powerful fuzzer)
    if [ -d honggfuzz ]; then
        cd honggfuzz
        make -j\$(nproc) 2>&1 | tail -10 || true
        ln -sf /opt/google-tools/honggfuzz/honggfuzz /usr/local/bin/honggfuzz || true
        cd ..
    fi
"

echo "✓ Google tools installed"

# ============================================================================
# VERIFICATION
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

chroot "$CHROOT_PATH" /bin/bash -c "
    echo '[Priority Targets]'
    for tool in wireshark tshark msfconsole msfvenom; do
        if which \$tool >/dev/null 2>&1; then
            echo \"✓ \$tool: \$(which \$tool)\"
        else
            echo \"✗ \$tool: NOT FOUND\"
        fi
    done

    echo ''
    echo '[Tool Count]'
    echo \"Binaries in /usr/bin: \$(ls /usr/bin | wc -l)\"
    echo \"Binaries in /usr/sbin: \$(ls /usr/sbin | wc -l)\"
    echo \"Tools in /opt: \$(ls -1 /opt 2>/dev/null | wc -l)\"

    echo ''
    echo '[Chroot Size]'
    du -sh / 2>/dev/null | head -1
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ NUCLEAR INSTALLATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next: Check if Wireshark and Metasploit are now available."
echo "If not, we'll build them manually with custom compilation flags."
echo ""
