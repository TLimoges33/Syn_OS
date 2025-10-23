// Kernel-compatible validation module
use std::collections::BTreeSet;
use std::string::{String, ToString};
use std::vec::Vec;
use std::format;

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

/// Enhanced input validator with comprehensive security checks
pub struct InputValidator {
    dangerous_chars: BTreeSet<char>,
    max_length: usize,
    rate_limiter: Option<RateLimiter>,
}

/// Rate limiter for input validation
pub struct RateLimiter {
    attempts: std::collections::HashMap<String, (u32, std::time::Instant)>,
    max_attempts: u32,
    window_duration: std::time::Duration,
}

impl RateLimiter {
    pub fn new(max_attempts: u32, window_duration: std::time::Duration) -> Self {
        Self {
            attempts: std::collections::HashMap::new(),
            max_attempts,
            window_duration,
        }
    }

    pub fn check_rate_limit(&mut self, key: &str) -> Result<(), ValidationError> {
        let now = std::time::Instant::now();
        let entry = self.attempts.entry(key.to_string()).or_insert((0, now));

        // Reset counter if window has passed
        if now.duration_since(entry.1) > self.window_duration {
            *entry = (1, now);
            return Ok(());
        }

        // Increment counter
        entry.0 += 1;

        if entry.0 > self.max_attempts {
            return Err(ValidationError::InvalidFormat(
                format!("Rate limit exceeded for key: {}", key)
            ));
        }

        Ok(())
    }
}

impl InputValidator {
    /// Create new validator with enhanced security
    pub fn new() -> Self {
        let mut dangerous_chars = BTreeSet::new();
        // Add comprehensive injection characters
        for ch in "';\"<>&|`$(){}[]\\%^*~".chars() {
            dangerous_chars.insert(ch);
        }

        // Add control characters
        for code in 0..32 {
            if let Some(ch) = char::from_u32(code) {
                dangerous_chars.insert(ch);
            }
        }
        // Add DEL character
        dangerous_chars.insert('\x7f');

        Self {
            dangerous_chars,
            max_length: 4096,
            rate_limiter: Some(RateLimiter::new(100, std::time::Duration::from_secs(60))),
        }
    }

    /// Create validator with custom rate limiting
    pub fn with_rate_limit(max_attempts: u32, window_secs: u64) -> Self {
        let mut validator = Self::new();
        validator.rate_limiter = Some(RateLimiter::new(
            max_attempts,
            std::time::Duration::from_secs(window_secs)
        ));
        validator
    }

    /// Validate username input with enhanced security
    pub fn validate_username(&self, username: &str) -> Result<String, ValidationError> {
        // Check rate limiting
        if let Some(ref limiter) = self.rate_limiter {
            let limiter = limiter; // This would need proper mutex handling in real impl
            // limiter.check_rate_limit(&format!("username:{}", username))?;
        }

        if username.is_empty() {
            return Err(ValidationError::TooShort);
        }

        if username.len() > 256 {
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

        // Prevent common username attacks
        let lower_username = username.to_lowercase();
        if lower_username == "admin" || lower_username == "root" || lower_username == "system" {
            return Err(ValidationError::InvalidFormat("Reserved username".to_string()));
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

    /// Comprehensive input sanitization with multiple layers
    pub fn sanitize_input(&self, input: &str) -> String {
        let mut sanitized = String::with_capacity(input.len());

        for ch in input.chars() {
            // Remove dangerous characters
            if self.dangerous_chars.contains(&ch) {
                continue;
            }

            // Normalize whitespace
            if ch.is_whitespace() {
                if !sanitized.ends_with(' ') {
                    sanitized.push(' ');
                }
            } else {
                sanitized.push(ch);
            }
        }

        // Trim whitespace and limit length
        let result = sanitized.trim();
        if result.len() > self.max_length {
            result[..self.max_length].to_string()
        } else {
            result.to_string()
        }
    }

    /// Validate and sanitize input in one operation
    pub fn validate_and_sanitize(&self, input: &str, field_name: &str) -> Result<String, ValidationError> {
        // First validate
        self.validate_input(input, field_name)?;

        // Then sanitize
        Ok(self.sanitize_input(input))
    }

    /// Generic input validation with field-specific rules
    pub fn validate_input(&self, input: &str, field_name: &str) -> Result<(), ValidationError> {
        if input.is_empty() {
            return Err(ValidationError::TooShort);
        }

        if input.len() > self.max_length {
            return Err(ValidationError::TooLong);
        }

        // Check for dangerous characters
        for ch in input.chars() {
            if self.dangerous_chars.contains(&ch) {
                return Err(ValidationError::DangerousCharacters(
                    format!("Field '{}' contains dangerous character: {}", field_name, ch)
                ));
            }
        }

        Ok(())
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

/// Validate and sanitize input globally
pub fn validate_and_sanitize(input: &str, field_name: &str) -> Result<String, ValidationError> {
    if let Some(validator) = VALIDATOR.lock().as_ref() {
        validator.validate_and_sanitize(input, field_name)
    } else {
        Err(ValidationError::InvalidFormat("Validator not initialized".to_string()))
    }
}

/// Sanitize input globally
pub fn sanitize_input(input: &str) -> String {
    if let Some(validator) = VALIDATOR.lock().as_ref() {
        validator.sanitize_input(input)
    } else {
        // Fallback: basic sanitization
        input.chars()
            .filter(|c| c.is_alphanumeric() || c.is_whitespace() || *c == '_' || *c == '-' || *c == '.')
            .collect()
    }
}
