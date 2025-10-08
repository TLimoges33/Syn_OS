/// Security Policy Enforcer
/// Real-time enforcement of security policies

use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Security policy
#[derive(Debug, Clone)]
pub struct SecurityPolicy {
    pub policy_id: u64,
    pub name: &'static str,
    pub rules: Vec<PolicyRule>,
    pub enabled: bool,
}

/// Policy rule
#[derive(Debug, Clone)]
pub struct PolicyRule {
    pub rule_type: RuleType,
    pub action: PolicyAction,
    pub priority: u8, // 0-255, higher = more important
}

/// Rule types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RuleType {
    NetworkAccess,
    FileSystemAccess,
    ProcessExecution,
    MemoryAccess,
    SystemCall,
    IpcCommunication,
}

/// Policy actions
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PolicyAction {
    Allow,
    Deny,
    AuditAllow, // Allow but log
    AuditDeny,  // Deny and log
}

/// Policy enforcement result
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EnforcementResult {
    Allowed,
    Denied,
    AuditAllowed,
    AuditDenied,
}

/// Policy enforcer
pub struct PolicyEnforcer {
    policies: BTreeMap<u64, SecurityPolicy>,
    next_policy_id: u64,
    enforcement_count: u64,
    violation_count: u64,
}

impl PolicyEnforcer {
    /// Create new policy enforcer
    pub fn new() -> Self {
        let mut enforcer = Self {
            policies: BTreeMap::new(),
            next_policy_id: 1,
            enforcement_count: 0,
            violation_count: 0,
        };

        // Load default policies
        enforcer.load_default_policies();

        enforcer
    }

    /// Load default security policies
    fn load_default_policies(&mut self) {
        // Strict network policy
        let network_policy = SecurityPolicy {
            policy_id: self.next_policy_id,
            name: "Strict Network Access",
            rules: vec![
                PolicyRule {
                    rule_type: RuleType::NetworkAccess,
                    action: PolicyAction::AuditAllow,
                    priority: 100,
                },
            ],
            enabled: true,
        };
        self.policies.insert(self.next_policy_id, network_policy);
        self.next_policy_id += 1;

        // File system protection
        let fs_policy = SecurityPolicy {
            policy_id: self.next_policy_id,
            name: "File System Protection",
            rules: vec![
                PolicyRule {
                    rule_type: RuleType::FileSystemAccess,
                    action: PolicyAction::AuditAllow,
                    priority: 90,
                },
            ],
            enabled: true,
        };
        self.policies.insert(self.next_policy_id, fs_policy);
        self.next_policy_id += 1;

        // Process execution control
        let exec_policy = SecurityPolicy {
            policy_id: self.next_policy_id,
            name: "Process Execution Control",
            rules: vec![
                PolicyRule {
                    rule_type: RuleType::ProcessExecution,
                    action: PolicyAction::AuditAllow,
                    priority: 95,
                },
            ],
            enabled: true,
        };
        self.policies.insert(self.next_policy_id, exec_policy);
        self.next_policy_id += 1;
    }

    /// Enforce policy for operation
    pub fn enforce(&mut self, rule_type: RuleType, _pid: u64, _context: &[u8]) -> EnforcementResult {
        self.enforcement_count += 1;

        // Find applicable policies
        let mut highest_priority_action = PolicyAction::Allow;
        let mut highest_priority = 0u8;

        for policy in self.policies.values() {
            if !policy.enabled {
                continue;
            }

            for rule in &policy.rules {
                if rule.rule_type == rule_type && rule.priority > highest_priority {
                    highest_priority = rule.priority;
                    highest_priority_action = rule.action;
                }
            }
        }

        // Convert action to result
        let result = match highest_priority_action {
            PolicyAction::Allow => EnforcementResult::Allowed,
            PolicyAction::Deny => {
                self.violation_count += 1;
                EnforcementResult::Denied
            }
            PolicyAction::AuditAllow => EnforcementResult::AuditAllowed,
            PolicyAction::AuditDeny => {
                self.violation_count += 1;
                EnforcementResult::AuditDenied
            }
        };

        result
    }

    /// Add custom policy
    pub fn add_policy(&mut self, name: &'static str, rules: Vec<PolicyRule>) -> u64 {
        let policy_id = self.next_policy_id;
        self.next_policy_id += 1;

        let policy = SecurityPolicy {
            policy_id,
            name,
            rules,
            enabled: true,
        };

        self.policies.insert(policy_id, policy);

        policy_id
    }

    /// Enable policy
    pub fn enable_policy(&mut self, policy_id: u64) -> Result<(), &'static str> {
        let policy = self.policies.get_mut(&policy_id)
            .ok_or("Policy not found")?;

        policy.enabled = true;
        Ok(())
    }

    /// Disable policy
    pub fn disable_policy(&mut self, policy_id: u64) -> Result<(), &'static str> {
        let policy = self.policies.get_mut(&policy_id)
            .ok_or("Policy not found")?;

        policy.enabled = false;
        Ok(())
    }

    /// Remove policy
    pub fn remove_policy(&mut self, policy_id: u64) -> Result<(), &'static str> {
        self.policies.remove(&policy_id)
            .ok_or("Policy not found")?;
        Ok(())
    }

    /// Get enforcement statistics
    pub fn get_statistics(&self) -> PolicyStatistics {
        PolicyStatistics {
            total_policies: self.policies.len(),
            active_policies: self.policies.values().filter(|p| p.enabled).count(),
            enforcement_count: self.enforcement_count,
            violation_count: self.violation_count,
        }
    }
}

/// Policy enforcement statistics
#[derive(Debug, Clone)]
pub struct PolicyStatistics {
    pub total_policies: usize,
    pub active_policies: usize,
    pub enforcement_count: u64,
    pub violation_count: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_policy_enforcer_init() {
        let enforcer = PolicyEnforcer::new();
        let stats = enforcer.get_statistics();

        assert!(stats.total_policies >= 3); // At least default policies
    }

    #[test]
    fn test_policy_enforcement() {
        let mut enforcer = PolicyEnforcer::new();

        let result = enforcer.enforce(RuleType::NetworkAccess, 100, b"context");

        assert!(matches!(result, EnforcementResult::Allowed | EnforcementResult::AuditAllowed));
    }

    #[test]
    fn test_custom_policy() {
        let mut enforcer = PolicyEnforcer::new();

        let rules = vec![
            PolicyRule {
                rule_type: RuleType::NetworkAccess,
                action: PolicyAction::Deny,
                priority: 200, // Higher than defaults
            },
        ];

        let policy_id = enforcer.add_policy("Test Deny Policy", rules);

        let result = enforcer.enforce(RuleType::NetworkAccess, 100, b"test");

        assert_eq!(result, EnforcementResult::Denied);

        // Cleanup
        enforcer.remove_policy(policy_id).unwrap();
    }

    #[test]
    fn test_policy_enable_disable() {
        let mut enforcer = PolicyEnforcer::new();

        let rules = vec![
            PolicyRule {
                rule_type: RuleType::FileSystemAccess,
                action: PolicyAction::Deny,
                priority: 250,
            },
        ];

        let policy_id = enforcer.add_policy("Test Policy", rules);

        // Disable policy
        enforcer.disable_policy(policy_id).unwrap();

        // Should now allow (policy disabled)
        let result = enforcer.enforce(RuleType::FileSystemAccess, 100, b"test");
        assert!(matches!(result, EnforcementResult::Allowed | EnforcementResult::AuditAllowed));

        // Re-enable
        enforcer.enable_policy(policy_id).unwrap();
    }
}
