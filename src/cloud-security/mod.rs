//! SynOS Cloud Security Module - V1.6 "Cloud Native Security"
//!
//! Multi-cloud security monitoring and threat detection across:
//! - **AWS:** GuardDuty, Security Hub, IAM Analyzer, CloudTrail
//! - **Azure:** Sentinel SIEM/SOAR, Security Center, AD Identity Protection
//! - **GCP:** Security Command Center, Cloud Asset Inventory, GKE Security
//!
//! # Features
//! - Unified multi-cloud security dashboard
//! - Real-time threat detection and alerting
//! - Compliance monitoring (CIS, PCI-DSS, NIST, ISO 27001)
//! - IAM policy analysis across clouds
//! - MITRE ATT&CK framework mapping
//! - Automated incident response (SOAR)
//! - Security scoring and risk metrics

pub mod aws_security_bridge;
pub mod azure_sentinel_bridge;
pub mod gcp_security_bridge;
pub mod cloud_security_orchestrator;

// Re-export commonly used types
pub use aws_security_bridge::{
    AWSSecurityBridge,
    AWSFinding,
    AWSResource,
    FindingType,
    Severity as AWSSeverity,
    IAMIssue,
    ComplianceReport,
    AWSComplianceChecker,
};

pub use azure_sentinel_bridge::{
    AzureSentinelBridge,
    SentinelAlert,
    AlertSeverity,
    AlertStatus,
    MITRETactic,
    Entity,
    KQLQuery,
    TimeRange,
    SecurityRecommendation,
    AzureADIdentityProtection,
    RiskyUser,
    RiskySignIn,
};

pub use gcp_security_bridge::{
    GCPSecurityBridge,
    GCPFinding,
    FindingCategory,
    Severity as GCPSeverity,
    FindingState,
    GCPAsset,
    ResourceDescriptor,
    IAMPolicy,
    IAMBinding,
    AccessLevel,
    IAMIssue as GCPIAMIssue,
    PublicResource,
    AuditLogAnomaly,
    AnomalyType,
    GKESecurityAnalyzer,
    GKESecurityIssue,
};

pub use cloud_security_orchestrator::{
    CloudSecurityOrchestrator,
    CloudSecurityDashboard,
    UnifiedFinding,
    UnifiedSeverity,
    CloudProvider,
    ComplianceSummary,
};

/// Initialize cloud security monitoring for all configured providers
pub async fn initialize_cloud_security() -> Result<CloudSecurityOrchestrator, String> {
    let orchestrator = CloudSecurityOrchestrator::new();

    // TODO: Load cloud provider credentials from secure storage
    // TODO: Auto-detect available cloud providers
    // TODO: Initialize bridges based on configuration

    Ok(orchestrator)
}

/// Quick security scan across all clouds
pub async fn quick_scan() -> Result<CloudSecurityDashboard, String> {
    let orchestrator = initialize_cloud_security().await?;
    orchestrator.get_unified_view().await
}

/// Get current multi-cloud security score (0-100)
pub async fn get_security_score() -> Result<u32, String> {
    let orchestrator = initialize_cloud_security().await?;
    orchestrator.calculate_security_score().await
}

/// Get all critical findings requiring immediate attention
pub async fn get_critical_alerts() -> Result<Vec<UnifiedFinding>, String> {
    let orchestrator = initialize_cloud_security().await?;
    orchestrator.get_critical_findings().await
}
