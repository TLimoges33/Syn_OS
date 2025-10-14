# Command Reference

## System Commands

### synos-status
Check system status and health.

```bash
# Basic status
synos-status

# Detailed status
synos-status --verbose

# Specific component status
synos-status --component consciousness
synos-status --component security
synos-status --component kernel
```

### synos-config
Manage system configuration.

```bash
# View current configuration
synos-config show

# Set configuration parameter
synos-config set consciousness.neural_populations 2048

# Get configuration parameter
synos-config get security.ebpf_enabled
```

## Consciousness Commands

### synos-consciousness
Manage consciousness substrate.

```bash
# Start consciousness substrate
synos-consciousness start

# Stop consciousness substrate
synos-consciousness stop

# Check consciousness status
synos-consciousness status

# Calibrate neural networks
synos-consciousness calibrate

# Backup consciousness state
synos-consciousness backup --output /backup/consciousness.bin
```

### synos-neural
Neural network management.

```bash
# List neural populations
synos-neural list

# Create new population
synos-neural create --size 1000 --type associative

# Train neural network
synos-neural train --population pop1 --dataset /data/training.dat
```

## Security Commands

### synos-security
Security management and monitoring.

```bash
# Check security status
synos-security status

# Load security program
synos-security load --program /etc/synos/security/monitor.bpf

# View security events
synos-security events --since "1 hour ago"

# Run security scan
synos-security scan --full
```

## Development Commands

### synos-build
Build system components.

```bash
# Build kernel modules
synos-build kernel

# Build consciousness components
synos-build consciousness

# Build all components
synos-build all

# Clean build artifacts
synos-build clean
```

### synos-test
Testing and validation.

```bash
# Run unit tests
synos-test unit

# Run integration tests
synos-test integration

# Run performance tests
synos-test performance

# Run all tests
synos-test all
```

## Diagnostic Commands

### synos-debug
Debug and troubleshooting.

```bash
# Enable debug mode
synos-debug enable

# Capture system trace
synos-debug trace --duration 30s --output trace.dat

# Analyze consciousness activity
synos-debug consciousness --monitor --duration 10s
```
