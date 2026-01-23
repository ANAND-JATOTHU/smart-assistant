# Changelog

## [1.2.0] - 2026-01-23

### Improved
- **Modern GUI Visual Design** - Premium, state-of-the-art interface
  - Vibrant cyan/teal gradient color scheme
  - Deeper, richer black backgrounds for better contrast
  - Enhanced typography with larger, more readable fonts
  - Message bubbles with subtle shadows for depth perception
  - Smooth rounded corners (20px) throughout the UI
  - Improved button designs with hover effects
  - Modern typing indicator with cyan accent
  - Enhanced welcome screen with better visual hierarchy
  - Better color contrast for improved readability
  - Consistent spacing and modern aesthetics

## [1.1.0] - 2026-01-20

### Fixed
- Duplicate `__init__` method in VoiceVisualization class that prevented proper initialization

## [1.0.1] - 2026-01-18

### Added
- **RAG (Retrieval Augmented Generation)** - Intelligent document Q&A system
  - Text chunking with overlap for better context preservation
  - Offline semantic search using sentence-transformers
  - Automatic embedding generation for uploaded documents
  - Context-aware AI responses based on document content
- **Enhanced File Upload GUI**
  - Visual file cards with icons, names, and sizes
  - Scrollable file preview panel
  - Individual file removal with ✕ button
  - File count badge on attach button
  - Support for PDF, DOCX, TXT, MD, images (OCR)
- Per-message audio playback buttons on AI responses
- Document upload system supporting PDF, DOCX, TXT, and images
- OCR support for extracting text from images
- Hover-based volume control slider
- Collapsible sidebar with dynamic hamburger menu
- Stop button for interrupting audio playback
- Theme management system

### Fixed
- TTS engine reliability - now works consistently on every response
- Audio playback button click handler
- Non-blocking audio playback
- Input fields remain enabled during TTS

### Changed
- Simplified input area to 5 essential buttons
- Hamburger menu repositions between sidebar and header
- Volume control via hover popup instead of static slider

## [1.0.0] - 2026-01-06

### Added
- Initial release
- 100% offline AI assistant
- Local GGUF model support
- Faster-Whisper STT
- pyttsx3 TTS
- Chat history management
- Voice input/output
