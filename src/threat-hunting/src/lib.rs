//! SynOS Advanced Threat Hunting Platform
//!
//! Comprehensive threat hunting capabilities with YARA, Sigma, custom queries, and timeline analysis

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use uuid::Uuid;

pub mod yara_engine;
pub mod sigma_detection;
pub mod query_language;
pub mod ioc_scanner;
pub mod timeline_analysis;
pub mod threat_profiling;

pub use yara_engine::YaraEngine;
pub use sigma_detection::SigmaDetectionEngine;
pub use query_language::HuntQueryEngine;
pub use ioc_scanner::IOCScanner;
pub use timeline_analysis::TimelineAnalyzer;
pub use threat_profiling::ThreatActorProfiler;

/// Threat hunting platform manager
pub struct ThreatHuntingPlatform {
    yara_engine: YaraEngine,
    sigma_engine: SigmaDetectionEngine,
    query_engine: HuntQueryEngine,
    ioc_scanner: IOCScanner,
    timeline_analyzer: TimelineAnalyzer,
    threat_profiler: ThreatActorProfiler,
    hunt_sessions: HashMap<Uuid, HuntSession>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HuntSession {
    pub id: Uuid,
    pub name: String,
    pub description: String,
    pub created_at: DateTime<Utc>,
    pub status: HuntStatus,
    pub findings: Vec<HuntFinding>,
    pub queries_executed: Vec<String>,
    pub iocs_searched: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum HuntStatus {
    Active,
    Paused,
    Completed,
    Archived,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HuntFinding {
    pub id: Uuid,
    pub session_id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub finding_type: FindingType,
    pub severity: FindingSeverity,
    pub description: String,
    pub evidence: Vec<Evidence>,
    pub mitre_tactics: Vec<String>,
    pub mitre_techniques: Vec<String>,
    pub confidence_score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FindingType {
    YaraMatch,
    SigmaDetection,
    IOCMatch,
    AnomalousBehavior,
    TTPMatch,
    TimelineCorrelation,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum FindingSeverity {
    Critical,
    High,
    Medium,
    Low,
    Info,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence {
    pub source: String,
    pub artifact_type: ArtifactType,
    pub data: String,
    pub hash: Option<String>,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ArtifactType {
    File,
    Process,
    Network,
    Registry,
    Memory,
    Log,
}

pub type Result<T> = std::result::Result<T, ThreatHuntingError>;

#[derive(Debug, thiserror::Error)]
pub enum ThreatHuntingError {
    #[error("YARA rule error: {0}")]
    YaraError(String),

    #[error("Sigma detection error: {0}")]
    SigmaError(String),

    #[error("Query parsing error: {0}")]
    QueryError(String),

    #[error("IOC scanning error: {0}")]
    IOCError(String),

    #[error("Timeline analysis error: {0}")]
    TimelineError(String),

    #[error("Profiling error: {0}")]
    ProfilingError(String),

    #[error("Session not found: {0}")]
    SessionNotFound(Uuid),
}

impl ThreatHuntingPlatform {
    pub fn new() -> Self {
        Self {
            yara_engine: YaraEngine::new(),
            sigma_engine: SigmaDetectionEngine::new(),
            query_engine: HuntQueryEngine::new(),
            ioc_scanner: IOCScanner::new(),
            timeline_analyzer: TimelineAnalyzer::new(),
            threat_profiler: ThreatActorProfiler::new(),
            hunt_sessions: HashMap::new(),
        }
    }

    /// Create new hunting session
    pub fn create_hunt_session(&mut self, name: String, description: String) -> Uuid {
        let session = HuntSession {
            id: Uuid::new_v4(),
            name,
            description,
            created_at: Utc::now(),
            status: HuntStatus::Active,
            findings: Vec::new(),
            queries_executed: Vec::new(),
            iocs_searched: Vec::new(),
        };

        let id = session.id;
        self.hunt_sessions.insert(id, session);
        id
    }

    /// Execute YARA scan
    pub fn yara_scan(&mut self, session_id: Uuid, path: &str, rules: Vec<String>) -> Result<Vec<HuntFinding>> {
        let session = self.hunt_sessions.get_mut(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        let matches = self.yara_engine.scan_path(path, &rules)?;

        let findings: Vec<HuntFinding> = matches.into_iter().map(|m| {
            HuntFinding {
                id: Uuid::new_v4(),
                session_id,
                timestamp: Utc::now(),
                finding_type: FindingType::YaraMatch,
                severity: FindingSeverity::High,
                description: format!("YARA rule '{}' matched: {}", m.rule_name, m.file_path),
                evidence: vec![Evidence {
                    source: m.file_path,
                    artifact_type: ArtifactType::File,
                    data: m.matched_strings.join(", "),
                    hash: Some(m.file_hash),
                    timestamp: Utc::now(),
                }],
                mitre_tactics: m.mitre_tactics,
                mitre_techniques: m.mitre_techniques,
                confidence_score: 0.9,
            }
        }).collect();

        session.findings.extend(findings.clone());
        Ok(findings)
    }

    /// Execute Sigma detection
    pub fn sigma_detect(&mut self, session_id: Uuid, log_source: &str, sigma_rules: Vec<String>) -> Result<Vec<HuntFinding>> {
        let session = self.hunt_sessions.get_mut(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        let detections = self.sigma_engine.detect(log_source, &sigma_rules)?;

        let findings: Vec<HuntFinding> = detections.into_iter().map(|d| {
            HuntFinding {
                id: Uuid::new_v4(),
                session_id,
                timestamp: Utc::now(),
                finding_type: FindingType::SigmaDetection,
                severity: d.severity,
                description: format!("Sigma detection: {}", d.title),
                evidence: d.matched_events.into_iter().map(|e| Evidence {
                    source: log_source.to_string(),
                    artifact_type: ArtifactType::Log,
                    data: e,
                    hash: None,
                    timestamp: Utc::now(),
                }).collect(),
                mitre_tactics: d.mitre_tactics,
                mitre_techniques: d.mitre_techniques,
                confidence_score: d.confidence,
            }
        }).collect();

        session.findings.extend(findings.clone());
        Ok(findings)
    }

    /// Execute custom hunt query
    pub fn execute_hunt_query(&mut self, session_id: Uuid, query: &str) -> Result<Vec<HuntFinding>> {
        let session = self.hunt_sessions.get_mut(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        session.queries_executed.push(query.to_string());

        let results = self.query_engine.execute(query)?;

        let findings: Vec<HuntFinding> = results.into_iter().map(|r| {
            HuntFinding {
                id: Uuid::new_v4(),
                session_id,
                timestamp: Utc::now(),
                finding_type: FindingType::AnomalousBehavior,
                severity: r.severity,
                description: r.description,
                evidence: r.evidence,
                mitre_tactics: r.tactics,
                mitre_techniques: r.techniques,
                confidence_score: r.confidence,
            }
        }).collect();

        session.findings.extend(findings.clone());
        Ok(findings)
    }

    /// Scan for IOCs
    pub fn scan_iocs(&mut self, session_id: Uuid, iocs: Vec<String>) -> Result<Vec<HuntFinding>> {
        let session = self.hunt_sessions.get_mut(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        session.iocs_searched.extend(iocs.clone());

        let matches = self.ioc_scanner.scan_system(&iocs)?;

        let findings: Vec<HuntFinding> = matches.into_iter().map(|m| {
            HuntFinding {
                id: Uuid::new_v4(),
                session_id,
                timestamp: Utc::now(),
                finding_type: FindingType::IOCMatch,
                severity: FindingSeverity::Critical,
                description: format!("IOC match: {} found in {}", m.ioc, m.location),
                evidence: vec![Evidence {
                    source: m.location,
                    artifact_type: m.artifact_type,
                    data: m.context,
                    hash: m.hash,
                    timestamp: Utc::now(),
                }],
                mitre_tactics: vec![],
                mitre_techniques: vec![],
                confidence_score: 0.95,
            }
        }).collect();

        session.findings.extend(findings.clone());
        Ok(findings)
    }

    /// Analyze timeline
    pub fn analyze_timeline(&mut self, session_id: Uuid, start: DateTime<Utc>, end: DateTime<Utc>) -> Result<Vec<HuntFinding>> {
        let session = self.hunt_sessions.get(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        let correlations = self.timeline_analyzer.analyze(start, end, &session.findings)?;

        let findings: Vec<HuntFinding> = correlations.into_iter().map(|c| {
            HuntFinding {
                id: Uuid::new_v4(),
                session_id,
                timestamp: Utc::now(),
                finding_type: FindingType::TimelineCorrelation,
                severity: c.severity,
                description: c.description,
                evidence: c.correlated_events,
                mitre_tactics: c.tactics,
                mitre_techniques: c.techniques,
                confidence_score: c.confidence,
            }
        }).collect();

        Ok(findings)
    }

    /// Profile threat actor
    pub fn profile_threat_actor(&self, session_id: Uuid) -> Result<ThreatActorProfile> {
        let session = self.hunt_sessions.get(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        self.threat_profiler.profile(&session.findings)
    }

    /// Get session statistics
    pub fn get_session_stats(&self, session_id: Uuid) -> Result<HuntSessionStats> {
        let session = self.hunt_sessions.get(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        let mut severity_counts = HashMap::new();
        let mut finding_type_counts = HashMap::new();

        for finding in &session.findings {
            *severity_counts.entry(format!("{:?}", finding.severity)).or_insert(0) += 1;
            *finding_type_counts.entry(format!("{:?}", finding.finding_type)).or_insert(0) += 1;
        }

        Ok(HuntSessionStats {
            session_id,
            total_findings: session.findings.len(),
            queries_executed: session.queries_executed.len(),
            iocs_searched: session.iocs_searched.len(),
            severity_distribution: severity_counts,
            finding_type_distribution: finding_type_counts,
            highest_severity: session.findings.iter()
                .max_by_key(|f| &f.severity)
                .map(|f| f.severity.clone())
                .unwrap_or(FindingSeverity::Info),
        })
    }

    /// List all sessions
    pub fn list_sessions(&self) -> Vec<&HuntSession> {
        self.hunt_sessions.values().collect()
    }

    /// Close hunt session
    pub fn close_session(&mut self, session_id: Uuid) -> Result<()> {
        let session = self.hunt_sessions.get_mut(&session_id)
            .ok_or(ThreatHuntingError::SessionNotFound(session_id))?;

        session.status = HuntStatus::Completed;
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HuntSessionStats {
    pub session_id: Uuid,
    pub total_findings: usize,
    pub queries_executed: usize,
    pub iocs_searched: usize,
    pub severity_distribution: HashMap<String, usize>,
    pub finding_type_distribution: HashMap<String, usize>,
    pub highest_severity: FindingSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThreatActorProfile {
    pub name: String,
    pub confidence: f32,
    pub ttps: Vec<String>,
    pub mitre_tactics: Vec<String>,
    pub mitre_techniques: Vec<String>,
    pub indicators: Vec<String>,
    pub attribution_score: f32,
}

impl Default for ThreatHuntingPlatform {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_hunt_session() {
        let mut platform = ThreatHuntingPlatform::new();
        let session_id = platform.create_hunt_session(
            "APT Hunt".to_string(),
            "Hunting for APT28 indicators".to_string(),
        );

        assert!(platform.hunt_sessions.contains_key(&session_id));
    }

    #[test]
    fn test_session_stats() {
        let mut platform = ThreatHuntingPlatform::new();
        let session_id = platform.create_hunt_session(
            "Test Hunt".to_string(),
            "Test session".to_string(),
        );

        let stats = platform.get_session_stats(session_id).unwrap();
        assert_eq!(stats.total_findings, 0);
        assert_eq!(stats.queries_executed, 0);
    }
}
