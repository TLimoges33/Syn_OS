//! ROI Analysis for Security Investments
//!
//! Calculates return on investment for security initiatives

#![no_std]

extern crate alloc;
use alloc::vec::Vec;
use alloc::string::String;

/// Security investment record
#[derive(Debug, Clone)]
pub struct SecurityInvestment {
    pub name: String,
    pub category: InvestmentCategory,
    pub cost: f64,
    pub annual_cost: f64,
    pub implementation_date: u64,
    pub expected_risk_reduction: f32,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum InvestmentCategory {
    Technology,
    Personnel,
    Training,
    Process,
    Compliance,
}

/// Security incident cost
#[derive(Debug, Clone)]
pub struct IncidentCost {
    pub incident_type: String,
    pub frequency_per_year: f32,
    pub avg_cost_per_incident: f64,
    pub prevented_by: Vec<String>, // Which investments prevent this
}

/// ROI Calculator
pub struct ROIAnalysis {
    investments: Vec<SecurityInvestment>,
    potential_incidents: Vec<IncidentCost>,
    actual_incidents_prevented: u32,
}

impl ROIAnalysis {
    /// Create new ROI analyzer
    pub fn new() -> Self {
        Self {
            investments: Vec::new(),
            potential_incidents: Vec::new(),
            actual_incidents_prevented: 0,
        }
    }

    /// Add security investment
    pub fn add_investment(&mut self, investment: SecurityInvestment) {
        self.investments.push(investment);
    }

    /// Add potential incident cost
    pub fn add_incident_cost(&mut self, incident: IncidentCost) {
        self.potential_incidents.push(incident);
    }

    /// Calculate total investment cost
    pub fn total_investment(&self) -> f64 {
        self.investments.iter()
            .map(|inv| inv.cost + inv.annual_cost)
            .sum()
    }

    /// Calculate potential loss without security investments
    pub fn calculate_potential_loss(&self) -> f64 {
        self.potential_incidents.iter()
            .map(|incident| {
                incident.frequency_per_year as f64 * incident.avg_cost_per_incident
            })
            .sum()
    }

    /// Calculate actual loss with current security posture
    pub fn calculate_actual_loss(&self) -> f64 {
        let mut total_loss = 0.0;

        for incident in &self.potential_incidents {
            // Calculate reduction factor based on investments
            let reduction_factor = self.calculate_reduction_factor(&incident.prevented_by);

            // Adjusted frequency after security investments
            let adjusted_frequency = incident.frequency_per_year * (1.0 - reduction_factor);

            total_loss += adjusted_frequency as f64 * incident.avg_cost_per_incident;
        }

        total_loss
    }

    /// Calculate reduction factor from investments
    fn calculate_reduction_factor(&self, investment_names: &[String]) -> f32 {
        let mut total_reduction = 0.0;

        for name in investment_names {
            if let Some(inv) = self.investments.iter().find(|i| &i.name == name) {
                total_reduction += inv.expected_risk_reduction;
            }
        }

        // Cap at 95% reduction (never 100% secure)
        total_reduction.min(0.95)
    }

    /// Calculate ROI percentage
    pub fn calculate_roi(&self) -> f64 {
        let total_investment = self.total_investment();
        let potential_loss = self.calculate_potential_loss();
        let actual_loss = self.calculate_actual_loss();

        let cost_avoidance = potential_loss - actual_loss;
        let net_benefit = cost_avoidance - total_investment;

        if total_investment > 0.0 {
            (net_benefit / total_investment) * 100.0
        } else {
            0.0
        }
    }

    /// Calculate cost avoidance
    pub fn calculate_cost_avoidance(&self) -> f64 {
        let potential_loss = self.calculate_potential_loss();
        let actual_loss = self.calculate_actual_loss();
        potential_loss - actual_loss
    }

    /// Generate ROI report
    pub fn generate_report(&self) -> ROIReport {
        ROIReport {
            total_investment: self.total_investment(),
            potential_loss: self.calculate_potential_loss(),
            actual_loss: self.calculate_actual_loss(),
            cost_avoidance: self.calculate_cost_avoidance(),
            roi_percentage: self.calculate_roi(),
            incidents_prevented: self.actual_incidents_prevented,
            investment_count: self.investments.len(),
        }
    }

    /// Record incident prevented
    pub fn record_prevented_incident(&mut self) {
        self.actual_incidents_prevented += 1;
    }
}

/// ROI Report structure
#[derive(Debug, Clone)]
pub struct ROIReport {
    pub total_investment: f64,
    pub potential_loss: f64,
    pub actual_loss: f64,
    pub cost_avoidance: f64,
    pub roi_percentage: f64,
    pub incidents_prevented: u32,
    pub investment_count: usize,
}

impl ROIReport {
    /// Format as executive summary
    pub fn executive_summary(&self) -> alloc::string::String {
        alloc::format!(
            "Security Investment ROI Analysis\n\
             Total Investment: ${:.2}\n\
             Cost Avoidance: ${:.2}\n\
             ROI: {:.1}%\n\
             Incidents Prevented: {}\n\
             Active Security Investments: {}",
            self.total_investment,
            self.cost_avoidance,
            self.roi_percentage,
            self.incidents_prevented,
            self.investment_count
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_roi_calculation() {
        let mut analysis = ROIAnalysis::new();

        // Add investment
        analysis.add_investment(SecurityInvestment {
            name: "WAF".into(),
            category: InvestmentCategory::Technology,
            cost: 50000.0,
            annual_cost: 10000.0,
            implementation_date: 0,
            expected_risk_reduction: 0.7,
        });

        // Add potential incident
        analysis.add_incident_cost(IncidentCost {
            incident_type: "Web Attack".into(),
            frequency_per_year: 5.0,
            avg_cost_per_incident: 100000.0,
            prevented_by: alloc::vec!["WAF".into()],
        });

        let roi = analysis.calculate_roi();
        assert!(roi > 0.0, "ROI should be positive with effective investment");
    }
}
