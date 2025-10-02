use std::collections::{HashMap, VecDeque};
use std::sync::Arc;
use petgraph::{Graph, Direction};
use petgraph::graph::{NodeIndex, UnGraph};
use crate::core::{Package, Dependency, VersionConstraint};

/// High-performance dependency resolver using graph algorithms
pub struct DependencyResolver {
    config: Arc<crate::PackageManagerConfig>,
    dependency_cache: tokio::sync::RwLock<HashMap<String, DependencyNode>>,
}

#[derive(Debug, Clone)]
struct DependencyNode {
    package: Package,
    resolved_dependencies: Vec<String>,
    resolution_time: chrono::DateTime<chrono::Utc>,
}

/// Dependency resolution plan with optimized installation order
#[derive(Debug, Clone)]
pub struct DependencyPlan {
    pub packages: Vec<Package>,
    pub installation_order: Vec<String>,
    pub conflicts: Vec<DependencyConflict>,
    pub total_size_bytes: u64,
    pub estimated_time_seconds: u32,
}

#[derive(Debug, Clone)]
pub struct DependencyConflict {
    pub package1: String,
    pub package2: String,
    pub reason: String,
    pub severity: ConflictSeverity,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ConflictSeverity {
    Warning,   // Can proceed with caution
    Error,     // Must be resolved before proceeding
    Critical,  // System stability at risk
}

impl DependencyResolver {
    pub fn new(config: Arc<crate::PackageManagerConfig>) -> Self {
        Self {
            config,
            dependency_cache: tokio::sync::RwLock::new(HashMap::new()),
        }
    }
    
    /// Resolve dependencies for a package with graph-based optimization
    pub async fn resolve_dependencies(&self, root_package: &Package) -> crate::Result<DependencyPlan> {
        let start = std::time::Instant::now();
        
        // Create dependency graph
        let mut graph = Graph::new_undirected();
        let mut package_nodes = HashMap::new();
        let mut packages = Vec::new();
        
        // Add root package
        let root_idx = graph.add_node(root_package.name.clone());
        package_nodes.insert(root_package.name.clone(), root_idx);
        packages.push(root_package.clone());
        
        // BFS to build dependency tree
        let mut queue = VecDeque::new();
        queue.push_back(root_package.clone());
        
        while let Some(current_package) = queue.pop_front() {
            let current_idx = package_nodes[&current_package.name];
            
            for dependency in &current_package.dependencies {
                // Check cache first
                if let Some(cached_node) = self.dependency_cache.read().await.get(&dependency.name) {
                    if self.is_cache_valid(&cached_node) {
                        // Use cached resolution
                        if !package_nodes.contains_key(&dependency.name) {
                            let dep_idx = graph.add_node(dependency.name.clone());
                            package_nodes.insert(dependency.name.clone(), dep_idx);
                            graph.add_edge(current_idx, dep_idx, ());
                            packages.push(cached_node.package.clone());
                        }
                        continue;
                    }
                }
                
                // Resolve dependency from repositories
                match self.resolve_single_dependency(dependency).await {
                    Ok(resolved_package) => {
                        if !package_nodes.contains_key(&resolved_package.name) {
                            let dep_idx = graph.add_node(resolved_package.name.clone());
                            package_nodes.insert(resolved_package.name.clone(), dep_idx);
                            graph.add_edge(current_idx, dep_idx, ());
                            
                            // Cache the resolution
                            let cache_node = DependencyNode {
                                package: resolved_package.clone(),
                                resolved_dependencies: resolved_package.dependencies
                                    .iter()
                                    .map(|d| d.name.clone())
                                    .collect(),
                                resolution_time: chrono::Utc::now(),
                            };
                            self.dependency_cache.write().await.insert(
                                resolved_package.name.clone(),
                                cache_node,
                            );
                            
                            packages.push(resolved_package.clone());
                            queue.push_back(resolved_package);
                        }
                    }
                    Err(e) if !dependency.optional => {
                        return Err(crate::PackageManagerError::DependencyConflict {
                            message: format!("Failed to resolve required dependency {}: {}", 
                                           dependency.name, e),
                        });
                    }
                    Err(_) => {
                        // Optional dependency failed - log but continue
                        tracing::warn!("Failed to resolve optional dependency: {}", dependency.name);
                    }
                }
            }
        }
        
        // Detect conflicts
        let conflicts = self.detect_conflicts(&packages)?;
        
        // Calculate installation order using topological sort
        let installation_order = self.calculate_installation_order(&graph, &package_nodes)?;
        
        // Calculate totals
        let total_size_bytes = packages.iter().map(|p| p.size_bytes).sum();
        let estimated_time_seconds = self.estimate_installation_time(&packages);
        
        let resolution_time = start.elapsed();
        tracing::info!(
            "Dependency resolution completed in {:?} for {} packages",
            resolution_time,
            packages.len()
        );
        
        Ok(DependencyPlan {
            packages,
            installation_order,
            conflicts,
            total_size_bytes,
            estimated_time_seconds,
        })
    }
    
    async fn resolve_single_dependency(&self, dependency: &Dependency) -> crate::Result<Package> {
        // This would typically query the repository manager
        // For now, create a mock resolved package
        let mut package = crate::core::Package::new(
            dependency.name.clone(),
            "1.0.0".to_string(), // TODO: Resolve actual version
            dependency.source_hint.clone().unwrap_or(crate::core::PackageSource::SynosOfficial),
        );
        
        // Set basic metadata
        package.description = format!("Dependency package: {}", dependency.name);
        package.size_bytes = 1024 * 1024; // 1MB default
        
        Ok(package)
    }
    
    fn detect_conflicts(&self, packages: &[Package]) -> crate::Result<Vec<DependencyConflict>> {
        let mut conflicts = Vec::new();
        
        // Check for version conflicts
        let mut package_versions: HashMap<String, Vec<&Package>> = HashMap::new();
        for package in packages {
            package_versions.entry(package.name.clone()).or_default().push(package);
        }
        
        for (package_name, versions) in package_versions {
            if versions.len() > 1 {
                for i in 0..versions.len() {
                    for j in i + 1..versions.len() {
                        conflicts.push(DependencyConflict {
                            package1: format!("{}@{}", package_name, versions[i].version),
                            package2: format!("{}@{}", package_name, versions[j].version),
                            reason: "Multiple versions of the same package".to_string(),
                            severity: ConflictSeverity::Error,
                        });
                    }
                }
            }
        }
        
        Ok(conflicts)
    }
    
    fn calculate_installation_order(
        &self,
        graph: &UnGraph<String, ()>,
        package_nodes: &HashMap<String, NodeIndex>,
    ) -> crate::Result<Vec<String>> {
        // Simple topological sort - dependencies first
        let mut order = Vec::new();
        let mut visited = std::collections::HashSet::new();
        
        // Start with packages that have no dependencies (leaf nodes)
        for (package_name, &node_idx) in package_nodes {
            if graph.neighbors_directed(node_idx, Direction::Outgoing).count() == 0 {
                if !visited.contains(package_name) {
                    self.dfs_order(graph, package_nodes, package_name, &mut visited, &mut order);
                }
            }
        }
        
        // Add any remaining packages
        for package_name in package_nodes.keys() {
            if !visited.contains(package_name) {
                self.dfs_order(graph, package_nodes, package_name, &mut visited, &mut order);
            }
        }
        
        Ok(order)
    }
    
    fn dfs_order(
        &self,
        graph: &UnGraph<String, ()>,
        package_nodes: &HashMap<String, NodeIndex>,
        package_name: &str,
        visited: &mut std::collections::HashSet<String>,
        order: &mut Vec<String>,
    ) {
        if visited.contains(package_name) {
            return;
        }
        
        visited.insert(package_name.to_string());
        
        if let Some(&node_idx) = package_nodes.get(package_name) {
            // Visit dependencies first
            for neighbor_idx in graph.neighbors(node_idx) {
                if let Some(neighbor_name) = graph.node_weight(neighbor_idx) {
                    if !visited.contains(neighbor_name) {
                        self.dfs_order(graph, package_nodes, neighbor_name, visited, order);
                    }
                }
            }
        }
        
        order.push(package_name.to_string());
    }
    
    fn estimate_installation_time(&self, packages: &[Package]) -> u32 {
        // Simple estimation: 10 seconds base + 1 second per MB
        let base_time = 10;
        let size_time = packages.iter()
            .map(|p| p.size_bytes / (1024 * 1024)) // Convert to MB
            .sum::<u64>() as u32;
        
        base_time + size_time
    }
    
    fn is_cache_valid(&self, cached_node: &DependencyNode) -> bool {
        // Cache is valid for 1 hour
        let cache_ttl = chrono::Duration::hours(1);
        chrono::Utc::now() - cached_node.resolution_time < cache_ttl
    }
    
    /// Clear the dependency resolution cache
    pub async fn clear_cache(&self) {
        self.dependency_cache.write().await.clear();
    }
    
    /// Get cache statistics
    pub async fn cache_stats(&self) -> CacheStats {
        let cache = self.dependency_cache.read().await;
        CacheStats {
            entries: cache.len(),
            memory_usage_mb: (cache.len() * std::mem::size_of::<DependencyNode>()) / (1024 * 1024),
        }
    }
}

#[derive(Debug)]
pub struct CacheStats {
    pub entries: usize,
    pub memory_usage_mb: usize,
}

impl DependencyPlan {
    /// Check if the plan has any critical conflicts
    pub fn has_critical_conflicts(&self) -> bool {
        self.conflicts.iter().any(|c| c.severity == ConflictSeverity::Critical)
    }
    
    /// Check if the plan has any error-level conflicts
    pub fn has_errors(&self) -> bool {
        self.conflicts.iter().any(|c| c.severity == ConflictSeverity::Error)
    }
    
    /// Get human-readable summary of the plan
    pub fn summary(&self) -> String {
        format!(
            "Installation plan: {} packages, {:.2} MB total, estimated {} seconds. {} conflicts.",
            self.packages.len(),
            self.total_size_bytes as f64 / (1024.0 * 1024.0),
            self.estimated_time_seconds,
            self.conflicts.len()
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::{PackageSource, Package};
    
    #[tokio::test]
    async fn test_dependency_resolution() {
        let config = Arc::new(crate::PackageManagerConfig::default());
        let resolver = DependencyResolver::new(config);
        
        let mut root_package = Package::new(
            "test-app".to_string(),
            "1.0.0".to_string(),
            PackageSource::SynosOfficial,
        );
        
        // Add some dependencies
        root_package.dependencies = vec![
            Dependency {
                name: "lib1".to_string(),
                version_constraint: crate::core::VersionConstraint::Any,
                optional: false,
                source_hint: None,
            },
            Dependency {
                name: "lib2".to_string(),
                version_constraint: crate::core::VersionConstraint::GreaterOrEqual("2.0.0".to_string()),
                optional: true,
                source_hint: None,
            },
        ];
        
        let plan = resolver.resolve_dependencies(&root_package).await.unwrap();
        
        assert!(!plan.packages.is_empty());
        assert!(!plan.installation_order.is_empty());
        assert!(plan.total_size_bytes > 0);
    }
}
