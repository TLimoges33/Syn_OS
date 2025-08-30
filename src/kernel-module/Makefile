# SynOS Consciousness Monitoring Kernel Module
# Phase 4.2: Advanced Logging and Debugging Infrastructure

obj-m += synos_consciousness.o

# Kernel build directory
KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build

# Build directory
PWD := $(shell pwd)

# Module info
MODULE_NAME = synos_consciousness
MODULE_VERSION = 4.2.0

# Compiler flags
ccflags-y += -DDEBUG
ccflags-y += -DMODULE_VERSION=\"$(MODULE_VERSION)\"

# Default target
all:
	@echo "Building SynOS Phase 4.2 consciousness monitoring kernel module..."
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules
	@echo "Module built successfully: $(MODULE_NAME).ko"

# Clean target
clean:
	@echo "Cleaning build artifacts..."
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean
	rm -f *.symvers *.order *.mod.c
	@echo "Clean complete"

# Install module (requires root)
install: all
	@echo "Installing SynOS consciousness monitoring module..."
	sudo insmod $(MODULE_NAME).ko
	@echo "Module installed. Check dmesg for status."
	@echo "Device available at: /dev/synos"
	@echo "Proc interface at: /proc/synos_consciousness"

# Remove module
remove:
	@echo "Removing SynOS consciousness monitoring module..."
	sudo rmmod $(MODULE_NAME)
	@echo "Module removed"

# Reload module (clean install)
reload: remove install

# Show module info
info:
	@echo "=== SynOS Phase 4.2 Module Information ==="
	@echo "Module: $(MODULE_NAME)"
	@echo "Version: $(MODULE_VERSION)"
	@echo "Source: $(PWD)/$(MODULE_NAME).c"
	@echo "Kernel: $(shell uname -r)"
	@echo "Build Dir: $(KERNEL_DIR)"
	@if lsmod | grep -q $(MODULE_NAME); then \
		echo "Status: LOADED"; \
		echo "Device: /dev/synos"; \
		echo "Proc: /proc/synos_consciousness"; \
	else \
		echo "Status: NOT LOADED"; \
	fi

# Test module functionality
test: install
	@echo "=== Testing SynOS Consciousness Module ==="
	@echo "1. Reading device status..."
	@sudo cat /dev/synos
	@echo ""
	@echo "2. Reading proc interface..."
	@cat /proc/synos_consciousness
	@echo ""
	@echo "3. Testing component registration..."
	@echo "REGISTER:test_component" | sudo tee /dev/synos > /dev/null
	@echo "4. Testing logging..."
	@echo "LOG:Test message from userspace" | sudo tee /dev/synos > /dev/null
	@echo "5. Testing events..."
	@echo "EVENT:Test event from userspace" | sudo tee /dev/synos > /dev/null
	@echo ""
	@echo "6. Final status check..."
	@cat /proc/synos_consciousness
	@echo ""
	@echo "Test complete!"

# Debug target - load module with debug info
debug: all
	@echo "Loading module in debug mode..."
	sudo dmesg -C  # Clear dmesg
	sudo insmod $(MODULE_NAME).ko
	@echo "Module loaded. Monitoring dmesg output:"
	dmesg | tail -20

# Monitor kernel messages
monitor:
	@echo "Monitoring SynOS kernel messages (Ctrl+C to exit)..."
	sudo dmesg -w | grep -i synos

# Show module dependencies
deps:
	@echo "=== Module Dependencies ==="
	@if [ -f $(MODULE_NAME).ko ]; then \
		modinfo $(MODULE_NAME).ko | grep depends; \
		modinfo $(MODULE_NAME).ko | grep vermagic; \
	else \
		echo "Module not built. Run 'make all' first."; \
	fi

# Help target
help:
	@echo "=== SynOS Phase 4.2 Kernel Module Build System ==="
	@echo ""
	@echo "Available targets:"
	@echo "  all       - Build the kernel module"
	@echo "  clean     - Remove build artifacts"
	@echo "  install   - Install the module (requires root)"
	@echo "  remove    - Remove the installed module"
	@echo "  reload    - Remove and reinstall the module"
	@echo "  info      - Show module information and status"
	@echo "  test      - Install and test module functionality"
	@echo "  debug     - Load module with debug monitoring"
	@echo "  monitor   - Monitor kernel messages from SynOS"
	@echo "  deps      - Show module dependencies"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Example usage:"
	@echo "  make all        # Build module"
	@echo "  make install    # Install module"
	@echo "  make test       # Test functionality"
	@echo "  make remove     # Remove module"
	@echo ""
	@echo "Phase 4.2 Features:"
	@echo "  ✓ Consciousness component monitoring"
	@echo "  ✓ Advanced logging with 9 levels, 11 categories"
	@echo "  ✓ Debug infrastructure and system analysis"
	@echo "  ✓ Kernel thread for continuous monitoring"
	@echo "  ✓ Device interface (/dev/synos)"
	@echo "  ✓ Proc interface (/proc/synos_consciousness)"
	@echo "  ✓ IOCTL commands for advanced control"

.PHONY: all clean install remove reload info test debug monitor deps help
