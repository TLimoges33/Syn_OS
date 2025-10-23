//! CTF Platform Engine - V1.9 "CTF Platform + Universal Wrapper"
//!
//! Complete CTF training platform with challenges, leaderboards, and flag validation.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// ============================================================================
// CORE TYPES
// ============================================================================

#[derive(Debug, Clone, Hash, Eq, PartialEq, Serialize, Deserialize)]
pub struct ChallengeId(pub String);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Challenge {
    pub id: ChallengeId,
    pub title: String,
    pub description: String,
    pub category: CTFCategory,
    pub difficulty: Difficulty,
    pub points: u32,
    pub flag: String,
    pub hints: Vec<Hint>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CTFCategory {
    Web,
    Pwn,
    Crypto,
    Forensics,
    ReverseEngineering,
    Misc,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Difficulty {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hint {
    pub text: String,
    pub cost: u32,
}

// ============================================================================
// CHALLENGE SESSIONS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengeSession {
    pub challenge_id: ChallengeId,
    pub user_id: String,
    pub started_at: chrono::DateTime<chrono::Utc>,
    pub attempts: u32,
    pub hints_used: Vec<usize>,
}

impl ChallengeSession {
    pub fn calculate_points(&self, base_points: u32, hints: &[Hint]) -> u32 {
        let mut points = base_points;
        for &hint_idx in &self.hints_used {
            if let Some(hint) = hints.get(hint_idx) {
                points = points.saturating_sub(hint.cost);
            }
        }
        points
    }
}

// ============================================================================
// LEADERBOARD
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Leaderboard {
    pub entries: HashMap<String, LeaderboardEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LeaderboardEntry {
    pub user_id: String,
    pub username: String,
    pub total_points: u32,
    pub challenges_solved: usize,
    pub rank: usize,
}

impl Leaderboard {
    pub fn new() -> Self {
        Self {
            entries: HashMap::new(),
        }
    }

    pub fn update(&mut self, user_id: String, username: String, points: u32) {
        self.entries
            .entry(user_id.clone())
            .and_modify(|e| {
                e.total_points += points;
                e.challenges_solved += 1;
            })
            .or_insert(LeaderboardEntry {
                user_id,
                username,
                total_points: points,
                challenges_solved: 1,
                rank: 0,
            });

        self.recalculate_ranks();
    }

    fn recalculate_ranks(&mut self) {
        let mut entries: Vec<_> = self.entries.values_mut().collect();
        entries.sort_by(|a, b| b.total_points.cmp(&a.total_points));

        for (idx, entry) in entries.iter_mut().enumerate() {
            entry.rank = idx + 1;
        }
    }

    pub fn get_top(&self, n: usize) -> Vec<LeaderboardEntry> {
        let mut entries: Vec<_> = self.entries.values().cloned().collect();
        entries.sort_by(|a, b| a.rank.cmp(&b.rank));
        entries.into_iter().take(n).collect()
    }
}

// ============================================================================
// FLAG VALIDATION
// ============================================================================

pub struct FlagValidator {
    flags: HashMap<ChallengeId, String>,
}

impl FlagValidator {
    pub fn new() -> Self {
        Self {
            flags: HashMap::new(),
        }
    }

    pub fn register(&mut self, challenge_id: ChallengeId, flag: String) {
        self.flags.insert(challenge_id, flag);
    }

    pub fn validate(&self, challenge_id: &ChallengeId, submitted_flag: &str) -> bool {
        if let Some(correct_flag) = self.flags.get(challenge_id) {
            correct_flag == submitted_flag
        } else {
            false
        }
    }
}

// ============================================================================
// SUBMIT RESULT
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SubmitResult {
    Correct {
        points: u32,
        rank: usize,
    },
    Incorrect {
        attempts_remaining: u32,
    },
    MaxAttemptsReached,
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

        platform.load_default_challenges();
        platform
    }

    fn load_default_challenges(&mut self) {
        // Challenge 1: Caesar Cipher
        let challenge = Challenge {
            id: ChallengeId("ctf_crypto_caesar".to_string()),
            title: "Caesar Cipher Cracking".to_string(),
            description: "Decode the message: URYYB_JBEYQ".to_string(),
            category: CTFCategory::Crypto,
            difficulty: Difficulty::Beginner,
            points: 50,
            flag: "SynOS{HELLO_WORLD}".to_string(),
            hints: vec![
                Hint {
                    text: "Try ROT13".to_string(),
                    cost: 10,
                },
            ],
        };
        self.add_challenge(challenge);

        // Challenge 2: SQL Injection
        let challenge = Challenge {
            id: ChallengeId("ctf_web_sqli".to_string()),
            title: "SQL Injection Attack".to_string(),
            description: "Find the admin password using SQL injection".to_string(),
            category: CTFCategory::Web,
            difficulty: Difficulty::Intermediate,
            points: 100,
            flag: "SynOS{1_equals_1_OR_NOT_2_equals_2}".to_string(),
            hints: vec![
                Hint {
                    text: "Try ' OR 1=1--".to_string(),
                    cost: 20,
                },
            ],
        };
        self.add_challenge(challenge);

        // Challenge 3: Buffer Overflow
        let challenge = Challenge {
            id: ChallengeId("ctf_pwn_overflow".to_string()),
            title: "Buffer Overflow".to_string(),
            description: "Exploit the buffer overflow vulnerability".to_string(),
            category: CTFCategory::Pwn,
            difficulty: Difficulty::Advanced,
            points: 250,
            flag: "SynOS{SMASH_THE_STACK}".to_string(),
            hints: vec![],
        };
        self.add_challenge(challenge);
    }

    fn add_challenge(&mut self, challenge: Challenge) {
        self.flag_validator.register(challenge.id.clone(), challenge.flag.clone());
        self.challenges.insert(challenge.id.clone(), challenge);
    }

    pub fn start_challenge(&mut self, challenge_id: &ChallengeId, user_id: String) -> Result<ChallengeSession, String> {
        if !self.challenges.contains_key(challenge_id) {
            return Err("Challenge not found".to_string());
        }

        let session = ChallengeSession {
            challenge_id: challenge_id.clone(),
            user_id: user_id.clone(),
            started_at: chrono::Utc::now(),
            attempts: 0,
            hints_used: vec![],
        };

        let key = format!("{}:{}", user_id, challenge_id.0);
        self.active_sessions.insert(key, session.clone());

        Ok(session)
    }

    pub fn request_hint(&mut self, challenge_id: &ChallengeId, user_id: &str, hint_idx: usize) -> Result<String, String> {
        let key = format!("{}:{}", user_id, challenge_id.0);
        let session = self.active_sessions.get_mut(&key)
            .ok_or("No active session found")?;

        let challenge = self.challenges.get(challenge_id)
            .ok_or("Challenge not found")?;

        let hint = challenge.hints.get(hint_idx)
            .ok_or("Hint not found")?;

        session.hints_used.push(hint_idx);

        Ok(hint.text.clone())
    }

    pub fn submit_flag(&mut self, challenge_id: &ChallengeId, user_id: &str, username: &str, flag: &str) -> SubmitResult {
        let key = format!("{}:{}", user_id, challenge_id.0);

        if !self.flag_validator.validate(challenge_id, flag) {
            if let Some(session) = self.active_sessions.get_mut(&key) {
                session.attempts += 1;
                let max_attempts = 5;
                if session.attempts >= max_attempts {
                    return SubmitResult::MaxAttemptsReached;
                }
                return SubmitResult::Incorrect {
                    attempts_remaining: max_attempts - session.attempts,
                };
            }
            return SubmitResult::Incorrect { attempts_remaining: 0 };
        }

        // Correct flag!
        let session = self.active_sessions.get(&key).unwrap();
        let challenge = self.challenges.get(challenge_id).unwrap();
        let points = session.calculate_points(challenge.points, &challenge.hints);

        self.leaderboard.update(user_id.to_string(), username.to_string(), points);

        let entry = self.leaderboard.entries.get(user_id).unwrap();
        SubmitResult::Correct {
            points,
            rank: entry.rank,
        }
    }
}
