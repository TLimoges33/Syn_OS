# SynOS Fuzzing Guide

## 🎯 Overview

This guide explains how to run fuzzing tests on SynOS to discover security vulnerabilities.

## 🔧 Prerequisites

```bash
# Install cargo-fuzz (already done)
cargo install cargo-fuzz

# Verify installation
cargo fuzz --version
```

## 🚀 Quick Start

### **Option 1: Automated Script (Recommended)**

Run both fuzz targets overnight (8 hours total):

```bash
cd /home/diablorain/Syn_OS
nohup ./scripts/run-fuzzing.sh > ~/fuzzing.log 2>&1 &

# Check progress
tail -f ~/fuzzing.log

# Check if still running
ps aux | grep cargo-fuzz
```

### **Option 2: Manual Execution**

Run individual fuzz targets:

```bash
cd /home/diablorain/Syn_OS/fuzz

# Quick test (1 minute)
cargo fuzz run fuzz_input_validation -- -max_total_time=60

# Medium test (1 hour)
cargo fuzz run fuzz_input_validation -- -max_total_time=3600

# Extended test (8 hours - overnight)
nohup cargo fuzz run fuzz_input_validation -- -max_total_time=28800 > ~/fuzz_results.txt 2>&1 &
```

## 📊 Fuzz Targets

### **1. fuzz_input_validation**
**Purpose**: Tests input validation functions

**Coverage**:
- Syscall number validation
- Memory address bounds checking
- Integer overflow detection
- Constant-time comparison (timing attack prevention)

**Expected Findings**:
- Invalid syscall numbers
- Out-of-bounds memory access
- Integer overflow edge cases

### **2. fuzz_parser**
**Purpose**: Tests parsing functions

**Coverage**:
- IPC message parsing
- Command string parsing (injection prevention)
- Buffer overflow in parsers

**Expected Findings**:
- Malformed IPC messages
- Command injection attempts
- Buffer overflow conditions

## 🔍 Interpreting Results

### **Success Output**
```
#12345: cov: 234 ft: 567 corp: 89/12Kb exec/s: 456 rss: 123Mb
```

Metrics:
- `cov: 234` - Code coverage (234 edges)
- `ft: 567` - Features found
- `corp: 89/12Kb` - Corpus size (89 inputs, 12KB)
- `exec/s: 456` - Executions per second
- `rss: 123Mb` - Memory usage

### **Crash Found!**
```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow
```

When fuzzing finds a crash:
1. **Crash artifact saved** to `fuzz/artifacts/<target_name>/`
2. **Reproduce** the crash:
   ```bash
   cargo fuzz run <target_name> artifacts/<target_name>/crash-abc123
   ```
3. **Debug** with more info:
   ```bash
   RUST_BACKTRACE=1 cargo fuzz run <target_name> artifacts/<target_name>/crash-abc123
   ```

## 🐛 What To Do When You Find Bugs

### **Step 1: Reproduce Locally**
```bash
cargo fuzz run fuzz_input_validation artifacts/fuzz_input_validation/crash-abc123
```

### **Step 2: Minimize Test Case**
```bash
cargo fuzz tmin fuzz_input_validation artifacts/fuzz_input_validation/crash-abc123
```

### **Step 3: Document the Vulnerability**

Create a file `docs/security/CVE-SYNOS-001.md`:

```markdown
# CVE-SYNOS-001: Integer Overflow in Syscall Validation

## Summary
Integer overflow in syscall number validation allows...

## Severity
🔴 CRITICAL (CVSS 9.8)

## Affected Code
`fuzz-testable/src/lib.rs:validate_syscall()`

## Proof of Concept
\`\`\`rust
validate_syscall(u32::MAX)  // Triggers overflow
\`\`\`

## Fix
\`\`\`rust
pub fn validate_syscall(syscall_num: u32) -> Result<&'static str, &'static str> {
    // Add bounds check
    if syscall_num > MAX_SYSCALL {
        return Err("Syscall number too large");
    }
    // ... rest of function
}
\`\`\`

## Discovered By
Fuzzing campaign on 2025-09-30

## Status
- [ ] Reproduced
- [ ] Fixed
- [ ] Tested
- [ ] Documented
```

### **Step 4: Fix the Bug**

Edit the vulnerable code and add test:

```rust
#[test]
fn test_syscall_overflow_prevention() {
    assert!(validate_syscall(u32::MAX).is_err());
}
```

### **Step 5: Verify Fix**

Re-run fuzzing to ensure crash is gone:

```bash
cargo fuzz run fuzz_input_validation -- -max_total_time=600
```

## 📈 Optimization Tips

### **Faster Fuzzing**

```bash
# Use more CPU cores
cargo fuzz run fuzz_input_validation -- -jobs=8

# Larger corpus
cargo fuzz run fuzz_input_validation -- -max_len=4096

# Focus on specific code
cargo fuzz run fuzz_input_validation -- -focus_function=validate_syscall
```

### **Better Coverage**

```bash
# Dictionary for guided fuzzing
echo "syscall" > fuzz/dict.txt
echo "0x" >> fuzz/dict.txt

cargo fuzz run fuzz_input_validation -- -dict=dict.txt
```

## 🎓 Learning Resources

### **Understanding Fuzzing Output**

- **Coverage (cov)**: Higher is better. Goal: 80%+ code coverage
- **Corpus size**: Grows as fuzzer finds interesting inputs
- **Exec/s**: Higher is better. Aim for 1000+ on modern CPUs

### **Common Crashes**

| Error | Meaning | Severity |
|-------|---------|----------|
| heap-buffer-overflow | Writing past buffer end | 🔴 Critical |
| stack-buffer-overflow | Stack smashing | 🔴 Critical |
| use-after-free | Accessing freed memory | 🔴 Critical |
| integer-overflow | Math overflow | 🟠 High |
| timeout | Infinite loop | 🟡 Medium |

### **Fuzzing Best Practices**

1. **Start small**: 1 minute → 1 hour → overnight
2. **Fix crashes immediately**: Don't accumulate bugs
3. **Document everything**: Future you will thank you
4. **Re-run after fixes**: Verify the fix works
5. **Share findings**: Blog posts, CVEs, papers

## 🏆 Success Metrics

Good fuzzing campaign should:
- ✅ Run for 8+ hours minimum
- ✅ Achieve 70%+ code coverage
- ✅ Generate 100+ corpus inputs
- ✅ Execute 500+ iterations/second
- ✅ Find at least 1 bug (even if minor)

## 📝 Results Template

After fuzzing, create a summary:

```markdown
# Fuzzing Results - 2025-09-30

## Campaign Details
- Duration: 8 hours
- Targets: 2
- CPU: 8 cores
- Iterations: ~14.4 million

## Findings
- **Bugs found**: 3
  - 2 integer overflows (fixed)
  - 1 buffer overflow (fixed)
- **Coverage**: 78%
- **Corpus size**: 234 inputs

## Impact
All critical vulnerabilities patched before release.
Demonstrates thorough security testing.
```

## 🔗 Additional Resources

- [cargo-fuzz Documentation](https://rust-fuzz.github.io/book/)
- [libFuzzer Options](https://llvm.org/docs/LibFuzzer.html)
- [Fuzzing Best Practices](https://google.github.io/fuzzing/tutorial/)

---

**Happy Fuzzing!** 🐛🔨

*Remember: Every bug you find is a vulnerability attackers won't exploit!*
