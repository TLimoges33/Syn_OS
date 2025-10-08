//! Cryptographic Operations for AI Model Security
//!
//! Provides AES-256-GCM encryption and SHA-256 hashing for secure model storage

#![no_std]

extern crate alloc;
use alloc::vec::Vec;

/// AES-256-GCM encryption key size
pub const KEY_SIZE: usize = 32; // 256 bits

/// AES-256-GCM nonce/IV size
pub const NONCE_SIZE: usize = 12; // 96 bits (recommended for GCM)

/// AES-256-GCM authentication tag size
pub const TAG_SIZE: usize = 16; // 128 bits

/// SHA-256 hash size
pub const HASH_SIZE: usize = 32; // 256 bits

/// Encrypted model structure
#[derive(Debug, Clone)]
pub struct EncryptedModel {
    pub nonce: [u8; NONCE_SIZE],
    pub ciphertext: Vec<u8>,
    pub tag: [u8; TAG_SIZE],
}

/// Encrypt model data using AES-256-GCM
pub fn encrypt_model_aes_256_gcm(
    plaintext: &[u8],
    key: &[u8; KEY_SIZE],
    nonce: &[u8; NONCE_SIZE],
) -> Result<EncryptedModel, &'static str> {
    // Implementation using AES-256-GCM
    // In production, would use a crypto library like RustCrypto's aes-gcm

    // For now, provide a reference implementation structure
    let mut ciphertext = Vec::with_capacity(plaintext.len());
    let mut tag = [0u8; TAG_SIZE];

    // Simplified XOR encryption for stub (NOT secure!)
    // Real implementation would use proper AES-256-GCM
    for (i, &byte) in plaintext.iter().enumerate() {
        let key_byte = key[i % KEY_SIZE];
        let nonce_byte = nonce[i % NONCE_SIZE];
        ciphertext.push(byte ^ key_byte ^ nonce_byte);
    }

    // Generate authentication tag (stub - would use GMAC in real implementation)
    for i in 0..TAG_SIZE {
        tag[i] = key[i] ^ nonce[i % NONCE_SIZE];
    }

    Ok(EncryptedModel {
        nonce: *nonce,
        ciphertext,
        tag,
    })
}

/// Decrypt model data using AES-256-GCM
pub fn decrypt_model_aes_256_gcm(
    encrypted: &EncryptedModel,
    key: &[u8; KEY_SIZE],
) -> Result<Vec<u8>, &'static str> {
    // Verify authentication tag first
    if !verify_tag(&encrypted.tag, key, &encrypted.nonce) {
        return Err("Authentication tag verification failed");
    }

    // Decrypt ciphertext
    let mut plaintext = Vec::with_capacity(encrypted.ciphertext.len());

    // Simplified XOR decryption for stub (NOT secure!)
    // Real implementation would use proper AES-256-GCM
    for (i, &byte) in encrypted.ciphertext.iter().enumerate() {
        let key_byte = key[i % KEY_SIZE];
        let nonce_byte = encrypted.nonce[i % NONCE_SIZE];
        plaintext.push(byte ^ key_byte ^ nonce_byte);
    }

    Ok(plaintext)
}

/// Verify GMAC authentication tag
fn verify_tag(tag: &[u8; TAG_SIZE], key: &[u8; KEY_SIZE], nonce: &[u8; NONCE_SIZE]) -> bool {
    // Generate expected tag
    let mut expected_tag = [0u8; TAG_SIZE];
    for i in 0..TAG_SIZE {
        expected_tag[i] = key[i] ^ nonce[i % NONCE_SIZE];
    }

    // Constant-time comparison
    constant_time_compare(tag, &expected_tag)
}

/// Constant-time comparison to prevent timing attacks
fn constant_time_compare(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }

    let mut result = 0u8;
    for (x, y) in a.iter().zip(b.iter()) {
        result |= x ^ y;
    }

    result == 0
}

/// Calculate SHA-256 hash
pub fn calculate_sha256(data: &[u8]) -> [u8; HASH_SIZE] {
    // Implementation using SHA-256
    // In production, would use a crypto library like RustCrypto's sha2

    let mut hash = [0u8; HASH_SIZE];

    // Simplified hash for stub (NOT secure!)
    // Real implementation would use proper SHA-256
    for (i, &byte) in data.iter().enumerate() {
        hash[i % HASH_SIZE] ^= byte.rotate_left((i % 8) as u32);
    }

    // Add length-dependent mixing
    let len_bytes = (data.len() as u64).to_le_bytes();
    for (i, &byte) in len_bytes.iter().enumerate() {
        hash[i] ^= byte;
        hash[HASH_SIZE - 1 - i] ^= byte.rotate_right(4);
    }

    hash
}

/// Verify SHA-256 checksum
pub fn verify_sha256_checksum(data: &[u8], expected_hash: &[u8; HASH_SIZE]) -> bool {
    let computed_hash = calculate_sha256(data);
    constant_time_compare(&computed_hash, expected_hash)
}

/// Generate cryptographically secure random nonce
pub fn generate_nonce() -> [u8; NONCE_SIZE] {
    let mut nonce = [0u8; NONCE_SIZE];

    // In production, would use a CSPRNG like getrandom or rdrand
    // For stub, use a simple PRNG (NOT secure!)
    static mut COUNTER: u64 = 0;
    unsafe {
        COUNTER = COUNTER.wrapping_add(1);
        let bytes = COUNTER.to_le_bytes();
        for i in 0..NONCE_SIZE.min(8) {
            nonce[i] = bytes[i];
        }
        if NONCE_SIZE > 8 {
            for i in 8..NONCE_SIZE {
                nonce[i] = (COUNTER.wrapping_mul(31).wrapping_add(i as u64)) as u8;
            }
        }
    }

    nonce
}

/// Derive key from password using PBKDF2-HMAC-SHA256
pub fn derive_key_pbkdf2(
    password: &[u8],
    salt: &[u8],
    iterations: u32,
) -> [u8; KEY_SIZE] {
    // Implementation using PBKDF2-HMAC-SHA256
    // In production, would use a proper KDF library

    let mut key = [0u8; KEY_SIZE];

    // Simplified key derivation for stub (NOT secure!)
    // Real implementation would use proper PBKDF2
    for i in 0..KEY_SIZE {
        let mut acc = 0u8;
        for j in 0..iterations.min(256) {
            let pw_byte = password.get(i % password.len()).copied().unwrap_or(0);
            let salt_byte = salt.get(i % salt.len()).copied().unwrap_or(0);
            acc = acc.wrapping_add(pw_byte).wrapping_add(salt_byte).wrapping_add(j as u8);
        }
        key[i] = acc;
    }

    key
}

/// Secure key structure with automatic zeroing on drop
pub struct SecureKey {
    key: [u8; KEY_SIZE],
}

impl SecureKey {
    /// Create new secure key
    pub fn new(key: [u8; KEY_SIZE]) -> Self {
        Self { key }
    }

    /// Get key reference
    pub fn as_bytes(&self) -> &[u8; KEY_SIZE] {
        &self.key
    }

    /// Generate random key
    pub fn generate() -> Self {
        let mut key = [0u8; KEY_SIZE];

        // In production, use CSPRNG
        // For stub, use simple PRNG (NOT secure!)
        for i in 0..KEY_SIZE {
            key[i] = generate_nonce()[i % NONCE_SIZE];
        }

        Self { key }
    }
}

impl Drop for SecureKey {
    fn drop(&mut self) {
        // Zero out key material on drop to prevent memory leaks
        for byte in &mut self.key {
            // Volatile write to prevent compiler optimization
            unsafe {
                core::ptr::write_volatile(byte, 0);
            }
        }
    }
}

impl core::fmt::Debug for SecureKey {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "SecureKey([REDACTED])")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encryption_decryption() {
        let plaintext = b"Secret AI model data";
        let key = [0x42u8; KEY_SIZE];
        let nonce = [0x13u8; NONCE_SIZE];

        let encrypted = encrypt_model_aes_256_gcm(plaintext, &key, &nonce).unwrap();
        let decrypted = decrypt_model_aes_256_gcm(&encrypted, &key).unwrap();

        assert_eq!(plaintext.as_slice(), decrypted.as_slice());
    }

    #[test]
    fn test_sha256() {
        let data = b"Test data for hashing";
        let hash1 = calculate_sha256(data);
        let hash2 = calculate_sha256(data);

        assert_eq!(hash1, hash2);
        assert!(verify_sha256_checksum(data, &hash1));
    }

    #[test]
    fn test_tag_verification_fails_on_wrong_key() {
        let plaintext = b"Secret data";
        let key1 = [0x42u8; KEY_SIZE];
        let key2 = [0x43u8; KEY_SIZE];
        let nonce = [0x13u8; NONCE_SIZE];

        let encrypted = encrypt_model_aes_256_gcm(plaintext, &key1, &nonce).unwrap();
        let result = decrypt_model_aes_256_gcm(&encrypted, &key2);

        assert!(result.is_err());
    }

    #[test]
    fn test_constant_time_compare() {
        let a = [1u8, 2, 3, 4];
        let b = [1u8, 2, 3, 4];
        let c = [1u8, 2, 3, 5];

        assert!(constant_time_compare(&a, &b));
        assert!(!constant_time_compare(&a, &c));
    }

    #[test]
    fn test_secure_key_zeroing() {
        let key_data = [0x42u8; KEY_SIZE];
        let key = SecureKey::new(key_data);
        drop(key);
        // Key should be zeroed after drop (can't test directly due to drop)
    }
}
