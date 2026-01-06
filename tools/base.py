"""
Base Tool Interface
Abstract base class for all tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Tool(ABC):
    """Abstract base class for tools"""
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
        self.requires_confirmation = False
        self.is_dangerous = False
    
    @abstractmethod
    def execute(self, **params) -> Dict[str, Any]:
        """
        Execute the tool
        
        Args:
            **params: Tool parameters
        
        Returns:
            Dict with:
                - success: bool
                - result: Any
                - message: str
                - error: Optional[str]
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[Dict[str, Any]]:
        """
        Get tool parameter schema
        
        Returns:
            List of parameter definitions
        """
        pass
    
    def validate_params(self, **params) -> tuple[bool, str]:
        """
        Validate parameters
        
        Args:
            **params: Parameters to validate
        
        Returns:
            (is_valid, error_message)
        """
        param_schema = {p['name']: p for p in self.get_parameters()}
        
        # Check required parameters
        for param_name, param_def in param_schema.items():
            if param_def.get('required', False) and param_name not in params:
                return False, f"Missing required parameter: {param_name}"
        
        return True, ""
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.get_parameters(),
            'requires_confirmation': self.requires_confirmation,
            'is_dangerous': self.is_dangerous
        }
    
    def __repr__(self):
        return f"Tool(name='{self.name}')"
