//! # SynOS Deception Technology Framework
//!
//! Advanced deception and honeypot technology for threat detection

pub mod honey_tokens;
pub mod credential_deception;
pub mod network_decoys;
pub mod ai_interaction;

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use thiserror::Error;
use uuid::Uuid;

#[derive(Error, Debug)]
pub enum DeceptionError {
    #[error("Token generation failed: {0}")]
    TokenGenerationError(String),
    #[error("Decoy deployment failed: {0}")]
    DecoyDeploymentError(String),
    #[error("Interaction recording failed: {0}")]
    InteractionError(String),
    #[error("AI analysis failed: {0}")]
    AIAnalysisError(String),
}

pub type Result<T> = std::result::Result<T, DeceptionError>;

/// Deception asset types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AssetType {
    HoneyToken,
    FakeCredential,
    NetworkDecoy,
    FileDecoy,
    DatabaseDecoy,
    ServiceDecoy,
}

/// Deception asset
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeceptionAsset {
    pub id: Uuid,
    pub asset_type: AssetType,
    pub name: String,
    pub description: String,
    pub deployed_at: DateTime<Utc>,
    pub location: String,
    pub metadata: HashMap<String, String>,
    pub interaction_count: usize,
}

impl DeceptionAsset {
    pub fn new(asset_type: AssetType, name: String, description: String, location: String) -> Self {
        Self {
            id: Uuid::new_v4(),
            asset_type,
            name,
            description,
            deployed_at: Utc::now(),
            location,
            metadata: HashMap::new(),
            interaction_count: 0,
        }
    }

    pub fn with_metadata(mut self, key: String, value: String) -> Self {
        self.metadata.insert(key, value);
        self
    }

    pub fn record_interaction(&mut self) {
        self.interaction_count += 1;
    }
}

/// Interaction with deception asset
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeceptionInteraction {
    pub id: Uuid,
    pub asset_id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub source_ip: String,
    pub source_port: u16,
    pub interaction_type: InteractionType,
    pub details: String,
    pub severity: ThreatSeverity,
    pub ai_analysis: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum InteractionType {
    Access,
    Modification,
    Deletion,
    Authentication,
    DataExfiltration,
    NetworkScan,
    ServiceProbe,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ThreatSeverity {
    Low,
    Medium,
    High,
    Critical,
}

impl DeceptionInteraction {
    pub fn new(
        asset_id: Uuid,
        source_ip: String,
        source_port: u16,
        interaction_type: InteractionType,
        details: String,
    ) -> Self {
        let severity = Self::assess_severity(&interaction_type);

        Self {
            id: Uuid::new_v4(),
            asset_id,
            timestamp: Utc::now(),
            source_ip,
            source_port,
            interaction_type,
            details,
            severity,
            ai_analysis: None,
        }
    }

    fn assess_severity(interaction_type: &InteractionType) -> ThreatSeverity {
        match interaction_type {
            InteractionType::Access => ThreatSeverity::Low,
            InteractionType::NetworkScan => ThreatSeverity::Low,
            InteractionType::ServiceProbe => ThreatSeverity::Medium,
            InteractionType::Authentication => ThreatSeverity::Medium,
            InteractionType::Modification => ThreatSeverity::High,
            InteractionType::Deletion => ThreatSeverity::High,
            InteractionType::DataExfiltration => ThreatSeverity::Critical,
        }
    }

    pub fn add_ai_analysis(&mut self, analysis: String) {
        self.ai_analysis = Some(analysis);
    }
}

/// Deception manager
pub struct DeceptionManager {
    assets: HashMap<Uuid, DeceptionAsset>,
    interactions: Vec<DeceptionInteraction>,
}

impl DeceptionManager {
    pub fn new() -> Self {
        Self {
            assets: HashMap::new(),
            interactions: Vec::new(),
        }
    }

    /// Deploy deception asset
    pub fn deploy_asset(&mut self, asset: DeceptionAsset) -> Uuid {
        let id = asset.id;
        self.assets.insert(id, asset);
        id
    }

    /// Record interaction with asset
    pub fn record_interaction(&mut self, interaction: DeceptionInteraction) -> Result<()> {
        // Update asset interaction count
        if let Some(asset) = self.assets.get_mut(&interaction.asset_id) {
            asset.record_interaction();
        }

        self.interactions.push(interaction);
        Ok(())
    }

    /// Get asset by ID
    pub fn get_asset(&self, id: &Uuid) -> Option<&DeceptionAsset> {
        self.assets.get(id)
    }

    /// Get all assets
    pub fn list_assets(&self) -> Vec<&DeceptionAsset> {
        self.assets.values().collect()
    }

    /// Get interactions for asset
    pub fn get_asset_interactions(&self, asset_id: &Uuid) -> Vec<&DeceptionInteraction> {
        self.interactions.iter()
            .filter(|i| &i.asset_id == asset_id)
            .collect()
    }

    /// Get high-severity interactions
    pub fn get_high_severity_interactions(&self) -> Vec<&DeceptionInteraction> {
        self.interactions.iter()
            .filter(|i| matches!(i.severity, ThreatSeverity::High | ThreatSeverity::Critical))
            .collect()
    }

    /// Get statistics
    pub fn get_statistics(&self) -> DeceptionStats {
        let total_assets = self.assets.len();
        let total_interactions = self.interactions.len();

        let mut severity_counts = HashMap::new();
        for interaction in &self.interactions {
            *severity_counts.entry(format!("{:?}", interaction.severity))
                .or_insert(0) += 1;
        }

        let mut type_counts = HashMap::new();
        for interaction in &self.interactions {
            *type_counts.entry(format!("{:?}", interaction.interaction_type))
                .or_insert(0) += 1;
        }

        DeceptionStats {
            total_assets,
            total_interactions,
            severity_counts,
            interaction_type_counts: type_counts,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeceptionStats {
    pub total_assets: usize,
    pub total_interactions: usize,
    pub severity_counts: HashMap<String, usize>,
    pub interaction_type_counts: HashMap<String, usize>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_asset_creation() {
        let asset = DeceptionAsset::new(
            AssetType::HoneyToken,
            "test-token".to_string(),
            "Test honey token".to_string(),
            "/var/log/test.log".to_string(),
        );

        assert_eq!(asset.asset_type, AssetType::HoneyToken);
        assert_eq!(asset.name, "test-token");
    }

    #[test]
    fn test_interaction_severity() {
        let interaction = DeceptionInteraction::new(
            Uuid::new_v4(),
            "192.168.1.100".to_string(),
            12345,
            InteractionType::DataExfiltration,
            "Attempted data exfiltration".to_string(),
        );

        assert_eq!(interaction.severity, ThreatSeverity::Critical);
    }

    #[test]
    fn test_deception_manager() {
        let mut manager = DeceptionManager::new();

        let asset = DeceptionAsset::new(
            AssetType::NetworkDecoy,
            "decoy-server".to_string(),
            "Fake SSH server".to_string(),
            "192.168.1.50:22".to_string(),
        );

        let asset_id = manager.deploy_asset(asset);
        assert_eq!(manager.list_assets().len(), 1);

        let interaction = DeceptionInteraction::new(
            asset_id,
            "10.0.0.5".to_string(),
            55555,
            InteractionType::Authentication,
            "Failed SSH login attempt".to_string(),
        );

        manager.record_interaction(interaction).unwrap();

        let stats = manager.get_statistics();
        assert_eq!(stats.total_assets, 1);
        assert_eq!(stats.total_interactions, 1);
    }
}
