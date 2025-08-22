"""
NATS Message Schema Validation
==============================

Provides JSON schema validation for all NATS message types in the
consciousness system to ensure data integrity and compatibility.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator


class MessageSchemaType(Enum):
    """Message schema types"""
    CONSCIOUSNESS_EVENT = "consciousness_event"
    ORCHESTRATOR_EVENT = "orchestrator_event"
    SECURITY_EVENT = "security_event"
    HEALTH_METRIC = "health_metric"
    PRIORITY_EVENT = "priority_event"
    GENERIC_EVENT = "generic_event"


@dataclass
class ValidationResult:
    """Schema validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    schema_type: Optional[MessageSchemaType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'schema_type': self.schema_type.value if self.schema_type else None
        }


class MessageSchemaValidator:
    """
    Validates NATS messages against predefined JSON schemas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.schemas: Dict[MessageSchemaType, Dict[str, Any]] = {}
        self.validators: Dict[MessageSchemaType, Draft7Validator] = {}
        
        # Initialize schemas
        self._initialize_schemas()
        self._create_validators()
    
    def _initialize_schemas(self):
        """Initialize JSON schemas for different message types"""
        
        # Base event schema
        base_event_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "type": {"type": "string", "minLength": 1},
                "source": {"type": "string", "minLength": 1},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {"type": "object"},
                "metadata": {"type": "object"},
                "priority": {"type": "integer", "minimum": 1, "maximum": 10},
                "correlation_id": {"type": ["string", "null"]},
                "retry_count": {"type": "integer", "minimum": 0}
            },
            "required": ["id", "type", "source", "timestamp", "data"],
            "additionalProperties": True
        }
        
        # Consciousness event schema
        self.schemas[MessageSchemaType.CONSCIOUSNESS_EVENT] = {
            **base_event_schema,
            "properties": {
                **base_event_schema["properties"],
                "type": {
                    "type": "string",
                    "enum": [
                        "consciousness.state_change",
                        "consciousness.attention_shift", 
                        "consciousness.memory_update",
                        "consciousness.decision_made",
                        "consciousness.learning_event",
                        "consciousness.error",
                        "consciousness.health.status"
                    ]
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "consciousness_level": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "attention_focus": {"type": "object"},
                        "emotional_state": {
                            "type": "object",
                            "properties": {
                                "valence": {"type": "number", "minimum": -1.0, "maximum": 1.0},
                                "arousal": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                            }
                        },
                        "cognitive_load": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "learning_mode": {"type": "string", "enum": ["adaptive", "focused", "exploratory"]}
                    }
                }
            }
        }
        
        # Orchestrator event schema
        self.schemas[MessageSchemaType.ORCHESTRATOR_EVENT] = {
            **base_event_schema,
            "properties": {
                **base_event_schema["properties"],
                "type": {
                    "type": "string",
                    "enum": [
                        "orchestrator.service.started",
                        "orchestrator.service.stopped",
                        "orchestrator.service.health",
                        "orchestrator.system.resource",
                        "orchestrator.user.request",
                        "orchestrator.service.action_request"
                    ]
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string"},
                        "service_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["started", "stopped", "healthy", "unhealthy", "failed"]},
                        "action": {"type": "string"},
                        "parameters": {"type": "object"},
                        "resource_usage": {
                            "type": "object",
                            "properties": {
                                "cpu_usage": {"type": "number", "minimum": 0.0, "maximum": 100.0},
                                "memory_usage": {"type": "number", "minimum": 0.0, "maximum": 100.0},
                                "disk_usage": {"type": "number", "minimum": 0.0, "maximum": 100.0}
                            }
                        }
                    }
                }
            }
        }
        
        # Security event schema
        self.schemas[MessageSchemaType.SECURITY_EVENT] = {
            **base_event_schema,
            "properties": {
                **base_event_schema["properties"],
                "type": {
                    "type": "string",
                    "enum": [
                        "security.threat.detected",
                        "security.incident.created",
                        "security.assessment.completed",
                        "security.alert.fired",
                        "security.vulnerability.found"
                    ]
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                        "threat_type": {"type": "string"},
                        "source_ip": {"type": ["string", "null"]},
                        "user_id": {"type": ["string", "null"]},
                        "description": {"type": "string"},
                        "indicators": {"type": "object"},
                        "recommended_actions": {"type": "array", "items": {"type": "string"}},
                        "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    },
                    "required": ["severity", "description"]
                }
            }
        }
        
        # Health metric schema
        self.schemas[MessageSchemaType.HEALTH_METRIC] = {
            **base_event_schema,
            "properties": {
                **base_event_schema["properties"],
                "type": {
                    "type": "string",
                    "enum": [
                        "health.component.status",
                        "health.system.metrics",
                        "metrics.performance.update",
                        "metrics.resource.usage"
                    ]
                },
                "data": {
                    "type": "object",
                    "properties": {
                        "component_id": {"type": "string"},
                        "health_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "status": {"type": "string", "enum": ["healthy", "degraded", "failed", "recovering"]},
                        "metrics": {
                            "type": "object",
                            "properties": {
                                "response_time_ms": {"type": "number", "minimum": 0},
                                "error_rate": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "throughput": {"type": "number", "minimum": 0}
                            }
                        },
                        "last_heartbeat": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
        
        # Priority event schema
        self.schemas[MessageSchemaType.PRIORITY_EVENT] = {
            **base_event_schema,
            "properties": {
                **base_event_schema["properties"],
                "type": {
                    "type": "string",
                    "enum": [
                        "priority.system.critical",
                        "critical.service.failure",
                        "alert.security.breach",
                        "priority.consciousness.emergency"
                    ]
                },
                "priority": {"type": "integer", "minimum": 8, "maximum": 10},
                "data": {
                    "type": "object",
                    "properties": {
                        "alert_level": {"type": "string", "enum": ["high", "critical", "emergency"]},
                        "affected_systems": {"type": "array", "items": {"type": "string"}},
                        "impact_assessment": {"type": "string"},
                        "immediate_actions": {"type": "array", "items": {"type": "string"}},
                        "escalation_required": {"type": "boolean"}
                    },
                    "required": ["alert_level", "impact_assessment"]
                }
            }
        }
        
        # Generic event schema (fallback)
        self.schemas[MessageSchemaType.GENERIC_EVENT] = base_event_schema
    
    def _create_validators(self):
        """Create JSON schema validators"""
        for schema_type, schema in self.schemas.items():
            try:
                self.validators[schema_type] = Draft7Validator(schema)
            except Exception as e:
                self.logger.error(f"Failed to create validator for {schema_type}: {e}")
    
    def validate_message(self, message: Dict[str, Any], 
                        schema_type: Optional[MessageSchemaType] = None) -> ValidationResult:
        """
        Validate a message against its schema
        
        Args:
            message: Message to validate
            schema_type: Specific schema type to validate against
            
        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        warnings = []
        
        try:
            # Auto-detect schema type if not provided
            if schema_type is None:
                schema_type = self._detect_schema_type(message)
            
            # Get validator
            validator = self.validators.get(schema_type)
            if not validator:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"No validator found for schema type: {schema_type}"],
                    warnings=[],
                    schema_type=schema_type
                )
            
            # Validate message
            validation_errors = list(validator.iter_errors(message))
            
            if validation_errors:
                for error in validation_errors:
                    error_path = " -> ".join([str(p) for p in error.path]) if error.path else "root"
                    errors.append(f"Path '{error_path}': {error.message}")
            
            # Additional custom validations
            custom_warnings = self._perform_custom_validations(message, schema_type)
            warnings.extend(custom_warnings)
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                schema_type=schema_type
            )
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation exception: {str(e)}"],
                warnings=[],
                schema_type=schema_type
            )
    
    def _detect_schema_type(self, message: Dict[str, Any]) -> MessageSchemaType:
        """Auto-detect schema type based on message content"""
        message_type = message.get('type', '')
        
        if message_type.startswith('consciousness.'):
            return MessageSchemaType.CONSCIOUSNESS_EVENT
        elif message_type.startswith('orchestrator.'):
            return MessageSchemaType.ORCHESTRATOR_EVENT
        elif message_type.startswith('security.'):
            return MessageSchemaType.SECURITY_EVENT
        elif message_type.startswith(('health.', 'metrics.')):
            return MessageSchemaType.HEALTH_METRIC
        elif message_type.startswith(('priority.', 'critical.', 'alert.')):
            return MessageSchemaType.PRIORITY_EVENT
        else:
            return MessageSchemaType.GENERIC_EVENT
    
    def _perform_custom_validations(self, message: Dict[str, Any], 
                                  schema_type: MessageSchemaType) -> List[str]:
        """Perform custom validation checks"""
        warnings = []
        
        # Check timestamp format and recency
        timestamp_str = message.get('timestamp')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                age_hours = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds() / 3600
                
                if age_hours > 24:
                    warnings.append(f"Message timestamp is {age_hours:.1f} hours old")
                elif age_hours > 1:
                    warnings.append(f"Message timestamp is {age_hours:.1f} hours old")
            except ValueError:
                warnings.append("Invalid timestamp format")
        
        # Check message size
        message_size = len(json.dumps(message).encode('utf-8'))
        if message_size > 1024 * 1024:  # 1MB
            warnings.append(f"Large message size: {message_size / 1024:.1f} KB")
        elif message_size > 100 * 1024:  # 100KB
            warnings.append(f"Message size: {message_size / 1024:.1f} KB")
        
        # Schema-specific validations
        if schema_type == MessageSchemaType.CONSCIOUSNESS_EVENT:
            data = message.get('data', {})
            if 'consciousness_level' in data and data['consciousness_level'] < 0.1:
                warnings.append("Very low consciousness level detected")
        
        elif schema_type == MessageSchemaType.SECURITY_EVENT:
            data = message.get('data', {})
            if data.get('severity') == 'critical' and not data.get('recommended_actions'):
                warnings.append("Critical security event without recommended actions")
        
        elif schema_type == MessageSchemaType.PRIORITY_EVENT:
            priority = message.get('priority', 1)
            if priority < 8:
                warnings.append("Priority event with low priority value")
        
        return warnings
    
    def validate_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, ValidationResult]:
        """Validate a batch of messages"""
        results = {}
        
        for i, message in enumerate(messages):
            message_id = message.get('id', f'message_{i}')
            results[message_id] = self.validate_message(message)
        
        return results
    
    def get_schema(self, schema_type: MessageSchemaType) -> Optional[Dict[str, Any]]:
        """Get schema definition for a specific type"""
        return self.schemas.get(schema_type)
    
    def get_all_schemas(self) -> Dict[MessageSchemaType, Dict[str, Any]]:
        """Get all schema definitions"""
        return self.schemas.copy()
    
    def add_custom_schema(self, schema_type: MessageSchemaType, schema: Dict[str, Any]):
        """Add a custom schema"""
        try:
            # Validate the schema itself
            Draft7Validator.check_schema(schema)
            
            # Add schema and validator
            self.schemas[schema_type] = schema
            self.validators[schema_type] = Draft7Validator(schema)
            
            self.logger.info(f"Added custom schema: {schema_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to add custom schema {schema_type}: {e}")
            raise
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'total_schemas': len(self.schemas),
            'available_validators': len(self.validators),
            'schema_types': [st.value for st in self.schemas.keys()]
        }


class NATSMessageValidator:
    """
    High-level NATS message validator with caching and performance optimization
    """
    
    def __init__(self):
        self.schema_validator = MessageSchemaValidator()
        self.logger = logging.getLogger(__name__)
        
        # Validation cache
        self.validation_cache: Dict[str, ValidationResult] = {}
        self.cache_max_size = 1000
        
        # Statistics
        self.validation_count = 0
        self.cache_hits = 0
        self.validation_errors = 0
    
    def validate_nats_message(self, subject: str, data: bytes, 
                            headers: Optional[Dict[str, str]] = None) -> ValidationResult:
        """
        Validate a NATS message
        
        Args:
            subject: NATS subject
            data: Message data (JSON bytes)
            headers: Optional message headers
            
        Returns:
            ValidationResult
        """
        self.validation_count += 1
        
        try:
            # Parse JSON data
            if isinstance(data, bytes):
                message_str = data.decode('utf-8')
            else:
                message_str = str(data)
            
            message = json.loads(message_str)
            
            # Add subject and headers to message for validation
            message['_nats_subject'] = subject
            if headers:
                message['_nats_headers'] = headers
            
            # Check cache
            cache_key = self._get_cache_key(message)
            if cache_key in self.validation_cache:
                self.cache_hits += 1
                return self.validation_cache[cache_key]
            
            # Validate message
            result = self.schema_validator.validate_message(message)
            
            # Cache result
            self._cache_result(cache_key, result)
            
            if not result.is_valid:
                self.validation_errors += 1
                self.logger.warning(f"Validation failed for subject {subject}: {result.errors}")
            
            return result
            
        except json.JSONDecodeError as e:
            self.validation_errors += 1
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid JSON: {str(e)}"],
                warnings=[]
            )
        except Exception as e:
            self.validation_errors += 1
            self.logger.error(f"Validation error for subject {subject}: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation exception: {str(e)}"],
                warnings=[]
            )
    
    def _get_cache_key(self, message: Dict[str, Any]) -> str:
        """Generate cache key for message"""
        # Use message type and a hash of the data for caching
        message_type = message.get('type', 'unknown')
        data_hash = hash(json.dumps(message.get('data', {}), sort_keys=True))
        return f"{message_type}_{data_hash}"
    
    def _cache_result(self, cache_key: str, result: ValidationResult):
        """Cache validation result"""
        if len(self.validation_cache) >= self.cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.validation_cache))
            del self.validation_cache[oldest_key]
        
        self.validation_cache[cache_key] = result
    
    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        self.logger.info("Validation cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        cache_hit_rate = (self.cache_hits / max(self.validation_count, 1)) * 100
        error_rate = (self.validation_errors / max(self.validation_count, 1)) * 100
        
        return {
            'total_validations': self.validation_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'validation_errors': self.validation_errors,
            'error_rate_percent': round(error_rate, 2),
            'cache_size': len(self.validation_cache),
            'schema_statistics': self.schema_validator.get_validation_statistics()
        }


# Global validator instance
nats_message_validator = NATSMessageValidator()