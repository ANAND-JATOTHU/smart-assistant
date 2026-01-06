"""
System Control Tool
Control volume, brightness, screenshots, clipboard
"""

import subprocess
from typing import Dict, Any, List
from .base import Tool


class SystemTool(Tool):
    """System control operations"""
    
    def __init__(self):
        super().__init__(
            name="system_control",
            description="Control system settings and take screenshots"
        )
        self.requires_confirmation = False
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'action',
                'type': 'string',
                'description': 'Action to perform',
                'required': True,
                'enum': ['volume', 'screenshot', 'clipboard']
            },
            {
                'name': 'value',
                'type': 'string',
                'description': 'Value for action (e.g., volume level, clipboard text)',
                'required': False
            }
        ]
    
    def execute(self, **params) -> Dict[str, Any]:
        """Execute system control"""
        is_valid, error = self.validate_params(**params)
        if not is_valid:
            return {'success': False, 'error': error}
        
        action = params['action']
        
        try:
            if action == 'volume':
                return self._control_volume(params.get('value'))
            elif action == 'screenshot':
                return self._take_screenshot()
            elif action == 'clipboard':
                return self._get_clipboard()
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _control_volume(self, value: str) -> Dict[str, Any]:
        """Control system volume"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            if value:
                if value.lower() in ['up', 'increase']:
                    current = volume.GetMasterVolumeLevelScalar()
                    volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
                    return {'success': True, 'message': 'Volume increased'}
                elif value.lower() in ['down', 'decrease']:
                    current = volume.GetMasterVolumeLevelScalar()
                    volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
                    return {'success': True, 'message': 'Volume decreased'}
                elif value.lower() == 'mute':
                    volume.SetMute(1, None)
                    return {'success': True, 'message': 'Volume muted'}
                elif value.lower() == 'unmute':
                    volume.SetMute(0, None)
                    return {'success': True, 'message': 'Volume unmuted'}
                else:
                    # Set specific level (0-100)
                    try:
                        level = int(value) / 100.0
                        volume.SetMasterVolumeLevelScalar(level, None)
                        return {'success': True, 'message': f'Volume set to {value}%'}
                    except ValueError:
                        return {'success': False, 'error': 'Invalid volume value'}
            else:
                current = volume.GetMasterVolumeLevelScalar()
                return {
                    'success': True,
                    'result': int(current * 100),
                    'message': f'Current volume: {int(current * 100)}%'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Volume control error: {e}'}
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            import pyautogui
            from datetime import datetime
            from pathlib import Path
            
            # Save to Pictures folder
            pictures_dir = Path.home() / "Pictures" / "Smart Assistant Screenshots"
            pictures_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = pictures_dir / f"screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            return {
                'success': True,
                'result': str(filename),
                'message': f'Screenshot saved to {filename}'
            }
        except Exception as e:
            return {'success': False, 'error': f'Screenshot error: {e}'}
    
    def _get_clipboard(self) -> Dict[str, Any]:
        """Get clipboard content"""
        try:
            import pyperclip
            
            content = pyperclip.paste()
            return {
                'success': True,
                'result': content,
                'message': 'Clipboard content retrieved'
            }
        except Exception as e:
            return {'success': False, 'error': f'Clipboard error: {e}'}
