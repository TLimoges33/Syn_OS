//! Bridge between Desktop Environment (no_std) and CTF Platform (std)
//!
//! This module provides a compatibility layer for CTF challenge integration
//! into the MATE desktop environment.

use alloc::{string::{String, ToString}, vec::Vec, format, boxed::Box};

/// CTF Challenge difficulty levels
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ChallengeDifficulty {
    Easy,
    Medium,
    Hard,
    Insane,
}

/// CTF Challenge categories
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ChallengeCategory {
    Web,
    Binary,
    Crypto,
    Forensics,
    Reverse,
    Pwn,
    Misc,
}

/// CTF Challenge information
#[derive(Debug, Clone)]
pub struct ChallengeInfo {
    pub id: u32,
    pub name: String,
    pub category: ChallengeCategory,
    pub difficulty: ChallengeDifficulty,
    pub points: u32,
    pub description: String,
    pub solved: bool,
}

/// User progress in CTF platform
#[derive(Debug, Clone)]
pub struct UserProgress {
    pub total_challenges: u32,
    pub solved_challenges: u32,
    pub total_points: u32,
    pub rank: u32,
    pub recent_solves: Vec<String>,
}

/// Leaderboard entry
#[derive(Debug, Clone)]
pub struct LeaderboardEntry {
    pub rank: u32,
    pub username: String,
    pub points: u32,
    pub challenges_solved: u32,
}

/// Bridge interface for CTF Platform integration
#[derive(Debug)]
pub struct CTFPlatformBridge {
    /// Track if the CTF daemon is available
    daemon_available: bool,
    /// Cached challenges (for desktop display)
    cached_challenges: Vec<ChallengeInfo>,
    /// Cached user progress
    cached_progress: Option<UserProgress>,
}

impl CTFPlatformBridge {
    /// Create a new bridge instance
    pub fn new() -> Self {
        Self {
            daemon_available: false,
            cached_challenges: Vec::new(),
            cached_progress: None,
        }
    }

    /// Check if CTF platform is available
    pub fn is_available(&self) -> bool {
        self.daemon_available
    }

    /// Activate the CTF platform daemon
    pub fn activate_daemon(&mut self) -> Result<(), String> {
        // In a full implementation, this would:
        // 1. Check if daemon is running
        // 2. Spawn daemon if needed
        // 3. Establish IPC connection
        // 4. Load initial data

        self.daemon_available = true;
        self.load_sample_challenges();
        self.load_sample_progress();
        Ok(())
    }

    /// Get available challenges
    pub fn get_challenges(&self) -> &[ChallengeInfo] {
        &self.cached_challenges
    }

    /// Get challenges by category
    pub fn get_challenges_by_category(&self, category: ChallengeCategory) -> Vec<ChallengeInfo> {
        self.cached_challenges
            .iter()
            .filter(|c| c.category == category)
            .cloned()
            .collect()
    }

    /// Get challenges by difficulty
    pub fn get_challenges_by_difficulty(&self, difficulty: ChallengeDifficulty) -> Vec<ChallengeInfo> {
        self.cached_challenges
            .iter()
            .filter(|c| c.difficulty == difficulty)
            .cloned()
            .collect()
    }

    /// Get unsolved challenges
    pub fn get_unsolved_challenges(&self) -> Vec<ChallengeInfo> {
        self.cached_challenges
            .iter()
            .filter(|c| !c.solved)
            .cloned()
            .collect()
    }

    /// Launch a challenge
    pub fn launch_challenge(&mut self, challenge_id: u32) -> Result<String, String> {
        if !self.daemon_available {
            return Err("CTF daemon not available".to_string());
        }

        // Find the challenge
        if let Some(_challenge) = self.cached_challenges.iter().find(|c| c.id == challenge_id) {
            // In a full implementation:
            // 1. Notify daemon to prepare challenge environment
            // 2. Set up isolated workspace
            // 3. Launch relevant tools
            // 4. Open challenge description

            Ok(format!("Challenge {} launched (integration point established)", challenge_id))
        } else {
            Err(format!("Challenge {} not found", challenge_id))
        }
    }

    /// Submit a flag
    pub fn submit_flag(&mut self, challenge_id: u32, flag: &str) -> Result<bool, String> {
        if !self.daemon_available {
            return Err("CTF daemon not available".to_string());
        }

        // In a full implementation:
        // 1. Send flag to CTF platform API
        // 2. Validate flag
        // 3. Update user progress
        // 4. Unlock new challenges (if applicable)

        // Stub response
        if flag.starts_with("flag{") || flag.starts_with("SYN{") {
            // Mark as solved
            if let Some(challenge) = self.cached_challenges.iter_mut().find(|c| c.id == challenge_id) {
                challenge.solved = true;
            }
            Ok(true)
        } else {
            Ok(false)
        }
    }

    /// Get user progress
    pub fn get_progress(&self) -> Option<&UserProgress> {
        self.cached_progress.as_ref()
    }

    /// Get leaderboard
    pub fn get_leaderboard(&self, limit: usize) -> Vec<LeaderboardEntry> {
        // Stub leaderboard data
        let mut leaderboard = Vec::new();
        for i in 1..=limit.min(10) {
            leaderboard.push(LeaderboardEntry {
                rank: i as u32,
                username: format!("User{}", i),
                points: 1000 - (i as u32 * 50),
                challenges_solved: 20 - (i as u32 * 2),
            });
        }
        leaderboard
    }

    /// Refresh challenges from platform
    pub fn refresh_challenges(&mut self) -> Result<(), String> {
        if !self.daemon_available {
            return Err("CTF daemon not available".to_string());
        }

        // In a full implementation:
        // 1. Query CTF platform API
        // 2. Update cached challenges
        // 3. Notify desktop of changes

        self.load_sample_challenges();
        Ok(())
    }

    /// Get recommended challenge based on user skill
    pub fn get_recommended_challenge(&self) -> Option<ChallengeInfo> {
        // Simple recommendation: unsolved challenge closest to user's skill level
        self.get_unsolved_challenges().into_iter().next()
    }

    /// Load sample challenges for demonstration
    fn load_sample_challenges(&mut self) {
        self.cached_challenges = alloc::vec![
            ChallengeInfo {
                id: 1,
                name: "Web Injection 101".to_string(),
                category: ChallengeCategory::Web,
                difficulty: ChallengeDifficulty::Easy,
                points: 100,
                description: "Basic SQL injection vulnerability".to_string(),
                solved: false,
            },
            ChallengeInfo {
                id: 2,
                name: "Buffer Overflow Basics".to_string(),
                category: ChallengeCategory::Binary,
                difficulty: ChallengeDifficulty::Medium,
                points: 250,
                description: "Classic stack-based buffer overflow".to_string(),
                solved: false,
            },
            ChallengeInfo {
                id: 3,
                name: "RSA Weakness".to_string(),
                category: ChallengeCategory::Crypto,
                difficulty: ChallengeDifficulty::Hard,
                points: 500,
                description: "Exploit weak RSA parameters".to_string(),
                solved: false,
            },
            ChallengeInfo {
                id: 4,
                name: "Hidden Data".to_string(),
                category: ChallengeCategory::Forensics,
                difficulty: ChallengeDifficulty::Medium,
                points: 300,
                description: "Extract hidden data from image file".to_string(),
                solved: false,
            },
            ChallengeInfo {
                id: 5,
                name: "Reverse Me".to_string(),
                category: ChallengeCategory::Reverse,
                difficulty: ChallengeDifficulty::Hard,
                points: 450,
                description: "Reverse engineer the binary to find the flag".to_string(),
                solved: false,
            },
        ];
    }

    /// Load sample user progress
    fn load_sample_progress(&mut self) {
        self.cached_progress = Some(UserProgress {
            total_challenges: 50,
            solved_challenges: 12,
            total_points: 1850,
            rank: 42,
            recent_solves: alloc::vec![
                "Web Injection 101".to_string(),
                "XSS Challenge".to_string(),
                "File Upload Bypass".to_string(),
            ],
        });
    }
}

/// CTF Platform UI state for desktop integration
#[derive(Debug)]
pub struct CTFPlatformUI {
    /// Bridge to CTF platform
    bridge: CTFPlatformBridge,
    /// Currently selected challenge
    selected_challenge: Option<u32>,
    /// Current filter category
    filter_category: Option<ChallengeCategory>,
    /// Current filter difficulty
    filter_difficulty: Option<ChallengeDifficulty>,
    /// Show only unsolved challenges
    show_only_unsolved: bool,
}

impl CTFPlatformUI {
    /// Create a new CTF Platform UI
    pub fn new() -> Self {
        let mut bridge = CTFPlatformBridge::new();
        let _ = bridge.activate_daemon(); // Initialize with sample data

        Self {
            bridge,
            selected_challenge: None,
            filter_category: None,
            filter_difficulty: None,
            show_only_unsolved: true,
        }
    }

    /// Get filtered challenges for display
    pub fn get_filtered_challenges(&self) -> Vec<ChallengeInfo> {
        let mut challenges = if self.show_only_unsolved {
            self.bridge.get_unsolved_challenges()
        } else {
            self.bridge.get_challenges().to_vec()
        };

        // Apply category filter
        if let Some(category) = self.filter_category {
            challenges.retain(|c| c.category == category);
        }

        // Apply difficulty filter
        if let Some(difficulty) = self.filter_difficulty {
            challenges.retain(|c| c.difficulty == difficulty);
        }

        challenges
    }

    /// Set category filter
    pub fn set_category_filter(&mut self, category: Option<ChallengeCategory>) {
        self.filter_category = category;
    }

    /// Set difficulty filter
    pub fn set_difficulty_filter(&mut self, difficulty: Option<ChallengeDifficulty>) {
        self.filter_difficulty = difficulty;
    }

    /// Toggle show unsolved only
    pub fn toggle_unsolved_only(&mut self) {
        self.show_only_unsolved = !self.show_only_unsolved;
    }

    /// Select a challenge
    pub fn select_challenge(&mut self, challenge_id: u32) {
        self.selected_challenge = Some(challenge_id);
    }

    /// Get selected challenge
    pub fn get_selected_challenge(&self) -> Option<ChallengeInfo> {
        self.selected_challenge.and_then(|id| {
            self.bridge.get_challenges().iter().find(|c| c.id == id).cloned()
        })
    }

    /// Launch selected challenge
    pub fn launch_selected(&mut self) -> Result<String, String> {
        if let Some(id) = self.selected_challenge {
            self.bridge.launch_challenge(id)
        } else {
            Err("No challenge selected".to_string())
        }
    }

    /// Submit flag for selected challenge
    pub fn submit_flag(&mut self, flag: &str) -> Result<bool, String> {
        if let Some(id) = self.selected_challenge {
            self.bridge.submit_flag(id, flag)
        } else {
            Err("No challenge selected".to_string())
        }
    }

    /// Get user progress
    pub fn get_progress(&self) -> Option<&UserProgress> {
        self.bridge.get_progress()
    }

    /// Get leaderboard
    pub fn get_leaderboard(&self) -> Vec<LeaderboardEntry> {
        self.bridge.get_leaderboard(10)
    }

    /// Get recommended challenge
    pub fn get_recommendation(&self) -> Option<ChallengeInfo> {
        self.bridge.get_recommended_challenge()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_challenge_filtering() {
        let ui = CTFPlatformUI::new();
        let challenges = ui.get_filtered_challenges();
        assert!(!challenges.is_empty());
    }

    #[test]
    fn test_difficulty_filter() {
        let mut ui = CTFPlatformUI::new();
        ui.set_difficulty_filter(Some(ChallengeDifficulty::Easy));
        ui.toggle_unsolved_only(); // Show all
        let challenges = ui.get_filtered_challenges();
        assert!(challenges.iter().all(|c| c.difficulty == ChallengeDifficulty::Easy));
    }

    #[test]
    fn test_category_filter() {
        let mut ui = CTFPlatformUI::new();
        ui.set_category_filter(Some(ChallengeCategory::Web));
        ui.toggle_unsolved_only(); // Show all
        let challenges = ui.get_filtered_challenges();
        assert!(challenges.iter().all(|c| c.category == ChallengeCategory::Web));
    }
}
