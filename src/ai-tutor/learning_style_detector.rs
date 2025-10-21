//! Learning Style Detector - V1.7 "AI Tutor & Skill Tree"
//!
//! Analyzes user behavior to detect their preferred learning style and
//! adapts teaching strategies accordingly.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// ============================================================================
// LEARNING STYLE TYPES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum LearningStyle {
    /// Prefers diagrams, videos, visual demonstrations
    Visual,
    /// Prefers voice explanations, audio tutorials, verbal instructions
    Auditory,
    /// Prefers hands-on practice, doing rather than reading
    Kinesthetic,
    /// Prefers text documentation, written guides, step-by-step instructions
    Reading,
    /// Mixed learning style (uses multiple approaches)
    Multimodal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearningProfile {
    pub primary_style: LearningStyle,
    pub secondary_style: Option<LearningStyle>,
    pub style_scores: HashMap<String, f32>, // Each style's confidence score
    pub detected_at: chrono::DateTime<chrono::Utc>,
    pub confidence: f32, // 0.0 - 1.0
    pub total_interactions: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserBehaviorMetrics {
    // Time spent on different content types
    pub time_on_video: u64,          // seconds
    pub time_on_documentation: u64,  // seconds
    pub time_on_interactive: u64,    // seconds
    pub time_on_audio: u64,          // seconds

    // Interaction patterns
    pub video_completion_rate: f32,  // 0.0 - 1.0
    pub doc_completion_rate: f32,
    pub hands_on_attempts: u32,
    pub audio_tutorial_listens: u32,

    // Success rates with different tutorial types
    pub video_tutorial_success: f32,
    pub text_tutorial_success: f32,
    pub hands_on_success: f32,
    pub audio_tutorial_success: f32,

    // Engagement metrics
    pub video_rewatch_count: u32,
    pub doc_reread_count: u32,
    pub practice_retry_count: u32,

    // Learning velocity
    pub average_time_to_complete_challenge: u64, // seconds
    pub skill_acquisition_rate: f32,             // skills/hour
}

impl Default for UserBehaviorMetrics {
    fn default() -> Self {
        Self {
            time_on_video: 0,
            time_on_documentation: 0,
            time_on_interactive: 0,
            time_on_audio: 0,
            video_completion_rate: 0.0,
            doc_completion_rate: 0.0,
            hands_on_attempts: 0,
            audio_tutorial_listens: 0,
            video_tutorial_success: 0.0,
            text_tutorial_success: 0.0,
            hands_on_success: 0.0,
            audio_tutorial_success: 0.0,
            video_rewatch_count: 0,
            doc_reread_count: 0,
            practice_retry_count: 0,
            average_time_to_complete_challenge: 0,
            skill_acquisition_rate: 0.0,
        }
    }
}

// ============================================================================
// LEARNING STYLE DETECTOR
// ============================================================================

pub struct LearningStyleDetector {
    current_profile: Option<LearningProfile>,
    behavior_history: Vec<UserBehaviorMetrics>,
}

impl LearningStyleDetector {
    pub fn new() -> Self {
        Self {
            current_profile: None,
            behavior_history: Vec::new(),
        }
    }

    /// Detect user's learning style based on behavior metrics
    pub fn detect_learning_style(&mut self, metrics: &UserBehaviorMetrics) -> LearningProfile {
        let mut style_scores = HashMap::new();

        // Calculate Visual score
        let visual_score = self.calculate_visual_score(metrics);
        style_scores.insert("visual".to_string(), visual_score);

        // Calculate Auditory score
        let auditory_score = self.calculate_auditory_score(metrics);
        style_scores.insert("auditory".to_string(), auditory_score);

        // Calculate Kinesthetic score
        let kinesthetic_score = self.calculate_kinesthetic_score(metrics);
        style_scores.insert("kinesthetic".to_string(), kinesthetic_score);

        // Calculate Reading score
        let reading_score = self.calculate_reading_score(metrics);
        style_scores.insert("reading".to_string(), reading_score);

        // Find primary and secondary styles
        let (primary_style, primary_score) = self.get_dominant_style(&style_scores);
        let secondary_style = self.get_secondary_style(&style_scores, &primary_style);

        // Calculate confidence based on score separation
        let confidence = self.calculate_confidence(&style_scores, primary_score);

        // Create learning profile
        let profile = LearningProfile {
            primary_style,
            secondary_style,
            style_scores,
            detected_at: chrono::Utc::now(),
            confidence,
            total_interactions: self.behavior_history.len() as u32 + 1,
        };

        self.current_profile = Some(profile.clone());
        self.behavior_history.push(metrics.clone());

        profile
    }

    fn calculate_visual_score(&self, metrics: &UserBehaviorMetrics) -> f32 {
        let mut score = 0.0;

        // High video engagement
        let total_time = metrics.time_on_video + metrics.time_on_documentation
            + metrics.time_on_interactive + metrics.time_on_audio;
        if total_time > 0 {
            score += (metrics.time_on_video as f32 / total_time as f32) * 40.0;
        }

        // Video completion and success rate
        score += metrics.video_completion_rate * 30.0;
        score += metrics.video_tutorial_success * 30.0;

        // Bonus for rewatching videos (indicates visual preference)
        if metrics.video_rewatch_count > 0 {
            score += (metrics.video_rewatch_count as f32).min(10.0);
        }

        score.min(100.0)
    }

    fn calculate_auditory_score(&self, metrics: &UserBehaviorMetrics) -> f32 {
        let mut score = 0.0;

        // High audio engagement
        let total_time = metrics.time_on_video + metrics.time_on_documentation
            + metrics.time_on_interactive + metrics.time_on_audio;
        if total_time > 0 {
            score += (metrics.time_on_audio as f32 / total_time as f32) * 50.0;
        }

        // Audio tutorial success
        score += metrics.audio_tutorial_success * 40.0;

        // Number of audio tutorial listens
        if metrics.audio_tutorial_listens > 0 {
            score += (metrics.audio_tutorial_listens as f32).min(10.0);
        }

        score.min(100.0)
    }

    fn calculate_kinesthetic_score(&self, metrics: &UserBehaviorMetrics) -> f32 {
        let mut score = 0.0;

        // High hands-on engagement
        let total_time = metrics.time_on_video + metrics.time_on_documentation
            + metrics.time_on_interactive + metrics.time_on_audio;
        if total_time > 0 {
            score += (metrics.time_on_interactive as f32 / total_time as f32) * 40.0;
        }

        // Hands-on success rate
        score += metrics.hands_on_success * 40.0;

        // High number of practice attempts (learning by doing)
        if metrics.hands_on_attempts > 0 {
            score += (metrics.hands_on_attempts as f32).min(20.0);
        }

        score.min(100.0)
    }

    fn calculate_reading_score(&self, metrics: &UserBehaviorMetrics) -> f32 {
        let mut score = 0.0;

        // High documentation engagement
        let total_time = metrics.time_on_video + metrics.time_on_documentation
            + metrics.time_on_interactive + metrics.time_on_audio;
        if total_time > 0 {
            score += (metrics.time_on_documentation as f32 / total_time as f32) * 40.0;
        }

        // Documentation completion and success rate
        score += metrics.doc_completion_rate * 30.0;
        score += metrics.text_tutorial_success * 30.0;

        // Bonus for rereading documentation
        if metrics.doc_reread_count > 0 {
            score += (metrics.doc_reread_count as f32).min(10.0);
        }

        score.min(100.0)
    }

    fn get_dominant_style(&self, scores: &HashMap<String, f32>) -> (LearningStyle, f32) {
        let mut max_score = 0.0;
        let mut dominant = "kinesthetic".to_string();

        for (style, score) in scores {
            if *score > max_score {
                max_score = *score;
                dominant = style.clone();
            }
        }

        let style = match dominant.as_str() {
            "visual" => LearningStyle::Visual,
            "auditory" => LearningStyle::Auditory,
            "kinesthetic" => LearningStyle::Kinesthetic,
            "reading" => LearningStyle::Reading,
            _ => LearningStyle::Kinesthetic,
        };

        (style, max_score)
    }

    fn get_secondary_style(&self, scores: &HashMap<String, f32>,
                           primary: &LearningStyle) -> Option<LearningStyle> {
        let primary_name = match primary {
            LearningStyle::Visual => "visual",
            LearningStyle::Auditory => "auditory",
            LearningStyle::Kinesthetic => "kinesthetic",
            LearningStyle::Reading => "reading",
            LearningStyle::Multimodal => return None,
        };

        let mut second_score = 0.0;
        let mut secondary = None;

        for (style, score) in scores {
            if style != primary_name && *score > second_score {
                second_score = *score;
                secondary = Some(style.clone());
            }
        }

        // Only return secondary if it's significant (>30% of primary)
        let primary_score = scores.get(primary_name).unwrap_or(&0.0);
        if second_score > primary_score * 0.3 {
            secondary.map(|s| match s.as_str() {
                "visual" => LearningStyle::Visual,
                "auditory" => LearningStyle::Auditory,
                "kinesthetic" => LearningStyle::Kinesthetic,
                "reading" => LearningStyle::Reading,
                _ => LearningStyle::Kinesthetic,
            })
        } else {
            None
        }
    }

    fn calculate_confidence(&self, scores: &HashMap<String, f32>, primary_score: f32) -> f32 {
        // Confidence based on:
        // 1. Separation between primary and others (higher = more confident)
        // 2. Number of interactions (more = more confident)

        let mut other_scores: Vec<f32> = scores.values()
            .filter(|&&s| s != primary_score)
            .copied()
            .collect();
        other_scores.sort_by(|a, b| b.partial_cmp(a).unwrap());

        let second_score = other_scores.first().unwrap_or(&0.0);
        let separation = (primary_score - second_score) / 100.0;

        // Confidence increases with number of interactions
        let interaction_factor = (self.behavior_history.len() as f32 / 10.0).min(1.0);

        // Combine factors
        let confidence = (separation * 0.7 + interaction_factor * 0.3).clamp(0.0, 1.0);

        confidence
    }

    pub fn get_current_profile(&self) -> Option<&LearningProfile> {
        self.current_profile.as_ref()
    }

    pub fn update_metrics(&mut self, metrics: UserBehaviorMetrics) {
        self.detect_learning_style(&metrics);
    }
}

impl Default for LearningStyleDetector {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_visual_learner_detection() {
        let mut detector = LearningStyleDetector::new();

        let metrics = UserBehaviorMetrics {
            time_on_video: 3600,
            time_on_documentation: 300,
            time_on_interactive: 600,
            time_on_audio: 100,
            video_completion_rate: 0.9,
            video_tutorial_success: 0.85,
            video_rewatch_count: 3,
            ..Default::default()
        };

        let profile = detector.detect_learning_style(&metrics);
        assert_eq!(profile.primary_style, LearningStyle::Visual);
        assert!(profile.confidence > 0.5);
    }

    #[test]
    fn test_kinesthetic_learner_detection() {
        let mut detector = LearningStyleDetector::new();

        let metrics = UserBehaviorMetrics {
            time_on_video: 300,
            time_on_documentation: 200,
            time_on_interactive: 3000,
            time_on_audio: 100,
            hands_on_attempts: 15,
            hands_on_success: 0.8,
            ..Default::default()
        };

        let profile = detector.detect_learning_style(&metrics);
        assert_eq!(profile.primary_style, LearningStyle::Kinesthetic);
    }

    #[test]
    fn test_confidence_increases_with_interactions() {
        let mut detector = LearningStyleDetector::new();

        let metrics = UserBehaviorMetrics {
            time_on_video: 1000,
            time_on_documentation: 100,
            time_on_interactive: 100,
            time_on_audio: 100,
            video_completion_rate: 0.9,
            video_tutorial_success: 0.9,
            ..Default::default()
        };

        let profile1 = detector.detect_learning_style(&metrics);
        let profile2 = detector.detect_learning_style(&metrics);
        let profile3 = detector.detect_learning_style(&metrics);

        assert!(profile3.confidence > profile1.confidence);
    }
}
