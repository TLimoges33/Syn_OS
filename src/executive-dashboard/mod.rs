//! Executive Dashboard Module
//!
//! Provides executive-level security metrics, ROI analysis, and reporting

#![no_std]

extern crate alloc;

pub mod risk_metrics;
pub mod roi_analysis;
pub mod compliance_scoring;

use risk_metrics::{RiskMetrics, RiskLevel};
use roi_analysis::{ROIAnalysis, ROIReport};
use alloc::string::String;
use alloc::vec::Vec;

/// Executive dashboard manager
pub struct ExecutiveDashboard {
    risk_metrics: RiskMetrics,
    roi_analysis: ROIAnalysis,
    dashboard_title: String,
}

impl ExecutiveDashboard {
    /// Create new executive dashboard
    pub fn new(title: String) -> Self {
        Self {
            risk_metrics: RiskMetrics::new(),
            roi_analysis: ROIAnalysis::new(),
            dashboard_title: title,
        }
    }

    /// Get risk metrics
    pub fn risk_metrics(&self) -> &RiskMetrics {
        &self.risk_metrics
    }

    /// Get mutable risk metrics
    pub fn risk_metrics_mut(&mut self) -> &mut RiskMetrics {
        &mut self.risk_metrics
    }

    /// Get ROI analysis
    pub fn roi_analysis(&self) -> &ROIAnalysis {
        &self.roi_analysis
    }

    /// Get mutable ROI analysis
    pub fn roi_analysis_mut(&mut self) -> &mut ROIAnalysis {
        &mut self.roi_analysis
    }

    /// Generate executive summary
    pub fn generate_executive_summary(&self) -> String {
        let risk_score = self.risk_metrics.total_score();
        let top_risks = self.risk_metrics.get_top_risks(5);
        let roi_report = self.roi_analysis.generate_report();

        let mut summary = alloc::format!(
            "=== {} ===\n\n\
             SECURITY POSTURE SUMMARY\n\
             ------------------------\n\
             Total Risk Score: {:.2}\n\
             Top Risks Count: {}\n\n\
             INVESTMENT PERFORMANCE\n\
             ----------------------\n\
             {}\n",
            self.dashboard_title,
            risk_score,
            top_risks.len(),
            roi_report.executive_summary()
        );

        summary
    }

    /// Get dashboard title
    pub fn title(&self) -> &str {
        &self.dashboard_title
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dashboard_creation() {
        let dashboard = ExecutiveDashboard::new("SynOS Security Dashboard".into());
        assert_eq!(dashboard.title(), "SynOS Security Dashboard");
    }
}
