/// Scenario Engine for Lab Environments
/// Sets up vulnerable applications and challenges

use alloc::collections::BTreeMap;
use alloc::vec::Vec;

/// Scenario types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ScenarioType {
    WebApp,           // Vulnerable web application
    NetworkService,   // Vulnerable network service
    BinaryChallenge,  // Binary exploitation challenge
    ForensicsImage,   // Forensics disk image
    MalwareSample,    // Malware analysis sample
}

/// Scenario configuration
#[derive(Debug, Clone)]
pub struct ScenarioConfig {
    pub scenario_type: ScenarioType,
    pub vulnerability_type: &'static str,
    pub target_port: Option<u16>,
    pub flags: Vec<&'static str>, // Hidden flags to find
}

/// Scenario engine
pub struct ScenarioEngine {
    active_scenarios: BTreeMap<u64, ScenarioConfig>, // lab_id -> config
}

impl ScenarioEngine {
    pub fn new() -> Self {
        Self {
            active_scenarios: BTreeMap::new(),
        }
    }

    /// Initialize scenario for lab
    pub fn initialize_scenario(&mut self, lab_id: u64) -> Result<(), &'static str> {
        let config = match lab_id {
            1 => ScenarioConfig {
                scenario_type: ScenarioType::WebApp,
                vulnerability_type: "SQL Injection",
                target_port: Some(8080),
                flags: vec!["flag{sql_1nj3ct10n_m4st3r}"],
            },
            2 => ScenarioConfig {
                scenario_type: ScenarioType::NetworkService,
                vulnerability_type: "Network Analysis",
                target_port: Some(9000),
                flags: vec!["flag{p4ck3t_sn1ff3r}"],
            },
            3 => ScenarioConfig {
                scenario_type: ScenarioType::BinaryChallenge,
                vulnerability_type: "Buffer Overflow",
                target_port: None,
                flags: vec!["flag{buff3r_0v3rfl0w}"],
            },
            4 => ScenarioConfig {
                scenario_type: ScenarioType::BinaryChallenge,
                vulnerability_type: "Weak RSA",
                target_port: None,
                flags: vec!["flag{cr4ck3d_rs4}"],
            },
            _ => return Err("Unknown lab scenario"),
        };

        self.active_scenarios.insert(lab_id, config);
        Ok(())
    }

    /// Verify flag submission
    pub fn verify_flag(&self, lab_id: u64, submitted_flag: &str) -> bool {
        if let Some(config) = self.active_scenarios.get(&lab_id) {
            config.flags.iter().any(|flag| *flag == submitted_flag)
        } else {
            false
        }
    }

    /// Cleanup scenario
    pub fn cleanup_scenario(&mut self, lab_id: u64) -> Result<(), &'static str> {
        self.active_scenarios.remove(&lab_id)
            .ok_or("Scenario not found")?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scenario_initialization() {
        let mut engine = ScenarioEngine::new();
        assert!(engine.initialize_scenario(1).is_ok());
    }

    #[test]
    fn test_flag_verification() {
        let mut engine = ScenarioEngine::new();
        engine.initialize_scenario(1).unwrap();

        assert!(engine.verify_flag(1, "flag{sql_1nj3ct10n_m4st3r}"));
        assert!(!engine.verify_flag(1, "wrong_flag"));
    }
}
