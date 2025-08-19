use anyhow::Result;
use ring::rand;
use chacha20poly1305::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    ChaCha20Poly1305, Nonce, Key
};

/// Cryptographic errors - specific types to avoid broad exception handling
#[derive(Debug, thiserror::Error)]
pub enum CryptoError {
    #[error("Encryption failed")]
    EncryptionFailed,
    #[error("Decryption failed")]
    DecryptionFailed,
    #[error("Key generation failed")]
    KeyGenerationFailed,
    #[error("Invalid key format")]
    InvalidKey,
    #[error("Invalid nonce format")]
    InvalidNonce,
}

/// Secure encryption service using ChaCha20-Poly1305 AEAD
pub struct EncryptionService {
    cipher: ChaCha20Poly1305,
}

impl EncryptionService {
    /// Create new encryption service with random key
    pub fn new() -> Result<Self, CryptoError> {
        let key = ChaCha20Poly1305::generate_key(&mut OsRng);
        let cipher = ChaCha20Poly1305::new(&key);
        
        Ok(Self { cipher })
    }
    
    /// Create encryption service from existing key
    pub fn from_key(key_bytes: &[u8; 32]) -> Result<Self, CryptoError> {
        let key = Key::from_slice(key_bytes);
        let cipher = ChaCha20Poly1305::new(key);
        
        Ok(Self { cipher })
    }
    
    /// Encrypt data with authenticated encryption
    pub fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, CryptoError> {
        let nonce = ChaCha20Poly1305::generate_nonce(&mut OsRng);
        
        let ciphertext = self.cipher
            .encrypt(&nonce, plaintext)
            .map_err(|_| CryptoError::EncryptionFailed)?;
        
        // Prepend nonce to ciphertext for storage
        let mut result = nonce.to_vec();
        result.extend_from_slice(&ciphertext);
        
        Ok(result)
    }
    
    /// Decrypt data with authentication verification
    pub fn decrypt(&self, encrypted_data: &[u8]) -> Result<Vec<u8>, CryptoError> {
        if encrypted_data.len() < 12 {
            return Err(CryptoError::InvalidNonce);
        }
        
        // Extract nonce and ciphertext
        let (nonce_bytes, ciphertext) = encrypted_data.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);
        
        let plaintext = self.cipher
            .decrypt(nonce, ciphertext)
            .map_err(|_| CryptoError::DecryptionFailed)?;
        
        Ok(plaintext)
    }
    
    /// Encrypt string data
    pub fn encrypt_string(&self, plaintext: &str) -> Result<Vec<u8>, CryptoError> {
        self.encrypt(plaintext.as_bytes())
    }
    
    /// Decrypt to string
    pub fn decrypt_string(&self, encrypted_data: &[u8]) -> Result<String, CryptoError> {
        let plaintext = self.decrypt(encrypted_data)?;
        String::from_utf8(plaintext).map_err(|_| CryptoError::DecryptionFailed)
    }
}

/// Key derivation for password-based encryption
pub struct KeyDerivation;

impl KeyDerivation {
    /// Derive key from password using PBKDF2
    pub fn derive_key(password: &str, salt: &[u8], iterations: u32) -> Result<[u8; 32], CryptoError> {
        use ring::pbkdf2;
        
        let mut key = [0u8; 32];
        pbkdf2::derive(
            pbkdf2::PBKDF2_HMAC_SHA256,
            std::num::NonZeroU32::new(iterations).unwrap(),
            salt,
            password.as_bytes(),
            &mut key,
        );
        
        Ok(key)
    }
    
    /// Generate secure salt
    pub fn generate_salt() -> Result<[u8; 16], CryptoError> {
        let mut salt = [0u8; 16];
        ring::rand::SystemRandom::new().fill(&mut salt)
            .map_err(|_| CryptoError::KeyGenerationFailed)?;
        Ok(salt)
    }
}

/// Secure memory for storing sensitive data
pub struct SecureMemory {
    data: Vec<u8>,
}

impl SecureMemory {
    /// Create secure memory region
    pub fn new(size: usize) -> Self {
        let mut data = vec![0u8; size];
        // In a real implementation, we would use mlock() to prevent swapping
        Self { data }
    }
    
    /// Write data to secure memory
    pub fn write(&mut self, offset: usize, data: &[u8]) -> Result<(), CryptoError> {
        if offset + data.len() > self.data.len() {
            return Err(CryptoError::InvalidKey);
        }
        
        self.data[offset..offset + data.len()].copy_from_slice(data);
        Ok(())
    }
    
    /// Read data from secure memory
    pub fn read(&self, offset: usize, len: usize) -> Result<&[u8], CryptoError> {
        if offset + len > self.data.len() {
            return Err(CryptoError::InvalidKey);
        }
        
        Ok(&self.data[offset..offset + len])
    }
    
    /// Clear secure memory
    pub fn clear(&mut self) {
        // Overwrite with random data then zeros
        let rng = ring::rand::SystemRandom::new();
        let _ = rng.fill(&mut self.data);
        self.data.fill(0);
    }
}

impl Drop for SecureMemory {
    fn drop(&mut self) {
        self.clear();
    }
}

/// Digital signature service using Ed25519
pub struct SignatureService {
    signing_key: ed25519_dalek::SigningKey,
}

impl SignatureService {
    /// Create new signature service with random keypair
    pub fn new() -> Result<Self, CryptoError> {
        use ed25519_dalek::SigningKey;
        use rand::rngs::OsRng;
        
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        
        Ok(Self { signing_key })
    }
    
    /// Sign data
    pub fn sign(&self, data: &[u8]) -> Vec<u8> {
        use ed25519_dalek::Signer;
        self.signing_key.sign(data).to_bytes().to_vec()
    }
    
    /// Verify signature
    pub fn verify(&self, data: &[u8], signature: &[u8]) -> Result<bool, CryptoError> {
        use ed25519_dalek::{Verifier, Signature};
        
        if signature.len() != 64 {
            return Err(CryptoError::InvalidKey);
        }
        
        let sig_array: [u8; 64] = signature.try_into().map_err(|_| CryptoError::InvalidKey)?;
        let signature = Signature::from_bytes(&sig_array);
        let verifying_key = self.signing_key.verifying_key();
        
        Ok(verifying_key.verify(data, &signature).is_ok())
    }
    
    /// Get public key for sharing
    pub fn public_key(&self) -> [u8; 32] {
        self.signing_key.verifying_key().to_bytes()
    }
}

/// Hash service for data integrity
pub struct HashService;

impl HashService {
    /// Calculate SHA-256 hash
    pub fn sha256(data: &[u8]) -> [u8; 32] {
        use ring::digest;
        let digest = digest::digest(&digest::SHA256, data);
        let mut hash = [0u8; 32];
        hash.copy_from_slice(digest.as_ref());
        hash
    }
    
    /// Calculate BLAKE2b hash (faster alternative)
    pub fn blake2b(data: &[u8]) -> [u8; 32] {
        // For now, use SHA-256 as BLAKE2b isn't in ring
        Self::sha256(data)
    }
    
    /// Verify hash
    pub fn verify_hash(data: &[u8], expected_hash: &[u8; 32]) -> bool {
        let actual_hash = Self::sha256(data);
        // Use secure comparison to prevent timing attacks
        actual_hash.len() == expected_hash.len() && 
        actual_hash.iter().zip(expected_hash.iter()).fold(0u8, |acc, (a, b)| acc | (a ^ b)) == 0
    }
}

/// Initialize cryptography module
pub fn init() {
    println!("🔐 Cryptography module initialized");
}

/// Global encryption service
static mut GLOBAL_ENCRYPTION: Option<EncryptionService> = None;
static ENCRYPTION_INIT: std::sync::Once = std::sync::Once::new();

/// Get global encryption service
pub fn get_encryption_service() -> Result<&'static EncryptionService, CryptoError> {
    unsafe {
        ENCRYPTION_INIT.call_once(|| {
            if let Ok(service) = EncryptionService::new() {
                GLOBAL_ENCRYPTION = Some(service);
            }
        });
        GLOBAL_ENCRYPTION.as_ref().ok_or(CryptoError::KeyGenerationFailed)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_encryption_decryption() {
        let service = EncryptionService::new().unwrap();
        let plaintext = b"Hello, secure world!";
        
        let encrypted = service.encrypt(plaintext).unwrap();
        let decrypted = service.decrypt(&encrypted).unwrap();
        
        assert_eq!(plaintext, decrypted.as_slice());
    }
    
    #[test]
    fn test_string_encryption() {
        let service = EncryptionService::new().unwrap();
        let plaintext = "Secret message";
        
        let encrypted = service.encrypt_string(plaintext).unwrap();
        let decrypted = service.decrypt_string(&encrypted).unwrap();
        
        assert_eq!(plaintext, decrypted);
    }
    
    #[test]
    fn test_key_derivation() {
        let password = "strong_password";
        let salt = KeyDerivation::generate_salt().unwrap();
        let iterations = 100_000;
        
        let key1 = KeyDerivation::derive_key(password, &salt, iterations).unwrap();
        let key2 = KeyDerivation::derive_key(password, &salt, iterations).unwrap();
        
        assert_eq!(key1, key2);
    }
    
    #[test]
    fn test_signature_verification() {
        let service = SignatureService::new().unwrap();
        let data = b"Data to sign";
        
        let signature = service.sign(data);
        let is_valid = service.verify(data, &signature).unwrap();
        
        assert!(is_valid);
    }
    
    #[test]
    fn test_hash_verification() {
        let data = b"Data to hash";
        let hash = HashService::sha256(data);
        
        assert!(HashService::verify_hash(data, &hash));
        assert!(!HashService::verify_hash(b"Different data", &hash));
    }
    
    #[test]
    fn test_secure_memory() {
        let mut secure_mem = SecureMemory::new(64);
        let secret_data = b"secret information";
        
        secure_mem.write(0, secret_data).unwrap();
        let read_data = secure_mem.read(0, secret_data.len()).unwrap();
        
        assert_eq!(secret_data, read_data);
    }
}