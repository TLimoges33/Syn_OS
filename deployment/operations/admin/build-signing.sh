#!/bin/bash
# Build Integrity & Signing System
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
BUILD_DIR="${PROJECT_ROOT}/build"
KEYS_DIR="${PROJECT_ROOT}/security/keys"

# Create secure keys directory
mkdir -p "$KEYS_DIR"
chmod 700 "$KEYS_DIR"

# Generate signing key if not exists
if [[ ! -f "$KEYS_DIR/build-signing.key" ]]; then
    echo "🔑 Generating build signing key..."
    openssl genpkey -algorithm RSA -out "$KEYS_DIR/build-signing.key" -pkcs8 -aes256
    openssl rsa -pubout -in "$KEYS_DIR/build-signing.key" -out "$KEYS_DIR/build-signing.pub"
    chmod 600 "$KEYS_DIR/build-signing.key"
    chmod 644 "$KEYS_DIR/build-signing.pub"
fi

# Sign build artifacts
sign_artifact() {
    local artifact="$1"
    local signature="${artifact}.sig"
    
    echo "✍️ Signing: $(basename "$artifact")"
    
    # Create SHA256 hash
    sha256sum "$artifact" > "${artifact}.sha256"
    
    # Create signature
    openssl dgst -sha256 -sign "$KEYS_DIR/build-signing.key" -out "$signature" "$artifact"
    
    echo "   ✅ Signature: $(basename "$signature")"
    echo "   ✅ Hash: $(basename "${artifact}.sha256")"
}

# Verify signature
verify_artifact() {
    local artifact="$1"
    local signature="${artifact}.sig"
    
    if [[ ! -f "$signature" ]]; then
        echo "❌ No signature found for: $(basename "$artifact")"
        return 1
    fi
    
    # Verify signature
    if openssl dgst -sha256 -verify "$KEYS_DIR/build-signing.pub" -signature "$signature" "$artifact"; then
        echo "✅ Verified: $(basename "$artifact")"
        return 0
    else
        echo "❌ Verification failed: $(basename "$artifact")"
        return 1
    fi
}

# Sign all build outputs
if [[ -d "$BUILD_DIR" ]]; then
    find "$BUILD_DIR" -name "*.iso" -o -name "*.bin" -o -name "kernel*" | while read -r artifact; do
        sign_artifact "$artifact"
    done
fi

echo "🔐 Build integrity signing complete"
