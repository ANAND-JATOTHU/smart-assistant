"""
Base LLM Interface
Abstract base class for all LLM implementations
"""

from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional


class BaseLLM(ABC):
    """Abstract base class for LLM implementations"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_online = False
        self.capabilities = {
            'streaming': False,
            'function_calling': False,
            'vision': False
        }
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response from prompt
        
        Args:
            prompt: Input text
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate response with streaming
        
        Args:
            prompt: Input text
            **kwargs: Additional parameters
        
        Yields:
            Text chunks
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if model is available and ready
        
        Returns:
            True if model can be used
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dict with model metadata
        """
        return {
            'name': self.model_name,
            'is_online': self.is_online,
            'capabilities': self.capabilities,
            'available': self.is_available()
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(model='{self.model_name}', online={self.is_online})"
