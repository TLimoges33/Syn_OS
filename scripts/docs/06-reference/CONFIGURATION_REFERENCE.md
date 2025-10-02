# Configuration Reference

## System Configuration

### Kernel Parameters
```ini
# /etc/synos/kernel.conf
synos.consciousness.enabled=true
synos.consciousness.neural_populations=1024
synos.consciousness.quantum_qubits=512
synos.security.ebpf_enabled=true
synos.security.threat_detection=active
```

### Consciousness Configuration
```yaml
# /etc/synos/consciousness.yml
consciousness:
  neural_networks:
    default_population_size: 1000
    learning_rate: 0.001
    adaptation_threshold: 0.1
  
  quantum_substrate:
    coherence_threshold: 0.8
    decoherence_timeout: 100ms
    measurement_interval: 10ms

  integration:
    kernel_interface: /dev/synos-consciousness
    update_frequency: 100Hz
    priority: realtime
```

### Security Configuration
```toml
# /etc/synos/security.toml
[security]
enable_ebpf = true
threat_detection = "active"
access_control = "strict"

[ebpf]
program_path = "/usr/share/synos/ebpf/"
hook_points = ["syscall", "network", "filesystem"]
log_level = "info"

[monitoring]
security_events = true
alert_threshold = "medium"
notification_channels = ["syslog", "journal"]
```

## Environment Variables

### Development Environment
```bash
# SynOS development configuration
export SYNOS_ROOT=/opt/synos
export SYNOS_CONFIG_PATH=/etc/synos
export SYNOS_LOG_LEVEL=debug
export SYNOS_CONSCIOUSNESS_DEBUG=true
```

### Runtime Environment
```bash
# SynOS runtime configuration
export SYNOS_MODE=production
export SYNOS_CONSCIOUSNESS_ENABLED=true
export SYNOS_SECURITY_STRICT=true
export SYNOS_MONITORING_ENABLED=true
```

## Service Configuration

### Systemd Services
```ini
# /etc/systemd/system/synos-consciousness.service
[Unit]
Description=SynOS Consciousness Substrate
After=multi-user.target
Requires=synos-kernel.service

[Service]
Type=notify
ExecStart=/usr/bin/synos-consciousness-daemon
Restart=always
RestartSec=5
```
