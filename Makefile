# SynapticOS Build Configuration

# Kernel build target
TARGET=x86_64-unknown-none

# Build profiles
PROFILE_DEV=dev
PROFILE_RELEASE=release
PROFILE_KERNEL=kernel

# Security flags
SECURITY_FLAGS=-Z sanitizer=address -Z sanitizer=memory
HARDENING_FLAGS=-C relocation-model=pic -C link-arg=-pie

# Build targets
.PHONY: all clean kernel test security-scan format audit

# Default build
all: kernel

# Build kernel
kernel:
	@echo "🔨 Building SynapticOS Kernel..."
	cargo build --target $(TARGET) --profile $(PROFILE_KERNEL) -p syn-kernel
	@echo "✅ Kernel build complete"

# Development build
dev:
	@echo "🔨 Building development version..."
	cargo build --profile $(PROFILE_DEV)
	@echo "✅ Development build complete"

# Release build
release:
	@echo "🔨 Building release version..."
	cargo build --profile $(PROFILE_RELEASE)
	@echo "✅ Release build complete"

# Run in QEMU
run: kernel
	@echo "🚀 Starting SynapticOS in QEMU..."
	cargo run --target $(TARGET) --profile $(PROFILE_KERNEL) -p syn-kernel

# Run tests
test:
	@echo "🧪 Running tests..."
	cargo test --workspace
	@echo "✅ Tests complete"

# Security scan
security-scan:
	@echo "🔍 Running security scan..."
	cargo audit
	cargo deny check
	@echo "✅ Security scan complete"

# Format code
format:
	@echo "🎨 Formatting code..."
	cargo fmt --all
	@echo "✅ Code formatted"

# Audit dependencies
audit:
	@echo "📋 Auditing dependencies..."
	cargo audit
	cargo deny check advisories
	@echo "✅ Audit complete"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	cargo clean
	@echo "✅ Clean complete"

# Setup development environment
setup:
	@echo "🛠️ Setting up development environment..."
	rustup target add $(TARGET)
	cargo install bootimage
	cargo install cargo-audit
	cargo install cargo-deny
	@echo "✅ Development environment ready"

# Create new module
new-module:
	@echo "📦 Creating new module: $(name)"
	@if [ -z "$(name)" ]; then \
		echo "❌ Error: Please specify name=<module_name>"; \
		exit 1; \
	fi
	mkdir -p src/$(name)/src
	echo '[package]\nname = "syn-$(name)"\nversion.workspace = true\nedition.workspace = true\nlicense.workspace = true\nauthors.workspace = true\n\n[dependencies]' > src/$(name)/Cargo.toml
	echo 'pub fn init() {\n    println!("✅ $(name) module initialized");\n}' > src/$(name)/src/lib.rs
	@echo "✅ Module $(name) created"

# Integration tests
integration-test:
	@echo "🔗 Running integration tests..."
	cargo test --test integration_tests
	@echo "✅ Integration tests complete"

# Performance benchmarks
benchmark:
	@echo "⚡ Running performance benchmarks..."
	cargo bench
	@echo "✅ Benchmarks complete"

# Documentation
docs:
	@echo "📚 Building documentation..."
	cargo doc --workspace --no-deps
	@echo "✅ Documentation built"

# Check code quality
check:
	@echo "🔍 Checking code quality..."
	cargo check --workspace
	cargo clippy --workspace -- -D warnings
	@echo "✅ Code quality check complete"

# Full validation pipeline
validate: format check test security-scan audit
	@echo "✅ Full validation complete"
