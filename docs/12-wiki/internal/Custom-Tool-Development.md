# 🔧 Custom Security Tool Development

**Complexity**: Intermediate to Advanced  
**Audience**: Tool Developers, Security Engineers  
**Prerequisites**: Python or Rust, security concepts

Develop custom security tools and integrate them with SynOS.

---

## Quick Start

### Python Security Tool

```python
#!/usr/bin/env python3
# port_scanner.py - Simple port scanner

import socket
from synos_tools import SecurityTool, register

class PortScanner(SecurityTool):
    """Custom port scanner tool"""
    
    name = "Port Scanner"
    category = "reconnaissance"
    version = "1.0"
    
    def __init__(self):
        super().__init__()
    
    def scan_port(self, host, port):
        """Scan single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def run(self, target, ports=None):
        """Run port scan"""
        if ports is None:
            ports = [20, 21, 22, 23, 25, 80, 443, 3389, 8080]
        
        self.log(f"Scanning {target}...")
        open_ports = []
        
        for port in ports:
            if self.scan_port(target, port):
                open_ports.append(port)
                self.log(f"Port {port}: OPEN", level="success")
            else:
                self.log(f"Port {port}: closed", level="debug")
        
        return {
            'target': target,
            'open_ports': open_ports,
            'total_scanned': len(ports)
        }

# Register tool with SynOS
if __name__ == "__main__":
    scanner = PortScanner()
    register(scanner)
```

### Rust Security Tool

```rust
// sql_detector.rs - SQL injection pattern detector
use synos_tools::{SecurityTool, ToolResult, register_tool};

pub struct SQLDetector {
    patterns: Vec<String>,
}

impl SQLDetector {
    pub fn new() -> Self {
        Self {
            patterns: vec![
                "' OR '1'='1".to_string(),
                "'; DROP TABLE".to_string(),
                "UNION SELECT".to_string(),
            ],
        }
    }
}

impl SecurityTool for SQLDetector {
    fn name(&self) -> &str {
        "SQL Injection Detector"
    }
    
    fn category(&self) -> &str {
        "web_security"
    }
    
    fn run(&mut self, input: &str) -> ToolResult {
        let mut findings = Vec::new();
        
        for pattern in &self.patterns {
            if input.to_uppercase().contains(&pattern.to_uppercase()) {
                findings.push(format!("Found pattern: {}", pattern));
            }
        }
        
        ToolResult {
            success: findings.is_empty(),
            message: format!("Detected {} potential SQLi patterns", findings.len()),
            data: findings,
        }
    }
}

fn main() {
    let detector = SQLDetector::new();
    register_tool(Box::new(detector));
}
```

---

## Tool Structure

### Directory Layout

```
my-security-tool/
├── src/
│   ├── main.py          # Entry point
│   ├── scanner.py       # Core logic
│   └── utils.py         # Utilities
├── config/
│   └── default.yml      # Configuration
├── tests/
│   └── test_scanner.py  # Unit tests
├── README.md
├── setup.py
└── requirements.txt
```

### Configuration

```yaml
# config/default.yml
tool:
  name: "My Scanner"
  version: "1.0.0"
  category: "reconnaissance"
  
scan:
  timeout: 5
  threads: 10
  ports: [80, 443, 8080]
  
output:
  format: "json"
  verbose: true
```

---

## Integration with SynOS

### Tool Registry

```python
# Register tool with SynOS registry
from synos_tools import register_tool

register_tool(
    name="my-scanner",
    command="/opt/my-scanner/run.py",
    category="reconnaissance",
    description="Custom network scanner",
    version="1.0.0"
)
```

### CLI Integration

```bash
# Use tool via synos-tools CLI
synos-tools run my-scanner --target 192.168.1.0/24

# List custom tools
synos-tools list --custom

# Update tool
synos-tools update my-scanner
```

### API Integration

```python
# REST API endpoint for custom tool
from synos_api import api_endpoint

@api_endpoint('/tools/my-scanner/scan')
def scan_endpoint(request):
    target = request.json.get('target')
    
    scanner = MyScanner()
    results = scanner.run(target)
    
    return {
        'status': 'success',
        'results': results
    }
```

---

## Best Practices

### 1. Error Handling

```python
try:
    results = scanner.scan(target)
except NetworkError as e:
    log.error(f"Network error: {e}")
    return {"error": str(e)}
except Exception as e:
    log.exception("Unexpected error")
    return {"error": "Internal error"}
```

### 2. Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Starting scan...")
logger.debug(f"Target: {target}")
logger.warning("Slow response detected")
logger.error("Scan failed")
```

### 3. Progress Reporting

```python
from tqdm import tqdm

for host in tqdm(hosts, desc="Scanning"):
    scan_host(host)
```

### 4. Multi-threading

```python
from concurrent.futures import ThreadPoolExecutor

def scan_host(host):
    # Scan logic
    pass

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(scan_host, hosts))
```

---

## Testing

```python
# tests/test_scanner.py
import unittest
from scanner import PortScanner

class TestPortScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = PortScanner()
    
    def test_scan_open_port(self):
        result = self.scanner.scan_port('localhost', 80)
        self.assertTrue(result)
    
    def test_scan_closed_port(self):
        result = self.scanner.scan_port('localhost', 9999)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
```

---

## Distribution

### PyPI Package

```python
# setup.py
from setuptools import setup

setup(
    name='my-security-tool',
    version='1.0.0',
    packages=['my_tool'],
    install_requires=[
        'synos-tools>=2.0',
        'requests>=2.25',
    ],
    entry_points={
        'console_scripts': [
            'my-tool=my_tool.main:main',
        ],
    },
)
```

### Docker Container

```dockerfile
FROM synos/base:latest

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN synos-tools register .

CMD ["python", "main.py"]
```

---

## Examples

**More examples**: `/opt/synos/examples/tools/`

---

**Last Updated**: October 4, 2025  
**Support**: tools@synos.dev
