//! YARA Rule Engine
//!
//! Pattern matching engine for malware detection

use crate::{Result, ThreatHuntingError};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use walkdir::WalkDir;
use sha2::{Sha256, Digest};

/// YARA engine for pattern matching
pub struct YaraEngine {
    compiled_rules: HashMap<String, YaraRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct YaraRule {
    pub name: String,
    pub description: String,
    pub patterns: Vec<Pattern>,
    pub condition: Condition,
    pub metadata: YaraMetadata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pattern {
    pub name: String,
    pub pattern_type: PatternType,
    pub value: String,
    pub modifiers: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PatternType {
    Text,
    Hex,
    Regex,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Condition {
    pub expression: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct YaraMetadata {
    pub author: String,
    pub description: String,
    pub reference: Vec<String>,
    pub mitre_tactics: Vec<String>,
    pub mitre_techniques: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct YaraMatch {
    pub rule_name: String,
    pub file_path: String,
    pub file_hash: String,
    pub matched_strings: Vec<String>,
    pub mitre_tactics: Vec<String>,
    pub mitre_techniques: Vec<String>,
}

impl YaraEngine {
    pub fn new() -> Self {
        let mut engine = Self {
            compiled_rules: HashMap::new(),
        };
        engine.load_default_rules();
        engine
    }

    fn load_default_rules(&mut self) {
        // APT malware detection rule
        let apt_rule = YaraRule {
            name: "APT_Malware_Generic".to_string(),
            description: "Detects common APT malware patterns".to_string(),
            patterns: vec![
                Pattern {
                    name: "$payload1".to_string(),
                    pattern_type: PatternType::Hex,
                    value: "4D 5A 90 00".to_string(),
                    modifiers: vec![],
                },
                Pattern {
                    name: "$c2_pattern".to_string(),
                    pattern_type: PatternType::Text,
                    value: "http://malicious-c2.example.com".to_string(),
                    modifiers: vec!["nocase".to_string()],
                },
                Pattern {
                    name: "$persistence".to_string(),
                    pattern_type: PatternType::Regex,
                    value: r"HKEY_.*\\Software\\Microsoft\\Windows\\CurrentVersion\\Run".to_string(),
                    modifiers: vec![],
                },
            ],
            condition: Condition {
                expression: "any of them".to_string(),
            },
            metadata: YaraMetadata {
                author: "SynOS Security Team".to_string(),
                description: "Generic APT malware detection".to_string(),
                reference: vec!["MITRE ATT&CK".to_string()],
                mitre_tactics: vec!["TA0002".to_string(), "TA0003".to_string()],
                mitre_techniques: vec!["T1547".to_string(), "T1071".to_string()],
            },
        };

        // Ransomware detection rule
        let ransomware_rule = YaraRule {
            name: "Ransomware_Generic".to_string(),
            description: "Detects ransomware characteristics".to_string(),
            patterns: vec![
                Pattern {
                    name: "$ransom_note".to_string(),
                    pattern_type: PatternType::Text,
                    value: "files have been encrypted".to_string(),
                    modifiers: vec!["nocase".to_string()],
                },
                Pattern {
                    name: "$bitcoin".to_string(),
                    pattern_type: PatternType::Regex,
                    value: r"[13][a-km-zA-HJ-NP-Z1-9]{25,34}".to_string(),
                    modifiers: vec![],
                },
                Pattern {
                    name: "$crypto_api".to_string(),
                    pattern_type: PatternType::Text,
                    value: "CryptEncrypt".to_string(),
                    modifiers: vec![],
                },
            ],
            condition: Condition {
                expression: "2 of them".to_string(),
            },
            metadata: YaraMetadata {
                author: "SynOS Security Team".to_string(),
                description: "Generic ransomware indicators".to_string(),
                reference: vec!["https://attack.mitre.org/tactics/TA0040/".to_string()],
                mitre_tactics: vec!["TA0040".to_string()],
                mitre_techniques: vec!["T1486".to_string()],
            },
        };

        // Webshell detection rule
        let webshell_rule = YaraRule {
            name: "Webshell_PHP_Generic".to_string(),
            description: "Detects PHP webshells".to_string(),
            patterns: vec![
                Pattern {
                    name: "$php_eval".to_string(),
                    pattern_type: PatternType::Text,
                    value: "eval($_".to_string(),
                    modifiers: vec![],
                },
                Pattern {
                    name: "$base64_decode".to_string(),
                    pattern_type: PatternType::Text,
                    value: "base64_decode".to_string(),
                    modifiers: vec![],
                },
                Pattern {
                    name: "$cmd_execution".to_string(),
                    pattern_type: PatternType::Text,
                    value: "system($_".to_string(),
                    modifiers: vec![],
                },
            ],
            condition: Condition {
                expression: "any of them".to_string(),
            },
            metadata: YaraMetadata {
                author: "SynOS Security Team".to_string(),
                description: "PHP webshell detection".to_string(),
                reference: vec![],
                mitre_tactics: vec!["TA0003".to_string()],
                mitre_techniques: vec!["T1505.003".to_string()],
            },
        };

        self.compiled_rules.insert(apt_rule.name.clone(), apt_rule);
        self.compiled_rules.insert(ransomware_rule.name.clone(), ransomware_rule);
        self.compiled_rules.insert(webshell_rule.name.clone(), webshell_rule);
    }

    /// Load custom YARA rule from string
    pub fn load_rule(&mut self, rule_content: &str) -> Result<()> {
        // Simplified YARA parsing (in production, use yara-rust crate)
        let rule = self.parse_yara_rule(rule_content)?;
        self.compiled_rules.insert(rule.name.clone(), rule);
        Ok(())
    }

    /// Scan file or directory with YARA rules
    pub fn scan_path(&self, path: &str, rule_names: &[String]) -> Result<Vec<YaraMatch>> {
        let mut matches = Vec::new();

        let rules_to_scan: Vec<&YaraRule> = if rule_names.is_empty() {
            self.compiled_rules.values().collect()
        } else {
            rule_names.iter()
                .filter_map(|name| self.compiled_rules.get(name))
                .collect()
        };

        if std::path::Path::new(path).is_dir() {
            for entry in WalkDir::new(path).follow_links(false) {
                let entry = entry.map_err(|e| ThreatHuntingError::YaraError(e.to_string()))?;

                if entry.file_type().is_file() {
                    if let Ok(file_matches) = self.scan_file(entry.path().to_str().unwrap(), &rules_to_scan) {
                        matches.extend(file_matches);
                    }
                }
            }
        } else {
            matches = self.scan_file(path, &rules_to_scan)?;
        }

        Ok(matches)
    }

    fn scan_file(&self, file_path: &str, rules: &[&YaraRule]) -> Result<Vec<YaraMatch>> {
        let content = std::fs::read_to_string(file_path)
            .or_else(|_| std::fs::read(file_path).map(|bytes| String::from_utf8_lossy(&bytes).to_string()))
            .map_err(|e| ThreatHuntingError::YaraError(format!("Failed to read file: {}", e)))?;

        let file_hash = self.calculate_hash(file_path)?;
        let mut matches = Vec::new();

        for rule in rules {
            if self.evaluate_rule(rule, &content) {
                let matched_strings = self.extract_matched_strings(rule, &content);

                matches.push(YaraMatch {
                    rule_name: rule.name.clone(),
                    file_path: file_path.to_string(),
                    file_hash: file_hash.clone(),
                    matched_strings,
                    mitre_tactics: rule.metadata.mitre_tactics.clone(),
                    mitre_techniques: rule.metadata.mitre_techniques.clone(),
                });
            }
        }

        Ok(matches)
    }

    fn evaluate_rule(&self, rule: &YaraRule, content: &str) -> bool {
        let mut pattern_matches = Vec::new();

        for pattern in &rule.patterns {
            let matches = match pattern.pattern_type {
                PatternType::Text => {
                    if pattern.modifiers.contains(&"nocase".to_string()) {
                        content.to_lowercase().contains(&pattern.value.to_lowercase())
                    } else {
                        content.contains(&pattern.value)
                    }
                }
                PatternType::Hex => {
                    // Simplified hex matching
                    content.contains(&pattern.value.replace(" ", ""))
                }
                PatternType::Regex => {
                    if let Ok(re) = regex::Regex::new(&pattern.value) {
                        re.is_match(content)
                    } else {
                        false
                    }
                }
            };

            pattern_matches.push(matches);
        }

        // Evaluate condition
        match rule.condition.expression.as_str() {
            "any of them" => pattern_matches.iter().any(|&m| m),
            "all of them" => pattern_matches.iter().all(|&m| m),
            expr if expr.starts_with(char::is_numeric) => {
                let count: usize = expr.chars().next().unwrap().to_digit(10).unwrap() as usize;
                pattern_matches.iter().filter(|&&m| m).count() >= count
            }
            _ => false,
        }
    }

    fn extract_matched_strings(&self, rule: &YaraRule, content: &str) -> Vec<String> {
        let mut matched = Vec::new();

        for pattern in &rule.patterns {
            match pattern.pattern_type {
                PatternType::Text => {
                    if content.contains(&pattern.value) {
                        matched.push(pattern.value.clone());
                    }
                }
                PatternType::Regex => {
                    if let Ok(re) = regex::Regex::new(&pattern.value) {
                        for cap in re.captures_iter(content) {
                            if let Some(m) = cap.get(0) {
                                matched.push(m.as_str().to_string());
                            }
                        }
                    }
                }
                _ => {}
            }
        }

        matched
    }

    fn calculate_hash(&self, file_path: &str) -> Result<String> {
        let content = std::fs::read(file_path)
            .map_err(|e| ThreatHuntingError::YaraError(format!("Failed to read file for hashing: {}", e)))?;

        let mut hasher = Sha256::new();
        hasher.update(&content);
        Ok(format!("{:x}", hasher.finalize()))
    }

    fn parse_yara_rule(&self, _content: &str) -> Result<YaraRule> {
        // Simplified parser - in production use proper YARA parser
        Ok(YaraRule {
            name: "CustomRule".to_string(),
            description: "Custom YARA rule".to_string(),
            patterns: vec![],
            condition: Condition {
                expression: "any of them".to_string(),
            },
            metadata: YaraMetadata {
                author: "Custom".to_string(),
                description: "Custom rule".to_string(),
                reference: vec![],
                mitre_tactics: vec![],
                mitre_techniques: vec![],
            },
        })
    }

    /// List all loaded rules
    pub fn list_rules(&self) -> Vec<String> {
        self.compiled_rules.keys().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_yara_engine_creation() {
        let engine = YaraEngine::new();
        assert!(!engine.compiled_rules.is_empty());
    }

    #[test]
    fn test_rule_evaluation() {
        let engine = YaraEngine::new();
        let content = "This file contains eval($_POST['cmd']) which is suspicious";

        if let Some(rule) = engine.compiled_rules.get("Webshell_PHP_Generic") {
            assert!(engine.evaluate_rule(rule, content));
        }
    }
}
