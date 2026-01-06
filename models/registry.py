"""
Model Registry
CRUD operations for managing models
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class ModelRegistry:
    """Manage registered models with persistence"""
    
    def __init__(self, registry_file: Optional[str] = None):
        """
        Initialize registry
        
        Args:
            registry_file: Path to JSON registry file
        """
        if registry_file is None:
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            registry_file = str(data_dir / "model_registry.json")
        
        self.registry_file = registry_file
        self.models: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """Load registry from file"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    self.models = json.load(f)
                print(f"✅ Loaded {len(self.models)} models from registry")
            except Exception as e:
                print(f"⚠️ Failed to load registry: {e}")
                self.models = {}
        else:
            self.models = {}
            self._save()
    
    def _save(self):
        """Save registry to file"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.models, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save registry: {e}")
    
    def add_model(
        self,
        key: str,
        model_type: str,
        model_path: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        is_default: bool = False,
        **kwargs
    ) -> bool:
        """
        Add a model to registry
        
        Args:
            key: Unique identifier
            model_type: 'local', 'gemini', 'openai', 'anthropic', 'groq'
            model_path: Path to GGUF file (for local models)
            model_name: Model name (e.g., 'gpt-4', 'gemini-pro')
            api_key: API key (for online models)
            is_default: Set as default for this type
            **kwargs: Additional parameters
        
        Returns:
            True if successful
        """
        if key in self.models:
            print(f"⚠️ Model '{key}' already exists. Use update_model() instead.")
            return False
        
        model_info = {
            'key': key,
            'type': model_type,
            'model_path': model_path,
            'model_name': model_name,
            'api_key': api_key,
            'is_default': is_default,
            'is_online': model_type != 'local',
            **kwargs
        }
        
        self.models[key] = model_info
        self._save()
        
        print(f"✅ Added model: {key} ({model_type})")
        return True
    
    def get_model(self, key: str) -> Optional[Dict]:
        """Get model info by key"""
        return self.models.get(key)
    
    def list_models(self, model_type: Optional[str] = None) -> List[Dict]:
        """
        List all models
        
        Args:
            model_type: Filter by type (optional)
        
        Returns:
            List of model info dicts
        """
        if model_type:
            return [
                info for info in self.models.values()
                if info['type'] == model_type
            ]
        return list(self.models.values())
    
    def update_model(self, key: str, **updates) -> bool:
        """
        Update model info
        
        Args:
            key: Model key
            **updates: Fields to update
        
        Returns:
            True if successful
        """
        if key not in self.models:
            print(f"❌ Model '{key}' not found")
            return False
        
        self.models[key].update(updates)
        self._save()
        
        print(f"✅ Updated model: {key}")
        return True
    
    def remove_model(self, key: str) -> bool:
        """
        Remove a model
        
        Args:
            key: Model key
        
        Returns:
            True if successful
        """
        if key not in self.models:
            print(f"❌ Model '{key}' not found")
            return False
        
        del self.models[key]
        self._save()
        
        print(f"✅ Removed model: {key}")
        return True
    
    def set_default(self, key: str) -> bool:
        """
        Set model as default for its type
        
        Args:
            key: Model key
        
        Returns:
            True if successful
        """
        if key not in self.models:
            print(f"❌ Model '{key}' not found")
            return False
        
        model_type = self.models[key]['type']
        
        # Unset other defaults of same type
        for k, info in self.models.items():
            if info['type'] == model_type:
                info['is_default'] = (k == key)
        
        self._save()
        print(f"✅ Set {key} as default {model_type} model")
        return True
    
    def get_default(self, model_type: str) -> Optional[Dict]:
        """Get default model for type"""
        for info in self.models.values():
            if info['type'] == model_type and info.get('is_default'):
                return info
        
        # If no default, return first of type
        models = self.list_models(model_type)
        return models[0] if models else None
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        stats = {
            'total': len(self.models),
            'local': 0,
            'online': 0,
            'by_type': {}
        }
        
        for info in self.models.values():
            model_type = info['type']
            
            if info['is_online']:
                stats['online'] += 1
            else:
                stats['local'] += 1
            
            if model_type not in stats['by_type']:
                stats['by_type'][model_type] = 0
            stats['by_type'][model_type] += 1
        
        return stats


if __name__ == "__main__":
    # Test registry
    registry = ModelRegistry()
    
    # Add some test models
    registry.add_model(
        key='mistral-7b',
        model_type='local',
        model_path='/path/to/mistral-7b.gguf',
        is_default=True
    )
    
    registry.add_model(
        key='gemini',
        model_type='gemini',
        model_name='gemini-pro',
        is_default=True
    )
    
    # List models
    print("\nAll models:")
    for model in registry.list_models():
        print(f"  {model['key']}: {model['type']}")
    
    # Get stats
    print("\nRegistry stats:")
    stats = registry.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
