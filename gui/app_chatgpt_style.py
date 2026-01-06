"""
Smart Assistant - Advanced GUI with Sidebar & Animations
Modern interface with chat history sidebar, settings, and PyQt6 animations
"""

import sys
import os
from datetime import datetime
from typing import Optional, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QScrollArea, 
    QFrame, QMessageBox, QDialog, QCheckBox, QComboBox, QSpinBox,
    QGridLayout, QListWidget, QListWidgetItem, QSplitter, QInputDialog
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, 
    QEasingCurve, QRect, QSize, pyqtProperty
)
from PyQt6.QtGui import (
    QFont, QTextCursor, QIcon, QPixmap, QPalette, QColor, QPainter
)

from core.listener import SpeechListener
from core.brain import AIBrain
from core.speaker import Speaker
from core.memory import Memory


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
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup the bubble UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
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
        
        # Setup UI
        self.init_ui()
        
        # State
        self.worker = None
        self.voice_enabled = True
        self.is_busy = False
        self.current_conversation_id = None
        self.loading_conversation = False  # Flag to prevent auto-scroll when loading
        
        # Load chat history
        self.load_chat_history()
        
        # Update status
        self.update_status("Ready", "#888")
    
    def init_components(self):
        """Initialize AI components"""
        print("Initializing Smart Assistant components...")
        
        try:
            self.listener = SpeechListener()
            self.brain = AIBrain()
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
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
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
    
    def create_sidebar(self):
        """Create sidebar with chat history and settings"""
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #3d3d3d;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
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
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Smart Assistant")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #10a37f;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        header.setLayout(layout)
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
        
        # Voice toggle
        self.voice_btn = AnimatedButton("🔊")
        self.voice_btn.setCheckable(True)
        self.voice_btn.setChecked(True)
        self.voice_btn.setToolTip("Toggle voice output")
        self.voice_btn.clicked.connect(self.toggle_voice)
        self.voice_btn.setFixedSize(50, 50)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
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
        layout.addWidget(self.voice_btn)
        
        # Text input - FIXED: Dark text on light background
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
        layout.addWidget(self.input_box)
        
        # Microphone button
        self.mic_btn = AnimatedButton("🎤")
        self.mic_btn.setToolTip("Voice input")
        self.mic_btn.clicked.connect(self.start_voice_input)
        self.mic_btn.setFixedSize(50, 50)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
            }
        """)
        layout.addWidget(self.mic_btn)
        
        # Send button
        self.send_btn = AnimatedButton("➤")
        self.send_btn.setToolTip("Send message")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setFixedSize(50, 50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #0d8c6e;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
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
        timestamp = datetime.now().strftime("%I:%M %p")
        bubble = MessageBubble(message, is_user, timestamp)
        
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
    
    def toggle_voice(self):
        """Toggle voice output"""
        self.voice_enabled = self.voice_btn.isChecked()
        if self.voice_enabled:
            self.voice_btn.setText("🔊")
        else:
            self.voice_btn.setText("🔇")
    
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
            self.voice_enabled
        )
        
        self.worker.status_update.connect(self.update_status)
        self.worker.user_message_ready.connect(lambda msg: self.add_message_bubble(msg, is_user=True))
        self.worker.ai_message_complete.connect(lambda msg: self.add_message_bubble(msg, is_user=False))
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(self.on_worker_finished)
        
        self.worker.start()
    
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
