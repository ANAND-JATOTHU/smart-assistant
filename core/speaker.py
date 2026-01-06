"""
Smart Assistant Speaker Module - 100% Offline
Text-to-Speech using pyttsx3 only (no internet required)
"""

import os
import sys
from typing import Optional
import threading

# Import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import (
    PYTTSX3_RATE,
    PYTTSX3_VOLUME,
    DEBUG_MODE
)


class Speaker:
    """Offline text-to-speech using pyttsx3"""
    
    def __init__(self):
        """Initialize pyttsx3 TTS engine"""
        self.stop_requested = False
        self._speaking = False
        self._lock = threading.Lock()
        
        # Initialize pyttsx3 (offline TTS)
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # Select best available voice
            voices = self.engine.getProperty('voices')
            selected_voice = None
            
            print(f"📢 Available voices ({len(voices)}):")
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice.name} - {voice.id}")
            
            # Try to find Indian English female voice
            for voice in voices:
                voice_lower = voice.name.lower()
                if ('female' in voice_lower or 'woman' in voice_lower):
                    if ('india' in voice_lower or 'hindi' in voice_lower or 'zira' in voice_lower):
                        selected_voice = voice.id
                        print(f"✅ Selected voice: {voice.name}")
                        break
            
            # Fallback: any female voice
            if not selected_voice:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        selected_voice = voice.id
                        print(f"✅ Selected voice: {voice.name}")
                        break
            
            # Set voice if found, otherwise use default
            if selected_voice:
                self.engine.setProperty('voice', selected_voice)
            else:
                print("⚠️  Using default voice")
            
            # Set rate and volume
            self.engine.setProperty('rate', PYTTSX3_RATE)
            self.engine.setProperty('volume', PYTTSX3_VOLUME)
            
            print("✅ Pyttsx3 TTS initialized (100% Offline)")
            
        except Exception as e:
            print(f"❌ Failed to initialize pyttsx3: {e}")
            raise RuntimeError("Offline TTS engine (pyttsx3) not available!")
    
    def speak(self, text: str, language: Optional[str] = None) -> bool:
        """
        Speak text using pyttsx3 (offline)
        
        Args:
            text: Text to speak
            language: Ignored (pyttsx3 doesn't support language selection)
            
        Returns:
            bool: True if successful
        """
        if not text or not text.strip():
            return False
        
        with self._lock:
            if self._speaking:
                print("⚠️  Already speaking, please wait...")
                return False
            
            self._speaking = True
            self.stop_requested = False
        
        try:
            print(f"🔊 Speaking (offline): {text[:50]}...")
            
            # Check if stop was requested before speaking
            if self.stop_requested:
                self.stop_requested = False
                self._speaking = False
                return False
            
            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            
            print("✅ Speech completed")
            return True
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ Pyttsx3 error: {e}")
            return False
        finally:
            self._speaking = False
    
    def stop(self):
        """Stop current speech"""
        self.stop_requested = True
        try:
            self.engine.stop()
        except:
            pass
        print("🛑 Speech stopped")
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self._speaking
    
    def get_voices(self) -> list:
        """Get list of available voices"""
        try:
            return self.engine.getProperty('voices')
        except:
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice by ID"""
        try:
            self.engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            if DEBUG_MODE:
                print(f"Failed to set voice: {e}")
            return False
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        try:
            self.engine.setProperty('rate', rate)
        except Exception as e:
            if DEBUG_MODE:
                print(f"Failed to set rate: {e}")
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        try:
            self.engine.setProperty('volume', volume)
        except Exception as e:
            if DEBUG_MODE:
                print(f"Failed to set volume: {e}")


def speak_text(text: str, language: Optional[str] = None) -> bool:
    """
    Convenience function to speak text
    
    Args:
        text: Text to speak
        language: Ignored (kept for compatibility)
        
    Returns:
        bool: True if successful
    """
    speaker = Speaker()
    return speaker.speak(text, language)


if __name__ == "__main__":
    # Test the speaker
    print("=" * 60)
    print("SRUTHI-AI Speaker Test - Offline Mode")
    print("=" * 60)
    
    speaker = Speaker()
    
    # List available voices
    voices = speaker.get_voices()
    print(f"\nAvailable voices: {len(voices)}")
    for i, voice in enumerate(voices):
        print(f"  {i+1}. {voice.name}")
    
    # Test speaking
    test_texts = [
        "Hello! I am Smart Assistant, your offline voice assistant.",
        "I work completely offline without internet connection.",
        "Your privacy is protected."
    ]
    
    for text in test_texts:
        print(f"\nSpeaking: {text}")
        speaker.speak(text)
        import time
        time.sleep(0.5)
    
    print("\n✅ Speaker test completed!")
