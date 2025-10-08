//! # SynOS Zero-Trust Network Architecture (ZTNA) Policy Engine
//!
//! Implements "never trust, always verify" security model with:
//! - Continuous identity verification
//! - Dynamic policy evaluation
//! - Network micro-segmentation
//! - Real-time threat hunting integration
//! - AI consciousness integration

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::IpAddr;
use chrono::{DateTime, Utc, Duration, Timelike};
use uuid::Uuid;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ZeroTrustError {
    #[error("Policy violation: {0}")]
    PolicyViolation(String),
    #[error("Authentication failed: {0}")]
    AuthenticationFailed(String),
    #[error("Authorization denied: {0}")]
    AuthorizationDenied(String),
    #[error("Trust score too low: {score}, required: {required}")]
    InsufficientTrust { score: f64, required: f64 },
    #[error("Session expired")]
    SessionExpired,
    #[error("Invalid context: {0}")]
    InvalidContext(String),
}

pub type Result<T> = std::result::Result<T, ZeroTrustError>;

/// Identity with continuous verification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Identity {
    pub id: Uuid,
    pub username: String,
    pub roles: Vec<String>,
    pub groups: Vec<String>,
    pub mfa_verified: bool,
    pub device_fingerprint: String,
    pub last_verified: DateTime<Utc>,
    pub trust_score: f64,
    pub attributes: HashMap<String, String>,
}

impl Identity {
    pub fn new(username: String, device_fingerprint: String) -> Self {
        Self {
            id: Uuid::new_v4(),
            username,
            roles: Vec::new(),
            groups: Vec::new(),
            mfa_verified: false,
            device_fingerprint,
            last_verified: Utc::now(),
            trust_score: 50.0,
            attributes: HashMap::new(),
        }
    }

    pub fn is_verification_required(&self, max_age: Duration) -> bool {
        Utc::now() - self.last_verified > max_age
    }

    pub fn update_trust_score(&mut self, delta: f64) {
        self.trust_score = (self.trust_score + delta).clamp(0.0, 100.0);
    }
}

/// Access context for policy evaluation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccessContext {
    pub identity: Identity,
    pub source_ip: IpAddr,
    pub destination_ip: IpAddr,
    pub destination_port: u16,
    pub protocol: String,
    pub resource_type: String,
    pub resource_id: String,
    pub action: String,
    pub time: DateTime<Utc>,
    pub threat_indicators: Vec<ThreatIndicator>,
}

/// Threat indicators from real-time analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThreatIndicator {
    pub indicator_type: String,
    pub severity: String,
    pub description: String,
    pub confidence: f64,
    pub detected_at: DateTime<Utc>,
}

/// Policy rule for zero-trust evaluation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyRule {
    pub id: String,
    pub name: String,
    pub priority: u32,
    pub conditions: Vec<PolicyCondition>,
    pub action: PolicyAction,
    pub min_trust_score: f64,
    pub require_mfa: bool,
    pub allowed_locations: Vec<String>,
    pub time_restrictions: Option<TimeRestriction>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyCondition {
    pub field: String,
    pub operator: ConditionOperator,
    pub value: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConditionOperator {
    Equals,
    NotEquals,
    Contains,
    In,
    GreaterThan,
    LessThan,
    Matches,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PolicyAction {
    Allow,
    Deny,
    RequireStepUp,
    Challenge,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimeRestriction {
    pub allowed_days: Vec<String>,
    pub allowed_hours_start: u8,
    pub allowed_hours_end: u8,
}

/// Policy decision with detailed reasoning
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyDecision {
    pub decision: PolicyAction,
    pub matched_rule: Option<String>,
    pub reasoning: Vec<String>,
    pub trust_score: f64,
    pub threat_level: String,
    pub session_id: Uuid,
    pub timestamp: DateTime<Utc>,
}

/// Network micro-segment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MicroSegment {
    pub id: String,
    pub name: String,
    pub network_cidr: String,
    pub allowed_protocols: Vec<String>,
    pub allowed_ports: Vec<u16>,
    pub isolation_level: String,
    pub member_identities: Vec<Uuid>,
    pub ingress_rules: Vec<SegmentRule>,
    pub egress_rules: Vec<SegmentRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SegmentRule {
    pub source_segment: Option<String>,
    pub destination_segment: Option<String>,
    pub protocol: String,
    pub port_range: (u16, u16),
    pub action: PolicyAction,
}

/// Zero-Trust Policy Engine
#[derive(Debug)]
pub struct ZeroTrustEngine {
    pub policies: Vec<PolicyRule>,
    pub segments: HashMap<String, MicroSegment>,
    pub active_sessions: HashMap<Uuid, TrustSession>,
    pub verification_interval: Duration,
    pub default_trust_score: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrustSession {
    pub session_id: Uuid,
    pub identity: Identity,
    pub created_at: DateTime<Utc>,
    pub last_activity: DateTime<Utc>,
    pub access_history: Vec<AccessContext>,
    pub current_trust_score: f64,
    pub threat_indicators: Vec<ThreatIndicator>,
}

impl ZeroTrustEngine {
    pub fn new() -> Self {
        Self {
            policies: Vec::new(),
            segments: HashMap::new(),
            active_sessions: HashMap::new(),
            verification_interval: Duration::minutes(5),
            default_trust_score: 50.0,
        }
    }

    /// Evaluate access request against zero-trust policies
    pub fn evaluate_access(&mut self, context: &AccessContext) -> Result<PolicyDecision> {
        let mut reasoning = Vec::new();
        let mut trust_score = context.identity.trust_score;

        // 1. Check identity verification freshness
        if context.identity.is_verification_required(self.verification_interval) {
            reasoning.push("Identity verification expired - re-authentication required".to_string());
            return Ok(PolicyDecision {
                decision: PolicyAction::RequireStepUp,
                matched_rule: None,
                reasoning,
                trust_score,
                threat_level: "MEDIUM".to_string(),
                session_id: Uuid::new_v4(),
                timestamp: Utc::now(),
            });
        }

        // 2. Analyze threat indicators
        let threat_level = self.calculate_threat_level(&context.threat_indicators);
        if threat_level == "CRITICAL" {
            reasoning.push(format!("Critical threat indicators detected: {} indicators", context.threat_indicators.len()));
            return Ok(PolicyDecision {
                decision: PolicyAction::Deny,
                matched_rule: None,
                reasoning,
                trust_score,
                threat_level,
                session_id: Uuid::new_v4(),
                timestamp: Utc::now(),
            });
        }

        // 3. Apply trust score modifiers based on threat level
        match threat_level.as_str() {
            "HIGH" => trust_score -= 20.0,
            "MEDIUM" => trust_score -= 10.0,
            "LOW" => trust_score -= 5.0,
            _ => {}
        }

        // 4. Evaluate policies (sorted by priority)
        let mut sorted_policies = self.policies.clone();
        sorted_policies.sort_by_key(|p| p.priority);

        for policy in sorted_policies {
            if self.evaluate_policy_conditions(&policy, context) {
                reasoning.push(format!("Matched policy: {} (priority {})", policy.name, policy.priority));

                // Check MFA requirement
                if policy.require_mfa && !context.identity.mfa_verified {
                    reasoning.push("MFA verification required".to_string());
                    return Ok(PolicyDecision {
                        decision: PolicyAction::RequireStepUp,
                        matched_rule: Some(policy.id),
                        reasoning,
                        trust_score,
                        threat_level,
                        session_id: Uuid::new_v4(),
                        timestamp: Utc::now(),
                    });
                }

                // Check trust score threshold
                if trust_score < policy.min_trust_score {
                    reasoning.push(format!("Trust score {} below required {}", trust_score, policy.min_trust_score));
                    return Ok(PolicyDecision {
                        decision: PolicyAction::Challenge,
                        matched_rule: Some(policy.id),
                        reasoning,
                        trust_score,
                        threat_level,
                        session_id: Uuid::new_v4(),
                        timestamp: Utc::now(),
                    });
                }

                // Check time restrictions
                if let Some(time_restriction) = &policy.time_restrictions {
                    if !self.check_time_restriction(time_restriction, context.time) {
                        reasoning.push("Access outside allowed time window".to_string());
                        return Ok(PolicyDecision {
                            decision: PolicyAction::Deny,
                            matched_rule: Some(policy.id),
                            reasoning,
                            trust_score,
                            threat_level,
                            session_id: Uuid::new_v4(),
                            timestamp: Utc::now(),
                        });
                    }
                }

                // Policy matched and all checks passed
                reasoning.push(format!("Policy action: {:?}", policy.action));
                return Ok(PolicyDecision {
                    decision: policy.action.clone(),
                    matched_rule: Some(policy.id),
                    reasoning,
                    trust_score,
                    threat_level,
                    session_id: Uuid::new_v4(),
                    timestamp: Utc::now(),
                });
            }
        }

        // 5. No policy matched - default deny
        reasoning.push("No matching policy - default deny".to_string());
        Ok(PolicyDecision {
            decision: PolicyAction::Deny,
            matched_rule: None,
            reasoning,
            trust_score,
            threat_level,
            session_id: Uuid::new_v4(),
            timestamp: Utc::now(),
        })
    }

    fn evaluate_policy_conditions(&self, policy: &PolicyRule, context: &AccessContext) -> bool {
        policy.conditions.iter().all(|condition| {
            self.evaluate_condition(condition, context)
        })
    }

    fn evaluate_condition(&self, condition: &PolicyCondition, context: &AccessContext) -> bool {
        let field_value = match condition.field.as_str() {
            "identity.username" => &context.identity.username,
            "identity.role" => {
                return context.identity.roles.iter().any(|r| match &condition.operator {
                    ConditionOperator::Equals => r == &condition.value,
                    ConditionOperator::Contains => r.contains(&condition.value),
                    _ => false,
                });
            },
            "resource_type" => &context.resource_type,
            "action" => &context.action,
            "protocol" => &context.protocol,
            _ => return false,
        };

        match &condition.operator {
            ConditionOperator::Equals => field_value == &condition.value,
            ConditionOperator::NotEquals => field_value != &condition.value,
            ConditionOperator::Contains => field_value.contains(&condition.value),
            _ => false,
        }
    }

    fn calculate_threat_level(&self, indicators: &[ThreatIndicator]) -> String {
        if indicators.is_empty() {
            return "NONE".to_string();
        }

        let max_severity = indicators.iter()
            .map(|i| match i.severity.as_str() {
                "CRITICAL" => 4,
                "HIGH" => 3,
                "MEDIUM" => 2,
                "LOW" => 1,
                _ => 0,
            })
            .max()
            .unwrap_or(0);

        match max_severity {
            4 => "CRITICAL".to_string(),
            3 => "HIGH".to_string(),
            2 => "MEDIUM".to_string(),
            1 => "LOW".to_string(),
            _ => "NONE".to_string(),
        }
    }

    fn check_time_restriction(&self, restriction: &TimeRestriction, time: DateTime<Utc>) -> bool {
        let day = time.format("%A").to_string();
        let hour = time.hour() as u8;

        restriction.allowed_days.contains(&day) &&
        hour >= restriction.allowed_hours_start &&
        hour < restriction.allowed_hours_end
    }

    /// Create or update session with continuous trust scoring
    pub fn update_session(&mut self, identity: Identity) -> Uuid {
        let session_id = Uuid::new_v4();
        let session = TrustSession {
            session_id,
            identity: identity.clone(),
            created_at: Utc::now(),
            last_activity: Utc::now(),
            access_history: Vec::new(),
            current_trust_score: identity.trust_score,
            threat_indicators: Vec::new(),
        };
        self.active_sessions.insert(session_id, session);
        session_id
    }

    /// Add threat indicator to session
    pub fn add_threat_indicator(&mut self, session_id: Uuid, indicator: ThreatIndicator) {
        if let Some(session) = self.active_sessions.get_mut(&session_id) {
            session.threat_indicators.push(indicator.clone());

            // Update trust score based on threat severity
            let trust_delta = match indicator.severity.as_str() {
                "CRITICAL" => -30.0,
                "HIGH" => -20.0,
                "MEDIUM" => -10.0,
                "LOW" => -5.0,
                _ => 0.0,
            } * indicator.confidence;

            session.current_trust_score = (session.current_trust_score + trust_delta).clamp(0.0, 100.0);
        }
    }

    /// Evaluate micro-segmentation rules
    pub fn evaluate_segment_access(
        &self,
        source_segment: &str,
        dest_segment: &str,
        protocol: &str,
        port: u16
    ) -> Result<PolicyAction> {
        if let Some(segment) = self.segments.get(dest_segment) {
            for rule in &segment.ingress_rules {
                if let Some(source) = &rule.source_segment {
                    if source == source_segment &&
                       &rule.protocol == protocol &&
                       port >= rule.port_range.0 && port <= rule.port_range.1 {
                        return Ok(rule.action.clone());
                    }
                }
            }
        }

        Ok(PolicyAction::Deny)
    }

    /// Add policy rule
    pub fn add_policy(&mut self, policy: PolicyRule) {
        self.policies.push(policy);
    }

    /// Add micro-segment
    pub fn add_segment(&mut self, segment: MicroSegment) {
        self.segments.insert(segment.id.clone(), segment);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_identity_verification_required() {
        let mut identity = Identity::new("test_user".to_string(), "device123".to_string());
        identity.last_verified = Utc::now() - Duration::minutes(10);

        assert!(identity.is_verification_required(Duration::minutes(5)));
        assert!(!identity.is_verification_required(Duration::minutes(15)));
    }

    #[test]
    fn test_trust_score_bounds() {
        let mut identity = Identity::new("test_user".to_string(), "device123".to_string());

        identity.update_trust_score(-100.0);
        assert_eq!(identity.trust_score, 0.0);

        identity.update_trust_score(200.0);
        assert_eq!(identity.trust_score, 100.0);
    }
}
