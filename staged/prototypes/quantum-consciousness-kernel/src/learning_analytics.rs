//! SynapticOS Learning Analytics Engine - Phase 2
//!
//! Advanced analytics for consciousness-aware educational effectiveness tracking

use crate::consciousness::{get_consciousness_level, get_kernel_consciousness_state};
use crate::education_platform::{
    AdaptiveDifficulty, LearningSessionReport, LearningStyle, PerformanceMetric, StudentProfile,
};
use crate::println;
use crate::security::SecurityContext;
use alloc::collections::BTreeMap;
use alloc::format;
use alloc::string::{String, ToString};
use alloc::vec;
use alloc::vec::Vec;
use core::sync::atomic::{AtomicU64, Ordering};
use lazy_static::lazy_static;
use spin::Mutex;

lazy_static! {
    /// Global analytics data store
    pub static ref ANALYTICS_ENGINE: Mutex<AdvancedAnalyticsEngine> =
        Mutex::new(AdvancedAnalyticsEngine::new());

    /// Real-time learning metrics
    pub static ref REAL_TIME_METRICS: Mutex<RealTimeLearningMetrics> =
        Mutex::new(RealTimeLearningMetrics::new());

    /// Predictive learning models
    pub static ref PREDICTIVE_MODELS: Mutex<PredictiveLearningEngine> =
        Mutex::new(PredictiveLearningEngine::new());
}

/// Advanced analytics engine for educational data
#[derive(Debug)]
pub struct AdvancedAnalyticsEngine {
    pub learning_patterns: BTreeMap<u64, LearningPattern>,
    pub consciousness_learning_correlation: BTreeMap<String, f64>,
    pub skill_progression_models: BTreeMap<String, f64>, // Simplified from SkillProgressionModel
    pub engagement_analytics: EngagementAnalytics,
    pub cross_platform_correlations: BTreeMap<String, Vec<PlatformCorrelation>>,
}

impl AdvancedAnalyticsEngine {
    pub fn new() -> Self {
        Self {
            learning_patterns: BTreeMap::new(),
            consciousness_learning_correlation: BTreeMap::new(),
            skill_progression_models: BTreeMap::new(),
            engagement_analytics: EngagementAnalytics::new(),
            cross_platform_correlations: BTreeMap::new(),
        }
    }

    /// Analyze individual student learning patterns
    pub fn analyze_student_pattern(&mut self, student: &StudentProfile) -> LearningPattern {
        let pattern = LearningPattern {
            student_id: student.student_id,
            dominant_learning_style: student.learning_style,
            optimal_consciousness_range: self.calculate_optimal_consciousness_range(student),
            learning_velocity: self.calculate_learning_velocity(student),
            strength_areas: self.identify_strength_areas(student),
            improvement_areas: self.identify_improvement_areas(student),
            predicted_success_rate: self.predict_success_rate(student),
            recommended_study_schedule: self.generate_study_schedule(student),
        };

        self.learning_patterns
            .insert(student.student_id, pattern.clone());
        pattern
    }

    fn calculate_optimal_consciousness_range(&self, student: &StudentProfile) -> (f64, f64) {
        // Analyze performance history to find optimal consciousness levels
        let mut best_performances = Vec::new();

        for performance in &student.performance_history {
            if performance.accuracy_score > 0.8 && performance.engagement_score > 0.7 {
                best_performances.push(performance.consciousness_level);
            }
        }

        if best_performances.is_empty() {
            (0.5, 0.8) // Default range
        } else {
            let min = best_performances.iter().fold(1.0f64, |a, &b| a.min(b));
            let max = best_performances.iter().fold(0.0f64, |a, &b| a.max(b));
            (min, max)
        }
    }

    fn calculate_learning_velocity(&self, student: &StudentProfile) -> f64 {
        if student.total_learning_time == 0 {
            return 0.0;
        }

        let modules_completed = student.completed_modules.len() as f64;
        let hours_spent = student.total_learning_time as f64 / 3600.0;
        modules_completed / hours_spent
    }

    fn identify_strength_areas(&self, student: &StudentProfile) -> Vec<String> {
        let mut strengths = Vec::new();

        for (skill, level) in &student.skill_levels {
            if *level > 0.7 {
                strengths.push(skill.clone());
            }
        }

        // If no high skills, identify areas with good performance
        if strengths.is_empty() {
            for performance in &student.performance_history {
                if performance.accuracy_score > 0.8 {
                    strengths.push(performance.module_name.clone());
                }
            }
        }

        strengths
    }

    fn identify_improvement_areas(&self, student: &StudentProfile) -> Vec<String> {
        let mut improvements = Vec::new();

        for (skill, level) in &student.skill_levels {
            if *level < 0.4 {
                improvements.push(skill.clone());
            }
        }

        // Identify modules with low performance
        for performance in &student.performance_history {
            if performance.accuracy_score < 0.6 && !improvements.contains(&performance.module_name)
            {
                improvements.push(performance.module_name.clone());
            }
        }

        improvements
    }

    fn predict_success_rate(&self, student: &StudentProfile) -> f64 {
        if student.performance_history.is_empty() {
            return 0.5; // Neutral prediction
        }

        let recent_performances: Vec<&PerformanceMetric> =
            student.performance_history.iter().rev().take(5).collect();

        let avg_accuracy: f64 = recent_performances
            .iter()
            .map(|p| p.accuracy_score)
            .sum::<f64>()
            / recent_performances.len() as f64;

        let avg_engagement: f64 = recent_performances
            .iter()
            .map(|p| p.engagement_score)
            .sum::<f64>()
            / recent_performances.len() as f64;

        let consciousness_correlation = student.consciousness_correlation;

        // Weighted prediction based on multiple factors
        (avg_accuracy * 0.4 + avg_engagement * 0.3 + consciousness_correlation * 0.3).min(1.0)
    }

    fn generate_study_schedule(&self, student: &StudentProfile) -> StudySchedule {
        let optimal_range = self.calculate_optimal_consciousness_range(student);
        let learning_velocity = self.calculate_learning_velocity(student);

        StudySchedule {
            recommended_session_duration: self
                .calculate_optimal_session_duration(learning_velocity),
            optimal_consciousness_target: (optimal_range.0 + optimal_range.1) / 2.0,
            study_frequency: self.calculate_study_frequency(student),
            break_intervals: self.calculate_break_intervals(student),
            difficulty_progression: self.recommend_difficulty_progression(student),
        }
    }

    fn calculate_optimal_session_duration(&self, learning_velocity: f64) -> u64 {
        // Base duration adjusted by learning velocity
        let base_duration = 45; // minutes
        let velocity_factor = learning_velocity.max(0.1).min(3.0);
        (base_duration as f64 * velocity_factor) as u64
    }

    fn calculate_study_frequency(&self, student: &StudentProfile) -> StudyFrequency {
        match student.learning_style {
            LearningStyle::Consciousness => StudyFrequency::Adaptive, // Adjusts based on consciousness
            LearningStyle::Kinesthetic => StudyFrequency::Daily,
            LearningStyle::Visual => StudyFrequency::EveryOtherDay,
            _ => StudyFrequency::ThreeTimesWeek,
        }
    }

    fn calculate_break_intervals(&self, student: &StudentProfile) -> u64 {
        // Break interval in minutes based on learning style and performance
        match student.learning_style {
            LearningStyle::Consciousness => 10, // Shorter breaks for consciousness-enhanced learning
            LearningStyle::Kinesthetic => 15,   // Longer breaks for hands-on learners
            _ => 12,
        }
    }

    fn recommend_difficulty_progression(&self, student: &StudentProfile) -> DifficultyProgression {
        let success_rate = self.predict_success_rate(student);

        match success_rate {
            rate if rate > 0.8 => DifficultyProgression::Accelerated,
            rate if rate > 0.6 => DifficultyProgression::Standard,
            rate if rate > 0.4 => DifficultyProgression::Gradual,
            _ => DifficultyProgression::Reinforcement,
        }
    }

    /// Analyze consciousness correlation with learning effectiveness
    pub fn analyze_consciousness_correlation(&mut self, sessions: &[LearningSessionReport]) {
        for session in sessions {
            let module = &session.module_name;
            let consciousness_impact = session.consciousness_improvement * session.accuracy_score;

            let current_correlation = self
                .consciousness_learning_correlation
                .get(module)
                .unwrap_or(&0.0);

            // Update correlation with exponential moving average
            let alpha = 0.1;
            let new_correlation =
                current_correlation * (1.0 - alpha) + consciousness_impact * alpha;

            self.consciousness_learning_correlation
                .insert(module.clone(), new_correlation);
        }
    }

    /// Generate comprehensive learning insights
    pub fn generate_learning_insights(&self) -> LearningInsights {
        LearningInsights {
            top_performing_modules: self.identify_top_performing_modules(),
            consciousness_effectiveness: self.calculate_consciousness_effectiveness(),
            learning_style_effectiveness: self.analyze_learning_style_effectiveness(),
            optimal_learning_conditions: self.identify_optimal_learning_conditions(),
            predictive_recommendations: self.generate_predictive_recommendations(),
        }
    }

    fn identify_top_performing_modules(&self) -> Vec<String> {
        let mut modules: Vec<_> = self.consciousness_learning_correlation.iter().collect();
        modules.sort_by(|a, b| b.1.partial_cmp(a.1).unwrap_or(core::cmp::Ordering::Equal));
        modules
            .into_iter()
            .take(3)
            .map(|(module, _)| module.clone())
            .collect()
    }

    fn calculate_consciousness_effectiveness(&self) -> f64 {
        if self.consciousness_learning_correlation.is_empty() {
            return 0.0;
        }

        let total: f64 = self.consciousness_learning_correlation.values().sum();
        total / self.consciousness_learning_correlation.len() as f64
    }

    fn analyze_learning_style_effectiveness(&self) -> BTreeMap<LearningStyle, f64> {
        let mut effectiveness = BTreeMap::new();

        for pattern in self.learning_patterns.values() {
            let style = pattern.dominant_learning_style;
            let current = effectiveness.get(&style).unwrap_or(&0.0);
            effectiveness.insert(style, current + pattern.predicted_success_rate);
        }

        // Average the effectiveness scores
        for (style, total) in effectiveness.iter_mut() {
            let count = self
                .learning_patterns
                .values()
                .filter(|p| p.dominant_learning_style == *style)
                .count() as f64;
            if count > 0.0 {
                *total /= count;
            }
        }

        effectiveness
    }

    fn identify_optimal_learning_conditions(&self) -> OptimalLearningConditions {
        // Analyze patterns to identify optimal conditions
        let mut optimal_consciousness = 0.0;
        let mut optimal_session_length = 0;
        let mut pattern_count = 0;

        for pattern in self.learning_patterns.values() {
            optimal_consciousness += (pattern.optimal_consciousness_range.0
                + pattern.optimal_consciousness_range.1)
                / 2.0;
            optimal_session_length += pattern
                .recommended_study_schedule
                .recommended_session_duration;
            pattern_count += 1;
        }

        if pattern_count > 0 {
            optimal_consciousness /= pattern_count as f64;
            optimal_session_length /= pattern_count;
        }

        OptimalLearningConditions {
            consciousness_level: optimal_consciousness,
            session_duration: optimal_session_length,
            learning_environment: "Consciousness-Enhanced".to_string(),
            recommended_tools: vec![
                "Real-time consciousness monitoring".to_string(),
                "Adaptive difficulty adjustment".to_string(),
                "Personalized feedback system".to_string(),
            ],
        }
    }

    fn generate_predictive_recommendations(&self) -> Vec<String> {
        let mut recommendations = Vec::new();

        let consciousness_effectiveness = self.calculate_consciousness_effectiveness();

        if consciousness_effectiveness > 0.7 {
            recommendations.push(
                "High consciousness correlation detected. Increase consciousness-enhanced modules."
                    .to_string(),
            );
        } else if consciousness_effectiveness < 0.3 {
            recommendations.push(
                "Low consciousness correlation. Consider traditional learning approaches."
                    .to_string(),
            );
        }

        if self.learning_patterns.len() > 10 {
            recommendations
                .push("Sufficient data available for advanced predictive modeling.".to_string());
        }

        recommendations
    }
}

/// Individual student learning pattern analysis
#[derive(Debug, Clone)]
pub struct LearningPattern {
    pub student_id: u64,
    pub dominant_learning_style: LearningStyle,
    pub optimal_consciousness_range: (f64, f64),
    pub learning_velocity: f64,
    pub strength_areas: Vec<String>,
    pub improvement_areas: Vec<String>,
    pub predicted_success_rate: f64,
    pub recommended_study_schedule: StudySchedule,
}

/// Recommended study schedule for optimal learning
#[derive(Debug, Clone)]
pub struct StudySchedule {
    pub recommended_session_duration: u64, // minutes
    pub optimal_consciousness_target: f64,
    pub study_frequency: StudyFrequency,
    pub break_intervals: u64, // minutes
    pub difficulty_progression: DifficultyProgression,
}

#[derive(Debug, Clone, Copy)]
pub enum StudyFrequency {
    Daily,
    EveryOtherDay,
    ThreeTimesWeek,
    Adaptive, // Adjusts based on consciousness and performance
}

#[derive(Debug, Clone, Copy)]
pub enum DifficultyProgression {
    Accelerated,   // Fast progression for high performers
    Standard,      // Normal progression
    Gradual,       // Slower progression with more reinforcement
    Reinforcement, // Focus on mastering current level
}

/// Real-time learning metrics tracking
#[derive(Debug)]
pub struct RealTimeLearningMetrics {
    pub active_learners: u64,
    pub current_average_consciousness: f64,
    pub learning_effectiveness_trend: EffectivenessTrend,
    pub engagement_metrics: EngagementMetrics,
    pub performance_distribution: PerformanceDistribution,
}

impl RealTimeLearningMetrics {
    pub fn new() -> Self {
        Self {
            active_learners: 0,
            current_average_consciousness: 0.0,
            learning_effectiveness_trend: EffectivenessTrend::Stable,
            engagement_metrics: EngagementMetrics::new(),
            performance_distribution: PerformanceDistribution::new(),
        }
    }

    /// Update real-time metrics
    pub fn update_metrics(&mut self, session_report: &LearningSessionReport) {
        self.active_learners += 1;

        // Update consciousness average
        let alpha = 0.1;
        let session_consciousness = session_report.consciousness_improvement + 0.5; // Approximate current level
        self.current_average_consciousness =
            self.current_average_consciousness * (1.0 - alpha) + session_consciousness * alpha;

        // Update engagement
        self.engagement_metrics
            .update_engagement(session_report.engagement_score);

        // Update performance distribution
        self.performance_distribution
            .add_performance(session_report.accuracy_score);

        // Update trend
        self.learning_effectiveness_trend = self.calculate_trend();
    }

    fn calculate_trend(&self) -> EffectivenessTrend {
        // Simplified trend calculation based on recent metrics
        if self.engagement_metrics.average_engagement > 0.7
            && self.current_average_consciousness > 0.6
        {
            EffectivenessTrend::Improving
        } else if self.engagement_metrics.average_engagement < 0.4
            || self.current_average_consciousness < 0.3
        {
            EffectivenessTrend::Declining
        } else {
            EffectivenessTrend::Stable
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum EffectivenessTrend {
    Improving,
    Stable,
    Declining,
}

/// Engagement analytics tracking
#[derive(Debug)]
pub struct EngagementAnalytics {
    pub total_engagement_score: f64,
    pub session_count: u64,
    pub high_engagement_sessions: u64,
    pub low_engagement_sessions: u64,
}

impl EngagementAnalytics {
    pub fn new() -> Self {
        Self {
            total_engagement_score: 0.0,
            session_count: 0,
            high_engagement_sessions: 0,
            low_engagement_sessions: 0,
        }
    }

    pub fn add_session_engagement(&mut self, engagement: f64) {
        self.total_engagement_score += engagement;
        self.session_count += 1;

        if engagement > 0.7 {
            self.high_engagement_sessions += 1;
        } else if engagement < 0.4 {
            self.low_engagement_sessions += 1;
        }
    }

    pub fn get_average_engagement(&self) -> f64 {
        if self.session_count > 0 {
            self.total_engagement_score / self.session_count as f64
        } else {
            0.0
        }
    }
}

/// Engagement metrics for real-time tracking
#[derive(Debug)]
pub struct EngagementMetrics {
    pub average_engagement: f64,
    pub engagement_trend: EffectivenessTrend,
    pub peak_engagement_time: u64,
    pub low_engagement_indicators: Vec<String>,
}

impl EngagementMetrics {
    pub fn new() -> Self {
        Self {
            average_engagement: 0.0,
            engagement_trend: EffectivenessTrend::Stable,
            peak_engagement_time: 0,
            low_engagement_indicators: Vec::new(),
        }
    }

    pub fn update_engagement(&mut self, new_engagement: f64) {
        let alpha = 0.2;
        self.average_engagement = self.average_engagement * (1.0 - alpha) + new_engagement * alpha;

        // Update trend
        if new_engagement > self.average_engagement + 0.1 {
            self.engagement_trend = EffectivenessTrend::Improving;
        } else if new_engagement < self.average_engagement - 0.1 {
            self.engagement_trend = EffectivenessTrend::Declining;
        } else {
            self.engagement_trend = EffectivenessTrend::Stable;
        }
    }
}

/// Performance distribution tracking
#[derive(Debug)]
pub struct PerformanceDistribution {
    pub excellent_performance: u64, // >90%
    pub good_performance: u64,      // 70-90%
    pub average_performance: u64,   // 50-70%
    pub poor_performance: u64,      // <50%
}

impl PerformanceDistribution {
    pub fn new() -> Self {
        Self {
            excellent_performance: 0,
            good_performance: 0,
            average_performance: 0,
            poor_performance: 0,
        }
    }

    pub fn add_performance(&mut self, accuracy: f64) {
        match accuracy {
            acc if acc >= 0.9 => self.excellent_performance += 1,
            acc if acc >= 0.7 => self.good_performance += 1,
            acc if acc >= 0.5 => self.average_performance += 1,
            _ => self.poor_performance += 1,
        }
    }
}

/// Predictive learning engine for forecasting student outcomes
#[derive(Debug)]
pub struct PredictiveLearningEngine {
    pub success_prediction_models: BTreeMap<String, SuccessPredictionModel>,
    pub learning_path_recommendations: BTreeMap<u64, Vec<String>>,
    pub risk_assessment_models: RiskAssessmentEngine,
}

impl PredictiveLearningEngine {
    pub fn new() -> Self {
        Self {
            success_prediction_models: BTreeMap::new(),
            learning_path_recommendations: BTreeMap::new(),
            risk_assessment_models: RiskAssessmentEngine::new(),
        }
    }

    /// Predict student success in upcoming modules
    pub fn predict_module_success(&self, student: &StudentProfile, module_name: &str) -> f64 {
        if let Some(model) = self.success_prediction_models.get(module_name) {
            model.predict_success(student)
        } else {
            // Default prediction based on general performance
            student.consciousness_correlation * 0.7
                + (student.performance_history.len() as f64 / 10.0).min(0.3)
        }
    }

    /// Generate personalized learning path recommendations
    pub fn recommend_learning_path(&mut self, student: &StudentProfile) -> Vec<String> {
        let mut recommendations = Vec::new();

        // Analyze strengths and weaknesses
        let mut skill_scores: Vec<_> = student.skill_levels.iter().collect();
        skill_scores.sort_by(|a, b| b.1.partial_cmp(a.1).unwrap_or(core::cmp::Ordering::Equal));

        // Recommend modules based on current skill levels and consciousness
        if student.consciousness_correlation > 0.7 {
            recommendations.push("Advanced Consciousness-Enhanced Programming".to_string());
        }

        // Fill knowledge gaps
        for (skill, level) in &student.skill_levels {
            if *level < 0.5 {
                recommendations.push(format!("Remedial {}", skill));
            }
        }

        self.learning_path_recommendations
            .insert(student.student_id, recommendations.clone());
        recommendations
    }
}

/// Success prediction model for specific modules
#[derive(Debug)]
pub struct SuccessPredictionModel {
    pub module_name: String,
    pub accuracy_weight: f64,
    pub consciousness_weight: f64,
    pub engagement_weight: f64,
    pub historical_data_points: u64,
}

impl SuccessPredictionModel {
    pub fn predict_success(&self, student: &StudentProfile) -> f64 {
        let avg_accuracy = if student.performance_history.is_empty() {
            0.5
        } else {
            student
                .performance_history
                .iter()
                .map(|p| p.accuracy_score)
                .sum::<f64>()
                / student.performance_history.len() as f64
        };

        let avg_engagement = if student.performance_history.is_empty() {
            0.5
        } else {
            student
                .performance_history
                .iter()
                .map(|p| p.engagement_score)
                .sum::<f64>()
                / student.performance_history.len() as f64
        };

        (avg_accuracy * self.accuracy_weight
            + student.consciousness_correlation * self.consciousness_weight
            + avg_engagement * self.engagement_weight)
            .min(1.0)
    }
}

/// Risk assessment for identifying students at risk of failure
#[derive(Debug)]
pub struct RiskAssessmentEngine {
    pub high_risk_indicators: Vec<String>,
    pub intervention_strategies: BTreeMap<String, Vec<String>>,
}

impl RiskAssessmentEngine {
    pub fn new() -> Self {
        let mut strategies = BTreeMap::new();
        strategies.insert(
            "Low Engagement".to_string(),
            vec![
                "Gamification elements".to_string(),
                "Peer learning groups".to_string(),
                "Shorter learning sessions".to_string(),
            ],
        );
        strategies.insert(
            "Poor Performance".to_string(),
            vec![
                "Additional practice exercises".to_string(),
                "One-on-one tutoring".to_string(),
                "Prerequisite review".to_string(),
            ],
        );

        Self {
            high_risk_indicators: vec![
                "Declining engagement trend".to_string(),
                "Low consciousness correlation".to_string(),
                "High mistake frequency".to_string(),
            ],
            intervention_strategies: strategies,
        }
    }

    pub fn assess_risk(&self, student: &StudentProfile) -> RiskLevel {
        let mut risk_factors = 0;

        // Check engagement trend
        if student.consciousness_correlation < 0.3 {
            risk_factors += 1;
        }

        // Check recent performance
        let recent_performance: Vec<_> = student.performance_history.iter().rev().take(3).collect();
        if recent_performance.len() >= 2 {
            let avg_recent = recent_performance
                .iter()
                .map(|p| p.accuracy_score)
                .sum::<f64>()
                / recent_performance.len() as f64;
            if avg_recent < 0.5 {
                risk_factors += 1;
            }
        }

        // Check learning velocity
        if student.total_learning_time > 0 {
            let velocity = student.completed_modules.len() as f64
                / (student.total_learning_time as f64 / 3600.0);
            if velocity < 0.1 {
                risk_factors += 1;
            }
        }

        match risk_factors {
            0 => RiskLevel::Low,
            1 => RiskLevel::Medium,
            _ => RiskLevel::High,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
}

/// Platform correlation analysis
#[derive(Debug, Clone)]
pub struct PlatformCorrelation {
    pub platform_name: String,
    pub skill_area: String,
    pub correlation_strength: f64,
    pub transfer_effectiveness: f64,
}

/// Comprehensive learning insights
#[derive(Debug, Clone)]
pub struct LearningInsights {
    pub top_performing_modules: Vec<String>,
    pub consciousness_effectiveness: f64,
    pub learning_style_effectiveness: BTreeMap<LearningStyle, f64>,
    pub optimal_learning_conditions: OptimalLearningConditions,
    pub predictive_recommendations: Vec<String>,
}

/// Optimal learning conditions identified by analysis
#[derive(Debug, Clone)]
pub struct OptimalLearningConditions {
    pub consciousness_level: f64,
    pub session_duration: u64,
    pub learning_environment: String,
    pub recommended_tools: Vec<String>,
}

/// Initialize the learning analytics system
pub fn init() {
    println!("📊 Initializing Learning Analytics Engine...");

    // Initialize analytics components
    {
        let mut analytics = ANALYTICS_ENGINE.lock();
        *analytics = AdvancedAnalyticsEngine::new();
    }

    {
        let mut metrics = REAL_TIME_METRICS.lock();
        *metrics = RealTimeLearningMetrics::new();
    }

    {
        let mut predictive = PREDICTIVE_MODELS.lock();
        *predictive = PredictiveLearningEngine::new();
    }

    println!("📊 Learning Analytics Engine initialized");
    println!("   Advanced pattern analysis: Active");
    println!("   Predictive modeling: Enabled");
    println!("   Real-time metrics: Active");
}

/// Analyze student and generate comprehensive learning insights
pub fn analyze_student_comprehensive(student: &StudentProfile) -> LearningPattern {
    let mut analytics = ANALYTICS_ENGINE.lock();
    analytics.analyze_student_pattern(student)
}

/// Update real-time metrics with new session data
pub fn update_real_time_metrics(session_report: &LearningSessionReport) {
    let mut metrics = REAL_TIME_METRICS.lock();
    metrics.update_metrics(session_report);
}

/// Generate platform-wide learning insights
pub fn generate_platform_insights() -> LearningInsights {
    let analytics = ANALYTICS_ENGINE.lock();
    analytics.generate_learning_insights()
}

/// Predict student success in a specific module
pub fn predict_student_success(student: &StudentProfile, module_name: &str) -> f64 {
    let predictive = PREDICTIVE_MODELS.lock();
    predictive.predict_module_success(student, module_name)
}

/// Assess student risk level and recommend interventions
pub fn assess_student_risk(student: &StudentProfile) -> (RiskLevel, Vec<String>) {
    let predictive = PREDICTIVE_MODELS.lock();
    let risk_level = predictive.risk_assessment_models.assess_risk(student);

    let interventions = match risk_level {
        RiskLevel::High => vec![
            "Immediate intervention required".to_string(),
            "Consider alternative learning approach".to_string(),
            "Increase support and guidance".to_string(),
        ],
        RiskLevel::Medium => vec![
            "Monitor progress closely".to_string(),
            "Provide additional practice".to_string(),
        ],
        RiskLevel::Low => vec!["Continue current approach".to_string()],
    };

    (risk_level, interventions)
}

/// Get current real-time learning metrics
pub fn get_real_time_metrics() -> RealTimeLearningMetrics {
    // Return a clone to avoid holding the lock
    REAL_TIME_METRICS.lock().clone()
}

impl Clone for RealTimeLearningMetrics {
    fn clone(&self) -> Self {
        Self {
            active_learners: self.active_learners,
            current_average_consciousness: self.current_average_consciousness,
            learning_effectiveness_trend: self.learning_effectiveness_trend,
            engagement_metrics: EngagementMetrics {
                average_engagement: self.engagement_metrics.average_engagement,
                engagement_trend: self.engagement_metrics.engagement_trend,
                peak_engagement_time: self.engagement_metrics.peak_engagement_time,
                low_engagement_indicators: self
                    .engagement_metrics
                    .low_engagement_indicators
                    .clone(),
            },
            performance_distribution: PerformanceDistribution {
                excellent_performance: self.performance_distribution.excellent_performance,
                good_performance: self.performance_distribution.good_performance,
                average_performance: self.performance_distribution.average_performance,
                poor_performance: self.performance_distribution.poor_performance,
            },
        }
    }
}
