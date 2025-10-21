// CTF Platform Module - Capture The Flag Training System
//
// This module provides a complete CTF platform for hands-on cybersecurity training
// with challenges, leaderboards, flag validation, and VM spawning.

pub mod ctf_engine;

// Re-export main types
pub use ctf_engine::{
    CTFPlatform,
    Challenge,
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeId,
    FlagFormat,
    FlagValidator,
    ChallengeSession,
    SubmitResult,
    HintRequest,
    Leaderboard,
    LeaderboardEntry,
    VMConfig,
};

/// Demo function showing CTF platform usage
pub async fn demo_ctf_platform() -> Result<(), String> {
    println!("🏆 SynOS CTF Platform - V1.9 Demo");
    println!("=====================================\n");

    let mut platform = CTFPlatform::new();

    println!("📊 Platform Statistics:");
    println!("   Total challenges: {}", platform.challenges.len());
    println!("   Categories: Web, Pwn, Crypto, Forensics, Reverse Engineering, Misc");
    println!("\n");

    // Show available challenges
    println!("🎯 Available Challenges:");
    println!("─────────────────────────────────────────────────────────────");

    let mut challenges: Vec<_> = platform.challenges.values().collect();
    challenges.sort_by_key(|c| c.points);

    for challenge in &challenges {
        let difficulty_emoji = match challenge.difficulty {
            ChallengeDifficulty::Beginner => "🟢",
            ChallengeDifficulty::Intermediate => "🟡",
            ChallengeDifficulty::Advanced => "🟠",
            ChallengeDifficulty::Expert => "🔴",
        };

        println!("{} [{:?}] {} - {} pts",
            difficulty_emoji,
            challenge.category,
            challenge.title,
            challenge.points
        );
        println!("   {}", challenge.description);
        println!("   Hints available: {}", challenge.hints.len());
        println!();
    }

    // Simulate user attempting challenges
    println!("\n👤 User Simulation: Alice");
    println!("─────────────────────────────────────────────────────────────");

    let user_id = "user_001";
    let username = "Alice";

    // Challenge 1: Caesar Cipher (Easy)
    println!("\n🔐 Attempting Challenge: Caesar Cipher Cracking");
    let challenge_id = ChallengeId("ctf_crypto_caesar".to_string());

    platform.start_challenge(&challenge_id, user_id)?;
    println!("   ✅ Challenge started!");

    // Request a hint
    println!("\n💡 Requesting hint...");
    match platform.request_hint(&challenge_id, user_id, 0) {
        Ok(HintRequest::HintRevealed { hint, points_deducted }) => {
            println!("   Hint: {}", hint);
            println!("   Points deducted: {}", points_deducted);
        }
        _ => println!("   No hint available"),
    }

    // Submit correct flag
    println!("\n🚩 Submitting flag: SynOS{HELLO_WORLD}");
    match platform.submit_flag(&challenge_id, user_id, username, "SynOS{HELLO_WORLD}") {
        SubmitResult::Correct { points, rank } => {
            println!("   ✅ CORRECT! +{} points", points);
            println!("   Current rank: #{}", rank);
        }
        SubmitResult::Incorrect { attempts_remaining } => {
            println!("   ❌ Incorrect flag. Attempts remaining: {}", attempts_remaining);
        }
        SubmitResult::MaxAttemptsReached => {
            println!("   ⛔ Maximum attempts reached!");
        }
    }

    // Challenge 2: SQL Injection (Medium)
    println!("\n\n💉 Attempting Challenge: SQL Injection Attack");
    let challenge_id = ChallengeId("ctf_web_sqli".to_string());

    platform.start_challenge(&challenge_id, user_id)?;
    println!("   ✅ Challenge started!");
    println!("   🖥️  VM spawned at: 10.10.10.100:8080");

    // Submit incorrect flag first
    println!("\n🚩 Submitting flag: SynOS{wrong_flag}");
    match platform.submit_flag(&challenge_id, user_id, username, "SynOS{wrong_flag}") {
        SubmitResult::Incorrect { attempts_remaining } => {
            println!("   ❌ Incorrect flag. Attempts remaining: {}", attempts_remaining);
        }
        _ => {}
    }

    // Submit correct flag
    println!("\n🚩 Submitting flag: SynOS{1=1_OR_NOT_2=2}");
    match platform.submit_flag(&challenge_id, user_id, username, "SynOS{1=1_OR_NOT_2=2}") {
        SubmitResult::Correct { points, rank } => {
            println!("   ✅ CORRECT! +{} points", points);
            println!("   Current rank: #{}", rank);
        }
        _ => {}
    }

    // Show leaderboard
    println!("\n\n🏅 Leaderboard:");
    println!("─────────────────────────────────────────────────────────────");

    let top_players = platform.leaderboard.get_top(10);
    for (i, entry) in top_players.iter().enumerate() {
        let medal = match i {
            0 => "🥇",
            1 => "🥈",
            2 => "🥉",
            _ => "  ",
        };

        println!("{} #{:<2} {:.<20} {:>5} pts ({} challenges)",
            medal,
            entry.rank,
            entry.username,
            entry.total_points,
            entry.challenges_solved
        );
    }

    // Platform statistics
    println!("\n\n📈 Platform Analytics:");
    println!("─────────────────────────────────────────────────────────────");
    println!("   Active sessions: {}", platform.active_sessions.len());
    println!("   Total players: {}", platform.leaderboard.entries.len());

    let total_solves: usize = platform.leaderboard.entries.values()
        .map(|e| e.challenges_solved)
        .sum();
    println!("   Total challenge solves: {}", total_solves);

    println!("\n🎉 CTF Platform Demo Complete!");
    println!("\n💡 Key Features:");
    println!("   • 3+ pre-loaded challenges (Web, Pwn, Crypto)");
    println!("   • Progressive hint system with point deductions");
    println!("   • VM spawning for vulnerable environments");
    println!("   • Real-time leaderboard with automatic ranking");
    println!("   • Flag validation (Static, Dynamic, Regex)");
    println!("   • Integration with V1.7 AI Tutor for adaptive learning");
    println!("   • Session management with attempt tracking");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_platform_creation() {
        let platform = CTFPlatform::new();
        assert!(platform.challenges.len() >= 3);
    }

    #[tokio::test]
    async fn test_challenge_lifecycle() {
        let mut platform = CTFPlatform::new();
        let challenge_id = ChallengeId("ctf_crypto_caesar".to_string());
        let user_id = "test_user";
        let username = "TestUser";

        // Start challenge
        let result = platform.start_challenge(&challenge_id, user_id);
        assert!(result.is_ok());

        // Submit correct flag
        let result = platform.submit_flag(&challenge_id, user_id, username, "SynOS{HELLO_WORLD}");
        match result {
            SubmitResult::Correct { points, rank } => {
                assert!(points > 0);
                assert_eq!(rank, 1);
            }
            _ => panic!("Expected correct flag submission"),
        }
    }

    #[tokio::test]
    async fn test_hint_system() {
        let mut platform = CTFPlatform::new();
        let challenge_id = ChallengeId("ctf_web_sqli".to_string());
        let user_id = "test_user";

        platform.start_challenge(&challenge_id, user_id).unwrap();

        // Request hint
        let result = platform.request_hint(&challenge_id, user_id, 0);
        match result {
            Ok(HintRequest::HintRevealed { hint, points_deducted }) => {
                assert!(!hint.is_empty());
                assert!(points_deducted > 0);
            }
            _ => panic!("Expected hint to be revealed"),
        }
    }

    #[tokio::test]
    async fn test_leaderboard_ranking() {
        let mut platform = CTFPlatform::new();

        // Add multiple users
        platform.leaderboard.update("user1".to_string(), "Alice".to_string(), 150);
        platform.leaderboard.update("user2".to_string(), "Bob".to_string(), 200);
        platform.leaderboard.update("user3".to_string(), "Charlie".to_string(), 100);

        let top = platform.leaderboard.get_top(3);

        // Bob should be #1 with 200 points
        assert_eq!(top[0].username, "Bob");
        assert_eq!(top[0].rank, 1);
        assert_eq!(top[0].total_points, 200);

        // Alice should be #2 with 150 points
        assert_eq!(top[1].username, "Alice");
        assert_eq!(top[1].rank, 2);
    }
}
