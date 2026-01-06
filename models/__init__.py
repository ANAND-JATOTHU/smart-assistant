"""
Smart Assistant Model Abstraction Layer (Offline Only)
Local GGUF models support
"""

from .base import BaseLLM
from .router import ModelRouter
from .registry import ModelRegistry

# Local model (requires llama-cpp-python)
try:
    from .local_model import LocalModel
    HAS_LOCAL_MODEL = True
except ImportError:
    LocalModel = None
    HAS_LOCAL_MODEL = False

__all__ = [
    'BaseLLM',
    'LocalModel',
    'ModelRouter',
    'ModelRegistry',
    'HAS_LOCAL_MODEL'
]

