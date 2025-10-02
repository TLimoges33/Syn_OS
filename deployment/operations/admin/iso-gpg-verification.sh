#!/bin/bash
# ISO GPG Verification System
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
ISO_DIR="${PROJECT_ROOT}/build"
GPG_DIR="${PROJECT_ROOT}/security/gpg"

# Create GPG directory
mkdir -p "$GPG_DIR"
chmod 700 "$GPG_DIR"

# Initialize GPG if needed
if [[ ! -f "$GPG_DIR/pubring.kbx" ]]; then
    echo "🔑 Initializing GPG for ISO verification..."
    export GNUPGHOME="$GPG_DIR"
    
    # Generate GPG key for ISO signing
    cat > "$GPG_DIR/key-params" <<EOF
Key-Type: RSA
Key-Length: 4096
Name-Real: Syn_OS Build System
Name-Email: build@syn-os.dev
Expire-Date: 1y
Passphrase: SynOS-Secure-Build-2025
%commit
EOF

    gpg --batch --generate-key "$GPG_DIR/key-params"
    rm "$GPG_DIR/key-params"
    
    # Export public key
    gpg --export --armor > "$GPG_DIR/syn-os-public.asc"
fi

# Sign ISO function
sign_iso() {
    local iso_file="$1"
    export GNUPGHOME="$GPG_DIR"
    
    echo "✍️ GPG signing: $(basename "$iso_file")"
    
    # Create detached signature
    echo "SynOS-Secure-Build-2025" | gpg --batch --yes --passphrase-fd 0 --detach-sign --armor "$iso_file"
    
    # Create checksums
    sha256sum "$iso_file" > "${iso_file}.sha256"
    md5sum "$iso_file" > "${iso_file}.md5"
    
    echo "   ✅ GPG signature: ${iso_file}.asc"
    echo "   ✅ SHA256: ${iso_file}.sha256"
    echo "   ✅ MD5: ${iso_file}.md5"
}

# Verify ISO function
verify_iso() {
    local iso_file="$1"
    export GNUPGHOME="$GPG_DIR"
    
    echo "🔍 Verifying: $(basename "$iso_file")"
    
    # Verify GPG signature
    if gpg --verify "${iso_file}.asc" "$iso_file" 2>/dev/null; then
        echo "   ✅ GPG signature valid"
    else
        echo "   ❌ GPG signature verification failed"
        return 1
    fi
    
    # Verify checksums
    if sha256sum -c "${iso_file}.sha256" >/dev/null 2>&1; then
        echo "   ✅ SHA256 checksum valid"
    else
        echo "   ❌ SHA256 checksum verification failed"
        return 1
    fi
    
    echo "✅ ISO verification complete: $(basename "$iso_file")"
}

# Process all ISO files
if [[ -d "$ISO_DIR" ]]; then
    find "$ISO_DIR" -name "*.iso" | while read -r iso_file; do
        if [[ "$1" == "sign" ]]; then
            sign_iso "$iso_file"
        elif [[ "$1" == "verify" ]]; then
            verify_iso "$iso_file"
        fi
    done
fi

echo "🔏 ISO GPG processing complete"
