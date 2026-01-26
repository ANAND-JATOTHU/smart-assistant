"""
SRUTHI-AI Listener Module
Speech-to-Text using faster-whisper with GPU acceleration
"""

import os
import speech_recognition as sr
from faster_whisper import WhisperModel
from typing import Optional
import sys

# Import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_LANGUAGE,
    LISTEN_TIMEOUT,
    LISTEN_PHRASE_TIME_LIMIT,
    DEBUG_MODE
)


class SpeechListener:
    """Handles speech recognition using faster-whisper"""
    
    def __init__(self):
        """Initialize the Whisper model and microphone"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Load Whisper model
        print(f"Loading Whisper model: {WHISPER_MODEL} on {WHISPER_DEVICE}...")
        try:
            self.model = WhisperModel(
                WHISPER_MODEL,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE
            )
            print(f"✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"⚠️ GPU initialization failed, falling back to CPU: {e}")
            self.model = WhisperModel(
                WHISPER_MODEL,
                device="cpu",
                compute_type="int8"
            )
        
        # Adjust for ambient noise
        print("Calibrating for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!")
    
    def listen(self) -> Optional[str]:
        """
        Listen for speech and transcribe using Whisper
        
        Returns:
            str: Transcribed text, or None if error/timeout
        """
        try:
            print("\n🎤 Listening...")
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=LISTEN_PHRASE_TIME_LIMIT
                )
            
            print("🔄 Transcribing...")
            
            # Save audio to temporary WAV file
            temp_file = "temp_audio.wav"
            with open(temp_file, "wb") as f:
                f.write(audio.get_wav_data())
            
            try:
                # Transcribe with Whisper
                segments, info = self.model.transcribe(
                    temp_file,
                    language=WHISPER_LANGUAGE,
                    beam_size=5
                )
                
                # Extract text from segments
                transcription = " ".join([segment.text for segment in segments]).strip()
            finally:
                # Always clean up temp file, even if error occurs
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        if DEBUG_MODE:
                            print(f"⚠️ Failed to remove temp file: {e}")
            
            if transcription:
                print(f"✅ You said: {transcription}")
                return transcription
            else:
                print("⚠️ No speech detected")
                return None
                
        except sr.WaitTimeoutError:
            print("⏱️ Timeout: No speech detected")
            return None
        except Exception as e:
            print(f"❌ Error during listening: {e}")
            if DEBUG_MODE:
                import traceback
                traceback.print_exc()
            return None


def listen_for_speech() -> Optional[str]:
    """
    Convenience function to create a listener and capture speech
    
    Returns:
        str: Transcribed text or None
    """
    listener = SpeechListener()
    return listener.listen()


if __name__ == "__main__":
    # Test the listener
    print("=" * 60)
    print("SRUTHI-AI Listener Test")
    print("=" * 60)
    
    listener = SpeechListener()
    
    while True:
        result = listener.listen()
        if result:
            print(f"\nTranscription: {result}")
        
        continue_input = input("\nTry again? (y/n): ")
        if continue_input.lower() != 'y':
            break
