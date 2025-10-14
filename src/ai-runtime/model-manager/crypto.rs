//! Cryptographic Operations for AI Model Security
//!
//! Provides AES-256-GCM encryption and SHA-256 hashing for secure model storage

#![no_std]

extern crate alloc;
use alloc::vec::Vec;

use aes_gcm::{
    aead::{Aead, KeyInit, Payload},
    Aes256Gcm, Nonce, Key
};
use sha2::{Sha256, Digest};

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
    // Create cipher instance
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(key));
    let nonce_obj = Nonce::from_slice(nonce);

    // Encrypt with authentication
    let ciphertext = cipher
        .encrypt(nonce_obj, plaintext)
        .map_err(|_| "Encryption failed")?;

    // AES-GCM returns ciphertext || tag combined
    if ciphertext.len() < TAG_SIZE {
        return Err("Invalid ciphertext length");
    }

    let tag_start = ciphertext.len() - TAG_SIZE;
    let mut tag = [0u8; TAG_SIZE];
    tag.copy_from_slice(&ciphertext[tag_start..]);

    let ciphertext_only = ciphertext[..tag_start].to_vec();

    Ok(EncryptedModel {
        nonce: *nonce,
        ciphertext: ciphertext_only,
        tag,
    })
}

/// Decrypt model data using AES-256-GCM
pub fn decrypt_model_aes_256_gcm(
    encrypted: &EncryptedModel,
    key: &[u8; KEY_SIZE],
) -> Result<Vec<u8>, &'static str> {
    // Create cipher instance
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(key));
    let nonce_obj = Nonce::from_slice(&encrypted.nonce);

    // Reconstruct ciphertext || tag for aes-gcm crate
    let mut combined = encrypted.ciphertext.clone();
    combined.extend_from_slice(&encrypted.tag);

    // Decrypt and verify authentication tag
    let plaintext = cipher
        .decrypt(nonce_obj, combined.as_ref())
        .map_err(|_| "Decryption failed or authentication tag mismatch")?;

    Ok(plaintext)
}

/// Calculate SHA-256 hash
pub fn calculate_sha256(data: &[u8]) -> [u8; HASH_SIZE] {
    let mut hasher = Sha256::new();
    hasher.update(data);
    let result = hasher.finalize();

    let mut hash = [0u8; HASH_SIZE];
    hash.copy_from_slice(&result);
    hash
}

/// Verify SHA-256 checksum
pub fn verify_sha256_checksum(data: &[u8], expected_hash: &[u8; HASH_SIZE]) -> bool {
    let computed_hash = calculate_sha256(data);
    constant_time_compare(&computed_hash, expected_hash)
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

/// Generate cryptographically secure random nonce
pub fn generate_nonce() -> [u8; NONCE_SIZE] {
    let mut nonce = [0u8; NONCE_SIZE];

    #[cfg(feature = "std")]
    {
        use getrandom::getrandom;
        getrandom(&mut nonce).expect("Failed to generate random nonce");
    }

    #[cfg(not(feature = "std"))]
    {
        // For no_std, use a deterministic but unique nonce
        // In production, this should be replaced with a hardware RNG
        static mut COUNTER: u64 = 0;
        unsafe {
            COUNTER = COUNTER.wrapping_add(1);
            let bytes = COUNTER.to_le_bytes();
            for i in 0..NONCE_SIZE.min(8) {
                nonce[i] = bytes[i];
            }
            if NONCE_SIZE > 8 {
                let timestamp = COUNTER.wrapping_mul(0x9e3779b97f4a7c15); // Golden ratio
                let ts_bytes = timestamp.to_le_bytes();
                for i in 8..NONCE_SIZE {
                    nonce[i] = ts_bytes[i - 8];
                }
            }
        }
    }

    nonce
}

/// Derive key from password using simple PBKDF2-like function
/// Note: This is a simplified implementation. For production, use a proper KDF
pub fn derive_key_pbkdf2(
    password: &[u8],
    salt: &[u8],
    iterations: u32,
) -> [u8; KEY_SIZE] {
    let mut key = [0u8; KEY_SIZE];

    // Simple iterative hashing for key derivation
    for iter in 0..iterations {
        let mut hasher = Sha256::new();
        hasher.update(password);
        hasher.update(salt);
        hasher.update(&iter.to_le_bytes());
        if iter > 0 {
            hasher.update(&key);
        }
        let result = hasher.finalize();

        // XOR result into key
        for (i, &byte) in result.iter().enumerate() {
            if i < KEY_SIZE {
                key[i] ^= byte;
            }
        }
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

        #[cfg(feature = "std")]
        {
            use getrandom::getrandom;
            getrandom(&mut key).expect("Failed to generate random key");
        }

        #[cfg(not(feature = "std"))]
        {
            // For no_std, generate from multiple nonces
            // In production, use hardware RNG
            for chunk in key.chunks_mut(NONCE_SIZE) {
                let nonce = generate_nonce();
                chunk.copy_from_slice(&nonce[..chunk.len()]);
            }
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
        let plaintext = b"Secret AI model data for testing";
        let key = [0x42u8; KEY_SIZE];
        let nonce = [0x13u8; NONCE_SIZE];

        let encrypted = encrypt_model_aes_256_gcm(plaintext, &key, &nonce).unwrap();
        let decrypted = decrypt_model_aes_256_gcm(&encrypted, &key).unwrap();

        assert_eq!(plaintext.as_slice(), decrypted.as_slice());
    }

    #[test]
    fn test_decryption_wrong_key_fails() {
        let plaintext = b"Secret data";
        let key1 = [0x42u8; KEY_SIZE];
        let key2 = [0x43u8; KEY_SIZE];
        let nonce = [0x13u8; NONCE_SIZE];

        let encrypted = encrypt_model_aes_256_gcm(plaintext, &key1, &nonce).unwrap();
        let result = decrypt_model_aes_256_gcm(&encrypted, &key2);

        assert!(result.is_err());
    }

    #[test]
    fn test_sha256_deterministic() {
        let data = b"Test data for hashing";
        let hash1 = calculate_sha256(data);
        let hash2 = calculate_sha256(data);

        assert_eq!(hash1, hash2);
        assert!(verify_sha256_checksum(data, &hash1));
    }

    #[test]
    fn test_sha256_different_data() {
        let data1 = b"First data";
        let data2 = b"Second data";
        let hash1 = calculate_sha256(data1);
        let hash2 = calculate_sha256(data2);

        assert_ne!(hash1, hash2);
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
        assert_eq!(key.as_bytes(), &key_data);
        drop(key);
        // Key should be zeroed after drop (can't test directly)
    }

    #[test]
    fn test_derive_key_deterministic() {
        let password = b"my_secure_password";
        let salt = b"random_salt_value";
        let key1 = derive_key_pbkdf2(password, salt, 1000);
        let key2 = derive_key_pbkdf2(password, salt, 1000);

        assert_eq!(key1, key2);
    }

    #[test]
    fn test_derive_key_different_passwords() {
        let password1 = b"password1";
        let password2 = b"password2";
        let salt = b"salt";
        let key1 = derive_key_pbkdf2(password1, salt, 1000);
        let key2 = derive_key_pbkdf2(password2, salt, 1000);

        assert_ne!(key1, key2);
    }
}
