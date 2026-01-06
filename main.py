"""
SRUTHI-AI - Optimized 100% Offline Voice Assistant

Run with: python main.py

Requirements:
- Python 3.10+
- GGUF model file (local LLM)
- PyQt6 for GUI
- faster-whisper for STT
- pyttsx3 for TTS

Setup:
1. pip install -r requirements.txt
2. Set GGUF_MODEL_PATH in .env
3. python main.py

No internet required. Complete privacy.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import PyQt6 GUI
from gui import main

if __name__ == "__main__":
    print("=" * 60)
    print("Smart Assistant - 100% Offline AI Assistant")
    print("=" * 60)
    print("Starting application...")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
