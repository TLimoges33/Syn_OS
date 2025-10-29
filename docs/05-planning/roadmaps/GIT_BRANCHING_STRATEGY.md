# SynOS Kernel Development - Git Branching Strategy

**Adopted:** October 29, 2025
**Purpose:** Maintain safe, stable kernel development with feature branches
**Scope:** AI Linux Kernel Development (Phases 2-6)

---

## 🎯 Strategy Overview

**Core Principle:** Each development phase gets its own feature branch, merged to master only after successful testing.

**Why?**
- ✅ **Safety:** Master always contains last known working kernel
- ✅ **Experimentation:** Can try different approaches without risk
- ✅ **Rollback:** Easy to return to stable state if phase fails
- ✅ **Comparison:** Can diff between phases to see changes
- ✅ **Professional:** Industry-standard Git workflow

---

## 🌳 Branch Structure

### Master Branch
**Purpose:** Stable, working kernel versions only

**Rules:**
- ✅ Only merge branches that pass all tests
- ✅ Every merge creates a new working kernel version
- ✅ Tag every major phase completion
- ❌ Never commit broken/untested code directly to master

**Current State:**
- Phase 1 baseline: `6.12.32-synos-ai-v0.1` (working, VM-tested)
- Tag: `phase1-complete`

### Feature Branches (One per Phase)

**Naming Convention:** `phaseN-feature-description`

**Phase 2:** `phase2-ai-syscalls`
- 5 AI-aware system calls
- /proc/synos/ interface
- Test programs

**Phase 3:** `phase3-ebpf-telemetry`
- eBPF monitoring programs
- Telemetry collection
- AI event streaming

**Phase 4:** `phase4-consciousness-scheduler`
- CFS scheduler patches
- AI-driven process priorities
- Consciousness state integration

**Phase 5:** `phase5-ai-runtime`
- TensorFlow Lite integration
- ChromaDB with sentence-transformers
- RAG pipeline
- Neural Darwinism evolution

**Phase 6:** `phase6-iso-integration`
- Final kernel build
- ISO builder integration
- Production release preparation

---

## 🔄 Development Workflow

### Step-by-Step for Each Phase

#### 1. Start New Phase
```bash
cd /usr/src/linux-source-6.12

# Ensure you're on master
git checkout master

# Create new feature branch
git checkout -b phase2-ai-syscalls

# Verify you're on the new branch
git branch --show-current
# Output: phase2-ai-syscalls
```

#### 2. Develop on Feature Branch
```bash
# Make changes (add files, modify code)
# ... edit kernel files ...

# Commit frequently (small, logical commits)
git add kernel/synos_ai.c
git commit -m "Add synos_register_consciousness syscall stub"

git add include/linux/synos_ai.h
git commit -m "Add consciousness state data structures"

git add arch/x86/entry/syscalls/syscall_64.tbl
git commit -m "Reserve syscall numbers 440-444 for SynOS"

# Continue developing...
```

**Best Practices:**
- Commit early, commit often
- Each commit should have one logical change
- Write descriptive commit messages
- Build and test after each major change

#### 3. Build and Test on Branch
```bash
# Build kernel on feature branch
make -j$(nproc) bzImage modules

# Create packages
make bindeb-pkg -j$(nproc)

# Test in VM
cd ~/SynOS-VM-Test
sudo ./test-kernel-qemu.sh

# Test syscalls
cd /usr/src/linux-source-6.12/tools/synos
make
sudo ./test_syscalls

# If tests fail, fix and commit again
# Repeat until everything works
```

#### 4. Final Testing Before Merge
```bash
# Comprehensive testing checklist
# On feature branch (phase2-ai-syscalls):

# ✅ Kernel compiles without errors
make -j$(nproc) bzImage modules

# ✅ Kernel boots in QEMU
~/SynOS-VM-Test/test-kernel-qemu.sh

# ✅ All syscalls work
tools/synos/test_syscalls

# ✅ /proc interface works
cat /proc/synos/consciousness

# ✅ No kernel panics
dmesg | grep -i "panic\|oops\|bug"

# ✅ Documentation updated
ls docs/05-planning/roadmaps/PHASE2_COMPLETION_REPORT.md
```

#### 5. Merge to Master (Only After Success!)
```bash
# Switch to master
git checkout master

# Verify master is clean
git status

# Merge feature branch
git merge phase2-ai-syscalls -m "Merge Phase 2: AI-aware system calls

Phase 2 adds 5 custom system calls for kernel<->AI communication:
- synos_register_consciousness (440)
- synos_update_state (441)
- synos_query_recommendation (442)
- synos_log_event (443)
- synos_get_telemetry (444)

Also includes:
- /proc/synos/ interface (consciousness, telemetry, events)
- Userspace test programs
- Comprehensive testing (all tests pass)

Testing Results:
✅ Kernel compiles without errors
✅ Boots successfully in QEMU
✅ Syscalls functional (tested with test_syscalls)
✅ /proc interface readable
✅ No kernel panics or crashes
✅ Documentation complete

See: docs/05-planning/roadmaps/PHASE2_COMPLETION_REPORT.md
"

# Verify merge was successful
git log --oneline -5
```

#### 6. Tag the Milestone
```bash
# Create annotated tag for Phase 2
git tag -a phase2-complete -m "Phase 2 Complete: AI-aware system calls

Custom syscalls (440-444) implemented and tested:
- Kernel<->AI daemon communication established
- /proc/synos/ interface operational
- Test programs verify functionality

This kernel has all Phase 1 + Phase 2 features.

To return to this state:
  git checkout phase2-complete

Next Phase: Phase 3 - eBPF Telemetry
"

# List all tags
git tag -l
```

#### 7. Clean Up (Optional)
```bash
# After successful merge, you can delete the feature branch
# (Optional - keep it if you want to reference it later)

git branch -d phase2-ai-syscalls

# Or keep it for reference:
# git branch  # Shows all branches including merged ones
```

---

## 📋 Quick Reference Commands

### Branch Management
```bash
# Create and switch to new branch
git checkout -b phase3-ebpf-telemetry

# Switch between branches
git checkout master
git checkout phase2-ai-syscalls

# List all branches
git branch -a

# Show current branch
git branch --show-current

# Delete branch (after merge)
git branch -d phase2-ai-syscalls
```

### Commits
```bash
# Add files
git add path/to/file.c
git add .  # Add all changes (careful!)

# Commit with message
git commit -m "Brief description"

# Commit with detailed message
git commit  # Opens editor for longer message

# Amend last commit (before push)
git commit --amend
```

### Viewing History
```bash
# Show commit history
git log
git log --oneline
git log --graph --oneline --all

# Show changes between branches
git diff master..phase2-ai-syscalls

# Show changes in specific file
git diff master..phase2-ai-syscalls kernel/synos_ai.c

# Show what changed in a commit
git show <commit-hash>
```

### Tags
```bash
# List tags
git tag -l

# Create annotated tag
git tag -a phase2-complete -m "Description"

# Show tag details
git show phase2-complete

# Checkout a specific tag (detached HEAD)
git checkout phase2-complete

# Return to latest on branch
git checkout master
```

### Undoing Changes
```bash
# Discard unstaged changes in file
git checkout -- path/to/file.c

# Unstage file (keep changes)
git reset HEAD path/to/file.c

# Return to last commit (lose all changes!)
git reset --hard HEAD

# Return to specific tag/commit
git checkout phase1-complete
git checkout master  # To get back
```

---

## 🚨 Emergency Rollback Procedures

### Scenario 1: Phase Branch is Broken, Can't Fix
```bash
# You're on phase2-ai-syscalls and it's not working

# Option A: Start over with new branch
git checkout master
git checkout -b phase2-ai-syscalls-v2
# Start fresh implementation

# Option B: Return to specific earlier commit on branch
git log --oneline  # Find good commit
git reset --hard <good-commit-hash>
```

### Scenario 2: Accidentally Merged Broken Code to Master
```bash
# Immediately after bad merge:
git reset --hard HEAD~1
# This undoes the merge (moves master back one commit)

# If you've made commits after the bad merge:
git revert <merge-commit-hash>
# This creates a new commit that undoes the merge
```

### Scenario 3: Need to Return to Phase 1 Baseline
```bash
# Return to Phase 1 (read-only)
git checkout phase1-complete

# Create new branch from Phase 1 to restart Phase 2
git checkout -b phase2-ai-syscalls-restart phase1-complete
```

### Scenario 4: Master is Broken, Lost Working Kernel
```bash
# Return to last known good tag
git checkout phase1-complete  # or phase2-complete, etc.

# Reset master to that tag
git checkout master
git reset --hard phase1-complete
```

---

## 📊 Workflow Diagram

```
master (stable)
   |
   |--- phase1-complete (tag)
   |
   |--- phase2-ai-syscalls (branch)
   |         |
   |         |--- Add syscall stubs (commit)
   |         |--- Add /proc interface (commit)
   |         |--- Add test programs (commit)
   |         |--- Fix bugs (commit)
   |         |--- All tests pass (commit)
   |         |
   |----[merge]--- phase2-complete (tag)
   |
   |--- phase3-ebpf-telemetry (branch)
   |         |
   |         |--- Add eBPF programs (commit)
   |         |--- Integration testing (commit)
   |         |
   |----[merge]--- phase3-complete (tag)
   |
   [continue for phases 4-6...]
```

---

## ✅ Best Practices

### Commits
1. **Commit often** - Small, logical changes
2. **Write good messages** - Describe what and why
3. **Test before committing** - At least compile check
4. **One feature per commit** - Makes rollback easier

### Branches
1. **One branch per phase** - Clear separation
2. **Test thoroughly on branch** - Before merging to master
3. **Keep master stable** - Only merge working code
4. **Tag major milestones** - Easy reference points

### Merging
1. **Always on master** - Don't merge branches into branches
2. **Test before merge** - Comprehensive testing on branch
3. **Document merge** - Detailed merge commit message
4. **Tag after merge** - Mark the milestone

### Safety
1. **Never force push** - Preserves history
2. **Backup before risky operations** - Copy .git folder
3. **Test in VM** - Never test unstable code on production system
4. **Keep documentation updated** - Commit docs with code

---

## 📁 Repository Structure

```
/usr/src/linux-source-6.12/
├── .git/                          # Git repository data
├── .gitignore                     # Files to ignore
├── arch/                          # Architecture-specific code
│   └── x86/entry/syscalls/
│       └── syscall_64.tbl         # Phase 2 modifies this
├── kernel/
│   └── synos_ai.c                 # Phase 2 adds this
├── include/
│   ├── linux/
│   │   └── synos_ai.h             # Phase 2 adds this
│   └── uapi/linux/
│       └── synos_ai.h             # Phase 2 adds this
├── fs/proc/
│   └── synos.c                    # Phase 2 adds this
└── tools/synos/                   # Phase 2 adds this
    ├── test_syscalls.c
    └── synos_ai_client.c
```

---

## 🎓 Learning Git for Kernel Development

### Essential Git Skills (Week 1)
- Creating and switching branches
- Committing changes with good messages
- Viewing history and diffs
- Merging branches
- Creating and using tags

### Advanced Git Skills (Optional)
- Rebasing (reorganizing commits)
- Cherry-picking (copying specific commits)
- Stashing (temporarily saving changes)
- Bisecting (finding which commit broke something)

### Resources
- **Pro Git Book:** https://git-scm.com/book
- **Git Cheat Sheet:** https://training.github.com/downloads/github-git-cheat-sheet.pdf
- **Kernel Git Tutorial:** https://www.kernel.org/doc/html/latest/process/

---

## 🎯 Phase-by-Phase Git Strategy

### Phase 1: Complete (master + tag)
```
master branch @ phase1-complete tag
- Baseline kernel 6.12.32-synos-ai-v0.1
- Compiles, boots, tested
```

### Phase 2: AI-Aware System Calls
```bash
git checkout -b phase2-ai-syscalls
# Develop, test, merge
git tag phase2-complete
```

### Phase 3: eBPF Telemetry
```bash
git checkout -b phase3-ebpf-telemetry
# Develop, test, merge
git tag phase3-complete
```

### Phase 4: Consciousness Scheduler
```bash
git checkout -b phase4-consciousness-scheduler
# Develop, test, merge
git tag phase4-complete
```

### Phase 5: AI Runtime Integration
```bash
git checkout -b phase5-ai-runtime
# Develop, test, merge
git tag phase5-complete
```

### Phase 6: ISO Integration
```bash
git checkout -b phase6-iso-integration
# Develop, test, merge
git tag phase6-complete v1.0.0
```

---

## 📞 Getting Help

**When Git Gets Confusing:**

1. **Check current status:**
   ```bash
   git status
   git branch --show-current
   ```

2. **Don't panic** - Git rarely loses data
3. **Ask before force operations** - get help if unsure
4. **Backup before experiments** - `cp -r .git .git.backup`

**Common Issues:**

**"Detached HEAD" state:**
```bash
# You checked out a tag/commit
git checkout master  # Return to normal
```

**Merge conflicts:**
```bash
# Edit conflicting files
# Look for <<<<<<< markers
git add resolved-file.c
git commit -m "Resolve merge conflict"
```

**Accidentally deleted uncommitted work:**
```bash
# If you used git add before:
git reflog  # Find the commit
git checkout <commit-hash> -- file.c
```

---

## ✅ Git Setup Checklist

Before starting Phase 2:

- [ ] Kernel source is a git repository
- [ ] Initial commit created (Phase 1 baseline)
- [ ] phase1-complete tag created
- [ ] .gitignore configured
- [ ] Git user.name and user.email set
- [ ] Understand branch creation (git checkout -b)
- [ ] Understand merging (git merge)
- [ ] Understand tagging (git tag -a)
- [ ] Know how to rollback (git checkout tag)

**Run the setup script:**
```bash
sudo /home/diablorain/Syn_OS/scripts/kernel/initialize-kernel-git.sh
```

---

**Adopted Strategy:** One feature branch per phase, merge to master only after comprehensive testing and success confirmation.

**Next Step:** Run initialize-kernel-git.sh, then create phase2-ai-syscalls branch when ready to start Phase 2.

---

**End of Git Branching Strategy Document**
