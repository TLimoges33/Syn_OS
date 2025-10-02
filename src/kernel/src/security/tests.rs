// Security Module Tests - Demonstrates security testing expertise

use super::*;

#[test]
fn test_security_context_creation() {
    let context = SecurityContext::new(1000, 1000);
    assert_eq!(context.user_id, 1000);
    assert_eq!(context.group_id, 1000);
    assert_eq!(context.capabilities.len(), 0);
    assert_eq!(context.security_level, SecurityLevel::Public);
    assert!(!context.trusted);
}

#[test]
fn test_capability_management() {
    let mut context = SecurityContext::new(1000, 1000);

    // Initially no capabilities
    assert!(!context.has_capability(SecurityCapability::FileRead));

    // Add capability
    context.add_capability(SecurityCapability::FileRead);
    assert!(context.has_capability(SecurityCapability::FileRead));

    // Adding same capability twice doesn't duplicate
    context.add_capability(SecurityCapability::FileRead);
    assert_eq!(context.capabilities.len(), 1);
}

#[test]
fn test_security_level_ordering() {
    assert!(SecurityLevel::Public < SecurityLevel::Basic);
    assert!(SecurityLevel::Enhanced < SecurityLevel::Paranoid);
    assert!(SecurityLevel::TopSecret > SecurityLevel::Public);
}

#[test]
fn test_security_manager_access_validation() {
    let manager = SecurityManager::new();

    let mut context = SecurityContext::new(1000, 1000);
    context.add_capability(SecurityCapability::FileRead);
    context.set_security_level(SecurityLevel::Enhanced);

    // Should succeed with proper capability and level
    assert!(manager.validate_access(
        &context,
        SecurityCapability::FileRead,
        SecurityLevel::Basic
    ));

    // Should fail with insufficient security level
    assert!(!manager.validate_access(
        &context,
        SecurityCapability::FileRead,
        SecurityLevel::TopSecret
    ));

    // Should fail without required capability
    assert!(!manager.validate_access(
        &context,
        SecurityCapability::SystemCall,
        SecurityLevel::Basic
    ));
}

#[test]
fn test_security_severity_ordering() {
    assert!(SecuritySeverity::Info < SecuritySeverity::Warning);
    assert!(SecuritySeverity::Critical < SecuritySeverity::Emergency);
    assert!(SecuritySeverity::Emergency > SecuritySeverity::Info);
}

#[test]
fn test_default_security_config() {
    let config = SecurityConfig::default();
    assert!(config.hardening_enabled);
    assert!(config.threat_detection_enabled);
    assert!(config.audit_logging_enabled);
    assert_eq!(config.security_level, SecurityLevel::Enhanced);
}

#[test]
fn test_security_context_trusted_flag() {
    let mut context = SecurityContext::new(0, 0);  // Root user
    assert!(!context.trusted);

    context.set_trusted(true);
    assert!(context.trusted);
}

#[test]
fn test_capability_enum_equality() {
    assert_eq!(SecurityCapability::FileRead, SecurityCapability::FileRead);
    assert_ne!(SecurityCapability::FileRead, SecurityCapability::FileWrite);
}

#[test]
fn test_enforcement_level_comparison() {
    assert_ne!(EnforcementLevel::Advisory, EnforcementLevel::Blocking);
    assert_eq!(EnforcementLevel::Terminating, EnforcementLevel::Terminating);
}

#[test]
fn test_security_event_type_variants() {
    let event_type = SecurityEventType::PrivilegeEscalation;
    assert_eq!(event_type, SecurityEventType::PrivilegeEscalation);
    assert_ne!(event_type, SecurityEventType::AccessViolation);
}
