//! AI Model Management
//!
//! Secure model storage, loading, and version management

#![no_std]

extern crate alloc;
use alloc::vec::Vec;
use alloc::string::String;
use alloc::collections::BTreeMap;

mod crypto;
pub use crypto::*;

/// AI Model metadata
#[derive(Debug, Clone)]
pub struct ModelMetadata {
    pub name: String,
    pub version: String,
    pub framework: ModelFramework,
    pub size_bytes: usize,
    pub checksum: [u8; 32],
    pub encrypted: bool,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ModelFramework {
    TensorFlowLite,
    ONNX,
    PyTorch,
}

/// Model storage manager
pub struct ModelManager {
    models: BTreeMap<String, ModelMetadata>,
    storage_path: String,
    encryption_enabled: bool,
    master_key: Option<SecureKey>,
}

impl ModelManager {
    /// Create new model manager
    pub fn new(storage_path: String) -> Self {
        Self {
            models: BTreeMap::new(),
            storage_path,
            encryption_enabled: true,
            master_key: Some(SecureKey::generate()),
        }
    }

    /// Create model manager with custom key
    pub fn with_key(storage_path: String, key: SecureKey) -> Self {
        Self {
            models: BTreeMap::new(),
            storage_path,
            encryption_enabled: true,
            master_key: Some(key),
        }
    }

    /// Register a new model
    pub fn register_model(&mut self, mut metadata: ModelMetadata) -> Result<(), &'static str> {
        let key = format!("{}-{}", metadata.name, metadata.version);

        // Note: Checksum will be calculated when storing the model
        // This just registers the metadata

        self.models.insert(key, metadata);
        Ok(())
    }

    /// Store model with encryption
    pub fn store_model(&mut self, name: &str, version: &str, model_data: &[u8]) -> Result<(), &'static str> {
        // Calculate checksum
        let checksum = calculate_sha256(model_data);

        // Update metadata with checksum
        let key = format!("{}-{}", name, version);
        if let Some(metadata) = self.models.get_mut(&key) {
            metadata.checksum = checksum;
            metadata.size_bytes = model_data.len();
        } else {
            return Err("Model not registered");
        }

        // Encrypt if enabled
        if self.encryption_enabled {
            let master_key = self.master_key.as_ref()
                .ok_or("No encryption key available")?;

            let nonce = generate_nonce();
            let encrypted = encrypt_model_aes_256_gcm(model_data, master_key.as_bytes(), &nonce)?;

            // In production, would write encrypted data to file system
            // For now, mark as encrypted in metadata
            if let Some(metadata) = self.models.get_mut(&key) {
                metadata.encrypted = true;
            }
        }

        Ok(())
    }

    /// Load model from storage
    pub fn load_model(&self, name: &str, version: &str) -> Result<Vec<u8>, &'static str> {
        let key = format!("{}-{}", name, version);

        let metadata = self.models.get(&key)
            .ok_or("Model not found")?;

        // In production, would read from file system
        // For now, return placeholder
        let mut model_data = Vec::new();

        // If encrypted, decrypt
        if metadata.encrypted {
            let master_key = self.master_key.as_ref()
                .ok_or("No decryption key available")?;

            // In production, would:
            // 1. Read encrypted file
            // 2. Extract nonce, ciphertext, tag
            // 3. Decrypt using master key
            // 4. Verify checksum
            // For now, stub
        }

        // Verify checksum
        if !model_data.is_empty() {
            if !verify_sha256_checksum(&model_data, &metadata.checksum) {
                return Err("Checksum verification failed");
            }
        }

        Ok(model_data)
    }

    /// Delete model from storage
    pub fn delete_model(&mut self, name: &str, version: &str) -> Result<(), &'static str> {
        let key = format!("{}-{}", name, version);

        self.models.remove(&key)
            .ok_or("Model not found")?;

        // In production, would delete encrypted file from storage
        // For now, just remove from registry

        Ok(())
    }

    /// List all available models
    pub fn list_models(&self) -> Vec<ModelMetadata> {
        self.models.values().cloned().collect()
    }

    /// Get model metadata
    pub fn get_metadata(&self, name: &str, version: &str) -> Option<&ModelMetadata> {
        let key = format!("{}-{}", name, version);
        self.models.get(&key)
    }

    /// Enable/disable encryption
    pub fn set_encryption(&mut self, enabled: bool) {
        self.encryption_enabled = enabled;
    }
}

// Encryption and checksum functions are now provided by crypto module
// Re-export for backwards compatibility
pub fn encrypt_model(data: &[u8], key: &[u8; 32]) -> Result<Vec<u8>, &'static str> {
    let nonce = generate_nonce();
    let encrypted = encrypt_model_aes_256_gcm(data, key, &nonce)?;

    // Serialize encrypted model: nonce || ciphertext || tag
    let mut result = Vec::with_capacity(NONCE_SIZE + encrypted.ciphertext.len() + TAG_SIZE);
    result.extend_from_slice(&encrypted.nonce);
    result.extend_from_slice(&encrypted.ciphertext);
    result.extend_from_slice(&encrypted.tag);

    Ok(result)
}

pub fn decrypt_model(encrypted: &[u8], key: &[u8; 32]) -> Result<Vec<u8>, &'static str> {
    if encrypted.len() < NONCE_SIZE + TAG_SIZE {
        return Err("Invalid encrypted data");
    }

    // Deserialize: nonce || ciphertext || tag
    let mut nonce = [0u8; NONCE_SIZE];
    let mut tag = [0u8; TAG_SIZE];

    nonce.copy_from_slice(&encrypted[..NONCE_SIZE]);
    let ciphertext_end = encrypted.len() - TAG_SIZE;
    tag.copy_from_slice(&encrypted[ciphertext_end..]);

    let ciphertext = encrypted[NONCE_SIZE..ciphertext_end].to_vec();

    let encrypted_model = EncryptedModel {
        nonce,
        ciphertext,
        tag,
    };

    decrypt_model_aes_256_gcm(&encrypted_model, key)
}

pub fn calculate_checksum(data: &[u8]) -> [u8; 32] {
    calculate_sha256(data)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_model_manager_creation() {
        let manager = ModelManager::new("/models".into());
        assert_eq!(manager.list_models().len(), 0);
    }

    #[test]
    fn test_model_registration() {
        let mut manager = ModelManager::new("/models".into());
        let metadata = ModelMetadata {
            name: "test_model".into(),
            version: "1.0".into(),
            framework: ModelFramework::TensorFlowLite,
            size_bytes: 1024,
            checksum: [0u8; 32],
            encrypted: true,
        };

        assert!(manager.register_model(metadata).is_ok());
        assert_eq!(manager.list_models().len(), 1);
    }
}
