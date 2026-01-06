"""
Command Parser - Natural Language to System Commands
Detects user intents and executes system commands
"""

import re
from typing import Dict, Any, Optional, Tuple


class CommandParser:
    """Parse natural language commands"""
    
    def __init__(self):
        """Initialize command parser with pattern matching"""
        self.command_patterns = {
            # Volume commands
            'volume_up': [
                r'(?:increase|raise|turn up|up)\s+(?:the\s+)?volume',
                r'volume\s+up',
                r'louder'
            ],
            'volume_down': [
                r'(?:decrease|lower|turn down|down)\s+(?:the\s+)?volume',
                r'volume\s+down',
                r'(?:make it\s+)?quieter'
            ],
            'volume_mute': [
                r'mute(?:\s+(?:the\s+)?(?:sound|volume|audio))?',
                r'silence(?:\s+(?:the\s+)?(?:sound|volume))?'
            ],
            'volume_unmute': [
                r'unmute(?:\s+(?:the\s+)?(?:sound|volume|audio))?',
                r'turn\s+(?:the\s+)?sound\s+back\s+on'
            ],
            'volume_set': [
                r'(?:set|change)\s+(?:the\s+)?volume\s+to\s+(\d+)',
                r'volume\s+(\d+)\s*(?:percent|%)?'
            ],
            
            # Settings commands
            'open_settings': [
                r'open\s+(?:windows\s+)?settings',
                r'(?:go|take me)\s+to\s+settings',
                r'show\s+(?:me\s+)?settings'
            ],
            
            # Search commands
            'search_chrome': [
                r'search\s+(?:for\s+)?"?(.+?)"?\s+(?:on|in)\s+(?:chrome|web|google)',
                r'google\s+"?(.+?)"?',
                r'search\s+"?(.+?)"?\s+on\s+(?:chrome|web)',
                r'look up\s+"?(.+?)"?\s+(?:on\s+)?(?:chrome|web)',
                r'(?:chrome|web)\s+search\s+"?(.+?)"?',
                r'search\s+(?:the\s+)?(?:web|internet)\s+for\s+"?(.+?)"?'
            ],
            'search_youtube': [
                r'search\s+(?:for\s+)?"?(.+?)"?\s+(?:on|in)\s+youtube',
                r'(?:find|search)\s+youtube\s+(?:for\s+)?"?(.+?)"?$',
                r'look up\s+"?(.+?)"?\s+(?:on\s+)?youtube',
                r'youtube\s+search\s+"?(.+?)"?$',
                r'"(.+)"\s+search\s+(?:on\s+)?youtube',
                r'search\s+"(.+)"\s+on\s+youtube'
            ],
            
            # Application commands
            'open_app': [
                r'open\s+(.+?)(?:\s+(?:app|application|program))?$',
                r'launch\s+(.+)',
                r'start\s+(.+?)(?:\s+(?:app|application))?$'
            ],
            
            # Website commands
            'open_website': [
                r'(?:open|go to|visit)\s+(.+?)\s+(?:on\s+)?(?:chrome|browser)',
                r'visit\s+(?:website\s+)?(.+)',
                r'(?:open|go to)\s+(?:the\s+)?website\s+(.+)',
                r'browse\s+(?:to\s+)?(.+\.(?:com|org|net|io|co|in))'
            ]
        }
    
    def parse(self, text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse text for commands
        
        Returns:
            Tuple of (command_type, params) or (None, None) if no command found
        """
        if not text:
            return None, None
        
        text_lower = text.lower().strip()
        
        # Check each command pattern
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Extract parameters if any
                    params = {}
                    if match.groups():
                        if command_type == 'search_chrome':
                            params['query'] = match.group(1).strip()
                        elif command_type == 'search_youtube':
                            params['query'] = match.group(1).strip()
                        elif command_type == 'volume_set':
                            params['level'] = int(match.group(1))
                        elif command_type == 'open_app':
                            params['app_name'] = match.group(1).strip()
                        elif command_type == 'open_website':
                            params['url'] = match.group(1).strip()
                    
                    return command_type, params
        
        return None, None
    
    def execute(self, command_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parsed command"""
        from tools.applications import (
            search_chrome, search_youtube, open_settings, open_website
        )
        from tools.system import SystemTool
        
        try:
            # Volume commands
            if command_type.startswith('volume_'):
                system_tool = SystemTool()
                
                if command_type == 'volume_up':
                    return system_tool._control_volume('up')
                elif command_type == 'volume_down':
                    return system_tool._control_volume('down')
                elif command_type == 'volume_mute':
                    return system_tool._control_volume('mute')
                elif command_type == 'volume_unmute':
                    return system_tool._control_volume('unmute')
                elif command_type == 'volume_set':
                    return system_tool._control_volume(str(params.get('level', 50)))
            
            # Settings command
            elif command_type == 'open_settings':
                return open_settings()
            
            # Search commands
            elif command_type == 'search_chrome':
                query = params.get('query', '')
                if query:
                    return search_chrome(query)
                else:
                    return {'success': False, 'error': 'No search query provided'}
            
            elif command_type == 'search_youtube':
                query = params.get('query', '')
                if query:
                    return search_youtube(query)
                else:
                    return {'success': False, 'error': 'No search query provided'}
            
            # Open application
            elif command_type == 'open_app':
                from tools.applications import ApplicationTool
                app_tool = ApplicationTool()
                app_name = params.get('app_name', '')
                if app_name:
                    return app_tool._open_app(app_name)
                else:
                    return {'success': False, 'error': 'No application name provided'}
            
            # Open website
            elif command_type == 'open_website':
                url = params.get('url', '')
                if url:
                    return open_website(url)
                else:
                    return {'success': False, 'error': 'No URL provided'}
            
            else:
                return {'success': False, 'error': f'Unknown command type: {command_type}'}
        
        except Exception as e:
            return {'success': False, 'error': f'Command execution error: {str(e)}'}


def parse_and_execute(text: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Convenience function to parse and execute command
    
    Returns:
        Tuple of (is_command, result)
        - is_command: True if text was a system command
        - result: Command execution result if is_command, else None
    """
    parser = CommandParser()
    command_type, params = parser.parse(text)
    
    if command_type:
        result = parser.execute(command_type, params)
        return True, result
    
    return False, None


# Test function
if __name__ == "__main__":
    parser = CommandParser()
    
    # Test cases
    test_commands = [
        "increase the volume",
        "search interview questions on chrome",
        "find python tutorials on youtube",
        "open settings",
        "set volume to 50",
        "mute",
        "open calculator"
    ]
    
    print("=== Command Parser Tests ===\n")
    for cmd in test_commands:
        command_type, params = parser.parse(cmd)
        print(f"Input: {cmd}")
        print(f"  → Command: {command_type}")
        print(f"  → Params: {params}")
        print()
