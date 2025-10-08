/// Response engine for threat mitigation
/// Executes automated responses to detected threats

use super::{Threat, ResponseAction, ThreatLevel};
use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Response rule
struct ResponseRule {
    min_severity: ThreatLevel,
    action: ResponseAction,
    delay_ns: u64,
}

/// Response engine
pub struct ResponseEngine {
    rules: Vec<ResponseRule>,
    responses_executed: u64,
    blocked_operations: BTreeMap<u64, u64>, // pid -> count
}

impl ResponseEngine {
    /// Create new response engine
    pub fn new() -> Self {
        let mut engine = Self {
            rules: Vec::new(),
            responses_executed: 0,
            blocked_operations: BTreeMap::new(),
        };

        // Load default response rules
        engine.load_default_rules();

        engine
    }

    /// Load default response rules
    fn load_default_rules(&mut self) {
        // Critical threats: immediate termination
        self.rules.push(ResponseRule {
            min_severity: ThreatLevel::Critical,
            action: ResponseAction::Terminate,
            delay_ns: 0, // Immediate
        });

        // High threats: isolate process
        self.rules.push(ResponseRule {
            min_severity: ThreatLevel::High,
            action: ResponseAction::Isolate,
            delay_ns: 100, // 100ns delay for logging
        });

        // Medium threats: block and alert
        self.rules.push(ResponseRule {
            min_severity: ThreatLevel::Medium,
            action: ResponseAction::Block,
            delay_ns: 1000,
        });

        // Low threats: just log
        self.rules.push(ResponseRule {
            min_severity: ThreatLevel::Low,
            action: ResponseAction::Log,
            delay_ns: 0,
        });
    }

    /// Select best response for threat
    pub fn select_response(&self, threat: &Threat) -> ResponseAction {
        // Find most appropriate rule
        for rule in &self.rules {
            if threat.severity >= rule.min_severity {
                return rule.action;
            }
        }

        // Default: log
        ResponseAction::Log
    }

    /// Execute response
    pub fn execute(&mut self, pid: u64, _threat: &Threat, action: ResponseAction) -> Result<(), &'static str> {
        self.responses_executed += 1;

        match action {
            ResponseAction::Log => {
                // Would write to security log
                Ok(())
            }
            ResponseAction::Alert => {
                // Would send alert notification
                Ok(())
            }
            ResponseAction::Block => {
                // Track blocked operation
                *self.blocked_operations.entry(pid).or_insert(0) += 1;
                Ok(())
            }
            ResponseAction::Isolate => {
                // Process isolation handled by caller
                Ok(())
            }
            ResponseAction::Terminate => {
                // Process termination handled by caller
                Ok(())
            }
            ResponseAction::Quarantine => {
                // Quarantine handled by caller
                Ok(())
            }
        }
    }

    /// Add custom response rule
    pub fn add_rule(&mut self, min_severity: ThreatLevel, action: ResponseAction, delay_ns: u64) {
        self.rules.push(ResponseRule {
            min_severity,
            action,
            delay_ns,
        });

        // Sort rules by severity (highest first)
        self.rules.sort_by(|a, b| b.min_severity.cmp(&a.min_severity));
    }

    /// Get blocked operation count for process
    pub fn get_blocked_count(&self, pid: u64) -> u64 {
        self.blocked_operations.get(&pid).copied().unwrap_or(0)
    }

    /// Get total responses executed
    pub fn get_responses_executed(&self) -> u64 {
        self.responses_executed
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::ThreatType;

    #[test]
    fn test_response_selection() {
        let engine = ResponseEngine::new();

        let critical_threat = Threat {
            threat_type: ThreatType::PrivilegeEscalation,
            severity: ThreatLevel::Critical,
            process_id: 100,
            timestamp_ns: 0,
            details: [0u8; 256],
            auto_mitigate: true,
        };

        let action = engine.select_response(&critical_threat);
        assert_eq!(action, ResponseAction::Terminate);
    }

    #[test]
    fn test_custom_rules() {
        let mut engine = ResponseEngine::new();

        engine.add_rule(ThreatLevel::Medium, ResponseAction::Quarantine, 500);

        assert!(engine.rules.len() > 4);
    }

    #[test]
    fn test_blocked_tracking() {
        let mut engine = ResponseEngine::new();

        let medium_threat = Threat {
            threat_type: ThreatType::UnauthorizedAccess,
            severity: ThreatLevel::Medium,
            process_id: 100,
            timestamp_ns: 0,
            details: [0u8; 256],
            auto_mitigate: false,
        };

        engine.execute(100, &medium_threat, ResponseAction::Block).unwrap();
        engine.execute(100, &medium_threat, ResponseAction::Block).unwrap();

        assert_eq!(engine.get_blocked_count(100), 2);
    }
}
