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