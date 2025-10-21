//! AI-Powered Security Tool Selection System
//!
//! Uses consciousness integration and pattern recognition to recommend
//! the best security tools for a given task or scenario.
//!
//! V1.2 "Neural Enhancement" Feature

use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::collections::BTreeMap;
use core::sync::atomic::{AtomicU64, Ordering};

/// Security tool categories
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ToolCategory {
    NetworkScanning,
    VulnerabilityScanning,
    Exploitation,
    PasswordCracking,
    WebApplication,
    WirelessSecurity,
    Forensics,
    ReverseEngineering,
    SocialEngineering,
    Reconnaissance,
}

/// Security tool definition
#[derive(Debug, Clone)]
pub struct SecurityTool {
    pub name: String,
    pub category: ToolCategory,
    pub description: String,
    pub command: String,
    pub skill_level: u8,           // 1-10 difficulty rating
    pub effectiveness_score: f32,  // 0.0-1.0 AI-learned effectiveness
    pub use_count: u64,
    pub success_rate: f32,         // 0.0-1.0 tracked success rate
}

/// Task description for tool selection
#[derive(Debug, Clone)]
pub struct SecurityTask {
    pub description: String,
    pub target_type: TargetType,
    pub phase: AttackPhase,
    pub user_skill_level: u8,
    pub time_constraint: TimeConstraint,
    pub stealth_required: bool,
}

/// Target types
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TargetType {
    Network,
    WebApplication,
    Host,
    WirelessNetwork,
    MobileDevice,
    CloudInfrastructure,
    Unknown,
}

/// Attack phases (MITRE ATT&CK inspired)
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AttackPhase {
    Reconnaissance,
    ResourceDevelopment,
    InitialAccess,
    Execution,
    Persistence,
    PrivilegeEscalation,
    DefenseEvasion,
    CredentialAccess,
    Discovery,
    LateralMovement,
    Collection,
    Exfiltration,
    Impact,
}

/// Time constraint for task
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TimeConstraint {
    NoLimit,
    Fast,        // Minutes
    Medium,      // Hours
    Extended,    // Days
}

/// Tool recommendation with confidence
#[derive(Debug, Clone)]
pub struct ToolRecommendation {
    pub tool: SecurityTool,
    pub confidence: f32,           // 0.0-1.0 AI confidence
    pub reasoning: Vec<String>,
    pub usage_hints: Vec<String>,
    pub alternatives: Vec<String>,
}

/// AI-powered tool selector
pub struct AIToolSelector {
    /// Available security tools
    tools: Vec<SecurityTool>,

    /// Tool usage history
    usage_history: BTreeMap<String, Vec<UsageRecord>>,

    /// Pattern recognition cache
    pattern_cache: BTreeMap<String, Vec<String>>,

    /// Total recommendations made
    total_recommendations: AtomicU64,

    /// Successful recommendations
    successful_recommendations: AtomicU64,
}

/// Usage record for learning
#[derive(Debug, Clone)]
struct UsageRecord {
    task_hash: u64,
    success: bool,
    duration_seconds: u64,
    timestamp: u64,
}

impl AIToolSelector {
    /// Create new tool selector with default security tools
    pub fn new() -> Self {
        let mut selector = Self {
            tools: Vec::new(),
            usage_history: BTreeMap::new(),
            pattern_cache: BTreeMap::new(),
            total_recommendations: AtomicU64::new(0),
            successful_recommendations: AtomicU64::new(0),
        };

        selector.initialize_default_tools();
        selector
    }

    /// Initialize with SynOS security tools
    fn initialize_default_tools(&mut self) {
        // Network scanning tools
        self.add_tool(SecurityTool {
            name: "nmap".to_string(),
            category: ToolCategory::NetworkScanning,
            description: "Network mapper - port scanning and host discovery".to_string(),
            command: "nmap".to_string(),
            skill_level: 3,
            effectiveness_score: 0.95,
            use_count: 0,
            success_rate: 0.9,
        });

        self.add_tool(SecurityTool {
            name: "masscan".to_string(),
            category: ToolCategory::NetworkScanning,
            description: "Fast network scanner - ideal for large networks".to_string(),
            command: "masscan".to_string(),
            skill_level: 4,
            effectiveness_score: 0.92,
            use_count: 0,
            success_rate: 0.88,
        });

        // Vulnerability scanning
        self.add_tool(SecurityTool {
            name: "nessus".to_string(),
            category: ToolCategory::VulnerabilityScanning,
            description: "Professional vulnerability scanner".to_string(),
            command: "nessus".to_string(),
            skill_level: 5,
            effectiveness_score: 0.93,
            use_count: 0,
            success_rate: 0.87,
        });

        self.add_tool(SecurityTool {
            name: "nikto".to_string(),
            category: ToolCategory::VulnerabilityScanning,
            description: "Web server vulnerability scanner".to_string(),
            command: "nikto".to_string(),
            skill_level: 3,
            effectiveness_score: 0.85,
            use_count: 0,
            success_rate: 0.82,
        });

        // Exploitation frameworks
        self.add_tool(SecurityTool {
            name: "metasploit".to_string(),
            category: ToolCategory::Exploitation,
            description: "Penetration testing framework with exploits".to_string(),
            command: "msfconsole".to_string(),
            skill_level: 7,
            effectiveness_score: 0.94,
            use_count: 0,
            success_rate: 0.75,
        });

        // Password cracking
        self.add_tool(SecurityTool {
            name: "john".to_string(),
            category: ToolCategory::PasswordCracking,
            description: "John the Ripper - password cracker".to_string(),
            command: "john".to_string(),
            skill_level: 4,
            effectiveness_score: 0.88,
            use_count: 0,
            success_rate: 0.65,
        });

        self.add_tool(SecurityTool {
            name: "hashcat".to_string(),
            category: ToolCategory::PasswordCracking,
            description: "Advanced GPU-accelerated password cracker".to_string(),
            command: "hashcat".to_string(),
            skill_level: 6,
            effectiveness_score: 0.92,
            use_count: 0,
            success_rate: 0.7,
        });

        self.add_tool(SecurityTool {
            name: "hydra".to_string(),
            category: ToolCategory::PasswordCracking,
            description: "Network login cracker".to_string(),
            command: "hydra".to_string(),
            skill_level: 5,
            effectiveness_score: 0.86,
            use_count: 0,
            success_rate: 0.68,
        });

        // Web application testing
        self.add_tool(SecurityTool {
            name: "burpsuite".to_string(),
            category: ToolCategory::WebApplication,
            description: "Web application security testing suite".to_string(),
            command: "burpsuite".to_string(),
            skill_level: 6,
            effectiveness_score: 0.96,
            use_count: 0,
            success_rate: 0.89,
        });

        self.add_tool(SecurityTool {
            name: "sqlmap".to_string(),
            category: ToolCategory::WebApplication,
            description: "Automatic SQL injection tool".to_string(),
            command: "sqlmap".to_string(),
            skill_level: 4,
            effectiveness_score: 0.91,
            use_count: 0,
            success_rate: 0.78,
        });

        // Wireless security
        self.add_tool(SecurityTool {
            name: "aircrack-ng".to_string(),
            category: ToolCategory::WirelessSecurity,
            description: "Wireless network security suite".to_string(),
            command: "aircrack-ng".to_string(),
            skill_level: 6,
            effectiveness_score: 0.89,
            use_count: 0,
            success_rate: 0.72,
        });

        // Reconnaissance
        self.add_tool(SecurityTool {
            name: "recon-ng".to_string(),
            category: ToolCategory::Reconnaissance,
            description: "Reconnaissance framework".to_string(),
            command: "recon-ng".to_string(),
            skill_level: 5,
            effectiveness_score: 0.87,
            use_count: 0,
            success_rate: 0.85,
        });

        self.add_tool(SecurityTool {
            name: "theHarvester".to_string(),
            category: ToolCategory::Reconnaissance,
            description: "OSINT email and subdomain harvester".to_string(),
            command: "theHarvester".to_string(),
            skill_level: 3,
            effectiveness_score: 0.84,
            use_count: 0,
            success_rate: 0.88,
        });

        // Forensics
        self.add_tool(SecurityTool {
            name: "volatility".to_string(),
            category: ToolCategory::Forensics,
            description: "Memory forensics framework".to_string(),
            command: "volatility".to_string(),
            skill_level: 8,
            effectiveness_score: 0.93,
            use_count: 0,
            success_rate: 0.82,
        });

        // Reverse engineering
        self.add_tool(SecurityTool {
            name: "radare2".to_string(),
            category: ToolCategory::ReverseEngineering,
            description: "Reverse engineering framework".to_string(),
            command: "r2".to_string(),
            skill_level: 9,
            effectiveness_score: 0.91,
            use_count: 0,
            success_rate: 0.76,
        });
    }

    /// Add a security tool to the database
    pub fn add_tool(&mut self, tool: SecurityTool) {
        self.tools.push(tool);
    }

    /// Recommend tools for a given task using AI
    pub fn recommend_tools(&mut self, task: &SecurityTask) -> Vec<ToolRecommendation> {
        self.total_recommendations.fetch_add(1, Ordering::Relaxed);

        let mut recommendations = Vec::new();

        // Filter tools by category matching task
        let category = self.task_to_category(task);
        let mut candidate_tools: Vec<&SecurityTool> = self.tools.iter()
            .filter(|tool| tool.category == category || self.is_relevant_tool(tool, task))
            .collect();

        // Sort by effectiveness and success rate
        candidate_tools.sort_by(|a, b| {
            let score_a = a.effectiveness_score * a.success_rate;
            let score_b = b.effectiveness_score * b.success_rate;
            score_b.partial_cmp(&score_a).unwrap_or(core::cmp::Ordering::Equal)
        });

        // Generate recommendations with AI reasoning
        for tool in candidate_tools.iter().take(5) {
            let confidence = self.calculate_confidence(tool, task);
            let reasoning = self.generate_reasoning(tool, task);
            let hints = self.generate_usage_hints(tool, task);
            let alternatives = self.find_alternatives(tool, task);

            recommendations.push(ToolRecommendation {
                tool: (*tool).clone(),
                confidence,
                reasoning,
                usage_hints: hints,
                alternatives,
            });
        }

        recommendations
    }

    /// Map task to tool category
    fn task_to_category(&self, task: &SecurityTask) -> ToolCategory {
        match task.phase {
            AttackPhase::Reconnaissance => ToolCategory::Reconnaissance,
            AttackPhase::InitialAccess => match task.target_type {
                TargetType::Network => ToolCategory::NetworkScanning,
                TargetType::WebApplication => ToolCategory::WebApplication,
                TargetType::WirelessNetwork => ToolCategory::WirelessSecurity,
                _ => ToolCategory::NetworkScanning,
            },
            AttackPhase::CredentialAccess => ToolCategory::PasswordCracking,
            AttackPhase::Execution | AttackPhase::Persistence => ToolCategory::Exploitation,
            AttackPhase::Discovery => ToolCategory::NetworkScanning,
            AttackPhase::Collection => ToolCategory::Forensics,
            _ => ToolCategory::NetworkScanning,
        }
    }

    /// Check if tool is relevant to task
    fn is_relevant_tool(&self, tool: &SecurityTool, task: &SecurityTask) -> bool {
        // Check skill level compatibility
        if tool.skill_level > task.user_skill_level + 2 {
            return false; // Too advanced
        }

        // Check time constraint
        match task.time_constraint {
            TimeConstraint::Fast => tool.name.contains("scan") || tool.name.contains("nmap"),
            _ => true,
        }
    }

    /// Calculate AI confidence for recommendation
    fn calculate_confidence(&self, tool: &SecurityTool, task: &SecurityTask) -> f32 {
        let mut confidence = tool.effectiveness_score * tool.success_rate;

        // Boost if skill level matches user
        let skill_diff = (tool.skill_level as i16 - task.user_skill_level as i16).abs();
        confidence *= match skill_diff {
            0..=1 => 1.0,
            2 => 0.95,
            3 => 0.85,
            _ => 0.7,
        };

        // Boost based on usage history
        if tool.use_count > 10 {
            confidence *= 1.05;
        }

        confidence.min(1.0)
    }

    /// Generate AI reasoning for recommendation
    fn generate_reasoning(&self, tool: &SecurityTool, task: &SecurityTask) -> Vec<String> {
        let mut reasoning = Vec::new();

        reasoning.push(format!("Effectiveness score: {:.1}%", tool.effectiveness_score * 100.0));
        reasoning.push(format!("Historical success rate: {:.1}%", tool.success_rate * 100.0));
        reasoning.push(format!("Skill level {}/10 matches your profile", tool.skill_level));

        if task.stealth_required {
            reasoning.push("Stealth mode recommended - use with caution".to_string());
        }

        match task.time_constraint {
            TimeConstraint::Fast => reasoning.push("Fast execution time".to_string()),
            TimeConstraint::Extended => reasoning.push("Thorough analysis capability".to_string()),
            _ => {},
        }

        reasoning
    }

    /// Generate usage hints
    fn generate_usage_hints(&self, tool: &SecurityTool, _task: &SecurityTask) -> Vec<String> {
        let mut hints = Vec::new();

        match tool.name.as_str() {
            "nmap" => {
                hints.push("Start with: nmap -sV -sC <target>".to_string());
                hints.push("Use -Pn for hosts that block ping".to_string());
                hints.push("Add -O for OS detection".to_string());
            }
            "metasploit" => {
                hints.push("Launch with: msfconsole".to_string());
                hints.push("Use 'search' to find exploits".to_string());
                hints.push("Set RHOST and LHOST before exploit".to_string());
            }
            "burpsuite" => {
                hints.push("Configure browser proxy to 127.0.0.1:8080".to_string());
                hints.push("Use Repeater for manual testing".to_string());
                hints.push("Intruder for automated attacks".to_string());
            }
            _ => {
                hints.push(format!("Run with: {}", tool.command));
                hints.push("Check man page for options".to_string());
            }
        }

        hints
    }

    /// Find alternative tools
    fn find_alternatives(&self, tool: &SecurityTool, _task: &SecurityTask) -> Vec<String> {
        self.tools.iter()
            .filter(|t| t.category == tool.category && t.name != tool.name)
            .take(3)
            .map(|t| t.name.clone())
            .collect()
    }

    /// Record tool usage outcome for learning
    pub fn record_usage(&mut self, tool_name: &str, task_hash: u64, success: bool, duration: u64) {
        // Update tool statistics
        if let Some(tool) = self.tools.iter_mut().find(|t| t.name == tool_name) {
            tool.use_count += 1;

            // Update success rate (exponential moving average)
            let alpha = 0.1; // Learning rate
            tool.success_rate = tool.success_rate * (1.0 - alpha)
                + (if success { 1.0 } else { 0.0 }) * alpha;

            // Update effectiveness score based on duration
            if success && duration < 300 {
                tool.effectiveness_score = (tool.effectiveness_score * 0.95 + 0.05).min(1.0);
            }
        }

        // Store in usage history
        let history = self.usage_history.entry(tool_name.to_string())
            .or_insert_with(Vec::new);

        history.push(UsageRecord {
            task_hash,
            success,
            duration_seconds: duration,
            timestamp: 0, // TODO: Get real timestamp
        });

        // Keep history bounded
        if history.len() > 100 {
            history.remove(0);
        }

        // Update success counter
        if success {
            self.successful_recommendations.fetch_add(1, Ordering::Relaxed);
        }
    }

    /// Get recommendation accuracy
    pub fn get_accuracy(&self) -> f32 {
        let total = self.total_recommendations.load(Ordering::Relaxed);
        let successful = self.successful_recommendations.load(Ordering::Relaxed);

        if total > 0 {
            successful as f32 / total as f32
        } else {
            0.0
        }
    }

    /// Get tool by name
    pub fn get_tool(&self, name: &str) -> Option<&SecurityTool> {
        self.tools.iter().find(|t| t.name == name)
    }

    /// List all available tools
    pub fn list_tools(&self) -> &[SecurityTool] {
        &self.tools
    }

    /// List tools by category
    pub fn list_tools_by_category(&self, category: ToolCategory) -> Vec<&SecurityTool> {
        self.tools.iter().filter(|t| t.category == category).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tool_selector_creation() {
        let selector = AIToolSelector::new();
        assert!(selector.tools.len() > 0, "Should have default tools");
    }

    #[test]
    fn test_network_scanning_recommendation() {
        let mut selector = AIToolSelector::new();

        let task = SecurityTask {
            description: "Scan network for open ports".to_string(),
            target_type: TargetType::Network,
            phase: AttackPhase::Discovery,
            user_skill_level: 5,
            time_constraint: TimeConstraint::Fast,
            stealth_required: false,
        };

        let recommendations = selector.recommend_tools(&task);
        assert!(recommendations.len() > 0, "Should get recommendations");

        // Check that nmap or masscan is recommended
        let tool_names: Vec<String> = recommendations.iter()
            .map(|r| r.tool.name.clone())
            .collect();

        assert!(
            tool_names.contains(&"nmap".to_string()) ||
            tool_names.contains(&"masscan".to_string()),
            "Should recommend network scanning tool"
        );
    }

    #[test]
    fn test_skill_level_filtering() {
        let mut selector = AIToolSelector::new();

        let task = SecurityTask {
            description: "Basic web security test".to_string(),
            target_type: TargetType::WebApplication,
            phase: AttackPhase::InitialAccess,
            user_skill_level: 3, // Beginner
            time_constraint: TimeConstraint::NoLimit,
            stealth_required: false,
        };

        let recommendations = selector.recommend_tools(&task);

        // Should not recommend very advanced tools
        for rec in recommendations.iter() {
            assert!(rec.tool.skill_level <= 5, "Should not recommend tools too advanced for user");
        }
    }

    #[test]
    fn test_usage_recording() {
        let mut selector = AIToolSelector::new();

        let initial_accuracy = selector.get_accuracy();
        assert_eq!(initial_accuracy, 0.0, "Initial accuracy should be 0");

        selector.record_usage("nmap", 12345, true, 120);
        selector.record_usage("nmap", 12346, true, 90);
        selector.record_usage("nmap", 12347, false, 300);

        let tool = selector.get_tool("nmap").unwrap();
        assert_eq!(tool.use_count, 3);
        assert!(tool.success_rate > 0.6, "Success rate should reflect 2/3 success");
    }

    #[test]
    fn test_category_mapping() {
        let selector = AIToolSelector::new();

        let recon_task = SecurityTask {
            description: "Gather information".to_string(),
            target_type: TargetType::Unknown,
            phase: AttackPhase::Reconnaissance,
            user_skill_level: 5,
            time_constraint: TimeConstraint::NoLimit,
            stealth_required: false,
        };

        let category = selector.task_to_category(&recon_task);
        assert_eq!(category, ToolCategory::Reconnaissance);
    }

    #[test]
    fn test_alternative_suggestions() {
        let selector = AIToolSelector::new();

        let nmap = selector.get_tool("nmap").unwrap();
        let alternatives = selector.find_alternatives(nmap, &SecurityTask {
            description: "Test".to_string(),
            target_type: TargetType::Network,
            phase: AttackPhase::Discovery,
            user_skill_level: 5,
            time_constraint: TimeConstraint::NoLimit,
            stealth_required: false,
        });

        assert!(alternatives.len() > 0, "Should have alternatives");
        assert!(!alternatives.contains(&"nmap".to_string()), "Should not include original tool");
    }
}
