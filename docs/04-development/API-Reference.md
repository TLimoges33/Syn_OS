# 📖 API Reference

**Complexity**: Intermediate to Advanced  
**Audience**: Developers, System Integrators, Tool Builders  
**Prerequisites**: Programming experience, REST APIs, system programming

This page provides a comprehensive reference to all SynOS APIs, including system calls, REST endpoints, Python bindings, and development libraries.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Call API](#system-call-api)
3. [REST API](#rest-api)
4. [Python Bindings](#python-bindings)
5. [Rust Libraries](#rust-libraries)
6. [CLI Tools](#cli-tools)
7. [API Authentication](#api-authentication)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Versioning](#versioning)

---

## 1. Overview

SynOS provides multiple API layers for different use cases:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  REST API        Python API      CLI Tools      Web UI      │
│  (HTTP/JSON)     (Bindings)      (Commands)     (Browser)   │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────┐
│                    Core Services                             │
│  • AI Engine  • Security  • Monitoring  • Management         │
└────────────┬─────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────┐
│                   System Call Interface                      │
│  • File I/O  • Process  • Memory  • Network  • SynOS-specific│
└────────────┬─────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────┐
│                         Kernel                               │
└──────────────────────────────────────────────────────────────┘
```

### API Documentation Locations

| API Type            | Documentation                                                         | Status      |
| ------------------- | --------------------------------------------------------------------- | ----------- |
| **System Calls**    | [/docs/api/SYSCALL_REFERENCE.md](../../docs/api/SYSCALL_REFERENCE.md) | ✅ Complete |
| **REST API**        | [/docs/api/REST_API.md](../../docs/api/REST_API.md)                   | ✅ Complete |
| **Python Bindings** | This page + inline docs                                               | ✅ Complete |
| **Rust Libraries**  | [docs.rs](https://docs.rs) + inline docs                              | ✅ Complete |
| **CLI Tools**       | Man pages + `--help`                                                  | ✅ Complete |

---

## 2. System Call API

### Complete Reference

For the **complete system call reference** including all POSIX and SynOS-specific system calls, see:

**📄 [System Call Interface Documentation](../../SYSCALL_INTERFACE_DOCUMENTATION.md)**

This comprehensive document includes:

-   All 43+ SynOS-specific system calls
-   200+ POSIX-compatible system calls
-   Function signatures and parameters
-   Return values and error codes
-   Code examples in C and Rust
-   Performance characteristics
-   Security considerations

### Quick Reference

**File I/O**:

```c
int synos_open(const char *path, int flags, mode_t mode);
ssize_t synos_read(int fd, void *buf, size_t count);
ssize_t synos_write(int fd, const void *buf, size_t count);
int synos_close(int fd);
```

**AI System Calls**:

```c
int synos_ai_query(const char *query, size_t len, char *response, size_t response_len);
int synos_ai_state(struct consciousness_state *state);
int synos_ai_learn(const char *data, size_t len);
```

**Security System Calls**:

```c
int synos_security_scan(uint32_t scan_type, struct scan_results *results);
int synos_check_capability(capability_t cap);
int synos_set_security_context(const struct security_context *ctx);
```

### Example: Using System Calls

```rust
// Rust example using system calls
use synos_sys::syscalls;

fn main() {
    // Query AI consciousness
    let query = "What is my current security posture?";
    let mut response = [0u8; 1024];

    unsafe {
        let result = syscalls::synos_ai_query(
            query.as_ptr(),
            query.len(),
            response.as_mut_ptr(),
            response.len(),
        );

        if result > 0 {
            let response_str = std::str::from_utf8(&response[..result as usize]).unwrap();
            println!("AI Response: {}", response_str);
        }
    }
}
```

---

## 3. REST API

### Base URL

```
https://localhost:8443/api/v1
```

### Authentication

All REST API requests require authentication via JWT token:

```bash
# Get authentication token
curl -X POST https://localhost:8443/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-10-05T00:00:00Z"
}

# Use token in subsequent requests
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  https://localhost:8443/api/v1/system/status
```

### Endpoints

#### System Endpoints

| Method | Endpoint           | Description            |
| ------ | ------------------ | ---------------------- |
| `GET`  | `/system/status`   | Get system status      |
| `GET`  | `/system/info`     | Get system information |
| `POST` | `/system/reboot`   | Reboot system          |
| `POST` | `/system/shutdown` | Shutdown system        |

**Example**:

```bash
# Get system status
curl -H "Authorization: Bearer $TOKEN" \
  https://localhost:8443/api/v1/system/status

# Response:
{
  "status": "healthy",
  "uptime": 86400,
  "cpu_usage": 25.5,
  "memory_usage": 60.2,
  "disk_usage": 45.0,
  "services": {
    "ai_engine": "running",
    "security_monitor": "running",
    "web_interface": "running"
  }
}
```

#### AI Endpoints

| Method | Endpoint      | Description                |
| ------ | ------------- | -------------------------- |
| `POST` | `/ai/query`   | Query AI consciousness     |
| `GET`  | `/ai/state`   | Get consciousness state    |
| `POST` | `/ai/learn`   | Teach AI new information   |
| `GET`  | `/ai/metrics` | Get AI performance metrics |

**Example**:

```bash
# Query AI
curl -X POST https://localhost:8443/api/v1/ai/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What threats are currently detected?"}'

# Response:
{
  "response": "Currently monitoring 3 suspicious connections from IP 192.168.1.100...",
  "confidence": 0.95,
  "processing_time_ms": 45
}
```

#### Security Endpoints

| Method | Endpoint             | Description            |
| ------ | -------------------- | ---------------------- |
| `POST` | `/security/scan`     | Initiate security scan |
| `GET`  | `/security/threats`  | List detected threats  |
| `GET`  | `/security/alerts`   | Get security alerts    |
| `POST` | `/security/block-ip` | Block IP address       |

**Example**:

```bash
# Start network scan
curl -X POST https://localhost:8443/api/v1/security/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "network",
    "target": "192.168.1.0/24",
    "options": {
      "syn_scan": true,
      "ports": "1-1000"
    }
  }'

# Response:
{
  "scan_id": "scan-123456",
  "status": "in_progress",
  "estimated_completion": "2025-10-04T12:30:00Z"
}

# Check scan results
curl -H "Authorization: Bearer $TOKEN" \
  https://localhost:8443/api/v1/security/scan/scan-123456
```

#### Tool Endpoints

| Method | Endpoint            | Description                   |
| ------ | ------------------- | ----------------------------- |
| `GET`  | `/tools/list`       | List available security tools |
| `POST` | `/tools/execute`    | Execute security tool         |
| `GET`  | `/tools/:id/output` | Get tool execution output     |

**Example**:

```bash
# Execute nmap scan
curl -X POST https://localhost:8443/api/v1/tools/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "nmap",
    "args": ["-sS", "-p", "1-1000", "192.168.1.1"],
    "ai_assist": true
  }'

# Response:
{
  "execution_id": "exec-789012",
  "status": "running",
  "pid": 12345
}
```

---

## 4. Python Bindings

### Installation

```bash
# Install SynOS Python library
pip install synos-sdk

# Or from source
cd /opt/synos/python
pip install -e .
```

### Usage

#### AI Consciousness

```python
from synos import AiEngine

# Initialize AI engine
ai = AiEngine()

# Query AI
response = ai.query("What is my current security posture?")
print(f"AI Response: {response.text}")
print(f"Confidence: {response.confidence}")

# Get consciousness state
state = ai.get_state()
print(f"Active neural groups: {state.active_groups}")
print(f"Learning progress: {state.learning_progress}%")

# Teach AI
ai.learn({
    "event": "login_attempt",
    "source_ip": "192.168.1.100",
    "success": False,
    "timestamp": "2025-10-04T12:00:00Z"
})
```

#### Security Operations

```python
from synos import SecurityEngine

# Initialize security engine
security = SecurityEngine()

# Perform network scan
scan = security.scan_network(
    target="192.168.1.0/24",
    ports="1-1000",
    scan_type="syn"
)

# Wait for completion
scan.wait()

# Get results
for host in scan.results.hosts:
    print(f"Host: {host.ip}")
    for port in host.open_ports:
        print(f"  Port {port.number}: {port.service}")

# Execute security tool
result = security.execute_tool(
    tool="nmap",
    args=["-sS", "-p", "80,443", "example.com"],
    ai_assist=True
)

print(f"Tool output: {result.stdout}")
```

#### System Management

```python
from synos import SystemManager

# Initialize system manager
system = SystemManager()

# Get system status
status = system.get_status()
print(f"CPU Usage: {status.cpu_usage}%")
print(f"Memory Usage: {status.memory_usage}%")

# Manage services
system.restart_service("synos-ai-engine")

# Get metrics
metrics = system.get_metrics(
    start_time="2025-10-04T00:00:00Z",
    end_time="2025-10-04T12:00:00Z"
)

for metric in metrics:
    print(f"{metric.name}: {metric.value} at {metric.timestamp}")
```

---

## 5. Rust Libraries

### Core Libraries

SynOS provides several Rust crates:

| Crate            | Description                     | Version |
| ---------------- | ------------------------------- | ------- |
| `synos-core`     | Core system types and utilities | 1.0.0   |
| `synos-ai`       | AI consciousness engine         | 1.0.0   |
| `synos-security` | Security framework              | 1.0.0   |
| `synos-kernel`   | Kernel interfaces               | 1.0.0   |
| `synos-sys`      | Low-level system calls          | 1.0.0   |

### Usage

Add to `Cargo.toml`:

```toml
[dependencies]
synos-core = "1.0"
synos-ai = "1.0"
synos-security = "1.0"
```

#### AI Consciousness Example

```rust
use synos_ai::{ConsciousnessEngine, Query};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize AI engine
    let mut engine = ConsciousnessEngine::new().await?;

    // Query AI
    let query = Query::new("What threats are detected?");
    let response = engine.query(query).await?;

    println!("Response: {}", response.text);
    println!("Confidence: {:.2}", response.confidence);

    // Subscribe to AI events
    let mut events = engine.subscribe_events();
    while let Some(event) = events.recv().await {
        println!("AI Event: {:?}", event);
    }

    Ok(())
}
```

#### Security Framework Example

```rust
use synos_security::{SecurityEngine, ScanType, AccessControl};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize security engine
    let security = SecurityEngine::new()?;

    // Check access control
    let allowed = security.check_access(
        subject_context,
        object_context,
        SecurityClass::File,
        &[Permission::Read],
    )?;

    if allowed {
        println!("Access granted");
    }

    // Perform security scan
    let scan = security.start_scan(ScanType::Network {
        target: "192.168.1.0/24".parse()?,
        ports: vec![80, 443, 8080],
    })?;

    // Wait for results
    let results = scan.wait()?;

    for threat in results.threats {
        println!("Threat: {:?}", threat);
    }

    Ok(())
}
```

---

## 6. CLI Tools

### SynOS Command-Line Tools

| Tool             | Description         | Man Page             |
| ---------------- | ------------------- | -------------------- |
| `synos`          | Main CLI tool       | `man synos`          |
| `synos-ai`       | AI management       | `man synos-ai`       |
| `synos-security` | Security operations | `man synos-security` |
| `synos-scan`     | Network scanning    | `man synos-scan`     |
| `synpkg`         | Package management  | `man synpkg`         |

### Examples

#### System Management

```bash
# Get system information
synos info

# Get system status
synos status

# View logs
synos logs --service ai-engine --tail 100

# Restart service
synos service restart synos-ai-engine
```

#### AI Operations

```bash
# Query AI
synos-ai query "What is my security posture?"

# Get AI state
synos-ai state

# Update AI models
synos-ai update-models

# View AI metrics
synos-ai metrics
```

#### Security Operations

```bash
# Scan network
synos-scan network 192.168.1.0/24 -p 1-1000

# Scan for vulnerabilities
synos-security vuln-scan --target localhost

# List detected threats
synos-security threats list

# Block IP address
synos-security block-ip 192.168.1.100

# View security logs
synos-security audit-log --since "1 hour ago"
```

---

## 7. API Authentication

### JWT Token Authentication

SynOS uses JWT (JSON Web Tokens) for API authentication:

```python
from synos.auth import authenticate

# Authenticate and get token
token = authenticate(
    username="admin",
    password="password",
    mfa_code="123456"  # If MFA enabled
)

# Use token in API calls
from synos import AiEngine

ai = AiEngine(auth_token=token)
response = ai.query("Hello")
```

### API Keys

For service-to-service authentication:

```bash
# Generate API key
synos api-key create --name "monitoring-service" \
  --permissions "read:metrics,write:logs"

# Use API key
curl -H "X-API-Key: your-api-key-here" \
  https://localhost:8443/api/v1/system/status
```

### OAuth2 Support

For third-party integrations:

```python
from synos.auth import OAuth2Client

client = OAuth2Client(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://your-app.com/callback"
)

# Get authorization URL
auth_url = client.get_authorization_url(
    scope=["read:ai", "write:security"]
)

# Exchange code for token
token = client.exchange_code(authorization_code)
```

---

## 8. Error Handling

### Error Codes

All APIs use consistent error codes:

| Code | Name           | Description                |
| ---- | -------------- | -------------------------- |
| 200  | Success        | Operation successful       |
| 400  | Bad Request    | Invalid request parameters |
| 401  | Unauthorized   | Authentication required    |
| 403  | Forbidden      | Insufficient permissions   |
| 404  | Not Found      | Resource not found         |
| 429  | Rate Limited   | Too many requests          |
| 500  | Internal Error | Server error               |

### Error Response Format

```json
{
    "error": {
        "code": "INVALID_PARAMETER",
        "message": "Invalid target IP address",
        "details": {
            "parameter": "target",
            "value": "invalid-ip",
            "expected": "Valid IPv4 or IPv6 address"
        }
    }
}
```

### Exception Handling (Python)

```python
from synos import AiEngine
from synos.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError,
    RateLimitError
)

try:
    ai = AiEngine()
    response = ai.query("Test query")
except AuthenticationError:
    print("Please authenticate first")
except PermissionDeniedError:
    print("Insufficient permissions")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ResourceNotFoundError:
    print("Resource not found")
```

---

## 9. Rate Limiting

### Default Limits

| API Type       | Rate Limit         |
| -------------- | ------------------ |
| REST API       | 1000 requests/hour |
| System Calls   | No limit           |
| AI Queries     | 100 queries/minute |
| Security Scans | 10 scans/hour      |

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1696435200
```

### Handling Rate Limits

```python
import time
from synos import AiEngine
from synos.exceptions import RateLimitError

def query_with_retry(ai, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return ai.query(query)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(e.retry_after)
            else:
                raise
```

---

## 10. Versioning

### API Version Policy

SynOS follows semantic versioning for APIs:

-   **Major version** (v1, v2): Breaking changes
-   **Minor version** (v1.1, v1.2): New features, backward compatible
-   **Patch version** (v1.1.1, v1.1.2): Bug fixes

### Version Support

| Version | Status  | Support Until |
| ------- | ------- | ------------- |
| v1.x    | Current | Ongoing       |
| v2.x    | Planned | TBD           |

### Specifying API Version

**REST API**:

```bash
# Version in URL (recommended)
curl https://localhost:8443/api/v1/system/status

# Version in header
curl -H "API-Version: 1.0" \
  https://localhost:8443/api/system/status
```

**Python**:

```python
from synos import AiEngine

# Specify version
ai = AiEngine(api_version="1.0")
```

---

## 📚 Additional Resources

### Documentation

-   **[System Call Reference](../../SYSCALL_INTERFACE_DOCUMENTATION.md)** - Complete system call documentation
-   **[Development Guide](Development-Guide.md)** - Development environment setup
-   **[Custom Kernel](Custom-Kernel.md)** - Kernel architecture details
-   **[Security Framework](Security-Framework.md)** - Security API details

### Code Examples

-   **[Example Projects](https://github.com/synos/examples)** - Sample applications
-   **[API Cookbook](https://docs.synos.dev/cookbook)** - Common recipes
-   **[Integration Guides](https://docs.synos.dev/integrations)** - Third-party integrations

### Support

-   **GitHub Issues**: [https://github.com/TLimoges33/Syn_OS/issues](https://github.com/TLimoges33/Syn_OS/issues)
-   **Documentation**: [https://docs.synos.dev](https://docs.synos.dev)
-   **Community**: [https://community.synos.dev](https://community.synos.dev)

---

**Last Updated**: October 4, 2025  
**API Version**: v1.0  
**Maintainer**: SynOS Development Team  
**License**: MIT

Happy coding! 🚀✨
