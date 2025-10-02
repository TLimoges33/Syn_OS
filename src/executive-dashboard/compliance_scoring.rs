//! Compliance Scoring System
//!
//! Tracks and scores compliance posture across multiple frameworks

#![no_std]

extern crate alloc;
use alloc::vec::Vec;
use alloc::string::String;
use alloc::collections::BTreeMap;

/// Compliance frameworks
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ComplianceFramework {
    NIST_CSF,
    ISO27001,
    PCI_DSS,
    SOX,
    GDPR,
    HIPAA,
    FedRAMP,
}

/// Compliance control status
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ControlStatus {
    NotImplemented,
    PartiallyImplemented,
    FullyImplemented,
    NotApplicable,
}

/// Individual compliance control
#[derive(Debug, Clone)]
pub struct ComplianceControl {
    pub id: String,
    pub framework: ComplianceFramework,
    pub name: String,
    pub description: String,
    pub status: ControlStatus,
    pub evidence: Vec<String>,
    pub last_assessed: u64,
}

/// Compliance scoring engine
pub struct ComplianceScoring {
    controls: Vec<ComplianceControl>,
    framework_weights: BTreeMap<ComplianceFramework, f32>,
}

impl ComplianceScoring {
    /// Create new compliance scoring system
    pub fn new() -> Self {
        let mut weights = BTreeMap::new();

        // Default equal weights
        weights.insert(ComplianceFramework::NIST_CSF, 1.0);
        weights.insert(ComplianceFramework::ISO27001, 1.0);
        weights.insert(ComplianceFramework::PCI_DSS, 1.0);
        weights.insert(ComplianceFramework::SOX, 1.0);
        weights.insert(ComplianceFramework::GDPR, 1.0);
        weights.insert(ComplianceFramework::HIPAA, 1.0);
        weights.insert(ComplianceFramework::FedRAMP, 1.0);

        Self {
            controls: Vec::new(),
            framework_weights: weights,
        }
    }

    /// Add compliance control
    pub fn add_control(&mut self, control: ComplianceControl) {
        self.controls.push(control);
    }

    /// Calculate compliance score for a framework (0-100)
    pub fn calculate_framework_score(&self, framework: ComplianceFramework) -> f32 {
        let framework_controls: Vec<&ComplianceControl> = self.controls.iter()
            .filter(|c| c.framework == framework)
            .collect();

        if framework_controls.is_empty() {
            return 0.0;
        }

        let mut total_score = 0.0;
        let mut applicable_controls = 0;

        for control in framework_controls {
            match control.status {
                ControlStatus::FullyImplemented => {
                    total_score += 1.0;
                    applicable_controls += 1;
                }
                ControlStatus::PartiallyImplemented => {
                    total_score += 0.5;
                    applicable_controls += 1;
                }
                ControlStatus::NotImplemented => {
                    applicable_controls += 1;
                }
                ControlStatus::NotApplicable => {
                    // Don't count in score
                }
            }
        }

        if applicable_controls > 0 {
            (total_score / applicable_controls as f32) * 100.0
        } else {
            0.0
        }
    }

    /// Calculate overall compliance score
    pub fn calculate_overall_score(&self) -> f32 {
        let mut weighted_sum = 0.0;
        let mut total_weight = 0.0;

        for (framework, weight) in &self.framework_weights {
            let score = self.calculate_framework_score(*framework);
            weighted_sum += score * weight;
            total_weight += weight;
        }

        if total_weight > 0.0 {
            weighted_sum / total_weight
        } else {
            0.0
        }
    }

    /// Get compliance gaps (controls not fully implemented)
    pub fn get_compliance_gaps(&self) -> Vec<&ComplianceControl> {
        self.controls.iter()
            .filter(|c| matches!(c.status, ControlStatus::NotImplemented | ControlStatus::PartiallyImplemented))
            .collect()
    }

    /// Get controls by framework
    pub fn get_framework_controls(&self, framework: ComplianceFramework) -> Vec<&ComplianceControl> {
        self.controls.iter()
            .filter(|c| c.framework == framework)
            .collect()
    }

    /// Set framework weight
    pub fn set_framework_weight(&mut self, framework: ComplianceFramework, weight: f32) {
        self.framework_weights.insert(framework, weight);
    }

    /// Generate compliance report
    pub fn generate_report(&self) -> ComplianceReport {
        let mut framework_scores = BTreeMap::new();

        for framework in [
            ComplianceFramework::NIST_CSF,
            ComplianceFramework::ISO27001,
            ComplianceFramework::PCI_DSS,
            ComplianceFramework::SOX,
            ComplianceFramework::GDPR,
            ComplianceFramework::HIPAA,
            ComplianceFramework::FedRAMP,
        ] {
            let score = self.calculate_framework_score(framework);
            framework_scores.insert(framework, score);
        }

        ComplianceReport {
            overall_score: self.calculate_overall_score(),
            framework_scores,
            total_controls: self.controls.len(),
            compliance_gaps: self.get_compliance_gaps().len(),
        }
    }
}

/// Compliance report
#[derive(Debug, Clone)]
pub struct ComplianceReport {
    pub overall_score: f32,
    pub framework_scores: BTreeMap<ComplianceFramework, f32>,
    pub total_controls: usize,
    pub compliance_gaps: usize,
}

impl ComplianceReport {
    /// Format as executive summary
    pub fn executive_summary(&self) -> String {
        let mut summary = alloc::format!(
            "Compliance Posture Summary\n\
             Overall Score: {:.1}%\n\
             Total Controls: {}\n\
             Compliance Gaps: {}\n\n\
             Framework Scores:\n",
            self.overall_score,
            self.total_controls,
            self.compliance_gaps
        );

        for (framework, score) in &self.framework_scores {
            let framework_name = match framework {
                ComplianceFramework::NIST_CSF => "NIST CSF",
                ComplianceFramework::ISO27001 => "ISO 27001",
                ComplianceFramework::PCI_DSS => "PCI DSS",
                ComplianceFramework::SOX => "SOX",
                ComplianceFramework::GDPR => "GDPR",
                ComplianceFramework::HIPAA => "HIPAA",
                ComplianceFramework::FedRAMP => "FedRAMP",
            };

            summary.push_str(&alloc::format!("  {}: {:.1}%\n", framework_name, score));
        }

        summary
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compliance_scoring() {
        let mut scoring = ComplianceScoring::new();

        let control = ComplianceControl {
            id: "NIST-1.1".into(),
            framework: ComplianceFramework::NIST_CSF,
            name: "Asset Inventory".into(),
            description: "Maintain asset inventory".into(),
            status: ControlStatus::FullyImplemented,
            evidence: Vec::new(),
            last_assessed: 0,
        };

        scoring.add_control(control);

        let score = scoring.calculate_framework_score(ComplianceFramework::NIST_CSF);
        assert_eq!(score, 100.0);
    }
}
