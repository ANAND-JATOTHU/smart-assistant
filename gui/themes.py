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


# Dark Theme - Modern & Vibrant
DARK_THEME = Theme(
    name="Dark",
    background="#0a0a0a",  # Deeper black
    surface="#1a1a1a",     # Richer dark gray
    primary="#00d9ff",     # Vibrant cyan
    primary_hover="#00b8d4",
    secondary="#2d2d2d",
    
    text_primary="#ffffff",     # Pure white for better contrast
    text_secondary="#a0a0a0",   # Lighter secondary text
    text_disabled="#666666",
    
    border="#2d2d2d",
    input_bg="#1a1a1a",
    input_border="#2d2d2d",
    input_focus_border="#00d9ff",
    
    user_bubble_bg="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00d9ff, stop:1 #10a37f)",
    user_bubble_text="#ffffff",
    ai_bubble_bg="#1a1a1a",
    ai_bubble_text="#ffffff",
    
    success="#00d9ff",
    error="#ff6b6b",
    warning="#ffd93d",
    info="#6c63ff"
)

# Light Theme - Modern & Clean
LIGHT_THEME = Theme(
    name="Light",
    background="#fafafa",
    surface="#ffffff",
    primary="#00d9ff",
    primary_hover="#00b8d4",
    secondary="#f0f0f0",
    
    text_primary="#1a1a1a",
    text_secondary="#666666",
    text_disabled="#cccccc",
    
    border="#e0e0e0",
    input_bg="#ffffff",
    input_border="#e0e0e0",
    input_focus_border="#00d9ff",
    
    user_bubble_bg="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00d9ff, stop:1 #10a37f)",
    user_bubble_text="#ffffff",
    ai_bubble_bg="#ffffff",
    ai_bubble_text="#1a1a1a",
    
    success="#00d9ff",
    error="#ff6b6b",
    warning="#ffd93d",
    info="#6c63ff"
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

# Midnight Blue Theme - Enhanced
MIDNIGHT_THEME = Theme(
    name="Midnight Blue",
    background="#0d1117",
    surface="#161b22",
    primary="#58a6ff",
    primary_hover="#4d96e6",
    secondary="#21262d",
    
    text_primary="#f0f6fc",
    text_secondary="#8b949e",
    text_disabled="#484f58",
    
    border="#30363d",
    input_bg="#161b22",
    input_border="#30363d",
    input_focus_border="#58a6ff",
    
    user_bubble_bg="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #58a6ff, stop:1 #3b8fd9)",
    user_bubble_text="#ffffff",
    ai_bubble_bg="#161b22",
    ai_bubble_text="#f0f6fc",
    
    success="#56d364",
    error="#f85149",
    warning="#d29922",
    info="#58a6ff"
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
    
    def get_common_styles(self) -> dict:
        """Get common CSS styles for consistent design"""
        return {
            "shadow_sm": "box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);",
            "shadow_md": "box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);",
            "shadow_lg": "box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);",
            "transition_fast": "transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);",
            "transition_base": "transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);",
            "transition_slow": "transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);",
            "hover_scale": "transform: scale(1.05);",
            "hover_scale_sm": "transform: scale(1.02);",
        }


# Global theme manager instance
theme_manager = ThemeManager()


if __name__ == "__main__":
    # Test theme manager
    print("Available themes:")
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        theme = theme_manager.get_theme()
        print(f"  - {theme.name}: {theme.background}")
