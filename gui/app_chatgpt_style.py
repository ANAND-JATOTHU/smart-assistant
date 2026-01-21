"""
Smart Assistant - Enhanced GUI with Advanced Features
Modern interface with themes, animations, export, search, and voice visualization
"""

import sys
import os
import json
from datetime import datetime
from typing import Optional, List
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QScrollArea, 
    QFrame, QMessageBox, QDialog, QCheckBox, QComboBox, QSpinBox,
    QGridLayout, QListWidget, QListWidgetItem, QSplitter, QInputDialog,
    QFileDialog, QSlider, QProgressBar, QMenu, QSystemTrayIcon
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, 
    QEasingCurve, QRect, QSize, pyqtProperty, QPoint, QSequentialAnimationGroup
)
from PyQt6.QtGui import (
    QFont, QTextCursor, QIcon, QPixmap, QPalette, QColor, QPainter,
    QKeySequence, QShortcut, QAction
)

from core.listener import SpeechListener
from core.brain import AIBrain
from core.speaker import Speaker
from core.memory import Memory
from gui.themes import theme_manager, Theme
from core.document_processor import DocumentProcessor


class WorkerThread(QThread):
    """Background worker for voice/text processing"""
    
    # Signals
    status_update = pyqtSignal(str, str)
    user_message_ready = pyqtSignal(str)
    ai_message_complete = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, task_type, brain, speaker, listener=None, text=None, use_voice=True):
        super().__init__()
        self.task_type = task_type
        self.brain = brain
        self.speaker = speaker
        self.listener = listener
        self.text = text
        self.use_voice = use_voice
        self._stop_flag = False
    
    def run(self):
        """Execute the task"""
        try:
            if self.task_type == "voice_input":
                self._process_voice_input()
            elif self.task_type == "text_input":
                self._process_text_input()
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()
    
    def _process_voice_input(self):
        """Process voice input"""
        try:
            self.status_update.emit("🎤 Listening...", "#10a37f")
            user_text = self.listener.listen()
            
            if self._stop_flag or not user_text:
                self.status_update.emit("Ready", "#888")
                return
            
            self.user_message_ready.emit(user_text)
            self._get_ai_response(user_text)
            
        except Exception as e:
            self.error.emit(f"Voice processing error: {str(e)}")
    
    def _process_text_input(self):
        """Process text input"""
        try:
            if not self.text or self._stop_flag:
                return
            self._get_ai_response(self.text)
        except Exception as e:
            self.error.emit(f"Text processing error: {str(e)}")
    
    def _get_ai_response(self, user_input: str):
        """Get and process AI response"""
        try:
            self.status_update.emit("🤔 Thinking...", "#10a37f")
            ai_response = self.brain.ask(user_input)
            
            if self._stop_flag:
                return
            
            if not ai_response:
                ai_response = "I apologize, I couldn't generate a response."
            
            self.ai_message_complete.emit(ai_response)
            
            if self.use_voice and not self._stop_flag:
                self.status_update.emit("🔊 Speaking...", "#10a37f")
                self.speaker.speak(ai_response)
            
            self.status_update.emit("Ready", "#888")
            
        except Exception as e:
            self.error.emit(f"AI response error: {str(e)}")
    
    def stop(self):
        """Stop the worker"""
        self._stop_flag = True
        if self.speaker:
            self.speaker.stop()


class AnimatedButton(QPushButton):
    """Button with hover animation"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setGraphicsEffect(None)
        self._hover = False
        
    def enterEvent(self, event):
        """Animate on hover"""
        self._hover = True
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Remove animation"""
        self._hover = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)


class MessageBubble(QFrame):
    """Animated message bubble widget"""
    
    def __init__(self, message: str, is_user: bool, timestamp: str, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp
        self.parent_window = parent
        self.is_playing = False  # Track if audio is currently playing
        print(f"📦 Created MessageBubble: is_user={is_user}, message_preview={message[:30]}...")
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup the bubble UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # AI message header with play button
        if not self.is_user:
            header = QHBoxLayout()
            ai_label = QLabel("🤖 AI")
            ai_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            ai_label.setStyleSheet("color: #10a37f; background: transparent;")
            header.addWidget(ai_label)
            header.addStretch()
            
            self.play_btn = QPushButton("🔊")
            self.play_btn.setFixedSize(26, 26)
            self.play_btn.setToolTip("Play message")
            self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.play_btn.clicked.connect(self.play_message_audio)
            self.play_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: white;
                    border: none;
                    border-radius: 13px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #10a37f; }
            """)
            header.addWidget(self.play_btn)
            layout.addLayout(header)
        
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        message_label.setFont(QFont("Segoe UI", 10))
        
        time_label = QLabel(self.timestamp)
        time_label.setFont(QFont("Segoe UI", 8))
        
        layout.addWidget(message_label)
        layout.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        
        if self.is_user:
            self.setStyleSheet("""
                MessageBubble {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #10a37f, stop:1 #0d8c6e);
                    border-radius: 18px;
                    color: white;
                }
                QLabel {
                    background-color: transparent;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                MessageBubble {
                    background-color: #2b2b2b;
                    border: 1px solid #3d3d3d;
                    border-radius: 18px;
                    color: #e0e0e0;
                }
                QLabel {
                    background-color: transparent;
                    color: #e0e0e0;
                }
            """)
        
        self.setMaximumWidth(600)
    
    def _setup_animation(self):
        """Setup fade-in animation"""
        self.setWindowOpacity(0)
        
        # Fade in animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        QTimer.singleShot(50, self.fade_anim.start)
    
    def play_message_audio(self):
        """Toggle play/stop audio for this message bubble"""
        try:
            print(f"\n{'='*60}")
            print(f"🎵 AUDIO BUTTON CLICKED")
            print(f"   Message preview: {self.message[:50]}...")
            print(f"   Current state: is_playing={self.is_playing}")
            print(f"{'='*60}\n")
            
            # Check if currently playing - if so, STOP
            if self.is_playing:
                print("⏸️  STOP requested (button was in pause state)")
                if not self.parent_window:
                    print("❌ Error: parent_window is None")
                    return
                if hasattr(self.parent_window, 'stop_message_audio'):
                    print("✅ Calling parent window's stop_message_audio method")
                    self.parent_window.stop_message_audio()
                else:
                    print("❌ Error: parent_window does not have stop_message_audio method")
                return
            
            # Otherwise, PLAY
            print("🔊 PLAY requested (button was in play state)")
            
            # Verify parent window exists
            if not self.parent_window:
                print("❌ Error: parent_window is None")
                return
            
            # Verify parent has the play_message_audio method
            if not hasattr(self.parent_window, 'play_message_audio'):
                print(f"❌ Error: parent_window {type(self.parent_window)} does not have play_message_audio method")
                return
            
            # Call the parent window's play method
            print("✅ Calling parent window's play_message_audio method")
            self.parent_window.play_message_audio(self.message, self)
            
        except Exception as e:
            print(f"❌ Error in MessageBubble.play_message_audio: {e}")
            import traceback
            traceback.print_exc()
    
    def set_playing(self, playing: bool):
        """Update playing state and button UI"""
        print(f"🎨 MessageBubble.set_playing({playing}) called")
        self.is_playing = playing  # Update state
        if hasattr(self, 'play_btn'):
            if playing:
                print("   → Setting button to PAUSE icon (⏸)")
                self.play_btn.setText("⏸")
                self.play_btn.setStyleSheet("QPushButton { background-color: #10a37f; color: white; border: none; border-radius: 13px; font-size: 12px; } QPushButton:hover { background-color: #0d8c6e; }")
            else:
                print("   → Setting button to PLAY icon (🔊)")
                self.play_btn.setText("🔊")
                self.play_btn.setStyleSheet("QPushButton { background-color: #3d3d3d; color: white; border: none; border-radius: 13px; font-size: 12px; } QPushButton:hover { background-color: #10a37f; }")


class TypingIndicator(QFrame):
    """Animated typing indicator (three dots)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup UI"""
        self.setStyleSheet("""
            TypingIndicator {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 18px;
                padding: 15px 20px;
            }
        """)
        self.setMaximumWidth(80)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)
        
        # Create three dots
        self.dots = []
        for i in range(3):
            dot = QLabel("●")
            dot.setFont(QFont("Segoe UI", 12))
            dot.setStyleSheet("color: #888; background: transparent;")
            layout.addWidget(dot)
            self.dots.append(dot)
        
        self.setLayout(layout)
    
    def _setup_animation(self):
        """Setup pulsing animation for dots"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate_dots)
        self.current_dot = 0
        
    def start(self):
        """Start animation"""
        self.timer.start(400)
        self.show()
    
    def stop(self):
        """Stop animation"""
        self.timer.stop()
        self.hide()
    
    def _animate_dots(self):
        """Animate the dots"""
        # Reset all dots
        for dot in self.dots:
            dot.setStyleSheet("color: #888; background: transparent;")
        
        # Highlight current dot
        self.dots[self.current_dot].setStyleSheet("color: #10a37f; background: transparent;")
        self.current_dot = (self.current_dot + 1) % 3


class WelcomeScreen(QWidget):
    """Welcome screen shown when no conversation active"""
    
    quick_prompt_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup welcome UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Welcome title
        title = QLabel("👋 Welcome to Smart Assistant")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #10a37f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Your 100% Offline AI Assistant")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Offline badge
        badge = QLabel("🔒 Fully Offline • Privacy Protected")
        badge.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        badge.setStyleSheet("""
            background-color: #2b2b2b;
            color: #10a37f;
            padding: 10px 20px;
            border-radius: 20px;
            border: 1px solid #10a37f;
        """)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(40)
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(20)
        
        # Quick start tips
        tips_label = QLabel("Quick Start Tips:")
        tips_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tips_label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(tips_label)
        
        tips = [
            "🎤 Click the microphone to start voice chat",
            "⌨️ Type your message and press Enter",
            "🔊 Toggle voice output with the speaker button",
            "⌨️ Press Ctrl+N for new chat",
            "💾 Conversations auto-save in the sidebar"
        ]
        
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setFont(QFont("Segoe UI", 11))
            tip_label.setStyleSheet("color: #888; padding: 5px;")
            layout.addWidget(tip_label)
        
        layout.addSpacing(20)
        
        # Keyboard shortcuts
        shortcuts_label = QLabel("Keyboard Shortcuts:")
        shortcuts_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        shortcuts_label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(shortcuts_label)
        
        shortcuts = [
            "Ctrl+N - New Chat",
            "Ctrl+L - Start Voice Input",
            "Ctrl+K - Clear Current Chat",
            "Ctrl+E - Export Conversation",
            "Ctrl+, - Open Settings"
        ]
        
        for shortcut in shortcuts:
            sc_label = QLabel(shortcut)
            sc_label.setFont(QFont("Courier New", 10))
            sc_label.setStyleSheet("color: #888; padding: 3px;")
            layout.addWidget(sc_label)
        
        self.setLayout(layout)


class VoiceVisualization(QWidget):
    """Simple voice visualization widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.levels = [0.2] * 20
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_levels)
        self.timer.start(50)
        
    def update_levels(self):
        """Update audio levels"""
        import random
        self.levels = [random.random() * 0.8 for _ in range(20)]
        self.update()
        
    def paintEvent(self, event):
        """Paint the visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width() / len(self.levels)
        for i, level in enumerate(self.levels):
            height = level * self.height()
            x = i * width
            y = self.height() - height
            
            painter.fillRect(
                int(x), int(y), int(width - 2), int(height),
                QColor("#10a37f")
            )


class VolumeSliderPopup(QWidget):
    """Popup volume slider that appears on hover"""
    
    volume_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(60, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container with background
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(8, 12, 8, 12)
        
        # Volume label
        self.volume_label = QLabel("100%")
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_label.setStyleSheet("color: #e0e0e0; font-size: 11px; background: transparent; border: none;")
        container_layout.addWidget(self.volume_label)
        
        # Vertical slider
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)
        self.slider.setFixedHeight(90)
        self.slider.valueChanged.connect(self.on_slider_change)
        self.slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: #3d3d3d;
                width: 6px;
                border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: #10a37f;
                height: 16px;
                margin: 0 -5px;
                border-radius: 8px;
            }
            QSlider::handle:vertical:hover {
                background: #0d8c6e;
            }
        """)
        container_layout.addWidget(self.slider, 0, Qt.AlignmentFlag.AlignCenter)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        self.setLayout(layout)
    
    def on_slider_change(self, value):
        """Handle slider value change"""
        self.volume_label.setText(f"{value}%")
        self.volume_changed.emit(value)
    
    def set_volume(self, value):
        """Set slider value programmatically"""
        self.slider.setValue(value)
    
    def get_volume(self):
        """Get current volume"""
        return self.slider.value()


class QuickPromptsDialog(QDialog):
    """Dialog for quick prompt selection"""
    
    prompt_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Prompts")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        title = QLabel("Quick Prompts")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        
        # Categories with prompts
        self.prompts = {
            "💻 Code": [
                "Explain this code concept",
                "Debug my code",
                "Write a function for",
                "Best practices for",
                "Optimize this algorithm"
            ],
            "✍️ Writing": [
                "Write an email about",
                "Summarize this text",
                "Improve this paragraph",
                "Create a outline for",
                "Proofread and edit"
            ],
            "📊 Analysis": [
                "Analyze this data",
                "Compare and contrast",
                "Pros and cons of",
                "Explain the implications",
                "What are the key points?"
            ],
            "🎓 Learning": [
                "Teach me about",
                "What is the difference between",
                "Explain like I'm 5",
                "Give me examples of",
                "Quiz me on"
            ],
            "💡 Ideas": [
                "Brainstorm ideas for",
                "Creative solutions for",
                "Alternative approaches to",
                "Innovative ways to",
                "What if scenarios"
            ]
        }
        
        # Create tabs or list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout()
        
        for category, prompts in self.prompts.items():
            # Category header
            cat_label = QLabel(category)
            cat_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            cat_label.setStyleSheet("color: #10a37f; padding: 10px 0;")
            content_layout.addWidget(cat_label)
            
            # Prompt buttons
            for prompt in prompts:
                btn = QPushButton(prompt)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2b2b2b;
                        color: #e0e0e0;
                        border: 1px solid #3d3d3d;
                        border-radius: 8px;
                        padding: 12px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #3d3d3d;
                        border-color: #10a37f;
                    }
                """)
                btn.clicked.connect(lambda checked, p=prompt: self._select_prompt(p))
                content_layout.addWidget(btn)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }")
    
    def _select_prompt(self, prompt: str):
        """Handle prompt selection"""
        self.prompt_selected.emit(prompt)
        self.accept()


class ChatHistoryItem(QWidget):
    """Chat history list item"""
    
    clicked = pyqtSignal(str)
    rename_requested = pyqtSignal(str, str)  # conv_id, current_title
    delete_requested = pyqtSignal(str)  # conv_id
    
    def __init__(self, title: str, timestamp: str, conv_id: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.timestamp = timestamp
        self.conv_id = conv_id
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #e0e0e0;")
        
        time_label = QLabel(self.timestamp)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: #888;")
        
        layout.addWidget(title_label)
        layout.addWidget(time_label)
        
        self.setLayout(layout)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
            ChatHistoryItem {
                background-color: transparent;
                border-radius: 8px;
                padding: 8px;
            }
            ChatHistoryItem:hover {
                background-color: #2b2b2b;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.conv_id)
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())
        super().mousePressEvent(event)
    
    def show_context_menu(self, pos):
        """Show context menu with rename and delete options"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #10a37f;
            }
        """)
        
        rename_action = menu.addAction("✏️ Rename")
        delete_action = menu.addAction("🗑️ Delete")
        
        action = menu.exec(self.mapToGlobal(pos))
        
        if action == rename_action:
            self.rename_requested.emit(self.conv_id, self.title)
        elif action == delete_action:
            self.delete_requested.emit(self.conv_id)


class AttachedFileCard(QFrame):
    """Visual card for attached document files"""
    
    remove_requested = pyqtSignal(str)  # filename
    
    def __init__(self, filename: str, file_type: str, size: int, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.file_type = file_type
        self.size = size
        self._setup_ui()
    
    def _get_file_icon(self):
        """Get emoji icon based on file type"""
        icons = {
            'pdf': '📄',
            'document': '📝',
            'image': '🖼️',
            'video': '🎬'
        }
        return icons.get(self.file_type, '📎')
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable form"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _setup_ui(self):
        """Setup the file card UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # File icon
        icon_label = QLabel(self._get_file_icon())
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)
        
        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(self.filename)
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setStyleSheet("color: #e0e0e0; background: transparent;")
        name_label.setMaximumWidth(200)
        name_label.setWordWrap(False)
        # Ellipsis for long names
        name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        info_layout.addWidget(name_label)
        
        size_label = QLabel(f"{self.file_type.upper()} • {self._format_size(self.size)}")
        size_label.setFont(QFont("Segoe UI", 8))
        size_label.setStyleSheet("color: #888; background: transparent;")
        info_layout.addWidget(size_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setToolTip("Remove file")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.filename))
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
        """)
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            AttachedFileCard {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
            AttachedFileCard:hover {
                border-color: #10a37f;
            }
        """)
        self.setMaximumHeight(60)


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Assistant Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        
        # Device Settings
        device_group = QFrame()
        device_group.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        device_layout = QVBoxLayout()
        
        device_title = QLabel("🖥️ Device Configuration")
        device_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        device_title.setStyleSheet("color: #10a37f;")
        device_layout.addWidget(device_title)
        
        whisper_layout = QHBoxLayout()
        whisper_label = QLabel("Speech Recognition:")
        whisper_label.setStyleSheet("color: #e0e0e0;")
        whisper_layout.addWidget(whisper_label)
        self.whisper_device = QComboBox()
        self.whisper_device.addItems(["GPU (CUDA)", "CPU"])
        self.whisper_device.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        whisper_layout.addWidget(self.whisper_device)
        device_layout.addLayout(whisper_layout)
        
        llm_layout = QHBoxLayout()
        llm_label = QLabel("AI Brain:")
        llm_label.setStyleSheet("color: #e0e0e0;")
        llm_layout.addWidget(llm_label)
        self.llm_device = QComboBox()
        self.llm_device.addItems(["GPU (CUDA)", "CPU"])
        self.llm_device.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        llm_layout.addWidget(self.llm_device)
        device_layout.addLayout(llm_layout)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Voice Settings
        voice_group = QFrame()
        voice_group.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        voice_layout = QVBoxLayout()
        
        voice_title = QLabel("🔊 Voice Settings")
        voice_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        voice_title.setStyleSheet("color: #10a37f;")
        voice_layout.addWidget(voice_title)
        
        self.voice_default = QCheckBox("Enable voice by default")
        self.voice_default.setChecked(True)
        self.voice_default.setStyleSheet("color: #e0e0e0;")
        voice_layout.addWidget(self.voice_default)
        
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = AnimatedButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
        """)
        
        cancel_btn = AnimatedButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }")


class SmartAssistantWindow(QMainWindow):
    """Main window with sidebar and animations"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.init_components()
        
        # Initialize document processor
        self.document_processor = DocumentProcessor()
        self.attached_files = []  # Track attached documents
        
        # Setup UI
        self.init_ui()
        
        # State
        self.worker = None
        self.voice_enabled = True
        self.is_busy = False
        self.current_conversation_id = None
        self.loading_conversation = False  # Flag to prevent auto-scroll when loading
        self.sidebar_visible = True  # Sidebar visibility state
        
        # UI Elements for new features
        self.typing_indicator = None
        self.voice_viz = None
        self.welcome_screen = None
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Load chat history
        self.load_chat_history()
        
        # Update status
        self.update_status("Ready", "#888")
    
    def init_components(self):
        """Initialize AI components"""
        print("Initializing Smart Assistant components...")
        
        try:
            self.listener = SpeechListener()
            self.document_processor = DocumentProcessor()  # Initialize document processor first
            self.brain = AIBrain(document_processor=self.document_processor)  # Pass to brain for RAG
            self.speaker = Speaker()
            self.memory = Memory()
            print("✅ All components initialized")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Initialization Error",
                f"Failed to initialize components:\n{str(e)}\n\nPlease check your configuration."
            )
            sys.exit(1)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Smart Assistant")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main chat area
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        chat_layout.addWidget(header)
        
        # Chat area
        chat_area = self.create_chat_area()
        chat_layout.addWidget(chat_area, 1)
        
        # Input area
        input_area = self.create_input_area()
        chat_layout.addWidget(input_area)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("padding: 5px 15px; color: #888; background-color: #1e1e1e;")
        chat_layout.addWidget(self.status_label)
        
        chat_widget.setLayout(chat_layout)
        main_layout.addWidget(chat_widget, 1)
        
        central_widget.setLayout(main_layout)
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def create_input_area(self):
        """Create input area with buttons"""
        input_widget = QWidget()
        input_widget.setMaximumHeight(180)  # Increased for file cards
        input_widget.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #3d3d3d;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # File cards area (scrollable)
        self.files_scroll = QScrollArea()
        self.files_scroll.setWidgetResizable(True)
        self.files_scroll.setMaximumHeight(100)
        self.files_scroll.setVisible(False)  # Hidden by default
        self.files_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
        """)
        
        files_widget = QWidget()
        self.files_layout = QHBoxLayout()
        self.files_layout.setSpacing(8)
        self.files_layout.setContentsMargins(15, 8, 15, 8)
        self.files_layout.addStretch()
        files_widget.setLayout(self.files_layout)
        
        self.files_scroll.setWidget(files_widget)
        main_layout.addWidget(self.files_scroll)
        
        # Input row
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Hamburger menu (starts in sidebar)
        self.sidebar_ham_widget = QWidget()
        self.sidebar_ham_layout = QHBoxLayout()
        self.sidebar_ham_layout.setContentsMargins(10, 10, 10, 5)
        self.hamburger_btn = AnimatedButton("☰")
        self.hamburger_btn.setFixedSize(35, 35)
        self.hamburger_btn.setToolTip("Show Sidebar")
        self.hamburger_btn.clicked.connect(self.toggle_sidebar)
        self.hamburger_btn.setStyleSheet("""QPushButton { background: transparent; color: #e0e0e0; border: none; border-radius: 8px; font-size: 18px; } QPushButton:hover { background-color: #2b2b2b; }""")
        self.sidebar_ham_layout.addWidget(self.hamburger_btn)
        self.sidebar_ham_layout.addStretch()
        self.sidebar_ham_widget.setLayout(self.sidebar_ham_layout)
        self.sidebar_ham_widget.setVisible(False) # Hidden by default, shown when sidebar is hidden
        layout.addWidget(self.sidebar_ham_widget)
        
        # Attach button
        attach_btn = AnimatedButton("📎")
        attach_btn.setFixedSize(35, 35)
        attach_btn.setToolTip("Attach Document")
        attach_btn.clicked.connect(self.attach_document)
        attach_btn.setStyleSheet("""QPushButton { background: transparent; color: #e0e0e0; border: none; border-radius: 8px; font-size: 18px; } QPushButton:hover { background-color: #2b2b2b; }""")
        layout.addWidget(attach_btn)
        
        # Text input
        self.text_input = ResizingTextEdit()
        self.text_input.setPlaceholderText("Type your message or ask a question...")
        self.text_input.setFont(QFont("Segoe UI", 10))
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #10a37f;
            }
            QTextEdit:focus {
                border: 1px solid #10a37f;
            }
        """)
        self.text_input.textChanged.connect(self.update_send_button_state)
        self.text_input.installEventFilter(self) # For Enter key
        layout.addWidget(self.text_input)
        
        # Send button
        self.send_button = AnimatedButton("➤")
        self.send_button.setFixedSize(35, 35)
        self.send_button.setToolTip("Send Message")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""QPushButton { background-color: #10a37f; color: white; border: none; border-radius: 8px; font-size: 18px; } QPushButton:hover { background-color: #0d8c6e; } QPushButton:disabled { background-color: #3d3d3d; color: #888; }""")
        self.send_button.setEnabled(False) # Disabled by default
        layout.addWidget(self.send_button)
        
        # Voice input button
        self.voice_input_button = AnimatedButton("🎙️")
        self.voice_input_button.setFixedSize(35, 35)
        self.voice_input_button.setToolTip("Voice Input")
        self.voice_input_button.clicked.connect(self.toggle_voice_input)
        self.voice_input_button.setStyleSheet("""QPushButton { background: transparent; color: #e0e0e0; border: none; border-radius: 8px; font-size: 18px; } QPushButton:hover { background-color: #2b2b2b; }""")
        layout.addWidget(self.voice_input_button)
        
        main_layout.addLayout(layout)
        input_widget.setLayout(main_layout)
        return input_widget

    def create_sidebar(self):
        """Create sidebar with chat history and settings"""
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #3d3d3d;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Hamburger menu (starts in sidebar)
        self.sidebar_ham_widget = QWidget()
        self.sidebar_ham_layout = QHBoxLayout()
        self.sidebar_ham_layout.setContentsMargins(10, 10, 10, 5)
        self.hamburger_btn = AnimatedButton("☰")
        self.hamburger_btn.setFixedSize(35, 35)
        self.hamburger_btn.setToolTip("Hide Sidebar")
        self.hamburger_btn.clicked.connect(self.toggle_sidebar)
        self.hamburger_btn.setStyleSheet("""QPushButton { background: transparent; color: #e0e0e0; border: none; border-radius: 8px; font-size: 18px; } QPushButton:hover { background-color: #2b2b2b; }""")
        self.sidebar_ham_layout.addWidget(self.hamburger_btn)
        self.sidebar_ham_layout.addStretch()
        self.sidebar_ham_widget.setLayout(self.sidebar_ham_layout)
        layout.addWidget(self.sidebar_ham_widget)
        
        # New chat button
        new_chat_btn = AnimatedButton("+ New Chat")
        new_chat_btn.setFont(QFont("Segoe UI", 11))
        new_chat_btn.clicked.connect(self.new_chat)
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                margin: 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
        """)
        layout.addWidget(new_chat_btn)
        
        # Chat history label
        history_label = QLabel("Chat History")
        history_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        history_label.setStyleSheet("color: #888; padding: 10px 15px;")
        layout.addWidget(history_label)
        
        # Chat history list
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d3d3d, stop:1 #4d4d4d);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10a37f, stop:1 #0d8c6e);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(5, 5, 5, 5)
        self.history_layout.setSpacing(5)
        self.history_layout.addStretch()
        self.history_container.setLayout(self.history_layout)
        self.history_scroll.setWidget(self.history_container)
        
        layout.addWidget(self.history_scroll, 1)
        
        # Settings section
        settings_label = QLabel("Settings")
        settings_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        settings_label.setStyleSheet("color: #888; padding: 10px 15px; border-top: 1px solid #3d3d3d;")
        layout.addWidget(settings_label)
        
        # Settings button
        settings_btn = AnimatedButton("⚙️  Preferences")
        settings_btn.setFont(QFont("Segoe UI", 10))
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(settings_btn)
        
        # Quick Prompts button
        prompts_btn = AnimatedButton("💡  Quick Prompts")
        prompts_btn.setFont(QFont("Segoe UI", 10))
        prompts_btn.clicked.connect(self.show_quick_prompts)
        prompts_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(prompts_btn)
        
        # Voice Settings button
        voice_btn = AnimatedButton("🎙️  Voice Settings")
        voice_btn.setFont(QFont("Segoe UI", 10))
        voice_btn.clicked.connect(self.show_voice_selector)
        voice_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(voice_btn)
        
        # Search button
        search_btn = AnimatedButton("🔍  Search")
        search_btn.setFont(QFont("Segoe UI", 10))
        search_btn.clicked.connect(self.show_search_dialog)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(search_btn)
        
        # Statistics button
        stats_btn = AnimatedButton("📊  Statistics")
        stats_btn.setFont(QFont("Segoe UI", 10))
        stats_btn.clicked.connect(self.show_statistics)
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(stats_btn)
        
        # Export button
        export_btn = AnimatedButton("💾  Export Chat")
        export_btn.setFont(QFont("Segoe UI", 10))
        export_btn.clicked.connect(self.export_conversation)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(export_btn)
        
        # Clear all button
        clear_btn = AnimatedButton("🗑️  Clear All")
        clear_btn.setFont(QFont("Segoe UI", 10))
        clear_btn.clicked.connect(self.clear_all_chats)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 5px 10px 15px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
            }
        """)
        layout.addWidget(clear_btn)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_header(self):
        """Create header"""
        header = QWidget()
        header.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #3d3d3d;")
        header.setFixedHeight(60)
        
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Smart Assistant")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #10a37f;")
        self.header_layout.addWidget(title)
        self.header_layout.addStretch()
        
        header.setLayout(self.header_layout)
        return header
    
    def create_chat_area(self):
        """Create scrollable chat area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d3d3d, stop:1 #4d4d4d);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4d4d4d, stop:1 #5d5d5d);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(15)
        
        # Add welcome screen initially
        self.welcome_screen = WelcomeScreen()
        self.chat_layout.addWidget(self.welcome_screen)
        
        self.chat_layout.addStretch()
        
        self.chat_container.setLayout(self.chat_layout)
        self.chat_container.setStyleSheet("background-color: #1e1e1e;")
        scroll.setWidget(self.chat_container)
        
        return scroll
    
    def create_input_area(self):
        """Create input area"""
        input_widget = QWidget()
        input_widget.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #3d3d3d;")
        input_widget.setFixedHeight(80)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # 1. Stop button (always available)
        self.stop_btn = AnimatedButton("⏹")
        self.stop_btn.setToolTip("Stop audio (Esc)")
        self.stop_btn.setFixedSize(50, 50)
        self.stop_btn.clicked.connect(self.stop_audio)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.stop_btn)
        
        # 2. Audio toggle button with volume popup
        self.audio_toggle_btn = AnimatedButton("🔊")
        self.audio_toggle_btn.setCheckable(True)
        self.audio_toggle_btn.setChecked(True)  # Default: audio enabled
        self.audio_toggle_btn.setToolTip("Click: Toggle audio | Hover: Adjust volume")
        self.audio_toggle_btn.setFixedSize(50, 50)
        self.audio_toggle_btn.clicked.connect(self.toggle_audio)
        self.audio_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:checked {
                background-color: #10a37f;
            }
            QPushButton:!checked {
                background-color: #3d3d3d;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
        """)
        
        # Create volume popup
        self.volume_popup = VolumeSliderPopup(self)
        self.volume_popup.volume_changed.connect(self.on_volume_change_realtime)
        self.volume_popup.hide()
        
        # Install event filter to show popup on hover
        self.audio_toggle_btn.installEventFilter(self)
        self.audio_hover_timer = QTimer()
        self.audio_hover_timer.setSingleShot(True)
        self.audio_hover_timer.timeout.connect(self.show_volume_popup)
        
        layout.addWidget(self.audio_toggle_btn)
        
        # 3. Text input
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type a message...")
        self.input_box.setFont(QFont("Segoe UI", 11))
        self.input_box.returnPressed.connect(self.send_message)
        self.input_box.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 25px;
                padding: 12px 20px;
            }
            QLineEdit:focus {
                border: 2px solid #10a37f;
                background-color: #2b2b2b;
            }
            QLineEdit::placeholder {
                color: #888;
            }
        """)
        layout.addWidget(self.input_box, 1)
        
        # 4. Voice input button
        self.mic_btn = AnimatedButton("🎤")
        self.mic_btn.setFixedSize(50, 50)
        self.mic_btn.setToolTip("Voice input (Ctrl+L)")
        self.mic_btn.clicked.connect(self.start_voice_input)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        layout.addWidget(self.mic_btn)
        
        # 5. Attach button
        self.attach_btn = AnimatedButton("📎")
        self.attach_btn.setFixedSize(50, 50)
        self.attach_btn.setToolTip("Attach PDF, DOCX, images, videos")
        self.attach_btn.clicked.connect(self.show_file_picker)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        layout.addWidget(self.attach_btn)
        
        # 6. Send button
        self.send_btn = AnimatedButton("➤")
        self.send_btn.setFixedSize(50, 50)
        self.send_btn.setToolTip("Send message (Enter)")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
        """)
        layout.addWidget(self.send_btn)
        
        input_widget.setLayout(layout)
        return input_widget
    
    def apply_dark_theme(self):
        """Apply modern dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
        """)
    
    def load_chat_history(self):
        """Load chat history from memory"""
        try:
            conversations = self.memory.list_conversations(limit=20)
            
            # Clear existing items
            while self.history_layout.count() > 1:
                item = self.history_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add conversations
            for conv in conversations:
                conv_id = conv.get('id', '')
                title = conv.get('title', 'Untitled Chat')
                timestamp = conv.get('created_at', '')  # Fixed: use created_at
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%b %d, %I:%M %p")
                except:
                    time_str = "Recent"
                
                item = ChatHistoryItem(title, time_str, conv_id)
                item.clicked.connect(self.load_conversation)
                item.rename_requested.connect(self.rename_conversation)
                item.delete_requested.connect(self.delete_conversation)
                
                self.history_layout.insertWidget(self.history_layout.count() - 1, item)
        
        except Exception as e:
            print(f"Error loading chat history: {e}")
    
    def load_conversation(self, conv_id: str):
        """Load a conversation"""
        try:
            conv_data = self.memory.get_conversation(conv_id)  # Fixed: use get_conversation
            if not conv_data:
                self.show_error("Conversation not found")
                return
            
            # Clear current chat
            self.clear_current_chat()
            
            # Set flag to prevent auto-scroll
            self.loading_conversation = True
            
            # Load messages from 'messages' key
            messages = conv_data.get('messages', [])
            if messages:
                for msg in messages:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    
                    if role == 'user':
                        self.add_message_bubble(content, is_user=True)
                    elif role == 'assistant':
                        self.add_message_bubble(content, is_user=False)
                
                # Load conversation history into brain
                self.brain.conversation_history = messages.copy()
            
            self.current_conversation_id = conv_id
            self.update_status("Conversation loaded", "#10a37f")
            
            # Reset flag after loading
            self.loading_conversation = False
        
        except Exception as e:
            print(f"Error loading conversation: {e}")
            self.show_error(f"Failed to load conversation: {str(e)}")
    
    def add_message_bubble(self, message: str, is_user: bool):
        """Add a message bubble to chat"""
        # Hide welcome screen on first message
        if self.welcome_screen and self.welcome_screen.isVisible():
            self.welcome_screen.hide()
            self.chat_layout.removeWidget(self.welcome_screen)
        
        timestamp = datetime.now().strftime("%I:%M %p")
        bubble = MessageBubble(message, is_user, timestamp, self)
        
        # Remove stretch
        if self.chat_layout.count() > 0:
            item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
            if item.spacerItem():
                self.chat_layout.removeItem(item)
        
        # Add bubble
        if is_user:
            bubble_layout = QHBoxLayout()
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
            self.chat_layout.addLayout(bubble_layout)
        else:
            bubble_layout = QHBoxLayout()
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()
            self.chat_layout.addLayout(bubble_layout)
        
        # Add stretch back
        self.chat_layout.addStretch()
        
        # Scroll to bottom
        # Only scroll to bottom if NOT loading a conversation
        if not self.loading_conversation:
            QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility and move hamburger button"""
        if self.sidebar_visible:
            # Hide sidebar
            self.sidebar.hide()
            self.sidebar_visible = False
            # Move hamburger to header (before title)
            self.header_layout.insertWidget(0, self.hamburger_btn)
            self.hamburger_btn.setToolTip("Show Sidebar")
        else:
            # Show sidebar
            self.sidebar.show()
            self.sidebar_visible = True
            # Move hamburger back to sidebar
            ham_layout = self.sidebar.findChild(QHBoxLayout)
            if ham_layout:
                ham_layout.insertWidget(0, self.hamburger_btn)
            self.hamburger_btn.setToolTip("Hide Sidebar")
    
    def toggle_audio(self):
        """Toggle audio output on/off"""
        is_enabled = self.audio_toggle_btn.isChecked()
        if is_enabled:
            self.audio_toggle_btn.setText("🔊")
            self.voice_enabled = True
        else:
            self.audio_toggle_btn.setText("🔇")
            self.voice_enabled = False
    
    def eventFilter(self, obj, event):
        """Event filter to show volume popup on hover"""
        if obj == self.audio_toggle_btn:
            if event.type() == event.Type.Enter:
                # Mouse entered button
                self.audio_hover_timer.start(300)  # Show after 300ms hover
            elif event.type() == event.Type.Leave:
                # Mouse left button
                self.audio_hover_timer.stop()
                # Hide popup after a delay
                QTimer.singleShot(500, self.hide_volume_popup_if_not_hovered)
        return super().eventFilter(obj, event)
    
    def show_volume_popup(self):
        """Show volume slider popup"""
        if self.volume_popup.isVisible():
            return
        
        # Position popup above button
        btn_pos = self.audio_toggle_btn.mapToGlobal(self.audio_toggle_btn.rect().topLeft())
        popup_x = btn_pos.x() - 5
        popup_y = btn_pos.y() - self.volume_popup.height() - 5
        
        self.volume_popup.move(popup_x, popup_y)
        self.volume_popup.show()
    
    def hide_volume_popup_if_not_hovered(self):
        """Hide volume popup if mouse not over it"""
        if not self.volume_popup.underMouse() and not self.audio_toggle_btn.underMouse():
            self.volume_popup.hide()
    
    def on_volume_change_realtime(self, value):
        """Handle real-time volume changes from popup slider"""
        volume = value / 100.0
        self.speaker.set_volume(volume)
        # Update button appearance based on volume
        if value == 0:
            self.audio_toggle_btn.setText("🔇")
            self.audio_toggle_btn.setChecked(False)
            self.voice_enabled = False
        else:
            if value < 33:
                self.audio_toggle_btn.setText("🔉")
            else:
                self.audio_toggle_btn.setText("🔊")
            self.audio_toggle_btn.setChecked(True)
            self.voice_enabled = True
    
    def on_volume_change(self, value):
        """Handle volume slider change (for sidebar volume control if added)"""
        volume = value / 100.0
        self.speaker.set_volume(volume)
    
    def toggle_mute(self):
        """Toggle mute/unmute (for sidebar if added)"""
        pass  # Can be extended if volume slider added to sidebar
    
    def play_message_audio(self, message: str, bubble: 'MessageBubble'):
        """Play audio for a specific message"""
        try:
            print(f"\n{'='*60}")
            print("🎶 MAIN WINDOW: play_message_audio called")
            print(f"   Message preview: {message[:50]}...")
            print(f"   Bubble: {bubble}")
            print(f"{'='*60}\n")
            
            # Stop any currently playing message
            print("🛑 Stopping any currently playing audio first...")
            self.stop_message_audio()
            
            # Set this bubble as currently playing
            print(f"🎯 Setting bubble as currently playing")
            self.currently_playing_bubble = bubble
            bubble.set_playing(True)
            
            # Update status
            print("📊 Updating status bar")
            self.update_status("🔊 Playing message...", "#10a37f")
            
            # Create background thread for speaking
            print("🧵 Creating speak thread...")
            from PyQt6.QtCore import QThread, pyqtSignal
            class SpeakThread(QThread):
                finished = pyqtSignal()
                
                def __init__(self, speaker, text):
                    super().__init__()
                    self.speaker = speaker
                    self.text = text
                
                def run(self):
                    try:
                        print(f"🎙️  Thread: Starting to speak: {self.text[:30]}...")
                        self.speaker.speak(self.text)
                        print("✅ Thread: Speaking completed")
                    except Exception as e:
                        print(f"❌ Thread: Error speaking: {e}")
                    self.finished.emit()
            
            self.speak_thread = SpeakThread(self.speaker, message)
            self.speak_thread.finished.connect(lambda: self.on_speak_finished(bubble))
            print("▶️  Starting speak thread...")
            self.speak_thread.start()
            print("✅ Speak thread started successfully\n")
            
        except Exception as e:
            print(f"❌ Error in play_message_audio: {e}")
            import traceback
            traceback.print_exc()
            bubble.set_playing(False)
    
    
    def on_speak_finished(self, bubble):
        """Called when speaking finishes"""
        print(f"\n🏁 on_speak_finished called for bubble")
        bubble.set_playing(False)
        self.update_status("Ready", "#888")
        print("✅ Audio playback finished naturally\n")
    
    
    def stop_message_audio(self):
        """Stop currently playing message audio"""
        print(f"\n{'='*60}")
        print("🛑 STOP_MESSAGE_AUDIO called")
        print(f"{'='*60}\n")
        
        # Update UI status
        print("🎯 Updating status to 'Stopped'")
        self.update_status("Stopped", "#888")
        
        # Reset playing bubble
        if hasattr(self, 'currently_playing_bubble') and self.currently_playing_bubble:
            print(f"🔄 Resetting currently playing bubble (was playing: {self.currently_playing_bubble.is_playing})")
            self.currently_playing_bubble.set_playing(False)
            self.currently_playing_bubble = None
        else:
            print("⚠️  No currently playing bubble to reset")
        
        # Stop the speaker
        print("🔇 Stopping speaker...")
        if self.speaker:
            try:
                self.speaker.stop()
                print("✅ Speaker stopped successfully")
            except Exception as e:
                print(f"❌ Error stopping speaker: {e}")
        else:
            print("⚠️  No speaker instance found")
        
        # Stop the thread
        if hasattr(self, 'speak_thread') and self.speak_thread and self.speak_thread.isRunning():
            print("🧵 Terminating speak thread...")
            try:
                self.speak_thread.terminate()
                self.speak_thread.wait(500)
                print("✅ Thread terminated successfully")
            except Exception as e:
                print(f"❌ Error terminating thread: {e}")
        else:
            print("⚠️  No running speak thread to terminate")
        
        print(f"\n{'='*60}")
        print("✅ STOP_MESSAGE_AUDIO completed")
        print(f"{'='*60}\n")
    
    def stop_audio(self):
        """Stop current audio playback and cancel operation"""
        # Stop message audio
        self.stop_message_audio()
        
        # Stop speaker
        if self.speaker and self.speaker.is_speaking():
            self.speaker.stop()
        
        # Stop worker thread if running
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)
        
        # Re-enable inputs
        self.is_busy = False
        self.mic_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)
        
        self.update_status("Stopped", "#888")
    
    def show_file_picker(self):
        """Show file picker for document upload"""
        file_filter = "All Supported (*.pdf *.doc *.docx *.txt *.md *.png *.jpg *.jpeg *.webp *.mp4);;PDF Files (*.pdf);;Word Documents (*.doc *.docx);;Text Files (*.txt *.md);;Images (*.png *.jpg *.jpeg *.webp);;Videos (*.mp4 *.avi *.mkv)"
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Attach Files",
            "",
            file_filter
        )
        
        if files:
            for filepath in files:
                self.attach_document(filepath)
    
    def attach_document(self, filepath: str):
        """Process and attach a document with visual card"""
        try:
            # Process the document
            result = self.document_processor.process_file(filepath)
            
            # Add to attached files
            self.attached_files.append(result)
            
            # Create file card
            file_card = AttachedFileCard(
                result['filename'],
                result['type'],
                result['size'],
                self
            )
            file_card.remove_requested.connect(self.remove_attached_file)
            
            # Add card to layout (before stretch)
            self.files_layout.insertWidget(self.files_layout.count() - 1, file_card)
            
            # Show files area
            if not self.files_scroll.isVisible():
                self.files_scroll.setVisible(True)
            
            # Show notification with snippet
            filename = result['filename']
            file_type = result['type']
            text_preview = result.get('text', '')[:100] + "..." if result.get('text') else ""
            
            # Update attach button badge
            count = len(self.attached_files)
            self.attach_btn.setText(f"📎{count}" if count > 0 else "📎")
            if count > 0:
                self.attach_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #10a37f;
                        color: white;
                        border: none;
                        border-radius: 25px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0d8c6e;
                    }
                """)
            
            self.update_status(f"Attached {filename} ({file_type}) - Ready for questions!", "#10a37f")
            
        except Exception as e:
            QMessageBox.warning(self, "Attachment Error", f"Could not attach file:\n{str(e)}")
    
    def remove_attached_file(self, filename: str):
        """Remove a specific attached file"""
        # Find and remove from list
        self.attached_files = [f for f in self.attached_files if f['filename'] != filename]
        
        # Remove card from layout
        for i in range(self.files_layout.count()):
            item = self.files_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, AttachedFileCard) and widget.filename == filename:
                    widget.deleteLater()
                    break
        
        # Update UI
        count = len(self.attached_files)
        if count == 0:
            self.files_scroll.setVisible(False)
            self.attach_btn.setText("📎")
            self.attach_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """)
            # Clear document processor chunks
            if hasattr(self.document_processor, 'clear_documents'):
                self.document_processor.clear_documents()
        else:
            self.attach_btn.setText(f"📎{count}")
        
        self.update_status(f"Removed {filename}", "#888")
    
    def send_message(self):
        """Send text message"""
        text = self.input_box.text().strip()
        if not text or self.is_busy:
            return
        
        self.input_box.clear()
        self.add_message_bubble(text, is_user=True)
        self.process_message(text, from_voice=False)
    
    def start_voice_input(self):
        """Start voice input"""
        if self.is_busy:
            return
        self.process_message(None, from_voice=True)
    
    def process_message(self, text: Optional[str], from_voice: bool):
        """Process user message"""
        if self.is_busy:
            return
        
        self.is_busy = True
        # Only disable during listening/thinking, NOT during speaking
        # This allows user to interrupt and send new commands
        if from_voice:
            self.mic_btn.setEnabled(False)
            self.send_btn.setEnabled(False)
            self.input_box.setEnabled(False)
        
        task_type = "voice_input" if from_voice else "text_input"
        
        self.worker = WorkerThread(
            task_type,
            self.brain,
            self.speaker,
            self.listener if from_voice else None,
            text,
            self.voice_enabled  # Use voice_enabled flag
        )
        
        self.worker.status_update.connect(self.update_status)
        self.worker.user_message_ready.connect(lambda msg: self.add_message_bubble(msg, is_user=True))
        self.worker.ai_message_complete.connect(lambda msg: self.add_message_bubble(msg, is_user=False))
        self.worker.ai_message_complete.connect(self.on_ai_response_ready)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(self.on_worker_finished)
        
        self.worker.start()
    
    def on_ai_response_ready(self, msg):
        """Re-enable inputs when AI has responded (before/during speaking)"""
        # Re-enable inputs so user can type while audio plays
        self.mic_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)
        self.is_busy = False
    
    def on_worker_finished(self):
        """Handle worker completion"""
        self.is_busy = False
        self.mic_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()
        
        # Save current conversation if it has messages
        if len(self.brain.conversation_history) >= 2 and not self.current_conversation_id:
            # This is a new conversation, save it
            self.current_conversation_id = self.brain.save_current_conversation()
        
        # Reload chat history to show the saved conversation
        self.load_chat_history()
    
    def update_status(self, text: str, color: str):
        """Update status label"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"padding: 5px 15px; color: {color}; background-color: #1e1e1e;")
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        self.update_status("Error", "#e74c3c")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Settings", "Settings saved! Restart the application for changes to take effect.")
    
    def new_chat(self):
        """Start a new chat - saves current conversation first"""
        # Save current conversation if it has messages
        if len(self.brain.conversation_history) >= 2 and not self.current_conversation_id:
            # This is an unsaved conversation, save it before clearing
            self.current_conversation_id = self.brain.save_current_conversation()
            self.load_chat_history()  # Refresh sidebar to show saved chat
        
        # Now clear and start fresh
        self.clear_current_chat()
        self.current_conversation_id = None
        self.update_status("New chat started", "#10a37f")
    
    def clear_current_chat(self):
        """Clear current chat display"""
        # Remove all message bubbles
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear brain history
        self.brain.clear_history()
    
    def rename_conversation(self, conv_id: str, current_title: str):
        """Rename a conversation"""
        new_title, ok = QInputDialog.getText(
            self,
            "Rename Conversation",
            "Enter new title:",
            QLineEdit.EchoMode.Normal,
            current_title
        )
        
        if ok and new_title and new_title != current_title:
            try:
                # Get conversation data
                data = self.memory._read_data()
                for conv in data["conversations"]:
                    if conv["id"] == conv_id:
                        conv["title"] = new_title
                        conv["last_updated"] = datetime.now().isoformat()
                        break
                
                self.memory._write_data(data)
                self.load_chat_history()
                self.update_status(f"Renamed to: {new_title}", "#10a37f")
            except Exception as e:
                self.show_error(f"Failed to rename: {str(e)}")
    
    def delete_conversation(self, conv_id: str):
        """Delete a conversation"""
        reply = QMessageBox.question(
            self,
            "Delete Conversation",
            "Are you sure you want to delete this conversation?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete from memory
                self.memory.delete_conversation(conv_id)
                
                # If we're viewing this conversation, clear it
                if self.current_conversation_id == conv_id:
                    self.new_chat()
                
                # Reload chat history
                self.load_chat_history()
                self.update_status("Conversation deleted", "#10a37f")
            except Exception as e:
                self.show_error(f"Failed to delete: {str(e)}")
    
    def clear_all_chats(self):
        """Clear all chat history"""
        reply = QMessageBox.question(
            self,
            "Clear All Chats",
            "Are you sure you want to delete all chat history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_current_chat()
            self.load_chat_history()
            self.update_status("All chats cleared", "#888")
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # New chat
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.new_chat)
        
        # Voice input
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.start_voice_input)
        
        # Clear chat
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.clear_current_chat)
        
        # Export conversation
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_conversation)
        
        # Settings
        QShortcut(QKeySequence("Ctrl+,"), self).activated.connect(self.open_settings)
        
        # Search
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_search_dialog)
        
        # Quick prompts
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.show_quick_prompts)
        
        # Voice selection
        QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.show_voice_selector)
    
    def export_conversation(self):
        """Export current conversation"""
        if not self.brain.conversation_history:
            QMessageBox.information(self, "Export", "No conversation to export!")
            return
        
        # Ask for format
        format_dialog = QDialog(self)
        format_dialog.setWindowTitle("Export Conversation")
        format_dialog.setModal(True)
        format_dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        label = QLabel("Select export format:")
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(label)
        
        format_combo = QComboBox()
        format_combo.addItems(["Text (.txt)", "Markdown (.md)", "JSON (.json)"])
        format_combo.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        layout.addWidget(format_combo)
        
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
        """)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
        """)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(export_btn)
        layout.addLayout(btn_layout)
        
        format_dialog.setLayout(layout)
        format_dialog.setStyleSheet("QDialog { background-color: #1e1e1e; }")
        
        export_btn.clicked.connect(format_dialog.accept)
        cancel_btn.clicked.connect(format_dialog.reject)
        
        if format_dialog.exec() == QDialog.DialogCode.Accepted:
            format_type = format_combo.currentIndex()
            extensions = [".txt", ".md", ".json"]
            filters = [
                "Text Files (*.txt)",
                "Markdown Files (*.md)",
                "JSON Files (*.json)"
            ]
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Conversation",
                f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extensions[format_type]}",
                filters[format_type]
            )
            
            if filename:
                try:
                    self._export_to_file(filename, format_type)
                    QMessageBox.information(self, "Export", f"Conversation exported to:\n{filename}")
                    self.update_status("Conversation exported", "#10a37f")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")
    
    def _export_to_file(self, filename: str, format_type: int):
        """Export conversation to file"""
        messages = self.brain.conversation_history
        
        if format_type == 0:  # TXT
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Smart Assistant Conversation\n")
                f.write("=" * 50 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for msg in messages:
                    role = "You" if msg['role'] == 'user' else "AI"
                    f.write(f"{role}:\n{msg['content']}\n\n")
        
        elif format_type == 1:  # Markdown
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Smart Assistant Conversation\n\n")
                f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
                for msg in messages:
                    role = "👤 **You**" if msg['role'] == 'user' else "🤖 **AI**"
                    f.write(f"### {role}\n\n")
                    f.write(f"{msg['content']}\n\n")
                    f.write("---\n\n")
        
        elif format_type == 2:  # JSON
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "conversation_id": self.current_conversation_id,
                "messages": messages
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def show_search_dialog(self):
        """Show search dialog"""
        search_text, ok = QInputDialog.getText(
            self,
            "Search Conversations",
            "Enter search term:",
            QLineEdit.EchoMode.Normal
        )
        
        if ok and search_text:
            self._search_conversations(search_text)
    
    def _search_conversations(self, query: str):
        """Search conversations"""
        try:
            all_convs = self.memory.list_conversations(limit=100)
            matches = []
            
            for conv in all_convs:
                # Search in title
                if query.lower() in conv.get('title', '').lower():
                    matches.append(conv)
                    continue
                
                # Search in messages
                messages = conv.get('messages', [])
                for msg in messages:
                    if query.lower() in msg.get('content', '').lower():
                        matches.append(conv)
                        break
            
            if matches:
                # Show results in a dialog
                self._show_search_results(query, matches)
            else:
                QMessageBox.information(self, "Search", f"No results found for '{query}'")
        
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Search failed:\n{str(e)}")
    
    def _show_search_results(self, query: str, results: list):
        """Show search results dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Search Results: '{query}'")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        label = QLabel(f"Found {len(results)} result(s)")
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(label)
        
        # Results list
        results_list = QListWidget()
        results_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        
        for result in results:
            title = result.get('title', 'Untitled')
            timestamp = result.get('created_at', '')
            item = QListWidgetItem(f"{title} - {timestamp}")
            item.setData(Qt.ItemDataRole.UserRole, result.get('id'))
            results_list.addItem(item)
        
        results_list.itemDoubleClicked.connect(
            lambda item: self._load_search_result(item, dialog)
        )
        layout.addWidget(results_list)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
        """)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.setStyleSheet("QDialog { background-color: #1e1e1e; }")
        dialog.exec()
    
    def _load_search_result(self, item, dialog):
        """Load conversation from search result"""
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_conversation(conv_id)
        dialog.accept()
    
    def show_quick_prompts(self):
        """Show quick prompts dialog"""
        dialog = QuickPromptsDialog(self)
        dialog.prompt_selected.connect(self._use_quick_prompt)
        dialog.exec()
    
    def _use_quick_prompt(self, prompt: str):
        """Use selected quick prompt"""
        self.input_box.setText(prompt)
        self.input_box.setFocus()
    
    def show_voice_selector(self):
        """Show voice selection dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Voice Selection")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        title = QLabel("Select Voice")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        
        # Get available voices
        voices = self.speaker.get_voices()
        
        # Voice list
        voice_list = QListWidget()
        voice_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #10a37f;
            }
        """)
        
        for voice in voices:
            item = QListWidgetItem(voice.name)
            item.setData(Qt.ItemDataRole.UserRole, voice.id)
            voice_list.addItem(item)
        
        layout.addWidget(voice_list)
        
        # Voice speed
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet("color: #e0e0e0;")
        speed_layout.addWidget(speed_label)
        
        speed_slider = QSlider(Qt.Orientation.Horizontal)
        speed_slider.setMinimum(50)
        speed_slider.setMaximum(300)
        speed_slider.setValue(150)
        speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #3d3d3d;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #10a37f;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        speed_layout.addWidget(speed_slider)
        
        speed_value = QLabel("150 WPM")
        speed_value.setStyleSheet("color: #888;")
        speed_layout.addWidget(speed_value)
        
        speed_slider.valueChanged.connect(
            lambda v: speed_value.setText(f"{v} WPM")
        )
        
        layout.addLayout(speed_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test Voice")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        test_btn.clicked.connect(
            lambda: self._test_voice(voice_list.currentItem())
        )
        
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
        """)
        apply_btn.clicked.connect(
            lambda: self._apply_voice(voice_list.currentItem(), speed_slider.value(), dialog)
        )
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
        """)
        
        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.setStyleSheet("QDialog { background-color: #1e1e1e; }")
        dialog.exec()
    
    def _test_voice(self, item):
        """Test selected voice"""
        if item:
            voice_id = item.data(Qt.ItemDataRole.UserRole)
            self.speaker.set_voice(voice_id)
            self.speaker.speak("Hello! This is how I sound.")
    
    def _apply_voice(self, item, speed, dialog):
        """Apply voice settings"""
        if item:
            voice_id = item.data(Qt.ItemDataRole.UserRole)
            self.speaker.set_voice(voice_id)
            self.speaker.set_rate(speed)
            QMessageBox.information(self, "Voice Settings", "Voice settings applied!")
            dialog.accept()
    
    def show_statistics(self):
        """Show statistics dashboard"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Statistics")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        title = QLabel("📊 Statistics Dashboard")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #10a37f;")
        layout.addWidget(title)
        
        # Calculate statistics
        all_convs = self.memory.list_conversations(limit=1000)
        total_convs = len(all_convs)
        total_messages = sum(len(c.get('messages', [])) for c in all_convs)
        
        stats_layout = QGridLayout()
        stats = [
            ("Total Conversations:", str(total_convs)),
            ("Total Messages:", str(total_messages)),
            ("Current Conversation:", str(len(self.brain.conversation_history)) + " messages"),
        ]
        
        for i, (label, value) in enumerate(stats):
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 11))
            label_widget.setStyleSheet("color: #e0e0e0;")
            
            value_widget = QLabel(value)
            value_widget.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            value_widget.setStyleSheet("color: #10a37f;")
            
            stats_layout.addWidget(label_widget, i, 0)
            stats_layout.addWidget(value_widget, i, 1)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.reject)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
        """)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.setStyleSheet("QDialog { background-color: #1e1e1e; }")
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Assistant")
    app.setStyle("Fusion")
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
    palette.setColor(QPalette.ColorRole.Base, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))
    palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(224, 224, 224))
    app.setPalette(palette)
    
    window = SmartAssistantWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
