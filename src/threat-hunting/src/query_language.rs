//! Custom Hunt Query Language
//!
//! Domain-specific language for threat hunting queries

use crate::{Result, ThreatHuntingError, FindingSeverity, Evidence, ArtifactType};
use std::collections::HashMap;

/// Hunt query engine
pub struct HuntQueryEngine {
    data_sources: HashMap<String, DataSource>,
}

#[derive(Debug, Clone)]
struct DataSource {
    name: String,
    source_type: SourceType,
    data: Vec<HashMap<String, String>>,
}

#[derive(Debug, Clone, PartialEq)]
enum SourceType {
    Process,
    Network,
    File,
    Registry,
    Event,
}

#[derive(Debug, Clone)]
pub struct QueryResult {
    pub description: String,
    pub severity: FindingSeverity,
    pub evidence: Vec<Evidence>,
    pub tactics: Vec<String>,
    pub techniques: Vec<String>,
    pub confidence: f32,
}

impl HuntQueryEngine {
    pub fn new() -> Self {
        let mut engine = Self {
            data_sources: HashMap::new(),
        };
        engine.initialize_mock_data();
        engine
    }

    fn initialize_mock_data(&mut self) {
        // Mock process data
        let mut process_data = Vec::new();
        process_data.push({
            let mut p = HashMap::new();
            p.insert("name".to_string(), "cmd.exe".to_string());
            p.insert("commandline".to_string(), "cmd.exe /c whoami".to_string());
            p.insert("parent".to_string(), "powershell.exe".to_string());
            p.insert("user".to_string(), "SYSTEM".to_string());
            p
        });
        process_data.push({
            let mut p = HashMap::new();
            p.insert("name".to_string(), "net.exe".to_string());
            p.insert("commandline".to_string(), "net user administrator P@ssw0rd /add".to_string());
            p.insert("parent".to_string(), "cmd.exe".to_string());
            p.insert("user".to_string(), "Administrator".to_string());
            p
        });

        self.data_sources.insert("processes".to_string(), DataSource {
            name: "processes".to_string(),
            source_type: SourceType::Process,
            data: process_data,
        });

        // Mock network data
        let mut network_data = Vec::new();
        network_data.push({
            let mut n = HashMap::new();
            n.insert("destination_ip".to_string(), "192.168.1.100".to_string());
            n.insert("destination_port".to_string(), "445".to_string());
            n.insert("protocol".to_string(), "SMB".to_string());
            n.insert("process".to_string(), "explorer.exe".to_string());
            n
        });

        self.data_sources.insert("network".to_string(), DataSource {
            name: "network".to_string(),
            source_type: SourceType::Network,
            data: network_data,
        });

        // Mock file data
        let mut file_data = Vec::new();
        file_data.push({
            let mut f = HashMap::new();
            f.insert("path".to_string(), "C:\\Windows\\Temp\\malicious.exe".to_string());
            f.insert("action".to_string(), "created".to_string());
            f.insert("process".to_string(), "powershell.exe".to_string());
            f
        });

        self.data_sources.insert("files".to_string(), DataSource {
            name: "files".to_string(),
            source_type: SourceType::File,
            data: file_data,
        });
    }

    /// Execute hunt query
    pub fn execute(&self, query: &str) -> Result<Vec<QueryResult>> {
        let parsed_query = self.parse_query(query)?;
        let results = self.execute_parsed_query(&parsed_query)?;
        Ok(results)
    }

    fn parse_query(&self, query: &str) -> Result<ParsedQuery> {
        // Simplified query parser
        // Format: "HUNT <source> WHERE <field> <operator> <value> [AND/OR ...]"

        let parts: Vec<&str> = query.split_whitespace().collect();

        if parts.len() < 4 || parts[0].to_uppercase() != "HUNT" {
            return Err(ThreatHuntingError::QueryError(
                "Query must start with 'HUNT <source> WHERE'".to_string()
            ));
        }

        let source = parts[1].to_string();

        if parts[2].to_uppercase() != "WHERE" {
            return Err(ThreatHuntingError::QueryError(
                "Expected 'WHERE' clause".to_string()
            ));
        }

        // Parse conditions
        let condition_str = parts[3..].join(" ");
        let conditions = self.parse_conditions(&condition_str)?;

        Ok(ParsedQuery {
            source,
            conditions,
        })
    }

    fn parse_conditions(&self, condition_str: &str) -> Result<Vec<Condition>> {
        let mut conditions = Vec::new();

        // Split by AND/OR (simplified - doesn't handle parentheses)
        let parts: Vec<&str> = condition_str.split(" AND ").collect();

        for part in parts {
            let tokens: Vec<&str> = part.split_whitespace().collect();

            if tokens.len() >= 3 {
                let field = tokens[0].to_string();
                let operator = match tokens[1].to_uppercase().as_str() {
                    "=" | "==" => Operator::Equals,
                    "!=" => Operator::NotEquals,
                    "CONTAINS" => Operator::Contains,
                    "STARTSWITH" => Operator::StartsWith,
                    "ENDSWITH" => Operator::EndsWith,
                    "MATCHES" => Operator::Regex,
                    _ => return Err(ThreatHuntingError::QueryError(
                        format!("Unknown operator: {}", tokens[1])
                    )),
                };
                let value = tokens[2..].join(" ").trim_matches('"').to_string();

                conditions.push(Condition {
                    field,
                    operator,
                    value,
                    logical_op: LogicalOperator::And,
                });
            }
        }

        Ok(conditions)
    }

    fn execute_parsed_query(&self, query: &ParsedQuery) -> Result<Vec<QueryResult>> {
        let data_source = self.data_sources.get(&query.source)
            .ok_or_else(|| ThreatHuntingError::QueryError(
                format!("Data source '{}' not found", query.source)
            ))?;

        let mut results = Vec::new();

        for record in &data_source.data {
            if self.evaluate_conditions(&query.conditions, record) {
                let result = self.create_query_result(record, &data_source.source_type);
                results.push(result);
            }
        }

        Ok(results)
    }

    fn evaluate_conditions(&self, conditions: &[Condition], record: &HashMap<String, String>) -> bool {
        for condition in conditions {
            let field_value = record.get(&condition.field).map(|s| s.as_str()).unwrap_or("");

            let matches = match condition.operator {
                Operator::Equals => field_value == condition.value,
                Operator::NotEquals => field_value != condition.value,
                Operator::Contains => field_value.contains(&condition.value),
                Operator::StartsWith => field_value.starts_with(&condition.value),
                Operator::EndsWith => field_value.ends_with(&condition.value),
                Operator::Regex => {
                    if let Ok(re) = regex::Regex::new(&condition.value) {
                        re.is_match(field_value)
                    } else {
                        false
                    }
                }
                _ => false,
            };

            if !matches {
                return false;
            }
        }

        true
    }

    fn create_query_result(&self, record: &HashMap<String, String>, source_type: &SourceType) -> QueryResult {
        let (severity, tactics, techniques, artifact_type) = match source_type {
            SourceType::Process => {
                if record.get("user").map(|u| u == "SYSTEM").unwrap_or(false) {
                    (
                        FindingSeverity::High,
                        vec!["TA0004".to_string()],
                        vec!["T1548".to_string()],
                        ArtifactType::Process,
                    )
                } else {
                    (
                        FindingSeverity::Medium,
                        vec!["TA0002".to_string()],
                        vec!["T1059".to_string()],
                        ArtifactType::Process,
                    )
                }
            }
            SourceType::Network => (
                FindingSeverity::Medium,
                vec!["TA0008".to_string()],
                vec!["T1021".to_string()],
                ArtifactType::Network,
            ),
            SourceType::File => (
                FindingSeverity::High,
                vec!["TA0003".to_string()],
                vec!["T1543".to_string()],
                ArtifactType::File,
            ),
            _ => (
                FindingSeverity::Low,
                vec![],
                vec![],
                ArtifactType::Log,
            ),
        };

        let description = format!(
            "Suspicious {:?} activity detected: {}",
            source_type,
            record.values().next().unwrap_or(&"<unknown>".to_string())
        );

        let evidence = record.iter().map(|(k, v)| {
            Evidence {
                source: k.clone(),
                artifact_type: artifact_type.clone(),
                data: v.clone(),
                hash: None,
                timestamp: chrono::Utc::now(),
            }
        }).collect();

        QueryResult {
            description,
            severity,
            evidence,
            tactics,
            techniques,
            confidence: 0.75,
        }
    }

    /// Add custom data source
    pub fn add_data_source(&mut self, name: String, data: Vec<HashMap<String, String>>) {
        self.data_sources.insert(name.clone(), DataSource {
            name: name.clone(),
            source_type: SourceType::Event,
            data,
        });
    }

    /// List available data sources
    pub fn list_data_sources(&self) -> Vec<String> {
        self.data_sources.keys().cloned().collect()
    }
}

#[derive(Debug, Clone)]
struct ParsedQuery {
    source: String,
    conditions: Vec<Condition>,
}

#[derive(Debug, Clone)]
struct Condition {
    field: String,
    operator: Operator,
    value: String,
    logical_op: LogicalOperator,
}

#[derive(Debug, Clone, PartialEq)]
enum Operator {
    Equals,
    NotEquals,
    Contains,
    StartsWith,
    EndsWith,
    Regex,
    GreaterThan,
    LessThan,
}

#[derive(Debug, Clone, PartialEq)]
enum LogicalOperator {
    And,
    Or,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_execution() {
        let engine = HuntQueryEngine::new();
        let results = engine.execute("HUNT processes WHERE user = SYSTEM").unwrap();
        assert!(!results.is_empty());
    }

    #[test]
    fn test_contains_query() {
        let engine = HuntQueryEngine::new();
        let results = engine.execute("HUNT processes WHERE commandline CONTAINS whoami").unwrap();
        assert!(!results.is_empty());
    }

    #[test]
    fn test_network_query() {
        let engine = HuntQueryEngine::new();
        let results = engine.execute("HUNT network WHERE destination_port = 445").unwrap();
        assert!(!results.is_empty());
    }
}
