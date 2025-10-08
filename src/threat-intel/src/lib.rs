//! # SynOS Threat Intelligence Feed Integration
//!
//! Integrates with multiple threat intelligence sources:
//! - MISP (Malware Information Sharing Platform)
//! - AlienVault OTX (Open Threat Exchange)
//! - abuse.ch feeds (URLhaus, Feodo, SSL Blacklist)
//! - Custom IOC management

pub mod misp_connector;
pub mod otx_connector;
pub mod abusech_connector;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use sha2::{Sha256, Digest};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ThreatIntelError {
    #[error("API request failed: {0}")]
    ApiError(String),
    #[error("Invalid IOC format: {0}")]
    InvalidIOC(String),
    #[error("Feed unavailable: {0}")]
    FeedUnavailable(String),
    #[error("Correlation failed: {0}")]
    CorrelationError(String),
}

pub type Result<T> = std::result::Result<T, ThreatIntelError>;

/// Indicator of Compromise (IOC) types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum IOCType {
    IPAddress,
    Domain,
    URL,
    FileHash,
    EmailAddress,
    CVE,
    YARA,
    Mutex,
    RegistryKey,
}

/// Threat severity levels
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum ThreatSeverity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

/// Indicator of Compromise
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IOC {
    pub ioc_type: IOCType,
    pub value: String,
    pub severity: ThreatSeverity,
    pub source: String,
    pub first_seen: DateTime<Utc>,
    pub last_seen: DateTime<Utc>,
    pub confidence: f64,
    pub tags: Vec<String>,
    pub description: String,
    pub references: Vec<String>,
}

impl IOC {
    pub fn new(ioc_type: IOCType, value: String, source: String) -> Self {
        let now = Utc::now();
        Self {
            ioc_type,
            value,
            severity: ThreatSeverity::Medium,
            source,
            first_seen: now,
            last_seen: now,
            confidence: 0.5,
            tags: Vec::new(),
            description: String::new(),
            references: Vec::new(),
        }
    }

    pub fn hash(&self) -> String {
        let mut hasher = Sha256::new();
        hasher.update(format!("{:?}:{}", self.ioc_type, self.value));
        format!("{:x}", hasher.finalize())
    }
}

/// MISP Event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MISPEvent {
    pub id: String,
    pub info: String,
    pub threat_level_id: u8,
    pub published: bool,
    pub timestamp: DateTime<Utc>,
    pub attributes: Vec<MISPAttribute>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MISPAttribute {
    pub id: String,
    pub event_id: String,
    pub category: String,
    pub attribute_type: String,
    pub value: String,
    pub to_ids: bool,
}

/// AlienVault OTX Pulse
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OTXPulse {
    pub id: String,
    pub name: String,
    pub description: String,
    pub author_name: String,
    pub created: DateTime<Utc>,
    pub modified: DateTime<Utc>,
    pub indicators: Vec<OTXIndicator>,
    pub tags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OTXIndicator {
    pub indicator: String,
    pub indicator_type: String,
    pub description: String,
}

/// abuse.ch Feed Entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AbuseCHEntry {
    pub id: String,
    pub feed_type: String,
    pub value: String,
    pub malware_family: Option<String>,
    pub first_seen: DateTime<Utc>,
    pub tags: Vec<String>,
}

/// IOC Manager
pub struct IOCManager {
    iocs: HashMap<String, IOC>,
    correlations: Vec<IOCCorrelation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IOCCorrelation {
    pub ioc1_hash: String,
    pub ioc2_hash: String,
    pub correlation_type: CorrelationType,
    pub confidence: f64,
    pub discovered: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CorrelationType {
    SameSource,
    SameCampaign,
    RelatedInfrastructure,
    CommonTags,
    TemporalProximity,
}

impl IOCManager {
    pub fn new() -> Self {
        Self {
            iocs: HashMap::new(),
            correlations: Vec::new(),
        }
    }

    pub fn add_ioc(&mut self, ioc: IOC) -> String {
        let hash = ioc.hash();
        self.iocs.insert(hash.clone(), ioc);
        hash
    }

    pub fn get_ioc(&self, hash: &str) -> Option<&IOC> {
        self.iocs.get(hash)
    }

    pub fn search_by_value(&self, value: &str) -> Vec<&IOC> {
        self.iocs.values()
            .filter(|ioc| ioc.value.contains(value))
            .collect()
    }

    pub fn search_by_type(&self, ioc_type: &IOCType) -> Vec<&IOC> {
        self.iocs.values()
            .filter(|ioc| &ioc.ioc_type == ioc_type)
            .collect()
    }

    pub fn search_by_tag(&self, tag: &str) -> Vec<&IOC> {
        self.iocs.values()
            .filter(|ioc| ioc.tags.iter().any(|t| t == tag))
            .collect()
    }

    pub fn add_correlation(&mut self, ioc1: &str, ioc2: &str, corr_type: CorrelationType, confidence: f64) {
        let correlation = IOCCorrelation {
            ioc1_hash: ioc1.to_string(),
            ioc2_hash: ioc2.to_string(),
            correlation_type: corr_type,
            confidence,
            discovered: Utc::now(),
        };
        self.correlations.push(correlation);
    }

    pub fn get_related_iocs(&self, hash: &str) -> Vec<(&IOC, &IOCCorrelation)> {
        let mut related = Vec::new();
        for corr in &self.correlations {
            if corr.ioc1_hash == hash {
                if let Some(ioc) = self.iocs.get(&corr.ioc2_hash) {
                    related.push((ioc, corr));
                }
            } else if corr.ioc2_hash == hash {
                if let Some(ioc) = self.iocs.get(&corr.ioc1_hash) {
                    related.push((ioc, corr));
                }
            }
        }
        related
    }

    pub fn auto_correlate(&mut self) {
        // Collect correlation data first to avoid borrow conflicts
        let mut correlations_to_add = Vec::new();

        let ioc_list: Vec<_> = self.iocs.iter().collect();

        for i in 0..ioc_list.len() {
            for j in i+1..ioc_list.len() {
                let (hash1, ioc1) = ioc_list[i];
                let (hash2, ioc2) = ioc_list[j];

                // Correlate by source
                if ioc1.source == ioc2.source {
                    correlations_to_add.push((hash1.clone(), hash2.clone(), CorrelationType::SameSource, 0.7));
                }

                // Correlate by common tags
                let common_tags: Vec<_> = ioc1.tags.iter()
                    .filter(|t| ioc2.tags.contains(t))
                    .collect();

                if !common_tags.is_empty() {
                    let confidence = (common_tags.len() as f64) / (ioc1.tags.len().max(ioc2.tags.len()) as f64);
                    correlations_to_add.push((hash1.clone(), hash2.clone(), CorrelationType::CommonTags, confidence));
                }

                // Correlate by temporal proximity (within 24 hours)
                let time_diff = (ioc1.first_seen - ioc2.first_seen).num_hours().abs();
                if time_diff <= 24 {
                    let confidence = 1.0 - (time_diff as f64 / 24.0);
                    correlations_to_add.push((hash1.clone(), hash2.clone(), CorrelationType::TemporalProximity, confidence));
                }
            }
        }

        // Now add all correlations
        for (h1, h2, corr_type, conf) in correlations_to_add {
            self.add_correlation(&h1, &h2, corr_type, conf);
        }
    }

    pub fn get_stats(&self) -> IOCStats {
        let mut by_type: HashMap<String, usize> = HashMap::new();
        let mut by_severity: HashMap<String, usize> = HashMap::new();
        let mut by_source: HashMap<String, usize> = HashMap::new();

        for ioc in self.iocs.values() {
            *by_type.entry(format!("{:?}", ioc.ioc_type)).or_insert(0) += 1;
            *by_severity.entry(format!("{:?}", ioc.severity)).or_insert(0) += 1;
            *by_source.entry(ioc.source.clone()).or_insert(0) += 1;
        }

        IOCStats {
            total_iocs: self.iocs.len(),
            by_type,
            by_severity,
            by_source,
            total_correlations: self.correlations.len(),
        }
    }

    /// Get all IOCs (for iteration)
    pub fn get_iocs(&self) -> &HashMap<String, IOC> {
        &self.iocs
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct IOCStats {
    pub total_iocs: usize,
    pub by_type: HashMap<String, usize>,
    pub by_severity: HashMap<String, usize>,
    pub by_source: HashMap<String, usize>,
    pub total_correlations: usize,
}

impl Default for IOCManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ioc_creation() {
        let ioc = IOC::new(
            IOCType::IPAddress,
            "192.0.2.1".to_string(),
            "Test".to_string()
        );
        assert_eq!(ioc.ioc_type, IOCType::IPAddress);
        assert_eq!(ioc.value, "192.0.2.1");
    }

    #[test]
    fn test_ioc_hash() {
        let ioc = IOC::new(
            IOCType::Domain,
            "evil.example.com".to_string(),
            "Test".to_string()
        );
        let hash = ioc.hash();
        assert!(!hash.is_empty());
        assert_eq!(hash.len(), 64); // SHA256 hex length
    }

    #[test]
    fn test_ioc_manager() {
        let mut manager = IOCManager::new();

        let ioc1 = IOC::new(
            IOCType::IPAddress,
            "203.0.113.1".to_string(),
            "MISP".to_string()
        );

        let hash = manager.add_ioc(ioc1);
        assert!(manager.get_ioc(&hash).is_some());
    }

    #[test]
    fn test_ioc_search() {
        let mut manager = IOCManager::new();

        let mut ioc = IOC::new(
            IOCType::Domain,
            "malware.example.com".to_string(),
            "OTX".to_string()
        );
        ioc.tags.push("malware".to_string());

        manager.add_ioc(ioc);

        let results = manager.search_by_tag("malware");
        assert_eq!(results.len(), 1);
    }

    #[test]
    fn test_auto_correlation() {
        let mut manager = IOCManager::new();

        let mut ioc1 = IOC::new(
            IOCType::IPAddress,
            "198.51.100.1".to_string(),
            "MISP".to_string()
        );
        ioc1.tags.push("apt28".to_string());

        let mut ioc2 = IOC::new(
            IOCType::Domain,
            "apt28.example.com".to_string(),
            "MISP".to_string()
        );
        ioc2.tags.push("apt28".to_string());

        manager.add_ioc(ioc1);
        let hash2 = manager.add_ioc(ioc2);

        manager.auto_correlate();

        let related = manager.get_related_iocs(&hash2);
        assert!(!related.is_empty());
    }
}
