//! Legendary Skill Tree System - V1.5 "Educational Gamification"
//!
//! Inspired by:
//! - World of Warcraft: Talent trees, specializations, mastery
//! - KOTOR 1/2: Force powers, prestige classes, alignment
//! - Cyberpunk 2077: Netrunner perks, street cred, iconic builds
//!
//! Developer Master ISO: All tools installed, skills unlock PERMISSIONS & FEATURES

extern crate alloc;

use alloc::vec::Vec;
use alloc::vec;
use alloc::format;
use alloc::string::{String, ToString};
use alloc::collections::BTreeMap;

// ============================================================================
// SKILL TREE ARCHITECTURE
// ============================================================================

/// Main skill tree system (like WoW talent trees)
pub struct LegendarySkillTree {
    /// Character/User profile
    character: CharacterProfile,

    /// All available skill trees (3 specializations per path)
    trees: BTreeMap<SkillPath, Vec<SkillNode>>,

    /// Mastery system (endgame progression)
    mastery: MasterySystem,

    /// Prestige classes (KOTOR-style advanced classes)
    prestige_classes: Vec<PrestigeClass>,

    /// Reputation factions (gain street cred)
    factions: Vec<Faction>,

    /// Achievement engine
    achievements: AchievementEngine,

    /// Iconic builds (Cyberpunk-style legendary builds)
    iconic_builds: Vec<IconicBuild>,
}

/// Character profile (like WoW character sheet)
#[derive(Debug, Clone)]
pub struct CharacterProfile {
    pub username: String,
    pub level: u32,               // 1-100
    pub total_xp: u64,
    pub unspent_skill_points: u32,

    /// Current specialization path
    pub active_path: Option<SkillPath>,
    pub active_spec: Option<Specialization>,

    /// Prestige class (unlocked at level 60)
    pub prestige_class: Option<PrestigeClass>,

    /// Alignment (Light/Dark side - KOTOR inspired)
    pub alignment: Alignment,

    /// Street cred (reputation level)
    pub street_cred: u32,         // 0-100

    /// Attributes (base stats)
    pub attributes: Attributes,

    /// Learned skills
    pub learned_skills: Vec<SkillId>,

    /// Active buffs/debuffs
    pub active_effects: Vec<StatusEffect>,

    /// Equipped title
    pub title: Option<String>,

    /// Total playtime (hours)
    pub playtime_hours: f32,
}

/// Primary skill paths (like WoW class specializations)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum SkillPath {
    /// Red Team Path: Offensive security, penetration testing
    RedTeam,

    /// Blue Team Path: Defensive security, monitoring
    BlueTeam,

    /// Purple Team Path: Hybrid offensive + defensive
    PurpleTeam,

    /// Bug Bounty Path: Web app hacking, automation
    BugBounty,

    /// Forensics Path: Digital investigation, memory analysis
    Forensics,

    /// Reverse Engineering Path: Malware analysis, binary exploitation
    ReverseEngineering,

    /// Social Engineering Path: OSINT, phishing, psychological manipulation
    SocialEngineering,

    /// Cloud Security Path: AWS/Azure/GCP security
    CloudSecurity,

    /// Cryptography Path: Encryption, code breaking
    Cryptography,
}

/// Specializations within each path (3 per path, like WoW)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Specialization {
    // Red Team Specs
    NetworkInfiltration,    // Focus: Network penetration
    ApplicationExploitation, // Focus: Web/app vulnerabilities
    PhysicalBreaching,      // Focus: Physical security, lock picking

    // Blue Team Specs
    ThreatHunting,          // Focus: Proactive threat detection
    IncidentResponse,       // Focus: Rapid incident handling
    SecurityArchitecture,   // Focus: Defense design, hardening

    // Purple Team Specs
    AttackSimulation,       // Focus: Red team tactics for blue team
    DefenseValidation,      // Focus: Testing defensive controls
    ThreatIntelligence,     // Focus: CTI, IOC analysis

    // Bug Bounty Specs
    WebApplicationHacking,  // Focus: OWASP Top 10, SQL injection
    WebApplicationSecurity, // Focus: Security assessment & defense
    APISecurityTesting,     // Focus: REST/GraphQL API exploitation
    MobileAppTesting,       // Focus: iOS/Android security

    // Forensics Specs
    MemoryForensics,        // Focus: RAM analysis, Volatility
    DiskForensics,          // Focus: File system analysis
    NetworkForensics,       // Focus: PCAP analysis, network traces

    // Reverse Engineering Specs
    MalwareAnalysis,        // Focus: Dissecting malware
    BinaryExploitation,     // Focus: Buffer overflows, ROP chains
    FirmwareReversing,      // Focus: IoT/embedded device analysis

    // Social Engineering Specs
    OSINTMastery,           // Focus: Open source intelligence
    PhishingOperations,     // Focus: Email/SMS phishing campaigns
    PretextingElicitation,  // Focus: Social manipulation
    PsychologicalWarfare,   // Focus: Advanced psychological operations

    // Cloud Security Specs
    CloudNativeSecurity,    // Focus: Cloud-native application security
    CloudPenetrationTesting, // Focus: Cloud infrastructure attacks
    ContainerSecurity,      // Focus: Docker/K8s security
    ServerlessSecurity,     // Focus: Lambda/Functions security

    // Cryptography Specs
    Cryptanalysis,          // Focus: Code breaking
    BlockchainSecurity,     // Focus: Smart contract auditing
    QuantumResistance,      // Focus: Post-quantum cryptography
}

/// Individual skill node (like WoW talent)
#[derive(Debug, Clone)]
pub struct SkillNode {
    pub id: SkillId,
    pub name: String,
    pub description: String,
    pub icon: String,

    /// Position in tree (row, column)
    pub tier: u32,              // 1-7 tiers (like WoW)
    pub column: u32,            // 0-3 columns

    /// Cost to unlock
    pub cost: u32,              // Skill points required

    /// Prerequisites
    pub requires_skills: Vec<SkillId>,
    pub requires_level: u32,
    pub requires_spec: Option<Specialization>,

    /// What this skill unlocks
    pub unlocks: Vec<UnlockReward>,

    /// Skill type
    pub skill_type: SkillType,

    /// Current rank (skills can have multiple ranks)
    pub max_rank: u32,
    pub current_rank: u32,
}

pub type SkillId = u32;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SkillType {
    /// Passive skill (always active)
    Passive,

    /// Active skill (must be triggered)
    Active,

    /// Mastery (endgame bonus)
    Mastery,

    /// Capstone (tier 7 ultimate ability)
    Capstone,
}

/// Rewards for unlocking skills
#[derive(Debug, Clone)]
pub enum UnlockReward {
    /// Tool usage permission (developer ISO: already installed)
    ToolPermission {
        tool_name: String,
        advanced_features: Vec<String>, // Unlock --expert mode, etc.
    },

    /// Attribute bonus
    AttributeBoost {
        attribute: AttributeType,
        amount: i32,
    },

    /// New ability/command
    Ability {
        name: String,
        description: String,
        cooldown_seconds: u32,
    },

    /// Unlock challenge/scenario
    Challenge {
        challenge_id: String,
        difficulty: Difficulty,
    },

    /// Cosmetic reward
    Cosmetic {
        cosmetic_type: CosmeticType,
        item_name: String,
    },

    /// XP multiplier
    XPBoost {
        multiplier: f32,  // 1.1 = +10% XP
        duration_hours: Option<u32>,
    },

    /// Unlock prestige class
    PrestigeClassUnlock {
        class_name: String,
    },
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CosmeticType {
    Title,
    Badge,
    Theme,
    TerminalEffect,
    BootAnimation,
    AIVoice,
}

/// Character attributes (base stats)
#[derive(Debug, Clone)]
pub struct Attributes {
    /// Technical proficiency
    pub intelligence: i32,      // Affects: Tool effectiveness, XP gain

    /// Speed and efficiency
    pub agility: i32,           // Affects: Scan speed, exploit speed

    /// Tool reliability
    pub precision: i32,         // Affects: False positive rate

    /// Persistence and stamina
    pub endurance: i32,         // Affects: Long-term engagement success

    /// Social manipulation effectiveness
    pub charisma: i32,          // Affects: Social engineering success rate

    /// Pattern recognition
    pub perception: i32,        // Affects: Vulnerability detection

    /// Creative problem solving
    pub creativity: i32,        // Affects: 0-day discovery chance
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AttributeType {
    Intelligence,
    Agility,
    Precision,
    Endurance,
    Charisma,
    Perception,
    Creativity,
}

/// Alignment system (KOTOR Light/Dark side)
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Alignment {
    /// -100 (Dark) to +100 (Light)
    pub value: i32,

    /// Alignment tier
    pub tier: AlignmentTier,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AlignmentTier {
    DarkMaster,      // -100 to -75 (Black hat, aggressive tactics)
    Dark,            // -74 to -25
    Neutral,         // -24 to +24 (Gray hat)
    Light,           // +25 to +74
    LightMaster,     // +75 to +100 (White hat, ethical only)
}

impl Alignment {
    pub fn new() -> Self {
        Self {
            value: 0,
            tier: AlignmentTier::Neutral,
        }
    }

    pub fn shift(&mut self, amount: i32) {
        self.value = (self.value + amount).clamp(-100, 100);
        self.tier = self.calculate_tier();
    }

    fn calculate_tier(&self) -> AlignmentTier {
        match self.value {
            -100..=-75 => AlignmentTier::DarkMaster,
            -74..=-25 => AlignmentTier::Dark,
            -24..=24 => AlignmentTier::Neutral,
            25..=74 => AlignmentTier::Light,
            75..=100 => AlignmentTier::LightMaster,
            _ => AlignmentTier::Neutral,
        }
    }

    /// Alignment affects skill effectiveness
    pub fn get_alignment_modifier(&self, skill_type: &str) -> f32 {
        match (self.tier, skill_type) {
            // Dark alignment boosts offensive skills
            (AlignmentTier::DarkMaster, "exploit") => 1.25,
            (AlignmentTier::Dark, "exploit") => 1.10,

            // Light alignment boosts defensive skills
            (AlignmentTier::LightMaster, "defense") => 1.25,
            (AlignmentTier::Light, "defense") => 1.10,

            // Neutral is balanced
            _ => 1.0,
        }
    }
}

// ============================================================================
// PRESTIGE CLASSES (KOTOR Advanced Classes)
// ============================================================================

/// Prestige classes (unlocked at level 60)
#[derive(Debug, Clone, PartialEq)]
pub struct PrestigeClass {
    pub name: String,
    pub description: String,
    pub icon: String,

    /// Requirements to unlock
    pub requires_level: u32,
    pub requires_path: SkillPath,
    pub requires_alignment: Option<AlignmentTier>,
    pub requires_achievements: Vec<String>,

    /// Unique bonuses
    pub passive_bonuses: Vec<PrestigeBonus>,

    /// Signature ability (ultimate power)
    pub signature_ability: SignatureAbility,
}

#[derive(Debug, Clone, PartialEq)]
pub enum PrestigeBonus {
    XPMultiplier(f32),
    ToolEffectiveness(f32),
    SpecialAccess(String),
    AttributeBoost(AttributeType, i32),
}

#[derive(Debug, Clone, PartialEq)]
pub struct SignatureAbility {
    pub name: String,
    pub description: String,
    pub cooldown_hours: u32,
    pub effect: AbilityEffect,
}

#[derive(Debug, Clone, PartialEq)]
pub enum AbilityEffect {
    AutoExploit {
        target_count: u32,
        success_rate_boost: f32,
    },

    ThreatVision {
        duration_minutes: u32,
        reveal_hidden_vulns: bool,
    },

    TimeFreeze {
        pause_all_scans: bool,
        duration_seconds: u32,
    },

    MassiveXPBoost {
        multiplier: f32,
        duration_hours: u32,
    },

    InstantAnalysis {
        analyze_target_instantly: bool,
        generate_report: bool,
    },
}

// ============================================================================
// MASTERY SYSTEM (Endgame Progression)
// ============================================================================

pub struct MasterySystem {
    /// Current mastery level (1-100)
    pub mastery_level: u32,

    /// Mastery points (earned after level 100)
    pub mastery_points: u32,

    /// Mastery bonuses (permanent upgrades)
    pub active_masteries: Vec<MasteryBonus>,
}

#[derive(Debug, Clone)]
pub struct MasteryBonus {
    pub name: String,
    pub description: String,
    pub cost: u32,
    pub effect: MasteryEffect,
}

#[derive(Debug, Clone)]
pub enum MasteryEffect {
    GlobalXPBoost(f32),
    ToolCooldownReduction(f32),
    CriticalSuccessChance(f32),
    ResourceEfficiency(f32),
    AutoCompleteBasicTasks(bool),
}

// ============================================================================
// FACTION & REPUTATION SYSTEM (Street Cred)
// ============================================================================

#[derive(Debug, Clone)]
pub struct Faction {
    pub name: String,
    pub description: String,
    pub alignment_preference: AlignmentTier,

    /// Current reputation (0-10000)
    pub reputation: u32,

    /// Reputation tier
    pub tier: ReputationTier,

    /// Faction rewards by tier
    pub rewards: BTreeMap<ReputationTier, Vec<FactionReward>>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ReputationTier {
    Hated,        // 0-1000
    Hostile,      // 1001-2000
    Unfriendly,   // 2001-3000
    Neutral,      // 3001-4000
    Friendly,     // 4001-6000
    Honored,      // 6001-8000
    Revered,      // 8001-9000
    Exalted,      // 9001-10000
}

#[derive(Debug, Clone)]
pub enum FactionReward {
    ExclusiveTool(String),
    SpecialTitle(String),
    VendorDiscount(f32),
    UniqueChallenge(String),
}

// ============================================================================
// ICONIC BUILDS (Cyberpunk 2077 Style)
// ============================================================================

/// Iconic builds (legendary character builds)
#[derive(Debug, Clone)]
pub struct IconicBuild {
    pub name: String,
    pub description: String,
    pub icon: String,

    /// Required skill combination
    pub required_skills: Vec<SkillId>,
    pub required_level: u32,
    pub required_prestige: Option<String>,

    /// Synergy bonuses (when all requirements met)
    pub synergy_bonuses: Vec<SynergyBonus>,
}

#[derive(Debug, Clone)]
pub enum SynergyBonus {
    SetBonus {
        name: String,
        description: String,
        multiplier: f32,
    },

    UniqueAbility {
        name: String,
        description: String,
    },

    StatOverride {
        attribute: AttributeType,
        new_value: i32,
    },
}

// ============================================================================
// STATUS EFFECTS (Buffs/Debuffs)
// ============================================================================

#[derive(Debug, Clone)]
pub struct StatusEffect {
    pub name: String,
    pub description: String,
    pub duration_seconds: u32,
    pub effect_type: EffectType,
    pub stacks: u32,
}

#[derive(Debug, Clone)]
pub enum EffectType {
    Buff {
        stat_boost: Vec<(AttributeType, i32)>,
        xp_multiplier: f32,
    },

    Debuff {
        stat_reduction: Vec<(AttributeType, i32)>,
        cooldown_increase: f32,
    },

    Transform {
        new_form: String,
        special_abilities: Vec<String>,
    },
}

// ============================================================================
// ACHIEVEMENT ENGINE
// ============================================================================

pub struct AchievementEngine {
    /// All available achievements (200+)
    pub achievements: Vec<Achievement>,

    /// Player's unlocked achievements
    pub unlocked: Vec<String>,

    /// Achievement points
    pub total_points: u32,
}

#[derive(Debug, Clone)]
pub struct Achievement {
    pub id: String,
    pub name: String,
    pub description: String,
    pub icon: String,

    /// Category
    pub category: AchievementCategory,

    /// Rarity
    pub rarity: AchievementRarity,

    /// Points awarded
    pub points: u32,

    /// Unlock criteria
    pub criteria: AchievementCriteria,

    /// Rewards
    pub rewards: Vec<AchievementReward>,

    /// Hidden achievement?
    pub hidden: bool,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AchievementCategory {
    Combat,         // Exploitation achievements
    Exploration,    // Discovery achievements
    Mastery,        // Skill mastery achievements
    Collection,     // Collect all X achievements
    Reputation,     // Faction achievements
    Legendary,      // Ultra-rare achievements
    Seasonal,       // Limited-time achievements
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum AchievementRarity {
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary,
    Mythic,
}

#[derive(Debug, Clone)]
pub enum AchievementCriteria {
    ReachLevel(u32),
    EarnXP(u64),
    CompleteQuests(u32),
    UnlockSkills(u32),
    DefeatBosses(Vec<String>),
    ExploitVulnerabilities(u32),
    FindFlags(u32),
    MaxReputation(String), // Faction name
    CompleteIconicBuild(String),
    Custom(String), // Custom condition
}

#[derive(Debug, Clone)]
pub enum AchievementReward {
    Title(String),
    SkillPoints(u32),
    XP(u64),
    StreetCred(u32),
    UnlockAbility(String),
    Cosmetic(CosmeticType, String),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Difficulty {
    Tutorial,
    Easy,
    Normal,
    Hard,
    Expert,
    Master,
    Legendary,
}

// ============================================================================
// SKILL TREE IMPLEMENTATION
// ============================================================================

impl LegendarySkillTree {
    /// Create new skill tree system
    pub fn new(username: String) -> Self {
        let mut trees = BTreeMap::new();

        // Initialize all skill paths
        for path in Self::all_paths() {
            trees.insert(path, Self::generate_skill_tree_for_path(path));
        }

        Self {
            character: CharacterProfile::new(username),
            trees,
            mastery: MasterySystem::new(),
            prestige_classes: Self::generate_prestige_classes(),
            factions: Self::generate_factions(),
            achievements: AchievementEngine::new(),
            iconic_builds: Self::generate_iconic_builds(),
        }
    }

    fn all_paths() -> Vec<SkillPath> {
        vec![
            SkillPath::RedTeam,
            SkillPath::BlueTeam,
            SkillPath::PurpleTeam,
            SkillPath::BugBounty,
            SkillPath::Forensics,
            SkillPath::ReverseEngineering,
            SkillPath::SocialEngineering,
            SkillPath::CloudSecurity,
            SkillPath::Cryptography,
        ]
    }

    /// Earn XP and level up
    pub fn earn_xp(&mut self, amount: u64, source: &str) {
        // Apply XP multipliers
        let mut final_amount = amount as f32;

        // Alignment bonus
        final_amount *= self.character.alignment.get_alignment_modifier(source);

        // Mastery bonus
        for mastery in &self.mastery.active_masteries {
            if let MasteryEffect::GlobalXPBoost(mult) = mastery.effect {
                final_amount *= mult;
            }
        }

        // Active buffs
        for effect in &self.character.active_effects {
            if let EffectType::Buff { xp_multiplier, .. } = &effect.effect_type {
                final_amount *= xp_multiplier;
            }
        }

        self.character.total_xp += final_amount as u64;

        // Check for level up
        while self.character.total_xp >= self.xp_required_for_next_level() {
            self.level_up();
        }
    }

    fn xp_required_for_next_level(&self) -> u64 {
        // Exponential curve (like WoW) - integer approximation for no_std
        let level = self.character.level as u64;
        // Approximate x^2.5 using x^2 + x/2 for simpler calculation in no_std
        let level_squared = level * level;
        let half_level = level / 2;
        (level_squared + level + half_level) * 100
    }

    fn level_up(&mut self) {
        self.character.level += 1;
        self.character.unspent_skill_points += 1;

        // Every 10 levels: bonus skill point
        if self.character.level % 10 == 0 {
            self.character.unspent_skill_points += 1;
        }

        // Check achievements
        self.achievements.check_level_achievement(self.character.level);

        // Unlock prestige classes at level 60
        if self.character.level == 60 {
            self.unlock_prestige_class_selection();
        }
    }

    /// Learn a skill
    pub fn learn_skill(&mut self, skill_id: SkillId) -> Result<(), &'static str> {
        // First, gather all the info we need without holding any borrows
        let (requires_level, cost, requires_skills, unlocks) = {
            let skill = self.find_skill(skill_id).ok_or("Skill not found")?;
            (
                skill.requires_level,
                skill.cost,
                skill.requires_skills.clone(),
                skill.unlocks.clone(),
            )
        };

        // Check requirements
        if self.character.level < requires_level {
            return Err("Level requirement not met");
        }

        if self.character.unspent_skill_points < cost {
            return Err("Not enough skill points");
        }

        // Check prerequisites
        for prereq in &requires_skills {
            if !self.character.learned_skills.contains(prereq) {
                return Err("Prerequisites not met");
            }
        }

        // Now we can safely mutate
        if let Some(skill) = self.find_skill_mut(skill_id) {
            skill.current_rank += 1;
        }

        self.character.unspent_skill_points -= cost;
        self.character.learned_skills.push(skill_id);

        // Apply rewards
        for reward in &unlocks {
            self.apply_reward(reward);
        }

        // Check for iconic build completion
        self.check_iconic_builds();

        Ok(())
    }

    fn find_skill(&self, skill_id: SkillId) -> Option<&SkillNode> {
        for tree in self.trees.values() {
            if let Some(skill) = tree.iter().find(|s| s.id == skill_id) {
                return Some(skill);
            }
        }
        None
    }

    fn find_skill_mut(&mut self, skill_id: SkillId) -> Option<&mut SkillNode> {
        for tree in self.trees.values_mut() {
            if let Some(skill) = tree.iter_mut().find(|s| s.id == skill_id) {
                return Some(skill);
            }
        }
        None
    }

    fn apply_reward(&mut self, reward: &UnlockReward) {
        match reward {
            UnlockReward::AttributeBoost { attribute, amount } => {
                self.character.attributes.boost(*attribute, *amount);
            }
            UnlockReward::XPBoost { multiplier, .. } => {
                // Add buff
                let buff = StatusEffect {
                    name: "XP Boost".to_string(),
                    description: format!("{}x XP gain", multiplier),
                    duration_seconds: 3600, // 1 hour
                    effect_type: EffectType::Buff {
                        stat_boost: Vec::new(),
                        xp_multiplier: *multiplier,
                    },
                    stacks: 1,
                };
                self.character.active_effects.push(buff);
            }
            _ => {}
        }
    }

    fn check_iconic_builds(&mut self) {
        // Collect builds to activate without holding a borrow
        let builds_to_activate: Vec<IconicBuild> = self.iconic_builds.iter()
            .filter(|build| self.has_all_skills(&build.required_skills))
            .cloned()
            .collect();

        // Now activate them
        for build in builds_to_activate {
            self.activate_iconic_build(build);
        }
    }

    fn has_all_skills(&self, skills: &[SkillId]) -> bool {
        skills.iter().all(|sid| self.character.learned_skills.contains(sid))
    }

    fn activate_iconic_build(&mut self, build: IconicBuild) {
        // Apply synergy bonuses
        for bonus in &build.synergy_bonuses {
            match bonus {
                SynergyBonus::SetBonus { name, multiplier, .. } => {
                    // 🌟 Iconic Build Activated: {name}
                    // {multiplier}x effectiveness!
                    // TODO: Add notification system instead of println
                    let _ = (name, multiplier); // Suppress unused warnings
                }
                _ => {}
            }
        }
    }

    fn unlock_prestige_class_selection(&mut self) {
        // 🏆 LEVEL 60 REACHED!
        // You can now choose a Prestige Class!
        // TODO: Add notification system instead of println
    }

    /// Generate skill tree for a specific path
    fn generate_skill_tree_for_path(_path: SkillPath) -> Vec<SkillNode> {
        // TODO: Generate 50+ skills per path
        Vec::new()
    }

    fn generate_prestige_classes() -> Vec<PrestigeClass> {
        // TODO: Generate prestige classes
        Vec::new()
    }

    fn generate_factions() -> Vec<Faction> {
        // TODO: Generate factions
        Vec::new()
    }

    fn generate_iconic_builds() -> Vec<IconicBuild> {
        // TODO: Generate iconic builds
        Vec::new()
    }
}

impl CharacterProfile {
    pub fn new(username: String) -> Self {
        Self {
            username,
            level: 1,
            total_xp: 0,
            unspent_skill_points: 3, // Start with 3 points
            active_path: None,
            active_spec: None,
            prestige_class: None,
            alignment: Alignment::new(),
            street_cred: 0,
            attributes: Attributes::new(),
            learned_skills: Vec::new(),
            active_effects: Vec::new(),
            title: None,
            playtime_hours: 0.0,
        }
    }
}

impl Attributes {
    pub fn new() -> Self {
        Self {
            intelligence: 10,
            agility: 10,
            precision: 10,
            endurance: 10,
            charisma: 10,
            perception: 10,
            creativity: 10,
        }
    }

    pub fn boost(&mut self, attribute: AttributeType, amount: i32) {
        match attribute {
            AttributeType::Intelligence => self.intelligence += amount,
            AttributeType::Agility => self.agility += amount,
            AttributeType::Precision => self.precision += amount,
            AttributeType::Endurance => self.endurance += amount,
            AttributeType::Charisma => self.charisma += amount,
            AttributeType::Perception => self.perception += amount,
            AttributeType::Creativity => self.creativity += amount,
        }
    }
}

impl MasterySystem {
    pub fn new() -> Self {
        Self {
            mastery_level: 1,
            mastery_points: 0,
            active_masteries: Vec::new(),
        }
    }
}

impl AchievementEngine {
    pub fn new() -> Self {
        Self {
            achievements: Self::generate_all_achievements(),
            unlocked: Vec::new(),
            total_points: 0,
        }
    }

    fn generate_all_achievements() -> Vec<Achievement> {
        // TODO: Generate 200+ achievements
        Vec::new()
    }

    pub fn check_level_achievement(&mut self, level: u32) {
        // Check if level milestone achievement should unlock
        let milestone = format!("reach_level_{}", level);
        if !self.unlocked.contains(&milestone) {
            self.unlock_achievement(&milestone);
        }
    }

    pub fn unlock_achievement(&mut self, achievement_id: &str) {
        if let Some(achievement) = self.achievements.iter()
            .find(|a| a.id == achievement_id)
        {
            self.unlocked.push(achievement_id.to_string());
            self.total_points += achievement.points;

            // 🏆 ACHIEVEMENT UNLOCKED: {achievement.name}
            // {achievement.description} (+{achievement.points} points)
            // TODO: Add notification system instead of println
            let _ = (&achievement.name, &achievement.description, achievement.points); // Suppress unused warnings
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_character_creation() {
        let tree = LegendarySkillTree::new("testuser".to_string());
        assert_eq!(tree.character.level, 1);
        assert_eq!(tree.character.unspent_skill_points, 3);
    }

    #[test]
    fn test_xp_and_leveling() {
        let mut tree = LegendarySkillTree::new("testuser".to_string());
        tree.earn_xp(1000, "test");
        assert!(tree.character.total_xp >= 1000);
    }

    #[test]
    fn test_alignment_system() {
        let mut alignment = Alignment::new();
        assert_eq!(alignment.tier, AlignmentTier::Neutral);

        alignment.shift(-50);
        assert_eq!(alignment.tier, AlignmentTier::Dark);

        alignment.shift(100);
        assert_eq!(alignment.tier, AlignmentTier::Light);
    }
}
