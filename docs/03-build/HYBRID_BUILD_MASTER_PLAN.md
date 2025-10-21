# SynOS v1.0 Hybrid Architecture - Complete Build Plan
**Date:** October 17, 2025
**Architecture:** Option 3 - Hybrid (Base + VM Orchestrator + Mega VM)
**Status:** Implementation Ready

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SynOS v1.0 Hybrid System                      │
└─────────────────────────────────────────────────────────────────┘

Boot Menu:
┌──────────────────────────────────────────────────┐
│  SynOS v1.0 - AI-Enhanced Security Platform     │
│                                                  │
│  [1] VM Orchestrator Mode (Recommended)         │
│      Launch AI-managed virtual lab environment  │
│                                                  │
│  [2] All-in-One Mode                            │
│      Boot into mega VM (traditional experience) │
│                                                  │
│  [3] Minimal Host Only                          │
│      Lightweight host, no VMs                   │
└──────────────────────────────────────────────────┘

OPTION 1: VM Orchestrator Mode
┌────────────────────────────────────────┐
│   SynOS Host OS (3-4GB)                │
│   ├── ParrotOS Minimal Base            │
│   ├── SynOS AI Components ⭐           │
│   │   ├── Consciousness Engine         │
│   │   ├── ALFRED Voice Assistant       │
│   │   └── VM Orchestrator Copilot ⭐   │
│   ├── KVM/QEMU + libvirt               │
│   └── Docker + Kubernetes (optional)   │
└────────────────────────────────────────┘
           │
           │ User selects lab/scenario
           ▼
┌────────────────────────────────────────┐
│   AI-Managed VM Library                │
│   ┌──────────────────────────────────┐ │
│   │  Active Scenario:                 │ │
│   │  "IT 651 - AD Attack Lab"         │ │
│   │                                   │ │
│   │  [VM] Kali Linux (attacker)       │ │
│   │  [VM] Windows Server 2022 DC      │ │
│   │  [VM] Windows 10 Client           │ │
│   │  [VM] Security Onion (monitor)    │ │
│   │                                   │ │
│   │  Network: Isolated 192.168.56.0/24│ │
│   └──────────────────────────────────┘ │
│                                        │
│   Available VMs (download on-demand):  │
│   ├── kali-full.qcow2 (8GB)           │
│   ├── parrot-security.qcow2 (6GB)     │
│   ├── windows-server-2022-dc.qcow2    │
│   ├── security-onion.qcow2 (8GB)      │
│   ├── metasploitable3.qcow2 (4GB)     │
│   └── 20+ more...                     │
└────────────────────────────────────────┘

OPTION 2: All-in-One Mode
┌────────────────────────────────────────┐
│   SynOS Host OS (3-4GB)                │
│   ├── Minimal bootloader               │
│   └── QEMU launcher                    │
└────────────────────────────────────────┘
           │
           │ Auto-launches mega VM (fullscreen)
           ▼
┌────────────────────────────────────────┐
│   Mega VM (15GB) - Traditional         │
│   ├── ParrotOS Full Base               │
│   ├── + Kali Tools (500+)              │
│   ├── + SynOS Custom Components        │
│   │   ├── Rust Kernel                  │
│   │   ├── AI Consciousness             │
│   │   └── ALFRED                       │
│   └── MATE Desktop (SynOS branded)     │
│                                        │
│   User experience: Feels like native OS│
│   But: Still a VM (snapshots, rollback)│
└────────────────────────────────────────┘
```

---

## Build Phases

### Phase 1: Minimal SynOS Base ISO (Week 1) ⭐ START HERE
**Goal:** 3-4GB bootable ISO with ParrotOS minimal + SynOS AI components
**Output:** `synos-base-v1.0.iso` (3-4GB)

### Phase 2: VM Orchestrator Implementation (Week 1-2)
**Goal:** Rust-based VM manager with AI consciousness integration
**Output:** `src/vm-orchestrator/` (working binary)

### Phase 3: Essential VMs (Week 2-3)
**Goal:** Build first 5 critical VMs for testing
**Output:** 5 `.qcow2` VM images

### Phase 4: Mega VM (Week 3)
**Goal:** All-in-one VM for traditional users
**Output:** `synos-mega-vm.qcow2` (15GB)

### Phase 5: Boot Menu Integration (Week 4)
**Goal:** GRUB menu with 3 boot options
**Output:** Unified ISO with boot selection

### Phase 6: Testing & Validation (Week 4)
**Goal:** End-to-end testing of all modes
**Output:** Working v1.0 system

---

## Phase 1: Minimal SynOS Base ISO (DETAILED)

### 1.1 Architecture

```
Minimal Base ISO (3-4GB)
├── ParrotOS Minimal Core
│   ├── Base system (Debian 12 Bookworm)
│   ├── Linux kernel 6.5
│   ├── Core utilities (bash, coreutils, systemd)
│   └── ESSENTIAL security tools ONLY:
│       ├── nmap
│       ├── wireshark/tshark
│       ├── burpsuite
│       ├── metasploit-framework
│       ├── john
│       ├── hashcat
│       ├── hydra
│       ├── netcat
│       ├── tcpdump
│       └── ~20 total (vs 500+ in full Parrot)
│
├── Virtualization Stack ⭐
│   ├── qemu-system-x86
│   ├── qemu-utils
│   ├── libvirt-daemon-system
│   ├── libvirt-clients
│   ├── virtinst
│   ├── virt-manager (GUI)
│   └── bridge-utils
│
├── SynOS Custom Components ⭐
│   ├── Rust Kernel (72KB) → /boot/synos/
│   ├── AI Consciousness Engine → /opt/synos/ai-engine/
│   ├── ALFRED Voice Assistant → /opt/synos/alfred/
│   ├── Neural Darwinism Framework → /opt/synos/consciousness/
│   ├── VM Orchestrator → /opt/synos/vm-orchestrator/
│   └── Security Modules → /opt/synos/security/
│
├── Desktop Environment (Lightweight)
│   ├── MATE Desktop (minimal install)
│   ├── SynOS Themes & Branding
│   ├── VM Manager GUI
│   └── AI Copilot Interface
│
└── Development Tools
    ├── Python 3.11 + pip
    ├── Rust toolchain (for on-system compilation)
    ├── Git
    └── Build essentials
```

### 1.2 Package List Strategy

**Create:** `config/package-lists/synos-minimal-base.list.chroot`

```bash
# ═══════════════════════════════════════════════════════════════
# SynOS Minimal Base - Core System Only
# Size Target: 2-3GB (vs 8GB full ParrotOS)
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# BASE SYSTEM
# ─────────────────────────────────────────────────────────────
live-boot
live-config
live-config-systemd
systemd
systemd-sysv

# ─────────────────────────────────────────────────────────────
# ESSENTIAL TOOLS (20 tools max - the rest come via VMs)
# ─────────────────────────────────────────────────────────────
nmap
wireshark
tshark
burpsuite
metasploit-framework
john
hashcat
hydra
netcat-traditional
tcpdump
aircrack-ng
sqlmap
nikto
dirb
gobuster
curl
wget
git
vim
tmux

# ─────────────────────────────────────────────────────────────
# VIRTUALIZATION STACK ⭐ CRITICAL
# ─────────────────────────────────────────────────────────────
qemu-system-x86
qemu-system-gui
qemu-utils
libvirt-daemon-system
libvirt-clients
virtinst
virt-manager
virt-viewer
bridge-utils
dnsmasq-base
ebtables
ovmf

# ─────────────────────────────────────────────────────────────
# DESKTOP (Minimal MATE)
# ─────────────────────────────────────────────────────────────
mate-desktop-environment-core
mate-terminal
mate-system-monitor
lightdm
xserver-xorg
xinit

# ─────────────────────────────────────────────────────────────
# AI/ML DEPENDENCIES (for SynOS components)
# ─────────────────────────────────────────────────────────────
python3
python3-pip
python3-dev
python3-venv
python3-numpy
python3-requests
python3-yaml

# ─────────────────────────────────────────────────────────────
# DEVELOPMENT TOOLS (for on-system compilation)
# ─────────────────────────────────────────────────────────────
build-essential
cmake
pkg-config
cargo
rustc

# ─────────────────────────────────────────────────────────────
# TOTAL: ~100 packages (minimal)
# Result: 3-4GB ISO
# ─────────────────────────────────────────────────────────────
```

### 1.3 Repository Configuration

**Keep ONLY ParrotOS (remove Kali entirely for base)**

```bash
# config/archives/parrot.list.chroot
deb http://deb.parrot.sh/parrot/ parrot main contrib non-free
deb http://deb.parrot.sh/parrot/ parrot-security main contrib non-free

# NO Kali, NO BlackArch in base
# Those tools come via VMs in orchestrator mode
```

### 1.4 Build Script

**Create:** `linux-distribution/SynOS-Linux-Builder/build-synos-base-v1.0.sh`

See next section for full script...

---

## Phase 2: VM Orchestrator Implementation

### 2.1 Rust Project Structure

```bash
src/vm-orchestrator/
├── Cargo.toml
├── src/
│   ├── main.rs                    # CLI entry point
│   ├── lib.rs                     # Library exports
│   ├── vm_manager.rs              # Core VM management (libvirt wrapper)
│   ├── network_builder.rs         # Virtual network creation
│   ├── scenario_engine.rs         # Lab scenario generator
│   ├── vm_library.rs              # VM catalog & download manager
│   ├── ai_integration.rs          # Consciousness engine integration
│   ├── curriculum_mapper.rs       # Course → VM mapping
│   └── cli/
│       ├── mod.rs
│       ├── commands.rs            # CLI subcommands
│       └── ui.rs                  # Terminal UI (TUI)
├── templates/
│   ├── scenarios/
│   │   ├── it-651-ad-lab.yaml     # IT 651 Active Directory lab
│   │   ├── mssp-financial.yaml    # MSSP financial client sim
│   │   └── purple-team-basic.yaml # Purple team exercise
│   └── vms/
│       └── vm-catalog.json        # VM metadata & download URLs
└── tests/
    ├── integration_tests.rs
    └── scenario_tests.rs
```

### 2.2 Core Dependencies (Cargo.toml)

```toml
[package]
name = "synos-vm-orchestrator"
version = "1.0.0"
edition = "2021"

[dependencies]
# VM Management
virt = "0.3"                       # libvirt bindings
qapi = "0.10"                      # QEMU QMP interface

# Async Runtime
tokio = { version = "1.0", features = ["full"] }
async-trait = "0.1"

# Configuration
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.9"
serde_json = "1.0"

# CLI & TUI
clap = { version = "4.0", features = ["derive"] }
ratatui = "0.24"                   # Terminal UI
crossterm = "0.27"

# Networking
reqwest = { version = "0.11", features = ["blocking"] }
sha2 = "0.10"                      # Checksum verification

# Logging
tracing = "0.1"
tracing-subscriber = "0.3"

# Integration with SynOS AI
synos-ai-engine = { path = "../ai-engine" }
synos-consciousness = { path = "../ai-engine/consciousness" }
```

### 2.3 Key Components

**VM Manager (`vm_manager.rs`):**
```rust
use virt::connect::Connect;
use virt::domain::Domain;

pub struct VMManager {
    conn: Connect,
    ai: Arc<ConsciousnessEngine>,
}

impl VMManager {
    pub async fn new() -> Result<Self> {
        let conn = Connect::open("qemu:///system")?;
        Ok(Self { conn, ai: ConsciousnessEngine::new() })
    }

    pub async fn launch_vm(&self, config: &VMConfig) -> Result<RunningVM> {
        // Generate libvirt XML from config
        let xml = self.generate_vm_xml(config)?;

        // Create domain
        let domain = Domain::create_xml(&self.conn, &xml, 0)?;

        // AI tracks VM state
        self.ai.track_vm_lifecycle(&domain).await?;

        Ok(RunningVM { domain, config })
    }

    pub async fn launch_scenario(&self, scenario: &Scenario) -> Result<Vec<RunningVM>> {
        // Create virtual network
        let network = self.create_network(&scenario.network)?;

        // Launch all VMs in parallel
        let mut vms = Vec::new();
        for vm_config in &scenario.vms {
            let vm = self.launch_vm(vm_config).await?;
            vms.push(vm);
        }

        // AI monitors scenario
        self.ai.monitor_scenario(scenario, &vms).await?;

        Ok(vms)
    }
}
```

**Scenario Engine (`scenario_engine.rs`):**
```rust
pub struct ScenarioEngine {
    templates: HashMap<String, ScenarioTemplate>,
    ai: Arc<ConsciousnessEngine>,
}

impl ScenarioEngine {
    pub async fn suggest_scenario(&self, context: &UserContext) -> Option<Scenario> {
        // Example: User is in IT 651, Module 8
        if context.current_course == "IT-651" && context.current_module == 8 {
            // AI suggests AD attack lab
            return self.load_template("it-651-ad-lab").ok();
        }

        // Example: User is MSSP consultant
        if context.user_role == UserRole::MSSPConsultant {
            // AI asks about client profile
            return self.ai.suggest_client_scenario(&context.client_profile).await;
        }

        None
    }

    pub fn load_template(&self, name: &str) -> Result<Scenario> {
        let template_path = format!("templates/scenarios/{}.yaml", name);
        let yaml = std::fs::read_to_string(template_path)?;
        let scenario: Scenario = serde_yaml::from_str(&yaml)?;
        Ok(scenario)
    }
}
```

**AI Integration (`ai_integration.rs`):**
```rust
use synos_ai_engine::ConsciousnessEngine;

pub struct VMCopilot {
    consciousness: Arc<ConsciousnessEngine>,
    vm_manager: Arc<VMManager>,
}

impl VMCopilot {
    pub async fn greet_user(&self, user: &User) -> String {
        let context = self.consciousness.get_user_context(user).await;

        match context.current_activity {
            Activity::Studying(course) => {
                format!(
                    "Welcome back! You're in {}, {}. \
                     I recommend the {} lab. Shall I prepare it?",
                    course.name,
                    course.current_module,
                    self.suggest_lab_name(&course)
                )
            }
            Activity::MSSPWork(client) => {
                format!(
                    "You have a {} assessment coming up. \
                     Shall I prepare a simulation environment?",
                    client.name
                )
            }
            _ => "Welcome to SynOS! How can I help you today?".to_string()
        }
    }

    pub async fn monitor_learning_progress(&self, scenario: &Scenario) {
        // AI watches user actions in VMs
        // Provides hints, tracks objectives, adapts difficulty

        loop {
            let user_actions = self.vm_manager.get_recent_actions().await;

            for action in user_actions {
                // Example: User ran nmap scan
                if action.command.contains("nmap") {
                    self.consciousness.log_learning_event(LearningEvent {
                        tool: "nmap",
                        skill: "network_scanning",
                        proficiency: self.assess_proficiency(&action),
                    }).await;

                    // Offer hint if struggling
                    if action.failed() {
                        self.offer_hint(&action).await;
                    }
                }
            }

            tokio::time::sleep(Duration::from_secs(5)).await;
        }
    }
}
```

---

## Phase 3: Essential VMs

### 3.1 VM Build Strategy

**VMs to Build (Priority Order):**

1. **kali-full.qcow2** (8GB) - Full Kali Linux Rolling
2. **windows-server-2022-dc.qcow2** (10GB) - Active Directory lab
3. **metasploitable3.qcow2** (4GB) - Practice target
4. **security-onion.qcow2** (8GB) - Blue team monitoring
5. **parrot-security.qcow2** (6GB) - Alternative to Kali

### 3.2 Automated VM Builder

**Create:** `scripts/vm-builder/build-vm-library.sh`

```bash
#!/bin/bash
# SynOS VM Library Builder
# Builds essential VMs with automated installation

set -euo pipefail

VM_OUTPUT_DIR="/home/diablorain/Syn_OS/vm-library"
TEMP_DIR="/tmp/synos-vm-builder"

mkdir -p "$VM_OUTPUT_DIR" "$TEMP_DIR"

# ═══════════════════════════════════════════════════════════════
# VM 1: Kali Full (8GB)
# ═══════════════════════════════════════════════════════════════
build_kali_full() {
    echo "Building kali-full.qcow2..."

    # Download Kali installer
    cd "$TEMP_DIR"
    wget -c https://cdimage.kali.org/kali-2025.1/kali-linux-2025.1-installer-amd64.iso

    # Create disk image
    qemu-img create -f qcow2 "$VM_OUTPUT_DIR/kali-full.qcow2" 30G

    # Automated install using preseed
    virt-install \
        --name kali-full-builder \
        --memory 4096 \
        --vcpus 2 \
        --disk path="$VM_OUTPUT_DIR/kali-full.qcow2",format=qcow2 \
        --cdrom kali-linux-2025.1-installer-amd64.iso \
        --os-variant debian11 \
        --network network=default \
        --graphics none \
        --console pty,target_type=serial \
        --location kali-linux-2025.1-installer-amd64.iso \
        --extra-args "auto=true priority=critical preseed/url=http://YOUR_SERVER/kali-preseed.cfg console=ttyS0,115200n8 serial" \
        --wait -1

    # Clean up
    virsh undefine kali-full-builder

    # Compress for distribution
    qemu-img convert -c -O qcow2 "$VM_OUTPUT_DIR/kali-full.qcow2" "$VM_OUTPUT_DIR/kali-full-compressed.qcow2"

    echo "✓ kali-full.qcow2 complete (8GB)"
}

# ═══════════════════════════════════════════════════════════════
# VM 2: Windows Server 2022 DC (10GB)
# ═══════════════════════════════════════════════════════════════
build_windows_ad() {
    echo "Building windows-server-2022-dc.qcow2..."

    # Download evaluation ISO (180-day trial)
    cd "$TEMP_DIR"
    wget -c https://software-download.microsoft.com/download/pr/SERVER_EVAL_x64FRE_en-us.iso

    # Create disk image
    qemu-img create -f qcow2 "$VM_OUTPUT_DIR/windows-server-2022-dc.qcow2" 40G

    # Automated install using autounattend.xml
    virt-install \
        --name windows-ad-builder \
        --memory 4096 \
        --vcpus 2 \
        --disk path="$VM_OUTPUT_DIR/windows-server-2022-dc.qcow2",format=qcow2,bus=virtio \
        --disk path="$TEMP_DIR/autounattend.iso",device=cdrom \
        --cdrom SERVER_EVAL_x64FRE_en-us.iso \
        --os-variant win2k22 \
        --network network=default,model=virtio \
        --graphics vnc \
        --wait -1

    # Post-install: Configure AD via PowerShell
    # (This part requires manual setup or WinRM automation)

    echo "✓ windows-server-2022-dc.qcow2 complete (10GB)"
    echo "  Note: Manual AD configuration required"
}

# ═══════════════════════════════════════════════════════════════
# VM 3: Metasploitable3 (4GB)
# ═══════════════════════════════════════════════════════════════
build_metasploitable3() {
    echo "Building metasploitable3.qcow2..."

    # Clone Metasploitable3 repo
    cd "$TEMP_DIR"
    git clone https://github.com/rapid7/metasploitable3.git
    cd metasploitable3

    # Build using Packer
    packer build windows_2008.json  # or ubuntu_1404.json for Linux version

    # Convert to qcow2
    qemu-img convert -O qcow2 \
        output-*/metasploitable3.vmdk \
        "$VM_OUTPUT_DIR/metasploitable3.qcow2"

    echo "✓ metasploitable3.qcow2 complete (4GB)"
}

# ═══════════════════════════════════════════════════════════════
# VM 4: Security Onion (8GB)
# ═══════════════════════════════════════════════════════════════
build_security_onion() {
    echo "Building security-onion.qcow2..."

    # Download Security Onion ISO
    cd "$TEMP_DIR"
    wget -c https://github.com/Security-Onion-Solutions/securityonion/releases/download/2.4.100/securityonion-2.4.100.iso

    # Create disk image
    qemu-img create -f qcow2 "$VM_OUTPUT_DIR/security-onion.qcow2" 200G

    # Install
    virt-install \
        --name security-onion-builder \
        --memory 8192 \
        --vcpus 4 \
        --disk path="$VM_OUTPUT_DIR/security-onion.qcow2",format=qcow2 \
        --cdrom securityonion-2.4.100.iso \
        --os-variant ubuntu22.04 \
        --network network=default \
        --graphics vnc \
        --wait -1

    echo "✓ security-onion.qcow2 complete (8GB)"
}

# ═══════════════════════════════════════════════════════════════
# VM 5: ParrotOS Security (6GB)
# ═══════════════════════════════════════════════════════════════
build_parrot_security() {
    echo "Building parrot-security.qcow2..."

    # Download ParrotOS Security Edition
    cd "$TEMP_DIR"
    wget -c https://deb.parrot.sh/parrot/iso/6.4/Parrot-security-6.4_amd64.iso

    # Create disk image
    qemu-img create -f qcow2 "$VM_OUTPUT_DIR/parrot-security.qcow2" 30G

    # Install
    virt-install \
        --name parrot-security-builder \
        --memory 4096 \
        --vcpus 2 \
        --disk path="$VM_OUTPUT_DIR/parrot-security.qcow2",format=qcow2 \
        --cdrom Parrot-security-6.4_amd64.iso \
        --os-variant debian11 \
        --network network=default \
        --graphics vnc \
        --wait -1

    echo "✓ parrot-security.qcow2 complete (6GB)"
}

# ═══════════════════════════════════════════════════════════════
# Main Build Process
# ═══════════════════════════════════════════════════════════════
main() {
    echo "SynOS VM Library Builder"
    echo "Building 5 essential VMs..."
    echo ""

    build_kali_full
    build_windows_ad
    build_metasploitable3
    build_security_onion
    build_parrot_security

    echo ""
    echo "✓ All VMs built successfully!"
    echo "  Output: $VM_OUTPUT_DIR"
    echo ""
    echo "Total size: $(du -sh $VM_OUTPUT_DIR | cut -f1)"
}

main "$@"
```

### 3.3 VM Catalog (Metadata)

**Create:** `src/vm-orchestrator/templates/vms/vm-catalog.json`

```json
{
  "vms": [
    {
      "id": "kali-full",
      "name": "Kali Linux Full",
      "version": "2025.1",
      "os_type": "linux",
      "os_variant": "debian11",
      "description": "Complete Kali Linux Rolling with all tools",
      "size_compressed": "3GB",
      "size_uncompressed": "8GB",
      "disk_size": "30GB",
      "recommended_ram": "4GB",
      "recommended_vcpus": 2,
      "download_url": "https://synos-vm-library.s3.amazonaws.com/kali-full-2025.1.qcow2.xz",
      "sha256": "abc123...",
      "tags": ["offensive", "pentesting", "essential"],
      "use_cases": ["penetration testing", "security research", "exploit development"]
    },
    {
      "id": "windows-server-2022-dc",
      "name": "Windows Server 2022 Domain Controller",
      "version": "2022-eval",
      "os_type": "windows",
      "os_variant": "win2k22",
      "description": "Pre-configured Active Directory domain controller (corp.local)",
      "size_compressed": "4GB",
      "size_uncompressed": "10GB",
      "disk_size": "40GB",
      "recommended_ram": "4GB",
      "recommended_vcpus": 2,
      "download_url": "https://synos-vm-library.s3.amazonaws.com/windows-server-2022-dc.qcow2.xz",
      "sha256": "def456...",
      "tags": ["infrastructure", "active-directory", "essential"],
      "use_cases": ["AD attacks", "Kerberoasting", "pass-the-hash", "golden ticket"],
      "credentials": {
        "domain": "corp.local",
        "admin_user": "Administrator",
        "admin_password": "P@ssw0rd123!"
      }
    },
    {
      "id": "metasploitable3",
      "name": "Metasploitable3",
      "version": "3.0",
      "os_type": "linux",
      "os_variant": "ubuntu14.04",
      "description": "Intentionally vulnerable target for practice",
      "size_compressed": "1.5GB",
      "size_uncompressed": "4GB",
      "disk_size": "20GB",
      "recommended_ram": "2GB",
      "recommended_vcpus": 1,
      "download_url": "https://synos-vm-library.s3.amazonaws.com/metasploitable3.qcow2.xz",
      "sha256": "ghi789...",
      "tags": ["vulnerable", "practice", "essential"],
      "use_cases": ["learning", "tool testing", "exploit practice"],
      "credentials": {
        "user": "vagrant",
        "password": "vagrant"
      }
    },
    {
      "id": "security-onion",
      "name": "Security Onion",
      "version": "2.4.100",
      "os_type": "linux",
      "os_variant": "ubuntu22.04",
      "description": "SIEM, IDS/IPS, network monitoring platform",
      "size_compressed": "2.5GB",
      "size_uncompressed": "8GB",
      "disk_size": "200GB",
      "recommended_ram": "8GB",
      "recommended_vcpus": 4,
      "download_url": "https://synos-vm-library.s3.amazonaws.com/security-onion.qcow2.xz",
      "sha256": "jkl012...",
      "tags": ["defensive", "blue-team", "essential"],
      "use_cases": ["threat detection", "log analysis", "network monitoring", "purple team"]
    },
    {
      "id": "parrot-security",
      "name": "ParrotOS Security Edition",
      "version": "6.4",
      "os_type": "linux",
      "os_variant": "debian11",
      "description": "ParrotOS with full security tool suite",
      "size_compressed": "2GB",
      "size_uncompressed": "6GB",
      "disk_size": "30GB",
      "recommended_ram": "4GB",
      "recommended_vcpus": 2,
      "download_url": "https://synos-vm-library.s3.amazonaws.com/parrot-security.qcow2.xz",
      "sha256": "mno345...",
      "tags": ["offensive", "pentesting", "alternative"],
      "use_cases": ["penetration testing", "privacy tools", "OSINT"]
    }
  ],

  "bundles": [
    {
      "id": "it-651-essentials",
      "name": "IT 651 Advanced Security Essentials",
      "description": "All VMs needed for IT 651 coursework",
      "vms": ["kali-full", "windows-server-2022-dc", "metasploitable3"],
      "total_size": "22GB",
      "download_url": "https://synos-vm-library.s3.amazonaws.com/bundles/it-651-essentials.tar.xz"
    },
    {
      "id": "mssp-starter",
      "name": "MSSP Starter Pack",
      "description": "Core VMs for MSSP operations",
      "vms": ["kali-full", "security-onion", "metasploitable3"],
      "total_size": "20GB",
      "download_url": "https://synos-vm-library.s3.amazonaws.com/bundles/mssp-starter.tar.xz"
    }
  ]
}
```

---

## Phase 4: Mega VM (All-in-One Option)

### 4.1 Mega VM Architecture

```
synos-mega-vm.qcow2 (15GB uncompressed, 40GB disk)
├── ParrotOS 6.4 Full Base
├── + Kali Tools (selective - no conflicts)
│   └── Use APT pinning to prefer ParrotOS, add Kali-only tools
├── + SynOS Custom Components
│   ├── Rust Kernel → /boot/synos/
│   ├── AI Consciousness → /opt/synos/
│   └── ALFRED → /opt/synos/
└── MATE Desktop (SynOS branded)
```

### 4.2 Mega VM Build Script

**Create:** `scripts/vm-builder/build-mega-vm.sh`

```bash
#!/bin/bash
# Build SynOS Mega VM (All-in-One)
# This is essentially a full ParrotOS with SynOS components

set -euo pipefail

MEGA_VM_PATH="/home/diablorain/Syn_OS/vm-library/synos-mega-vm.qcow2"
BUILD_DIR="/tmp/synos-mega-build"

mkdir -p "$BUILD_DIR"

echo "Building SynOS Mega VM..."

# Create disk image (40GB for all tools)
qemu-img create -f qcow2 "$MEGA_VM_PATH" 40G

# Use Parrot Security ISO as base
cd "$BUILD_DIR"
wget -c https://deb.parrot.sh/parrot/iso/6.4/Parrot-security-6.4_amd64.iso

# Install with customization
virt-install \
    --name synos-mega-builder \
    --memory 4096 \
    --vcpus 2 \
    --disk path="$MEGA_VM_PATH",format=qcow2 \
    --cdrom Parrot-security-6.4_amd64.iso \
    --os-variant debian11 \
    --network network=default \
    --graphics vnc \
    --wait -1

# Post-install customization (via virt-customize)
virt-customize -a "$MEGA_VM_PATH" \
    --hostname synos-mega \
    --root-password password:synos \
    --run-command 'apt-get update' \
    --install qemu-guest-agent \
    --copy-in /home/diablorain/Syn_OS/src/kernel/target/x86_64-unknown-none/release/kernel:/boot/synos/ \
    --copy-in /home/diablorain/Syn_OS/build/synos-ai-engine:/opt/synos/ \
    --copy-in /home/diablorain/Syn_OS/build/alfred:/opt/synos/ \
    --firstboot-command 'systemctl enable synos-ai-daemon'

# Clean up builder domain
virsh undefine synos-mega-builder

# Compress for distribution
qemu-img convert -c -O qcow2 "$MEGA_VM_PATH" "$MEGA_VM_PATH.compressed"

echo "✓ Mega VM complete: $MEGA_VM_PATH"
echo "  Size: $(du -sh $MEGA_VM_PATH | cut -f1)"
```

---

## Phase 5: Boot Menu Integration

### 5.1 GRUB Menu Configuration

**Create:** `linux-distribution/SynOS-Linux-Builder/config/includes.binary/boot/grub/grub.cfg`

```bash
# SynOS v1.0 Hybrid Boot Menu

set default=0
set timeout=10

# SynOS Branding
set theme=/boot/grub/themes/synos/theme.txt

menuentry "SynOS VM Orchestrator Mode (Recommended)" {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components quiet splash synos_mode=orchestrator
    initrd /live/initrd.img
}

menuentry "SynOS All-in-One Mode (Traditional)" {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components quiet splash synos_mode=mega-vm
    initrd /live/initrd.img
}

menuentry "SynOS Minimal Host Only" {
    set gfxpayload=keep
    linux /live/vmlinuz boot=live components quiet splash synos_mode=host-only
    initrd /live/initrd.img
}

submenu "Advanced Options" {
    menuentry "Boot with SynOS Custom Kernel" {
        linux /boot/synos/kernel
    }

    menuentry "Boot to Recovery Mode" {
        linux /live/vmlinuz boot=live components single
        initrd /live/initrd.img
    }
}
```

### 5.2 Boot Mode Handler

**Create:** `linux-distribution/SynOS-Linux-Builder/config/hooks/live/9999-setup-boot-mode.hook.chroot`

```bash
#!/bin/bash
# Handle boot mode selection

set -e

cat > /usr/local/bin/synos-boot-handler << 'EOFSCRIPT'
#!/bin/bash
# SynOS Boot Mode Handler
# Reads synos_mode= kernel parameter and acts accordingly

BOOT_MODE=$(grep -oP 'synos_mode=\K\w+' /proc/cmdline)

case "$BOOT_MODE" in
    orchestrator)
        echo "Starting VM Orchestrator Mode..."
        # Start libvirtd
        systemctl start libvirtd
        systemctl start virtlogd

        # Launch VM orchestrator GUI
        /opt/synos/vm-orchestrator/synos-vm-copilot --gui
        ;;

    mega-vm)
        echo "Launching All-in-One Mega VM..."
        # Auto-launch mega VM in fullscreen
        /usr/bin/virt-manager --connect qemu:///system \
            --show-domain-console synos-mega-vm \
            --full-screen
        ;;

    host-only)
        echo "Starting Minimal Host Mode..."
        # Just boot to desktop, no VMs
        ;;

    *)
        # Default: orchestrator mode
        exec /usr/local/bin/synos-boot-handler synos_mode=orchestrator
        ;;
esac
EOFSCRIPT

chmod +x /usr/local/bin/synos-boot-handler

# Add to systemd startup
cat > /etc/systemd/system/synos-boot-mode.service << 'EOFSERVICE'
[Unit]
Description=SynOS Boot Mode Handler
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/synos-boot-handler
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOFSERVICE

systemctl enable synos-boot-mode.service

echo "✓ Boot mode handler installed"
```

---

## Implementation Timeline

### Week 1: Foundation (Days 1-7)

**Day 1-2: Minimal Base ISO**
- [ ] Create `synos-minimal-base.list.chroot` (100 packages)
- [ ] Clean repository config (ParrotOS only)
- [ ] Build script: `build-synos-base-v1.0.sh`
- [ ] First build attempt (expect 2-3 hours)
- [ ] Test ISO in QEMU

**Day 3-4: VM Orchestrator Skeleton**
- [ ] Create `src/vm-orchestrator/` structure
- [ ] Implement basic `vm_manager.rs` (launch/stop VMs)
- [ ] Implement `network_builder.rs` (create virtual networks)
- [ ] CLI: `synos-vm-copilot launch <vm-name>`
- [ ] Test: Launch a simple VM

**Day 5-7: Build First VM**
- [ ] Build `kali-full.qcow2` (8GB)
- [ ] Test launching from orchestrator
- [ ] Create VM catalog metadata
- [ ] Implement VM download manager

### Week 2: Core VMs (Days 8-14)

**Day 8-10: Windows AD VM**
- [ ] Build `windows-server-2022-dc.qcow2`
- [ ] Configure Active Directory
- [ ] Seed test users/groups
- [ ] Create snapshot

**Day 11-12: Practice Targets**
- [ ] Build `metasploitable3.qcow2`
- [ ] Build `security-onion.qcow2`

**Day 13-14: Integration Testing**
- [ ] Launch multi-VM scenario (Kali + AD + Metasploitable)
- [ ] Test networking between VMs
- [ ] Verify AI monitoring works

### Week 3: Mega VM & Scenarios (Days 15-21)

**Day 15-17: Mega VM**
- [ ] Build `synos-mega-vm.qcow2` (15GB)
- [ ] Install SynOS components in VM
- [ ] Test fullscreen launch

**Day 18-20: Scenario Templates**
- [ ] Create `it-651-ad-lab.yaml`
- [ ] Create `mssp-financial.yaml`
- [ ] Create `purple-team-basic.yaml`
- [ ] Test scenario engine

**Day 21: AI Integration**
- [ ] Connect consciousness engine to VM orchestrator
- [ ] Implement learning progress tracking
- [ ] Test AI suggestions

### Week 4: Polish & Testing (Days 22-28)

**Day 22-24: Boot Menu**
- [ ] GRUB configuration with 3 modes
- [ ] Boot mode handler systemd service
- [ ] Test all 3 boot modes

**Day 25-27: End-to-End Testing**
- [ ] Test orchestrator mode with 3 scenarios
- [ ] Test mega VM mode
- [ ] Test host-only mode
- [ ] Performance tuning

**Day 28: Documentation & Release**
- [ ] User guide (how to use VM orchestrator)
- [ ] Developer guide (how to add VMs)
- [ ] Demo video
- [ ] v1.0 release!

---

## Next Immediate Steps (START NOW)

1. **Review this plan** - Make sure you agree with the architecture
2. **Create minimal package list** - I'll generate the exact file next
3. **Build minimal base ISO** - First working ISO (3-4GB)
4. **Implement VM orchestrator** - Start with basic VM launch
5. **Build Kali VM** - First VM in library

**Ready to start? Should I create the minimal base ISO build script first?**
