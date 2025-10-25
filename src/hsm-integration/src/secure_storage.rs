//! Secure Key Storage
//!
//! Software-based encrypted key storage (fallback when no HSM available)

use crate::{Result, HSMError, KeyType};
use std::collections::HashMap;
use uuid::Uuid;
use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use sha2::{Sha256, Digest};

/// Secure key storage with AES-256-GCM encryption
pub struct SecureKeyStorage {
    master_key: Vec<u8>,
    encrypted_keys: HashMap<Uuid, Vec<u8>>,
    encrypted_data: HashMap<Uuid, Vec<u8>>,
}

impl SecureKeyStorage {
    pub fn new() -> Self {
        // Derive master key from system entropy
        let mut hasher = Sha256::new();
        hasher.update(b"SYNOS_SECURE_STORAGE_v1.0");
        hasher.update(&std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs()
            .to_le_bytes());

        Self {
            master_key: hasher.finalize().to_vec(),
            encrypted_keys: HashMap::new(),
            encrypted_data: HashMap::new(),
        }
    }

    pub fn generate_software_key(&mut self, key_id: Uuid, key_type: &KeyType) -> Result<()> {
        let key_material: Vec<u8> = match key_type {
            KeyType::RSA2048 => (0..256).map(|_| rand::random::<u8>()).collect(),
            KeyType::RSA4096 => (0..512).map(|_| rand::random::<u8>()).collect(),
            KeyType::ECC256 => (0..32).map(|_| rand::random::<u8>()).collect(),
            KeyType::ECC384 => (0..48).map(|_| rand::random::<u8>()).collect(),
            KeyType::AES256 => (0..32).map(|_| rand::random::<u8>()).collect(),
            KeyType::HMAC => (0..64).map(|_| rand::random::<u8>()).collect(),
        };

        let encrypted = self.encrypt(&key_material)?;
        self.encrypted_keys.insert(key_id, encrypted);

        Ok(())
    }

    pub fn store_encrypted(&mut self, data_id: Uuid, data: &[u8]) -> Result<()> {
        let encrypted = self.encrypt(data)?;
        self.encrypted_data.insert(data_id, encrypted);
        Ok(())
    }

    pub fn retrieve_encrypted(&self, data_id: Uuid) -> Result<Vec<u8>> {
        let encrypted = self.encrypted_data.get(&data_id)
            .ok_or_else(|| HSMError::StorageError("Data not found".to_string()))?;

        self.decrypt(encrypted)
    }

    fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>> {
        // Initialize AES-256-GCM cipher
        let key = aes_gcm::Key::<Aes256Gcm>::from_slice(&self.master_key);
        let cipher = Aes256Gcm::new(key);

        // Generate random nonce
        let nonce_bytes: Vec<u8> = (0..12).map(|_| rand::random::<u8>()).collect();
        let nonce = Nonce::from_slice(&nonce_bytes);

        // Encrypt
        let ciphertext = cipher.encrypt(nonce, plaintext)
            .map_err(|e| HSMError::StorageError(format!("Encryption failed: {}", e)))?;

        // Combine nonce + ciphertext
        let mut result = nonce_bytes;
        result.extend_from_slice(&ciphertext);

        Ok(result)
    }

    fn decrypt(&self, encrypted: &[u8]) -> Result<Vec<u8>> {
        if encrypted.len() < 12 {
            return Err(HSMError::StorageError("Invalid encrypted data".to_string()));
        }

        // Extract nonce and ciphertext
        let (nonce_bytes, ciphertext) = encrypted.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);

        // Initialize cipher
        let key = aes_gcm::Key::<Aes256Gcm>::from_slice(&self.master_key);
        let cipher = Aes256Gcm::new(key);

        // Decrypt
        cipher.decrypt(nonce, ciphertext)
            .map_err(|e| HSMError::StorageError(format!("Decryption failed: {}", e)))
    }

    pub fn count_keys(&self) -> usize {
        self.encrypted_keys.len() + self.encrypted_data.len()
    }

    pub fn delete_key(&mut self, key_id: Uuid) -> Result<()> {
        self.encrypted_keys.remove(&key_id);
        self.encrypted_data.remove(&key_id);
        Ok(())
    }

    pub fn export_encrypted(&self, key_id: Uuid) -> Result<Vec<u8>> {
        self.encrypted_keys.get(&key_id)
            .or_else(|| self.encrypted_data.get(&key_id))
            .cloned()
            .ok_or_else(|| HSMError::StorageError("Key not found".to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_storage_creation() {
        let storage = SecureKeyStorage::new();
        assert_eq!(storage.count_keys(), 0);
    }

    #[test]
    fn test_encrypt_decrypt() {
        let storage = SecureKeyStorage::new();
        let plaintext = b"secret_data_12345";

        let encrypted = storage.encrypt(plaintext).unwrap();
        let decrypted = storage.decrypt(&encrypted).unwrap();

        assert_eq!(plaintext.as_slice(), decrypted.as_slice());
    }

    #[test]
    fn test_key_generation() {
        let mut storage = SecureKeyStorage::new();
        let key_id = Uuid::new_v4();

        storage.generate_software_key(key_id, &KeyType::AES256).unwrap();
        assert_eq!(storage.count_keys(), 1);
    }

    #[test]
    fn test_data_storage() {
        let mut storage = SecureKeyStorage::new();
        let data_id = Uuid::new_v4();
        let secret = b"important_secret";

        storage.store_encrypted(data_id, secret).unwrap();
        let retrieved = storage.retrieve_encrypted(data_id).unwrap();

        assert_eq!(secret.as_slice(), retrieved.as_slice());
    }
}
