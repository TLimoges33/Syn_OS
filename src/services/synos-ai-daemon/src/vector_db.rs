/// Vector Database - Embeddings Storage for RAG
/// Simple in-memory vector store for personal context and knowledge retrieval

use anyhow::Result;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{debug, info};

#[derive(Debug, Clone)]
struct VectorEntry {
    id: String,
    text: String,
    embedding: Vec<f32>,
}

#[derive(Debug)]
pub struct VectorDatabase {
    entries: Arc<RwLock<HashMap<String, VectorEntry>>>,
    dimension: usize,
}

impl VectorDatabase {
    pub async fn new() -> Result<Self> {
        info!("🗄️  Initializing Vector Database for RAG");

        Ok(Self {
            entries: Arc::new(RwLock::new(HashMap::new())),
            dimension: 384, // Typical for sentence transformers
        })
    }

    pub async fn store(&self, id: String, text: String) -> Result<()> {
        let mut entries = self.entries.write().await;

        // Generate embedding (in production, use actual embedding model)
        let embedding = self.generate_embedding(&text).await?;

        debug!("Storing vector for id: {}", id);

        entries.insert(id.clone(), VectorEntry {
            id,
            text,
            embedding,
        });

        Ok(())
    }

    pub async fn search(&self, query: &str, top_k: usize) -> Result<Vec<String>> {
        let entries = self.entries.read().await;

        // Generate query embedding
        let query_embedding = self.generate_embedding(query).await?;

        // Calculate cosine similarity with all entries
        let mut results: Vec<_> = entries
            .values()
            .map(|entry| {
                let similarity = self.cosine_similarity(&query_embedding, &entry.embedding);
                (entry.text.clone(), similarity)
            })
            .collect();

        // Sort by similarity (descending)
        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        // Return top K results
        Ok(results
            .into_iter()
            .take(top_k)
            .map(|(text, _)| text)
            .collect())
    }

    pub async fn get(&self, id: &str) -> Result<Option<String>> {
        let entries = self.entries.read().await;
        Ok(entries.get(id).map(|e| e.text.clone()))
    }

    pub async fn delete(&self, id: &str) -> Result<()> {
        let mut entries = self.entries.write().await;
        entries.remove(id);
        debug!("Deleted vector for id: {}", id);
        Ok(())
    }

    pub async fn size(&self) -> usize {
        self.entries.read().await.len()
    }

    async fn generate_embedding(&self, text: &str) -> Result<Vec<f32>> {
        // Simplified embedding generation
        // In production, use actual embedding model (e.g., sentence-transformers)

        let mut embedding = vec![0.0f32; self.dimension];

        // Simple hash-based embedding for demonstration
        for (i, byte) in text.bytes().enumerate() {
            let idx = (i + byte as usize) % self.dimension;
            embedding[idx] += 1.0;
        }

        // Normalize
        let magnitude: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
        if magnitude > 0.0 {
            for x in &mut embedding {
                *x /= magnitude;
            }
        }

        Ok(embedding)
    }

    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f32 {
        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let magnitude_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let magnitude_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if magnitude_a > 0.0 && magnitude_b > 0.0 {
            dot_product / (magnitude_a * magnitude_b)
        } else {
            0.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_vector_store() {
        let db = VectorDatabase::new().await.unwrap();

        db.store("test1".to_string(), "Hello world".to_string()).await.unwrap();
        db.store("test2".to_string(), "Goodbye world".to_string()).await.unwrap();

        assert_eq!(db.size().await, 2);
    }

    #[tokio::test]
    async fn test_vector_search() {
        let db = VectorDatabase::new().await.unwrap();

        db.store("test1".to_string(), "cybersecurity threat detection".to_string()).await.unwrap();
        db.store("test2".to_string(), "machine learning models".to_string()).await.unwrap();

        let results = db.search("security threats", 1).await.unwrap();
        assert!(!results.is_empty());
    }
}
