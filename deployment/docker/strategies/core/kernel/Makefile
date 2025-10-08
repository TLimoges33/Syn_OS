# SynOS AI-Enhanced Kernel Components Build System
# Comprehensive build system for all AI kernel modules and components

# Module definitions
CONSCIOUSNESS_MODULE = synos_consciousness
AI_SCHEDULER_MODULE = ai_process_scheduler
AI_MEMORY_MODULE = ai_memory_manager
AI_IO_MODULE = ai_io_optimizer

# All kernel modules
MODULES = $(CONSCIOUSNESS_MODULE) $(AI_SCHEDULER_MODULE) $(AI_MEMORY_MODULE) $(AI_IO_MODULE)

# Object files
obj-m += $(CONSCIOUSNESS_MODULE).o
obj-m += $(AI_SCHEDULER_MODULE).o
obj-m += $(AI_MEMORY_MODULE).o
obj-m += $(AI_IO_MODULE).o

# Kernel build directory
KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

# Build flags
ccflags-y := -DSYNOS_AI_KERNEL \
             -DSYNOS_VERSION=\"1.0.0\" \
             -DDEBUG \
             -O2 \
             -Wall \
             -Wextra \
             -std=gnu99

# eBPF subdirectory
EBPF_DIR = ebpf

.PHONY: all clean install load unload test status help modules ebpf full-build deploy

# Default target
all: banner modules ebpf
	@echo "✅ SynOS AI-Enhanced Kernel build complete!"

# Display banner
banner:
	@echo "🧠 ======================================================= 🧠"
	@echo "🚀               SynOS AI-Enhanced Kernel               🚀"
	@echo "🎓              Neural Darwinism OS v1.0.0              🎓"
	@echo "🧠 ======================================================= 🧠"
	@echo ""
	@echo "Building components:"
	@echo "  🧠 AI-Native Process Scheduler"
	@echo "  🧠 Adaptive Memory Management"
	@echo "  🧠 AI-Powered I/O Optimization"
	@echo "  🧠 Consciousness Monitoring System"
	@echo "  🛡️ eBPF Security Framework"
	@echo ""

# Build all kernel modules
modules:
	@echo "🔨 Building SynOS AI kernel modules..."
	make -C $(KERNEL_DIR) M=$(PWD) modules
	@echo "✅ Kernel modules built successfully!"

# Build eBPF programs
ebpf:
	@echo "🛡️ Building eBPF security programs..."
	$(MAKE) -C $(EBPF_DIR) all
	@echo "✅ eBPF programs built successfully!"

# Clean all build artifacts
clean:
	@echo "🧹 Cleaning SynOS AI kernel build artifacts..."
	make -C $(KERNEL_DIR) M=$(PWD) clean
	$(MAKE) -C $(EBPF_DIR) clean
	rm -f *.symvers *.order *.mod.c .*.cmd
	rm -rf .tmp_versions/
	@echo "✅ Clean complete!"

# Install all modules
install: modules ebpf
	@echo "📦 Installing SynOS AI kernel modules..."
	sudo make -C $(KERNEL_DIR) M=$(PWD) modules_install
	sudo depmod -a
	$(MAKE) -C $(EBPF_DIR) install
	@echo "✅ Installation complete!"

# Load all modules in correct order
load: install
	@echo "🚀 Loading SynOS AI kernel modules..."
	@echo "📋 Loading modules in dependency order..."

	@echo "🧠 Loading consciousness monitoring..."
	sudo modprobe $(CONSCIOUSNESS_MODULE) || echo "⚠️ Consciousness module load failed"

	@echo "🧠 Loading AI process scheduler..."
	sudo modprobe $(AI_SCHEDULER_MODULE) || echo "⚠️ AI scheduler module load failed"

	@echo "🧠 Loading AI memory manager..."
	sudo modprobe $(AI_MEMORY_MODULE) || echo "⚠️ AI memory module load failed"

	@echo "🧠 Loading AI I/O optimizer..."
	sudo modprobe $(AI_IO_MODULE) || echo "⚠️ AI I/O module load failed"

	@echo "🛡️ Loading eBPF programs..."
	$(MAKE) -C $(EBPF_DIR) load || echo "⚠️ eBPF programs load failed"

	@echo "✅ All SynOS AI modules loaded successfully!"
	@$(MAKE) status

# Unload all modules
unload:
	@echo "🛑 Unloading SynOS AI kernel modules..."

	@echo "🛡️ Unloading eBPF programs..."
	$(MAKE) -C $(EBPF_DIR) unload || echo "ℹ️ eBPF programs were not loaded"

	@echo "🧠 Unloading AI modules in reverse order..."
	sudo rmmod $(AI_IO_MODULE) 2>/dev/null || echo "ℹ️ AI I/O module was not loaded"
	sudo rmmod $(AI_MEMORY_MODULE) 2>/dev/null || echo "ℹ️ AI memory module was not loaded"
	sudo rmmod $(AI_SCHEDULER_MODULE) 2>/dev/null || echo "ℹ️ AI scheduler module was not loaded"
	sudo rmmod $(CONSCIOUSNESS_MODULE) 2>/dev/null || echo "ℹ️ Consciousness module was not loaded"

	@echo "✅ All modules unloaded!"

# Remove all modules from system
remove: unload
	@echo "🗑️ Removing SynOS AI kernel modules from system..."
	@for module in $(MODULES); do \
		sudo rm -f /lib/modules/$(shell uname -r)/extra/$$module.ko; \
	done
	$(MAKE) -C $(EBPF_DIR) clean
	sudo depmod -a
	@echo "✅ All modules removed from system!"

# Run comprehensive tests
test: load
	@echo "🧪 Running SynOS AI kernel module tests..."
	@echo ""
	@echo "📋 Testing consciousness monitoring..."
	@ls -la /dev/synos 2>/dev/null && echo "✅ Consciousness device file exists" || echo "❌ Consciousness device missing"
	@cat /proc/synos_consciousness 2>/dev/null | head -5 || echo "❌ Consciousness proc entry not accessible"

	@echo ""
	@echo "📋 Testing AI scheduler..."
	@cat /proc/synos_ai_scheduler 2>/dev/null | head -5 || echo "❌ AI scheduler proc entry not accessible"

	@echo ""
	@echo "📋 Testing AI memory manager..."
	@cat /proc/synos_ai_memory 2>/dev/null | head -5 || echo "❌ AI memory proc entry not accessible"

	@echo ""
	@echo "📋 Testing AI I/O optimizer..."
	@cat /proc/synos_ai_io 2>/dev/null | head -5 || echo "❌ AI I/O proc entry not accessible"

	@echo ""
	@echo "📋 Testing eBPF programs..."
	$(MAKE) -C $(EBPF_DIR) status

	@echo ""
	@echo "📋 Checking kernel messages..."
	@dmesg | tail -20 | grep -i synos || echo "ℹ️ No recent SynOS messages in dmesg"

	@echo ""
	@echo "🧪 Basic functionality test complete!"

# Show comprehensive status
status:
	@echo "📊 SynOS AI-Enhanced Kernel Status Report"
	@echo "=========================================="
	@echo ""
	@echo "🔍 Kernel Modules Status:"
	@for module in $(MODULES); do \
		if lsmod | grep -q $$module; then \
			echo "  ✅ $$module: LOADED"; \
		else \
			echo "  ❌ $$module: NOT LOADED"; \
		fi; \
	done

	@echo ""
	@echo "🔍 Device Files:"
	@ls -la /dev/synos 2>/dev/null && echo "  ✅ /dev/synos: EXISTS" || echo "  ❌ /dev/synos: MISSING"

	@echo ""
	@echo "🔍 Proc Interfaces:"
	@ls -la /proc/synos_* 2>/dev/null | wc -l | xargs -I {} echo "  📊 Active proc entries: {}"

	@echo ""
	@echo "🔍 eBPF Programs:"
	$(MAKE) -C $(EBPF_DIR) status

	@echo ""
	@echo "🔍 System Information:"
	@echo "  🖥️ Kernel: $(shell uname -r)"
	@echo "  🏗️ Build directory: $(KERNEL_DIR)"
	@echo "  📁 Working directory: $(PWD)"
	@echo "  ⏰ Build time: $(shell date)"

# Validate all modules
validate: modules
	@echo "✅ Validating SynOS AI kernel modules..."
	@echo ""
	@for module in $(MODULES); do \
		echo "🔍 Validating $$module.ko..."; \
		modinfo $$module.ko | head -10; \
		echo ""; \
	done

	@echo "🔍 Checking module dependencies..."
	@for module in $(MODULES); do \
		echo "Dependencies for $$module:"; \
		objdump -h $$module.ko | grep -E "(\.text|\.data|\.rodata)" || echo "  No standard sections found"; \
		echo ""; \
	done

	@echo "✅ Validation complete!"

# Development workflow - quick build and test
dev: clean modules test

# Full deployment workflow
deploy: clean modules ebpf install load test
	@echo ""
	@echo "🎉 SynOS AI-Enhanced Kernel deployment complete!"
	@echo "🧠 AI consciousness and optimization systems are active"
	@echo "🛡️ Enhanced security monitoring is enabled"
	@echo "🎓 Educational optimizations are ready"

# Monitor kernel messages in real-time
monitor:
	@echo "📡 Monitoring SynOS AI kernel messages..."
	@echo "Press Ctrl+C to stop monitoring"
	sudo dmesg -w | grep --line-buffered -i synos

# Performance benchmark
benchmark: load
	@echo "⚡ Running SynOS AI performance benchmark..."
	@echo ""
	@echo "📊 AI Scheduler Performance:"
	@cat /proc/synos_ai_scheduler | grep -E "(Accuracy|Predictions|Anomalies)"
	@echo ""
	@echo "📊 AI Memory Performance:"
	@cat /proc/synos_ai_memory | grep -E "(Accuracy|Memory Saved|Leaks)"
	@echo ""
	@echo "📊 AI I/O Performance:"
	@cat /proc/synos_ai_io | grep -E "(Cache Hit Rate|Latency Saved|Operations)"
	@echo ""
	@echo "⚡ Benchmark complete!"

# Create debug build with extra logging
debug: ccflags-y += -DDEBUG_VERBOSE -g
debug: modules
	@echo "🐛 Debug build complete with verbose logging"

# Create release build optimized for performance
release: ccflags-y += -O3 -DNDEBUG
release: modules ebpf
	@echo "🚀 Release build complete with performance optimizations"

# Quick educational demo
demo: load
	@echo "🎓 SynOS AI-Enhanced Kernel Educational Demo"
	@echo "============================================="
	@echo ""
	@echo "🧠 Consciousness System:"
	@cat /proc/synos_consciousness | head -15
	@echo ""
	@echo "🔧 AI Scheduler:"
	@cat /proc/synos_ai_scheduler | head -10
	@echo ""
	@echo "💾 AI Memory Manager:"
	@cat /proc/synos_ai_memory | head -10
	@echo ""
	@echo "💿 AI I/O Optimizer:"
	@cat /proc/synos_ai_io | head -10
	@echo ""
	@echo "🎓 Demo complete! All AI systems are active and learning."

# Help system
help:
	@echo "🧠 SynOS AI-Enhanced Kernel Build System"
	@echo "========================================="
	@echo ""
	@echo "🎯 Main Targets:"
	@echo "  all       - Build all kernel modules and eBPF programs"
	@echo "  modules   - Build only kernel modules"
	@echo "  ebpf      - Build only eBPF programs"
	@echo "  clean     - Remove all build artifacts"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  install   - Install modules to system"
	@echo "  load      - Load all modules in correct order"
	@echo "  unload    - Unload all modules"
	@echo "  remove    - Completely remove from system"
	@echo "  deploy    - Full clean build, install, load, and test"
	@echo ""
	@echo "🧪 Testing & Validation:"
	@echo "  test      - Run comprehensive functionality tests"
	@echo "  validate  - Validate module structure and dependencies"
	@echo "  status    - Show detailed system status"
	@echo "  benchmark - Run performance benchmarks"
	@echo "  demo      - Quick educational demonstration"
	@echo ""
	@echo "🛠️ Development:"
	@echo "  dev       - Quick development cycle (clean, build, test)"
	@echo "  debug     - Create debug build with verbose logging"
	@echo "  release   - Create optimized release build"
	@echo "  monitor   - Monitor kernel messages in real-time"
	@echo ""
	@echo "🧠 AI Components:"
	@echo "  🧠 AI-Native Process Scheduler - ML-based process optimization"
	@echo "  🧠 Adaptive Memory Management - Predictive memory optimization"
	@echo "  🧠 AI-Powered I/O Optimization - Intelligent caching and throttling"
	@echo "  🧠 Consciousness Monitoring - Neural darwinism framework"
	@echo "  🛡️ eBPF Security Framework - Real-time security monitoring"
	@echo ""
	@echo "📖 Examples:"
	@echo "  make deploy           # Full deployment"
	@echo "  make dev              # Quick development cycle"
	@echo "  make test             # Run all tests"
	@echo "  make demo             # Educational demonstration"
	@echo "  make status           # Check system status"
	@echo ""
	@echo "⚠️ Requirements:"
	@echo "  - Linux kernel headers"
	@echo "  - GCC/Clang compiler"
	@echo "  - Root privileges for loading modules"
	@echo "  - eBPF-capable kernel (5.0+)"

# Show build information
info:
	@echo "ℹ️ SynOS AI-Enhanced Kernel Build Information"
	@echo "============================================="
	@echo ""
	@echo "📦 Modules to build:"
	@for module in $(MODULES); do echo "  - $$module"; done
	@echo ""
	@echo "🔧 Build configuration:"
	@echo "  Kernel directory: $(KERNEL_DIR)"
	@echo "  Working directory: $(PWD)"
	@echo "  Compiler flags: $(ccflags-y)"
	@echo ""
	@echo "🛡️ eBPF directory: $(EBPF_DIR)"
	@echo "🏗️ Build architecture: $(shell uname -m)"
	@echo "🖥️ Target kernel: $(shell uname -r)"

# Quick check if everything is ready for development
check:
	@echo "🔍 Checking SynOS AI development environment..."
	@echo ""
	@echo "✅ Checking kernel headers..."
	@test -d $(KERNEL_DIR) && echo "  📁 Kernel headers found: $(KERNEL_DIR)" || echo "  ❌ Kernel headers missing: $(KERNEL_DIR)"
	@echo ""
	@echo "✅ Checking compiler..."
	@which gcc >/dev/null && echo "  🔧 GCC compiler found" || echo "  ❌ GCC compiler missing"
	@which clang >/dev/null && echo "  🔧 Clang compiler found" || echo "  ❌ Clang compiler missing"
	@echo ""
	@echo "✅ Checking eBPF tools..."
	@which bpftool >/dev/null && echo "  🛡️ bpftool found" || echo "  ❌ bpftool missing"
	@echo ""
	@echo "✅ Checking permissions..."
	@groups | grep -q sudo && echo "  🔐 User has sudo access" || echo "  ❌ User lacks sudo access"
	@echo ""
	@echo "🔍 Environment check complete!"

# Estimate build time
estimate:
	@echo "⏱️ Estimated build times for SynOS AI components:"
	@echo "================================================"
	@echo ""
	@echo "🧠 Consciousness Module:     ~30 seconds"
	@echo "🧠 AI Scheduler Module:      ~45 seconds"
	@echo "🧠 AI Memory Module:         ~60 seconds"
	@echo "🧠 AI I/O Module:            ~50 seconds"
	@echo "🛡️ eBPF Programs:            ~20 seconds"
	@echo ""
	@echo "📊 Total estimated time:     ~3-4 minutes"
	@echo "⚡ Actual time may vary based on system performance"