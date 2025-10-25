# SynOS Consciousness Kernel Module Makefile
# Advanced build system for consciousness-aware kernel module

obj-m := synos_consciousness.o

# Kernel build directory - autodetect
KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build

# Module information
MODULE_NAME = synos_consciousness
MODULE_VERSION = 4.2.0

# Build flags for enhanced debugging and optimization
ccflags-y := -DMODULE_VERSION=\"$(MODULE_VERSION)\" \
             -DDEBUG \
             -O2 \
             -Wall \
             -Wextra

# Default target
all: build

# Build the kernel module
build:
	@echo "🧠 Building SynOS Consciousness Kernel Module v$(MODULE_VERSION)..."
	make -C $(KERNEL_DIR) M=$(PWD) modules
	@echo "✅ Build complete!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	make -C $(KERNEL_DIR) M=$(PWD) clean
	rm -f *.symvers *.order *.mod.c
	@echo "✅ Clean complete!"

# Install the module
install: build
	@echo "📦 Installing SynOS Consciousness Module..."
	sudo make -C $(KERNEL_DIR) M=$(PWD) modules_install
	sudo depmod -a
	@echo "✅ Installation complete!"

# Load the module
load: install
	@echo "🚀 Loading SynOS Consciousness Module..."
	sudo modprobe $(MODULE_NAME)
	@echo "✅ Module loaded successfully!"
	@echo "📊 Module information:"
	@lsmod | grep $(MODULE_NAME) || echo "❌ Module not found in lsmod"
	@echo "🔍 Device information:"
	@ls -la /dev/synos 2>/dev/null || echo "❌ Device file not created"

# Unload the module
unload:
	@echo "🛑 Unloading SynOS Consciousness Module..."
	sudo rmmod $(MODULE_NAME) 2>/dev/null || echo "ℹ️ Module was not loaded"
	@echo "✅ Module unloaded!"

# Remove/uninstall the module
remove: unload
	@echo "🗑️ Removing SynOS Consciousness Module..."
	sudo rm -f /lib/modules/$(shell uname -r)/extra/$(MODULE_NAME).ko
	sudo depmod -a
	@echo "✅ Module removed!"

# Test the module
test: load
	@echo "🧪 Testing SynOS Consciousness Module..."
	@echo "📋 Checking kernel messages..."
	@dmesg | tail -10 | grep -i synos || echo "⚠️ No SynOS messages in dmesg"
	@echo "🔍 Checking device file..."
	@ls -la /dev/synos || echo "❌ Device file not found"
	@echo "📊 Checking proc entry..."
	@ls -la /proc/synos_consciousness 2>/dev/null || echo "ℹ️ Proc entry not found (may be normal)"
	@echo "🔍 Module information:"
	@modinfo $(MODULE_NAME).ko | head -10

# Debug mode - load with verbose kernel messages
debug: build
	@echo "🐛 Loading module in debug mode..."
	sudo dmesg -C  # Clear kernel messages
	sudo insmod ./$(MODULE_NAME).ko
	@echo "📋 Recent kernel messages:"
	@dmesg | tail -20

# Monitor kernel messages in real-time
monitor:
	@echo "📡 Monitoring kernel messages for SynOS..."
	@echo "Press Ctrl+C to stop monitoring"
	sudo dmesg -w | grep --line-buffered -i synos

# Show module status
status:
	@echo "📊 SynOS Consciousness Module Status"
	@echo "===================================="
	@echo "🔍 Module loaded:"
	@lsmod | grep $(MODULE_NAME) && echo "✅ YES" || echo "❌ NO"
	@echo "🔍 Device file:"
	@ls -la /dev/synos 2>/dev/null && echo "✅ EXISTS" || echo "❌ MISSING"
	@echo "🔍 Kernel version compatibility:"
	@uname -r
	@echo "🔍 Build directory:"
	@echo "$(KERNEL_DIR)"

# Validate module and dependencies
validate: build
	@echo "✅ Validating SynOS Consciousness Module..."
	@echo "🔍 Module information:"
	@modinfo $(MODULE_NAME).ko
	@echo "🔍 Symbol dependencies:"
	@objdump -t $(MODULE_NAME).ko | grep UND | head -10 || echo "ℹ️ No undefined symbols found"
	@echo "🔍 Module size:"
	@ls -lh $(MODULE_NAME).ko

# Development help
help:
	@echo "🧠 SynOS Consciousness Kernel Module Build System"
	@echo "================================================="
	@echo ""
	@echo "Available targets:"
	@echo "  build     - Compile the kernel module"
	@echo "  clean     - Remove build artifacts"
	@echo "  install   - Install module to system"
	@echo "  load      - Load the module into kernel"
	@echo "  unload    - Unload the module from kernel"
	@echo "  remove    - Completely remove module from system"
	@echo "  test      - Load and test module functionality"
	@echo "  debug     - Load with debug output"
	@echo "  monitor   - Monitor kernel messages in real-time"
	@echo "  status    - Show current module status"
	@echo "  validate  - Validate module build and dependencies"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Usage examples:"
	@echo "  make build          # Just compile"
	@echo "  make test           # Full build, install, load, and test"
	@echo "  make debug          # Load with verbose debugging"
	@echo "  make monitor        # Watch kernel messages"
	@echo "  make clean remove   # Complete cleanup"
	@echo ""
	@echo "Module: $(MODULE_NAME) v$(MODULE_VERSION)"
	@echo "Kernel: $(shell uname -r)"

# Quick development cycle
dev: clean build debug

# Complete build and test cycle
full: clean build install test

# Safety target to prevent accidental makes
.PHONY: all build clean install load unload remove test debug monitor status validate help dev full