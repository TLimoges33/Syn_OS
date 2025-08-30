"""
NATS Circuit Breaker and Resilience Patterns
============================================

Implements circuit breaker patterns, fallback mechanisms, and resilience
features for NATS communication in the consciousness system.
"""

import asyncio
import logging
import time
from typing import Optional, Callable, Any, Dict
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: float = 60.0      # Seconds before trying half-open
    success_threshold: int = 3          # Successes to close from half-open
    timeout: float = 30.0               # Request timeout
    
    # Exponential backoff settings
    initial_backoff: float = 1.0        # Initial backoff delay
    max_backoff: float = 300.0          # Maximum backoff delay
    backoff_multiplier: float = 2.0     # Backoff multiplier


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    current_consecutive_failures: int = 0
    current_consecutive_successes: int = 0


class CircuitBreaker:
    """
    Circuit breaker implementation for NATS operations
    
    Provides automatic failure detection, fast-fail behavior,
    and automatic recovery testing.
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker
        
        Args:
            name: Circuit breaker name for logging
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # State management
        self._state_lock = asyncio.Lock()
        self._last_failure_time = 0.0
        self._next_attempt_time = 0.0
        self._current_backoff = self.config.initial_backoff
        
        # Fallback handlers
        self._fallback_handler: Optional[Callable] = None
        self._health_check_handler: Optional[Callable] = None
    
    def set_fallback_handler(self, handler: Callable):
        """Set fallback handler for when circuit is open"""
        self._fallback_handler = handler
    
    def set_health_check_handler(self, handler: Callable):
        """Set health check handler for recovery testing"""
        self._health_check_handler = handler
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback result
            
        Raises:
            CircuitBreakerOpenError: When circuit is open and no fallback
        """
        async with self._state_lock:
            # Check if we should attempt the call
            if not await self._can_attempt():
                if self._fallback_handler:
                    self.logger.debug(f"Circuit {self.name} open, using fallback")
                    return await self._fallback_handler(*args, **kwargs)
                else:
                    raise CircuitBreakerOpenError(f"Circuit {self.name} is open")
            
            # Attempt the call
            try:
                self.metrics.total_requests += 1
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
                
                # Record success
                await self._record_success()
                return result
                
            except asyncio.TimeoutError:
                self.metrics.timeouts += 1
                await self._record_failure()
                raise
                
            except Exception as e:
                await self._record_failure()
                raise
    
    async def _can_attempt(self) -> bool:
        """Check if we can attempt a call based on circuit state"""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if current_time >= self._next_attempt_time:
                self.state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit {self.name} transitioning to HALF_OPEN")
                return True
            return False
        
        elif self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    async def _record_success(self):
        """Record a successful operation"""
        self.metrics.successful_requests += 1
        self.metrics.current_consecutive_successes += 1
        self.metrics.current_consecutive_failures = 0
        self.metrics.last_success_time = datetime.now()
        
        # Reset backoff on success
        self._current_backoff = self.config.initial_backoff
        
        # Check if we should close the circuit
        if self.state == CircuitState.HALF_OPEN:
            if self.metrics.current_consecutive_successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.metrics.current_consecutive_successes = 0
                self.logger.info(f"Circuit {self.name} closed after successful recovery")
    
    async def _record_failure(self):
        """Record a failed operation"""
        self.metrics.failed_requests += 1
        self.metrics.current_consecutive_failures += 1
        self.metrics.current_consecutive_successes = 0
        self.metrics.last_failure_time = datetime.now()
        
        current_time = time.time()
        self._last_failure_time = current_time
        
        # Check if we should open the circuit
        if (self.state == CircuitState.CLOSED and 
            self.metrics.current_consecutive_failures >= self.config.failure_threshold):
            
            await self._open_circuit()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Failed during recovery, go back to open
            await self._open_circuit()
    
    async def _open_circuit(self):
        """Open the circuit breaker"""
        self.state = CircuitState.OPEN
        self.metrics.circuit_opens += 1
        
        # Calculate next attempt time with exponential backoff
        self._next_attempt_time = time.time() + self._current_backoff
        self._current_backoff = min(
            self._current_backoff * self.config.backoff_multiplier,
            self.config.max_backoff
        )
        
        self.logger.warning(
            f"Circuit {self.name} opened after {self.metrics.current_consecutive_failures} "
            f"consecutive failures. Next attempt in {self._current_backoff:.1f}s"
        )
    
    async def force_open(self):
        """Manually force circuit open"""
        async with self._state_lock:
            await self._open_circuit()
            self.logger.info(f"Circuit {self.name} manually forced open")
    
    async def force_close(self):
        """Manually force circuit closed"""
        async with self._state_lock:
            self.state = CircuitState.CLOSED
            self.metrics.current_consecutive_failures = 0
            self.metrics.current_consecutive_successes = 0
            self._current_backoff = self.config.initial_backoff
            self.logger.info(f"Circuit {self.name} manually forced closed")
    
    async def health_check(self) -> bool:
        """Perform health check if handler is available"""
        if not self._health_check_handler:
            return True
        
        try:
            return await self._health_check_handler()
        except Exception as e:
            self.logger.error(f"Health check failed for circuit {self.name}: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        return {
            'name': self.name,
            'state': self.state.value,
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'success_rate': (
                self.metrics.successful_requests / max(self.metrics.total_requests, 1)
            ),
            'timeouts': self.metrics.timeouts,
            'circuit_opens': self.metrics.circuit_opens,
            'consecutive_failures': self.metrics.current_consecutive_failures,
            'consecutive_successes': self.metrics.current_consecutive_successes,
            'last_failure': (
                self.metrics.last_failure_time.isoformat() 
                if self.metrics.last_failure_time else None
            ),
            'last_success': (
                self.metrics.last_success_time.isoformat() 
                if self.metrics.last_success_time else None
            ),
            'next_attempt_time': self._next_attempt_time,
            'current_backoff': self._current_backoff
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class NATSResilienceManager:
    """
    Manages circuit breakers and resilience patterns for NATS operations
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(__name__)
        
        # Default circuit breakers for NATS operations
        self._create_default_circuit_breakers()
    
    def _create_default_circuit_breakers(self):
        """Create default circuit breakers for common NATS operations"""
        
        # Connection circuit breaker
        connection_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2,
            timeout=10.0
        )
        self.circuit_breakers['connection'] = CircuitBreaker('connection', connection_config)
        
        # Publishing circuit breaker
        publish_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=3,
            timeout=30.0
        )
        self.circuit_breakers['publish'] = CircuitBreaker('publish', publish_config)
        
        # Subscription circuit breaker
        subscribe_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=45.0,
            success_threshold=2,
            timeout=20.0
        )
        self.circuit_breakers['subscribe'] = CircuitBreaker('subscribe', subscribe_config)
        
        # JetStream circuit breaker
        jetstream_config = CircuitBreakerConfig(
            failure_threshold=4,
            recovery_timeout=90.0,
            success_threshold=3,
            timeout=45.0
        )
        self.circuit_breakers['jetstream'] = CircuitBreaker('jetstream', jetstream_config)
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def add_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Add a new circuit breaker"""
        circuit_breaker = CircuitBreaker(name, config)
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker
    
    async def execute_with_circuit_breaker(self, 
                                         circuit_name: str,
                                         func: Callable,
                                         *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        circuit_breaker = self.circuit_breakers.get(circuit_name)
        if not circuit_breaker:
            # No circuit breaker, execute directly
            return await func(*args, **kwargs)
        
        return await circuit_breaker.call(func, *args, **kwargs)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all circuit breakers"""
        results = {}
        for name, circuit_breaker in self.circuit_breakers.items():
            results[name] = await circuit_breaker.health_check()
        return results
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        return {
            name: circuit_breaker.get_metrics()
            for name, circuit_breaker in self.circuit_breakers.items()
        }
    
    async def force_open_all(self):
        """Force open all circuit breakers (emergency mode)"""
        for circuit_breaker in self.circuit_breakers.values():
            await circuit_breaker.force_open()
        self.logger.warning("All circuit breakers forced open (emergency mode)")
    
    async def force_close_all(self):
        """Force close all circuit breakers (recovery mode)"""
        for circuit_breaker in self.circuit_breakers.values():
            await circuit_breaker.force_close()
        self.logger.info("All circuit breakers forced closed (recovery mode)")


# Global resilience manager instance
resilience_manager = NATSResilienceManager()


# Decorator for easy circuit breaker usage
def with_circuit_breaker(circuit_name: str):
    """Decorator to add circuit breaker protection to a function"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await resilience_manager.execute_with_circuit_breaker(
                circuit_name, func, *args, **kwargs
            )
        return wrapper
    return decorator