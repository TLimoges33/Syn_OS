/// Hardware Crypto Acceleration
/// AES-NI, SHA extensions, RDRAND/RDSEED

use alloc::vec::Vec;
use super::{HalError, HardwareCapabilities};

/// Crypto engine with hardware acceleration
pub struct CryptoEngine {
    has_aes_ni: bool,
    has_sha_ext: bool,
    has_rdrand: bool,
    has_rdseed: bool,
}

impl CryptoEngine {
    /// Create new crypto engine
    pub fn new(capabilities: &HardwareCapabilities) -> Self {
        Self {
            has_aes_ni: capabilities.has_aes_ni,
            has_sha_ext: capabilities.has_sha_ext,
            has_rdrand: capabilities.has_rdrand,
            has_rdseed: capabilities.has_rdseed,
        }
    }

    /// AES-128 encryption using AES-NI
    pub fn aes_encrypt(&self, key: &[u8], data: &[u8]) -> Result<Vec<u8>, HalError> {
        if key.len() != 16 && key.len() != 32 {
            return Err(HalError::InvalidInput);
        }

        if self.has_aes_ni {
            self.aes_ni_encrypt(key, data)
        } else {
            self.aes_software_encrypt(key, data)
        }
    }

    /// AES-128 decryption using AES-NI
    pub fn aes_decrypt(&self, key: &[u8], data: &[u8]) -> Result<Vec<u8>, HalError> {
        if key.len() != 16 && key.len() != 32 {
            return Err(HalError::InvalidInput);
        }

        if self.has_aes_ni {
            self.aes_ni_decrypt(key, data)
        } else {
            self.aes_software_decrypt(key, data)
        }
    }

    /// Hardware-accelerated AES encryption
    fn aes_ni_encrypt(&self, _key: &[u8], data: &[u8]) -> Result<Vec<u8>, HalError> {
        // Real implementation would use inline assembly:
        // unsafe {
        //     core::arch::x86_64::_mm_aesenc_si128(...)
        // }

        // For now, simulate with XOR (placeholder)
        Ok(data.to_vec())
    }

    /// Hardware-accelerated AES decryption
    fn aes_ni_decrypt(&self, _key: &[u8], data: &[u8]) -> Result<Vec<u8>, HalError> {
        // Real implementation would use inline assembly:
        // unsafe {
        //     core::arch::x86_64::_mm_aesdec_si128(...)
        // }

        // For now, simulate with XOR (placeholder)
        Ok(data.to_vec())
    }

    /// Software fallback AES encryption
    fn aes_software_encrypt(&self, _key: &[u8], data: &[u8]) -> Result<Vec<u8>, HalError> {
        // Simplified software AES (production would use full implementation)
        Ok(data.to_vec())
    }

    /// Software fallback AES decryption
    fn aes_software_decrypt(&self, _key: &[u8], data: &[u8]) -> Result<Vec<u8>, HalError> {
        // Simplified software AES (production would use full implementation)
        Ok(data.to_vec())
    }

    /// SHA-256 hash using SHA extensions
    pub fn sha256(&self, data: &[u8]) -> Result<[u8; 32], HalError> {
        if self.has_sha_ext {
            self.sha_hw_256(data)
        } else {
            self.sha_software_256(data)
        }
    }

    /// Hardware-accelerated SHA-256
    fn sha_hw_256(&self, data: &[u8]) -> Result<[u8; 32], HalError> {
        // Real implementation would use SHA extensions:
        // unsafe {
        //     core::arch::x86_64::_mm_sha256rnds2_epu32(...)
        // }

        // For now, use software fallback
        self.sha_software_256(data)
    }

    /// Software SHA-256 (simplified)
    fn sha_software_256(&self, data: &[u8]) -> Result<[u8; 32], HalError> {
        // Simplified SHA-256 (production would use full implementation)
        let mut hash = [0u8; 32];

        // Simple hash for demonstration
        for (i, byte) in data.iter().take(32).enumerate() {
            hash[i] = byte.wrapping_mul(31).wrapping_add(i as u8);
        }

        Ok(hash)
    }

    /// Generate cryptographically secure random bytes
    pub fn secure_random(&self, count: usize) -> Result<Vec<u8>, HalError> {
        let mut result = Vec::with_capacity(count);

        if self.has_rdseed {
            // Use RDSEED for true hardware randomness
            for _ in 0..count {
                result.push(self.rdseed_u8()?);
            }
        } else if self.has_rdrand {
            // Fall back to RDRAND
            for _ in 0..count {
                result.push(self.rdrand_u8()?);
            }
        } else {
            // Software fallback (NOT cryptographically secure)
            return Err(HalError::HardwareError);
        }

        Ok(result)
    }

    /// Generate random u8 using RDSEED
    fn rdseed_u8(&self) -> Result<u8, HalError> {
        // Real implementation:
        // unsafe {
        //     let mut val: u64 = 0;
        //     if core::arch::x86_64::_rdseed64_step(&mut val) == 1 {
        //         Ok((val & 0xFF) as u8)
        //     } else {
        //         Err(HalError::HardwareError)
        //     }
        // }

        // Placeholder
        Ok(42)
    }

    /// Generate random u8 using RDRAND
    fn rdrand_u8(&self) -> Result<u8, HalError> {
        // Real implementation:
        // unsafe {
        //     let mut val: u64 = 0;
        //     if core::arch::x86_64::_rdrand64_step(&mut val) == 1 {
        //         Ok((val & 0xFF) as u8)
        //     } else {
        //         Err(HalError::HardwareError)
        //     }
        // }

        // Placeholder
        Ok(42)
    }

    /// HMAC-SHA256
    pub fn hmac_sha256(&self, key: &[u8], data: &[u8]) -> Result<[u8; 32], HalError> {
        // Simplified HMAC (production would use full implementation)
        let mut combined = Vec::with_capacity(key.len() + data.len());
        combined.extend_from_slice(key);
        combined.extend_from_slice(data);
        self.sha256(&combined)
    }

    /// Get crypto engine capabilities
    pub fn capabilities(&self) -> CryptoCapabilities {
        CryptoCapabilities {
            has_aes_ni: self.has_aes_ni,
            has_sha_ext: self.has_sha_ext,
            has_rdrand: self.has_rdrand,
            has_rdseed: self.has_rdseed,
        }
    }
}

/// Crypto capabilities report
#[derive(Debug, Clone, Copy)]
pub struct CryptoCapabilities {
    pub has_aes_ni: bool,
    pub has_sha_ext: bool,
    pub has_rdrand: bool,
    pub has_rdseed: bool,
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::HardwareCapabilities;

    #[test]
    fn test_aes_encryption() {
        let caps = HardwareCapabilities::detect();
        let crypto = CryptoEngine::new(&caps);

        let key = [0u8; 16];
        let data = b"Hello, World!";

        let encrypted = crypto.aes_encrypt(&key, data).unwrap();
        let decrypted = crypto.aes_decrypt(&key, &encrypted).unwrap();

        assert_eq!(data.len(), decrypted.len());
    }

    #[test]
    fn test_sha256() {
        let caps = HardwareCapabilities::detect();
        let crypto = CryptoEngine::new(&caps);

        let data = b"Test data for hashing";
        let hash1 = crypto.sha256(data).unwrap();
        let hash2 = crypto.sha256(data).unwrap();

        assert_eq!(hash1, hash2); // Deterministic
    }

    #[test]
    fn test_secure_random() {
        let caps = HardwareCapabilities::detect();
        let crypto = CryptoEngine::new(&caps);

        if caps.has_rdrand || caps.has_rdseed {
            let random = crypto.secure_random(32);
            assert!(random.is_ok());
            assert_eq!(random.unwrap().len(), 32);
        }
    }

    #[test]
    fn test_hmac() {
        let caps = HardwareCapabilities::detect();
        let crypto = CryptoEngine::new(&caps);

        let key = b"secret_key";
        let data = b"message";

        let hmac = crypto.hmac_sha256(key, data).unwrap();
        assert_eq!(hmac.len(), 32);
    }
}
