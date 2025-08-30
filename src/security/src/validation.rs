// Kernel-compatible validation module
use alloc::collections::BTreeSet;
use alloc::string::{String, ToString};
use alloc::vec::Vec;
use alloc::format;

/// Validation errors with specific types
#[derive(Debug)]
pub enum ValidationError {
    DangerousCharacters(String),
    TooLong,
    TooShort,
    InvalidFormat(String),
}

impl core::fmt::Display for ValidationError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            ValidationError::DangerousCharacters(msg) => write!(f, "Dangerous characters: {}", msg),
            ValidationError::TooLong => write!(f, "Input too long"),
            ValidationError::TooShort => write!(f, "Input too short"),
            ValidationError::InvalidFormat(msg) => write!(f, "Invalid format: {}", msg),
        }
    }
}

/// Input validator for security
pub struct InputValidator {
    dangerous_chars: BTreeSet<char>,
    max_length: usize,
}

impl InputValidator {
    /// Create new validator
    pub fn new() -> Self {
        let mut dangerous_chars = BTreeSet::new();
        // Add common injection characters
        for ch in "';\"<>&|`$(){}[]\\".chars() {
            dangerous_chars.insert(ch);
        }
        
        Self {
            dangerous_chars,
            max_length: 4096,
        }
    }
    
    /// Validate username input
    pub fn validate_username(&self, username: &str) -> Result<String, ValidationError> {
        if username.is_empty() || username.len() > 256 {
            return Err(ValidationError::TooLong);
        }
        
        // Check for dangerous characters
        for ch in username.chars() {
            if self.dangerous_chars.contains(&ch) {
                return Err(ValidationError::DangerousCharacters(
                    format!("Field 'username' contains dangerous character: {}", ch)
                ));
            }
        }
        
        // Only allow alphanumeric and safe symbols
        if !username.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-' || c == '.') {
            return Err(ValidationError::InvalidFormat("Invalid username format".to_string()));
        }
        
        Ok(username.to_string())
    }
    
    /// Validate path input to prevent traversal
    pub fn validate_path(&self, path: &str) -> Result<String, ValidationError> {
        if path.contains("..") || path.contains("//") {
            return Err(ValidationError::InvalidFormat("Path traversal detected".to_string()));
        }
        
        if path.len() > self.max_length {
            return Err(ValidationError::TooLong);
        }
        
        Ok(path.to_string())
    }
    
    /// Validate command input to prevent injection
    pub fn validate_command(&self, cmd: &str) -> Result<String, ValidationError> {
        if cmd.is_empty() {
            return Err(ValidationError::TooShort);
        }
        
        if cmd.len() > 1024 {
            return Err(ValidationError::TooLong);
        }
        
        // Check for shell injection characters
        for ch in cmd.chars() {
            if self.dangerous_chars.contains(&ch) {
                return Err(ValidationError::DangerousCharacters(
                    format!("Command contains dangerous character: {}", ch)
                ));
            }
        }
        
        Ok(cmd.to_string())
    }
    
    /// Validate email format (basic)
    pub fn validate_email(&self, email: &str) -> Result<String, ValidationError> {
        if email.is_empty() || email.len() > 320 {
            return Err(ValidationError::TooLong);
        }
        
        let parts: Vec<&str> = email.split('@').collect();
        if parts.len() != 2 {
            return Err(ValidationError::InvalidFormat("Invalid email format".to_string()));
        }
        
        let local = parts[0];
        let domain = parts[1];
        
        if local.is_empty() || domain.is_empty() {
            return Err(ValidationError::InvalidFormat("Empty email parts".to_string()));
        }
        
        if !domain.contains('.') {
            return Err(ValidationError::InvalidFormat("Invalid domain".to_string()));
        }
        
        Ok(email.to_string())
    }
    
    /// Validate URL to prevent SSRF and other attacks
    pub fn validate_url(&self, url: &str) -> Result<String, ValidationError> {
        if url.is_empty() || url.len() > 2048 {
            return Err(ValidationError::TooLong);
        }
        
        // Basic URL validation - starts with http/https
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(ValidationError::InvalidFormat("Invalid URL scheme".to_string()));
        }
        
        // Prevent local/private addresses in basic way
        if url.contains("localhost") || url.contains("127.0.0.1") || url.contains("::1") {
            return Err(ValidationError::InvalidFormat("Local URLs not allowed".to_string()));
        }
        
        Ok(url.to_string())
    }
    
    /// Sanitize input by removing dangerous characters
    pub fn sanitize_input(&self, input: &str) -> String {
        input.chars()
            .filter(|c| !self.dangerous_chars.contains(c))
            .collect()
    }
}

/// Global validator instance
static VALIDATOR: spin::Mutex<Option<InputValidator>> = spin::Mutex::new(None);

/// Initialize validation module
pub fn init() {
    let validator = InputValidator::new();
    *VALIDATOR.lock() = Some(validator);
}

/// Validate username globally
pub fn validate_username(username: &str) -> Result<String, ValidationError> {
    if let Some(validator) = VALIDATOR.lock().as_ref() {
        validator.validate_username(username)
    } else {
        Err(ValidationError::InvalidFormat("Validator not initialized".to_string()))
    }
}

/// Validate path globally  
pub fn validate_path(path: &str) -> Result<String, ValidationError> {
    if let Some(validator) = VALIDATOR.lock().as_ref() {
        validator.validate_path(path)
    } else {
        Err(ValidationError::InvalidFormat("Validator not initialized".to_string()))
    }
}
