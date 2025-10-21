//! CTF Platform Engine - V1.9 "CTF Platform + Universal Wrapper"
//!
//! Built-in Capture The Flag training platform with challenges,
//! leaderboards, flag validation, and automated scoring.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// ============================================================================
// CHALLENGE TYPES
// ============================================================================

#[derive(Debug, Clone, Hash, Eq, PartialEq, Serialize, Deserialize)]
pub struct ChallengeId(pub String);

impl ChallengeId {
    pub fn new(id: &str) -> Self {
        Self(id.to_string())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Challenge {
    pub id: ChallengeId,
    pub title: String,
    pub category: CTFCategory,
    pub difficulty: Difficulty,
    pub points: u32,
    pub flag: Flag,
    pub description: String,
    pub hints: Vec<Hint>,
    pub vm_config: Option<VMConfig>,
    pub files: Vec<ChallengeFile>,
    pub author: String,
    pub tags: Vec<String>,
    pub solve_count: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CTFCategory {
    Web,
    Binary,
    Crypto,
    Forensics,
    OSINT,
    ReverseEngineering,
    Network,
    Pwn,
    Misc,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, PartialOrd)]
pub enum Difficulty {
    Beginner = 1,
    Easy = 2,
    Medium = 3,
    Hard = 4,
    Expert = 5,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Flag {
    pub value: String,
    pub format: FlagFormat,
    pub case_sensitive: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FlagFormat {
    Static,       // Fixed flag
    Dynamic,      // Generated per user
    Regex,        // Matches pattern
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hint {
    pub cost: u32,  // Points deducted
    pub text: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VMConfig {
    pub image: String,
    pub memory_mb: u32,
    pub cpu_cores: u32,
    pub network: VMNetworkConfig,
    pub startup_script: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VMNetworkConfig {
    pub mode: NetworkMode,
    pub ip_address: Option<String>,
    pub exposed_ports: Vec<u16>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum NetworkMode {
    Isolated,     // No external network
    NAT,          // NAT to host
    Bridged,      // Bridge to physical network
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengeFile {
    pub name: String,
    pub path: String,
    pub size: u64,
    pub checksum: String,
}

// ============================================================================
// CHALLENGE SESSION
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengeSession {
    pub challenge_id: ChallengeId,
    pub user_id: String,
    pub started_at: chrono::DateTime<chrono::Utc>,
    pub hints_used: Vec<usize>,
    pub attempts: u32,
    pub solved: bool,
    pub solved_at: Option<chrono::DateTime<chrono::Utc>>,
    pub vm_id: Option<String>,
}

impl ChallengeSession {
    pub fn new(challenge: &Challenge, user_id: String) -> Self {
        Self {
            challenge_id: challenge.id.clone(),
            user_id,
            started_at: chrono::Utc::now(),
            hints_used: Vec::new(),
            attempts: 0,
            solved: false,
            solved_at: None,
            vm_id: None,
        }
    }

    pub fn use_hint(&mut self, hint_index: usize) {
        if !self.hints_used.contains(&hint_index) {
            self.hints_used.push(hint_index);
        }
    }

    pub fn calculate_points(&self, base_points: u32, hints: &[Hint]) -> u32 {
        let mut points = base_points;

        // Deduct for hints
        for hint_idx in &self.hints_used {
            if let Some(hint) = hints.get(*hint_idx) {
                points = points.saturating_sub(hint.cost);
            }
        }

        // Bonus for first blood (not implemented yet)
        // Bonus for speed (not implemented yet)

        points
    }
}

// ============================================================================
// LEADERBOARD
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Leaderboard {
    pub entries: Vec<LeaderboardEntry>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LeaderboardEntry {
    pub rank: u32,
    pub user_id: String,
    pub username: String,
    pub total_points: u32,
    pub challenges_solved: u32,
    pub last_solve: Option<chrono::DateTime<chrono::Utc>>,
}

impl Leaderboard {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
            updated_at: chrono::Utc::now(),
        }
    }

    pub fn update(&mut self, user_id: String, username: String, points: u32) {
        // Find or create entry
        if let Some(entry) = self.entries.iter_mut().find(|e| e.user_id == user_id) {
            entry.total_points += points;
            entry.challenges_solved += 1;
            entry.last_solve = Some(chrono::Utc::now());
        } else {
            self.entries.push(LeaderboardEntry {
                rank: 0,
                user_id,
                username,
                total_points: points,
                challenges_solved: 1,
                last_solve: Some(chrono::Utc::now()),
            });
        }

        // Recalculate ranks
        self.recalculate_ranks();
        self.updated_at = chrono::Utc::now();
    }

    fn recalculate_ranks(&mut self) {
        // Sort by points (descending), then by last solve (ascending)
        self.entries.sort_by(|a, b| {
            b.total_points.cmp(&a.total_points)
                .then_with(|| a.last_solve.cmp(&b.last_solve))
        });

        // Assign ranks
        for (idx, entry) in self.entries.iter_mut().enumerate() {
            entry.rank = (idx + 1) as u32;
        }
    }

    pub fn get_top(&self, n: usize) -> Vec<LeaderboardEntry> {
        self.entries.iter().take(n).cloned().collect()
    }

    pub fn get_user_rank(&self, user_id: &str) -> Option<u32> {
        self.entries.iter()
            .find(|e| e.user_id == user_id)
            .map(|e| e.rank)
    }
}

impl Default for Leaderboard {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// FLAG VALIDATOR
// ============================================================================

pub struct FlagValidator {
    flags: HashMap<ChallengeId, Flag>,
}

impl FlagValidator {
    pub fn new() -> Self {
        Self {
            flags: HashMap::new(),
        }
    }

    pub fn add_flag(&mut self, challenge_id: ChallengeId, flag: Flag) {
        self.flags.insert(challenge_id, flag);
    }

    pub fn validate(&self, challenge_id: &ChallengeId, submitted_flag: &str) -> bool {
        if let Some(flag) = self.flags.get(challenge_id) {
            match flag.format {
                FlagFormat::Static => {
                    if flag.case_sensitive {
                        submitted_flag == flag.value
                    } else {
                        submitted_flag.to_lowercase() == flag.value.to_lowercase()
                    }
                }
                FlagFormat::Dynamic => {
                    // TODO: Implement dynamic flag validation
                    false
                }
                FlagFormat::Regex => {
                    // TODO: Implement regex flag validation
                    false
                }
            }
        } else {
            false
        }
    }
}

impl Default for FlagValidator {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// CTF PLATFORM
// ============================================================================

pub struct CTFPlatform {
    pub challenges: HashMap<ChallengeId, Challenge>,
    pub active_sessions: HashMap<String, ChallengeSession>,
    pub leaderboard: Leaderboard,
    pub flag_validator: FlagValidator,
}

impl CTFPlatform {
    pub fn new() -> Self {
        let mut platform = Self {
            challenges: HashMap::new(),
            active_sessions: HashMap::new(),
            leaderboard: Leaderboard::new(),
            flag_validator: FlagValidator::new(),
        };

        // Load default challenges
        platform.load_default_challenges();
        platform
    }

    fn load_default_challenges(&mut self) {
        // Web challenge
        let web_challenge = Challenge {
            id: ChallengeId::new("web-001"),
            title: "SQL Injection 101".to_string(),
            category: CTFCategory::Web,
            difficulty: Difficulty::Beginner,
            points: 100,
            flag: Flag {
                value: "SynOS{basic_sqli_ftw}".to_string(),
                format: FlagFormat::Static,
                case_sensitive: true,
            },
            description: "Find the SQL injection vulnerability and extract the flag from the database.".to_string(),
            hints: vec![
                Hint {
                    cost: 20,
                    text: "Try single quotes in the username field".to_string(),
                },
                Hint {
                    cost: 30,
                    text: "Use UNION SELECT to extract data".to_string(),
                },
            ],
            vm_config: Some(VMConfig {
                image: "synos/vulnerable-web:latest".to_string(),
                memory_mb: 512,
                cpu_cores: 1,
                network: VMNetworkConfig {
                    mode: NetworkMode::NAT,
                    ip_address: None,
                    exposed_ports: vec![80, 443],
                },
                startup_script: None,
            }),
            files: vec![],
            author: "SynOS Team".to_string(),
            tags: vec!["sql".to_string(), "injection".to_string(), "beginner".to_string()],
            solve_count: 0,
        };

        self.add_challenge(web_challenge);

        // Binary exploitation challenge
        let pwn_challenge = Challenge {
            id: ChallengeId::new("pwn-001"),
            title: "Buffer Overflow Basics".to_string(),
            category: CTFCategory::Pwn,
            difficulty: Difficulty::Medium,
            points: 250,
            flag: Flag {
                value: "SynOS{stack_smashing_detected}".to_string(),
                format: FlagFormat::Static,
                case_sensitive: true,
            },
            description: "Exploit the buffer overflow to get a shell and read the flag.".to_string(),
            hints: vec![
                Hint {
                    cost: 50,
                    text: "Look for gets() or strcpy() calls".to_string(),
                },
                Hint {
                    cost: 75,
                    text: "Check if NX is disabled with checksec".to_string(),
                },
            ],
            vm_config: None,
            files: vec![
                ChallengeFile {
                    name: "vuln".to_string(),
                    path: "/challenges/pwn-001/vuln".to_string(),
                    size: 16384,
                    checksum: "abc123...".to_string(),
                },
            ],
            author: "SynOS Team".to_string(),
            tags: vec!["binary".to_string(), "overflow".to_string(), "shellcode".to_string()],
            solve_count: 0,
        };

        self.add_challenge(pwn_challenge);

        // Cryptography challenge
        let crypto_challenge = Challenge {
            id: ChallengeId::new("crypto-001"),
            title: "Caesar's Secret".to_string(),
            category: CTFCategory::Crypto,
            difficulty: Difficulty::Beginner,
            points: 50,
            flag: Flag {
                value: "SynOS{caesar_was_here}".to_string(),
                format: FlagFormat::Static,
                case_sensitive: true,
            },
            description: "Decrypt the Caesar cipher to reveal the flag: 'VlaRV{fdhvdu_zdv_khuh}'".to_string(),
            hints: vec![
                Hint {
                    cost: 10,
                    text: "Try all 26 possible shifts".to_string(),
                },
            ],
            vm_config: None,
            files: vec![],
            author: "SynOS Team".to_string(),
            tags: vec!["crypto".to_string(), "caesar".to_string(), "easy".to_string()],
            solve_count: 0,
        };

        self.add_challenge(crypto_challenge);
    }

    pub fn add_challenge(&mut self, challenge: Challenge) {
        self.flag_validator.add_flag(challenge.id.clone(), challenge.flag.clone());
        self.challenges.insert(challenge.id.clone(), challenge);
    }

    pub fn get_challenge(&self, challenge_id: &ChallengeId) -> Option<&Challenge> {
        self.challenges.get(challenge_id)
    }

    pub fn list_challenges(&self) -> Vec<&Challenge> {
        self.challenges.values().collect()
    }

    pub fn list_by_category(&self, category: CTFCategory) -> Vec<&Challenge> {
        self.challenges.values()
            .filter(|c| c.category == category)
            .collect()
    }

    pub fn start_challenge(&mut self, challenge_id: &ChallengeId, user_id: String) -> Result<ChallengeSession, String> {
        let challenge = self.get_challenge(challenge_id)
            .ok_or("Challenge not found")?;

        let mut session = ChallengeSession::new(challenge, user_id.clone());

        // Spin up VM if needed
        if let Some(vm_config) = &challenge.vm_config {
            println!("🖥️  Spinning up VM: {}", vm_config.image);
            // TODO: Actually spawn VM
            session.vm_id = Some(format!("vm-{}", uuid::Uuid::new_v4()));
        }

        self.active_sessions.insert(user_id, session.clone());

        println!("✅ Challenge started: {}", challenge.title);
        Ok(session)
    }

    pub fn submit_flag(&mut self, challenge_id: &ChallengeId, user_id: &str, username: &str, flag: &str) -> SubmitResult {
        // Validate flag
        if !self.flag_validator.validate(challenge_id, flag) {
            // Increment attempts
            if let Some(session) = self.active_sessions.get_mut(user_id) {
                session.attempts += 1;
            }

            return SubmitResult::Incorrect {
                attempts: self.active_sessions.get(user_id).map(|s| s.attempts).unwrap_or(0),
            };
        }

        // Flag is correct!
        if let Some(session) = self.active_sessions.get_mut(user_id) {
            if session.solved {
                return SubmitResult::AlreadySolved;
            }

            session.solved = true;
            session.solved_at = Some(chrono::Utc::now());

            // Calculate points
            let challenge = self.challenges.get(challenge_id).unwrap();
            let points = session.calculate_points(challenge.points, &challenge.hints);

            // Update leaderboard
            self.leaderboard.update(user_id.to_string(), username.to_string(), points);

            // Increment solve count
            if let Some(challenge) = self.challenges.get_mut(challenge_id) {
                challenge.solve_count += 1;
            }

            println!("🎉 {} solved {} for {} points!", username, challenge.title, points);

            SubmitResult::Correct {
                points,
                rank: self.leaderboard.get_user_rank(user_id).unwrap_or(0),
            }
        } else {
            SubmitResult::Incorrect { attempts: 0 }
        }
    }

    pub fn use_hint(&mut self, challenge_id: &ChallengeId, user_id: &str, hint_index: usize) -> Result<Hint, String> {
        let challenge = self.challenges.get(challenge_id)
            .ok_or("Challenge not found")?;

        let hint = challenge.hints.get(hint_index)
            .ok_or("Hint not found")?
            .clone();

        // Record hint usage
        if let Some(session) = self.active_sessions.get_mut(user_id) {
            session.use_hint(hint_index);
            println!("💡 Hint used (-{} points): {}", hint.cost, hint.text);
        }

        Ok(hint)
    }

    pub fn get_leaderboard(&self, top_n: usize) -> Vec<LeaderboardEntry> {
        self.leaderboard.get_top(top_n)
    }

    pub fn print_leaderboard(&self) {
        println!("\n╔══════════════════════════════════════════════════════════════╗");
        println!("║                    CTF LEADERBOARD                           ║");
        println!("╚══════════════════════════════════════════════════════════════╝");

        let top_10 = self.get_leaderboard(10);
        for entry in top_10 {
            println!("  #{} {} - {} pts ({} solves)",
                     entry.rank,
                     entry.username,
                     entry.total_points,
                     entry.challenges_solved);
        }
        println!();
    }
}

impl Default for CTFPlatform {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SubmitResult {
    Correct {
        points: u32,
        rank: u32,
    },
    Incorrect {
        attempts: u32,
    },
    AlreadySolved,
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ctf_platform_creation() {
        let platform = CTFPlatform::new();
        assert!(!platform.challenges.is_empty());
    }

    #[test]
    fn test_flag_validation() {
        let mut validator = FlagValidator::new();
        let challenge_id = ChallengeId::new("test-001");

        validator.add_flag(challenge_id.clone(), Flag {
            value: "SynOS{test_flag}".to_string(),
            format: FlagFormat::Static,
            case_sensitive: true,
        });

        assert!(validator.validate(&challenge_id, "SynOS{test_flag}"));
        assert!(!validator.validate(&challenge_id, "wrong_flag"));
    }

    #[test]
    fn test_leaderboard() {
        let mut leaderboard = Leaderboard::new();

        leaderboard.update("user1".to_string(), "Alice".to_string(), 100);
        leaderboard.update("user2".to_string(), "Bob".to_string(), 150);
        leaderboard.update("user1".to_string(), "Alice".to_string(), 50);

        let top = leaderboard.get_top(2);
        assert_eq!(top[0].username, "Bob");
        assert_eq!(top[0].total_points, 150);
        assert_eq!(top[1].username, "Alice");
        assert_eq!(top[1].total_points, 150);
    }
}
