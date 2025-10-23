//! Real-time Hint System - V1.7 "AI Tutor & Skill Tree"
//!
//! Provides contextual, progressive hints based on user progress and
//! time spent on challenges. Implements the Zone of Proximal Development (ZPD)
//! by providing just enough help to keep users learning.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use super::adaptive_difficulty::{Challenge, ChallengeCategory};
use super::learning_style_detector::LearningStyle;

// ============================================================================
// HINT TYPES
// ============================================================================

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum HintLevel {
    /// Gentle nudge in the right direction
    Nudge = 1,
    /// More specific guidance
    Guide = 2,
    /// Detailed step-by-step
    Detailed = 3,
    /// Full solution walkthrough
    Solution = 4,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hint {
    pub level: HintLevel,
    pub content: String,
    pub learning_style_variant: Option<String>, // Adapted for visual/auditory/etc
    pub next_steps: Vec<String>,
    pub related_concepts: Vec<String>,
    pub estimated_time_saving: u64, // seconds
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChallengeContext {
    pub challenge_id: String,
    pub challenge_category: ChallengeCategory,
    pub difficulty: f32,
    pub time_started: chrono::DateTime<chrono::Utc>,
    pub time_stuck: u64, // seconds user has been stuck
    pub hints_used: Vec<HintLevel>,
    pub current_step: Option<String>,
    pub user_actions: Vec<String>, // What the user has tried
}

// ============================================================================
// HINT SYSTEM
// ============================================================================

pub struct HintSystem {
    hint_database: HashMap<String, Vec<Hint>>,
    learning_style: Option<LearningStyle>,
}

impl HintSystem {
    pub fn new() -> Self {
        Self {
            hint_database: Self::build_hint_database(),
            learning_style: None,
        }
    }

    pub fn set_learning_style(&mut self, style: LearningStyle) {
        self.learning_style = Some(style);
    }

    /// Provide contextual hint based on challenge context
    pub fn provide_hint(&self, context: &ChallengeContext) -> Hint {
        let hint_level = self.determine_hint_level(context);

        // Get hints for this challenge
        let hints = self.hint_database.get(&context.challenge_id)
            .or_else(|| {
                // Fallback to category-based hints
                let category_key = format!("{:?}", context.challenge_category);
                self.hint_database.get(&category_key)
            });

        if let Some(hint_list) = hints {
            // Find appropriate hint for level
            let mut hint = hint_list.iter()
                .find(|h| h.level == hint_level)
                .cloned()
                .unwrap_or_else(|| {
                    // Fallback to first hint
                    hint_list.first().cloned().unwrap_or_else(|| {
                        Hint {
                            level: HintLevel::Nudge,
                            content: "Keep trying! You're on the right track.".to_string(),
                            learning_style_variant: None,
                            next_steps: vec![],
                            related_concepts: vec![],
                            estimated_time_saving: 300,
                        }
                    })
                });

            // Adapt hint to learning style
            if let Some(style) = &self.learning_style {
                hint = self.adapt_hint_to_learning_style(hint, style);
            }

            hint
        } else {
            // Generate generic hint
            self.generate_generic_hint(context, hint_level)
        }
    }

    fn determine_hint_level(&self, context: &ChallengeContext) -> HintLevel {
        let time_stuck = context.time_stuck;
        let hints_used_count = context.hints_used.len();

        // Progressive hint levels based on time and previous hints
        match (time_stuck, hints_used_count) {
            (0..=300, _) => HintLevel::Nudge,      // 0-5 minutes
            (301..=900, 0) => HintLevel::Nudge,    // 5-15 min, no hints yet
            (301..=900, _) => HintLevel::Guide,    // 5-15 min, seen nudges
            (901..=1800, _) if hints_used_count < 2 => HintLevel::Guide,   // 15-30 min
            (901..=1800, _) => HintLevel::Detailed, // 15-30 min, seen multiple hints
            (1801.., _) if hints_used_count < 3 => HintLevel::Detailed,
            (1801.., _) => HintLevel::Solution,    // 30+ min, show solution
            _ => HintLevel::Nudge,
        }
    }

    fn adapt_hint_to_learning_style(&self, mut hint: Hint, style: &LearningStyle) -> Hint {
        match style {
            LearningStyle::Visual => {
                // Add ASCII diagrams, visual representations
                hint.learning_style_variant = Some(format!(
                    "{}\n\n📊 Visual Breakdown:\n{}",
                    hint.content,
                    "   [Network] -> [Scanner] -> [Results]"
                ));
            }
            LearningStyle::Auditory => {
                // Add "read this aloud" suggestions
                hint.learning_style_variant = Some(format!(
                    "🔊 Read this aloud:\n{}",
                    hint.content
                ));
            }
            LearningStyle::Kinesthetic => {
                // Emphasize hands-on steps
                hint.learning_style_variant = Some(format!(
                    "🖐️ Try this now:\n{}",
                    hint.content
                ));
            }
            LearningStyle::Reading => {
                // Add detailed written explanation
                hint.learning_style_variant = Some(format!(
                    "📖 Detailed explanation:\n{}",
                    hint.content
                ));
            }
            LearningStyle::Multimodal => {
                // Keep original, it's already multi-modal
                hint.learning_style_variant = Some(hint.content.clone());
            }
        }

        hint
    }

    fn generate_generic_hint(&self, context: &ChallengeContext, level: HintLevel) -> Hint {
        let content = match level {
            HintLevel::Nudge => {
                format!(
                    "💡 Think about what you're trying to discover in this {} challenge. What tool is commonly used for this?",
                    format!("{:?}", context.challenge_category).to_lowercase()
                )
            }
            HintLevel::Guide => {
                format!(
                    "🎯 For {} challenges, you typically want to:\n1. Identify your target\n2. Choose the right tool\n3. Analyze the results",
                    format!("{:?}", context.challenge_category).to_lowercase()
                )
            }
            HintLevel::Detailed => {
                "🔍 Here's a step-by-step approach:\n1. Read the challenge description carefully\n2. Check the man page for the suggested tool\n3. Start with basic flags before advanced options\n4. Document your findings".to_string()
            }
            HintLevel::Solution => {
                "📝 It seems you're stuck. Would you like to see the full solution? (This will reduce XP gain but help you learn)".to_string()
            }
        };

        Hint {
            level,
            content,
            learning_style_variant: None,
            next_steps: vec![
                "Try the command and observe output".to_string(),
                "Research any errors you encounter".to_string(),
            ],
            related_concepts: vec![],
            estimated_time_saving: match level {
                HintLevel::Nudge => 300,
                HintLevel::Guide => 600,
                HintLevel::Detailed => 900,
                HintLevel::Solution => 1800,
            },
        }
    }

    fn build_hint_database() -> HashMap<String, Vec<Hint>> {
        let mut db = HashMap::new();

        // Reconnaissance hints
        db.insert("recon-001".to_string(), vec![
            Hint {
                level: HintLevel::Nudge,
                content: "💡 Have you considered using nmap for network discovery?".to_string(),
                learning_style_variant: None,
                next_steps: vec![
                    "Check nmap's help: nmap -h".to_string(),
                    "Look for host discovery options".to_string(),
                ],
                related_concepts: vec![
                    "ARP scanning".to_string(),
                    "ICMP echo requests".to_string(),
                ],
                estimated_time_saving: 300,
            },
            Hint {
                level: HintLevel::Guide,
                content: "🎯 Try using nmap with the -sn flag for ping sweeps. The syntax is:\nnmap -sn <network_range>".to_string(),
                learning_style_variant: None,
                next_steps: vec![
                    "Determine the network range (e.g., 192.168.1.0/24)".to_string(),
                    "Run the scan and observe live hosts".to_string(),
                ],
                related_concepts: vec![
                    "CIDR notation".to_string(),
                    "Network subnetting".to_string(),
                ],
                estimated_time_saving: 600,
            },
            Hint {
                level: HintLevel::Detailed,
                content: "🔍 Step-by-step solution:\n1. Find your network range: ip addr show\n2. Run host discovery: nmap -sn 192.168.1.0/24\n3. Note all live hosts in the output".to_string(),
                learning_style_variant: None,
                next_steps: vec![
                    "Document discovered hosts".to_string(),
                    "Proceed to port scanning".to_string(),
                ],
                related_concepts: vec![
                    "Subnet masks".to_string(),
                    "Network addressing".to_string(),
                ],
                estimated_time_saving: 900,
            },
            Hint {
                level: HintLevel::Solution,
                content: "📝 Full solution:\n```bash\n# Discover your network\nip addr show | grep inet\n\n# Scan for live hosts\nnmap -sn 192.168.1.0/24\n\n# Output will show:\nHost is up (0.00050s latency).\nMAC Address: XX:XX:XX:XX:XX:XX\n```".to_string(),
                learning_style_variant: None,
                next_steps: vec![
                    "Review the nmap output".to_string(),
                    "Understand each field".to_string(),
                ],
                related_concepts: vec![
                    "MAC addresses".to_string(),
                    "Latency measurement".to_string(),
                ],
                estimated_time_saving: 1800,
            },
        ]);

        // Port scanning hints
        db.insert("scan-001".to_string(), vec![
            Hint {
                level: HintLevel::Nudge,
                content: "💡 Think about what information you need: which ports are open and what services are running?".to_string(),
                learning_style_variant: None,
                next_steps: vec![
                    "Consider using nmap again".to_string(),
                    "Look for service detection flags".to_string(),
                ],
                related_concepts: vec!["Port numbers".to_string(), "Service banners".to_string()],
                estimated_time_saving: 300,
            },
            Hint {
                level: HintLevel::Guide,
                content: "🎯 Use nmap with -sV for version detection. Common syntax:\nnmap -sV -p- <target_ip>".to_string(),
                learning_style_variant: None,
                next_steps: vec![
                    "Choose your target from recon".to_string(),
                    "Scan all ports or specific ranges".to_string(),
                ],
                related_concepts: vec!["TCP/UDP ports".to_string(), "Service fingerprinting".to_string()],
                estimated_time_saving: 600,
            },
        ]);

        // Generic category hints
        let categories = vec![
            ("Reconnaissance", "Think about gathering information without direct interaction"),
            ("Scanning", "Focus on identifying open services and ports"),
            ("Enumeration", "Extract detailed information from discovered services"),
            ("Exploitation", "Look for known vulnerabilities in the enumerated services"),
        ];

        for (category, nudge) in categories {
            db.insert(category.to_string(), vec![
                Hint {
                    level: HintLevel::Nudge,
                    content: format!("💡 {}", nudge),
                    learning_style_variant: None,
                    next_steps: vec![],
                    related_concepts: vec![],
                    estimated_time_saving: 300,
                },
            ]);
        }

        db
    }

    /// Check if user should get a hint (time-based)
    pub fn should_offer_hint(&self, context: &ChallengeContext) -> bool {
        // Offer hint at intervals: 5 min, 10 min, 15 min, 20 min
        let hint_intervals = vec![300, 600, 900, 1200, 1800];
        let hints_seen = context.hints_used.len();

        if hints_seen < hint_intervals.len() {
            context.time_stuck >= hint_intervals[hints_seen]
        } else {
            false
        }
    }

    /// Get hint for a specific challenge and level
    pub fn get_hint(&self, challenge_id: &str, level: HintLevel) -> Option<Hint> {
        self.hint_database.get(challenge_id)
            .and_then(|hints| hints.iter().find(|h| h.level == level).cloned())
    }
}

impl Default for HintSystem {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// HINT FORMATTER
// ============================================================================

pub struct HintFormatter;

impl HintFormatter {
    pub fn format_hint(hint: &Hint) -> String {
        let icon = match hint.level {
            HintLevel::Nudge => "💡",
            HintLevel::Guide => "🎯",
            HintLevel::Detailed => "🔍",
            HintLevel::Solution => "📝",
        };

        let mut output = format!("{} {} HINT\n", icon, format!("{:?}", hint.level).to_uppercase());
        output.push_str(&"-".repeat(50));
        output.push('\n');

        // Main content (learning style adapted if available)
        if let Some(variant) = &hint.learning_style_variant {
            output.push_str(variant);
        } else {
            output.push_str(&hint.content);
        }

        // Next steps
        if !hint.next_steps.is_empty() {
            output.push_str("\n\n📋 Next Steps:\n");
            for (i, step) in hint.next_steps.iter().enumerate() {
                output.push_str(&format!("   {}. {}\n", i + 1, step));
            }
        }

        // Related concepts
        if !hint.related_concepts.is_empty() {
            output.push_str("\n🔗 Related Concepts:\n");
            for concept in &hint.related_concepts {
                output.push_str(&format!("   • {}\n", concept));
            }
        }

        // Time saving estimate
        output.push_str(&format!(
            "\n⏱️  This hint could save you approximately {} minutes\n",
            hint.estimated_time_saving / 60
        ));

        output.push_str(&"-".repeat(50));
        output
    }

    pub fn format_hint_offer(context: &ChallengeContext) -> String {
        format!(
            "🤔 You've been working on this challenge for {} minutes. Would you like a hint? (y/n)",
            context.time_stuck / 60
        )
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hint_level_progression() {
        let context = ChallengeContext {
            challenge_id: "test-001".to_string(),
            challenge_category: ChallengeCategory::Reconnaissance,
            difficulty: 1.0,
            time_started: chrono::Utc::now(),
            time_stuck: 0,
            hints_used: vec![],
            current_step: None,
            user_actions: vec![],
        };

        let hint_system = HintSystem::new();

        // Early on: Nudge
        let mut ctx = context.clone();
        ctx.time_stuck = 200;
        let level = hint_system.determine_hint_level(&ctx);
        assert_eq!(level, HintLevel::Nudge);

        // After 10 min: Guide
        ctx.time_stuck = 700;
        ctx.hints_used.push(HintLevel::Nudge);
        let level = hint_system.determine_hint_level(&ctx);
        assert_eq!(level, HintLevel::Guide);

        // After 20 min: Detailed
        ctx.time_stuck = 1200;
        ctx.hints_used.push(HintLevel::Guide);
        let level = hint_system.determine_hint_level(&ctx);
        assert_eq!(level, HintLevel::Detailed);

        // After 30+ min: Solution
        ctx.time_stuck = 2000;
        ctx.hints_used.push(HintLevel::Detailed);
        let level = hint_system.determine_hint_level(&ctx);
        assert_eq!(level, HintLevel::Solution);
    }

    #[test]
    fn test_hint_database_contains_recon() {
        let hint_system = HintSystem::new();
        let hint = hint_system.get_hint("recon-001", HintLevel::Nudge);
        assert!(hint.is_some());
        assert!(hint.unwrap().content.contains("nmap"));
    }

    #[test]
    fn test_should_offer_hint_timing() {
        let mut context = ChallengeContext {
            challenge_id: "test-001".to_string(),
            challenge_category: ChallengeCategory::Scanning,
            difficulty: 2.0,
            time_started: chrono::Utc::now(),
            time_stuck: 0,
            hints_used: vec![],
            current_step: None,
            user_actions: vec![],
        };

        let hint_system = HintSystem::new();

        // Too early
        context.time_stuck = 100;
        assert!(!hint_system.should_offer_hint(&context));

        // Just right for first hint (5 min)
        context.time_stuck = 350;
        assert!(hint_system.should_offer_hint(&context));

        // After taking first hint
        context.hints_used.push(HintLevel::Nudge);
        context.time_stuck = 650;
        assert!(hint_system.should_offer_hint(&context));
    }
}
