//! Documentation and Help System
//!
//! Provides comprehensive documentation and context-sensitive help.

use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::collections::BTreeMap;

/// Documentation system
#[derive(Debug)]
pub struct DocumentationSystem {
    help_topics: BTreeMap<String, HelpTopic>,
    search_index: Vec<SearchEntry>,
    initialized: bool,
}

/// Help system wrapper
pub type HelpSystem = DocumentationSystem;

/// Help topic
#[derive(Debug, Clone)]
pub struct HelpTopic {
    pub topic_id: String,
    pub title: String,
    pub content: String,
    pub category: HelpCategory,
    pub tags: Vec<String>,
    pub related_topics: Vec<String>,
}

/// Help categories
#[derive(Debug, Clone, PartialEq)]
pub enum HelpCategory {
    General,
    SystemCommands,
    Configuration,
    Troubleshooting,
    AIFeatures,
    Security,
    Development,
}

/// Search index entry
#[derive(Debug, Clone)]
pub struct SearchEntry {
    pub topic_id: String,
    pub keywords: Vec<String>,
    pub relevance_score: f32,
}

impl DocumentationSystem {
    /// Create new documentation system
    pub fn new() -> Self {
        Self {
            help_topics: BTreeMap::new(),
            search_index: Vec::new(),
            initialized: false,
        }
    }
    
    /// Initialize documentation system
    pub async fn initialize(&mut self) -> Result<(), &'static str> {
        if self.initialized {
            return Err("Documentation system already initialized");
        }
        
        // Load default help topics
        self.load_default_topics().await?;
        
        // Build search index
        self.build_search_index().await?;
        
        self.initialized = true;
        Ok(())
    }
    
    /// Shutdown documentation system
    pub async fn shutdown(&mut self) -> Result<(), &'static str> {
        self.help_topics.clear();
        self.search_index.clear();
        self.initialized = false;
        Ok(())
    }
    
    /// Get help for a specific topic
    pub async fn get_help(&self, topic: &str) -> Result<String, &'static str> {
        if !self.initialized {
            return Err("Documentation system not initialized");
        }
        
        if let Some(help_topic) = self.help_topics.get(topic) {
            Ok(self.format_help_topic(help_topic))
        } else {
            // Try to find similar topics
            let suggestions = self.find_similar_topics(topic).await;
            if suggestions.is_empty() {
                Ok(format!("Help topic '{}' not found. Type 'help topics' to see available topics.", topic))
            } else {
                Ok(format!(
                    "Help topic '{}' not found. Did you mean one of these?\n{}",
                    topic,
                    suggestions.join("\n- ")
                ))
            }
        }
    }
    
    /// Search documentation
    pub async fn search(&self, query: &str) -> Result<Vec<String>, &'static str> {
        if !self.initialized {
            return Err("Documentation system not initialized");
        }
        
        let query_lowercase = query.to_lowercase();
        let query_words: Vec<&str> = query_lowercase.split_whitespace().collect();
        let mut results: Vec<(String, f32)> = Vec::new();
        
        // Search through index
        for entry in &self.search_index {
            let mut score = 0.0;
            for word in &query_words {
                for keyword in &entry.keywords {
                    if keyword.contains(word) {
                        score += entry.relevance_score;
                        if keyword == word {
                            score += 1.0; // Exact match bonus
                        }
                    }
                }
            }
            
            if score > 0.0 {
                results.push((entry.topic_id.clone(), score));
            }
        }
        
        // Sort by relevance
        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        
        Ok(results.into_iter().map(|(topic, _)| topic).take(10).collect())
    }
    
    /// List all available topics
    pub fn list_topics(&self) -> Vec<String> {
        self.help_topics.keys().cloned().collect()
    }
    
    /// Get topics by category
    pub fn get_topics_by_category(&self, category: HelpCategory) -> Vec<String> {
        self.help_topics.iter()
            .filter(|(_, topic)| topic.category == category)
            .map(|(id, _)| id.clone())
            .collect()
    }
    
    /// Add custom help topic
    pub async fn add_topic(&mut self, topic: HelpTopic) -> Result<(), &'static str> {
        self.help_topics.insert(topic.topic_id.clone(), topic.clone());
        
        // Update search index
        self.add_to_search_index(&topic).await?;
        
        Ok(())
    }
    
    /// Remove help topic
    pub async fn remove_topic(&mut self, topic_id: &str) -> Result<(), &'static str> {
        if self.help_topics.remove(topic_id).is_some() {
            // Remove from search index
            self.search_index.retain(|entry| entry.topic_id != topic_id);
            Ok(())
        } else {
            Err("Topic not found")
        }
    }
    
    // Private helper methods
    
    async fn load_default_topics(&mut self) -> Result<(), &'static str> {
        let topics = vec![
            HelpTopic {
                topic_id: String::from("overview"),
                title: String::from("SynOS Overview"),
                content: String::from(
                    "SynOS is a consciousness-aware operating system that integrates AI \
                    capabilities throughout the kernel. It provides:\n\
                    - AI-powered resource management\n\
                    - Adaptive system optimization\n\
                    - Intelligent security monitoring\n\
                    - Educational features for learning\n\n\
                    Use 'help <topic>' to learn more about specific features."
                ),
                category: HelpCategory::General,
                tags: vec![String::from("overview"), String::from("intro"), String::from("synos")],
                related_topics: vec![String::from("ai"), String::from("security")],
            },
            
            HelpTopic {
                topic_id: String::from("ai"),
                title: String::from("AI Consciousness System"),
                content: String::from(
                    "The AI consciousness system provides intelligent system management:\n\n\
                    - Adaptive learning from user behavior\n\
                    - Predictive resource allocation\n\
                    - Intelligent decision making\n\
                    - Pattern recognition and anomaly detection\n\n\
                    The AI system continuously learns and adapts to improve system \
                    performance and user experience."
                ),
                category: HelpCategory::AIFeatures,
                tags: vec![String::from("ai"), String::from("consciousness"), String::from("learning")],
                related_topics: vec![String::from("overview"), String::from("performance")],
            },
            
            HelpTopic {
                topic_id: String::from("security"),
                title: String::from("Security Features"),
                content: String::from(
                    "SynOS provides comprehensive security features:\n\n\
                    - Real-time threat detection\n\
                    - System hardening and protection\n\
                    - Access control and authentication\n\
                    - Security monitoring and auditing\n\
                    - Encryption services\n\n\
                    Security is integrated throughout the system with AI-powered \
                    threat analysis and response."
                ),
                category: HelpCategory::Security,
                tags: vec![String::from("security"), String::from("protection"), String::from("threats")],
                related_topics: vec![String::from("ai"), String::from("monitoring")],
            },
        ];
        
        for topic in topics {
            self.help_topics.insert(topic.topic_id.clone(), topic);
        }
        
        Ok(())
    }
    
    async fn build_search_index(&mut self) -> Result<(), &'static str> {
        self.search_index.clear();
        
        let topics: Vec<_> = self.help_topics.values().cloned().collect();
        for topic in topics {
            self.add_to_search_index(&topic).await?;
        }
        
        Ok(())
    }
    
    async fn add_to_search_index(&mut self, topic: &HelpTopic) -> Result<(), &'static str> {
        let mut keywords = topic.tags.clone();
        
        // Add words from title
        keywords.extend(
            topic.title.to_lowercase()
                .split_whitespace()
                .map(|s| s.to_string())
        );
        
        // Add words from content (first 100 characters)
        let content_preview = if topic.content.len() > 100 {
            &topic.content[..100]
        } else {
            &topic.content
        };
        
        keywords.extend(
            content_preview.to_lowercase()
                .split_whitespace()
                .map(|s| s.to_string())
        );
        
        let entry = SearchEntry {
            topic_id: topic.topic_id.clone(),
            keywords,
            relevance_score: 1.0,
        };
        
        self.search_index.push(entry);
        Ok(())
    }
    
    fn format_help_topic(&self, topic: &HelpTopic) -> String {
        let mut formatted = format!("{}\n{}\n\n{}", 
            topic.title, 
            "=".repeat(topic.title.len()),
            topic.content
        );
        
        if !topic.related_topics.is_empty() {
            formatted.push_str(&format!(
                "\n\nRelated topics: {}",
                topic.related_topics.join(", ")
            ));
        }
        
        formatted
    }
    
    async fn find_similar_topics(&self, query: &str) -> Vec<String> {
        let query_lower = query.to_lowercase();
        let mut similar: Vec<String> = Vec::new();
        
        for (topic_id, topic) in &self.help_topics {
            if topic_id.contains(&query_lower) || 
               topic.title.to_lowercase().contains(&query_lower) ||
               topic.tags.iter().any(|tag| tag.contains(&query_lower)) {
                similar.push(topic_id.clone());
            }
        }
        
        similar
    }
}
