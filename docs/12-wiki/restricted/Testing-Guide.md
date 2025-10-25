# 🧪 Testing Guide

**Test Types**: Unit, integration, system  
**Frameworks**: Rust test, pytest, QEMU  
**Coverage**: 75%+ target

---

## Running Tests

```bash
# All tests
make test

# Kernel tests
cd src/kernel
cargo test

# Security tests
cd core/security
cargo test

# Python tests
cd development/tests
pytest

# Integration tests
./scripts/run-integration-tests.sh
```

---

## Test Structure

```
tests/
├── unit/           # Unit tests
│   ├── kernel/
│   ├── security/
│   └── userspace/
├── integration/    # Integration tests
│   ├── api/
│   ├── cli/
│   └── system/
└── system/         # Full system tests
    ├── boot/
    ├── network/
    └── security/
```

---

## Writing Tests

### Rust Unit Test

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memory_alloc() {
        let ptr = allocate(1024);
        assert!(!ptr.is_null());
        deallocate(ptr);
    }
}
```

### Python Integration Test

```python
import pytest
from synos_api import SynOS

def test_ai_inference():
    client = SynOS()
    result = client.ai.infer("model.onnx", input_data)
    assert result.success
    assert len(result.output) > 0
```

---

## CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: make test
      - name: Coverage
        run: cargo tarpaulin --out Xml
```

---

## Coverage

```bash
# Generate coverage
cargo tarpaulin --out Html

# View report
firefox tarpaulin-report.html

# Coverage badge
cargo tarpaulin --out Xml
bash <(curl -s https://codecov.io/bash)
```

---

## Performance Tests

```bash
# Benchmark kernel
cd src/kernel
cargo bench

# System benchmarks
./scripts/run-benchmarks.sh

# Load testing
ab -n 10000 -c 100 http://localhost:8080/
```

---

**Test Dashboard**: https://ci.synos.dev  
**Coverage**: https://codecov.io/gh/synos/syn_os
