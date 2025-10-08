//! AI-Powered Interaction Deception
//!
//! Intelligent responses to attacker interactions with deception assets

use crate::{DeceptionInteraction, InteractionType, Result, DeceptionError};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// AI interaction engine
pub struct AIInteractionEngine {
    response_patterns: HashMap<String, Vec<ResponsePattern>>,
    conversation_state: HashMap<String, ConversationState>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ResponsePattern {
    trigger_keywords: Vec<String>,
    responses: Vec<String>,
    delay_ms: u64,
    believability_score: f32,
}

#[derive(Debug, Clone)]
struct ConversationState {
    session_id: String,
    interaction_count: usize,
    last_interaction: chrono::DateTime<chrono::Utc>,
    attacker_ip: String,
}

impl AIInteractionEngine {
    pub fn new() -> Self {
        let mut engine = Self {
            response_patterns: HashMap::new(),
            conversation_state: HashMap::new(),
        };

        engine.initialize_patterns();
        engine
    }

    fn initialize_patterns(&mut self) {
        // SSH interaction patterns
        self.response_patterns.insert(
            "ssh_login".to_string(),
            vec![
                ResponsePattern {
                    trigger_keywords: vec!["login".to_string(), "user".to_string()],
                    responses: vec![
                        "login: ".to_string(),
                        "Password: ".to_string(),
                        "Last login: Tue Oct  1 14:23:15 2024 from 192.168.1.1\r\n".to_string(),
                    ],
                    delay_ms: 500,
                    believability_score: 0.9,
                },
                ResponsePattern {
                    trigger_keywords: vec!["fail".to_string(), "invalid".to_string()],
                    responses: vec![
                        "Permission denied, please try again.\r\n".to_string(),
                        "Access denied.\r\n".to_string(),
                    ],
                    delay_ms: 1000,
                    believability_score: 0.95,
                },
            ],
        );

        // Database interaction patterns
        self.response_patterns.insert(
            "database_query".to_string(),
            vec![
                ResponsePattern {
                    trigger_keywords: vec!["select".to_string(), "show".to_string()],
                    responses: vec![
                        "ERROR 1045 (28000): Access denied for user 'admin'@'localhost'\r\n".to_string(),
                        "FATAL:  password authentication failed\r\n".to_string(),
                    ],
                    delay_ms: 200,
                    believability_score: 0.85,
                },
            ],
        );

        // Web admin interaction patterns
        self.response_patterns.insert(
            "web_admin".to_string(),
            vec![
                ResponsePattern {
                    trigger_keywords: vec!["admin".to_string(), "dashboard".to_string()],
                    responses: vec![
                        r#"{"status":"error","message":"Invalid credentials"}"#.to_string(),
                        "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\"Admin Area\"\r\n\r\n".to_string(),
                    ],
                    delay_ms: 300,
                    believability_score: 0.88,
                },
            ],
        );

        // File system interaction patterns
        self.response_patterns.insert(
            "file_access".to_string(),
            vec![
                ResponsePattern {
                    trigger_keywords: vec!["ls".to_string(), "dir".to_string(), "cat".to_string()],
                    responses: vec![
                        "bash: permission denied\r\n".to_string(),
                        "Access is denied.\r\n".to_string(),
                        "total 0\r\ndrwxr-xr-x 2 root root 4096 Oct  1 12:00 .\r\ndrwxr-xr-x 3 root root 4096 Oct  1 12:00 ..\r\n".to_string(),
                    ],
                    delay_ms: 100,
                    believability_score: 0.92,
                },
            ],
        );
    }

    /// Generate AI-powered response to interaction
    pub fn generate_response(&mut self, interaction: &DeceptionInteraction, input: &str) -> AIResponse {
        // Update conversation state
        let interaction_count = {
            let state = self.conversation_state
                .entry(interaction.source_ip.clone())
                .or_insert_with(|| ConversationState {
                    session_id: uuid::Uuid::new_v4().to_string(),
                    interaction_count: 0,
                    last_interaction: chrono::Utc::now(),
                    attacker_ip: interaction.source_ip.clone(),
                });

            state.interaction_count += 1;
            state.last_interaction = chrono::Utc::now();
            state.interaction_count
        };

        // Determine interaction category
        let category = self.categorize_interaction(&interaction.interaction_type, input);

        // Find matching response pattern
        if let Some(patterns) = self.response_patterns.get(&category) {
            for pattern in patterns {
                if self.matches_keywords(input, &pattern.trigger_keywords) {
                    let response_text = self.select_response(&pattern.responses, interaction_count);

                    return AIResponse {
                        text: response_text,
                        delay_ms: pattern.delay_ms + self.calculate_adaptive_delay(interaction_count),
                        believability_score: pattern.believability_score,
                        should_log: true,
                        escalate_alert: interaction_count > 5,
                    };
                }
            }
        }

        // Default response
        AIResponse {
            text: "Unknown command\r\n".to_string(),
            delay_ms: 500,
            believability_score: 0.5,
            should_log: true,
            escalate_alert: false,
        }
    }

    /// Analyze interaction pattern for threat intelligence
    pub fn analyze_interaction_pattern(&self, source_ip: &str) -> ThreatAnalysis {
        if let Some(state) = self.conversation_state.get(source_ip) {
            let sophistication = if state.interaction_count > 20 {
                "Advanced"
            } else if state.interaction_count > 10 {
                "Intermediate"
            } else {
                "Basic"
            };

            let threat_level = if state.interaction_count > 15 {
                "High"
            } else if state.interaction_count > 5 {
                "Medium"
            } else {
                "Low"
            };

            ThreatAnalysis {
                source_ip: source_ip.to_string(),
                total_interactions: state.interaction_count,
                sophistication_level: sophistication.to_string(),
                threat_level: threat_level.to_string(),
                persistence_score: (state.interaction_count as f32 / 20.0).min(1.0),
                recommendations: self.generate_recommendations(state.interaction_count),
            }
        } else {
            ThreatAnalysis::default(source_ip)
        }
    }

    /// Generate believable error messages
    pub fn generate_believable_error(&self, context: &str) -> String {
        match context {
            "ssh" => "Permission denied (publickey,password).\r\n".to_string(),
            "ftp" => "530 Login incorrect.\r\n".to_string(),
            "http" => "HTTP/1.1 403 Forbidden\r\n\r\n".to_string(),
            "database" => "ERROR 1045: Access denied for user\r\n".to_string(),
            "smb" => "NT_STATUS_LOGON_FAILURE\r\n".to_string(),
            _ => "Access Denied\r\n".to_string(),
        }
    }

    /// Simulate realistic system delays
    fn calculate_adaptive_delay(&self, interaction_count: usize) -> u64 {
        // More interactions = slightly longer delays (simulating "system load")
        let base_delay = 100;
        let load_factor = (interaction_count as u64).min(10) * 20;
        base_delay + load_factor
    }

    fn categorize_interaction(&self, interaction_type: &InteractionType, input: &str) -> String {
        let category = match interaction_type {
            InteractionType::Authentication => {
                if input.contains("ssh") || input.contains("login") {
                    "ssh_login"
                } else {
                    "web_admin"
                }
            }
            InteractionType::Access => {
                if input.contains("select") || input.contains("show") {
                    "database_query"
                } else {
                    "file_access"
                }
            }
            _ => "general",
        };
        category.to_string()
    }

    fn matches_keywords(&self, input: &str, keywords: &[String]) -> bool {
        let input_lower = input.to_lowercase();
        keywords.iter().any(|kw| input_lower.contains(&kw.to_lowercase()))
    }

    fn select_response(&self, responses: &[String], interaction_count: usize) -> String {
        // Vary responses to seem more realistic
        let index = interaction_count % responses.len();
        responses[index].clone()
    }

    fn generate_recommendations(&self, interaction_count: usize) -> Vec<String> {
        let mut recommendations = Vec::new();

        if interaction_count > 15 {
            recommendations.push("🚨 IMMEDIATE ACTION: Block source IP at firewall".to_string());
            recommendations.push("📊 Investigate for lateral movement attempts".to_string());
        } else if interaction_count > 5 {
            recommendations.push("⚠️  Monitor source IP for escalation".to_string());
            recommendations.push("📝 Review logs for credential theft attempts".to_string());
        } else {
            recommendations.push("ℹ️  Continue monitoring - initial reconnaissance phase".to_string());
        }

        recommendations
    }

    /// Get conversation statistics
    pub fn get_statistics(&self) -> HashMap<String, usize> {
        let mut stats = HashMap::new();

        let total_sessions = self.conversation_state.len();
        let total_interactions: usize = self.conversation_state.values()
            .map(|s| s.interaction_count)
            .sum();

        stats.insert("total_sessions".to_string(), total_sessions);
        stats.insert("total_interactions".to_string(), total_interactions);

        stats
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIResponse {
    pub text: String,
    pub delay_ms: u64,
    pub believability_score: f32,
    pub should_log: bool,
    pub escalate_alert: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThreatAnalysis {
    pub source_ip: String,
    pub total_interactions: usize,
    pub sophistication_level: String,
    pub threat_level: String,
    pub persistence_score: f32,
    pub recommendations: Vec<String>,
}

impl ThreatAnalysis {
    fn default(source_ip: &str) -> Self {
        Self {
            source_ip: source_ip.to_string(),
            total_interactions: 0,
            sophistication_level: "Unknown".to_string(),
            threat_level: "Low".to_string(),
            persistence_score: 0.0,
            recommendations: vec!["Monitor for additional activity".to_string()],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ThreatSeverity;
    use uuid::Uuid;

    #[test]
    fn test_ai_response_generation() {
        let mut engine = AIInteractionEngine::new();

        let interaction = DeceptionInteraction {
            id: Uuid::new_v4(),
            asset_id: Uuid::new_v4(),
            timestamp: chrono::Utc::now(),
            source_ip: "10.0.0.5".to_string(),
            source_port: 12345,
            interaction_type: InteractionType::Authentication,
            details: "SSH login attempt".to_string(),
            severity: ThreatSeverity::Medium,
            ai_analysis: None,
        };

        let response = engine.generate_response(&interaction, "login admin");

        assert!(!response.text.is_empty());
        assert!(response.believability_score > 0.0);
    }

    #[test]
    fn test_threat_analysis() {
        let mut engine = AIInteractionEngine::new();
        let source_ip = "192.168.1.100";

        // Simulate multiple interactions
        for _ in 0..10 {
            let interaction = DeceptionInteraction {
                id: Uuid::new_v4(),
                asset_id: Uuid::new_v4(),
                timestamp: chrono::Utc::now(),
                source_ip: source_ip.to_string(),
                source_port: 12345,
                interaction_type: InteractionType::Access,
                details: "File access".to_string(),
                severity: ThreatSeverity::Low,
                ai_analysis: None,
            };

            engine.generate_response(&interaction, "ls /etc");
        }

        let analysis = engine.analyze_interaction_pattern(source_ip);

        assert_eq!(analysis.total_interactions, 10);
        assert_eq!(analysis.threat_level, "Medium");
        assert!(!analysis.recommendations.is_empty());
    }

    #[test]
    fn test_believable_errors() {
        let engine = AIInteractionEngine::new();

        let ssh_error = engine.generate_believable_error("ssh");
        assert!(ssh_error.contains("Permission denied"));

        let db_error = engine.generate_believable_error("database");
        assert!(db_error.contains("Access denied"));
    }
}
