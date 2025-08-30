# Code Signing Guide for SynapticOS

## Why Code Signing?
- Ensures authenticity and integrity of scripts and binaries
- Prevents tampering and supply chain attacks

## How to Sign a Script or Binary (GPG Example)

### 1. Generate a GPG Key (if you don’t have one)
```bash
gpg --full-generate-key
```

### 2. Sign a File
```bash
gpg --armor --detach-sign your_script.sh
```

### 3. Verify a Signature
```bash
gpg --verify your_script.sh.asc your_script.sh
```

## Advanced: Sigstore/Cosign (for containers)
- See: https://docs.sigstore.dev/cosign/overview/

## Policy
- All critical scripts and release binaries must be signed before distribution.
- Verification is required in CI before deployment.
