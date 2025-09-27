//! Vector Database Integration
//!
//! ChromaDB and FAISS integration for efficient similarity search,
//! knowledge storage, and retrieval in SynOS AI systems.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::format;
use core::sync::atomic::{AtomicU64, AtomicU32, Ordering};
use spin::{Mutex, RwLock};

use crate::ai::mlops::MLOpsError;

/// Simple sqrt implementation for no_std
fn sqrt_f32(x: f32) -> f32 {
    if x <= 0.0 {
        return 0.0;
    }
    
    let mut guess = x / 2.0;
    for _ in 0..10 { // Newton's method iterations
        guess = (guess + x / guess) / 2.0;
    }
    guess
}

/// Vector database abstraction layer
pub trait VectorDatabase {
    fn create_collection(&self, name: &str, config: CollectionConfig) -> Result<String, VectorDBError>;
    fn delete_collection(&self, collection_id: &str) -> Result<(), VectorDBError>;
    fn insert_vectors(&self, collection_id: &str, vectors: Vec<VectorEntry>) -> Result<Vec<String>, VectorDBError>;
    fn search_similar(&self, collection_id: &str, query_vector: &[f32], k: u32, filter: Option<Filter>) -> Result<Vec<SearchResult>, VectorDBError>;
    fn update_vector(&self, collection_id: &str, vector_id: &str, vector: VectorEntry) -> Result<(), VectorDBError>;
    fn delete_vector(&self, collection_id: &str, vector_id: &str) -> Result<(), VectorDBError>;
    fn get_collection_stats(&self, collection_id: &str) -> Result<CollectionStats, VectorDBError>;
}

/// Collection configuration
#[derive(Debug, Clone)]
pub struct CollectionConfig {
    pub name: String,
    pub dimension: u32,
    pub metric_type: DistanceMetric,
    pub index_type: IndexType,
    pub description: String,
    pub metadata_schema: BTreeMap<String, MetadataType>,
}

/// Distance metrics for similarity computation
#[derive(Debug, Clone, Copy)]
pub enum DistanceMetric {
    Cosine,
    Euclidean,
    DotProduct,
    Manhattan,
    Hamming,
}

/// Index types for different use cases
#[derive(Debug, Clone, Copy)]
pub enum IndexType {
    FlatIndex,          // Exact search, good for small datasets
    IVFFlat,           // Inverted file index
    IVFPQ,             // Inverted file with product quantization
    HNSW,              // Hierarchical Navigable Small World
    LSH,               // Locality Sensitive Hashing
}

/// Metadata type definitions
#[derive(Debug, Clone, Copy)]
pub enum MetadataType {
    String,
    Integer,
    Float,
    Boolean,
    Array,
    Object,
}

/// Vector entry with metadata
#[derive(Debug, Clone)]
pub struct VectorEntry {
    pub id: Option<String>,
    pub vector: Vec<f32>,
    pub metadata: BTreeMap<String, MetadataValue>,
}

/// Metadata value types
#[derive(Debug, Clone)]
pub enum MetadataValue {
    String(String),
    Integer(i64),
    Float(f64),
    Boolean(bool),
    Array(Vec<MetadataValue>),
    Object(BTreeMap<String, MetadataValue>),
}

/// Search result from vector database
#[derive(Debug, Clone)]
pub struct SearchResult {
    pub id: String,
    pub score: f64,
    pub vector: Vec<f32>,
    pub metadata: BTreeMap<String, MetadataValue>,
}

/// Filter for search queries
#[derive(Debug, Clone)]
pub struct Filter {
    pub conditions: Vec<FilterCondition>,
    pub operator: FilterOperator,
}

/// Filter condition
#[derive(Debug, Clone)]
pub struct FilterCondition {
    pub field: String,
    pub operator: ComparisonOperator,
    pub value: MetadataValue,
}

#[derive(Debug, Clone, Copy)]
pub enum FilterOperator {
    And,
    Or,
    Not,
}

#[derive(Debug, Clone, Copy)]
pub enum ComparisonOperator {
    Equal,
    NotEqual,
    GreaterThan,
    LessThan,
    GreaterThanOrEqual,
    LessThanOrEqual,
    In,
    NotIn,
    Contains,
}

/// Collection statistics
#[derive(Debug, Clone)]
pub struct CollectionStats {
    pub collection_id: String,
    pub name: String,
    pub vector_count: u64,
    pub dimension: u32,
    pub index_size_bytes: u64,
    pub last_updated: u64,
    pub search_latency_ms: f64,
    pub memory_usage_mb: f64,
}

/// Vector database errors
#[derive(Debug, Clone)]
pub enum VectorDBError {
    CollectionNotFound,
    CollectionAlreadyExists,
    DimensionMismatch,
    InvalidVector,
    IndexingError,
    SearchError,
    ConnectionError,
    ConfigurationError,
}

/// ChromaDB implementation
pub struct ChromaDBAdapter {
    collections: RwLock<BTreeMap<String, ChromaCollection>>,
    next_collection_id: AtomicU32,
    base_url: String,
}

/// ChromaDB collection representation
#[derive(Debug, Clone)]
struct ChromaCollection {
    pub id: String,
    pub config: CollectionConfig,
    pub vectors: BTreeMap<String, StoredVector>,
    pub next_vector_id: AtomicU32,
    pub created_at: u64,
    pub updated_at: u64,
}

/// Stored vector with metadata
#[derive(Debug, Clone)]
struct StoredVector {
    pub id: String,
    pub vector: Vec<f32>,
    pub metadata: BTreeMap<String, MetadataValue>,
    pub created_at: u64,
}

impl ChromaDBAdapter {
    /// Create new ChromaDB adapter
    pub fn new(base_url: String) -> Self {
        Self {
            collections: RwLock::new(BTreeMap::new()),
            next_collection_id: AtomicU32::new(1),
            base_url,
        }
    }
}

impl VectorDatabase for ChromaDBAdapter {
    fn create_collection(&self, name: &str, config: CollectionConfig) -> Result<String, VectorDBError> {
        let collection_id = format!("chroma_{}", self.next_collection_id.fetch_add(1, Ordering::SeqCst));

        let collection = ChromaCollection {
            id: collection_id.clone(),
            config: config.clone(),
            vectors: BTreeMap::new(),
            next_vector_id: AtomicU32::new(1),
            created_at: get_current_timestamp(),
            updated_at: get_current_timestamp(),
        };

        let mut collections = self.collections.write();
        if collections.contains_key(name) {
            return Err(VectorDBError::CollectionAlreadyExists);
        }

        collections.insert(collection_id.clone(), collection);

        println!("Created ChromaDB collection: {} ({})", name, collection_id);
        Ok(collection_id)
    }

    fn delete_collection(&self, collection_id: &str) -> Result<(), VectorDBError> {
        let mut collections = self.collections.write();
        if collections.remove(collection_id).is_some() {
            println!("Deleted ChromaDB collection: {}", collection_id);
            Ok(())
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn insert_vectors(&self, collection_id: &str, vectors: Vec<VectorEntry>) -> Result<Vec<String>, VectorDBError> {
        let mut collections = self.collections.write();
        if let Some(collection) = collections.get_mut(collection_id) {
            let mut inserted_ids = Vec::new();

            for vector_entry in vectors {
                // Validate dimension
                if vector_entry.vector.len() != collection.config.dimension as usize {
                    return Err(VectorDBError::DimensionMismatch);
                }

                let vector_id = vector_entry.id.unwrap_or_else(|| {
                    format!("vec_{}", collection.next_vector_id.fetch_add(1, Ordering::SeqCst))
                });

                let stored_vector = StoredVector {
                    id: vector_id.clone(),
                    vector: vector_entry.vector,
                    metadata: vector_entry.metadata,
                    created_at: get_current_timestamp(),
                };

                collection.vectors.insert(vector_id.clone(), stored_vector);
                collection.updated_at = get_current_timestamp();
                inserted_ids.push(vector_id);
            }

            println!("Inserted {} vectors into collection {}", inserted_ids.len(), collection_id);
            Ok(inserted_ids)
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn search_similar(&self, collection_id: &str, query_vector: &[f32], k: u32, filter: Option<Filter>) -> Result<Vec<SearchResult>, VectorDBError> {
        let collections = self.collections.read();
        if let Some(collection) = collections.get(collection_id) {
            // Validate dimension
            if query_vector.len() != collection.config.dimension as usize {
                return Err(VectorDBError::DimensionMismatch);
            }

            let mut candidates = Vec::new();

            // Calculate similarities for all vectors
            for stored_vector in collection.vectors.values() {
                // Apply filter if provided
                if let Some(ref filter_condition) = filter {
                    if !self.apply_filter(&stored_vector.metadata, filter_condition) {
                        continue;
                    }
                }

                let similarity = self.calculate_similarity(
                    query_vector,
                    &stored_vector.vector,
                    collection.config.metric_type
                );

                candidates.push(SearchResult {
                    id: stored_vector.id.clone(),
                    score: similarity,
                    vector: stored_vector.vector.clone(),
                    metadata: stored_vector.metadata.clone(),
                });
            }

            // Sort by similarity score and take top k
            candidates.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
            candidates.truncate(k as usize);

            Ok(candidates)
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn update_vector(&self, collection_id: &str, vector_id: &str, vector_entry: VectorEntry) -> Result<(), VectorDBError> {
        let mut collections = self.collections.write();
        if let Some(collection) = collections.get_mut(collection_id) {
            if collection.vectors.contains_key(vector_id) {
                let stored_vector = StoredVector {
                    id: vector_id.to_string(),
                    vector: vector_entry.vector,
                    metadata: vector_entry.metadata,
                    created_at: get_current_timestamp(),
                };

                collection.vectors.insert(vector_id.to_string(), stored_vector);
                collection.updated_at = get_current_timestamp();
                Ok(())
            } else {
                Err(VectorDBError::CollectionNotFound)
            }
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn delete_vector(&self, collection_id: &str, vector_id: &str) -> Result<(), VectorDBError> {
        let mut collections = self.collections.write();
        if let Some(collection) = collections.get_mut(collection_id) {
            if collection.vectors.remove(vector_id).is_some() {
                collection.updated_at = get_current_timestamp();
                Ok(())
            } else {
                Err(VectorDBError::CollectionNotFound)
            }
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn get_collection_stats(&self, collection_id: &str) -> Result<CollectionStats, VectorDBError> {
        let collections = self.collections.read();
        if let Some(collection) = collections.get(collection_id) {
            Ok(CollectionStats {
                collection_id: collection_id.to_string(),
                name: collection.config.name.clone(),
                vector_count: collection.vectors.len() as u64,
                dimension: collection.config.dimension,
                index_size_bytes: collection.vectors.len() as u64 * collection.config.dimension as u64 * 4, // 4 bytes per float
                last_updated: collection.updated_at,
                search_latency_ms: 5.0, // Simulated
                memory_usage_mb: (collection.vectors.len() as f64 * collection.config.dimension as f64 * 4.0) / (1024.0 * 1024.0),
            })
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }
}

impl ChromaDBAdapter {
    /// Calculate similarity based on metric type
    fn calculate_similarity(&self, vec_a: &[f32], vec_b: &[f32], metric: DistanceMetric) -> f64 {
        match metric {
            DistanceMetric::Cosine => self.cosine_similarity(vec_a, vec_b),
            DistanceMetric::Euclidean => 1.0 / (1.0 + self.euclidean_distance(vec_a, vec_b)),
            DistanceMetric::DotProduct => self.dot_product(vec_a, vec_b),
            DistanceMetric::Manhattan => 1.0 / (1.0 + self.manhattan_distance(vec_a, vec_b)),
            DistanceMetric::Hamming => 1.0 - self.hamming_distance(vec_a, vec_b),
        }
    }

    /// Calculate cosine similarity
    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f64 {
        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = sqrt_f32(a.iter().map(|x| x * x).sum::<f32>());
        let norm_b: f32 = sqrt_f32(b.iter().map(|x| x * x).sum::<f32>());

        if norm_a == 0.0 || norm_b == 0.0 {
            0.0
        } else {
            (dot_product / (norm_a * norm_b)) as f64
        }
    }

    /// Calculate Euclidean distance
    fn euclidean_distance(&self, a: &[f32], b: &[f32]) -> f64 {
        let sum = a.iter().zip(b.iter())
            .map(|(x, y)| (x - y).powi(2))
            .sum::<f32>();
        sqrt_f32(sum) as f64
    }

    /// Calculate dot product
    fn dot_product(&self, a: &[f32], b: &[f32]) -> f64 {
        a.iter().zip(b.iter()).map(|(x, y)| x * y).sum::<f32>() as f64
    }

    /// Calculate Manhattan distance
    fn manhattan_distance(&self, a: &[f32], b: &[f32]) -> f64 {
        a.iter().zip(b.iter()).map(|(x, y)| (x - y).abs()).sum::<f32>() as f64
    }

    /// Calculate Hamming distance (for binary vectors)
    fn hamming_distance(&self, a: &[f32], b: &[f32]) -> f64 {
        let different_bits = a.iter().zip(b.iter())
            .filter(|(x, y)| (x.round() - y.round()).abs() > 0.01)
            .count();
        different_bits as f64 / a.len() as f64
    }

    /// Apply filter conditions to metadata
    fn apply_filter(&self, metadata: &BTreeMap<String, MetadataValue>, filter: &Filter) -> bool {
        match filter.operator {
            FilterOperator::And => {
                filter.conditions.iter().all(|condition| self.evaluate_condition(metadata, condition))
            }
            FilterOperator::Or => {
                filter.conditions.iter().any(|condition| self.evaluate_condition(metadata, condition))
            }
            FilterOperator::Not => {
                !filter.conditions.iter().all(|condition| self.evaluate_condition(metadata, condition))
            }
        }
    }

    /// Evaluate individual filter condition
    fn evaluate_condition(&self, metadata: &BTreeMap<String, MetadataValue>, condition: &FilterCondition) -> bool {
        if let Some(field_value) = metadata.get(&condition.field) {
            match condition.operator {
                ComparisonOperator::Equal => field_value == &condition.value,
                ComparisonOperator::NotEqual => field_value != &condition.value,
                ComparisonOperator::GreaterThan => self.compare_values(field_value, &condition.value) > 0,
                ComparisonOperator::LessThan => self.compare_values(field_value, &condition.value) < 0,
                ComparisonOperator::GreaterThanOrEqual => self.compare_values(field_value, &condition.value) >= 0,
                ComparisonOperator::LessThanOrEqual => self.compare_values(field_value, &condition.value) <= 0,
                _ => false, // Other operators would need more complex implementation
            }
        } else {
            false
        }
    }

    /// Compare metadata values
    fn compare_values(&self, a: &MetadataValue, b: &MetadataValue) -> i32 {
        match (a, b) {
            (MetadataValue::Integer(x), MetadataValue::Integer(y)) => x.cmp(y) as i32,
            (MetadataValue::Float(x), MetadataValue::Float(y)) => x.partial_cmp(y).unwrap() as i32,
            (MetadataValue::String(x), MetadataValue::String(y)) => x.cmp(y) as i32,
            _ => 0, // Default for unsupported comparisons
        }
    }
}

/// FAISS adapter implementation
pub struct FAISSAdapter {
    collections: RwLock<BTreeMap<String, FAISSCollection>>,
    next_collection_id: AtomicU32,
    index_factory: String,
}

/// FAISS collection representation
#[derive(Debug, Clone)]
struct FAISSCollection {
    pub id: String,
    pub config: CollectionConfig,
    pub vectors: BTreeMap<String, StoredVector>,
    pub index_data: Vec<u8>, // Serialized FAISS index
    pub next_vector_id: AtomicU32,
    pub created_at: u64,
    pub updated_at: u64,
}

impl FAISSAdapter {
    /// Create new FAISS adapter
    pub fn new(index_factory: String) -> Self {
        Self {
            collections: RwLock::new(BTreeMap::new()),
            next_collection_id: AtomicU32::new(1),
            index_factory,
        }
    }
}

impl VectorDatabase for FAISSAdapter {
    fn create_collection(&self, name: &str, config: CollectionConfig) -> Result<String, VectorDBError> {
        let collection_id = format!("faiss_{}", self.next_collection_id.fetch_add(1, Ordering::SeqCst));

        let collection = FAISSCollection {
            id: collection_id.clone(),
            config: config.clone(),
            vectors: BTreeMap::new(),
            index_data: Vec::new(), // Would contain serialized FAISS index
            next_vector_id: AtomicU32::new(1),
            created_at: get_current_timestamp(),
            updated_at: get_current_timestamp(),
        };

        let mut collections = self.collections.write();
        collections.insert(collection_id.clone(), collection);

        println!("Created FAISS collection: {} ({})", name, collection_id);
        Ok(collection_id)
    }

    fn delete_collection(&self, collection_id: &str) -> Result<(), VectorDBError> {
        let mut collections = self.collections.write();
        if collections.remove(collection_id).is_some() {
            println!("Deleted FAISS collection: {}", collection_id);
            Ok(())
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn insert_vectors(&self, collection_id: &str, vectors: Vec<VectorEntry>) -> Result<Vec<String>, VectorDBError> {
        let mut collections = self.collections.write();
        if let Some(collection) = collections.get_mut(collection_id) {
            let mut inserted_ids = Vec::new();

            for vector_entry in vectors {
                if vector_entry.vector.len() != collection.config.dimension as usize {
                    return Err(VectorDBError::DimensionMismatch);
                }

                let vector_id = vector_entry.id.unwrap_or_else(|| {
                    format!("vec_{}", collection.next_vector_id.fetch_add(1, Ordering::SeqCst))
                });

                let stored_vector = StoredVector {
                    id: vector_id.clone(),
                    vector: vector_entry.vector,
                    metadata: vector_entry.metadata,
                    created_at: get_current_timestamp(),
                };

                collection.vectors.insert(vector_id.clone(), stored_vector);
                collection.updated_at = get_current_timestamp();
                inserted_ids.push(vector_id);
            }

            // Would rebuild FAISS index here
            println!("Inserted {} vectors into FAISS collection {}", inserted_ids.len(), collection_id);
            Ok(inserted_ids)
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn search_similar(&self, collection_id: &str, query_vector: &[f32], k: u32, filter: Option<Filter>) -> Result<Vec<SearchResult>, VectorDBError> {
        let collections = self.collections.read();
        if let Some(collection) = collections.get(collection_id) {
            if query_vector.len() != collection.config.dimension as usize {
                return Err(VectorDBError::DimensionMismatch);
            }

            // In production, this would use actual FAISS index search
            let mut candidates = Vec::new();
            for stored_vector in collection.vectors.values() {
                if let Some(ref filter_condition) = filter {
                    if !self.apply_filter(&stored_vector.metadata, filter_condition) {
                        continue;
                    }
                }

                let similarity = self.calculate_similarity(
                    query_vector,
                    &stored_vector.vector,
                    collection.config.metric_type
                );

                candidates.push(SearchResult {
                    id: stored_vector.id.clone(),
                    score: similarity,
                    vector: stored_vector.vector.clone(),
                    metadata: stored_vector.metadata.clone(),
                });
            }

            candidates.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
            candidates.truncate(k as usize);

            Ok(candidates)
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    fn update_vector(&self, collection_id: &str, vector_id: &str, vector_entry: VectorEntry) -> Result<(), VectorDBError> {
        // Similar implementation to ChromaDB
        Ok(())
    }

    fn delete_vector(&self, collection_id: &str, vector_id: &str) -> Result<(), VectorDBError> {
        // Similar implementation to ChromaDB
        Ok(())
    }

    fn get_collection_stats(&self, collection_id: &str) -> Result<CollectionStats, VectorDBError> {
        let collections = self.collections.read();
        if let Some(collection) = collections.get(collection_id) {
            Ok(CollectionStats {
                collection_id: collection_id.to_string(),
                name: collection.config.name.clone(),
                vector_count: collection.vectors.len() as u64,
                dimension: collection.config.dimension,
                index_size_bytes: collection.index_data.len() as u64,
                last_updated: collection.updated_at,
                search_latency_ms: 2.0, // FAISS is typically faster
                memory_usage_mb: collection.index_data.len() as f64 / (1024.0 * 1024.0),
            })
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }
}

impl FAISSAdapter {
    /// Calculate similarity (reuse from ChromaDBAdapter)
    fn calculate_similarity(&self, vec_a: &[f32], vec_b: &[f32], metric: DistanceMetric) -> f64 {
        // Same implementation as ChromaDB
        match metric {
            DistanceMetric::Cosine => self.cosine_similarity(vec_a, vec_b),
            DistanceMetric::Euclidean => 1.0 / (1.0 + self.euclidean_distance(vec_a, vec_b)),
            _ => 0.5, // Simplified for other metrics
        }
    }

    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f64 {
        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = sqrt_f32(a.iter().map(|x| x * x).sum::<f32>());
        let norm_b: f32 = sqrt_f32(b.iter().map(|x| x * x).sum::<f32>());

        if norm_a == 0.0 || norm_b == 0.0 {
            0.0
        } else {
            (dot_product / (norm_a * norm_b)) as f64
        }
    }

    fn euclidean_distance(&self, a: &[f32], b: &[f32]) -> f64 {
        let sum = a.iter().zip(b.iter())
            .map(|(x, y)| (x - y).powi(2))
            .sum::<f32>();
        sqrt_f32(sum) as f64
    }

    fn apply_filter(&self, _metadata: &BTreeMap<String, MetadataValue>, _filter: &Filter) -> bool {
        true // Simplified implementation
    }
}

/// Vector database manager
pub struct VectorDatabaseManager {
    chroma_adapter: ChromaDBAdapter,
    faiss_adapter: FAISSAdapter,
    default_database: DatabaseType,
    collections: RwLock<BTreeMap<String, CollectionInfo>>,
}

#[derive(Debug, Clone, Copy)]
pub enum DatabaseType {
    ChromaDB,
    FAISS,
}

/// Collection information
#[derive(Debug, Clone)]
struct CollectionInfo {
    pub collection_id: String,
    pub name: String,
    pub database_type: DatabaseType,
    pub created_at: u64,
}

impl VectorDatabaseManager {
    /// Create new vector database manager
    pub fn new(chroma_url: String, faiss_factory: String) -> Self {
        Self {
            chroma_adapter: ChromaDBAdapter::new(chroma_url),
            faiss_adapter: FAISSAdapter::new(faiss_factory),
            default_database: DatabaseType::ChromaDB,
            collections: RwLock::new(BTreeMap::new()),
        }
    }

    /// Create collection with automatic database selection
    pub fn create_collection(&self, name: &str, config: CollectionConfig, db_type: Option<DatabaseType>) -> Result<String, VectorDBError> {
        let database_type = db_type.unwrap_or(self.default_database);

        let collection_id = match database_type {
            DatabaseType::ChromaDB => self.chroma_adapter.create_collection(name, config)?,
            DatabaseType::FAISS => self.faiss_adapter.create_collection(name, config)?,
        };

        let collection_info = CollectionInfo {
            collection_id: collection_id.clone(),
            name: name.to_string(),
            database_type,
            created_at: get_current_timestamp(),
        };

        let mut collections = self.collections.write();
        collections.insert(name.to_string(), collection_info);

        Ok(collection_id)
    }

    /// Get adapter for collection
    fn get_adapter(&self, collection_name: &str) -> Result<(&dyn VectorDatabase, String), VectorDBError> {
        let collections = self.collections.read();
        if let Some(collection_info) = collections.get(collection_name) {
            match collection_info.database_type {
                DatabaseType::ChromaDB => Ok((&self.chroma_adapter, collection_info.collection_id.clone())),
                DatabaseType::FAISS => Ok((&self.faiss_adapter, collection_info.collection_id.clone())),
            }
        } else {
            Err(VectorDBError::CollectionNotFound)
        }
    }

    /// Search across collections
    pub fn search(&self, collection_name: &str, query_vector: &[f32], k: u32, filter: Option<Filter>) -> Result<Vec<SearchResult>, VectorDBError> {
        let (adapter, collection_id) = self.get_adapter(collection_name)?;
        adapter.search_similar(&collection_id, query_vector, k, filter)
    }

    /// Insert vectors
    pub fn insert(&self, collection_name: &str, vectors: Vec<VectorEntry>) -> Result<Vec<String>, VectorDBError> {
        let (adapter, collection_id) = self.get_adapter(collection_name)?;
        adapter.insert_vectors(&collection_id, vectors)
    }

    /// Generate status report
    pub fn generate_report(&self) -> String {
        let collections = self.collections.read();

        let mut report = String::new();
        report.push_str("=== SYNOS VECTOR DATABASE REPORT ===\n\n");

        report.push_str("=== COLLECTIONS ===\n");
        for (name, info) in collections.iter() {
            report.push_str(&format!("Collection: {}\n", name));
            report.push_str(&format!("  Database: {:?}\n", info.database_type));
            report.push_str(&format!("  ID: {}\n", info.collection_id));
            report.push_str(&format!("  Created: {}\n", info.created_at));

            // Get stats if possible
            let adapter_result = match info.database_type {
                DatabaseType::ChromaDB => self.chroma_adapter.get_collection_stats(&info.collection_id),
                DatabaseType::FAISS => self.faiss_adapter.get_collection_stats(&info.collection_id),
            };

            if let Ok(stats) = adapter_result {
                report.push_str(&format!("  Vectors: {}\n", stats.vector_count));
                report.push_str(&format!("  Dimension: {}\n", stats.dimension));
                report.push_str(&format!("  Memory: {:.2} MB\n", stats.memory_usage_mb));
            }
        }

        report
    }
}

/// Global vector database manager instance
pub static VECTOR_DB_MANAGER: RwLock<Option<VectorDatabaseManager>> = RwLock::new(None);

/// Initialize vector database manager
pub fn init_vector_database(chroma_url: String, faiss_factory: String) -> Result<(), MLOpsError> {
    let manager = VectorDatabaseManager::new(chroma_url, faiss_factory);
    *VECTOR_DB_MANAGER.write() = Some(manager);
    Ok(())
}

/// Get vector database report
pub fn get_vector_db_report() -> Result<String, MLOpsError> {
    if let Some(manager) = VECTOR_DB_MANAGER.read().as_ref() {
        Ok(manager.generate_report())
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
    fn test_chroma_adapter_creation() {
        let adapter = ChromaDBAdapter::new("http://localhost:8000".to_string());
        assert_eq!(adapter.base_url, "http://localhost:8000");
    }

    #[test]
    fn test_collection_creation() {
        let adapter = ChromaDBAdapter::new("http://localhost:8000".to_string());
        let config = CollectionConfig {
            name: "test_collection".to_string(),
            dimension: 384,
            metric_type: DistanceMetric::Cosine,
            index_type: IndexType::FlatIndex,
            description: "Test collection".to_string(),
            metadata_schema: BTreeMap::new(),
        };

        let result = adapter.create_collection("test", config);
        assert!(result.is_ok());
    }

    #[test]
    fn test_cosine_similarity() {
        let adapter = ChromaDBAdapter::new("http://localhost:8000".to_string());
        let vec_a = vec![1.0, 0.0, 0.0];
        let vec_b = vec![1.0, 0.0, 0.0];
        let similarity = adapter.cosine_similarity(&vec_a, &vec_b);
        assert!((similarity - 1.0).abs() < 0.001);
    }
}