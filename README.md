# Smart Assistant - 100% Offline AI Voice Assistant

🤖 **A Modern, ChatGPT-Style Voice Assistant** with GPU-accelerated STT, Local LLM, and Advanced PyQt6 GUI - Completely Offline!

## ✨ Features

- 🎤 **Speech Recognition**: GPU-accelerated Whisper (faster-whisper) - 100% Offline
- 🧠 **Local AI Brain**: GGUF models via llama-cpp-python - No Internet Required
- 🔊 **Text-to-Speech**: Pyttsx3 (offline only)
- 🎨 **Modern ChatGPT-Style GUI**: Dark-themed PyQt6 interface with chat history sidebar
- 💬 **Chat History**: Persistent conversations with sidebar navigation
- 🎬 **Smooth Animations**: PyQt6 animations for professional feel
- ⚙️ **System Commands**: Control volume, open apps, search Chrome/YouTube
- 🔒 **100% Privacy**: All processing happens locally - ZERO internet usage
- ⚡ **Non-blocking UI**: Threading ensures GUI never freezes
- 🌙 **Dark Theme**: Modern, easy-on-the-eyes interface

## 🏗️ Architecture

```
MVC (Model-View-Controller) Pattern:
├── Model (core/)       - Business logic (listener, brain, speaker)
├── View (gui/)         - PyQt6 ChatGPT-style interface
└── Controller (main.py) - Coordination
```

## 📋 Prerequisites

### 1. **Python 3.10+**
Ensure Python is installed and available in PATH.

### 2. **GGUF Model** (Required)
Download a GGUF model for local LLM inference:
- [Hugging Face GGUF Models](https://huggingface.co/models?search=gguf)
- Recommended: CodeLlama 7B, Mistral 7B, or Llama 3 8B
- Place the model file in your preferred location
- Update the path in `.env` file

### 3. **NVIDIA GPU** (Optional but Recommended)
For GPU-accelerated speech recognition and LLM inference.
- Works on CPU too, but slower!

## 🚀 Installation

### Step 1: Clone/Download Project
```bash
cd "c:\Users\JATOTHU ANAND\Desktop\sruthi ai"
```

### Step 2: Activate Virtual Environment
```bash
# PowerShell (Windows)
.\env_sruthi\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example environment file
copy .env.example .env

# Edit .env and set your GGUF model path
notepad .env
```

## 🎯 Usage

### Running the Application
```bash
# Make sure env_sruthi is activated
.\env_sruthi\Scripts\Activate.ps1

# Run Smart Assistant
python main.py
```

### Using the Interface

**Modern ChatGPT-Style Interface:**
- **Left Sidebar**: Browse and load previous conversations
- **Chat Area**: Message bubbles with smooth animations  
- **Input Box**: Type messages or use voice input
- **Voice Toggle**: Control voice output per message (🔊/🔇)

**Features:**
1. **Text Input**: Type your message and press Enter or click Send
2. **Voice Input**: Click 🎤 microphone button and speak
3. **Voice Control**: Toggle 🔊 button to enable/disable voice output
4. **Chat History**: Click any conversation in sidebar to load it
5. **New Chat**: Click "+ New Chat" to start fresh conversation
6. **System Commands**: 
   - "Increase volume"
   - "Search python tutorials on Chrome"
   - "Find cooking videos on YouTube"
   - "Open settings"

## ⚙️ System Commands

Smart Assistant can execute system commands naturally:

**Volume Control:**
```
"Increase the volume"
"Turn volume down"
"Set volume to 50"
"Mute"
```

**Search:**
```
"Search machine learning on Chrome"
"Find recipe videos on YouTube"
```

**System:**
```
"Open settings"
"Open calculator"
```

## 🛠️ Configuration

Edit `utils/config.py` or `.env` file to customize:

```python
# Whisper Model: tiny, base, small, medium, large
WHISPER_MODEL = "small"  # Default: optimized for 6GB VRAM

# GGUF Model Path
GGUF_MODEL_PATH = "path/to/your/model.gguf"

# GPU Settings
GGUF_GPU_LAYERS = 35  # Adjust based on your VRAM
GGUF_USE_GPU = True

# TTS Voice Settings
PYTTSX3_RATE = 160  # Words per minute
PYTTSX3_VOLUME = 0.9  # 0.0 to 1.0
```

## 📁 Project Structure

```
sruthi ai/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment configuration template
├── env_sruthi/            # Virtual environment
├── assets/                # Temp audio files
├── data/                  # Conversation memory
├── core/                  # MVC Model - Business Logic
│   ├── listener.py       # Speech-to-Text (Whisper)
│   ├── brain.py          # LLM Integration (GGUF)
│   ├── speaker.py        # Text-to-Speech (Pyttsx3)
│   └── memory.py         # Conversation memory
├── gui/                   # MVC View - User Interface
│   └── app_chatgpt_style.py  # Modern ChatGPT-style GUI
├── models/                # LLM abstraction layer
├── tools/                 # System tools
│   ├── applications.py   # App launcher & web search
│   ├── files.py          # File operations
│   └── system.py         # System controls & volume
├── intelligence/          # Command parsing
│   └── command_parser.py # Natural language command detection
└── utils/                 # Utilities
    └── config.py         # Configuration settings
```

## ⚠️ Troubleshooting

### "GGUF model not found"
- Make sure you downloaded a GGUF model
- Update `GGUF_MODEL_PATH` in `.env` file with correct path
- Verify file exists at the specified location

### "No NVIDIA GPU detected"
- Normal on CPU-only systems
- Will use CPU mode (slower but functional)
- Check with: `nvidia-smi`

### "Microphone not detected"
- Check microphone permissions in Windows Settings
- Ensure microphone is connected and set as default

### CUDA/GPU Issues
- Install CUDA Toolkit 11.8+ from NVIDIA
- Install PyTorch with CUDA support:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

## 📊 System Requirements

### Minimum
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8GB
- Disk: 5GB free space (+ model size)
- OS: Windows 10/11

### Recommended
- GPU: NVIDIA RTX 3050 (6GB VRAM) or better
- RAM: 16GB
- CPU: Modern multi-core processor
- OS: Windows 11

## 🔒 Privacy Features

- ✅ Speech recognition: 100% local (faster-whisper)
- ✅ AI reasoning: 100% local (GGUF model)
- ✅ Text-to-speech: 100% local (pyttsx3)
- ✅ **NO data sent to external servers**
- ✅ **NO internet connection required**
- ✅ **NO API keys needed**

## 📝 License

Created for educational purposes. Feel free to modify and distribute.

## 🙏 Acknowledgments

- **faster-whisper**: GPU-accelerated Whisper implementation
- **llama-cpp-python**: Local GGUF model inference
- **PyQt6**: Modern Python GUI framework
- **pyttsx3**: Offline text-to-speech

---

**Made with ❤️ for privacy-conscious AI enthusiasts**

**🔐 100% Offline | 🚫 Zero Tracking | 💯 Complete Privacy**
