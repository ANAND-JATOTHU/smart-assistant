"""
Model Router - 100% Offline
Routes all requests to local GGUF model only
"""

from typing import Optional, Dict
from .base import BaseLLM
from .local_model import LocalModel


class ModelRouter:
    """Route requests to local model only (offline operation)"""
    
    # Task type definitions
    TASK_SYSTEM_COMMAND = "system_command"
    TASK_PLANNING = "planning"
    TASK_CONVERSATION = "conversation"
    TASK_CODING = "coding"
    TASK_ANALYSIS = "analysis"
    
    def __init__(self, registry=None, mode: str = "offline"):
        """
        Initialize router (always offline)
        
        Args:
            registry: ModelRegistry instance (optional)
            mode: Always 'offline'
        """
        self.mode = "offline"  # Force offline mode
        self.registry = registry
        self.models: Dict[str, BaseLLM] = {}
        self.default_local: Optional[BaseLLM] = None
    
    def register_model(self, key: str, model: BaseLLM):
        """Register a local model"""
        self.models[key] = model
        
        if not model.is_online and self.default_local is None:
            self.default_local = model
    
    def set_default_local(self, key: str):
        """Set default local model"""
        if key in self.models and not self.models[key].is_online:
            self.default_local = self.models[key]
    
    def route(
        self,
        task_type: str = TASK_CONVERSATION,
        prefer_online: bool = False
    ) -> Optional[BaseLLM]:
        """
        Route to local model (always offline)
        
        Args:
            task_type: Type of task (ignored in offline mode)
            prefer_online: Ignored (always offline)
        
        Returns:
            Local GGUF model or None
        """
        # Always return local model in offline mode
        return self._select_local_model(task_type)
    
    def _select_local_model(self, task_type: str) -> Optional[BaseLLM]:
        """Select local model (only one available)"""
        return self.default_local
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get info about available local models"""
        return {
            key: model.get_info()
            for key, model in self.models.items()
            if model.is_available()
        }
    
    def classify_task(self, user_input: str) -> str:
        """
        Classify task type from user input
        
        Args:
            user_input: User's message
        
        Returns:
            Task type constant
        """
        input_lower = user_input.lower()
        
        # System commands
        system_keywords = [
            'open', 'close', 'launch', 'start', 'stop', 'kill',
            'volume', 'brightness', 'screenshot', 'minimize', 'maximize'
        ]
        if any(keyword in input_lower for keyword in system_keywords):
            return self.TASK_SYSTEM_COMMAND
        
        # Planning/reasoning
        planning_keywords = [
            'plan', 'strategy', 'how to', 'steps', 'approach',
            'design', 'architecture', 'organize'
        ]
        if any(keyword in input_lower for keyword in planning_keywords):
            return self.TASK_PLANNING
        
        # Coding
        coding_keywords = [
            'code', 'program', 'function', 'class', 'debug',
            'python', 'javascript', 'write a script'
        ]
        if any(keyword in input_lower for keyword in coding_keywords):
            return self.TASK_CODING
        
        # Default to conversation
        return self.TASK_CONVERSATION
    
    def generate(self, prompt: str, model_preference: str = 'local', **kwargs) -> str:
        """
        Generate response using local model
        
        Args:
            prompt: User prompt
            model_preference: Ignored (always local)
            **kwargs: Additional generation parameters
        
        Returns:
            Generated response
        """
        model = self.default_local
        if not model or not model.is_available():
            return "Local model not available. Please check configuration."
        
        try:
            return model.generate(prompt, **kwargs)
        except Exception as e:
            return f"Error generating response: {str(e)}"


if __name__ == "__main__":
    # Test router
    from .registry import ModelRegistry
    from utils.config import GGUF_MODEL_PATH
    import os
    
    print("=" * 60)
    print("Testing Model Router (Offline Mode)")
    print("=" * 60)
    
    # Create router
    registry = ModelRegistry()
    router = ModelRouter(registry=registry, mode="offline")
    
    # Register local model if exists
    if os.path.exists(GGUF_MODEL_PATH):
        registry.register_model('local', 'gguf', model_path=GGUF_MODEL_PATH)
        print(f"✅ Local model registered")
    else:
        print(f"⚠️  Model not found at: {GGUF_MODEL_PATH}")
    
    # Test task classification
    test_inputs = [
        "Open Chrome browser",
        "How do I plan a vacation?",
        "Write a Python function to sort a list",
        "Hello, how are you?"
    ]
    
    print("\nTask Classification:")
    for inp in test_inputs:
        task = router.classify_task(inp)
        print(f"  '{inp}' -> {task}")
    
    print("\n✅ Router test completed!")
