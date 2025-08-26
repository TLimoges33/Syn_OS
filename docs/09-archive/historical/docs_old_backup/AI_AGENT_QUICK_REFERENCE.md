# AI Agent Quick Reference Guide

## 🚀 Project: SynapticOS (ParrotOS Fork with AI Consciousness)

### Agent Assignments

## Agent 1: Repository & Infrastructure

* *Branch**: `feature/parrotos-fork`
* *Primary Files**:

- `config/synapticos-branding.conf`
- `build/Dockerfile`
- `.github/workflows/`

* *Day 1 Tasks**:

1. Fork ParrotOS repository
2. Apply SynapticOS branding
3. Set up package structure
4. Configure build system

* *Key Commands**:

```bash
git clone https://github.com/parrotsec/parrot.git synapticos
cd synapticos
git checkout -b feature/parrotos-fork

## Apply changes from docs/AI_AGENT_TASKS_PARROTOS_FORK.md - Task A1

```text

```text

```text
```text

- --

## Agent 2: Kernel Development

* *Branch**: `feature/kernel-customization`
* *Primary Files**:

- `kernel/synapticos/core.c`
- `include/linux/synapticos.h`
- `kernel/synapticos/Kconfig`

* *Day 1 Tasks**:

1. Set up kernel build environment
2. Create microprocess API headers
3. Implement basic AI hooks
4. Test kernel module loading

* *Key Commands**:

```bash
* *Branch**: `feature/kernel-customization`
* *Primary Files**:

- `kernel/synapticos/core.c`
- `include/linux/synapticos.h`
- `kernel/synapticos/Kconfig`

* *Day 1 Tasks**:

1. Set up kernel build environment
2. Create microprocess API headers
3. Implement basic AI hooks
4. Test kernel module loading

* *Key Commands**:

```bash

* *Branch**: `feature/kernel-customization`
* *Primary Files**:

- `kernel/synapticos/core.c`
- `include/linux/synapticos.h`
- `kernel/synapticos/Kconfig`

* *Day 1 Tasks**:

1. Set up kernel build environment
2. Create microprocess API headers
3. Implement basic AI hooks
4. Test kernel module loading

* *Key Commands**:

```bash

- `include/linux/synapticos.h`
- `kernel/synapticos/Kconfig`

* *Day 1 Tasks**:

1. Set up kernel build environment
2. Create microprocess API headers
3. Implement basic AI hooks
4. Test kernel module loading

* *Key Commands**:

```bash
cd kernel
make menuconfig  # Enable SYNAPTICOS options
make modules
insmod synapticos_core.ko
```text

```text

```text
```text

- --

## Agent 3: LM Studio Integration

* *Branch**: `feature/consciousness-system`
* *Primary Files**:

- `packages/consciousness/synapticos_consciousness/lm_studio.py`
- `packages/consciousness/requirements.txt`
- `/etc/systemd/system/synapticos-consciousness.service`

* *Day 1 Tasks**:

1. Create LM Studio client
2. Implement model management
3. Build inference pipeline
4. Set up systemd service

* *Key Commands**:

```bash
* *Branch**: `feature/consciousness-system`
* *Primary Files**:

- `packages/consciousness/synapticos_consciousness/lm_studio.py`
- `packages/consciousness/requirements.txt`
- `/etc/systemd/system/synapticos-consciousness.service`

* *Day 1 Tasks**:

1. Create LM Studio client
2. Implement model management
3. Build inference pipeline
4. Set up systemd service

* *Key Commands**:

```bash

* *Branch**: `feature/consciousness-system`
* *Primary Files**:

- `packages/consciousness/synapticos_consciousness/lm_studio.py`
- `packages/consciousness/requirements.txt`
- `/etc/systemd/system/synapticos-consciousness.service`

* *Day 1 Tasks**:

1. Create LM Studio client
2. Implement model management
3. Build inference pipeline
4. Set up systemd service

* *Key Commands**:

```bash

- `packages/consciousness/requirements.txt`
- `/etc/systemd/system/synapticos-consciousness.service`

* *Day 1 Tasks**:

1. Create LM Studio client
2. Implement model management
3. Build inference pipeline
4. Set up systemd service

* *Key Commands**:

```bash
cd packages/consciousness
pip install -r requirements.txt
python -m pytest tests/test_lm_studio.py
sudo systemctl start synapticos-consciousness
```text

```text

```text
```text

- --

## Agent 4: Personal Context Engine

* *Branch**: `feature/context-engine`
* *Primary Files**:

- `packages/consciousness/synapticos_consciousness/context_engine.py`
- `packages/consciousness/synapticos_consciousness/security_tutor.py`
- `/usr/local/bin/synapticos-context`

* *Day 1 Tasks**:

1. Create user profiling system
2. Implement skill tracking
3. Build tutorial framework
4. Create CLI tools

* *Key Commands**:

```bash
* *Branch**: `feature/context-engine`
* *Primary Files**:

- `packages/consciousness/synapticos_consciousness/context_engine.py`
- `packages/consciousness/synapticos_consciousness/security_tutor.py`
- `/usr/local/bin/synapticos-context`

* *Day 1 Tasks**:

1. Create user profiling system
2. Implement skill tracking
3. Build tutorial framework
4. Create CLI tools

* *Key Commands**:

```bash

* *Branch**: `feature/context-engine`
* *Primary Files**:

- `packages/consciousness/synapticos_consciousness/context_engine.py`
- `packages/consciousness/synapticos_consciousness/security_tutor.py`
- `/usr/local/bin/synapticos-context`

* *Day 1 Tasks**:

1. Create user profiling system
2. Implement skill tracking
3. Build tutorial framework
4. Create CLI tools

* *Key Commands**:

```bash

- `packages/consciousness/synapticos_consciousness/security_tutor.py`
- `/usr/local/bin/synapticos-context`

* *Day 1 Tasks**:

1. Create user profiling system
2. Implement skill tracking
3. Build tutorial framework
4. Create CLI tools

* *Key Commands**:

```bash
cd packages/consciousness
python -m synapticos_consciousness.context_engine init
synapticos-context profile
synapticos-context skills
```text

```text

```text
```text

- --

## 📋 Daily Checklist

### Morning (10 AM EST Standup)

- [ ] Pull latest changes from main
- [ ] Review assigned tasks
- [ ] Check integration points with other agents
- [ ] Update project board

### Development

- [ ] Write tests first (TDD)
- [ ] Implement features
- [ ] Run security scans
- [ ] Update documentation

### Evening

- [ ] Commit changes with clear messages
- [ ] Push to feature branch
- [ ] Create PR if ready for review
- [ ] Update tomorrow's plan

- --

## 🔧 Common Commands

### Git Workflow

```bash
### Morning (10 AM EST Standup)

- [ ] Pull latest changes from main
- [ ] Review assigned tasks
- [ ] Check integration points with other agents
- [ ] Update project board

### Development

- [ ] Write tests first (TDD)
- [ ] Implement features
- [ ] Run security scans
- [ ] Update documentation

### Evening

- [ ] Commit changes with clear messages
- [ ] Push to feature branch
- [ ] Create PR if ready for review
- [ ] Update tomorrow's plan

- --

## 🔧 Common Commands

### Git Workflow

```bash

### Morning (10 AM EST Standup)

- [ ] Pull latest changes from main
- [ ] Review assigned tasks
- [ ] Check integration points with other agents
- [ ] Update project board

### Development

- [ ] Write tests first (TDD)
- [ ] Implement features
- [ ] Run security scans
- [ ] Update documentation

### Evening

- [ ] Commit changes with clear messages
- [ ] Push to feature branch
- [ ] Create PR if ready for review
- [ ] Update tomorrow's plan

- --

## 🔧 Common Commands

### Git Workflow

```bash
- [ ] Check integration points with other agents
- [ ] Update project board

### Development

- [ ] Write tests first (TDD)
- [ ] Implement features
- [ ] Run security scans
- [ ] Update documentation

### Evening

- [ ] Commit changes with clear messages
- [ ] Push to feature branch
- [ ] Create PR if ready for review
- [ ] Update tomorrow's plan

- --

## 🔧 Common Commands

### Git Workflow

```bash

## Start new feature

git checkout main
git pull origin main
git checkout -b feature/your-feature

## Commit changes

git add .
git commit -m "feat: implement X for Y reason"
git push origin feature/your-feature
```text

git checkout -b feature/your-feature

## Commit changes

git add .
git commit -m "feat: implement X for Y reason"
git push origin feature/your-feature

```text
git checkout -b feature/your-feature

## Commit changes

git add .
git commit -m "feat: implement X for Y reason"
git push origin feature/your-feature

```text
git commit -m "feat: implement X for Y reason"
git push origin feature/your-feature

```text

### Testing

```bash

```bash
```bash

```bash

## Python tests

python -m pytest tests/ -v

## Kernel tests

make test-modules

## Integration tests

./scripts/run-integration-tests.sh
```text
## Kernel tests

make test-modules

## Integration tests

./scripts/run-integration-tests.sh

```text

## Kernel tests

make test-modules

## Integration tests

./scripts/run-integration-tests.sh

```text
## Integration tests

./scripts/run-integration-tests.sh

```text

### Building

```bash

```bash
```bash

```bash

## Build packages

cd packages/consciousness
python setup.py bdist_wheel

## Build kernel modules

cd kernel
make modules

## Build ISO

./scripts/build-iso.sh
```text

## Build kernel modules

cd kernel
make modules

## Build ISO

./scripts/build-iso.sh

```text

## Build kernel modules

cd kernel
make modules

## Build ISO

./scripts/build-iso.sh

```text

## Build ISO

./scripts/build-iso.sh

```text

- --

## 🚨 Troubleshooting

### LM Studio Connection Issues

```bash
### LM Studio Connection Issues

```bash

### LM Studio Connection Issues

```bash
```bash

## Check if LM Studio is running

curl http://localhost:1234/v1/models

## Restart service

sudo systemctl restart lmstudio
```text
## Restart service

sudo systemctl restart lmstudio

```text

## Restart service

sudo systemctl restart lmstudio

```text
```text

### Kernel Module Problems

```bash

```bash
```bash

```bash

## Check kernel logs

dmesg | grep synapticos

## Remove and reload module

rmmod synapticos_core
insmod synapticos_core.ko debug=1
```text
## Remove and reload module

rmmod synapticos_core
insmod synapticos_core.ko debug=1

```text

## Remove and reload module

rmmod synapticos_core
insmod synapticos_core.ko debug=1

```text

```text

### Context Engine Database

```bash

```bash
```bash

```bash

## Reset database

rm /var/lib/synapticos/context.db
python -m synapticos_consciousness.context_engine init
```text

```text

```text
```text

- --

## 📞 Integration Points

### Agent 1 ↔ Agent 2

- Kernel patches location: `patches/`
- Build configuration: `config/kernel.conf`

### Agent 2 ↔ Agent 3

- AI callback registration
- Process inspection API

### Agent 3 ↔ Agent 4

- Shared LM Studio client
- User context for prompts

### All Agents

- Integration tests: `tests/integration/`
- CI/CD pipeline: `.github/workflows/`

- --

## 📊 Success Metrics

### Performance

- AI inference: <100ms
- Kernel overhead: <5%
- Memory usage: <500MB for AI

### Quality

- Test coverage: >80%
- Security scan: 0 critical issues
- Documentation: 100% API coverage

### User Experience

- Tutorial completion: >90%
- Skill improvement: Measurable
- System stability: 99.9% uptime

### Agent 1 ↔ Agent 2

- Kernel patches location: `patches/`
- Build configuration: `config/kernel.conf`

### Agent 2 ↔ Agent 3

- AI callback registration
- Process inspection API

### Agent 3 ↔ Agent 4

- Shared LM Studio client
- User context for prompts

### All Agents

- Integration tests: `tests/integration/`
- CI/CD pipeline: `.github/workflows/`

- --

## 📊 Success Metrics

### Performance

- AI inference: <100ms
- Kernel overhead: <5%
- Memory usage: <500MB for AI

### Quality

- Test coverage: >80%
- Security scan: 0 critical issues
- Documentation: 100% API coverage

### User Experience

- Tutorial completion: >90%
- Skill improvement: Measurable
- System stability: 99.9% uptime
### Agent 1 ↔ Agent 2

- Kernel patches location: `patches/`
- Build configuration: `config/kernel.conf`

### Agent 2 ↔ Agent 3

- AI callback registration
- Process inspection API

### Agent 3 ↔ Agent 4

- Shared LM Studio client
- User context for prompts

### All Agents

- Integration tests: `tests/integration/`
- CI/CD pipeline: `.github/workflows/`

- --

## 📊 Success Metrics

### Performance

- AI inference: <100ms
- Kernel overhead: <5%
- Memory usage: <500MB for AI

### Quality

- Test coverage: >80%
- Security scan: 0 critical issues
- Documentation: 100% API coverage

### User Experience

- Tutorial completion: >90%
- Skill improvement: Measurable
- System stability: 99.9% uptime

### Agent 1 ↔ Agent 2

- Kernel patches location: `patches/`
- Build configuration: `config/kernel.conf`

### Agent 2 ↔ Agent 3

- AI callback registration
- Process inspection API

### Agent 3 ↔ Agent 4

- Shared LM Studio client
- User context for prompts

### All Agents

- Integration tests: `tests/integration/`
- CI/CD pipeline: `.github/workflows/`

- --

## 📊 Success Metrics

### Performance

- AI inference: <100ms
- Kernel overhead: <5%
- Memory usage: <500MB for AI

### Quality

- Test coverage: >80%
- Security scan: 0 critical issues
- Documentation: 100% API coverage

### User Experience

- Tutorial completion: >90%
- Skill improvement: Measurable
- System stability: 99.9% uptime