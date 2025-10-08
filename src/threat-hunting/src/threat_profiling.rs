//! Threat Actor Profiling
//!
//! Attribution and TTP analysis for threat actors

use crate::{Result, ThreatHuntingError, HuntFinding, ThreatActorProfile};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Threat actor profiler
pub struct ThreatActorProfiler {
    known_actors: HashMap<String, KnownThreatActor>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct KnownThreatActor {
    name: String,
    aliases: Vec<String>,
    country: Option<String>,
    motivation: Vec<String>,
    target_sectors: Vec<String>,
    signature_ttps: Vec<String>,
    signature_tactics: Vec<String>,
    signature_techniques: Vec<String>,
    common_tools: Vec<String>,
}

impl ThreatActorProfiler {
    pub fn new() -> Self {
        let mut profiler = Self {
            known_actors: HashMap::new(),
        };
        profiler.load_known_actors();
        profiler
    }

    fn load_known_actors(&mut self) {
        // APT28 (Fancy Bear)
        self.known_actors.insert("APT28".to_string(), KnownThreatActor {
            name: "APT28".to_string(),
            aliases: vec!["Fancy Bear".to_string(), "Sofacy".to_string(), "Sednit".to_string()],
            country: Some("Russia".to_string()),
            motivation: vec!["Espionage".to_string(), "Political".to_string()],
            target_sectors: vec!["Government".to_string(), "Military".to_string(), "Defense".to_string()],
            signature_ttps: vec![
                "Spear phishing emails".to_string(),
                "Zero-day exploits".to_string(),
                "DLL side-loading".to_string(),
            ],
            signature_tactics: vec!["TA0001".to_string(), "TA0002".to_string(), "TA0003".to_string()],
            signature_techniques: vec!["T1566.001".to_string(), "T1203".to_string(), "T1574.002".to_string()],
            common_tools: vec!["X-Agent".to_string(), "Sofacy".to_string(), "Cannon".to_string()],
        });

        // APT29 (Cozy Bear)
        self.known_actors.insert("APT29".to_string(), KnownThreatActor {
            name: "APT29".to_string(),
            aliases: vec!["Cozy Bear".to_string(), "The Dukes".to_string()],
            country: Some("Russia".to_string()),
            motivation: vec!["Espionage".to_string(), "Intelligence gathering".to_string()],
            target_sectors: vec!["Government".to_string(), "Think tanks".to_string(), "Healthcare".to_string()],
            signature_ttps: vec![
                "Spear phishing".to_string(),
                "Watering hole attacks".to_string(),
                "Stealth and persistence".to_string(),
            ],
            signature_tactics: vec!["TA0001".to_string(), "TA0003".to_string(), "TA0005".to_string()],
            signature_techniques: vec!["T1566".to_string(), "T1189".to_string(), "T1027".to_string()],
            common_tools: vec!["WellMess".to_string(), "WellMail".to_string(), "CozyDuke".to_string()],
        });

        // Lazarus Group
        self.known_actors.insert("Lazarus".to_string(), KnownThreatActor {
            name: "Lazarus Group".to_string(),
            aliases: vec!["Hidden Cobra".to_string(), "Guardians of Peace".to_string()],
            country: Some("North Korea".to_string()),
            motivation: vec!["Financial gain".to_string(), "Espionage".to_string(), "Destructive attacks".to_string()],
            target_sectors: vec!["Financial".to_string(), "Cryptocurrency".to_string(), "Entertainment".to_string()],
            signature_ttps: vec![
                "Ransomware deployment".to_string(),
                "Cryptocurrency theft".to_string(),
                "Data destruction".to_string(),
            ],
            signature_tactics: vec!["TA0040".to_string(), "TA0010".to_string()],
            signature_techniques: vec!["T1486".to_string(), "T1565".to_string()],
            common_tools: vec!["WannaCry".to_string(), "Ryuk".to_string(), "FALLCHILL".to_string()],
        });

        // FIN7
        self.known_actors.insert("FIN7".to_string(), KnownThreatActor {
            name: "FIN7".to_string(),
            aliases: vec!["Carbanak".to_string()],
            country: Some("Unknown".to_string()),
            motivation: vec!["Financial gain".to_string()],
            target_sectors: vec!["Retail".to_string(), "Hospitality".to_string(), "Financial".to_string()],
            signature_ttps: vec![
                "Point-of-sale malware".to_string(),
                "Phishing with malicious attachments".to_string(),
                "Fileless malware".to_string(),
            ],
            signature_tactics: vec!["TA0001".to_string(), "TA0006".to_string()],
            signature_techniques: vec!["T1566.001".to_string(), "T1003".to_string()],
            common_tools: vec!["Carbanak".to_string(), "BOOSTWRITE".to_string()],
        });

        // APT41
        self.known_actors.insert("APT41".to_string(), KnownThreatActor {
            name: "APT41".to_string(),
            aliases: vec!["Barium".to_string(), "Winnti".to_string()],
            country: Some("China".to_string()),
            motivation: vec!["Espionage".to_string(), "Financial gain".to_string()],
            target_sectors: vec!["Healthcare".to_string(), "Telecommunications".to_string(), "Technology".to_string()],
            signature_ttps: vec![
                "Supply chain compromise".to_string(),
                "Web shell deployment".to_string(),
                "Rootkit usage".to_string(),
            ],
            signature_tactics: vec!["TA0001".to_string(), "TA0003".to_string(), "TA0005".to_string()],
            signature_techniques: vec!["T1195".to_string(), "T1505.003".to_string(), "T1014".to_string()],
            common_tools: vec!["Winnti".to_string(), "PlugX".to_string(), "China Chopper".to_string()],
        });
    }

    /// Profile threat actor based on findings
    pub fn profile(&self, findings: &[HuntFinding]) -> Result<ThreatActorProfile> {
        if findings.is_empty() {
            return Err(ThreatHuntingError::ProfilingError(
                "No findings provided for profiling".to_string()
            ));
        }

        // Extract TTPs from findings
        let observed_tactics: Vec<String> = findings.iter()
            .flat_map(|f| f.mitre_tactics.clone())
            .collect();

        let observed_techniques: Vec<String> = findings.iter()
            .flat_map(|f| f.mitre_techniques.clone())
            .collect();

        // Calculate match scores for each known actor
        let mut scores: Vec<(String, f32)> = self.known_actors.iter()
            .map(|(name, actor)| {
                let score = self.calculate_match_score(actor, &observed_tactics, &observed_techniques);
                (name.clone(), score)
            })
            .collect();

        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        // Get best match
        let (best_match_name, best_score) = scores.first()
            .ok_or_else(|| ThreatHuntingError::ProfilingError("No matches found".to_string()))?;

        if *best_score < 0.3 {
            // Unknown actor
            Ok(ThreatActorProfile {
                name: "Unknown Actor".to_string(),
                confidence: 0.0,
                ttps: self.extract_ttps_description(findings),
                mitre_tactics: observed_tactics,
                mitre_techniques: observed_techniques,
                indicators: findings.iter()
                    .flat_map(|f| f.evidence.iter().map(|e| e.data.clone()))
                    .collect(),
                attribution_score: 0.0,
            })
        } else {
            let actor = self.known_actors.get(best_match_name).unwrap();

            Ok(ThreatActorProfile {
                name: format!("{} ({})", actor.name, actor.aliases.join(", ")),
                confidence: *best_score,
                ttps: actor.signature_ttps.clone(),
                mitre_tactics: observed_tactics,
                mitre_techniques: observed_techniques,
                indicators: findings.iter()
                    .flat_map(|f| f.evidence.iter().map(|e| e.data.clone()))
                    .collect(),
                attribution_score: *best_score,
            })
        }
    }

    fn calculate_match_score(
        &self,
        actor: &KnownThreatActor,
        observed_tactics: &[String],
        observed_techniques: &[String],
    ) -> f32 {
        let mut score = 0.0;
        let mut total_weight = 0.0;

        // Tactic matching (weight: 0.4)
        let tactic_weight = 0.4;
        let tactic_matches = observed_tactics.iter()
            .filter(|t| actor.signature_tactics.contains(t))
            .count();

        if !actor.signature_tactics.is_empty() {
            score += (tactic_matches as f32 / actor.signature_tactics.len() as f32) * tactic_weight;
        }
        total_weight += tactic_weight;

        // Technique matching (weight: 0.6)
        let technique_weight = 0.6;
        let technique_matches = observed_techniques.iter()
            .filter(|t| actor.signature_techniques.contains(t))
            .count();

        if !actor.signature_techniques.is_empty() {
            score += (technique_matches as f32 / actor.signature_techniques.len() as f32) * technique_weight;
        }
        total_weight += technique_weight;

        score / total_weight
    }

    fn extract_ttps_description(&self, findings: &[HuntFinding]) -> Vec<String> {
        findings.iter()
            .map(|f| f.description.clone())
            .collect()
    }

    /// Get known actor information
    pub fn get_actor_info(&self, actor_name: &str) -> Option<ActorInfo> {
        self.known_actors.get(actor_name).map(|actor| ActorInfo {
            name: actor.name.clone(),
            aliases: actor.aliases.clone(),
            country: actor.country.clone(),
            motivation: actor.motivation.clone(),
            target_sectors: actor.target_sectors.clone(),
            signature_ttps: actor.signature_ttps.clone(),
            common_tools: actor.common_tools.clone(),
        })
    }

    /// List all known actors
    pub fn list_known_actors(&self) -> Vec<String> {
        self.known_actors.keys().cloned().collect()
    }

    /// Search actors by country
    pub fn search_by_country(&self, country: &str) -> Vec<String> {
        self.known_actors.iter()
            .filter(|(_, actor)| {
                actor.country.as_ref().map(|c| c.to_lowercase().contains(&country.to_lowercase())).unwrap_or(false)
            })
            .map(|(name, _)| name.clone())
            .collect()
    }

    /// Search actors by sector
    pub fn search_by_sector(&self, sector: &str) -> Vec<String> {
        self.known_actors.iter()
            .filter(|(_, actor)| {
                actor.target_sectors.iter().any(|s| s.to_lowercase().contains(&sector.to_lowercase()))
            })
            .map(|(name, _)| name.clone())
            .collect()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActorInfo {
    pub name: String,
    pub aliases: Vec<String>,
    pub country: Option<String>,
    pub motivation: Vec<String>,
    pub target_sectors: Vec<String>,
    pub signature_ttps: Vec<String>,
    pub common_tools: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{FindingType, FindingSeverity};
    use uuid::Uuid;

    #[test]
    fn test_threat_profiler_creation() {
        let profiler = ThreatActorProfiler::new();
        assert!(!profiler.known_actors.is_empty());
    }

    #[test]
    fn test_actor_search() {
        let profiler = ThreatActorProfiler::new();
        let russian_actors = profiler.search_by_country("Russia");
        assert!(russian_actors.contains(&"APT28".to_string()));
    }

    #[test]
    fn test_sector_search() {
        let profiler = ThreatActorProfiler::new();
        let financial_actors = profiler.search_by_sector("Financial");
        assert!(!financial_actors.is_empty());
    }
}
