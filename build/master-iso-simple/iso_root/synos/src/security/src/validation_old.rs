use anyhow::{anyhow, Result};
use alloc::collections::BTreeSet;
use alloc::string::{String, ToString};
use alloc::vec::Vec;
use alloc::format;

/// Input validation errors - specific types to avoid broad exception handling
#[derive(Debug, thiserror::Error)]
pub enum ValidationError {
    #[error("Input contains dangerous characters: {0}")]
    DangerousCharacters(String),
    #[error("Input exceeds maximum length: {actual} > {max}")]
    TooLong { actual: usize, max: usize },
    #[error("Input is empty when value required")]
    Empty,
    #[error("Input format is invalid: {0}")]
    InvalidFormat(String),
    #[error("Input contains potential command injection")]
    CommandInjection,
}

/// Dangerous characters that can lead to command injection
const DANGEROUS_CHARS: &[char] = &['|', '&', ';', '`', '$', '(', ')', '{', '}', '[', ']', '<', '>', '\'', '"', '\\'];

/// Command injection patterns to detect
const INJECTION_PATTERNS: &[&str] = &[
    "||", "&&", ";", "|", "$(",
    "$(", "`", "sh ", "bash ", "cmd ",
    "/bin/", "/etc/", "../", "./",
    "rm ", "del ", "format ", "kill ",
];

/// Input validator for preventing SynapticOS security vulnerabilities
pub struct InputValidator {
    max_string_length: usize,
    allow_special_chars: bool,
    dangerous_chars: HashSet<char>,
}

impl InputValidator {
    /// Create new validator with security-first defaults
    pub fn new() -> Self {
        Self {
            max_string_length: 1024,
            allow_special_chars: false,
            dangerous_chars: DANGEROUS_CHARS.iter().cloned().collect(),
        }
    }
    
    /// Create validator that allows some special characters (use with caution)
    pub fn lenient() -> Self {
        Self {
            max_string_length: 1024,
            allow_special_chars: true,
            dangerous_chars: ['|', '&', ';', '`', '$'].iter().cloned().collect(),
        }
    }
    
    /// Validate string input - prevents command injection from SynapticOS
    pub fn validate_string(&self, input: &str, field_name: &str) -> Result<String, ValidationError> {
        // Check for empty input
        if input.is_empty() {
            return Err(ValidationError::Empty);
        }
        
        // Check length
        if input.len() > self.max_string_length {
            return Err(ValidationError::TooLong {
                actual: input.len(),
                max: self.max_string_length,
            });
        }
        
        // Check for dangerous characters
        if !self.allow_special_chars {
            for &dangerous_char in &self.dangerous_chars {
                if input.contains(dangerous_char) {
                    return Err(ValidationError::DangerousCharacters(
                        format!("Field '{}' contains dangerous character: {}", field_name, dangerous_char)
                    ));
                }
            }
        }
        
        // Check for command injection patterns
        let input_lower = input.to_lowercase();
        for &pattern in INJECTION_PATTERNS {
            if input_lower.contains(pattern) {
                return Err(ValidationError::CommandInjection);
            }
        }
        
        // Return sanitized input
        Ok(input.to_string())
    }
    
    /// Validate username - alphanumeric, underscore, hyphen only
    pub fn validate_username(&self, username: &str) -> Result<String, ValidationError> {
        if username.is_empty() {
            return Err(ValidationError::Empty);
        }
        
        if username.len() > 64 {
            return Err(ValidationError::TooLong {
                actual: username.len(),
                max: 64,
            });
        }
        
        // Username must be alphanumeric with underscore/hyphen
        if !username.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
            return Err(ValidationError::InvalidFormat(
                "Username must contain only letters, numbers, underscore, or hyphen".to_string()
            ));
        }
        
        // Must start with letter or number
        if !username.chars().next().unwrap().is_alphanumeric() {
            return Err(ValidationError::InvalidFormat(
                "Username must start with letter or number".to_string()
            ));
        }
        
        Ok(username.to_string())
    }
    
    /// Validate email address
    pub fn validate_email(&self, email: &str) -> Result<String, ValidationError> {
        if email.is_empty() {
            return Err(ValidationError::Empty);
        }
        
        if email.len() > 254 {
            return Err(ValidationError::TooLong {
                actual: email.len(),
                max: 254,
            });
        }
        
        // Basic email validation
        if !email.contains('@') || email.split('@').count() != 2 {
            return Err(ValidationError::InvalidFormat(
                "Email must contain exactly one @ symbol".to_string()
            ));
        }
        
        let parts: Vec<&str> = email.split('@').collect();
        let local = parts[0];
        let domain = parts[1];
        
        if local.is_empty() || domain.is_empty() {
            return Err(ValidationError::InvalidFormat(
                "Email local and domain parts cannot be empty".to_string()
            ));
        }
        
        if !domain.contains('.') {
            return Err(ValidationError::InvalidFormat(
                "Email domain must contain at least one dot".to_string()
            ));
        }
        
        Ok(email.to_lowercase())
    }
    
    /// Validate numeric input
    pub fn validate_port(&self, port: u16) -> Result<u16, ValidationError> {
        if port == 0 {
            return Err(ValidationError::InvalidFormat(
                "Port cannot be 0".to_string()
            ));
        }
        
        if port < 1024 && port != 80 && port != 443 {
            return Err(ValidationError::InvalidFormat(
                "Ports below 1024 are reserved (except 80, 443)".to_string()
            ));
        }
        
        Ok(port)
    }
    
    /// Validate file path - prevent directory traversal
    pub fn validate_file_path(&self, path: &str) -> Result<String, ValidationError> {
        if path.is_empty() {
            return Err(ValidationError::Empty);
        }
        
        // Check for directory traversal attempts
        if path.contains("../") || path.contains("..\\") {
            return Err(ValidationError::InvalidFormat(
                "Path cannot contain directory traversal sequences".to_string()
            ));
        }
        
        // Check for absolute path attempts
        if path.starts_with('/') || path.starts_with('\\') || path.contains(':') {
            return Err(ValidationError::InvalidFormat(
                "Absolute paths not allowed".to_string()
            ));
        }
        
        // Check for null bytes
        if path.contains('\0') {
            return Err(ValidationError::DangerousCharacters(
                "Path cannot contain null bytes".to_string()
            ));
        }
        
        Ok(path.to_string())
    }
    
    /// Sanitize input by removing dangerous characters
    pub fn sanitize_input(&self, input: &str) -> String {
        input.chars()
            .filter(|c| !self.dangerous_chars.contains(c))
            .collect()
    }
}

/// Global validator instance
static mut GLOBAL_VALIDATOR: Option<InputValidator> = None;
static VALIDATOR_INIT: std::sync::Once = std::sync::Once::new();

/// Get global validator instance
pub fn get_validator() -> &'static InputValidator {
    unsafe {
        VALIDATOR_INIT.call_once(|| {
            GLOBAL_VALIDATOR = Some(InputValidator::new());
        });
        GLOBAL_VALIDATOR.as_ref().unwrap()
    }
}

/// Convenience function to validate strings
pub fn validate_string(input: &str, field_name: &str) -> Result<String, ValidationError> {
    get_validator().validate_string(input, field_name)
}

/// Convenience function to validate usernames
pub fn validate_username(username: &str) -> Result<String, ValidationError> {
    get_validator().validate_username(username)
}

/// Initialize validation module
pub fn init() {
    let _ = get_validator(); // Initialize global validator
    println!("🛡️ Input validation module initialized");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_valid_username() {
        let validator = InputValidator::new();
        let result = validator.validate_username("valid_user123");
        assert!(result.is_ok());
    }
    
    #[test]
    fn test_invalid_username_with_pipes() {
        let validator = InputValidator::new();
        let result = validator.validate_username("user|admin");
        assert!(result.is_err());
    }
    
    #[test]
    fn test_command_injection_detection() {
        let validator = InputValidator::new();
        let result = validator.validate_string("test; rm -rf /", "command");
        assert!(matches!(result, Err(ValidationError::CommandInjection)));
    }
    
    #[test]
    fn test_directory_traversal_detection() {
        let validator = InputValidator::new();
        let result = validator.validate_file_path("../../../etc/passwd");
        assert!(result.is_err());
    }
    
    #[test]
    fn test_valid_email() {
        let validator = InputValidator::new();
        let result = validator.validate_email("user@example.com");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "user@example.com");
    }
    
    #[test]
    fn test_port_validation() {
        let validator = InputValidator::new();
        assert!(validator.validate_port(8080).is_ok());
        assert!(validator.validate_port(80).is_ok());
        assert!(validator.validate_port(0).is_err());
        assert!(validator.validate_port(22).is_err()); // Reserved port
    }
}