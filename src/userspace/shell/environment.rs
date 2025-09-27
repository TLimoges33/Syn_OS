//! # Environment Management for SynShell
//! 
//! Environment variable management with security considerations

use alloc::{collections::BTreeMap, string::String, vec::Vec};

/// Environment variable manager
#[derive(Debug, Clone)]
pub struct Environment {
    variables: BTreeMap<String, String>,
}

impl Environment {
    /// Create a new environment
    pub fn new() -> Self {
        Self {
            variables: BTreeMap::new(),
        }
    }

    /// Set an environment variable
    pub fn set(&mut self, key: String, value: String) {
        self.variables.insert(key, value);
    }

    /// Get an environment variable
    pub fn get(&self, key: &str) -> Option<String> {
        self.variables.get(key).cloned()
    }

    /// Remove an environment variable
    pub fn unset(&mut self, key: &str) {
        self.variables.remove(key);
    }

    /// Check if a variable exists
    pub fn contains(&self, key: &str) -> bool {
        self.variables.contains_key(key)
    }

    /// Get all environment variables
    pub fn iter(&self) -> impl Iterator<Item = (&String, &String)> {
        self.variables.iter()
    }

    /// Clear all environment variables
    pub fn clear(&mut self) {
        self.variables.clear();
    }

    /// Load default environment variables
    pub fn load_defaults(&mut self) {
        self.set("PATH".to_string(), "/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin".to_string());
        self.set("HOME".to_string(), "/home/user".to_string());
        self.set("SHELL".to_string(), "/bin/synshell".to_string());
        self.set("USER".to_string(), "user".to_string());
        self.set("TERM".to_string(), "xterm-256color".to_string());
        self.set("LANG".to_string(), "en_US.UTF-8".to_string());
        self.set("PWD".to_string(), "/".to_string());
        self.set("OLDPWD".to_string(), "/".to_string());
    }

    /// Load security-specific environment variables
    pub fn load_security_defaults(&mut self) {
        self.set("SYNOS_SECURITY_LEVEL".to_string(), "HIGH".to_string());
        self.set("SYNOS_AUDIT_ENABLED".to_string(), "1".to_string());
        self.set("SYNOS_NETWORK_MONITOR".to_string(), "1".to_string());
        self.set("SYNOS_LOG_LEVEL".to_string(), "INFO".to_string());
        self.set("SYNOS_ENCRYPTION_REQUIRED".to_string(), "1".to_string());
    }

    /// Export variables to a format suitable for process execution
    pub fn export_for_exec(&self) -> Vec<String> {
        self.variables.iter()
            .map(|(key, value)| format!("{}={}", key, value))
            .collect()
    }

    /// Import variables from environment strings
    pub fn import_from_strings(&mut self, env_strings: &[String]) {
        for env_string in env_strings {
            if let Some(eq_pos) = env_string.find('=') {
                let key = env_string[..eq_pos].to_string();
                let value = env_string[eq_pos + 1..].to_string();
                self.set(key, value);
            }
        }
    }

    /// Validate environment variable name
    pub fn validate_var_name(name: &str) -> bool {
        if name.is_empty() {
            return false;
        }

        // First character must be letter or underscore
        let first_char = name.chars().next().unwrap();
        if !first_char.is_ascii_alphabetic() && first_char != '_' {
            return false;
        }

        // Remaining characters must be alphanumeric or underscore
        name.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
    }

    /// Expand variable references in a string
    pub fn expand_string(&self, input: &str) -> String {
        let mut result = String::new();
        let mut chars = input.chars().peekable();

        while let Some(ch) = chars.next() {
            if ch == '$' {
                if chars.peek() == Some(&'{') {
                    // ${VAR} syntax
                    chars.next(); // consume '{'
                    let mut var_name = String::new();
                    
                    while let Some(ch) = chars.next() {
                        if ch == '}' {
                            break;
                        }
                        var_name.push(ch);
                    }
                    
                    if let Some(value) = self.get(&var_name) {
                        result.push_str(&value);
                    }
                } else {
                    // $VAR syntax
                    let mut var_name = String::new();
                    
                    while let Some(&ch) = chars.peek() {
                        if ch.is_ascii_alphanumeric() || ch == '_' {
                            var_name.push(chars.next().unwrap());
                        } else {
                            break;
                        }
                    }
                    
                    if !var_name.is_empty() {
                        if let Some(value) = self.get(&var_name) {
                            result.push_str(&value);
                        }
                    } else {
                        result.push('$');
                    }
                }
            } else {
                result.push(ch);
            }
        }

        result
    }

    /// Get environment size in bytes
    pub fn size(&self) -> usize {
        self.variables.iter()
            .map(|(k, v)| k.len() + v.len() + 2) // +2 for '=' and null terminator
            .sum()
    }

    /// Check if environment is within safe limits
    pub fn is_within_limits(&self) -> bool {
        const MAX_ENV_SIZE: usize = 32 * 1024; // 32KB limit
        const MAX_VAR_COUNT: usize = 256;
        
        self.size() <= MAX_ENV_SIZE && self.variables.len() <= MAX_VAR_COUNT
    }
}

impl Default for Environment {
    fn default() -> Self {
        let mut env = Self::new();
        env.load_defaults();
        env
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_environment_basic_operations() {
        let mut env = Environment::new();
        
        env.set("TEST_VAR".to_string(), "test_value".to_string());
        assert_eq!(env.get("TEST_VAR"), Some("test_value".to_string()));
        
        env.unset("TEST_VAR");
        assert_eq!(env.get("TEST_VAR"), None);
    }

    #[test]
    fn test_variable_name_validation() {
        assert!(Environment::validate_var_name("VALID_VAR"));
        assert!(Environment::validate_var_name("_VALID"));
        assert!(Environment::validate_var_name("VAR123"));
        
        assert!(!Environment::validate_var_name("123VAR"));
        assert!(!Environment::validate_var_name(""));
        assert!(!Environment::validate_var_name("VAR-NAME"));
    }

    #[test]
    fn test_string_expansion() {
        let mut env = Environment::new();
        env.set("USER".to_string(), "testuser".to_string());
        env.set("HOME".to_string(), "/home/testuser".to_string());
        
        assert_eq!(env.expand_string("Hello $USER"), "Hello testuser");
        assert_eq!(env.expand_string("${HOME}/documents"), "/home/testuser/documents");
        assert_eq!(env.expand_string("$UNDEFINED"), "");
    }

    #[test]
    fn test_environment_limits() {
        let mut env = Environment::new();
        
        // Add many variables to test limits
        for i in 0..100 {
            env.set(format!("VAR_{}", i), format!("value_{}", i));
        }
        
        assert!(env.is_within_limits());
    }
}
