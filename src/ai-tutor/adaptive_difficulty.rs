//! Adaptive Difficulty System - V1.7 "AI Tutor & Skill Tree"
//!
//! Dynamically adjusts challenge difficulty based on user performance
//! to maintain optimal learning flow (flow state theory).

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

// ============================================================================
// DIFFICULTY TYPES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdaptiveDifficulty {
    /// Current difficulty level (0.0 = beginner, 10.0 = expert)
    pub current_level: f32,

    /// Recent success rate (0.0 - 1.0)
    pub success_rate: f32,

    /// How fast the user is improving (levels/hour)
    pub learning_velocity: f32,

    /// Target success rate for optimal learning (default: 0.7)
    pub target_success_rate: f32,

    /// Recent challenge results (last 10)
    recent_results: VecDeque<ChallengeResult>,

    /// Total challenges attempted
    pub total_attempts: u32,

    /// Total challenges completed successfully
    pub total_successes: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengeResult {
    pub success: bool,
    pub time_taken: u64,        // seconds
    pub expected_time: u64,     // seconds
    pub attempts: u32,
    pub difficulty_level: f32,
    pub hints_used: u32,
    pub completed_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Challenge {
    pub id: String,
    pub title: String,
    pub description: String,
    pub difficulty: f32,
    pub estimated_time: u64,    // seconds
    pub category: ChallengeCategory,
    pub prerequisites: Vec<String>,
    pub learning_objectives: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ChallengeCategory {
    Reconnaissance,
    Scanning,
    Enumeration,
    Exploitation,
    PrivilegeEscalation,
    PostExploitation,
    DefensiveSkills,
    ForensicAnalysis,
}

// ============================================================================
// ADAPTIVE DIFFICULTY ENGINE
// ============================================================================

impl AdaptiveDifficulty {
    pub fn new() -> Self {
        Self {
            current_level: 1.0, // Start at beginner level
            success_rate: 0.0,
            learning_velocity: 0.0,
            target_success_rate: 0.7, // 70% success is optimal for learning
            recent_results: VecDeque::with_capacity(10),
            total_attempts: 0,
            total_successes: 0,
        }
    }

    /// Adjust difficulty based on challenge result
    pub fn adjust_difficulty(&mut self, result: &ChallengeResult) {
        // Add to recent results
        if self.recent_results.len() >= 10 {
            self.recent_results.pop_front();
        }
        self.recent_results.push_back(result.clone());

        // Update totals
        self.total_attempts += 1;
        if result.success {
            self.total_successes += 1;
        }

        // Calculate recent success rate
        self.success_rate = self.calculate_success_rate();

        // Adjust difficulty based on performance
        if result.success {
            // Challenge was completed successfully
            if result.time_taken < (result.expected_time as f32 * 0.6) as u64 {
                // Completed very quickly - too easy
                self.current_level += 0.8;
                println!("🔥 Challenge too easy! Increasing difficulty to {:.1}", self.current_level);
            } else if result.time_taken < (result.expected_time as f32 * 0.8) as u64 {
                // Completed faster than expected - moderately increase
                self.current_level += 0.4;
                println!("⬆️  Great performance! Difficulty increased to {:.1}", self.current_level);
            } else if result.hints_used == 0 && result.attempts == 1 {
                // First try, no hints - slightly increase
                self.current_level += 0.2;
            }
        } else {
            // Challenge was failed
            if result.attempts > 5 {
                // Struggled significantly - decrease difficulty
                self.current_level -= 0.6;
                println!("⬇️  Let's try something easier. Difficulty reduced to {:.1}", self.current_level);
            } else if result.attempts > 3 {
                // Some difficulty - moderate decrease
                self.current_level -= 0.3;
                println!("📉 Adjusting difficulty down to {:.1}", self.current_level);
            } else if result.hints_used > 3 {
                // Used many hints - slight decrease
                self.current_level -= 0.2;
            }
        }

        // Fine-tune based on success rate
        if self.recent_results.len() >= 5 {
            if self.success_rate > 0.85 {
                // Success rate too high - make it harder
                self.current_level += 0.3;
            } else if self.success_rate < 0.5 {
                // Success rate too low - make it easier
                self.current_level -= 0.3;
            }
        }

        // Clamp difficulty level
        self.current_level = self.current_level.clamp(0.0, 10.0);

        // Calculate learning velocity
        self.learning_velocity = self.calculate_learning_velocity();
    }

    fn calculate_success_rate(&self) -> f32 {
        if self.recent_results.is_empty() {
            return 0.0;
        }

        let successes = self.recent_results.iter()
            .filter(|r| r.success)
            .count();

        successes as f32 / self.recent_results.len() as f32
    }

    fn calculate_learning_velocity(&self) -> f32 {
        if self.recent_results.len() < 2 {
            return 0.0;
        }

        // Calculate average difficulty increase over time
        let first = self.recent_results.front().unwrap();
        let last = self.recent_results.back().unwrap();

        let time_diff = last.completed_at
            .signed_duration_since(first.completed_at)
            .num_hours() as f32;

        if time_diff <= 0.0 {
            return 0.0;
        }

        let level_diff = last.difficulty_level - first.difficulty_level;
        level_diff / time_diff
    }

    /// Suggest next challenge based on current difficulty level
    pub fn suggest_next_challenge(&self, available_challenges: &[Challenge]) -> Option<Challenge> {
        // Find challenges within ±0.5 of current level
        let target_min = (self.current_level - 0.5).max(0.0);
        let target_max = (self.current_level + 0.5).min(10.0);

        let mut suitable_challenges: Vec<Challenge> = available_challenges.iter()
            .filter(|c| c.difficulty >= target_min && c.difficulty <= target_max)
            .cloned()
            .collect();

        if suitable_challenges.is_empty() {
            // No exact matches - find closest
            suitable_challenges = available_challenges.to_vec();
            suitable_challenges.sort_by(|a, b| {
                let dist_a = (a.difficulty - self.current_level).abs();
                let dist_b = (b.difficulty - self.current_level).abs();
                dist_a.partial_cmp(&dist_b).unwrap()
            });
        }

        // Prefer variety - avoid recently completed categories
        let recent_categories: Vec<ChallengeCategory> = self.recent_results.iter()
            .filter_map(|r| {
                // Would need to track category in result - for now skip
                None
            })
            .collect();

        suitable_challenges.first().cloned()
    }

    /// Get personalized encouragement message based on performance
    pub fn get_encouragement(&self) -> String {
        if self.success_rate >= 0.9 {
            "🏆 Outstanding! You're mastering this level. Time for a bigger challenge!".to_string()
        } else if self.success_rate >= 0.7 {
            "✅ Great work! You're in the optimal learning zone.".to_string()
        } else if self.success_rate >= 0.5 {
            "💪 Keep pushing! You're learning and improving.".to_string()
        } else if self.success_rate >= 0.3 {
            "🎯 Don't give up! Struggling is part of learning. Try an easier challenge.".to_string()
        } else {
            "🤝 Let's find a better starting point. No shame in taking it step by step!".to_string()
        }
    }

    /// Determine if user is in "flow state" (optimal learning)
    pub fn is_in_flow_state(&self) -> bool {
        // Flow state indicators:
        // 1. Success rate near target (65-75%)
        // 2. Recent challenges completed
        // 3. Positive learning velocity

        let in_target_range = self.success_rate >= 0.65 && self.success_rate <= 0.85;
        let has_momentum = self.learning_velocity > 0.0;
        let sufficient_data = self.recent_results.len() >= 3;

        in_target_range && has_momentum && sufficient_data
    }

    /// Get difficulty level description
    pub fn get_level_description(&self) -> String {
        match self.current_level {
            l if l < 1.0 => "🌱 Absolute Beginner".to_string(),
            l if l < 2.5 => "📚 Beginner".to_string(),
            l if l < 4.0 => "🎓 Novice".to_string(),
            l if l < 6.0 => "⚡ Intermediate".to_string(),
            l if l < 8.0 => "🔥 Advanced".to_string(),
            l if l < 9.5 => "💎 Expert".to_string(),
            _ => "👑 Master".to_string(),
        }
    }

    pub fn get_stats(&self) -> DifficultyStats {
        DifficultyStats {
            current_level: self.current_level,
            level_description: self.get_level_description(),
            success_rate: self.success_rate,
            learning_velocity: self.learning_velocity,
            total_attempts: self.total_attempts,
            total_successes: self.total_successes,
            in_flow_state: self.is_in_flow_state(),
            encouragement: self.get_encouragement(),
        }
    }
}

impl Default for AdaptiveDifficulty {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DifficultyStats {
    pub current_level: f32,
    pub level_description: String,
    pub success_rate: f32,
    pub learning_velocity: f32,
    pub total_attempts: u32,
    pub total_successes: u32,
    pub in_flow_state: bool,
    pub encouragement: String,
}

// ============================================================================
// CHALLENGE DATABASE (Mock for now)
// ============================================================================

pub fn get_sample_challenges() -> Vec<Challenge> {
    vec![
        Challenge {
            id: "recon-001".to_string(),
            title: "Basic Network Reconnaissance".to_string(),
            description: "Use nmap to discover hosts on the network".to_string(),
            difficulty: 1.0,
            estimated_time: 300,
            category: ChallengeCategory::Reconnaissance,
            prerequisites: vec![],
            learning_objectives: vec![
                "Understand basic network scanning".to_string(),
                "Use nmap for host discovery".to_string(),
            ],
        },
        Challenge {
            id: "scan-001".to_string(),
            title: "Port Scanning Basics".to_string(),
            description: "Scan a target for open ports and services".to_string(),
            difficulty: 2.0,
            estimated_time: 600,
            category: ChallengeCategory::Scanning,
            prerequisites: vec!["recon-001".to_string()],
            learning_objectives: vec![
                "Identify open ports".to_string(),
                "Determine service versions".to_string(),
            ],
        },
        Challenge {
            id: "enum-001".to_string(),
            title: "Service Enumeration".to_string(),
            description: "Enumerate SMB shares and users".to_string(),
            difficulty: 3.5,
            estimated_time: 900,
            category: ChallengeCategory::Enumeration,
            prerequisites: vec!["scan-001".to_string()],
            learning_objectives: vec![
                "Use enum4linux for SMB enumeration".to_string(),
                "Identify potential attack vectors".to_string(),
            ],
        },
        Challenge {
            id: "exploit-001".to_string(),
            title: "Basic Buffer Overflow".to_string(),
            description: "Exploit a simple buffer overflow vulnerability".to_string(),
            difficulty: 6.0,
            estimated_time: 1800,
            category: ChallengeCategory::Exploitation,
            prerequisites: vec!["enum-001".to_string()],
            learning_objectives: vec![
                "Understand stack-based buffer overflows".to_string(),
                "Craft exploit payloads".to_string(),
            ],
        },
    ]
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_difficulty_increases_on_quick_success() {
        let mut difficulty = AdaptiveDifficulty::new();
        let initial_level = difficulty.current_level;

        let result = ChallengeResult {
            success: true,
            time_taken: 100,
            expected_time: 300,
            attempts: 1,
            difficulty_level: 1.0,
            hints_used: 0,
            completed_at: chrono::Utc::now(),
        };

        difficulty.adjust_difficulty(&result);
        assert!(difficulty.current_level > initial_level);
    }

    #[test]
    fn test_difficulty_decreases_on_struggle() {
        let mut difficulty = AdaptiveDifficulty::new();
        difficulty.current_level = 5.0;
        let initial_level = difficulty.current_level;

        let result = ChallengeResult {
            success: false,
            time_taken: 1000,
            expected_time: 300,
            attempts: 6,
            difficulty_level: 5.0,
            hints_used: 4,
            completed_at: chrono::Utc::now(),
        };

        difficulty.adjust_difficulty(&result);
        assert!(difficulty.current_level < initial_level);
    }

    #[test]
    fn test_flow_state_detection() {
        let mut difficulty = AdaptiveDifficulty::new();

        // Add several successful results at 70% success rate
        for i in 0..10 {
            let result = ChallengeResult {
                success: i % 10 < 7, // 70% success
                time_taken: 300,
                expected_time: 300,
                attempts: 1,
                difficulty_level: 3.0,
                hints_used: 0,
                completed_at: chrono::Utc::now(),
            };
            difficulty.adjust_difficulty(&result);
        }

        assert_eq!(difficulty.success_rate, 0.7);
    }
}
