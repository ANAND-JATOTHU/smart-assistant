"""
File Operations Tool
Search, open, and manage files
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from .base import Tool


class FileTool(Tool):
    """File operations"""
    
    def __init__(self):
        super().__init__(
            name="file_operations",
            description="Search, open, and manage files"
        )
        self.requires_confirmation = True
        self.is_dangerous = True
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'action',
                'type': 'string',
                'description': 'Action to perform',
                'required': True,
                'enum': ['search', 'open', 'create', 'delete']
            },
            {
                'name': 'path',
                'type': 'string',
                'description': 'File or folder path',
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
        """Execute file operation"""
        is_valid, error = self.validate_params(**params)
        if not is_valid:
            return {'success': False, 'error': error}
        
        action = params['action']
        
        try:
            if action == 'search':
                return self._search_files(params.get('query'))
            elif action == 'open':
                return self._open_file(params.get('path'))
            elif action == 'create':
                return self._create_file(params.get('path'))
            elif action == 'delete':
                return self._delete_file(params.get('path'))
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _search_files(self, query: str) -> Dict[str, Any]:
        """Search for files"""
        if not query:
            return {'success': False, 'error': 'query required'}
        
        try:
            # Search in common directories
            search_dirs = [
                Path.home() / "Desktop",
                Path.home() / "Documents",
                Path.home() / "Downloads"
            ]
            
            results = []
            for search_dir in search_dirs:
                if search_dir.exists():
                    for file in search_dir.rglob(f"*{query}*"):
                        if file.is_file():
                            results.append(str(file))
                        if len(results) >= 10:  # Limit results
                            break
            
            return {
                'success': True,
                'result': results,
                'message': f'Found {len(results)} files matching "{query}"'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _open_file(self, path: str) -> Dict[str, Any]:
        """Open a file"""
        if not path:
            return {'success': False, 'error': 'path required'}
        
        try:
            if os.path.exists(path):
                os.startfile(path)
                return {
                    'success': True,
                    'result': f'Opened {path}',
                    'message': f'Successfully opened {path}'
                }
            else:
                return {'success': False, 'error': f'File not found: {path}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_file(self, path: str) -> Dict[str, Any]:
        """Create a file"""
        if not path:
            return {'success': False, 'error': 'path required'}
        
        try:
            Path(path).touch()
            return {
                'success': True,
                'result': f'Created {path}',
                'message': f'Successfully created {path}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file"""
        if not path:
            return {'success': False, 'error': 'path required'}
        
        try:
            if os.path.exists(path):
                os.remove(path)
                return {
                    'success': True,
                    'result': f'Deleted {path}',
                    'message': f'Successfully deleted {path}'
                }
            else:
                return {'success': False, 'error': f'File not found: {path}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
