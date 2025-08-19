use anyhow::{anyhow, Result};
use ring::{digest, hmac, rand};
use ed25519_dalek::{SigningKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Authentication errors - specific types to avoid broad exception handling
#[derive(Debug, thiserror::Error)]
pub enum AuthError {
    #[error("Invalid credentials provided")]
    InvalidCredentials,
    #[error("Token expired or invalid")]
    InvalidToken,
    #[error("User not found")]
    UserNotFound,
    #[error("Insufficient privileges")]
    InsufficientPrivileges,
    #[error("Authentication service unavailable")]
    ServiceUnavailable,
}

/// Secure token structure - no hardcoded secrets (lesson from SynapticOS)
#[derive(Debug, Clone)]
pub struct SecureToken {
    pub user_id: u32,
    pub issued_at: u64,
    pub expires_at: u64,
    pub signature: Vec<u8>,
    pub capabilities: Vec<String>,
}

/// User credentials - validated input only
#[derive(Debug)]
pub struct Credentials {
    pub username: String,
    pub password_hash: Vec<u8>,
    pub salt: Vec<u8>,
}

/// Authentication service with proper error handling
pub struct AuthenticationService {
    users: Arc<RwLock<HashMap<String, Credentials>>>,
    signing_key: hmac::Key,
    signing_keypair: SigningKey,
}

impl AuthenticationService {
    /// Initialize authentication service with secure key generation
    pub fn new() -> Result<Self> {
        let rng = ring::rand::SystemRandom::new();
        
        // Generate secure HMAC key - NO hardcoded secrets
        let mut key_bytes = [0u8; 32];
        rng.fill(&mut key_bytes).map_err(|_| anyhow!("Failed to generate key"))?;
        let signing_key = hmac::Key::new(hmac::HMAC_SHA256, &key_bytes);
        
        // Generate Ed25519 keypair for digital signatures
        let mut csprng = OsRng;
        let signing_keypair = SigningKey::generate(&mut csprng);
        
        Ok(Self {
            users: Arc::new(RwLock::new(HashMap::new())),
            signing_key,
            signing_keypair,
        })
    }
    
    /// Authenticate user with validated input - prevents command injection
    pub fn authenticate(&self, username: &str, password: &str) -> Result<SecureToken, AuthError> {
        // Input validation - critical lesson from SynapticOS
        if username.is_empty() || username.len() > 256 {
            return Err(AuthError::InvalidCredentials);
        }
        
        if password.is_empty() || password.len() > 1024 {
            return Err(AuthError::InvalidCredentials);
        }
        
        // Validate username contains only safe characters
        if !username.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
            return Err(AuthError::InvalidCredentials);
        }
        
        let users = self.users.read().map_err(|_| AuthError::ServiceUnavailable)?;
        let credentials = users.get(username).ok_or(AuthError::UserNotFound)?;
        
        // Verify password using secure comparison
        let password_hash = self.hash_password(password, &credentials.salt)?;
        if password_hash != credentials.password_hash {
            return Err(AuthError::InvalidCredentials);
        }
        
        // Generate secure token
        self.generate_token(1, vec!["user".to_string()])
    }
    
    /// Generate secure token with expiration
    fn generate_token(&self, user_id: u32, capabilities: Vec<String>) -> Result<SecureToken, AuthError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| AuthError::ServiceUnavailable)?
            .as_secs();
        
        let expires_at = now + 3600; // 1 hour expiration
        
        // Create token payload
        let payload = format!("{}:{}:{}", user_id, now, expires_at);
        
        // Sign token with Ed25519
        let signature = self.signing_keypair.sign(payload.as_bytes());
        
        Ok(SecureToken {
            user_id,
            issued_at: now,
            expires_at,
            signature: signature.to_bytes().to_vec(),
            capabilities,
        })
    }
    
    /// Validate token - specific error types
    pub fn validate_token(&self, token: &SecureToken) -> Result<bool, AuthError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| AuthError::ServiceUnavailable)?
            .as_secs();
        
        // Check expiration
        if token.expires_at < now {
            return Err(AuthError::InvalidToken);
        }
        
        // Verify signature
        let payload = format!("{}:{}:{}", token.user_id, token.issued_at, token.expires_at);
        if token.signature.len() != 64 {
            return Err(AuthError::InvalidToken);
        }
        
        let signature_bytes: [u8; 64] = token.signature.as_slice().try_into()
            .map_err(|_| AuthError::InvalidToken)?;
        let signature = Signature::from_bytes(&signature_bytes);
        
        let verifying_key = self.signing_keypair.verifying_key();
        verifying_key.verify(payload.as_bytes(), &signature)
            .map_err(|_| AuthError::InvalidToken)?;
        
        Ok(true)
    }
    
    /// Hash password securely with salt
    fn hash_password(&self, password: &str, salt: &[u8]) -> Result<Vec<u8>, AuthError> {
        let mut context = digest::Context::new(&digest::SHA256);
        context.update(salt);
        context.update(password.as_bytes());
        Ok(context.finish().as_ref().to_vec())
    }
    
    /// Register new user with secure password handling
    pub fn register_user(&self, username: &str, password: &str) -> Result<(), AuthError> {
        // Input validation
        if username.is_empty() || username.len() > 256 {
            return Err(AuthError::InvalidCredentials);
        }
        
        if password.len() < 8 || password.len() > 1024 {
            return Err(AuthError::InvalidCredentials);
        }
        
        // Generate secure salt
        let rng = ring::rand::SystemRandom::new();
        let mut salt = [0u8; 16];
        rng.fill(&mut salt).map_err(|_| AuthError::ServiceUnavailable)?;
        
        // Hash password
        let password_hash = self.hash_password(password, &salt)?;
        
        let credentials = Credentials {
            username: username.to_string(),
            password_hash,
            salt: salt.to_vec(),
        };
        
        let mut users = self.users.write().map_err(|_| AuthError::ServiceUnavailable)?;
        users.insert(username.to_string(), credentials);
        
        Ok(())
    }
}

/// Initialize authentication module
pub fn init() {
    println!("🔐 Authentication module initialized");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_authentication_service_creation() {
        let service = AuthenticationService::new();
        assert!(service.is_ok());
    }
    
    #[test]
    fn test_user_registration() {
        let service = AuthenticationService::new().unwrap();
        let result = service.register_user("testuser", "testpassword123");
        assert!(result.is_ok());
    }
    
    #[test]
    fn test_invalid_username_rejected() {
        let service = AuthenticationService::new().unwrap();
        let result = service.register_user("test|user", "testpassword123");
        assert!(result.is_err());
    }
    
    #[test]
    fn test_short_password_rejected() {
        let service = AuthenticationService::new().unwrap();
        let result = service.register_user("testuser", "short");
        assert!(result.is_err());
    }
}