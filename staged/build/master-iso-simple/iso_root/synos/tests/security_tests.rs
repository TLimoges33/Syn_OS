use syn_security::{
    auth::{AuthenticationService, AuthError},
    validation::{InputValidator, ValidationError},
    crypto::{EncryptionService, CryptoError, KeyDerivation, SignatureService},
    monitoring::{SecurityMonitor, SecurityEvent, ThreatLevel},
    audit::{AuditLogger, AuditLevel, AuditEntry},
};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// Test suite for authentication module
#[cfg(test)]
mod auth_tests {
    use super::*;
    
    #[test]
    fn test_authentication_service_initialization() {
        let service = AuthenticationService::new();
        assert!(service.is_ok(), "Authentication service should initialize successfully");
    }
    
    #[test]
    fn test_user_registration_and_authentication() {
        let service = AuthenticationService::new().unwrap();
        
        // Register user
        let result = service.register_user("testuser", "securepassword123");
        assert!(result.is_ok(), "User registration should succeed");
        
        // Authenticate user
        let token_result = service.authenticate("testuser", "securepassword123");
        assert!(token_result.is_ok(), "Authentication should succeed with correct credentials");
        
        // Test token validation
        let token = token_result.unwrap();
        let validation_result = service.validate_token(&token);
        assert!(validation_result.is_ok(), "Token validation should succeed");
        assert!(validation_result.unwrap(), "Token should be valid");
    }
    
    #[test]
    fn test_authentication_failures() {
        let service = AuthenticationService::new().unwrap();
        
        // Test authentication without registration
        let result = service.authenticate("nonexistent", "password");
        assert!(matches!(result, Err(AuthError::UserNotFound)));
        
        // Register user then test wrong password
        service.register_user("testuser", "correct_password").unwrap();
        let result = service.authenticate("testuser", "wrong_password");
        assert!(matches!(result, Err(AuthError::InvalidCredentials)));
    }
    
    #[test]
    fn test_input_validation_on_registration() {
        let service = AuthenticationService::new().unwrap();
        
        // Test empty username
        let result = service.register_user("", "password123");
        assert!(matches!(result, Err(AuthError::InvalidCredentials)));
        
        // Test short password
        let result = service.register_user("testuser", "short");
        assert!(matches!(result, Err(AuthError::InvalidCredentials)));
        
        // Test username with dangerous characters
        let result = service.register_user("test|user", "password123");
        assert!(matches!(result, Err(AuthError::InvalidCredentials)));
    }
}

/// Test suite for input validation module
#[cfg(test)]
mod validation_tests {
    use super::*;
    
    #[test]
    fn test_username_validation() {
        let validator = InputValidator::new();
        
        // Valid usernames
        assert!(validator.validate_username("valid_user123").is_ok());
        assert!(validator.validate_username("user-name").is_ok());
        assert!(validator.validate_username("123user").is_ok());
        
        // Invalid usernames
        assert!(validator.validate_username("").is_err());
        assert!(validator.validate_username("user|name").is_err());
        assert!(validator.validate_username("user;name").is_err());
        assert!(validator.validate_username("user name").is_err());
    }
    
    #[test]
    fn test_command_injection_prevention() {
        let validator = InputValidator::new();
        
        // Common injection patterns
        let dangerous_inputs = vec![
            "test; rm -rf /",
            "test | cat /etc/passwd",
            "test && ls -la",
            "test `whoami`",
            "test $(id)",
            "test || echo 'hacked'",
        ];
        
        for input in dangerous_inputs {
            let result = validator.validate_string(input, "test");
            assert!(result.is_err(), "Should reject dangerous input: {}", input);
        }
    }
    
    #[test]
    fn test_directory_traversal_prevention() {
        let validator = InputValidator::new();
        
        let traversal_attempts = vec![
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "test/../admin/config",
            "/etc/passwd",
            "C:\\Windows\\System32",
        ];
        
        for path in traversal_attempts {
            let result = validator.validate_file_path(path);
            assert!(result.is_err(), "Should reject traversal attempt: {}", path);
        }
    }
    
    #[test]
    fn test_email_validation() {
        let validator = InputValidator::new();
        
        // Valid emails
        assert!(validator.validate_email("user@example.com").is_ok());
        assert!(validator.validate_email("test.email@domain.org").is_ok());
        
        // Invalid emails
        assert!(validator.validate_email("").is_err());
        assert!(validator.validate_email("invalid-email").is_err());
        assert!(validator.validate_email("@domain.com").is_err());
        assert!(validator.validate_email("user@").is_err());
        assert!(validator.validate_email("user@@domain.com").is_err());
    }
    
    #[test]
    fn test_port_validation() {
        let validator = InputValidator::new();
        
        // Valid ports
        assert!(validator.validate_port(80).is_ok());
        assert!(validator.validate_port(443).is_ok());
        assert!(validator.validate_port(8080).is_ok());
        
        // Invalid ports
        assert!(validator.validate_port(0).is_err());
        assert!(validator.validate_port(22).is_err()); // Reserved port
        assert!(validator.validate_port(23).is_err()); // Reserved port
    }
}

/// Test suite for cryptography module
#[cfg(test)]
mod crypto_tests {
    use super::*;
    
    #[test]
    fn test_encryption_decryption_roundtrip() {
        let service = EncryptionService::new().unwrap();
        let original_data = b"This is secret data that needs encryption";
        
        let encrypted = service.encrypt(original_data).unwrap();
        assert_ne!(encrypted.as_slice(), original_data, "Encrypted data should differ from original");
        
        let decrypted = service.decrypt(&encrypted).unwrap();
        assert_eq!(decrypted.as_slice(), original_data, "Decrypted data should match original");
    }
    
    #[test]
    fn test_string_encryption() {
        let service = EncryptionService::new().unwrap();
        let original_string = "Secret message with unicode: 🔒🛡️";
        
        let encrypted = service.encrypt_string(original_string).unwrap();
        let decrypted = service.decrypt_string(&encrypted).unwrap();
        
        assert_eq!(decrypted, original_string);
    }
    
    #[test]
    fn test_key_derivation_consistency() {
        let password = "test_password_123";
        let salt = KeyDerivation::generate_salt().unwrap();
        let iterations = 10000;
        
        let key1 = KeyDerivation::derive_key(password, &salt, iterations).unwrap();
        let key2 = KeyDerivation::derive_key(password, &salt, iterations).unwrap();
        
        assert_eq!(key1, key2, "Key derivation should be deterministic");
        
        // Different salt should produce different key
        let different_salt = KeyDerivation::generate_salt().unwrap();
        let key3 = KeyDerivation::derive_key(password, &different_salt, iterations).unwrap();
        assert_ne!(key1, key3, "Different salt should produce different key");
    }
    
    #[test]
    fn test_digital_signatures() {
        let service = SignatureService::new().unwrap();
        let data = b"Data to be signed";
        
        let signature = service.sign(data);
        assert!(!signature.is_empty(), "Signature should not be empty");
        
        let is_valid = service.verify(data, &signature).unwrap();
        assert!(is_valid, "Signature should be valid for original data");
        
        // Test with modified data
        let modified_data = b"Modified data";
        let is_valid_modified = service.verify(modified_data, &signature).unwrap();
        assert!(!is_valid_modified, "Signature should be invalid for modified data");
    }
    
    #[test]
    fn test_hash_functions() {
        use syn_security::crypto::HashService;
        
        let data = b"Data to hash";
        let hash1 = HashService::sha256(data);
        let hash2 = HashService::sha256(data);
        
        assert_eq!(hash1, hash2, "Hash should be deterministic");
        
        let different_data = b"Different data";
        let hash3 = HashService::sha256(different_data);
        assert_ne!(hash1, hash3, "Different data should produce different hash");
        
        // Test hash verification
        assert!(HashService::verify_hash(data, &hash1));
        assert!(!HashService::verify_hash(different_data, &hash1));
    }
}

/// Test suite for security monitoring module
#[cfg(test)]
mod monitoring_tests {
    use super::*;
    
    #[test]
    fn test_security_monitor_initialization() {
        let monitor = SecurityMonitor::new();
        assert_eq!(monitor.get_active_sessions_count(), 0);
    }
    
    #[test]
    fn test_brute_force_detection() {
        let monitor = SecurityMonitor::new();
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let source_ip = "192.168.1.100";
        
        // Record multiple failed login attempts
        for i in 0..7 {
            monitor.record_event(SecurityEvent::AuthenticationAttempt {
                username: "testuser".to_string(),
                success: false,
                source_ip: source_ip.to_string(),
                timestamp: timestamp + i,
            });
        }
        
        // Should detect brute force after multiple failures
        let events = monitor.get_events_by_type("suspicious_activity", 10);
        let has_brute_force = events.iter().any(|event| {
            if let SecurityEvent::SuspiciousActivity { event_type, .. } = event {
                event_type == "brute_force_attack"
            } else {
                false
            }
        });
        
        assert!(has_brute_force, "Should detect brute force attack");
    }
    
    #[test]
    fn test_privilege_escalation_detection() {
        let monitor = SecurityMonitor::new();
        let user_id = 123;
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        
        monitor.record_event(SecurityEvent::AuthorizationFailure {
            user_id,
            resource: "admin_panel".to_string(),
            action: "admin_access".to_string(),
            timestamp,
        });
        
        let events = monitor.get_events_by_type("suspicious_activity", 10);
        let has_privilege_escalation = events.iter().any(|event| {
            if let SecurityEvent::SuspiciousActivity { event_type, .. } = event {
                event_type == "privilege_escalation_attempt"
            } else {
                false
            }
        });
        
        assert!(has_privilege_escalation, "Should detect privilege escalation attempt");
    }
    
    #[test]
    fn test_threat_level_calculation() {
        let monitor = SecurityMonitor::new();
        let user_id = 456;
        
        // Initially should be low threat
        assert_eq!(monitor.get_threat_level(user_id), ThreatLevel::Low);
        
        // Record several authorization failures
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        for _ in 0..4 {
            monitor.record_event(SecurityEvent::AuthorizationFailure {
                user_id,
                resource: "secure_resource".to_string(),
                action: "access".to_string(),
                timestamp,
            });
        }
        
        // Should escalate to medium threat
        assert_eq!(monitor.get_threat_level(user_id), ThreatLevel::Medium);
    }
    
    #[test]
    fn test_session_management() {
        let monitor = SecurityMonitor::new();
        
        // Register session
        monitor.register_session(1, "session123".to_string(), "192.168.1.1".to_string());
        assert_eq!(monitor.get_active_sessions_count(), 1);
        
        // Update activity
        monitor.update_session_activity(1);
        assert_eq!(monitor.get_active_sessions_count(), 1);
        
        // Test session cleanup
        monitor.cleanup_expired_sessions(0); // Expire all sessions
        assert_eq!(monitor.get_active_sessions_count(), 0);
    }
    
    #[test]
    fn test_security_report_generation() {
        let monitor = SecurityMonitor::new();
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        
        // Record various events
        monitor.record_event(SecurityEvent::AuthenticationAttempt {
            username: "user1".to_string(),
            success: true,
            source_ip: "192.168.1.1".to_string(),
            timestamp,
        });
        
        monitor.record_event(SecurityEvent::SuspiciousActivity {
            event_type: "test_threat".to_string(),
            details: "Test threat for report".to_string(),
            severity: ThreatLevel::High,
            timestamp,
        });
        
        let report = monitor.generate_report();
        assert_eq!(report.total_events, 2);
        assert_eq!(report.high_severity_events, 1);
        assert!(report.events_by_type.contains_key("authentication"));
        assert!(report.events_by_type.contains_key("suspicious_activity"));
    }
}

/// Test suite for audit logging module
#[cfg(test)]
mod audit_tests {
    use super::*;
    use std::fs;
    
    #[test]
    fn test_audit_logger_creation() {
        let temp_path = "/tmp/test_audit.log";
        let logger = AuditLogger::new(temp_path);
        assert!(logger.is_ok(), "Audit logger should initialize successfully");
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_audit_entry_logging() {
        let temp_path = "/tmp/test_audit_entry.log";
        let logger = AuditLogger::new(temp_path).unwrap();
        
        let mut details = HashMap::new();
        details.insert("test_key".to_string(), "test_value".to_string());
        
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: AuditLevel::Info,
            component: "test_component".to_string(),
            user_id: Some(123),
            session_id: Some("session_456".to_string()),
            action: "test_action".to_string(),
            resource: "test_resource".to_string(),
            result: "success".to_string(),
            details,
        };
        
        let result = logger.log(entry);
        assert!(result.is_ok(), "Audit entry logging should succeed");
        
        // Verify file contents
        let contents = fs::read_to_string(temp_path).unwrap();
        assert!(contents.contains("test_action"));
        assert!(contents.contains("test_component"));
        assert!(contents.contains("user_id"));
        assert!(contents.contains("session_456"));
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_json_escaping() {
        let temp_path = "/tmp/test_json_escape.log";
        let logger = AuditLogger::new(temp_path).unwrap();
        
        let entry = AuditEntry {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            level: AuditLevel::Info,
            component: r#"component"with"quotes"#.to_string(),
            user_id: None,
            session_id: None,
            action: "test_action".to_string(),
            resource: "test_resource".to_string(),
            result: "success".to_string(),
            details: HashMap::new(),
        };
        
        let result = logger.log(entry);
        assert!(result.is_ok(), "Should handle JSON escaping correctly");
        
        // Verify escaped content
        let contents = fs::read_to_string(temp_path).unwrap();
        assert!(contents.contains(r#"\""#)); // Should contain escaped quotes
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_authentication_logging() {
        let temp_path = "/tmp/test_auth_audit.log";
        let logger = AuditLogger::new(temp_path).unwrap();
        
        // Test successful authentication
        logger.log_authentication(Some(123), "testuser", true, "192.168.1.1");
        
        // Test failed authentication
        logger.log_authentication(None, "baduser", false, "192.168.1.2");
        
        let contents = fs::read_to_string(temp_path).unwrap();
        assert!(contents.contains("testuser"));
        assert!(contents.contains("baduser"));
        assert!(contents.contains("192.168.1.1"));
        assert!(contents.contains("success"));
        assert!(contents.contains("failure"));
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
    
    #[test]
    fn test_security_incident_logging() {
        let temp_path = "/tmp/test_incident_audit.log";
        let logger = AuditLogger::new(temp_path).unwrap();
        
        logger.log_security_incident("brute_force_attack", AuditLevel::Critical, "Multiple failed login attempts detected");
        
        let contents = fs::read_to_string(temp_path).unwrap();
        assert!(contents.contains("brute_force_attack"));
        assert!(contents.contains("CRITICAL"));
        assert!(contents.contains("incident"));
        
        // Cleanup
        let _ = fs::remove_file(temp_path);
    }
}

/// Integration tests for security framework
#[cfg(test)]
mod integration_tests {
    use super::*;
    
    #[test]
    fn test_complete_authentication_flow() {
        // Initialize security framework
        let auth_service = AuthenticationService::new().unwrap();
        let monitor = SecurityMonitor::new();
        
        // Register user
        let username = "integration_user";
        let password = "secure_password_123";
        auth_service.register_user(username, password).unwrap();
        
        // Authenticate user
        let token = auth_service.authenticate(username, password).unwrap();
        
        // Validate token
        assert!(auth_service.validate_token(&token).unwrap());
        
        // Record authentication event
        monitor.record_event(SecurityEvent::AuthenticationAttempt {
            username: username.to_string(),
            success: true,
            source_ip: "192.168.1.100".to_string(),
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        });
        
        // Verify event was recorded
        let events = monitor.get_events_by_type("authentication", 1);
        assert_eq!(events.len(), 1);
    }
    
    #[test]
    fn test_security_violation_detection_flow() {
        let monitor = SecurityMonitor::new();
        let validator = InputValidator::new();
        
        // Test dangerous input
        let dangerous_input = "user; rm -rf /";
        let validation_result = validator.validate_username(dangerous_input);
        assert!(validation_result.is_err());
        
        // Record security event
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        monitor.record_event(SecurityEvent::SuspiciousActivity {
            event_type: "malicious_input".to_string(),
            details: format!("Dangerous input detected: {}", dangerous_input),
            severity: ThreatLevel::High,
            timestamp,
        });
        
        // Verify high severity events are captured
        let high_severity_events = monitor.get_events_by_severity(ThreatLevel::High, 10);
        assert!(!high_severity_events.is_empty());
    }
}