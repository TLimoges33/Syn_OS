//! Prestige Classes & Iconic Builds
//!
//! KOTOR-inspired Prestige Classes (unlock at level 60)
//! Cyberpunk 2077-inspired Iconic Builds (legendary synergies)

extern crate alloc;

use alloc::vec;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use super::legendary_skill_tree::*;

// ============================================================================
// PRESTIGE CLASSES - Advanced Specializations (Level 60+)
// ============================================================================

pub fn generate_all_prestige_classes() -> Vec<PrestigeClass> {
    vec![
        // ===== RED TEAM PRESTIGE CLASSES =====
        PrestigeClass {
            name: "Shadow Operative".to_string(),
            description: "Master of stealth and covert operations. APT-level capabilities.".to_string(),
            icon: "🥷".to_string(),
            requires_level: 60,
            requires_path: SkillPath::RedTeam,
            requires_alignment: Some(AlignmentTier::Dark),
            requires_achievements: vec![
                "complete_50_stealth_challenges".to_string(),
                "zero_detection_streak_20".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::ToolEffectiveness(1.5),  // 50% more effective
                PrestigeBonus::XPMultiplier(1.25),
                PrestigeBonus::SpecialAccess("Advanced Evasion Techniques".to_string()),
            ],
            signature_ability: SignatureAbility {
                name: "Ghost Protocol".to_string(),
                description: "Become completely undetectable for 10 minutes. All logs erased in real-time.".to_string(),
                cooldown_hours: 24,
                effect: AbilityEffect::TimeFreeze {
                    pause_all_scans: true,
                    duration_seconds: 600,
                },
            },
        },

        PrestigeClass {
            name: "Exploit Architect".to_string(),
            description: "Legendary exploit developer. Create weaponized 0-days.".to_string(),
            icon: "🏗️".to_string(),
            requires_level: 60,
            requires_path: SkillPath::RedTeam,
            requires_alignment: None, // Any alignment
            requires_achievements: vec![
                "develop_10_custom_exploits".to_string(),
                "discover_5_zero_days".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::AttributeBoost(AttributeType::Creativity, 25),
                PrestigeBonus::AttributeBoost(AttributeType::Intelligence, 25),
                PrestigeBonus::XPMultiplier(1.3),
            ],
            signature_ability: SignatureAbility {
                name: "Auto-Exploit Engine".to_string(),
                description: "Automatically craft exploits for any detected vulnerability.".to_string(),
                cooldown_hours: 48,
                effect: AbilityEffect::AutoExploit {
                    target_count: 10,
                    success_rate_boost: 0.9,  // 90% success rate
                },
            },
        },

        PrestigeClass {
            name: "Digital Phantom".to_string(),
            description: "Master of deception and misdirection. Leave no trace.".to_string(),
            icon: "👻".to_string(),
            requires_level: 60,
            requires_path: SkillPath::RedTeam,
            requires_alignment: Some(AlignmentTier::DarkMaster),
            requires_achievements: vec![
                "complete_apt_simulation".to_string(),
                "maintain_persistence_30_days".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::ToolEffectiveness(2.0),  // DOUBLE effectiveness
                PrestigeBonus::SpecialAccess("Rootkit Arsenal".to_string()),
            ],
            signature_ability: SignatureAbility {
                name: "Phantom Strike".to_string(),
                description: "Execute perfect attack chain: recon → exploit → persist → exfiltrate → vanish".to_string(),
                cooldown_hours: 72,
                effect: AbilityEffect::InstantAnalysis {
                    analyze_target_instantly: true,
                    generate_report: true,
                },
            },
        },

        // ===== BLUE TEAM PRESTIGE CLASSES =====
        PrestigeClass {
            name: "Threat Hunter Elite".to_string(),
            description: "Proactive threat detection specialist. Find threats before they strike.".to_string(),
            icon: "🎯".to_string(),
            requires_level: 60,
            requires_path: SkillPath::BlueTeam,
            requires_alignment: Some(AlignmentTier::Light),
            requires_achievements: vec![
                "detect_100_threats".to_string(),
                "zero_false_positives_streak_50".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::AttributeBoost(AttributeType::Perception, 30),
                PrestigeBonus::XPMultiplier(1.25),
            ],
            signature_ability: SignatureAbility {
                name: "Threat Vision".to_string(),
                description: "See ALL active threats across entire infrastructure in real-time for 1 hour.".to_string(),
                cooldown_hours: 12,
                effect: AbilityEffect::ThreatVision {
                    duration_minutes: 60,
                    reveal_hidden_vulns: true,
                },
            },
        },

        PrestigeClass {
            name: "Incident Commander".to_string(),
            description: "Master incident responder. Contain and neutralize any breach.".to_string(),
            icon: "🚨".to_string(),
            requires_level: 60,
            requires_path: SkillPath::BlueTeam,
            requires_alignment: Some(AlignmentTier::LightMaster),
            requires_achievements: vec![
                "respond_to_50_incidents".to_string(),
                "contain_breach_under_5_minutes".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::AttributeBoost(AttributeType::Agility, 25),
                PrestigeBonus::ToolEffectiveness(1.5),
            ],
            signature_ability: SignatureAbility {
                name: "Emergency Lockdown".to_string(),
                description: "Instantly isolate compromised systems and initiate automated remediation.".to_string(),
                cooldown_hours: 6,
                effect: AbilityEffect::InstantAnalysis {
                    analyze_target_instantly: true,
                    generate_report: true,
                },
            },
        },

        // ===== PURPLE TEAM PRESTIGE CLASS =====
        PrestigeClass {
            name: "Purple Phoenix".to_string(),
            description: "Ultimate hybrid warrior. Master both offense and defense.".to_string(),
            icon: "🟣".to_string(),
            requires_level: 60,
            requires_path: SkillPath::PurpleTeam,
            requires_alignment: Some(AlignmentTier::Neutral),
            requires_achievements: vec![
                "complete_purple_team_exercise_100".to_string(),
                "master_both_red_and_blue_paths".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::XPMultiplier(1.5),
                PrestigeBonus::ToolEffectiveness(1.75),
                PrestigeBonus::AttributeBoost(AttributeType::Intelligence, 20),
                PrestigeBonus::AttributeBoost(AttributeType::Perception, 20),
            ],
            signature_ability: SignatureAbility {
                name: "Perfect Storm".to_string(),
                description: "Execute simultaneous red team attack + blue team defense validation.".to_string(),
                cooldown_hours: 24,
                effect: AbilityEffect::AutoExploit {
                    target_count: 20,
                    success_rate_boost: 0.95,
                },
            },
        },

        // ===== FORENSICS PRESTIGE CLASS =====
        PrestigeClass {
            name: "Digital Archaeologist".to_string(),
            description: "Uncover the impossible. Recover deleted data, trace attackers.".to_string(),
            icon: "🔬".to_string(),
            requires_level: 60,
            requires_path: SkillPath::Forensics,
            requires_alignment: None,
            requires_achievements: vec![
                "complete_50_forensics_cases".to_string(),
                "recover_impossible_evidence".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::AttributeBoost(AttributeType::Perception, 35),
                PrestigeBonus::AttributeBoost(AttributeType::Precision, 25),
            ],
            signature_ability: SignatureAbility {
                name: "Time Machine".to_string(),
                description: "Reconstruct complete attack timeline from any artifact.".to_string(),
                cooldown_hours: 48,
                effect: AbilityEffect::InstantAnalysis {
                    analyze_target_instantly: true,
                    generate_report: true,
                },
            },
        },

        // ===== BUG BOUNTY PRESTIGE CLASS =====
        PrestigeClass {
            name: "Bounty Legend".to_string(),
            description: "Elite bug hunter. Six-figure bounties are your norm.".to_string(),
            icon: "💰".to_string(),
            requires_level: 60,
            requires_path: SkillPath::BugBounty,
            requires_alignment: None,
            requires_achievements: vec![
                "earn_1000000_bounty_points".to_string(),
                "critical_vulnerabilities_50".to_string(),
            ],
            passive_bonuses: vec![
                PrestigeBonus::XPMultiplier(2.0),  // DOUBLE XP!
                PrestigeBonus::AttributeBoost(AttributeType::Creativity, 30),
            ],
            signature_ability: SignatureAbility {
                name: "Vulnerability Radar".to_string(),
                description: "Instantly identify all vulnerabilities in target application.".to_string(),
                cooldown_hours: 24,
                effect: AbilityEffect::ThreatVision {
                    duration_minutes: 30,
                    reveal_hidden_vulns: true,
                },
            },
        },
    ]
}

// ============================================================================
// ICONIC BUILDS - Legendary Character Builds (Cyberpunk 2077 Style)
// ============================================================================

pub fn generate_all_iconic_builds() -> Vec<IconicBuild> {
    vec![
        // ===== THE GHOST =====
        IconicBuild {
            name: "The Ghost".to_string(),
            description: "Maximum stealth, zero detection. Leave no trace of your existence.".to_string(),
            icon: "👤".to_string(),
            required_skills: vec![
                1003, // Stealth Scanning
                1032, // Persistence Mechanisms
                1033, // Lateral Movement
                // ... more stealth-focused skills
            ],
            required_level: 50,
            required_prestige: Some("Shadow Operative".to_string()),
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Invisible Presence".to_string(),
                    description: "100% IDS/IPS evasion, logs automatically deleted".to_string(),
                    multiplier: 2.5,
                },
                SynergyBonus::UniqueAbility {
                    name: "Phase Shift".to_string(),
                    description: "Teleport through firewalls and network boundaries".to_string(),
                },
            ],
        },

        // ===== THE SPEEDRUNNER =====
        IconicBuild {
            name: "The Speedrunner".to_string(),
            description: "Lightning-fast exploitation. Pwn targets in seconds.".to_string(),
            icon: "⚡".to_string(),
            required_skills: vec![
                1004, // Masscan Mastery
                1022, // Payload Crafting
                1023, // Remote Code Execution
            ],
            required_level: 45,
            required_prestige: None,
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Hyperdrive".to_string(),
                    description: "All scans and exploits execute at 10x speed".to_string(),
                    multiplier: 10.0,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Agility,
                    new_value: 100,  // Maximum agility!
                },
            ],
        },

        // ===== THE FORTRESS =====
        IconicBuild {
            name: "The Fortress".to_string(),
            description: "Impenetrable defense. Nothing gets past you.".to_string(),
            icon: "🏰".to_string(),
            required_skills: vec![
                2011, // IDS/IPS Configuration
                2021, // Incident Response Framework
                // ... defensive skills
            ],
            required_level: 50,
            required_prestige: Some("Incident Commander".to_string()),
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Unbreakable Wall".to_string(),
                    description: "Block 99% of attacks automatically, instant incident response".to_string(),
                    multiplier: 3.0,
                },
            ],
        },

        // ===== THE NETRUNNER =====
        IconicBuild {
            name: "The Netrunner".to_string(),
            description: "Cyberpunk 2077's legendary netrunner. Control the digital realm.".to_string(),
            icon: "🧠".to_string(),
            required_skills: vec![
                1041, // Active Directory Attacks
                1042, // 0-Day Discovery
                1051, // Custom Exploit Development
            ],
            required_level: 60,
            required_prestige: Some("Exploit Architect".to_string()),
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Breach Protocol".to_string(),
                    description: "Upload daemons to target networks, remote neural control".to_string(),
                    multiplier: 5.0,
                },
                SynergyBonus::UniqueAbility {
                    name: "System Reset".to_string(),
                    description: "Crash any target system instantly (cooldown: 10min)".to_string(),
                },
                SynergyBonus::UniqueAbility {
                    name: "Memory Wipe".to_string(),
                    description: "Erase all traces of your actions from target".to_string(),
                },
            ],
        },

        // ===== THE COLLECTOR =====
        IconicBuild {
            name: "The Collector".to_string(),
            description: "Gotta catch 'em all! Master of all paths.".to_string(),
            icon: "🎨".to_string(),
            required_skills: vec![
                // Requires at least 10 skills from EACH path
            ],
            required_level: 80,
            required_prestige: None,
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Jack of All Trades, Master of All".to_string(),
                    description: "25% effectiveness boost to ALL tools and abilities".to_string(),
                    multiplier: 1.25,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Intelligence,
                    new_value: 100,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Perception,
                    new_value: 100,
                },
            ],
        },

        // ===== THE DARK LORD =====
        IconicBuild {
            name: "The Dark Lord".to_string(),
            description: "KOTOR Dark Side Master. Unlimited power!".to_string(),
            icon: "😈".to_string(),
            required_skills: vec![
                1052, // APT Simulation
                1061, // Red Team Commander (Capstone)
            ],
            required_level: 70,
            required_prestige: Some("Digital Phantom".to_string()),
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Unlimited Power".to_string(),
                    description: "All offensive abilities deal 200% damage, no cooldowns".to_string(),
                    multiplier: 3.0,
                },
                SynergyBonus::UniqueAbility {
                    name: "Force Lightning".to_string(),
                    description: "Instant system compromise on ANY target".to_string(),
                },
            ],
        },

        // ===== THE JEDI MASTER =====
        IconicBuild {
            name: "The Jedi Master".to_string(),
            description: "KOTOR Light Side Master. Defender of the innocent.".to_string(),
            icon: "⭐".to_string(),
            required_skills: vec![
                2061, // SOC Director (Capstone)
            ],
            required_level: 70,
            required_prestige: Some("Threat Hunter Elite".to_string()),
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Force Sense".to_string(),
                    description: "Predict attacks before they happen, auto-block all threats".to_string(),
                    multiplier: 3.0,
                },
                SynergyBonus::UniqueAbility {
                    name: "Force Heal".to_string(),
                    description: "Automatically remediate all vulnerabilities".to_string(),
                },
            ],
        },

        // ===== THE GOD MODE =====
        IconicBuild {
            name: "The God Mode".to_string(),
            description: "LEGENDARY: Unlock ALL skills, prestige classes, and abilities.".to_string(),
            icon: "🔱".to_string(),
            required_skills: vec![
                // Requires EVERY skill in the game unlocked
            ],
            required_level: 100,
            required_prestige: None, // Can have any prestige
            synergy_bonuses: vec![
                SynergyBonus::SetBonus {
                    name: "Omnipotence".to_string(),
                    description: "INFINITE XP, ALL abilities unlocked, NO cooldowns".to_string(),
                    multiplier: 999.0,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Intelligence,
                    new_value: 9999,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Agility,
                    new_value: 9999,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Perception,
                    new_value: 9999,
                },
                SynergyBonus::StatOverride {
                    attribute: AttributeType::Creativity,
                    new_value: 9999,
                },
                SynergyBonus::UniqueAbility {
                    name: "Reality Control".to_string(),
                    description: "Bend the digital realm to your will. You ARE the system.".to_string(),
                },
            ],
        },
    ]
}
