# SynapticOS Consciousness System V2 API Reference
## Complete API Documentation

### Table of Contents

1. [REST API Endpoints](#rest-api-endpoints)
2. [WebSocket API](#websocket-api)
3. [Python SDK](#python-sdk)
4. [Event Types Reference](#event-types-reference)
5. [Data Models Reference](#data-models-reference)
6. [Error Codes](#error-codes)
7. [Rate Limiting](#rate-limiting)
8. [Authentication](#authentication)

- --

## REST API Endpoints

### Base URL

- **Production**: `https://api.synapticos.com/v2`
- **Development**: `http://localhost:8080/api/v2`

### Authentication

All API requests require authentication via JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```text

```text

```text
```text

- --

### System Status Endpoints

#### Get System Status

```http
#### Get System Status

```http

#### Get System Status

```http

```http
GET /consciousness/status
```text

```text

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "consciousness_level": 0.8,
  "system_health": "healthy",
  "active_components": 7,
  "uptime_seconds": 86400,
  "version": "2.0.0",
  "environment": "production"
}
```text

  "version": "2.0.0",
  "environment": "production"
}

```text
  "version": "2.0.0",
  "environment": "production"
}

```text
```text

#### Get Component Status

```http
```http

```http

```http
GET /consciousness/components
```text

```text

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "components": [
    {
      "component_id": "neural_darwinism_engine",
      "component_type": "intelligence",
      "state": "healthy",
      "health_score": 0.95,
      "last_heartbeat": "2024-01-15T10:30:00Z",
      "response_time_ms": 45.2,
      "throughput": 150.5,
      "error_rate": 0.001
    }
  ]
}
```text

      "state": "healthy",
      "health_score": 0.95,
      "last_heartbeat": "2024-01-15T10:30:00Z",
      "response_time_ms": 45.2,
      "throughput": 150.5,
      "error_rate": 0.001
    }
  ]
}

```text
      "state": "healthy",
      "health_score": 0.95,
      "last_heartbeat": "2024-01-15T10:30:00Z",
      "response_time_ms": 45.2,
      "throughput": 150.5,
      "error_rate": 0.001
    }
  ]
}

```text
      "error_rate": 0.001
    }
  ]
}

```text

#### Get System Metrics

```http
```http

```http

```http
GET /consciousness/metrics
```text

```text

```text
```text

* *Query Parameters**:

- `start_time` (optional): ISO 8601 timestamp
- `end_time` (optional): ISO 8601 timestamp
- `component_id` (optional): Filter by component

* *Response**:

```json
- `component_id` (optional): Filter by component

* *Response**:

```json

- `component_id` (optional): Filter by component

* *Response**:

```json

```json
{
  "metrics": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "consciousness_level": 0.8,
      "event_processing_rate": 1250.5,
      "neural_evolution_cycles": 42,
      "active_users": 156
    }
  ]
}
```text

      "event_processing_rate": 1250.5,
      "neural_evolution_cycles": 42,
      "active_users": 156
    }
  ]
}

```text
      "event_processing_rate": 1250.5,
      "neural_evolution_cycles": 42,
      "active_users": 156
    }
  ]
}

```text
}

```text

- --

### User Management Endpoints

#### Create User Context

```http
#### Create User Context

```http

#### Create User Context

```http

```http
POST /users/{user_id}/context
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "skill_levels": {
    "python": "intermediate",
    "security": "beginner",
    "networking": "advanced"
  },
  "learning_preferences": {
    "pace": "normal",
    "difficulty": "adaptive",
    "visual_aids": true,
    "hands_on_preference": 0.8
  },
  "goals": [
    "Complete Python certification",
    "Improve security awareness"
  ]
}
```text

  },
  "learning_preferences": {
    "pace": "normal",
    "difficulty": "adaptive",
    "visual_aids": true,
    "hands_on_preference": 0.8
  },
  "goals": [
    "Complete Python certification",
    "Improve security awareness"
  ]
}

```text
  },
  "learning_preferences": {
    "pace": "normal",
    "difficulty": "adaptive",
    "visual_aids": true,
    "hands_on_preference": 0.8
  },
  "goals": [
    "Complete Python certification",
    "Improve security awareness"
  ]
}

```text
    "hands_on_preference": 0.8
  },
  "goals": [
    "Complete Python certification",
    "Improve security awareness"
  ]
}

```text

* *Response**:

```json
```json

```json

```json
{
  "user_id": "user123",
  "context_created": true,
  "initial_consciousness_level": 0.6,
  "recommended_starting_modules": [
    "python_intermediate_1",
    "security_basics_1"
  ]
}
```text

    "python_intermediate_1",
    "security_basics_1"
  ]
}

```text
    "python_intermediate_1",
    "security_basics_1"
  ]
}

```text
```text

#### Get User Context

```http
```http

```http

```http
GET /users/{user_id}/context
```text

```text

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "user_id": "user123",
  "created_at": "2024-01-15T09:00:00Z",
  "last_updated": "2024-01-15T10:30:00Z",
  "skill_levels": {
    "python": "intermediate",
    "security": "beginner"
  },
  "current_consciousness_level": 0.75,
  "total_time_spent": 7200,
  "achievements": [
    "first_module_complete",
    "security_awareness_bronze"
  ],
  "current_session": {
    "session_id": "session456",
    "start_time": "2024-01-15T10:00:00Z",
    "current_module": "python_functions",
    "progress": 0.65
  }
}
```text

    "python": "intermediate",
    "security": "beginner"
  },
  "current_consciousness_level": 0.75,
  "total_time_spent": 7200,
  "achievements": [
    "first_module_complete",
    "security_awareness_bronze"
  ],
  "current_session": {
    "session_id": "session456",
    "start_time": "2024-01-15T10:00:00Z",
    "current_module": "python_functions",
    "progress": 0.65
  }
}

```text
    "python": "intermediate",
    "security": "beginner"
  },
  "current_consciousness_level": 0.75,
  "total_time_spent": 7200,
  "achievements": [
    "first_module_complete",
    "security_awareness_bronze"
  ],
  "current_session": {
    "session_id": "session456",
    "start_time": "2024-01-15T10:00:00Z",
    "current_module": "python_functions",
    "progress": 0.65
  }
}

```text
  "achievements": [
    "first_module_complete",
    "security_awareness_bronze"
  ],
  "current_session": {
    "session_id": "session456",
    "start_time": "2024-01-15T10:00:00Z",
    "current_module": "python_functions",
    "progress": 0.65
  }
}

```text

#### Update User Progress

```http
```http

```http

```http
POST /users/{user_id}/progress
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "module_id": "python_functions",
  "progress_percentage": 75.5,
  "time_spent_seconds": 1800,
  "exercises_completed": 8,
  "exercises_total": 12,
  "score": 0.85,
  "difficulty_rating": "appropriate"
}
```text

  "exercises_total": 12,
  "score": 0.85,
  "difficulty_rating": "appropriate"
}

```text
  "exercises_total": 12,
  "score": 0.85,
  "difficulty_rating": "appropriate"
}

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "progress_updated": true,
  "new_skill_level": "intermediate",
  "consciousness_adaptation": {
    "level_change": 0.05,
    "reason": "consistent_progress"
  },
  "next_recommendations": [
    "python_advanced_functions",
    "python_error_handling"
  ]
}
```text

    "reason": "consistent_progress"
  },
  "next_recommendations": [
    "python_advanced_functions",
    "python_error_handling"
  ]
}

```text
    "reason": "consistent_progress"
  },
  "next_recommendations": [
    "python_advanced_functions",
    "python_error_handling"
  ]
}

```text
  ]
}

```text

- --

### Learning Endpoints

#### Get Learning Recommendations

```http
#### Get Learning Recommendations

```http

#### Get Learning Recommendations

```http

```http
GET /users/{user_id}/recommendations
```text

```text

```text
```text

* *Query Parameters**:

- `domain` (optional): Filter by domain (python, security, networking)
- `difficulty` (optional): Filter by difficulty level
- `limit` (optional): Number of recommendations (default: 10)

* *Response**:

```json
- `limit` (optional): Number of recommendations (default: 10)

* *Response**:

```json

- `limit` (optional): Number of recommendations (default: 10)

* *Response**:

```json

```json
{
  "recommendations": [
    {
      "module_id": "python_advanced_functions",
      "title": "Advanced Python Functions",
      "difficulty": "intermediate",
      "estimated_duration": 3600,
      "consciousness_optimized": true,
      "relevance_score": 0.92,
      "prerequisites": ["python_basic_functions"],
      "learning_objectives": [
        "Master lambda functions",
        "Understand decorators",
        "Use higher-order functions"
      ]
    }
  ],
  "learning_path": {
    "current_position": 3,
    "total_modules": 15,
    "estimated_completion": "2024-02-15T00:00:00Z"
  }
}
```text

      "difficulty": "intermediate",
      "estimated_duration": 3600,
      "consciousness_optimized": true,
      "relevance_score": 0.92,
      "prerequisites": ["python_basic_functions"],
      "learning_objectives": [
        "Master lambda functions",
        "Understand decorators",
        "Use higher-order functions"
      ]
    }
  ],
  "learning_path": {
    "current_position": 3,
    "total_modules": 15,
    "estimated_completion": "2024-02-15T00:00:00Z"
  }
}

```text
      "difficulty": "intermediate",
      "estimated_duration": 3600,
      "consciousness_optimized": true,
      "relevance_score": 0.92,
      "prerequisites": ["python_basic_functions"],
      "learning_objectives": [
        "Master lambda functions",
        "Understand decorators",
        "Use higher-order functions"
      ]
    }
  ],
  "learning_path": {
    "current_position": 3,
    "total_modules": 15,
    "estimated_completion": "2024-02-15T00:00:00Z"
  }
}

```text
      "learning_objectives": [
        "Master lambda functions",
        "Understand decorators",
        "Use higher-order functions"
      ]
    }
  ],
  "learning_path": {
    "current_position": 3,
    "total_modules": 15,
    "estimated_completion": "2024-02-15T00:00:00Z"
  }
}

```text

#### Start Learning Session

```http
```http

```http

```http
POST /users/{user_id}/sessions
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "module_id": "python_advanced_functions",
  "learning_mode": "focused",
  "consciousness_level": 0.8
}
```text

```text

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "session_id": "session789",
  "session_started": true,
  "adaptive_content": {
    "difficulty_level": "intermediate_plus",
    "content_style": "hands_on",
    "estimated_duration": 3600
  },
  "consciousness_adaptations": [
    "increased_example_complexity",
    "added_practical_exercises"
  ]
}
```text

    "content_style": "hands_on",
    "estimated_duration": 3600
  },
  "consciousness_adaptations": [
    "increased_example_complexity",
    "added_practical_exercises"
  ]
}

```text
    "content_style": "hands_on",
    "estimated_duration": 3600
  },
  "consciousness_adaptations": [
    "increased_example_complexity",
    "added_practical_exercises"
  ]
}

```text
    "added_practical_exercises"
  ]
}

```text

#### End Learning Session

```http
```http

```http

```http
POST /users/{user_id}/sessions/{session_id}/end
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "completion_status": "completed",
  "final_score": 0.88,
  "feedback": {
    "difficulty": "appropriate",
    "engagement": "high",
    "content_quality": "excellent"
  }
}
```text

    "engagement": "high",
    "content_quality": "excellent"
  }
}

```text
    "engagement": "high",
    "content_quality": "excellent"
  }
}

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "session_ended": true,
  "session_summary": {
    "duration_seconds": 3420,
    "modules_completed": 1,
    "exercises_completed": 12,
    "average_score": 0.88
  },
  "skill_updates": {
    "python": "advanced"
  },
  "achievements_unlocked": [
    "python_functions_master"
  ]
}
```text

    "exercises_completed": 12,
    "average_score": 0.88
  },
  "skill_updates": {
    "python": "advanced"
  },
  "achievements_unlocked": [
    "python_functions_master"
  ]
}

```text
    "exercises_completed": 12,
    "average_score": 0.88
  },
  "skill_updates": {
    "python": "advanced"
  },
  "achievements_unlocked": [
    "python_functions_master"
  ]
}

```text
  },
  "achievements_unlocked": [
    "python_functions_master"
  ]
}

```text

- --

### Security Assessment Endpoints

#### Generate Security Scenario

```http
#### Generate Security Scenario

```http

#### Generate Security Scenario

```http

```http
POST /security/scenarios/generate
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "user_id": "user123",
  "scenario_type": "phishing",
  "difficulty": "intermediate",
  "context": {
    "user_role": "developer",
    "company_type": "tech_startup"
  }
}
```text

    "user_role": "developer",
    "company_type": "tech_startup"
  }
}

```text
    "user_role": "developer",
    "company_type": "tech_startup"
  }
}

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "scenario_id": "scenario456",
  "scenario_type": "phishing",
  "title": "Suspicious Email Assessment",
  "description": "Evaluate the following email for potential phishing indicators",
  "content": {
    "email_subject": "Urgent: Account Verification Required",
    "email_body": "...",
    "sender_address": "security@fake-bank.com",
    "attachments": ["verification_form.pdf"]
  },
  "assessment_criteria": [
    "sender_authenticity",
    "urgency_tactics",
    "suspicious_links",
    "attachment_safety"
  ],
  "time_limit_seconds": 300
}
```text

  "content": {
    "email_subject": "Urgent: Account Verification Required",
    "email_body": "...",
    "sender_address": "security@fake-bank.com",
    "attachments": ["verification_form.pdf"]
  },
  "assessment_criteria": [
    "sender_authenticity",
    "urgency_tactics",
    "suspicious_links",
    "attachment_safety"
  ],
  "time_limit_seconds": 300
}

```text
  "content": {
    "email_subject": "Urgent: Account Verification Required",
    "email_body": "...",
    "sender_address": "security@fake-bank.com",
    "attachments": ["verification_form.pdf"]
  },
  "assessment_criteria": [
    "sender_authenticity",
    "urgency_tactics",
    "suspicious_links",
    "attachment_safety"
  ],
  "time_limit_seconds": 300
}

```text
  },
  "assessment_criteria": [
    "sender_authenticity",
    "urgency_tactics",
    "suspicious_links",
    "attachment_safety"
  ],
  "time_limit_seconds": 300
}

```text

#### Submit Security Assessment

```http
```http

```http

```http
POST /security/scenarios/{scenario_id}/assess
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "user_id": "user123",
  "assessment": {
    "threat_detected": true,
    "threat_type": "phishing",
    "confidence": 0.9,
    "indicators_identified": [
      "suspicious_sender_domain",
      "urgency_language",
      "request_for_credentials"
    ],
    "recommended_action": "delete_and_report",
    "reasoning": "Multiple phishing indicators present including suspicious domain and urgency tactics"
  },
  "time_taken_seconds": 180
}
```text

    "confidence": 0.9,
    "indicators_identified": [
      "suspicious_sender_domain",
      "urgency_language",
      "request_for_credentials"
    ],
    "recommended_action": "delete_and_report",
    "reasoning": "Multiple phishing indicators present including suspicious domain and urgency tactics"
  },
  "time_taken_seconds": 180
}

```text
    "confidence": 0.9,
    "indicators_identified": [
      "suspicious_sender_domain",
      "urgency_language",
      "request_for_credentials"
    ],
    "recommended_action": "delete_and_report",
    "reasoning": "Multiple phishing indicators present including suspicious domain and urgency tactics"
  },
  "time_taken_seconds": 180
}

```text
    ],
    "recommended_action": "delete_and_report",
    "reasoning": "Multiple phishing indicators present including suspicious domain and urgency tactics"
  },
  "time_taken_seconds": 180
}

```text

* *Response**:

```json
```json

```json

```json
{
  "assessment_id": "assessment789",
  "score": 0.92,
  "feedback": {
    "overall": "Excellent threat detection and analysis",
    "strengths": [
      "Correctly identified phishing indicators",
      "Appropriate recommended action",
      "Good reasoning provided"
    ],
    "improvements": [
      "Could have noted the suspicious attachment"
    ]
  },
  "consciousness_adaptation": {
    "difficulty_adjustment": "increase_slightly",
    "next_scenario_type": "advanced_phishing"
  },
  "security_awareness_update": {
    "previous_level": 0.7,
    "new_level": 0.75,
    "improvement": 0.05
  }
}
```text

    "strengths": [
      "Correctly identified phishing indicators",
      "Appropriate recommended action",
      "Good reasoning provided"
    ],
    "improvements": [
      "Could have noted the suspicious attachment"
    ]
  },
  "consciousness_adaptation": {
    "difficulty_adjustment": "increase_slightly",
    "next_scenario_type": "advanced_phishing"
  },
  "security_awareness_update": {
    "previous_level": 0.7,
    "new_level": 0.75,
    "improvement": 0.05
  }
}

```text
    "strengths": [
      "Correctly identified phishing indicators",
      "Appropriate recommended action",
      "Good reasoning provided"
    ],
    "improvements": [
      "Could have noted the suspicious attachment"
    ]
  },
  "consciousness_adaptation": {
    "difficulty_adjustment": "increase_slightly",
    "next_scenario_type": "advanced_phishing"
  },
  "security_awareness_update": {
    "previous_level": 0.7,
    "new_level": 0.75,
    "improvement": 0.05
  }
}

```text
    "improvements": [
      "Could have noted the suspicious attachment"
    ]
  },
  "consciousness_adaptation": {
    "difficulty_adjustment": "increase_slightly",
    "next_scenario_type": "advanced_phishing"
  },
  "security_awareness_update": {
    "previous_level": 0.7,
    "new_level": 0.75,
    "improvement": 0.05
  }
}

```text

- --

### Neural Darwinism Endpoints

#### Get Population Statistics

```http
#### Get Population Statistics

```http

#### Get Population Statistics

```http

```http
GET /neural/populations
```text

```text

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "populations": [
    {
      "population_id": "executive",
      "size": 1000,
      "specialization": "executive_control",
      "fitness_average": 0.78,
      "diversity_index": 0.65,
      "generation": 142,
      "evolution_cycles": 1420,
      "last_evolution": "2024-01-15T10:25:00Z",
      "performance_metrics": {
        "decision_accuracy": 0.82,
        "response_time": 45.2,
        "adaptation_rate": 0.15
      }
    }
  ],
  "overall_consciousness_level": 0.8,
  "system_intelligence_score": 0.85
}
```text

      "specialization": "executive_control",
      "fitness_average": 0.78,
      "diversity_index": 0.65,
      "generation": 142,
      "evolution_cycles": 1420,
      "last_evolution": "2024-01-15T10:25:00Z",
      "performance_metrics": {
        "decision_accuracy": 0.82,
        "response_time": 45.2,
        "adaptation_rate": 0.15
      }
    }
  ],
  "overall_consciousness_level": 0.8,
  "system_intelligence_score": 0.85
}

```text
      "specialization": "executive_control",
      "fitness_average": 0.78,
      "diversity_index": 0.65,
      "generation": 142,
      "evolution_cycles": 1420,
      "last_evolution": "2024-01-15T10:25:00Z",
      "performance_metrics": {
        "decision_accuracy": 0.82,
        "response_time": 45.2,
        "adaptation_rate": 0.15
      }
    }
  ],
  "overall_consciousness_level": 0.8,
  "system_intelligence_score": 0.85
}

```text
      "last_evolution": "2024-01-15T10:25:00Z",
      "performance_metrics": {
        "decision_accuracy": 0.82,
        "response_time": 45.2,
        "adaptation_rate": 0.15
      }
    }
  ],
  "overall_consciousness_level": 0.8,
  "system_intelligence_score": 0.85
}

```text

#### Trigger Evolution Cycle

```http
```http

```http

```http
POST /neural/populations/{population_id}/evolve
```text

```text

```text
```text

* *Request Body**:

```json
```json

```json

```json
{
  "fitness_feedback": {
    "user_satisfaction": 0.9,
    "task_completion": 0.85,
    "response_accuracy": 0.88
  },
  "evolution_pressure": 0.3
}
```text

  },
  "evolution_pressure": 0.3
}

```text
  },
  "evolution_pressure": 0.3
}

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "evolution_triggered": true,
  "evolution_id": "evolution123",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "expected_improvements": [
    "increased_decision_accuracy",
    "reduced_response_time",
    "better_user_adaptation"
  ]
}
```text

    "increased_decision_accuracy",
    "reduced_response_time",
    "better_user_adaptation"
  ]
}

```text
    "increased_decision_accuracy",
    "reduced_response_time",
    "better_user_adaptation"
  ]
}

```text

```text

- --

## WebSocket API

### Connection

```javascript
### Connection

```javascript

### Connection

```javascript

```javascript
const ws = new WebSocket('wss://api.synapticos.com/v2/ws');

// Authentication
ws.onopen = function() {
    ws.send(JSON.stringify({
        type: 'authenticate',
        token: 'your_jwt_token'
    }));
};
```text

        type: 'authenticate',
        token: 'your_jwt_token'
    }));
};

```text
        type: 'authenticate',
        token: 'your_jwt_token'
    }));
};

```text
```text

### Real-time Events

#### Consciousness Level Updates

```json
```json

```json

```json
{
  "type": "consciousness_update",
  "data": {
    "consciousness_level": 0.82,
    "change": 0.02,
    "reason": "user_engagement_increase",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```text

    "reason": "user_engagement_increase",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

```text
    "reason": "user_engagement_increase",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

```text
```text

#### Learning Progress Updates

```json
```json

```json

```json
{
  "type": "learning_progress",
  "data": {
    "user_id": "user123",
    "session_id": "session456",
    "module_id": "python_functions",
    "progress": 0.75,
    "time_spent": 1800,
    "current_exercise": 8,
    "total_exercises": 12
  }
}
```text

    "module_id": "python_functions",
    "progress": 0.75,
    "time_spent": 1800,
    "current_exercise": 8,
    "total_exercises": 12
  }
}

```text
    "module_id": "python_functions",
    "progress": 0.75,
    "time_spent": 1800,
    "current_exercise": 8,
    "total_exercises": 12
  }
}

```text
  }
}

```text

#### System Alerts

```json
```json

```json

```json
{
  "type": "system_alert",
  "data": {
    "alert_type": "performance_degradation",
    "severity": "medium",
    "component": "neural_darwinism_engine",
    "message": "Response time increased above threshold",
    "timestamp": "2024-01-15T10:30:00Z",
    "recommended_action": "check_system_resources"
  }
}
```text

    "component": "neural_darwinism_engine",
    "message": "Response time increased above threshold",
    "timestamp": "2024-01-15T10:30:00Z",
    "recommended_action": "check_system_resources"
  }
}

```text
    "component": "neural_darwinism_engine",
    "message": "Response time increased above threshold",
    "timestamp": "2024-01-15T10:30:00Z",
    "recommended_action": "check_system_resources"
  }
}

```text
}

```text

- --

## Python SDK

### Installation

```bash
### Installation

```bash

### Installation

```bash

```bash
pip install synapticos-consciousness-sdk
```text

```text

```text
```text

### Basic Usage

```python
```python

```python

```python
from synapticos import ConsciousnessClient

## Initialize client

client = ConsciousnessClient(
    api_url="https://api.synapticos.com/v2",
    api_key="your_api_key"
)

## Get system status

status = await client.get_system_status()
print(f"Consciousness level: {status.consciousness_level}")

## Create user context

user_context = await client.create_user_context(
    user_id="user123",
    skill_levels={"python": "intermediate"},
    learning_preferences={"pace": "normal"}
)

## Start learning session

session = await client.start_learning_session(
    user_id="user123",
    module_id="python_functions"
)

## Update progress

progress = await client.update_progress(
    user_id="user123",
    session_id=session.session_id,
    progress_data={
        "progress_percentage": 75.0,
        "time_spent_seconds": 1800,
        "score": 0.85
    }
)
```text

    api_url="https://api.synapticos.com/v2",
    api_key="your_api_key"
)

## Get system status

status = await client.get_system_status()
print(f"Consciousness level: {status.consciousness_level}")

## Create user context

user_context = await client.create_user_context(
    user_id="user123",
    skill_levels={"python": "intermediate"},
    learning_preferences={"pace": "normal"}
)

## Start learning session

session = await client.start_learning_session(
    user_id="user123",
    module_id="python_functions"
)

## Update progress

progress = await client.update_progress(
    user_id="user123",
    session_id=session.session_id,
    progress_data={
        "progress_percentage": 75.0,
        "time_spent_seconds": 1800,
        "score": 0.85
    }
)

```text
    api_url="https://api.synapticos.com/v2",
    api_key="your_api_key"
)

## Get system status

status = await client.get_system_status()
print(f"Consciousness level: {status.consciousness_level}")

## Create user context

user_context = await client.create_user_context(
    user_id="user123",
    skill_levels={"python": "intermediate"},
    learning_preferences={"pace": "normal"}
)

## Start learning session

session = await client.start_learning_session(
    user_id="user123",
    module_id="python_functions"
)

## Update progress

progress = await client.update_progress(
    user_id="user123",
    session_id=session.session_id,
    progress_data={
        "progress_percentage": 75.0,
        "time_spent_seconds": 1800,
        "score": 0.85
    }
)

```text

status = await client.get_system_status()
print(f"Consciousness level: {status.consciousness_level}")

## Create user context

user_context = await client.create_user_context(
    user_id="user123",
    skill_levels={"python": "intermediate"},
    learning_preferences={"pace": "normal"}
)

## Start learning session

session = await client.start_learning_session(
    user_id="user123",
    module_id="python_functions"
)

## Update progress

progress = await client.update_progress(
    user_id="user123",
    session_id=session.session_id,
    progress_data={
        "progress_percentage": 75.0,
        "time_spent_seconds": 1800,
        "score": 0.85
    }
)

```text

### Advanced Usage

```python

```python
```python

```python

## Real-time event streaming

async def handle_consciousness_update(event):
    print(f"Consciousness level: {event.consciousness_level}")

## Subscribe to events

await client.subscribe_to_events(
    event_types=["consciousness_update", "learning_progress"],
    handler=handle_consciousness_update
)

## Generate security scenario

scenario = await client.generate_security_scenario(
    user_id="user123",
    scenario_type="phishing",
    difficulty="intermediate"
)

## Submit assessment

assessment = await client.submit_security_assessment(
    scenario_id=scenario.scenario_id,
    user_id="user123",
    assessment_data={
        "threat_detected": True,
        "threat_type": "phishing",
        "confidence": 0.9
    }
)
```text

## Subscribe to events

await client.subscribe_to_events(
    event_types=["consciousness_update", "learning_progress"],
    handler=handle_consciousness_update
)

## Generate security scenario

scenario = await client.generate_security_scenario(
    user_id="user123",
    scenario_type="phishing",
    difficulty="intermediate"
)

## Submit assessment

assessment = await client.submit_security_assessment(
    scenario_id=scenario.scenario_id,
    user_id="user123",
    assessment_data={
        "threat_detected": True,
        "threat_type": "phishing",
        "confidence": 0.9
    }
)

```text

## Subscribe to events

await client.subscribe_to_events(
    event_types=["consciousness_update", "learning_progress"],
    handler=handle_consciousness_update
)

## Generate security scenario

scenario = await client.generate_security_scenario(
    user_id="user123",
    scenario_type="phishing",
    difficulty="intermediate"
)

## Submit assessment

assessment = await client.submit_security_assessment(
    scenario_id=scenario.scenario_id,
    user_id="user123",
    assessment_data={
        "threat_detected": True,
        "threat_type": "phishing",
        "confidence": 0.9
    }
)

```text
    handler=handle_consciousness_update
)

## Generate security scenario

scenario = await client.generate_security_scenario(
    user_id="user123",
    scenario_type="phishing",
    difficulty="intermediate"
)

## Submit assessment

assessment = await client.submit_security_assessment(
    scenario_id=scenario.scenario_id,
    user_id="user123",
    assessment_data={
        "threat_detected": True,
        "threat_type": "phishing",
        "confidence": 0.9
    }
)

```text

- --

## Event Types Reference

### Core System Events

- `CONSCIOUSNESS_UPDATE`: Consciousness level changes
- `SYSTEM_STARTUP`: System initialization complete
- `SYSTEM_SHUTDOWN`: System shutdown initiated
- `COMPONENT_REGISTERED`: New component registered
- `COMPONENT_UNREGISTERED`: Component unregistered
- `HEALTH_CHECK`: Component health status update

### Learning Events

- `LEARNING_SESSION_START`: Learning session initiated
- `LEARNING_SESSION_END`: Learning session completed
- `LEARNING_PROGRESS`: Progress update within session
- `SKILL_ASSESSMENT`: Skill level assessment completed
- `MODULE_COMPLETED`: Learning module finished
- `ACHIEVEMENT_UNLOCKED`: New achievement earned

### Security Events

- `SECURITY_THREAT_DETECTED`: Security threat identified
- `SECURITY_ASSESSMENT`: Security assessment completed
- `SECURITY_TRAINING_COMPLETE`: Security training finished
- `THREAT_INTELLIGENCE_UPDATE`: New threat data available

### Performance Events

- `PERFORMANCE_UPDATE`: Performance metrics update
- `RESOURCE_ALERT`: Resource usage alert
- `NEURAL_EVOLUTION_COMPLETE`: Neural evolution cycle finished

- --

## Data Models Reference

### ConsciousnessState

```typescript
### Core System Events

- `CONSCIOUSNESS_UPDATE`: Consciousness level changes
- `SYSTEM_STARTUP`: System initialization complete
- `SYSTEM_SHUTDOWN`: System shutdown initiated
- `COMPONENT_REGISTERED`: New component registered
- `COMPONENT_UNREGISTERED`: Component unregistered
- `HEALTH_CHECK`: Component health status update

### Learning Events

- `LEARNING_SESSION_START`: Learning session initiated
- `LEARNING_SESSION_END`: Learning session completed
- `LEARNING_PROGRESS`: Progress update within session
- `SKILL_ASSESSMENT`: Skill level assessment completed
- `MODULE_COMPLETED`: Learning module finished
- `ACHIEVEMENT_UNLOCKED`: New achievement earned

### Security Events

- `SECURITY_THREAT_DETECTED`: Security threat identified
- `SECURITY_ASSESSMENT`: Security assessment completed
- `SECURITY_TRAINING_COMPLETE`: Security training finished
- `THREAT_INTELLIGENCE_UPDATE`: New threat data available

### Performance Events

- `PERFORMANCE_UPDATE`: Performance metrics update
- `RESOURCE_ALERT`: Resource usage alert
- `NEURAL_EVOLUTION_COMPLETE`: Neural evolution cycle finished

- --

## Data Models Reference

### ConsciousnessState

```typescript

### Core System Events

- `CONSCIOUSNESS_UPDATE`: Consciousness level changes
- `SYSTEM_STARTUP`: System initialization complete
- `SYSTEM_SHUTDOWN`: System shutdown initiated
- `COMPONENT_REGISTERED`: New component registered
- `COMPONENT_UNREGISTERED`: Component unregistered
- `HEALTH_CHECK`: Component health status update

### Learning Events

- `LEARNING_SESSION_START`: Learning session initiated
- `LEARNING_SESSION_END`: Learning session completed
- `LEARNING_PROGRESS`: Progress update within session
- `SKILL_ASSESSMENT`: Skill level assessment completed
- `MODULE_COMPLETED`: Learning module finished
- `ACHIEVEMENT_UNLOCKED`: New achievement earned

### Security Events

- `SECURITY_THREAT_DETECTED`: Security threat identified
- `SECURITY_ASSESSMENT`: Security assessment completed
- `SECURITY_TRAINING_COMPLETE`: Security training finished
- `THREAT_INTELLIGENCE_UPDATE`: New threat data available

### Performance Events

- `PERFORMANCE_UPDATE`: Performance metrics update
- `RESOURCE_ALERT`: Resource usage alert
- `NEURAL_EVOLUTION_COMPLETE`: Neural evolution cycle finished

- --

## Data Models Reference

### ConsciousnessState

```typescript

- `SYSTEM_SHUTDOWN`: System shutdown initiated
- `COMPONENT_REGISTERED`: New component registered
- `COMPONENT_UNREGISTERED`: Component unregistered
- `HEALTH_CHECK`: Component health status update

### Learning Events

- `LEARNING_SESSION_START`: Learning session initiated
- `LEARNING_SESSION_END`: Learning session completed
- `LEARNING_PROGRESS`: Progress update within session
- `SKILL_ASSESSMENT`: Skill level assessment completed
- `MODULE_COMPLETED`: Learning module finished
- `ACHIEVEMENT_UNLOCKED`: New achievement earned

### Security Events

- `SECURITY_THREAT_DETECTED`: Security threat identified
- `SECURITY_ASSESSMENT`: Security assessment completed
- `SECURITY_TRAINING_COMPLETE`: Security training finished
- `THREAT_INTELLIGENCE_UPDATE`: New threat data available

### Performance Events

- `PERFORMANCE_UPDATE`: Performance metrics update
- `RESOURCE_ALERT`: Resource usage alert
- `NEURAL_EVOLUTION_COMPLETE`: Neural evolution cycle finished

- --

## Data Models Reference

### ConsciousnessState

```typescript
interface ConsciousnessState {
  consciousness_level: number;        // 0.0 to 1.0
  emergence_strength: number;         // 0.0 to 1.0
  adaptation_rate: number;           // 0.0 to 1.0
  neural_populations: PopulationState[];
  user_contexts: UserContextState[];
  timestamp: string;                 // ISO 8601
  version: string;
  checksum: string;
}
```text

  user_contexts: UserContextState[];
  timestamp: string;                 // ISO 8601
  version: string;
  checksum: string;
}

```text
  user_contexts: UserContextState[];
  timestamp: string;                 // ISO 8601
  version: string;
  checksum: string;
}

```text

```text

### UserContextState

```typescript
```typescript

```typescript

```typescript
interface UserContextState {
  user_id: string;
  created_at: string;               // ISO 8601
  last_updated: string;             // ISO 8601
  skill_levels: Record<string, SkillLevel>;
  learning_preferences: Record<string, any>;
  current_consciousness_level: number;
  total_time_spent: number;         // seconds
  achievements: string[];
  current_session?: SessionState;
}
```text

  learning_preferences: Record<string, any>;
  current_consciousness_level: number;
  total_time_spent: number;         // seconds
  achievements: string[];
  current_session?: SessionState;
}

```text
  learning_preferences: Record<string, any>;
  current_consciousness_level: number;
  total_time_spent: number;         // seconds
  achievements: string[];
  current_session?: SessionState;
}

```text
}

```text

### PopulationState

```typescript
```typescript

```typescript

```typescript
interface PopulationState {
  population_id: string;
  size: number;
  specialization: string;
  fitness_average: number;          // 0.0 to 1.0
  diversity_index: number;          // 0.0 to 1.0
  generation: number;
  evolution_cycles: number;
  last_evolution: string;           // ISO 8601
  performance_metrics: Record<string, number>;
}
```text

  diversity_index: number;          // 0.0 to 1.0
  generation: number;
  evolution_cycles: number;
  last_evolution: string;           // ISO 8601
  performance_metrics: Record<string, number>;
}

```text
  diversity_index: number;          // 0.0 to 1.0
  generation: number;
  evolution_cycles: number;
  last_evolution: string;           // ISO 8601
  performance_metrics: Record<string, number>;
}

```text
}

```text

### SecurityScenario

```typescript
```typescript

```typescript

```typescript
interface SecurityScenario {
  scenario_id: string;
  scenario_type: string;
  title: string;
  description: string;
  difficulty: string;
  content: Record<string, any>;
  assessment_criteria: string[];
  time_limit_seconds?: number;
  created_at: string;               // ISO 8601
}
```text

  difficulty: string;
  content: Record<string, any>;
  assessment_criteria: string[];
  time_limit_seconds?: number;
  created_at: string;               // ISO 8601
}

```text
  difficulty: string;
  content: Record<string, any>;
  assessment_criteria: string[];
  time_limit_seconds?: number;
  created_at: string;               // ISO 8601
}

```text
}

```text

- --

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Custom Error Codes

```json
### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Custom Error Codes

```json

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Custom Error Codes

```json

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Custom Error Codes

```json
{
  "error": {
    "code": "CONSCIOUSNESS_LEVEL_INVALID",
    "message": "Consciousness level must be between 0.0 and 1.0",
    "details": {
      "provided_value": 1.5,
      "valid_range": "0.0 - 1.0"
    }
  }
}
```text

      "provided_value": 1.5,
      "valid_range": "0.0 - 1.0"
    }
  }
}

```text
      "provided_value": 1.5,
      "valid_range": "0.0 - 1.0"
    }
  }
}

```text

```text

#### Error Code Reference

- `USER_NOT_FOUND`: User context does not exist
- `SESSION_NOT_ACTIVE`: Learning session not active
- `INVALID_SKILL_LEVEL`: Invalid skill level provided
- `MODULE_NOT_AVAILABLE`: Learning module not available
- `CONSCIOUSNESS_LEVEL_INVALID`: Invalid consciousness level
- `NEURAL_POPULATION_ERROR`: Neural population operation failed
- `SECURITY_SCENARIO_EXPIRED`: Security scenario has expired
- `ASSESSMENT_ALREADY_SUBMITTED`: Assessment already completed

- --

## Rate Limiting

### Rate Limits

- **General API**: 1000 requests per hour per user
- **Real-time Events**: 100 connections per user
- **Learning Progress**: 60 updates per minute per session
- **Security Assessments**: 10 assessments per hour per user

### Rate Limit Headers

```http
- `INVALID_SKILL_LEVEL`: Invalid skill level provided
- `MODULE_NOT_AVAILABLE`: Learning module not available
- `CONSCIOUSNESS_LEVEL_INVALID`: Invalid consciousness level
- `NEURAL_POPULATION_ERROR`: Neural population operation failed
- `SECURITY_SCENARIO_EXPIRED`: Security scenario has expired
- `ASSESSMENT_ALREADY_SUBMITTED`: Assessment already completed

- --

## Rate Limiting

### Rate Limits

- **General API**: 1000 requests per hour per user
- **Real-time Events**: 100 connections per user
- **Learning Progress**: 60 updates per minute per session
- **Security Assessments**: 10 assessments per hour per user

### Rate Limit Headers

```http

- `INVALID_SKILL_LEVEL`: Invalid skill level provided
- `MODULE_NOT_AVAILABLE`: Learning module not available
- `CONSCIOUSNESS_LEVEL_INVALID`: Invalid consciousness level
- `NEURAL_POPULATION_ERROR`: Neural population operation failed
- `SECURITY_SCENARIO_EXPIRED`: Security scenario has expired
- `ASSESSMENT_ALREADY_SUBMITTED`: Assessment already completed

- --

## Rate Limiting

### Rate Limits

- **General API**: 1000 requests per hour per user
- **Real-time Events**: 100 connections per user
- **Learning Progress**: 60 updates per minute per session
- **Security Assessments**: 10 assessments per hour per user

### Rate Limit Headers

```http

- `SECURITY_SCENARIO_EXPIRED`: Security scenario has expired
- `ASSESSMENT_ALREADY_SUBMITTED`: Assessment already completed

- --

## Rate Limiting

### Rate Limits

- **General API**: 1000 requests per hour per user
- **Real-time Events**: 100 connections per user
- **Learning Progress**: 60 updates per minute per session
- **Security Assessments**: 10 assessments per hour per user

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```text

```text

```text
```text

### Rate Limit Exceeded Response

```json
```json

```json

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 3600
  }
}
```text

  }
}

```text
  }
}

```text
```text

- --

## Authentication

### JWT Token Structure

```json
### JWT Token Structure

```json

### JWT Token Structure

```json

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user123",
    "iat": 1642248000,
    "exp": 1642251600,
    "scope": ["consciousness:read", "consciousness:write"],
    "consciousness_level": 0.8
  }
}
```text

  "payload": {
    "sub": "user123",
    "iat": 1642248000,
    "exp": 1642251600,
    "scope": ["consciousness:read", "consciousness:write"],
    "consciousness_level": 0.8
  }
}

```text
  "payload": {
    "sub": "user123",
    "iat": 1642248000,
    "exp": 1642251600,
    "scope": ["consciousness:read", "consciousness:write"],
    "consciousness_level": 0.8
  }
}

```text
    "consciousness_level": 0.8
  }
}

```text

### Scopes

- `consciousness:read`: Read consciousness system data
- `consciousness:write`: Modify consciousness system data
- `user:manage`: Manage user contexts and sessions
- `security:assess`: Access security assessment features
- `neural:monitor`: Monitor neural population data
- `admin:system`: Administrative system access

### Token Refresh

```http
- `user:manage`: Manage user contexts and sessions
- `security:assess`: Access security assessment features
- `neural:monitor`: Monitor neural population data
- `admin:system`: Administrative system access

### Token Refresh

```http

- `user:manage`: Manage user contexts and sessions
- `security:assess`: Access security assessment features
- `neural:monitor`: Monitor neural population data
- `admin:system`: Administrative system access

### Token Refresh

```http

### Token Refresh

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```text

}

```text
}

```text
```text

* *Response**:

```json
```json

```json

```json
{
  "access_token": "new_jwt_token",
  "token_type": "Bearer",
  "expires_in": 3600
}
```text

```text

```text
```text

This comprehensive API reference provides complete documentation for integrating with the SynapticOS Consciousness
System V2, enabling developers to build consciousness-aware applications and services.