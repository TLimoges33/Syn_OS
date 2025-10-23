# SynOS AI Subsystem Architecture

This directory contains all AI-related components organized into a unified architecture.

## Directory Structure

```
src/ai/
├── daemons/              # Python AI daemons and services
│   ├── alfred/           # ALFRED voice assistant (90% complete, 314 lines)
│   │   ├── alfred-daemon.py
│   │   ├── alfred.service
│   │   └── commands/     # Voice command modules
│   └── consciousness/    # AI consciousness daemon
│       ├── consciousness-daemon.py  # Neural Darwinism security monitoring
│       └── README.md
│
├── advanced/             # C-based advanced AI features
│   ├── autonomous_optimization/
│   ├── autonomous_systems/
│   ├── consciousness_future/
│   ├── neural_evolution/
│   ├── predictive_intelligence/
│   ├── quantum_consciousness/
│   ├── quantum_entanglement/
│   ├── quantum_forecasting/
│   ├── quantum_hardware/
│   ├── quantum_ml/
│   └── quantum_simulation/
│
├── engine/               # Rust high-level AI engine (synaptic-ai-engine)
│   ├── Cargo.toml
│   ├── REORGANIZATION_GUIDE.md
│   └── src/
│       ├── lib.rs        # Main AI engine interface
│       ├── consciousness/ # Neural Darwinism consciousness
│       ├── hal/          # Hardware abstraction layer
│       ├── ipc/          # Inter-process communication
│       ├── linux/        # Linux integration
│       ├── models/       # ML model management
│       └── runtime/      # Task scheduling and execution
│
└── runtime/              # Rust low-level inference engine (synos-ai-runtime)
    ├── Cargo.toml
    ├── build.rs          # FFI library linking
    ├── lib.rs            # Runtime interface (no_std compatible)
    ├── native_inference.rs # Pure Rust neural networks
    ├── model-manager/    # Model encryption and storage
    ├── tflite/           # TensorFlow Lite FFI (75% complete, library installed)
    ├── onnx/             # ONNX Runtime FFI (30% complete, 4 stubs remain)
    └── pytorch/          # PyTorch LibTorch FFI (25% complete, 3 stubs remain)
```

## Component Roles

### 🐍 Daemons (Python)
**Purpose:** User-facing AI services and assistants
- **ALFRED:** Voice assistant with British butler persona, security tool launching
- **Consciousness:** Real-time security monitoring and threat detection
- **Integration:** systemd services, NATS message bus, RESTful APIs

### 🔬 Advanced (C)
**Purpose:** Cutting-edge AI research implementations
- Quantum computing integration
- Neural evolution engines
- Predictive intelligence systems
- Future consciousness modeling

### 🏗️ Engine (Rust std)
**Purpose:** High-level AI orchestration and management
- **Crate:** `synaptic-ai-engine`
- **Target:** Standard Linux distribution (std environment)
- **Features:**
  - Multi-runtime support (TFLite, ONNX, PyTorch)
  - Hardware acceleration (NPU, GPU, TPU via HAL)
  - Consciousness engine with Neural Darwinism
  - Linux integration (systemd, D-Bus)
  - Model lifecycle management

### ⚡ Runtime (Rust no_std)
**Purpose:** Low-level inference engine for kernel and embedded
- **Crate:** `synos-ai-runtime`
- **Target:** no_std compatible (kernel, embedded systems)
- **Features:**
  - Lightweight native inference (pure Rust neural networks)
  - FFI bindings to TensorFlow Lite, ONNX Runtime, PyTorch
  - Model encryption (AES-256-GCM)
  - Hardware acceleration support
  - Zero external dependencies (configurable)

## AI Runtime Status (October 22, 2025)

### TensorFlow Lite ✅ 75% Complete
- **Library:** INSTALLED at `/usr/local/lib/libtensorflowlite_c.so` (4.4MB)
- **Status:** FFI bindings complete, stubs removed
- **Remaining:** GPU delegate integration, benchmarks, testing

### ONNX Runtime ⏳ 30% Complete
- **Library:** NOT INSTALLED (blocker)
- **Status:** Structure exists, 4 stubs remain
- **Stub Locations:** `runtime/onnx/mod.rs` lines 162, 169, 176, 184
- **Required:** Install ONNX Runtime v1.16.0

### PyTorch LibTorch ⏳ 25% Complete
- **Library:** NOT INSTALLED (blocker)
- **Status:** Structure exists, 3 stubs remain
- **Stub Locations:** `runtime/pytorch/mod.rs` lines 173, 184, 225
- **Required:** Install LibTorch v2.1.0

## Integration Points

### Kernel Integration
```rust
// Kernel AI interface (src/kernel/src/ai_interface.rs)
use synos_ai_runtime::{NeuralNetwork, ModelWeights};

pub struct AIInterface {
    optimization_level: u8,
    awareness_level: u8,
    memory_patterns: BTreeMap<u64, u64>,
}
```

### Userspace Integration
```rust
// AI Engine integration (src/ai/engine/src/lib.rs)
use synaptic_ai_engine::{AIEngine, RuntimeConfig};

let engine = AIEngine::new().await?;
engine.start_runtime(config).await?;
```

### Python Integration
```python
# ALFRED integration with consciousness daemon
from consciousness_daemon import ConsciousnessState, PatternRecognizer

state = ConsciousnessState()
recognizer = PatternRecognizer()
```

## Development Roadmap

### Short-Term (Next Month)
1. ✅ **TFLite GPU Delegate** - Complete hardware acceleration
2. 🔄 **Install ONNX Runtime** - Unblock Week 3-4 development
3. 🔄 **Install PyTorch LibTorch** - Unblock Week 5-6 development
4. 🔄 **Remove Remaining Stubs** - 7 stubs total (4 ONNX + 3 PyTorch)
5. 🔄 **ALFRED Polish** - Reach 100% completion

### Medium-Term (3-6 Months)
- Model encryption and signing complete
- Educational AI tutor integration
- Cross-tool automation workflows
- Advanced consciousness features

## Documentation

- **Engine Details:** `engine/REORGANIZATION_GUIDE.md`
- **Runtime API:** `runtime/README.md`
- **ALFRED Commands:** `daemons/alfred/commands/`
- **Consciousness System:** `daemons/consciousness/README.md`
- **Roadmap Audit:** `../../docs/07-audits/ROADMAP_AUDIT_2025-10-22.md`

## Building

```bash
# Build AI engine (high-level orchestration)
cargo build --package synaptic-ai-engine

# Build AI runtime (low-level inference)
cargo build --package synos-ai-runtime

# Build with specific runtime features
cargo build --package synos-ai-runtime --features "tensorflow-lite,onnx-runtime,pytorch"

# Start ALFRED voice assistant
sudo systemctl start alfred

# Start consciousness daemon
sudo systemctl start synos-consciousness
```

## Previous Organization (Archive)

**Old Structure (before October 22, 2025):**
- `src/ai-engine/` → NOW: `src/ai/engine/`
- `src/ai-runtime/` → NOW: `src/ai/runtime/`
- `src/ai/alfred/` → NOW: `src/ai/daemons/alfred/`
- `src/ai/consciousness/` → NOW: `src/ai/daemons/consciousness/`

**Reason for Reorganization:**
- Reduced redundancy and improved discoverability
- Unified AI architecture under single parent directory
- Clearer separation of concerns (daemons vs engine vs runtime)
- Better alignment with project structure conventions

## Contributing

When adding new AI features:
1. **Python services** → `daemons/` (systemd services, APIs)
2. **Rust high-level** → `engine/src/` (orchestration, management)
3. **Rust low-level** → `runtime/` (inference, FFI bindings)
4. **C research** → `advanced/` (experimental features)

See `CONTRIBUTING.md` for detailed guidelines.
