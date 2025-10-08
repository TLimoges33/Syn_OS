//! YubiKey Interface
//!
//! YubiKey PIV and FIDO2 support

use crate::{Result, HSMError, KeyType};
use std::collections::HashMap;
use uuid::Uuid;
use sha2::{Sha256, Digest};

/// YubiKey interface
pub struct YubiKeyInterface {
    connected: bool,
    serial_number: Option<String>,
    piv_keys: HashMap<Uuid, Vec<u8>>,
    pin_verified: bool,
}

impl YubiKeyInterface {
    pub fn initialize() -> Result<Self> {
        // In production, use yubikey crate to detect actual device
        // For now, create simulated interface
        Ok(Self {
            connected: false, // Simulated as not connected
            serial_number: Some("EMULATED-1234567".to_string()),
            piv_keys: HashMap::new(),
            pin_verified: false,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connected || self.check_usb_yubikey()
    }

    fn check_usb_yubikey(&self) -> bool {
        // Check for YubiKey USB device
        // In production: use libusb to detect Yubico VID/PID
        false
    }

    pub fn verify_pin(&mut self, _pin: &str) -> Result<bool> {
        // In production: verify actual PIN
        // For emulation: accept any PIN
        self.pin_verified = true;
        Ok(true)
    }

    pub fn generate_key(&mut self, key_id: Uuid, key_type: &KeyType) -> Result<()> {
        if !self.pin_verified {
            return Err(HSMError::YubiKeyError("PIN not verified".to_string()));
        }

        let key_material = match key_type {
            KeyType::RSA2048 => vec![0u8; 256],
            KeyType::ECC256 => vec![0u8; 32],
            KeyType::ECC384 => vec![0u8; 48],
            _ => return Err(HSMError::YubiKeyError(
                format!("Unsupported key type: {:?}", key_type)
            )),
        };

        self.piv_keys.insert(key_id, key_material);
        Ok(())
    }

    pub fn sign(&self, key_id: Uuid, data: &[u8]) -> Result<Vec<u8>> {
        if !self.pin_verified {
            return Err(HSMError::YubiKeyError("PIN not verified".to_string()));
        }

        let _key = self.piv_keys.get(&key_id)
            .ok_or_else(|| HSMError::YubiKeyError("Key not found".to_string()))?;

        // Simulate ECDSA signature
        let mut hasher = Sha256::new();
        hasher.update(data);
        hasher.update(key_id.as_bytes());
        hasher.update(b"YUBIKEY_SIGN");

        Ok(hasher.finalize().to_vec())
    }

    pub fn verify_signature(&self, key_id: Uuid, data: &[u8], signature: &[u8]) -> Result<bool> {
        let expected_sig = self.sign(key_id, data)?;
        Ok(signature == expected_sig.as_slice())
    }

    pub fn get_serial_number(&self) -> Option<&str> {
        self.serial_number.as_deref()
    }

    pub fn challenge_response(&self, challenge: &[u8]) -> Result<Vec<u8>> {
        // HMAC-SHA1 challenge-response
        let mut hasher = Sha256::new();
        hasher.update(challenge);
        hasher.update(b"YUBIKEY_SECRET");

        Ok(hasher.finalize().to_vec())
    }

    pub fn fido2_make_credential(
        &mut self,
        rp_id: &str,
        user_id: &[u8],
        _user_name: &str,
    ) -> Result<(Vec<u8>, Vec<u8>)> {
        if !self.pin_verified {
            return Err(HSMError::YubiKeyError("PIN not verified".to_string()));
        }

        // Generate credential ID
        let mut cred_hasher = Sha256::new();
        cred_hasher.update(rp_id.as_bytes());
        cred_hasher.update(user_id);
        let credential_id = cred_hasher.finalize().to_vec();

        // Generate public key
        let mut pubkey_hasher = Sha256::new();
        pubkey_hasher.update(&credential_id);
        pubkey_hasher.update(b"PUBLIC_KEY");
        let public_key = pubkey_hasher.finalize().to_vec();

        Ok((credential_id, public_key))
    }

    pub fn fido2_get_assertion(
        &self,
        rp_id: &str,
        credential_id: &[u8],
        client_data_hash: &[u8],
    ) -> Result<Vec<u8>> {
        if !self.pin_verified {
            return Err(HSMError::YubiKeyError("PIN not verified".to_string()));
        }

        // Generate assertion signature
        let mut hasher = Sha256::new();
        hasher.update(rp_id.as_bytes());
        hasher.update(credential_id);
        hasher.update(client_data_hash);
        hasher.update(b"ASSERTION");

        Ok(hasher.finalize().to_vec())
    }

    pub fn reset(&mut self) -> Result<()> {
        self.piv_keys.clear();
        self.pin_verified = false;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_yubikey_initialization() {
        let yk = YubiKeyInterface::initialize().unwrap();
        assert!(yk.get_serial_number().is_some());
    }

    #[test]
    fn test_pin_verification() {
        let mut yk = YubiKeyInterface::initialize().unwrap();
        assert!(yk.verify_pin("123456").unwrap());
        assert!(yk.pin_verified);
    }

    #[test]
    fn test_challenge_response() {
        let yk = YubiKeyInterface::initialize().unwrap();
        let response = yk.challenge_response(b"test_challenge").unwrap();
        assert!(!response.is_empty());
    }

    #[test]
    fn test_fido2_flow() {
        let mut yk = YubiKeyInterface::initialize().unwrap();
        yk.verify_pin("123456").unwrap();

        let (cred_id, _pubkey) = yk.fido2_make_credential(
            "example.com",
            b"user123",
            "testuser"
        ).unwrap();

        let assertion = yk.fido2_get_assertion(
            "example.com",
            &cred_id,
            b"client_data_hash"
        ).unwrap();

        assert!(!assertion.is_empty());
    }
}
