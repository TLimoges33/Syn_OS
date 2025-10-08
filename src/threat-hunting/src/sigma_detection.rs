//! Sigma Detection Engine
//!
//! SIEM-agnostic detection rule engine

use crate::{Result, ThreatHuntingError, FindingSeverity};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Sigma detection engine
pub struct SigmaDetectionEngine {
    rules: HashMap<String, SigmaRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SigmaRule {
    pub id: String,
    pub title: String,
    pub description: String,
    pub status: RuleStatus,
    pub level: SigmaLevel,
    pub logsource: LogSource,
    pub detection: Detection,
    pub falsepositives: Vec<String>,
    pub tags: Vec<String>,
    pub mitre_tactics: Vec<String>,
    pub mitre_techniques: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RuleStatus {
    Stable,
    Test,
    Experimental,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SigmaLevel {
    Critical,
    High,
    Medium,
    Low,
    Informational,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogSource {
    pub category: String,
    pub product: String,
    pub service: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Detection {
    pub selection: HashMap<String, SelectionValue>,
    pub condition: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum SelectionValue {
    Single(String),
    Multiple(Vec<String>),
}

#[derive(Debug, Clone)]
pub struct SigmaDetection {
    pub rule_id: String,
    pub title: String,
    pub severity: FindingSeverity,
    pub matched_events: Vec<String>,
    pub confidence: f32,
    pub mitre_tactics: Vec<String>,
    pub mitre_techniques: Vec<String>,
}

impl SigmaDetectionEngine {
    pub fn new() -> Self {
        let mut engine = Self {
            rules: HashMap::new(),
        };
        engine.load_default_rules();
        engine
    }

    fn load_default_rules(&mut self) {
        // Mimikatz detection
        let mimikatz_rule = SigmaRule {
            id: "sigma_001".to_string(),
            title: "Mimikatz Credential Dumping".to_string(),
            description: "Detects Mimikatz credential dumping activity".to_string(),
            status: RuleStatus::Stable,
            level: SigmaLevel::Critical,
            logsource: LogSource {
                category: "process_creation".to_string(),
                product: "windows".to_string(),
                service: None,
            },
            detection: Detection {
                selection: {
                    let mut map = HashMap::new();
                    map.insert(
                        "CommandLine".to_string(),
                        SelectionValue::Multiple(vec![
                            "sekurlsa::logonpasswords".to_string(),
                            "lsadump::sam".to_string(),
                            "privilege::debug".to_string(),
                        ]),
                    );
                    map
                },
                condition: "selection".to_string(),
            },
            falsepositives: vec!["Security testing".to_string()],
            tags: vec!["attack.credential_access".to_string(), "attack.t1003".to_string()],
            mitre_tactics: vec!["TA0006".to_string()],
            mitre_techniques: vec!["T1003.001".to_string()],
        };

        // PowerShell suspicious commands
        let powershell_rule = SigmaRule {
            id: "sigma_002".to_string(),
            title: "Suspicious PowerShell Commands".to_string(),
            description: "Detects suspicious PowerShell command execution".to_string(),
            status: RuleStatus::Stable,
            level: SigmaLevel::High,
            logsource: LogSource {
                category: "process_creation".to_string(),
                product: "windows".to_string(),
                service: Some("powershell".to_string()),
            },
            detection: Detection {
                selection: {
                    let mut map = HashMap::new();
                    map.insert(
                        "ScriptBlockText".to_string(),
                        SelectionValue::Multiple(vec![
                            "Invoke-Mimikatz".to_string(),
                            "DumpCreds".to_string(),
                            "Net.WebClient".to_string(),
                            "DownloadString".to_string(),
                            "IEX".to_string(),
                        ]),
                    );
                    map
                },
                condition: "selection".to_string(),
            },
            falsepositives: vec!["Administrative scripts".to_string()],
            tags: vec!["attack.execution".to_string(), "attack.t1059.001".to_string()],
            mitre_tactics: vec!["TA0002".to_string()],
            mitre_techniques: vec!["T1059.001".to_string()],
        };

        // Lateral movement via SMB
        let lateral_movement_rule = SigmaRule {
            id: "sigma_003".to_string(),
            title: "Lateral Movement via SMB".to_string(),
            description: "Detects lateral movement using SMB admin shares".to_string(),
            status: RuleStatus::Stable,
            level: SigmaLevel::High,
            logsource: LogSource {
                category: "network_connection".to_string(),
                product: "windows".to_string(),
                service: None,
            },
            detection: Detection {
                selection: {
                    let mut map = HashMap::new();
                    map.insert(
                        "DestinationPort".to_string(),
                        SelectionValue::Single("445".to_string()),
                    );
                    map.insert(
                        "DestinationPath".to_string(),
                        SelectionValue::Multiple(vec![
                            "\\\\*\\ADMIN$".to_string(),
                            "\\\\*\\C$".to_string(),
                            "\\\\*\\IPC$".to_string(),
                        ]),
                    );
                    map
                },
                condition: "selection".to_string(),
            },
            falsepositives: vec!["Legitimate administrative access".to_string()],
            tags: vec!["attack.lateral_movement".to_string(), "attack.t1021.002".to_string()],
            mitre_tactics: vec!["TA0008".to_string()],
            mitre_techniques: vec!["T1021.002".to_string()],
        };

        // Suspicious scheduled task
        let schtask_rule = SigmaRule {
            id: "sigma_004".to_string(),
            title: "Suspicious Scheduled Task Creation".to_string(),
            description: "Detects creation of suspicious scheduled tasks for persistence".to_string(),
            status: RuleStatus::Stable,
            level: SigmaLevel::Medium,
            logsource: LogSource {
                category: "process_creation".to_string(),
                product: "windows".to_string(),
                service: None,
            },
            detection: Detection {
                selection: {
                    let mut map = HashMap::new();
                    map.insert(
                        "Image".to_string(),
                        SelectionValue::Single("*\\schtasks.exe".to_string()),
                    );
                    map.insert(
                        "CommandLine".to_string(),
                        SelectionValue::Multiple(vec![
                            "*/create*".to_string(),
                            "*/sc minute*".to_string(),
                        ]),
                    );
                    map
                },
                condition: "selection".to_string(),
            },
            falsepositives: vec!["Software installation".to_string()],
            tags: vec!["attack.persistence".to_string(), "attack.t1053.005".to_string()],
            mitre_tactics: vec!["TA0003".to_string()],
            mitre_techniques: vec!["T1053.005".to_string()],
        };

        // Web shell access
        let webshell_rule = SigmaRule {
            id: "sigma_005".to_string(),
            title: "Web Shell Access Pattern".to_string(),
            description: "Detects web shell access patterns in web server logs".to_string(),
            status: RuleStatus::Test,
            level: SigmaLevel::Critical,
            logsource: LogSource {
                category: "webserver".to_string(),
                product: "apache".to_string(),
                service: None,
            },
            detection: Detection {
                selection: {
                    let mut map = HashMap::new();
                    map.insert(
                        "RequestUri".to_string(),
                        SelectionValue::Multiple(vec![
                            "*.php?cmd=*".to_string(),
                            "*.jsp?cmd=*".to_string(),
                            "*/upload.php*".to_string(),
                        ]),
                    );
                    map
                },
                condition: "selection".to_string(),
            },
            falsepositives: vec!["Legitimate file upload functionality".to_string()],
            tags: vec!["attack.persistence".to_string(), "attack.t1505.003".to_string()],
            mitre_tactics: vec!["TA0003".to_string()],
            mitre_techniques: vec!["T1505.003".to_string()],
        };

        self.rules.insert(mimikatz_rule.id.clone(), mimikatz_rule);
        self.rules.insert(powershell_rule.id.clone(), powershell_rule);
        self.rules.insert(lateral_movement_rule.id.clone(), lateral_movement_rule);
        self.rules.insert(schtask_rule.id.clone(), schtask_rule);
        self.rules.insert(webshell_rule.id.clone(), webshell_rule);
    }

    /// Detect threats in log source
    pub fn detect(&self, log_source: &str, rule_ids: &[String]) -> Result<Vec<SigmaDetection>> {
        let rules_to_check: Vec<&SigmaRule> = if rule_ids.is_empty() {
            self.rules.values().collect()
        } else {
            rule_ids.iter()
                .filter_map(|id| self.rules.get(id))
                .collect()
        };

        let log_events = self.parse_log_source(log_source)?;
        let mut detections = Vec::new();

        for rule in rules_to_check {
            let matched_events = self.evaluate_rule(rule, &log_events);

            if !matched_events.is_empty() {
                detections.push(SigmaDetection {
                    rule_id: rule.id.clone(),
                    title: rule.title.clone(),
                    severity: self.convert_level(&rule.level),
                    matched_events,
                    confidence: self.calculate_confidence(rule),
                    mitre_tactics: rule.mitre_tactics.clone(),
                    mitre_techniques: rule.mitre_techniques.clone(),
                });
            }
        }

        Ok(detections)
    }

    fn parse_log_source(&self, log_source: &str) -> Result<Vec<HashMap<String, String>>> {
        // Simplified log parsing - in production parse actual log formats
        let mut events = Vec::new();

        for line in log_source.lines() {
            let mut event = HashMap::new();
            event.insert("raw".to_string(), line.to_string());

            // Extract key-value pairs
            for part in line.split_whitespace() {
                if let Some(pos) = part.find('=') {
                    let (key, value) = part.split_at(pos);
                    event.insert(key.to_string(), value[1..].to_string());
                }
            }

            events.push(event);
        }

        Ok(events)
    }

    fn evaluate_rule(&self, rule: &SigmaRule, events: &[HashMap<String, String>]) -> Vec<String> {
        let mut matched = Vec::new();

        for event in events {
            if self.matches_detection(&rule.detection, event) {
                matched.push(
                    event.get("raw")
                        .unwrap_or(&"<no raw event>".to_string())
                        .clone()
                );
            }
        }

        matched
    }

    fn matches_detection(&self, detection: &Detection, event: &HashMap<String, String>) -> bool {
        for (field, value) in &detection.selection {
            let event_value = event.get(field);

            let matches = match value {
                SelectionValue::Single(v) => {
                    event_value.map(|ev| self.match_pattern(ev, v)).unwrap_or(false)
                }
                SelectionValue::Multiple(values) => {
                    event_value.map(|ev| {
                        values.iter().any(|v| self.match_pattern(ev, v))
                    }).unwrap_or(false)
                }
            };

            if !matches {
                return false;
            }
        }

        true
    }

    fn match_pattern(&self, value: &str, pattern: &str) -> bool {
        if pattern.contains('*') {
            let pattern_regex = pattern.replace('*', ".*");
            if let Ok(re) = regex::Regex::new(&pattern_regex) {
                return re.is_match(value);
            }
        }

        value.contains(pattern)
    }

    fn convert_level(&self, level: &SigmaLevel) -> FindingSeverity {
        match level {
            SigmaLevel::Critical => FindingSeverity::Critical,
            SigmaLevel::High => FindingSeverity::High,
            SigmaLevel::Medium => FindingSeverity::Medium,
            SigmaLevel::Low => FindingSeverity::Low,
            SigmaLevel::Informational => FindingSeverity::Info,
        }
    }

    fn calculate_confidence(&self, rule: &SigmaRule) -> f32 {
        match rule.status {
            RuleStatus::Stable => 0.95,
            RuleStatus::Test => 0.80,
            RuleStatus::Experimental => 0.60,
        }
    }

    /// Load Sigma rule from YAML
    pub fn load_rule(&mut self, rule_yaml: &str) -> Result<()> {
        let rule: SigmaRule = serde_yaml::from_str(rule_yaml)
            .map_err(|e| ThreatHuntingError::SigmaError(format!("Failed to parse Sigma rule: {}", e)))?;

        self.rules.insert(rule.id.clone(), rule);
        Ok(())
    }

    /// List all rules
    pub fn list_rules(&self) -> Vec<String> {
        self.rules.keys().cloned().collect()
    }

    /// Get rule by ID
    pub fn get_rule(&self, rule_id: &str) -> Option<&SigmaRule> {
        self.rules.get(rule_id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sigma_engine_creation() {
        let engine = SigmaDetectionEngine::new();
        assert!(!engine.rules.is_empty());
    }

    #[test]
    fn test_mimikatz_detection() {
        let engine = SigmaDetectionEngine::new();
        let log = "CommandLine=sekurlsa::logonpasswords process=mimikatz.exe";

        let detections = engine.detect(log, &[]).unwrap();
        assert!(!detections.is_empty());
    }
}
