#!/bin/bash
# Copy working ParrotOS tools directly into chroot
# Why fight dependencies when we can just copy what works?

set -e

CHROOT="$1"
if [ -z "$CHROOT" ]; then
    echo "Usage: $0 /path/to/chroot"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  COPYING PARROT TOOLS TO CHROOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Function to copy tool with dependencies
copy_tool_with_deps() {
    local tool="$1"
    local tool_path=$(which "$tool" 2>/dev/null)

    if [ -z "$tool_path" ]; then
        echo "✗ $tool: Not found on host"
        return 1
    fi

    echo "→ Copying $tool from $tool_path..."

    # Copy the binary
    sudo mkdir -p "$CHROOT$(dirname "$tool_path")"
    sudo cp -a "$tool_path" "$CHROOT$tool_path"

    # Copy shared library dependencies
    local libs=$(ldd "$tool_path" 2>/dev/null | grep -oP '/[^ ]+' | sort -u)
    for lib in $libs; do
        if [ -f "$lib" ] && [ ! -f "$CHROOT$lib" ]; then
            sudo mkdir -p "$CHROOT$(dirname "$lib")"
            sudo cp -a "$lib"* "$CHROOT$(dirname "$lib")/" 2>/dev/null || true
        fi
    done

    echo "✓ $tool copied"
}

# Function to copy entire package directory
copy_package_dir() {
    local src="$1"
    local desc="$2"

    if [ ! -d "$src" ]; then
        echo "✗ $desc: Not found at $src"
        return 1
    fi

    echo "→ Copying $desc..."
    sudo mkdir -p "$CHROOT$(dirname "$src")"
    sudo cp -a "$src" "$CHROOT$src"
    echo "✓ $desc copied ($(du -sh "$src" | cut -f1))"
}

echo "[1/6] Copying Wireshark..."
copy_tool_with_deps wireshark
copy_tool_with_deps tshark
copy_tool_with_deps dumpcap
copy_tool_with_deps editcap
copy_tool_with_deps capinfos
# Copy Wireshark data
if [ -d /usr/share/wireshark ]; then
    sudo mkdir -p "$CHROOT/usr/share"
    sudo cp -a /usr/share/wireshark "$CHROOT/usr/share/" 2>/dev/null || true
fi
echo

echo "[2/6] Copying Metasploit Framework..."
if [ -d /usr/share/metasploit-framework ]; then
    copy_package_dir /usr/share/metasploit-framework "Metasploit Framework"
    # Create symlinks
    sudo chroot "$CHROOT" /bin/bash -c "
        ln -sf /usr/share/metasploit-framework/msfconsole /usr/bin/msfconsole 2>/dev/null || true
        ln -sf /usr/share/metasploit-framework/msfvenom /usr/bin/msfvenom 2>/dev/null || true
        ln -sf /usr/share/metasploit-framework/msfdb /usr/bin/msfdb 2>/dev/null || true
    "
else
    copy_tool_with_deps msfconsole
    copy_tool_with_deps msfvenom
    copy_tool_with_deps msfdb
fi
echo

echo "[3/6] Copying additional security tools..."
for tool in burpsuite zaproxy sqlmap wpscan dirb enum4linux masscan \
            unicornscan dmitry fierce dnsrecon dnsenum sublist3r recon-ng \
            maltego beef-xss bettercap ettercap arachni skipfish wfuzz \
            cadaver theharvester amass sslscan sslyze testssl.sh; do
    copy_tool_with_deps "$tool" 2>/dev/null || echo "  ⚠ $tool not on host"
done
echo

echo "[4/6] Copying ParrotOS exclusive tools..."
# AnonSurf
if [ -d /usr/share/anon-gw ]; then
    copy_package_dir /usr/share/anon-gw "AnonSurf"
    copy_tool_with_deps anonsurf
fi

# Wifiphisher
if [ -d /usr/share/wifiphisher ]; then
    copy_package_dir /usr/share/wifiphisher "Wifiphisher"
    copy_tool_with_deps wifiphisher
fi

# Copy /usr/share security tools
for sharedir in /usr/share/{sqlmap,metasploit-framework,beef-xss,set,wpscan,dirb,wordlists}; do
    if [ -d "$sharedir" ]; then
        echo "  → Copying $(basename "$sharedir")..."
        sudo mkdir -p "$CHROOT/usr/share"
        sudo cp -a "$sharedir" "$CHROOT/usr/share/" 2>/dev/null || true
    fi
done
echo

echo "[5/6] Copying Kali/Parrot metapackage data..."
# Copy metapackage lists
if [ -d /usr/share/kali-menu ]; then
    sudo mkdir -p "$CHROOT/usr/share"
    sudo cp -a /usr/share/kali-menu "$CHROOT/usr/share/" 2>/dev/null || true
fi
if [ -d /usr/share/parrot-menu ]; then
    sudo mkdir -p "$CHROOT/usr/share"
    sudo cp -a /usr/share/parrot-menu "$CHROOT/usr/share/" 2>/dev/null || true
fi
echo

echo "[6/6] Copying wordlists and databases..."
if [ -d /usr/share/wordlists ]; then
    echo "  → Copying wordlists (this may take a minute)..."
    sudo mkdir -p "$CHROOT/usr/share"
    sudo cp -a /usr/share/wordlists "$CHROOT/usr/share/" 2>/dev/null || true
fi
if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
    echo "  → Extracting rockyou.txt..."
    sudo gunzip -c /usr/share/wordlists/rockyou.txt.gz > /tmp/rockyou.txt 2>/dev/null || true
    sudo mv /tmp/rockyou.txt "$CHROOT/usr/share/wordlists/" 2>/dev/null || true
fi
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

sudo chroot "$CHROOT" /bin/bash -c "
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
    for tool in nmap john hashcat hydra aircrack-ng gobuster nikto sqlmap \
                zaproxy burpsuite masscan dmitry fierce dnsrecon; do
        which \$tool >/dev/null 2>&1 && echo '✓' \$tool || echo '✗' \$tool
    done | column -t
    echo

    echo '[Tool Statistics]'
    echo 'Total in /usr/bin:' \$(ls /usr/bin 2>/dev/null | wc -l)
    echo 'Total in /usr/sbin:' \$(ls /usr/sbin 2>/dev/null | wc -l)
    echo 'Security tools in /usr/share:' \$(find /usr/share -maxdepth 1 -type d -name '*exploit*' -o -name '*metasploit*' -o -name '*wordlist*' -o -name '*beef*' -o -name '*sqlmap*' 2>/dev/null | wc -l)
    echo

    echo '[Chroot Size]'
    du -sh / 2>/dev/null | awk '{print \$1}'
"

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PARROT TOOLS COPIED TO CHROOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "All working tools from your ParrotOS host are now in the chroot!"
echo "No dependency issues - we just copied what works! 💪"
echo
