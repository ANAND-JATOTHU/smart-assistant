"""
Settings Manager - Backend Implementation
Handles actual mode switching, feature toggling, and configuration
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv, set_key

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class SettingsManager:
    """Manage application settings with backend implementation"""
    
    def __init__(self, app):
        """
        Initialize settings manager
        
        Args:
            app: Main application instance
        """
        self.app = app
        self.env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(self.env_file)
    
    def apply_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Apply settings changes
        
        Args:
            settings: Dictionary of settings to apply
        
        Returns:
            bool: True if successful
        """
        try:
            # Save to .env file
            self._save_to_env(settings)
            
            # Apply runtime changes
            self._apply_runtime_changes(settings)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply settings: {e}")
            return False
    
    def _save_to_env(self, settings: Dict[str, Any]):
        """Save settings to .env file"""
        set_key(self.env_file, 'SRUTHI_MODE', settings.get('mode', 'online'))
        set_key(self.env_file, 'TTS_MODE', settings.get('tts_mode', 'offline'))
        set_key(self.env_file, 'TTS_VOICE', settings.get('tts_voice', 'alloy'))
        set_key(self.env_file, 'WAKE_WORD_ENABLED', str(settings.get('wake_word_enabled', False)).lower())
        set_key(self.env_file, 'GESTURE_ENABLED', str(settings.get('gesture_enabled', False)).lower())
        
        print("✅ Settings saved to .env")
    
    def _apply_runtime_changes(self, settings: Dict[str, Any]):
        """Apply settings changes at runtime (without restart)"""
        
        # 1. Change TTS mode
        if 'tts_mode' in settings and self.app.speaker:
            new_tts_mode = settings['tts_mode']
            if new_tts_mode != self.app.speaker.mode:
                print(f"🔄 Switching TTS mode: {self.app.speaker.mode} → {new_tts_mode}")
                self.app.speaker.set_mode(new_tts_mode)
                
                # Update voice if online
                if new_tts_mode == 'online' and 'tts_voice' in settings:
                    self.app.speaker.set_voice(settings['tts_voice'])
        
        # 2. Change TTS voice (if online)
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
        """Get current settings"""
        load_dotenv(self.env_file)
        
        return {
            'mode': os.getenv('SRUTHI_MODE', 'online'),
            'tts_mode': os.getenv('TTS_MODE', 'offline'),
            'tts_voice': os.getenv('TTS_VOICE', 'alloy'),
            'wake_word_enabled': os.getenv('WAKE_WORD_ENABLED', 'false').lower() == 'true',
            'gesture_enabled': os.getenv('GESTURE_ENABLED', 'false').lower() == 'true'
        }


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
