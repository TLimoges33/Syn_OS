//! Dependency resolution for SynPkg
//! 
//! Implements advanced dependency resolution with conflict detection
//! and consciousness-aware optimization

use std::collections::{HashMap, HashSet, VecDeque};
use anyhow::{Result, anyhow};

use crate::core::PackageInfo;
use crate::repository::RepositoryManager;

/// Dependency resolution result
#[derive(Debug)]
pub struct DependencyResolution {
    pub install_order: Vec<String>,
    pub conflicts: Vec<String>,
    pub warnings: Vec<String>,
    pub total_size: u64,
}

/// Dependency resolver with consciousness optimization
pub struct DependencyResolver {
    /// Cache of resolved dependencies to avoid recalculation
    cache: HashMap<String, Vec<String>>,
}

impl DependencyResolver {
    /// Create new dependency resolver
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    /// Resolve dependencies for a package
    pub async fn resolve(&mut self, package: &PackageInfo, repo_manager: &RepositoryManager) -> Result<DependencyResolution> {
        let mut to_install = Vec::new();
        let mut conflicts = Vec::new();
        let mut warnings = Vec::new();
        let mut total_size = 0;
        let mut visited = HashSet::new();
        let mut queue = VecDeque::new();

        // Start with the main package
        queue.push_back(package.name.clone());

        while let Some(current_pkg) = queue.pop_front() {
            if visited.contains(&current_pkg) {
                continue;
            }
            visited.insert(current_pkg.clone());

            // Find package info
            let pkg_info = match repo_manager.find_package(&current_pkg, None).await {
                Ok(info) => info,
                Err(_) => {
                    warnings.push(format!("Could not find package: {}", current_pkg));
                    continue;
                }
            };

            // Check for conflicts
            for conflict in &pkg_info.conflicts {
                // This is a simplified conflict check
                // In a real implementation, this would check if the conflicting package is installed
                if self.is_package_installed(conflict).await {
                    conflicts.push(format!("{} conflicts with {}", current_pkg, conflict));
                }
            }

            // Add to install list
            to_install.push(current_pkg.clone());
            total_size += pkg_info.size;

            // Add dependencies to queue
            for dep in &pkg_info.dependencies {
                if !visited.contains(dep) && !self.is_package_installed(dep).await {
                    queue.push_back(dep.clone());
                }
            }
        }

        // Optimize installation order using topological sort
        let install_order = self.optimize_install_order(&to_install, repo_manager).await?;

        Ok(DependencyResolution {
            install_order,
            conflicts,
            warnings,
            total_size,
        })
    }

    /// Optimize installation order using dependency analysis
    async fn optimize_install_order(&self, packages: &[String], repo_manager: &RepositoryManager) -> Result<Vec<String>> {
        let mut graph: HashMap<String, Vec<String>> = HashMap::new();
        let mut in_degree: HashMap<String, usize> = HashMap::new();

        // Build dependency graph
        for pkg_name in packages {
            let pkg_info = repo_manager.find_package(pkg_name, None).await?;
            let dependencies: Vec<String> = pkg_info.dependencies.iter()
                .filter(|dep| packages.contains(dep))
                .cloned()
                .collect();

            graph.insert(pkg_name.clone(), dependencies.clone());
            in_degree.insert(pkg_name.clone(), 0);

            for dep in dependencies {
                in_degree.entry(dep).or_insert(0);
            }
        }

        // Calculate in-degrees
        for (_, deps) in &graph {
            for dep in deps {
                *in_degree.get_mut(dep).unwrap() += 1;
            }
        }

        // Topological sort (Kahn's algorithm)
        let mut queue: VecDeque<String> = in_degree.iter()
            .filter(|(_, &degree)| degree == 0)
            .map(|(pkg, _)| pkg.clone())
            .collect();

        let mut result = Vec::new();

        while let Some(current) = queue.pop_front() {
            result.push(current.clone());

            if let Some(dependencies) = graph.get(&current) {
                for dep in dependencies {
                    *in_degree.get_mut(dep).unwrap() -= 1;
                    if in_degree[dep] == 0 {
                        queue.push_back(dep.clone());
                    }
                }
            }
        }

        // Check for circular dependencies
        if result.len() != packages.len() {
            return Err(anyhow!("Circular dependency detected"));
        }

        // Reverse to get correct installation order (dependencies first)
        result.reverse();
        Ok(result)
    }

    /// Check if a package is already installed
    async fn is_package_installed(&self, _package_name: &str) -> bool {
        // Simplified check - in reality, this would query the package database
        false
    }

    /// Clear dependency cache
    pub fn clear_cache(&mut self) {
        self.cache.clear();
    }

    /// Get dependency tree for visualization
    pub async fn get_dependency_tree(&self, package: &PackageInfo, repo_manager: &RepositoryManager) -> Result<DependencyTree> {
        let mut tree = DependencyTree {
            package: package.name.clone(),
            dependencies: Vec::new(),
        };

        self.build_dependency_tree(&mut tree, &package.name, repo_manager, &mut HashSet::new()).await?;
        Ok(tree)
    }

    async fn build_dependency_tree(
        &self,
        tree: &mut DependencyTree,
        package_name: &str,
        repo_manager: &RepositoryManager,
        visited: &mut HashSet<String>
    ) -> Result<()> {
        if visited.contains(package_name) {
            return Ok(()); // Avoid cycles
        }
        visited.insert(package_name.to_string());

        let pkg_info = repo_manager.find_package(package_name, None).await?;

        for dep_name in &pkg_info.dependencies {
            let mut dep_tree = DependencyTree {
                package: dep_name.clone(),
                dependencies: Vec::new(),
            };

            // Use Box::pin to handle recursion in async function
            Box::pin(self.build_dependency_tree(&mut dep_tree, dep_name, repo_manager, visited)).await?;
            tree.dependencies.push(dep_tree);
        }

        visited.remove(package_name);
        Ok(())
    }
}

/// Dependency tree structure for visualization
#[derive(Debug)]
pub struct DependencyTree {
    pub package: String,
    pub dependencies: Vec<DependencyTree>,
}

impl DependencyTree {
    /// Print dependency tree
    pub fn print(&self, indent: usize) {
        println!("{}{}", "  ".repeat(indent), self.package);
        for dep in &self.dependencies {
            dep.print(indent + 1);
        }
    }

    /// Count total dependencies
    pub fn count_dependencies(&self) -> usize {
        let mut count = self.dependencies.len();
        for dep in &self.dependencies {
            count += dep.count_dependencies();
        }
        count
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_dependency_resolver() {
        let resolver = DependencyResolver::new();
        assert_eq!(resolver.cache.len(), 0);
    }

    #[test]
    fn test_dependency_tree_count() {
        let tree = DependencyTree {
            package: "test".to_string(),
            dependencies: vec![
                DependencyTree {
                    package: "dep1".to_string(),
                    dependencies: vec![],
                },
                DependencyTree {
                    package: "dep2".to_string(),
                    dependencies: vec![
                        DependencyTree {
                            package: "dep2-1".to_string(),
                            dependencies: vec![],
                        }
                    ],
                },
            ],
        };

        assert_eq!(tree.count_dependencies(), 3);
    }
}
