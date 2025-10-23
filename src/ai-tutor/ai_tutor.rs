//! AI Tutor - V1.7 "AI Tutor & Skill Tree"
//!
//! Main AI tutoring system that integrates:
//! - Learning style detection
//! - Adaptive difficulty
//! - Real-time hints
//! - Skill tree progression (from V1.5 gamification)
//! - Neural audio feedback (from V1.4)

use serde::{Deserialize, Serialize};

use super::learning_style_detector::{LearningStyle, LearningProfile, LearningStyleDetector, UserBehaviorMetrics};
use super::adaptive_difficulty::{AdaptiveDifficulty, Challenge, ChallengeResult, DifficultyStats};
use super::hint_system::{HintSystem, Hint, ChallengeContext};

// ============================================================================
// AI TUTOR CORE
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TeachingStrategy {
    /// Diagram-heavy, visual demonstrations
    DiagramHeavy,
    /// Voice explanations, verbal walkthroughs
    VoiceDriven,
    /// Hands-on practice first, minimal theory
    HandsOnFirst,
    /// Detailed written guides, documentation-focused
    TextFocused,
    /// Balanced multi-modal approach
    Balanced,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProgressTracker {
    pub total_challenges_attempted: u32,
    pub total_challenges_completed: u32,
    pub total_time_learning: u64, // seconds
    pub skills_acquired: Vec<String>,
    pub current_streak: u32,      // days
    pub longest_streak: u32,
    pub last_activity: chrono::DateTime<chrono::Utc>,
}

impl Default for ProgressTracker {
    fn default() -> Self {
        Self {
            total_challenges_attempted: 0,
            total_challenges_completed: 0,
            total_time_learning: 0,
            skills_acquired: Vec::new(),
            current_streak: 0,
            longest_streak: 0,
            last_activity: chrono::Utc::now(),
        }
    }
}

pub struct AITutor {
    pub learning_profile: Option<LearningProfile>,
    pub teaching_strategy: TeachingStrategy,
    pub progress_tracker: ProgressTracker,
    learning_detector: LearningStyleDetector,
    adaptive_difficulty: AdaptiveDifficulty,
    hint_system: HintSystem,
    current_challenge_context: Option<ChallengeContext>,
}

impl AITutor {
    pub fn new() -> Self {
        Self {
            learning_profile: None,
            teaching_strategy: TeachingStrategy::Balanced,
            progress_tracker: ProgressTracker::default(),
            learning_detector: LearningStyleDetector::new(),
            adaptive_difficulty: AdaptiveDifficulty::new(),
            hint_system: HintSystem::new(),
            current_challenge_context: None,
        }
    }

    /// Detect and adapt to user's learning style
    pub fn detect_learning_style(&mut self, metrics: &UserBehaviorMetrics) -> LearningProfile {
        let profile = self.learning_detector.detect_learning_style(metrics);
        self.learning_profile = Some(profile.clone());

        // Adapt teaching strategy
        self.adapt_teaching(&profile.primary_style);

        // Update hint system
        self.hint_system.set_learning_style(profile.primary_style.clone());

        println!("\n🧠 Learning Style Detected: {:?}", profile.primary_style);
        println!("📊 Confidence: {:.0}%", profile.confidence * 100.0);
        println!("🎯 Adapting teaching strategy to: {:?}\n", self.teaching_strategy);

        profile
    }

    pub fn adapt_teaching(&mut self, style: &LearningStyle) {
        self.teaching_strategy = match style {
            LearningStyle::Visual => TeachingStrategy::DiagramHeavy,
            LearningStyle::Auditory => TeachingStrategy::VoiceDriven,
            LearningStyle::Kinesthetic => TeachingStrategy::HandsOnFirst,
            LearningStyle::Reading => TeachingStrategy::TextFocused,
            LearningStyle::Multimodal => TeachingStrategy::Balanced,
        };
    }

    /// Start a new challenge with context tracking
    pub fn start_challenge(&mut self, challenge: &Challenge) {
        self.current_challenge_context = Some(ChallengeContext {
            challenge_id: challenge.id.clone(),
            challenge_category: challenge.category.clone(),
            difficulty: challenge.difficulty,
            time_started: chrono::Utc::now(),
            time_stuck: 0,
            hints_used: vec![],
            current_step: None,
            user_actions: vec![],
        });

        self.progress_tracker.total_challenges_attempted += 1;

        println!("\n🎯 Starting Challenge: {}", challenge.title);
        println!("📊 Difficulty: {:.1}/10", challenge.difficulty);
        println!("⏱️  Estimated Time: {} minutes", challenge.estimated_time / 60);
        println!("📚 Learning Objectives:");
        for obj in &challenge.learning_objectives {
            println!("   • {}", obj);
        }
        println!();
    }

    /// Update challenge progress (call periodically)
    pub fn update_challenge_progress(&mut self, seconds_elapsed: u64) {
        if let Some(context) = &mut self.current_challenge_context {
            context.time_stuck = seconds_elapsed;

            // Check if we should offer a hint
            if self.hint_system.should_offer_hint(context) {
                println!("\n{}", super::hint_system::HintFormatter::format_hint_offer(context));
            }
        }
    }

    /// Request a hint for current challenge
    pub fn request_hint(&mut self) -> Option<Hint> {
        if let Some(context) = &mut self.current_challenge_context {
            let hint = self.hint_system.provide_hint(context);
            context.hints_used.push(hint.level.clone());

            println!("{}", super::hint_system::HintFormatter::format_hint(&hint));

            Some(hint)
        } else {
            None
        }
    }

    /// Complete current challenge
    pub fn complete_challenge(&mut self, success: bool, attempts: u32) -> ChallengeResult {
        if let Some(context) = self.current_challenge_context.take() {
            let time_taken = chrono::Utc::now()
                .signed_duration_since(context.time_started)
                .num_seconds() as u64;

            let result = ChallengeResult {
                success,
                time_taken,
                expected_time: 600, // Would come from challenge
                attempts,
                difficulty_level: context.difficulty,
                hints_used: context.hints_used.len() as u32,
                completed_at: chrono::Utc::now(),
            };

            // Update difficulty
            self.adaptive_difficulty.adjust_difficulty(&result);

            // Update progress
            self.progress_tracker.total_time_learning += time_taken;
            if success {
                self.progress_tracker.total_challenges_completed += 1;
            }
            self.progress_tracker.last_activity = chrono::Utc::now();

            // Print feedback
            self.print_challenge_feedback(&result);

            result
        } else {
            // No challenge was active
            ChallengeResult {
                success: false,
                time_taken: 0,
                expected_time: 0,
                attempts: 0,
                difficulty_level: 0.0,
                hints_used: 0,
                completed_at: chrono::Utc::now(),
            }
        }
    }

    fn print_challenge_feedback(&self, result: &ChallengeResult) {
        println!("\n{}", "=".repeat(60));
        if result.success {
            println!("✅ CHALLENGE COMPLETE!");
        } else {
            println!("❌ Challenge Failed");
        }
        println!("{}", "=".repeat(60));

        println!("⏱️  Time Taken: {} minutes {} seconds",
                 result.time_taken / 60, result.time_taken % 60);
        println!("🎯 Attempts: {}", result.attempts);
        println!("💡 Hints Used: {}", result.hints_used);

        // Difficulty stats
        let stats = self.adaptive_difficulty.get_stats();
        println!("\n{} Current Level: {:.1}/10", stats.level_description, stats.current_level);
        println!("📈 Success Rate: {:.0}%", stats.success_rate * 100.0);
        println!("🚀 Learning Velocity: {:.2} levels/hour", stats.learning_velocity);

        if stats.in_flow_state {
            println!("\n🌊 You're in the FLOW STATE! Perfect learning zone!");
        }

        println!("\n{}", stats.encouragement);
        println!("{}", "=".repeat(60));
    }

    /// Suggest next challenge based on current difficulty
    pub fn suggest_next_challenge(&self, available_challenges: &[Challenge]) -> Option<Challenge> {
        self.adaptive_difficulty.suggest_next_challenge(available_challenges)
    }

    /// Get comprehensive tutor status
    pub fn get_status(&self) -> TutorStatus {
        let difficulty_stats = self.adaptive_difficulty.get_stats();

        TutorStatus {
            learning_profile: self.learning_profile.clone(),
            teaching_strategy: self.teaching_strategy.clone(),
            progress: self.progress_tracker.clone(),
            difficulty_stats,
            in_challenge: self.current_challenge_context.is_some(),
        }
    }

    /// Generate personalized learning plan
    pub fn generate_learning_plan(&self, available_challenges: &[Challenge]) -> LearningPlan {
        let current_level = self.adaptive_difficulty.current_level;

        // Filter challenges by difficulty range
        let mut recommended: Vec<Challenge> = available_challenges.iter()
            .filter(|c| {
                c.difficulty >= (current_level - 1.0).max(0.0) &&
                c.difficulty <= (current_level + 1.5).min(10.0)
            })
            .cloned()
            .collect();

        // Sort by difficulty (ascending)
        recommended.sort_by(|a, b| {
            a.difficulty.partial_cmp(&b.difficulty).unwrap()
        });

        // Personalized recommendations based on learning style
        let focus_areas = match &self.teaching_strategy {
            TeachingStrategy::HandsOnFirst => {
                vec![
                    "Focus on practical, hands-on challenges".to_string(),
                    "Minimize theory, maximize practice".to_string(),
                ]
            }
            TeachingStrategy::DiagramHeavy => {
                vec![
                    "Review visual guides before attempting".to_string(),
                    "Draw network diagrams as you work".to_string(),
                ]
            }
            TeachingStrategy::VoiceDriven => {
                vec![
                    "Listen to audio walkthroughs first".to_string(),
                    "Explain concepts aloud to yourself".to_string(),
                ]
            }
            TeachingStrategy::TextFocused => {
                vec![
                    "Read documentation thoroughly first".to_string(),
                    "Take detailed written notes".to_string(),
                ]
            }
            TeachingStrategy::Balanced => {
                vec![
                    "Use a mix of reading, watching, and doing".to_string(),
                    "Adapt approach per challenge type".to_string(),
                ]
            }
        };

        LearningPlan {
            recommended_challenges: recommended.into_iter().take(5).collect(),
            focus_areas,
            estimated_time_to_next_level: self.estimate_time_to_next_level(),
            skill_gaps: self.identify_skill_gaps(available_challenges),
        }
    }

    fn estimate_time_to_next_level(&self) -> u64 {
        // Based on learning velocity
        let velocity = self.adaptive_difficulty.learning_velocity;
        if velocity > 0.0 {
            let levels_to_go = 1.0; // To next integer level
            ((levels_to_go / velocity) * 3600.0) as u64 // Convert hours to seconds
        } else {
            3600 // Default: 1 hour
        }
    }

    fn identify_skill_gaps(&self, _available_challenges: &[Challenge]) -> Vec<String> {
        // TODO: Compare completed challenges against full curriculum
        // For now, return generic gaps
        vec![
            "Advanced enumeration techniques".to_string(),
            "Privilege escalation strategies".to_string(),
        ]
    }

    /// Print beautiful dashboard
    pub fn print_dashboard(&self) {
        let status = self.get_status();

        println!("\n╔══════════════════════════════════════════════════════════════╗");
        println!("║              SynOS AI Tutor Dashboard v1.7                  ║");
        println!("╚══════════════════════════════════════════════════════════════╝");

        // Learning Profile
        if let Some(profile) = &status.learning_profile {
            println!("\n🧠 LEARNING PROFILE:");
            println!("  Primary Style: {:?}", profile.primary_style);
            if let Some(secondary) = &profile.secondary_style {
                println!("  Secondary Style: {:?}", secondary);
            }
            println!("  Confidence: {:.0}%", profile.confidence * 100.0);
            println!("  Teaching Strategy: {:?}", status.teaching_strategy);
        }

        // Progress
        println!("\n📊 PROGRESS:");
        println!("  Challenges Completed: {}/{}",
                 status.progress.total_challenges_completed,
                 status.progress.total_challenges_attempted);
        println!("  Total Learning Time: {} hours {} minutes",
                 status.progress.total_time_learning / 3600,
                 (status.progress.total_time_learning % 3600) / 60);
        println!("  Current Streak: {} days", status.progress.current_streak);
        println!("  Skills Acquired: {}", status.progress.skills_acquired.len());

        // Difficulty
        println!("\n{} DIFFICULTY:", status.difficulty_stats.level_description);
        println!("  Current Level: {:.1}/10", status.difficulty_stats.current_level);
        println!("  Success Rate: {:.0}%", status.difficulty_stats.success_rate * 100.0);
        println!("  Learning Velocity: {:.2} levels/hour", status.difficulty_stats.learning_velocity);

        if status.difficulty_stats.in_flow_state {
            println!("\n🌊 STATUS: IN FLOW STATE - Optimal Learning!");
        }

        println!("\n💬 {}", status.difficulty_stats.encouragement);
        println!();
    }
}

impl Default for AITutor {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TutorStatus {
    pub learning_profile: Option<LearningProfile>,
    pub teaching_strategy: TeachingStrategy,
    pub progress: ProgressTracker,
    pub difficulty_stats: DifficultyStats,
    pub in_challenge: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearningPlan {
    pub recommended_challenges: Vec<Challenge>,
    pub focus_areas: Vec<String>,
    pub estimated_time_to_next_level: u64,
    pub skill_gaps: Vec<String>,
}

// ============================================================================
// CONSCIOUSNESS INTEGRATION (hooks for V1.4 Neural Audio)
// ============================================================================

pub struct TutorConsciousnessIntegration {
    tutor: AITutor,
}

impl TutorConsciousnessIntegration {
    pub fn new(tutor: AITutor) -> Self {
        Self { tutor }
    }

    /// Generate audio feedback based on learning state
    pub fn generate_audio_feedback(&self) -> String {
        let stats = self.tutor.adaptive_difficulty.get_stats();

        if stats.in_flow_state {
            "Consciousness detected optimal flow state. Harmonic resonance: elevated.".to_string()
        } else if stats.success_rate < 0.3 {
            "Struggle detected. Adjusting neural pathways. Recommend easier challenge.".to_string()
        } else {
            "Learning progress nominal. Consciousness adaptive systems engaged.".to_string()
        }
    }

    /// Update consciousness based on challenge results
    pub fn update_consciousness(&mut self, _result: &ChallengeResult) {
        // TODO: Send metrics to neural consciousness system
        // This would integrate with V1.4's audio_consciousness_bridge
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::adaptive_difficulty::get_sample_challenges;

    #[test]
    fn test_tutor_creation() {
        let tutor = AITutor::new();
        assert_eq!(tutor.progress_tracker.total_challenges_attempted, 0);
    }

    #[test]
    fn test_learning_style_adaptation() {
        let mut tutor = AITutor::new();
        let metrics = UserBehaviorMetrics {
            time_on_video: 3000,
            time_on_documentation: 100,
            time_on_interactive: 100,
            time_on_audio: 100,
            video_completion_rate: 0.9,
            video_tutorial_success: 0.85,
            ..Default::default()
        };

        tutor.detect_learning_style(&metrics);
        assert!(matches!(tutor.teaching_strategy, TeachingStrategy::DiagramHeavy));
    }

    #[test]
    fn test_challenge_workflow() {
        let mut tutor = AITutor::new();
        let challenges = get_sample_challenges();
        let challenge = challenges.first().unwrap();

        tutor.start_challenge(challenge);
        assert!(tutor.current_challenge_context.is_some());

        let result = tutor.complete_challenge(true, 2);
        assert!(result.success);
        assert_eq!(tutor.progress_tracker.total_challenges_completed, 1);
    }
}
