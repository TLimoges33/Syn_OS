//! Consciousness integration for SynPkg
//! 
//! Provides AI-powered package recommendations, optimization,
//! and learning capabilities

use std::collections::HashMap;
use anyhow::{Result, anyhow};
use serde::{Deserialize, Serialize};

use crate::core::PackageInfo;
use crate::repository::PackageSource;

/// Package recommendation from consciousness engine
#[derive(Debug, Clone)]
pub struct PackageRecommendation {
    pub package: String,
    pub confidence: f64,
    pub reason: String,
    pub preferred_source: Option<PackageSource>,
}

/// Installation context for consciousness decision making
#[derive(Debug, Clone)]
pub enum InstallationContext {
    Operational,   // Production security operations
    Educational,   // Learning and training
    Research,      // Security research and development
    Testing,       // Penetration testing
    Forensics,     // Digital forensics investigation
}

impl InstallationContext {
    pub fn from_str(s: &str) -> Result<Self> {
        match s.to_lowercase().as_str() {
            "operational" => Ok(Self::Operational),
            "educational" => Ok(Self::Educational),
            "research" => Ok(Self::Research),
            "testing" => Ok(Self::Testing),
            "forensics" => Ok(Self::Forensics),
            _ => Err(anyhow!("Unknown installation context: {}", s)),
        }
    }
}

/// Consciousness engine for package management
pub struct ConsciousnessEngine {
    /// Learning data for package recommendations
    learning_data: HashMap<String, PackageLearningData>,
    /// User context patterns
    context_patterns: HashMap<String, ContextPattern>,
    /// Package compatibility matrix
    compatibility_matrix: HashMap<String, f64>,
}

/// Learning data for each package
#[derive(Debug, Clone, Serialize, Deserialize)]
struct PackageLearningData {
    installation_count: u32,
    success_rate: f64,
    average_usage_time: f64,
    contexts_used: Vec<String>,
    co_installed_packages: HashMap<String, u32>,
    user_feedback_score: f64,
}

/// Pattern data for different contexts
#[derive(Debug, Clone)]
struct ContextPattern {
    common_packages: Vec<String>,
    package_priorities: HashMap<String, f64>,
    typical_workflow: Vec<String>,
}

impl ConsciousnessEngine {
    /// Create new consciousness engine
    pub async fn new() -> Result<Self> {
        let mut engine = Self {
            learning_data: HashMap::new(),
            context_patterns: HashMap::new(),
            compatibility_matrix: HashMap::new(),
        };

        engine.initialize_default_patterns().await?;
        Ok(engine)
    }

    /// Initialize default consciousness patterns
    async fn initialize_default_patterns(&mut self) -> Result<()> {
        // Operational context pattern
        let operational_pattern = ContextPattern {
            common_packages: vec![
                "nmap".to_string(),
                "wireshark".to_string(),
                "metasploit-framework".to_string(),
                "burpsuite".to_string(),
            ],
            package_priorities: {
                let mut priorities = HashMap::new();
                priorities.insert("nmap".to_string(), 0.9);
                priorities.insert("wireshark".to_string(), 0.85);
                priorities.insert("metasploit-framework".to_string(), 0.8);
                priorities.insert("burpsuite".to_string(), 0.75);
                priorities
            },
            typical_workflow: vec![
                "reconnaissance".to_string(),
                "vulnerability-scanning".to_string(),
                "exploitation".to_string(),
                "post-exploitation".to_string(),
            ],
        };
        self.context_patterns.insert("operational".to_string(), operational_pattern);

        // Educational context pattern
        let educational_pattern = ContextPattern {
            common_packages: vec![
                "john".to_string(),
                "hashcat".to_string(),
                "aircrack-ng".to_string(),
                "sqlmap".to_string(),
            ],
            package_priorities: {
                let mut priorities = HashMap::new();
                priorities.insert("john".to_string(), 0.9);
                priorities.insert("hashcat".to_string(), 0.85);
                priorities.insert("aircrack-ng".to_string(), 0.8);
                priorities.insert("sqlmap".to_string(), 0.75);
                priorities
            },
            typical_workflow: vec![
                "fundamentals".to_string(),
                "hands-on-practice".to_string(),
                "skill-building".to_string(),
                "certification-prep".to_string(),
            ],
        };
        self.context_patterns.insert("educational".to_string(), educational_pattern);

        // Research context pattern
        let research_pattern = ContextPattern {
            common_packages: vec![
                "radare2".to_string(),
                "ghidra".to_string(),
                "volatility".to_string(),
                "yara".to_string(),
            ],
            package_priorities: {
                let mut priorities = HashMap::new();
                priorities.insert("radare2".to_string(), 0.95);
                priorities.insert("ghidra".to_string(), 0.9);
                priorities.insert("volatility".to_string(), 0.85);
                priorities.insert("yara".to_string(), 0.8);
                priorities
            },
            typical_workflow: vec![
                "analysis".to_string(),
                "reverse-engineering".to_string(),
                "malware-research".to_string(),
                "vulnerability-research".to_string(),
            ],
        };
        self.context_patterns.insert("research".to_string(), research_pattern);

        Ok(())
    }

    /// Get package recommendation based on name and context
    pub async fn recommend_package(
        &self,
        package_name: &str,
        context: &str,
        preferred_source: Option<&str>
    ) -> Result<PackageRecommendation> {
        let install_context = InstallationContext::from_str(context)?;
        
        // Get context pattern
        let pattern = self.context_patterns.get(context)
            .ok_or_else(|| anyhow!("Unknown context: {}", context))?;

        // Calculate confidence based on various factors
        let mut confidence: f64 = 0.5; // Base confidence

        // Boost confidence if package is common in this context
        if pattern.common_packages.contains(&package_name.to_string()) {
            confidence += 0.3;
        }

        // Check package priority in this context
        if let Some(&priority) = pattern.package_priorities.get(package_name) {
            confidence = confidence.max(priority);
        }

        // Check learning data
        if let Some(learning) = self.learning_data.get(package_name) {
            confidence += (learning.success_rate - 0.5) * 0.2;
            if learning.contexts_used.contains(&context.to_string()) {
                confidence += 0.1;
            }
        }

        // Determine preferred source based on context and package
        let recommended_source = match install_context {
            InstallationContext::Operational => {
                // Prefer Kali for operational tools
                if self.is_kali_package(package_name) {
                    Some(PackageSource::Kali)
                } else {
                    Some(PackageSource::SynOS)
                }
            },
            InstallationContext::Educational => {
                // Prefer educational-focused distributions
                Some(PackageSource::Parrot)
            },
            InstallationContext::Research => {
                // Prefer BlackArch for research tools
                Some(PackageSource::BlackArch)
            },
            InstallationContext::Testing => {
                Some(PackageSource::Kali)
            },
            InstallationContext::Forensics => {
                Some(PackageSource::SynOS)
            },
        };

        // Override with user preference if provided
        let final_source = if let Some(pref) = preferred_source {
            match pref {
                "kali" => Some(PackageSource::Kali),
                "blackarch" => Some(PackageSource::BlackArch),
                "parrot" => Some(PackageSource::Parrot),
                "synos" => Some(PackageSource::SynOS),
                _ => recommended_source,
            }
        } else {
            recommended_source
        };

        let reason = self.generate_recommendation_reason(package_name, context, confidence);

        Ok(PackageRecommendation {
            package: package_name.to_string(),
            confidence: confidence.min(1.0),
            reason,
            preferred_source: final_source,
        })
    }

    /// Generate human-readable reason for recommendation
    fn generate_recommendation_reason(&self, _package_name: &str, context: &str, confidence: f64) -> String {
        if confidence > 0.8 {
            format!("Highly recommended for {} context. This package is commonly used and has proven effectiveness.", context)
        } else if confidence > 0.6 {
            format!("Good choice for {} context. Package aligns well with typical workflows.", context)
        } else if confidence > 0.4 {
            format!("Suitable for {} context. Package may be useful but consider alternatives.", context)
        } else {
            format!("Limited recommendation for {} context. Consider if this package fits your specific needs.", context)
        }
    }

    /// Rank search results using consciousness insights
    pub async fn rank_search_results(&self, mut results: Vec<PackageInfo>, query: &str) -> Result<Vec<PackageInfo>> {
        // Sort by consciousness compatibility and relevance
        results.sort_by(|a, b| {
            let score_a = self.calculate_relevance_score(a, query);
            let score_b = self.calculate_relevance_score(b, query);
            score_b.partial_cmp(&score_a).unwrap_or(std::cmp::Ordering::Equal)
        });

        Ok(results)
    }

    /// Calculate relevance score for search ranking
    fn calculate_relevance_score(&self, package: &PackageInfo, query: &str) -> f64 {
        let mut score = 0.0;

        // Exact name match gets highest score
        if package.name == query {
            score += 1.0;
        } else if package.name.contains(query) {
            score += 0.8;
        }

        // Description relevance
        if package.description.to_lowercase().contains(&query.to_lowercase()) {
            score += 0.3;
        }

        // Consciousness compatibility boost
        score += package.consciousness_compatibility * 0.2;

        // Educational value boost
        score += (package.educational_value as f64 / 10.0) * 0.1;

        // Source preference (SynOS packages get slight boost)
        if package.source == PackageSource::SynOS {
            score += 0.1;
        }

        score
    }

    /// Get general recommendations for a context
    pub async fn get_recommendations(&self, context: &str) -> Result<Vec<PackageRecommendation>> {
        let pattern = self.context_patterns.get(context)
            .ok_or_else(|| anyhow!("Unknown context: {}", context))?;

        let mut recommendations = Vec::new();

        for package_name in &pattern.common_packages {
            let recommendation = self.recommend_package(package_name, context, None).await?;
            recommendations.push(recommendation);
        }

        // Sort by confidence
        recommendations.sort_by(|a, b| b.confidence.partial_cmp(&a.confidence).unwrap_or(std::cmp::Ordering::Equal));

        Ok(recommendations)
    }

    /// Optimize upgrade order using consciousness insights
    pub async fn optimize_upgrade_order(&self, packages: &[String]) -> Result<Vec<String>> {
        let mut prioritized: Vec<(String, f64)> = packages.iter()
            .map(|pkg| {
                let priority = self.calculate_upgrade_priority(pkg);
                (pkg.clone(), priority)
            })
            .collect();

        // Sort by priority (highest first)
        prioritized.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        Ok(prioritized.into_iter().map(|(pkg, _)| pkg).collect())
    }

    /// Calculate upgrade priority for a package
    fn calculate_upgrade_priority(&self, package_name: &str) -> f64 {
        let mut priority = 0.5; // Base priority

        // Security packages get higher priority
        if self.is_security_package(package_name) {
            priority += 0.3;
        }

        // System packages get higher priority
        if self.is_system_package(package_name) {
            priority += 0.2;
        }

        // Check learning data for usage patterns
        if let Some(learning) = self.learning_data.get(package_name) {
            priority += learning.average_usage_time * 0.1;
        }

        priority.min(1.0)
    }

    /// Suggest package optimizations
    pub async fn suggest_optimizations(&self, installed_packages: &[String]) -> Result<Vec<String>> {
        let mut suggestions = Vec::new();

        // Look for unused packages
        for package in installed_packages {
            if let Some(learning) = self.learning_data.get(package) {
                if learning.average_usage_time < 0.1 {
                    suggestions.push(format!("Consider removing '{}' - rarely used", package));
                }
            }
        }

        // Look for missing complementary packages
        for package in installed_packages {
            if let Some(learning) = self.learning_data.get(package) {
                for (complement, count) in &learning.co_installed_packages {
                    if *count > 5 && !installed_packages.contains(complement) {
                        suggestions.push(format!("Consider installing '{}' - often used with '{}'", complement, package));
                    }
                }
            }
        }

        Ok(suggestions)
    }

    /// Record installation outcome for learning
    pub async fn record_installation(&mut self, package_name: &str, context: &str, success: bool) -> Result<()> {
        let learning_data = self.learning_data.entry(package_name.to_string())
            .or_insert_with(|| PackageLearningData {
                installation_count: 0,
                success_rate: 0.5,
                average_usage_time: 0.0,
                contexts_used: Vec::new(),
                co_installed_packages: HashMap::new(),
                user_feedback_score: 0.5,
            });

        learning_data.installation_count += 1;
        
        // Update success rate using exponential moving average
        let alpha = 0.1; // Learning rate
        let success_value = if success { 1.0 } else { 0.0 };
        learning_data.success_rate = (1.0 - alpha) * learning_data.success_rate + alpha * success_value;

        // Add context if not already tracked
        if !learning_data.contexts_used.contains(&context.to_string()) {
            learning_data.contexts_used.push(context.to_string());
        }

        Ok(())
    }

    /// Helper methods
    fn is_kali_package(&self, package_name: &str) -> bool {
        // Common Kali packages
        matches!(package_name, "nmap" | "metasploit-framework" | "wireshark" | "burpsuite" | "sqlmap" | "john" | "hashcat" | "aircrack-ng")
    }

    fn is_security_package(&self, package_name: &str) -> bool {
        package_name.contains("security") || 
        package_name.contains("crypto") ||
        package_name.contains("ssl") ||
        package_name.contains("firewall") ||
        self.is_kali_package(package_name)
    }

    fn is_system_package(&self, package_name: &str) -> bool {
        matches!(package_name, "kernel" | "systemd" | "glibc" | "openssl" | "bash" | "coreutils")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_consciousness_engine_creation() {
        let engine = ConsciousnessEngine::new().await.unwrap();
        assert!(engine.context_patterns.contains_key("operational"));
        assert!(engine.context_patterns.contains_key("educational"));
        assert!(engine.context_patterns.contains_key("research"));
    }

    #[tokio::test]
    async fn test_package_recommendation() {
        let engine = ConsciousnessEngine::new().await.unwrap();
        let recommendation = engine.recommend_package("nmap", "operational", None).await.unwrap();
        
        assert_eq!(recommendation.package, "nmap");
        assert!(recommendation.confidence > 0.5);
    }

    #[test]
    fn test_installation_context_parsing() {
        assert!(matches!(InstallationContext::from_str("operational").unwrap(), InstallationContext::Operational));
        assert!(matches!(InstallationContext::from_str("educational").unwrap(), InstallationContext::Educational));
        assert!(InstallationContext::from_str("invalid").is_err());
    }
}
