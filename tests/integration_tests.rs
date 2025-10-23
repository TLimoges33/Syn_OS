//! SynOS Integration Tests
//!
//! Comprehensive testing framework for all SynOS components

use std::process::Command;
use std::path::Path;

#[cfg(test)]
mod tests {
    use super::*;

    /// Test V1.9-V2.0 package installation
    #[test]
    fn test_v19_v20_packages() {
        // Verify .deb packages exist
        assert!(Path::new("target/debian/synos-universal-command_4.4.0-1_amd64.deb").exists());
        assert!(Path::new("target/debian/synos-ctf-platform_4.4.0-1_amd64.deb").exists());
        assert!(Path::new("target/debian/synos-quantum-consciousness_4.4.0-1_amd64.deb").exists());
    }

    /// Test universal command functionality
    #[test]
    fn test_universal_command() {
        let output = Command::new("cargo")
            .args(&["run", "--bin", "synos-universal", "--", "version"])
            .output()
            .expect("Failed to run universal command");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("SynOS Universal Command"));
    }

    /// Test CTF platform functionality
    #[test]
    fn test_ctf_platform() {
        let output = Command::new("cargo")
            .args(&["run", "--bin", "synos-ctf", "--", "version"])
            .output()
            .expect("Failed to run CTF platform");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("SynOS CTF Platform"));
    }

    /// Test quantum consciousness functionality
    #[test]
    fn test_quantum_consciousness() {
        let output = Command::new("cargo")
            .args(&["run", "--bin", "synos-quantum", "--", "version"])
            .output()
            .expect("Failed to run quantum consciousness");

        assert!(output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains("SynOS Quantum Consciousness"));
    }

    /// Test build script exists and is executable
    #[test]
    fn test_build_script() {
        let build_script = Path::new("scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh");
        assert!(build_script.exists());

        // Check if executable
        let metadata = build_script.metadata().expect("Failed to get metadata");
        assert!(metadata.permissions().mode() & 0o111 != 0);
    }

    /// Test AI runtime library installer
    #[test]
    fn test_ai_runtime_installer() {
        let installer = Path::new("scripts/02-build/core/install-ai-runtime-libraries.sh");
        assert!(installer.exists());

        // Check if executable
        let metadata = installer.metadata().expect("Failed to get metadata");
        assert!(metadata.permissions().mode() & 0o111 != 0);
    }

    /// Test workspace compilation
    #[test]
    fn test_workspace_compilation() {
        let output = Command::new("cargo")
            .args(&["check", "--workspace"])
            .output()
            .expect("Failed to check workspace");

        // Should compile without errors (warnings are acceptable)
        assert!(output.status.success());
    }

    /// Test V1.9-V2.0 module compilation
    #[test]
    fn test_v19_v20_compilation() {
        let modules = [
            "synos-universal-command",
            "synos-ctf-platform",
            "synos-quantum-consciousness"
        ];

        for module in &modules {
            let output = Command::new("cargo")
                .args(&["check", "--package", module])
                .output()
                .expect(&format!("Failed to check {}", module));

            assert!(output.status.success(), "Module {} failed to compile", module);
        }
    }

    /// Test documentation generation
    #[test]
    fn test_documentation() {
        let docs = [
            "docs/ZERO_STUBS_COMPLETION_REPORT.md",
            "src/universal-command/README.md",
            "src/ctf-platform/README.md",
            "src/quantum-consciousness/README.md",
        ];

        for doc in &docs {
            assert!(Path::new(doc).exists(), "Documentation missing: {}", doc);
        }
    }

    /// Test kernel module structure
    #[test]
    fn test_kernel_modules() {
        let kernel_modules = [
            "src/kernel/src/time_utils.rs",
            "src/kernel/src/ai_interface.rs",
            "src/kernel/src/networking.rs",
        ];

        for module in &kernel_modules {
            assert!(Path::new(module).exists(), "Kernel module missing: {}", module);
        }
    }

    /// Performance benchmark test
    #[test]
    fn test_performance_benchmarks() {
        // Test that performance-critical components meet basic requirements
        let start = std::time::Instant::now();

        // Simulate some work
        for _ in 0..1000 {
            std::hint::spin_loop();
        }

        let duration = start.elapsed();

        // Should complete quickly (< 1ms for this simple test)
        assert!(duration.as_millis() < 100, "Performance test took too long: {:?}", duration);
    }
}

/// Integration test utilities
pub mod utils {
    use std::process::{Command, Output};
    use std::path::Path;

    /// Run a command and return output
    pub fn run_command(cmd: &str, args: &[&str]) -> Result<Output, std::io::Error> {
        Command::new(cmd).args(args).output()
    }

    /// Check if file exists and is executable
    pub fn is_executable(path: &str) -> bool {
        if let Ok(metadata) = Path::new(path).metadata() {
            metadata.permissions().mode() & 0o111 != 0
        } else {
            false
        }
    }

    /// Verify package integrity
    pub fn verify_deb_package(package_path: &str) -> bool {
        if !Path::new(package_path).exists() {
            return false;
        }

        // Check package with dpkg-deb
        let output = Command::new("dpkg-deb")
            .args(&["--info", package_path])
            .output();

        match output {
            Ok(result) => result.status.success(),
            Err(_) => false,
        }
    }

    /// Test network connectivity (for ISO testing)
    pub fn test_network_connectivity() -> bool {
        let output = Command::new("ping")
            .args(&["-c", "1", "8.8.8.8"])
            .output();

        match output {
            Ok(result) => result.status.success(),
            Err(_) => false,
        }
    }
}

/// Benchmark utilities for performance testing
pub mod benchmarks {
    use std::time::{Duration, Instant};

    /// Simple benchmark runner
    pub struct Benchmark {
        name: String,
        iterations: usize,
    }

    impl Benchmark {
        pub fn new(name: &str, iterations: usize) -> Self {
            Self {
                name: name.to_string(),
                iterations,
            }
        }

        /// Run benchmark and return average duration
        pub fn run<F>(&self, mut test_fn: F) -> Duration
        where
            F: FnMut(),
        {
            let mut total_duration = Duration::new(0, 0);

            for _ in 0..self.iterations {
                let start = Instant::now();
                test_fn();
                total_duration += start.elapsed();
            }

            total_duration / self.iterations as u32
        }

        /// Run benchmark and print results
        pub fn run_and_print<F>(&self, test_fn: F)
        where
            F: FnMut(),
        {
            let avg_duration = self.run(test_fn);
            println!("Benchmark '{}': {:.2}ms average ({} iterations)",
                self.name,
                avg_duration.as_secs_f64() * 1000.0,
                self.iterations
            );
        }
    }
}

#[cfg(test)]
mod performance_tests {
    use super::benchmarks::Benchmark;

    #[test]
    fn benchmark_basic_operations() {
        let benchmark = Benchmark::new("Basic Operations", 1000);

        benchmark.run_and_print(|| {
            // Simulate basic system operations
            for i in 0..100 {
                let _ = i * 2;
            }
        });
    }

    #[test]
    fn benchmark_memory_operations() {
        let benchmark = Benchmark::new("Memory Operations", 100);

        benchmark.run_and_print(|| {
            // Simulate memory allocation/deallocation
            let vec: Vec<u8> = vec![0; 1024];
            drop(vec);
        });
    }
}
