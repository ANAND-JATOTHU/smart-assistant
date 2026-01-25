"""
Browser Control Tool
Open URLs, search engines, manage browser operations
"""

import webbrowser
import urllib.parse
from typing import Dict, Any, List
from .base import Tool


class BrowserTool(Tool):
    """Control browser operations"""
    
    def __init__(self):
        super().__init__(
            name="browser_control",
            description="Open URLs, search Google, search YouTube"
        )
        self.requires_confirmation = False
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'action',
                'type': 'string',
                'description': 'Action to perform',
                'required': True,
                'enum': ['open', 'search', 'youtube']
            },
            {
                'name': 'url',
                'type': 'string',
                'description': 'URL to open',
                'required': False
            },
            {
                'name': 'query',
                'type': 'string',
                'description': 'Search query',
                'required': False
            }
        ]
    
    def execute(self, **params) -> Dict[str, Any]:
        """Execute browser control"""
        is_valid, error = self.validate_params(**params)
        if not is_valid:
            return {'success': False, 'error': error}
        
        action = params['action']
        
        try:
            if action == 'open':
                return self._open_url(params.get('url'))
            elif action == 'search':
                return self._search_google(params.get('query'))
            elif action == 'youtube':
                return self._search_youtube(params.get('query'))
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _open_url(self, url: str) -> Dict[str, Any]:
        """Open a specific URL"""
        if not url:
            return {'success': False, 'error': 'URL required'}
        
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
            return {'success': False, 'error': f'Failed to open URL: {e}'}
    
    def _search_google(self, query: str) -> Dict[str, Any]:
        """Search on Google"""
        if not query:
            return {'success': False, 'error': 'Query required'}
        
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            
            # Try Chrome first, fallback to default browser
            try:
                webbrowser.get('chrome').open(search_url)
            except:
                webbrowser.open(search_url)
            
            return {
                'success': True,
                'result': f'Searching for: {query}',
                'message': f'Opened browser with Google search: {query}'
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to search: {e}'}
    
    def _search_youtube(self, query: str) -> Dict[str, Any]:
        """Search on YouTube"""
        if not query:
            return {'success': False, 'error': 'Query required'}
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            
            return {
                'success': True,
                'result': f'Searching YouTube for: {query}',
                'message': f'Opened YouTube with search: {query}'
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to search YouTube: {e}'}


# Utility functions
def search_google(query: str) -> Dict[str, Any]:
    """Search on Google Chrome"""
    tool = BrowserTool()
    return tool.execute(action='search', query=query)


def search_youtube(query: str) -> Dict[str, Any]:
    """Search on YouTube"""
    tool = BrowserTool()
    return tool.execute(action='youtube', query=query)


def open_url(url: str) -> Dict[str, Any]:
    """Open a specific website"""
    tool = BrowserTool()
    return tool.execute(action='open', url=url)


if __name__ == "__main__":
    # Test browser tool
    tool = BrowserTool()
    
    print("Testing browser tool...")
    
    # Test Google search
    result = tool.execute(action='search', query='Python programming')
    print(f"\nGoogle search: {result}")
    
    # Test YouTube search
    result = tool.execute(action='youtube', query='AI tutorials')
    print(f"\nYouTube search: {result}")
    
    # Test URL open
    result = tool.execute(action='open', url='github.com')
    print(f"\nURL open: {result}")
