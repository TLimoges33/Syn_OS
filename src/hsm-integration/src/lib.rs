//! SynOS Hardware Security Module (HSM) Integration
//!
//! Unified interface for TPM 2.0, YubiKey, and Intel SGX

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

pub mod tpm;
pub mod yubikey;
pub mod sgx;
pub mod secure_storage;

pub use tpm::TPMInterface;
pub use yubikey::YubiKeyInterface;
pub use sgx::SGXEnclaveInterface;
pub use secure_storage::SecureKeyStorage;

/// HSM Manager for unified hardware security operations
pub struct HSMManager {
    tpm: Option<TPMInterface>,
    yubikey: Option<YubiKeyInterface>,
    sgx: Option<SGXEnclaveInterface>,
    secure_storage: SecureKeyStorage,
    attestation_log: Vec<AttestationRecord>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttestationRecord {
    pub id: Uuid,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub device_type: DeviceType,
    pub measurement: Vec<u8>,
    pub pcr_values: Option<HashMap<u8, Vec<u8>>>,
    pub attestation_signature: Vec<u8>,
    pub nonce: Vec<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum DeviceType {
    TPM,
    YubiKey,
    SGX,
    SoftwareEmulation,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecureKey {
    pub id: Uuid,
    pub key_type: KeyType,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub hsm_backed: bool,
    pub device_type: Option<DeviceType>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum KeyType {
    RSA2048,
    RSA4096,
    ECC256,
    ECC384,
    AES256,
    HMAC,
}

pub type Result<T> = std::result::Result<T, HSMError>;

#[derive(Debug, thiserror::Error)]
pub enum HSMError {
    #[error("TPM error: {0}")]
    TPMError(String),

    #[error("YubiKey error: {0}")]
    YubiKeyError(String),

    #[error("SGX error: {0}")]
    SGXError(String),

    #[error("Key storage error: {0}")]
    StorageError(String),

    #[error("Attestation failed: {0}")]
    AttestationFailed(String),

    #[error("Device not available: {0:?}")]
    DeviceNotAvailable(DeviceType),
}

impl HSMManager {
    pub fn new() -> Self {
        Self {
            tpm: TPMInterface::initialize().ok(),
            yubikey: YubiKeyInterface::initialize().ok(),
            sgx: SGXEnclaveInterface::initialize().ok(),
            secure_storage: SecureKeyStorage::new(),
            attestation_log: Vec::new(),
        }
    }

    /// Initialize all available HSM devices
    pub fn initialize_all(&mut self) -> Result<HSMStatus> {
        let mut status = HSMStatus {
            tpm_available: false,
            yubikey_available: false,
            sgx_available: false,
            secure_boot_enabled: false,
        };

        if let Some(tpm) = &self.tpm {
            status.tpm_available = tpm.is_available();
            status.secure_boot_enabled = tpm.verify_secure_boot().unwrap_or(false);
        }

        if let Some(yk) = &self.yubikey {
            status.yubikey_available = yk.is_connected();
        }

        if let Some(sgx) = &self.sgx {
            status.sgx_available = sgx.is_enabled();
        }

        Ok(status)
    }

    /// Generate key in HSM
    pub fn generate_key(&mut self, key_type: KeyType, device: DeviceType) -> Result<SecureKey> {
        let key_id = Uuid::new_v4();

        match device {
            DeviceType::TPM => {
                let tpm = self.tpm.as_mut()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::TPM))?;

                tpm.generate_key(key_id, &key_type)?;

                Ok(SecureKey {
                    id: key_id,
                    key_type,
                    created_at: chrono::Utc::now(),
                    hsm_backed: true,
                    device_type: Some(DeviceType::TPM),
                })
            }
            DeviceType::YubiKey => {
                let yk = self.yubikey.as_mut()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::YubiKey))?;

                yk.generate_key(key_id, &key_type)?;

                Ok(SecureKey {
                    id: key_id,
                    key_type,
                    created_at: chrono::Utc::now(),
                    hsm_backed: true,
                    device_type: Some(DeviceType::YubiKey),
                })
            }
            DeviceType::SGX => {
                let sgx = self.sgx.as_mut()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::SGX))?;

                sgx.seal_key(key_id, &key_type)?;

                Ok(SecureKey {
                    id: key_id,
                    key_type,
                    created_at: chrono::Utc::now(),
                    hsm_backed: true,
                    device_type: Some(DeviceType::SGX),
                })
            }
            DeviceType::SoftwareEmulation => {
                self.secure_storage.generate_software_key(key_id, &key_type)?;

                Ok(SecureKey {
                    id: key_id,
                    key_type,
                    created_at: chrono::Utc::now(),
                    hsm_backed: false,
                    device_type: Some(DeviceType::SoftwareEmulation),
                })
            }
        }
    }

    /// Sign data with HSM-backed key
    pub fn sign(&self, key_id: Uuid, data: &[u8], device: DeviceType) -> Result<Vec<u8>> {
        match device {
            DeviceType::TPM => {
                let tpm = self.tpm.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::TPM))?;
                tpm.sign(key_id, data)
            }
            DeviceType::YubiKey => {
                let yk = self.yubikey.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::YubiKey))?;
                yk.sign(key_id, data)
            }
            _ => Err(HSMError::DeviceNotAvailable(device)),
        }
    }

    /// Perform remote attestation
    pub fn attest(&mut self, nonce: Vec<u8>, device: DeviceType) -> Result<AttestationRecord> {
        let record = match device {
            DeviceType::TPM => {
                let tpm = self.tpm.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::TPM))?;

                let (measurement, pcr_values, signature) = tpm.create_attestation(&nonce)?;

                AttestationRecord {
                    id: Uuid::new_v4(),
                    timestamp: chrono::Utc::now(),
                    device_type: DeviceType::TPM,
                    measurement,
                    pcr_values: Some(pcr_values),
                    attestation_signature: signature,
                    nonce,
                }
            }
            DeviceType::SGX => {
                let sgx = self.sgx.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::SGX))?;

                let (quote, signature) = sgx.generate_quote(&nonce)?;

                AttestationRecord {
                    id: Uuid::new_v4(),
                    timestamp: chrono::Utc::now(),
                    device_type: DeviceType::SGX,
                    measurement: quote,
                    pcr_values: None,
                    attestation_signature: signature,
                    nonce,
                }
            }
            _ => return Err(HSMError::DeviceNotAvailable(device)),
        };

        self.attestation_log.push(record.clone());
        Ok(record)
    }

    /// Verify attestation
    pub fn verify_attestation(&self, record: &AttestationRecord) -> Result<bool> {
        match record.device_type {
            DeviceType::TPM => {
                let tpm = self.tpm.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::TPM))?;

                tpm.verify_attestation(&record.measurement, &record.attestation_signature)
            }
            DeviceType::SGX => {
                let sgx = self.sgx.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::SGX))?;

                sgx.verify_quote(&record.measurement, &record.attestation_signature)
            }
            _ => Err(HSMError::AttestationFailed("Unsupported device type".to_string())),
        }
    }

    /// Store secret in HSM
    pub fn store_secret(&mut self, secret: &[u8], device: DeviceType) -> Result<Uuid> {
        let secret_id = Uuid::new_v4();

        match device {
            DeviceType::TPM => {
                let tpm = self.tpm.as_mut()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::TPM))?;
                tpm.seal_data(secret_id, secret)?;
            }
            DeviceType::SGX => {
                let sgx = self.sgx.as_mut()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::SGX))?;
                sgx.seal_data(secret_id, secret)?;
            }
            _ => {
                self.secure_storage.store_encrypted(secret_id, secret)?;
            }
        }

        Ok(secret_id)
    }

    /// Retrieve secret from HSM
    pub fn retrieve_secret(&self, secret_id: Uuid, device: DeviceType) -> Result<Vec<u8>> {
        match device {
            DeviceType::TPM => {
                let tpm = self.tpm.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::TPM))?;
                tpm.unseal_data(secret_id)
            }
            DeviceType::SGX => {
                let sgx = self.sgx.as_ref()
                    .ok_or(HSMError::DeviceNotAvailable(DeviceType::SGX))?;
                sgx.unseal_data(secret_id)
            }
            _ => {
                self.secure_storage.retrieve_encrypted(secret_id)
            }
        }
    }

    /// Get attestation log
    pub fn get_attestation_log(&self) -> &[AttestationRecord] {
        &self.attestation_log
    }

    /// Get HSM statistics
    pub fn get_statistics(&self) -> HSMStatistics {
        HSMStatistics {
            total_keys: self.secure_storage.count_keys(),
            attestations_performed: self.attestation_log.len(),
            tpm_enabled: self.tpm.is_some(),
            yubikey_connected: self.yubikey.as_ref().map(|yk| yk.is_connected()).unwrap_or(false),
            sgx_available: self.sgx.as_ref().map(|sgx| sgx.is_enabled()).unwrap_or(false),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HSMStatus {
    pub tpm_available: bool,
    pub yubikey_available: bool,
    pub sgx_available: bool,
    pub secure_boot_enabled: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HSMStatistics {
    pub total_keys: usize,
    pub attestations_performed: usize,
    pub tpm_enabled: bool,
    pub yubikey_connected: bool,
    pub sgx_available: bool,
}

impl Default for HSMManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hsm_manager_creation() {
        let manager = HSMManager::new();
        let stats = manager.get_statistics();
        assert_eq!(stats.total_keys, 0);
    }

    #[test]
    fn test_software_key_generation() {
        let mut manager = HSMManager::new();
        let key = manager.generate_key(KeyType::AES256, DeviceType::SoftwareEmulation).unwrap();
        assert_eq!(key.key_type, KeyType::AES256);
        assert!(!key.hsm_backed);
    }
}
