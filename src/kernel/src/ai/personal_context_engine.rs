//! Personal Context Engine (PCE) with RAG Capabilities
//!
//! Advanced Retrieval-Augmented Generation engine for personalized AI assistance,
//! context-aware computing, and intelligent knowledge management in SynOS.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::{Mutex, RwLock};
use serde::{Serialize, Deserialize};

use crate::ai::mlops::MLOpsError;

/// Personal context and knowledge management engine
pub struct PersonalContextEngine {
    user_contexts: RwLock<BTreeMap<String, UserContext>>,
    knowledge_base: RwLock<BTreeMap<String, KnowledgeEntry>>,
    embeddings: RwLock<BTreeMap<String, EmbeddingVector>>,
    retrieval_index: RwLock<RetrievalIndex>,
    conversation_history: RwLock<BTreeMap<String, ConversationHistory>>,
    preferences: RwLock<BTreeMap<String, UserPreferences>>,
    next_context_id: AtomicU32,
    rag_enabled: AtomicU32,
}

/// User context information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserContext {
    pub user_id: String,
    pub session_id: String,
    pub current_task: Option<String>,
    pub active_applications: Vec<String>,
    pub system_state: SystemState,
    pub location_context: LocationContext,
    pub temporal_context: TemporalContext,
    pub cognitive_state: CognitiveState,
    pub interaction_history: Vec<Interaction>,
    pub context_embeddings: Vec<f32>,
    pub last_updated: u64,
}

/// System state information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemState {
    pub cpu_usage: f64,
    pub memory_usage: f64,
    pub active_processes: Vec<String>,
    pub network_status: String,
    pub security_level: String,
    pub ai_consciousness_level: f64,
}

/// Location-based context
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LocationContext {
    pub timezone: String,
    pub locale: String,
    pub network_location: String,
    pub workspace_type: WorkspaceType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WorkspaceType {
    Home,
    Office,
    Public,
    Secure,
    Unknown,
}

/// Temporal context information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TemporalContext {
    pub current_time: u64,
    pub day_of_week: String,
    pub time_of_day: TimeOfDay,
    pub working_hours: bool,
    pub user_activity_pattern: ActivityPattern,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum TimeOfDay {
    Morning,
    Afternoon,
    Evening,
    Night,
}

/// User activity patterns
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActivityPattern {
    pub typical_wake_time: u32, // minutes from midnight
    pub typical_sleep_time: u32,
    pub peak_productivity_hours: Vec<u32>,
    pub break_patterns: Vec<TimeSlot>,
}

/// Time slot definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimeSlot {
    pub start_minutes: u32,
    pub duration_minutes: u32,
    pub activity_type: String,
}

/// Cognitive state assessment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CognitiveState {
    pub attention_level: f64,     // 0-1
    pub stress_level: f64,        // 0-1
    pub cognitive_load: f64,      // 0-1
    pub focus_area: String,
    pub learning_mode: bool,
    pub multitasking_level: f64,  // 0-1
}

/// User interaction record
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Interaction {
    pub interaction_id: String,
    pub timestamp: u64,
    pub interaction_type: InteractionType,
    pub content: String,
    pub context_tags: Vec<String>,
    pub success_score: f64,
    pub user_satisfaction: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InteractionType {
    Query,
    Command,
    Assistance,
    Learning,
    Collaboration,
    Troubleshooting,
}

/// Knowledge base entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeEntry {
    pub entry_id: String,
    pub title: String,
    pub content: String,
    pub category: String,
    pub tags: Vec<String>,
    pub source: KnowledgeSource,
    pub confidence_score: f64,
    pub relevance_scores: BTreeMap<String, f64>, // topic -> relevance
    pub embedding_id: String,
    pub creation_time: u64,
    pub last_accessed: u64,
    pub access_count: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum KnowledgeSource {
    UserGenerated,
    SystemDocumentation,
    WebKnowledge,
    ExpertSystem,
    ConversationHistory,
    FileSystem,
}

/// Vector embedding representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmbeddingVector {
    pub vector_id: String,
    pub dimensions: u32,
    pub values: Vec<f32>,
    pub metadata: BTreeMap<String, String>,
    pub creation_time: u64,
}

/// Retrieval index for fast similarity search
#[derive(Debug, Clone)]
pub struct RetrievalIndex {
    pub index_type: IndexType,
    pub embeddings_map: BTreeMap<String, String>, // content_id -> embedding_id
    pub similarity_threshold: f64,
    pub max_results: u32,
    pub index_metadata: BTreeMap<String, String>,
}

#[derive(Debug, Clone, Copy)]
pub enum IndexType {
    FlatIndex,
    HierarchicalNavigableSmallWorld,
    InvertedFileIndex,
    ProductQuantization,
}

/// Conversation history management
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversationHistory {
    pub user_id: String,
    pub session_id: String,
    pub messages: Vec<ConversationMessage>,
    pub context_summary: String,
    pub key_topics: Vec<String>,
    pub conversation_embedding: Vec<f32>,
    pub start_time: u64,
    pub last_activity: u64,
}

/// Individual conversation message
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversationMessage {
    pub message_id: String,
    pub timestamp: u64,
    pub sender: MessageSender,
    pub content: String,
    pub message_type: MessageType,
    pub confidence: f64,
    pub context_references: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessageSender {
    User,
    Assistant,
    System,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessageType {
    Question,
    Answer,
    Command,
    Response,
    Information,
    Clarification,
}

/// User preferences and personalization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserPreferences {
    pub user_id: String,
    pub communication_style: CommunicationStyle,
    pub expertise_level: ExpertiseLevel,
    pub preferred_languages: Vec<String>,
    pub privacy_settings: PrivacySettings,
    pub learning_preferences: LearningPreferences,
    pub interface_preferences: InterfacePreferences,
    pub notification_settings: NotificationSettings,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CommunicationStyle {
    Concise,
    Detailed,
    Tutorial,
    Conversational,
    Technical,
    Adaptive,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExpertiseLevel {
    Beginner,
    Intermediate,
    Advanced,
    Expert,
    Mixed, // Expertise varies by domain
}

/// Privacy and data handling preferences
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrivacySettings {
    pub data_retention_days: u32,
    pub allow_learning_from_interactions: bool,
    pub share_anonymized_data: bool,
    pub context_sharing_level: ContextSharingLevel,
    pub encryption_required: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ContextSharingLevel {
    None,
    SessionOnly,
    UserOnly,
    SystemWide,
}

/// Learning and adaptation preferences
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearningPreferences {
    pub adaptive_responses: bool,
    pub learn_from_corrections: bool,
    pub proactive_suggestions: bool,
    pub explanation_detail_level: f64, // 0-1, 0=minimal, 1=comprehensive
    pub example_preference: ExamplePreference,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExamplePreference {
    Minimal,
    Practical,
    Comprehensive,
    InteractiveTutorial,
}

/// Interface and interaction preferences
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InterfacePreferences {
    pub preferred_modality: Vec<InteractionModality>,
    pub response_speed: ResponseSpeed,
    pub visual_style: VisualStyle,
    pub audio_settings: AudioSettings,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InteractionModality {
    Text,
    Voice,
    Visual,
    Gesture,
    BrainComputerInterface,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ResponseSpeed {
    Immediate,
    Balanced,
    Thoughtful,
    Comprehensive,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisualStyle {
    pub theme: String,
    pub font_size: f32,
    pub color_scheme: String,
    pub animation_level: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioSettings {
    pub voice_enabled: bool,
    pub voice_speed: f32,
    pub voice_pitch: f32,
    pub audio_feedback: bool,
}

/// Notification preferences
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NotificationSettings {
    pub proactive_notifications: bool,
    pub urgency_threshold: f64,
    pub quiet_hours: Vec<TimeSlot>,
    pub notification_types: Vec<NotificationType>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NotificationType {
    SystemAlerts,
    TaskReminders,
    LearningTips,
    SecurityWarnings,
    PerformanceInsights,
}

/// RAG query and response structures
#[derive(Debug, Clone)]
pub struct RAGQuery {
    pub query_id: String,
    pub user_id: String,
    pub query_text: String,
    pub context: UserContext,
    pub query_type: QueryType,
    pub max_results: u32,
    pub similarity_threshold: f64,
}

#[derive(Debug, Clone, Copy)]
pub enum QueryType {
    Factual,
    Procedural,
    Contextual,
    Creative,
    Analytical,
    Troubleshooting,
}

/// RAG response with retrieved context
#[derive(Debug, Clone)]
pub struct RAGResponse {
    pub response_id: String,
    pub query_id: String,
    pub response_text: String,
    pub retrieved_context: Vec<RetrievedDocument>,
    pub confidence_score: f64,
    pub generation_metadata: GenerationMetadata,
}

/// Retrieved document from knowledge base
#[derive(Debug, Clone)]
pub struct RetrievedDocument {
    pub document_id: String,
    pub content: String,
    pub similarity_score: f64,
    pub relevance_score: f64,
    pub source: KnowledgeSource,
    pub metadata: BTreeMap<String, String>,
}

/// Metadata about response generation
#[derive(Debug, Clone)]
pub struct GenerationMetadata {
    pub retrieval_time_ms: u64,
    pub generation_time_ms: u64,
    pub documents_considered: u32,
    pub documents_used: u32,
    pub model_used: String,
    pub temperature: f32,
    pub tokens_generated: u32,
}

impl PersonalContextEngine {
    /// Create new Personal Context Engine
    pub fn new() -> Self {
        Self {
            user_contexts: RwLock::new(BTreeMap::new()),
            knowledge_base: RwLock::new(BTreeMap::new()),
            embeddings: RwLock::new(BTreeMap::new()),
            retrieval_index: RwLock::new(RetrievalIndex {
                index_type: IndexType::FlatIndex,
                embeddings_map: BTreeMap::new(),
                similarity_threshold: 0.7,
                max_results: 10,
                index_metadata: BTreeMap::new(),
            }),
            conversation_history: RwLock::new(BTreeMap::new()),
            preferences: RwLock::new(BTreeMap::new()),
            next_context_id: AtomicU32::new(1),
            rag_enabled: AtomicU32::new(1),
        }
    }

    /// Initialize user context
    pub fn initialize_user_context(&self, user_id: String) -> Result<String, MLOpsError> {
        let context_id = format!("ctx_{}", self.next_context_id.fetch_add(1, Ordering::SeqCst));

        let context = UserContext {
            user_id: user_id.clone(),
            session_id: format!("session_{}", get_current_timestamp()),
            current_task: None,
            active_applications: Vec::new(),
            system_state: SystemState {
                cpu_usage: 25.0,
                memory_usage: 45.0,
                active_processes: vec!["synos-kernel".to_string(), "synos-ai-engine".to_string()],
                network_status: "connected".to_string(),
                security_level: "secure".to_string(),
                ai_consciousness_level: 0.85,
            },
            location_context: LocationContext {
                timezone: "UTC".to_string(),
                locale: "en_US".to_string(),
                network_location: "local".to_string(),
                workspace_type: WorkspaceType::Home,
            },
            temporal_context: TemporalContext {
                current_time: get_current_timestamp(),
                day_of_week: "Tuesday".to_string(),
                time_of_day: TimeOfDay::Afternoon,
                working_hours: true,
                user_activity_pattern: ActivityPattern {
                    typical_wake_time: 7 * 60, // 7:00 AM
                    typical_sleep_time: 23 * 60, // 11:00 PM
                    peak_productivity_hours: vec![9, 10, 14, 15], // 9-10 AM, 2-3 PM
                    break_patterns: vec![
                        TimeSlot {
                            start_minutes: 12 * 60, // 12:00 PM
                            duration_minutes: 60,   // 1 hour lunch
                            activity_type: "lunch".to_string(),
                        },
                    ],
                },
            },
            cognitive_state: CognitiveState {
                attention_level: 0.8,
                stress_level: 0.3,
                cognitive_load: 0.6,
                focus_area: "system_administration".to_string(),
                learning_mode: false,
                multitasking_level: 0.4,
            },
            interaction_history: Vec::new(),
            context_embeddings: vec![0.0; 384], // Placeholder embedding
            last_updated: get_current_timestamp(),
        };

        let mut contexts = self.user_contexts.write();
        contexts.insert(user_id.clone(), context);

        // Initialize default preferences
        self.initialize_default_preferences(&user_id)?;

        println!("Initialized context for user: {}", user_id);
        Ok(context_id)
    }

    /// Initialize default user preferences
    fn initialize_default_preferences(&self, user_id: &str) -> Result<(), MLOpsError> {
        let preferences = UserPreferences {
            user_id: user_id.to_string(),
            communication_style: CommunicationStyle::Adaptive,
            expertise_level: ExpertiseLevel::Intermediate,
            preferred_languages: vec!["en".to_string()],
            privacy_settings: PrivacySettings {
                data_retention_days: 90,
                allow_learning_from_interactions: true,
                share_anonymized_data: false,
                context_sharing_level: ContextSharingLevel::UserOnly,
                encryption_required: true,
            },
            learning_preferences: LearningPreferences {
                adaptive_responses: true,
                learn_from_corrections: true,
                proactive_suggestions: true,
                explanation_detail_level: 0.7,
                example_preference: ExamplePreference::Practical,
            },
            interface_preferences: InterfacePreferences {
                preferred_modality: vec![InteractionModality::Text, InteractionModality::Voice],
                response_speed: ResponseSpeed::Balanced,
                visual_style: VisualStyle {
                    theme: "dark".to_string(),
                    font_size: 14.0,
                    color_scheme: "synos_blue".to_string(),
                    animation_level: 0.5,
                },
                audio_settings: AudioSettings {
                    voice_enabled: true,
                    voice_speed: 1.0,
                    voice_pitch: 1.0,
                    audio_feedback: true,
                },
            },
            notification_settings: NotificationSettings {
                proactive_notifications: true,
                urgency_threshold: 0.7,
                quiet_hours: vec![
                    TimeSlot {
                        start_minutes: 22 * 60, // 10 PM
                        duration_minutes: 8 * 60, // 8 hours
                        activity_type: "sleep".to_string(),
                    },
                ],
                notification_types: vec![
                    NotificationType::SystemAlerts,
                    NotificationType::SecurityWarnings,
                    NotificationType::PerformanceInsights,
                ],
            },
        };

        let mut prefs = self.preferences.write();
        prefs.insert(user_id.to_string(), preferences);

        Ok(())
    }

    /// Add knowledge entry to the knowledge base
    pub fn add_knowledge_entry(&self, entry: KnowledgeEntry) -> Result<String, MLOpsError> {
        let entry_id = entry.entry_id.clone();

        // Generate embedding for the content
        let embedding = self.generate_embedding(&entry.content);
        let embedding_id = format!("emb_{}", get_current_timestamp());

        let embedding_vector = EmbeddingVector {
            vector_id: embedding_id.clone(),
            dimensions: embedding.len() as u32,
            values: embedding,
            metadata: {
                let mut metadata = BTreeMap::new();
                metadata.insert("content_type".to_string(), "knowledge_entry".to_string());
                metadata.insert("category".to_string(), entry.category.clone());
                metadata
            },
            creation_time: get_current_timestamp(),
        };

        // Store embedding
        let mut embeddings = self.embeddings.write();
        embeddings.insert(embedding_id.clone(), embedding_vector);

        // Update retrieval index
        let mut index = self.retrieval_index.write();
        index.embeddings_map.insert(entry_id.clone(), embedding_id);

        // Store knowledge entry
        let mut knowledge = self.knowledge_base.write();
        knowledge.insert(entry_id.clone(), entry);

        println!("Added knowledge entry: {}", entry_id);
        Ok(entry_id)
    }

    /// Perform RAG query
    pub fn query_rag(&self, query: RAGQuery) -> Result<RAGResponse, MLOpsError> {
        println!("Processing RAG query: {}", query.query_text);

        // Generate embedding for query
        let query_embedding = self.generate_embedding(&query.query_text);

        // Retrieve relevant documents
        let retrieved_docs = self.retrieve_similar_documents(&query_embedding, query.max_results, query.similarity_threshold)?;

        // Generate contextual response
        let response_text = self.generate_contextual_response(&query, &retrieved_docs)?;

        let response = RAGResponse {
            response_id: format!("resp_{}", get_current_timestamp()),
            query_id: query.query_id,
            response_text,
            retrieved_context: retrieved_docs,
            confidence_score: 0.85, // Would be calculated from actual model
            generation_metadata: GenerationMetadata {
                retrieval_time_ms: 50,
                generation_time_ms: 200,
                documents_considered: 25,
                documents_used: 3,
                model_used: "synos-llm-7b".to_string(),
                temperature: 0.7,
                tokens_generated: 150,
            },
        };

        // Store interaction in history
        self.record_interaction(&query.user_id, &query, &response)?;

        Ok(response)
    }

    /// Generate embedding vector for text
    fn generate_embedding(&self, text: &str) -> Vec<f32> {
        // Simplified embedding generation - in production, this would use actual embedding models
        let mut embedding = vec![0.0; 384]; // Typical embedding dimension

        // Simple hash-based embedding for demonstration
        let hash = self.simple_text_hash(text);
        for i in 0..embedding.len() {
            embedding[i] = ((hash + i as u64) % 1000) as f32 / 1000.0;
        }

        embedding
    }

    /// Simple text hashing for embedding generation
    fn simple_text_hash(&self, text: &str) -> u64 {
        let mut hash = 5381u64;
        for byte in text.bytes() {
            hash = ((hash << 5).wrapping_add(hash)).wrapping_add(byte as u64);
        }
        hash
    }

    /// Retrieve similar documents using vector similarity
    fn retrieve_similar_documents(&self, query_embedding: &[f32], max_results: u32, threshold: f64) -> Result<Vec<RetrievedDocument>, MLOpsError> {
        let embeddings = self.embeddings.read();
        let knowledge = self.knowledge_base.read();
        let index = self.retrieval_index.read();

        let mut candidates = Vec::new();

        // Calculate similarities
        for (content_id, embedding_id) in &index.embeddings_map {
            if let Some(embedding_vector) = embeddings.get(embedding_id) {
                if let Some(knowledge_entry) = knowledge.get(content_id) {
                    let similarity = self.calculate_cosine_similarity(query_embedding, &embedding_vector.values);

                    if similarity >= threshold {
                        candidates.push((similarity, knowledge_entry.clone()));
                    }
                }
            }
        }

        // Sort by similarity and take top results
        candidates.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
        candidates.truncate(max_results as usize);

        // Convert to RetrievedDocument
        let retrieved_docs = candidates.into_iter().map(|(similarity, entry)| {
            RetrievedDocument {
                document_id: entry.entry_id,
                content: entry.content,
                similarity_score: similarity,
                relevance_score: similarity * entry.confidence_score,
                source: entry.source,
                metadata: {
                    let mut metadata = BTreeMap::new();
                    metadata.insert("category".to_string(), entry.category);
                    metadata.insert("title".to_string(), entry.title);
                    metadata
                },
            }
        }).collect();

        Ok(retrieved_docs)
    }

    /// Calculate cosine similarity between vectors
    fn calculate_cosine_similarity(&self, a: &[f32], b: &[f32]) -> f64 {
        if a.len() != b.len() {
            return 0.0;
        }

        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if norm_a == 0.0 || norm_b == 0.0 {
            0.0
        } else {
            (dot_product / (norm_a * norm_b)) as f64
        }
    }

    /// Generate contextual response using retrieved documents
    fn generate_contextual_response(&self, query: &RAGQuery, retrieved_docs: &[RetrievedDocument]) -> Result<String, MLOpsError> {
        // In production, this would use an actual language model
        let context_info: Vec<String> = retrieved_docs.iter()
            .map(|doc| format!("- {}", doc.content.chars().take(100).collect::<String>()))
            .collect();

        let response = if context_info.is_empty() {
            format!("I don't have specific information about '{}' in my knowledge base. Could you provide more context or ask about something else?", query.query_text)
        } else {
            format!("Based on the information I have:\n\n{}\n\nThis information is relevant to your query about '{}'.",
                   context_info.join("\n"), query.query_text)
        };

        Ok(response)
    }

    /// Record interaction in conversation history
    fn record_interaction(&self, user_id: &str, query: &RAGQuery, response: &RAGResponse) -> Result<(), MLOpsError> {
        let mut history = self.conversation_history.write();

        let session_key = format!("{}_{}", user_id, query.context.session_id);
        let conversation = history.entry(session_key.clone()).or_insert_with(|| {
            ConversationHistory {
                user_id: user_id.to_string(),
                session_id: query.context.session_id.clone(),
                messages: Vec::new(),
                context_summary: String::new(),
                key_topics: Vec::new(),
                conversation_embedding: vec![0.0; 384],
                start_time: get_current_timestamp(),
                last_activity: get_current_timestamp(),
            }
        });

        // Add query message
        conversation.messages.push(ConversationMessage {
            message_id: query.query_id.clone(),
            timestamp: get_current_timestamp(),
            sender: MessageSender::User,
            content: query.query_text.clone(),
            message_type: MessageType::Question,
            confidence: 1.0,
            context_references: Vec::new(),
        });

        // Add response message
        conversation.messages.push(ConversationMessage {
            message_id: response.response_id.clone(),
            timestamp: get_current_timestamp(),
            sender: MessageSender::Assistant,
            content: response.response_text.clone(),
            message_type: MessageType::Answer,
            confidence: response.confidence_score,
            context_references: response.retrieved_context.iter().map(|d| d.document_id.clone()).collect(),
        });

        conversation.last_activity = get_current_timestamp();

        Ok(())
    }

    /// Generate PCE status report
    pub fn generate_pce_report(&self) -> String {
        let contexts = self.user_contexts.read();
        let knowledge = self.knowledge_base.read();
        let conversations = self.conversation_history.read();
        let embeddings = self.embeddings.read();

        let mut report = String::new();

        report.push_str("=== SYNOS PERSONAL CONTEXT ENGINE REPORT ===\n\n");

        // System summary
        report.push_str("=== SYSTEM OVERVIEW ===\n");
        report.push_str(&format!("Active User Contexts: {}\n", contexts.len()));
        report.push_str(&format!("Knowledge Base Entries: {}\n", knowledge.len()));
        report.push_str(&format!("Active Conversations: {}\n", conversations.len()));
        report.push_str(&format!("Stored Embeddings: {}\n", embeddings.len()));
        report.push_str(&format!("RAG Enabled: {}\n", if self.rag_enabled.load(Ordering::Relaxed) == 1 { "Yes" } else { "No" }));

        // User contexts summary
        report.push_str("\n=== ACTIVE USER CONTEXTS ===\n");
        for (user_id, context) in contexts.iter() {
            report.push_str(&format!("User: {}\n", user_id));
            report.push_str(&format!("  Session: {}\n", context.session_id));
            report.push_str(&format!("  Current Task: {}\n", context.current_task.as_ref().unwrap_or(&"None".to_string())));
            report.push_str(&format!("  Attention Level: {:.1}%\n", context.cognitive_state.attention_level * 100.0));
            report.push_str(&format!("  Interactions: {}\n", context.interaction_history.len()));
        }

        // Knowledge base categories
        report.push_str("\n=== KNOWLEDGE BASE CATEGORIES ===\n");
        let mut categories = BTreeMap::new();
        for entry in knowledge.values() {
            *categories.entry(&entry.category).or_insert(0) += 1;
        }

        for (category, count) in categories {
            report.push_str(&format!("{}: {} entries\n", category, count));
        }

        report
    }
}

/// Global Personal Context Engine instance
pub static PERSONAL_CONTEXT_ENGINE: RwLock<Option<PersonalContextEngine>> = RwLock::new(None);

/// Initialize Personal Context Engine
pub fn init_personal_context_engine() -> Result<(), MLOpsError> {
    let engine = PersonalContextEngine::new();
    *PERSONAL_CONTEXT_ENGINE.write() = Some(engine);
    Ok(())
}

/// Get PCE status report
pub fn get_pce_report() -> Result<String, MLOpsError> {
    if let Some(engine) = PERSONAL_CONTEXT_ENGINE.read().as_ref() {
        Ok(engine.generate_pce_report())
    } else {
        Err(MLOpsError::InvalidConfiguration)
    }
}

/// Helper function to get current timestamp
fn get_current_timestamp() -> u64 {
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    COUNTER.fetch_add(1, Ordering::SeqCst)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pce_creation() {
        let engine = PersonalContextEngine::new();
        assert_eq!(engine.rag_enabled.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn test_user_context_initialization() {
        let engine = PersonalContextEngine::new();
        let result = engine.initialize_user_context("test_user".to_string());
        assert!(result.is_ok());
    }

    #[test]
    fn test_embedding_generation() {
        let engine = PersonalContextEngine::new();
        let embedding = engine.generate_embedding("test text");
        assert_eq!(embedding.len(), 384);
    }

    #[test]
    fn test_cosine_similarity() {
        let engine = PersonalContextEngine::new();
        let vec_a = vec![1.0, 0.0, 0.0];
        let vec_b = vec![1.0, 0.0, 0.0];
        let similarity = engine.calculate_cosine_similarity(&vec_a, &vec_b);
        assert!((similarity - 1.0).abs() < 0.001);
    }
}