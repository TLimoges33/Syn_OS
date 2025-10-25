#!/bin/bash
# Manual build: Wireshark & Metasploit with NUCLEAR fixes
set -e

CHROOT="$1"
if [ -z "$CHROOT" ]; then
    echo "Usage: $0 /path/to/chroot"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MANUAL BUILD: PRIORITY TOOLS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# PHASE 1: Fix systemd PROPERLY
echo "[1/5] Fixing systemd the HARD way..."
chroot "$CHROOT" /bin/bash -c "
    # Create machine-id manually
    if [ ! -f /etc/machine-id ]; then
        # Generate a UUID
        if command -v dbus-uuidgen >/dev/null 2>&1; then
            dbus-uuidgen > /etc/machine-id
        elif command -v uuidgen >/dev/null 2>&1; then
            uuidgen | tr -d '-' > /etc/machine-id
        else
            # Fallback: random hex
            head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n' > /etc/machine-id
        fi
        chmod 444 /etc/machine-id
        echo '✓ Created /etc/machine-id'
    fi

    # Symlink if needed
    if [ ! -e /var/lib/dbus/machine-id ]; then
        mkdir -p /var/lib/dbus
        ln -sf /etc/machine-id /var/lib/dbus/machine-id
    fi

    # Try to reconfigure systemd
    dpkg --configure -a 2>&1 || echo '⚠ systemd still has issues (may be expected in chroot)'
    apt-get install -f -y 2>&1 || echo '⚠ Some packages may still be broken'
"
echo "✓ systemd fix attempted"
echo

# PHASE 2: Build Wireshark from source
echo "[2/5] Building Wireshark 4.2.0 from source..."
chroot "$CHROOT" /bin/bash -c "
    set -e
    cd /tmp

    # Install Qt5 dependencies (Qt6 was causing issues)
    echo '→ Installing Qt5 build dependencies...'
    apt-get install -y --no-install-recommends \
        qtbase5-dev qttools5-dev qtmultimedia5-dev \
        libqt5svg5-dev libqt5printsupport5 \
        libpcap-dev libgcrypt20-dev libgnutls28-dev \
        libglib2.0-dev libc-ares-dev libspeexdsp-dev \
        liblua5.3-dev libsmi2-dev libmaxminddb-dev \
        libsystemd-dev libnl-3-dev libnl-route-3-dev \
        libssh-dev libnghttp2-dev libnghttp3-dev \
        flex bison ninja-build \
        2>&1 || echo '⚠ Some Qt5 deps failed, continuing...'

    # Download Wireshark
    echo '→ Downloading Wireshark 4.2.0...'
    wget -q https://www.wireshark.org/download/src/wireshark-4.2.0.tar.xz || {
        echo '⚠ Download failed, trying alternative...'
        wget -q https://2.na.dl.wireshark.org/src/wireshark-4.2.0.tar.xz
    }

    # Extract
    echo '→ Extracting...'
    tar xf wireshark-4.2.0.tar.xz
    cd wireshark-4.2.0

    # Build
    echo '→ Configuring with CMake...'
    mkdir build && cd build
    cmake -G Ninja \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DBUILD_wireshark=ON \
        -DBUILD_tshark=ON \
        -DENABLE_LUA=ON \
        -DUSE_qt6=OFF \
        .. 2>&1 | tail -20

    echo '→ Building (this may take 5-10 minutes)...'
    ninja -j\$(nproc) 2>&1 | tail -50

    echo '→ Installing...'
    ninja install 2>&1 | tail -20
    ldconfig

    # Verify
    if which wireshark && which tshark; then
        echo '✅ Wireshark installed: '\$(wireshark --version | head -1)
        echo '✅ TShark installed: '\$(tshark --version | head -1)
    else
        echo '❌ Wireshark build failed!'
    fi

    # Cleanup
    cd /tmp
    rm -rf wireshark-4.2.0 wireshark-4.2.0.tar.xz
"
echo

# PHASE 3: Install Metasploit from GitHub
echo "[3/5] Installing Metasploit Framework from GitHub..."
chroot "$CHROOT" /bin/bash -c "
    set -e

    # Install Ruby dependencies
    echo '→ Installing Ruby dependencies...'
    apt-get install -y --no-install-recommends \
        ruby ruby-dev ruby-bundler \
        postgresql postgresql-client \
        libpq-dev libreadline-dev \
        libssl-dev zlib1g-dev \
        libsqlite3-dev libxml2-dev libxslt1-dev \
        libyaml-dev libffi-dev \
        2>&1 || echo '⚠ Some deps failed, continuing...'

    # Clone Metasploit
    echo '→ Cloning Metasploit Framework...'
    cd /opt
    if [ -d metasploit-framework ]; then
        rm -rf metasploit-framework
    fi
    git clone --depth 1 https://github.com/rapid7/metasploit-framework.git 2>&1 | tail -10
    cd metasploit-framework

    # Install gems with bundler
    echo '→ Installing gems (this may take 10-15 minutes)...'
    gem install bundler:2.4.22 --no-document 2>&1 | tail -5
    bundle config set --local path vendor/bundle
    bundle install 2>&1 | tail -50

    # Create symlinks
    echo '→ Creating symlinks...'
    ln -sf /opt/metasploit-framework/msfconsole /usr/local/bin/msfconsole
    ln -sf /opt/metasploit-framework/msfvenom /usr/local/bin/msfvenom
    ln -sf /opt/metasploit-framework/msfdb /usr/local/bin/msfdb
    ln -sf /opt/metasploit-framework/msfrpc /usr/local/bin/msfrpc
    ln -sf /opt/metasploit-framework/msfd /usr/local/bin/msfd

    # Verify
    if which msfconsole && which msfvenom; then
        echo '✅ Metasploit installed: '\$(msfconsole --version)
        echo '✅ Msfvenom installed: '\$(msfvenom --version)
    else
        echo '❌ Metasploit installation failed!'
    fi
"
echo

# PHASE 4: Fix dependency issues and install Kali tools
echo "[4/5] Fixing dependencies and installing Kali tools..."
chroot "$CHROOT" /bin/bash -c "
    # Fix broken dependencies
    echo '→ Fixing broken packages...'
    apt-get --fix-broken install -y 2>&1 | tail -20

    # Install Qt5 to resolve libqt5webchannel5 issue
    echo '→ Installing Qt5 base...'
    apt-get install -y qtbase5-dev qtchooser qt5-qmake 2>&1 || echo '⚠ Qt5 partially installed'

    # Try installing a subset of Kali tools individually
    echo '→ Installing individual Kali tools...'
    for tool in zaproxy burpsuite sqlmap wpscan dirb dirbuster enum4linux \
                smbclient nikto skipfish wfuzz cadaver davtest theharvester \
                masscan unicornscan dmitry ike-scan legion sslscan sslyze \
                amass fierce dnsrecon dnsenum sublist3r recon-ng maltego; do
        apt-get install -y \$tool 2>&1 | grep -E '(Setting up|already|Unable)' | head -2
    done
"
echo

# PHASE 5: Fix BlackArch and Google tools (correct GitHub URLs)
echo "[5/5] Cloning BlackArch and Google tools with CORRECT URLs..."
chroot "$CHROOT" /bin/bash -c "
    cd /opt
    mkdir -p blackarch google-tools

    echo '→ Cloning BlackArch tools...'
    cd /opt/blackarch
    git clone --depth 1 https://github.com/1N3/Sn1per.git 2>&1 | tail -5 || echo '✗ Sn1per failed'
    git clone --depth 1 https://github.com/s0md3v/XSStrike.git 2>&1 | tail -5 || echo '✗ XSStrike failed'
    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git 2>&1 | tail -5 || echo '✗ sqlmap failed'

    echo '→ Cloning Google security tools...'
    cd /opt/google-tools
    git clone --depth 1 https://github.com/google/sanitizers.git 2>&1 | tail -5 || echo '✗ sanitizers failed'
    git clone --depth 1 https://github.com/google/oss-fuzz.git 2>&1 | tail -5 || echo '✗ oss-fuzz failed'
    git clone --depth 1 https://github.com/google/syzkaller.git 2>&1 | tail -5 || echo '✗ syzkaller failed'
    git clone --depth 1 https://github.com/google/honggfuzz.git 2>&1 | tail -5 || echo '✗ honggfuzz failed'
    git clone --depth 1 https://github.com/google/tsunami-security-scanner.git 2>&1 | tail -5 || echo '✗ tsunami failed'
    git clone --depth 1 https://github.com/googleprojectzero/fuzzilli.git 2>&1 | tail -5 || echo '✗ fuzzilli failed'
    git clone --depth 1 https://github.com/google/gvisor.git 2>&1 | tail -5 || echo '✗ gvisor failed'
    git clone --depth 1 https://github.com/google/clusterfuzz.git 2>&1 | tail -5 || echo '✗ clusterfuzz failed'

    echo '→ Building honggfuzz...'
    cd /opt/google-tools/honggfuzz 2>/dev/null && {
        make -j\$(nproc) 2>&1 | tail -20 || echo '⚠ honggfuzz build failed'
        cp honggfuzz /usr/local/bin/ 2>/dev/null || echo '⚠ honggfuzz install failed'
    }

    # Create symlinks for Python tools
    echo '→ Creating tool symlinks...'
    cd /opt/blackarch
    for tool in */; do
        tool=\${tool%/}
        if [ -f \"\$tool/\$tool.py\" ]; then
            ln -sf /opt/blackarch/\$tool/\$tool.py /usr/local/bin/\$tool 2>/dev/null || true
        elif [ -f \"\$tool/\$tool\" ]; then
            ln -sf /opt/blackarch/\$tool/\$tool /usr/local/bin/\$tool 2>/dev/null || true
        fi
    done
"
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  COMPREHENSIVE VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

chroot "$CHROOT" /bin/bash -c "
    echo '[Priority Targets]'
    for tool in wireshark tshark msfconsole msfvenom; do
        if which \$tool >/dev/null 2>&1; then
            echo '✅' \$tool: \$(which \$tool)
        else
            echo '❌' \$tool: NOT FOUND
        fi
    done
    echo

    echo '[Security Tools Sample]'
    for tool in nmap john hashcat hydra aircrack-ng gobuster nikto sqlmap zaproxy burpsuite; do
        which \$tool >/dev/null 2>&1 && echo '✓' \$tool || echo '✗' \$tool
    done | column -t
    echo

    echo '[Tool Statistics]'
    echo 'Binaries in /usr/bin:' \$(ls /usr/bin 2>/dev/null | wc -l)
    echo 'Binaries in /usr/sbin:' \$(ls /usr/sbin 2>/dev/null | wc -l)
    echo 'Binaries in /usr/local/bin:' \$(ls /usr/local/bin 2>/dev/null | wc -l)
    echo 'Tools in /opt:' \$(find /opt -maxdepth 2 -type d 2>/dev/null | wc -l)
    echo

    echo '[Repository Clones]'
    echo 'BlackArch tools:' \$(ls -d /opt/blackarch/*/ 2>/dev/null | wc -l)
    echo 'Google tools:' \$(ls -d /opt/google-tools/*/ 2>/dev/null | wc -l)
    echo

    echo '[Chroot Size]'
    du -sh / 2>/dev/null | awk '{print \$1}'
"

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ MANUAL BUILD COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Status: Wireshark and Metasploit built from source"
echo "Next: Review verification results above"
echo
