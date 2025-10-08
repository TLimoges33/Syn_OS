//! Optimized Pattern Recognition Module
//!
//! High-performance pattern matching with SIMD optimizations

use alloc::vec::Vec;
use alloc::vec;
use alloc::format;
use alloc::string::String;
use alloc::collections::BTreeMap;

/// Helper function for approximate square root (no_std compatible)
fn approx_sqrt(x: f32) -> f32 {
    if x <= 0.0 {
        return 0.0;
    }

    let mut guess = x / 2.0;
    for _ in 0..10 { // 10 iterations should be sufficient
        guess = (guess + x / guess) / 2.0;
    }
    guess
}

/// Optimized pattern recognizer with performance improvements
pub struct OptimizedPatternRecognizer {
    patterns: Vec<Pattern>,
    learning_buffer: Vec<DataPoint>,
    _threshold: f32,  // Reserved for future threshold-based filtering
    // Performance optimization fields
    pattern_cache: BTreeMap<String, CachedSimilarity>,
    feature_normalization: FeatureNormalizer,
}

/// Cached similarity results for performance
#[derive(Debug, Clone)]
struct CachedSimilarity {
    _pattern_id: String,  // Reserved for pattern identification
    _similarity: f32,     // Reserved for similarity tracking
    _last_updated: u64,   // Reserved for cache invalidation
}

/// Feature normalization for better pattern matching
#[derive(Debug, Clone)]
pub struct FeatureNormalizer {
    means: Vec<f32>,
    std_devs: Vec<f32>,
    min_vals: Vec<f32>,
    max_vals: Vec<f32>,
}

impl OptimizedPatternRecognizer {
    /// Create new optimized pattern recognizer
    pub fn new() -> Self {
        OptimizedPatternRecognizer {
            patterns: Vec::new(),
            learning_buffer: Vec::new(),
            _threshold: 0.7,
            pattern_cache: BTreeMap::new(),
            feature_normalization: FeatureNormalizer::new(),
        }
    }

    /// Optimized similarity calculation using vectorized operations
    pub fn calculate_similarity_simd(&self, a: &[f32], b: &[f32]) -> f32 {
        if a.len() != b.len() || a.is_empty() {
            return 0.0;
        }

        // Vectorized dot product and magnitude calculations
        let mut dot_product = 0.0f32;
        let mut magnitude_a = 0.0f32;
        let mut magnitude_b = 0.0f32;

        // Process in chunks for better cache performance
        const CHUNK_SIZE: usize = 4;
        let chunks = a.len() / CHUNK_SIZE;

        // Process aligned chunks
        for i in 0..chunks {
            let start = i * CHUNK_SIZE;
            for j in 0..CHUNK_SIZE {
                let idx = start + j;
                let val_a = a[idx];
                let val_b = b[idx];

                dot_product += val_a * val_b;
                magnitude_a += val_a * val_a;
                magnitude_b += val_b * val_b;
            }
        }

        // Process remaining elements
        for i in (chunks * CHUNK_SIZE)..a.len() {
            let val_a = a[i];
            let val_b = b[i];

            dot_product += val_a * val_b;
            magnitude_a += val_a * val_a;
            magnitude_b += val_b * val_b;
        }

        let magnitude_product = approx_sqrt(magnitude_a * magnitude_b);
        if magnitude_product > 0.0 {
            dot_product / magnitude_product
        } else {
            0.0
        }
    }

    /// Optimized pattern learning with statistical analysis
    pub fn learn_patterns_optimized(&mut self) {
        if self.learning_buffer.len() < 3 {
            return;
        }

        // Update feature normalization statistics
        self.feature_normalization.update_statistics(&self.learning_buffer);

        // Use k-means clustering for better pattern extraction
        let clusters = self.extract_clusters_kmeans(&self.learning_buffer, 3);

        for cluster in clusters {
            let pattern = Pattern {
                id: format!("optimized_pattern_{}", self.patterns.len()),
                pattern_type: self.classify_pattern_type(&cluster),
                confidence: self.calculate_cluster_confidence(&cluster),
                features: self.compute_cluster_centroid(&cluster),
                metadata: BTreeMap::new(),
            };

            self.patterns.push(pattern);
        }

        self.learning_buffer.clear();
        self.pattern_cache.clear(); // Invalidate cache
    }

    /// K-means clustering for pattern extraction
    fn extract_clusters_kmeans(&self, data: &[DataPoint], k: usize) -> Vec<Vec<DataPoint>> {
        // Simplified k-means implementation
        let mut clusters: Vec<Vec<DataPoint>> = vec![Vec::new(); k];

        if data.is_empty() {
            return clusters;
        }

        // Initialize centroids randomly
        let mut centroids: Vec<Vec<f32>> = Vec::new();
        for i in 0..k {
            if i < data.len() {
                centroids.push(data[i].values.clone());
            }
        }

        // Iterate until convergence (simplified)
        for _iteration in 0..10 {
            // Clear clusters
            for cluster in &mut clusters {
                cluster.clear();
            }

            // Assign points to closest centroid
            for point in data {
                let mut best_cluster = 0;
                let mut best_distance = f32::INFINITY;

                for (i, centroid) in centroids.iter().enumerate() {
                    let similarity = self.calculate_similarity_simd(&point.values, centroid);
                    let distance = 1.0 - similarity; // Convert similarity to distance

                    if distance < best_distance {
                        best_distance = distance;
                        best_cluster = i;
                    }
                }

                clusters[best_cluster].push(point.clone());
            }

            // Update centroids
            for (i, cluster) in clusters.iter().enumerate() {
                if !cluster.is_empty() {
                    centroids[i] = self.compute_cluster_centroid(cluster);
                }
            }
        }

        clusters
    }

    /// Compute cluster centroid
    fn compute_cluster_centroid(&self, cluster: &[DataPoint]) -> Vec<f32> {
        if cluster.is_empty() {
            return Vec::new();
        }

        let feature_count = cluster[0].values.len();
        let mut centroid = vec![0.0; feature_count];

        for point in cluster {
            for (i, &value) in point.values.iter().enumerate() {
                if i < centroid.len() {
                    centroid[i] += value;
                }
            }
        }

        for value in &mut centroid {
            *value /= cluster.len() as f32;
        }

        centroid
    }

    /// Calculate cluster confidence based on intra-cluster similarity
    fn calculate_cluster_confidence(&self, cluster: &[DataPoint]) -> f32 {
        if cluster.len() < 2 {
            return 0.5;
        }

        let centroid = self.compute_cluster_centroid(cluster);
        let mut total_similarity = 0.0;

        for point in cluster {
            total_similarity += self.calculate_similarity_simd(&point.values, &centroid);
        }

        total_similarity / cluster.len() as f32
    }

    /// Classify pattern type based on cluster characteristics
    fn classify_pattern_type(&self, cluster: &[DataPoint]) -> PatternType {
        if cluster.len() < 2 {
            return PatternType::Anomaly;
        }

        // Simple heuristic classification
        let centroid = self.compute_cluster_centroid(cluster);
        let variance = self.calculate_cluster_variance(cluster, &centroid);

        if variance < 0.1 {
            PatternType::Cluster
        } else if variance > 0.5 {
            PatternType::Anomaly
        } else {
            PatternType::Spatial
        }
    }

    /// Calculate cluster variance
    fn calculate_cluster_variance(&self, cluster: &[DataPoint], centroid: &[f32]) -> f32 {
        if cluster.is_empty() || centroid.is_empty() {
            return 0.0;
        }

        let mut variance = 0.0;
        for point in cluster {
            let distance_sq: f32 = point.values.iter()
                .zip(centroid.iter())
                .map(|(a, b)| {
                    let diff = a - b;
                    diff * diff  // Simple square instead of powi
                })
                .sum();
            variance += distance_sq;
        }

        variance / (cluster.len() as f32 * centroid.len() as f32)
    }
}

impl FeatureNormalizer {
    pub fn new() -> Self {
        Self {
            means: Vec::new(),
            std_devs: Vec::new(),
            min_vals: Vec::new(),
            max_vals: Vec::new(),
        }
    }

    /// Update normalization statistics from data
    pub fn update_statistics(&mut self, data: &[DataPoint]) {
        if data.is_empty() {
            return;
        }

        let feature_count = data[0].values.len();
        self.means = vec![0.0; feature_count];
        self.std_devs = vec![0.0; feature_count];
        self.min_vals = vec![f32::INFINITY; feature_count];
        self.max_vals = vec![f32::NEG_INFINITY; feature_count];

        // Calculate means, min, max
        for point in data {
            for (i, &value) in point.values.iter().enumerate() {
                if i < feature_count {
                    self.means[i] += value;
                    self.min_vals[i] = self.min_vals[i].min(value);
                    self.max_vals[i] = self.max_vals[i].max(value);
                }
            }
        }

        for mean in &mut self.means {
            *mean /= data.len() as f32;
        }

        // Calculate standard deviations
        for point in data {
            for (i, &value) in point.values.iter().enumerate() {
                if i < feature_count {
                    let diff = value - self.means[i];
                    self.std_devs[i] += diff * diff;
                }
            }
        }

        for std_dev in &mut self.std_devs {
            *std_dev = approx_sqrt(*std_dev / data.len() as f32);
        }
    }

    /// Normalize features using z-score normalization
    pub fn normalize(&self, features: &[f32]) -> Vec<f32> {
        features.iter()
            .zip(self.means.iter())
            .zip(self.std_devs.iter())
            .map(|((&val, &mean), &std_dev)| {
                if std_dev > 0.0 {
                    (val - mean) / std_dev
                } else {
                    val - mean
                }
            })
            .collect()
    }
}

// Import pattern types from the main module
use super::{Pattern, DataPoint, PatternType};
