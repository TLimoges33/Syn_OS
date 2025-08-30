# SynapticOS Makefile for Real Kernel Development

# Configuration
KERNEL_TARGET = x86_64-unknown-none
KERNEL_DIR = src/kernel
BUILD_DIR = build
ISO_DIR = $(BUILD_DIR)/iso
KERNEL_BIN = $(BUILD_DIR)/kernel.bin

# Tools
CARGO = cargo
RUST_FLAGS = --release
QEMU = qemu-system-x86_64
GRUB_MKRESCUE = grub-mkrescue

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
NC := \033[0m

.PHONY: all kernel clean qemu-test iso help dev-setup test

# Default target
all: kernel

# Build the kernel
kernel:
	@echo "$(BLUE)Building SynapticOS kernel...$(NC)"
	cd $(KERNEL_DIR) && $(CARGO) build $(RUST_FLAGS) --target $(KERNEL_TARGET)
	@mkdir -p $(BUILD_DIR)
	@cp $(KERNEL_DIR)/target/$(KERNEL_TARGET)/release/kernel $(KERNEL_BIN)
	@echo "$(GREEN)Kernel built successfully: $(KERNEL_BIN)$(NC)"

# Create bootable ISO
iso: kernel
	@echo "$(BLUE)Creating bootable ISO...$(NC)"
	@mkdir -p $(ISO_DIR)/boot/grub
	@cp $(KERNEL_BIN) $(ISO_DIR)/boot/kernel.bin
	@echo 'menuentry "SynapticOS" { multiboot /boot/kernel.bin }' > $(ISO_DIR)/boot/grub/grub.cfg
	$(GRUB_MKRESCUE) -o $(BUILD_DIR)/synapticos.iso $(ISO_DIR)
	@echo "$(GREEN)ISO created: $(BUILD_DIR)/synapticos.iso$(NC)"

# Test kernel in QEMU
qemu-test: kernel
	@echo "$(BLUE)Testing kernel in QEMU...$(NC)"
	$(QEMU) -kernel $(KERNEL_BIN) -display curses -serial stdio

# Test ISO in QEMU
qemu-iso: iso
	@echo "$(BLUE)Testing ISO in QEMU...$(NC)"
	$(QEMU) -cdrom $(BUILD_DIR)/synapticos.iso -display curses -serial stdio

# Clean build artifacts
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	cd $(KERNEL_DIR) && $(CARGO) clean
	rm -rf $(BUILD_DIR)
	@echo "$(GREEN)Clean complete$(NC)"

# Development setup
dev-setup:
	@echo "$(BLUE)Setting up development environment...$(NC)"
	rustup install nightly
	rustup component add rust-src llvm-tools-preview --toolchain nightly
	rustup target add $(KERNEL_TARGET) --toolchain nightly
	@echo "$(GREEN)Development environment ready$(NC)"

# Run kernel tests
test:
	@echo "$(BLUE)Running kernel tests...$(NC)"
	cd $(KERNEL_DIR) && $(CARGO) test --target $(KERNEL_TARGET)

# Phase 1 development targets
phase1-milestone1:
	@echo "$(YELLOW)Phase 1.1: Implementing multiboot2 bootloader...$(NC)"
	@echo "$(RED)TODO: Implement proper multiboot2 header$(NC)"
	@echo "$(RED)TODO: Set up GDT (Global Descriptor Table)$(NC)"
	@echo "$(RED)TODO: Initialize IDT (Interrupt Descriptor Table)$(NC)"
	@echo "$(RED)TODO: Set up basic exception handlers$(NC)"
	@echo "$(RED)TODO: Create proper kernel entry point$(NC)"

phase1-milestone2:
	@echo "$(YELLOW)Phase 1.2: Memory Management...$(NC)"
	@echo "$(RED)TODO: Physical memory manager (frame allocator)$(NC)"
	@echo "$(RED)TODO: Virtual memory with paging$(NC)"
	@echo "$(RED)TODO: Heap allocator for kernel$(NC)"
	@echo "$(RED)TODO: Memory protection mechanisms$(NC)"

cybersec-tools:
	@echo "$(YELLOW)Cybersecurity Tools Integration...$(NC)"
	@echo "$(RED)TODO: Integrate ParrotOS security tools$(NC)"
	@echo "$(RED)TODO: Add Kali Linux penetration testing suite$(NC)"
	@echo "$(RED)TODO: Include BlackArch exploit database$(NC)"
	@echo "$(RED)TODO: Ubuntu LTS stability features$(NC)"

# Check code quality
check:
	@echo "🔍 Checking code quality..."
	cargo check --workspace
	cargo clippy --workspace -- -D warnings
	@echo "✅ Code quality check complete"

# Full validation pipeline
validate: format check test security-scan audit
	@echo "✅ Full validation complete"

# ===== MERGED CONTENT FROM CONFLICT RESOLUTION =====

# SynapticOS Makefile for Real Kernel Development

# Configuration
KERNEL_TARGET = x86_64-unknown-none
KERNEL_DIR = src/kernel
BUILD_DIR = build
ISO_DIR = $(BUILD_DIR)/iso
KERNEL_BIN = $(BUILD_DIR)/kernel.bin

# Tools
CARGO = cargo
RUST_FLAGS = --release
QEMU = qemu-system-x86_64
GRUB_MKRESCUE = grub-mkrescue

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
NC := \033[0m

.PHONY: all kernel clean qemu-test iso help dev-setup test

# Default target
all: kernel

# Build the kernel
kernel:
	@echo "$(BLUE)Building SynapticOS kernel...$(NC)"
	cd $(KERNEL_DIR) && $(CARGO) build $(RUST_FLAGS) --target $(KERNEL_TARGET)
	@mkdir -p $(BUILD_DIR)
	@cp $(KERNEL_DIR)/target/$(KERNEL_TARGET)/release/kernel $(KERNEL_BIN)
	@echo "$(GREEN)Kernel built successfully: $(KERNEL_BIN)$(NC)"

# Create bootable ISO
iso: kernel
	@echo "$(BLUE)Creating bootable ISO...$(NC)"
	@mkdir -p $(ISO_DIR)/boot/grub
	@cp $(KERNEL_BIN) $(ISO_DIR)/boot/kernel.bin
	@echo 'menuentry "SynapticOS" { multiboot /boot/kernel.bin }' > $(ISO_DIR)/boot/grub/grub.cfg
	$(GRUB_MKRESCUE) -o $(BUILD_DIR)/synapticos.iso $(ISO_DIR)
	@echo "$(GREEN)ISO created: $(BUILD_DIR)/synapticos.iso$(NC)"

# Test kernel in QEMU
qemu-test: kernel
	@echo "$(BLUE)Testing kernel in QEMU...$(NC)"
	$(QEMU) -kernel $(KERNEL_BIN) -display curses -serial stdio

# Test ISO in QEMU
qemu-iso: iso
	@echo "$(BLUE)Testing ISO in QEMU...$(NC)"
	$(QEMU) -cdrom $(BUILD_DIR)/synapticos.iso -display curses -serial stdio

# Clean build artifacts
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	cd $(KERNEL_DIR) && $(CARGO) clean
	rm -rf $(BUILD_DIR)
	@echo "$(GREEN)Clean complete$(NC)"

# Development setup
dev-setup:
	@echo "$(BLUE)Setting up development environment...$(NC)"
	rustup install nightly
	rustup component add rust-src llvm-tools-preview --toolchain nightly
	rustup target add $(KERNEL_TARGET) --toolchain nightly
	@echo "$(GREEN)Development environment ready$(NC)"

# Run kernel tests
test:
	@echo "$(BLUE)Running kernel tests...$(NC)"
	cd $(KERNEL_DIR) && $(CARGO) test --target $(KERNEL_TARGET)

# Phase 1 development targets
phase1-milestone1:
	@echo "$(YELLOW)Phase 1.1: Implementing multiboot2 bootloader...$(NC)"
	@echo "$(RED)TODO: Implement proper multiboot2 header$(NC)"
	@echo "$(RED)TODO: Set up GDT (Global Descriptor Table)$(NC)"
	@echo "$(RED)TODO: Initialize IDT (Interrupt Descriptor Table)$(NC)"
	@echo "$(RED)TODO: Set up basic exception handlers$(NC)"
	@echo "$(RED)TODO: Create proper kernel entry point$(NC)"

phase1-milestone2:
	@echo "$(YELLOW)Phase 1.2: Memory Management...$(NC)"
	@echo "$(RED)TODO: Physical memory manager (frame allocator)$(NC)"
	@echo "$(RED)TODO: Virtual memory with paging$(NC)"
	@echo "$(RED)TODO: Heap allocator for kernel$(NC)"
	@echo "$(RED)TODO: Memory protection mechanisms$(NC)"

cybersec-tools:
	@echo "$(YELLOW)Cybersecurity Tools Integration...$(NC)"
	@echo "$(RED)TODO: Integrate ParrotOS security tools$(NC)"
	@echo "$(RED)TODO: Add Kali Linux penetration testing suite$(NC)"
	@echo "$(RED)TODO: Include BlackArch exploit database$(NC)"
	@echo "$(RED)TODO: Ubuntu LTS stability features$(NC)"

# Help
help:
	@echo "$(GREEN)SynapticOS Real OS Development Build System$(NC)"
	@echo ""
	@echo "$(BLUE)Core Targets:$(NC)"
	@echo "  kernel          - Build the kernel binary"
	@echo "  iso             - Create bootable ISO image"
	@echo "  qemu-test       - Test kernel directly in QEMU"
	@echo "  qemu-iso        - Test ISO in QEMU"
	@echo "  test            - Run kernel unit tests"
	@echo "  clean           - Clean build artifacts"
	@echo "  dev-setup       - Setup development environment"
	@echo ""
	@echo "$(BLUE)Development Phases:$(NC)"
	@echo "  phase1-milestone1 - Phase 1.1 tasks (Bootloader)"
	@echo "  phase1-milestone2 - Phase 1.2 tasks (Memory Management)"
	@echo "  cybersec-tools    - Cybersecurity tools integration"
	@echo ""
	@echo "$(BLUE)Real OS Development Focus:$(NC)"
	@echo "  - Building actual bootable kernel (not simulation)"
	@echo "  - Cybersecurity education platform foundation"
	@echo "  - MSSP operations capabilities"
	@echo "  - ParrotOS enhancement with AI integration"
	@echo "  - ParrotOS enhancement with AI integration"
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
