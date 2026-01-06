# 🚀 SRUTHI-AI Quick Start Guide - 100% Offline Mode

## Installation Steps

### 1. Install New Dependencies

```bash
# Activate virtual environment
.\env_sruthi\Scripts\Activate.ps1

# Install PyQt6 and update dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure your `.env` file has the correct GGUF model path:

```bash
# Edit .env file
notepad .env
```

Verify this line points to your GGUF model:
```
GGUF_MODEL_PATH=C:\path\to\your\model.gguf
```

### 3. Run SRUTHI-AI

```bash
# Make sure virtual environment is activated
.\env_sruthi\Scripts\Activate.ps1

# Launch the application
python main.py
```

## What's Changed?

### ✅ Now 100% Offline:
- **TTS**: pyttsx3 only (no gTTS, no edge-tts)
- **LLM**: Local GGUF models only (no Gemini, OpenAI, etc.)
- **STT**: faster-whisper (already offline)
- **GUI**: PyQt6 (replaced customtkinter)

### ❌ Removed Features:
- All online LLM providers (Gemini, OpenAI, Anthropic, Groq)
- Online TTS services (gTTS, edge-tts)
- Wake word detection (required API)  
- Gesture recognition
- Browser automation
- ChromaDB and vector embeddings

### ✅ New Features:
- Modern dark-themed PyQt6 GUI
- Threaded operations (non-blocking)
- Improved error handling
- Cleaner, simpler codebase

## First Time Setup

1. **Download a GGUF Model** (if you haven't already):
   - Visit [Hugging Face](https://huggingface.co/models?search=gguf)
   - Recommended models:
     - `TheBloke/CodeLlama-7B-Instruct-GGUF`
     - `TheBloke/Mistral-7B-Instruct-v0.2-GGUF`
     - `TheBloke/Llama-2-7B-Chat-GGUF`
   - Download a Q4 or Q5 quantized version (smaller, faster)

2. **Update Model Path**:
   ```bash
   # Copy example env file if needed
   copy .env.example .env
   
   # Edit and set GGUF_MODEL_PATH
   notepad .env
   ```

3. **Test Components**:
   ```bash
   # Test TTS
   python -c "from core.speaker import Speaker; s = Speaker(); s.speak('Hello')"
   
   # Test STT  
   python -c "from core.listener import SpeechListener; l = SpeechListener(); print('Ready')"
   
   # Test LLM
   python -c "from core.brain import AIBrain; b = AIBrain(); print(b.ask('Hi'))"
   ```

## Using the Application

1. **Launch**: `python main.py`

2. **Interface**:
   - **Speak Button (🎤)**: Click to start voice interaction
   - **Stop Button (🛑)**: Stop current speech
   - **Clear Button (🗑️)**: Clear conversation history

3. **Workflow**:
   - Click "Speak"
   - Say something into your microphone
   - Wait for AI to think and respond
   - Listen to the response

## Troubleshooting

### PyQt6 Not Found
```bash
pip install PyQt6 PyQt6-Qt6
```

### Model Not Loading
- Check GGUF_MODEL_PATH in `.env`
- Verify file exists
- Try reducing GGUF_GPU_LAYERS if out of VRAM

### Pyttsx3 Voice Issues
```python
# List available voices
from core.speaker import Speaker
s = Speaker()
voices = s.get_voices()
for v in voices:
    print(v)
```

### GUI Not Starting
- Ensure PyQt6 is installed
- Check console for error messages
- Try: `python gui/app_pyqt6.py` directly

## Performance Tips

### For Better Speed:
1. **Use GPU**: Set `GGUF_USE_GPU=true` in `.env`
2. **Increase GPU Layers**: Set `GGUF_GPU_LAYERS=35` or higher
3. **Use Smaller Model**: Try a 3B or 7B parameter model
4. **Reduce Context**: Lower `GGUF_CONTEXT_SIZE` to 2048

### For Lower VRAM:
1. **Reduce GPU Layers**: Set `GGUF_GPU_LAYERS=20` or lower
2. **Use smaller Whisper**: Set `WHISPER_MODEL=tiny` or `base`
3. **CPU Mode**: Set `GGUF_USE_GPU=false`

## Offline Verification

To verify 100% offline operation:

1. Disable WiFi/Ethernet completely
2. Run `python main.py`
3. Have a complete conversation
4. Everything should work without:
   - Connection errors
   - Timeout errors
   - API errors

## System Requirements

### Minimum:
- Python 3.10+
- 8GB RAM
- 5GB disk space + model size
- Windows 10/11

### Recommended:
- NVIDIA GPU with 6GB+ VRAM
- 16GB RAM
- SSD for faster model loading

---

## 🎉 You're Ready!

Your SRUTHI-AI is now completely offline and privacy-focused!

**No internet needed. No tracking. 100% local.**
