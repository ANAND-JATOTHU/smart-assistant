"""
Settings Manager - Backend Implementation
Handles actual mode switching, feature toggling, and configuration
"""

import os
import sys
from typing import Dict, Any

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import config functions
from utils.config import load_user_settings, save_user_settings


class SettingsManager:
    """Manage application settings with backend implementation"""
    
    def __init__(self, app):
        """
        Initialize settings manager
        
        Args:
            app: Main application instance
        """
        self.app = app
    
    def apply_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Apply settings changes
        
        Args:
            settings: Dictionary of settings to apply
        
        Returns:
            bool: True if successful
        """
        try:
            # Save to user settings JSON
            self._save_settings(settings)
            
            # Apply runtime changes
            self._apply_runtime_changes(settings)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply settings: {e}")
            return False
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings to user_settings.json"""
        current_settings = load_user_settings()
        
        # Update with new settings
        if 'theme' in settings:
            current_settings['theme'] = settings['theme']
        if 'tts_mode' in settings:
            current_settings['tts_mode'] = settings['tts_mode']
        if 'tts_voice' in settings:
            current_settings['tts_voice'] = settings['tts_voice']
        if 'wake_word_enabled' in settings:
            current_settings['wake_word_enabled'] = settings['wake_word_enabled']
        if 'gesture_enabled' in settings:
            current_settings['gesture_enabled'] = settings['gesture_enabled']
        
        if save_user_settings(current_settings):
            print("✅ Settings saved to user_settings.json")
        else:
            print("❌ Failed to save settings")
    
    def _apply_runtime_changes(self, settings: Dict[str, Any]):
        """Apply settings changes at runtime (without restart)"""
        
        # 1. Change theme (immediate)
        if 'theme' in settings:
            new_theme = settings['theme']
            print(f"🎨 Applying theme: {new_theme}")
            if hasattr(self.app, 'apply_theme'):
                self.app.apply_theme(new_theme)
        
        # 2. Change TTS mode
        if 'tts_mode' in settings and self.app.speaker:
            new_tts_mode = settings['tts_mode']
            if new_tts_mode != self.app.speaker.mode:
                print(f"🔄 Switching TTS mode: {self.app.speaker.mode} → {new_tts_mode}")
                self.app.speaker.set_mode(new_tts_mode)
                
                # Update voice if online
                if new_tts_mode == 'online' and 'tts_voice' in settings:
                    self.app.speaker.set_voice(settings['tts_voice'])
        
        # 3. Change TTS voice (if online)
        if 'tts_voice' in settings and self.app.speaker:
            if self.app.speaker.mode == 'online':
                self.app.speaker.set_voice(settings['tts_voice'])
                print(f"🔄 Voice changed to: {settings['tts_voice']}")
        
        # 3. AI Mode change (requires restart for now)
        if 'mode' in settings:
            new_mode = settings['mode']
            current_mode = self.app.brain.mode if self.app.brain else 'unknown'
            
            if new_mode != current_mode:
                print(f"⚠️ AI mode change ({current_mode} → {new_mode}) requires restart")
                return False  # Indicate restart needed
        
        # 4. Wake word (requires restart)
        if 'wake_word_enabled' in settings:
            print("⚠️ Wake word changes require restart")
        
        # 5. Gesture (requires restart)
        if 'gesture_enabled' in settings:
            print("⚠️ Gesture recognition changes require restart")
        
        return True
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings from user_settings.json"""
        return load_user_settings()


if __name__ == "__main__":
    # Test settings manager
    class MockApp:
        def __init__(self):
            self.brain = type('obj', (object,), {'mode': 'online'})()
            self.speaker = type('obj', (object,), {
                'mode': 'offline',
                'set_mode': lambda m: print(f"Set mode: {m}"),
                'set_voice': lambda v: print(f"Set voice: {v}")
            })()
    
    app = MockApp()
    manager = SettingsManager(app)
    
    # Test getting settings
    print("Current settings:")
    print(manager.get_current_settings())
    
    # Test applying settings
    print("\nApplying new settings...")
    manager.apply_settings({
        'mode': 'online',
        'tts_mode': 'online',
        'tts_voice': 'nova',
        'wake_word_enabled': False,
        'gesture_enabled': False
    })
