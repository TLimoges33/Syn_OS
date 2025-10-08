//! Intel SGX Enclave Interface
//!
//! Software Guard Extensions for trusted execution

use crate::{Result, HSMError, KeyType};
use std::collections::HashMap;
use uuid::Uuid;
use sha2::{Sha256, Digest};

/// SGX Enclave interface
pub struct SGXEnclaveInterface {
    enabled: bool,
    sealed_data: HashMap<Uuid, Vec<u8>>,
    enclave_keys: HashMap<Uuid, Vec<u8>>,
    mrenclave: Vec<u8>, // Measurement of enclave code
    mrsigner: Vec<u8>,  // Measurement of enclave signer
}

impl SGXEnclaveInterface {
    pub fn initialize() -> Result<Self> {
        // In production, check for SGX support via CPUID
        let mut mrenclave_hasher = Sha256::new();
        mrenclave_hasher.update(b"SYNOS_SGX_ENCLAVE_v1.0");
        let mrenclave = mrenclave_hasher.finalize().to_vec();

        let mut mrsigner_hasher = Sha256::new();
        mrsigner_hasher.update(b"SYNOS_SECURITY_TEAM");
        let mrsigner = mrsigner_hasher.finalize().to_vec();

        Ok(Self {
            enabled: Self::check_sgx_support(),
            sealed_data: HashMap::new(),
            enclave_keys: HashMap::new(),
            mrenclave,
            mrsigner,
        })
    }

    fn check_sgx_support() -> bool {
        // Check /dev/sgx_enclave or CPUID
        std::path::Path::new("/dev/sgx_enclave").exists()
    }

    pub fn is_enabled(&self) -> bool {
        self.enabled
    }

    pub fn seal_key(&mut self, key_id: Uuid, key_type: &KeyType) -> Result<()> {
        let key_material = match key_type {
            KeyType::AES256 => vec![0u8; 32],
            KeyType::ECC256 => vec![0u8; 32],
            _ => return Err(HSMError::SGXError(
                format!("Unsupported key type: {:?}", key_type)
            )),
        };

        // Seal with MRENCLAVE policy
        let mut sealed = Vec::new();
        sealed.extend_from_slice(&self.mrenclave);
        sealed.extend_from_slice(&key_material);

        self.enclave_keys.insert(key_id, sealed);
        Ok(())
    }

    pub fn seal_data(&mut self, data_id: Uuid, data: &[u8]) -> Result<()> {
        // Seal data to enclave identity
        let mut sealed = Vec::new();

        // Add MRENCLAVE (enclave measurement)
        sealed.extend_from_slice(&self.mrenclave);

        // Add MRSIGNER (signer measurement)
        sealed.extend_from_slice(&self.mrsigner);

        // Add nonce for freshness
        let nonce: Vec<u8> = (0..16).map(|_| rand::random::<u8>()).collect();
        sealed.extend_from_slice(&nonce);

        // Encrypt data (simulated with XOR for demo)
        let encrypted: Vec<u8> = data.iter()
            .zip(nonce.iter().cycle())
            .map(|(d, k)| d ^ k)
            .collect();

        sealed.extend_from_slice(&encrypted);

        self.sealed_data.insert(data_id, sealed);
        Ok(())
    }

    pub fn unseal_data(&self, data_id: Uuid) -> Result<Vec<u8>> {
        let sealed = self.sealed_data.get(&data_id)
            .ok_or_else(|| HSMError::SGXError("Sealed data not found".to_string()))?;

        // Verify measurements
        let mrenclave_size = self.mrenclave.len();
        let mrsigner_size = self.mrsigner.len();
        let nonce_size = 16;

        if sealed.len() < mrenclave_size + mrsigner_size + nonce_size {
            return Err(HSMError::SGXError("Invalid sealed data".to_string()));
        }

        if &sealed[..mrenclave_size] != self.mrenclave.as_slice() {
            return Err(HSMError::SGXError("MRENCLAVE mismatch".to_string()));
        }

        if &sealed[mrenclave_size..mrenclave_size + mrsigner_size] != self.mrsigner.as_slice() {
            return Err(HSMError::SGXError("MRSIGNER mismatch".to_string()));
        }

        // Extract nonce
        let nonce_start = mrenclave_size + mrsigner_size;
        let nonce = &sealed[nonce_start..nonce_start + nonce_size];

        // Decrypt data
        let encrypted = &sealed[nonce_start + nonce_size..];
        let decrypted: Vec<u8> = encrypted.iter()
            .zip(nonce.iter().cycle())
            .map(|(e, k)| e ^ k)
            .collect();

        Ok(decrypted)
    }

    pub fn generate_quote(&self, nonce: &[u8]) -> Result<(Vec<u8>, Vec<u8>)> {
        // Generate SGX quote (attestation evidence)
        let mut quote = Vec::new();

        // Quote structure (simplified)
        quote.extend_from_slice(&self.mrenclave);
        quote.extend_from_slice(&self.mrsigner);
        quote.extend_from_slice(nonce);

        // Add report data (user data in quote)
        let mut report_hasher = Sha256::new();
        report_hasher.update(&quote);
        let report_data = report_hasher.finalize();
        quote.extend_from_slice(&report_data);

        // Sign quote (simulated ECDSA)
        let mut sig_hasher = Sha256::new();
        sig_hasher.update(&quote);
        sig_hasher.update(b"SGX_QUOTING_KEY");
        let signature = sig_hasher.finalize().to_vec();

        Ok((quote, signature))
    }

    pub fn verify_quote(&self, quote: &[u8], signature: &[u8]) -> Result<bool> {
        // Verify quote signature
        let mut sig_hasher = Sha256::new();
        sig_hasher.update(quote);
        sig_hasher.update(b"SGX_QUOTING_KEY");
        let expected_sig = sig_hasher.finalize();

        Ok(signature == expected_sig.as_slice())
    }

    pub fn derive_key(&self, label: &str, context: &[u8]) -> Result<Vec<u8>> {
        // Derive key from enclave seal key
        let mut hasher = Sha256::new();
        hasher.update(&self.mrenclave);
        hasher.update(label.as_bytes());
        hasher.update(context);

        Ok(hasher.finalize().to_vec())
    }

    pub fn get_enclave_report(&self) -> EnclaveReport {
        EnclaveReport {
            mrenclave: self.mrenclave.clone(),
            mrsigner: self.mrsigner.clone(),
            isvprodid: 1,
            isvsvn: 1,
            attributes: vec![0x01, 0x00], // DEBUG | MODE64BIT
        }
    }
}

#[derive(Debug, Clone)]
pub struct EnclaveReport {
    pub mrenclave: Vec<u8>,
    pub mrsigner: Vec<u8>,
    pub isvprodid: u16,
    pub isvsvn: u16,
    pub attributes: Vec<u8>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sgx_initialization() {
        let sgx = SGXEnclaveInterface::initialize().unwrap();
        assert!(!sgx.mrenclave.is_empty());
    }

    #[test]
    fn test_seal_unseal() {
        let mut sgx = SGXEnclaveInterface::initialize().unwrap();
        let data_id = Uuid::new_v4();
        let secret = b"enclave_secret_data";

        sgx.seal_data(data_id, secret).unwrap();
        let unsealed = sgx.unseal_data(data_id).unwrap();

        assert_eq!(secret.as_slice(), unsealed.as_slice());
    }

    #[test]
    fn test_quote_generation() {
        let sgx = SGXEnclaveInterface::initialize().unwrap();
        let nonce = b"random_nonce_12345";

        let (quote, signature) = sgx.generate_quote(nonce).unwrap();

        assert!(sgx.verify_quote(&quote, &signature).unwrap());
    }

    #[test]
    fn test_key_derivation() {
        let sgx = SGXEnclaveInterface::initialize().unwrap();
        let key1 = sgx.derive_key("storage", b"context1").unwrap();
        let key2 = sgx.derive_key("storage", b"context2").unwrap();

        assert_ne!(key1, key2);
    }
}
