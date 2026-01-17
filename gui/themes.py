"""
Smart Assistant Theme System
Provides multiple themes with easy switching capability
"""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication
from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Theme configuration"""
    name: str
    # Main colors
    background: str
    surface: str
    primary: str
    primary_hover: str
    secondary: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    
    # UI element colors
    border: str
    input_bg: str
    input_border: str
    input_focus_border: str
    
    # Message bubble colors
    user_bubble_bg: str
    user_bubble_text: str
    ai_bubble_bg: str
    ai_bubble_text: str
    
    # Status colors
    success: str
    error: str
    warning: str
    info: str


# Dark Theme (Current)
DARK_THEME = Theme(
    name="Dark",
    background="#1e1e1e",
    surface="#2b2b2b",
    primary="#10a37f",
    primary_hover="#0d8c6e",
    secondary="#3d3d3d",
    
    text_primary="#e0e0e0",
    text_secondary="#888",
    text_disabled="#555",
    
    border="#3d3d3d",
    input_bg="#2b2b2b",
    input_border="#3d3d3d",
    input_focus_border="#10a37f",
    
    user_bubble_bg="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10a37f, stop:1 #0d8c6e)",
    user_bubble_text="#ffffff",
    ai_bubble_bg="#2b2b2b",
    ai_bubble_text="#e0e0e0",
    
    success="#10a37f",
    error="#e74c3c",
    warning="#f39c12",
    info="#3498db"
)

# Light Theme
LIGHT_THEME = Theme(
    name="Light",
    background="#ffffff",
    surface="#f5f5f5",
    primary="#10a37f",
    primary_hover="#0d8c6e",
    secondary="#e0e0e0",
    
    text_primary="#2b2b2b",
    text_secondary="#666666",
    text_disabled="#cccccc",
    
    border="#d0d0d0",
    input_bg="#ffffff",
    input_border="#d0d0d0",
    input_focus_border="#10a37f",
    
    user_bubble_bg="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10a37f, stop:1 #0d8c6e)",
    user_bubble_text="#ffffff",
    ai_bubble_bg="#f5f5f5",
    ai_bubble_text="#2b2b2b",
    
    success="#10a37f",
    error="#e74c3c",
    warning="#f39c12",
    info="#3498db"
)

# High Contrast Theme
HIGH_CONTRAST_THEME = Theme(
    name="High Contrast",
    background="#000000",
    surface="#1a1a1a",
    primary="#00ff00",
    primary_hover="#00cc00",
    secondary="#333333",
    
    text_primary="#ffffff",
    text_secondary="#cccccc",
    text_disabled="#666666",
    
    border="#ffffff",
    input_bg="#000000",
    input_border="#ffffff",
    input_focus_border="#00ff00",
    
    user_bubble_bg="#00ff00",
    user_bubble_text="#000000",
    ai_bubble_bg="#1a1a1a",
    ai_bubble_text="#ffffff",
    
    success="#00ff00",
    error="#ff0000",
    warning="#ffff00",
    info="#00ffff"
)

# Midnight Blue Theme
MIDNIGHT_THEME = Theme(
    name="Midnight Blue",
    background="#0f1419",
    surface="#1a1f2e",
    primary="#4a9eff",
    primary_hover="#3a8eef",
    secondary="#2d3748",
    
    text_primary="#e2e8f0",
    text_secondary="#94a3b8",
    text_disabled="#64748b",
    
    border="#2d3748",
    input_bg="#1a1f2e",
    input_border="#2d3748",
    input_focus_border="#4a9eff",
    
    user_bubble_bg="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9eff, stop:1 #3a8eef)",
    user_bubble_text="#ffffff",
    ai_bubble_bg="#1a1f2e",
    ai_bubble_text="#e2e8f0",
    
    success="#10b981",
    error="#ef4444",
    warning="#f59e0b",
    info="#3b82f6"
)


class ThemeManager:
    """Manages theme switching and application"""
    
    THEMES: Dict[str, Theme] = {
        "dark": DARK_THEME,
        "light": LIGHT_THEME,
        "high_contrast": HIGH_CONTRAST_THEME,
        "midnight": MIDNIGHT_THEME,
    }
    
    def __init__(self):
        self.current_theme = DARK_THEME
    
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name.lower() in self.THEMES:
            self.current_theme = self.THEMES[theme_name.lower()]
            return True
        return False
    
    def get_theme(self) -> Theme:
        """Get current theme"""
        return self.current_theme
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.THEMES.keys())
    
    def apply_to_palette(self, app: QApplication):
        """Apply theme to Qt palette"""
        palette = QPalette()
        theme = self.current_theme
        
        # Parse colors
        bg_color = QColor(theme.background)
        surface_color = QColor(theme.surface)
        text_color = QColor(theme.text_primary)
        
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, surface_color)
        palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, surface_color)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        
        app.setPalette(palette)
    
    def get_stylesheet(self, widget_type: str = "main") -> str:
        """Get stylesheet for specific widget type"""
        theme = self.current_theme
        
        if widget_type == "main":
            return f"""
                QMainWindow {{
                    background-color: {theme.background};
                }}
                QWidget {{
                    background-color: {theme.background};
                    color: {theme.text_primary};
                }}
            """
        
        elif widget_type == "input":
            return f"""
                QLineEdit {{
                    background-color: {theme.input_bg};
                    color: {theme.text_primary};
                    border: 1px solid {theme.input_border};
                    border-radius: 25px;
                    padding: 12px 20px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {theme.input_focus_border};
                    background-color: {theme.input_bg};
                }}
                QLineEdit::placeholder {{
                    color: {theme.text_secondary};
                }}
            """
        
        elif widget_type == "button_primary":
            return f"""
                QPushButton {{
                    background-color: {theme.primary};
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 20px;
                }}
                QPushButton:hover {{
                    background-color: {theme.primary_hover};
                }}
                QPushButton:disabled {{
                    background-color: {theme.secondary};
                }}
            """
        
        elif widget_type == "user_bubble":
            return f"""
                MessageBubble {{
                    background: {theme.user_bubble_bg};
                    border-radius: 18px;
                    color: {theme.user_bubble_text};
                }}
                QLabel {{
                    background-color: transparent;
                    color: {theme.user_bubble_text};
                }}
            """
        
        elif widget_type == "ai_bubble":
            return f"""
                MessageBubble {{
                    background-color: {theme.ai_bubble_bg};
                    border: 1px solid {theme.border};
                    border-radius: 18px;
                    color: {theme.ai_bubble_text};
                }}
                QLabel {{
                    background-color: transparent;
                    color: {theme.ai_bubble_text};
                }}
            """
        
        return ""


# Global theme manager instance
theme_manager = ThemeManager()


if __name__ == "__main__":
    # Test theme manager
    print("Available themes:")
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        theme = theme_manager.get_theme()
        print(f"  - {theme.name}: {theme.background}")
