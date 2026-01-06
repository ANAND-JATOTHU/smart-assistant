"""
Configuration settings for Smart Assistant - 100% Offline Mode
Environment variables and constants
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# MODE SETTINGS (Always Offline)
# ============================================================================
MODE = "offline"  # Always offline - no internet required

# ============================================================================
# LLM SETTINGS (GGUF Model - Offline Only)
# ============================================================================
GGUF_MODEL_PATH = os.getenv('GGUF_MODEL_PATH', r"C:\Users\JATOTHU ANAND\Desktop\Smart Real-time Unified Tool for Human-AI Interaction sruthi-ai\assistant\codellama-7b-instruct.Q4_K_M.gguf")
GGUF_USE_GPU = True  # GPU acceleration (CUDA)
GGUF_GPU_LAYERS = 35  # Layers to offload to GPU (0-40 for 7B models, adjust based on VRAM)
GGUF_CONTEXT_SIZE = 4096  # Context window size
GGUF_MAX_TOKENS = 512  # Max tokens per response
GGUF_TEMPERATURE = 0.7  # Creativity (0.0-1.0, lower = more focused)
GGUF_TIMEOUT = 60  # seconds

# ============================================================================
# WHISPER (STT) SETTINGS - Offline Speech Recognition
# ============================================================================
# Model size options: tiny, base, small, medium, large
WHISPER_MODEL = "small"  # Supports 90+ languages offline
WHISPER_DEVICE = "cuda"  # Options: cuda, cpu, auto
WHISPER_COMPUTE_TYPE = "float16"  # Options: float16, int8 (float16 for GPU)
WHISPER_LANGUAGE = None  # Auto-detect (supports Telugu, Hindi, English, etc.)

# ============================================================================
# TTS SETTINGS (Pyttsx3 - Offline Only)
# ============================================================================
PYTTSX3_VOICE_GENDER = "female"  # Prefer female voice
PYTTSX3_VOICE_LANGUAGE = "en-IN"  # Indian English (if available)
PYTTSX3_RATE = 160  # Words per minute
PYTTSX3_VOLUME = 0.9  # 0.0 to 1.0

# ============================================================================
# AUDIO SETTINGS
# ============================================================================
LISTEN_TIMEOUT = 10  # seconds to wait for speech
LISTEN_PHRASE_TIME_LIMIT = 30  # max seconds to record (longer for complete sentences)
TEMP_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "temp")

# ============================================================================
# MEMORY SETTINGS
# ============================================================================
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "memory.json")
AUTO_SAVE_CONVERSATIONS = True  # Auto-save conversations after N messages
AUTO_SAVE_THRESHOLD = 4  # Save after this many messages (2 Q&A pairs)

# ============================================================================
# GUI SETTINGS (PyQt6)
# ============================================================================
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Smart Assistant - Offline Voice Assistant"
THEME = "dark"
APPEARANCE_MODE = "dark"

# Colors (Dark Theme)
COLOR_USER_MESSAGE = "#1f538d"
COLOR_AI_MESSAGE = "#2d2d2d"
COLOR_STATUS_READY = "#2ecc71"
COLOR_STATUS_LISTENING = "#f39c12"
COLOR_STATUS_THINKING = "#e67e22"
COLOR_STATUS_SPEAKING = "#3498db"
COLOR_STATUS_ERROR = "#e74c3c"

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_SIZE_CHAT = 11
FONT_SIZE_STATUS = 10
FONT_SIZE_BUTTON = 12

# ============================================================================
# TOOL EXECUTION SETTINGS
# ============================================================================
TOOLS_ENABLED = True
TOOLS_REQUIRE_CONFIRMATION = True  # Confirm dangerous actions
TOOLS_ALLOW_FILE_DELETE = False  # Extra safety for file deletion

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================
DEBUG_MODE = True  # Enable debug logging
LOG_CONVERSATIONS = False  # Save conversation history to file

# Create temp directory if it doesn't exist
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
