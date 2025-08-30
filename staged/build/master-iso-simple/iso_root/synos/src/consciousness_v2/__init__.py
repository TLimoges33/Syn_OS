"""
SynapticOS Consciousness System v2
==================================

A complete rebuild of the consciousness system with unified integration,
real-time feedback loops, and high-performance processing.

This package provides:
- Consciousness Bus for event-driven communication
- State Manager for unified consciousness state
- Enhanced Neural Darwinism Engine with GPU acceleration
- Real-time Context Engine with consciousness feedback
- Consciousness-aware Security Tutor
- Performance monitoring and debugging tools
"""

__version__ = "2.0.0"
__author__ = "SynapticOS Team"

# Core components
from .core.consciousness_bus import ConsciousnessBus
from .core.state_manager import StateManager
from .core.event_types import EventType, ConsciousnessEvent
from .core.data_models import ConsciousnessState, PopulationState, UserContextState

# Component interfaces
from .interfaces.consciousness_component import ConsciousnessComponent

# Enhanced components
from .components.neural_darwinism_v2 import EnhancedNeuralDarwinismEngine, NeuralConfiguration
from .components.lm_studio_v2 import (
    ConsciousnessAwareLMStudio, LMStudioConfiguration,
    ConsciousnessAwareRequest, ConsciousnessAwareResponse
)

# Additional interfaces and components will be imported as they are implemented
# from .interfaces.neural_darwinism import NeuralDarwinismInterface
# from .interfaces.lm_studio import LMStudioInterface
# from .interfaces.context_engine import PersonalContextInterface
# from .interfaces.security_tutor import SecurityTutorInterface

# Additional components (to be implemented)
# from .components.lm_studio_v2 import ConsciousnessAwareLMStudio
# from .components.context_engine_v2 import RealTimeContextEngine
# from .components.security_tutor_v2 import ConsciousnessAwareSecurityTutor

# Utilities (to be implemented)
# from .utils.performance_monitor import PerformanceMonitor
# from .utils.logger import get_consciousness_logger
# from .utils.config import ConsciousnessConfig

# Factory functions
from .core.data_models import (
    create_default_consciousness_state,
    create_population_state,
    create_user_context,
    create_component_status
)

__all__ = [
    # Core components
    'ConsciousnessBus',
    'StateManager',
    'EventType',
    'ConsciousnessEvent',
    'ConsciousnessState',
    'PopulationState',
    'UserContextState',
    
    # Interfaces
    'ConsciousnessComponent',
    
    # Enhanced components
    'EnhancedNeuralDarwinismEngine',
    'NeuralConfiguration',
    'ConsciousnessAwareLMStudio',
    'LMStudioConfiguration',
    'ConsciousnessAwareRequest',
    'ConsciousnessAwareResponse',
    
    # Factory functions
    'create_default_consciousness_state',
    'create_population_state',
    'create_user_context',
    'create_component_status'
]