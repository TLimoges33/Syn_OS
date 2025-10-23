//! SynOS Gamification System
//!
//! WoW/KOTOR/Cyberpunk-inspired skill tree system for cybersecurity education.
//!
//! # Features
//! - 9 complete skill paths (Red Team, Blue Team, Purple Team, etc.)
//! - 450+ skills across 7 tiers per path
//! - 12 prestige classes (unlock at level 60)
//! - 7 iconic builds (legendary synergies)
//! - 200+ achievements across 7 categories
//! - Alignment system (-100 Dark to +100 Light)
//! - Street cred reputation (0-100)
//! - Tool permission progression system

#![no_std]

extern crate alloc;

pub mod legendary_skill_tree;
pub mod skill_tree_database;
pub mod prestige_and_iconic;
pub mod achievements_database;

// Re-export commonly used types
pub use legendary_skill_tree::{
    LegendarySkillTree,
    CharacterProfile,
    SkillPath,
    Specialization,
    SkillNode,
    UnlockReward,
    Alignment,
    AlignmentTier,
    Attributes,
    AttributeType,
    StatusEffect,
};

pub use skill_tree_database::generate_all_skill_trees;

pub use prestige_and_iconic::{
    PrestigeClass,
    IconicBuild,
    SignatureAbility,
    SynergyBonus,
};

pub use achievements_database::{
    Achievement,
    AchievementCategory,
    AchievementRarity,
    AchievementCriteria,
    AchievementReward,
};

/// Initialize the gamification system for a new user
pub fn initialize_new_character(username: &str) -> LegendarySkillTree {
    LegendarySkillTree::new(username)
}

/// Load character progress from persistent storage
pub fn load_character(username: &str) -> Result<LegendarySkillTree, &'static str> {
    // TODO: Implement persistence layer
    // For now, return new character
    Ok(LegendarySkillTree::new(username))
}

/// Save character progress to persistent storage
pub fn save_character(tree: &LegendarySkillTree) -> Result<(), &'static str> {
    // TODO: Implement persistence layer
    Ok(())
}
