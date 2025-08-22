"""
Bridges package for Consciousness System V2

This package contains bridge modules that connect the consciousness system
to external services and message buses.
"""

from .nats_bridge import NATSBridge, create_nats_bridge

__all__ = ['NATSBridge', 'create_nats_bridge']