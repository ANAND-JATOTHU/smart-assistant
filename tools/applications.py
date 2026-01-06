"""
Application Control Tool - Enhanced
Open, close, manage applications, and search Chrome/YouTube
"""

import os
import subprocess
import psutil
import webbrowser
import urllib.parse
from typing import Dict, Any, List
from .base import Tool


class ApplicationTool(Tool):
    """Control applications"""
    
    def __init__(self):
        super().__init__(
            name="application_control",
            description="Open, close, and manage applications"
        )
        self.requires_confirmation = False
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'action',
                'type': 'string',
                'description': 'Action to perform',
                'required': True,
                'enum': ['open', 'close', 'list']
            },
            {
                'name': 'app_name',
                'type': 'string',
                'description': 'Application name',
                'required': False
            }
        ]
    
    def execute(self, **params) -> Dict[str, Any]:
        """Execute application control"""
        is_valid, error = self.validate_params(**params)
        if not is_valid:
            return {'success': False, 'error': error}
        
        action = params['action']
        
        try:
            if action == 'open':
                return self._open_app(params.get('app_name'))
            elif action == 'close':
                return self._close_app(params.get('app_name'))
            elif action == 'list':
                return self._list_apps()
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _open_app(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        if not app_name:
            return {'success': False, 'error': 'app_name required'}
        
        # Special handling for Windows Settings
        if app_name.lower() in ['settings', 'windows settings', 'system settings']:
            try:
                subprocess.Popen('start ms-settings:', shell=True)
                return {
                    'success': True,
                    'result': 'Opened Windows Settings',
                    'message': 'Successfully opened Windows Settings'
                }
            except Exception as e:
                return {'success': False, 'error': f'Failed to open settings: {e}'}
        
        # Common Windows applications
        app_map = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'vscode': 'code.exe',
            'spotify': 'spotify.exe'
        }
        
        app_lower = app_name.lower()
        executable = app_map.get(app_lower, app_name)
        
        try:
            subprocess.Popen(executable, shell=True)
            return {
                'success': True,
                'result': f'Opened {app_name}',
                'message': f'Successfully opened {app_name}'
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to open {app_name}: {e}'}
    
    def _close_app(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        if not app_name:
            return {'success': False, 'error': 'app_name required'}
        
        try:
            closed = False
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed = True
            
            if closed:
                return {
                    'success': True,
                    'result': f'Closed {app_name}',
                    'message': f'Successfully closed {app_name}'
                }
            else:
                return {'success': False, 'error': f'{app_name} not running'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to close {app_name}: {e}'}
    
    def _list_apps(self) -> Dict[str, Any]:
        """List running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['name', 'pid']):
                apps.append({
                    'name': proc.info['name'],
                    'pid': proc.info['pid']
                })
            
            return {
                'success': True,
                'result': apps,
                'message': f'Found {len(apps)} running processes'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Utility functions for easy access
def search_chrome(query: str) -> Dict[str, Any]:
    """Search on Google Chrome"""
    try:
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        # Try Chrome first
        try:
            webbrowser.get('chrome').open(search_url)
        except:
            # Fallback to default browser
            webbrowser.open(search_url)
        return {
            'success': True,
            'result': f'Searching for: {query}',
            'message': f'Opened browser with search: {query}'
        }
    except Exception as e:
        return {'success': False, 'error': f'Failed to open browser: {e}'}


def search_youtube(query: str) -> Dict[str, Any]:
    """Search on YouTube"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        return {
            'success': True,
            'result': f'Searching YouTube for: {query}',
            'message': f'Opened YouTube with search: {query}'
        }
    except Exception as e:
        return {'success': False, 'error': f'Failed to open YouTube: {e}'}


def open_settings() -> Dict[str, Any]:
    """Open Windows Settings"""
    try:
        subprocess.Popen('start ms-settings:', shell=True)
        return {
            'success': True,
            'result': 'Opened Windows Settings',
            'message': 'Successfully opened Windows Settings'
        }
    except Exception as e:
        return {'success': False, 'error': f'Failed to open settings: {e}'}


def open_website(url: str) -> Dict[str, Any]:
    """Open a specific website"""
    try:
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
        return {
            'success': True,
            'result': f'Opened {url}',
            'message': f'Successfully opened {url}'
        }
    except Exception as e:
        return {'success': False, 'error': f'Failed to open website: {e}'}
