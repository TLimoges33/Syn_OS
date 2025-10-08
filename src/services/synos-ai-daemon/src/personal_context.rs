/// Personal Context Engine - RAG (Retrieval Augmented Generation)
/// Manages user context, learning history, and personalized AI responses

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info};

use crate::consciousness::ConsciousnessState;
use crate::vector_db::VectorDatabase;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserContext {
    pub user_id: String,
    pub skill_level: SkillLevel,
    pub learning_history: Vec<String>,
    pub completed_challenges: Vec<String>,
    pub preferences: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SkillLevel {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
}

#[derive(Debug)]
pub struct PersonalContextEngine {
    vector_db: Arc<VectorDatabase>,
    user_contexts: Arc<RwLock<HashMap<String, UserContext>>>,
    consciousness_insights: Arc<RwLock<Option<ConsciousnessState>>>,
}

impl PersonalContextEngine {
    pub async fn new(vector_db: Arc<VectorDatabase>) -> Result<Self> {
        info!("📚 Initializing Personal Context Engine with RAG");

        Ok(Self {
            vector_db,
            user_contexts: Arc::new(RwLock::new(HashMap::new())),
            consciousness_insights: Arc::new(RwLock::new(None)),
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("🚀 Personal Context Engine operational");

        loop {
            // Process context updates
            self.process_context_updates().await?;

            tokio::time::sleep(tokio::time::Duration::from_secs(30)).await;
        }
    }

    async fn process_context_updates(&self) -> Result<()> {
        let contexts = self.user_contexts.read().await;

        debug!("Processing context updates for {} users", contexts.len());

        // Update vector embeddings for each user context
        for (user_id, context) in contexts.iter() {
            self.update_user_embeddings(user_id, context).await?;
        }

        Ok(())
    }

    async fn update_user_embeddings(&self, user_id: &str, context: &UserContext) -> Result<()> {
        // Generate embedding from user context
        let context_text = format!(
            "User {}: Level {:?}, Challenges: {}",
            user_id,
            context.skill_level,
            context.completed_challenges.len()
        );

        // Store in vector database
        self.vector_db.store(user_id.to_string(), context_text).await?;

        Ok(())
    }

    pub async fn get_user_context(&self, user_id: &str) -> Result<Option<UserContext>> {
        let contexts = self.user_contexts.read().await;
        Ok(contexts.get(user_id).cloned())
    }

    pub async fn create_user_context(&self, user_id: String) -> Result<()> {
        let mut contexts = self.user_contexts.write().await;

        let context = UserContext {
            user_id: user_id.clone(),
            skill_level: SkillLevel::Beginner,
            learning_history: Vec::new(),
            completed_challenges: Vec::new(),
            preferences: HashMap::new(),
        };

        contexts.insert(user_id.clone(), context);
        info!("✓ Created context for user: {}", user_id);

        Ok(())
    }

    pub async fn update_consciousness_context(&self, state: ConsciousnessState) -> Result<()> {
        let mut insights = self.consciousness_insights.write().await;
        *insights = Some(state);

        debug!("Updated consciousness insights");
        Ok(())
    }

    pub async fn get_personalized_recommendation(&self, user_id: &str) -> Result<String> {
        let contexts = self.user_contexts.read().await;

        if let Some(context) = contexts.get(user_id) {
            // Use RAG to generate personalized recommendation
            let query = format!("Recommend next challenge for {:?} level user", context.skill_level);
            let results = self.vector_db.search(&query, 5).await?;

            if !results.is_empty() {
                return Ok(format!(
                    "Based on your {} level, try: {}",
                    match context.skill_level {
                        SkillLevel::Beginner => "beginner",
                        SkillLevel::Intermediate => "intermediate",
                        SkillLevel::Advanced => "advanced",
                        SkillLevel::Expert => "expert",
                    },
                    results[0]
                ));
            }
        }

        Ok("Start with beginner challenges".to_string())
    }
}
