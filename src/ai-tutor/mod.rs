//! SynOS AI Tutor Module - V1.7 "AI Tutor & Skill Tree"
//!
//! Consciousness-aware AI tutoring system that adapts to individual learning styles
//! and provides personalized cybersecurity education.
//!
//! # Features
//! - **Learning Style Detection:** Analyzes behavior to detect Visual/Auditory/Kinesthetic/Reading preferences
//! - **Adaptive Difficulty:** Dynamically adjusts challenge difficulty based on performance
//! - **Real-time Hints:** Progressive hint system (Nudge → Guide → Detailed → Solution)
//! - **Flow State Detection:** Identifies optimal learning zones (70% success rate)
//! - **Personalized Teaching:** Adapts content delivery to learning style
//! - **Progress Tracking:** Comprehensive metrics and streaks
//! - **Consciousness Integration:** Hooks into V1.4 Neural Audio system
//!
//! # Integration
//! Integrates with:
//! - V1.5 Gamification (Skill Trees)
//! - V1.4 Neural Audio (Consciousness feedback)
//! - V1.6 Cloud Security (Security challenge generation)

pub mod learning_style_detector;
pub mod adaptive_difficulty;
pub mod hint_system;
pub mod ai_tutor;

// Re-export main types
pub use learning_style_detector::{
    LearningStyle,
    LearningProfile,
    LearningStyleDetector,
    UserBehaviorMetrics,
};

pub use adaptive_difficulty::{
    AdaptiveDifficulty,
    Challenge,
    ChallengeResult,
    ChallengeCategory,
    DifficultyStats,
    get_sample_challenges,
};

pub use hint_system::{
    HintSystem,
    Hint,
    HintLevel,
    ChallengeContext,
    HintFormatter,
};

pub use ai_tutor::{
    AITutor,
    TeachingStrategy,
    ProgressTracker,
    TutorStatus,
    LearningPlan,
    TutorConsciousnessIntegration,
};

/// Quick-start: Create a new AI tutor instance
pub fn create_tutor() -> AITutor {
    AITutor::new()
}

/// Quick-start: Initialize tutor with learning style detection
pub fn initialize_tutor(metrics: &UserBehaviorMetrics) -> AITutor {
    let mut tutor = AITutor::new();
    tutor.detect_learning_style(metrics);
    tutor
}

/// Example usage and demonstration
pub fn demo() {
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║        SynOS AI Tutor v1.7 - Demonstration                  ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");

    // Create tutor
    let mut tutor = AITutor::new();

    // Simulate user behavior (visual learner)
    let metrics = UserBehaviorMetrics {
        time_on_video: 3600,
        time_on_documentation: 400,
        time_on_interactive: 800,
        time_on_audio: 200,
        video_completion_rate: 0.9,
        doc_completion_rate: 0.6,
        hands_on_attempts: 5,
        audio_tutorial_listens: 1,
        video_tutorial_success: 0.85,
        text_tutorial_success: 0.7,
        hands_on_success: 0.75,
        audio_tutorial_success: 0.6,
        video_rewatch_count: 3,
        doc_reread_count: 1,
        practice_retry_count: 2,
        average_time_to_complete_challenge: 600,
        skill_acquisition_rate: 1.5,
    };

    // Detect learning style
    println!("1️⃣  Analyzing learning behavior...\n");
    let _profile = tutor.detect_learning_style(&metrics);

    // Get available challenges
    let challenges = get_sample_challenges();

    // Start a challenge
    println!("\n2️⃣  Starting first challenge...\n");
    if let Some(challenge) = challenges.first() {
        tutor.start_challenge(challenge);

        // Simulate working on challenge
        println!("\n3️⃣  Simulating challenge progress...\n");
        tutor.update_challenge_progress(400);

        // Request a hint
        println!("\n4️⃣  User requests hint...\n");
        if let Some(_hint) = tutor.request_hint() {
            println!("\n   (Hint provided above)\n");
        }

        // Complete challenge
        println!("\n5️⃣  Completing challenge...\n");
        let _result = tutor.complete_challenge(true, 2);
    }

    // Show dashboard
    println!("\n6️⃣  Displaying tutor dashboard...\n");
    tutor.print_dashboard();

    // Generate learning plan
    println!("\n7️⃣  Generating personalized learning plan...\n");
    let plan = tutor.generate_learning_plan(&challenges);
    println!("📚 RECOMMENDED CHALLENGES:");
    for (i, challenge) in plan.recommended_challenges.iter().enumerate() {
        println!("   {}. {} (Difficulty: {:.1}/10)",
                 i + 1, challenge.title, challenge.difficulty);
    }

    println!("\n🎯 FOCUS AREAS:");
    for area in &plan.focus_areas {
        println!("   • {}", area);
    }

    println!("\n⏱️  Estimated time to next level: {} minutes\n",
             plan.estimated_time_to_next_level / 60);

    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║                    Demo Complete!                           ║");
    println!("╚══════════════════════════════════════════════════════════════╝");
}
