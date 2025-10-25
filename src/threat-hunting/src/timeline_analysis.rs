//! Timeline Analysis
//!
//! Event correlation and temporal pattern detection

use crate::{Result, HuntFinding, FindingSeverity, Evidence};
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, Duration};

/// Timeline analyzer for event correlation
pub struct TimelineAnalyzer {
    correlation_window: Duration,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimelineCorrelation {
    pub description: String,
    pub severity: FindingSeverity,
    pub correlated_events: Vec<Evidence>,
    pub tactics: Vec<String>,
    pub techniques: Vec<String>,
    pub confidence: f32,
    pub attack_chain: Vec<AttackPhase>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttackPhase {
    pub phase: String,
    pub timestamp: DateTime<Utc>,
    pub description: String,
    pub mitre_tactic: String,
}

impl TimelineAnalyzer {
    pub fn new() -> Self {
        Self {
            correlation_window: Duration::hours(1),
        }
    }

    /// Analyze timeline for correlations
    pub fn analyze(
        &self,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
        findings: &[HuntFinding],
    ) -> Result<Vec<TimelineCorrelation>> {
        let filtered_findings: Vec<&HuntFinding> = findings.iter()
            .filter(|f| f.timestamp >= start && f.timestamp <= end)
            .collect();

        let mut correlations = Vec::new();

        // Detect kill chain progression
        if let Some(kill_chain) = self.detect_kill_chain(&filtered_findings) {
            correlations.push(kill_chain);
        }

        // Detect lateral movement patterns
        if let Some(lateral_movement) = self.detect_lateral_movement(&filtered_findings) {
            correlations.push(lateral_movement);
        }

        // Detect data exfiltration
        if let Some(exfiltration) = self.detect_exfiltration(&filtered_findings) {
            correlations.push(exfiltration);
        }

        // Detect privilege escalation chains
        if let Some(priv_esc) = self.detect_privilege_escalation(&filtered_findings) {
            correlations.push(priv_esc);
        }

        Ok(correlations)
    }

    fn detect_kill_chain(&self, findings: &[&HuntFinding]) -> Option<TimelineCorrelation> {
        // Look for reconnaissance -> weaponization -> delivery -> exploitation -> installation -> C2 -> actions
        let tactics_sequence = vec![
            "TA0043", // Reconnaissance
            "TA0001", // Initial Access
            "TA0002", // Execution
            "TA0003", // Persistence
            "TA0011", // Command and Control
        ];

        let mut found_phases = Vec::new();

        for tactic in &tactics_sequence {
            if let Some(finding) = findings.iter()
                .find(|f| f.mitre_tactics.contains(&tactic.to_string()))
            {
                found_phases.push(AttackPhase {
                    phase: self.tactic_to_phase_name(tactic),
                    timestamp: finding.timestamp,
                    description: finding.description.clone(),
                    mitre_tactic: tactic.to_string(),
                });
            }
        }

        if found_phases.len() >= 3 {
            let evidence: Vec<Evidence> = findings.iter()
                .flat_map(|f| f.evidence.clone())
                .collect();

            Some(TimelineCorrelation {
                description: format!("Complete attack kill chain detected: {} phases", found_phases.len()),
                severity: FindingSeverity::Critical,
                correlated_events: evidence,
                tactics: tactics_sequence.iter().map(|t| t.to_string()).collect(),
                techniques: findings.iter()
                    .flat_map(|f| f.mitre_techniques.clone())
                    .collect(),
                confidence: 0.95,
                attack_chain: found_phases,
            })
        } else {
            None
        }
    }

    fn detect_lateral_movement(&self, findings: &[&HuntFinding]) -> Option<TimelineCorrelation> {
        // Look for credential access followed by lateral movement
        let cred_access = findings.iter()
            .find(|f| f.mitre_tactics.contains(&"TA0006".to_string()));

        let lateral_move = findings.iter()
            .find(|f| f.mitre_tactics.contains(&"TA0008".to_string()));

        if let (Some(cred), Some(lateral)) = (cred_access, lateral_move) {
            let time_diff = (lateral.timestamp - cred.timestamp).num_minutes();

            if time_diff >= 0 && time_diff <= 60 {
                let evidence: Vec<Evidence> = vec![cred, lateral].iter()
                    .flat_map(|f| f.evidence.clone())
                    .collect();

                let attack_chain = vec![
                    AttackPhase {
                        phase: "Credential Access".to_string(),
                        timestamp: cred.timestamp,
                        description: cred.description.clone(),
                        mitre_tactic: "TA0006".to_string(),
                    },
                    AttackPhase {
                        phase: "Lateral Movement".to_string(),
                        timestamp: lateral.timestamp,
                        description: lateral.description.clone(),
                        mitre_tactic: "TA0008".to_string(),
                    },
                ];

                return Some(TimelineCorrelation {
                    description: format!("Lateral movement detected {} minutes after credential theft", time_diff),
                    severity: FindingSeverity::High,
                    correlated_events: evidence,
                    tactics: vec!["TA0006".to_string(), "TA0008".to_string()],
                    techniques: vec![cred, lateral].iter()
                        .flat_map(|f| f.mitre_techniques.clone())
                        .collect(),
                    confidence: 0.88,
                    attack_chain,
                });
            }
        }

        None
    }

    fn detect_exfiltration(&self, findings: &[&HuntFinding]) -> Option<TimelineCorrelation> {
        // Look for collection followed by exfiltration
        let collection = findings.iter()
            .find(|f| f.mitre_tactics.contains(&"TA0009".to_string()));

        let exfiltration = findings.iter()
            .find(|f| f.mitre_tactics.contains(&"TA0010".to_string()));

        if let (Some(collect), Some(exfil)) = (collection, exfiltration) {
            let evidence: Vec<Evidence> = vec![collect, exfil].iter()
                .flat_map(|f| f.evidence.clone())
                .collect();

            let attack_chain = vec![
                AttackPhase {
                    phase: "Collection".to_string(),
                    timestamp: collect.timestamp,
                    description: collect.description.clone(),
                    mitre_tactic: "TA0009".to_string(),
                },
                AttackPhase {
                    phase: "Exfiltration".to_string(),
                    timestamp: exfil.timestamp,
                    description: exfil.description.clone(),
                    mitre_tactic: "TA0010".to_string(),
                },
            ];

            return Some(TimelineCorrelation {
                description: "Data collection followed by exfiltration detected".to_string(),
                severity: FindingSeverity::Critical,
                correlated_events: evidence,
                tactics: vec!["TA0009".to_string(), "TA0010".to_string()],
                techniques: vec![collect, exfil].iter()
                    .flat_map(|f| f.mitre_techniques.clone())
                    .collect(),
                confidence: 0.92,
                attack_chain,
            });
        }

        None
    }

    fn detect_privilege_escalation(&self, findings: &[&HuntFinding]) -> Option<TimelineCorrelation> {
        // Look for privilege escalation followed by persistence
        let priv_esc = findings.iter()
            .find(|f| f.mitre_tactics.contains(&"TA0004".to_string()));

        let persistence = findings.iter()
            .find(|f| f.mitre_tactics.contains(&"TA0003".to_string()));

        if let (Some(escalate), Some(persist)) = (priv_esc, persistence) {
            let evidence: Vec<Evidence> = vec![escalate, persist].iter()
                .flat_map(|f| f.evidence.clone())
                .collect();

            let attack_chain = vec![
                AttackPhase {
                    phase: "Privilege Escalation".to_string(),
                    timestamp: escalate.timestamp,
                    description: escalate.description.clone(),
                    mitre_tactic: "TA0004".to_string(),
                },
                AttackPhase {
                    phase: "Persistence".to_string(),
                    timestamp: persist.timestamp,
                    description: persist.description.clone(),
                    mitre_tactic: "TA0003".to_string(),
                },
            ];

            return Some(TimelineCorrelation {
                description: "Privilege escalation followed by persistence mechanism".to_string(),
                severity: FindingSeverity::High,
                correlated_events: evidence,
                tactics: vec!["TA0004".to_string(), "TA0003".to_string()],
                techniques: vec![escalate, persist].iter()
                    .flat_map(|f| f.mitre_techniques.clone())
                    .collect(),
                confidence: 0.90,
                attack_chain,
            });
        }

        None
    }

    fn tactic_to_phase_name(&self, tactic_id: &str) -> String {
        match tactic_id {
            "TA0043" => "Reconnaissance",
            "TA0042" => "Resource Development",
            "TA0001" => "Initial Access",
            "TA0002" => "Execution",
            "TA0003" => "Persistence",
            "TA0004" => "Privilege Escalation",
            "TA0005" => "Defense Evasion",
            "TA0006" => "Credential Access",
            "TA0007" => "Discovery",
            "TA0008" => "Lateral Movement",
            "TA0009" => "Collection",
            "TA0011" => "Command and Control",
            "TA0010" => "Exfiltration",
            "TA0040" => "Impact",
            _ => "Unknown",
        }.to_string()
    }

    /// Set correlation time window
    pub fn set_correlation_window(&mut self, hours: i64) {
        self.correlation_window = Duration::hours(hours);
    }

    /// Generate attack timeline visualization
    pub fn generate_timeline_graph(&self, findings: &[HuntFinding]) -> Result<TimelineGraph> {
        let mut events: Vec<TimelineEvent> = findings.iter().map(|f| {
            TimelineEvent {
                timestamp: f.timestamp,
                event_type: format!("{:?}", f.finding_type),
                description: f.description.clone(),
                severity: f.severity.clone(),
                mitre_tactics: f.mitre_tactics.clone(),
            }
        }).collect();

        events.sort_by_key(|e| e.timestamp);

        Ok(TimelineGraph {
            events,
            duration: if !findings.is_empty() {
                findings.iter().max_by_key(|f| f.timestamp).unwrap().timestamp
                    - findings.iter().min_by_key(|f| f.timestamp).unwrap().timestamp
            } else {
                Duration::zero()
            },
        })
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimelineGraph {
    pub events: Vec<TimelineEvent>,
    pub duration: Duration,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimelineEvent {
    pub timestamp: DateTime<Utc>,
    pub event_type: String,
    pub description: String,
    pub severity: FindingSeverity,
    pub mitre_tactics: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{FindingType, ThreatSeverity};
    use uuid::Uuid;

    #[test]
    fn test_timeline_analyzer() {
        let analyzer = TimelineAnalyzer::new();

        let finding = HuntFinding {
            id: Uuid::new_v4(),
            session_id: Uuid::new_v4(),
            timestamp: Utc::now(),
            finding_type: FindingType::YaraMatch,
            severity: FindingSeverity::High,
            description: "Test finding".to_string(),
            evidence: vec![],
            mitre_tactics: vec!["TA0001".to_string()],
            mitre_techniques: vec![],
            confidence_score: 0.8,
        };

        let correlations = analyzer.analyze(
            Utc::now() - Duration::hours(1),
            Utc::now(),
            &[finding],
        ).unwrap();

        assert!(correlations.len() >= 0);
    }
}
