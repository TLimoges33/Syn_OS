use anyhow::{anyhow, Result};
use ring::{digest, hmac, rand::SecureRandom};
use ed25519_dalek::{SigningKey, Signature, Signer, Verifier, SecretKey};
use rand_core::{OsRng, RngCore};
use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use spin::{RwLock, Mutex};
use core::sync::atomic::{AtomicU64, Ordering};

/// Get kernel timestamp (placeholder)
fn get_kernel_timestamp() -> u64 {
    // Use the global function from lib.rs
    crate::get_kernel_timestamp()
}

/// Authentication errors
#[derive(Debug)]
pub enum AuthError {
    InvalidCredentials,
    TokenExpired,
    TokenGenerationFailed,
    PermissionDenied,
    UserNotFound,
    InvalidToken,
}

impl core::fmt::Display for AuthError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            AuthError::InvalidCredentials => write!(f, "Invalid credentials"),
            AuthError::TokenExpired => write!(f, "Token expired"),
            AuthError::TokenGenerationFailed => write!(f, "Token generation failed"),
            AuthError::PermissionDenied => write!(f, "Permission denied"),
            AuthError::UserNotFound => write!(f, "User not found"),
            AuthError::InvalidToken => write!(f, "Invalid token"),
        }
    }
}

/// JWT-like token structure
#[derive(Debug, Clone)]
pub struct Token {
    pub user_id: u32,
    pub issued_at: u64,
    pub expires_at: u64,
    pub permissions: Vec<String>,
    pub signature: Vec<u8>,
}

/// User credentials
#[derive(Debug, Clone)]
pub struct User {
    pub id: u32,
    pub username: String,
    pub password_hash: Vec<u8>,
    pub salt: Vec<u8>,
    pub permissions: Vec<String>,
    pub created_at: u64,
    pub last_login: u64,
}

/// Authentication service
pub struct AuthService {
    users: RwLock<BTreeMap<u32, User>>,
    sessions: RwLock<BTreeMap<String, Token>>,
    signing_key: SigningKey,
    next_user_id: AtomicU64,
}

impl AuthService {
    /// Create new authentication service
    pub fn new() -> Result<Self, AuthError> {
        // Generate a random signing key for tokens
        let mut key_bytes = [0u8; 32];
        let rng = ring::rand::SystemRandom::new();
        rng.fill(&mut key_bytes).map_err(|_| AuthError::TokenGenerationFailed)?;
        
        let secret_key = SecretKey::from_bytes(&key_bytes);
        let signing_key = SigningKey::from_bytes(&secret_key);
        
        Ok(Self {
            users: RwLock::new(BTreeMap::new()),
            sessions: RwLock::new(BTreeMap::new()),
            signing_key,
            next_user_id: AtomicU64::new(1),
        })
    }
    
    /// Hash password with salt
    fn hash_password(&self, password: &str, salt: &[u8]) -> Result<Vec<u8>, AuthError> {
        let mut hash = [0u8; 32];
        let iterations = core::num::NonZeroU32::new(100_000).unwrap();
        
        ring::pbkdf2::derive(
            ring::pbkdf2::PBKDF2_HMAC_SHA256,
            iterations,
            salt,
            password.as_bytes(),
            &mut hash,
        );
        
        Ok(hash.to_vec())
    }
    
    /// Generate secure salt
    fn generate_salt(&self) -> Result<Vec<u8>, AuthError> {
        let mut salt = [0u8; 16];
        let rng = ring::rand::SystemRandom::new();
        rng.fill(&mut salt).map_err(|_| AuthError::TokenGenerationFailed)?;
        Ok(salt.to_vec())
    }
    
    /// Create a new user
    pub fn create_user(&self, username: &str, password: &str, permissions: Vec<String>) -> Result<u32, AuthError> {
        let salt = self.generate_salt()?;
        let password_hash = self.hash_password(password, &salt)?;
        
        let user_id = self.next_user_id.fetch_add(1, Ordering::SeqCst) as u32;
        let user = User {
            id: user_id,
            username: username.to_string(),
            password_hash,
            salt,
            permissions,
            created_at: get_kernel_timestamp(),
            last_login: 0,
        };
        
        self.users.write().insert(user_id, user);
        Ok(user_id)
    }
    
    /// Authenticate user and return a token
    pub fn authenticate(&self, username: &str, password: &str) -> Result<String, AuthError> {
        let users = self.users.read();
        
        // Find user by username
        let user = users.values()
            .find(|u| u.username == username)
            .ok_or(AuthError::UserNotFound)?;
        
        // Verify password
        let password_hash = self.hash_password(password, &user.salt)?;
        if password_hash != user.password_hash {
            return Err(AuthError::InvalidCredentials);
        }
        
        drop(users); // Release read lock
        
        // Generate token
        self.generate_token(user.id, user.permissions.clone())
    }
    
    /// Generate a signed token
    pub fn generate_token(&self, user_id: u32, permissions: Vec<String>) -> Result<String, AuthError> {
        let now = get_kernel_timestamp();
        let expires_at = now + 3600; // 1 hour expiration
        
        // Create token payload
        let payload = format!("{}:{}:{}:{:?}", user_id, now, expires_at, permissions);
        let signature = self.signing_key.sign(payload.as_bytes()).to_bytes().to_vec();
        
        let token = Token {
            user_id,
            issued_at: now,
            expires_at,
            permissions,
            signature,
        };
        
        // Store session
        let token_str = format!("{}:{}", user_id, now);
        self.sessions.write().insert(token_str.clone(), token);
        
        Ok(token_str)
    }
    
    /// Verify and parse a token
    pub fn verify_token(&self, token_str: &str) -> Result<Token, AuthError> {
        let sessions = self.sessions.read();
        let token = sessions.get(token_str).ok_or(AuthError::InvalidToken)?.clone();
        
        // Check expiration
        let now = get_kernel_timestamp();
        if now > token.expires_at {
            drop(sessions);
            self.sessions.write().remove(token_str); // Clean up expired token
            return Err(AuthError::TokenExpired);
        }
        
        // Verify signature
        let payload = format!("{}:{}:{}:{:?}", token.user_id, token.issued_at, token.expires_at, token.permissions);
        let expected_signature = self.signing_key.sign(payload.as_bytes()).to_bytes().to_vec();
        
        if token.signature != expected_signature {
            return Err(AuthError::InvalidToken);
        }
        
        Ok(token)
    }
    
    /// Check if user has permission
    pub fn has_permission(&self, token_str: &str, required_permission: &str) -> Result<bool, AuthError> {
        let token = self.verify_token(token_str)?;
        Ok(token.permissions.contains(&required_permission.to_string()))
    }
    
    /// Revoke a token (logout)
    pub fn revoke_token(&self, token_str: &str) -> Result<(), AuthError> {
        self.sessions.write().remove(token_str);
        Ok(())
    }
    
    /// Clean up expired tokens
    pub fn cleanup_expired_tokens(&self) {
        let now = get_kernel_timestamp();
        self.sessions.write().retain(|_, token| token.expires_at > now);
    }
    
    /// Get user information by ID
    pub fn get_user(&self, user_id: u32) -> Option<User> {
        self.users.read().get(&user_id).cloned()
    }
    
    /// Update user permissions
    pub fn update_permissions(&self, user_id: u32, permissions: Vec<String>) -> Result<(), AuthError> {
        if let Some(user) = self.users.write().get_mut(&user_id) {
            user.permissions = permissions;
            Ok(())
        } else {
            Err(AuthError::UserNotFound)
        }
    }
}

/// Global authentication service
static AUTH_SERVICE: Mutex<Option<AuthService>> = Mutex::new(None);

/// Initialize authentication module
pub fn init() {
    if let Ok(service) = AuthService::new() {
        *AUTH_SERVICE.lock() = Some(service);
    }
}

/// Authenticate user globally
pub fn authenticate_user(username: &str, password: &str) -> Result<String, AuthError> {
    if let Some(service) = AUTH_SERVICE.lock().as_ref() {
        service.authenticate(username, password)
    } else {
        Err(AuthError::TokenGenerationFailed)
    }
}

/// Verify token globally
pub fn verify_user_token(token: &str) -> Result<Token, AuthError> {
    if let Some(service) = AUTH_SERVICE.lock().as_ref() {
        service.verify_token(token)
    } else {
        Err(AuthError::InvalidToken)
    }
}

/// Create admin user on first run
pub fn create_admin_user() -> Result<String, AuthError> {
    if let Some(service) = AUTH_SERVICE.lock().as_ref() {
        let mut permissions = Vec::new();
        permissions.push("admin".to_string());
        
        let admin_id = service.create_user("admin", "admin123", permissions)?;
        service.generate_token(admin_id, vec!["user".to_string()])
    } else {
        Err(AuthError::TokenGenerationFailed)
    }
}
