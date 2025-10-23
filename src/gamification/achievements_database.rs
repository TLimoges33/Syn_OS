//! Achievement Database - 200+ Achievements
//!
//! Categories: Combat, Exploration, Mastery, Collection, Reputation, Legendary, Seasonal

#![no_std]

extern crate alloc;

use alloc::vec::Vec;
use alloc::string::{String, ToString};
use super::legendary_skill_tree::*;

/// Generate all 200+ achievements
pub fn generate_all_achievements() -> Vec<Achievement> {
    let mut achievements = Vec::new();

    // ========== LEVEL & XP ACHIEVEMENTS ==========
    achievements.extend(generate_level_achievements());

    // ========== COMBAT ACHIEVEMENTS (Exploitation) ==========
    achievements.extend(generate_combat_achievements());

    // ========== EXPLORATION ACHIEVEMENTS (Discovery) ==========
    achievements.extend(generate_exploration_achievements());

    // ========== MASTERY ACHIEVEMENTS (Skill Perfection) ==========
    achievements.extend(generate_mastery_achievements());

    // ========== COLLECTION ACHIEVEMENTS (Completionism) ==========
    achievements.extend(generate_collection_achievements());

    // ========== REPUTATION ACHIEVEMENTS (Factions) ==========
    achievements.extend(generate_reputation_achievements());

    // ========== LEGENDARY ACHIEVEMENTS (Ultra-Rare) ==========
    achievements.extend(generate_legendary_achievements());

    // ========== SEASONAL ACHIEVEMENTS (Limited Time) ==========
    achievements.extend(generate_seasonal_achievements());

    achievements
}

// ============================================================================
// LEVEL & XP ACHIEVEMENTS
// ============================================================================

fn generate_level_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "first_steps".to_string(),
            name: "First Steps".to_string(),
            description: "Reach level 5".to_string(),
            icon: "🐣".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Common,
            points: 10,
            criteria: AchievementCriteria::ReachLevel(5),
            rewards: vec![
                AchievementReward::XP(500),
                AchievementReward::SkillPoints(1),
            ],
            hidden: false,
        },

        Achievement {
            id: "apprentice".to_string(),
            name: "Apprentice Hacker".to_string(),
            description: "Reach level 10".to_string(),
            icon: "🎓".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Common,
            points: 20,
            criteria: AchievementCriteria::ReachLevel(10),
            rewards: vec![
                AchievementReward::Title("Apprentice".to_string()),
                AchievementReward::XP(1000),
            ],
            hidden: false,
        },

        Achievement {
            id: "journeyman".to_string(),
            name: "Journeyman".to_string(),
            description: "Reach level 25".to_string(),
            icon: "⚒️".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Uncommon,
            points: 50,
            criteria: AchievementCriteria::ReachLevel(25),
            rewards: vec![
                AchievementReward::Title("Journeyman".to_string()),
                AchievementReward::XP(5000),
                AchievementReward::SkillPoints(2),
            ],
            hidden: false,
        },

        Achievement {
            id: "expert".to_string(),
            name: "Expert Practitioner".to_string(),
            description: "Reach level 50".to_string(),
            icon: "🎖️".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Rare,
            points: 100,
            criteria: AchievementCriteria::ReachLevel(50),
            rewards: vec![
                AchievementReward::Title("Expert".to_string()),
                AchievementReward::XP(25000),
                AchievementReward::SkillPoints(5),
                AchievementReward::StreetCred(10),
            ],
            hidden: false,
        },

        Achievement {
            id: "master".to_string(),
            name: "Master of the Craft".to_string(),
            description: "Reach level 75".to_string(),
            icon: "👑".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Epic,
            points: 200,
            criteria: AchievementCriteria::ReachLevel(75),
            rewards: vec![
                AchievementReward::Title("Master".to_string()),
                AchievementReward::XP(100000),
                AchievementReward::SkillPoints(10),
                AchievementReward::StreetCred(25),
            ],
            hidden: false,
        },

        Achievement {
            id: "legendary_100".to_string(),
            name: "LEGENDARY".to_string(),
            description: "Reach level 100 - The ultimate achievement".to_string(),
            icon: "🔱".to_string(),
            category: AchievementCategory::Legendary,
            rarity: AchievementRarity::Legendary,
            points: 1000,
            criteria: AchievementCriteria::ReachLevel(100),
            rewards: vec![
                AchievementReward::Title("LEGEND".to_string()),
                AchievementReward::XP(1000000),
                AchievementReward::SkillPoints(50),
                AchievementReward::StreetCred(100),
                AchievementReward::Cosmetic(
                    CosmeticType::Theme,
                    "Legendary Gold Theme".to_string()
                ),
            ],
            hidden: false,
        },

        // XP Milestones
        Achievement {
            id: "xp_millionaire".to_string(),
            name: "XP Millionaire".to_string(),
            description: "Earn 1,000,000 total XP".to_string(),
            icon: "💰".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Epic,
            points: 150,
            criteria: AchievementCriteria::EarnXP(1000000),
            rewards: vec![
                AchievementReward::SkillPoints(5),
                AchievementReward::Title("Millionaire".to_string()),
            ],
            hidden: false,
        },
    ]
}

// ============================================================================
// COMBAT ACHIEVEMENTS (Exploitation & Hacking)
// ============================================================================

fn generate_combat_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "first_blood".to_string(),
            name: "First Blood".to_string(),
            description: "Successfully exploit your first vulnerability".to_string(),
            icon: "🩸".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Common,
            points: 10,
            criteria: AchievementCriteria::ExploitVulnerabilities(1),
            rewards: vec![
                AchievementReward::XP(500),
            ],
            hidden: false,
        },

        Achievement {
            id: "serial_pwner".to_string(),
            name: "Serial Pwner".to_string(),
            description: "Exploit 50 vulnerabilities".to_string(),
            icon: "🎯".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Rare,
            points: 75,
            criteria: AchievementCriteria::ExploitVulnerabilities(50),
            rewards: vec![
                AchievementReward::Title("Serial Pwner".to_string()),
                AchievementReward::XP(10000),
                AchievementReward::StreetCred(15),
            ],
            hidden: false,
        },

        Achievement {
            id: "exploit_master".to_string(),
            name: "Exploitation Master".to_string(),
            description: "Exploit 500 vulnerabilities".to_string(),
            icon: "💣".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Legendary,
            points: 500,
            criteria: AchievementCriteria::ExploitVulnerabilities(500),
            rewards: vec![
                AchievementReward::Title("Exploitation Master".to_string()),
                AchievementReward::XP(100000),
                AchievementReward::SkillPoints(20),
                AchievementReward::StreetCred(50),
            ],
            hidden: false,
        },

        Achievement {
            id: "zero_day_hunter".to_string(),
            name: "Zero-Day Hunter".to_string(),
            description: "Discover your first 0-day vulnerability".to_string(),
            icon: "💎".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Epic,
            points: 200,
            criteria: AchievementCriteria::Custom("discover_zero_day".to_string()),
            rewards: vec![
                AchievementReward::Title("Zero-Day Hunter".to_string()),
                AchievementReward::XP(50000),
                AchievementReward::SkillPoints(10),
                AchievementReward::StreetCred(30),
            ],
            hidden: false,
        },

        Achievement {
            id: "stealth_master".to_string(),
            name: "Ghost in the Machine".to_string(),
            description: "Complete 20 challenges without being detected".to_string(),
            icon: "👻".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Epic,
            points: 150,
            criteria: AchievementCriteria::Custom("stealth_streak_20".to_string()),
            rewards: vec![
                AchievementReward::Title("Ghost".to_string()),
                AchievementReward::UnlockAbility("Invisibility Cloak".to_string()),
            ],
            hidden: false,
        },

        Achievement {
            id: "speed_demon".to_string(),
            name: "Speed Demon".to_string(),
            description: "Pwn a target in under 60 seconds".to_string(),
            icon: "⚡".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Rare,
            points: 100,
            criteria: AchievementCriteria::Custom("speed_pwn_60s".to_string()),
            rewards: vec![
                AchievementReward::Title("Speed Demon".to_string()),
                AchievementReward::XP(15000),
            ],
            hidden: false,
        },

        Achievement {
            id: "persistent_adversary".to_string(),
            name: "Persistent Adversary".to_string(),
            description: "Maintain persistence on a system for 30 days".to_string(),
            icon: "🔒".to_string(),
            category: AchievementCategory::Combat,
            rarity: AchievementRarity::Epic,
            points: 250,
            criteria: AchievementCriteria::Custom("persistence_30_days".to_string()),
            rewards: vec![
                AchievementReward::Title("Persistent Threat".to_string()),
                AchievementReward::XP(75000),
                AchievementReward::StreetCred(40),
            ],
            hidden: false,
        },
    ]
}

// ============================================================================
// EXPLORATION ACHIEVEMENTS
// ============================================================================

fn generate_exploration_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "cartographer".to_string(),
            name: "Cartographer".to_string(),
            description: "Scan 100 different networks".to_string(),
            icon: "🗺️".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Uncommon,
            points: 50,
            criteria: AchievementCriteria::Custom("scan_100_networks".to_string()),
            rewards: vec![
                AchievementReward::Title("Network Cartographer".to_string()),
                AchievementReward::XP(5000),
            ],
            hidden: false,
        },

        Achievement {
            id: "flag_collector".to_string(),
            name: "Flag Collector".to_string(),
            description: "Capture 100 CTF flags".to_string(),
            icon: "🚩".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Rare,
            points: 100,
            criteria: AchievementCriteria::FindFlags(100),
            rewards: vec![
                AchievementReward::Title("Flag Master".to_string()),
                AchievementReward::XP(20000),
                AchievementReward::SkillPoints(5),
            ],
            hidden: false,
        },

        Achievement {
            id: "root_of_all_evil".to_string(),
            name: "Root of All Evil".to_string(),
            description: "Gain root access on 50 different systems".to_string(),
            icon: "👑".to_string(),
            category: AchievementCategory::Exploration,
            rarity: AchievementRarity::Epic,
            points: 200,
            criteria: AchievementCriteria::Custom("root_50_systems".to_string()),
            rewards: vec![
                AchievementReward::Title("Root Collector".to_string()),
                AchievementReward::XP(50000),
                AchievementReward::StreetCred(25),
            ],
            hidden: false,
        },
    ]
}

// ============================================================================
// MASTERY ACHIEVEMENTS
// ============================================================================

fn generate_mastery_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "skill_apprentice".to_string(),
            name: "Skill Apprentice".to_string(),
            description: "Unlock 10 skills".to_string(),
            icon: "📖".to_string(),
            category: AchievementCategory::Mastery,
            rarity: AchievementRarity::Common,
            points: 25,
            criteria: AchievementCriteria::UnlockSkills(10),
            rewards: vec![
                AchievementReward::XP(2000),
            ],
            hidden: false,
        },

        Achievement {
            id: "skill_collector".to_string(),
            name: "Skill Collector".to_string(),
            description: "Unlock 50 skills".to_string(),
            icon: "📚".to_string(),
            category: AchievementCategory::Mastery,
            rarity: AchievementRarity::Rare,
            points: 100,
            criteria: AchievementCriteria::UnlockSkills(50),
            rewards: vec![
                AchievementReward::Title("Skill Collector".to_string()),
                AchievementReward::XP(25000),
                AchievementReward::SkillPoints(10),
            ],
            hidden: false,
        },

        Achievement {
            id: "master_of_all".to_string(),
            name: "Master of All Trades".to_string(),
            description: "Max out all skill trees".to_string(),
            icon: "🎨".to_string(),
            category: AchievementCategory::Mastery,
            rarity: AchievementRarity::Mythic,
            points: 2000,
            criteria: AchievementCriteria::Custom("max_all_trees".to_string()),
            rewards: vec![
                AchievementReward::Title("Omnipotent".to_string()),
                AchievementReward::XP(500000),
                AchievementReward::SkillPoints(100),
                AchievementReward::StreetCred(100),
                AchievementReward::Cosmetic(
                    CosmeticType::Theme,
                    "Mythic Rainbow Theme".to_string()
                ),
            ],
            hidden: false,
        },

        Achievement {
            id: "tool_master_nmap".to_string(),
            name: "Nmap Grandmaster".to_string(),
            description: "Complete 1000 nmap scans with perfect flags".to_string(),
            icon: "🔍".to_string(),
            category: AchievementCategory::Mastery,
            rarity: AchievementRarity::Epic,
            points: 150,
            criteria: AchievementCriteria::Custom("nmap_1000_perfect".to_string()),
            rewards: vec![
                AchievementReward::Title("Nmap Grandmaster".to_string()),
                AchievementReward::XP(30000),
            ],
            hidden: false,
        },

        Achievement {
            id: "metasploit_wizard".to_string(),
            name: "Metasploit Wizard".to_string(),
            description: "Successfully exploit 500 targets with Metasploit".to_string(),
            icon: "🧙".to_string(),
            category: AchievementCategory::Mastery,
            rarity: AchievementRarity::Legendary,
            points: 500,
            criteria: AchievementCriteria::Custom("metasploit_500".to_string()),
            rewards: vec![
                AchievementReward::Title("Metasploit Wizard".to_string()),
                AchievementReward::XP(100000),
                AchievementReward::StreetCred(50),
            ],
            hidden: false,
        },
    ]
}

// ============================================================================
// COLLECTION ACHIEVEMENTS
// ============================================================================

fn generate_collection_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "tool_collector".to_string(),
            name: "Tool Collector".to_string(),
            description: "Unlock access to 100 different tools".to_string(),
            icon: "🧰".to_string(),
            category: AchievementCategory::Collection,
            rarity: AchievementRarity::Rare,
            points: 100,
            criteria: AchievementCriteria::Custom("unlock_100_tools".to_string()),
            rewards: vec![
                AchievementReward::Title("Tool Master".to_string()),
                AchievementReward::XP(20000),
            ],
            hidden: false,
        },

        Achievement {
            id: "achievement_hunter".to_string(),
            name: "Achievement Hunter".to_string(),
            description: "Unlock 50 achievements".to_string(),
            icon: "🏆".to_string(),
            category: AchievementCategory::Collection,
            rarity: AchievementRarity::Epic,
            points: 200,
            criteria: AchievementCriteria::Custom("unlock_50_achievements".to_string()),
            rewards: vec![
                AchievementReward::Title("Achievement Hunter".to_string()),
                AchievementReward::XP(50000),
                AchievementReward::SkillPoints(15),
            ],
            hidden: false,
        },

        Achievement {
            id: "completionist".to_string(),
            name: "The Completionist".to_string(),
            description: "Unlock ALL achievements (except this one)".to_string(),
            icon: "💯".to_string(),
            category: AchievementCategory::Collection,
            rarity: AchievementRarity::Mythic,
            points: 5000,
            criteria: AchievementCriteria::Custom("unlock_all_achievements".to_string()),
            rewards: vec![
                AchievementReward::Title("THE COMPLETIONIST".to_string()),
                AchievementReward::XP(1000000),
                AchievementReward::SkillPoints(200),
                AchievementReward::StreetCred(100),
                AchievementReward::Cosmetic(
                    CosmeticType::Badge,
                    "Platinum Trophy".to_string()
                ),
            ],
            hidden: false,
        },
    ]
}

// ============================================================================
// REPUTATION ACHIEVEMENTS
// ============================================================================

fn generate_reputation_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "street_cred_50".to_string(),
            name: "Street Legend".to_string(),
            description: "Reach 50 street cred".to_string(),
            icon: "🌟".to_string(),
            category: AchievementCategory::Reputation,
            rarity: AchievementRarity::Rare,
            points: 100,
            criteria: AchievementCriteria::Custom("street_cred_50".to_string()),
            rewards: vec![
                AchievementReward::Title("Street Legend".to_string()),
                AchievementReward::XP(25000),
            ],
            hidden: false,
        },

        Achievement {
            id: "faction_exalted_red_team".to_string(),
            name: "Red Team Exalted".to_string(),
            description: "Reach Exalted reputation with Red Team faction".to_string(),
            icon: "🔴".to_string(),
            category: AchievementCategory::Reputation,
            rarity: AchievementRarity::Epic,
            points: 200,
            criteria: AchievementCriteria::MaxReputation("Red Team".to_string()),
            rewards: vec![
                AchievementReward::Title("Red Team Elite".to_string()),
                AchievementReward::XP(50000),
                AchievementReward::StreetCred(30),
            ],
            hidden: false,
        },
    ]
}

// ============================================================================
// LEGENDARY ACHIEVEMENTS (Ultra-Rare, Hidden)
// ============================================================================

fn generate_legendary_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "one_shot_one_kill".to_string(),
            name: "One Shot, One Kill".to_string(),
            description: "Pwn a target with a single perfectly-crafted exploit".to_string(),
            icon: "🎯".to_string(),
            category: AchievementCategory::Legendary,
            rarity: AchievementRarity::Legendary,
            points: 500,
            criteria: AchievementCriteria::Custom("one_shot_exploit".to_string()),
            rewards: vec![
                AchievementReward::Title("Sniper".to_string()),
                AchievementReward::XP(100000),
                AchievementReward::UnlockAbility("Perfect Shot".to_string()),
            ],
            hidden: true,
        },

        Achievement {
            id: "digital_god".to_string(),
            name: "Digital God".to_string(),
            description: "???".to_string(),
            icon: "🔱".to_string(),
            category: AchievementCategory::Legendary,
            rarity: AchievementRarity::Mythic,
            points: 10000,
            criteria: AchievementCriteria::Custom("unlock_god_mode_build".to_string()),
            rewards: vec![
                AchievementReward::Title("DIGITAL GOD".to_string()),
                AchievementReward::XP(9999999),
                AchievementReward::SkillPoints(999),
                AchievementReward::StreetCred(100),
                AchievementReward::Cosmetic(
                    CosmeticType::Theme,
                    "Godmode Golden Theme".to_string()
                ),
            ],
            hidden: true, // Secret achievement!
        },

        Achievement {
            id: "the_matrix".to_string(),
            name: "I Know Kung Fu".to_string(),
            description: "Download all skills instantly like Neo".to_string(),
            icon: "🥋".to_string(),
            category: AchievementCategory::Legendary,
            rarity: AchievementRarity::Mythic,
            points: 5000,
            criteria: AchievementCriteria::Custom("instant_skill_download".to_string()),
            rewards: vec![
                AchievementReward::Title("The One".to_string()),
                AchievementReward::SkillPoints(100),
            ],
            hidden: true,
        },
    ]
}

// ============================================================================
// SEASONAL ACHIEVEMENTS (Limited Time)
// ============================================================================

fn generate_seasonal_achievements() -> Vec<Achievement> {
    vec![
        Achievement {
            id: "halloween_2025".to_string(),
            name: "Trick or Pwn (Halloween 2025)".to_string(),
            description: "Complete Halloween special challenges".to_string(),
            icon: "🎃".to_string(),
            category: AchievementCategory::Seasonal,
            rarity: AchievementRarity::Epic,
            points: 300,
            criteria: AchievementCriteria::Custom("halloween_2025_complete".to_string()),
            rewards: vec![
                AchievementReward::Title("Pumpkin Pwner".to_string()),
                AchievementReward::Cosmetic(
                    CosmeticType::Theme,
                    "Spooky Orange Theme".to_string()
                ),
            ],
            hidden: false,
        },

        Achievement {
            id: "new_year_2026".to_string(),
            name: "New Year, New Exploits".to_string(),
            description: "Be active during New Year 2026 event".to_string(),
            icon: "🎆".to_string(),
            category: AchievementCategory::Seasonal,
            rarity: AchievementRarity::Rare,
            points: 150,
            criteria: AchievementCriteria::Custom("new_year_2026_active".to_string()),
            rewards: vec![
                AchievementReward::XP(50000),
                AchievementReward::Cosmetic(
                    CosmeticType::BootAnimation,
                    "Fireworks Boot".to_string()
                ),
            ],
            hidden: false,
        },
    ]
}
