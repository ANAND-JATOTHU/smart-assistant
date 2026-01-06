"""
Local GGUF Model Implementation
Offline LLM using llama-cpp-python
"""

import os
from typing import Iterator, Optional

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    Llama = None
    HAS_LLAMA_CPP = False

from .base import BaseLLM



class LocalModel(BaseLLM):
    """Local GGUF model using llama-cpp-python"""
    
    def __init__(
        self,
        model_path: str,
        model_name: Optional[str] = None,
        use_gpu: bool = True,
        gpu_layers: int = 35,
        context_size: int = 4096,
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize local GGUF model
        
        Args:
            model_path: Path to .gguf file
            model_name: Display name (defaults to filename)
            use_gpu: Enable GPU acceleration
            gpu_layers: Number of layers to offload to GPU
            context_size: Context window size
            temperature: Sampling temperature
            max_tokens: Max tokens per response
        """
        if model_name is None:
            model_name = os.path.basename(model_path)
        
        super().__init__(model_name)
        
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.gpu_layers = gpu_layers if use_gpu else 0
        self.context_size = context_size
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.is_online = False
        
        self.capabilities = {
            'streaming': True,
            'function_calling': False,
            'vision': False
        }
        
        self.model: Optional[Llama] = None
        self._load_model()
    
    def _load_model(self):
        """Load the GGUF model"""
        try:
            print(f"Loading local model: {self.model_name}")
            print(f"  Path: {self.model_path}")
            print(f"  GPU Layers: {self.gpu_layers}")
            
            self.model = Llama(
                model_path=self.model_path,
                n_gpu_layers=self.gpu_layers,
                n_ctx=self.context_size,
                verbose=False
            )
            
            print(f"✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model is not None and os.path.exists(self.model_path)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response from prompt
        
        Args:
            prompt: Input text
            **kwargs: Override default parameters
        
        Returns:
            Generated text
        """
        if not self.is_available():
            raise RuntimeError(f"Model {self.model_name} is not available")
        
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        
        try:
            response = self.model(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["</s>", "User:", "Human:"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return f"Error: {str(e)}"
    
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate response with streaming
        
        Args:
            prompt: Input text
            **kwargs: Override default parameters
        
        Yields:
            Text chunks
        """
        if not self.is_available():
            raise RuntimeError(f"Model {self.model_name} is not available")
        
        temperature = kwargs.get('temperature', self.temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        
        try:
            stream = self.model(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["</s>", "User:", "Human:"],
                stream=True,
                echo=False
            )
            
            for chunk in stream:
                text = chunk['choices'][0]['text']
                if text:
                    yield text
                    
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            yield f"Error: {str(e)}"
    
    def unload(self):
        """Unload model from memory"""
        if self.model:
            del self.model
            self.model = None
            print(f"Model {self.model_name} unloaded")


if __name__ == "__main__":
    # Test local model
    model_path = r"C:\Users\JATOTHU ANAND\Desktop\Smart Real-time Unified Tool for Human-AI Interaction sruthi-ai\assistant\codellama-7b-instruct.Q4_K_M.gguf"
    
    if os.path.exists(model_path):
        model = LocalModel(model_path, gpu_layers=35)
        
        if model.is_available():
            print("\nTesting generation:")
            response = model.generate("Hello! Who are you?")
            print(f"Response: {response}")
    else:
        print(f"Model not found: {model_path}")
