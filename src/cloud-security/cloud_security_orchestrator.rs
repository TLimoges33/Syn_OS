//! Cloud Security Orchestrator - V1.6 "Cloud Native Security"
//!
//! Unified multi-cloud security dashboard aggregating findings from:
//! - AWS (GuardDuty, Security Hub, IAM Analyzer, CloudTrail)
//! - Azure (Sentinel SIEM/SOAR, Security Center, AD Identity Protection)
//! - GCP (Security Command Center, Cloud Asset Inventory, GKE Security)

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};

use crate::aws_security_bridge::{AWSSecurityBridge, AWSFinding, Severity as AWSSeverity};
use crate::azure_sentinel_bridge::{AzureSentinelBridge, SentinelAlert, AlertSeverity};
use crate::gcp_security_bridge::{GCPSecurityBridge, GCPFinding, Severity as GCPSeverity};

// ============================================================================
// UNIFIED SECURITY TYPES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum UnifiedSeverity {
    Critical,
    High,
    Medium,
    Low,
    Informational,
}

impl From<AWSSeverity> for UnifiedSeverity {
    fn from(severity: AWSSeverity) -> Self {
        match severity {
            AWSSeverity::Critical => UnifiedSeverity::Critical,
            AWSSeverity::High => UnifiedSeverity::High,
            AWSSeverity::Medium => UnifiedSeverity::Medium,
            AWSSeverity::Low => UnifiedSeverity::Low,
            AWSSeverity::Informational => UnifiedSeverity::Informational,
        }
    }
}

impl From<AlertSeverity> for UnifiedSeverity {
    fn from(severity: AlertSeverity) -> Self {
        match severity {
            AlertSeverity::Critical => UnifiedSeverity::Critical,
            AlertSeverity::High => UnifiedSeverity::High,
            AlertSeverity::Medium => UnifiedSeverity::Medium,
            AlertSeverity::Low => UnifiedSeverity::Low,
            AlertSeverity::Informational => UnifiedSeverity::Informational,
        }
    }
}

impl From<GCPSeverity> for UnifiedSeverity {
    fn from(severity: GCPSeverity) -> Self {
        match severity {
            GCPSeverity::Critical => UnifiedSeverity::Critical,
            GCPSeverity::High => UnifiedSeverity::High,
            GCPSeverity::Medium => UnifiedSeverity::Medium,
            GCPSeverity::Low => UnifiedSeverity::Low,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CloudProvider {
    AWS,
    Azure,
    GCP,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnifiedFinding {
    pub id: String,
    pub provider: CloudProvider,
    pub severity: UnifiedSeverity,
    pub title: String,
    pub description: String,
    pub resource: String,
    pub timestamp: DateTime<Utc>,
    pub remediation: Option<String>,
    pub compliance_frameworks: Vec<String>,
    pub mitre_tactics: Vec<String>,
}

impl From<AWSFinding> for UnifiedFinding {
    fn from(finding: AWSFinding) -> Self {
        UnifiedFinding {
            id: finding.id,
            provider: CloudProvider::AWS,
            severity: finding.severity.into(),
            title: finding.title,
            description: finding.description,
            resource: finding.resource.arn,
            timestamp: finding.last_seen,
            remediation: finding.remediation,
            compliance_frameworks: finding.compliance,
            mitre_tactics: Vec::new(), // AWS findings don't include MITRE
        }
    }
}

impl From<SentinelAlert> for UnifiedFinding {
    fn from(alert: SentinelAlert) -> Self {
        UnifiedFinding {
            id: alert.id,
            provider: CloudProvider::Azure,
            severity: alert.severity.into(),
            title: alert.alert_name,
            description: alert.description,
            resource: alert.entities.first()
                .map(|e| format!("{:?}", e))
                .unwrap_or_else(|| "Unknown".to_string()),
            timestamp: alert.start_time,
            remediation: Some(alert.remediation_steps.join("\n")),
            compliance_frameworks: Vec::new(), // Azure alerts don't include compliance
            mitre_tactics: alert.tactics.iter()
                .map(|t| format!("{:?}", t))
                .collect(),
        }
    }
}

impl From<GCPFinding> for UnifiedFinding {
    fn from(finding: GCPFinding) -> Self {
        UnifiedFinding {
            id: finding.name,
            provider: CloudProvider::GCP,
            severity: finding.severity.into(),
            title: format!("{:?}", finding.category),
            description: finding.source_properties.get("description")
                .cloned()
                .unwrap_or_else(|| format!("{:?} detected", finding.category)),
            resource: finding.resource_name,
            timestamp: finding.event_time,
            remediation: None, // GCP findings don't include remediation
            compliance_frameworks: Vec::new(),
            mitre_tactics: Vec::new(),
        }
    }
}

// ============================================================================
// CLOUD SECURITY DASHBOARD
// ============================================================================

#[derive(Debug, Serialize, Deserialize)]
pub struct CloudSecurityDashboard {
    pub total_findings: usize,
    pub critical_count: usize,
    pub high_count: usize,
    pub medium_count: usize,
    pub low_count: usize,
    pub findings_by_provider: HashMap<String, usize>,
    pub overall_security_score: u32,
    pub findings: Vec<UnifiedFinding>,
    pub top_risks: Vec<UnifiedFinding>,
    pub compliance_summary: ComplianceSummary,
    pub generated_at: DateTime<Utc>,
}

impl CloudSecurityDashboard {
    pub fn new(findings: Vec<UnifiedFinding>) -> Self {
        let total_findings = findings.len();

        let critical_count = findings.iter()
            .filter(|f| f.severity == UnifiedSeverity::Critical)
            .count();

        let high_count = findings.iter()
            .filter(|f| f.severity == UnifiedSeverity::High)
            .count();

        let medium_count = findings.iter()
            .filter(|f| f.severity == UnifiedSeverity::Medium)
            .count();

        let low_count = findings.iter()
            .filter(|f| f.severity == UnifiedSeverity::Low)
            .count();

        let mut findings_by_provider = HashMap::new();
        for finding in &findings {
            let provider = match finding.provider {
                CloudProvider::AWS => "AWS",
                CloudProvider::Azure => "Azure",
                CloudProvider::GCP => "GCP",
            };
            *findings_by_provider.entry(provider.to_string()).or_insert(0) += 1;
        }

        // Calculate security score (0-100, higher is better)
        let mut score: u32 = 100;
        score = score.saturating_sub(critical_count as u32 * 20);
        score = score.saturating_sub(high_count as u32 * 10);
        score = score.saturating_sub(medium_count as u32 * 5);
        score = score.saturating_sub(low_count as u32 * 2);

        // Top 10 most critical risks
        let mut sorted_findings = findings.clone();
        sorted_findings.sort_by(|a, b| {
            b.severity.cmp(&a.severity)
                .then_with(|| b.timestamp.cmp(&a.timestamp))
        });
        let top_risks: Vec<UnifiedFinding> = sorted_findings
            .into_iter()
            .take(10)
            .collect();

        // Compliance summary
        let compliance_summary = ComplianceSummary::from_findings(&findings);

        CloudSecurityDashboard {
            total_findings,
            critical_count,
            high_count,
            medium_count,
            low_count,
            findings_by_provider,
            overall_security_score: score,
            findings,
            top_risks,
            compliance_summary,
            generated_at: Utc::now(),
        }
    }

    pub fn to_json(&self) -> Result<String, String> {
        serde_json::to_string_pretty(self)
            .map_err(|e| format!("Failed to serialize dashboard: {}", e))
    }

    pub fn print_summary(&self) {
        println!("\n╔══════════════════════════════════════════════════════════════╗");
        println!("║         SynOS Multi-Cloud Security Dashboard v1.6           ║");
        println!("╚══════════════════════════════════════════════════════════════╝");
        println!("\n📊 OVERALL SECURITY SCORE: {}/100", self.overall_security_score);
        println!("\n🔍 FINDINGS SUMMARY:");
        println!("  Total Findings: {}", self.total_findings);
        println!("  🔴 Critical: {}", self.critical_count);
        println!("  🟠 High: {}", self.high_count);
        println!("  🟡 Medium: {}", self.medium_count);
        println!("  🟢 Low: {}", self.low_count);

        println!("\n☁️  FINDINGS BY CLOUD PROVIDER:");
        for (provider, count) in &self.findings_by_provider {
            println!("  {}: {}", provider, count);
        }

        println!("\n⚠️  TOP 5 CRITICAL RISKS:");
        for (i, risk) in self.top_risks.iter().take(5).enumerate() {
            println!("  {}. [{:?}] {} - {}",
                i + 1, risk.severity, risk.title, risk.provider.to_string());
        }

        println!("\n✅ COMPLIANCE STATUS:");
        println!("  CIS Benchmarks: {} controls failed", self.compliance_summary.cis_failed);
        println!("  PCI-DSS: {} controls failed", self.compliance_summary.pci_dss_failed);
        println!("  NIST: {} controls failed", self.compliance_summary.nist_failed);
        println!("\nGenerated: {}\n", self.generated_at.format("%Y-%m-%d %H:%M:%S UTC"));
    }
}

impl CloudProvider {
    fn to_string(&self) -> String {
        match self {
            CloudProvider::AWS => "AWS".to_string(),
            CloudProvider::Azure => "Azure".to_string(),
            CloudProvider::GCP => "GCP".to_string(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ComplianceSummary {
    pub cis_failed: usize,
    pub pci_dss_failed: usize,
    pub nist_failed: usize,
    pub iso27001_failed: usize,
}

impl ComplianceSummary {
    fn from_findings(findings: &[UnifiedFinding]) -> Self {
        let mut cis = 0;
        let mut pci = 0;
        let mut nist = 0;
        let mut iso = 0;

        for finding in findings {
            for framework in &finding.compliance_frameworks {
                if framework.contains("CIS") {
                    cis += 1;
                } else if framework.contains("PCI") {
                    pci += 1;
                } else if framework.contains("NIST") {
                    nist += 1;
                } else if framework.contains("ISO") {
                    iso += 1;
                }
            }
        }

        ComplianceSummary {
            cis_failed: cis,
            pci_dss_failed: pci,
            nist_failed: nist,
            iso27001_failed: iso,
        }
    }
}

// ============================================================================
// CLOUD SECURITY ORCHESTRATOR
// ============================================================================

#[derive(Debug)]
pub struct CloudSecurityOrchestrator {
    pub aws: Option<AWSSecurityBridge>,
    pub azure: Option<AzureSentinelBridge>,
    pub gcp: Option<GCPSecurityBridge>,
}

impl CloudSecurityOrchestrator {
    pub fn new() -> Self {
        Self {
            aws: None,
            azure: None,
            gcp: None,
        }
    }

    pub fn with_aws(mut self, bridge: AWSSecurityBridge) -> Self {
        self.aws = Some(bridge);
        self
    }

    pub fn with_azure(mut self, bridge: AzureSentinelBridge) -> Self {
        self.azure = Some(bridge);
        self
    }

    pub fn with_gcp(mut self, bridge: GCPSecurityBridge) -> Self {
        self.gcp = Some(bridge);
        self
    }

    /// Get unified security view across all configured cloud providers
    pub async fn get_unified_view(&self) -> Result<CloudSecurityDashboard, String> {
        let mut all_findings: Vec<UnifiedFinding> = Vec::new();

        // Collect AWS findings
        if let Some(aws) = &self.aws {
            let aws_findings = aws.get_unified_findings().await?;
            all_findings.extend(
                aws_findings.into_iter().map(|f| f.into())
            );
        }

        // Collect Azure findings
        if let Some(azure) = &self.azure {
            let azure_alerts = azure.get_active_alerts().await?;
            all_findings.extend(
                azure_alerts.into_iter().map(|a| a.into())
            );
        }

        // Collect GCP findings
        if let Some(gcp) = &self.gcp {
            let gcp_findings = gcp.get_findings().await?;
            all_findings.extend(
                gcp_findings.into_iter().map(|f| f.into())
            );
        }

        Ok(CloudSecurityDashboard::new(all_findings))
    }

    /// Calculate overall multi-cloud security score
    pub async fn calculate_security_score(&self) -> Result<u32, String> {
        let dashboard = self.get_unified_view().await?;
        Ok(dashboard.overall_security_score)
    }

    /// Get critical findings that require immediate attention
    pub async fn get_critical_findings(&self) -> Result<Vec<UnifiedFinding>, String> {
        let dashboard = self.get_unified_view().await?;
        Ok(dashboard.findings.into_iter()
            .filter(|f| f.severity == UnifiedSeverity::Critical)
            .collect())
    }

    /// Export security report in JSON format
    pub async fn export_report(&self, path: &str) -> Result<(), String> {
        let dashboard = self.get_unified_view().await?;
        let json = dashboard.to_json()?;

        std::fs::write(path, json)
            .map_err(|e| format!("Failed to write report: {}", e))?;

        Ok(())
    }

    /// Print summary to console
    pub async fn print_summary(&self) -> Result<(), String> {
        let dashboard = self.get_unified_view().await?;
        dashboard.print_summary();
        Ok(())
    }
}

impl Default for CloudSecurityOrchestrator {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_orchestrator_creation() {
        let orchestrator = CloudSecurityOrchestrator::new();
        assert!(orchestrator.aws.is_none());
        assert!(orchestrator.azure.is_none());
        assert!(orchestrator.gcp.is_none());
    }

    #[tokio::test]
    async fn test_dashboard_scoring() {
        let findings = vec![
            UnifiedFinding {
                id: "test-1".to_string(),
                provider: CloudProvider::AWS,
                severity: UnifiedSeverity::Critical,
                title: "Test Finding".to_string(),
                description: "Test".to_string(),
                resource: "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0".to_string(),
                timestamp: Utc::now(),
                remediation: None,
                compliance_frameworks: vec![],
                mitre_tactics: vec![],
            },
        ];

        let dashboard = CloudSecurityDashboard::new(findings);

        assert_eq!(dashboard.total_findings, 1);
        assert_eq!(dashboard.critical_count, 1);
        assert!(dashboard.overall_security_score < 100);
    }
}
