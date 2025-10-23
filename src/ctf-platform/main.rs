//! SynOS CTF Platform - Main Binary
//!
//! Command-line interface for the CTF training platform

use synos_ctf_platform::{CTFPlatform, ChallengeId, SubmitResult};
use std::env;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        print_usage();
        return Ok(());
    }

    let mut platform = CTFPlatform::new();

    match args[1].as_str() {
        "list" => {
            println!("🏆 Available CTF Challenges:");
            println!();

            for (_, challenge) in &platform.challenges {
                println!("  {} - {} ({} points)",
                    challenge.id.0,
                    challenge.title,
                    challenge.points
                );
                println!("    Category: {:?} | Difficulty: {:?}",
                    challenge.category,
                    challenge.difficulty
                );
                println!("    {}", challenge.description);
                println!();
            }
        }
        "start" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-ctf start <challenge_id>");
                return Ok(());
            }

            let challenge_id = ChallengeId(args[2].clone());
            let user_id = get_user_id();

            match platform.start_challenge(&challenge_id, user_id) {
                Ok(session) => {
                    println!("✅ Challenge started: {}", challenge_id.0);

                    if let Some(challenge) = platform.challenges.get(&challenge_id) {
                        println!();
                        println!("📋 Challenge: {}", challenge.title);
                        println!("🎯 Description: {}", challenge.description);
                        println!("💰 Points: {}", challenge.points);
                        println!("📚 Category: {:?}", challenge.category);
                        println!("⚡ Difficulty: {:?}", challenge.difficulty);
                        println!();
                        println!("🚀 Good luck! Submit your flag with: synos-ctf submit {} <flag>", challenge_id.0);
                    }
                }
                Err(e) => {
                    eprintln!("❌ Failed to start challenge: {}", e);
                }
            }
        }
        "submit" => {
            if args.len() < 4 {
                eprintln!("Usage: synos-ctf submit <challenge_id> <flag>");
                return Ok(());
            }

            let challenge_id = ChallengeId(args[2].clone());
            let flag = args[3].clone();
            let user_id = get_user_id();
            let username = get_username();

            match platform.submit_flag(&challenge_id, &user_id, &username, &flag) {
                SubmitResult::Correct { points, rank } => {
                    println!("🎉 Correct! You earned {} points!", points);
                    println!("🏆 Current rank: #{}", rank);

                    // Show updated leaderboard
                    show_leaderboard(&platform);
                }
                SubmitResult::Incorrect { attempts_remaining } => {
                    println!("❌ Incorrect flag. {} attempts remaining.", attempts_remaining);
                }
                SubmitResult::MaxAttemptsReached => {
                    println!("🚫 Maximum attempts reached for this challenge.");
                }
            }
        }
        "hint" => {
            if args.len() < 3 {
                eprintln!("Usage: synos-ctf hint <challenge_id>");
                return Ok(());
            }

            let challenge_id = ChallengeId(args[2].clone());
            let user_id = get_user_id();

            match platform.request_hint(&challenge_id, &user_id, 0) {
                Ok(hint) => {
                    println!("💡 Hint: {}", hint);
                    println!("⚠️  Note: Using hints may reduce your final score.");
                }
                Err(e) => {
                    eprintln!("❌ Failed to get hint: {}", e);
                }
            }
        }
        "leaderboard" => {
            show_leaderboard(&platform);
        }
        "status" => {
            let user_id = get_user_id();
            let username = get_username();

            println!("👤 User: {} (ID: {})", username, user_id);

            if let Some(entry) = platform.leaderboard.entries.get(&user_id) {
                println!("🏆 Rank: #{}", entry.rank);
                println!("💰 Total Points: {}", entry.total_points);
                println!("🎯 Challenges Solved: {}", entry.challenges_solved);
            } else {
                println!("📊 No challenges completed yet. Start with: synos-ctf list");
            }
        }
        "demo" => {
            println!("🚀 SynOS CTF Platform Demo");
            println!("Available challenges: {}", platform.challenges.len());

            // Demo the platform
            let demo_user = "demo_user".to_string();
            let demo_challenge = ChallengeId("ctf_crypto_caesar".to_string());

            println!("Starting demo challenge...");
            if let Ok(_session) = platform.start_challenge(&demo_challenge, demo_user.clone()) {
                println!("✅ Demo challenge started");

                // Try submitting correct flag
                let result = platform.submit_flag(&demo_challenge, &demo_user, "Demo User", "SynOS{HELLO_WORLD}");
                match result {
                    SubmitResult::Correct { points, rank } => {
                        println!("🎉 Demo completed! Earned {} points, rank #{}", points, rank);
                    }
                    _ => {
                        println!("Demo submission result: {:?}", result);
                    }
                }
            }
        }
        "version" => {
            println!("SynOS CTF Platform v{}", env!("CARGO_PKG_VERSION"));
        }
        "help" | "--help" | "-h" => {
            print_usage();
        }
        _ => {
            eprintln!("Unknown command: {}", args[1]);
            print_usage();
        }
    }

    Ok(())
}

fn show_leaderboard(platform: &CTFPlatform) {
    println!("🏆 CTF Leaderboard:");
    println!();

    let top_entries = platform.leaderboard.get_top(10);
    for entry in &top_entries {
        println!("  #{} - {} ({} points, {} challenges)",
            entry.rank,
            entry.username,
            entry.total_points,
            entry.challenges_solved
        );
    }

    if top_entries.is_empty() {
        println!("  No participants yet. Be the first!");
    }
}

fn get_user_id() -> String {
    // In production, this would get the actual user ID
    // For now, use environment or default
    env::var("USER").unwrap_or_else(|_| "synos_user".to_string())
}

fn get_username() -> String {
    // In production, this would get the actual username
    // For now, use environment or default
    env::var("USER").unwrap_or_else(|_| "synos_user".to_string())
}

fn print_usage() {
    println!("SynOS CTF Platform - Capture The Flag training system");
    println!();
    println!("USAGE:");
    println!("    synos-ctf <COMMAND> [OPTIONS]");
    println!();
    println!("COMMANDS:");
    println!("    list                     List available challenges");
    println!("    start <challenge_id>     Start a specific challenge");
    println!("    submit <challenge_id> <flag>  Submit flag for challenge");
    println!("    hint <challenge_id>      Get hint for challenge (may reduce score)");
    println!("    leaderboard              Show current leaderboard");
    println!("    status                   Show your current status and progress");
    println!("    demo                     Run platform demonstration");
    println!("    version                  Show version information");
    println!("    help                     Show this help message");
    println!();
    println!("EXAMPLES:");
    println!("    synos-ctf list");
    println!("    synos-ctf start ctf_crypto_caesar");
    println!("    synos-ctf submit ctf_crypto_caesar SYNOS{{HELLO_WORLD}}");
    println!("    synos-ctf hint ctf_crypto_caesar");
    println!("    synos-ctf leaderboard");
    println!();
    println!("For more information, see: https://github.com/TLimoges33/Syn_OS");
}
