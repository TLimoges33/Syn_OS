# Syn_OS API Documentation

## Overview

The Syn_OS consciousness-aware infrastructure platform provides comprehensive REST APIs for interacting with the service orchestrator, consciousness system, and user applications. This documentation covers all available endpoints, authentication methods, and integration patterns.

## Base URLs

- **Service Orchestrator**: `http://localhost:8080/api/v1`
- **Consciousness System**: `http://localhost:8081/api/v1`
- **Web Dashboard**: `http://localhost:8083/api/v1`
- **Security Tutor**: `http://localhost:8082/api/v1`

## Authentication

### JWT Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2024-01-01T12:00:00Z",
    "user": {
        "id": "user-uuid",
        "username": "your_username",
        "role": "admin"
    }
}
```

### Refreshing Tokens

```http
POST /api/v1/auth/refresh
Authorization: Bearer <your-jwt-token>
```

## Service Orchestrator API

### Service Management

#### List Services

```http
GET /api/v1/services
Authorization: Bearer <token>
```

**Response:**
```json
{
    "services": [
        {
            "id": "service-uuid",
            "name": "consciousness-system",
            "type": "python",
            "status": "running",
            "health": "healthy",
            "port": 8081,
            "cpu_usage": 15.2,
            "memory_usage": 256.7,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10
}
```

#### Get Service Details

```http
GET /api/v1/services/{service_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
    "id": "service-uuid",
    "name": "consciousness-system",
    "type": "python",
    "status": "running",
    "health": "healthy",
    "configuration": {
        "port": 8081,
        "environment": "production",
        "log_level": "info"
    },
    "metrics": {
        "cpu_usage": 15.2,
        "memory_usage": 256.7,
        "requests_per_second": 45.3,
        "error_rate": 0.01
    },
    "dependencies": ["postgres", "redis", "nats"],
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

#### Create Service

```http
POST /api/v1/services
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "new-service",
    "type": "go",
    "configuration": {
        "port": 8084,
        "environment": "production",
        "replicas": 2
    },
    "dependencies": ["postgres"]
}
```

#### Update Service

```http
PUT /api/v1/services/{service_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "configuration": {
        "replicas": 3,
        "log_level": "debug"
    }
}
```

#### Delete Service

```http
DELETE /api/v1/services/{service_id}
Authorization: Bearer <token>
```

### Service Control

#### Start Service

```http
POST /api/v1/services/{service_id}/start
Authorization: Bearer <token>
```

#### Stop Service

```http
POST /api/v1/services/{service_id}/stop
Authorization: Bearer <token>
```

#### Restart Service

```http
POST /api/v1/services/{service_id}/restart
Authorization: Bearer <token>
```

#### Scale Service

```http
POST /api/v1/services/{service_id}/scale
Authorization: Bearer <token>
Content-Type: application/json

{
    "replicas": 5
}
```

### Health Monitoring

#### System Health

```http
GET /api/v1/health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "services": {
        "orchestrator": "healthy",
        "consciousness": "healthy",
        "postgres": "healthy",
        "redis": "healthy",
        "nats": "healthy"
    },
    "metrics": {
        "total_services": 5,
        "running_services": 5,
        "cpu_usage": 25.3,
        "memory_usage": 1024.5,
        "disk_usage": 45.2
    }
}
```

#### Service Health

```http
GET /api/v1/services/{service_id}/health
Authorization: Bearer <token>
```

### Event Management

#### List Events

```http
GET /api/v1/events?limit=50&offset=0&type=service_started
Authorization: Bearer <token>
```

**Response:**
```json
{
    "events": [
        {
            "id": "event-uuid",
            "type": "service_started",
            "service_id": "service-uuid",
            "data": {
                "service_name": "consciousness-system",
                "port": 8081
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "processed": true
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 50
}
```

#### Create Event

```http
POST /api/v1/events
Authorization: Bearer <token>
Content-Type: application/json

{
    "type": "custom_event",
    "service_id": "service-uuid",
    "data": {
        "message": "Custom event data",
        "priority": "high"
    }
}
```

## Consciousness System API

### Consciousness State

#### Get Consciousness State

```http
GET /api/v1/consciousness/state
Authorization: Bearer <token>
```

**Response:**
```json
{
    "state": "active",
    "awareness_level": 0.85,
    "cognitive_load": 0.42,
    "active_processes": 12,
    "memory_usage": {
        "working_memory": 0.65,
        "long_term_memory": 0.23,
        "episodic_memory": 0.18
    },
    "emotional_state": {
        "valence": 0.7,
        "arousal": 0.4,
        "dominance": 0.8
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Update Consciousness Parameters

```http
PUT /api/v1/consciousness/parameters
Authorization: Bearer <token>
Content-Type: application/json

{
    "learning_rate": 0.01,
    "attention_threshold": 0.5,
    "memory_consolidation_rate": 0.1
}
```

### Cognitive Processes

#### List Active Processes

```http
GET /api/v1/consciousness/processes
Authorization: Bearer <token>
```

**Response:**
```json
{
    "processes": [
        {
            "id": "process-uuid",
            "type": "pattern_recognition",
            "status": "active",
            "priority": 0.8,
            "cpu_usage": 15.2,
            "memory_usage": 64.3,
            "started_at": "2024-01-01T11:30:00Z",
            "data": {
                "input_patterns": 156,
                "recognized_patterns": 142,
                "accuracy": 0.91
            }
        }
    ],
    "total_processes": 1,
    "active_processes": 1
}
```

#### Start Cognitive Process

```http
POST /api/v1/consciousness/processes
Authorization: Bearer <token>
Content-Type: application/json

{
    "type": "learning_session",
    "priority": 0.7,
    "parameters": {
        "dataset": "security_patterns",
        "epochs": 100
    }
}
```

#### Stop Cognitive Process

```http
DELETE /api/v1/consciousness/processes/{process_id}
Authorization: Bearer <token>
```

### Memory Management

#### Query Memory

```http
GET /api/v1/consciousness/memory?type=episodic&limit=10
Authorization: Bearer <token>
```

**Response:**
```json
{
    "memories": [
        {
            "id": "memory-uuid",
            "type": "episodic",
            "content": {
                "event": "security_incident_detected",
                "context": "user_login_anomaly",
                "timestamp": "2024-01-01T11:45:00Z",
                "confidence": 0.92
            },
            "associations": ["security", "anomaly", "user_behavior"],
            "importance": 0.85,
            "created_at": "2024-01-01T11:45:00Z"
        }
    ],
    "total": 1
}
```

#### Store Memory

```http
POST /api/v1/consciousness/memory
Authorization: Bearer <token>
Content-Type: application/json

{
    "type": "semantic",
    "content": {
        "concept": "new_security_pattern",
        "definition": "Pattern description",
        "examples": ["example1", "example2"]
    },
    "associations": ["security", "pattern", "detection"],
    "importance": 0.7
}
```

### Learning and Adaptation

#### Get Learning Status

```http
GET /api/v1/consciousness/learning
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "active",
    "current_session": {
        "id": "session-uuid",
        "type": "reinforcement_learning",
        "progress": 0.65,
        "accuracy": 0.89,
        "started_at": "2024-01-01T10:00:00Z"
    },
    "recent_improvements": [
        {
            "skill": "threat_detection",
            "improvement": 0.12,
            "timestamp": "2024-01-01T11:30:00Z"
        }
    ],
    "adaptation_rate": 0.08
}
```

#### Trigger Learning Session

```http
POST /api/v1/consciousness/learning/session
Authorization: Bearer <token>
Content-Type: application/json

{
    "type": "supervised_learning",
    "dataset": "security_incidents",
    "parameters": {
        "learning_rate": 0.01,
        "batch_size": 32,
        "epochs": 50
    }
}
```

## Web Dashboard API

### Dashboard Data

#### Get Dashboard Overview

```http
GET /api/v1/dashboard/overview
Authorization: Bearer <token>
```

**Response:**
```json
{
    "system_status": "healthy",
    "active_services": 5,
    "consciousness_state": "active",
    "recent_events": 23,
    "alerts": 1,
    "performance": {
        "cpu_usage": 25.3,
        "memory_usage": 1024.5,
        "disk_usage": 45.2,
        "network_io": 156.7
    },
    "consciousness_metrics": {
        "awareness_level": 0.85,
        "cognitive_load": 0.42,
        "learning_progress": 0.78
    }
}
```

#### Get Real-time Metrics

```http
GET /api/v1/dashboard/metrics?timerange=1h
Authorization: Bearer <token>
```

### User Management

#### List Users

```http
GET /api/v1/users
Authorization: Bearer <token>
```

**Response:**
```json
{
    "users": [
        {
            "id": "user-uuid",
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "last_login": "2024-01-01T11:30:00Z",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1
}
```

#### Create User

```http
POST /api/v1/users
Authorization: Bearer <token>
Content-Type: application/json

{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "secure_password",
    "role": "user"
}
```

## Security Tutor API

### Learning Sessions

#### Start Learning Session

```http
POST /api/v1/tutor/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
    "topic": "network_security",
    "difficulty": "intermediate",
    "user_id": "user-uuid"
}
```

**Response:**
```json
{
    "session_id": "session-uuid",
    "topic": "network_security",
    "difficulty": "intermediate",
    "estimated_duration": 1800,
    "consciousness_adaptation": {
        "user_skill_level": 0.65,
        "recommended_approach": "hands_on_practice",
        "personalization_factors": ["visual_learner", "prefers_examples"]
    }
}
```

#### Get Session Progress

```http
GET /api/v1/tutor/sessions/{session_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
    "session_id": "session-uuid",
    "progress": 0.45,
    "current_module": "firewall_configuration",
    "completed_modules": ["network_basics", "threat_identification"],
    "score": 85,
    "time_spent": 810,
    "consciousness_feedback": {
        "engagement_level": 0.8,
        "comprehension_rate": 0.75,
        "suggested_adjustments": ["increase_practical_examples"]
    }
}
```

### Assessment and Feedback

#### Submit Answer

```http
POST /api/v1/tutor/sessions/{session_id}/answer
Authorization: Bearer <token>
Content-Type: application/json

{
    "question_id": "question-uuid",
    "answer": "user_answer_content",
    "time_taken": 45
}
```

#### Get Personalized Feedback

```http
GET /api/v1/tutor/sessions/{session_id}/feedback
Authorization: Bearer <token>
```

## WebSocket APIs

### Real-time Updates

#### Connect to Dashboard Updates

```javascript
const ws = new WebSocket('ws://localhost:8083/ws/dashboard');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Dashboard update:', data);
};
```

#### Connect to Consciousness Stream

```javascript
const ws = new WebSocket('ws://localhost:8081/ws/consciousness');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Consciousness update:', data);
};
```

## Error Handling

### Standard Error Response

```json
{
    "error": {
        "code": "INVALID_REQUEST",
        "message": "The request is invalid",
        "details": "Missing required field: service_name",
        "timestamp": "2024-01-01T12:00:00Z",
        "request_id": "req-uuid"
    }
}
```

### Common Error Codes

- `UNAUTHORIZED` (401): Invalid or missing authentication token
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `INVALID_REQUEST` (400): Malformed request
- `RATE_LIMITED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error
- `SERVICE_UNAVAILABLE` (503): Service temporarily unavailable

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **Read operations**: 100 requests per minute
- **Write operations**: 50 requests per minute
- **WebSocket connections**: 10 concurrent connections per user

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDK and Client Libraries

### Python SDK

```python
from syn_os_sdk import SynOSClient

client = SynOSClient(
    base_url="http://localhost:8080",
    token="your-jwt-token"
)

# List services
services = client.services.list()

# Get consciousness state
state = client.consciousness.get_state()

# Start learning session
session = client.tutor.start_session(
    topic="network_security",
    difficulty="intermediate"
)
```

### JavaScript SDK

```javascript
import { SynOSClient } from 'syn-os-sdk';

const client = new SynOSClient({
    baseUrl: 'http://localhost:8080',
    token: 'your-jwt-token'
});

// List services
const services = await client.services.list();

// Get consciousness state
const state = await client.consciousness.getState();

// Start learning session
const session = await client.tutor.startSession({
    topic: 'network_security',
    difficulty: 'intermediate'
});
```

### Go SDK

```go
package main

import (
    "github.com/your-org/syn-os-go-sdk"
)

func main() {
    client := synos.NewClient(&synos.Config{
        BaseURL: "http://localhost:8080",
        Token:   "your-jwt-token",
    })

    // List services
    services, err := client.Services.List()
    if err != nil {
        log.Fatal(err)
    }

    // Get consciousness state
    state, err := client.Consciousness.GetState()
    if err != nil {
        log.Fatal(err)
    }
}
```

## Integration Examples

### Monitoring Integration

```python
# Prometheus metrics integration
import requests
from prometheus_client import Gauge, Counter

# Define metrics
consciousness_awareness = Gauge('consciousness_awareness_level', 'Current awareness level')
service_health = Gauge('service_health_status', 'Service health status', ['service_name'])

def update_metrics():
    # Get consciousness state
    response = requests.get('http://localhost:8081/api/v1/consciousness/state')
    state = response.json()
    consciousness_awareness.set(state['awareness_level'])
    
    # Get service health
    response = requests.get('http://localhost:8080/api/v1/services')
    services = response.json()['services']
    
    for service in services:
        health_value = 1 if service['health'] == 'healthy' else 0
        service_health.labels(service_name=service['name']).set(health_value)
```

### Alerting Integration

```python
# Slack alerting integration
import requests
import json

def send_alert(message, severity='info'):
    webhook_url = 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    
    color_map = {
        'info': '#36a64f',
        'warning': '#ff9900',
        'error': '#ff0000'
    }
    
    payload = {
        'attachments': [{
            'color': color_map.get(severity, '#36a64f'),
            'text': message,
            'title': f'Syn_OS Alert ({severity.upper()})',
            'timestamp': int(time.time())
        }]
    }
    
    requests.post(webhook_url, data=json.dumps(payload))

# Monitor consciousness state changes
def monitor_consciousness():
    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8081/ws/consciousness')
    
    while True:
        message = ws.recv()
        data = json.loads(message)
        
        if data['awareness_level'] < 0.3:
            send_alert(
                f"Consciousness awareness level critically low: {data['awareness_level']}",
                severity='error'
            )
```

## Best Practices

### Authentication
- Always use HTTPS in production
- Implement token refresh logic
- Store tokens securely
- Use appropriate token expiration times

### Error Handling
- Implement retry logic with exponential backoff
- Handle rate limiting gracefully
- Log errors with sufficient context
- Provide meaningful error messages to users

### Performance
- Use pagination for large datasets
- Implement caching where appropriate
- Use WebSockets for real-time updates
- Monitor API response times

### Security
- Validate all input data
- Use parameterized queries
- Implement proper access controls
- Audit API usage regularly

## Changelog

### v1.0.0 (2024-01-01)
- Initial API release
- Service orchestrator endpoints
- Consciousness system integration
- Authentication and authorization
- WebSocket support for real-time updates

### v1.1.0 (TBD)
- Enhanced consciousness learning APIs
- Improved error handling
- Additional monitoring endpoints
- Performance optimizations

For the latest API updates and changes, refer to the project's changelog and release notes.