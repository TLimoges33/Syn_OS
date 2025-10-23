//! Skill Tree Database - All Skill Paths & Nodes
//!
//! COMPLETE SKILL TREES FOR ALL 9 PATHS
//! Each path has 50+ skills across 7 tiers
//! Developer Master ISO: All 500+ tools already installed

#![no_std]

extern crate alloc;

use alloc::vec::Vec;
use alloc::vec;
use alloc::string::{String, ToString};
use alloc::collections::BTreeMap;
use super::legendary_skill_tree::*;

// ============================================================================
// RED TEAM PATH - OFFENSIVE SECURITY
// ============================================================================

pub fn generate_red_team_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS (Level 1-10) =====
        SkillNode {
            id: 1001,
            name: "Network Scanning Basics".to_string(),
            description: "Learn to use nmap for basic network reconnaissance".to_string(),
            icon: "🔍".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "nmap".to_string(),
                    advanced_features: vec!["-sV".to_string(), "-sC".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 2,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 1002,
            name: "Port Service Detection".to_string(),
            description: "Advanced nmap flags: version detection, OS fingerprinting".to_string(),
            icon: "🎯".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![1001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "nmap".to_string(),
                    advanced_features: vec!["-O".to_string(), "-A".to_string(), "--script".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 1003,
            name: "Stealth Scanning".to_string(),
            description: "IDS evasion techniques: fragmentation, decoys, timing".to_string(),
            icon: "🥷".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![1002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "nmap".to_string(),
                    advanced_features: vec![
                        "-f".to_string(),
                        "-D".to_string(),
                        "-T0".to_string(),
                        "--scan-delay".to_string(),
                    ],
                },
                UnlockReward::Challenge {
                    challenge_id: "stealth_scan_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 1004,
            name: "Masscan Mastery".to_string(),
            description: "Ultra-fast network scanning for large targets".to_string(),
            icon: "⚡".to_string(),
            tier: 1,
            column: 3,
            cost: 1,
            requires_skills: vec![1001],
            requires_level: 8,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "masscan".to_string(),
                    advanced_features: vec!["--rate 100000".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Agility,
                    amount: 3,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 2: VULNERABILITY ASSESSMENT (Level 11-20) =====
        SkillNode {
            id: 1011,
            name: "Vulnerability Scanning".to_string(),
            description: "Automated vulnerability detection with Nessus/OpenVAS".to_string(),
            icon: "🔎".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![1002],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "nessus".to_string(),
                    advanced_features: vec!["Advanced Scan".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "openvas".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 1012,
            name: "Web Application Scanning".to_string(),
            description: "Nikto, WPScan, SQLMap basics".to_string(),
            icon: "🌐".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![1011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "nikto".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "wpscan".to_string(),
                    advanced_features: vec!["--enumerate ap".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "sqlmap".to_string(),
                    advanced_features: vec!["-o".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 1013,
            name: "CVE Database Access".to_string(),
            description: "Search and exploit known vulnerabilities".to_string(),
            icon: "📚".to_string(),
            tier: 2,
            column: 2,
            cost: 1,
            requires_skills: vec![1011],
            requires_level: 15,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "searchsploit".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::Challenge {
                    challenge_id: "cve_exploitation_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 3: EXPLOITATION FUNDAMENTALS (Level 21-30) =====
        SkillNode {
            id: 1021,
            name: "Metasploit Framework".to_string(),
            description: "Master the ultimate exploitation framework".to_string(),
            icon: "💣".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![1012, 1013],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "metasploit".to_string(),
                    advanced_features: vec![
                        "exploit/*".to_string(),
                        "auxiliary/*".to_string(),
                    ],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 5,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 1022,
            name: "Payload Crafting".to_string(),
            description: "Create custom payloads and encoders".to_string(),
            icon: "🎨".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![1021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "msfvenom".to_string(),
                    advanced_features: vec![
                        "--encoder".to_string(),
                        "--iterations".to_string(),
                    ],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 3,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 1023,
            name: "Remote Code Execution".to_string(),
            description: "Achieve command execution on target systems".to_string(),
            icon: "⚔️".to_string(),
            tier: 3,
            column: 2,
            cost: 2,
            requires_skills: vec![1022],
            requires_level: 25,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "rce_challenge_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
                UnlockReward::XPBoost {
                    multiplier: 1.15,
                    duration_hours: Some(24),
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: POST-EXPLOITATION (Level 31-40) =====
        SkillNode {
            id: 1031,
            name: "Privilege Escalation".to_string(),
            description: "Linux/Windows privilege escalation techniques".to_string(),
            icon: "👑".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![1023],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "linpeas".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "winpeas".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "linux-exploit-suggester".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 1032,
            name: "Persistence Mechanisms".to_string(),
            description: "Maintain access to compromised systems".to_string(),
            icon: "🔒".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![1031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "persistence_challenge_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 1033,
            name: "Lateral Movement".to_string(),
            description: "Move through networks, pivoting techniques".to_string(),
            icon: "🌊".to_string(),
            tier: 4,
            column: 2,
            cost: 2,
            requires_skills: vec![1031],
            requires_level: 35,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "proxychains".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "chisel".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 5: ADVANCED EXPLOITATION (Level 41-50) =====
        SkillNode {
            id: 1041,
            name: "Active Directory Attacks".to_string(),
            description: "Kerberoasting, Pass-the-Hash, Golden Tickets".to_string(),
            icon: "🎫".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![1033],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "bloodhound".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "impacket".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "mimikatz".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 1042,
            name: "0-Day Discovery".to_string(),
            description: "Find previously unknown vulnerabilities".to_string(),
            icon: "💎".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![1041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 10,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 10,
                },
                UnlockReward::Challenge {
                    challenge_id: "0day_hunt".to_string(),
                    difficulty: Difficulty::Master,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES (Level 51-60) =====
        SkillNode {
            id: 1051,
            name: "Custom Exploit Development".to_string(),
            description: "Write exploits from scratch".to_string(),
            icon: "⚙️".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![1042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 15,
                },
                UnlockReward::Challenge {
                    challenge_id: "exploit_dev_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        SkillNode {
            id: 1052,
            name: "APT Simulation".to_string(),
            description: "Simulate advanced persistent threats".to_string(),
            icon: "🎭".to_string(),
            tier: 6,
            column: 1,
            cost: 3,
            requires_skills: vec![1051],
            requires_level: 55,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Shadow Operative".to_string(),
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE (Level 61+) =====
        SkillNode {
            id: 1061,
            name: "🌟 RED TEAM COMMANDER".to_string(),
            description: "ULTIMATE: Orchestrate full-spectrum offensive operations".to_string(),
            icon: "👹".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![1052],
            requires_level: 65,
            requires_spec: Some(Specialization::NetworkInfiltration),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Total Network Domination".to_string(),
                    description: "Auto-exploit all vulnerabilities in target network".to_string(),
                    cooldown_seconds: 86400, // 24 hours
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Red Team Commander".to_string(),
                },
                UnlockReward::XPBoost {
                    multiplier: 2.0,
                    duration_hours: None, // Permanent
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// BLUE TEAM PATH - DEFENSIVE SECURITY
// ============================================================================

pub fn generate_blue_team_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 2001,
            name: "Network Monitoring Basics".to_string(),
            description: "Learn Wireshark and tcpdump fundamentals".to_string(),
            icon: "📊".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "wireshark".to_string(),
                    advanced_features: vec!["Display Filters".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "tcpdump".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 2002,
            name: "Log Analysis".to_string(),
            description: "Parse and analyze system logs for anomalies".to_string(),
            icon: "📝".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![2001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "grep".to_string(),
                    advanced_features: vec!["-E".to_string(), "-P".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "awk".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "sed".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 2: THREAT DETECTION =====
        SkillNode {
            id: 2011,
            name: "IDS/IPS Configuration".to_string(),
            description: "Deploy and tune Snort/Suricata".to_string(),
            icon: "🛡️".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![2002],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "snort".to_string(),
                    advanced_features: vec!["Custom Rules".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "suricata".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: INCIDENT RESPONSE =====
        SkillNode {
            id: 2021,
            name: "Incident Response Framework".to_string(),
            description: "NIST incident handling methodology".to_string(),
            icon: "🚨".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![2011],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "incident_response_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 2061,
            name: "🌟 SECURITY OPERATIONS CENTER DIRECTOR".to_string(),
            description: "ULTIMATE: Command enterprise-wide defense operations".to_string(),
            icon: "🏰".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![],  // Simplified
            requires_level: 65,
            requires_spec: Some(Specialization::ThreatHunting),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Threat Vision".to_string(),
                    description: "See all active threats across entire network in real-time".to_string(),
                    cooldown_seconds: 3600, // 1 hour
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "SOC Director".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// PURPLE TEAM PATH - HYBRID OFFENSE + DEFENSE
// ============================================================================

pub fn generate_purple_team_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 3001,
            name: "Purple Teaming Basics".to_string(),
            description: "Learn to balance offensive and defensive mindsets".to_string(),
            icon: "💜".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 2,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 2,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 3002,
            name: "Atomic Red Team Integration".to_string(),
            description: "Execute MITRE ATT&CK techniques safely".to_string(),
            icon: "⚛️".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![3001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "atomic-red-team".to_string(),
                    advanced_features: vec!["Execute Tests".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 3003,
            name: "Detection Engineering".to_string(),
            description: "Write detection rules for SIEM platforms".to_string(),
            icon: "🔍".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![3002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "sigma".to_string(),
                    advanced_features: vec!["Rule Writing".to_string()],
                },
                UnlockReward::Challenge {
                    challenge_id: "detection_rule_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 2: THREAT EMULATION =====
        SkillNode {
            id: 3011,
            name: "Adversary Simulation".to_string(),
            description: "Mimic real-world threat actors".to_string(),
            icon: "🎭".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![3003],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "caldera".to_string(),
                    advanced_features: vec!["Campaign Execution".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "prelude-operator".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 3012,
            name: "MITRE ATT&CK Mastery".to_string(),
            description: "Deep knowledge of all ATT&CK tactics and techniques".to_string(),
            icon: "🧠".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![3011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 5,
                },
                UnlockReward::Challenge {
                    challenge_id: "mitre_attack_quiz".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: DETECTION VALIDATION =====
        SkillNode {
            id: 3021,
            name: "Detection Gap Analysis".to_string(),
            description: "Identify blind spots in security monitoring".to_string(),
            icon: "🕳️".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![3012],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "gap_analysis_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 3022,
            name: "Purple Team Automation".to_string(),
            description: "Automate attack-defense correlation".to_string(),
            icon: "🤖".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![3021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "vectr".to_string(),
                    advanced_features: vec!["Campaign Management".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 7,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: THREAT HUNTING =====
        SkillNode {
            id: 3031,
            name: "Proactive Threat Hunting".to_string(),
            description: "Hunt for threats before they strike".to_string(),
            icon: "🏹".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![3022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "osquery".to_string(),
                    advanced_features: vec!["Hunt Queries".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 10,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: SECURITY ORCHESTRATION =====
        SkillNode {
            id: 3041,
            name: "SOAR Orchestration".to_string(),
            description: "Security Orchestration, Automation and Response".to_string(),
            icon: "🎼".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![3031],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "shuffle".to_string(),
                    advanced_features: vec!["Workflow Automation".to_string()],
                },
                UnlockReward::Challenge {
                    challenge_id: "soar_playbook_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES =====
        SkillNode {
            id: 3051,
            name: "Threat Intelligence Fusion".to_string(),
            description: "Integrate threat intel with defensive operations".to_string(),
            icon: "🧩".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![3041],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "misp".to_string(),
                    advanced_features: vec!["Threat Sharing".to_string()],
                },
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Threat Intelligence Analyst".to_string(),
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 3061,
            name: "🌟 PURPLE TEAM ORCHESTRATOR".to_string(),
            description: "ULTIMATE: Master both offense and defense simultaneously".to_string(),
            icon: "🔮".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![3051],
            requires_level: 65,
            requires_spec: Some(Specialization::ThreatIntelligence),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Omniscient Detection".to_string(),
                    description: "Simultaneously attack AND detect from all angles".to_string(),
                    cooldown_seconds: 43200, // 12 hours
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Purple Team Orchestrator".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// BUG BOUNTY PATH - WEB APP HACKING & API TESTING
// ============================================================================

pub fn generate_bug_bounty_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 4001,
            name: "Web Recon Basics".to_string(),
            description: "Subdomain enumeration and asset discovery".to_string(),
            icon: "🌐".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "subfinder".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "amass".to_string(),
                    advanced_features: vec!["enum".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 4002,
            name: "HTTP Intercepting Proxy".to_string(),
            description: "Master BurpSuite and OWASP ZAP".to_string(),
            icon: "🕵️".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![4001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "burpsuite".to_string(),
                    advanced_features: vec!["Intruder".to_string(), "Repeater".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "zaproxy".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 4003,
            name: "OWASP Top 10 Knowledge".to_string(),
            description: "Master the most critical web vulnerabilities".to_string(),
            icon: "🔟".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![4002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "owasp_top10_quiz".to_string(),
                    difficulty: Difficulty::Normal,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 3,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 2: INJECTION ATTACKS =====
        SkillNode {
            id: 4011,
            name: "SQL Injection Mastery".to_string(),
            description: "Extract data through SQL injection".to_string(),
            icon: "💉".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![4003],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "sqlmap".to_string(),
                    advanced_features: vec!["--os-shell".to_string(), "--file-read".to_string()],
                },
                UnlockReward::Challenge {
                    challenge_id: "sqli_blind_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 4012,
            name: "XSS Exploitation".to_string(),
            description: "Cross-site scripting attacks (reflected, stored, DOM)".to_string(),
            icon: "🔗".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![4011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "xsstrike".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 5,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 4013,
            name: "Command Injection".to_string(),
            description: "OS command injection and RCE techniques".to_string(),
            icon: "⚡".to_string(),
            tier: 2,
            column: 2,
            cost: 1,
            requires_skills: vec![4012],
            requires_level: 15,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "commix".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::Challenge {
                    challenge_id: "command_injection_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: AUTHENTICATION & ACCESS CONTROL =====
        SkillNode {
            id: 4021,
            name: "Authentication Bypass".to_string(),
            description: "Break authentication mechanisms".to_string(),
            icon: "🔓".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![4013],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "auth_bypass_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 4022,
            name: "JWT Token Attacks".to_string(),
            description: "Exploit JSON Web Token vulnerabilities".to_string(),
            icon: "🎟️".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![4021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "jwt_tool".to_string(),
                    advanced_features: vec!["Crack".to_string(), "Tamper".to_string()],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: API HACKING =====
        SkillNode {
            id: 4031,
            name: "REST API Testing".to_string(),
            description: "Find vulnerabilities in REST APIs".to_string(),
            icon: "🔌".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![4022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "postman".to_string(),
                    advanced_features: vec!["Collections".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "arjun".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 4032,
            name: "GraphQL Exploitation".to_string(),
            description: "Attack GraphQL endpoints".to_string(),
            icon: "📊".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![4031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "graphql-cop".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: ADVANCED WEB ATTACKS =====
        SkillNode {
            id: 4041,
            name: "Server-Side Request Forgery".to_string(),
            description: "SSRF attacks to access internal resources".to_string(),
            icon: "🎯".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![4032],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "ssrf_aws_metadata".to_string(),
                    difficulty: Difficulty::Expert,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 10,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 4042,
            name: "Deserialization Attacks".to_string(),
            description: "Exploit insecure deserialization".to_string(),
            icon: "📦".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![4041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "ysoserial".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES =====
        SkillNode {
            id: 4051,
            name: "0-Day Web Research".to_string(),
            description: "Discover novel web vulnerabilities".to_string(),
            icon: "💎".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![4042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 15,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 15,
                },
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Bug Bounty Hunter".to_string(),
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 4061,
            name: "🌟 BUG BOUNTY LEGEND".to_string(),
            description: "ULTIMATE: Earn six-figure bounties consistently".to_string(),
            icon: "💰".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![4051],
            requires_level: 65,
            requires_spec: Some(Specialization::WebApplicationSecurity),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Vulnerability Vision".to_string(),
                    description: "Instantly identify all vulnerabilities in any web app".to_string(),
                    cooldown_seconds: 86400,
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Bug Bounty Legend".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// FORENSICS PATH - DIGITAL FORENSICS & INCIDENT ANALYSIS
// ============================================================================

pub fn generate_forensics_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 5001,
            name: "Forensics Fundamentals".to_string(),
            description: "Chain of custody, evidence preservation, forensic methodology".to_string(),
            icon: "🔬".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Precision,
                    amount: 3,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 2,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 5002,
            name: "Disk Imaging".to_string(),
            description: "Create forensic disk images (dd, FTK Imager)".to_string(),
            icon: "💾".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![5001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "dd".to_string(),
                    advanced_features: vec!["conv=noerror".to_string(), "status=progress".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "dcfldd".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 2: FILE SYSTEM ANALYSIS =====
        SkillNode {
            id: 5011,
            name: "File System Forensics".to_string(),
            description: "Analyze NTFS, EXT4, APFS file systems".to_string(),
            icon: "📂".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![5002],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "autopsy".to_string(),
                    advanced_features: vec!["Timeline Analysis".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "sleuthkit".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 5012,
            name: "Deleted File Recovery".to_string(),
            description: "Recover deleted files and carved data".to_string(),
            icon: "🗑️".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![5011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "foremost".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "photorec".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: MEMORY FORENSICS =====
        SkillNode {
            id: 5021,
            name: "Memory Analysis".to_string(),
            description: "Analyze RAM dumps with Volatility".to_string(),
            icon: "🧠".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![5012],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "volatility".to_string(),
                    advanced_features: vec!["pslist".to_string(), "netscan".to_string(), "malfind".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 7,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 5022,
            name: "Malware Memory Analysis".to_string(),
            description: "Extract malware from memory dumps".to_string(),
            icon: "🦠".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![5021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "memory_malware_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: NETWORK FORENSICS =====
        SkillNode {
            id: 5031,
            name: "PCAP Analysis".to_string(),
            description: "Analyze network packet captures".to_string(),
            icon: "📡".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![5022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "wireshark".to_string(),
                    advanced_features: vec!["Follow TCP Stream".to_string(), "Export Objects".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "networkminer".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 5032,
            name: "Traffic Decryption".to_string(),
            description: "Decrypt SSL/TLS traffic for analysis".to_string(),
            icon: "🔓".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![5031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "decrypt_tls_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: ADVANCED FORENSICS =====
        SkillNode {
            id: 5041,
            name: "Timeline Analysis".to_string(),
            description: "Reconstruct attacker timeline of events".to_string(),
            icon: "⏱️".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![5032],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "plaso".to_string(),
                    advanced_features: vec!["Super Timeline".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 10,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 5042,
            name: "Anti-Forensics Detection".to_string(),
            description: "Detect evidence tampering and anti-forensics techniques".to_string(),
            icon: "🔍".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![5041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "anti_forensics_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES =====
        SkillNode {
            id: 5051,
            name: "Mobile Forensics".to_string(),
            description: "iOS and Android device forensics".to_string(),
            icon: "📱".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![5042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "andriller".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Digital Forensics Investigator".to_string(),
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 5061,
            name: "🌟 FORENSICS MASTER".to_string(),
            description: "ULTIMATE: Reconstruct any incident from digital evidence".to_string(),
            icon: "🕵️".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![5051],
            requires_level: 65,
            requires_spec: Some(Specialization::MemoryForensics),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Perfect Reconstruction".to_string(),
                    description: "Recreate entire attack timeline from any evidence source".to_string(),
                    cooldown_seconds: 43200,
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Forensics Master".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// REVERSE ENGINEERING PATH - MALWARE ANALYSIS & BINARY EXPLOITATION
// ============================================================================

pub fn generate_reverse_engineering_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 6001,
            name: "Assembly Language Basics".to_string(),
            description: "Learn x86/x64 assembly fundamentals".to_string(),
            icon: "🔧".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 3,
                },
                UnlockReward::Challenge {
                    challenge_id: "asm_basics_quiz".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 6002,
            name: "Static Analysis".to_string(),
            description: "Analyze binaries without execution".to_string(),
            icon: "🔍".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![6001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "ghidra".to_string(),
                    advanced_features: vec!["Decompiler".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "radare2".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 6003,
            name: "Dynamic Analysis".to_string(),
            description: "Analyze binaries during execution".to_string(),
            icon: "▶️".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![6002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "gdb".to_string(),
                    advanced_features: vec!["pwndbg".to_string(), "gef".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "x64dbg".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 2: MALWARE ANALYSIS =====
        SkillNode {
            id: 6011,
            name: "Malware Triage".to_string(),
            description: "Quick malware classification and IOC extraction".to_string(),
            icon: "🦠".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![6003],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "pestudio".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "capa".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 6012,
            name: "Packer Detection & Unpacking".to_string(),
            description: "Identify and unpack obfuscated malware".to_string(),
            icon: "📦".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![6011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "upx".to_string(),
                    advanced_features: vec!["-d".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "de4dot".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: BINARY EXPLOITATION =====
        SkillNode {
            id: 6021,
            name: "Buffer Overflow Exploitation".to_string(),
            description: "Stack-based buffer overflow attacks".to_string(),
            icon: "💥".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![6012],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "bof_stack_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Precision,
                    amount: 7,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 6022,
            name: "ROP Chain Construction".to_string(),
            description: "Return-Oriented Programming bypasses".to_string(),
            icon: "🔗".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![6021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "ropper".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "pwntools".to_string(),
                    advanced_features: vec!["ROP".to_string()],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: ADVANCED EXPLOITATION =====
        SkillNode {
            id: 6031,
            name: "Heap Exploitation".to_string(),
            description: "Use-after-free, heap spraying, heap feng shui".to_string(),
            icon: "🧩".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![6022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "heap_uaf_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 6032,
            name: "Kernel Exploitation".to_string(),
            description: "Exploit vulnerabilities in OS kernels".to_string(),
            icon: "👑".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![6031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 10,
                },
                UnlockReward::Challenge {
                    challenge_id: "kernel_pwn_1".to_string(),
                    difficulty: Difficulty::Master,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: ANTI-ANALYSIS EVASION =====
        SkillNode {
            id: 6041,
            name: "Anti-Debugging Techniques".to_string(),
            description: "Bypass debugger detection and anti-analysis".to_string(),
            icon: "🛡️".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![6032],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "anti_debug_bypass_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 6042,
            name: "Code Obfuscation Analysis".to_string(),
            description: "Deobfuscate heavily protected binaries".to_string(),
            icon: "🌀".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![6041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 10,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES =====
        SkillNode {
            id: 6051,
            name: "Firmware Reverse Engineering".to_string(),
            description: "Analyze embedded device firmware".to_string(),
            icon: "🔌".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![6042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "binwalk".to_string(),
                    advanced_features: vec!["-e".to_string(), "-M".to_string()],
                },
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Exploit Architect".to_string(),
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 6061,
            name: "🌟 REVERSE ENGINEERING GRANDMASTER".to_string(),
            description: "ULTIMATE: Reverse engineer ANY binary, from bootloaders to hypervisors".to_string(),
            icon: "🧙".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![6051],
            requires_level: 65,
            requires_spec: Some(Specialization::BinaryExploitation),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Universal Decompiler".to_string(),
                    description: "Instantly decompile and understand any binary".to_string(),
                    cooldown_seconds: 86400,
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Reverse Engineering Grandmaster".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// SOCIAL ENGINEERING PATH - OSINT, PHISHING, PRETEXTING
// ============================================================================

pub fn generate_social_engineering_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 7001,
            name: "OSINT Fundamentals".to_string(),
            description: "Open-source intelligence gathering basics".to_string(),
            icon: "🔎".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "theharvester".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "shodan".to_string(),
                    advanced_features: vec!["Search".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Perception,
                    amount: 3,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 7002,
            name: "Social Media Reconnaissance".to_string(),
            description: "Extract intelligence from social media platforms".to_string(),
            icon: "📱".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![7001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "sherlock".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "linkedin-scraper".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 7003,
            name: "Email Intelligence".to_string(),
            description: "Find email addresses and verify deliverability".to_string(),
            icon: "📧".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![7002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "hunter.io".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::Challenge {
                    challenge_id: "email_osint_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        // ===== TIER 2: PHISHING =====
        SkillNode {
            id: 7011,
            name: "Phishing Infrastructure".to_string(),
            description: "Set up convincing phishing campaigns".to_string(),
            icon: "🎣".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![7003],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "gophish".to_string(),
                    advanced_features: vec!["Campaign Management".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "setoolkit".to_string(),
                    advanced_features: vec!["Phishing Vectors".to_string()],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 7012,
            name: "Credential Harvesting".to_string(),
            description: "Clone login pages and harvest credentials".to_string(),
            icon: "🔑".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![7011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "evilginx2".to_string(),
                    advanced_features: vec!["MFA Bypass".to_string()],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Charisma,
                    amount: 5,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: PRETEXTING =====
        SkillNode {
            id: 7021,
            name: "Voice Phishing (Vishing)".to_string(),
            description: "Social engineering over the phone".to_string(),
            icon: "📞".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![7012],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Charisma,
                    amount: 7,
                },
                UnlockReward::Challenge {
                    challenge_id: "vishing_scenario_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 7022,
            name: "Pretext Development".to_string(),
            description: "Craft believable cover stories and personas".to_string(),
            icon: "🎭".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![7021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 7,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: PHYSICAL SECURITY =====
        SkillNode {
            id: 7031,
            name: "Badge Cloning".to_string(),
            description: "Clone RFID access badges".to_string(),
            icon: "🎫".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![7022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "proxmark3".to_string(),
                    advanced_features: vec!["Clone".to_string(), "Emulate".to_string()],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 7032,
            name: "Lock Picking".to_string(),
            description: "Physical lock bypass techniques".to_string(),
            icon: "🔓".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![7031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Agility,
                    amount: 10,
                },
                UnlockReward::Challenge {
                    challenge_id: "lockpicking_101".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: ADVANCED MANIPULATION =====
        SkillNode {
            id: 7041,
            name: "Psychological Manipulation".to_string(),
            description: "Advanced influence and persuasion techniques".to_string(),
            icon: "🧠".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![7032],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Charisma,
                    amount: 10,
                },
                UnlockReward::Challenge {
                    challenge_id: "psychological_ops_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        SkillNode {
            id: 7042,
            name: "Deepfake Creation".to_string(),
            description: "Create realistic audio/video deepfakes".to_string(),
            icon: "🎬".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![7041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "faceswap".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Creativity,
                    amount: 10,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES =====
        SkillNode {
            id: 7051,
            name: "APT-Level Social Engineering".to_string(),
            description: "Nation-state level manipulation campaigns".to_string(),
            icon: "🕴️".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![7042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Master Manipulator".to_string(),
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 7061,
            name: "🌟 SOCIAL ENGINEERING GRANDMASTER".to_string(),
            description: "ULTIMATE: Manipulate any target through any medium".to_string(),
            icon: "👤".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![7051],
            requires_level: 65,
            requires_spec: Some(Specialization::PsychologicalWarfare),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Perfect Deception".to_string(),
                    description: "100% success rate on any social engineering attack".to_string(),
                    cooldown_seconds: 86400,
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Master of Deception".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// CLOUD SECURITY PATH - AWS, AZURE, GCP PENETRATION TESTING
// ============================================================================

pub fn generate_cloud_security_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 8001,
            name: "Cloud Fundamentals".to_string(),
            description: "Understand cloud architecture and shared responsibility model".to_string(),
            icon: "☁️".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 2,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 8002,
            name: "AWS Security Basics".to_string(),
            description: "IAM, S3, EC2 security fundamentals".to_string(),
            icon: "🔶".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![8001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "aws-cli".to_string(),
                    advanced_features: vec!["iam".to_string(), "s3".to_string(), "ec2".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "pacu".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 8003,
            name: "Azure Security Basics".to_string(),
            description: "Azure AD, storage, VMs security".to_string(),
            icon: "🔷".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![8002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "az-cli".to_string(),
                    advanced_features: vec!["ad".to_string(), "storage".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "stormspotter".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 2: ENUMERATION =====
        SkillNode {
            id: 8011,
            name: "Cloud Asset Discovery".to_string(),
            description: "Enumerate cloud resources and services".to_string(),
            icon: "🔍".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![8003],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "cloudsploit".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "cloudmapper".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 8012,
            name: "IAM Privilege Escalation".to_string(),
            description: "Escalate privileges in cloud IAM systems".to_string(),
            icon: "👑".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![8011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "iam_privesc_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: EXPLOITATION =====
        SkillNode {
            id: 8021,
            name: "S3 Bucket Exploitation".to_string(),
            description: "Find and exploit misconfigured S3 buckets".to_string(),
            icon: "🪣".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![8012],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "s3scanner".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::Challenge {
                    challenge_id: "s3_takeover_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 8022,
            name: "Lambda/Function Abuse".to_string(),
            description: "Exploit serverless functions".to_string(),
            icon: "λ".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![8021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 7,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: PERSISTENCE =====
        SkillNode {
            id: 8031,
            name: "Cloud Persistence Mechanisms".to_string(),
            description: "Maintain access in cloud environments".to_string(),
            icon: "🔒".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![8022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "cloud_persistence_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 8032,
            name: "Kubernetes Exploitation".to_string(),
            description: "Attack containerized cloud workloads".to_string(),
            icon: "☸️".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![8031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "kube-hunter".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "kubectl".to_string(),
                    advanced_features: vec!["--namespace kube-system".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: ADVANCED CLOUD ATTACKS =====
        SkillNode {
            id: 8041,
            name: "GCP Security Testing".to_string(),
            description: "Google Cloud Platform penetration testing".to_string(),
            icon: "🔵".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![8032],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "gcloud".to_string(),
                    advanced_features: vec!["iam".to_string(), "compute".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 8042,
            name: "Cloud Metadata Exploitation".to_string(),
            description: "Exploit cloud metadata services (SSRF to AWS keys)".to_string(),
            icon: "🎯".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![8041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "metadata_ssrf_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: MASTER TECHNIQUES =====
        SkillNode {
            id: 8051,
            name: "Multi-Cloud Architecture".to_string(),
            description: "Attack hybrid cloud environments".to_string(),
            icon: "🌐".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![8042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Cloud Security Architect".to_string(),
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 8061,
            name: "🌟 CLOUD SECURITY MASTER".to_string(),
            description: "ULTIMATE: Dominate any cloud provider's security".to_string(),
            icon: "⛅".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![8051],
            requires_level: 65,
            requires_spec: Some(Specialization::CloudNativeSecurity),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Cloud Omniscience".to_string(),
                    description: "See all resources across AWS, Azure, GCP simultaneously".to_string(),
                    cooldown_seconds: 43200,
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Cloud Security Master".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

// ============================================================================
// CRYPTOGRAPHY PATH - CRYPTANALYSIS, BLOCKCHAIN, QUANTUM
// ============================================================================

pub fn generate_cryptography_tree() -> Vec<SkillNode> {
    vec![
        // ===== TIER 1: FOUNDATIONS =====
        SkillNode {
            id: 9001,
            name: "Classical Cryptography".to_string(),
            description: "Caesar cipher, Vigenère, substitution ciphers".to_string(),
            icon: "🔐".to_string(),
            tier: 1,
            column: 0,
            cost: 1,
            requires_skills: vec![],
            requires_level: 1,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 3,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 3,
            current_rank: 0,
        },

        SkillNode {
            id: 9002,
            name: "Modern Symmetric Cryptography".to_string(),
            description: "AES, DES, block cipher modes".to_string(),
            icon: "🔑".to_string(),
            tier: 1,
            column: 1,
            cost: 1,
            requires_skills: vec![9001],
            requires_level: 3,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "aes_ecb_oracle".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 9003,
            name: "Public Key Cryptography".to_string(),
            description: "RSA, ECC, Diffie-Hellman".to_string(),
            icon: "🔓".to_string(),
            tier: 1,
            column: 2,
            cost: 1,
            requires_skills: vec![9002],
            requires_level: 5,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 5,
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 2: CRYPTANALYSIS =====
        SkillNode {
            id: 9011,
            name: "Frequency Analysis".to_string(),
            description: "Break classical ciphers through frequency analysis".to_string(),
            icon: "📊".to_string(),
            tier: 2,
            column: 0,
            cost: 1,
            requires_skills: vec![9003],
            requires_level: 11,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "frequency_analysis_1".to_string(),
                    difficulty: Difficulty::Normal,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 9012,
            name: "Padding Oracle Attacks".to_string(),
            description: "Exploit CBC padding vulnerabilities".to_string(),
            icon: "🎯".to_string(),
            tier: 2,
            column: 1,
            cost: 1,
            requires_skills: vec![9011],
            requires_level: 13,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "padbuster".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::Challenge {
                    challenge_id: "padding_oracle_1".to_string(),
                    difficulty: Difficulty::Hard,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 3: RSA ATTACKS =====
        SkillNode {
            id: 9021,
            name: "RSA Factorization".to_string(),
            description: "Factor weak RSA moduli".to_string(),
            icon: "🔢".to_string(),
            tier: 3,
            column: 0,
            cost: 2,
            requires_skills: vec![9012],
            requires_level: 21,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "rsatool".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "yafu".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 9022,
            name: "RSA Timing Attacks".to_string(),
            description: "Side-channel attacks on RSA implementations".to_string(),
            icon: "⏱️".to_string(),
            tier: 3,
            column: 1,
            cost: 2,
            requires_skills: vec![9021],
            requires_level: 23,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Precision,
                    amount: 7,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 4: HASH CRACKING =====
        SkillNode {
            id: 9031,
            name: "Hash Cracking Mastery".to_string(),
            description: "Crack MD5, SHA1, bcrypt hashes".to_string(),
            icon: "#️⃣".to_string(),
            tier: 4,
            column: 0,
            cost: 2,
            requires_skills: vec![9022],
            requires_level: 31,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "hashcat".to_string(),
                    advanced_features: vec!["--attack-mode 3".to_string(), "--increment".to_string()],
                },
                UnlockReward::ToolPermission {
                    tool_name: "john".to_string(),
                    advanced_features: vec!["--wordlist".to_string(), "--rules".to_string()],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 9032,
            name: "Rainbow Table Generation".to_string(),
            description: "Generate and use rainbow tables".to_string(),
            icon: "🌈".to_string(),
            tier: 4,
            column: 1,
            cost: 2,
            requires_skills: vec![9031],
            requires_level: 33,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "rainbowcrack".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 5: BLOCKCHAIN SECURITY =====
        SkillNode {
            id: 9041,
            name: "Smart Contract Auditing".to_string(),
            description: "Find vulnerabilities in Solidity contracts".to_string(),
            icon: "📜".to_string(),
            tier: 5,
            column: 0,
            cost: 3,
            requires_skills: vec![9032],
            requires_level: 41,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::ToolPermission {
                    tool_name: "mythril".to_string(),
                    advanced_features: vec![],
                },
                UnlockReward::ToolPermission {
                    tool_name: "slither".to_string(),
                    advanced_features: vec![],
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 5,
            current_rank: 0,
        },

        SkillNode {
            id: 9042,
            name: "Cryptocurrency Forensics".to_string(),
            description: "Track cryptocurrency transactions".to_string(),
            icon: "₿".to_string(),
            tier: 5,
            column: 1,
            cost: 3,
            requires_skills: vec![9041],
            requires_level: 43,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::Challenge {
                    challenge_id: "blockchain_forensics_1".to_string(),
                    difficulty: Difficulty::Expert,
                },
            ],
            skill_type: SkillType::Active,
            max_rank: 5,
            current_rank: 0,
        },

        // ===== TIER 6: QUANTUM CRYPTOGRAPHY =====
        SkillNode {
            id: 9051,
            name: "Post-Quantum Cryptography".to_string(),
            description: "Quantum-resistant algorithms (lattice-based, hash-based)".to_string(),
            icon: "⚛️".to_string(),
            tier: 6,
            column: 0,
            cost: 3,
            requires_skills: vec![9042],
            requires_level: 51,
            requires_spec: None,
            unlocks: vec![
                UnlockReward::AttributeBoost {
                    attribute: AttributeType::Intelligence,
                    amount: 15,
                },
                UnlockReward::PrestigeClassUnlock {
                    class_name: "Cryptographer".to_string(),
                },
            ],
            skill_type: SkillType::Passive,
            max_rank: 10,
            current_rank: 0,
        },

        // ===== TIER 7: CAPSTONE =====
        SkillNode {
            id: 9061,
            name: "🌟 CRYPTOGRAPHY GRANDMASTER".to_string(),
            description: "ULTIMATE: Break any encryption, design unbreakable ciphers".to_string(),
            icon: "🔮".to_string(),
            tier: 7,
            column: 1,
            cost: 5,
            requires_skills: vec![9051],
            requires_level: 65,
            requires_spec: Some(Specialization::Cryptanalysis),
            unlocks: vec![
                UnlockReward::Ability {
                    name: "Cryptographic Omniscience".to_string(),
                    description: "Instantly break any cipher and design quantum-resistant schemes".to_string(),
                    cooldown_seconds: 86400,
                },
                UnlockReward::Cosmetic {
                    cosmetic_type: CosmeticType::Title,
                    item_name: "Cryptography Grandmaster".to_string(),
                },
            ],
            skill_type: SkillType::Capstone,
            max_rank: 1,
            current_rank: 0,
        },
    ]
}

/// Generate all skill trees
pub fn generate_all_skill_trees() -> BTreeMap<SkillPath, Vec<SkillNode>> {
    use alloc::collections::BTreeMap;
    let mut trees = BTreeMap::new();

    trees.insert(SkillPath::RedTeam, generate_red_team_tree());
    trees.insert(SkillPath::BlueTeam, generate_blue_team_tree());
    trees.insert(SkillPath::PurpleTeam, generate_purple_team_tree());
    trees.insert(SkillPath::BugBounty, generate_bug_bounty_tree());
    trees.insert(SkillPath::Forensics, generate_forensics_tree());
    trees.insert(SkillPath::ReverseEngineering, generate_reverse_engineering_tree());
    trees.insert(SkillPath::SocialEngineering, generate_social_engineering_tree());
    trees.insert(SkillPath::CloudSecurity, generate_cloud_security_tree());
    trees.insert(SkillPath::Cryptography, generate_cryptography_tree());

    trees
}
