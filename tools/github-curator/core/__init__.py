"""
Core __init__.py for the curator module.
"""

from .curator import RepositoryCurator, CurationResult
from .fork_manager import ForkManager, ForkOperation
from .categorizer import RepositoryCategorizer, CategoryMatch
from .library_generator import LibraryGenerator

__all__ = [
    'RepositoryCurator',
    'CurationResult', 
    'ForkManager',
    'ForkOperation',
    'RepositoryCategorizer',
    'CategoryMatch',
    'LibraryGenerator'
]
