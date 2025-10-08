//! SynOS VM/War Games Platform
//!
//! Training environment orchestration, CTF challenges, and progress tracking

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct WarGamesEnvironment {
    id: Uuid,
    name: String,
    difficulty: Difficulty,
    challenges: Vec<Challenge>,
    leaderboard: Vec<PlayerScore>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
enum Difficulty {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Challenge {
    id: Uuid,
    name: String,
    category: ChallengeCategory,
    points: u32,
    flags: Vec<String>,
    hints: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum ChallengeCategory {
    WebExploitation,
    BinaryExploitation,
    Cryptography,
    Forensics,
    ReverseEngineering,
    NetworkSecurity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PlayerScore {
    player_id: String,
    score: u32,
    challenges_solved: Vec<Uuid>,
}

fn main() {
    println!("🎮 SynOS VM/War Games Platform");
    println!("===============================\n");

    demo_environment_orchestration();
    println!();
    demo_ctf_challenges();
    println!();
    demo_progress_tracking();
}

fn demo_environment_orchestration() {
    println!("🖥️  Training Environment Orchestration");
    println!("─────────────────────────────────────");

    println!("✅ Virtual Machine Templates:");
    println!("   • Ubuntu 22.04 - Web exploitation lab");
    println!("   • Kali Linux - Penetration testing");
    println!("   • Windows Server - Active Directory scenarios");
    println!("   • Metasploitable 3 - Vulnerable targets");
    println!("   • DVWA - Web application security");

    println!("\n⚙️  Orchestration Features:");
    println!("   • Automated VM deployment");
    println!("   • Network isolation");
    println!("   • Snapshot management");
    println!("   • Resource allocation");
    println!("   • Auto-reset on completion");

    println!("\n🌐 Network Simulation:");
    println!("   • Isolated subnets");
    println!("   • Firewall rules");
    println!("   • Traffic monitoring");
    println!("   • Attack/defense scenarios");
}

fn demo_ctf_challenges() {
    println!("🏆 CTF Challenge System");
    println!("───────────────────────");

    let mut challenges = Vec::new();

    challenges.push(Challenge {
        id: Uuid::new_v4(),
        name: "SQL Injection 101".to_string(),
        category: ChallengeCategory::WebExploitation,
        points: 100,
        flags: vec!["SynOS{sql_injection_basic}".to_string()],
        hints: vec!["Check the login form".to_string()],
    });

    challenges.push(Challenge {
        id: Uuid::new_v4(),
        name: "Buffer Overflow Challenge".to_string(),
        category: ChallengeCategory::BinaryExploitation,
        points: 250,
        flags: vec!["SynOS{buffer_overflow_pwned}".to_string()],
        hints: vec!["Look for unsafe strcpy()".to_string()],
    });

    challenges.push(Challenge {
        id: Uuid::new_v4(),
        name: "RSA Crypto Breaking".to_string(),
        category: ChallengeCategory::Cryptography,
        points: 300,
        flags: vec!["SynOS{weak_rsa_exponent}".to_string()],
        hints: vec!["Check the public exponent".to_string()],
    });

    println!("✅ Available Challenges:");
    for (i, challenge) in challenges.iter().enumerate() {
        println!("   {}. {} - {:?} ({} points)",
            i + 1,
            challenge.name,
            challenge.category,
            challenge.points
        );
    }

    println!("\n🏅 Challenge Categories:");
    let mut category_counts: HashMap<String, usize> = HashMap::new();
    for challenge in &challenges {
        *category_counts.entry(format!("{:?}", challenge.category)).or_insert(0) += 1;
    }
    for (category, count) in category_counts {
        println!("   • {}: {}", category, count);
    }
}

fn demo_progress_tracking() {
    println!("📊 Progress Tracking & Leaderboard");
    println!("──────────────────────────────────");

    let mut leaderboard = vec![
        PlayerScore {
            player_id: "alice".to_string(),
            score: 850,
            challenges_solved: vec![Uuid::new_v4(), Uuid::new_v4()],
        },
        PlayerScore {
            player_id: "bob".to_string(),
            score: 650,
            challenges_solved: vec![Uuid::new_v4()],
        },
        PlayerScore {
            player_id: "charlie".to_string(),
            score: 450,
            challenges_solved: vec![Uuid::new_v4()],
        },
    ];

    leaderboard.sort_by(|a, b| b.score.cmp(&a.score));

    println!("🏆 Leaderboard:");
    for (rank, player) in leaderboard.iter().enumerate() {
        println!("   {}. {} - {} points ({} challenges)",
            rank + 1,
            player.player_id,
            player.score,
            player.challenges_solved.len()
        );
    }

    println!("\n📈 Training Metrics:");
    println!("   • Total Players: {}", leaderboard.len());
    println!("   • Average Score: {}", leaderboard.iter().map(|p| p.score).sum::<u32>() / leaderboard.len() as u32);
    println!("   • Total Challenges Solved: {}", leaderboard.iter().map(|p| p.challenges_solved.len()).sum::<usize>());

    let env = WarGamesEnvironment {
        id: Uuid::new_v4(),
        name: "SynOS Cybersecurity Training Lab".to_string(),
        difficulty: Difficulty::Intermediate,
        challenges: vec![],
        leaderboard,
    };

    println!("\n✅ Environment: {}", env.name);
    println!("   Difficulty: {:?}", env.difficulty);
    println!("   Environment ID: {}", env.id);

    println!("\n✅ VM/War Games Platform ready!");
}
