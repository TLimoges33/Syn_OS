# Syn_OS Component Interface Specifications

* *Version**: 1.0
* *Date**: 2025-07-23
* *Purpose**: Define standardized interfaces for all Syn_OS components

## Table of Contents

1. [Interface Standards](#interface-standards)
2. [Service Orchestrator API](#service-orchestrator-api)
3. [Message Bus Events](#message-bus-events)
4. [Security Framework API](#security-framework-api)
5. [Neural Darwinism API](#neural-darwinism-api)
6. [Context Engine API](#context-engine-api)
7. [LM Studio Proxy API](#lm-studio-proxy-api)
8. [Common Data Models](#common-data-models)

## Interface Standards

### API Design Principles

1. **RESTful**: Use HTTP methods appropriately (GET, POST, PUT, DELETE)
2. **Versioned**: All APIs include version in path `/api/v1/`
3. **JSON**: Request/response bodies in JSON format
4. **Status Codes**: Use standard HTTP status codes
5. **Authentication**: Bearer token in Authorization header
6. **Pagination**: Limit/offset for list endpoints
7. **Filtering**: Query parameters for filtering
8. **Error Format**: Consistent error response structure

### Standard Error Response

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Service 'neural-darwinism' not found",
    "details": {
      "service_name": "neural-darwinism",
      "timestamp": "2025-07-23T10:30:00Z"
    }
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```text

      "service_name": "neural-darwinism",
      "timestamp": "2025-07-23T10:30:00Z"
    }
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}

```text
      "service_name": "neural-darwinism",
      "timestamp": "2025-07-23T10:30:00Z"
    }
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}

```text
}

```text

### Standard Success Response

```json
```json

```json

```json
{
  "data": {
    // Response data here
  },
  "metadata": {
    "timestamp": "2025-07-23T10:30:00Z",
    "version": "1.0.0",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```text

    "timestamp": "2025-07-23T10:30:00Z",
    "version": "1.0.0",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}

```text
    "timestamp": "2025-07-23T10:30:00Z",
    "version": "1.0.0",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}

```text

```text

## Service Orchestrator API

### Base URL: `http://localhost:8080/api/v1/orchestrator`

### Endpoints

#### 1. Register Service

```http
### Endpoints

#### 1. Register Service

```http

### Endpoints

#### 1. Register Service

```http

```http
POST /services
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "neural-darwinism",
  "type": "container",
  "config": {
    "image": "synos/neural-darwinism:latest",
    "environment": {
      "LOG_LEVEL": "info",
      "MESSAGE_BUS_URL": "nats://message-bus:4222"
    },
    "resources": {
      "cpu_limit": "2.0",
      "memory_limit": "4Gi"
    },
    "health_check": {
      "endpoint": "/health",
      "interval": "30s",
      "timeout": "5s"
    },
    "dependencies": ["message-bus", "security-framework"]
  }
}

Response: 201 Created
{
  "data": {
    "service_id": "svc_123456",
    "name": "neural-darwinism",
    "status": "registered",
    "created_at": "2025-07-23T10:30:00Z"
  }
}
```text

  "name": "neural-darwinism",
  "type": "container",
  "config": {
    "image": "synos/neural-darwinism:latest",
    "environment": {
      "LOG_LEVEL": "info",
      "MESSAGE_BUS_URL": "nats://message-bus:4222"
    },
    "resources": {
      "cpu_limit": "2.0",
      "memory_limit": "4Gi"
    },
    "health_check": {
      "endpoint": "/health",
      "interval": "30s",
      "timeout": "5s"
    },
    "dependencies": ["message-bus", "security-framework"]
  }
}

Response: 201 Created
{
  "data": {
    "service_id": "svc_123456",
    "name": "neural-darwinism",
    "status": "registered",
    "created_at": "2025-07-23T10:30:00Z"
  }
}

```text
  "name": "neural-darwinism",
  "type": "container",
  "config": {
    "image": "synos/neural-darwinism:latest",
    "environment": {
      "LOG_LEVEL": "info",
      "MESSAGE_BUS_URL": "nats://message-bus:4222"
    },
    "resources": {
      "cpu_limit": "2.0",
      "memory_limit": "4Gi"
    },
    "health_check": {
      "endpoint": "/health",
      "interval": "30s",
      "timeout": "5s"
    },
    "dependencies": ["message-bus", "security-framework"]
  }
}

Response: 201 Created
{
  "data": {
    "service_id": "svc_123456",
    "name": "neural-darwinism",
    "status": "registered",
    "created_at": "2025-07-23T10:30:00Z"
  }
}

```text
      "LOG_LEVEL": "info",
      "MESSAGE_BUS_URL": "nats://message-bus:4222"
    },
    "resources": {
      "cpu_limit": "2.0",
      "memory_limit": "4Gi"
    },
    "health_check": {
      "endpoint": "/health",
      "interval": "30s",
      "timeout": "5s"
    },
    "dependencies": ["message-bus", "security-framework"]
  }
}

Response: 201 Created
{
  "data": {
    "service_id": "svc_123456",
    "name": "neural-darwinism",
    "status": "registered",
    "created_at": "2025-07-23T10:30:00Z"
  }
}

```text

#### 2. Start Service

```http
```http

```http

```http
POST /services/{service_name}/start
Authorization: Bearer <token>

Response: 200 OK
{
  "data": {
    "service_name": "neural-darwinism",
    "status": "starting",
    "message": "Service start initiated"
  }
}
```text

  "data": {
    "service_name": "neural-darwinism",
    "status": "starting",
    "message": "Service start initiated"
  }
}

```text
  "data": {
    "service_name": "neural-darwinism",
    "status": "starting",
    "message": "Service start initiated"
  }
}

```text
}

```text

#### 3. Get Service Status

```http
```http

```http

```http
GET /services/{service_name}/status
Authorization: Bearer <token>

Response: 200 OK
{
  "data": {
    "service_name": "neural-darwinism",
    "status": "running",
    "health": "healthy",
    "uptime": "2h30m",
    "resources": {
      "cpu_usage": "0.5",
      "memory_usage": "2.1Gi"
    },
    "last_health_check": "2025-07-23T10:29:30Z"
  }
}
```text

  "data": {
    "service_name": "neural-darwinism",
    "status": "running",
    "health": "healthy",
    "uptime": "2h30m",
    "resources": {
      "cpu_usage": "0.5",
      "memory_usage": "2.1Gi"
    },
    "last_health_check": "2025-07-23T10:29:30Z"
  }
}

```text
  "data": {
    "service_name": "neural-darwinism",
    "status": "running",
    "health": "healthy",
    "uptime": "2h30m",
    "resources": {
      "cpu_usage": "0.5",
      "memory_usage": "2.1Gi"
    },
    "last_health_check": "2025-07-23T10:29:30Z"
  }
}

```text
    "resources": {
      "cpu_usage": "0.5",
      "memory_usage": "2.1Gi"
    },
    "last_health_check": "2025-07-23T10:29:30Z"
  }
}

```text

#### 4. List All Services

```http
```http

```http

```http
GET /services?status=running&limit=10&offset=0
Authorization: Bearer <token>

Response: 200 OK
{
  "data": {
    "services": [
      {
        "name": "neural-darwinism",
        "status": "running",
        "health": "healthy"
      },
      {
        "name": "context-engine",
        "status": "running",
        "health": "healthy"
      }
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  }
}
```text

  "data": {
    "services": [
      {
        "name": "neural-darwinism",
        "status": "running",
        "health": "healthy"
      },
      {
        "name": "context-engine",
        "status": "running",
        "health": "healthy"
      }
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  }
}

```text
  "data": {
    "services": [
      {
        "name": "neural-darwinism",
        "status": "running",
        "health": "healthy"
      },
      {
        "name": "context-engine",
        "status": "running",
        "health": "healthy"
      }
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  }
}

```text
        "health": "healthy"
      },
      {
        "name": "context-engine",
        "status": "running",
        "health": "healthy"
      }
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  }
}

```text

## Message Bus Events

### Event Format

```json
```json

```json

```json
{
  "event_id": "evt_123456",
  "event_type": "service.started",
  "timestamp": "2025-07-23T10:30:00Z",
  "source": "service-orchestrator",
  "data": {
    // Event-specific data
  },
  "metadata": {
    "correlation_id": "corr_789012",
    "user_id": "user_123",
    "trace_id": "trace_345678"
  }
}
```text

  "data": {
    // Event-specific data
  },
  "metadata": {
    "correlation_id": "corr_789012",
    "user_id": "user_123",
    "trace_id": "trace_345678"
  }
}

```text
  "data": {
    // Event-specific data
  },
  "metadata": {
    "correlation_id": "corr_789012",
    "user_id": "user_123",
    "trace_id": "trace_345678"
  }
}

```text
    "user_id": "user_123",
    "trace_id": "trace_345678"
  }
}

```text

### Core Event Types

#### Service Events

- `service.registered` - New service registered
- `service.started` - Service started successfully
- `service.stopped` - Service stopped
- `service.failed` - Service failed
- `service.health_changed` - Health status changed

#### Security Events

- `auth.login_success` - User logged in
- `auth.login_failed` - Login attempt failed
- `auth.token_refreshed` - Token refreshed
- `authz.access_granted` - Access granted to resource
- `authz.access_denied` - Access denied to resource

#### AI Events

- `ai.inference_requested` - AI inference requested
- `ai.inference_completed` - AI inference completed
- `ai.model_loaded` - AI model loaded
- `ai.context_updated` - User context updated
- `ai.learning_milestone` - Learning milestone reached

### Event Subscription

```python
- `service.registered` - New service registered
- `service.started` - Service started successfully
- `service.stopped` - Service stopped
- `service.failed` - Service failed
- `service.health_changed` - Health status changed

#### Security Events

- `auth.login_success` - User logged in
- `auth.login_failed` - Login attempt failed
- `auth.token_refreshed` - Token refreshed
- `authz.access_granted` - Access granted to resource
- `authz.access_denied` - Access denied to resource

#### AI Events

- `ai.inference_requested` - AI inference requested
- `ai.inference_completed` - AI inference completed
- `ai.model_loaded` - AI model loaded
- `ai.context_updated` - User context updated
- `ai.learning_milestone` - Learning milestone reached

### Event Subscription

```python

- `service.registered` - New service registered
- `service.started` - Service started successfully
- `service.stopped` - Service stopped
- `service.failed` - Service failed
- `service.health_changed` - Health status changed

#### Security Events

- `auth.login_success` - User logged in
- `auth.login_failed` - Login attempt failed
- `auth.token_refreshed` - Token refreshed
- `authz.access_granted` - Access granted to resource
- `authz.access_denied` - Access denied to resource

#### AI Events

- `ai.inference_requested` - AI inference requested
- `ai.inference_completed` - AI inference completed
- `ai.model_loaded` - AI model loaded
- `ai.context_updated` - User context updated
- `ai.learning_milestone` - Learning milestone reached

### Event Subscription

```python
- `service.health_changed` - Health status changed

#### Security Events

- `auth.login_success` - User logged in
- `auth.login_failed` - Login attempt failed
- `auth.token_refreshed` - Token refreshed
- `authz.access_granted` - Access granted to resource
- `authz.access_denied` - Access denied to resource

#### AI Events

- `ai.inference_requested` - AI inference requested
- `ai.inference_completed` - AI inference completed
- `ai.model_loaded` - AI model loaded
- `ai.context_updated` - User context updated
- `ai.learning_milestone` - Learning milestone reached

### Event Subscription

```python

## Python example

import asyncio
from nats.aio.client import Client as NATS

async def message_handler(msg):
    event = json.loads(msg.data.decode())
    print(f"Received event: {event['event_type']}")

async def subscribe():
    nc = NATS()
    await nc.connect("nats://message-bus:4222")

    # Subscribe to all service events
    await nc.subscribe("events.service.*", cb=message_handler)

    # Subscribe to specific event
    await nc.subscribe("events.ai.inference_completed", cb=message_handler)
```text

async def message_handler(msg):
    event = json.loads(msg.data.decode())
    print(f"Received event: {event['event_type']}")

async def subscribe():
    nc = NATS()
    await nc.connect("nats://message-bus:4222")

    # Subscribe to all service events
    await nc.subscribe("events.service.*", cb=message_handler)

    # Subscribe to specific event
    await nc.subscribe("events.ai.inference_completed", cb=message_handler)

```text

async def message_handler(msg):
    event = json.loads(msg.data.decode())
    print(f"Received event: {event['event_type']}")

async def subscribe():
    nc = NATS()
    await nc.connect("nats://message-bus:4222")

    # Subscribe to all service events
    await nc.subscribe("events.service.*", cb=message_handler)

    # Subscribe to specific event
    await nc.subscribe("events.ai.inference_completed", cb=message_handler)

```text
async def subscribe():
    nc = NATS()
    await nc.connect("nats://message-bus:4222")

    # Subscribe to all service events
    await nc.subscribe("events.service.*", cb=message_handler)

    # Subscribe to specific event
    await nc.subscribe("events.ai.inference_completed", cb=message_handler)

```text

## Security Framework API

### Base URL: `http://localhost:8081/api/v1/security`

### Authentication Endpoints

#### 1. Login

```http
### Authentication Endpoints

#### 1. Login

```http

### Authentication Endpoints

#### 1. Login

```http

```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password",
  "mfa_code": "123456"  // Optional
}

Response: 200 OK
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"]
    }
  }
}
```text

  "password": "secure_password",
  "mfa_code": "123456"  // Optional
}

Response: 200 OK
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"]
    }
  }
}

```text
  "password": "secure_password",
  "mfa_code": "123456"  // Optional
}

Response: 200 OK
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"]
    }
  }
}

```text
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"]
    }
  }
}

```text

#### 2. Validate Token

```http
```http

```http

```http
POST /auth/validate
Authorization: Bearer <token>

Response: 200 OK
{
  "data": {
    "valid": true,
    "claims": {
      "sub": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"],
      "exp": 1721736600
    }
  }
}
```text

  "data": {
    "valid": true,
    "claims": {
      "sub": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"],
      "exp": 1721736600
    }
  }
}

```text
  "data": {
    "valid": true,
    "claims": {
      "sub": "user_123",
      "email": "user@example.com",
      "roles": ["user", "developer"],
      "exp": 1721736600
    }
  }
}

```text
      "roles": ["user", "developer"],
      "exp": 1721736600
    }
  }
}

```text

### Authorization Endpoints

#### 1. Check Permission

```http
```http

```http

```http
POST /authz/check
Authorization: Bearer <token>
Content-Type: application/json

{
  "resource": "service:neural-darwinism",
  "action": "start",
  "context": {
    "ip_address": "192.168.1.100",
    "user_agent": "SynOS-CLI/1.0"
  }
}

Response: 200 OK
{
  "data": {
    "allowed": true,
    "reason": "User has 'service:manage' permission"
  }
}
```text

  "resource": "service:neural-darwinism",
  "action": "start",
  "context": {
    "ip_address": "192.168.1.100",
    "user_agent": "SynOS-CLI/1.0"
  }
}

Response: 200 OK
{
  "data": {
    "allowed": true,
    "reason": "User has 'service:manage' permission"
  }
}

```text
  "resource": "service:neural-darwinism",
  "action": "start",
  "context": {
    "ip_address": "192.168.1.100",
    "user_agent": "SynOS-CLI/1.0"
  }
}

Response: 200 OK
{
  "data": {
    "allowed": true,
    "reason": "User has 'service:manage' permission"
  }
}

```text
  }
}

Response: 200 OK
{
  "data": {
    "allowed": true,
    "reason": "User has 'service:manage' permission"
  }
}

```text

## Neural Darwinism API

### Base URL: `http://localhost:8082/api/v1/consciousness`

### Endpoints

#### 1. Process Input

```http
### Endpoints

#### 1. Process Input

```http

### Endpoints

#### 1. Process Input

```http

```http
POST /process
Authorization: Bearer <token>
Content-Type: application/json

{
  "input": {
    "type": "security_query",
    "content": "How do I scan for open ports?",
    "context": {
      "user_skill_level": 0.3,
      "previous_tools": ["nmap"],
      "session_id": "sess_123"
    }
  },
  "options": {
    "evolution_cycles": 10,
    "population_size": 100,
    "selection_pressure": 0.7
  }
}

Response: 200 OK
{
  "data": {
    "response": {
      "content": "To scan for open ports, you can use nmap...",
      "confidence": 0.92,
      "reasoning_path": [
        "Identified security tool query",
        "User skill level: beginner",
        "Selected educational response pattern"
      ]
    },
    "evolution_metrics": {
      "generations": 8,
      "fitness_score": 0.89,
      "diversity_index": 0.34
    }
  }
}
```text

  "input": {
    "type": "security_query",
    "content": "How do I scan for open ports?",
    "context": {
      "user_skill_level": 0.3,
      "previous_tools": ["nmap"],
      "session_id": "sess_123"
    }
  },
  "options": {
    "evolution_cycles": 10,
    "population_size": 100,
    "selection_pressure": 0.7
  }
}

Response: 200 OK
{
  "data": {
    "response": {
      "content": "To scan for open ports, you can use nmap...",
      "confidence": 0.92,
      "reasoning_path": [
        "Identified security tool query",
        "User skill level: beginner",
        "Selected educational response pattern"
      ]
    },
    "evolution_metrics": {
      "generations": 8,
      "fitness_score": 0.89,
      "diversity_index": 0.34
    }
  }
}

```text
  "input": {
    "type": "security_query",
    "content": "How do I scan for open ports?",
    "context": {
      "user_skill_level": 0.3,
      "previous_tools": ["nmap"],
      "session_id": "sess_123"
    }
  },
  "options": {
    "evolution_cycles": 10,
    "population_size": 100,
    "selection_pressure": 0.7
  }
}

Response: 200 OK
{
  "data": {
    "response": {
      "content": "To scan for open ports, you can use nmap...",
      "confidence": 0.92,
      "reasoning_path": [
        "Identified security tool query",
        "User skill level: beginner",
        "Selected educational response pattern"
      ]
    },
    "evolution_metrics": {
      "generations": 8,
      "fitness_score": 0.89,
      "diversity_index": 0.34
    }
  }
}

```text
      "previous_tools": ["nmap"],
      "session_id": "sess_123"
    }
  },
  "options": {
    "evolution_cycles": 10,
    "population_size": 100,
    "selection_pressure": 0.7
  }
}

Response: 200 OK
{
  "data": {
    "response": {
      "content": "To scan for open ports, you can use nmap...",
      "confidence": 0.92,
      "reasoning_path": [
        "Identified security tool query",
        "User skill level: beginner",
        "Selected educational response pattern"
      ]
    },
    "evolution_metrics": {
      "generations": 8,
      "fitness_score": 0.89,
      "diversity_index": 0.34
    }
  }
}

```text

#### 2. Get Consciousness State

```http
```http

```http

```http
GET /state
Authorization: Bearer <token>

Response: 200 OK
{
  "data": {
    "active_populations": 5,
    "total_neurons": 10000,
    "average_fitness": 0.76,
    "emergence_indicators": {
      "coherence": 0.82,
      "complexity": 0.91,
      "adaptability": 0.88
    },
    "resource_usage": {
      "cpu_percent": 45.2,
      "memory_mb": 2048
    }
  }
}
```text

  "data": {
    "active_populations": 5,
    "total_neurons": 10000,
    "average_fitness": 0.76,
    "emergence_indicators": {
      "coherence": 0.82,
      "complexity": 0.91,
      "adaptability": 0.88
    },
    "resource_usage": {
      "cpu_percent": 45.2,
      "memory_mb": 2048
    }
  }
}

```text
  "data": {
    "active_populations": 5,
    "total_neurons": 10000,
    "average_fitness": 0.76,
    "emergence_indicators": {
      "coherence": 0.82,
      "complexity": 0.91,
      "adaptability": 0.88
    },
    "resource_usage": {
      "cpu_percent": 45.2,
      "memory_mb": 2048
    }
  }
}

```text
      "coherence": 0.82,
      "complexity": 0.91,
      "adaptability": 0.88
    },
    "resource_usage": {
      "cpu_percent": 45.2,
      "memory_mb": 2048
    }
  }
}

```text

## Context Engine API

### Base URL: `http://localhost:8083/api/v1/context`

### Endpoints

#### 1. Update User Context

```http
### Endpoints

#### 1. Update User Context

```http

### Endpoints

#### 1. Update User Context

```http

```http
PUT /users/{user_id}/context
Authorization: Bearer <token>
Content-Type: application/json

{
  "activity": {
    "tool": "metasploit",
    "action": "exploit_completed",
    "success": true,
    "duration_seconds": 300
  },
  "skill_updates": {
    "exploitation": 0.05,
    "metasploit": 0.08
  }
}

Response: 200 OK
{
  "data": {
    "user_id": "user_123",
    "updated_skills": {
      "exploitation": 0.65,
      "metasploit": 0.72
    },
    "achievements_unlocked": [
      {
        "id": "first_exploit",
        "name": "First Successful Exploit",
        "xp_gained": 100
      }
    ],
    "next_recommendations": [
      "Try privilege escalation techniques",
      "Learn about post-exploitation"
    ]
  }
}
```text

  "activity": {
    "tool": "metasploit",
    "action": "exploit_completed",
    "success": true,
    "duration_seconds": 300
  },
  "skill_updates": {
    "exploitation": 0.05,
    "metasploit": 0.08
  }
}

Response: 200 OK
{
  "data": {
    "user_id": "user_123",
    "updated_skills": {
      "exploitation": 0.65,
      "metasploit": 0.72
    },
    "achievements_unlocked": [
      {
        "id": "first_exploit",
        "name": "First Successful Exploit",
        "xp_gained": 100
      }
    ],
    "next_recommendations": [
      "Try privilege escalation techniques",
      "Learn about post-exploitation"
    ]
  }
}

```text
  "activity": {
    "tool": "metasploit",
    "action": "exploit_completed",
    "success": true,
    "duration_seconds": 300
  },
  "skill_updates": {
    "exploitation": 0.05,
    "metasploit": 0.08
  }
}

Response: 200 OK
{
  "data": {
    "user_id": "user_123",
    "updated_skills": {
      "exploitation": 0.65,
      "metasploit": 0.72
    },
    "achievements_unlocked": [
      {
        "id": "first_exploit",
        "name": "First Successful Exploit",
        "xp_gained": 100
      }
    ],
    "next_recommendations": [
      "Try privilege escalation techniques",
      "Learn about post-exploitation"
    ]
  }
}

```text
  },
  "skill_updates": {
    "exploitation": 0.05,
    "metasploit": 0.08
  }
}

Response: 200 OK
{
  "data": {
    "user_id": "user_123",
    "updated_skills": {
      "exploitation": 0.65,
      "metasploit": 0.72
    },
    "achievements_unlocked": [
      {
        "id": "first_exploit",
        "name": "First Successful Exploit",
        "xp_gained": 100
      }
    ],
    "next_recommendations": [
      "Try privilege escalation techniques",
      "Learn about post-exploitation"
    ]
  }
}

```text

#### 2. Get User Profile

```http
```http

```http

```http
GET /users/{user_id}/profile
Authorization: Bearer <token>

Response: 200 OK
{
  "data": {
    "user_id": "user_123",
    "skill_levels": {
      "networking": 0.8,
      "exploitation": 0.65,
      "forensics": 0.4,
      "cryptography": 0.3
    },
    "learning_path": {
      "current_module": "exploitation_basics",
      "progress": 0.75,
      "estimated_completion": "2 hours"
    },
    "preferences": {
      "difficulty": "adaptive",
      "learning_style": "hands-on",
      "notification_level": "moderate"
    },
    "statistics": {
      "total_sessions": 45,
      "total_hours": 67.5,
      "tools_mastered": 12,
      "achievements": 23
    }
  }
}
```text

  "data": {
    "user_id": "user_123",
    "skill_levels": {
      "networking": 0.8,
      "exploitation": 0.65,
      "forensics": 0.4,
      "cryptography": 0.3
    },
    "learning_path": {
      "current_module": "exploitation_basics",
      "progress": 0.75,
      "estimated_completion": "2 hours"
    },
    "preferences": {
      "difficulty": "adaptive",
      "learning_style": "hands-on",
      "notification_level": "moderate"
    },
    "statistics": {
      "total_sessions": 45,
      "total_hours": 67.5,
      "tools_mastered": 12,
      "achievements": 23
    }
  }
}

```text
  "data": {
    "user_id": "user_123",
    "skill_levels": {
      "networking": 0.8,
      "exploitation": 0.65,
      "forensics": 0.4,
      "cryptography": 0.3
    },
    "learning_path": {
      "current_module": "exploitation_basics",
      "progress": 0.75,
      "estimated_completion": "2 hours"
    },
    "preferences": {
      "difficulty": "adaptive",
      "learning_style": "hands-on",
      "notification_level": "moderate"
    },
    "statistics": {
      "total_sessions": 45,
      "total_hours": 67.5,
      "tools_mastered": 12,
      "achievements": 23
    }
  }
}

```text
      "forensics": 0.4,
      "cryptography": 0.3
    },
    "learning_path": {
      "current_module": "exploitation_basics",
      "progress": 0.75,
      "estimated_completion": "2 hours"
    },
    "preferences": {
      "difficulty": "adaptive",
      "learning_style": "hands-on",
      "notification_level": "moderate"
    },
    "statistics": {
      "total_sessions": 45,
      "total_hours": 67.5,
      "tools_mastered": 12,
      "achievements": 23
    }
  }
}

```text

## LM Studio Proxy API

### Base URL: `http://localhost:8084/api/v1/ai`

### Endpoints

#### 1. Generate Completion

```http
### Endpoints

#### 1. Generate Completion

```http

### Endpoints

#### 1. Generate Completion

```http

```http
POST /completions
Authorization: Bearer <token>
Content-Type: application/json

{
  "model": "llama-2-7b-security",
  "messages": [
    {
      "role": "system",
      "content": "You are a cybersecurity tutor..."
    },
    {
      "role": "user",
      "content": "Explain buffer overflow attacks"
    }
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  },
  "context": {
    "user_skill_level": 0.6,
    "topic": "exploitation"
  }
}

Response: 200 OK
{
  "data": {
    "completion": {
      "content": "A buffer overflow attack occurs when...",
      "model": "llama-2-7b-security",
      "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 387,
        "total_tokens": 432
      }
    },
    "metadata": {
      "inference_time_ms": 1250,
      "cache_hit": false
    }
  }
}
```text

  "model": "llama-2-7b-security",
  "messages": [
    {
      "role": "system",
      "content": "You are a cybersecurity tutor..."
    },
    {
      "role": "user",
      "content": "Explain buffer overflow attacks"
    }
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  },
  "context": {
    "user_skill_level": 0.6,
    "topic": "exploitation"
  }
}

Response: 200 OK
{
  "data": {
    "completion": {
      "content": "A buffer overflow attack occurs when...",
      "model": "llama-2-7b-security",
      "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 387,
        "total_tokens": 432
      }
    },
    "metadata": {
      "inference_time_ms": 1250,
      "cache_hit": false
    }
  }
}

```text
  "model": "llama-2-7b-security",
  "messages": [
    {
      "role": "system",
      "content": "You are a cybersecurity tutor..."
    },
    {
      "role": "user",
      "content": "Explain buffer overflow attacks"
    }
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  },
  "context": {
    "user_skill_level": 0.6,
    "topic": "exploitation"
  }
}

Response: 200 OK
{
  "data": {
    "completion": {
      "content": "A buffer overflow attack occurs when...",
      "model": "llama-2-7b-security",
      "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 387,
        "total_tokens": 432
      }
    },
    "metadata": {
      "inference_time_ms": 1250,
      "cache_hit": false
    }
  }
}

```text
    },
    {
      "role": "user",
      "content": "Explain buffer overflow attacks"
    }
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  },
  "context": {
    "user_skill_level": 0.6,
    "topic": "exploitation"
  }
}

Response: 200 OK
{
  "data": {
    "completion": {
      "content": "A buffer overflow attack occurs when...",
      "model": "llama-2-7b-security",
      "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 387,
        "total_tokens": 432
      }
    },
    "metadata": {
      "inference_time_ms": 1250,
      "cache_hit": false
    }
  }
}

```text

#### 2. Stream Completion

```http
```http

```http

```http
POST /completions/stream
Authorization: Bearer <token>
Content-Type: application/json

// Same request body as above with "stream": true

Response: 200 OK (Server-Sent Events)
data: {"token": "A", "index": 0}
data: {"token": " buffer", "index": 1}
data: {"token": " overflow", "index": 2}
...
data: {"done": true, "usage": {...}}
```text

Response: 200 OK (Server-Sent Events)
data: {"token": "A", "index": 0}
data: {"token": " buffer", "index": 1}
data: {"token": " overflow", "index": 2}
...
data: {"done": true, "usage": {...}}

```text

Response: 200 OK (Server-Sent Events)
data: {"token": "A", "index": 0}
data: {"token": " buffer", "index": 1}
data: {"token": " overflow", "index": 2}
...
data: {"done": true, "usage": {...}}

```text
...
data: {"done": true, "usage": {...}}

```text

## Common Data Models

### User Model

```typescript
```typescript

```typescript

```typescript
interface User {
  id: string;
  email: string;
  username: string;
  roles: string[];
  created_at: string;
  last_login: string;
  profile: UserProfile;
}

interface UserProfile {
  skill_levels: Record<string, number>;
  preferences: UserPreferences;
  achievements: Achievement[];
  learning_history: LearningEvent[];
}
```text

  created_at: string;
  last_login: string;
  profile: UserProfile;
}

interface UserProfile {
  skill_levels: Record<string, number>;
  preferences: UserPreferences;
  achievements: Achievement[];
  learning_history: LearningEvent[];
}

```text
  created_at: string;
  last_login: string;
  profile: UserProfile;
}

interface UserProfile {
  skill_levels: Record<string, number>;
  preferences: UserPreferences;
  achievements: Achievement[];
  learning_history: LearningEvent[];
}

```text
interface UserProfile {
  skill_levels: Record<string, number>;
  preferences: UserPreferences;
  achievements: Achievement[];
  learning_history: LearningEvent[];
}

```text

### Service Model

```typescript
```typescript

```typescript

```typescript
interface Service {
  id: string;
  name: string;
  type: 'container' | 'systemd' | 'process';
  status: 'registered' | 'starting' | 'running' | 'stopping' | 'stopped' | 'failed';
  health: 'healthy' | 'unhealthy' | 'unknown';
  config: ServiceConfig;
  metrics: ServiceMetrics;
}

interface ServiceConfig {
  image?: string;
  command?: string[];
  environment: Record<string, string>;
  resources: ResourceLimits;
  dependencies: string[];
  health_check: HealthCheckConfig;
}
```text

  health: 'healthy' | 'unhealthy' | 'unknown';
  config: ServiceConfig;
  metrics: ServiceMetrics;
}

interface ServiceConfig {
  image?: string;
  command?: string[];
  environment: Record<string, string>;
  resources: ResourceLimits;
  dependencies: string[];
  health_check: HealthCheckConfig;
}

```text
  health: 'healthy' | 'unhealthy' | 'unknown';
  config: ServiceConfig;
  metrics: ServiceMetrics;
}

interface ServiceConfig {
  image?: string;
  command?: string[];
  environment: Record<string, string>;
  resources: ResourceLimits;
  dependencies: string[];
  health_check: HealthCheckConfig;
}

```text
interface ServiceConfig {
  image?: string;
  command?: string[];
  environment: Record<string, string>;
  resources: ResourceLimits;
  dependencies: string[];
  health_check: HealthCheckConfig;
}

```text

### Event Model

```typescript
```typescript

```typescript

```typescript
interface Event {
  event_id: string;
  event_type: string;
  timestamp: string;
  source: string;
  data: any;
  metadata: EventMetadata;
}

interface EventMetadata {
  correlation_id?: string;
  user_id?: string;
  trace_id?: string;
  [key: string]: any;
}
```text

  data: any;
  metadata: EventMetadata;
}

interface EventMetadata {
  correlation_id?: string;
  user_id?: string;
  trace_id?: string;
  [key: string]: any;
}

```text
  data: any;
  metadata: EventMetadata;
}

interface EventMetadata {
  correlation_id?: string;
  user_id?: string;
  trace_id?: string;
  [key: string]: any;
}

```text
  correlation_id?: string;
  user_id?: string;
  trace_id?: string;
  [key: string]: any;
}

```text

## Integration Examples

### Python Service Integration

```python
```python

```python

```python
import aiohttp
import asyncio
from typing import Dict, Any

class SynOSClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def start_service(self, service_name: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/orchestrator/services/{service_name}/start"
        async with self.session.post(url) as response:
            return await response.json()

    async def get_context(self, user_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/context/users/{user_id}/profile"
        async with self.session.get(url) as response:
            return await response.json()
```text

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def start_service(self, service_name: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/orchestrator/services/{service_name}/start"
        async with self.session.post(url) as response:
            return await response.json()

    async def get_context(self, user_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/context/users/{user_id}/profile"
        async with self.session.get(url) as response:
            return await response.json()

```text
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def start_service(self, service_name: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/orchestrator/services/{service_name}/start"
        async with self.session.post(url) as response:
            return await response.json()

    async def get_context(self, user_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/context/users/{user_id}/profile"
        async with self.session.get(url) as response:
            return await response.json()

```text
    async def start_service(self, service_name: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/orchestrator/services/{service_name}/start"
        async with self.session.post(url) as response:
            return await response.json()

    async def get_context(self, user_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/context/users/{user_id}/profile"
        async with self.session.get(url) as response:
            return await response.json()

```text

### Go Service Integration

```go
```go

```go

```go
package synos

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type Client struct {
    BaseURL string
    Token   string
    client  *http.Client
}

func (c *Client) StartService(serviceName string) (*ServiceResponse, error) {
    url := fmt.Sprintf("%s/api/v1/orchestrator/services/%s/start", c.BaseURL, serviceName)
    req, err := http.NewRequest("POST", url, nil)
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+c.Token)

    resp, err := c.client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result ServiceResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }

    return &result, nil
}
```text

    "fmt"
    "net/http"
)

type Client struct {
    BaseURL string
    Token   string
    client  *http.Client
}

func (c *Client) StartService(serviceName string) (*ServiceResponse, error) {
    url := fmt.Sprintf("%s/api/v1/orchestrator/services/%s/start", c.BaseURL, serviceName)
    req, err := http.NewRequest("POST", url, nil)
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+c.Token)

    resp, err := c.client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result ServiceResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }

    return &result, nil
}

```text
    "fmt"
    "net/http"
)

type Client struct {
    BaseURL string
    Token   string
    client  *http.Client
}

func (c *Client) StartService(serviceName string) (*ServiceResponse, error) {
    url := fmt.Sprintf("%s/api/v1/orchestrator/services/%s/start", c.BaseURL, serviceName)
    req, err := http.NewRequest("POST", url, nil)
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+c.Token)

    resp, err := c.client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result ServiceResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }

    return &result, nil
}

```text
    BaseURL string
    Token   string
    client  *http.Client
}

func (c *Client) StartService(serviceName string) (*ServiceResponse, error) {
    url := fmt.Sprintf("%s/api/v1/orchestrator/services/%s/start", c.BaseURL, serviceName)
    req, err := http.NewRequest("POST", url, nil)
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+c.Token)

    resp, err := c.client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result ServiceResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, err
    }

    return &result, nil
}

```text

## API Gateway Configuration

All services should be accessible through the Kong API Gateway:

```yaml

```yaml
```yaml

```yaml

## Kong service configuration

services:

  - name: orchestrator

    url: http://service-orchestrator:8080
    routes:

      - name: orchestrator-route

        paths:

          - /api/v1/orchestrator

        strip_path: false
    plugins:

      - name: jwt
      - name: rate-limiting

        config:
          minute: 60
          policy: local

      - name: cors

  - name: consciousness

    url: http://neural-darwinism:8082
    routes:

      - name: consciousness-route

        paths:

          - /api/v1/consciousness

        strip_path: false
    plugins:

      - name: jwt
      - name: request-transformer

        config:
          add:
            headers:

              - X-Service-Name:consciousness

```text
  - name: orchestrator

    url: http://service-orchestrator:8080
    routes:

      - name: orchestrator-route

        paths:

          - /api/v1/orchestrator

        strip_path: false
    plugins:

      - name: jwt
      - name: rate-limiting

        config:
          minute: 60
          policy: local

      - name: cors

  - name: consciousness

    url: http://neural-darwinism:8082
    routes:

      - name: consciousness-route

        paths:

          - /api/v1/consciousness

        strip_path: false
    plugins:

      - name: jwt
      - name: request-transformer

        config:
          add:
            headers:

              - X-Service-Name:consciousness

```text

  - name: orchestrator

    url: http://service-orchestrator:8080
    routes:

      - name: orchestrator-route

        paths:

          - /api/v1/orchestrator

        strip_path: false
    plugins:

      - name: jwt
      - name: rate-limiting

        config:
          minute: 60
          policy: local

      - name: cors

  - name: consciousness

    url: http://neural-darwinism:8082
    routes:

      - name: consciousness-route

        paths:

          - /api/v1/consciousness

        strip_path: false
    plugins:

      - name: jwt
      - name: request-transformer

        config:
          add:
            headers:

              - X-Service-Name:consciousness

```text

      - name: orchestrator-route

        paths:

          - /api/v1/orchestrator

        strip_path: false
    plugins:

      - name: jwt
      - name: rate-limiting

        config:
          minute: 60
          policy: local

      - name: cors

  - name: consciousness

    url: http://neural-darwinism:8082
    routes:

      - name: consciousness-route

        paths:

          - /api/v1/consciousness

        strip_path: false
    plugins:

      - name: jwt
      - name: request-transformer

        config:
          add:
            headers:

              - X-Service-Name:consciousness

```text

## Versioning Strategy

1. **URL Versioning**: `/api/v1/`, `/api/v2/`
2. **Breaking Changes**: New major version
3. **Non-breaking Changes**: Same version
4. **Deprecation**: 6-month notice
5. **Version Header**: `X-API-Version: 1.0.0`

## Rate Limiting

Default rate limits per service:

- Orchestrator: 60 requests/minute
- Security: 100 requests/minute
- AI Services: 30 requests/minute
- Context Engine: 120 requests/minute

## Monitoring Endpoints

All services must expose:

- `/health` - Basic health check
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe
- `/info` - Service information

This specification ensures consistent, secure, and scalable communication between all Syn_OS components.

1. **Non-breaking Changes**: Same version
2. **Deprecation**: 6-month notice
3. **Version Header**: `X-API-Version: 1.0.0`

## Rate Limiting

Default rate limits per service:

- Orchestrator: 60 requests/minute
- Security: 100 requests/minute
- AI Services: 30 requests/minute
- Context Engine: 120 requests/minute

## Monitoring Endpoints

All services must expose:

- `/health` - Basic health check
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe
- `/info` - Service information

This specification ensures consistent, secure, and scalable communication between all Syn_OS components.
1. **Non-breaking Changes**: Same version
2. **Deprecation**: 6-month notice
3. **Version Header**: `X-API-Version: 1.0.0`

## Rate Limiting

Default rate limits per service:

- Orchestrator: 60 requests/minute
- Security: 100 requests/minute
- AI Services: 30 requests/minute
- Context Engine: 120 requests/minute

## Monitoring Endpoints

All services must expose:

- `/health` - Basic health check
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe
- `/info` - Service information

This specification ensures consistent, secure, and scalable communication between all Syn_OS components.

1. **Non-breaking Changes**: Same version
2. **Deprecation**: 6-month notice
3. **Version Header**: `X-API-Version: 1.0.0`

## Rate Limiting

Default rate limits per service:

- Orchestrator: 60 requests/minute
- Security: 100 requests/minute
- AI Services: 30 requests/minute
- Context Engine: 120 requests/minute

## Monitoring Endpoints

All services must expose:

- `/health` - Basic health check
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe
- `/info` - Service information

This specification ensures consistent, secure, and scalable communication between all Syn_OS components.