//! Minimal Advanced Applications - V1.0 Compatible
//! 
//! This is a simplified version that actually compiles and works
//! in the no_std kernel environment.

extern crate alloc;
use alloc::string::String;
use alloc::vec::Vec;
use alloc::format;
use core::sync::atomic::{AtomicBool, AtomicU64, Ordering};

/// Global applications state
static APPS_ACTIVE: AtomicBool = AtomicBool::new(false);
static CHALLENGE_COUNT: AtomicU64 = AtomicU64::new(0);

/// Simple challenge difficulty
#[derive(Debug, Clone, Copy)]
pub enum ChallengeDifficulty {
    Easy,
    Medium,
    Hard,
}

/// Basic CTF challenge
#[derive(Debug, Clone)]
pub struct Challenge {
    pub id: u64,
    pub title: String,
    pub difficulty: ChallengeDifficulty,
    pub points: u32,
}

/// Simple bias analysis result
#[derive(Debug, Clone)]
pub struct BiasAnalysis {
    pub content: String,
    pub bias_score: f32,
    pub detected_issues: Vec<String>,
}

/// Initialize applications
pub fn init() {
    APPS_ACTIVE.store(true, Ordering::SeqCst);
}

/// Check if apps are active
pub fn is_apps_active() -> bool {
    APPS_ACTIVE.load(Ordering::SeqCst)
}

/// Check if applications are active
#[allow(dead_code)]
pub fn is_advanced_apps_active() -> bool {
    APPS_ACTIVE.load(Ordering::SeqCst)
}

/// Generate a simple CTF challenge
#[allow(dead_code)]
pub fn generate_simple_challenge(difficulty: ChallengeDifficulty) -> Challenge {
    let challenge_id = CHALLENGE_COUNT.fetch_add(1, Ordering::SeqCst);
    
    let (title, points) = match difficulty {
        ChallengeDifficulty::Easy => ("Basic Buffer Overflow", 100),
        ChallengeDifficulty::Medium => ("Web SQL Injection", 250),
        ChallengeDifficulty::Hard => ("Reverse Engineering", 500),
    };
    
    Challenge {
        id: challenge_id,
        title: title.into(),
        difficulty,
        points,
    }
}

/// Simple bias analysis
pub fn analyze_content_bias(content: &str) -> BiasAnalysis {
    let mut bias_score = 0.0f32;
    let mut issues = Vec::new();
    
    // Simple keyword-based bias detection
    let bias_keywords = ["shocking", "devastating", "must", "only", "always", "never"];
    
    for keyword in bias_keywords.iter() {
        if content.to_lowercase().contains(keyword) {
            bias_score += 0.2;
            issues.push(format!("Potential bias keyword: {}", keyword).into());
        }
    }
    
    // Cap at 1.0
    if bias_score > 1.0 {
        bias_score = 1.0;
    }
    
    BiasAnalysis {
        content: content.into(),
        bias_score,
        detected_issues: issues,
    }
}

/// Get simple package recommendation
pub fn get_basic_package_recommendation(category: &str) -> String {
    match category {
        "security" => "Basic Security Tools".into(),
        "development" => "Essential Dev Tools".into(),
        "education" => "Learning Resources".into(),
        _ => "General Purpose Tools".into(),
    }
}

/// Get application statistics
pub fn get_application_stats() -> (u64, bool) {
    (
        CHALLENGE_COUNT.load(Ordering::SeqCst),
        is_advanced_apps_active()
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_advanced_apps_initialization() {
        init();
        assert!(is_advanced_apps_active());
    }

    #[test]
    fn test_ctf_generation() {
        init();
        let challenge = generate_simple_challenge(ChallengeDifficulty::Easy);
        assert!(!challenge.title.is_empty());
        assert!(challenge.points > 0);
    }

    #[test]
    fn test_bias_analysis() {
        init();
        let biased_content = "This shocking news proves that we must choose between only two devastating options!";
        let result = analyze_content_bias(biased_content);
        assert!(!result.detected_issues.is_empty());
        assert!(result.bias_score > 0.0);
    }

    #[test]
    fn test_package_recommendation() {
        init();
        let rec = get_basic_package_recommendation("security");
        assert!(!rec.is_empty());
    }
}
