"""
Persistence package for Consciousness System V2

This package provides data persistence and user context management
for the consciousness system, including user profiles, learning patterns,
and behavioral analysis.
"""

from .user_context_manager import (
    UserContextManager,
    UserContext,
    UserProfile,
    ContextType,
    create_user_context_manager
)

__all__ = [
    'UserContextManager',
    'UserContext', 
    'UserProfile',
    'ContextType',
    'create_user_context_manager'
]