use anyhow::Result;
use tracing::debug;

pub struct PromptOptimizer {
    optimization_count: u64,
}

impl PromptOptimizer {
    pub fn new() -> Result<Self> {
        Ok(Self {
            optimization_count: 0,
        })
    }

    pub async fn optimize(&mut self, prompt: &str) -> Result<String> {
        self.optimization_count += 1;

        debug!(
            "Optimizing prompt #{}: {} chars",
            self.optimization_count,
            prompt.len()
        );

        // Basic prompt optimization
        let optimized = prompt
            .trim()
            .replace("  ", " ") // Remove double spaces
            .replace("\n\n\n", "\n\n"); // Remove excessive newlines

        // Add system instructions if needed
        let with_instructions = if !optimized.starts_with("You are") {
            format!("You are a helpful AI assistant. {}", optimized)
        } else {
            optimized
        };

        Ok(with_instructions)
    }

    pub fn get_optimization_count(&self) -> u64 {
        self.optimization_count
    }
}
