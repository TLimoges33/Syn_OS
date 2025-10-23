// CTF Platform Module - Capture The Flag Training System
//
// This module provides a complete CTF platform for hands-on cybersecurity training
// with challenges, leaderboards, flag validation, and VM spawning.

pub mod ctf_engine;

// Re-export main types
pub use ctf_engine::{
    CTFPlatform,
    Challenge,
    CTFCategory,
    Difficulty,
    ChallengeId,
    FlagValidator,
    ChallengeSession,
    SubmitResult,
    Leaderboard,
    LeaderboardEntry,
    Hint,
};

/// Demo function showing CTF platform usage
pub async fn demo_ctf_platform() -> Result<(), String> {
    println!("🏆 SynOS CTF Platform - V1.9 Demo");
    println!("=====================================\n");

    let mut platform = CTFPlatform::new();

    println!("📊 Platform Statistics:");
    println!("   Total challenges: {}", platform.challenges.len());
    println!("\n");

    // Simulate user
    let user_id = "user_001".to_string();
    let username = "Alice";

    // Challenge 1: Caesar Cipher
    println!("🔐 Attempting Challenge: Caesar Cipher Cracking");
    let challenge_id = ChallengeId("ctf_crypto_caesar".to_string());

    platform.start_challenge(&challenge_id, user_id.clone())?;
    println!("   ✅ Challenge started!");

    // Submit correct flag
    println!("\n🚩 Submitting flag...");
    match platform.submit_flag(&challenge_id, &user_id, username, "SynOS{HELLO_WORLD}") {
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

    println!("\n🎉 CTF Platform Demo Complete!");

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
    async fn test_challenge_submission() {
        let mut platform = CTFPlatform::new();
        let challenge_id = ChallengeId("ctf_crypto_caesar".to_string());
        let user_id = "test_user".to_string();
        let username = "TestUser";

        platform.start_challenge(&challenge_id, user_id.clone()).unwrap();

        let result = platform.submit_flag(&challenge_id, &user_id, username, "SynOS{HELLO_WORLD}");
        match result {
            SubmitResult::Correct { points, .. } => {
                assert!(points > 0);
            }
            _ => panic!("Expected correct flag submission"),
        }
    }
}
