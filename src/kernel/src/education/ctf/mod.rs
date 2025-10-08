/// CTF (Capture The Flag) Auto-Generation Engine
/// AI-powered challenge generation for cybersecurity training

use alloc::vec::Vec;
use alloc::collections::BTreeMap;
use alloc::string::String;

pub mod challenge_generator;
pub mod flag_system;
pub mod scoring;
pub mod hints;

/// CTF engine manager
pub struct CtfEngine {
    challenges: BTreeMap<u64, CtfChallenge>,
    teams: BTreeMap<u64, Team>,
    next_challenge_id: u64,
    next_team_id: u64,
    generator: challenge_generator::ChallengeGenerator,
    flag_system: flag_system::FlagSystem,
    scoring_engine: scoring::ScoringEngine,
    hint_system: hints::HintSystem,
}

/// CTF challenge
#[derive(Debug, Clone)]
pub struct CtfChallenge {
    pub challenge_id: u64,
    pub name: String,
    pub description: String,
    pub category: ChallengeCategory,
    pub difficulty: crate::education::DifficultyLevel,
    pub points: u32,
    pub flag: String,
    pub hints: Vec<String>,
    pub files: Vec<ChallengeFile>,
    pub deployment_info: Option<DeploymentInfo>,
    pub solves: u32,
    pub first_blood: Option<u64>, // team_id
}

/// Challenge categories
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ChallengeCategory {
    WebExploitation,
    BinaryExploitation,
    ReverseEngineering,
    Cryptography,
    Forensics,
    OSINT,
    Pwn,
    Miscellaneous,
    Networking,
    Steganography,
}

/// Challenge files (downloadable resources)
#[derive(Debug, Clone)]
pub struct ChallengeFile {
    pub filename: String,
    pub file_type: FileType,
    pub download_url: String,
}

#[derive(Debug, Clone, Copy)]
pub enum FileType {
    Binary,
    SourceCode,
    PCAP,
    Image,
    Document,
    Archive,
}

/// Deployment information for live challenges
#[derive(Debug, Clone)]
pub struct DeploymentInfo {
    pub host: String,
    pub port: u16,
    pub protocol: String,
    pub container_id: Option<u64>,
}

/// Team structure
#[derive(Debug, Clone)]
pub struct Team {
    pub team_id: u64,
    pub name: String,
    pub members: Vec<String>,
    pub solved_challenges: Vec<u64>,
    pub total_points: u32,
    pub last_solve_time: u64,
}

impl CtfEngine {
    pub fn new() -> Self {
        Self {
            challenges: BTreeMap::new(),
            teams: BTreeMap::new(),
            next_challenge_id: 1,
            next_team_id: 1,
            generator: challenge_generator::ChallengeGenerator::new(),
            flag_system: flag_system::FlagSystem::new(),
            scoring_engine: scoring::ScoringEngine::new(),
            hint_system: hints::HintSystem::new(),
        }
    }

    /// Generate a new challenge using AI
    pub fn generate_challenge(
        &mut self,
        category: ChallengeCategory,
        difficulty: crate::education::DifficultyLevel,
    ) -> Result<u64, &'static str> {
        let challenge_id = self.next_challenge_id;
        self.next_challenge_id += 1;

        // Use AI to generate challenge
        let generated = self.generator.generate_challenge(category, difficulty)?;

        // Generate flag
        let flag = self.flag_system.generate_flag(challenge_id)?;

        // Calculate points based on difficulty
        let points = self.scoring_engine.calculate_base_points(difficulty);

        let challenge = CtfChallenge {
            challenge_id,
            name: generated.name,
            description: generated.description,
            category,
            difficulty,
            points,
            flag,
            hints: generated.hints,
            files: generated.files,
            deployment_info: generated.deployment_info,
            solves: 0,
            first_blood: None,
        };

        self.challenges.insert(challenge_id, challenge);
        Ok(challenge_id)
    }

    /// Submit flag for verification
    pub fn submit_flag(
        &mut self,
        team_id: u64,
        challenge_id: u64,
        submitted_flag: &str,
    ) -> Result<bool, &'static str> {
        let challenge = self.challenges.get_mut(&challenge_id)
            .ok_or("Challenge not found")?;

        let team = self.teams.get_mut(&team_id)
            .ok_or("Team not found")?;

        // Check if already solved
        if team.solved_challenges.contains(&challenge_id) {
            return Err("Challenge already solved by this team");
        }

        // Verify flag
        if !self.flag_system.verify_flag(&challenge.flag, submitted_flag) {
            return Ok(false);
        }

        // Correct flag!
        team.solved_challenges.push(challenge_id);

        // Calculate points with dynamic scoring
        let points = self.scoring_engine.calculate_solve_points(
            challenge.difficulty,
            challenge.solves,
        );

        team.total_points += points;
        team.last_solve_time = 0; // Would use actual timestamp

        // Update challenge statistics
        challenge.solves += 1;
        if challenge.first_blood.is_none() {
            challenge.first_blood = Some(team_id);
        }

        Ok(true)
    }

    /// Create team
    pub fn create_team(&mut self, name: String, members: Vec<String>) -> Result<u64, &'static str> {
        let team_id = self.next_team_id;
        self.next_team_id += 1;

        let team = Team {
            team_id,
            name,
            members,
            solved_challenges: Vec::new(),
            total_points: 0,
            last_solve_time: 0,
        };

        self.teams.insert(team_id, team);
        Ok(team_id)
    }

    /// Get leaderboard
    pub fn get_leaderboard(&self) -> Vec<&Team> {
        let mut teams: Vec<_> = self.teams.values().collect();

        // Sort by points (descending), then by last solve time (ascending)
        teams.sort_by(|a, b| {
            b.total_points.cmp(&a.total_points)
                .then(a.last_solve_time.cmp(&b.last_solve_time))
        });

        teams
    }

    /// Get hint for challenge
    pub fn get_hint(
        &mut self,
        challenge_id: u64,
        hint_index: usize,
    ) -> Result<String, &'static str> {
        let challenge = self.challenges.get(&challenge_id)
            .ok_or("Challenge not found")?;

        if hint_index >= challenge.hints.len() {
            return Err("No more hints available");
        }

        Ok(challenge.hints[hint_index].clone())
    }

    /// List available challenges
    pub fn list_challenges(&self) -> Vec<&CtfChallenge> {
        self.challenges.values().collect()
    }

    /// List challenges by category
    pub fn list_by_category(&self, category: ChallengeCategory) -> Vec<&CtfChallenge> {
        self.challenges.values()
            .filter(|c| c.category == category)
            .collect()
    }

    /// Get challenge details
    pub fn get_challenge(&self, challenge_id: u64) -> Option<&CtfChallenge> {
        self.challenges.get(&challenge_id)
    }

    /// Get team details
    pub fn get_team(&self, team_id: u64) -> Option<&Team> {
        self.teams.get(&team_id)
    }

    /// Get CTF statistics
    pub fn get_statistics(&self) -> CtfStatistics {
        let total_solves: u32 = self.challenges.values()
            .map(|c| c.solves)
            .sum();

        CtfStatistics {
            total_challenges: self.challenges.len(),
            total_teams: self.teams.len(),
            total_solves,
            challenges_by_category: self.count_by_category(),
            average_solve_rate: if !self.challenges.is_empty() {
                (total_solves as f32) / (self.challenges.len() as f32)
            } else {
                0.0
            },
        }
    }

    fn count_by_category(&self) -> BTreeMap<String, usize> {
        let mut counts = BTreeMap::new();

        for challenge in self.challenges.values() {
            let category = format!("{:?}", challenge.category);
            *counts.entry(category).or_insert(0) += 1;
        }

        counts
    }
}

/// CTF platform statistics
#[derive(Debug, Clone)]
pub struct CtfStatistics {
    pub total_challenges: usize,
    pub total_teams: usize,
    pub total_solves: u32,
    pub challenges_by_category: BTreeMap<String, usize>,
    pub average_solve_rate: f32,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::education::DifficultyLevel;

    #[test]
    fn test_challenge_generation() {
        let mut engine = CtfEngine::new();

        let challenge_id = engine.generate_challenge(
            ChallengeCategory::WebExploitation,
            DifficultyLevel::Beginner,
        );

        assert!(challenge_id.is_ok());
    }

    #[test]
    fn test_team_creation() {
        let mut engine = CtfEngine::new();

        let team_id = engine.create_team(
            "Team Alpha".into(),
            vec!["Alice".into(), "Bob".into()],
        );

        assert!(team_id.is_ok());
    }

    #[test]
    fn test_flag_submission() {
        let mut engine = CtfEngine::new();

        let challenge_id = engine.generate_challenge(
            ChallengeCategory::Cryptography,
            DifficultyLevel::Intermediate,
        ).unwrap();

        let team_id = engine.create_team(
            "Test Team".into(),
            vec!["Tester".into()],
        ).unwrap();

        let challenge = engine.get_challenge(challenge_id).unwrap();
        let flag = challenge.flag.clone();

        let result = engine.submit_flag(team_id, challenge_id, &flag);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), true);
    }

    #[test]
    fn test_leaderboard() {
        let mut engine = CtfEngine::new();

        engine.create_team("Team 1".into(), vec!["A".into()]).unwrap();
        engine.create_team("Team 2".into(), vec!["B".into()]).unwrap();

        let leaderboard = engine.get_leaderboard();
        assert_eq!(leaderboard.len(), 2);
    }
}
