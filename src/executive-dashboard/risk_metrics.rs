//! Risk Metrics Calculation
//!
//! Calculates and tracks security risk metrics for executive reporting

#![no_std]

extern crate alloc;
use alloc::vec::Vec;
use alloc::string::String;
use alloc::collections::BTreeMap;

/// Risk severity levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

/// Risk category
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RiskCategory {
    Vulnerability,
    ThreatActor,
    Compliance,
    Operational,
    DataBreach,
}

/// Individual risk item
#[derive(Debug, Clone)]
pub struct RiskItem {
    pub id: u64,
    pub category: RiskCategory,
    pub level: RiskLevel,
    pub title: String,
    pub description: String,
    pub likelihood: f32,  // 0.0 to 1.0
    pub impact: f32,      // 0.0 to 1.0
    pub mitigation_status: MitigationStatus,
    pub business_impact: String,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum MitigationStatus {
    Unmitigated,
    InProgress,
    Mitigated,
    Accepted,
}

/// Risk metrics calculator
pub struct RiskMetrics {
    risks: Vec<RiskItem>,
    total_risk_score: f32,
    risk_trend: RiskTrend,
}

#[derive(Debug, Clone, Copy)]
pub enum RiskTrend {
    Increasing,
    Stable,
    Decreasing,
}

impl RiskMetrics {
    /// Create new risk metrics tracker
    pub fn new() -> Self {
        Self {
            risks: Vec::new(),
            total_risk_score: 0.0,
            risk_trend: RiskTrend::Stable,
        }
    }

    /// Add a risk item
    pub fn add_risk(&mut self, risk: RiskItem) {
        self.risks.push(risk);
        self.recalculate_score();
    }

    /// Calculate total risk score
    fn recalculate_score(&mut self) {
        let mut total = 0.0;

        for risk in &self.risks {
            if risk.mitigation_status != MitigationStatus::Mitigated {
                // Risk score = likelihood × impact × severity multiplier
                let severity_multiplier = match risk.level {
                    RiskLevel::Low => 1.0,
                    RiskLevel::Medium => 2.0,
                    RiskLevel::High => 4.0,
                    RiskLevel::Critical => 8.0,
                };

                total += risk.likelihood * risk.impact * severity_multiplier;
            }
        }

        self.total_risk_score = total;
    }

    /// Get risk distribution by level
    pub fn get_risk_distribution(&self) -> BTreeMap<RiskLevel, usize> {
        let mut distribution = BTreeMap::new();

        for risk in &self.risks {
            if risk.mitigation_status != MitigationStatus::Mitigated {
                *distribution.entry(risk.level).or_insert(0) += 1;
            }
        }

        distribution
    }

    /// Get risk distribution by category
    pub fn get_category_distribution(&self) -> BTreeMap<RiskCategory, usize> {
        let mut distribution = BTreeMap::new();

        for risk in &self.risks {
            if risk.mitigation_status != MitigationStatus::Mitigated {
                *distribution.entry(risk.category).or_insert(0) += 1;
            }
        }

        distribution
    }

    /// Calculate risk reduction percentage
    pub fn calculate_risk_reduction(&self, previous_score: f32) -> f32 {
        if previous_score > 0.0 {
            ((previous_score - self.total_risk_score) / previous_score) * 100.0
        } else {
            0.0
        }
    }

    /// Get top risks
    pub fn get_top_risks(&self, count: usize) -> Vec<&RiskItem> {
        let mut risks: Vec<&RiskItem> = self.risks.iter()
            .filter(|r| r.mitigation_status != MitigationStatus::Mitigated)
            .collect();

        // Sort by risk score (likelihood × impact × severity)
        risks.sort_by(|a, b| {
            let score_a = a.likelihood * a.impact * Self::severity_to_multiplier(a.level);
            let score_b = b.likelihood * b.impact * Self::severity_to_multiplier(b.level);
            score_b.partial_cmp(&score_a).unwrap()
        });

        risks.into_iter().take(count).collect()
    }

    fn severity_to_multiplier(level: RiskLevel) -> f32 {
        match level {
            RiskLevel::Low => 1.0,
            RiskLevel::Medium => 2.0,
            RiskLevel::High => 4.0,
            RiskLevel::Critical => 8.0,
        }
    }

    /// Get total risk score
    pub fn total_score(&self) -> f32 {
        self.total_risk_score
    }

    /// Get risk trend
    pub fn trend(&self) -> RiskTrend {
        self.risk_trend
    }

    /// Update risk trend based on historical data
    pub fn update_trend(&mut self, historical_scores: &[f32]) {
        if historical_scores.len() < 2 {
            return;
        }

        let recent_avg = historical_scores[historical_scores.len() - 3..]
            .iter()
            .sum::<f32>() / 3.0;

        let older_avg = historical_scores[..historical_scores.len() - 3]
            .iter()
            .sum::<f32>() / (historical_scores.len() - 3) as f32;

        if recent_avg > older_avg * 1.1 {
            self.risk_trend = RiskTrend::Increasing;
        } else if recent_avg < older_avg * 0.9 {
            self.risk_trend = RiskTrend::Decreasing;
        } else {
            self.risk_trend = RiskTrend::Stable;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_risk_calculation() {
        let mut metrics = RiskMetrics::new();

        let risk = RiskItem {
            id: 1,
            category: RiskCategory::Vulnerability,
            level: RiskLevel::High,
            title: "SQL Injection".into(),
            description: "Unvalidated input".into(),
            likelihood: 0.8,
            impact: 0.9,
            mitigation_status: MitigationStatus::Unmitigated,
            business_impact: "Data breach".into(),
        };

        metrics.add_risk(risk);
        assert!(metrics.total_score() > 0.0);
    }
}
